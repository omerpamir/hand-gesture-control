import math
import numpy as np
import time
from ctypes import cast, POINTER
import pyautogui
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import HandTrackingModule as hTm
import cv2


# Function to put text on the image
def puttext(text_mode, loc=(250, 450), text_color=(0, 255, 255)):
    cv2.putText(img, str(text_mode), loc, cv2.FONT_HERSHEY_COMPLEX_SMALL, 3, text_color, 3)


# Set the width and height of the camera
wCam, hCam = 640, 480
# Initialize the camera
cap = cv2.VideoCapture(0)
# Set the width and height of the camera
cap.set(3, wCam)
cap.set(4, hCam)
# Initialize the time variables for the frame rate
pTime, cTime = 0, 0

# Initialize the hand detector
detector = hTm.handDetector(max_num_hands=1, min_detection_confidence=0.85, min_tracking_confidence=0.8)

# Get the audio devices
devices = AudioUtilities.GetSpeakers()
# Activate the audio interface
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
# Get the volume control and the volume range
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()

# Initialize the volume variables
minVol = -50
maxVol = volRange[1]
print(volRange)
# Initialize the volume bar and volume percentage
volBar = 400
volPer = 0
# Initialize the volume and color
vol = 0
color = (0, 215, 255)
# Set the minimum and maximum height
hmin = 50
hmax = 200

# Set the fingertip IDs
tipIds = [4, 8, 12, 16, 20]
# Initialize the mode and active variables
mode = ''
active = 0

# Set the failsafe to false for pyautogui to not stop the program
pyautogui.FAILSAFE = False

# Start the main loop
while True:
    # Read the image from the camera and flip it
    success, img = cap.read()
    img = cv2.flip(img, 1)
    # Find the hands in the image and get the landmarks
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    fingers = []

    # If there are hands in the image
    if len(lmList) != 0:
        # Check the thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0 - 1]][1]:
            if lmList[tipIds[0]][1] >= lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
        elif lmList[tipIds[0]][1] < lmList[tipIds[0 - 1]][1]:
            if lmList[tipIds[0]][1] <= lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)

        # Check the other fingers
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        # Check the mode
        if (fingers == [0, 0, 0, 0, 0]) & (active == 0):
            mode = 'N'
        elif (fingers == [0, 1, 0, 0, 0] or fingers == [0, 1, 1, 0, 0]) & (active == 0):
            mode = 'Scroll'
            active = 1
        elif (fingers == [1, 1, 0, 0, 0]) & (active == 0):
            mode = 'Volume'
            active = 1
        elif (fingers == [1, 1, 1, 1, 1]) & (active == 0):
            mode = 'Cursor'
            active = 1

    # If the mode is Scroll
    if mode == 'Scroll':
        active = 1
        puttext(mode)
        cv2.rectangle(img, (200, 410), (245, 460), (255, 255, 255), cv2.FILLED)
        if len(lmList) != 0:
            if fingers == [0, 1, 0, 0, 0]:
                puttext(text_mode='U', loc=(200, 455), text_color=(0, 255, 0))
                pyautogui.scroll(300)

            if fingers == [0, 1, 1, 0, 0]:
                puttext(text_mode='D', loc=(200, 455), text_color=(0, 0, 255))
                pyautogui.scroll(-300)
            elif fingers == [0, 0, 0, 0, 0]:
                active = 0
                mode = 'N'
    # If the mode is Volume
    if mode == 'Volume':
        active = 1
        puttext(mode)
        if len(lmList) != 0:
            if fingers[-1] == 1:
                active = 0
                mode = 'N'
                print(mode)

            else:
                # Calculate the distance between the thumb and the index finger and adjust the volume
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]
                x3, y3 = lmList[0][1], lmList[0][2]
                x4, y4 = lmList[5][1], lmList[5][2]
                measured_distance = math.hypot(x4 - x3, y4 - y3)
                scale_factor = 100 / measured_distance
                temp_x1, temp_y1 = int(x1 * scale_factor), int(y1 * scale_factor)
                temp_x2, temp_y2 = int(x2 * scale_factor), int(y2 * scale_factor)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                # Draw the volume control and the volume percentage
                cv2.circle(img, (x1, y1), 10, color, cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, color, cv2.FILLED)
                cv2.line(img, (x1, y1), (x2, y2), color, 3)
                cv2.circle(img, (cx, cy), 8, color, cv2.FILLED)

                length = math.hypot(temp_x2 - temp_x1, temp_y2 - temp_y1)
                vol = np.interp(length, [hmin, hmax], [minVol, maxVol])
                volBar = np.interp(vol, [minVol, maxVol], [400, 150])
                volPer = np.interp(vol, [minVol, maxVol], [0, 100])
                print(vol)
                print(maxVol)
                print(length)

                volN = int(vol)
                if volN % 4 != 0:
                    volN = volN - volN % 4
                    if volN >= 0:
                        volN = 0
                    elif volN <= -64:
                        volN = -64
                    elif vol >= -11:
                        volN = vol

                volume.SetMasterVolumeLevel(vol, None)
                if length < 50:
                    cv2.circle(img, (cx, cy), 11, (0, 0, 255), cv2.FILLED)

                # Draw the volume bar
                cv2.rectangle(img, (30, 150), (55, 400), (209, 206, 0), 3)
                cv2.rectangle(img, (30, int(volBar)), (55, 400), (215, 255, 127), cv2.FILLED)
                cv2.putText(img, f'{int(volPer)}%', (25, 430), cv2.FONT_HERSHEY_COMPLEX, 0.9, (209, 206, 0), 3)

    # If the mode is Cursor
    if mode == 'Cursor':
        active = 1
        puttext(mode)
        cv2.rectangle(img, (110, 20), (620, 350), (255, 255, 255), 3)

        if fingers[1:] == [0, 0, 0, 0]:  # thumb excluded
            active = 0
            mode = 'N'
            print(mode)
        else:
            if len(lmList) != 0:
                # Move the cursor
                x1, y1 = lmList[8][1], lmList[8][2]
                w, h = pyautogui.size()
                X = int(np.interp(x1, [110, 620], [0, w - 1]))
                Y = int(np.interp(y1, [20, 350], [0, h - 1]))
                cv2.circle(img, (lmList[8][1], lmList[8][2]), 7, (255, 255, 255), cv2.FILLED)
                cv2.circle(img, (lmList[4][1], lmList[4][2]), 10, (0, 255, 0), cv2.FILLED)  # thumb

                if X % 2 != 0:
                    X = X - X % 2
                if Y % 2 != 0:
                    Y = Y - Y % 2
                print(X, Y)
                pyautogui.moveTo(X, Y, _pause=False)
                if fingers[0] == 0:
                    cv2.circle(img, (lmList[4][1], lmList[4][2]), 10, (0, 0, 255), cv2.FILLED)  # thumb
                    pyautogui.click(interval=0.5)

    # Calculate the FPS
    cTime = time.time()
    fps = 1 / ((cTime + 0.01) - pTime)
    pTime = cTime

    # Display the FPS
    cv2.putText(img, f'FPS:{int(fps)}', (480, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)
    cv2.imshow('Hand Cam', img)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
