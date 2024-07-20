from flask import Flask, request, jsonify, send_from_directory
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import mysql.connector
from mysql.connector import errorcode
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load pre-trained model and tokenizer
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
model = GPT2LMHeadModel.from_pretrained(model_name)

# Create a Flask app
app = Flask(__name__)

# Database configuration
db_config = {
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME')
}

# Connect to the database
def connect_db():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    return None

# Function to generate a response
def generate_response(user_input):
    inputs = tokenizer.encode(user_input + tokenizer.eos_token, return_tensors='pt')
    attention_mask = torch.ones(inputs.shape, dtype=torch.long)
    outputs = model.generate(inputs,attention_mask=attention_mask, max_length=100, pad_token_id=tokenizer.eos_token_id)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

# Function to store conversation
def store_conversation(user_message, bot_response):
    conn = connect_db()
    if conn is None:
        return
    cursor = conn.cursor()
    query = "INSERT INTO conversations (user_message, bot_response) VALUES (%s, %s)"
    cursor.execute(query, (user_message, bot_response))
    conn.commit()
    cursor.close()
    conn.close()

# Define a route for the chatbot
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    if not user_input:
        return jsonify({"error": "No input message provided"}), 400
    response = generate_response(user_input)
    store_conversation(user_input, response)
    return jsonify({"response": response})

# Serve the frontend files
@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
    return send_from_directory('frontend', path)

@app.route('/')
def root():
    return send_from_directory('frontend', 'index.html')

if __name__ == "__main__":
    app.run(debug=True)
