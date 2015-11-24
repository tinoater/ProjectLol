__author__ = 'Ahab'

import csv
import random

import constants as c

RANK_DICT = {2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'T', 11: 'J', 12: 'Q', 13: 'K',
             14: 'A'}
SUIT_DICT = {1: 'H', 2: 'D', 3: 'S', 4: 'C'}
BETSTRING_DICT = {'FOLD': 'X', 'RAISE': 'R', 'ALLIN': 'A', 'CALL': 'C', 'SB': 'SB', 'BB': 'BB'}
PREM_PAIRS = [14, 13, 12]
HAND_DICT = {1: 'Royal Flush', 2: 'Straight Flush', 3: 'Four of a Kind', 4: 'Full House', 5: 'Flush', 6: 'Straight',
             7: 'Three of a Kind', 8: 'Two Pairs', 9: 'One Pair', 10: 'High Card'}


class Card:
    """
    Creates a card object with properties of rank and suit
    """

    def __init__(self, rank, suit):
        if rank not in RANK_DICT:
            raise Exception("Card rank invalid")
        if suit not in SUIT_DICT:
            raise Exception("Card suit invalid")
        self.rank = rank
        self.suit = suit

    def __eq__(self, other):
        if other is None:
            return False
        if type(other) != Card:
            return False
        return self.rank == other.rank and self.suit == other.suit

    def __str__(self):
        return RANK_DICT[self.rank] + SUIT_DICT[self.suit]

    def getCard(self):
        return self.rank, self.suit


class Deck:
    def __init__(self, cardlist=None):
        """
        Creates a deck of cards with an optional list parameter of cards to be excluded

        Pass in a list of cards that should not appear in the deck (i.e already dealt out)
        :return:
        """
        if cardlist is None:
            cardlist = []
        self.deck = []
        tuplelist = []
        for each in cardlist:
            if each is not None:
                tuplelist.append((each.rank, each.suit))
        for rank in RANK_DICT:
            for suit in SUIT_DICT:
                if (rank, suit) not in tuplelist:
                    card = Card(rank, suit)
                    self.deck.append(card)

    def shuffle(self):
        random.shuffle(self.deck)


class Stats:
    def __init__(self, hands=0, VPIP=0, PFR=0, Call=0, CBet=0, CBet_F=0, CBet_C=0, CBet_R=0, CBet_T=0, **kwargs):
        if kwargs.get('empty',False):
            self.statsPresent = False
        else:
            self.statsPresent = True

        self.numhands = hands
        self.VPIP = VPIP
        self.PFR = PFR
        self.Call = Call
        self.CBet = CBet
        self.CBet_F = CBet_F
        self.CBet_C = CBet_C
        self.CBet_R = CBet_R
        self.CBet_T = CBet_T

class Player:
    """
    Creates an object to hold information for seat, name, cash, stats

    :type seat:int
    :type name:str
    :type cash:int
    :type stats:Stats

    """

    def __init__(self, seat, name, cash, stats = Stats(empty=True)):
        if type(seat) != int:
            raise Exception("Seat type invalid")
        if type(name) != str:
            raise Exception("Name type invalid")
        if type(cash) != int:
            raise Exception("Cash type invalid")
        if stats is not None:
            if type(stats) != Stats:
                raise Exception("Stats type invalid")
        else:
            stats = Stats(0,0,0,0,0,0,0,0,0)
        self.seat = seat
        self.name = name
        self.cash = cash
        self.stats = stats
        self.bHist = [[], [], [], []]
        self.foldedInd = 0
        self.cashWon = 0
        self.cashWonAgainstHero = 0
        self.handsPlayed = 0

    def updatePlayerbHist(self, street, betstring):
        """
        Updates the Player instances betting history and FoldedInd
        :param street:
        :param betstring:
        :return:
        """
        # TODO: If i don't destroy the players I can keep a global betting move count
        if betstring not in BETSTRING_DICT.values():
            raise Exception("Betstring invalid")
        self.bHist[street].append(betstring)
        if betstring == BETSTRING_DICT['FOLD']:
            self.foldedInd = 1

    def resetPlayer(self, cashWon=0.00, cashWonAgainstHero=0.00):
        """
        Resets the variables for the player at the end of a hand
        :return:
        """
        self.handsPlayed += 1
        self.cashWon += cashWon
        self.cashWonAgainstHero += cashWonAgainstHero
        self.foldedInd = 0

    def debugPlayerInfo(self):
        string = self.name
        string += " in seat " + str(self.seat)
        string += " with cash " + str(self.cash)
        string += " with betting history:" + str(self.bHist)
        string += " cash won: " + str(self.cashWon)
        string += " cash won against hero: " + str(self.cashWonAgainstHero)

        return string


