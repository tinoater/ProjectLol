__author__ = 'Ahab'

import math
import csv
import operator
import functools
import random
from PIL import Image, ImageFilter, ImageGrab, ImageEnhance, ImageChops
import time
import psycopg2
import fileinput
import linecache
import logging
import logging.config

import constants as c
import nlhutils

# TODO - after tests are written refactor all the variable names

class Card:

    def __init__(self, rank, suit):
        if rank not in c.RANK_DICT:
            raise Exception("Card rank invalid")
        if suit not in c.SUIT_DICT:
            raise Exception("Card suit invalid")
        self._rank = rank
        self._suit = suit

    def __eq__(self, other):
        if other == None:
            return False
        return (self._rank == other.getRank() and self._suit == other.getSuit())

    def __str__(self):
        return c.RANK_DICT[self._rank]+ c.SUIT_DICT[self._suit]

    def getRank(self):
        return (self._rank)

    def getSuit(self):
        return (self._suit)

    def getCard(self):
        return (self.getRank(), self.getSuit())

class Hand:
    def __init__(self, *cards):
    #TODO change the *cards so its standard
        self._cards = []
        for card in cards:
            self._cards.append(card)
        self.numCards = len(self._cards)
        if self.numCards == 2:
            self.setPreHandValue()
            self.sharedCards = []
        elif self.numCards >= 5:
            self.setPostHandValue()
        self.PreFlopOdds = 0
        self.PostFlopOdds = 0
    #TODO update this so the sharedCards are read from the *cards input

    def __add__(self, other):
        self._cards.append(other)
        self.numCards = len(self._cards)
        if self.numCards >= 3:
            self.sharedCards.append(other)
        return True

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

    def addSharedCards(self, cards):
        for each in cards:
            self.__add__(each)
        if self.numCards >=2:
            self.setPostHandValue()

    def setPreHandValue(self):
        if self.numCards != 2:
            raise Exception("Trying to set PreHandValue with more than two cards")

        if self._cards[0].getSuit() == self._cards[1].getSuit():
            self.suitedInd = 1
        else:
            self.suitedInd = 0

        self.connectedInd = 0
        self.oneSpaceConnectedInd = 0
        self.PremInd = 0
        self.highcard = max(self._cards[0].getRank(), self._cards[1].getRank())
        self.lowcard = min(self._cards[0].getRank(), self._cards[1].getRank())

        if abs(self._cards[0].getRank() - self._cards[1].getRank()) == 1:
            self.connectedInd = 1
        elif abs(self._cards[0].getRank() - self._cards[1].getRank()) == 2:
            self.oneSpaceConnectedInd = 1
            if self._cards[0].getRank() == 14 and self._cards[1].getRank() == 2:
                self.connectedInd = 1
            elif self._cards[1].getRank() == 14 and self._cards[0].getRank() == 2:
                self.connectedInd = 1
            elif self._cards[1].getRank() == 14 and self._cards[0].getRank() == 3:
                self.oneSpaceConnectedInd = 1
            elif self._cards[0].getRank() == 14 and self._cards[1].getRank() == 3:
                self.oneSpaceConnectedInd = 1

        if self._cards[0].getRank() == self._cards[1].getRank():
            self.PPInd = 1
            self.PPCard = self._cards[0].getRank()
        else:
            self.PPInd = 0
            self.PPCard = 0

        if self.PPInd == 1 and self.PPCard in c.PREM_PAIRS:
            self.PremInd = 1
        elif self.suitedInd == 1:
            if (self._cards[0].getRank() == 14 and self._cards[1].getRank() == 13):
                self.PremInd =  1
            elif (self._cards[1].getRank() == 14 and self._cards[0].getRank() == 13):
                self.PremInd =  1
        else:
            self.PremInd = 0

        self.preFlopOdds10 = self.getPreHandOdds(10)

    def setPostHandValue(self):
        card_list = []
        rank_list = []
        suit_list = []
        self.FlushInd = 0
        self.FlushSuit = 0
        for each in self._cards:
            card_list.append([each.getRank(),each.getSuit()])
            rank_list.append(each.getRank())
            suit_list.append(each.getSuit())
        card_list = sorted(card_list, key=lambda tup: tup[0], reverse = True)

        #Check for flushInd
        self.FlushInd = 0
        self.FlushSuit = 0
        for i in c.SUIT_DICT:
            if suit_list.count(i) >= 5:
                self.FlushInd = 1
                self.FlushSuit = i
                self.HighCard = max([e1 for (e1,e2) in card_list if e2 == self.FlushSuit])

        #Check for straightInd
        straight_list = sorted(list(set(rank_list)), reverse = True)
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
            straight_list = sorted([1 if x==14 else x for x in straight_list], reverse = True)
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
        for i in c.RANK_DICT:
            if rank_list.count(i) == 4:
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
        for i in sorted(list(c.RANK_DICT), reverse = True):
            if rank_list.count(i) == 3:
                self.TripInd = 1
                self.TripRank = i
                #Check for full house
                fh_list = [x for x in rank_list if x != i]
                for j in sorted(list(c.RANK_DICT), reverse = True):
                    if fh_list.count(j) == 2:
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
        for i in sorted(list(c.RANK_DICT), reverse = True):
            if rank_list.count(i) == 2:
                self.Pair1Rank = i
                #Check for second pair house
                p2_list = [x for x in rank_list if x != i]
                for j in range(max(c.RANK_DICT),min(c.RANK_DICT),-1):
                    if p2_list.count(j) == 2:
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
        #TODO move to a new variable called FlushHighCard?
        self.HighCard = 0
        for i in sorted(list(c.RANK_DICT), reverse = True):
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
            cardList.append(each)
        return cardList

    def getPreHandSimple(self):
        if self.PPInd == 1:
            suited_ind = ''
        elif self.suitedInd == 1:
            suited_ind = 's'
        else:
            suited_ind = 'o'

        return c.RANK_DICT[max(self._cards[0].getRank(),self._cards[1].getRank())] \
               + c.RANK_DICT[min(self._cards[0].getRank(),self._cards[1].getRank())]+suited_ind

        #TODO change this to a setPreHandOdds function
        #TOD the getPreHandsOdds function should just return these

    def getPreHandOdds(self,players):
        target_players = players
        odds = 0
        targethand = self.getPreHandSimple()

        pf_file = open(c.MEDIA_DIR + c.PF_ODDS_FILENAME,"r")
        pf_reader = csv.reader(pf_file)

        for row in pf_reader:
            if row[0] == targethand:
                odds = float(row[int(target_players) - 1])

        pf_file.close()
        self.PreFlopOdds = odds
        return odds

    def getPostCurrentHandString(self):
        HandOutput = c.HAND_DICT[self.PostHandType]
        if self.PostHandType == 2:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.HighCard] + " high"
        elif self.PostHandType == 3:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.QuadRank] + "s"
        elif self.PostHandType == 4:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.TripRank] + "s over " + c.RANK_DICT[self.Pair1Rank]
        elif self.PostHandType == 5:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.HighCard]
        elif self.PostHandType == 6:
            HandOutput = HandOutput + " High card " + c.RANK_DICT[self.StraightHead]
        elif self.PostHandType == 7:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.TripRank] + "s"
        elif self.PostHandType == 8:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.Pair1Rank] + "s and " + c.RANK_DICT[self.Pair2Rank] + "s"
        elif self.PostHandType == 9:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.Pair1Rank] + "s"
        elif self.PostHandType == 10:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.HighCard]
        return HandOutput

