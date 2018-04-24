import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(16,GPIO.IN) #GPGPIO 14 -> IR sensor as input
count=0
while True:
    if(GPIO.input(16)==True): #object is far away
            count+=1
            print("Car has arrived -",count)
            time.sleep(2)
