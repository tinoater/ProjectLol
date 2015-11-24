__author__ = 'Ahab'

import operator
import itertools
import copy

import constants as c
import cardutils


class Game:
    def __init__(self, heroName, hand, players):
        """
        Class that takes a herohand and a list of players to create a game.

        Hero must be specified and the Game must be created before the heros first bet
        """
        if hand.numCards != 2:
            raise Exception ("Game can only be created before the flop")

        # Init the variables from inputs
        # TODO: Added this deepcopy in for the tests. Not sure if this makes sense at runtime
        self.players = copy.deepcopy(players)
        self.hand = copy.deepcopy(hand)
        self.initNumPlayers = len(self.players)
        self.preFlopOdds = hand.preFlopOdds
        self.preFlopOdds10 = hand.preFlopOdds10

        # Set betting vars from the pre-flop hand
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

        # Init variables
        self.postFlopOdds = None
        self.position = None
        self.PPInd = hand.PPInd
        self.bettingHist = [[], [], [], []]
        self.heroCash = 0.00
        self.street = 0
        self.streetCount = 0
        self.totalHandBet = 0
        self.potAmount = 0
        self.aggressor = [99, 99, 99, 99]
        self.aggresActed = [99, 99, 99, 99]
        self.CBetInd = 0
        self.currBet = -1
        self.heroPlayer = -1
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

        self.setHeroPlayer(heroName)

        # If BB bet is present then can set hero position
        for each in [each.bHist[0] for each in self.players]:
            try:
                if each[0] == 'BB':
                    self.setHeroPosition()
            except:
                if each == 'BB':
                    self.setHeroPosition()

    def setHeroPlayer(self, playername):
        """
        Sets the hero for the Game, as well as the heroCash
        :param playername:
        :return:
        """
        for x in range(0, self.initNumPlayers):
            if self.players[x].name == playername:
                self.heroPlayer = x

        if self.heroPlayer == -1:
            raise Exception("Hero not found")

        self.heroCash = self.players[self.heroPlayer].cash

    def setHeroPosition(self):
        """
        Sets the playing position if the position is not yet set

        This is done by finding the BB and counting back.
        SB = 1
        BB = 2
        ...
        :return:
        """
        # TODO: I am using BB here as i think this is the thing I can determine from 888. Check
        heroseat = self.players[self.heroPlayer].seat
        if self.position is None:
            for each in self.players:
                if each.bHist[0] == [cardutils.BETSTRING_DICT["BB"]]:
                    BBseat = each.seat
                    break

            seatlist = [each.seat for each in self.players]
            seatlist.sort()

            if heroseat == BBseat:
                self.position = 2
            elif heroseat > BBseat:
                self.position = len([seat for seat in seatlist if seat <= heroseat and seat >= BBseat]) + 1
            else:
                self.position = len([seat for seat in seatlist if seat >= BBseat or seat <= heroseat]) \
                                % self.initNumPlayers + 1

        # # If not found then hero is the BB
        # if self.position is None:
        #     self.position = 2

    def getUnMovedPlayers(self):
        """
        Returns the number of players left to act from the heros position
        """
        unmovedplayers = 0
        heropos = self.position
        heropos = self.players[self.heroPlayer].seat
        if self.street == 0:
            if heropos == 2:
                unmovedplayers = 0
            elif heropos == 1:
                unmovedplayers = 1
            else:
                for each in self.players:
                    if each.foldedInd == 0 and ((each.seat > heropos) or (each.seat in (1, 2))):
                        unmovedplayers += 1
        else:
            for each in self.players:
                if each.foldedInd == 0 and each.seat > heropos:
                    unmovedplayers += 1

        return unmovedplayers

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
        if tempaggres == self.heroPlayer:
            self.aggressor[self.street - 1] = -1
            self.aggresActed[self.street - 1] = 0
        else:
            self.aggressor[self.street - 1] = tempaggres
            if len(self.players[self.aggressor[self.street - 1]].bHist[1]) == 0:
                self.aggresActed[self.street - 1] = 0
            else:
                self.aggresActed[self.street - 1] = 1

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
        self.numPlayers = [x.foldedInd for x in self.players].count(0)

    def updateHeroBetting(self, action, bet=0.00):
        """
        Sets info about the hand before each bet:
        totalHandBet, bettingHist.
        """
        # TODO: Add a new hero-only betting history to also include the amount?
        self.totalHandBet += bet
        self.heroCash -= bet
        self.players[self.heroPlayer].bHist[self.street].extend(action)

    def analyseBoard(self):
        """
        Sets the instances board information:
        BHInd, drawInd, drawPresent, PFAggresActed, PFAggressor

        self.checkedPot means not raised, not self.currBet = 0
        """
        # Set number of players acted/not acted and set checkedPot indicator
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

        # SetAggressorInds, BHInd, postHandType/Value, drawInd, drawOdds, drawPresent, madeInd
        if self.street > 0:
            self.setPotOdds()
            if self.streetCount == 0:
                self.setAggressorInds()

            if self.hand.postFlopOdds >= c.BH_THRESHOLD:
                self.BHInd = 1
            else:
                self.BHInd = 0

            # TODO: Empty logic for altering BHInd for flush and straights
            if self.hand.postHandType == 5 and self.hand.highCard != 14:
                pass
            if self.hand.postHandType == 4:
                pass

            rank_list = []
            suit_list = []
            sharedrank_list = []
            sharedsuit_list = []
            for each in self.hand.cards:
                rank_list.append(each.rank)
                suit_list.append(each.suit)
            rank_list = list(set(rank_list))
            rank_list.sort()

            for each in self.hand.sharedCards:
                sharedrank_list.append(int(each.rank))
                sharedsuit_list.append(each.suit)
            sharedrank_list = list(set(sharedrank_list))
            sharedrank_list.sort()

            # TODO - This only counts when you have two cards to the flush draw
            # TODO - Consider a structure to hold all the draw variables
            if max(map(lambda x: suit_list.count(x), [1, 2, 3, 4])) == 4 and self.hand.suitedInd == 1:
                self.drawInd = 1
            else:
                self.drawInd = 0

            # TODO: This won't deal with 1 card in a straight draw
            # TODO: This will show incorrect odds for one-way straights
            if self.hand.connectedInd == 1:
                for k, g in itertools.groupby(enumerate(rank_list), lambda x: x[0] - x[1]):
                    thing = list(map(operator.itemgetter(1), g))
                    if thing.__len__() == 4:
                        self.drawInd = 1
                        self.drawStraightOdds = 2 * 8 / 100
                    else:
                        self.drawStraightOdds = 0

            if max(map(lambda x: sharedsuit_list.count(x), [1, 2, 3, 4])) >= 2:
                self.drawPresentInd = 1
                if max(map(lambda x: sharedsuit_list.count(x), [1, 2, 3, 4])) == 2:
                    self.drawFlushOdds = 2 * 12 / 100
                else:
                    self.drawFlushOdds = 1
            else:
                self.drawPresentInd = 0
                self.drawFlushOdds = 0

            # TODO: This won't deal with 1 card in a straight draw
            # TODO: This won't deal with more complicated two card draws either
            for k, g in itertools.groupby(enumerate(sharedrank_list), lambda x: x[0] - x[1]):
                thing = list(map(operator.itemgetter(1), g))
                if thing.__len__() == 3:
                    self.drawPresentInd = 1

            if self.hand.postHandType <= 8:
                self.madeInd = 1
            else:
                self.madeInd = 0



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
