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
endPoint = False

x=0
y=0

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
        ext1 = tuple(c[c[:, :, 0].argmin()][0])
        #extRight = tuple(c[c[:, :, 0].argmax()][0])
        ext2 = tuple(c[c[:, :, 1].argmin()][0])
        ext3 = tuple(c[c[:, :, 1].argmax()][0])
        #print(extLeft, extTop, extBot)
        x2=ext2[0]
        y2=ext2[1]
        x3=ext3[0]
        y3=ext3[1]
        x1=ext1[0]
        y1=ext1[1]
        print calculateDistance(x2, y2, x3, y3)
        dist1 = calculateDistance(x2, y2, x3, y3)
        #dist1 compares x2 and x3
        print calculateDistance(x2, y2, x1, y1)
        dist2 = calculateDistance(x2, y2, x1, y1)
        #dist2 compares x2 and x1
        print calculateDistance(x3, y3, x1, y1)
        dist3 = calculateDistance(x3, y3, x1, y1)
        #dist3 compares x1 and x3
        if((dist2 > dist1) and (dist3 > dist1)):
            fx = x1
            print("1st")
            fy = y1
        elif((dist1 > dist2) and (dist3 > dist2)):
            fx = x1
            print("2nd")
            fy = y1
        elif((dist1 > dist3) and (dist2 > dist3)):
            fx = x2
            print("3rd")
            fy = y2
            
        print(fx,fy)
        ##lets work out which way is forward.
        ##the points with the greates difference in x and y coords is forward.
        #posible combos.ybot-yleft
#        ax = xtop-xbot
#        ay = ytop-ybot
#        bx = xtop-xleft
#        by = ytop-yleft
#        cx = xbot-xleft
#        cy = ybot-yleft
        #if()
        #print(xtop-xbot,ytop-ybot)
        #print(xtop-xleft,ytop-yleft)
        #print(xbot-xleft,ybot-yleft)
        cv2.line(image, (fx,fy), (cX,cY),(255,255,255), 1)
        #cv2.waitKey(10)
        #cv2.imwrite(image)
        cv2.waitKey(1)
        print("centre  ",cX,cY)
        #cv2.imshow("Image",image)
        adj=fx-cX
        opp=fy-cY
        orien=math.degrees(math.atan(opp/adj))
        cv2.setMouseCallback("Image", click_and_crop)
        #if(endPoint==True):
        #cv2.circle(image, (refPt[0][0],refPt[0][1]), 1, (255, 255, 255), -1)
        #cv2.line(image, (refPt[0][0],refPt[0][1]), (cX,cY),(255,255,255), 1)
        print(orien)
        #print("x is ",x,"Y is ",y)
        cv2.imshow("Image", image) 
        
        # show the frame
    #cv2.imshow("Frame", image)
    key = cv2.waitKey(1) & 0xFF

    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

