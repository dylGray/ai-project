'use strict';

const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userMessage = userInput.value.trim();
    if (!userMessage) return;

    chatBox.innerHTML += `
    <div class="flex items-start justify-end space-x-2 space-x-reverse">
        <div class="bg-blue-600 text-white px-4 py-2 rounded-lg max-w-xl text-left">${userMessage}</div>
        <div class="text-2xl">👤</div>
    </div>
    `;

    userInput.value = '';
    chatBox.scrollTop = chatBox.scrollHeight;

    const thinkingIndicator = document.createElement('div');
    thinkingIndicator.className = "text-left flex items-center space-x-2";
    thinkingIndicator.innerHTML = `
        <div class="inline-block px-4 py-2 rounded-lg">
            <div class="dot-flashing"></div>
        </div>
    `;
    chatBox.appendChild(thinkingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;

    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
    });

    chatBox.removeChild(thinkingIndicator);

    const data = await response.json();
    const reply = data.response || `<span class="text-red-400">Error:</span> ${data.error}`;

    chatBox.innerHTML += `
        <div class="flex items-start space-x-2">
            <div class="text-2xl">🤖</div>
            <div class="bg-green-700 text-white px-4 py-2 rounded-lg max-w-xl">${reply}</div>
        </div>
    `;

    chatBox.scrollTop = chatBox.scrollHeight;
});