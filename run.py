'''
The following dependencies are imported.

google.cloud ---> provides support for OCR.
cv2 ---> Image Processing.
'''

import RPi.GPIO as GPIO
import numpy as np
from google.cloud import vision
from google.cloud.vision import types
import os,sys,logging,time,cv2,requests,Adafruit_PCA9685
from picamera import PiCamera

# Google Vision OCR Json file settings
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'GCP_SERVICE_ACCOUNT_CREDENTIALS.json'

#Camera settings
camera=PiCamera()
camera.resolution=(512,512)
camera.awb_mode="fluorescent"
camera.iso = 800
camera.contrast=25
camera.brightness=50
camera.sharpness=100

#Ir sensor settings
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.IN) # Bigger IR to pin 16 and it is exit control sensor. Use OUT1 pin only. DO NOT use OUT2 pin.
GPIO.setup(18,GPIO.IN) # Smaller IR to pin 18 and it is entry control sensor.

#PCA9685 settings
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

#creating logging file
logging.basicConfig(filename="error_log.log",level=logging.DEBUG)

# parking slots and car count initialization
count=0 # universal counter to keep a track of the number of ocr operations.
empty_slots=10 # empty parking slots counter.

# Helper function to control the opening of the gates.
def gateOpen(pin,intial,final):
    for i in range(intial,final,1):
        pwm.set_pwm(pin,0,i)
        time.sleep(0.01)

# Helper function to control the closing of the gates.
def gateClose(pin,intial,final):
    for i in range(intial,final,-1):
        pwm.set_pwm(pin,0,i)
        time.sleep(0.01)

# Gate control related functions.
def openGate1():
    gateOpen(0,90,180)

def closeGate1():
    gateClose(0,180,90)

def openGate2():
    gateOpen(15,90,180)

def closeGate2():
    gateClose(15,180,90)


''' A global database for criminal/illegal cars is updated.
blacklist --->updates the list of illegal cars to be denied entry into the parking lot.
'''
def updateCriminalDatabase(number_plate):
    blacklist=requests.get("https://api.thingspeak.com/update?api_key=QDYY29TD1PPNWDIK&field1="+str(number_plate))
    if blacklist.status_code==str(200):
        print("Successfully updated the blacklist database.")
    else:
        logging.error(number_plate+"failed to be added in the blacklist database.")


''' Criminal Database is checked prior to granting parking space.
 Returns True if number is blacklisted.
 blacklist ---> receives the updated list of illegal cars to be denied entry into the parking lot.
 number_plate ---> The  car license number that needs to be checked in the database.
 '''
def checkCriminalDatabse(number_plate):
    blacklist=requests.get("https://api.thingspeak.com/channels/482414/fields/1.json?")
    blacklist=yaml.load(blacklist.text)
    for i in blacklist['feeds']:
        if (str(i['field1'])).lower()==number_plate.lower():
            return True
    return False


''' 
The following function updates the database after every entry/exit.
This database stores ----> Number plate of car entered/exited, entry/exit status and the current slots available after entry/exit
It also stores those blacklisted cars that to enter the parking lot.
'''
def updateParkingDatabase(number_plate,occupied_slots,status):
    data={"api_key":"8RZ3DCTHQ6995PIE","field1":number_plate,"field2":occupied_slots,"field3":status}
    req=requests.post("https://api.thingspeak.com/update.json",data=data)
    if req.status_code==str(200):
        print("Succesfully updated the parking database.")
    else:
        logging.error(number_plate+"failed to be added in the parking database.")


# The following function uses Raspberry Pi camera to capture the number Plate.
def captureNumberPlate(filename):
    camera.start_preview()
    time.sleep(1)
    camera.capture(filename)
    camera.stop_preview()
    print("Captured number plate.")

''' 
The following function is used to extract only the number plate from the image for better OCR response.
Cannny edge detection is used to extract the image of the number plate from the car's body.
Extracted number plate is saved as a new image and sent to Vision API for OCR detection.
labels ---> receives the OCR output.
'''
def ocr(filename):
    captureNumberPlate(filename)
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

    return labels.text # This returns the OCR number plates.



# User prompt to update the blacklist databse on system start.
updateBlacklist=input("Do you want to add a number to the blacklist database?  Y/N : ")
if updateBlacklist.lower()=="y" or updateBlacklist.lower()=="yes":
    blacklistNumber=str(input("Enter the blacklist number plate : ")).strip()
    updateCriminalDatabase(blacklistNumber)

print("Total parking slots available ",str(empty_slots))

'''
GPIO 16 ---> IR connected to the exit gate.
GPIO 18 ---> IR connected to the entry gate.
The cars belonging to the criminal database are not allowed entry into the lot.
'''
try:
    while True:
        #exit control
        if(GPIO.input(16)==True) and empty_slots<10: # bigger IR signals True when object is near.
            count+=1
            filename="image"+str(count)+".jpg"
            empty_slots+=1
            openGate2() # open Gate 1 and let the car in if there are empty slots
            time.sleep(5)
            closeGate2()
            print("Processing number plate")
            text=str(ocr(filename)).strip()
            print("Detected car number - ",text)
            openGate1()
            time.sleep(5)
            closeGate1()
            print("Car exited succesfully to vehicle number - ",text)
            updateParkingDatabase(text,empty_slots,"exit") # updating thingspeak api with the data ---> Number plate , current slots in parking lot and extry/exit
            print("Remaining parking slots - "+str(empty_slots))
            
        #entry control
        if(GPIO.input(18)!=True) and empty_slots>0: # smaller IR signals false when object is near.
            openGate1()
            time.sleep(5)
            closeGate1()
            print("Processing number plate")
            count+=1
            filename="image"+str(count)+".jpg"
            text=str(ocr(filename)).strip()# ocr function will return the license plate as text
            print("Detected car number - ",text)
            if  not  checkCriminalDatabse(text):
                openGate2()
                time.sleep(5)
                closeGate2()
                print("Entry permitted succesfully to vehicle number - ",text)
                empty_slots-=1
                print("Reamaining slots -",str(empty_slots))
                updateParkingDatabase(text,empty_slots,"entry")
                print("Remaining parking slots - "+str(empty_slots))
            else:
                print("Sorry, this parking lot is only for law abiding citizens!")
                openGate1()
                time.sleep(5)
                closeGate1()
                print("Entry restricted succesfully to vehicle number - ",text)
                updateParkingDatabase(text,empty_slots,"rejected")
                print("Remaining parking slots - "+str(empty_slots))
except Exception as e:
    print(e)
    GPIO.cleanup()
    print("Program ended.")