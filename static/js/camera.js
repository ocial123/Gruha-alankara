document.addEventListener('DOMContentLoaded', () => {
    const videoElement = document.getElementById('cameraFeed');
    const canvasElement = document.getElementById('captureCanvas');
    const captureBtn = document.getElementById('captureBtn');

    // Only execute if camera elements exist on the page
    if (!videoElement) return;

    // 1. Configure and Request Camera Access (WebRTC / MediaDevices API)
    const constraints = {
        video: {
            facingMode: "environment",
            width: { ideal: 1280 },
            height: { ideal: 720 }
        }
    };

    navigator.mediaDevices.getUserMedia(constraints)
        .then(stream => {
            videoElement.srcObject = stream;
            videoElement.play();
        })
        .catch(err => {
            console.error("Camera error: ", err);
            alert("Unable to access the camera. Please check your browser permissions.");
        });

    // 2. Theme Selection Logic
    let selectedTheme = "Modern"; // Default theme
    const themeCards = document.querySelectorAll('.theme-card');

    // Set default selected state visually
    const defaultCard = document.querySelector('[data-theme="Modern"]');
    if (defaultCard) defaultCard.classList.add('selected');

    themeCards.forEach(card => {
        card.addEventListener('click', () => {
            themeCards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selectedTheme = card.getAttribute('data-theme');
        });
    });

    // 3. Capture & Upload Logic
    if (captureBtn && canvasElement) {
        captureBtn.addEventListener('click', () => {
            const context = canvasElement.getContext('2d');
            canvasElement.width = videoElement.videoWidth;
            canvasElement.height = videoElement.videoHeight;

            // Draw the current video frame to the hidden canvas
            context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

            // Convert to blob and send to backend

            canvasElement.toBlob(blob => {
                const formData = new FormData();
                const selectedLanguage = document.getElementById('languageSelect').value;

                formData.append('image', blob, 'captured_room.jpg');
                formData.append('theme', selectedTheme);
                formData.append('language', selectedLanguage); // Send the selected language

                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.error) {
                            alert("Error: " + data.error);
                        } else if (data.redirect) {
                            // This tells the browser to go to the results page
                            window.location.href = data.redirect;
                        }
                    })
                    .catch(error => {
                        console.error('Upload error:', error);
                        alert("Failed to upload image.");
                    })
                    .finally(() => {
                        captureBtn.textContent = "Capture & Apply Theme";
                        captureBtn.disabled = false;
                    });
            }, 'image/jpeg', 0.9);
        });
    }
});