__author__ = 'Ahab'

import math
import csv
import sys
import random
import psycopg2

PF_ODDS_FILENAME = 'PreFlop.csv'
RANK_DICT = {2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'T',11:'J',12:'Q',13:'K',14:'A'}
SUIT_DICT = {'1':'H','2':'D','3':'S','4':'C'}
PREM_PARIS = [14,13,12]
HAND_DICT = {1:'Royal Flush', 2:'Straight Flush', 3:'Four of a Kind', 4:'Full House', 5:'Flush', 6:'Straight'
             ,7:'Three of a Kind',8:'Two Pairs',9:'One Pair',10:'High Card'}
QUERY_DICT={'Name':0, 'NumHands':1, 'VPIP_Perc':2, 'PFR_Perc':3, 'Call_Perc':4, 'CBet_Perc':5, 'CBet_Fold_Perc':6
          , 'CBet_Call_Perc':7, 'CBet_Raise_Perc':8, 'CBet_Turn_Perc':9}

class Card:
    #Rank = (0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14)
    #Suit = ('O', 'S', 'H', 'C', 'D')

    def __init__(self, rank, suit):
        self._rank = rank
        self._suit = suit

    def __eq__(self, other):
        return (self._rank == other.getRank() and self._suit == other.getSuit())

    def __str__(self):
        return RANK_DICT[self._rank]+ SUIT_DICT[self._suit]

    def getRank(self):
        return (self._rank)

    def getSuit(self):
        return (self._suit)

    def getCard(self):
        return (self.getRank(), self.getSuit())

