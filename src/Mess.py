__author__ = 'Ahab'

import math
import operator
import functools
import csv
import sys
import random
import win32api
import win32con
import win32com
import win32gui
import win32ui
from PIL import Image, ImageFilter, ImageGrab, ImageEnhance, ImageChops
import time
import pyperclip
import tkinter
import os
import selectors

HAND_DICT = {1:'Royal Flush', 2:'Straight Flush', 3:'Four of a Kind', 4:'Full House', 5:'Flush', 6:'Straight'
             ,7:'Three of a Kind',8:'Two Pairs',9:'One Pair',10:'High Card'}
RANK_DICT = {2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'T',11:'J',12:'Q',13:'K',14:'A'}
SUIT_DICT = {1:'H',2:'D',3:'S',4:'C'}
CARD1POS = (215,223,245,244)
HEROCARDPOS = (220,270,288,271)
CARD2POS = (245,223,278,244)
FLOP1POS = (170,122,179,136)
FLOP2POS = (204,123,213,135)
FLOP3POS = (237,123,246,135)
FLOP4POS = (270,123,279,135)
FLOP5POS = (303,123,312,135)

FLOP1POS = (169,121,180,137)
FLOP2POS = (203,121,214,137)
FLOP3POS = (236,121,247,137)
FLOP4POS = (269,121,280,137)
FLOP5POS = (302,121,313,137)

STREETPOS = (170,123,335,135)

class Card:

    def __init__(self, rank, suit):
        self._rank = rank
        self._suit = suit

    def __eq__(self, other):
        return (self._rank == other.getRank() and self._suit == other.getSuit())

    def __str__(self):
        return RANK_DICT[self._rank]+ SUIT_DICT[self._suit]

    def getRank(self):
        return (self._rank)

    def getSuit(self):
        return (self._suit)

    def getCard(self):
        return (self.getRank(), self.getSuit())

