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

import screenutils

class Card:

    def __init__(self, rank, suit):
        self._rank = rank
        self._suit = suit

    def __eq__(self, other):
        if other == None:
            return False
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
        self.PreFlopOdds = 0
        self.PostFlopOdds = 0

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
        self.PremInd = 0

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
            self.PPCard = card_list[0]
        else:
            self.PPInd = 0
            self.PPCard = 0

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
            card_list.append([each.getRank(),each.getSuit()])
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
                self.FlushSuit = i
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
        if self.PreFlopOdds != 0:
            return self.PreFlopOdds
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
        self.PreFlopOdds = odds
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

class Deck:
    def __init__(self):
        self._Deck = []
        for rank in range(2,15):
            for suit in [1,2,3,4]:
                c = Card(rank,suit)
                self._Deck.append(c)

    def shuffle(self):
        random.shuffle(self._Deck)

    def print(self):
        for each in self._Deck:
            each.printCard()

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

class Game:
    def __init__(self, players):
        self.player = players
        self.potsize = 0
        self.initnumplayers = len(self.player)
        self.position = None

class BettingStrat:
    def __init__(self, game, hand, aggro = 0):
    #TODO need to implement the aggro parameter
        self.game = game
        self.preFlopOdds = hand.PreFlopOdds
        self.postFlopOdds = hand.PostFlopOdds
        self.position = game.position
        if hand.PPInd == 1:
            self.drawInd = 1
        else:
            self.drawInd = 0
        if hand.PremInd == 1:
            self.madeInd = 1
        else:
            self.madeInd = 0
        if hand._cards[0].getRank() == 14 & hand._cards[1].getRank() == 14:
            self.BHInd = 1
        else:
            self.BHInd = 0
        if hand.suitedInd == 1 or hand.connectedInd == 1:
            self.drawInd = 1
        self.PPInd = hand.PPInd
        self.aggro = aggro
        self.bettingHist=[[],[],[],[]]
        self.street = 0
        self.streetcount = -1
        self.totalhandbet = 0
        self.potamount = 0
        self.herocash = 0

    def getUnMovedPlayers(self):
        unMovedPlayers = 0
        heropos = self.position
        if self.street == 0:
            for each in self.game.player:
                if each.FoldedInd != 0 & ((each.seat > heropos) or (each.seat in (0,1))):
                    unMovedPlayers += 1
        else:
            for each in self.game.player:
                if each.FoldedInd != 0 & each.seat > heropos:
                    unMovedPlayers += 1

        return unMovedPlayers

    def betPreFlop(self,currbet,potamount,herocash):
        #comment
        self.potamount = potamount
        self.herocash = herocash
        self.streetcount =+ 1
        wait = random.uniform(1,4)
        logging.info("Pot amount is " + str(potamount))
        logging.info("Call bet amount is " + str(currbet))
        #TODO - Incorporate position into betting strat
        #Set up the oppactions sumary list
        oppactions = []
        for each in self.game.player:
            try:
                oppactions.extend(each.bHist[0][self.streetcount])
            except IndexError:
                oppactions.extend(each.bHist[0])
        movedPlayers = oppactions.count("R") + oppactions.count("A") + oppactions.count("C")
        unmovedPlayers = self.getUnMovedPlayers()

        #Try to go all in with Aces pre-flop
        if self.BHInd == 1:
            logging.info("Have Aces")
            bet = round(currbet * (random.uniform(2,3)))
            logging.info("Herocash:" +str(self.herocash) + " desired raise:" + str(bet))
            if self.herocash <= bet:
                logging.info("Have to go all in")
                self.bettingHist[0].extend(("A",0))
                return 3, 0, wait
            if self.herocash - bet <= bet*RAISE_TO_ALLIN_THRESH:
                logging.info("Rounding up to all in")
                self.bettingHist[0].extend(("A",0))
                return 3, 0, wait
            self.totalhandbet += bet
            wait = random.uniform(3,4)
            logging.info("Raising")
            self.bettingHist[0].extend(("R",bet))
            return 2, bet, wait

        #Premium hands - push for max bet
        if self.madeInd == 1:
            logging.info("Have Premium Hand")
            if oppactions.count("R") + oppactions.count("A") == 0:
                bet = round(currbet * (random.uniform(2,3)))
                self.totalhandbet += bet
                logging.info("Open pot with a raise")
                self.bettingHist[0].extend(("R",bet))
                return 2, bet, wait
            else:
                if currbet <= 3 * BIGBLIND:
                    bet = round(currbet * (random.uniform(2,3)))
                    self.totalhandbet += bet
                    logging.info("Will reraise as currbet:" + str(currbet))
                    self.bettingHist[0].extend(("R",bet))
                    return 2, bet, wait
                else:
                    if random.uniform(0,1) <= PF_PREM_RERAISE_PERC:
                        logging.info("Currbet is large, but will reraise anyway. Parameter:" + str(PF_PREM_RERAISE_PERC))
                        bet = round(currbet * (random.uniform(2,3)))
                        self.totalhandbet += bet
                        self.bettingHist[0].extend(("R",bet))
                        return 2, bet, wait
                    else:
                        logging.info("Will call")
                        self.totalhandbet += currbet
                        self.bettingHist[0].extend(("C",currbet))
                        return 1, 0, wait


        #Pocket pairs - draw with all pairs if its cheap/many players. Aggressive with larger pairs
        if self.PPInd == 1:
            logging.info("Have pocket pairs")
            if movedPlayers == 0:
                logging.info("First to enter the pot")
                if self.hand.PPCard >= 9:
                    logging.info("Strong pair so raise")
                    bet = round(BIGBLIND * (random.uniform(2,3)))
                    self.totalhandbet += bet
                    self.bettingHist[0].extend(("R",bet))
                    return 2, bet, wait
                else:
                    if random.uniform(0,1) <= PF_PP_BELOW_9_RAISE:
                        bet = round(BIGBLIND * (random.uniform(2,3)))
                        self.totalhandbet += bet
                        logging.info("Weak pair but raise anyway. Parameter:" + str(PF_PP_BELOW_9_RAISE))
                        self.bettingHist[0].extend(("R",bet))
                        return 2, bet, wait
                    elif random.uniform(0,1) <= PF_PP_BELOW_9_CALL:
                        logging.info("Call to draw to set")
                        self.totalhandbet += currbet
                        self.bettingHist[0].extend(("C",currbet))
                        return 1, 0, wait
                    else:
                        self.bettingHist[0].extend(("X",0))
                        return 0, 0, wait
            else:
                logging.info("Other players are in the pot. Prediction of pot size is:" + str(PF_SMALL_PAIR * ((movedPlayers * PF_CALL_AFTER_RAISE_PERC) + (unmovedPlayers * PF_CALL_PERC))))
                if PF_SMALL_PAIR / 10 * ((movedPlayers * PF_CALL_AFTER_RAISE_PERC) + (unmovedPlayers * PF_CALL_PERC)) \
                        >= currbet:
                    self.totalhandbet += currbet
                    logging.info("Call worth it")
                    self.bettingHist[0].extend(("C",currbet))
                    return 1, 0, wait
                else:
                    logging.info("Call not worth it")
                    self.bettingHist[0].extend(("X",0))
                    return 0, 0, wait

        #Flush or Straight Draws
        if self.drawInd == 1:
            logging.info("Have a flush or straigt draw")
            logging.info("Prediction of pot size is:" + str(PF_FL_STR_DRAW * ((movedPlayers * PF_CALL_AFTER_RAISE_PERC)
                                                                              + (unmovedPlayers * PF_CALL_PERC))
                                                                                + potamount))
            if PF_FL_STR_DRAW / 10 * ((movedPlayers * PF_CALL_AFTER_RAISE_PERC) + (unmovedPlayers * PF_CALL_PERC)) + potamount \
                    >= currbet:
                self.totalhandbet += currbet
                logging.info("Call worth it")
                self.bettingHist[0].extend(("C",currbet))
                return 1, 0, wait
            else:
                logging.info("Call not worth it")
                self.bettingHist[0].extend(("X",0))
                return 0, 0, wait
        #All other hands
        logging.info("Misc. hands")
        if movedPlayers == 0:
            logging.info("No one has entered pot")
            logging.info("Hand Odds are:" + str(self.preFlopOdds / 100) + " Adjusted odds are:"
                         + str((self.preFlopOdds * random.uniform(0,1))) + " threshold is:" + str(PF_OTHER_HANDS_OPEN))
            if self.preFlopOdds >= 10 & (self.preFlopOdds / 100 * random.uniform(0,1) <= PF_OTHER_HANDS_OPEN):
                bet = round(BIGBLIND * (random.uniform(2,3)))
                self.totalhandbet += bet
                logging.info("Open raise")
                self.bettingHist[0].extend(("R",bet))
                return 2, bet, wait

        if movedPlayers != 0:
            logging.info("People have entered the pot")
            logging.info("Hand Odds are:" + str(self.preFlopOdds) + " Adjusted odds are:"
                         + str((self.preFlopOdds / 100 * random.uniform(0,1))) + " threshold is:" + str(PF_OTHER_HANDS_CALL))
            if self.preFlopOdds >= 10 & (self.preFlopOdds / 100 * random.uniform(0,1) <= PF_OTHER_HANDS_CALL):
                if currbet <= 3 * BIGBLIND:
                    self.totalhandbet += currbet
                    self.bettingHist[0].extend(("C",currbet))
                    return 1, 0, wait

        #If no one has opened the pot then try to steal
        if movedPlayers == 0:
            logging.info("No one has entered the pot")
            logging.info("Steal threshold is:" + str(PF_STEAL))
            if unmovedPlayers <=3 & (random.uniform(0,1) <= PF_STEAL):
                bet = round(BIGBLIND * (random.uniform(2,3)))
                self.totalhandbet += bet
                logging.info("Attempt to steal")
                self.bettingHist[0].extend(("R",bet))
                return 2, bet, wait

        #Else just fold
            logging.info("Just fold")
            self.bettingHist[0].extend(("X",0))
            return 0, 0, wait

    def betFlop(self,currbet,potamount,herocash):

