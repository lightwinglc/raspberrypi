#!/usr/bin/env python
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
import atexit


# 车轮控制类
class PiWheel(object):
    # 控制并联的一组轮子使用3个GPIO端口：IN1,IN2,EN
    # 设置车轮速度，ispwm设为1表示开启调速，为0表示全速运行，调速使用的参数频率（frequency）和占空比（dutycycle）
    def __init__(self, in1, in2, en, ispwm = 1, frequency = 50, dutycycle = 60):
        self.in1 = in1
        self.in2 = in2
        self.en = en
        self.ispwm = ispwm
        self.frequency = frequency
        self.dutycycle = dutycycle

        # 初始化将使用的GPIO端口都设为输出
        GPIO.setup(in1, GPIO.OUT)
        GPIO.setup(in2, GPIO.OUT)
        GPIO.setup(en, GPIO.OUT)

        # 检查是否调速
        if 1 == ispwm:
            self.p = GPIO.PWM(self.en, frequency)
            self.p.start(dutycycle)
        elif 0 == ispwm:
            GPIO.output(self.en, GPIO.HIGH)
        else:
            print "Invalid parameter ispwm %d." % ispwm
            exit()

    def __del__(self):
        # 检查是否调速
        if 1 == self.ispwm:
            self.p.stop()

    # 开启调速时可用
    def changespeed(self, frequency, dutycycle):
        if 1 == self.ispwm:
            self.frequency = frequency
            self.dutycycle = dutycycle
            self.p.ChangeFrequency(frequency)
            self.p.ChangeDutyCycle(dutycycle)

    # 开启全速
    def fullspeed(self):
        if 1 == self.ispwm:
            self.p.stop()
            self.ispwm = 0
        GPIO.output(self.en, GPIO.HIGH)

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


# 开车控制类
class PiDrive(object):
    def __init__(self, in1, in2, en1, in3, in4, en2, ispwm = 1, frequency = 50, dutycycle = 60):
        # 定义左右两组车轮
        self.leftwheel = PiWheel(in1, in2, en1, ispwm, frequency, dutycycle)
        self.rightwheel = PiWheel(in3, in4, en2, ispwm, frequency, dutycycle)

    # 修改速度
    def changespeed(self, frequency, dutycycle):
        self.leftwheel.changespeed(frequency, dutycycle)
        self.rightwheel.changespeed(frequency, dutycycle)

    # 前进
    def forward(self):
        self.leftwheel.forward()
        self.rightwheel.forward()
        print "drive forward"

    # 后退
    def backward(self):
        self.leftwheel.backward()
        self.rightwheel.backward()
        print "drive backward"

    # 停止
    def stop(self):
        self.leftwheel.stop()
        self.rightwheel.stop()

    # 原地左转90
    def turnleft(self):
        self.leftwheel.backward()
        self.rightwheel.forward()
        time.sleep(0.75)
        self.stop()
        print "drive left"

    # 原地左转45
    def turnleft45(self):
        self.leftwheel.backward()
        self.rightwheel.forward()
        time.sleep(0.4)
        self.stop()
        print "drive left45"

    # 原地右转90
    def turnright(self):
        self.leftwheel.forward()
        self.rightwheel.backward()
        time.sleep(0.75)
        self.stop()
        print "drive right"

    # 原地右转40
    def turnright45(self):
        self.leftwheel.forward()
        self.rightwheel.backward()
        time.sleep(0.4)
        self.stop()
        print "drive right45"

    # 掉头
    def turnback(self):
        self.leftwheel.forward()
        self.rightwheel.backward()
        time.sleep(1.4)
        self.stop()
        print "drive turnback"


