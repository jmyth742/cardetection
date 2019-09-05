# USAGE
# python test_video.py

# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
from pyimagesearch.shapedetector import ShapeDetector
from random import randint
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
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
endPoint = False

broker="192.168.43.112"
client = paho.Client("P1") #create new instance
port=1883
def on_publish(client,userdata,result):             #create function for callback
    print("data published \n")
    pass

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



client.on_publish = on_publish                          #assign function to callback
client.connect(broker,port)                                 #establish connection
#client.subscribe("kalman")
#client.on_message=on_message                        #assign function to callback



def calculateDistance(x1,y1,x2,y2):
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
     return dist

kalmanX=0
kalmanY=0
kalmanT=0
kalmanX1=0
kalmanY1=0
kalmanT1=0
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
count = 0
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image, then initialize the timestamp
    # and occupied/unoccupied text
    image = frame.array
    iframe+=1
    count=count+1
    pHeight=600
    pWidth=800
    metricH=2.00
    metricW=2.50
    xmp=2.00/pHeight
    ymp=2.50/pWidth
    client.loop_start()
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
    listY = list(range(20))
    ciX = list(range(20))
    ciY = list(range(20))
    sqX = list(range(20))
    sqY = list(range(20))
    area = list(range(20))
    # loop over the contours
    for c in cnts:
        i+=1
        # compute the center of the contour, then detect the name of the
        # shape using only the contour
        M = cv2.moments(c)
        
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
        
#        if shape == 'circle':
#            print("circle")
#            ciX[i]=cX
#            ciY[i]=cY
#        elif shape == 'sqaure' or 'rectangle':
#            print("square")
#            sqX[i]=cX
#            sqY[i]=cY
            
        # multiply the contour (x, y)-coordinates by the resize ratio,
        # then draw the contours and the name of the shape on the image
        c = c.astype("float")
        #c *= ratio
        c = c.astype("int")
        cv2.drawContours(image, [c], -1, (0, 255, 0), 1)
        cv2.circle(image, (cX, cY), 1, (255, 255, 255), -1)
        
        cv2.waitKey(1)
        cv2.setMouseCallback("Image", click_and_crop)
        
         
    bot = list(range(7))    
        # show the frame
    bot[1] = area[1]+area[2]
    bot1 = bot[1]
    bot[2] = area[1]+area[3]
    bot2=bot[2]
    bot[3] = area[1]+area[4]
    bot3=bot[3]
    bot[4] = area[2]+area[3]
    bot4=bot[4]
    bot[5] = area[2]+area[4]
    bot5=bot[5]
    bot[6] = area[3]+area[4]
    bot6=bot[6]
    bot.sort()
    robot1=bot[5]

    print(robot1)
    robot2=bot[2]
    print(robot2)

    if(robot1==bot1):
        print("area 1 and 2 are big robot")
        if(area[1] > area[2]):
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
    elif(robot1==bot2):
        print("area 1 and 3 are big robot")
        if(area[1] > area[3]):
            back = area[1]
            front = area[3]
            fx = listX[3]
            fy = listY[3]
            bx = listX[1]
            by = listY[1]
        elif(area[3]>area[1]):
            back = area[3]
            front = area[1]
            fx = listX[1]
            fy = listY[1]
            bx = listX[3]
            by = listY[3]
    elif(robot1==bot3):
        print("area 1 and 4 are big robot")
        if(area[1] > area[4]):
            print()
            back = area[1]
            front = area[4]
            fx = listX[4]
            fy = listY[4]
            bx = listX[1]
            by = listY[1]
        elif(area[4]>area[1]):
            back = area[4]
            front = area[1]
            fx = listX[1]
            fy = listY[1]
            bx = listX[4]
            by = listY[4]
    elif(robot1==bot4):
        print("area 2 and 3 are big robot")
        if(area[3] > area[2]):
            back = area[3]
            front = area[2]
            fx = listX[2]
            fy = listY[2]
            bx = listX[3]
            by = listY[3]
        elif(area[2]>area[3]):
            back = area[2]
            front = area[3]
            fx = listX[3]
            fy = listY[3]
            bx = listX[2]
            by = listY[2]
    elif(robot1==bot5):
        print("area 2 and 4 are big robot")
        if(area[4] > area[2]):
            back = area[4]
            front = area[2]
            fx = listX[2]
            fy = listY[2]
            bx = listX[4]
            by = listY[4]
        elif(area[2]>area[4]):
            back = area[2]
            front = area[4]
            fx = listX[4]
            fy = listY[4]
            bx = listX[2]
            by = listY[2]
    elif(robot1==bot6):
        print("area 3 and 4 are big robot")
        if(area[3] > area[4]):
            back = area[3]
            front = area[4]
            fx = listX[4]
            fy = listY[4]
            bx = listX[3]
            by = listY[3]
        elif(area[4]>area[3]):
            back = area[4]
            front = area[3]
            fx = listX[3]
            fy = listY[3]
            bx = listX[4]
            by = listY[4]

