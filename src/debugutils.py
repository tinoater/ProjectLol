__author__ = 'Ahab'

import win32gui
import time

#DEBUG functions
def printcursorpoint(t=5):
    starttime = time.time()
    while time.time() <= starttime + t:
        print(win32gui.GetCursorPos())
        time.sleep(0.1)