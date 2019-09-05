from pyimagesearch.shapedetector import ShapeDetector

import cv2
import os
import time

import argparse
import imutils
import numpy as np
import math


def localiseRobot(image):
    image = cv2.imread(image)
    resized = imutils.resize(image, width=300, height=300)
    ratio = image.shape[0] / float(resized.shape[0])

    ##lower and upper bounds for the shape colors
    #   R: 176 G: 62 B: 84      R: 148 G: 50 B: 72
    #   R: 186 G: 140 B: 171
    #lower1 = np.array([148,50,72])
    #upper1 = np.array([185,150,183])
    #   R: 158 G: 79 B: 116
    # convert the resized image to grayscale, blur it slightly,
    # and threshold it
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (13, 13), 0)
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
    edged = cv2.Canny(thresh,50,100)
    edged = cv2.dilate(edged,None,iterations=1)
    edged = cv2.erode(edged,None,iterations=1)
    #cv2.imshow("window", edged)
    # find contours in the thresholded image and initialize the
    # shape detector
    #dst = cv2.cornerHarris(gray,5,3,0.04)
    #x,y=np.nonzero(dst > 0.01 * dst.max())
    #cv2.waitKey(0)
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
        cX = int((M["m10"] / M["m00"]) * ratio)
        cY = int((M["m01"] / M["m00"]) * ratio)
        #print(cX,cY)
        shape = sd.detect(c)
        # multiply the contour (x, y)-coordinates by the resize ratio,
        # then draw the contours and the name of the shape on the image
        c = c.astype("float")
        c *= ratio
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
        cv2.line(edged, (extTop), (cX,cY),(255,255,255), 1)
        cv2.imshow("Image", image)

    print("centre  ",cX,cY)
    cv2.imshow("Image",image)
    adj=xtop-cX
    opp=ytop-cY
    orien=math.degrees(math.atan(opp/adj))
    #cv2.setMouseCallback("Image", click_and_crop)
    print(orien)



def extractFrames(pathIn, pathOut):
    os.mkdir(pathOut)
 
    cap = cv2.VideoCapture(pathIn)
    count = 0
 
    while (cap.isOpened()):
 
        # Capture frame-by-frame
        ret, frame = cap.read()
 
        if ret == True:
            print('Read %d frame: ' % count, ret)
            cv2.imwrite(os.path.join(pathOut, "frame{:d}.jpg".format(count)), frame)  # save frame as JPEG file
            #time.sleep(1)
            img=cv2.imread('data/frame{:d}.jpg'.format(count))
            cv2.imshow('image',img)
            #localiseRobot(img)
            #img=cv2.imread('data/frame0.jpg')
            #cv2.imshow('ImageWindow',img)
            #cv2.waitKey(1)
            count += 1
        else:
            break
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()
 
def main():
    extractFrames('bot2.mp4', 'data')
 
if __name__=="__main__":
    main()