##for robot 2 now

    if(robot2==bot1):
        print("area 1 and 2 are wee robot")
        if(area[1] > area[2]):
            back1 = area[1]
            front1 = area[2]
            fx1 = listX[2]
            fy1 = listY[2]
            bx1 = listX[1]
            by1 = listY[1]
        elif(area[2]>area[1]):
            back1 = area[2]
            front1 = area[1]
            fx1 = listX[1]
            fy1 = listY[1]
            bx1 = listX[2]
            by1 = listY[2]
    elif(robot2==bot2):
        print("area 1 and 3 are wee robot")
        if(area[1] > area[3]):
            back1 = area[1]
            front1 = area[3]
            fx1 = listX[3]
            fy1 = listY[3]
            bx1 = listX[1]
            by1 = listY[1]
        elif(area[3]>area[1]):
            back1 = area[3]
            front1 = area[1]
            fx1 = listX[1]
            fy1 = listY[1]
            bx1 = listX[3]
            by1 = listY[3]
    elif(robot2==bot3):
        print("area 1 and 4 are wee robot")
        if(area[1] > area[4]):
            print()
            back1 = area[1]
            front1 = area[4]
            fx1 = listX[4]
            fy1 = listY[4]
            bx1 = listX[1]
            by1 = listY[1]
        elif(area[4]>area[1]):
            back1 = area[4]
            front1 = area[1]
            fx1 = listX[1]
            fy1 = listY[1]
            bx1 = listX[4]
            by1 = listY[4]
    elif(robot2==bot4):
        print("area 2 and 3 are wee robot")
        if(area[3] > area[2]):
            back1 = area[3]
            front1 = area[2]
            fx1 = listX[2]
            fy1 = listY[2]
            bx1 = listX[3]
            by1 = listY[3]
        elif(area[2]>area[3]):
            back1 = area[2]
            front1 = area[3]
            fx1 = listX[3]
            fy1 = listY[3]
            bx1 = listX[2]
            by1 = listY[2]
    elif(robot2==bot5):
        print("area 2 and 4 are wee robot")
        if(area[4] > area[2]):
            back1 = area[4]
            front1 = area[2]
            fx1 = listX[2]
            fy1 = listY[2]
            bx1 = listX[4]
            by1 = listY[4]
        elif(area[2]>area[4]):
            back1 = area[2]
            front1 = area[4]
            fx1 = listX[4]
            fy1 = listY[4]
            bx1 = listX[2]
            by1 = listY[2]
    elif(robot2==bot6):
        print("area 3 and 4 are wee robot")
        if(area[3] > area[4]):
            back1 = area[3]
            front1 = area[4]
            fx1 = listX[4]
            fy1 = listY[4]
            bx1 = listX[3]
            by1 = listY[3]
        elif(area[4]>area[3]):
            back1 = area[4]
            front1 = area[3]
            fx1 = listX[3]
            fy1 = listY[3]
            bx1 = listX[4]
            by1 = listY[4]


    cv2.line(image, (bx1,by1), (fx1,fy1),(255,0,255), 1)
    cv2.line(image, (bx,by), (fx,fy),(255,255,255), 1)
    midx=(bx+fx)/2
    midy=(by+fy)/2
    adj=(midx-fx)#abs(midx-fx)
    opp=(midy-fy)#abs(midy-fy)
    #orien=math.degrees(math.atan(opp/adj))
    adj=adj+1
    orien=(math.atan(opp/adj))
    
    midx1=(bx1+fx1)/2
    midy1=(by1+fy1)/2
    print("midx ", midx1)
    print("midy ", midy1)
    cv2.circle(image, (int(midx1+randint(0,5)), int(midy1+randint(0,5))), 1, (0, 0, 255), 2)
    cv2.circle(image, (int(midx+randint(0,5)), int(midy+randint(0,5))), 1, (255, 0, 255), 2)
    adj1=(midx1-fx1)#abs(midx-fx)
    opp1=(midy1-fy1)#abs(midy-fy)
    orien=math.degrees(math.atan(opp/adj))
    adj1=adj+1
    opp1=opp1+1
    orien1=(math.atan(opp1/adj1))
    print(math.degrees(orien1))
    xpos=midy*ymp
    ypos=midx*xmp
    xpos1=midy1*ymp
    ypos1=midx1*xmp
    data = {}
    data['x'] = midy*ymp
    data['y'] = midx*xmp
    data['theta'] = orien
    json_data = json.dumps(data)
    ret= client.publish("positions",json_data)
    
    data1 = {}
    data1['x'] = midy1*ymp
    data1['y'] = midx1*xmp
    data1['theta'] = orien1
    json_data = json.dumps(data1)
    ret= client.publish("positions1",json_data)
    
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
    
    
    hs = open("camXpos1.txt","a")
    hs.write(str(xpos1))
    hs.write("\n")
    hs.close()
    hs = open("camYpos1.txt","a")
    hs.write(str(ypos1))
    hs.write("\n")
    hs.close()
    hs = open("camTheta1.txt","a")
    hs.write(str(orien1))
    hs.write("\n")
    hs.close()
    
    key = cv2.waitKey(1) & 0xFF
    # clear the stream in preparation for the next frame    
    cv2.imwrite("frame{:d}.jpg".format(count), image)  # save frame as JPEG file
    cv2.imshow("Image", image)
    client.loop_stop()
    rawCapture.truncate(0)

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break


