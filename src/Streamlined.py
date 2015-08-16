__author__ = 'Ahab'

import time
import logging
import logging.config


import constants as c
import cardutils
import screenutils
import cardutils
import nlhutils

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename=c.LOG_FILE_DIR + c.LOG_FILE_NAME
                        ,format='%(asctime)s %(levelname)s:%(message)s')
    logging.info("\n \n")
    logging.info("POKER ENGINE PROGRAM STARTED")

    #potamount = getpotamount(FULLPOTBETBOXPOS, BETBOXPOS)
    logging.debug("Moving the window")
    screenutils.setwindowposition()
    #Get latest table information
    tablename = screenutils.getwindownameofNLH()
    date = time.strftime("%Y%m%d")
    SB = c.BIGBLIND / 200
    BB = c.BIGBLIND / 100
    logging.debug("Waiting for heros turn pre flop")
    logging.debug("-" * 20)
    #Wait until it's heros turn
    if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
        logging.debug("Poll for hero turn timeout!")
    logging.debug("PreFlop")
    logging.debug("-" * 20)
    logging.debug("Grabbing cards for hero")
    print("Grabbing cards")
    #grab the hero cards and create them as a hand
    #TODO clean this up a bit?
    herocardim1 = cardutils.grabcard(c.CARD1POS)
    herocard1suit = cardutils.findcardsuit(herocardim1)
    herocardim1 = cardutils.processflopcard(herocardim1)
    herocardim2 = cardutils.grabcard(c.CARD2POS)
    herocard2suit = cardutils.findcardsuit(herocardim2)
    herocardim2 = cardutils.processflopcard(herocardim2)
    herocard1rank = cardutils.findcardrank(herocardim1, herocard1suit)
    herocard2rank = cardutils.findcardrank(herocardim2, herocard2suit)
    logging.debug("Card 1 is " + str(herocard1rank) + " of " + c.SUIT_DICT[herocard1suit])
    logging.debug("Card 2 is " + str(herocard2rank) + " of " + c.SUIT_DICT[herocard2suit])
    herohand = cardutils.Hand([cardutils.Card(herocard1rank,herocard1suit),cardutils.Card(herocard2rank,herocard2suit)])

    #TODO - this won't work if you play around midnight, which is pretty shit. THink it goes off GMT? Test at 1am
    filename = "\\888poker" + date + " " + tablename + " $" + str(SB) + "-$" + str(BB) + " No Limit Holdem.txt"
    logging.debug("Using file " + filename)
    logging.debug("Get data from file")
    CurrentGame = cardutils.Game(herohand,players = cardutils.getplayersfor9table888(filename))
    logging.debug("Data read from file")

    print("Entering street loop")

    isstreet = True
    while isstreet == True:
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")

        print("Start sleep")
        time.sleep(2.5)
        cardutils.updatetablebetting(CurrentGame, 0, c.PLAYERPOSLIST)
        print("Done updated table")
        CurrentGame.currbet = screenutils.getbetamount(c.BETBOXPOS) / 2
        CurrentGame.potamount = screenutils.getpotamount(c.FULLPOTBETBOXPOS, c.BETBOXPOS)
        if CurrentGame.currbet != c.BIGBLIND:
            CurrentGame.potamount = CurrentGame.potamount - 2*CurrentGame.currbet
        else:
            CurrentGame.potamount = CurrentGame.potamount - CurrentGame.currbet
        CurrentGame.herocash = float(CurrentGame.player[0].cash)

        logging.debug("We have this many players " + str(CurrentGame.numplayers))
        logging.debug("Hero has " + herohand.getPreHandSimple() + " with odds "
              + str(herohand.getPreHandOdds(CurrentGame.numplayers)))
        for each in CurrentGame.player:
            if each.FoldedInd != 1:
                logging.debug(each.debugPlayerInfo())
        logging.debug("Current bet is " + str(CurrentGame.currbet))
        logging.debug("Current pot size is " + str(CurrentGame.potamount))
        logging.debug("Hero has cash " + str(CurrentGame.herocash))

        print("Start betting funct")
        #MAIN BETTING FUNCTION
        action, amount, wait = CurrentGame.betPreFlop()
        logging.info("We will do action " + str(action) + " with amount " + str(amount) +
                     " and wait " + str(wait))
        logging.info("----Beginning bet wait----")
        screenutils.bettingAction(action, amount, wait)
        logging.info("----Bet complete----")

        time.sleep(1)
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        time.sleep(2.5)
        #Check if we have a flop or if is still pre-flop
        if cardutils.findstreet(c.STREETBOXPOS) == 1:
            logging.debug("Still pre-flop")
        else:
            isstreet = False

    logging.debug("Flop")
    logging.debug("-" * 20)
    streetcard1 = cardutils.grabstreetcard(c.STREET1POS)
    streetcard2 = cardutils.grabstreetcard(c.STREET2POS)
    streetcard3 = cardutils.grabstreetcard(c.STREET3POS)
    herohand.addSharedCards([streetcard1, streetcard2, streetcard3])
    logging.info("Flop Cards are: " + streetcard1.__str__() + " " + streetcard2.__str__()
                 + " " + streetcard3.__str__())
    logging.info("Hero has " + herohand.getPostCurrentHandString())
    CurrentGame.streetcount = -1
    isstreet = True
    while isstreet == True:
        #HERO WILL ACT HERE FLOP
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        cardutils.updatetablebetting(CurrentGame, 1, c.PLAYERPOSLIST)
        CurrentGame.currbet = screenutils.getbetamount(c.BETBOXPOS) / 2
        CurrentGame.potamount = screenutils.getpotamount(c.FULLPOTBETBOXPOS, c.BETBOXPOS)
        if CurrentGame.currbet != c.BIGBLIND:
            CurrentGame.potamount -= 2*CurrentGame.currbet
        else:
            CurrentGame.potamount -= CurrentGame.currbet
        CurrentGame.herocash = float(CurrentGame.player[0].cash)

        for each in CurrentGame.player:
            if each.FoldedInd != 1:
                logging.debug(each.debugPlayerInfo())
        logging.debug("Current bet is " + str(CurrentGame.currbet))
        logging.debug("Current pot size is " + str(CurrentGame.potamount))
        logging.debug("Hero has cash " + str(CurrentGame.herocash))
        logging.debug("Beginning odds function")
        CurrentGame.PostFlopOdds = cardutils.GenerateProbabilities(CurrentGame.numplayers, cardutils.Card(herocard1rank,herocard1suit)
                                         ,cardutils.Card(herocard2rank,herocard2suit),streetcard1, streetcard2
                                         ,streetcard3)
        logging.debug("Exiting odds function")
        logging.info("Players post flop odds are :" + str(CurrentGame.PostFlopOdds))
        action, amount, wait = CurrentGame.betFlop()
        logging.info("We will do action " + str(action) + " with amount " + str(amount) +
                     " and wait " + str(wait))
        logging.info("----Beginning bet wait----")
        screenutils.bettingAction(action, amount, wait)
        logging.info("----Bet complete----")

        time.sleep(1)
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        time.sleep(2.5)
        #Check if we have a turn or if is flop
        if cardutils.findstreet(c.STREETBOXPOS) == 2:
            logging.debug("Still flop")
        else:
            isstreet = False

