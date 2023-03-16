#!/usr/bin/python3

"""
    @file   commmunicationHandler.py
    
    @brief  
    @date   10.03.23 
    @author Thomas Matre
"""

import RPi.GPIO as GPIO
import time

output_pinspwm = {'JETSON_NANO': 33}
output_pinpwm = output_pinspwm.get(GPIO.model, None)
output_pinsOE = {'JETSON_NANO': 36}
output_pinOE = output_pinsOE.get(GPIO.model, None)
if output_pinpwm is None or output_pinOE is None:
    raise Exception('PWM not supported on this board')

def main():
    # Pin Setup:
    # Board pin-numbering scheme
    GPIO.setmode(GPIO.BOARD)
    # set pin as an output pin with optional initial state of HIGH
    GPIO.setup(output_pinpwm, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(output_pinOE, GPIO.OUT, initial=GPIO.HIGH)
    p = GPIO.PWM(output_pinpwm, 50)
    GPIO.output(output_pinOE, False)
    val = 25
    incr = 1
    p.start(val)

    print("PWM running. Press CTRL+C to exit.")
    try:
        while True:
            time.sleep(1)
            if val >= 10:
                step = -incr
            if val <= 5:
                step = incr
            val += step
            p.ChangeDutyCycle(val)
            print(val)
    finally:
        p.stop()
        GPIO.cleanup()
if __name__ == "__main__":
    main()