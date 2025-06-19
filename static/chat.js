'use strict';

const chatContainer = document.getElementById('chat-container');
const chatBox = document.getElementById('chat-box');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const headText = document.getElementById('head-text-container');

// chatContainer.classList.remove('bg-neutral-800');

// store the “normal” form classes to restore after first submit
const normalFormClasses = "mt-4 flex items-center bg-neutral-700 rounded-full px-4 py-2 shadow-lg h-14";

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const userMessage = userInput.value.trim();
    if (!userMessage) return;

    // if this is the very first message, unhide the chat window and reposition the form
    if (chatBox.classList.contains('hidden')) {
        // Hide all children of #main-container
        const mainContainer = document.getElementById('main-container');
        if (mainContainer) {
            Array.from(mainContainer.children).forEach(child => {
                child.style.display = 'none';
            });
        }

        chatBox.classList.remove('hidden');
        chatForm.className = normalFormClasses;

        const isDark = document.body.classList.contains('dark-mode');
        // if (isDark) {  
        //     chatContainer.classList.remove('bg-neutral-100');
        //     chatContainer.classList.add('bg-neutral-900');
        // } else {
        //     chatContainer.classList.remove('bg-neutral-800'); 
        //     chatContainer.classList.add('bg-neutral-200');  
        // }

        // chatContainer.classList.add('bg-neutral-800');
        headText.classList.remove('mt-24', 'md:mt-40');
        headText.classList.add('mt-12', 'md:mt-20');

        const helpButton = document.getElementById('help-button');
        const mobileMessage = document.getElementById('mobile-message');
        if (helpButton) helpButton.style.display = 'none';
        if (mobileMessage) mobileMessage.style.display = 'none';

        const refreshContainer = document.getElementById('refresh-container');
        if (refreshContainer) refreshContainer.classList.remove('hidden');

        const sendButton = document.getElementById('send-button');
        if (sendButton) sendButton.classList.add('hidden');
    }

    chatBox.innerHTML += `
      <div class="flex items-start justify-end space-x-2 space-x-reverse">
        <div class="bg-blue-600 text-white px-4 py-2 rounded-lg max-w-xl text-left"><span id="user-message">${userMessage}</span></div>
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

    // typewriter effect for AI response
    const aiContainer = document.createElement('div');
    aiContainer.className = "flex items-start space-x-2";
    aiContainer.innerHTML = `
      <img src="/static/images/tps-logo.webp" alt="AI Logo" class="w-5 h-5 mt-2 rounded shadow-md" />
      <div id="model-output" class="bg-green-700 text-white px-4 py-2 rounded-lg max-w-xl typewriter-output"></div>
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

const refreshBtn = document.getElementById('refresh-chat-btn');
if (refreshBtn) {
    refreshBtn.addEventListener('click', () => {
        window.location.reload();
    });
}

// New Chat button functionality (same as refresh)
const newChatBtn = document.getElementById('new-chat-btn');
if (newChatBtn) {
    newChatBtn.addEventListener('click', () => {
        window.location.reload();
    });
}

// Theme toggle logic
const themeToggle = document.getElementById('theme-toggle');
const themeToggleText = document.getElementById('theme-toggle-text');

function setTheme(dark) {
  if (dark) {
    document.body.classList.add('dark-mode');
    document.documentElement.classList.add('dark-mode');
    if (themeToggle) themeToggle.querySelector('i').className = 'fa-solid fa-sun';
    localStorage.setItem('theme', 'dark');
    
  } else {
    document.body.classList.remove('dark-mode');
    document.documentElement.classList.remove('dark-mode');
    if (themeToggle) themeToggle.querySelector('i').className = 'fa-solid fa-moon';
    localStorage.setItem('theme', 'light');
  }
}

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const isDark = document.body.classList.contains('dark-mode');
    setTheme(!isDark);

    // if (chatBox && !chatBox.classList.contains('hidden')) {
    //   // Chat form has been submitted at least once
    //   if (document.body.classList.contains('dark-mode')) {
    //     chatContainer.classList.remove('bg-neutral-200');
    //     chatContainer.classList.add('bg-neutral-800');
    //   } else {
    //     chatContainer.classList.remove('bg-neutral-800');
    //     chatContainer.classList.add('bg-neutral-200');
    //   }
    // }

  });
}

// On load, set theme from localStorage or system preference
(function() {
  const saved = localStorage.getItem('theme');
  if (saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    setTheme(true);
  } else {
    setTheme(false);
  }
})();
