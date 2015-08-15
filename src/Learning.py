__author__ = 'Ahab'

import win32api
import win32con
import win32gui
from PIL import Image, ImageFilter, ImageGrab, ImageEnhance, ImageChops
import time
import math
import functools
import operator
import itertools

class Hand(object):
    def __init__(self):
        self.variable = 10


class Game(object):
    def __init__(self, hand):
        self.hand = hand
    def childfunc(self,value):
        return str(value) + " sommit"
    def parentfunc(self):
        value = 10
        return self.childfunc(value)


if __name__ == "__main__":
    currenthand = Hand()
    currentgame = Game(currenthand)
    print(currentgame.parentfunc())