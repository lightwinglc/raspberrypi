#!/usr/bin/python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time


# 车轮控制类
class PiWheel(object):
    # 控制并联的一组轮子使用3个GPIO端口：IN1,IN2,EN
    def __init__(self, in1, in2, en):
        self.in1 = in1
        self.in2 = in2
        self.en = en
        # 初始化将使用的GPIO端口都设为输出
        GPIO.setup(in1, GPIO.OUT)
        GPIO.setup(in2, GPIO.OUT)
        GPIO.setup(en, GPIO.OUT)

    def clean(self):
        # 检查是否调速
        if 1 == self.ispwm:
            self.p.stop()
        # 释放GPIO端口资源
        GPIO.cleanup(self.in1)
        GPIO.cleanup(self.in2)
        GPIO.cleanup(self.en)

    # 设置车轮速度
    # ispwm设为1表示开启调速，为0表示全速运行，调速使用的参数频率（frequency）和占空比（dutycycle）
    def setSpeed(self, ispwm, frequency = 20, dutycycle = 80):
        self.ispwm = ispwm
        self.frequency = frequency
        self.dutycycle = dutycycle
        # 检查是否调速
        if 1 == ispwm:
            self.p = GPIO.PWM(self.en, frequency)
            self.p.start(dutycycle)
        elif 0 == ispwm:
            GPIO.output(self.en, GPIO.HIGH)
        else:
            print "Invalid parameter ispwm " + ispwm

    # 开启调速时可用
    def changeSpeed(self, frequency, dutycycle):
        if 1 == self.ispwm:
            self.frequency = frequency
            self.dutycycle = dutycycle
            self.p.ChangeFrequency(frequency)
            self.p.ChangeDutyCycle(dutycycle)

    # 前进
    def forward(self):
        GPIO.output(self.in1, GPIO.HIGH)
        GPIO.output(self.in2, GPIO.LOW)

    # 后退
    def backward(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.HIGH)

    # 停止
    def stop(self):
        GPIO.output(self.in1, GPIO.LOW)
        GPIO.output(self.in2, GPIO.LOW)


# 小车控制类
class PiCar(object):
    def __init__(self):
        # 设置引脚编号方式
        GPIO.setmode(GPIO.BOARD)
        # 定义左右两组车轮
        self.leftwheel = PiWheel(13, 15, 11)
        self.rightwheel = PiWheel(38, 36, 40)

    def clean(self):
        self.leftwheel.clean()
        self.rightwheel.clean()

    # 设置速度
    def setSpeed(self, ispwm, frequency = 20, dutycycle = 80):
        self.ispwm = ispwm
        self.frequency = frequency
        self.dutycycle = dutycycle
        self.leftwheel.setSpeed(ispwm, frequency, dutycycle)
        self.rightwheel.setSpeed(ispwm, frequency, dutycycle)

    # 修改速度
    def changeSpeed(self, frequency, dutycycle):
        self.frequency = frequency
        self.dutycycle = dutycycle
        self.leftwheel.changeSpeed(frequency, dutycycle)
        self.rightwheel.changeSpeed(frequency, dutycycle)

    # 前进
    def forward(self):
        self.leftwheel.forward()
        self.rightwheel.forward()

    # 后退
    def backward(self):
        self.leftwheel.backward()
        self.rightwheel.backward()

    # 停止
    def stop(self):
        self.leftwheel.stop()
        self.rightwheel.stop()

    # 原地左转
    def turnLeft(self):
        self.leftwheel.backward()
        self.rightwheel.forward()

    # 原地右转
    def turnRight(self):
        self.leftwheel.forward()
        self.rightwheel.backward()


if __name__ == '__main__':
    lccar = PiCar()
    lccar.setSpeed(1, 25, 50)
    # lccar.setSpeed(0)
    print '''Please use 'w', 'a', 's', 'd', 'x' control car.'''
    while True:
        order = raw_input("input:")
        if order == "w":
            lccar.stop()
            lccar.changeSpeed(25, 50)
            lccar.forward()
        elif order == "a":
            lccar.stop()
            lccar.changeSpeed(25, 50)
            lccar.turnLeft()
        elif order == "s":
            lccar.stop()
        elif order == "d":
            lccar.stop()
            lccar.changeSpeed(25, 50)
            lccar.turnRight()
        elif order == "x":
            lccar.stop()
            lccar.changeSpeed(25, 50)
            lccar.backward()
        else:
            lccar.stop()
            break
    lccar.clean()



