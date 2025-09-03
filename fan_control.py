import cv2
import serial
import time
import mediapipe as mp
import math

# Connect to Arduino (change COM3 if needed) pip install opencv-python
#pip install pyserial
# Open webcam pip install mediapipe

arduino = serial.Serial('COM6', 9600)
time.sleep(2)

# Setup for hand tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)
            lm_list = []
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                lm_list.append((int(lm.x * w), int(lm.y * h)))

            if len(lm_list) >= 9:
                x1, y1 = lm_list[4]  # Thumb tip
                x2, y2 = lm_list[8]  # Index finger tip

                # Draw and calculate
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 2)
                cv2.circle(img, (x1, y1), 5, (0, 255, 0), -1)
                cv2.circle(img, (x2, y2), 5, (0, 255, 0), -1)

                distance = int(math.hypot(x2 - x1, y2 - y1))
                speed = int((distance / 200) * 255)
                speed = min(255, max(0, speed))

                arduino.write(f"{speed}\n".encode())

                cv2.putText(img, f"Speed: {speed}", (10, 70),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("Fan Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