#Card functions
def findcardrank(cardimage, suitInd):
    deckfilename = "Deck1_" + SUIT_DICT[suitInd] + ".bmp"
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
        if DEBUGPRINT == True:
            deckcardtry.save("DECKCARDTRY "+ str(i+2) + SUIT_DICT[suitInd] +".jpg")

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
    if DEBUGPRINT == True:
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
    #if DEBUGPRINT:
    #    print(card)

    return card

def updatetablebetting(game, street, poslist):
    game.numplayers = 1
    for each in game.player:
        position = each.seat
        if position == 0:
            continue
        game.numplayers += findplayerpresent(PLAYERPOSLIST[position])
        betstring = findplayeraction(PLAYERACTIONPOSLIST[position])
        if betstring != None:
            each.bHist[street].append(betstring)
            if betstring == "X":
                each.FoldedInd = 1
    if street == 0 and game.player[0].bHist[0] == []:
        if game.player[len(game.player)-1].bHist[0] == "SB":
            game.player[0].bHist[0].append("BB")

    if game.position == None:
        for each in game.player:
            if each.bHist[0] == ["BB"]:
                game.position = game.initnumplayers - each.seat + 3
                break

    #If not found then hero is the BB
    if game.position == None:
        game.position = 2
    return

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
            return 1, findstreet(STREETBOXPOS)

        count = count + 1
        if DEBUGPRINT == True:
            if count % 10 == 0:
                logging.debug("Poll for Hero Turn sleeping " + str(count))

        if count >= 600:
            if DEBUGPRINT == True:
                logging.critical("Timeout - exiting Poll for Hero Turn")
            return 0
        time.sleep(0.5)

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
        logging.critical("Unable to open preflop")
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
        logging.critical("Unable to open flop")
        return
    streetim = ImageEnhance.Color(streetim).enhance(0.0)
    streetim = streetim.filter(ImageFilter.CONTOUR)
    rms = rmsdiff(streetim, streetboxim)
    if rms <=30:
        return 2

    #test for turn
    streetboxim = streetboxim.crop((32,0,64,12))
    streetfilename = "2-Turn.jpg"
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

