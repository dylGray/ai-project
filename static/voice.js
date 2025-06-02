'use strict';

// using the webkitSpeechRecognition API for voice input
// this is a non-standard API, so it may not work in all browsers

const micButton = document.getElementById("mic-button");

if ('webkitSpeechRecognition' in window) {
  const recognition = new webkitSpeechRecognition();
  recognition.continuous = true; 
  recognition.interimResults = false; 
  recognition.lang = 'en-US';

  let recognizing = false;
  let finalTranscript = ""; 

  micButton.addEventListener("click", (event) => {
    // only toggle mic if the click is a real mouse click (event.detail !== 0)
    // this prevents Enter/Space from toggling the mic when the button is focused
    if (event.detail === 0) return;
    if (!recognizing) {
      finalTranscript = ""; 
      recognition.start();
      recognizing = true;
      micButton.classList.add("text-red-500");
    } else {
      recognition.stop();
      recognizing = false;
      micButton.classList.remove("text-red-500");
    }
  });

  recognition.onresult = (event) => {
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript + " ";
      }
    }
  };

  recognition.onend = () => {
    if (finalTranscript.trim().length > 0) {
      document.getElementById("user-input").value = finalTranscript.trim();
      document.getElementById("chat-form").dispatchEvent(new Event("submit"));
    }
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    recognizing = false;
    micButton.classList.remove("text-red-500");
  };
} else {
  micButton.disabled = true;
  micButton.classList.add("opacity-50", "cursor-not-allowed");
  micButton.title = "Voice input not supported in this browser";
}