class Hand:
    def __init__(self, *cards):
        for card in cards:
            self._cards = card

    def __add__(self, other):
        return(Hand(self, other))

    def __radd__(self, other):
        if other == 0:
            return self
        else:
            return self.__add__(other)

    def __str__(self):
        output = ""
        for each in self._cards:
            (rank, suit) = each.getCard()
            output = output + RANK_DICT[rank] + str(suit).lower() + ", "
        return output[:-2]

    def getCards(self):
        cardList = []
        for each in self._cards:
            cardList = cardList + [each]
        return(cardList)

    def getNumCards(self):
        return (len(self._cards))

    #def printHand(self):
    #    output = ""
    #    for each in self._cards:
    #        (rank, suit) = each.getCard()
    #       output = output + RANK_DICT[rank] + (str(suit)).lower() + ", "
    #   print(output[:-2])

    def getSuitedInd(self):
        card_list = []
        for each in self._cards:
            card_list = card_list + [each.getRank()]
            card_list = card_list + [each.getSuit()]

        if card_list[1] == card_list[3]:
            return 1
        else:
            return 0

    def getConnectedInd(self,space):
        card_list = []
        for each in self._cards:
            card_list = card_list + [each.getRank()]
            card_list = card_list + [each.getSuit()]

        if abs(int(card_list[0]) - int(card_list[2])) == space + 1:
            return 1
        else:
            if space == 0:
                if int(card_list[0]) == 14 and int(card_list[2]) == 2:
                    return 1
                elif int(card_list[2]) == 14 and int(card_list[0]) == 2:
                    return 1
                else:
                    return 0
            else:
                return 0

    def getPPInd(self):
        card_list = []
        for each in self._cards:
            card_list = card_list + [each.getRank()]
            card_list = card_list + [each.getSuit()]

        if card_list[0] == card_list[2]:
            return 1
        else:
            return 0

    def getPremInd(self):
        card_list = []
        for each in self._cards:
            card_list = card_list + [each.getRank()]
            card_list = card_list + [each.getSuit()]

        if card_list[0] == card_list[2]:
            if card_list[0] in PREM_PARIS:
                return 1
        elif self.getSuitedInd() == 1:
            if (card_list[0] == '14' and card_list[1] == '13'):
                return 1
            elif (card_list[1] == '14' and card_list[0] == '13'):
                return 1
            else:
                return 0

    def getPreHandSimple(self):
        #work out if on suit or not
        card_list = []
        for each in self._cards:
            card_list = card_list + [each.getRank()]
            card_list = card_list + [each.getSuit()]
        if card_list[0] == card_list[2]:
            suited_ind = ''
        elif card_list[1] == card_list[3]:
            suited_ind = 's'
        else:
            suited_ind = 'o'
        #take the numbers

        card_list.__delitem__(1)
        card_list.__delitem__(2)
        #sort desc.
        card_list.sort(reverse=True)

        return RANK_DICT[card_list[0]]+RANK_DICT[card_list[1]]+suited_ind

    def getPreHandOdds(self,players):
        target_players = players
        odds = 0
        if len(self._cards) != 2:
            return False

        targethand = self.getPreHandSimple()

        pf_file = open(PF_ODDS_FILENAME,"r")
        pf_reader = csv.reader(pf_file)

        for row in pf_reader:
            if row[0] == targethand:
                odds = float(row[int(target_players) - 1])

        pf_file.close()

        return odds

    def getPreHandValue(self,players):
        if len(self._cards) != 2:
            return False

        ##SuitedInd, ConnectedInd, 1-space ConnectedInd, PocketPairInd, PremiumInd (AA,KK,QQ,AKs)
        pre_hand_value = {'SuitedInd': 0
                       , 'ConnectedInd': 0
                       , '1SpaceConnectedInd': 0
                       , 'PPInd': 0
                       , 'PremInd': 0
                       , 'Odds': 0}
        #this should probably be abstracted to a function
        pre_hand_value['SuitedInd'] = self.getSuitedInd()
        pre_hand_value['ConnectedInd'] = self.getConnectedInd(0)
        pre_hand_value['1SpaceConnectedInd'] = self.getConnectedInd(1)
        pre_hand_value['PPInd'] = self.getPPInd()
        pre_hand_value['PremInd'] = self.getPremInd()
        pre_hand_value['Odds'] = self.getPreHandOdds(players)

        return pre_hand_value

    def getPostCurrentHandValue(self):
        card_list = []
        rank_list = []
        suit_list = []
        FlushInd = 0
        FlushSuit = '0'
        for each in self._cards:
            card_list.append([[each.getRank()],[each.getSuit()]])
            rank_list.append(int(each.getRank()))
            suit_list.append(each.getSuit())
        card_list = sorted(card_list, key=lambda tup: tup[0], reverse = True)

        #Check for flushInd
        FlushInd = 0
        FlushSuit = 0
        for i in range(1,5):
            count = suit_list.count(SUIT_DICT[str(i)])
            if count >= 5:
                FlushInd = 1
                FlushSuit = str(i)
                HighCard = 0
                for (e1,e2) in card_list:
                    if e2 == FlushSuit:
                        if e1 > HighCard:
                            HighCard = e1

        #Check for straightInd
        rank_list = sorted(rank_list, reverse = True)
        straight_list = []
        for i in rank_list:
            if straight_list.count(i) == 0:
                straight_list.append(i)
        i = 0
        StraightInd = 0
        StraightHead = 0
        while i+5 <= straight_list.__len__():
            if straight_list[i] - straight_list[i+4] == 4:
                StraightInd = 1
                StraightHead = straight_list[i]
            i = i+1

        if FlushInd == 1 and StraightInd == 1 and StraightHead == 14:
            return (1, StraightHead, FlushSuit, 0, 0, 0, 0, 0, 1)
        elif FlushInd == 1 and StraightInd == 1:
            #Hand type,Straight Head,Flush Type,Quad Head,Trip Head,Pair Head,Pair Head,High Card
            return (2, StraightHead, FlushSuit, 0, 0, 0, 0, 0, 2 - StraightHead + 14) #16-7=9

        #Check for 4 of a kind
        for i in range(2,15):
            count = rank_list.count(i)
            if count == 4:
                QuadInd = 1
                QuadRank = i
                return(3, 0, 0, QuadRank, 0, 0, 0, 0, 10 - QuadRank + 14) #10-2+14 = 22

        #Check for 3 of a kind
        TripInd = 0
        TripRank = 0
        FHInd = 0
        Pair1Rank = 0
        for i in range(14,1,-1):
            count = rank_list.count(i)
            if count == 3:
                TripInd = 1
                TripRank = i
                #Check for full house
                fh_list = [x for x in rank_list if x != i]
                for j in range(14,1,-1):
                    count2 = fh_list.count(j)
                    if count2 >= 2:
                        FHInd = 1
                        TripInd = 0
                        Pair1Rank = j
                if Pair1Rank != 0:
                    break
            if Pair1Rank != 0:
                break

        if FHInd == 1:
            return (4, 0, 0, 0, TripRank, Pair1Rank, 0, 23 - (TripRank - 1) * 12 - (Pair1Rank - 1) + 168) #177
        elif FlushInd == 1:
            return (5, 0, FlushSuit, 0, 0, 0, 0, HighCard, 178 - HighCard + 14) #184
        elif StraightInd == 1:
            return (6, StraightHead, 0, 0, 0, 0, 0, 0, 185 - StraightHead + 14) #192
        elif TripInd == 1:
            return (7, 0, 0, 0, TripRank, 0, 0, 193 - TripRank + 14)

        #Check for pairs
        Pair1Rank = 0
        Pair2Rank = 0
        for i in range(14,1,-1):
            count = rank_list.count(i)
            if count == 2:
                Pair1Rank = i
                #Check for second pair house
                p2_list = [x for x in rank_list if x != i]
                for j in range(14,1,-1):
                    count2 = p2_list.count(j)
                    if count2 >= 2:
                        Pair2Rank = j
                    if Pair2Rank != 0:
                        break
            if Pair2Rank != 0:
                break

        if Pair1Rank != 0 and Pair2Rank != 0:
            return (8, 0, 0, 0, 0, Pair1Rank, Pair2Rank, 0, 206 - (Pair1Rank - 1) * 12 - (Pair2Rank - 1) + 168) #349
        elif Pair1Rank != 0:
            return (9, 0, 0, 0, 0, Pair1Rank, 0, 350 - Pair1Rank + 14)#362

        HighCard = 0
        for i in range(14,1,-1):
            count = rank_list.count(i)
            if count >= 1:
                HighCard = i
            if HighCard != 0:
                break

        return (10, 0, 0, 0, 0, 0, 0, HighCard, 363 - HighCard + 14)