class Hand:
    def __init__(self, *cards):
        for card in cards:
            self._cards = card
        self.numCards = len(self._cards)
        if self.numCards == 2:
            self.setPreHandValue()
        elif self.numCards >= 5:
            self.setPostHandValue()

    def __add__(self, other):
        TempList = self.getCards()
        TempList.append(other)
        self = Hand(TempList)
        return(Hand(TempList))

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __str__(self):
        string = ""
        for each in self._cards:
            string = string + str(each) + " "
        return(string)

    def setPreHandValue(self):
        card_list = []
        for each in self._cards:
            card_list = card_list + [each.getRank()]
            card_list = card_list + [each.getSuit()]

        if card_list[1] == card_list[3]:
            self.suitedInd = 1
        else:
            self.suitedInd = 0

        self.connectedInd = 0
        self.oneSpaceConnectedInd = 0

        card_list = []
        for each in self._cards:
            card_list = card_list + [each.getRank()]
            card_list = card_list + [each.getSuit()]

        if abs(int(card_list[0]) - int(card_list[2])) == 1:
            self.connectedInd = 1
        elif abs(int(card_list[0]) - int(card_list[2])) == 2:
            self.oneSpaceConnectedInd = 1
            if int(card_list[0]) == 14 and int(card_list[2]) == 2:
                self.connectedInd = 1
            elif int(card_list[2]) == 14 and int(card_list[0]) == 2:
                self.connectedInd = 1
            elif int(card_list[2]) == 14 and int(card_list[0]) == 3:
                self.oneSpaceConnectedInd = 1
            elif int(card_list[0]) == 14 and int(card_list[2]) == 3:
                self.oneSpaceConnectedInd = 1

        card_list = []
        for each in self._cards:
            card_list = card_list + [each.getRank()]
            card_list = card_list + [each.getSuit()]

        if card_list[0] == card_list[2]:
            self.PPInd = 1
        else:
            self.PPInd = 0

        card_list = []
        for each in self._cards:
            card_list = card_list + [each.getRank()]
            card_list = card_list + [each.getSuit()]

        if card_list[0] == card_list[2]:
            if card_list[0] in PREM_PARIS:
                self.PremInd = 1
        elif self.suitedInd == 1:
            if (card_list[0] == '14' and card_list[1] == '13'):
                self.PremInd =  1
            elif (card_list[1] == '14' and card_list[0] == '13'):
                self.PremInd =  1
            else:
                self.PremInd = 0

    def setPostHandValue(self):
        card_list = []
        rank_list = []
        suit_list = []
        self.FlushInd = 0
        self.FlushSuit = 0
        for each in self._cards:
            card_list.append([[each.getRank()],[each.getSuit()]])
            rank_list.append(int(each.getRank()))
            suit_list.append(each.getSuit())
        card_list = sorted(card_list, key=lambda tup: tup[0], reverse = True)

        #Check for flushInd
        self.FlushInd = 0
        self.FlushSuit = 0
        for i in range(1,5):
            count = suit_list.count(i)
            if count >= 5:
                self.FlushInd = 1
                self.FlushSuit = str(i)
                self.HighCard = 0
                for (e1,e2) in card_list:
                    if e2 == self.FlushSuit:
                        if e1 > self.HighCard:
                            self.HighCard = e1

        #Check for straightInd
        rank_list = sorted(rank_list, reverse = True)
        straight_list = []
        for i in rank_list:
            if straight_list.count(i) == 0:
                straight_list.append(i)
        i = 0
        self.StraightInd = 0
        self.StraightHead = 0
        while i+5 <= straight_list.__len__():
            if straight_list[i] - straight_list[i+4] == 4:
                self.StraightInd = 1
                self.StraightHead = straight_list[i]
            i = i+1

        if self.StraightInd == 0:
            #check for low card ace straight
            straight_list = [1 if x==14 else x for x in straight_list]
            straight_list = sorted(straight_list, reverse = True)
            i = 0
            while i+5 <= straight_list.__len__():
                if straight_list[i] - straight_list[i+4] == 4:
                    self.StraightInd = 1
                    self.StraightHead = straight_list[i]
                i = i + 1

        if self.FlushInd == 1 and self.StraightInd == 1 and self.StraightHead == 14:
            self.PostHandType = 1
            self.PostHandValue = 1
            return True
        elif self.FlushInd == 1 and self.StraightInd == 1:
            self.PostHandType = 2
            self.PostHandValue = 2 - self.StraightHead + 13 #10
            return True

        #Check for 4 of a kind
        self.QuadInd = 0
        self.QuadRank = 0
        for i in range(2,15):
            count = rank_list.count(i)
            if count == 4:
                self.QuadInd = 1
                self.QuadRank = i
                self.PostHandType = 3
                self.PostHandValue = 11 - self.QuadRank + 14 #23
                return True

        #Check for 3 of a kind
        self.TripInd = 0
        self.TripRank = 0
        self.FHInd = 0
        self.Pair1Rank = 0
        for i in range(14,1,-1):
            count = rank_list.count(i)
            if count == 3:
                self.TripInd = 1
                self.TripRank = i
                #Check for full house
                fh_list = [x for x in rank_list if x != i]
                for j in range(14,1,-1):
                    count2 = fh_list.count(j)
                    if count2 == 2:
                        self.FHInd = 1
                        self.TripInd = 0
                        self.Pair1Rank = j
                if self.Pair1Rank != 0:
                    break
            if self.Pair1Rank != 0:
                break

        if self.FHInd == 1:
            self.PostHandType = 4
            self.PostHandValue = 24 - (self.TripRank - 1) * 12 - (self.Pair1Rank - 1) + 168 #178
            return True
        elif self.FlushInd == 1:
            self.PostHandType = 5
            self.PostHandValue = 179 - self.HighCard + 14 #186
            return True
        elif self.StraightInd == 1:
            self.PostHandType = 6
            self.PostHandValue = 187 - self.StraightHead + 14 #196
            return True
        elif self.TripInd == 1:
            self.PostHandType = 7
            self.PostHandValue = 197 - self.TripRank + 14 #209
            return True

        #Check for pairs
        self.Pair1Rank = 0
        self.Pair2Rank = 0
        for i in range(14,1,-1):
            count = rank_list.count(i)
            if count == 2:
                self.Pair1Rank = i
                #Check for second pair house
                p2_list = [x for x in rank_list if x != i]
                for j in range(14,1,-1):
                    count2 = p2_list.count(j)
                    if count2 == 2:
                        self.Pair2Rank = j
                    if self.Pair2Rank != 0:
                        break
            if self.Pair2Rank != 0:
                break

        if self.Pair1Rank != 0 and self.Pair2Rank != 0:
            self.PostHandType = 8
            self.PostHandValue = 210 - (self.Pair1Rank - 1) - (self.Pair2Rank - 1) + 25 #232
            return True
        elif self.Pair1Rank != 0:
            self.PostHandType = 9
            self.PostHandValue = 233 - self.Pair1Rank + 14 #245
            return True

        self.HighCard = 0
        for i in range(14,1,-1):
            count = rank_list.count(i)
            if count >= 1:
                self.HighCard = i
            if self.HighCard != 0:
                break
        self.PostHandType = 10
        self.PostHandValue = 247 - self.HighCard + 14 #254
        return True

    def getCards(self):
        cardList = []
        for each in self._cards:
            cardList = cardList + [each]
        return(cardList)

    def getPreHandSimple(self):
        card_list = []
        suited_ind = ''
        for each in self._cards:
            card_list = card_list + [each.getRank()]
            card_list = card_list + [each.getSuit()]
        if self.PPInd == 1:
            suited_ind == ''
        elif self.suitedInd == 1:
            suited_ind = 's'
        else:
            suited_ind = 'o'
        #take the numbers
        card_list.__delitem__(1)
        card_list.__delitem__(2)
        #sort desc.
        card_list.sort(reverse=True)

        return RANK_DICT[card_list[0]]+RANK_DICT[card_list[1]]+suited_ind

    def getPreHandOdds(self,players):
        target_players = players
        odds = 0
        if len(self._cards) != 2:
            return False

        targethand = self.getPreHandSimple()

        pf_file = open(PF_ODDS_FILENAME,"r")
        pf_reader = csv.reader(pf_file)

        for row in pf_reader:
            if row[0] == targethand:
                odds = float(row[int(target_players) - 1])

        pf_file.close()

        return odds

    def getPostCurrentHandString(self):
        HandOutput = HAND_DICT[self.PostHandType]
        if self.PostHandType == 2:
            HandOutput = HandOutput + " " + RANK_DICT[self.HighCard] + " high"
        elif self.PostHandType == 3:
            HandOutput = HandOutput + " " + RANK_DICT[self.QuadRank] + "s"
        elif self.PostHandType == 4:
            HandOutput = HandOutput + " " + RANK_DICT[self.TripRank] + "s over " + RANK_DICT[self.Pair1Rank]
        elif self.PostHandType == 5:
            HandOutput = HandOutput + " " + RANK_DICT[self.HighCard]
        elif self.PostHandType == 6:
            HandOutput = HandOutput + " High card " + RANK_DICT[self.StraightHead]
        elif self.PostHandType == 7:
            HandOutput = HandOutput + " " + RANK_DICT[self.TripRank] + "s"
        elif self.PostHandType == 8:
            HandOutput = HandOutput + " " + RANK_DICT[self.Pair1Rank] + "s and " + RANK_DICT[self.Pair2Rank] + "s"
        elif self.PostHandType == 9:
            HandOutput = HandOutput + " " + RANK_DICT[self.Pair1Rank] + "s"
        elif self.PostHandType == 10:
            HandOutput = HandOutput + " " + RANK_DICT[self.HighCard]
        return HandOutput

