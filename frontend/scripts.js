async function sendMessage() {
    const userInput = document.getElementById('user-input').value;
    if (!userInput) return;

    appendMessage(userInput, 'user-message');

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userInput })
        });
        const data = await response.json();
        appendMessage(data.response, 'bot-message');
    } catch (error) {
        appendMessage('Error: Unable to get response from the bot.', 'bot-message');
    }

    document.getElementById('user-input').value = '';
    document.getElementById('user-input').focus();
}

function appendMessage(message, className) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${className}`;
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight;
}