class Hand:
    def __init__(self, cardList, **kwargs):
        """
        Class to hold a list of cards. The private cards are the first two
        :param cardList: List of cards in the hand
        :param kwargs:
        :return:
        """
        self.calcAllStreetValues = kwargs.get('setCalcAllStreetValues', 1)
        self.suitedInd = 0
        self.connectedInd = 0
        self.oneSpaceConnectedInd = 0
        self.premInd = 0
        self.highCard = 0
        self.lowCard = 0
        self.PPInd = 0
        self.PPCard = 0
        self.premInd = 0
        self.preFlopOdds10 = 0
        self.flushInd = 0
        self.flushSuit = 0
        self.highCard = 0
        self.flushHighCard = 0
        self.straightInd = 0
        self.straightHead = 0
        self.quadInd = 0
        self.quadRank = 0
        self.tripInd = 0
        self.tripRank = 0
        self.FHInd = 0
        self.pair1Rank = 0
        self.pair2Rank = 0
        self.postHandType = 0
        self.postHandValue = 0
        self.preFlopOdds = None
        self.postFlopOdds = None
        self.cards = []
        self.sharedCards = []
        for card in cardList:
            self.__add__(card)
        if self.numCards == 2:
            if self.calcAllStreetValues == 1:
                self.setPreHandValue()
        elif (self.numCards >= 5 and self.calcAllStreetValues == 1) or \
                (self.calcAllStreetValues == 0 and self.numCards == 7):
            self.setPostHandValue()

    def __add__(self, other):
        if type(other) != Card:
            raise Exception("Can only add Cards to a Hand")
        self.cards.append(other)
        self.numCards = len(self.cards)
        if self.numCards >= 3:
            self.sharedCards.append(other)

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __str__(self):
        string = ""
        for each in self.cards:
            string = string + str(each) + " "
        return string

    def addSharedCards(self, cards):
        """
        Add shared cards to the hand
        :param cards:
        :type cards: list of Cards
        :return:
        """
        if self.numCards < 2:
            raise Exception("Cannot add shared cards without hole cards")
        for each in cards:
            self.__add__(each)
        if self.numCards >= 2:
            if self.calcAllStreetValues == 1 or (self.calcAllStreetValues == 0 and self.numCards == 7):
                self.setPostHandValue()

    def setPreHandValue(self):
        if self.numCards != 2:
            raise Exception("Trying to set PreHandValue with more than two cards")

        if self.cards[0].suit == self.cards[1].suit:
            self.suitedInd = 1
        else:
            self.suitedInd = 0

        self.connectedInd = 0
        self.oneSpaceConnectedInd = 0
        self.premInd = 0
        self.highCard = max(self.cards[0].rank, self.cards[1].rank)
        self.lowCard = min(self.cards[0].rank, self.cards[1].rank)

        if abs(self.cards[0].rank - self.cards[1].rank) == 1:
            self.connectedInd = 1
        elif abs(self.cards[0].rank - self.cards[1].rank) == 2:
            self.oneSpaceConnectedInd = 1
            if self.cards[0].rank == 14 and self.cards[1].rank == 2:
                self.connectedInd = 1
            elif self.cards[1].rank == 14 and self.cards[0].rank == 2:
                self.connectedInd = 1
            elif self.cards[1].rank == 14 and self.cards[0].rank == 3:
                self.oneSpaceConnectedInd = 1
            elif self.cards[0].rank == 14 and self.cards[1].rank == 3:
                self.oneSpaceConnectedInd = 1

        if self.cards[0].rank == self.cards[1].rank:
            self.PPInd = 1
            self.PPCard = self.cards[0].rank
        else:
            self.PPInd = 0
            self.PPCard = 0

        if self.PPInd == 1 and self.PPCard in PREM_PAIRS:
            self.premInd = 1
        elif self.suitedInd == 1:
            if self.cards[0].rank == 14 and self.cards[1].rank == 13:
                self.premInd = 1
            elif self.cards[1].rank == 14 and self.cards[0].rank == 13:
                self.premInd = 1
        else:
            self.premInd = 0

        self.preFlopOdds10 = self.setPreHandOdds(10)

    def setPostHandValue(self):
        card_list = []
        rank_list = []
        suit_list = []
        for each in self.cards:
            card_list.append([each.rank, each.suit])
            rank_list.append(each.rank)
            suit_list.append(each.suit)
        card_list = sorted(card_list, key=lambda tup: tup[0], reverse=True)

        # Check for flushInd
        self.flushInd = 0
        self.flushSuit = 0
        self.flushHighCard = 0
        for i in SUIT_DICT:
            if suit_list.count(i) >= 5:
                self.flushInd = 1
                self.flushSuit = i
                self.flushHighCard = max([e1 for (e1, e2) in card_list if e2 == self.flushSuit])

        # Check for straightInd
        straight_list = sorted(list(set(rank_list)), reverse=True)
        i = 0
        self.straightInd = 0
        self.straightHead = 0
        while i + 5 <= straight_list.__len__():
            if straight_list[i] - straight_list[i + 4] == 4:
                self.straightInd = 1
                self.straightHead = straight_list[i]
            i += 1

        if self.straightInd == 0:
            # Check for low card ace straight
            straight_list = sorted([1 if x == 14 else x for x in straight_list], reverse=True)
            i = 0
            while i + 5 <= straight_list.__len__():
                if straight_list[i] - straight_list[i + 4] == 4:
                    self.straightInd = 1
                    self.straightHead = straight_list[i]
                i += 1

        if self.flushInd == 1 and self.straightInd == 1 and self.straightHead == 14:
            self.postHandType = 1
            self.postHandValue = 1
            return
        elif self.flushInd == 1 and self.straightInd == 1:
            self.postHandType = 2
            self.postHandValue = 2 - self.straightHead + 13  # 10
            return

        # Check for 4 of a kind
        self.quadInd = 0
        self.quadRank = 0
        for i in RANK_DICT:
            if rank_list.count(i) == 4:
                self.quadInd = 1
                self.quadRank = i
                self.postHandType = 3
                self.postHandValue = 11 - self.quadRank + 14  # 23
                return

        # Check for 3 of a kind
        self.tripInd = 0
        self.tripRank = 0
        self.FHInd = 0
        self.pair1Rank = 0
        for i in sorted(list(RANK_DICT), reverse=True):
            if rank_list.count(i) == 3:
                self.tripInd = 1
                self.tripRank = i
                # Check for full house
                fh_list = [x for x in rank_list if x != i]
                for j in sorted(list(RANK_DICT), reverse=True):
                    if fh_list.count(j) == 2:
                        self.FHInd = 1
                        self.tripInd = 0
                        self.pair1Rank = j
                if self.pair1Rank != 0:
                    break
            if self.pair1Rank != 0:
                break

        if self.FHInd == 1:
            self.postHandType = 4
            self.postHandValue = 24 - (self.tripRank - 1) * 12 - (self.pair1Rank - 1) + 168  # 178
            return
        elif self.flushInd == 1:
            self.postHandType = 5
            self.postHandValue = 179 - self.highCard + 14  # 186
            return
        elif self.straightInd == 1:
            self.postHandType = 6
            self.postHandValue = 187 - self.straightHead + 14  # 196
            return
        elif self.tripInd == 1:
            self.postHandType = 7
            self.postHandValue = 197 - self.tripRank + 14  # 209
            return

        # Check for pairs
        self.pair1Rank = 0
        self.pair2Rank = 0
        for i in sorted(list(RANK_DICT), reverse=True):
            if rank_list.count(i) == 2:
                self.pair1Rank = i
                # Check for second pair house
                p2_list = [x for x in rank_list if x != i]
                for j in range(max(RANK_DICT), min(RANK_DICT), -1):
                    if p2_list.count(j) == 2:
                        self.pair2Rank = j
                    if self.pair2Rank != 0:
                        break
            if self.pair2Rank != 0:
                break

        if self.pair1Rank != 0 and self.pair2Rank != 0:
            self.postHandType = 8
            self.postHandValue = 210 - (self.pair1Rank - 1) - (self.pair2Rank - 1) + 25  # 232
            return
        elif self.pair1Rank != 0:
            self.postHandType = 9
            self.postHandValue = 233 - self.pair1Rank + 14  # 245
            return
        self.highCard = 0
        for i in sorted(list(RANK_DICT), reverse=True):
            count = rank_list.count(i)
            if count >= 1:
                self.highCard = i
            if self.highCard != 0:
                break
        self.postHandType = 10
        self.postHandValue = 247 - self.highCard + 14  # 254
        return

    def getPreHandSimple(self):
        """
        Returns the pre-flop hand expression
        :return:
        """
        if self.PPInd == 1:
            suited_ind = ''
        elif self.suitedInd == 1:
            suited_ind = 's'
        else:
            suited_ind = 'o'

        return RANK_DICT[max(self.cards[0].rank, self.cards[1].rank)] \
               + RANK_DICT[min(self.cards[0].rank, self.cards[1].rank)] + suited_ind

    def setPreHandOdds(self, players):
        """
        Sets the instance Hands PreFlopOdds from a csv file
        :param players:
        :return:
        """
        targethand = self.getPreHandSimple()
        odds = None

        pf_file = open(c.MEDIA_DIR + c.PF_ODDS_FILENAME, "r")
        pf_reader = csv.reader(pf_file)

        for row in pf_reader:
            if row[0] == targethand:
                odds = float(row[int(players) - 1])
                break

        pf_file.close()
        if odds is None:
            raise Exception("Failed to get pre flop odds")
        self.preFlopOdds = odds

        return self.preFlopOdds

    def getPostCurrentHandString(self):
        handoutput = HAND_DICT[self.postHandType]
        if self.postHandType == 2:
            handoutput = handoutput + " " + RANK_DICT[self.highCard] + " high"
        elif self.postHandType == 3:
            handoutput = handoutput + " " + RANK_DICT[self.quadRank] + "s"
        elif self.postHandType == 4:
            handoutput = handoutput + " " + RANK_DICT[self.tripRank] + "s over " + RANK_DICT[self.pair1Rank]
        elif self.postHandType == 5:
            handoutput = handoutput + " " + RANK_DICT[self.highCard]
        elif self.postHandType == 6:
            handoutput = handoutput + " High card " + RANK_DICT[self.straightHead]
        elif self.postHandType == 7:
            handoutput = handoutput + " " + RANK_DICT[self.tripRank] + "s"
        elif self.postHandType == 8:
            handoutput = handoutput + " " + RANK_DICT[self.pair1Rank] + "s and " + RANK_DICT[self.pair2Rank] + "s"
        elif self.postHandType == 9:
            handoutput = handoutput + " " + RANK_DICT[self.pair1Rank] + "s"
        elif self.postHandType == 10:
            handoutput = handoutput + " " + RANK_DICT[self.highCard]
        return handoutput