class Deck:
    def __init__(self):
        self._Deck = []
        for rank in c.RANK_DICT:
            for suit in c.SUIT_DICT:
                c = Card(rank,suit)
                self._Deck.append(c)

    def shuffle(self):
        random.shuffle(self._Deck)

class Player:
    def __init__(self,seat,name,cash,stats):
        self.seat = seat
        self.name = name
        self.cash = cash
        self.stats = stats
        self.bHist = [[],[],[],[]]
        self.FoldedInd = 0

    def debugPlayerInfo(self):
        string = self.name
        string += " in seat " + str(self.seat)
        string += " with cash " + str(self.cash)
        string += " with betting history:" + str(self.bHist)

        return string

class Stats:
    def __init__(self, hands, VPIP, PFR, Call, CBet, CBet_F, CBet_C, CBet_R, CBet_T):
        self.numhands = hands
        self.VPIP = VPIP
        self.PFR = PFR
        self.Call = Call
        self.CBet = CBet
        self.CBet_F = CBet_F
        self.CBet_C = CBet_C
        self.CBet_R = CBet_R
        self.CBet_T = CBet_T

#Card functions
def findcardrank(cardimage, suitInd):
    deckfilename = c.MEDIA_DIR + "\\Deck1_" + c.SUIT_DICT[suitInd] + ".bmp"
    try:
        deckcard = Image.open(deckfilename)
    except:
        logging.critical("Unable to open deck")
        return

    xpoint = 2
    ypoint = 2
    width = 9
    height = 14
    xmove = 36
    res = []
    for i in range(0,14):
        cardbox = (xpoint, ypoint, xpoint + width, ypoint + height)
        deckcardtry = deckcard.convert("RGB")
        deckcardtry = ImageEnhance.Color(deckcardtry).enhance(0.0)
        deckcardtry = deckcardtry.filter(ImageFilter.CONTOUR)
        deckcardtry = deckcardtry.crop(cardbox)
        if c.DEBUGPRINT == True:
            deckcardtry.save("DECKCARDTRY "+ str(i+2) + c.SUIT_DICT[suitInd] +".jpg")

        rms = rmsdiff(deckcardtry, cardimage)
        #print("This is card number: " + str(i + 2) + " with difference: " + str(rms))
        res.append((i+2,rms))
        xpoint = xpoint + xmove
    res = sorted(res, key=lambda tup: tup[1])
    found = res[0][0]
    #print(res)
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

