import cv2
import numpy as np
from djitellopy import tello

me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()
me.takeoff()


fbRage = [6200, 6800]
pid = [0.4, 0.4, 0]
pError = 0
w, h = 360, 240


def findface(img):
    faceCascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    myFaceListC = []
    MyFacelistArea = []

    for (x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (0,0,255), 2)
        cx = x+ w // 2
        cy = y + h // 2
        area = w * h
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        myFaceListC.append([cx, cy])
        MyFacelistArea.append(area)
    if len(MyFacelistArea) != 0:
        i = MyFacelistArea.index(max(MyFacelistArea))
        return img, [myFaceListC[i], MyFacelistArea[i]]
    else:
        return img, [[0,0], 0]

def trackface(me, info, w, pid, pError):
    area = info[1]
    x,y = info[0]
    fb = 0
    error = x - w//2
    speed = pid[0] * error + pid[1]* (error - pError)
    speed = int(np.clip(speed, -100, 100))

    if area > fbRage[0] and area < fbRage[1]:
        fb = 0
    elif area > fbRage[1]:
        fb = -20
    elif area < fbRage[0] and area !=0:
        fb = 20

    if x == 0:
        speed = 0
        error = 0
    me.send_rc_control(0, fb, 0, speed)
    return error

while True:
    img  = me.get_frame_read().frame
    img = cv2.resize(img, (w, h))
    img, info = findface(img)
    eError = trackface(me, info, w, pid, pError)
    print("Area", info[1])
    print("Center")
    cv2.imshow("output", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break
