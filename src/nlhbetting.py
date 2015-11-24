__author__ = 'Ahab'

import random
import copy
import constants as c
import cardutils

#TODO: Can incorporate an aggro parameter - have it as an input?
class BettingStrat:
    def __init__(self, **kwargs):
        """
        Creates a betting strategy for a passed in Game or an empty strategy

        :param kwargs: gameInstance - Game object
        :return:
        """
        gameinstance = kwargs.get("gameInstance")
        if gameinstance is not None:
            # Game information
            self.players = copy.deepcopy(gameinstance.players)
            self.street = gameinstance.street
            self.streetCount = gameinstance.streetCount
            self.wait = gameinstance.wait
            self.currBet = gameinstance.currBet
            self.heroCash = gameinstance.heroCash
            self.potAmount = gameinstance.potAmount
            self.aggressor = copy.deepcopy(gameinstance.aggressor)
            self.aggresActed = copy.deepcopy(gameinstance.aggresActed)
            self.CBetInd = gameinstance.CBetInd
            self.CBetTInd = gameinstance.CBetTInd

            self.checkedPot = gameinstance.checkedPot
            self.movedPlayers = gameinstance.movedPlayers
            self.unmovedPlayers = gameinstance.unmovedPlayers

            # Debug information
            self.errorstr = gameinstance.errorstr
            self.logstr = gameinstance.logstr

            # Hand information
            self.hand = copy.deepcopy(gameinstance.hand)
            self.BHInd = gameinstance.BHInd
            self.madeInd = gameinstance.madeInd
            self.PPInd = gameinstance.PPInd
            self.drawInd = gameinstance.drawInd
            self.drawFlushOdds = gameinstance.drawFlushOdds
            self.drawStraightOdds = gameinstance.drawStraightOdds
            self.potOdds = gameinstance.potOdds
            self.preFlopOdds10 = gameinstance.preFlopOdds10
            self.postFlopOdds = gameinstance.postFlopOdds
        else:
            self.players = None
            self.street = None
            self.streetCount = None
            self.wait = None
            self.currBet = None
            self.heroCash = None
            self.potAmount = None
            self.aggressor = [99, 99, 99, 99]
            self.aggresActed = [99, 99, 99, 99]
            self.CBetInd = None
            self.CBetTInd = None

            self.checkedPot = None
            self.movedPlayers = None
            self.unmovedPlayers = None

            # Debug information
            self.errorstr = ""
            self.logstr = ""

            # Hand information
            self.hand = None
            self.BHInd = None
            self.madeInd = None
            self.PPInd = None
            self.drawInd = None
            self.drawFlushOdds = None
            self.drawStraightOdds = None
            self.potOdds = None
            self.preFlopOdds10 = None
            self.postFlopOdds = None

        self.aggressorAction = ""

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
        if self.potOdds <= max(self.drawStraightOdds, self.drawFlushOdds):
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

    def betOutput(self, action, bet=0.00):
        """
        Returns the betting action variables after they have been calculated:
        bettingaction, betamount, wait
        """
        if action == 0:
            self.addLogging("Folding")
            return 0, 0
        elif action == 3:
            self.addLogging("Going all-in")
            return 3, 0
        elif action == 1:
            bet = self.currBet

        if self.heroCash <= bet:
            self.addLogging("Not enough cash so going all-in")
            return 3, 0
        elif self.heroCash - bet <= bet * c.RAISE_TO_ALLIN_THRESH:
            self.addLogging("Rounding up to all in")
            return 3, 0
        else:
            self.addLogging("Bet is " + str(bet))
            return action, bet

    def bet(self):
        """
        Master betting function that calls the other betting functions
        :return:
        """
        # TODO - Incorporate position into betting strat
        # TODO: Add some generic call logic function for premMadeHands
        # TODO: Add logic to steal a boring looking flop for Misc hands
        # TODO: Remember tht analyseBoard needs to have been run in the Game class to set the correct vars
        self.errorstr = ""
        self.logstr = ""
        self.aggressorAction = ""
        self.addLogging("Pot amount is " + str(self.potAmount) + " Call bet amount is " + str(self.currBet))

        if self.street == 0:
            return self.betPreFlop()
        elif self.street == 1:
            try:
                self.aggressorAction = self.players[self.aggressor[self.street - 1]].bHist[1][0]
            except:
                self.aggressorAction = ""
            return self.betFlop()
        elif self.street == 2:
            try:
                self.aggressorAction = self.players[self.aggressor[self.street - 1]].bHist[2][0]
            except:
                self.aggressorAction = ""
            return self.betTurn()
        elif self.street == 3:
            try:
                self.aggressorAction = self.players[self.aggressor[self.street - 1]].bHist[3][0]
            except:
                self.aggressorAction = ""
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
        # set wait to zero as getting pot odds takes so long
        self.wait = 0

        # If BH then we want to push for max value
        if self.BHInd == 1:
            return self.betBHStreet1()
        # Try CBet, else check/call
        elif self.drawInd == 1:
            return self.betDrawStreet1()
        elif self.madeInd == 1:
            return self.betPremMadeHandStreet1()
        else:
            return self.betMiscStreet1()

    def betTurn(self):
        """
        Returns the betting action to be made on the Turn
        """
        # set wait to zero as getting pot odds takes so long
        self.wait = 0

        # If BH then we want to push for max value
        if self.BHInd == 1:
            return self.betBHStreet2()
        # Try CBet, else check/call
        elif self.drawInd == 1:
            return self.betDrawStreet2()
        elif self.madeInd == 1:
            return self.betPremMadeHandStreet2()
        else:
            return self.betMiscStreet2()

    def betRiver(self):
        """
        Returns the betting action to be made on the River
        """
        # set wait to zero as getting pot odds takes so long
        self.wait = 0

        # If BH then we want to push for max value
        if self.BHInd == 1:
            return self.betBHStreet3()
        elif self.madeInd == 1:
            return self.betPremMadeHandStreet3()
        else:
            return self.betMiscStreet3()

    def betBHStreet0(self):
        bet = round(self.currBet * (random.uniform(2, 3)))
        self.addLogging("Herocash:" + str(self.heroCash) + " Calculated raise:" + str(bet))
        return self.betOutput(2, bet)

    def betBHStreet1(self):
        self.addLogging("Have BH with prob " + str(self.postFlopOdds))
        if self.aggressor[self.street - 1] != -1:
            if self.aggresActed[self.street - 1] == 0:
                if self.checkedPot == 1 and self.streetCount == 0:
                    self.addLogging("Check to raiser")
                    return self.betOutput(1, self.currBet)
                elif self.checkedPot == 0 and self.streetCount == 0:
                    if random.uniform(0, 1) <= c.BH_RERAISE[self.street - 1]:
                        self.addLogging("Will reraise due to threshold" + str(c.BH_RERAISE[self.street - 1]))
                        bet = round(self.currBet * random.uniform(2, 3))
                        return self.betOutput(2, bet)
                    else:
                        self.addLogging("Call the bet")
                        return self.betOutput(1, self.currBet)
            elif self.streetCount == 0:
                if self.aggressorAction == cardutils.BETSTRING_DICT['CALL']:
                    if self.checkedPot == 1:
                        self.addLogging("Raiser checked")
                        bet = round(self.potAmount * (random.uniform(0.5, 0.7)))
                        self.addLogging("Unopened pot so bet")
                        return self.betOutput(2, bet)
                    elif random.uniform(0, 1) <= c.BH_RERAISE[self.street - 1]:
                        self.addLogging("Raiser called")
                        self.addLogging("Will reraise due to threshold " + str(c.BH_RERAISE[self.street - 1]))
                        bet = round(self.currBet * random.uniform(2, 3))
                        return self.betOutput(2, bet)
                    else:
                        self.addLogging("Raiser called")
                        self.addLogging("Call the flop bet")
                        return self.betOutput(1, self.currBet)
                elif self.aggressorAction == cardutils.BETSTRING_DICT['FOLD']:
                    self.addLogging("Raised folded")
                    if self.checkedPot == 1:
                        bet = round(self.potAmount * (random.uniform(0.5, 0.7)))
                        self.addLogging("Unopened pot so bet")
                        return self.betOutput(2, bet)
                    elif random.uniform(0, 1) <= c.BH_RERAISE[self.street - 1]:
                        self.addLogging("Will reraise due to threshold " + str(c.BH_RERAISE[self.street - 1]))
                        bet = round(self.currBet * random.uniform(2, 3))
                        return self.betOutput(2, bet)
                    else:
                        self.addLogging("Call the bet")
                        return self.betOutput(1, self.currBet)
                elif self.aggressorAction in (cardutils.BETSTRING_DICT['RAISE'], cardutils.BETSTRING_DICT['ALLIN']):
                    self.addLogging("Raiser raised")
                    if random.uniform(0, 1) <= c.BH_RERAISE[self.street - 1]:
                        self.addLogging("Will reraise due to threshold " + str(c.BH_RERAISE[self.street - 1]))
                        bet = round(self.currBet * random.uniform(2, 3))
                        return self.betOutput(2, bet)
                    else:
                        return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Further round of betting, so reraise")
                bet = round(self.currBet * random.uniform(2, 3))
                return self.betOutput(2, bet)
        elif self.aggressor[self.street - 1] == -1 and self.checkedPot == 1:
            bet = round(self.potAmount * (random.uniform(0.5, 0.7)))
            self.addLogging("Open pot with a raise")
            return self.betOutput(2, bet)
        elif self.aggressor[self.street - 1] == -1 and self.checkedPot == 0:
            if random.uniform(0, 1) <= c.BH_RERAISE[self.street - 1]:
                self.addLogging("Will reraise due to threshold " + str(c.BH_RERAISE[self.street - 1]))
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
        self.betBHStreet1()

    def betBHStreet3(self):
        self.betBHStreet1()

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
            predictedSDPot = ((self.movedPlayers * c.PF_CALL_AFTER_RAISE_PERC)
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
            self.addLogging("Is predicted pot size / factor >= bet * high card scale?:")
            self.addLogging(str(predictedSDPot) + " / " + str(c.PF_STRFL_ODDS) + " >= " + str(self.currBet) + " * " \
                            + str(14 / self.hand.highcard) + " ?")
            if predictedSDPot / c.PF_STRFL_ODDS >= (self.currBet * 14 / self.hand.highcard):
                self.addLogging("Call worth it")
                return self.betOutput(1, self.currBet)
            else:
                self.addLogging("Call not worth it")
                return self.betOutput(0, 0)
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
            else:
                self.addLogging("Call not worth it")
                return self.betOutput(0, 0)
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
            else:
                self.addLogging("Call not worth it")
                return self.betOutput(0, 0)

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
            else:
                self.addLogging("Draw too costly, fold")
                return self.betOutput(0, 0)

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