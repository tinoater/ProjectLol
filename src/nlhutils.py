__author__ = 'Ahab'

import operator
import random
import logging
import logging.config
import itertools

import constants as c
import cardutils

class Game:
    def __init__(self, hand, players):
        """
        Class that takes a herohand and a list of players to create a game
        """
        #TODO: Update to pass in heroname and then call these things in the init :setHeroPosition(),setHeroPlayer("hero"),updateNumPlayers()
        self.player = players
        self.hand = hand
        self.initnumplayers = len(self.player)
        self.position = None
        # TODO need to implement an aggro parameter
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
        if hand._cards[0]._rank == 14 and hand._cards[1]._rank == 14:
            self.BHInd = 1
        else:
            self.BHInd = 0
        if hand.suitedInd == 1 or hand.connectedInd == 1:
            self.drawInd = 1
        self.PPInd = hand.PPInd
        self.bettingHist = [[], [], [], []]
        self.street = 0
        self.streetcount = 0
        self.totalhandbet = 0
        self.potamount = 0
        self.PFAggressor = 0
        self.FLAggressor = 0
        self.CBetInd = 0
        self.currbet = 0
        self.heroplayer = 0

    def setHeroPlayer(self, playername):
        for x in range(0, self.initnumplayers):
            if self.player[x].name == playername:
                self.heroplayer = x

        self.herocash = self.player[x].cash

    def getUnMovedPlayers(self):
        """
        Returns the number of players left to act from the heros position
        """
        unMovedPlayers = 0
        heropos = self.position
        if self.street == 0:
            for each in self.player:
                if each.FoldedInd != 0 and ((each.seat > heropos) or (each.seat in (0, 1))):
                    unMovedPlayers += 1
        else:
            for each in self.player:
                if each.FoldedInd != 0 and each.seat > heropos:
                    unMovedPlayers += 1

        return unMovedPlayers

    def setHeroPosition(self):
        """
        Sets the instance variable position if the position is not yet set
        :return:
        """
        if self.position == None:
            for each in self.player:
                if each.bHist[0] == [c.BETSTRING_BB]:
                    self.position = self.initnumplayers - each.seat + 2
                    break

        # If not found then hero is the BB
        if self.position == None:
            self.position = 2

    def setPreFlopInds(self):
        """
        Sets the instance variables for PFAgressor. If no one was PFAgreesor set to hero
        :return:
        """

    def setAggressorInds(self):
        """
        Set value of PFAggresActed
        :return:
        """
        tempAggres = self.heroplayer
        for each in self.player:
            try:
                if each.bHist[self.street - 1][0] in ('R','A'):
                    tempPFAggres = [pl.seat for pl in self.player].index(each.seat)
                    break
            except:
                continue
        if self.street == 1:
            if tempAggres == self.heroplayer:
                self.PFAggressor = -1
            else:
                self.PFAggressor = tempAggres

            if len(self.player[self.PFAggressor].bHist[1]) == 0:
                self.PFAggresActed = 0
            else:
                self.PFAggresActed = 1
        elif self.street == 2:
            if tempAggres == self.heroplayer:
                self.FLAggressor = -1
            else:
                self.FLAggressor = tempAggres

            if len(self.player[self.FLAggressor].bHist[1]) == 0:
                self.FLAggresActed = 0
            else:
                self.FLAggresActed = 1
        elif self.street == 3:
            if tempAggres == self.heroplayer:
                self.TAggressor = -1
            else:
                self.TAggressor = tempAggres

            if len(self.player[self.TAggressor].bHist[1]) == 0:
                self.TAggresActed = 0
            else:
                self.TAggresActed = 1

    def updateNumPlayers(self):
        """
        Updates the numPlayers instance variable
        :return:
        """
        self.numplayers = [x.FoldedInd for x in self.player].count(0)

    def updateHeroBetting(self, action, bet=0):
        """
        Sets info about the hand before each bet:
        totalhandbet, bettingHist,PFAgressor.
        """
        self.totalhandbet += bet
        self.herocash -= bet
        self.bettingHist[self.street].extend((action, bet))

        if self.street == 0:
            if action == "R":
                self.PFAggressor = 1
            else:
                self.PFAggressor = 0
        return True

        # TODO set the herocash so that it is measured in pennies

    def betoutput(self, action, bet=0, cBetInd=0):
        """
        Returns the betting action variables after they have been calculated:
        bettingaction, betamount, wait
        """
        self.streetcount += 1
        if action == 1:
            bet = self.currbet
        if self.herocash * 100 <= bet:
            self.logstr += ". Not enough cash so going all-in"
            self.updateHeroBetting(c.ACTION_DICT[3])
            return 3, 0, self.wait, self.logstr
        elif self.herocash * 100 - bet <= bet * c.RAISE_TO_ALLIN_THRESH:
            self.logstr += ". Rounding up to all in"
            self.updateHeroBetting(c.ACTION_DICT[3])
            return 3, 0, self.wait, self.logstr
        else:
            self.updateHeroBetting(action)
            self.logstr += ". Desired bet is " + str(bet)
            return action, bet, self.wait, self.logstr

    def bet(self):
        """
        Master betting function that calls the other betting functions
        :return:
        """
        # TODO - Incorporate position into betting strat
        if self.street > 0:
            self.analyseBoard()
        self.wait = random.uniform(1, 4)
        self.logstr = ""
        self.logstr += "Pot amount is " + str(self.potamount) + "\n"
        self.logstr += "Call bet amount is " + str(self.currbet) + "\n"

        oppactions = []
        for each in self.player:
            try:
                oppactions.extend(each.bHist[self.street][self.streetcount])
            except IndexError:
                oppactions.extend(each.bHist[self.street])
        self.movedPlayers = oppactions.count("R") + oppactions.count("A") + oppactions.count("C")
        self.unmovedPlayers = self.getUnMovedPlayers()
        if oppactions.count("R") + oppactions.count("A") == 0:
            self.checkedPot = 1
        else:
            self.checkedPot = 0

        if self.street == 0:
            return self.betPreFlop()
        elif self.street == 1:
            return self.betFlop()
        elif self.street == 2:
            return self.betTurn()
        elif self.street == 3:
            return self.betRiver()

    def betPreFlop(self):
        """
        Returns the betting action to be made PreFlop.
        :returns: action, betamount, wait, logstring
        """
        self.logstr = ""
        self.wait = random.uniform(3, 4)
        # Try to go all in with Aces pre-flop
        if self.BHInd == 1:
            return self.betBH()

        # Premium hands - push for max bet
        if self.madeInd == 1:
            return self.betPremMadeHand()

        # Pocket pairs - draw with all pairs if its cheap/many players. Aggressive with larger pairs
        if self.PPInd == 1:
            return self.betPP()

        # Flush or Straight Draws
        if self.drawInd == 1:
            return self.betDraw()

        # All other hands
        return self.betMisc()

    def betFlop(self):
        """
        Returns the betting action to be made on the Flop
        """
        self.logstr = ''
        self.potodds = self.currbet / (self.potamount + self.currbet)
        # set wait to zero as getting pot odds takes so long
        self.wait = 0
        self.logstr += "Pot amount is " + str(self.potamount) + "\n"
        self.logstr += "Call bet amount is " + str(self.currbet) + "\n"

        # If BH then we want to push for max value
        if self.BHInd ==1:
            return self.betBH()

        # Try CBet, else check/call
        if self.drawInd == 1:
            return self.betDraw()

        if self.madeInd == 1:
            return self.betPremMadeHand()

        return self.betMisc()

    def betTurn(self):
        """
        Returns the betting action to be made on the Turn
        """
        self.logstr = ''
        self.potodds = self.currbet / (self.potamount + self.currbet)
        # set wait to zero as getting pot odds takes so long
        self.wait = 0
        self.logstr += "Pot amount is " + str(self.potamount) + "\n"
        self.logstr += "Call bet amount is " + str(self.currbet) + "\n"

        # If BH then we want to push for max value
        if self.BHInd ==1:
            return self.betBH()

        # Try CBet, else check/call
        if self.drawInd == 1:
            return self.betDraw()

        if self.madeInd == 1:
            return self.betPremMadeHand()

        return self.betMisc()

    def betRiver(self):
        """
        Returns the betting action to be made on the River
        """
        self.logstr = ''
        self.potodds = self.currbet / (self.potamount + self.currbet)
        # set wait to zero as getting pot odds takes so long
        self.wait = 0
        self.logstr += "Pot amount is " + str(self.potamount) + "\n"
        self.logstr += "Call bet amount is " + str(self.currbet) + "\n"

        # If BH then we want to push for max value
        if self.BHInd ==1:
            return self.betBH()

        if self.madeInd == 1:
            return self.betPremMadeHand()

        return self.betMisc()

    def betBH(self):
        """
        Handles betting when the hero has BH
        :param logstr:
        :param wait:
        :return:
        """
        self.logstr += "Have best hand "
        if self.street == 0:
            bet = round(self.currbet * (random.uniform(2, 3)))
            self.logstr += "Herocash:" + str(self.herocash) + " desired raise:" + str(bet) + ". "
            return self.betoutput(2, bet)
        elif self.street == 1:
            self.logstr = "Have BH with prob " + str(self.hand.PostFlopOdds) + ". "
            if self.PFAggressor != -1:
                if self.PFAggresActed == 0 and self.checkedPot == 1 and self.streetcount == 0:
                    self.logstr += "Check to PF raiser "
                    return self.betoutput(1, self.currbet)
                elif self.PFAggresActed == 0 and self.checkedPot == 0 and self.streetcount == 0:
                    if random.uniform(0, 1) <= c.BH_FP_RAISE:
                        self.logstr += "will reraise due to threshold " + str(c.BH_FP_RAISE)
                        bet = round(self.currbet * random.uniform(2, 3))
                        return self.betoutput(2, bet)
                    else:
                        self.logstr += "call the flop bet"
                        return self.betoutput(1, self.currbet)
                elif self.streetcount == 0:
                    if self.player[self.PFAggressor].bHist[1] == "C":
                        self.logstr += "PF raiser checked(called), "
                        if self.checkedPot == 1:
                            bet = round(self.potamount * (random.uniform(0.5, 0.7)))
                            self.logstr += "unopened pot so bet"
                            return self.betoutput(2, bet)
                        elif random.uniform(0, 1) <= c.BH_FP_RAISE:
                            self.logstr += "will reraise due to threshold " + str(c.BH_FP_RAISE)
                            bet = round(self.currbet * random.uniform(2, 3))
                            return self.betoutput(2, bet)
                        else:
                            self.logstr += "call the flop bet"
                            return self.betoutput(1, self.currbet)
                else:
                    self.logstr += " further round of betting, so reraise"
                    bet = round(self.currbet * random.uniform(2, 3))
                    return self.betoutput(2, bet)
            if self.PFAggressor == -1 and self.checkedPot == 1:
                bet = round(self.potamount * (random.uniform(0.5, 0.7)))
                self.logstr += " Open pot with a raise"
                return self.betoutput(2, bet)
            elif self.PFAggressor == -1 and self.checkedPot == 0:
                if random.uniform(0, 1) <= c.BH_FP_RAISE:
                    self.logstr += " will reraise due to threshold " + str(c.BH_FP_RAISE) + "."
                    bet = round(self.currbet * random.uniform(2, 3))
                    return self.betoutput(2, bet)
                else:
                    self.logstr += " will smooth call"
                    return self.betoutput(1, self.currbet)
            else:
                self.logstr += "No action defined!"
                logging.error("No action defined in Flop bet BH==1")
                return self.betoutput(0, 0)
        elif self.street == 2:
            self.logstr = "Have BH with prob " + str(self.hand.PostFlopOdds) + ". "
            if self.FLAggressor != -1:
                if self.FLAggresActed == 0 and self.checkedPot == 1 and self.streetcount == 0:
                    self.logstr += "Check to FL raiser "
                    return self.betoutput(1, self.currbet)
                elif self.FLAggresActed == 0 and self.checkedPot == 0 and self.streetcount == 0:
                    if random.uniform(0, 1) <= c.BH_T_RAISE:
                        self.logstr += "will reraise due to threshold " + str(c.BH_T_RAISE)
                        bet = round(self.currbet * random.uniform(2, 3))
                        return self.betoutput(2, bet)
                    else:
                        self.logstr += "call the flop bet"
                        return self.betoutput(1, self.currbet)
                elif self.streetcount == 0:
                    if self.player[self.FLAggressor].bHist[1] == "C":
                        self.logstr += "FL raiser checked(called), "
                        if self.checkedPot == 1:
                            bet = round(self.potamount * (random.uniform(0.5, 0.7)))
                            self.logstr += "unopened pot so bet"
                            return self.betoutput(2, bet)
                        elif random.uniform(0, 1) <= c.BH_T_RAISE:
                            self.logstr += "will reraise due to threshold " + str(c.BH_T_RAISE)
                            bet = round(self.currbet * random.uniform(2, 3))
                            return self.betoutput(2, bet)
                        else:
                            self.logstr += "call the turn bet"
                            return self.betoutput(1, self.currbet)
                else:
                    self.logstr += " further round of betting, so reraise"
                    bet = round(self.currbet * random.uniform(2, 3))
                    return self.betoutput(2, bet)
            if self.FLAggressor == -1 and self.checkedPot == 1:
                bet = round(self.potamount * (random.uniform(0.5, 0.7)))
                self.logstr += " Open pot with a raise"
                return self.betoutput(2, bet)
            elif self.FLAggressor == -1 and self.checkedPot == 0:
                if random.uniform(0, 1) <= c.BH_T_RAISE:
                    self.logstr += " will reraise due to threshold " + str(c.BH_T_RAISE) + "."
                    bet = round(self.currbet * random.uniform(2, 3))
                    return self.betoutput(2, bet)
                else:
                    self.logstr += " will smooth call"
                    return self.betoutput(1, self.currbet)
            else:
                self.logstr += "No action defined!"
                logging.error("No action defined in Turn bet BH==1")
                return self.betoutput(0, 0)
        elif self.street == 3:
            self.logstr = "Have BH with prob " + str(self.hand.PostFlopOdds) + ". "
            if self.TAggressor != -1:
                if self.TAggresActed == 0 and self.checkedPot == 1 and self.streetcount == 0:
                    self.logstr += "Check to T raiser "
                    return self.betoutput(1, self.currbet)
                elif self.TAggresActed == 0 and self.checkedPot == 0 and self.streetcount == 0:
                    if random.uniform(0, 1) <= c.BH_R_RAISE:
                        self.logstr += "will reraise due to threshold " + str(c.BH_R_RAISE)
                        bet = round(self.currbet * random.uniform(2, 3))
                        return self.betoutput(2, bet)
                    else:
                        self.logstr += "call the river bet"
                        return self.betoutput(1, self.currbet)
                elif self.streetcount == 0:
                    if self.player[self.TAggressor].bHist[1] == "C":
                        self.logstr += "T raiser checked(called), "
                        if self.checkedPot == 1:
                            bet = round(self.potamount * (random.uniform(0.5, 0.7)))
                            self.logstr += "unopened pot so bet"
                            return self.betoutput(2, bet)
                        elif random.uniform(0, 1) <= c.BH_R_RAISE:
                            self.logstr += "will reraise due to threshold " + str(c.BH_R_RAISE)
                            bet = round(self.currbet * random.uniform(2, 3))
                            return self.betoutput(2, bet)
                        else:
                            self.logstr += "call the river bet"
                            return self.betoutput(1, self.currbet)
                else:
                    self.logstr += " further round of betting, so reraise"
                    bet = round(self.currbet * random.uniform(2, 3))
                    return self.betoutput(2, bet)
            if self.TAggressor == -1 and self.checkedPot == 1:
                bet = round(self.potamount * (random.uniform(0.5, 0.7)))
                self.logstr += " Open pot with a raise"
                return self.betoutput(2, bet)
            elif self.TAggressor == -1 and self.checkedPot == 0:
                if random.uniform(0, 1) <= c.BH_R_RAISE:
                    self.logstr += " will reraise due to threshold " + str(c.BH_R_RAISE) + "."
                    bet = round(self.currbet * random.uniform(2, 3))
                    return self.betoutput(2, bet)
                else:
                    self.logstr += " will smooth call"
                    return self.betoutput(1, self.currbet)
            else:
                self.logstr += "No action defined!"
                logging.error("No action defined in River bet BH==1")
                return self.betoutput(0, 0)

    def betPP(self):
        if self.street == 0:
            self.logstr += "Have pocket pairs "
            if self.movedPlayers == 0:
                self.logstr += "First to enter the pot "
                if self.hand.PPCard >= 9:
                    self.logstr += "Strong pair so raise "
                    bet = round(c.BIGBLIND * (random.uniform(2, 3)))
                    return self.betoutput(2, bet)
                else:
                    if random.uniform(0, 1) <= c.PF_PP_BELOW_9_RAISE:
                        bet = round(c.BIGBLIND * (random.uniform(2, 3)))
                        self.logstr += "Weak pair but raise anyway. Parameter:" + str(c.PF_PP_BELOW_9_RAISE)
                        return self.betoutput(2, bet)
                    elif random.uniform(0, 1) <= c.PF_PP_BELOW_9_CALL:
                        self.logstr += "Call to draw to set"
                        return self.betoutput(1, self.currbet)
                    else:
                        return self.betoutput(0, 0)
            else:
                predictedSDPot = c.PF_SMALL_PAIR * ((self.movedPlayers * c.PF_CALL_AFTER_RAISE_PERC)
                                                    + (self.unmovedPlayers * c.PF_CALL_PERC))
                self.logstr += "\n Other players are in the pot. Prediction of pot size is:" + str(predictedSDPot)
                if c.PF_SMALL_PAIR / 10 * predictedSDPot >= self.currbet:
                    self.logstr += " Call worth it"
                    return self.betoutput(1, self.currbet)
                else:
                    self.logstr += " Call not worth it"
                    return self.betoutput(0, 0)

    def betPremMadeHand(self):
        # TODO: Add some generic call logic function here
        if self.street == 0:
            self.logstr += "Have a premium made hand "
            if self.checkedPot == 1:
                bet = round(self.currbet * (random.uniform(2, 3)))
                self.logstr += "Open pot with a raise"
                return self.betoutput(2, bet)
            else:
                if self.currbet <= 3 * c.BIGBLIND:
                    bet = round(self.currbet * (random.uniform(2, 3)))
                    self.logstr += "Will reraise as currbet:" + str(self.currbet)
                    return self.betoutput(2, bet)
                else:
                    if random.uniform(0, 1) <= c.PF_PREM_RERAISE_PERC:
                        self.logstr += "Currbet is large, but will reraise anyway. Parameter:" + str(c.PF_PREM_RERAISE_PERC)
                        bet = round(self.currbet * (random.uniform(2, 3)))
                        return self.betoutput(2, bet)
                    else:
                        self.logstr += "Will call"
                        return self.betoutput(1, self.currbet)
        elif self.street == 1:
            self.logstr += "Have a made hand."
            if self.checkedPot == 1:
                self.logstr += "Open the pot."
                bet = round(self.potamount * random.uniform(0.5, 0.7))
                return self.betoutput(2, bet)
            else:
                self.logstr += "Call the bet."
                return self.betoutput(1, self.currbet)
        elif self.street == 2:
            self.logstr += "Have a made hand."
            if self.checkedPot == 1:
                self.logstr += "Open the pot."
                bet = round(self.potamount * random.uniform(0.5, 0.7))
                return self.betoutput(2, bet)
            else:
                self.logstr += "Call the bet."
                return self.betoutput(1, self.currbet)
        elif self.street == 3:
            self.logstr += "Have a made hand."
            if self.checkedPot == 1:
                self.logstr += "Open the pot."
                bet = round(self.potamount * random.uniform(0.5, 0.7))
                return self.betoutput(2, bet)
            else:
                self.logstr += "Call the bet."
                return self.betoutput(1, self.currbet)

    def betDraw(self):
        if self.street == 0:
            if self.hand.suitedInd == 1 and self.hand.connectedInd == 1:
                self.logstr += ",have a connected flush draw"
                predictedSDPot = c.PF_STRFL_DRAW * ((self.movedPlayers * c.PF_CALL_AFTER_RAISE_PERC
                                                     + self.unmovedPlayers * c.PF_CALL_PERC) * self.currbet + self.potamount)
                self.logstr += "\n Predicted pot size / factor >= bet * high card scale?:"
                self.logstr += str(predictedSDPot) + " / " + str(c.PF_STRFL_ODDS) + " >= " + str(self.currbet) + " * " \
                               + str(14 / self.hand.highcard) + " ? \n"
                if predictedSDPot / c.PF_STRFL_ODDS >= (self.currbet * 14 / self.hand.highcard):
                    self.logstr += " Call worth it"
                    return self.betoutput(1, self.currbet)
            self.logstr += "Have a flush or straight draw"
            if self.hand.suitedInd == 1:
                self.logstr += ",have a flush draw"
                predictedSDPot = c.PF_FL_DRAW * ((self.movedPlayers * c.PF_CALL_AFTER_RAISE_PERC
                                                  + self.unmovedPlayers * c.PF_CALL_PERC) * self.currbet + self.potamount)
                self.logstr += "\n Predicted pot size / factor >= bet * high card scale?:"
                self.logstr += str(predictedSDPot) + " / " + str(c.PF_FL_ODDS) + " >= " + str(self.currbet) + " * " \
                               + str(14 / self.hand.highcard) + " ? \n"
                if predictedSDPot / c.PF_FL_ODDS >= (self.currbet * 14 / self.hand.highcard):
                    self.logstr += " Call worth it"
                    return self.betoutput(1, self.currbet)
            if self.hand.connectedInd == 1:
                self.logstr += ",have a straight draw"
                predictedSDPot = c.PF_STR_DRAW * ((self.movedPlayers * c.PF_CALL_AFTER_RAISE_PERC
                                                   + self.unmovedPlayers * c.PF_CALL_PERC) * self.currbet + self.potamount)
                self.logstr += "\n Predicted pot size / factor >= bet * high card scale?:"
                self.logstr += str(predictedSDPot) + " / " + str(c.PF_STR_ODDS) + " >= " + str(self.currbet) + " * " \
                               + str(14 / self.hand.highcard) + " ? \n"
                if predictedSDPot / c.PF_STR_ODDS >= (self.currbet * 14 / self.hand.highcard):
                    self.logstr += " Call worth it"
                    return self.betoutput(1, self.currbet)
        elif self.street == 1:
            self.logstr += "Have a drawing hand."
            if self.checkedPot == 1:
                self.logstr += "Checked pot."
                if self.PFAggressor == -1:
                    self.logstr += "Was the PF Agressor."
                    if self.shouldCBet() == 1:
                        self.CBetInd == 1
                        self.logstr += "Will CBet anyway."
                        bet = round(self.potamount * random.uniform(0.5, 0.7))
                        return self.betoutput(2, bet)
                    else:
                        self.logstr += "Will try to draw for free."
                        return self.betoutput(1, self.currbet)
                else:
                    self.logstr += "Was not the PF Agrssor."
                    if self.shouldSteal() == 1:
                        self.logstr += "Try to steal flop."
                        bet = round(self.potamount * random.uniform(0.5, 0.7))
                        return self.betoutput(2, bet)
                    else:
                        self.logstr += "Will try to draw for free."
                        return self.betoutput(1, self.currbet)
            else:
                self.logstr += "Pots been opened."
                if self.shouldDraw == 1:
                    self.logstr += "Try to draw."
                    return self.betoutput(1, self.currbet)
        elif self.street == 2:
            self.logstr += "Have a drawing hand."
            if self.checkedPot == 1:
                self.logstr += "Checked pot."
                if self.FLAggressor == -1:
                    self.logstr += "Was the FL Agressor."
                    if self.shouldCBet() == 1:
                        self.CBetTInd == 1
                        self.logstr += "Will CBet anyway."
                        bet = round(self.potamount * random.uniform(0.5, 0.7))
                        return self.betoutput(2, bet)
                    else:
                        self.logstr += "Will try to draw for free."
                        return self.betoutput(1, self.currbet)
                else:
                    self.logstr += "Was not the FL Agrssor."
                    if self.shouldSteal() == 1:
                        self.logstr += "Try to steal turn."
                        bet = round(self.potamount * random.uniform(0.5, 0.7))
                        return self.betoutput(2, bet)
                    else:
                        self.logstr += "Will try to draw for free."
                        return self.betoutput(1, self.currbet)
            else:
                self.logstr += "Pots been opened."
                if self.shouldDraw == 1:
                    self.logstr += "Try to draw."
                    return self.betoutput(1, self.currbet)

    def betMisc(self):
        # TODO: Add logic to steal a boring looking flop
        if self.street == 0:
            self.logstr += "Misc. hands"
            if self.checkedPot == 1:
                self.logstr += "No one has entered pot "
                self.logstr += "\n Hand Odds are:" + str(self.preFlopOdds10 / 100) + " Adjusted odds are:" \
                               + str((self.preFlopOdds10 / 100 * random.uniform(0, 1))) + " threshold is:" + str(
                    c.PF_OTHER_HANDS_OPEN)
                if self.preFlopOdds10 >= 10 and (self.preFlopOdds10 / 100 * random.uniform(0, 1) <= c.PF_OTHER_HANDS_OPEN):
                    bet = round(c.BIGBLIND * (random.uniform(2, 3)))
                    self.logstr += "Open raise"
                    return self.betoutput(2, bet)

            if self.checkedPot == 0:
                self.logstr += " People have entered the pot"
                self.logstr += " Hand Odds are:" + str(self.preFlopOdds10) + " Adjusted odds are:" \
                               + str((self.preFlopOdds10 / 100 * random.uniform(0, 1))) + " threshold is:" + str(
                    c.PF_OTHER_HANDS_CALL)
                if self.preFlopOdds10 >= 10 and (self.preFlopOdds10 / 100 * random.uniform(0, 1) <= c.PF_OTHER_HANDS_CALL):
                    if self.currbet <= 3 * c.BIGBLIND:
                        return self.betoutput(1, self.currbet)

            # If no one has opened the pot then try to steal
            if self.checkedPot == 1:
                self.logstr += " No one has entered the pot"
                self.logstr += " Steal threshold is:" + str(c.PF_STEAL)
                if self.unmovedPlayers <= 3 and (random.uniform(0, 1) <= c.PF_STEAL):
                    bet = round(c.BIGBLIND * (random.uniform(2, 3)))
                    self.logstr += " Attempt to steal"
                    return self.betoutput(2, bet)

                    # Else just fold
                self.logstr += " Just fold"
                return self.betoutput(0, 0)
        elif self.street == 1:
            self.logstr += "Have a misc hand."
            if self.PFAggressor == -1:
                self.logstr += "Was the PF aggressor."
                if self.checkedPot == 1:
                    self.logstr += "Pot has been checked"
                    if self.shouldCBet() == 1:
                        self.logstr += "Will try to CBet."
                        bet = round(self.potamount * random.uniform(0.5, 0.7))
                        return self.betoutput(2, bet)
                    else:
                        self.logstr += "Won't CBet"
                        return self.betoutput(1, self.currbet)
                else:
                    self.logstr += "Pot has been opened."
                    if self.shouldCall() == 1:
                        self.logstr += "Will call"
                        return self.betoutput(1, self.currbet)
                    else:
                        self.logstr += "Will fold"
                        return self.betoutput(0, 0)
            else:
                self.logstr += "Was not the PF aggressor."
                if self.checkedPot == 1:
                    self.logstr += "Pot has been checked"
                    if self.shouldSteal() == 1:
                        self.logstr += "Will try to Steal."
                        bet = round(self.potamount * random.uniform(0.5, 0.7))
                        return self.betoutput(2, bet)
                    else:
                        self.logstr += "Won't Steal."
                        return self.betoutput(1, self.currbet)
                else:
                    self.logstr += "Pot has been opened."
                    if self.shouldCall() == 1:
                        self.logstr += "Will call"
                        return self.betoutput(1, self.currbet)
                    else:
                        self.logstr += "Will fold"
                        return self.betoutput(0, 0)

    def analyseBoard(self):
        """
        Sets the instances board information:
        BHInd, drawInd, drawPresent, PFAggresActed, PFAggressor
        """
        if self.streetcount == 0:
            self.setAggressorInds()
            self.setPreFlopInds()

        if self.hand.PostFlopOdds >= c.BH_THRESHOLD:
            self.BHInd = 1
        else:
            self.BHInd = 0

        # TODO: Empty logic for altering BHInd for flush and straights
        if self.hand.PostHandType == 5 and self.hand.HighCard != 14:
            pass
        if self.hand.PostHandType == 4:
            pass

        rank_list = []
        suit_list = []
        sharedrank_list = []
        sharedsuit_list = []
        for each in self.hand._cards:
            rank_list.append(int(each._rank))
            suit_list.append(each._suit)
        rank_list = list(set(rank_list))
        rank_list.sort()

        for each in self.hand.sharedCards:
            sharedrank_list.append(int(each._rank))
            sharedsuit_list.append(each._suit)
        sharedrank_list = list(set(sharedrank_list))
        sharedrank_list.sort()

        if max(map(lambda x: suit_list.count(x), [1, 2, 3, 4])) == 4 and self.hand.suitedInd == 1:
            self.drawInd = 1
            logging.info("We have a flush draw")
        else:
            self.drawInd = 0

        # TODO: This won't deal with 1 card in a straight draw
        if self.hand.connectedInd == 1:
            for k, g in itertools.groupby(enumerate(rank_list), lambda x: x[0] - x[1]):
                thing = list(map(operator.itemgetter(1), g))
                if thing.__len__() == 4:
                    self.drawInd = 1
                    self.drawStraightOdds = 2 * 8 / 100
                    logging.info("We have a straight draw")
                else:
                    self.drawStraightOdds == 0

        if max(map(lambda x: sharedsuit_list.count(x), [1, 2, 3, 4])) == 2:
            self.drawPresentInd = 1
            self.drawFlushOdds = 2 * 12 / 100
            logging.info("There is a flush draw")
        else:
            self.drawPresentInd = 0
            self.drawFlushOdds = 0

        # TODO: This won't deal with 1 card in a straight draw
        for k, g in itertools.groupby(enumerate(sharedrank_list), lambda x: x[0] - x[1]):
            thing = list(map(operator.itemgetter(1), g))
            if thing.__len__() == 3:
                self.drawPresentInd = 1
                logging.info("There is a straight draw")

        if self.hand.PostHandType <= 8:
            self.madeInd = 1
        else:
            self.madeInd = 0

    def shouldCBet(self):
        """
        Returns ind if flop should be CBet
        """
        # TODO: Improve this Cbet proc
        # TODO: Add street ind to also handle Turn (and River?) CBet
        if self.street == 1:
            if random.uniform(0, 1) <= c.FLOP_CBET:
                return 1
            else:
                return 0
        elif self.street == 2:
            if random.uniform(0, 1) <= c.TURN_CBET:
                return 1
            else:
                return 0
        elif self.street == 3:
            if random.uniform(0, 1) <= c.RIVER_CBET:
                return 1
            else:
                return 0

    def shouldSteal(self):
        """
        Returns ind if flop should be stolen
        """
        # TODO: Improve the flop steal
        if self.street == 1:
            if random.uniform(0, 1) <= c.FLOP_STEAL:
                return 1
            else:
                return 0
        elif self.street == 2:
            if random.uniform(0, 1) <= c.TURN_STEAL:
                return 1
            else:
                return 0
        elif self.street == 3:
            if random.uniform(0, 1) <= c.RIVER_STEAL:
                return 1
            else:
                return 0

    def shouldDraw(self):
        """
        Returns ind if a draw is worth drawing for. Uses the potodds vs the drawodds
        """
        # TODO: Improve the draw proc
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
        """
        Returns ind to handle making calls with middling hands. Uses potodds vs currentbet
        """
        # TODO: Improve
        # TODO: Take street input and use this on later streets
        if self.potodds <= self.currbet:
            return 1
        else:
            return 0