###########################################################################
    logging.debug("Turn")
    logging.debug("-" * 20)
    streetcard4 = cardutils.grabstreetcard(c.STREET4POS)
    if c.DEBUGPRINT:
        logging.debug(herohand.getPostCurrentHandString())
    herohand.addSharedCards([streetcard4])
    isstreet = True
    streetcount = 0
    while isstreet == True:
        #HERO WILL ACT HERE TURN
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        numplayers = cardutils.updatetablebetting(c.PLAYERPOSLIST)
        CurrentGame.currbet = screenutils.getbetamount(c.BETBOXPOS) / 2
        CurrentGame.potamount = screenutils.getpotamount(c.FULLPOTBETBOXPOS, c.BETBOXPOS)
        if CurrentGame.currbet != c.BIGBLIND:
            CurrentGame.potamount -= 2*CurrentGame.currbet
        else:
            CurrentGame.potamount -= CurrentGame.currbet
        CurrentGame.herocash = float(CurrentGame.player[0].cash)

        for each in CurrentGame.player:
            if each.FoldedInd != 1:
                logging.debug(each.debugPlayerInfo())
        logging.debug("Current bet is " + str(CurrentGame.currbet))
        logging.debug("Current pot size is " + str(CurrentGame.potamount))
        logging.debug("Hero has cash " + str(CurrentGame.herocash))
        logging.debug("Beginning odds function")
        CurrentGame.PostFlopOdds = cardutils.GenerateProbabilities(CurrentGame.numplayers, cardutils.Card(herocard1rank,herocard1suit)
                                         ,cardutils.Card(herocard2rank,herocard2suit),streetcard1, streetcard2
                                         ,streetcard3,streetcard4)
        logging.debug("Exiting odds function")
        logging.info("Players post flop odds are :" + str(CurrentGame.PostFlopOdds))
        action, amount, wait = CurrentGame.betTurn()
        logging.info("We will do action " + str(action) + " with amount " + str(amount) +
                     " and wait " + str(wait))
        logging.info("----Beginning bet wait----")
        screenutils.bettingAction(action, amount, wait)
        logging.info("----Bet complete----")

        time.sleep(1)
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        time.sleep(2.5)
        #Check if we have a river or if is turn
        if cardutils.findstreet(c.STREETBOXPOS) == 3:
            logging.debug("Still turn")
        else:
            isstreet = False

    logging.debug("River")
    logging.debug("-" * 20)
    streetcard5 = cardutils.grabstreetcard(c.STREET5POS)
    herohand = herohand + streetcard5
    if c.DEBUGPRINT:
        logging.debug(herohand.getPostCurrentHandString())
    isstreet = True
    streetcount = 0
    while isstreet == True:
        #HERO WILL ACT HERE FLOP
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        numplayers = cardutils.updatetablebetting(c.PLAYERPOSLIST)

        #Check if it is still river
        if cardutils.findstreet(c.STREETBOXPOS) == 4:
            logging.debug("Still river")
            streetcount = streetcount + 1
        else:
            break

    logging.info("POKER ENGINE PROGRAM EXITED")