def findplayerpresent(box):
    playerim = ImageGrab.grab(box)
    sum = [[1,0],[4,0],[2,0]]
    for i, value in enumerate(playerim.histogram()):
        j = i % 256
        if i <= 256:
            sum[0][1] = sum[0][1] + j * value
        elif i <= 512:
            sum[1][1] = sum[1][1] + j * value
        else:
            sum[2][1] = sum[2][1] + j * value
    if (sum[0][1] > sum[1][1]) & (sum[0][1] > sum[2][1]):
        return 1
    else:
        return 0

def findplayeraction(box):
    playerim = ImageGrab.grab(box)
    r, g, b = playerim.getpixel((30,0))
    rgbint = r*256^2 + g*256 + b

    if abs(rgbint - c.PLAYERFOLDRGB) <=1000:
        return "X"
    elif abs(rgbint - c.PLAYERCALLRGB) <=1000:
        return "C"
    elif abs(rgbint - c.PLAYERRAISERGB) <=1000:
        return "R"
    elif abs(rgbint - c.PLAYERALLINRGB) <=1000:
        return "A"
    elif abs(rgbint - c.PLAYERSBRGB) <=10:
        return "SB"
    elif abs(rgbint - c.PLAYERBBRGB) <=10:
        return "BB"
    else:
        return

def grabcard(x):
    (left, top, right, bot) = x
    cardim = ImageGrab.grab(bbox = (left, top, right, bot))
    cardim = cardim.convert("RGB")
    return cardim

def processflopcard(cardim):
    cardim = cardim.filter(ImageFilter.CONTOUR)
    cardim = ImageEnhance.Color(cardim).enhance(0.0)
    cardim = ImageEnhance.Sharpness(cardim).enhance(2)
    cardim = cardim.crop((1,1,10,15))
    if c.DEBUGPRINT == True:
        cardim.save("Card"+str(time.time())+".jpg")
    return cardim

def grabstreetcard(box):
    cardim = grabcard(box)
    suit = findcardsuit(cardim)
    cardim = cardim.filter(ImageFilter.CONTOUR)
    (x,y) = cardim.size
    cardim = cardim.crop((1,1,x - 1,y - 1))
    cardim = ImageEnhance.Color(cardim).enhance(0.0)
    cardim = ImageEnhance.Sharpness(cardim).enhance(2)
    card = Card(findcardrank(cardim,suit),suit)
    return card

