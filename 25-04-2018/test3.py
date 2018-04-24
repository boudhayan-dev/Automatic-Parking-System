import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
from google.cloud import vision
from google.cloud.vision import types
import os,sys
from picamera import PiCamera

def openGate1():
	pass

def closeGate1():
	pass

def checkCriminalDatabse(number_plate):
	return False #return true in case the number is in the databse


def capturePlate(filename):
    camera.start_preview()
    time.sleep(1)
    camera.capture(filename)
    camera.stop_preview()

def ocr(filename):
    capturePlate(filename)
    client = vision.ImageAnnotatorClient()
    img = cv2.imread(filename)

    img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
    noise_removal = cv2.bilateralFilter(img_gray,7,85,85)


    ret,thresh_image = cv2.threshold(noise_removal,0,255,cv2.THRESH_OTSU+cv2.THRESH_BINARY)
    equalize= cv2.equalizeHist(thresh_image)

    canny_image = cv2.Canny(equalize,250,255)
    canny_image = cv2.convertScaleAbs(canny_image)

    kernel = np.ones((3,3), np.uint8)
    dilated_image = cv2.dilate(canny_image,kernel,iterations=3)

    new,contours, hierarchy = cv2.findContours(dilated_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours= sorted(contours, key = cv2.contourArea, reverse = True)[:10]

    screenCnt = None
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.06 * peri, True)  
        if len(approx) == 4:  
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

    return labels.text



def openGate2():
	pass

def closeGate2():
	pass



empty_slots=2
car_in_box=0

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'boodi.json'
camera=PiCamera()
camera.resolution=(512,512)
camera.awb_mode="fluorescent"
camera.iso = 800
camera.contrast=25
camera.brightness=50
camera.sharpness=100
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.IN) #GPGPIO 14 -> IR sensor as input
GPIO.setup(18,GPIO.IN)
count=0

print("Total parking slots available ",str(empty_slots))

while True:
    if(GPIO.input(16)==True) and car_in_box==0: #object is far away
        if empty_slots!=0:
            count+=1
            print("Car has arrived -",count)
            openGate1() # open Gate 1 and let the car in if there are empty slots
            time.sleep(2)
            closeGate1()
            car_in_box=1
        else:
            print("Sorry we are out of parking spaces ! Try again in few hours.")
            time.sleep(2)
        
    if(GPIO.input(18)!=True):
        car_in_box=0
        print("Processing number plate")
        filename="image"+str(count)+".jpg"
        text=str(ocr(filename)).strip()# ocr function will return the license plate as text
        if  not  checkCriminalDatabse(text):
            openGate2()
            time.sleep(2)
            closeGate2()
            print("Entry permitted succesfully.")
            empty_slots-=1
            print("Reamaining slots -",str(empty_slots))
        else:
            print("Sorry, this parking lot is only for law abiding citizens !")
            openGate1()
            time.sleep(2)
            closeGate1()
            print("Entry restricted succesfully.")
    elif car_in_box==1:
        print("Please move your car slightly ahead!")
        time.sleep(2)