def PlayOddsHand(NumPlayers, HeroCards, FlopCards, OutputInd=0):
    """
    Returns ind if the hero won the game given a heros hand and either the flop, turn or river shared cards
    """
    removeList = []
    for each in HeroCards:
        removeList.append(each)
    for each in FlopCards:
        removeList.append(each)
    try:
        removeList.remove(None)
    except:
        pass

    # Set up the Deck
    FirstDeck = cardutils.Deck(removeList)
    FirstDeck.shuffle()
    # Set up hero hand
    PlayerHands = []
    PlayerHands.append(cardutils.Hand(HeroCards[0], HeroCards[1], setCalcAllStreetValues = 0))

    while len(FlopCards)<5:
        FlopCards.append(FirstDeck._Deck.pop())

    for i in range(1, NumPlayers):
        PlayerHands.append(cardutils.Hand(FirstDeck._Deck.pop(), FirstDeck._Deck.pop(), setCalcAllStreetValues = 0))
    if OutputInd != 0:
        for i in range(0, NumPlayers):
            logging.debug("Player " + str(i) + " has the hand", end=" ")
            logging.debug(PlayerHands[i].getPreHandSimple())
    # Generate the flop
    if OutputInd != 0:
        for each in FlopCards:
            print(each)
    for i in range(0, NumPlayers):
        PlayerHands[i].addSharedCards(FlopCards)
    if OutputInd != 0:
        print("SHOWDOWN")
    winningHand = []
    for i in range(0, NumPlayers):
        winningHand.append((i, PlayerHands[i].PostHandValue))
    winningHand.sort(key=lambda t: t[1])
    if OutputInd != 0:
        print("The winner was Player " + str(winningHand[0][0]) + " with hand "
              + PlayerHands[winningHand[0][0]].getPostCurrentHandString())

    return (winningHand[0][0])


def GenerateProbabilities(NumPlayers, HeroCards, FlopCards, Runs=1000, OutputInd=0):
    """
    Outputs the Monte Carlo chance of heros odds. Runs PlaysOddsHands in a loop
    """
    HeroWin = 0
    for i in range(0, Runs):
        result = PlayOddsHand(NumPlayers, HeroCards, FlopCards, OutputInd = OutputInd)
        if result == 0:
            HeroWin += 1

    if OutputInd != 0:
        print("Hero won " + str(HeroWin) + " out of " + str(Runs) + " : " + str(HeroWin / Runs * 100))
    return (HeroWin * 100) / Runs
