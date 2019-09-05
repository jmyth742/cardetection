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
camera.framerate = 50
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
    hs = open("xpos.txt","a")
    hs.write(str(kalmanX))
    hs.write("\n")
    hs.close() 
    kalmanX=(kalmanX/2.50)*800
    kalmanY=float(floats[1])
    hs = open("ypos.txt","a")
    hs.write(str(kalmanY))
    hs.write("\n")
    hs.close()
    kalmanY=(kalmanY/2.00)*600
    kalmanT=float(floats[2])
    hs = open("theta.txt","a")
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
    #cv2.circle(image, (int(kalmanY), int(kalmanX)), 1, (255, 0, 255), 2)
    #cv2.imshow("Image", image)
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
    listX = list(range(20))
    map(float, listX)
    listY = list(range(20))
    map(float, listY)
    area = list(range(20))
    map(float, area)
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
        listX[i]=cX
        listY[i]=cY
        area[i]=cv2.contourArea(c)
        shape = sd.detect(c)
        #if shape == 'circle':
         #      print("circle")
        # multiply the contour (x, y)-coordinates by the resize ratio,
        # then draw the contours and the name of the shape on the image
        c = c.astype("float")
        #c *= ratio
        c = c.astype("int")
        cv2.drawContours(image, [c], -1, (0, 255, 0), 1)
        cv2.circle(image, (cX, cY), 1, (255, 255, 255), -1)
        # determine the most extreme points along the contour

        cv2.waitKey(1)
        #print("centre  ",cX,cY)
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
        
         
        
        # show the frame
    #cv2.imshow("Frame", image)
    #print(listX[1],listY[1], listX[2],listY[2])
    #print(area[1],area[2])
    if(area[1] > area[2]):
        #print()
        back = area[1]
        front = area[2]
        fx = listX[2]
        fy = listY[2]
        bx = listX[1]
        by = listY[1]
    elif(area[2]>area[1]):
        back = area[2]
        front = area[1]
        fx = listX[1]
        fy = listY[1]
        bx = listX[2]
        by = listY[2]
        
    cv2.line(image, (bx,by), (fx,fy),(255,255,255), 1)
    midx=(bx+fx)/2
    midy=(by+fy)/2
    opp=0.00
    adj=0.00
    adj=(midx-fx)#abs(midx-fx)
    opp=(midy-fy)#abs(midy-fy)
    #orien=math.degrees(math.atan(opp/adj))
    adj=adj+0.01
    orien=(math.atan2(adj,opp))
    #print(opp)
    #print(adj)
    #print(midx)
    #print (midx*xmp)
    #print(midy)
    #print(midy*ymp)
    print(math.degrees(orien))
    #if (iframe % 5 ==0):
    xpos=midy*ymp
    ypos=midx*xmp
    data = {}
    data['x'] = midy*ymp
    data['y'] = midx*xmp
    data['theta'] = orien
    json_data = json.dumps(data)
    hs = open("camXpos.txt","a")
    hs.write(str(xpos))
    hs.write("\n")
    hs.close()
    hs = open("camYpos.txt","a")
    hs.write(str(ypos))
    hs.write("\n")
    hs.close()
    hs = open("camTheta.txt","a")
    hs.write(str(orien))
    hs.write("\n")
    hs.close()
    ret= client.publish("positions",json_data)
    key = cv2.waitKey(1) & 0xFF
    #print(int(kalmanX), int(kalmanY))
    cv2.circle(image, (int(kalmanY), int(kalmanX)), 1, (255, 0, 255), 2)
    cv2.imshow("Image", image)
    cv2.imwrite("frame{:d}.jpg".format(count), image)  # save frame as JPEG file

    #cv2.imwrite
    # clear the stream in preparation for the next frame
    client.loop_stop()
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break

