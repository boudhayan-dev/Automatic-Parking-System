import RPi.GPIO as GPIO
import time

def openGate1():
	pass

def closeGate1():
	pass

def checkCriminalDatabse(number_plate):
	return False #return true in case the number is in the databse

def ocr():
	pass

def openGate2():
	pass

def closeGate2():
	pass

empty_slots=2
car_in_box=0


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
        text=str(ocr())# ocr function will return the license plate as text
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


