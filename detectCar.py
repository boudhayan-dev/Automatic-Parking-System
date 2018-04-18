import cv2

c=cv2.imread('10.png')
cap=cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
blur = cv2.blur(cap,(5,5))
#ret,thresh1 = cv2.threshold(blur,200,255,cv2.THRESH_BINARY)

th3 = cv2.adaptiveThreshold(blur,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)

cv2.imshow('number plate',th3)
cv2.imshow('number plate original',c)

cv2.waitKey(0)
