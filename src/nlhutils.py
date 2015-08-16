__author__ = 'Ahab'

import operator
import random
import logging
import logging.config
import itertools

import constants as c

class Game:
    def __init__(self, hand, players):
        self.player = players
        self.hand = hand
        self.potsize = 0
        self.initnumplayers = len(self.player)
        self.position = None
        #TODO need to implement an aggro parameter
        self.preFlopOdds = hand.PreFlopOdds
        self.preFlopOdds10 = hand.preFlopOdds10
        self.postFlopOdds = hand.PostFlopOdds
        if hand.PPInd == 1:
            self.drawInd = 1
        else:
            self.drawInd = 0
        if hand.PremInd == 1:
            self.madeInd = 1
        else:
            self.madeInd = 0
        if hand._cards[0].getRank() == 14 and hand._cards[1].getRank() == 14:
            self.BHInd = 1
        else:
            self.BHInd = 0
        if hand.suitedInd == 1 or hand.connectedInd == 1:
            self.drawInd = 1
        self.PPInd = hand.PPInd
        self.bettingHist=[[],[],[],[]]
        self.street = 0
        self.streetcount = -1
        self.totalhandbet = 0
        self.potamount = 0
        self.herocash = 0
        self.PFAggressor = 0
        self.CBetInd = 0

    def getUnMovedPlayers(self):
        unMovedPlayers = 0
        heropos = self.position
        if self.street == 0:
            for each in self.player:
                if each.FoldedInd != 0 and ((each.seat > heropos) or (each.seat in (0,1))):
                    unMovedPlayers += 1
        else:
            for each in self.player:
                if each.FoldedInd != 0 and each.seat > heropos:
                    unMovedPlayers += 1

        return unMovedPlayers

    def updateHeroBetting(self, action, street, logstring, bet = 0):
        self.totalhandbet += bet
        self.bettingHist[street].extend((action,bet))
        logging.info(logstring)

        if street == 0:
            if action == "R":
                self.PFAggressor = 1
            else:
                self.PFAggressor = 0
        return True

        #TODO set the herocash so that it is measured in pennies

    def betoutput(self, action, street, wait, logstring, bet = 0, cBetInd = 0):
        if action == 1:
            bet = self.currbet
        if self.herocash * 100 <= bet:
            logstring += ". Not enough cash so going all-in"
            self.updateHeroBetting(c.ACTION_DICT[3],street, logstring, self.herocash)
            return 3, 0, wait
        elif self.herocash * 100 - bet <= bet * c.RAISE_TO_ALLIN_THRESH:
            logstring += ". Rounding up to all in"
            self.updateHeroBetting(c.ACTION_DICT[3],street, logstring, self.herocash)
            return 3, 0, wait
        else:
            self.updateHeroBetting(action,street,logstring,bet)
            return action, bet, wait

    def betPreFlop(self):
        self.streetcount =+ 1
        wait = random.uniform(1,4)
        logging.info("Pot amount is " + str(self.potamount))
        logging.info("Call bet amount is " + str(self.currbet))
        #TODO - Incorporate position into betting strat
        #Set up the oppactions sumary list
        oppactions = []
        for each in self.player:
            try:
                oppactions.extend(each.bHist[0][self.streetcount])
            except IndexError:
                oppactions.extend(each.bHist[0])
        movedPlayers = oppactions.count("R") + oppactions.count("A") + oppactions.count("C")
        unmovedPlayers = self.getUnMovedPlayers()
        if oppactions.count("R") + oppactions.count("A") == 0:
            checkedPot = 1
        else:
            checkedPot = 0
        logstr = ""
        bet = self.currbet

        #Try to go all in with Aces pre-flop
        if self.BHInd == 1:
            logstr += "Have Aces "
            bet = round(self.currbet * (random.uniform(2,3)))
            logstr += "Herocash:" +str(self.herocash) + " desired raise:" + str(bet) + ". "
            wait = random.uniform(3,4)
            return self.betoutput(2,0,wait,logstr,bet)

        #Premium hands - push for max bet
        if self.madeInd == 1:
            logstr += "Have Premium Hand "
            if checkedPot == 1:
                bet = round(self.currbet * (random.uniform(2,3)))
                logstr += "Open pot with a raise"
                return self.betoutput(2,0,wait,logstr,bet)
            else:
                if self.currbet <= 3 * c.BIGBLIND:
                    bet = round(self.currbet * (random.uniform(2,3)))
                    logstr += "Will reraise as currbet:" + str(self.currbet)
                    return self.betoutput(2,0,wait,logstr,bet)
                else:
                    if random.uniform(0,1) <= c.PF_PREM_RERAISE_PERC:
                        logstr += "Currbet is large, but will reraise anyway. Parameter:" + str(c.PF_PREM_RERAISE_PERC)
                        bet = round(self.currbet * (random.uniform(2,3)))
                        return self.betoutput(2,0,wait,logstr,bet)
                    else:
                        logstr += "Will call"
                        return self.betoutput(1,0,wait,logstr,bet)


        #Pocket pairs - draw with all pairs if its cheap/many players. Aggressive with larger pairs
        if self.PPInd == 1:
            logstr += "Have pocket pairs "
            if movedPlayers == 0:
                logstr += "First to enter the pot "
                if self.hand.PPCard >= 9:
                    logstr += "Strong pair so raise "
                    bet = round(c.BIGBLIND * (random.uniform(2,3)))
                    return self.betoutput(2,0,wait,logstr,bet)
                else:
                    if random.uniform(0,1) <= c.PF_PP_BELOW_9_RAISE:
                        bet = round(c.BIGBLIND * (random.uniform(2,3)))
                        logstr += "Weak pair but raise anyway. Parameter:" + str(c.PF_PP_BELOW_9_RAISE)
                        return self.betoutput(2,0,wait,logstr,bet)
                    elif random.uniform(0,1) <= c.PF_PP_BELOW_9_CALL:
                        logstr += "Call to draw to set"
                        return self.betoutput(1,0,wait,logstr,bet)
                    else:
                        return self.betoutput(0,0,wait,logstr,bet)
            else:
                logstr += "\n Other players are in the pot. Prediction of pot size is:" + str(c.PF_SMALL_PAIR * ((movedPlayers * c.PF_CALL_AFTER_RAISE_PERC) + (unmovedPlayers * c.PF_CALL_PERC)))
                if c.PF_SMALL_PAIR / 10 * ((movedPlayers * c.PF_CALL_AFTER_RAISE_PERC) + (unmovedPlayers * c.PF_CALL_PERC)) \
                        >= self.currbet:
                    logstr += " Call worth it"
                    return self.betoutput(1,0,wait,logstr,bet)
                else:
                    logstr += " Call not worth it"
                    return self.betoutput(0,0,wait,logstr,bet)

        #Flush or Straight Draws
        if self.drawInd == 1:
            if self.hand.suitedInd == 1 & self.hand.connectedInd == 1:
                logstr += ",have a connected flush draw"
                predictedSDPot = c.PF_STRFL_DRAW * ((movedPlayers * c.PF_CALL_AFTER_RAISE_PERC
                                                 + unmovedPlayers * c.PF_CALL_PERC) * self.currbet + self.potamount)
                logstr += "\n Predicted pot size / factor >= bet * high card scale?:"
                logstr += str(predictedSDPot) + " / " + str(c.PF_STRFL_ODDS) + " >= " + str(self.currbet) + " * "\
                          + str(14/self.hand.highcard) + " ? \n"
                if predictedSDPot / c.PF_STRFL_ODDS >= (self.currbet * 14 / self.hand.highcard):
                    logstr += " Call worth it"
                    return self.betoutput(1,0,wait,logstr,bet)
            logstr += "Have a flush or straight draw"
            if self.hand.suitedInd == 1:
                logstr += ",have a flush draw"
                predictedSDPot = c.PF_FL_DRAW * ((movedPlayers * c.PF_CALL_AFTER_RAISE_PERC
                                                 + unmovedPlayers * c.PF_CALL_PERC) * self.currbet + self.potamount)
                logstr += "\n Predicted pot size / factor >= bet * high card scale?:"
                logstr += str(predictedSDPot) + " / " + str(c.PF_FL_ODDS) + " >= " + str(self.currbet) + " * "\
                          + str(14/self.hand.highcard) + " ? \n"
                if predictedSDPot / c.PF_FL_ODDS >= (self.currbet * 14 / self.hand.highcard):
                    logstr += " Call worth it"
                    return self.betoutput(1,0,wait,logstr,bet)
            if self.hand.connectedInd == 1:
                logstr += ",have a straight draw"
                predictedSDPot = c.PF_STR_DRAW * ((movedPlayers * c.PF_CALL_AFTER_RAISE_PERC
                                                 + unmovedPlayers * c.PF_CALL_PERC) * self.currbet + self.potamount)
                logstr += "\n Predicted pot size / factor >= bet * high card scale?:"
                logstr += str(predictedSDPot) + " / " + str(c.PF_STR_ODDS) + " >= " + str(self.currbet) + " * "\
                          + str(14/self.hand.highcard) + " ? \n"
                if predictedSDPot / c.PF_STR_ODDS >= (self.currbet * 14 / self.hand.highcard):
                    logstr += " Call worth it"
                    return self.betoutput(1,0,wait,logstr,bet)
        #All other hands
        logstr += "Misc. hands"
        if checkedPot == 1:
            logstr += "No one has entered pot "
            logstr += "\n Hand Odds are:" + str(self.preFlopOdds10 / 100) + " Adjusted odds are:" \
                      + str((self.preFlopOdds10 / 100 * random.uniform(0,1))) + " threshold is:" + str(c.PF_OTHER_HANDS_OPEN)
            if self.preFlopOdds10 >= 10 & (self.preFlopOdds10 / 100 * random.uniform(0,1) <= c.PF_OTHER_HANDS_OPEN):
                bet = round(c.BIGBLIND * (random.uniform(2,3)))
                logstr += "Open raise"
                return self.betoutput(2,0,wait,logstr,bet)

        if checkedPot == 0:
            logstr += " People have entered the pot"
            logstr += " Hand Odds are:" + str(self.preFlopOdds10) + " Adjusted odds are:" \
                      + str((self.preFlopOdds10 / 100 * random.uniform(0,1))) + " threshold is:" + str(c.PF_OTHER_HANDS_CALL)
            if self.preFlopOdds10 >= 10 & (self.preFlopOdds10 / 100 * random.uniform(0,1) <= c.PF_OTHER_HANDS_CALL):
                if self.currbet <= 3 * c.BIGBLIND:
                    return self.betoutput(1,0,wait,logstr,bet)

        #If no one has opened the pot then try to steal
        if checkedPot == 1:
            logstr += " No one has entered the pot"
            logstr += " Steal threshold is:" + str(c.PF_STEAL)
            if unmovedPlayers <=3 & (random.uniform(0,1) <= c.PF_STEAL):
                bet = round(c.BIGBLIND * (random.uniform(2,3)))
                logstr += " Attempt to steal"
                return self.betoutput(2,0,wait,logstr,bet)

        #Else just fold
            logstr += " Just fold"
            return self.betoutput(0,0,wait,logstr,bet)

    def analyseBoard(self,street):
        if self.hand.PostFlopOdds >= c.BH_THRESHOLD:
            self.BHInd = 1
        else:
            self.BHInd = 0

        #TODO: Empty logic for altering BHInd for flush and straights
        if self.hand.PostHandType == 5 & self.hand.HighCard != 14:
            pass
        if self.hand.PostHandType == 4:
            pass

        rank_list = []
        suit_list = []
        sharedrank_list = []
        sharedsuit_list = []
        for each in self.hand:
            rank_list.append(int(each.getRank()))
            suit_list.append(each.getSuit())
        rank_list = list(set(rank_list)).sort()

        for each in self.hands.sharedCards:
            sharedrank_list.append(int(each.getRank()))
            sharedsuit_list.append(each.getSuit())
        sharedrank_list = list(set(rank_list)).sort()

        #TODO: Turn this into a setter method that will set the betting strategy to Draw?
        if max(map(lambda x: suit_list.count(x), [1,2,3,4])) == 4 & self.hand.suitedInd == 1:
            self.drawInd = 1
            logging.info("We have a flush draw")
        else:
            self.drawInd = 0

        #TODO: This won't deal with 1 card in a straight draw
        if self.hand.connectedInd == 1:
            for k, g in itertools.groupby(enumerate(rank_list), lambda x:x[0] - x[1]):
                thing = list(map(operator.itemgetter(1),g))
                if thing.__len__() == 4:
                    self.drawInd = 1
                    self.drawStraightOdds = 2 * 8 / 100
                    logging.info("We have a straight draw")
                else:
                    self.drawStraightOdds == 0

        if max(map(lambda x: sharedsuit_list.count(x), [1,2,3,4])) == 2:
            self.drawPresentInd = 1
            self.drawFlushOdds = 2 * 12 / 100
            logging.info("There is a flush draw")
        else:
            self.drawPresentInd = 0
            self.drawFlushOdds = 0

        #TODO: This won't deal with 1 card in a straight draw
        for k, g in itertools.groupby(enumerate(sharedrank_list), lambda x:x[0] - x[1]):
            thing = list(map(operator.itemgetter(1),g))
            if thing.__len__() == 3:
                self.drawPresentInd = 1
                logging.info("There is a straight draw")

        if self.hand.PostHandType <= 8:
            self.madeInd = 1
        else:
            self.madeInd = 0

    def shouldCBet(self):
        #TODO: Improve this Cbet proc
        if random.uniform(0,1) <= c.FLOP_CBET:
            return 1
        else:
            return 0

    def shouldFSteal(self):
        #TODO: Improve the flop steal
        if random.uniform(0,1) <= c.FLOP_STEAL:
            return 1
        else:
            return 0

    def shouldDraw(self):
        #TODO: Improve the draw proc
        if self.drawFlushOdds == 0 or self.drawStraightOdds == 0:
            if self.potodds <= self.drawStraightOdds or self.potodds <= self.drawFlushOdds:
                return 1
            else:
                return 0
        else:
            if self.potodds <= min(self.drawStraightOdds, self.drawFlushOdds):
                return 1
            else:
                return 0

    def shouldCall(self):
        #TODO: Improve
        if self.potodds <= self.currbet:
            return 1
        else:
            return 0

    def betFlop(self):
        currbet = self.currbet
        potamount = self.potamount
        herocash = self.herocash - self.totalhandbet
        self.streetcount =+ 1
        #set wait to zero as getting pot odds takes so long
        wait = 0
        logging.info("Pot amount is " + str(potamount))
        logging.info("Call bet amount is " + str(currbet))
        #TODO - Incorporate position into betting strat
        #Set up the oppactions sumary list
        oppactions = []
        for each in self.player:
            try:
                oppactions.extend(each.bHist[1][self.streetcount])
            except IndexError:
                oppactions.extend(each.bHist[1])

        movedPlayers = oppactions.count("R") + oppactions.count("A") + oppactions.count("C")
        unmovedPlayers = self.getUnMovedPlayers()
        if oppactions.count("R") + oppactions.count("A") == 0:
            checkedPot = 1
        else:
            checkedPot = 0
        logstr = ""
        bet = self.currbet

        self.potodds = self.currbet / (self.potamount + self.currbet)
        #If BH then we want to push for max value
        if self.BHInd == 1:
            logstr = "Have BH with prob " + str(self.hand.PostFlopOdds) + ". "
            if self.PFAggressor == 0:
                if self.PFAggresActed == 0 & checkedPot == 1 & self.streetcount == 0:
                    logstr += "Check to PF raiser "
                    self.updateHeroBetting("C",1, logstr, 0)
                elif self.PFAggresActed == 0 & checkedPot == 0 & self.streetcount == 0:
                    if random.uniform(0,1) <= c.BH_FP_RAISE:
                        logstr += "will reraise due to threshold " + str(c.BH_FP_RAISE)
                        bet = round(currbet * random.uniform(2,3))
                        return self.betoutput(2,wait,logstr,bet)
                    else:
                        logstr += "call the flop bet"
                        return self.betoutput(1,wait,logstr,bet)
                elif self.streetcount == 0:
                    if self.player[self.PFAggressor].bHist[1] == "C":
                        logstr += "PF raiser checked(called), "
                        if checkedPot == 1:
                            bet = round(potamount * (random.uniform(0.5,0.7)))
                            logstr += "unopened pot so bet"
                            return self.betoutput(2,wait,logstr,bet)
                        elif random.uniform(0,1) <= c.BH_FP_RAISE:
                            logstr += "will reraise due to threshold " + str(c.BH_FP_RAISE)
                            bet = round(currbet * random.uniform(2,3))
                            return self.betoutput(2,wait,logstr,bet)
                        else:
                            logstr += "call the flop bet"
                            return self.betoutput(1,wait,logstr,bet)
                else:
                    logstr += " further round of betting, so reraise"
                    bet = round(currbet * random.uniform(2,3))
                    return self.betoutput(2,wait,logstr,bet)
            if self.PFAggressor == 1 & checkedPot == 1:
                bet = round(self.potamount * (random.uniform(0.5,0.7)))
                logstr += " Open pot with a raise"
                return self.betoutput(2, wait,logstr,bet)
            elif self.PFAggressor == 1 & checkedPot == 0:
                logstr += " will reraise due to threshold " + str(c.BH_FP_RAISE) + "."
                bet = round(currbet * random.uniform(2,3))
                return self.betoutput(2, wait,logstr,bet)
            else:
                logstr += "No action defined!"
                logging.error("No action defined in Flop bet BH==1")
                return self.betoutput(0, wait,logstr,bet)

        #Try CBet, else check/call
        if self.drawInd == 1:
            logstr += "Have a drawing hand."
            if checkedPot == 1:
                logstr += "Checked pot."
                if self.PFAggressor == 1:
                    logstr += "Was the PF Agressor."
                    if self.shouldCBet() == 1:
                        self.CBetInd == 1
                        logstr += "Will CBet anyway."
                        bet = round(self.potamount * random.uniform(0.5,0.7))
                        return self.betoutput(2, wait,logstr,bet)
                    else:
                        logstr += "Will try to draw for free."
                        return self.betoutput(1, wait,logstr,bet)
                else:
                    logstr += "Was not the PF Agrssor."
                    if self.shouldFSteal == 1:
                        logstr += "Try to steal flop."
                        bet = round(self.potamount * random.uniform(0.5,0.7))
                        return self.betoutput(2, wait,logstr,bet)
                    else:
                        logstr += "Will try to draw for free."
                        return self.betoutput(1, wait,logstr,bet)
            else:
                logstr += "Pots been opened."
                if self.shouldDraw == 1:
                    logstr += "Try to draw."
                    return self.betoutput(1, wait,logstr,bet)

        #TODO: Add some generic call logic function here
        if self.madeInd == 1:
            logstr += "Have a made hand."
            if checkedPot == 1:
                logstr += "Open the pot."
                bet = round(self.potamount * random.uniform(0.5,0.7))
                return self.betoutput(2,wait,logstr,bet)
            else:
                logstr += "Call the bet."
                return self.betoutput(1,wait,logstr,bet)

        #TODO: Add logic to steal a boring looking flop
        else:
            logstr += "Have a misc hand."
            if self.PFAggressor == 1:
                logstr += "Was the PF aggressor."
                if checkedPot == 1:
                    logstr += "Pot has been checked"
                    if self.shouldCBet() == 1:
                        logstr += "Will try to CBet."
                        bet = round(self.potamount * random.uniform(0.5,0.7))
                        return self.betoutput(2,wait,logstr,bet)
                    else:
                        logstr += "Won't CBet"
                        return self.betoutput(1,wait,logstr,bet)
                else:
                    logstr += "Pot has been opened."
                    if self.shouldCall() == 1:
                        logstr += "Will call"
                        return self.betoutput(1,wait,logstr,bet)
                    else:
                        logstr += "Will fold"
                        return self.betoutput(0,wait,logstr,bet)
            else:
                logstr += "Was not the PF aggressor."
                if checkedPot == 1:
                    logstr += "Pot has been checked"
                    if self.shouldFSteal() == 1:
                        logstr += "Will try to Steal."
                        bet = round(self.potamount * random.uniform(0.5,0.7))
                        return self.betoutput(2,wait,logstr,bet)
                    else:
                        logstr += "Won't Steal."
                        return self.betoutput(1,wait,logstr,bet)
                else:
                    logstr += "Pot has been opened."
                    if self.shouldCall() == 1:
                        logstr += "Will call"
                        return self.betoutput(1,wait,logstr,bet)
                    else:
                        logstr += "Will fold"
                        return self.betoutput(0,wait,logstr,bet)

