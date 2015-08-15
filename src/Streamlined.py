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

LOG_FILE_DIR = "C:\\Users\\Ahab\\Desktop"
LOG_FILE_NAME = "\\PokerEnging.log"
HAND_HISTORY_DIR ="C:\\Users\\Ahab\\AppData\\Roaming\\PacificPoker\\HandHistory\\tinoater"
PF_ODDS_FILENAME = 'PreFlop.csv'
RANK_DICT = {2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'T',11:'J',12:'Q',13:'K',14:'A'}
SUIT_DICT = {1:'H',2:'D',3:'S',4:'C'}
PREM_PARIS = [14,13,12]
HAND_DICT = {1:'Royal Flush', 2:'Straight Flush', 3:'Four of a Kind', 4:'Full House', 5:'Flush', 6:'Straight'
             ,7:'Three of a Kind',8:'Two Pairs',9:'One Pair',10:'High Card'}
QUERY_DICT={'Name':0, 'NumHands':1, 'VPIP_Perc':2, 'PFR_Perc':3, 'Call_Perc':4, 'CBet_Perc':5, 'CBet_Fold_Perc':6
          , 'CBet_Call_Perc':7, 'CBet_Raise_Perc':8, 'CBet_Turn_Perc':9}
#These card positions are hardcoded
#Hero cards
CARD1POS = (215, 222, 245, 239)
CARD2POS = (245, 222, 278, 239)
#These cards are 1px too large, to be cropped after contour
STREET1POS = (169,121,180,137)
STREET2POS = (203,121,214,137)
STREET3POS = (236,121,247,137)
STREET4POS = (269,121,280,137)
STREET5POS = (302,121,313,137)
STREETBOXPOS = (170,123,335,135)
#Hero time bar
HEROBOXPOS = (220,270,288,271)
BETBOXPOS = (457,332)
HALFPOTBETBOXPOS = (349,318)
FULLPOTBETBOXPOS = (420,318)
ALLINPOTBETBOXPOS = (457,318)
RAISEBUTTONPOS = (444,298)
CALLBUTTONPOS = (344,298)
FOLDBUTTONPOS = (244,298)
#Player presence
PLAYERPOSLIST = [(0,0,0,0),(120, 232, 148, 244), (43, 164, 71, 176), (43 , 97, 71, 109), (163, 40, 191, 52)
    , (297, 40, 325, 52), (428, 97, 456, 109), (428, 164, 456, 176), (341, 232, 369, 244)]
PLAYERACTIONPOSLIST = [(0,0,0,0),(114,270,177,271),(37,200,101,201),(37,136,101,137),(157,79,221,80)
    ,(292,79,355,80),(422,136,486,137),(422,200,486,201),(334,270,397,271)]

PLAYERFOLDRGB = 34776
PLAYERCALLRGB = 54574
PLAYERRAISERGB = 32774
PLAYERALLINRGB = 65026
PLAYERSBRGB = 115
PLAYERBBRGB = 173
DEBUGPRINT = False
#Table config
BIGBLIND = 2
#Betting config
PF_PREM_RERAISE_PERC = 0.2 #How often reraise preflop curr bet >3BB
PF_PP_BELOW_9_RAISE =  0.3 #How often open raise preflop with PP <9
PF_PP_BELOW_9_CALL = 1 #How often open call with PF with PP <9
PF_SMALL_PAIR = 25 * BIGBLIND #Threshold to call PF with pocket pairs, per player
PF_FL_STR_DRAW = 20 * BIGBLIND #Threshold to call PF with suited or connected
RAISE_TO_ALLIN_THRESH = 0.2 #If 1+this * raise >= cash then go all in

PF_CALL_AFTER_RAISE_PERC = 0.8 #Perc of a PF call of a raise
PF_CALL_PERC = 0.3 #Perc of a PF open call
PF_STEAL = 0.3 #Perc of trying to steal from button or more
PF_OTHER_HANDS_OPEN = 0.8 #Perc of PF opening the pot with other hand > 10%
PF_OTHER_HANDS_CALL = 0.7 #Perc of PF callling into the pot with other hand > 10%

