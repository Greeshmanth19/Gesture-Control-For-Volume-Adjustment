#############################################################

# IMPORTING LIBRARIES
#############################################################

import cv2
import numpy as np
import mediapipe as mp
import time
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#############################################################

# Initiligations
#############################################################

# Hand detection and hand tarcking
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils

# Volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Frame rate
ptime = 0
ctime = 0

# webcam
wcam, hcam = 640, 480
cam = cv2.VideoCapture(0)
cam.set(3, wcam)
cam.set(4, hcam)

# Points
p1 = (0, 0)
p2 = (0, 0)

# volumes
minlen = 60
maxlen = 300
minvolumerange = -65.0
maxvolumerange = 0.0
volumerange = 0
volbar = 400
#############################################################

# loading each frame from webcam
#############################################################

while True:

    # reading frames in the image
    success, img = cam.read()

    # converting the image to RGB because mediapipe can only handle RGB images
    rgbImg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # storign the processed data in the results
    results = hands.process(rgbImg)
    if results.multi_hand_landmarks:
        for handlms in results.multi_hand_landmarks:

            # drawing the landmarks on the hands using inbuild method in mediapipe name draw_landmarks
            mpDraw.draw_landmarks(img, handlms, mpHands.HAND_CONNECTIONS)

            # getting the landmark of each id form handlms
            for id, lm in  enumerate(handlms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                # highlighting the id 4 and id 8 with a circle
                if id == 4:
                    cv2.circle(img, (cx, cy), 6, (255, 0, 255), -1)
                    p1 = (cx, cy)
                if id == 8:
                    cv2.circle(img, (cx, cy), 6, (255, 0, 255), -1)
                    p2 = (cx, cy)

                # Drawing a line between id 4 and id 8
                cv2.line(img, p1, p2, (255, 0, 255), 5)

                # calculating the distance between the landmarks of id 4 and id 8 using equlidian distance
                distance = np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

                # highlighting the center of the line drawn above
                center = ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2)
                cv2.circle(img, center, 10, (255, 0, 255), -1)

                # Changing the color of the center if id 4(Thumb) and id 8(index finger) meets
                if distance <= 50:
                    cv2.circle(img, center, 10, (0, 255, 0), -1)

                    # seting the volumelevel to 0
                    volume.SetMasterVolumeLevel(-65.0, None)
                else:

                    # calculating the volume level
                    volumerange = np.interp(distance, [minlen, maxlen], [minvolumerange, maxvolumerange])

                    # setting the volume level to the calculated value
                    print("Volume : ", volumerange)
                    volume.SetMasterVolumeLevel(volumerange, None)

                # creating a volume bar on the window

                volbar = np.interp(distance, [50, 300], [400, 150])
                volper = np.interp(distance, [50, 300], [0, 100])
                cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
                cv2.rectangle(img, (50,(int(volbar))), (85, 400), (255, 0, 0), cv2.FILLED)
                cv2.putText(img, f'{int(volper)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)

    # printing the frame rate on the screen
    ctime = time.time()
    fps = int(1/(ctime - ptime))
    ptime = ctime
    text = str(fps)
    cv2.putText(img, text, (10, 50), cv2.FONT_ITALIC, 1, (255, 0, 0), 2)

    # opening a window to show the hands and landmarks
    cv2.imshow("Hand Detectoin", img)

    # exit if clikced q key
    if cv2.waitKey(1) & 0xff == ord("q"):
        break
