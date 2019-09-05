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

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))

# allow the camera to warmup
time.sleep(0.1)

# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array    
    #image=cv2.imread('data/frame{:d}.jpg'.format(count))
    #image = cv2.imread(image)
    #resized = imutils.resize(image, width=300, height=300)
    #ratio = image.shape[0] #/ float(resized.shape[0])
    #kernel = np.ones((5,5),np.float32)/25
    #dst = cv2.filter2D(image,-1,kernel)
    #cv2.imshow('kernel', dst)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #cv2.imshow('gray', gray)
    blurred = cv2.GaussianBlur(gray, (13, 13), 0)
    thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)[1]
    edged = cv2.Canny(thresh,100,200)
    edged = cv2.dilate(edged,None,iterations=1)
    edged = cv2.erode(edged,None,iterations=1)
    #cv2.imshow("window", edged)
    #cv2.waitKey(1)
    # find contours in the thresholded image and initialize the
    # shape detector
    #dst = cv2.cornerHarris(thresh,5,3,0.04)
    #x,y=np.nonzero(dst > 0.01 * dst.max())
    #v2.waitKey(0)
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
         cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    sd = ShapeDetector()
    i = 0
    # loop over the contours
    for c in cnts:
        i+=1
        # compute the center of the contour, then detect the name of the
        # shape using only the contour
        M = cv2.moments(c)
        #cv2.imshow("Image", image)
        #cv2.waitKey(0)
        #if (int(M["m10"] == 0)):
        #    break
        if (int(M["m00"] == 0)):
             break
        #if (int(M["m01"] == 0)):
        #    break
        cX = int((M["m10"] / M["m00"]) )
        cY = int((M["m01"] / M["m00"]) )
        #print(cX,cY)
        shape = sd.detect(c)
        # multiply the contour (x, y)-coordinates by the resize ratio,
        # then draw the contours and the name of the shape on the image
        c = c.astype("float")
        #c *= ratio
        c = c.astype("int")
        cv2.drawContours(image, [c], -1, (0, 255, 0), 1)
        cv2.circle(image, (cX, cY), 1, (255, 255, 255), -1)
        # determine the most extreme points along the contour
        extLeft = tuple(c[c[:, :, 0].argmin()][0])
        #extRight = tuple(c[c[:, :, 0].argmax()][0])
        extTop = tuple(c[c[:, :, 1].argmin()][0])
        extBot = tuple(c[c[:, :, 1].argmax()][0])
        print(extLeft, extTop, extBot)
        xtop=extTop[0]
        ytop=extTop[1]
        cv2.line(thresh, (extTop), (cX,cY),(255,255,255), 1)
        cv2.imshow("Image", image)
        cv2.waitKey(1)
        #print("centre  ",cX,cY)
        #cv2.imshow("Image",image)
        #adj=xtop-cX
        #opp=ytop-cY
        #orien=math.degrees(math.atan(opp/adj))
        #cv2.setMouseCallback("Image", click_and_crop)
        #print(orien)
        #count += 1
        
        # show the frame
    #cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