#Game functions
def PlayHand(NumPlayers,HeroCard1, HeroCard2, FlopCard1 = None, FlopCard2 = None, FlopCard3 = None, OutputInd = 0):
    #Set up the Dec
    FirstDeck = Deck()
    FirstDeck.shuffle()
    #Set up hero hand
    PlayerHands = []
    PlayerHands.append(Hand([HeroCard1,HeroCard2]))
    FirstDeck._Deck.remove(HeroCard1)
    FirstDeck._Deck.remove(HeroCard2)

    #Want to randomise the Flop now
    if FlopCard1 == None:
        FlopCard1 = FirstDeck._Deck.pop()
    else:
        FirstDeck._Deck.remove(FlopCard1)
    if FlopCard2 == None:
        FlopCard2 = FirstDeck._Deck.pop()
    else:
        FirstDeck._Deck.remove(FlopCard2)
    if FlopCard3 == None:
        FlopCard3 = FirstDeck._Deck.pop()
    else:
        FirstDeck._Deck.remove(FlopCard3)

    #FirstDeck._Deck.remove(FlopCard1)
    #FirstDeck._Deck.remove(FlopCard2)
    #FirstDeck._Deck.remove(FlopCard3)

    for i in range(1,NumPlayers):
        PlayerHands.append(Hand([FirstDeck._Deck.pop(),FirstDeck._Deck.pop()]))
    if OutputInd != 0:
        for i in range(0,NumPlayers):
            logging.debug("Player "+str(i)+" has the hand", end = " ")
            logging.debug(PlayerHands[i].getPreHandSimple())
    #Generate the flop
    ThirdCard = FlopCard1
    FourthCard = FlopCard2
    FifthCard = FlopCard3
    if OutputInd != 0:
        logging.debug("-" * 20)
        logging.debug("FLOP")
        logging.debug("-" * 20)
        logging.debug(ThirdCard)
        logging.debug(FourthCard)
        logging.debug(FifthCard)
    for i in range(0,NumPlayers):
        TempList = PlayerHands[i].getCards()
        TempList.append(ThirdCard)
        TempList.append(FourthCard)
        TempList.append(FifthCard)
        PlayerHands[i] = Hand(TempList)
    for i in range(0,NumPlayers):
        HandValue = PlayerHands[i].getPostCurrentHandString()
        if OutputInd != 0:
            logging.debug("FLOP: Player "+str(i)+" has the hand "+ HandValue)
    if OutputInd != 0:
        logging.debug("-" * 20)
        logging.debug("TURN")
        logging.debug("-" * 20)
    SixthCard = FirstDeck._Deck.pop()
    for i in range(0,NumPlayers):
        TempList = PlayerHands[i].getCards()
        TempList.append(SixthCard)
        PlayerHands[i] = Hand(TempList)
    for i in range(0,NumPlayers):
        HandValue = PlayerHands[i].getPostCurrentHandString()
        if OutputInd != 0:
            logging.debug("TURN: Player "+str(i)+" has the hand "+ HandValue)
    if OutputInd != 0:
        logging.debug("-" * 20)
        logging.debug("RIVER")
        logging.debug("-" * 20)
    SeventhCard = FirstDeck._Deck.pop()
    for i in range(0,NumPlayers):
        TempList = PlayerHands[i].getCards()
        TempList.append(SeventhCard)
        PlayerHands[i] = Hand(TempList)
    for i in range(0,NumPlayers):
        HandValue = PlayerHands[i].getPostCurrentHandString()
        if OutputInd != 0:
            logging.debug("RIVER: Player "+str(i)+" has the hand "+ HandValue)
    if OutputInd != 0:
        logging.debug("-" * 20)
        logging.debug("SHOWDOWN")
        logging.debug("-" * 20)
    winningHand = []
    for i in range(0,NumPlayers):
        winningHand.append((i,PlayerHands[i].PostHandValue))
    winningHand.sort(key=lambda t:t[1])
    if OutputInd != 0:
        logging.debug("The winner was Player " + str(winningHand[0][0]) + " with hand "
      + PlayerHands[winningHand[0][0]].getPostCurrentHandString())

    return(winningHand[0][0])

def GenerateProbabilities(NumPlayers, HeroCard1, HeroCard2, FlopCard1, FlopCard2, FlopCard3, Runs = 1000):
    HeroWin = 0

    for i in range(0,Runs):
        result = PlayHand(NumPlayers,HeroCard1 ,HeroCard2 ,FlopCard1, FlopCard2, FlopCard3)
        if result == 0:
            HeroWin = HeroWin + 1
        #if (i % 1000 == 0 & DEBUGPRINT):
        #    logging.debug(str(i))

    logging.debug("Hero won " + str(HeroWin) + " out of " + str(Runs) + " : " + str(HeroWin/Runs * 100))
    return (HeroWin * 100)/Runs

def getbetamount(p):
    move(p,0.1)
    click(p)
    click(p)
    time.sleep(0.1)
    #Copy all text
    dokey(0x43,17)
    variable = pyperclip.paste()
    return float(variable)

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
    filename = HAND_HISTORY_DIR + filename
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
    game = Game(p)
    logging.debug("DB queries finished")
    return game