def pollforheroturn(box):
    timeout = False
    count = 0
    while timeout == False:
        playerbarim = ImageGrab.grab(box)
        playerbarim = playerbarim.convert("RGB")

        #Poll until it is heros turn
        total = [0]*256
        for i, value in enumerate(playerbarim.histogram()):
            total[i % 256] = total[i % 256] + value

        if total[255] >= sum(total)*0.6:
            return 1, findstreet(c.STREETBOXPOS)

        count = count + 1
        if c.DEBUGPRINT == True:
            if count % 10 == 0:
                logging.debug("Poll for Hero Turn sleeping " + str(count))

        if count >= 600:
            if c.DEBUGPRINT == True:
                logging.critical("Timeout - exiting Poll for Hero Turn")
            return 0
        time.sleep(0.5)

def findstreet(box):
    streetboxim = ImageGrab.grab(box)
    streetboxim = streetboxim.convert("RGB")
    streetboxim = ImageEnhance.Color(streetboxim).enhance(0.0)
    streetboxim = streetboxim.filter(ImageFilter.CONTOUR)

    #check for flop
    streetfilename = c.MEDIA_DIR + "\\0-PreFlop.jpg"
    try:
        streetim = Image.open(streetfilename)
    except:
        logging.critical("Unable to open preflop")
        return
    streetim = ImageEnhance.Color(streetim).enhance(0.0)
    streetim = streetim.filter(ImageFilter.CONTOUR)
    rms = rmsdiff(streetim, streetboxim)
    if rms <= 30:
        return 1

    #test for flop
    streetboxim = streetboxim.crop((101,0,165,12))
    streetfilename = c.MEDIA_DIR + "\\1-Flop.jpg"
    try:
        streetim = Image.open(streetfilename)
    except:
        logging.critical("Unable to open flop")
        return
    streetim = ImageEnhance.Color(streetim).enhance(0.0)
    streetim = streetim.filter(ImageFilter.CONTOUR)
    rms = rmsdiff(streetim, streetboxim)
    if rms <=30:
        return 2

    #test for turn
    streetboxim = streetboxim.crop((32,0,64,12))
    streetfilename = c.MEDIA_DIR + "\\2-Turn.jpg"
    try:
        streetim = Image.open(streetfilename)
    except:
        logging.critical("Unable to open preflop")
        return
    streetim = ImageEnhance.Color(streetim).enhance(0.0)
    streetim = streetim.filter(ImageFilter.CONTOUR)
    rms = rmsdiff(streetim, streetboxim)
    if rms <=60:
        return 3
    else:
        return 4

