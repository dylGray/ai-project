'use strict';

// using the webkitSpeechRecognition API for voice input
// this is a non-standard API, so it may not work in all browsers

const micButton = document.getElementById("mic-button");
const sendButton = document.getElementById('send-button');

userInput.addEventListener('input', () => {
  if (userInput.value.trim().length > 0) {
    sendButton.classList.remove('hidden');
  } else {
    sendButton.classList.add('hidden');
  }
});

if ('webkitSpeechRecognition' in window) {
  const recognition = new webkitSpeechRecognition();
  recognition.continuous = true; 
  recognition.interimResults = false; 
  recognition.lang = 'en-US';

  let recognizing = false;
  let finalTranscript = ""; 

  // Helper to add/remove red pulsing dot during recording
  function showRecordingDot(show) {
    let dot = document.getElementById('recording-dot');
    if (show) {
      if (!dot) {
        dot = document.createElement('span');
        dot.id = 'recording-dot';
        dot.className = 'pulsing-dot-red ml-2';
        micButton.parentNode.insertBefore(dot, micButton.nextSibling);
      }
    } else {
      if (dot) dot.remove();
    }
  }

  // Helper to show/hide the recording overlay
  function toggleRecordingOverlay(show) {
    let overlay = document.getElementById('recording-overlay');
    const inputField = document.getElementById('user-input');
    if (show) {
      if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'recording-overlay';
        overlay.className = 'absolute left-0 top-0 w-full h-full flex items-center px-3 bg-transparent pointer-events-none';
        overlay.innerHTML = '<span class="pulsing-dot-red mr-2"></span><span class="text-gray-400">Recording... </span>';
        inputField.parentNode.style.position = 'relative';
        inputField.classList.add('opacity-0');
        inputField.parentNode.appendChild(overlay);
      }
    } else {
      if (overlay) overlay.remove();
      inputField.classList.remove('opacity-0');
    }
  }

  micButton.addEventListener("click", (event) => {
    if (event.detail === 0) return;
    const inputField = document.getElementById("user-input");

    if (!recognizing) {
      finalTranscript = ""; 
      recognition.start();
      recognizing = true;
      micButton.classList.add("text-red-500");
      inputField.placeholder = "Recording... ";
      toggleRecordingOverlay(true);
    } else {
      recognition.stop();
      recognizing = false;
      micButton.classList.remove("text-red-500");
      inputField.placeholder = "Click the mic to start your pitch, click again to end your pitch.";

      if (window.innerWidth < 768) {
        userInput.placeholder = "Press the mic to start your pitch";
      } else {
          userInput.placeholder = "Click the mic to start your pitch, click again to end your pitch.";
      }

      toggleRecordingOverlay(false);
    }
  });

  recognition.onresult = (event) => {
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript + " ";
      }
    }
  };

  recognition.onend = async () => {
    if (finalTranscript.trim().length > 0) {
      let processed = finalTranscript.trim();
      // send to backend for punctuation/capitalization
      try {
        const response = await fetch('/clean', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: processed })
        });
        const data = await response.json();
        if (data.punctuated) {
          processed = data.punctuated;
        } else if (data.error) {
          console.error('Punctuation API error:', data.error);
        }
      } catch (err) {
        console.error('Error calling punctuation API:', err);
      }
      document.getElementById("user-input").value = processed;
      document.getElementById("chat-form").dispatchEvent(new Event("submit"));
    }
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    recognizing = false;
    micButton.classList.remove("text-red-500");
    toggleRecordingOverlay(false);
  };
} else {
  micButton.disabled = true;
  micButton.classList.add("opacity-50", "cursor-not-allowed");
  micButton.title = "Voice input not supported in this browser";
}