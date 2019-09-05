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
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (800, 600)
camera.framerate = 20
rawCapture = PiRGBArray(camera, size=(800, 600))
endPoint = False

broker="192.168.43.112"
client = paho.Client("P1") #create new instance
port=1883
def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass

client.on_publish = on_publish                          #assign function to callback
client.connect(broker,port)                                 #establish connection
ret= client.publish("house","on")

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
   
#    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#    blurred = cv2.GaussianBlur(gray, (13, 13), 0)
#    thresh = cv2.threshold(blurred, 50, 255, cv2.THRESH_BINARY)[1]
#    edged = cv2.Canny(thresh,100,200)
#    edged = cv2.dilate(edged,None,iterations=1)
#    edged = cv2.erode(edged,None,iterations=1)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (9, 9), 0)
     
    # perform edge detection, then perform a dilation + erosion to
    # close gaps in between object edges
    edged = cv2.Canny(gray, 10, 160)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

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
        ext4 = tuple(c[c[:, :, 0].argmax()][0])
        ext2 = tuple(c[c[:, :, 1].argmin()][0])
        ext3 = tuple(c[c[:, :, 1].argmax()][0])
        #print(extLeft, extTop, extBot)
        x2=ext2[0]
        y2=ext2[1]
        x3=ext3[0]
        y3=ext3[1]
        x1=ext1[0]
        y1=ext1[1]
        x4=ext4[0]
        y4=ext4[1]
        print (ext1)
        print(ext2)
        print(ext3)
        print(ext4)
        #extright and top
        print ("dist1", calculateDistance(cX,cY, x1, y1))
        dist1 = calculateDistance(cX,cY, x1, y1)
        print ("dist2",calculateDistance(cX,cY, x2, y2))
        dist2 = calculateDistance(cX,cY, x2, y2)
        print("dist3",calculateDistance(cX,cY, x3, y3))
        dist3 = calculateDistance(cX,cY, x3, y3)
        dist4 = ("dist4",calculateDistance(cX,cY, x4, y4))
        print(dist4)
        p2p1 = calculateDistance(x1,y1, x2, y2)
        p2p2 = calculateDistance(x2,y2, x3, y3)
        p2p3 = calculateDistance(x3,y3, x4, y4)
        p2p4 = calculateDistance(x4,y4, x1, y1)
        if(p2p1<p2p2 and p2p1<p2p3 and p2p1<p2p4):
            shortest=p2p1
            print("p2p1 shortest")
            cv2.line(image, (x1,y1), (cX,cY),(255,255,255), 1)
        elif(p2p2<p2p1 and p2p2<p2p3 and p2p2<p2p4):
            shortest=p2p2
            print("p2p2 shortest")
            cv2.line(image, (x2,y2), (cX,cY),(255,255,255), 1)
        elif(p2p3<p2p2 and p2p3<p2p2 and p2p3<p2p4):
            shortest=p2p3
            print("p2p3 shortest")
            cv2.line(image, (x3,y3), (cX,cY),(255,255,255), 1)
        elif(p2p4<p2p2 and p2p4<p2p3 and p2p4<p2p1):
            shortest=p2p4
            print("p2p4 shortest")
            cv2.line(image, (x4,y4), (cX,cY),(255,255,255), 1)
        
        #bool short
        if(dist1>dist2 and dist1>dist3 and dist1>dist4):
            fx=x1
            fy=y1
            print("longest distance dist1")
        elif(dist2>dist1 and dist2>dist3 and dist2>dist4):
            fx=x2
            fy=y2
            print("longest distance dist2")
        elif(dist3>dist2 and dist3>dist1 and dist3>dist4):
            fx=x3
            fy=y3
            print("longest distance dist3")
        elif(dist4>dist2 and dist4>dist3 and dist4>dist1):
            fx=x4
            fy=y4
            print("longest distance dist4")
#        if(dist2 < dist1) and (dist2 < dist3):# and dist2 > 20:
#            fx = (x1+x2)/2
#            fy = (y1+y2)/2
#            print("dist 2 is shortest")
#        elif(dist1 < dist2) and (dist1 < dist3):# and dist1 > 20:
#            fx = (x3+x2)/2
#            fy = (y3+y2)/2
#            print("dist 1 is shortest")
#        elif(dist3 < dist1) and (dist3 < dist2):# and dist3 > 20:# and (dist3 > 15):
#            #if(dist3>15):
#            fx = x3#(x1+x3)/2
#            fy = y3#(y1+y3)/2
#            print("dist 3 is shortest")
#        elif(dist4 < dist3 and dist4 < dist1):# and dist4 > 20:
#            fx = (x4+x3)/2
#            fy = (y4+y3)/2
##            print("dist 4 is shortest")                   
#        print(fx,fy)
#        print(ext1)
#        print(ext2)
#        print(ext3)
#        print(ext4)
        cv2.line(image, (fx,fy), (cX,cY),(255,255,255), 1)
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
        #cv2.line(image, (fx,fy), (cX,cY),(255,255,255), 1)
        #cv2.waitKey(10)
        #cv2.imwrite(image)
        cv2.waitKey(1)
        print("centre  ",cX,cY)
        #cv2.imshow("Image",image)
        #adj=fx-cX
        #opp=fy-cY
        #orien=math.degrees(math.atan(opp/adj))
        cv2.setMouseCallback("Image", click_and_crop)
        #if(endPoint==True):
        #cv2.circle(image, (refPt[0][0],refPt[0][1]), 1, (255, 255, 255), -1)
        #cv2.line(image, (refPt[0][0],refPt[0][1]), (cX,cY),(255,255,255), 1)
        #print(orien)
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
