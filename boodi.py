import cv2
import numpy as np

# Reading Image
img = cv2.imread("13.png")
cv2.namedWindow("Original Image",cv2.WINDOW_NORMAL)
cv2.imshow("Original Image",img)

img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY) # gray  convert maadidene

noise_removal = cv2.bilateralFilter(img_gray,9,75,75) # blur maadidene


equal_histogram = cv2.equalizeHist(noise_removal) # equalize the histogram for easing canny edge detection later

# dilate and erode
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
morph_image = cv2.morphologyEx(equal_histogram,cv2.MORPH_OPEN,kernel,iterations=15)

# Image subtraction(Subtracting the Morphed image from the histogram equalised Image)
sub_morp_image = cv2.subtract(equal_histogram,morph_image)


ret,thresh_image = cv2.threshold(sub_morp_image,0,255,cv2.THRESH_OTSU)

# Applying Canny Edge detection
canny_image = cv2.Canny(thresh_image,250,255)
canny_image = cv2.convertScaleAbs(canny_image)


kernel = np.ones((3,3), np.uint8)
dilated_image = cv2.dilate(canny_image,kernel,iterations=1)

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
#cv2.namedWindow("Final_image",cv2.WINDOW_NORMAL)
#cv2.imshow("Final_image",new_image)


y,cr,cb = cv2.split(cv2.cvtColor(new_image,cv2.COLOR_RGB2YCrCb))
y = cv2.equalizeHist(y)
# Applying histogram equalisation
final_image = cv2.cvtColor(cv2.merge([y,cr,cb]),cv2.COLOR_YCrCb2RGB)
# Merging the 3 channels
cv2.namedWindow("Enhanced Number Plate",cv2.WINDOW_NORMAL)
# Creating a Named window to display image
cv2.imshow("Enhanced Number Plate",final_image)
# Display image
cv2.waitKey() # Wait for a keystroke from the user
