__author__ = 'Ahab'

import operator
import random
import logging
import logging.config
import itertools

import constants as c
import cardutils


class Game:
    def __init__(self, hand, players, **kwargs):
        """
        Class that takes a herohand and a list of players to create a game
        """
        self.players = players
        self.hand = hand
        self.initNumPlayers = len(self.players)
        self.position = None
        # TODO need to implement an aggro parameter
        self.preFlopOdds = hand.preFlopOdds
        self.preFlopOdds10 = hand.preFlopOdds10
        self.postFlopOdds = hand.postFlopOdds
        if hand.PPInd == 1:
            self.drawInd = 1
        else:
            self.drawInd = 0
        if hand.premInd == 1:
            self.madeInd = 1
        else:
            self.madeInd = 0
        if hand.cards[0].rank == 14 and hand.cards[1].rank == 14:
            self.BHInd = 1
        else:
            self.BHInd = 0
        if hand.suitedInd == 1 or hand.connectedInd == 1:
            self.drawInd = 1
        self.PPInd = hand.PPInd
        self.bettingHist = [[], [], [], []]
        self.heroCash = 0.00
        self.street = 0
        self.streetCount = 0
        self.totalHandBet = 0
        self.potAmount = 0
        self.PFAggressor = None
        self.PFAggresActed = None
        self.FLAggressor = None
        self.FLAggresActed = None
        self.TAggressor = None
        self.TAggresActed = None
        self.CBetInd = 0
        self.currBet = 0
        self.heroPlayer = 0
        self.numPlayers = 0

        # Betting variables
        self.wait = 0
        self.errorstr = ""
        self.logstr = ""
        self.movedPlayers = 0
        self.unmovedPlayers = 0
        self.checkedPot = 0
        self.potOdds = 0
        self.CBetTInd = 0
        self.drawFlushOdds = 0
        self.drawStraightOdds = 0
        self.drawPresentInd = 0

        if kwargs.get("heroName") is not None:
            self.setHeroPlayer(kwargs.get("heroName"))

    def setHeroPlayer(self, playername):
        for x in range(0, self.initNumPlayers):
            if self.players[x].name == playername:
                self.heroPlayer = x

        self.heroCash = self.players[x].cash

    def getUnMovedPlayers(self):
        """
        Returns the number of players left to act from the heros position
        """
        unmovedplayers = 0
        heropos = self.position
        if self.street == 0:
            for each in self.players:
                if each.FoldedInd != 0 and ((each.seat > heropos) or (each.seat in (0, 1))):
                    unmovedplayers += 1
        else:
            for each in self.players:
                if each.FoldedInd != 0 and each.seat > heropos:
                    unmovedplayers += 1

        return unmovedplayers

    def setHeroPosition(self):
        """
        Sets the instance variable position if the position is not yet set

        This is done by finding the BB and counting back
        :return:
        """
        if self.position is None:
            for each in self.players:
                if each.bHist[0] == [cardutils.BETSTRING_DICT["BB"]]:
                    self.position = self.initNumPlayers - each.seat + 2
                    break

        # If not found then hero is the BB
        if self.position is None:
            self.position = 2

    def setAggressorInds(self):
        """
        Set value of street aggressors from the previous street and if they have acted on this street
        :return:
        """
        tempaggres = self.heroPlayer
        for each in self.players:
            try:
                if each.bHist[self.street - 1][-1] in (
                        cardutils.BETSTRING_DICT['RAISE'], cardutils.BETSTRING_DICT['ALLIN']):
                    tempaggres = [pl.seat for pl in self.players].index(each.seat)
                    break
            except:
                continue
        if self.street == 1:
            if tempaggres == self.heroPlayer:
                self.PFAggressor = -1
                self.PFAggresActed = 0
            else:
                self.PFAggressor = tempaggres
                if len(self.players[self.PFAggressor].bHist[1]) == 0:
                    self.PFAggresActed = 0
                else:
                    self.PFAggresActed = 1
        elif self.street == 2:
            if tempaggres == self.heroPlayer:
                self.FLAggressor = -1
                self.FLAggresActed = 0
            else:
                self.FLAggressor = tempaggres
                if len(self.players[self.FLAggressor].bHist[1]) == 0:
                    self.FLAggresActed = 0
                else:
                    self.FLAggresActed = 1
        elif self.street == 3:
            if tempaggres == self.heroPlayer:
                self.TAggressor = -1
                self.TAggresActed = 0
            else:
                self.TAggressor = tempaggres
                if len(self.players[self.TAggressor].bHist[1]) == 0:
                    self.TAggresActed = 0
                else:
                    self.TAggresActed = 1

    def setPotOdds(self):
        """
        Sets the pot odds of the game
        :return:
        """
        self.potOdds = self.currBet / (self.potAmount + self.currBet)

    def updateNumPlayers(self):
        """
        Updates the numPlayers instance variable
        :return:
        """
        self.numPlayers = [x.FoldedInd for x in self.players].count(0)

    def updateHeroBetting(self, action, bet=0.00):
        """
        Sets info about the hand before each bet:
        totalHandBet, bettingHist.
        """
        self.totalHandBet += bet
        self.heroCash -= bet
        self.bettingHist[self.street].extend((action, bet))

    def addLogging(self, msg, errortype=0):
        """
        Handles logging for the betting program
        :param msg: logging string
        :param errortype: 0 = logging, 1 = error
        :return:
        """
        separator = "\n"
        if errortype == 0:
            msg += separator
            self.logstr += msg

        if errortype == 1:
            msg += separator
            self.errorstr += msg

    def betOutput(self, action, bet=0.00):
        """
        Returns the betting action variables after they have been calculated:
        bettingaction, betamount, wait
        """
        self.streetCount += 1
        if action == 1:
            bet = self.currBet
        if self.heroCash <= bet:
            self.addLogging("Not enough cash so going all-in")
            self.updateHeroBetting(cardutils.BETSTRING_DICT["ALLIN"])
            return 3, 0, self.wait, self.logstr
        elif self.heroCash - bet <= bet * c.RAISE_TO_ALLIN_THRESH:
            self.addLogging("Rounding up to all in")
            self.updateHeroBetting(cardutils.BETSTRING_DICT["ALLIN"])
            return 3, 0, self.wait, self.logstr
        else:
            self.updateHeroBetting(action)
            self.addLogging("Calculated bet is " + str(bet))
            return action, bet, self.wait, self.logstr

    def bet(self):
        """
        Master betting function that calls the other betting functions
        :return:
        """
        # TODO - Incorporate position into betting strat
        # TODO: Add some generic call logic function for premMadeHands
        # TODO: Add logic to steal a boring looking flop for Misc hands
        if self.street > 0:
            self.analyseBoard()
        self.wait = random.uniform(1, 4)
        self.errorstr = ""
        self.logstr = ""
        self.addLogging("Pot amount is " + str(self.potAmount) + " Call bet amount is " + str(self.currBet))

        oppactions = []
        for each in self.players:
            try:
                oppactions.extend(each.bHist[self.street][self.streetCount])
            except IndexError:
                oppactions.extend(each.bHist[self.street])
        self.movedPlayers = oppactions.count(cardutils.BETSTRING_DICT['RAISE']) \
                            + oppactions.count(cardutils.BETSTRING_DICT['ALLIN']) \
                            + oppactions.count(cardutils.BETSTRING_DICT['CALL'])
        self.unmovedPlayers = self.getUnMovedPlayers()
        if oppactions.count(cardutils.BETSTRING_DICT['RAISE']) \
                + oppactions.count(cardutils.BETSTRING_DICT['ALLIN']) == 0:
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
        else:
            raise Exception("Street incorrect - cannot devise bet")

    def betPreFlop(self):
        """
        Returns the betting action to be made PreFlop.
        :returns:
        """
        self.wait = random.uniform(3, 4)
        # Try to go all in with Aces pre-flop
        if self.BHInd == 1:
            return self.betBHStreet0()

        # Premium hands - push for max bet
        if self.madeInd == 1:
            return self.betPremMadeHandStreet0()

        # Pocket pairs - draw with all pairs if its cheap/many players. Aggressive with larger pairs
        if self.PPInd == 1:
            return self.betPPStreet0()

        # Flush or Straight Draws
        if self.drawInd == 1:
            return self.betDrawStreet0()

        # All other hands
        return self.betMiscStreet0()

    def betFlop(self):
        """
        Returns the betting action to be made on the Flop
        """
        self.setPotOdds()
        # set wait to zero as getting pot odds takes so long
        self.wait = 0

        # If BH then we want to push for max value
        if self.BHInd == 1:
            return self.betBHStreet1()

        # Try CBet, else check/call
        if self.drawInd == 1:
            return self.betDrawStreet1()

        if self.madeInd == 1:
            return self.betPremMadeHandStreet1()

        return self.betMiscStreet1()

    def betTurn(self):
        """
        Returns the betting action to be made on the Turn
        """
        self.setPotOdds()
        # set wait to zero as getting pot odds takes so long
        self.wait = 0

        # If BH then we want to push for max value
        if self.BHInd == 1:
            return self.betBHStreet2()

        # Try CBet, else check/call
        if self.drawInd == 1:
            return self.betDrawStreet2()

        if self.madeInd == 1:
            return self.betPremMadeHandStreet2()

        return self.betMiscStreet2()

    def betRiver(self):
        """
        Returns the betting action to be made on the River
        """
        self.setPotOdds()
        # set wait to zero as getting pot odds takes so long
        self.wait = 0

        # If BH then we want to push for max value
        if self.BHInd == 1:
            return self.betBHStreet3()

        if self.madeInd == 1:
            return self.betPremMadeHandStreet3()

        return self.betMiscStreet3()

    def betBHStreet0(self):
        bet = round(self.currBet * (random.uniform(2, 3)))
        self.addLogging("Herocash:" + str(self.heroCash) + " Calculated raise:" + str(bet))
        return self.betOutput(2, bet)

    def betBHStreet1(self):
        self.addLogging("Have BH with prob " + str(self.hand.PostFlopOdds))
        if self.PFAggressor != -1:
            if self.PFAggresActed == 0 and self.checkedPot == 1 and self.streetCount == 0:
                self.addLogging("Check to PF raiser")
                return self.betOutput(1, self.currBet)
            elif self.PFAggresActed == 0 and self.checkedPot == 0 and self.streetCount == 0:
                if random.uniform(0, 1) <= c.BH_FP_RAISE:
                    self.addLogging("Will reraise due to threshold" + str(c.BH_FP_RAISE))
                    bet = round(self.currBet * random.uniform(2, 3))
                    return self.betOutput(2, bet)
                else:
                    self.addLogging("Call the flop bet")
                    return self.betOutput(1, self.currBet)
            elif self.streetCount == 0:
                if self.players[self.PFAggressor].bHist[1] == "C":
                    self.addLogging("PF raiser checked(called)")
                    if self.checkedPot == 1:
                        bet = round(self.potAmount * (random.uniform(0.5, 0.7)))
                        self.addLogging("Unopened pot so bet")
                        return self.betOutput(2, bet)
                    elif random.uniform(0, 1) <= c.BH_FP_RAISE:
                        self.addLogging("Will reraise due to threshold " + str(c.BH_FP_RAISE))
                        bet = round(self.currBet * random.uniform(2, 3))
                        return self.betOutput(2, bet)
                    else:
                        self.addLogging("Call the flop bet")
                        return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Further round of betting, so reraise")
                bet = round(self.currBet * random.uniform(2, 3))
                return self.betOutput(2, bet)
        if self.PFAggressor == -1 and self.checkedPot == 1:
            bet = round(self.potAmount * (random.uniform(0.5, 0.7)))
            self.addLogging("Open pot with a raise")
            return self.betOutput(2, bet)
        elif self.PFAggressor == -1 and self.checkedPot == 0:
            if random.uniform(0, 1) <= c.BH_FP_RAISE:
                self.addLogging("Will reraise due to threshold " + str(c.BH_FP_RAISE))
                bet = round(self.currBet * random.uniform(2, 3))
                return self.betOutput(2, bet)
            else:
                self.addLogging("Will smooth call")
                return self.betOutput(1, self.currBet)
        else:
            self.addLogging("No action defined!")
            self.addLogging("No action defined in Flop bet BH==1", 1)
            return self.betOutput(0, 0)

    def betBHStreet2(self):
        self.addLogging("Have BH with prob " + str(self.hand.PostFlopOdds))
        if self.FLAggressor != -1:
            if self.FLAggresActed == 0 and self.checkedPot == 1 and self.streetCount == 0:
                self.addLogging("Check to FL raiser")
                return self.betOutput(1, self.currBet)
            elif self.FLAggresActed == 0 and self.checkedPot == 0 and self.streetCount == 0:
                if random.uniform(0, 1) <= c.BH_T_RAISE:
                    self.addLogging("Will reraise due to threshold " + str(c.BH_T_RAISE))
                    bet = round(self.currBet * random.uniform(2, 3))
                    return self.betOutput(2, bet)
                else:
                    self.addLogging("Call the flop bet")
                    return self.betOutput(1, self.currBet)
            elif self.streetCount == 0:
                if self.players[self.FLAggressor].bHist[1] == "C":
                    self.addLogging("FL raiser checked(called)")
                    if self.checkedPot == 1:
                        bet = round(self.potAmount * (random.uniform(0.5, 0.7)))
                        self.addLogging("Unopened pot so bet")
                        return self.betOutput(2, bet)
                    elif random.uniform(0, 1) <= c.BH_T_RAISE:
                        self.addLogging("Will reraise due to threshold " + str(c.BH_T_RAISE))
                        bet = round(self.currBet * random.uniform(2, 3))
                        return self.betOutput(2, bet)
                    else:
                        self.addLogging("Call the turn bet")
                        return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Further round of betting, so reraise")
                bet = round(self.currBet * random.uniform(2, 3))
                return self.betOutput(2, bet)
        if self.FLAggressor == -1 and self.checkedPot == 1:
            bet = round(self.potAmount * (random.uniform(0.5, 0.7)))
            self.addLogging("Open pot with a raise")
            return self.betOutput(2, bet)
        elif self.FLAggressor == -1 and self.checkedPot == 0:
            if random.uniform(0, 1) <= c.BH_T_RAISE:
                self.addLogging("Will reraise due to threshold " + str(c.BH_T_RAISE))
                bet = round(self.currBet * random.uniform(2, 3))
                return self.betOutput(2, bet)
            else:
                self.addLogging("Will smooth call")
                return self.betOutput(1, self.currBet)
        else:
            self.addLogging("No action defined!")
            self.addLogging("No action defined in Turn bet BH==1", 1)
            return self.betOutput(0, 0)

    def betBHStreet3(self):
        self.addLogging("Have BH with prob " + str(self.hand.PostFlopOdds))
        if self.TAggressor != -1:
            if self.TAggresActed == 0 and self.checkedPot == 1 and self.streetCount == 0:
                self.addLogging("Check to T raiser")
                return self.betOutput(1, self.currBet)
            elif self.TAggresActed == 0 and self.checkedPot == 0 and self.streetCount == 0:
                if random.uniform(0, 1) <= c.BH_R_RAISE:
                    self.addLogging("Will reraise due to threshold " + str(c.BH_R_RAISE))
                    bet = round(self.currBet * random.uniform(2, 3))
                    return self.betOutput(2, bet)
                else:
                    self.addLogging("Call the river bet")
                    return self.betOutput(1, self.currBet)
            elif self.streetCount == 0:
                if self.players[self.TAggressor].bHist[1] == "C":
                    self.addLogging("T raiser checked(called)")
                    if self.checkedPot == 1:
                        bet = round(self.potAmount * (random.uniform(0.5, 0.7)))
                        self.addLogging("Unopened pot so bet")
                        return self.betOutput(2, bet)
                    elif random.uniform(0, 1) <= c.BH_R_RAISE:
                        self.addLogging("Will reraise due to threshold " + str(c.BH_R_RAISE))
                        bet = round(self.currBet * random.uniform(2, 3))
                        return self.betOutput(2, bet)
                    else:
                        self.addLogging("Call the river bet")
                        return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Further round of betting, so reraise")
                bet = round(self.currBet * random.uniform(2, 3))
                return self.betOutput(2, bet)
        if self.TAggressor == -1 and self.checkedPot == 1:
            bet = round(self.potAmount * (random.uniform(0.5, 0.7)))
            self.addLogging("Open pot with a raise")
            return self.betOutput(2, bet)
        elif self.TAggressor == -1 and self.checkedPot == 0:
            if random.uniform(0, 1) <= c.BH_R_RAISE:
                self.addLogging("Will reraise due to threshold " + str(c.BH_R_RAISE))
                bet = round(self.currBet * random.uniform(2, 3))
                return self.betOutput(2, bet)
            else:
                self.addLogging("Will smooth call")
                return self.betOutput(1, self.currBet)
        else:
            self.addLogging("No action defined!")
            self.addLogging("No action defined in River bet BH==1", 1)
            return self.betOutput(0, 0)

    def betPPStreet0(self):
        # TODO: Update logic here to play sneakily if I flop a set?
        self.addLogging("Have pocket pairs")
        if self.movedPlayers == 0:
            self.addLogging("First to enter the pot")
            if self.hand.PPCard >= 9:
                self.addLogging("Strong pair so raise")
                bet = round(c.BIGBLIND * (random.uniform(2, 3)))
                return self.betOutput(2, bet)
            else:
                if random.uniform(0, 1) <= c.PF_PP_BELOW_9_RAISE:
                    bet = round(c.BIGBLIND * (random.uniform(2, 3)))
                    self.addLogging("Weak pair but raise anyway. Parameter:" + str(c.PF_PP_BELOW_9_RAISE))
                    return self.betOutput(2, bet)
                elif random.uniform(0, 1) <= c.PF_PP_BELOW_9_CALL:
                    self.addLogging("Call to draw to set")
                    return self.betOutput(1, self.currBet)
                else:
                    return self.betOutput(0, 0)
        else:
            predictedSDPot = c.PF_SMALL_PAIR * ((self.movedPlayers * c.PF_CALL_AFTER_RAISE_PERC)
                                                + (self.unmovedPlayers * c.PF_CALL_PERC))
            self.addLogging("Other players are in the pot. Prediction of pot size is:" + str(predictedSDPot))
            if c.PF_SMALL_PAIR / 10 * predictedSDPot >= self.currBet:
                self.addLogging("Call worth it")
                return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Call not worth it")
                return self.betOutput(0, 0)

    def betPremMadeHandStreet0(self):
        self.addLogging("Have a premium made hand")
        if self.checkedPot == 1:
            bet = round(self.currBet * (random.uniform(2, 3)))
            self.addLogging("Open pot with a raise")
            return self.betOutput(2, bet)
        else:
            if self.currBet <= 3 * c.BIGBLIND:
                bet = round(self.currBet * (random.uniform(2, 3)))
                self.addLogging("Will reraise as currbet:" + str(self.currBet))
                return self.betOutput(2, bet)
            else:
                if random.uniform(0, 1) <= c.PF_PREM_RERAISE_PERC:
                    self.addLogging(
                        "Currbet is large, but will reraise anyway. Parameter:" + str(c.PF_PREM_RERAISE_PERC))
                    bet = round(self.currBet * (random.uniform(2, 3)))
                    return self.betOutput(2, bet)
                else:
                    self.addLogging("Will call")
                    return self.betOutput(1, self.currBet)

    def betPremMadeHandStreet1(self):
        self.addLogging("Have a made hand")
        if self.checkedPot == 1:
            self.addLogging("Open the pot")
            bet = round(self.potAmount * random.uniform(0.5, 0.7))
            return self.betOutput(2, bet)
        else:
            self.addLogging("Call the bet")
            return self.betOutput(1, self.currBet)

    def betPremMadeHandStreet2(self):
        self.betPremMadeHandStreet1()

    def betPremMadeHandStreet3(self):
        self.betPremMadeHandStreet1()

    def betDrawStreet0(self):
        if self.hand.suitedInd == 1 and self.hand.connectedInd == 1:
            self.addLogging("Have a connected flush draw")
            predictedSDPot = c.PF_STRFL_DRAW * ((self.movedPlayers * c.PF_CALL_AFTER_RAISE_PERC
                                                 + self.unmovedPlayers * c.PF_CALL_PERC) * self.currBet + self.potAmount)
            self.addLogging("Predicted pot size / factor >= bet * high card scale?:")
            self.addLogging(str(predictedSDPot) + " / " + str(c.PF_STRFL_ODDS) + " >= " + str(self.currBet) + " * " \
                            + str(14 / self.hand.highcard) + " ?")
            if predictedSDPot / c.PF_STRFL_ODDS >= (self.currBet * 14 / self.hand.highcard):
                self.addLogging("Call worth it")
                return self.betOutput(1, self.currBet)
        self.addLogging("Have a flush or straight draw")
        if self.hand.suitedInd == 1:
            self.addLogging("Have a flush draw")
            predictedSDPot = c.PF_FL_DRAW * ((self.movedPlayers * c.PF_CALL_AFTER_RAISE_PERC
                                              + self.unmovedPlayers * c.PF_CALL_PERC) * self.currBet + self.potAmount)
            self.addLogging("Predicted pot size / factor >= bet * high card scale?:")
            self.addLogging(str(predictedSDPot) + " / " + str(c.PF_FL_ODDS) + " >= " + str(self.currBet) + " * " \
                            + str(14 / self.hand.highcard) + " ?")
            if predictedSDPot / c.PF_FL_ODDS >= (self.currBet * 14 / self.hand.highcard):
                self.addLogging("Call worth it")
                return self.betOutput(1, self.currBet)
        if self.hand.connectedInd == 1:
            self.addLogging("Have a straight draw")
            predictedSDPot = c.PF_STR_DRAW * ((self.movedPlayers * c.PF_CALL_AFTER_RAISE_PERC
                                               + self.unmovedPlayers * c.PF_CALL_PERC) * self.currBet + self.potAmount)
            self.addLogging("Predicted pot size / factor >= bet * high card scale?:")
            self.addLogging(str(predictedSDPot) + " / " + str(c.PF_STR_ODDS) + " >= " + str(self.currBet) + " * " \
                            + str(14 / self.hand.highcard) + " ?")
            if predictedSDPot / c.PF_STR_ODDS >= (self.currBet * 14 / self.hand.highcard):
                self.addLogging("Call worth it")
                return self.betOutput(1, self.currBet)

    def betDrawStreet1(self):
        self.addLogging("Have a drawing hand")
        if self.checkedPot == 1:
            self.addLogging("Checked pot")
            if self.PFAggressor == -1:
                self.addLogging("Was the PF Agressor")
                if self.shouldCBet() == 1:
                    self.CBetInd = 1
                    self.addLogging("Will CBet anyway")
                    bet = round(self.potAmount * random.uniform(0.5, 0.7))
                    return self.betOutput(2, bet)
                else:
                    self.addLogging("Will try to draw for free")
                    return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Was not the PF Agrssor")
                if self.shouldSteal() == 1:
                    self.addLogging("Try to steal flop")
                    bet = round(self.potAmount * random.uniform(0.5, 0.7))
                    return self.betOutput(2, bet)
                else:
                    self.addLogging("Will try to draw for free")
                    return self.betOutput(1, self.currBet)
        else:
            self.addLogging("Pots been opened")
            if self.shouldDraw == 1:
                self.addLogging("Try to draw")
                return self.betOutput(1, self.currBet)

    def betDrawStreet2(self):
        self.addLogging("Have a drawing hand")
        if self.checkedPot == 1:
            self.addLogging("Checked pot")
            if self.FLAggressor == -1:
                self.addLogging("Was the FL Agressor")
                if self.shouldCBet() == 1:
                    self.CBetTInd = 1
                    self.addLogging("Will CBet anyway")
                    bet = round(self.potAmount * random.uniform(0.5, 0.7))
                    return self.betOutput(2, bet)
                else:
                    self.addLogging("Will try to draw for free")
                    return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Was not the FL Agrssor")
                if self.shouldSteal() == 1:
                    self.addLogging("Try to steal turn")
                    bet = round(self.potAmount * random.uniform(0.5, 0.7))
                    return self.betOutput(2, bet)
                else:
                    self.addLogging("Will try to draw for free")
                    return self.betOutput(1, self.currBet)
        else:
            self.addLogging("Pots been opened")
            if self.shouldDraw == 1:
                self.addLogging("Try to draw")
                return self.betOutput(1, self.currBet)

    def betMiscStreet0(self):
        self.addLogging("Misc. hands")
        if self.checkedPot == 1:
            self.addLogging("No one has entered pot")
            self.addLogging("Hand Odds are:" + str(self.preFlopOdds10 / 100) + " Adjusted odds are:" \
                            + str((self.preFlopOdds10 / 100 * random.uniform(0, 1))) + " threshold is:" + str(
                c.PF_OTHER_HANDS_OPEN))
            if self.preFlopOdds10 >= 10 and (self.preFlopOdds10 / 100 * random.uniform(0, 1) <= c.PF_OTHER_HANDS_OPEN):
                bet = round(c.BIGBLIND * (random.uniform(2, 3)))
                self.addLogging("Open raise")
                return self.betOutput(2, bet)
            else:
                # If no one has opened the pot then try to steal
                self.addLogging("Steal threshold is:" + str(c.PF_STEAL))
                if self.unmovedPlayers <= 3 and (random.uniform(0, 1) <= c.PF_STEAL):
                    bet = round(c.BIGBLIND * (random.uniform(2, 3)))
                    self.addLogging("Attempt to steal")
                    return self.betOutput(2, bet)

        elif self.checkedPot == 0:
            self.addLogging("People have entered the pot")
            self.addLogging("Hand Odds are:" + str(self.preFlopOdds10) + " Adjusted odds are:" \
                            + str((self.preFlopOdds10 / 100 * random.uniform(0, 1))) + " threshold is:" + str(
                c.PF_OTHER_HANDS_CALL))
            if self.preFlopOdds10 >= 10 and (self.preFlopOdds10 / 100 * random.uniform(0, 1) <= c.PF_OTHER_HANDS_CALL):
                if self.currBet <= 3 * c.BIGBLIND:
                    return self.betOutput(1, self.currBet)

        # Else just fold
        self.addLogging("Just fold")
        return self.betOutput(0, 0)

    def betMiscStreet1(self):
        self.addLogging("Have a misc hand")
        if self.PFAggressor == -1:
            self.addLogging("Was the PF aggressor")
            if self.checkedPot == 1:
                self.addLogging("Pot has been checked")
                if self.shouldCBet() == 1:
                    self.addLogging("Will try to CBet")
                    bet = round(self.potAmount * random.uniform(0.5, 0.7))
                    return self.betOutput(2, bet)
                else:
                    self.addLogging("Won't CBet")
                    return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Pot has been opened")
                if self.shouldCall() == 1:
                    self.addLogging("Will call")
                    return self.betOutput(1, self.currBet)
                else:
                    self.addLogging("Will fold")
                    return self.betOutput(0, 0)
        else:
            self.addLogging("Was not the PF aggressor")
            if self.checkedPot == 1:
                self.addLogging("Pot has been checked")
                if self.shouldSteal() == 1:
                    self.addLogging("Will try to Steal")
                    bet = round(self.potAmount * random.uniform(0.5, 0.7))
                    return self.betOutput(2, bet)
                else:
                    self.addLogging("Won't Steal")
                    return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Pot has been opened")
                if self.shouldCall() == 1:
                    self.addLogging("Will call")
                    return self.betOutput(1, self.currBet)
                else:
                    self.addLogging("Will fold")
                    return self.betOutput(0, 0)

    def betMiscStreet2(self):
        # Not bothering with 2nd street CBetting at this point. Just consider calling/stealing
        self.addLogging("Have a misc hand")
        if self.checkedPot == 1:
            self.addLogging("Pot has been checked")
            if self.shouldSteal() == 1:
                self.addLogging("Will try to Steal")
                bet = round(self.potAmount * random.uniform(0.5, 0.7))
                return self.betOutput(2, bet)
            else:
                self.addLogging("Won't Steal")
                return self.betOutput(1, self.currBet)
        else:
            self.addLogging("Pot has been opened")
            if self.shouldCall() == 1:
                self.addLogging("Will call")
                return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Will fold")
                return self.betOutput(0, 0)

    def betMiscStreet3(self):
        # Not bothering with 3rd street CBetting at this point. Just consider calling/stealing
        self.addLogging("Have a misc hand")
        if self.checkedPot == 1:
            self.addLogging("Pot has been checked")
            if self.shouldSteal() == 1:
                self.addLogging("Will try to Steal")
                bet = round(self.potAmount * random.uniform(0.5, 0.7))
                return self.betOutput(2, bet)
            else:
                self.addLogging("Won't Steal")
                return self.betOutput(1, self.currBet)
        else:
            self.addLogging("Pot has been opened")
            if self.shouldCall() == 1:
                self.addLogging("Will call")
                return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Will fold")
                return self.betOutput(0, 0)

    def analyseBoard(self):
        """
        Sets the instances board information:
        BHInd, drawInd, drawPresent, PFAggresActed, PFAggressor
        """
        if self.streetCount == 0:
            self.setAggressorInds()

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
        for each in self.hand.cards:
            rank_list.append(int(each.rank))
            suit_list.append(each.suit)
        rank_list = list(set(rank_list))
        rank_list.sort()

        for each in self.hand.sharedCards:
            sharedrank_list.append(int(each.rank))
            sharedsuit_list.append(each.suit)
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
                    self.drawStraightOdds = 0

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
            if self.potOdds <= self.drawStraightOdds or self.potOdds <= self.drawFlushOdds:
                return 1
            else:
                return 0
        else:
            if self.potOdds <= min(self.drawStraightOdds, self.drawFlushOdds):
                return 1
            else:
                return 0

    def shouldCall(self):
        """
        Returns ind to handle making calls with middling hands. Uses potodds vs currentbet
        """
        # TODO: Improve, take into account street
        if self.potOdds <= self.currBet:
            return 1
        else:
            return 0