def click(x,y):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def move(p, t=1):
    (x, y) = p
    (x1,y1) = win32api.GetCursorPos()
    (dx,dy) = (x - x1,y - y1)
    for i in range(1,100):
        x2 = math.floor(x1 + i * (dx / 100))
        y2 = math.floor(y1 + i * (dy / 100))
        win32api.SetCursorPos((x2, y2))
        time.sleep(t/100)

def printcursorpoint(t=5):
    starttime = time.time()
    while time.time() <= starttime + t:
        print(win32gui.GetCursorPos())
        time.sleep(0.1)

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
    emptylist = [(e1,e2,e3,e4,e5,e6,e7) for (e1,e2,e3,e4,e5,e6,e7) in emptylist]
    #print(emptylist)
    #print(win32gui.GetClassName(emptylist[0][0]))
    return(emptylist)

def setwindowposition():
    win32gui.MoveWindow(gethandleofNLH(), 0, 0, 502, 362, 1)

def findcardrank(cardimage, suitInd):
    deckfilename = "Deck1_" + SUIT_DICT[suitInd] + ".bmp"
    try:
        deckcard = Image.open(deckfilename)
    except:
        print("Unable to open deck")
        return

    xpoint = 2
    ypoint = 2
    width = 10
    height = 15
    xmove = 36
    res = []
    for i in range(0,14):
        cardbox = (xpoint, ypoint, xpoint + width, ypoint + height)
        deckcardtry = deckcard.convert("RGB")
        ImageEnhance.Color(deckcardtry).enhance(0.0)
        deckcardtry = deckcardtry.filter(ImageFilter.CONTOUR)
        deckcardtry = deckcardtry.crop(cardbox)
        rms = rmsdiff(deckcardtry, cardimage)
        #print("This is card number: " + str(i + 2) + " with difference: " + str(rms))
        res.append((i+2,rms))
        xpoint = xpoint + xmove
    res = sorted(res, key=lambda tup: tup[1])
    found = res[0][0]
    print(res)
    return(found)

