#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# autojump.py
# @Author : damone (summur0shine@gmail.com)
# @Link   : 
# @Date   : 2018-1-14 04:47:46

import os
import sys
import cv2  
import numpy as np  
from matplotlib import pyplot as plt  
import numpy
import math
import time
import random

class device_tool:
    @staticmethod
    def press_screen(time):
        os.system("adb shell input swipe 250 250 250 250 " + str(time))
    @staticmethod
    def click(x, y):
        os.system("adb shell input  tap " + str(x) + " " + str(y))
    @staticmethod
    def screenshot(filename):
        os.system("adb shell /system/bin/screencap -p " + filename)
    @staticmethod
    def download_file(device_filename, host_filename):
        os.system("adb pull " + device_filename + " " + host_filename)
    @staticmethod
    def upload_file(host_filename, device_filename):
        os.system("adb push " + host_filename + " " + device_filename)
    @staticmethod
    def mkdir(path):
        os.system("adb shell mkdir  " + path)
        

def detector_person(filename):
    img = cv2.imread(filename,0)
    template = cv2.imread("obj.png",0)  
    w,h = template.shape[::-1]
  
    method = eval('cv2.TM_CCOEFF')  
    res = cv2.matchTemplate(img,template,method)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  
    top_left = max_loc  
    bottom_right = (top_left[0] + w, top_left[1] + h)

    # img = cv2.imread(filename,3)
    # cv2.rectangle(img,top_left, bottom_right, 255, 2)

    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # plt.imshow(img)
    # plt.show()
    return  top_left, bottom_right;

def canny(filename):
    image = cv2.imread(filename)  
    image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h,s,v = cv2.split(image)
    gray = h
  
    canny = cv2.Canny(gray, 5, 15)  
    thresh = cv2.threshold(canny, 10, 255, cv2.THRESH_BINARY)[1]

     # 扩展阀值图像填充孔洞，然后找到阀值图像上的轮廓
    _, cnts, hierarchy = cv2.findContours( thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # show contours
    cv2.drawContours(image, cnts, -1, 255, 2) 

    image = cv2.cvtColor(image, cv2.COLOR_HSV2RGB)
    #plt.imshow(canny, cmap = plt.cm.gray)
    plt.imshow(image, cmap = plt.cm.gray)
    plt.show()


class detecter:
    templatefilename = None
    template = None
    width = 0
    height = 0
    def __init__(self, templatefilename):
        self.templatefilename = templatefilename
        self.template = cv2.imread(templatefilename, 0)  
        self.width,self.height = self.template.shape[::-1]

    def detector_person(self, gray):
        method = eval('cv2.TM_CCOEFF')  
        res = cv2.matchTemplate(gray,self.template,method)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  
        top_left = max_loc  
        bottom_right = (top_left[0] + self.width, top_left[1] + self.height)

        return  top_left, bottom_right

    def detector_next_position(self, image, top, bottom):
        image2 = image.copy()
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)
        h,s,v = cv2.split(image2)
        canny =  cv2.Canny(h, 5, 5)  
        canny |= cv2.Canny(s, 5, 5)  
        canny |= cv2.Canny(v, 5, 5)  
        thresh = cv2.threshold(canny, 0, 255, cv2.THRESH_BINARY)[1]
        thresh[top[1]:bottom[1],top[0] : bottom[0]] = 0
        # 扩展阀值图像填充孔洞，然后找到阀值图像上的轮廓
        _, cnts, hierarchy = cv2.findContours( thresh.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # find contour
        dest_cnt = None
        dest_pos = None
        dest_y = 10000
        for c in cnts:
            # if the contour is too small, ignore it
            (x, y, w, h) = cv2.boundingRect(c)
            if y < 350 or w < 60 or h < 20:
                continue

            pos_t, _ = self.get_position_top(c, y)
            if pos_t[0] >= top[0] and pos_t[0] <= bottom[0] and pos_t[1] >= top[1] and pos_t[1] <= bottom[1]:
                continue

            if y < dest_y:
                dest_y = y
                dest_cnt = c
                dest_pos = pos_t

        return dest_cnt, dest_pos

    def get_position_top(self, cnt, min_y):
        pos = [0,0]
        count = 0
        for p in cnt:
            p = p[0]
            if(p[1] - min_y < 5):
                count += 1
                pos[0] += p[0]
                pos[1] += p[1]
        pos[0] /= count
        pos[1] /= count   
        return  (int(pos[0]), int(pos[1])), count
    
    def get_person_pos(self, top, bottom):
        x = int((top[0] + bottom[0]) / 2)
        y = bottom[1] - 15
        return (x,y)

    def get_position_center(self, pos_s, pos_t):
        x = pos_t[0]
        y = pos_s[1]
        y = int(y - 0.60 * abs(x - pos_s[0])) - 15
        if y < (pos_t[1] + 25) or y > (pos_t[1] + 100):
            y = pos_t[1] + 25
        return (x,y)


    def show_results(self, image, cnt, top, bottom, pos_s, pos_e, pos_t, count):
        cv2.circle(image, pos_t, 7, (255, 0, 0), -1)
        cv2.circle(image, pos_s, 7, (0, 0, 255), -1)
        cv2.circle(image, pos_e, 7, (0, 255, 0), -1)

        cv2.drawContours(image, [cnt], -1, (0, 255, 0), 2)
        cv2.rectangle(image,top, bottom, (0, 0, 255), 2)
        filename = "data/%d.png" % (count)
        cv2.imwrite(filename, image)

        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        # plt.imshow(image)
        # plt.show()

    def detect_image(self, filename, count):
        image = cv2.imread(filename)  
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        top, bottom = self.detector_person(gray)

        cnt, pos_t = self.detector_next_position(image,top, bottom)
        pos_s = self.get_person_pos(top, bottom)
        pos_e = self.get_position_center(pos_s, pos_t)
        self.show_results(image, cnt, top, bottom, pos_s, pos_e, pos_t, count)
        return pos_s, pos_e

def jump():
    count = 0
    det = detecter("obj.png")
    while True:
        count += 1
        device_tool.screenshot("/sdcard/test.png")
        device_tool.download_file("/sdcard/test.png", "test.png")
        pos_s, pos_e = det.detect_image("test.png", count)
        s = math.sqrt(math.pow(pos_s[0] - pos_e[0], 2) + math.pow(pos_s[1] - pos_e[1], 2))
        t = int(s * 1.352)
        if t < 50:
            t = 50
        device_tool.press_screen(t)
        time.sleep(random.uniform(1.5, 2.5))
        
        # exit = input('input a q to quit!')
        # if exit == "q":
        #     break

jump()
#canny("data/126.png")