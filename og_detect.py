# USAGE
# python detect_shapes.py --image shapes_and_colors.png

# import the necessary packages
from pyimagesearch.shapedetector import ShapeDetector
import argparse
import imutils
import cv2
import numpy as np
import math
# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
	help="path to the input image")
args = vars(ap.parse_args())


















# load the image and resize it to a smaller factor so that
# the shapes can be approximated better
image = cv2.imread(args["image"])
resized = imutils.resize(image, width=300, height=300)
ratio = image.shape[0] / float(resized.shape[0])

# convert the resized image to grayscale, blur it slightly,
# and threshold it
gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (11, 11), 0)
thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]
edged = cv2.Canny(thresh,50,100)
edged = cv2.dilate(edged,None,iterations=1)
edged = cv2.erode(edged,None,iterations=1)
#cv2.imshow("window", edged)
# find contours in the thresholded image and initialize the
# shape detector
#dst = cv2.cornerHarris(gray,5,3,0.04)
#x,y=np.nonzero(dst > 0.01 * dst.max())

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
	#cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
	#	0.5, (255, 255, 255), 2)

	# show the output image
	#image = cv2.resize(image,(800,600))
	xtop=extTop[0]
	ytop=extTop[1]
	#print(xtop)
	cv2.line(image, (extTop), (cX,cY),(255,255,255), 1)
	cv2.imshow("Image", image)
	cv2.waitKey(0)

print("centre  ",cX,cY)
cv2.imshow("Image",image)
adj=xtop-cX
opp=ytop-cY
orien=math.degrees(math.atan(opp/adj))
print(orien)