def rmsdiff(im1, im2):
    "Calculate the root-mean-square difference between two images"

    h = ImageChops.difference(im1, im2).histogram()

    # calculate rms
    return math.sqrt(functools.reduce(operator.add,
        map(lambda h, i: h*(i**2), h, range(256))
    ) / (float(im1.size[0]) * im1.size[1]))

def findcardsuit(cardimage):
    sum = [[1,0],[4,0],[2,0]]
    for i, value in enumerate(cardimage.histogram()):
        j = i % 256
        if i <= 256:
            sum[0][1] = sum[0][1] + j * value
        elif i <= 512:
            sum[1][1] = sum[1][1] + j * value
        else:
            sum[2][1] = sum[2][1] + j * value

    #if all similar then a spade
    average = (sum[0][1] + sum[1][1] + sum[2][1])/3
    if abs(average - sum[0][1]) <= 500:
        if abs(average - sum[1][1]) <= 500:
            if abs(average - sum[2][1]) <= 500:
                return 3

    sum = sorted(sum, key=lambda tup:tup[1], reverse=True)
    return sum[0][0]

def grabcard(x):
    (left, top, right, bot) = x
    cardim = ImageGrab.grab(bbox = (left, top, right, bot))
    cardim = cardim.convert("RGB")
    return cardim

def processcard(cardim):
    cardim = cardim.filter(ImageFilter.CONTOUR)
    cardim = ImageEnhance.Color(cardim).enhance(0.0)
    cardim = ImageEnhance.Sharpness(cardim).enhance(10.0)
    cardim = cardim.crop((1,1,10,15))
    cardim.save("Card"+str(time.localtime())+".jpg")
    return cardim

def mess():
    try:
        myimage = Image.open("pic.jpg")
    except:
        print("Unable to open Image")

    print("The size of the picture is: ")
    print(str(myimage.format), str(myimage.size), str(myimage.mode))

    #changed = myimage.filter(ImageFilter.BLUR)
    #changed.show()

    try:
        screenshot = ImageGrab.grab(bbox=(10,50,100,500))
        #screenshot = screenshot.filter((ImageFilter.CONTOUR))

        shot2 = ImageGrab.grab(bbox = (10,50,100,500))
        if screenshot == shot2:
            print("Theyre the same!")
        else:
            print("They ain't the same")

        screenshot.show()
    except:
        print("Couldn't take screenshot")


    emptylist =[]
    win32gui.EnumWindows(callback, emptylist)
    emptylist = [(e1,e2,e3,e4,e5,e6,e7) for (e1,e2,e3,e4,e5,e6,e7) in emptylist if "NLH" in e2]
    print(emptylist)
    print(win32gui.GetClassName(emptylist[0][0]))

    emptylist2 = []
    win32gui.EnumChildWindows(2884084, callback, emptylist2)
    print(emptylist2)

    for (e1,e2,e3,e4,e5,e6,e7) in emptylist2:
        screenshot = ImageGrab.grab(bbox = (e3,e4,e3 + e5,e4 + e6))
        screenshot.show(title = str(e1) + str(e7))
        win32gui.SetActiveWindow(emptylist[0][0])
        time.sleep(.5)

