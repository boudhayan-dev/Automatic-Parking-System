import RPi.GPIO as GPIO
import numpy as np
from google.cloud import vision
from google.cloud.vision import types
import os,sys,logging,time,cv2,yaml
from picamera import PiCamera

# Function to adjust the pwm needed for the servo motors
def setAngle(pin,angle):
    duty = angle / 18 + 2
    GPIO.output(pin, True)
    pwm.ChangeDutyCycle(duty)
    time.sleep(1)
    GPIO.output(pin, False)
    pwm.ChangeDutyCycle(0)

# Motor controls
def openGate1():
    setAngle(motor1,70)

def closeGate1():
    setAngle(motor1,0)

def openGate2():
    setAngle(motor2,70)

def closeGate2():
    setAngle(motor2,70)


# A global database for criminal/illegal cars is updated.
def updateCriminalDatabase(number_plate):
    blacklist=requests.get("https://api.thingspeak.com/update?api_key=QDYY29TD1PPNWDIK&field1="+str(number_plate))
    if blacklist.status_code==str(200):
        print("Successfully updated the blacklist database.")
    else:
        logging.error(number_plate+"failed to be added in the blacklist database.")

# Criminal Database is checked prior to granting parking space.
# Returns True if number is blacklisted.
def checkCriminalDatabse(number_plate):
    blacklist=requests.get("https://api.thingspeak.com/channels/482414/fields/1.json?")
    blacklist=yaml.load(blacklist.text)
    for i in blacklist['feeds']:
        if (str(i['field1'])).lower()==number_plate.lower():
            return True
    return False

# This database stores ----> Number plate of car entered/exited, entry/exit status and the current slots available after entry/exit
# It also stores those blacklisted cars that tried availing the service.
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

# The following function is used to extract the only the number plate from the image for better processing.
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


# Google Vision OCR Json file settings
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'boodi.json'
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
#Set the servo motor
motor1=11
motor2=13
GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor1, GPIO.OUT)
GPIO.setup(motor2, GPIO.OUT)
pwm1=GPIO.PWM(motor1, 50)
pwm2=GPIO.PWM(motor2, 50)
pwm1.start(0)
pwm2.start(0)
#creating logging file
logging.basicConfig(filename="example.log",level=logging.DEBUG)
# parking slots and car count initialization
count=0 # universal counter to keep a track of the number of ocr operations.
empty_slots=5 # empty parking slots counter.

# User prompt to facilitate updation of the blacklist database.
updateBlacklist=input("Do you want to add to the blacklist database?  Y/N : ")
if updateBlacklist.lower()=="y" or updateBlacklist.lower()=="yes":
    blacklistNumber=str(input("Enter the blacklist number plate : ")).strip()
    updateCriminalDatabase(blacklistNumber)

print("Total parking slots available ",str(empty_slots))

try:

    while True:
        #exit control
        if(GPIO.input(16)==True): # bigger IR signals True when object is near.
            count+=1
            filename="image"+str(count)+".jpg"
            empty_slots+=1
            openGate2() # open Gate 1 and let the car in if there are empty slots
            time.sleep(2)
            closeGate2()
            print("Processing number plate")
            text=str(ocr(filename)).strip()
            openGate1()
            time.sleep(2)
            closeGate1()
            print("Car exited succesfully.")
            updateParkingDatabase(text,empty_slots,"exit") # updating thingspeak api with the data ---> Number plate , current slots in parking lot and extry/exit
            print("Remaining parking slots - "+str(empty_slots))
            
        #entry control
        if(GPIO.input(18)!=True): # smaller IR signals false when object is near.
            openGate1()
            time.sleep(2)
            closeGate1()
            print("Processing number plate")
            count+=1
            filename="image"+str(count)+".jpg"
            text=str(ocr(filename)).strip()# ocr function will return the license plate as text
            if  not  checkCriminalDatabse(text):
                openGate2()
                time.sleep(2)
                closeGate2()
                print("Entry permitted succesfully.")
                empty_slots-=1
                print("Reamaining slots -",str(empty_slots))
                updateParkingDatabase(text,empty_slots,"entry")
                print("Remaining parking slots - "+str(empty_slots))
            else:
                print("Sorry, this parking lot is only for law abiding citizens!")
                openGate1()
                time.sleep(2)
                closeGate1()
                print("Entry restricted succesfully.")
                updateParkingDatabase(text,empty_slots,"rejected")
                print("Remaining parking slots - "+str(empty_slots))
except:
    pwm1.stop()
    pwm2.stop()
    GPIO.cleanup()
    print("Program ended.")


