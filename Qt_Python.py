import sys
import RPi.GPIO as GPIO
import time

from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

servo_pin = 17
buzzer_pin = 13
led = 20
led2 = 21
min = 1
max = 9.5
pinTrigger = 0
pinEcho = 1

GPIO.setmode(GPIO.BCM)
GPIO.setup(buzzer_pin, GPIO.OUT)
GPIO.setup(led,GPIO.OUT)
GPIO.setup(led2,GPIO.OUT)
GPIO.setup(servo_pin, GPIO.OUT)
GPIO.setup(pinTrigger, GPIO.OUT)
GPIO.setup(pinEcho, GPIO.IN)


pwm_1 = GPIO.PWM(servo_pin, 50)	# frequency set 주파수 설정
pwm_1.start(1.5)		#cycle set 주기 설정
pwm = GPIO.PWM(buzzer_pin,1)

melody = [262,294,330,349,392,440,494,523]

star = [1,1,5,5,6,6,5,4,4,3,3,2,2,1,
		5,5,4,4,3,3,2,5,5,4,4,3,3,2,
		1,1,5,5,6,6,5,4,4,3,3,2,2,1]

class myWindow(QWidget):
	def __init__(self, parent = None):
		super().__init__(parent)
		self.ui = uic.loadUi("last.ui",self)
		self.ui.show()
		self.th = BuzzerThread(self)
		self.th.daemon = True
		self.th.threadEvent.connect(self.threadEventHandler)
		self.th_2 = UltraThread(self)
		self.th_2.daemon = True
		self.th_2.threadEvent_2.connect(self.threadEventHandler1)
		
	def slot_exit(self):

		print("bye~~")
		sys.exit()

	def slot_on(self):
		self.ui.label.setText("ON")
		GPIO.output(led,True)
		GPIO.output(led2,True)
	def slot_off(self):
		self.ui.label.setText("OFF")
		GPIO.output(led,False)
		GPIO.output(led2,False)
	def dial(self):
		motor_dial = self.ui.lcdNumber_3.value()
		dial_value = (((max-min)/180)*motor_dial)+min
		pwm_1.ChangeDutyCycle(dial_value)
		time.sleep(0.01)

	def star(self):
		pwm.start(50.0)
		self.th.isRun = True
		self.th.start()

	def stop(self):
		self.th.isRun = False
		self.th.stop1()
	def threadEventHandler(self, n):
		pass
		
	def threadEventHandler1(self,distance):
		self.ui.label_3.setText("%.2fcm"%distance)

	def ultra_on(self):
		if not self.th_2.isRun:
			self.th_2.isRun = True
			self.th_2.start()

	def ultra_stop(self):
		if self.th_2.isRun:
			self.th_2.isRun = False

class BuzzerThread(QThread):
	threadEvent = pyqtSignal(int)

	def __init__(self, parent=None):
		super().__init__()
		self.n = 0
		self.isRun = False

	def run(self):
		while self.isRun:
			pwm.ChangeFrequency(melody[star[self.n]])
			if self.n==6 or self.n==13 or self.n==20 or self.n ==27 or self.n==34 or self.n==41:
				time.sleep(1)
			else:
				time.sleep(0.5)

			self.threadEvent.emit(self.n)
			self.n += 1

			if self.n == 43:
				break
		pwm.stop()
		self.isRun = False

	def stop1(self):
		pwm.stop()

class UltraThread(QThread):
	threadEvent_2 = pyqtSignal(float)

	def __init__(self, parent=None):
		super().__init__()
		self.distance = 0.0
		self.isRun = False

	def measure(self):
		GPIO.output(pinTrigger,True)
		time.sleep(0.0001)
		GPIO.output(pinTrigger,False)

		start  = time.time()
		while GPIO.input(pinEcho) == False:
			start = time.time()
		while GPIO.input(pinEcho) == True:
			stop = time.time()

		elapsed = stop - start
		distance = (elapsed * 19000) / 2
		return distance

	def run(self):
		while self.isRun:
			self.distance = self.measure()
#			print("嫄곕━ : %.2f cm" %distance)
			self.threadEvent_2.emit(self.distance)
			time.sleep(0.1)

if __name__ == "__main__":
	app = QApplication(sys.argv)
	myapp = myWindow()
	app.exec()