def updatetablebetting(game, street, poslist):
    game.numplayers = 1
    for each in game.player:
        position = each.seat
        if position == 0:
            continue
        game.numplayers += findplayerpresent(c.PLAYERPOSLIST[position])
        betstring = findplayeraction(c.PLAYERACTIONPOSLIST[position])
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

#Game functions
def PlayOddsHand(NumPlayers,HeroCard1, HeroCard2, FlopCard1 = None, FlopCard2 = None, FlopCard3 = None,
                 FlopCard4 = None, FlopCard5 = None, OutputInd = 0):
    #Set up the Deck
    FirstDeck = Deck()
    FirstDeck.shuffle()
    #Set up hero hand
    PlayerHands = []
    PlayerHands.append(Hand([HeroCard1,HeroCard2]))
    FirstDeck._Deck.remove(HeroCard1)
    FirstDeck._Deck.remove(HeroCard2)

    #Need to remove all known cards
    if FlopCard1 is not None:
        FirstDeck._Deck.remove(FlopCard1)
    if FlopCard2 is not None:
        FirstDeck._Deck.remove(FlopCard2)
    if FlopCard3 is not None:
        FirstDeck._Deck.remove(FlopCard3)
    if FlopCard4 is not None:
        FirstDeck._Deck.remove(FlopCard4)
    if FlopCard5 is not None:
        FirstDeck._Deck.remove(FlopCard5)

    if FlopCard1 is None:
        FlopCard1 = FirstDeck._Deck.pop()
    if FlopCard2 is None:
        FlopCard2 = FirstDeck._Deck.pop()
    if FlopCard3 is None:
        FlopCard3 = FirstDeck._Deck.pop()
    if FlopCard4 is None:
        FlopCard4 = FirstDeck._Deck.pop()
    if FlopCard5 is None:
        FlopCard5 = FirstDeck._Deck.pop()

    for i in range(1,NumPlayers):
        PlayerHands.append(Hand([FirstDeck._Deck.pop(),FirstDeck._Deck.pop()]))
    if OutputInd != 0:
        for i in range(0,NumPlayers):
            logging.debug("Player "+str(i)+" has the hand", end = " ")
            logging.debug(PlayerHands[i].getPreHandSimple())
    #Generate the flop
    if OutputInd != 0:
        print(FlopCard1)
        print(FlopCard2)
        print(FlopCard3)
        print(FlopCard4)
        print(FlopCard5)
    for i in range(0,NumPlayers):
        PlayerHands[i].addSharedCards([FlopCard1, FlopCard2, FlopCard3, FlopCard4, FlopCard5])
    for i in range(0,NumPlayers):
        HandValue = PlayerHands[i].getPostCurrentHandString()
    if OutputInd != 0:
        print("SHOWDOWN")
    winningHand = []
    for i in range(0,NumPlayers):
        winningHand.append((i,PlayerHands[i].PostHandValue))
    winningHand.sort(key=lambda t:t[1])
    if OutputInd != 0:
        print("The winner was Player " + str(winningHand[0][0]) + " with hand "
      + PlayerHands[winningHand[0][0]].getPostCurrentHandString())

    return(winningHand[0][0])

