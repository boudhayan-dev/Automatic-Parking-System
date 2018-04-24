import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11, GPIO.OUT)
pwm=GPIO.PWM(11, 50)
pwm.start(0)

def SetAngle(angle):
	duty = angle / 18 + 2
	GPIO.output(11, True)
	pwm.ChangeDutyCycle(duty)
	time.sleep(1)
	GPIO.output(11, False)
	pwm.ChangeDutyCycle(0)

SetAngle(70) 
time.sleep(1)
SetAngle(0)

GPIO.cleanup()
