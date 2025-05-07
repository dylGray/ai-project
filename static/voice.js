const micButton = document.getElementById("mic-button");

if ('webkitSpeechRecognition' in window) {
  const recognition = new webkitSpeechRecognition();
  recognition.continuous = true; // keep capturing until stopped manually
  recognition.interimResults = false; // only use final results
  recognition.lang = 'en-US';

  let recognizing = false;
  let finalTranscript = ""; // to accumulate the results

  micButton.addEventListener("click", () => {
    if (!recognizing) {
      finalTranscript = ""; // reset transcript when starting
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
    // Iterate through the results and accumulate final transcripts.
    for (let i = event.resultIndex; i < event.results.length; i++) {
      if (event.results[i].isFinal) {
        finalTranscript += event.results[i][0].transcript + " ";
      }
    }
  };

  recognition.onend = () => {
    if (finalTranscript.trim().length > 0) {
      document.getElementById("user-input").value = finalTranscript.trim();
      // Automatically submit the form when recognition stops.
      document.getElementById("chat-form").dispatchEvent(new Event("submit"));
    }
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error:", event.error);
    recognizing = false;
    micButton.classList.remove("text-red-500");
  };
} else {
  // Disable mic button if not supported
  micButton.disabled = true;
  micButton.classList.add("opacity-50", "cursor-not-allowed");
  micButton.title = "Voice input not supported in this browser";
}