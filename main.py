from picamera import PiCamera
from time import sleep
from datetime import datetime
import os.path
from os.path import isfile, join
from os import listdir
from shutil import copyfile
import math
import RPi.GPIO as GPIO
import subprocess
import traceback

print("Starting...")

big = 27
small =  17
led = 18

flash_drive = "fd"#name of the flash drive to use
saveDir = "img/"
outputDir = "/media/" + flash_drive + "/img/"

def pad(digits, text):
    ret = ""
    for i in range(0, digits):
        if len(text) + i < digits:
            ret = ret + "0"
    return ret + text

def blink(times, speed):
    for i in range(0, times):
        GPIO.output(led, GPIO.HIGH)
        sleep(speed)
        GPIO.output(led, GPIO.LOW)
        sleep(speed)

cam = PiCamera()
cam.resolution = (1280, 720)

GPIO.setmode(GPIO.BCM)

GPIO.setup(big, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(small, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(18, GPIO.OUT)

GPIO.output(led, GPIO.HIGH)
sleep(1)
GPIO.output(led, GPIO.LOW)

state = 0
dontTakeAgain = ''

print("Set up done, running main loop.")

while True:

    t = datetime.today()

    if not GPIO.input(big):
        state = state + 1
    else:
        state = 0


    if not GPIO.input(small):
        blink(5, 0.3)
        if not GPIO.input(small):
            blink(3, 0.1)
            break

    #cam.capture('image{0:04d}.jpg'.format(i))
    
    #print('year: ', pad(4, str(t.year)))
    #print('month: ', pad(2, str(t.month)))
    #print('day: ', pad(2, str(t.day)))
    #print('hour: ', pad(2, str(t.hour)))
    #print('minute: ', pad(2, str(t.minute)))
    #print('second: ', math.floor(t.second/10))

    #print('Hello{0:03d}'.format(t.minute) + '{0:02d}'.format(t.second))

    filename = 'img{0:04d}'.format(t.year) + '{0:02d}'.format(t.month) + '{0:02d}'.format(t.day) + '{0:02d}'.format(t.hour) + '{0:02d}'.format(t.minute//15) + '.jpg'

    if not os.path.isfile(saveDir + filename) and not saveDir + filename == dontTakeAgain:

        print('Taking photo... (' + saveDir + filename + ')')
        cam.capture(saveDir + filename)
        print('Photo taken: ' + saveDir + filename)
    
    if state == 0:
        GPIO.output(led, GPIO.LOW)
        sleep(3)
    elif state == 1:
        GPIO.output(led, GPIO.HIGH)
        sleep(3)
    elif state == 2:
        GPIO.output(led, GPIO.LOW)
        sleep(1)
        GPIO.output(led, GPIO.HIGH)
        sleep(1)
        GPIO.output(led, GPIO.LOW)
        sleep(2)
    elif state == 3:
        blink(3, 0.1)
        GPIO.output(led, GPIO.HIGH)
        sleep(0.5)
        error = False

        try:
            subprocess.call(['sudo mkdir /media/' + flash_drive], shell=True)
            subprocess.call(['sudo mount /dev/sda1 /media/' + flash_drive], shell=True)
        except Exception:
            print(traceback.format_exc())
            error = True

        try:
            theFiles = [f for f in sorted(listdir(saveDir)) if isfile(join(saveDir, f))]
            for i in range(0, len(theFiles)):
                copyfile(saveDir + theFiles[i], outputDir + theFiles[i])
                os.remove(saveDir + theFiles[i])
                print("Copied and removed " + theFiles[i])
                dontTakeAgain = saveDir + theFiles[i]
        except Exception:
            print(traceback.format_exc())
            error = True

        try:
            subprocess.call(['sudo umount /media/' + flash_drive], shell=True)
        except Exception:
            print(traceback.format_exc())
            error = True
        try:
            subprocess.call(['sudo rm -r /media/' + flash_drive], shell=True)
        except Exception:
            print(traceback.format_exc())
            error = True
        if error:
            blink(4, 0.8)
        blink(3, 0.8)
