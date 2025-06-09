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
    if (event.detail === 0) return;
    const inputField = document.getElementById("user-input");

    if (!recognizing) {
      finalTranscript = ""; 
      recognition.start();
      recognizing = true;
      micButton.classList.add("text-red-500");
      inputField.placeholder = "Recording... speak now and click the mic again to stop.";
    } else {
      recognition.stop();
      recognizing = false;
      micButton.classList.remove("text-red-500");
      inputField.placeholder = "Click the mic to start your pitch, click again to end your pitch...";
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
      // Send to backend for punctuation/capitalization
      try {
        const response = await fetch('/punctuate', {
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
  };
} else {
  micButton.disabled = true;
  micButton.classList.add("opacity-50", "cursor-not-allowed");
  micButton.title = "Voice input not supported in this browser";
}