def PlayOddsHand(numPlayers, heroCards, flopCards):
    """
    Returns ind if the hero won the game given a heros hand and either the flop, turn or river shared cards.

    1 = win
    0.5 = draw
    0 = loss
    """
    flopcards = flopCards[0:]
    removelist = []
    for each in heroCards:
        removelist.append(each)
    for each in flopcards:
        removelist.append(each)
    try:
        removelist.remove(None)
    except:
        pass

    # Set up the Deck
    firstdeck = cardutils.Deck(removelist)
    firstdeck.shuffle()
    # Set up hero hand
    playerhands = [cardutils.Hand([heroCards[0], heroCards[1]], setCalcAllStreetValues=0)]

    while len(flopcards) < 5:
        flopcards.append(firstdeck.deck.pop())

    for i in range(1, numPlayers):
        playerhands.append(cardutils.Hand([firstdeck.deck.pop(), firstdeck.deck.pop()], setCalcAllStreetValues=0))
    # Generate the flop
    for i in range(0, numPlayers):
        playerhands[i].addSharedCards(flopcards)
    winninghand = []
    for i in range(0, numPlayers):
        winninghand.append((i, playerhands[i].postHandValue))
    winninghand.sort(key=lambda t: t[1])

    if winninghand[0][0] == 0:
        if winninghand[0][1] == winninghand[1][1]:
            return 0.5
        else:
            return 1
    else:
        return 0


def GenerateProbabilities(NumPlayers, HeroCards, FlopCards, Runs=c.ODDSRUNCOUNT):
    """
    Outputs the Monte Carlo chance of heros odds. Runs PlaysOddsHands in a loop
    """
    HeroWin = 0
    for i in range(0, Runs):
        HeroWin += PlayOddsHand(NumPlayers, HeroCards, FlopCards)
    return HeroWin * 100 / Runs
