#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time

Trig_BCM = 19
Echo_BCM = 26

def checkdist():
    # 发出触发信号
    GPIO.output(Trig_BCM, GPIO.HIGH)
    # 保持10us以上（我选择15us）
    time.sleep(0.000012)
    GPIO.output(Trig_BCM, GPIO.LOW)
    resulthigh = GPIO.wait_for_edge(Echo_BCM, GPIO.RISING, timeout=5000)
    if resulthigh is None:
        print "High level timeout occurred."
        return 0
    # 发现高电平时开时计时
    t1 = time.time()
    resultlow = GPIO.wait_for_edge(Echo_BCM, GPIO.FALLING, timeout=5000)
    if resultlow is None:
        print "Low level timeout occurred."
        return 0
    # 高电平结束停止计时
    t2 = time.time()
    # 返回距离，单位为米
    return (t2-t1)*340/2

GPIO.setmode(GPIO.BCM)
GPIO.setup(Trig_BCM, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Echo_BCM, GPIO.IN)

time.sleep(2)
try:
    while True:
        print 'Distance: %0.2f m' %checkdist()
        time.sleep(0.5)
except KeyboardInterrupt:
    GPIO.cleanup()