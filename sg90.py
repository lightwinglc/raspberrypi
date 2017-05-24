#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import signal
import atexit

atexit.register(GPIO.cleanup)

servopin = 4
GPIO.setmode(GPIO.BCM)
GPIO.setup(servopin, GPIO.OUT, initial=False)
p = GPIO.PWM(servopin, 50)  # 50HZ
p.start(0)
time.sleep(1)


p.ChangeDutyCycle(12.1)
time.sleep(3)
p.ChangeDutyCycle(2.5)
time.sleep(3)
p.ChangeDutyCycle(6.9)
time.sleep(3)

try:
    while False:
        for i in range(0, 180, 10):
            p.ChangeDutyCycle(2.5 + 10 * i / 180)  # 设置转动角度
            time.sleep(0.02)  # 等该20ms周期结束
    #        p.ChangeDutyCycle(0)  # 归零信号
    #        time.sleep(0.2)

        for i in range(180, 0, -10):
            p.ChangeDutyCycle(2.5 + 10 * i / 180)
            time.sleep(0.02)
    #        p.ChangeDutyCycle(0)
    #        time.sleep(0.2)
except KeyboardInterrupt:
    pass

p.stop()