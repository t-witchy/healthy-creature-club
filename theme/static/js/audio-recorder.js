document.addEventListener("DOMContentLoaded", function () {
  const recordAudioButton = document.getElementById("recordAudioButton");
  const audioPlayer = document.getElementById("audioPlayer");
  const responseContainer = document.getElementById("responseContainer");

  let isRecording = false;
  let mediaRecorder;
  let recordedChunks = [];

  // Toggle recording on button click
  recordAudioButton.addEventListener("click", async () => {
    if (!isRecording) {
      // Start recording
      recordAudioButton.classList.remove("bg-indigo-600", "hover:bg-indigo-500");
      recordAudioButton.classList.add("bg-red-600", "hover:bg-red-500");
      recordAudioButton.textContent = "⏸";

      isRecording = true;
      startRecording();
    } else {
      // Stop recording
      recordAudioButton.classList.remove("bg-red-600", "hover:bg-red-500");
      recordAudioButton.classList.add("bg-indigo-600", "hover:bg-indigo-500");
      recordAudioButton.textContent = "🎤";

      isRecording = false;
      stopRecording();
    }
  });

  // Start recording function
  async function startRecording() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

      // Use the most compatible MIME type
      let options = { mimeType: "audio/webm" };
      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        options = { mimeType: "audio/ogg" };
      }

      if (!MediaRecorder.isTypeSupported(options.mimeType)) {
        throw new Error("No supported MIME types for MediaRecorder.");
      }

      mediaRecorder = new MediaRecorder(stream, options);

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          recordedChunks.push(event.data);
        }
      };

      mediaRecorder.start();
    } catch (error) {
      console.error("Error accessing microphone:", error);
      alert("Could not access microphone. Please check your permissions.");
    }
  }

  // Stop recording function
  function stopRecording() {
    if (mediaRecorder) {
      mediaRecorder.stop();
      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(recordedChunks, { type: mediaRecorder.mimeType });
        const audioUrl = URL.createObjectURL(audioBlob);
        audioPlayer.src = audioUrl;
        recordedChunks = [];

        // Send the audio to the backend
        const response = await sendAudioToBackend(audioBlob);
        responseContainer.textContent = response.message;
      };
    }
  }

  // Function to send audio to the backend
  async function sendAudioToBackend(audioBlob) {
    const formData = new FormData();
    formData.append("audio", audioBlob);

    try {
      const response = await fetch("/transcribe-and-analyze/", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        return await response.json();
      } else {
        console.error("Failed to process audio:", response.statusText);
        return { message: "An error occurred while processing the audio." };
      }
    } catch (error) {
      console.error("Error sending audio to backend:", error);
      return { message: "An error occurred while sending the audio." };
    }
  }
});
