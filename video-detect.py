from pyimagesearch.shapedetector import ShapeDetector
from picamera.array import PiRGBArray
from picamera import PiCamera

import cv2
import os
import time

import argparse
import imutils
import numpy as np
import math


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
            image=cv2.imread('data/frame{:d}.jpg'.format(count))
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
            cv2.imshow("window", edged)
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
            count += 1
        else:
            break
    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()



def extractFrames2(pathIn, pathOut):
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
            localiseRobot(img)
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
    extractFrames('pivideo.mp4', 'data')
 
if __name__=="__main__":
    main()

