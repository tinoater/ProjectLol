__author__ = 'Ahab'

import math
import csv
import sys
import random
import operator
import functools
import random
import win32api
import win32con
import win32gui
from PIL import Image, ImageFilter, ImageGrab, ImageEnhance, ImageChops
import time
import pyperclip
import tkinter
import psycopg2
import fileinput
import linecache
import logging
import logging.config

def click(p):
    (x,y) = p
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def move(p, t=1.00):
    (x, y) = p
    (x1,y1) = win32api.GetCursorPos()
    (dx,dy) = (x - x1,y - y1)
    for i in range(1,100):
        x2 = math.floor(x1 + i * (dx / 100))
        y2 = math.floor(y1 + i * (dy / 100))
        win32api.SetCursorPos((x2, y2))
        time.sleep(t/100)

def callback(hwnd, resultList):
    rect = win32gui.GetWindowRect(hwnd)
    x = rect[0]
    y = rect[1]
    w = rect[2] - x
    h = rect[3] - y
    resultList.append((hwnd, win32gui.GetWindowText(hwnd), x, y, w, h, win32gui.GetClassName(hwnd)))

def gethandleofNLH():
    emptylist =[]
    win32gui.EnumWindows(callback, emptylist)
    emptylist = [(e1,e2,e3,e4,e5,e6,e7) for (e1,e2,e3,e4,e5,e6,e7) in emptylist if "NLH" in e2]
    logging.debug("gethandleofNLH ")
    logging.debug(str(emptylist))
    if len(emptylist) == 1:
        return(emptylist[0][0])
    else:
        return(emptylist[0][0])

def getwindownameofNLH():
    emptylist =[]
    win32gui.EnumWindows(callback, emptylist)
    emptylist = [[e1,e2,e3,e4,e5,e6,e7] for [e1,e2,e3,e4,e5,e6,e7] in emptylist if "NLH" in e2]
    windowname =  emptylist[0][1]
    windowname = windowname[:windowname.find("NLH") - 1]
    return str(windowname)

def setwindowposition():
    win32gui.MoveWindow(gethandleofNLH(), 0, 0, 502, 362, 1)

def dokey(key1,key2=None):
#shift - 16, ctrl = 17, left = 37, right = 39, space = 32
    if key2 == None:
        win32api.keybd_event(key1,0,0,0)
        time.sleep(0.1)
        win32api.keybd_event(key1,0,win32con.KEYEVENTF_KEYUP,0)
    else:
        win32api.keybd_event(key2,0,0,0)
        win32api.keybd_event(key1,0,0,0)
        time.sleep(0.1)
        win32api.keybd_event(key2,0,win32con.KEYEVENTF_KEYUP,0)
        win32api.keybd_event(key1,0,win32con.KEYEVENTF_KEYUP,0)

def bettingAction(action, amount, wait = 2):
    if action == 0:
        foldAction(wait)
    elif action == 1:
        callAction(wait)
    elif action == 2:
        betAction(amount, wait)
    elif action == 3:
        allInAction(wait)
    return True

def allInAction(wait):
    time.sleep(wait)
    move(ALLINPOTBETBOXPOS, 0.1)
    click(BETBOXPOS)
    move(RAISEBUTTONPOS,0.1)
    click(RAISEBUTTONPOS)
    return True

def betAction(amount, wait):
    time.sleep(wait)
    move(BETBOXPOS,0.1)
    click(BETBOXPOS)
    pyperclip.copy(str(amount))
    time.sleep(0.1)
    dokey(0x43,17)
    move(RAISEBUTTONPOS,0.1)
    click(RAISEBUTTONPOS)
    return True

def callAction(wait):
    time.sleep(wait)
    move(CALLBUTTONPOS,0.1)
    click(CALLBUTTONPOS)
    return True

def foldAction(wait):
    time.sleep(wait)
    move(FOLDBUTTONPOS,0.1)
    click(FOLDBUTTONPOS)
    return True