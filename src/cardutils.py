__author__ = 'Ahab'

import csv
import random

import constants as c

# TODO - after tests are written refactor all the variable names
class Card:

    def __init__(self, rank, suit):
        if rank not in c.RANK_DICT:
            raise Exception("Card rank invalid")
        if suit not in c.SUIT_DICT:
            raise Exception("Card suit invalid")
        self._rank = rank
        self._suit = suit

    def __eq__(self, other):
        if other == None:
            return False
        return (self._rank == other.getRank() and self._suit == other.getSuit())

    def __str__(self):
        return c.RANK_DICT[self._rank]+ c.SUIT_DICT[self._suit]

    def getRank(self):
        return (self._rank)

    def getSuit(self):
        return (self._suit)

    def getCard(self):
        return (self.getRank(), self.getSuit())

class Hand:
    def __init__(self, *cards):
    #TODO change the *cards so its standard
        self.PreFlopOdds = None
        self.PostFlopOdds = None
        self._cards = []
        for card in cards:
            self._cards.append(card)
        self.numCards = len(self._cards)
        if self.numCards == 2:
            self.setPreHandValue()
            self.sharedCards = []
        elif self.numCards >= 5:
            self.setPostHandValue()
    #TODO update this so the sharedCards are read from the *cards input

    def __add__(self, other):
        self._cards.append(other)
        self.numCards = len(self._cards)
        if self.numCards >= 3:
            self.sharedCards.append(other)
        return True

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

    def addSharedCards(self, cards):
        for each in cards:
            self.__add__(each)
        if self.numCards >=2:
            self.setPostHandValue()

    def setPreHandValue(self):
        if self.numCards != 2:
            raise Exception("Trying to set PreHandValue with more than two cards")

        if self._cards[0].getSuit() == self._cards[1].getSuit():
            self.suitedInd = 1
        else:
            self.suitedInd = 0

        self.connectedInd = 0
        self.oneSpaceConnectedInd = 0
        self.PremInd = 0
        self.highcard = max(self._cards[0].getRank(), self._cards[1].getRank())
        self.lowcard = min(self._cards[0].getRank(), self._cards[1].getRank())

        if abs(self._cards[0].getRank() - self._cards[1].getRank()) == 1:
            self.connectedInd = 1
        elif abs(self._cards[0].getRank() - self._cards[1].getRank()) == 2:
            self.oneSpaceConnectedInd = 1
            if self._cards[0].getRank() == 14 and self._cards[1].getRank() == 2:
                self.connectedInd = 1
            elif self._cards[1].getRank() == 14 and self._cards[0].getRank() == 2:
                self.connectedInd = 1
            elif self._cards[1].getRank() == 14 and self._cards[0].getRank() == 3:
                self.oneSpaceConnectedInd = 1
            elif self._cards[0].getRank() == 14 and self._cards[1].getRank() == 3:
                self.oneSpaceConnectedInd = 1

        if self._cards[0].getRank() == self._cards[1].getRank():
            self.PPInd = 1
            self.PPCard = self._cards[0].getRank()
        else:
            self.PPInd = 0
            self.PPCard = 0

        if self.PPInd == 1 and self.PPCard in c.PREM_PAIRS:
            self.PremInd = 1
        elif self.suitedInd == 1:
            if (self._cards[0].getRank() == 14 and self._cards[1].getRank() == 13):
                self.PremInd =  1
            elif (self._cards[1].getRank() == 14 and self._cards[0].getRank() == 13):
                self.PremInd =  1
        else:
            self.PremInd = 0

        self.preFlopOdds10 = self.getPreHandOdds(10)

    def setPostHandValue(self):
        card_list = []
        rank_list = []
        suit_list = []
        self.FlushInd = 0
        self.FlushSuit = 0
        for each in self._cards:
            card_list.append([each.getRank(),each.getSuit()])
            rank_list.append(each.getRank())
            suit_list.append(each.getSuit())
        card_list = sorted(card_list, key=lambda tup: tup[0], reverse = True)

        #Check for flushInd
        self.FlushInd = 0
        self.FlushSuit = 0
        for i in c.SUIT_DICT:
            if suit_list.count(i) >= 5:
                self.FlushInd = 1
                self.FlushSuit = i
                self.HighCard = max([e1 for (e1,e2) in card_list if e2 == self.FlushSuit])

        #Check for straightInd
        straight_list = sorted(list(set(rank_list)), reverse = True)
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
            straight_list = sorted([1 if x==14 else x for x in straight_list], reverse = True)
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
        for i in c.RANK_DICT:
            if rank_list.count(i) == 4:
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
        for i in sorted(list(c.RANK_DICT), reverse = True):
            if rank_list.count(i) == 3:
                self.TripInd = 1
                self.TripRank = i
                #Check for full house
                fh_list = [x for x in rank_list if x != i]
                for j in sorted(list(c.RANK_DICT), reverse = True):
                    if fh_list.count(j) == 2:
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
        for i in sorted(list(c.RANK_DICT), reverse = True):
            if rank_list.count(i) == 2:
                self.Pair1Rank = i
                #Check for second pair house
                p2_list = [x for x in rank_list if x != i]
                for j in range(max(c.RANK_DICT),min(c.RANK_DICT),-1):
                    if p2_list.count(j) == 2:
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
        #TODO move to a new variable called FlushHighCard?
        self.HighCard = 0
        for i in sorted(list(c.RANK_DICT), reverse = True):
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
            cardList.append(each)
        return cardList

    def getPreHandSimple(self):
        if self.PPInd == 1:
            suited_ind = ''
        elif self.suitedInd == 1:
            suited_ind = 's'
        else:
            suited_ind = 'o'

        return c.RANK_DICT[max(self._cards[0].getRank(),self._cards[1].getRank())] \
               + c.RANK_DICT[min(self._cards[0].getRank(),self._cards[1].getRank())]+suited_ind

    def setPreHandOdds(self,players):
        """
        Sets the instance Hands PreFlopOdds from a csv file
        :param players:
        :return:
        """
        targethand = self.getPreHandSimple()

        pf_file = open(c.MEDIA_DIR + c.PF_ODDS_FILENAME,"r")
        pf_reader = csv.reader(pf_file)

        for row in pf_reader:
            if row[0] == targethand:
                odds = float(row[int(players) - 1])

        pf_file.close()
        if odds == None:
            raise Exception("Failed to get pre flop odds")
        self.PreFlopOdds = odds

    def getPreHandOdds(self,players):
        """
        Returns the PreFlop odds of the instance Hand. If None then will set them first.
        :param players:
        :return: PreFlop odds
        """
        if self.PreFlopOdds is None:
            self.setPreHandOdds(players)
        return self.PreFlopOdds

    def getPostCurrentHandString(self):
        HandOutput = c.HAND_DICT[self.PostHandType]
        if self.PostHandType == 2:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.HighCard] + " high"
        elif self.PostHandType == 3:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.QuadRank] + "s"
        elif self.PostHandType == 4:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.TripRank] + "s over " + c.RANK_DICT[self.Pair1Rank]
        elif self.PostHandType == 5:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.HighCard]
        elif self.PostHandType == 6:
            HandOutput = HandOutput + " High card " + c.RANK_DICT[self.StraightHead]
        elif self.PostHandType == 7:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.TripRank] + "s"
        elif self.PostHandType == 8:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.Pair1Rank] + "s and " + c.RANK_DICT[self.Pair2Rank] + "s"
        elif self.PostHandType == 9:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.Pair1Rank] + "s"
        elif self.PostHandType == 10:
            HandOutput = HandOutput + " " + c.RANK_DICT[self.HighCard]
        return HandOutput

class Deck:
    def __init__(self):
        self._Deck = []
        for rank in c.RANK_DICT:
            for suit in c.SUIT_DICT:
                c = Card(rank,suit)
                self._Deck.append(c)

    def shuffle(self):
        random.shuffle(self._Deck)

class Player:
    def __init__(self,seat,name,cash,stats):
        self.seat = int(seat)
        self.name = name
        self.cash = int(cash)
        self.stats = stats
        self.bHist = [[],[],[],[]]
        self.FoldedInd = 0

    def updatePlayerbHist(self,street,betstring):
        """
        Updates the Player instances betting history and FoldedInd
        :param street:
        :param betstring:
        :return:
        """

        #TODO: If i don't destroy the players I can keep a global betting move count
        self.bHist[street].append(betstring)
        if betstring == c.BETSTRING_FOLD:
            self.FoldedInd = 1

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

