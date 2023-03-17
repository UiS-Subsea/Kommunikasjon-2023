#!/usr/bin/python3

"""
    @file   camPWMr.py
    
    @brief  Driver for adafruit servomotor
    @date   16.03.23 
    @author Thomas Matre
"""

import RPi.GPIO as GPIO

def scale2x(X0, X1, Y0, Y1, inValue):
    xRange = X1-X0
    yRange = Y1-Y0
    if xRange != 0:
        Value = (yRange / xRange) * (inValue - X0) + Y0
    else:
        Value = 0
    return Value

class adafruitServoPWM:
    def __init__(self, pin=32, freq=50, startDT:float=7.5) -> None:
        self.usrpin = pin
        self.freq = freq
        self.startDT = startDT
        if (pin != 32) or (pin != 33):
            self.pinPwm = {'JETSON_NANO': 32}
        else:
            self.pinPwm = {'JETSON_NANO': self.usrpin}
        self.outputPwm = self.pinPwm.get(GPIO.model, None)
        self.initPWM()

    def initPWM(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.outputPwm, GPIO.OUT, initial=GPIO.HIGH)
        self.PWM = GPIO.PWM(self.outputPwm, self.freq)
        self.PWM.start(self.startDT)
    
    def newAngle(self, angle):
        if 0 <= angle <= 180:
            value = scale2x(X0=0, X1=180, Y0=5, Y1=10, inValue=angle)
        else:
            value = 7.5
        self.PWM.ChangeDutyCycle(value)
        print(value)
    def cleanup(self):
        self.PWM.stop()
        GPIO.cleanup()

if __name__ == '__main__':
    pin = int(input("pin"))
    pwm = adafruitServoPWM(pin=32,freq=50)
    try:
        while True:
            a = float(input("angle: "))
            pwm.newAngle(a)
    finally:
        pwm.cleanup()