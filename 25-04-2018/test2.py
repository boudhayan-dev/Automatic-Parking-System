import cv2
import numpy as np
from google.cloud import vision
from google.cloud.vision import types
import os,sys

filename=sys.argv[1]

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'boodi.json'
client = vision.ImageAnnotatorClient()
# Reading Image
img = cv2.imread(filename)
cv2.namedWindow("Original Image",cv2.WINDOW_NORMAL)
#img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2HSV)
#h,s,img_gray = cv2.split(img_gray)


img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
noise_removal = cv2.bilateralFilter(img_gray,7,85,85)

'''kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
morph_image = cv2.morphologyEx(equalize,cv2.MORPH_OPEN,kernel,iterations=2)

sub_morp_image = cv2.subtract(equalize,noise_removal)'''

ret,thresh_image = cv2.threshold(noise_removal,0,255,cv2.THRESH_OTSU+cv2.THRESH_BINARY)
equalize= cv2.equalizeHist(thresh_image)

canny_image = cv2.Canny(equalize,250,255)
canny_image = cv2.convertScaleAbs(canny_image)

cv2.namedWindow("equalixed",cv2.WINDOW_NORMAL)
cv2.imshow("equalixed",canny_image)

kernel = np.ones((3,3), np.uint8)
dilated_image = cv2.dilate(canny_image,kernel,iterations=3)

new,contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contours= sorted(contours, key = cv2.contourArea, reverse = True)[:10]

screenCnt = None
# loop over our contours
for c in contours:
 # approximate the contour
 peri = cv2.arcLength(c, True)
 approx = cv2.approxPolyDP(c, 0.06 * peri, True)  # Approximating with 6% error
 # if our approximated contour has four points, then
 # we can assume that we have found our screen
 if len(approx) == 4:  # Select the contour with 4 corners
  screenCnt = approx
  break

final = cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)

mask = np.zeros(img_gray.shape,np.uint8)
new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
new_image = cv2.bitwise_and(img,img,mask=mask)

y,cr,cb = cv2.split(cv2.cvtColor(new_image,cv2.COLOR_RGB2YCrCb))
y = cv2.equalizeHist(y)
final_image = cv2.cvtColor(cv2.merge([y,cr,cb]),cv2.COLOR_YCrCb2RGB)

cv2.imwrite("extracted"+filename,final_image)

with open("extracted"+filename, 'rb') as image_file:
	content = image_file.read()
print("Sending Image to OCR . . ")

image = types.Image(content=content)
response = client.document_text_detection(image=image)
labels = response.full_text_annotation

print(labels.text)


cv2.namedWindow("final",cv2.WINDOW_NORMAL)
cv2.imshow('final',new_image)



cv2.namedWindow("extracted",cv2.WINDOW_NORMAL)
cv2.imshow('extracted',new_image)

cv2.imshow("Original Image",img)
cv2.waitKey() 