def findstreet(box):
    streetboxim = ImageGrab.grab(box)
    streetboxim = streetboxim.convert("RGB")
    streetboxim = ImageEnhance.Color(streetboxim).enhance(0.0)
    streetboxim = streetboxim.filter(ImageFilter.CONTOUR)

    #check for flop
    streetfilename = "0-PreFlop.jpg"
    try:
        streetim = Image.open(streetfilename)
    except:
        print("Unable to open preflop")
        return
    streetim = ImageEnhance.Color(streetim).enhance(0.0)
    streetim = streetim.filter(ImageFilter.CONTOUR)
    rms = rmsdiff(streetim, streetboxim)
    if rms <= 30:
        return 1

    #test for flop
    streetboxim = streetboxim.crop((101,0,165,12))
    streetfilename = "1-Flop.jpg"
    try:
        streetim = Image.open(streetfilename)
    except:
        print("Unable to open flop")
        return
    streetim = ImageEnhance.Color(streetim).enhance(0.0)
    streetim = streetim.filter(ImageFilter.CONTOUR)
    rms = rmsdiff(streetim, streetboxim)
    print(rms)
    if rms <=30:
        return 2

    #test for turn
    streetboxim = streetboxim.crop((32,0,64,12))
    streetfilename = "2-Turn.jpg"
    try:
        streetim = Image.open(streetfilename)
    except:
        print("Unable to open preflop")
        return
    streetim = ImageEnhance.Color(streetim).enhance(0.0)
    streetim = streetim.filter(ImageFilter.CONTOUR)
    rms = rmsdiff(streetim, streetboxim)
    if rms <=60:
        return 3
    else:
        return 4

def dokey(key1,key2=None):
#shift - 16, ctrl = 17, left = 37, right = 39, space = 32
    if key2 == None:
        win32api.keybd_event(key1,0,0,0)
        win32api.keybd_event(key1,0,win32con.KEYEVENTF_KEYUP,0)
    else:
        win32api.keybd_event(key2,0,0,0)
        win32api.keybd_event(key1,0,0,0)
        win32api.keybd_event(key1,0,win32con.KEYEVENTF_KEYUP,0)
        win32api.keybd_event(key2,0,win32con.KEYEVENTF_KEYUP,0)

#class GUITHREADINFO(Structure):
# _fields_ = [
#     ("cbSize", c_ulong),
#     ("flags", c_ulong),
#     ("hwndActive", c_ulong),
#     ("hwndFocus", c_ulong),
#     ("hwndCapture", c_ulong),
#     ("hwndMenuOwner", c_ulong),
#     ("hwndMoveSize", c_ulong),
#     ("hwndCaret", c_ulong),
#     ("rcCaret", RECT)
# ]

#print(gethandleofNLH())
#gui = GUITHREADINFO(cbSize = sizeof(GUITHREADINFO))
#hwnd = 3409688
#thing = win32gui.SendMessage(hwnd,win32con.WM_GETTEXTLENGTH, 0, 0)
#print(thing)
#buffer = win32gui.PyMakeBuffer(thing)
#win32gui.SendMessage(hwnd,win32con.WM_GETTEXT, thing, buffer)
#txt = buffer[:thing]
#print(txt)

#wnd = win32ui.GetForegroundWindow()
#print(wnd.GetWindowText())
##win32api.keybd_event(win32con.LEFT_CTRL_PRESSED, ord('o'), win32con.KEYEVENTF_EXTENDEDKEY, 0)
#shell = win32com.client.Dispatch("WScript.Shell")
#shell.AppActivate

#print("Start")
#time.sleep(2)
#dokey(0x41,17)
#dokey(0x43,17)
#variable = pyperclip.paste()
#print(variable)
#print("Done")

#top = tkinter.Tk()
#top.mainloop()

#r_fd, w_fd = os.pipe()

#p = select()
#p.register(r_fd, select.POLLIN)

#os.write(w_fd, 'X') # Put something in the pipe so p.poll() will return

#while True:
#    events = p.poll(100)
#    for e in events:
#        print(e)
#        os.read(r_fd, 1)

f = open(r"C:\Users\Ahab\AppData\Roaming\PacificPoker\HandHistory\tinoater\888poker20150712 Harare $0.01-$0.02 No "
            r"Limit Holdem.txt")

sel = selectors.SelectSelector()

sel.register(sel,f,selectors.EVENT_READ)


#for line in file:
#    print(line, end=",")

#[Sb Bb  1st 2nd 3rd 4th 5th 6th But ]
#[?  ?   0   1   1   2   0   1   H   ]
#Expected