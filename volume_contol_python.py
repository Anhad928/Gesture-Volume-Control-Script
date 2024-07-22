import cv2
import mediapipe as mp
import subprocess
import math
import time

# Initialize variables
x1 = y1 = x2 = y2 = 0
webcam = cv2.VideoCapture(0)  # Use the default camera
my_hand = mp.solutions.hands.Hands()
drawing_util = mp.solutions.drawing_utils

# Set the resolution of the webcam feed to a lower value
webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def get_volume():
    volume = subprocess.check_output(["osascript", "-e", "output volume of (get volume settings)"]).strip()
    return int(volume)

def set_volume(volume):
    subprocess.call(["osascript", "-e", f"set volume output volume {volume} --100%"])

def change_volume(direction):
    current_volume = get_volume()
    if direction == 'up' and current_volume < 100:
        set_volume(min(100, current_volume + 5))
    elif direction == 'down' and current_volume > 0:
        set_volume(max(0, current_volume - 5))

while True:
    ret, image = webcam.read()
    if not ret:
        break

    frame_height, frame_width, _ = image.shape

    # Convert the image to RGB
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    output = my_hand.process(rgb_image)
    hands = output.multi_hand_landmarks

    if hands:
        for hand in hands:
            drawing_util.draw_landmarks(image, hand)
            landmarks = hand.landmark

            for id, landmark in enumerate(landmarks):
                x = int(landmark.x * frame_width)
                y = int(landmark.y * frame_height)

                if id == 8:  # Index finger tip
                    cv2.circle(img=image, center=(x, y), radius=8, color=(0, 255, 255), thickness=3)
                    x1 = x
                    y1 = y

                if id == 4:  # Thumb tip
                    cv2.circle(img=image, center=(x, y), radius=8, color=(0, 0, 255), thickness=3)
                    x2 = x
                    y2 = y

            # Calculate the distance between thumb tip and index finger tip
            dist = math.hypot(x2 - x1, y2 - y1)
            cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 5)

            if dist > 50:
                change_volume('up')
            elif dist < 30:
                change_volume('down')

    # Show the image
    cv2.imshow("Hand Volume Control in Python", image)
    
    # Break the loop when 'Escape' key is pressed
    key = cv2.waitKey(10)
    if key == 27:
        break

    # Sleep for a short while to avoid too frequent volume changes
    time.sleep(0.1)

# Release the webcam and close windows
webcam.release()
cv2.destroyAllWindows()