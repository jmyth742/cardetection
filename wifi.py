# USAGE
# python test_video.py

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from pyimagesearch.shapedetector import ShapeDetector

import cv2
import os
import time
import argparse
import imutils
import numpy as np
import math
import paho.mqtt.client as paho
import json
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
#camera.resolution = (640, 480)
camera.resolution = (800, 600)
camera.framerate = 90
#rawCapture = PiRGBArray(camera, size=(640, 480))
rawCapture = PiRGBArray(camera, size=(800, 600))

endPoint = False

broker="192.168.43.112"
client = paho.Client("P1") #create new instance
port=1883


pathOut = "data"

def on_message(client, userdata, message):
    global kalmanX
    global kalmanY
    global kalmanT
    kalman=str(message.payload.decode("utf-8"))
    print(kalman)
    #print("message received " ,str(message.payload.decode("utf-8")))
    floats=map(float, kalman.split(' ',3))
    kalmanX=float(floats[0])
    hs = open("Xrssi.txt","a")
    hs.write(str(kalmanX))
    hs.write("\n")
    hs.close() 
    kalmanX=(kalmanX/2.50)*800
    kalmanY=float(floats[1])
    hs = open("Yrssi.txt","a")
    hs.write(str(kalmanY))
    hs.write("\n")
    hs.close()
    kalmanY=(kalmanY/2.00)*600
    kalmanT=float(floats[2])
    hs = open("tRssi.txt","a")
    hs.write(str(kalmanT))
    hs.write("\n")
    hs.close() 
    
    #print("hello world")
    
def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass

count=0
client.on_publish = on_publish                          #assign function to callback
client.connect(broker,port)                                 #establish connection
client.subscribe("kalman")
client.on_message=on_message

def calculateDistance(x1,y1,x2,y2):
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
     return dist


# allow the camera to warmup
time.sleep(0.1)
def click_and_crop(event, x, y, flags, param):
        # grab references to the global variables
        global refPt
 
        # if the left mouse button was clicked, record the starting
        # (x, y) coordinates and indicate that cropping is being
        # performed
        if event == cv2.EVENT_LBUTTONDOWN:
                endPoint = True
                refPt = [(x, y)]
                print(refPt)
                x=(refPt[0][0])
                y=(refPt[0][1])
                print(x," ",y)


        # check to see if the left mouse button was released
        elif event == cv2.EVENT_LBUTTONUP:
                # record the ending (x, y) coordinates and indicate that
                refPt.append((x, y))
                cv2.circle(image, (x,y), 1, (255, 255, 255), -1)
                cv2.line(image, (x,y), (cX,cY),(255,255,255), 1)
                #cv2.imshow("Image", image)
iframe = 0
kalmanX=0
kalmanY=0
kalmanT=0
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    count=count+1
    pHeight=600
    pWidth=800
    metricH=2.00
    metricW=2.50
    xmp=2.00/pHeight
    ymp=2.50/pWidth
    
    client.loop_start()
    image = frame.array
    iframe+=1
                # show the frame
    #cv2.imshow("Frame", image)
  
    #print(opp)
    #print(adj)
    #print(midx)
    #print (midx*xmp)
    #print(midy)
    #print(midy*y
    cv2.waitKey(1)
    key = cv2.waitKey(1) & 0xFF
    #print(int(kalmanX), int(kalmanY))
    cv2.circle(image, (int(kalmanY), int(kalmanX)), 1, (255, 0, 255), 15)
    cv2.circle(image, (0, 0), 1, (0, 255, 0), 15)
    cv2.circle(image, (800, 0), 1, (0, 255, 0), 15)
    cv2.circle(image, (0, 600), 1, (0, 255, 0), 15)
    cv2.imshow("Image", image)
    cv2.imwrite("rssi-test{:d}.jpg".format(count), image)  # save frame as JPEG file

    #cv2.imwrite
    # clear the stream in preparation for the next frame
    client.loop_stop()
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break


