__author__ = 'Ahab'

import math
import win32api
import win32con
import win32gui
import time
import pyperclip
from PIL import ImageGrab

import constants as c


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
    move(c.ALLINPOTBETBOXPOS, 0.1)
    click(c.BETBOXPOS)
    move(c.RAISEBUTTONPOS,0.1)
    click(c.RAISEBUTTONPOS)
    return True


def betAction(amount, wait):
    time.sleep(wait)
    move(c.BETBOXPOS,0.1)
    click(c.BETBOXPOS)
    pyperclip.copy(str(amount))
    time.sleep(0.1)
    dokey(0x43,17)
    move(c.RAISEBUTTONPOS,0.1)
    click(c.RAISEBUTTONPOS)
    return True


def callAction(wait):
    time.sleep(wait)
    move(c.CALLBUTTONPOS,0.1)
    click(c.CALLBUTTONPOS)
    return True


def foldAction(wait):
    time.sleep(wait)
    move(c.FOLDBUTTONPOS,0.1)
    click(c.FOLDBUTTONPOS)
    return True


def grabcard(x):
    """
    Returns an image from the BBox
    :param x: BBox
    :return:
    """
    (left, top, right, bot) = x
    cardim = ImageGrab.grab(bbox = (left, top, right, bot))
   #cardim = cardim.convert("RGB")
    return cardim


def getbetamount(p):
    move(p,0.1)
    click(p)
    click(p)
    time.sleep(0.1)
    #Copy all text
    dokey(0x43,17)
    variable = pyperclip.paste()
    return float(float(variable) * 100)


def getpotamount(p1,p2):
    move(p1, 0.1)
    click(p1)
    time.sleep(0.1)
    amount = getbetamount(p2)
    return amount


def getpotsize(potbetbox,betbox):
    move(potbetbox,0.01)
    click(potbetbox)
    time.sleep(0.01)
    move(betbox,0.01)
    click(betbox)
    click(betbox)
    dokey(0x41,17)
    dokey(0x43,17)
    variable = pyperclip.paste()
    return variable