#DEBUG functions
def printcursorpoint(t=5):
    starttime = time.time()
    while time.time() <= starttime + t:
        print(win32gui.GetCursorPos())
        time.sleep(0.1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE_DIR + LOG_FILE_NAME
                        ,format='%(asctime)s %(levelname)s:%(message)s')
    logging.info("\n \n")
    logging.info("POKER ENGINE PROGRAM STARTED")

    #potamount = getpotamount(FULLPOTBETBOXPOS, BETBOXPOS)
        logging.debug("Moving the window")
    setwindowposition()
    #Get latest table information
    tablename = getwindownameofNLH()
    date = time.strftime("%Y%m%d")
    SB = BIGBLIND / 200
    BB = BIGBLIND / 100
    #TODO - this won't work if you play around midnight, which is pretty shit. THink it goes off GMT? Test at 1am
    filename = "\\888poker" + date + " " + tablename + " $" + str(SB) + "-$" + str(BB) + " No Limit Holdem.txt"
    logging.debug("Using file " + filename)
    logging.debug("Get data from file")
    CurrentGame = getplayersfor9table888(filename)
    logging.debug("Data read from file")
    logging.debug("Waiting for heros turn pre flop")
    logging.debug("-" * 20)
    #Wait until it's heros turn
    if pollforheroturn(HEROBOXPOS) == 0:
        logging.debug("Poll for hero turn timeout!")
    logging.debug("PreFlop")
    logging.debug("-" * 20)
    logging.debug("Grabbing cards for hero")
    #grab the hero cards and create them as a hand
    herocardim1 = grabcard(CARD1POS)
    herocard1suit = findcardsuit(herocardim1)
    herocardim1 = processflopcard(herocardim1)
    herocardim2 = grabcard(CARD2POS)
    herocard2suit = findcardsuit(herocardim2)
    herocardim2 = processflopcard(herocardim2)
    herocard1rank = findcardrank(herocardim1, herocard1suit)
    herocard2rank = findcardrank(herocardim2, herocard2suit)
    logging.debug("Card 1 is " + str(herocard1rank) + " of " + SUIT_DICT[herocard1suit])
    logging.debug("Card 2 is " + str(herocard2rank) + " of " + SUIT_DICT[herocard2suit])

    herohand = Hand([Card(herocard1rank,herocard1suit),Card(herocard2rank,herocard2suit)])
    isstreet = True
    while isstreet == True:
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if pollforheroturn(HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")

        time.sleep(2.5)
        updatetablebetting(CurrentGame, 0, PLAYERPOSLIST)
        currbet = getbetamount(BETBOXPOS) / 2
        potamount = getpotamount(FULLPOTBETBOXPOS, BETBOXPOS)
        if currbet != BIGBLIND:
            potamount = potamount - 2*currbet
        else:
            potamount = potamount - currbet
        herocash = CurrentGame.player[0].cash

        logging.debug("We have this many players " + str(CurrentGame.numplayers))
        logging.debug("Hero has " + herohand.getPreHandSimple() + " with odds "
              + str(herohand.getPreHandOdds(CurrentGame.numplayers)))
        for each in CurrentGame.player:
            if each.FoldedInd != 1:
                logging.debug(each.debugPlayerInfo())
        logging.debug("Current bet is " + str(currbet))
        logging.debug("Current pot size is " + str(potamount))
        logging.debug("Hero has cash " + str(herocash))

        #MAIN BETTING FUNCTION
        CurrentStrat = BettingStrat(CurrentGame, herohand)
        action, amount, wait = CurrentStrat.betPreFlop(currbet, potamount, herocash)
        logging.info("We will do action " + str(action) + " with amount " + str(amount) +
                     " and wait " + str(wait))
        logging.info("----Beginning bet wait----")
        bettingAction(action, amount, wait)
        logging.info("----Bet complete----")

        time.sleep(1)
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if pollforheroturn(HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        time.sleep(2.5)
        #Check if we have a flop or if is still pre-flop
        if findstreet(STREETBOXPOS) == 1:
            logging.debug("Still pre-flop")
        else:
            isstreet = False

    logging.debug("Flop")
    logging.debug("-" * 20)
    streetcard1 = grabstreetcard(STREET1POS)
    streetcard2 = grabstreetcard(STREET2POS)
    streetcard3 = grabstreetcard(STREET3POS)
    herohand = herohand + streetcard1 + streetcard2 + streetcard3
    logging.info("Flop Cards are: " + streetcard1.__str__() + " " + streetcard2.__str__()
                 + " " + streetcard3.__str__())
    logging.info("Hero has " + herohand.getPostCurrentHandString())
    isstreet = True
    while isstreet == True:
        #HERO WILL ACT HERE FLOP
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if pollforheroturn(HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        updatetablebetting(CurrentGame, 1, PLAYERPOSLIST)
        logging.debug("Beginning odds function")
        herohand.PostFlopOdds = GenerateProbabilities(CurrentGame.numplayers, Card(herocard1rank,herocard1suit)
                                         ,Card(herocard2rank,herocard2suit),streetcard1, streetcard2
                                         ,streetcard3)
        CurrentStrat.PostFlopOdds = herohand.PostFlopOdds
        logging.debug("Exiting odds function")
        logging.info("Players post flop odds are :" + str(herohand.PostFlopOdds))
        action, amount, wait = CurrentStrat.betFlop(currbet, potamount, herocash)
        #Check if we have a turn or if is still flop
        if findstreet(STREETBOXPOS) == 2:
            logging.debug("Still flop")
            streetcount = streetcount + 1
        else:
            break

    logging.debug("Turn")
    logging.debug("-" * 20)
    streetcard4 = grabstreetcard(STREET4POS)
    if DEBUGPRINT:
        logging.debug(herohand.getPostCurrentHandString())
    herohand = herohand + streetcard4
    isstreet = True
    streetcount = 0
    while isstreet == True:
        #HERO WILL ACT HERE FLOP
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if pollforheroturn(HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        numplayers = updatetablebetting(PLAYERPOSLIST)

        #Check if we have a river or if is still turn
        if findstreet(STREETBOXPOS) == 3:
            logging.debug("Still turn")
            streetcount = streetcount + 1
        else:
            break

    logging.debug("River")
    logging.debug("-" * 20)
    streetcard5 = grabstreetcard(STREET5POS)
    herohand = herohand + streetcard5
    if DEBUGPRINT:
        logging.debug(herohand.getPostCurrentHandString())
    isstreet = True
    streetcount = 0
    while isstreet == True:
        #HERO WILL ACT HERE FLOP
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if pollforheroturn(HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        numplayers = updatetablebetting(PLAYERPOSLIST)

        #Check if it is still river
        if findstreet(STREETBOXPOS) == 4:
            logging.debug("Still river")
            streetcount = streetcount + 1
        else:
            break

    logging.info("POKER ENGINE PROGRAM EXITED")