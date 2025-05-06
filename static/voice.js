const micButton = document.getElementById("mic-button");

if ('webkitSpeechRecognition' in window) {
  const recognition = new webkitSpeechRecognition();
  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.lang = 'en-US';

  let recognizing = false;

  micButton.addEventListener("click", () => {
    if (!recognizing) {
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
    const transcript = event.results[0][0].transcript.trim();
    document.getElementById("user-input").value = transcript;

    // Automatically submit the form
    document.getElementById("chat-form").dispatchEvent(new Event("submit"));
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
