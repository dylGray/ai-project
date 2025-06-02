'use strict';

const chatContainer = document.getElementById('chat-container');
const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const headText = document.getElementById('head-text-container');

chatContainer.classList.remove('bg-neutral-800');

// store the “normal” form classes to restore after first submit
const normalFormClasses = "mt-4 flex items-center bg-neutral-700 rounded-full px-4 py-2 shadow-lg h-14";

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userMessage = userInput.value.trim();
    if (!userMessage) return;

    // if this is the very first message, unhide the chat window and reposition the form
    if (chatBox.classList.contains('hidden')) {
        chatBox.classList.remove('hidden');
        chatForm.className = normalFormClasses;
        chatContainer.classList.add('bg-neutral-800');
        headText.classList.remove('mt-24', 'md:mt-40');
        headText.classList.add('mt-12', 'md:mt-20');
    }

    chatBox.innerHTML += `
      <div class="flex items-start justify-end space-x-2 space-x-reverse">
        <div class="bg-blue-600 text-white px-4 py-2 rounded-lg max-w-xl text-left">${userMessage}</div>
        <i style="margin: 2.5px -5px 0 7.5px;" class="fa-solid fa-user"></i>
      </div>
    `;

    userInput.value = '';

    const instructions = document.getElementById('mobile-instructions');
    if (instructions) {
        instructions.style.display = 'none';
    }

    chatBox.scrollTop = chatBox.scrollHeight;

    // “thinking” indicator
    const thinkingIndicator = document.createElement('div');
    thinkingIndicator.className = "text-left flex items-center space-x-2";
    thinkingIndicator.innerHTML = `
      <div class="inline-block px-4 py-2 rounded-lg">
        <div class="dot-flashing"></div>
      </div>
    `;
    chatBox.appendChild(thinkingIndicator);
    chatBox.scrollTop = chatBox.scrollHeight;

    // send to backend
    const response = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
    });

    chatBox.removeChild(thinkingIndicator);

    const data = await response.json();
    const reply = data.response || `<span class="text-red-400">Error:</span> ${data.error}`;

    // Typewriter effect for AI response
    const aiContainer = document.createElement('div');
    aiContainer.className = "flex items-start space-x-2";
    aiContainer.innerHTML = `
      <img src="/static/images/tps-logo.webp" alt="AI Logo" class="w-5 h-5 mt-2 rounded shadow-md" />
      <div class="bg-green-700 text-white px-4 py-2 rounded-lg max-w-xl typewriter-output"></div>
    `;
    chatBox.appendChild(aiContainer);
    chatBox.scrollTop = chatBox.scrollHeight;

    const outputDiv = aiContainer.querySelector('.typewriter-output');
    let i = 0;
    function typeWriter() {
      if (i < reply.length) {
        outputDiv.innerHTML += reply[i] === '\n' ? '<br>' : reply[i];
        i++;
        chatBox.scrollTop = chatBox.scrollHeight;
        setTimeout(typeWriter, 15); // adjust typing speed here
      }
    }
    typeWriter();

    chatBox.scrollTop = chatBox.scrollHeight;
});