class Hcsr04(object):
    def __init__(self, trig, echo):
        self.trig = trig
        self.echo = echo
        GPIO.setup(trig, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(echo, GPIO.IN)

    # 测距函数
    def getdistance(self):
        # 发出触发信号
        GPIO.output(self.trig, GPIO.HIGH)
        # 保持10us以上（我选择15us）
        time.sleep(0.000015)
        GPIO.output(self.trig, GPIO.LOW)
        resultrise = GPIO.wait_for_edge(self.echo, GPIO.RISING, timeout=300)
        if resultrise is None:
            return -1
        # 发现高电平时开时计时
        t1 = time.time()
        resultfall = GPIO.wait_for_edge(self.echo, GPIO.FALLING, timeout=300)
        if resultfall is None:
            return -2
        # 高电平结束停止计时
        t2 = time.time()
        # 返回距离，单位为cm
        return (t2 - t1) * 34000 / 2


class Sg90(object):
    def __init__(self, control):
        self.control = control
        GPIO.setup(control, GPIO.OUT, initial=False)
        self.p = GPIO.PWM(control, 50)  # 50HZ
        self.p.start(6.9)
        time.sleep(0.4)
        self.direction = "forward"

    def turnleft(self):
        self.p.ChangeDutyCycle(12.1)
        time.sleep(0.4)
        self.direction = "left"
        print "sg90 turnleft"

    def turnleft45(self):
        self.p.ChangeDutyCycle(9.5)
        time.sleep(0.4)
        self.direction = "left45"
        print "sg90 turnleft45"

    def forward(self):
        self.p.ChangeDutyCycle(6.9)
        time.sleep(0.4)
        self.direction = "forward"
        print "sg90 forward"

    def turnright(self):
        self.p.ChangeDutyCycle(2.5)
        time.sleep(0.4)
        self.direction = "right"
        print "sg90 turnright"

    def turnright45(self):
        self.p.ChangeDutyCycle(4.7)
        time.sleep(0.4)
        self.direction = "right45"
        print "sg90 turnright45"


def main():
    print "autodrive"
    # 退出自动清理GPIO通道
    atexit.register(GPIO.cleanup)
    # 关闭告警
    GPIO.setwarnings(False)
    # 设置引脚编号方式
    GPIO.setmode(GPIO.BOARD)

    # 初始化小车动力模块，超声模块和舵机模块
    driver = PiDrive(13, 15, 11, 38, 36, 40)
    hcsr04 = Hcsr04(35, 37)
    sg90 = Sg90(7)

    try:
        while True:
            # 超声探测距离
            distance = hcsr04.getdistance()

            # 测距异常，包括测距超时，大于450cm，等待一段时间重测
            if distance < 0:
                print "distance %d error" % distance
                time.sleep(0.1)

            elif distance < 2:
                # 距离非常近时停车，后退
                driver.stop()
                driver.backward()
                time.sleep(0.1)
                print "distance 0"

            elif distance <= 20 or distance > 450:
                # 距离不足，先停车
                driver.stop()
                print "distance %d" % distance

                # sg90转向探测
                if sg90.direction == "forward":
                    sg90.turnleft45()
                elif sg90.direction == "left45":
                    sg90.turnleft()
                elif sg90.direction == "left":
                    sg90.turnright45()
                elif sg90.direction == "right45":
                    sg90.turnright()
                # 向右并且距离不足，小车掉头，sg90归位
                else:
                    sg90.forward()
                    driver.turnback()
                    print "sg90 forward and dirve back"

            else:
                # 距离足够，检查sg90的转向
                if sg90.direction == "forward":
                    driver.forward()
                elif sg90.direction == "left45":
                    print "distance %d" % distance
                    # sg90回正，小车左转45度，停
                    sg90.forward()
                    driver.turnleft45()
                elif sg90.direction == "left":
                    print "distance %d" % distance
                    sg90.forward()
                    driver.turnleft()
                elif sg90.direction == "right45":
                    print "distance %d" % distance
                    sg90.forward()
                    driver.turnright45()
                else:
                    print "distance %d" % distance
                    sg90.forward()
                    driver.turnright()
    except KeyboardInterrupt:
        exit()


if __name__ == '__main__':
    main()