def getQueryResults(names):
    """Return the DB stats for a list of players"""
    namelist = []
    for each in names:
       namelist.append(each)
    if len(namelist) == 1:
        singleind = 1
    else:
        singleind = 0
    try:
        conn = psycopg2.connect(dbname = "HoldemManager2", user="postgres", host="localhost", password="postgrespass", port=5432)
    except psycopg2.Error as e:
        logging.critical("Cannot connect to DB")
        logging.debug(e)

    query = """SELECT p.playername
     , SUM(totalhands) AS Total_Hands
     , (SUM(cpr.vpiphands) * 100 / SUM(cpr.totalhands)) AS VPIP_Perc
     , (SUM(cpr.pfrhands) * 100 / SUM(cpr.totalhands)) AS PFR_Perc
     , CASE WHEN SUM(cpr.couldcoldcall) = 0 THEN -1
            ELSE (SUM(cpr.didcoldcall) * 100 / SUM(cpr.couldcoldcall))
            END AS Call_Perc
     , CASE WHEN SUM(cpr.flopcontinuationbetpossible) = 0 THEN -1
            ELSE (SUM(cpr.flopcontinuationbetmade) * 100 / SUM(cpr.flopcontinuationbetpossible))
            END AS CBet_Perc
     , CASE WHEN SUM(cpr.facingflopcontinuationbet) = 0 THEN -1
            ELSE (SUM(cpr.foldedtoflopcontinuationbet) * 100 / SUM(cpr.facingflopcontinuationbet))
            END AS CBet_Fold_Perc
     , CASE WHEN SUM(cpr.facingflopcontinuationbet) = 0 THEN -1
            ELSE (SUM(cpr.calledflopcontinuationbet) * 100 / SUM(cpr.facingflopcontinuationbet))
            END AS CBet_Call_Perc
     , CASE WHEN SUM(cpr.facingflopcontinuationbet) = 0 THEN -1
            ELSE (SUM(cpr.raisedflopcontinuationbet) * 100 / SUM(cpr.facingflopcontinuationbet))
            END AS CBet_Raise_Perc
     , CASE WHEN SUM(cpr.turncontinuationbetpossible) = 0 THEN -1
            ELSE (SUM(cpr.turncontinuationbetmade) * 100 / SUM(cpr.turncontinuationbetpossible))
            END AS CBet_Turn_Perc
  FROM players p
  JOIN compiledplayerresults cpr
    ON p.player_id = cpr.player_id
  JOIN gametypes g
    ON cpr.gametype_id = g.gametype_id
  WHERE p.playername IN ("""
    for name in namelist:
        query += "'" + name + "',"
    query = query[:-1]
    query += """)
    --AND p.pokersite_id = 12
    --AND g.istourney = FALSE
    --AND g.bigblindincents <=10
    --AND g.tablesize <=10
    --AND g.pokergametype_id = 0 --NLH
  GROUP BY p.playername"""

    #Connect to DB and run query
    cur = conn.cursor()
    cur.execute(query)
    statlist = []
    for row in cur.fetchall():
        statlist += [list(row)]
#    #append the positions
#    for each in statlist:
#        name = each[0]
#        for r in names:
#            if r == name:
#                each.append(r[1])
#    statlist.sort(key=lambda x: x[10])

    if singleind == 1:
        if len(statlist) == 0:
            #if no stats found then set to zeros
            statlist = [[0,0,0,0,0,0,0,0,0,0]]
        return(statlist[0][1:])
    else:
        return(statlist)

def getplayersfor9table888(filename,heroname = 'tinoater'):
    """Returns the players and cash of the table. Hero at 0"""

    pointer = 0
    GAMESTRING = '#Game No'
    filename = c.HAND_HISTORY_DIR + filename
    for line in fileinput.input(filename):
        if line[0:len(GAMESTRING)] == GAMESTRING:
            pointer = fileinput.lineno()
    pointer += 6

    lines = []
    for i in range(0,10):
        line = linecache.getline(filename,pointer + i)
        if line[:5] == "Seat ":
            if line[6] == ":":
                seat = int(line[5])
                name = line[8:]
            else:
                seat = int(line[5:7])
                name = line[9:]
            a = 0
            flag = True
            while flag == True:
                if name[a] == " ":
                    name = name[:a]
                    flag = False
                else:
                    a += 1
            flag = True
            i = 0
            while flag == True:
                if line[i] == "$":
                    cash = line[i+1:]
                    flag = False
                else:
                    i += 1
            flag = True
            i = 0
            while flag == True:
                if cash[i] == ")":
                    cash = cash[:i-1]
                    flag = False
                else:
                    i += 1
            lines.append([seat,name,cash])


    #For 9 people tables there is no Seat 8 for some reason
    for i in range(0,len(lines)):
        if lines[i][0] > 8:
            lines[i][0] -= 1

    maxi = max([e1 for [e1,e2,e3] in lines])
    #Now rearrange around hero
    for each in lines:
        if each[1] == heroname:
            heronum = each[0]
    for each in lines:
        if each[0] >= heronum:
            each[0] -= heronum
        else:
            each[0] += maxi - heronum

    #TODO - Look through the betting to derive current cash amounts

    lines.sort(key=lambda x: x[0])
    p=[]
    logging.debug("Beginning queries to DB")
    for i in range(0,len(lines)):
        p.append(Player(lines[i][0], lines[i][1], lines[i][2]
                        , Stats(*tuple(getQueryResults([lines[i][1]])))))
    logging.debug("DB queries finished")
    return p