def GenerateProbabilities(NumPlayers, HeroCard1, HeroCard2, FlopCard1, FlopCard2, FlopCard3, FlopCard4 = None,
                          FlopCard5 = None, Runs = 1000, OutputInd = 0):
    HeroWin = 0

    #TODO Why does this always take 12 seconds? Maybe doing the iterations is awful
    #TODO Make the flop cards a list
    if FlopCard4 is None:
        for i in range(0,Runs):
            result = PlayOddsHand(NumPlayers,HeroCard1 ,HeroCard2 ,FlopCard1, FlopCard2, FlopCard3,
                                  OutputInd)
            if result == 0:
                HeroWin += 1
    elif FlopCard5 is None:
        for i in range(0,Runs):
            result = PlayOddsHand(NumPlayers,HeroCard1 ,HeroCard2 ,FlopCard1, FlopCard2, FlopCard3,
                                  FlopCard4, OutputInd)
            if result == 0:
                HeroWin += 1
    else:
        for i in range(0,Runs):
            result = PlayOddsHand(NumPlayers,HeroCard1 ,HeroCard2 ,FlopCard1, FlopCard2,
                                  FlopCard3, FlopCard4, FlopCard5, OutputInd)
            if result == 0:
                HeroWin += 1

    if OutputInd != 0:
        print("Hero won " + str(HeroWin) + " out of " + str(Runs) + " : " + str(HeroWin/Runs * 100))
    return (HeroWin * 100)/Runs
