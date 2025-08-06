import cv2
from cvzone.PoseModule import PoseDetector
from datetime import datetime
import os
import threading
import pyttsx3
from send import sendSmsWithImage, upload_to_cloudinary  # Import helper functions

# Initialize PoseDetector and TTS engine
detector = PoseDetector()
tts_engine = pyttsx3.init()
tts_engine.setProperty("rate", 150)

# Start webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Width
cap.set(4, 480)  # Height

# Create folders if not exist
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

if not os.path.exists("recordings"):
    os.makedirs("recordings")

# Set up video recording
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
video_filename = f"recordings/intruder_recording_{timestamp}.avi"
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec for AVI format
fps = 20
frame_size = (640, 480)
video_writer = cv2.VideoWriter(video_filename, fourcc, fps, frame_size)

# Flags
immediate_screenshot_taken = False
sms_sent = False  

# Function to save and send screenshot
def save_screenshot(image, tag):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"screenshots/{tag}_{timestamp}.jpg"
    cv2.imwrite(filename, image)
    print(f"✅ Screenshot saved: {filename}")

    # Upload to Cloudinary
    image_url = upload_to_cloudinary(filename)

    # Send SMS with image URL
    if image_url:
        sendSmsWithImage(image_url)
    else:
        print("❌ Image upload failed, SMS not sent.")

# Function to start voice alert
def start_voice_alert():
    tts_engine.say("Intruder Detected!")
    tts_engine.runAndWait()

print("Webcam starting...")

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to access the webcam.")
        break

    # Write frame to video file
    video_writer.write(frame)

    processed_frame = detector.findPose(frame, draw=True)
    lmList, bboxInfo = detector.findPosition(processed_frame, bboxWithHands=False, draw=True)

    if bboxInfo:
        x, y, w, h = bboxInfo['bbox']
        print("🚨 Intruder Detected!")

        # Display Alert on screen
        cv2.putText(processed_frame, "Intruder Detected!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Start voice alert
        threading.Thread(target=start_voice_alert, daemon=True).start()

        # Take the first screenshot immediately
        if not immediate_screenshot_taken:
            save_screenshot(frame, "intruder_detected")
            immediate_screenshot_taken = True

        # Send SMS only once per detection
        if not sms_sent:
            save_screenshot(frame, "intruder_detected_center")  # Extra screenshot
            sms_sent = True  

    else:
        immediate_screenshot_taken = False
        sms_sent = False  

    cv2.imshow("Pose Detection", processed_frame)

    key = cv2.waitKey(10) & 0xFF
    if key == ord('q'):
        print("Q pressed. Exiting...")
        break


# Release resources
cap.release()
video_writer.release()  # Save the video file
cv2.destroyAllWindows()
print(f"Video saved: {video_filename}")
print("Webcam stopped.")