class Deck:
    def __init__(self):
        self._Deck = []
        for rank in range(2,15):
            for suit in ['1','2','3','4']:
                c = Card(rank,suit)
                self._Deck.append(c)

    def shuffle(self):
        random.shuffle(self._Deck)

    def print(self):
        for each in self._Deck:
            each.printCard()

def CreateRandomCard():
    return Card(random.randint(2,14), str(random.randint(1,4)))

def getPostCurrentHandString(HandValue):
    HandOutput = HAND_DICT[HandValue[0]]
    if HandValue[0] == 2:
        HandOutput = HandOutput + " " + RANK_DICT[HandValue[1]] + " high"
    elif HandValue[0] == 3:
        HandOutput = HandOutput + " " + RANK_DICT[HandValue[3]] + "s"
    elif HandValue[0] == 4:
        HandOutput = HandOutput + " " + RANK_DICT[HandValue[4]] + "s over " + RANK_DICT[HandValue[5]]
    elif HandValue[0] == 6:
        HandOutput = HandOutput + " High card " + RANK_DICT[HandValue[7]]
    elif HandValue[0] == 7:
        HandOutput = HandOutput + " " + RANK_DICT[HandValue[4]] + "s"
    elif HandValue[0] == 8:
        HandOutput = HandOutput + " " + RANK_DICT[HandValue[5]] + "s and " + RANK_DICT[HandValue[6]] + "s"
    elif HandValue[0] == 9:
        HandOutput = HandOutput + " " + RANK_DICT[HandValue[5]] + "s"
    elif HandValue[0] == 10:
        HandOutput = HandOutput + " " + RANK_DICT[HandValue[7]]
    return HandOutput

def FindWinningHand(HandList):
    pass

def PlayHand(NumPlayers,HeroCard1, HeroCard2):

    #Set up the Dec
    FirstDeck = Deck()
    FirstDeck.shuffle()
    #Set up hero hand
    PlayerHands = []
    PlayerHands.append(Hand([HeroCard1,HeroCard2]))
    FirstDeck._Deck.remove(HeroCard1)
    FirstDeck._Deck.remove(HeroCard2)

    for i in range(1,NumPlayers):
        PlayerHands.append(Hand([FirstDeck._Deck.pop(),FirstDeck._Deck.pop()]))
    for i in range(0,NumPlayers):
        print("Player "+str(i)+" has the hand", end = " ")
        print(PlayerHands[i].getPreHandSimple())
    #Generate the flop
    ThirdCard = FirstDeck._Deck.pop()
    FourthCard = FirstDeck._Deck.pop()
    FifthCard = FirstDeck._Deck.pop()
    print("-" * 20)
    print("FLOP")
    print("-" * 20)
    print(ThirdCard)
    print(FourthCard)
    print(FifthCard)
    for i in range(0,NumPlayers):
        TempList = PlayerHands[i].getCards()
        TempList.append(ThirdCard)
        TempList.append(FourthCard)
        TempList.append(FifthCard)
        PlayerHands[i] = Hand(TempList)
    for i in range(0,NumPlayers):
        HandValue = getPostCurrentHandString(PlayerHands[i].getPostCurrentHandValue())
        print("FLOP: Player "+str(i)+" has the hand "+ HandValue)
    print("-" * 20)
    print("TURN")
    print("-" * 20)
    SixthCard = FirstDeck._Deck.pop()
    for i in range(0,NumPlayers):
        TempList = PlayerHands[i].getCards()
        TempList.append(SixthCard)
        PlayerHands[i] = Hand(TempList)
    for i in range(0,NumPlayers):
        HandValue = getPostCurrentHandString(PlayerHands[i].getPostCurrentHandValue())
        print("TURN: Player "+str(i)+" has the hand "+ HandValue)
    print("-" * 20)
    print("RIVER")
    print("-" * 20)
    SeventhCard = FirstDeck._Deck.pop()
    for i in range(0,NumPlayers):
        TempList = PlayerHands[i].getCards()
        TempList.append(SeventhCard)
        PlayerHands[i] = Hand(TempList)
    for i in range(0,NumPlayers):
        HandValue = getPostCurrentHandString(PlayerHands[i].getPostCurrentHandValue())
        print("RIVER: Player "+str(i)+" has the hand "+ HandValue)



print("Test Poker Hand program")
print("-" * 30)

#FirstCard = CreateRandomCard()
FirstCard = Card(14,'1')
SecondCard = Card(14,'2')
#SecondCard = CreateRandomCard()
nothing = PlayHand(10,FirstCard,SecondCard)
