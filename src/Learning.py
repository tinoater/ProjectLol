__author__ = 'Ahab'

import win32api
import win32con
import win32gui
from PIL import Image, ImageFilter, ImageGrab, ImageEnhance, ImageChops
import time
import math
import functools
import operator

#DEBUG functions
def printcursorpoint(t=5):
    starttime = time.time()
    while time.time() <= starttime + t:
        print(win32gui.GetCursorPos())
        time.sleep(0.1)

def rmsdiff(im1, im2):
    "Calculate the root-mean-square difference between two images"

    h = ImageChops.difference(im1, im2).histogram()

    # calculate rms
    return math.sqrt(functools.reduce(operator.add,
        map(lambda h, i: h*(i**2), h, range(256))
    ) / (float(im1.size[0]) * im1.size[1]))

def findplayeraction(box):
    playerim = ImageGrab.grab(box)
    print("Fold "+ str(rmsdiff(playerim,Image.open("Actions-Fold.jpg"))))
    print("Call "+ str(rmsdiff(playerim,Image.open("Actions-Call.jpg"))))
    print("Raise "+ str(rmsdiff(playerim,Image.open("Actions-Raise.jpg"))))
    print("AllIn "+ str(rmsdiff(playerim,Image.open("Actions-AllIn.jpg"))))
    print("SB "+ str(rmsdiff(playerim,Image.open("Actions-SB.jpg"))))
    print("BB "+ str(rmsdiff(playerim,Image.open("Actions-BB.jpg"))))
    if rmsdiff(playerim,Image.open("Actions-Fold.jpg")) == 0:
        return "X"
    elif rmsdiff(playerim,Image.open("Actions-Call.jpg")) == 0:
        return "C"
    elif rmsdiff(playerim,Image.open("Actions-Raise.jpg")) == 0:
        return "R"
    elif rmsdiff(playerim,Image.open("Actions-AllIn.jpg")) == 0:
        return "A"
    elif rmsdiff(playerim,Image.open("Actions-SB.jpg")) == 0:
        return "SB"
    elif rmsdiff(playerim,Image.open("Actions-BB.jpg")) == 0:
        return "BB"
    else:
        return()

def findplayeraction(box):
    playerim = ImageGrab.grab(box)
    r, g, b = playerim.getpixel((30,0))
    rgbint = r*256^2 + g*256 + b

    if abs(rgbint - PLAYERFOLDRGB) <=1000:
        return "X"
    elif abs(rgbint - PLAYERCALLRGB) <=1000:
        return "C"
    elif abs(rgbint - PLAYERRAISERGB) <=1000:
        return "R"
    elif abs(rgbint - PLAYERALLINRGB) <=1000:
        return "A"
    elif abs(rgbint - PLAYERSBRGB) <=10:
        return "SB"
    elif abs(rgbint - PLAYERBBRGB) <=10:
        return "BB"
    else:
        return

if __name__ == "__main__":
    P1ACTIONPOS = (114,270,177,271)
    P2ACTIONPOS = (37,200,101,201)
    P3ACTIONPOS = (37,136,101,137)
    P4ACTIONPOS = (157,79,221,80)
    P5ACTIONPOS = (292,79,355,80)
    P6ACTIONPOS = (422,136,486,137)
    P7ACTIONPOS = (422,200,486,201)
    P8ACTIONPOS = (334,270,397,271)

    PLAYERFOLDRGB = 34776
    PLAYERCALLRGB = 54574
    PLAYERRAISERGB = 32774
    PLAYERALLINRGB = 65026
    PLAYERSBRGB = 115
    PLAYERBBRGB = 173

    #printcursorpoint()
    #playerim = ImageGrab.grab(P3ACTIONPOS)
    #findplayeraction(P5ACTIONPOS)
    #print("1" + str(findplayeraction(P1ACTIONPOS)))
    #print("2" + str(findplayeraction(P2ACTIONPOS)))
    #print("3" + str(findplayeraction(P3ACTIONPOS)))
    #print("4" + str(findplayeraction(P4ACTIONPOS)))
    #print("5" + str(findplayeraction(P5ACTIONPOS)))
    #print("6" + str(findplayeraction(P6ACTIONPOS)))
    #print("7" + str(findplayeraction(P7ACTIONPOS)))
    #print("8" + str(findplayeraction(P8ACTIONPOS)))

    print("1" + str(findplayeraction2(P1ACTIONPOS)))
    print("2" + str(findplayeraction2(P2ACTIONPOS)))
    print("3" + str(findplayeraction2(P3ACTIONPOS)))
    print("4" + str(findplayeraction2(P4ACTIONPOS)))
    print("5" + str(findplayeraction2(P5ACTIONPOS)))
    print("6" + str(findplayeraction2(P6ACTIONPOS)))
    print("7" + str(findplayeraction2(P7ACTIONPOS)))
    print("8" + str(findplayeraction2(P8ACTIONPOS)))

    #Im = Image.open("Actions-Raise.jpg")
    #r, g, b = Im.getpixel((30,0))
    #print(str(r*256^2 + g*256 + b))