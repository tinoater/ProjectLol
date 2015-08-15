__author__ = 'Ahab'

#import math
#import csv
#import sys
#import random
#import operator
#import functools
#import random
#import win32api
#import win32con
#import win32gui
#from PIL import Image, ImageFilter, ImageGrab, ImageEnhance, ImageChops
#import time
#import pyperclip
#import tkinter
#import psycopg2
#import fileinput
#import linecache
#import logging
#import logging.config

import screenutils
import constants
import cardutils
import debugutils

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename=LOG_FILE_DIR + LOG_FILE_NAME
                        ,format='%(asctime)s %(levelname)s:%(message)s')
    logging.info("\n \n")
    logging.info("POKER ENGINE PROGRAM STARTED")

    #potamount = getpotamount(FULLPOTBETBOXPOS, BETBOXPOS)
        logging.debug("Moving the window")
    screenutils.setwindowposition()
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