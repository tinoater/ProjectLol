import unittest

import cardutils

# ----------------
# Card class tests
# ----------------
class CardTestCase(unittest.TestCase):
    """Tests for Card class in cardutils.py."""

    def test_does_rank_error(self):
        """Does Card error when given invalid rank?"""
        self.assertRaises(Exception,lambda: cardutils.Card(1,1))

    def test_does_suit_error(self):
        """Does Card error when given invalid rank?"""
        self.assertRaises(Exception,lambda: cardutils.Card(10,0))

    def test_is_rank_integer(self):
        """Is rank returned as integer?"""
        self.assertIsInstance(cardutils.Card(10,1).rank, int)

    def test_is_suit_integer(self):
        """Is suit returned as integer?"""
        self.assertIsInstance(cardutils.Card(10,1).suit, int)

    def test_is_str_rep_string(self):
        """Is the string representation of type string?"""
        self.assertIsInstance(cardutils.Card(10,1).__str__(), str)

class CardEqualityTestCase(unittest.TestCase):
    """Tests to check the card equality tests work"""
    def setUp(self):
        self.card1 = cardutils.Card(13,2)
        self.card2 = cardutils.Card(13,2)
        self.card3 = cardutils.Card(13,1)
        self.card4 = cardutils.Card(12,2)

    def tearDown(self):
        self.card1 = None
        self.card2 = None
        self.card3 = None
        self.card4 = None

    def test_cards_are_equal(self):
        self.assertTrue(self.card1 == self.card2)

    def test_cards_are_not_equal_suit(self):
        self.assertTrue(self.card1 != self.card4)

    def test_cards_are_not_equal_rank(self):
        self.assertTrue(self.card1 != self.card3)

# ----------------
# Deck class tests
# ----------------
class FullDeckTestCase(unittest.TestCase):
    """Tests for Deck class in cardutils.py."""
    def test_deck_has_52_cards(self):
        """Does a new deck have 52 cards?"""
        self.assertEqual(len(cardutils.Deck().deck), 52)

class PartialDeckTestCase(unittest.TestCase):
    def setUp(self):
        self.ignoreList = []
        self.ignoreList.append(cardutils.Card(13,1))
        self.ignoreList.append(cardutils.Card(8,3))
        self.ignoreList.append(cardutils.Card(6,2))
        self.ignoreList.append(cardutils.Card(12,3))
        self.ignoreList.append(cardutils.Card(11,2))
        self.ignoreList.append(cardutils.Card(10,1))
        self.partialDeck = cardutils.Deck(self.ignoreList)

        self.ignoredCardPresent = False
        for each in self.partialDeck.deck:
            for eachig in self.ignoreList:
                if eachig == each:
                    self.ignoredCardPresent = True

    def tearDown(self):
        self.ignoreList = None
        self.parialDeck = None

    def test_partial_deck_has_fewer_cards(self):
        """ Check the passed in cards have been removed from the Deck"""
        self.assertEqual(len(self.partialDeck.deck), 46)

    def test_partial_deck_doesnt_have_ignored_cards(self):
        """ Check that the ignored cards are ignored from the Deck"""
        self.assertEqual(self.ignoredCardPresent, False)

# ----------------
# Stats class tests
# ----------------
class StatsTestCase(unittest.TestCase):
    def setUp(self):
        self.stats = cardutils.Stats(100,10,10,50,20,60,70,80,90)

    def tearDown(self):
        self.stats = None

    def test_stats_class_initialisation(self):
        """ Check that the Stats class can be created"""
        self.assertIsInstance(self.stats,cardutils.Stats)

    def test_stats_class_init_statsPresentInd(self):
        """Check that the statsPresent Ind is created properly"""
        self.assertEqual(self.stats.statsPresent, True)

class StatsEmptyTestCase(unittest.TestCase):
    def setUp(self):
        self.stats = cardutils.Stats(empty = True)

    def tearDown(self):
        self.stats = None

    def test_stats_class_init_empty(self):
        """ Check that the Stats class can be created as empty"""
        self.assertIsInstance(self.stats, cardutils.Stats)

    def test_stats_class_init_statsPresentInd(self):
        """Check that the statsPresent Ind is created properly"""
        self.assertEqual(self.stats.statsPresent, False)
# ----------------
# Player class tests
# ----------------
class PlayerTestCase(unittest.TestCase):
    """Tests for Player class in cardutils"""
    def setUp(self):
        self.stats = cardutils.Stats(100,10,10,50,20,60,70,80,90)
        self.player = cardutils.Player(4,'name',100,self.stats)
        self.player.updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
        self.player.updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
        self.player.updatePlayerbHist(1,cardutils.BETSTRING_DICT['CALL'])
        self.player.updatePlayerbHist(2,cardutils.BETSTRING_DICT['FOLD'])

    def tearDown(self):
        self.stats = None
        self.player = None

    def test_exception_seat(self):
        self.assertRaises(Exception,lambda: cardutils.Player('lol','name',111,self.stats))

    def test_exception_name(self):
        self.assertRaises(Exception,lambda: cardutils.Player(4,90,111,self.stats))

    def test_exception_cash(self):
        self.assertRaises(Exception,lambda: cardutils.Player(4,'name',100.11,self.stats))

    def test_exception_stats(self):
        self.assertRaises(Exception,lambda: cardutils.Player(4,'name',111,(100,10,10,50,20,60,70,80,90)))

    def test_updatePlayerbHist_multiactions_1(self):
        """ Check that the updatePlayerbHist function sets up the playerbHist correctly for many actions on a street"""
        self.assertEqual(self.player.bHist[0][0], cardutils.BETSTRING_DICT['RAISE'])

    def test_updatePlayerbHist_multiactions_2(self):
        """ Check that the updatePlayerbHist function sets up the playerbHist correctly for many actions on a street"""
        self.assertEqual(self.player.bHist[0][1], cardutils.BETSTRING_DICT['CALL'])

    def test_updatePlayerbHist_singleaction(self):
        """ Check that the updatePlayerbHist function sets up the playerbHist correctly for a single action on a street"""
        self.assertEqual(self.player.bHist[1], [cardutils.BETSTRING_DICT['CALL']])

    def test_updatePlayerbHist_fold_1(self):
        """ Check that the updatePlayerbHist function sets up the playerbHist correctly for a folded action"""
        self.assertEqual(self.player.bHist[2], [cardutils.BETSTRING_DICT['FOLD']])

    def test_updatePlayerbHist_fold_2(self):
        """ Check that the updatePlayerbHist function sets up the foldedInd correctly for a folded action"""
        self.assertEqual(self.player.foldedInd, 1)

class ResetPlayersTestCase(unittest.TestCase):
    def setUp(self):
        PlayerTestCase.setUp(self)
        self.player.resetPlayer(4.40, 2.20)

    def tearDown(self):
        PlayerTestCase.tearDown(self)

    def test_handsPlayed(self):
        self.assertEqual(self.player.handsPlayed, 1)

    def test_cashWon(self):
        self.assertEqual(self.player.cashWon, 4.40)

    def test_cashWonAgainstHero(self):
        self.assertEqual(self.player.cashWonAgainstHero, 2.20)

    def test_resetPlayer_foldedInd(self):
        self.assertEqual(self.player.foldedInd, 0)

# ----------------
# Hand class tests
# ----------------
# Test Cases for methods
class HandAddTestCase(unittest.TestCase):

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(13,1), cardutils.Card(13,2)])
        self.hand + cardutils.Card(13,3)

    def tearDown(self):
        self.hand = None

    def test_after_add_numCards(self):
        self.assertEqual(self.hand.numCards, 3)

    def test_after_add_sharedCards(self):
        self.assertEqual(self.hand.sharedCards, [cardutils.Card(13,3)])

    def test_after_add_cards(self):
        self.assertEqual(self.hand.cards[2], cardutils.Card(13,3))

# Test Cases for example hands for each possible hand type
class AKsHandTestCase(unittest.TestCase):
    """Tests for AKs Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(14,1),cardutils.Card(13,1)])

    def tearDown(self):
        self.hand = None

    def test_shared_cards_are_zero(self):
        """Is share cards zero when only 2 cards in hand?"""
        self.assertEqual(len(self.hand.sharedCards), 0)

    def test_numcards_is_two(self):
        """Is the number of cards two for two cards in hand?"""
        self.assertEqual(self.hand.numCards, 2)

    def test_AKs_Properties(self):
        """Are the properties of AKs correct? Suited,Connected etc"""
        self.assertEqual(self.hand.premInd, 1)
        self.assertEqual(self.hand.connectedInd, 1)
        self.assertEqual(self.hand.suitedInd, 1)

    def test_AKs_correct_preflop_odds(self):
        """Is AKs preflop 10 player odds the correct value"""
        self.assertEqual(self.hand.preFlopOdds10, 20.7)

    def test_is_AKs_preHandSimple_correct(self):
        """Does AKs have the correct preHandSimple expression?"""
        self.assertEqual(self.hand.getPreHandSimple(), 'AKs')

class PocketNineHandTestCase(unittest.TestCase):
    """Tests for 99 Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(9,1),cardutils.Card(9,2)])

    def tearDown(self):
        self.hand = None

    def test_is_99_1SpaceConnected(self):
        """Are the properties of 99 correct? Suited,Connected etc"""
        self.assertEqual(self.hand.oneSpaceConnectedInd, 0)
        self.assertEqual(self.hand.suitedInd, 0)
        self.assertEqual(self.hand.premInd, 0)
        self.assertEqual(self.hand.connectedInd, 0)
        self.assertEqual(self.hand.PPInd, 1)
        self.assertEqual(self.hand.PPCard, 9)

    def test_99_correct_preflop_odds(self):
        """Is 99 preflop 10 player odds the correct value"""
        self.assertEqual(self.hand.preFlopOdds10, 15.6)

    def test_is_99_preHandSimple_correct(self):
        """Does 99 have the correct preHandSimple expression?"""
        self.assertEqual(self.hand.getPreHandSimple(), '99')

class FiveSevenOffHandTestCase(unittest.TestCase):
    """Tests for 57o Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(5,1),cardutils.Card(7,2)])

    def tearDown(self):
        self.hand = None

    def test_57o_Properties(self):
        """Are the properties of 99 correct? Suited,Connected etc"""
        self.assertEqual(self.hand.premInd, 0)
        self.assertEqual(self.hand.connectedInd, 0)
        self.assertEqual(self.hand.oneSpaceConnectedInd, 1)
        self.assertEqual(self.hand.suitedInd, 0)
        self.assertEqual(self.hand.PPInd, 0)
        self.assertEqual(self.hand.PPCard, 0)

    def test_57o_correct_preflop_odds(self):
        """Is 57o preflop 10 player odds the correct value"""
        self.assertEqual(self.hand.preFlopOdds10, 7.9)

    def test_is_57o_preHandSimple_correct(self):
        """Does 57o have the correct preHandSimple expression?"""
        self.assertEqual(self.hand.getPreHandSimple(), '75o')

class AKsHandAddFlushFlopTestCase(unittest.TestCase):
    """Tests for adding flop cards to make a flush in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(14,1),cardutils.Card(13,1)])
        self.hand.addSharedCards([cardutils.Card(2,1),cardutils.Card(4,1),cardutils.Card(8,1)])

    def tearDown(self):
        self.hand = None

    def test_shared_cards_len(self):
        """Are shared cards now 3?"""
        self.assertEqual(len(self.hand.sharedCards), 3)

    def test_numcards_is_two(self):
        """Is the number of cards five for five cards in hand?"""
        self.assertEqual(self.hand.numCards, 5)

    def test_is_a_properties(self):
        """Are the hand properties correct?"""
        self.assertEqual(self.hand.flushInd, 1)
        self.assertEqual(self.hand.straightInd, 0)

class RoyalFlushTestCase(unittest.TestCase):
    """Tests for a royal flush in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(14,1),cardutils.Card(13,1)])
        self.hand.addSharedCards([cardutils.Card(12,1),cardutils.Card(11,1),cardutils.Card(10,1)])

    def tearDown(self):
        self.hand = None

    def test_royal_flush_properties(self):
        """Are the hand properties correct?"""
        self.assertEqual(self.hand.flushInd, 1)
        self.assertEqual(self.hand.straightInd, 1)
        self.assertEqual(self.hand.straightHead, 14)
        self.assertEqual(self.hand.postHandType, 1)
        self.assertEqual(self.hand.postHandValue, 1)

    def test_is_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'Royal Flush')

class StraightFlushTestCase(unittest.TestCase):
    """Tests for a straight flush in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(10,1),cardutils.Card(7,1)])
        self.hand.addSharedCards([cardutils.Card(9,1),cardutils.Card(8,1),cardutils.Card(6,1)])

    def tearDown(self):
        self.hand = None

    def test_straight_flush_properties(self):
        """Are the hand properties correct?"""
        self.assertEqual(self.hand.flushInd, 1)
        self.assertEqual(self.hand.straightInd, 1)
        self.assertEqual(self.hand.straightHead, 10)
        self.assertEqual(self.hand.postHandType, 2)
        self.assertEqual(self.hand.postHandValue, 5)

    def test_is_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'Straight Flush T high')

class FourOfAKindTestCase(unittest.TestCase):
    """Tests for a quads in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(10,1),cardutils.Card(10,2)])
        self.hand.addSharedCards([cardutils.Card(10,3),cardutils.Card(10,4),cardutils.Card(6,1)])

    def tearDown(self):
        self.hand = None

    def test_quad_flush_ind(self):
        """Are the hand properties correct?"""

    def test_quad_properties(self):
        """Is the straight ind set correctly for quads?"""
        self.assertEqual(self.hand.flushInd, 0)
        self.assertEqual(self.hand.straightInd, 0)
        self.assertEqual(self.hand.straightHead, 0)
        self.assertEqual(self.hand.quadRank, 10)
        self.assertEqual(self.hand.quadInd, 1)
        self.assertEqual(self.hand.postHandType, 3)
        self.assertEqual(self.hand.postHandValue, 15)

    def test_is_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'Four of a Kind Ts')

class FullHouseTestCase(unittest.TestCase):
    """Tests for a full house in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(10,1),cardutils.Card(10,2)])
        self.hand.addSharedCards([cardutils.Card(2,1),cardutils.Card(2,2),cardutils.Card(2,3)])

    def tearDown(self):
        self.hand = None

    def test_full_house_flush_ind(self):
        """Are the hand properties correct?"""

    def test_full_house_properties(self):
        """Is the straight ind set correctly for full house?"""
        self.assertEqual(self.hand.flushInd, 0)
        self.assertEqual(self.hand.straightInd, 0)
        self.assertEqual(self.hand.straightHead, 0)
        self.assertEqual(self.hand.postHandType, 4)
        self.assertEqual(self.hand.postHandValue, 171)

    def test_is_full_house_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'Full House 2s over T')

class FlushTestCase(unittest.TestCase):
    """Tests for a flush in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(10,1),cardutils.Card(7,1)])
        self.hand.addSharedCards([cardutils.Card(9,1),cardutils.Card(8,1),cardutils.Card(5,1)])

    def tearDown(self):
        self.hand = None

    def test_flush_properties(self):
        """Are the hand properties correct?"""
        self.assertEqual(self.hand.flushInd, 1)
        self.assertEqual(self.hand.straightInd, 0)
        self.assertEqual(self.hand.highCard, 10)
        self.assertEqual(self.hand.postHandType, 5)
        self.assertEqual(self.hand.postHandValue, 183)

    def test_is_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'Flush T')

class StraightTestCase(unittest.TestCase):
    """Tests for a straight in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(14,1),cardutils.Card(2,1)])
        self.hand.addSharedCards([cardutils.Card(3,1),cardutils.Card(4,2),cardutils.Card(5,1)])

    def tearDown(self):
        self.hand = None

    def test_straight_properties(self):
        """Are the hand properties correct?"""
        self.assertEqual(self.hand.flushInd, 0)
        self.assertEqual(self.hand.straightInd, 1)
        self.assertEqual(self.hand.straightHead, 5)
        self.assertEqual(self.hand.postHandType, 6)
        self.assertEqual(self.hand.postHandValue, 196)

    def test_is_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'Straight High card 5')

class TripsTestCase(unittest.TestCase):
    """Tests for a trips in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(14,1),cardutils.Card(14,2)])
        self.hand.addSharedCards([cardutils.Card(3,1),cardutils.Card(14,4),cardutils.Card(5,1)])

    def tearDown(self):
        self.hand = None

    def test_trips_properties(self):
        """Are the hand properties correct?"""
        self.assertEqual(self.hand.flushInd, 0)
        self.assertEqual(self.hand.tripInd, 1)
        self.assertEqual(self.hand.tripRank, 14)
        self.assertEqual(self.hand.postHandType, 7)
        self.assertEqual(self.hand.postHandValue, 197)

    def test_is_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'Three of a Kind As')

class TwoPairTestCase(unittest.TestCase):
    """Tests for two pair in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(14,1),cardutils.Card(14,2)])
        self.hand.addSharedCards([cardutils.Card(4,1),cardutils.Card(4,2),cardutils.Card(5,1)])

    def tearDown(self):
        self.hand = None

    def test_twopair_properties(self):
        """Are the hand properties correct?"""
        self.assertEqual(self.hand.pair1Rank, 14)
        self.assertEqual(self.hand.pair2Rank, 4)
        self.assertEqual(self.hand.postHandType, 8)
        self.assertEqual(self.hand.postHandValue, 219)

    def test_is_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'Two Pairs As and 4s')

class PairTestCase(unittest.TestCase):
    """Tests for pair in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(14,1),cardutils.Card(2,2)])
        self.hand.addSharedCards([cardutils.Card(4,1),cardutils.Card(4,2),cardutils.Card(5,1)])

    def tearDown(self):
        self.hand = None

    def test_pair_properties(self):
        """Are the hand properties correct?"""
        self.assertEqual(self.hand.pair1Rank, 4)
        self.assertEqual(self.hand.pair2Rank, 0)
        self.assertEqual(self.hand.postHandType, 9)
        self.assertEqual(self.hand.postHandValue, 243)

    def test_is_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'One Pair 4s')

class highCardTestCase(unittest.TestCase):
    """Tests for high cards in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(14,1),cardutils.Card(13,2)])
        self.hand.addSharedCards([cardutils.Card(4,1),cardutils.Card(6,2),cardutils.Card(5,1)])

    def tearDown(self):
        self.hand = None

    def test_highcard_properties(self):
        """Are the hand properties correct?"""
        self.assertEqual(self.hand.pair1Rank, 0)
        self.assertEqual(self.hand.highCard, 14)
        self.assertEqual(self.hand.postHandType, 10)
        self.assertEqual(self.hand.postHandValue, 247)

    def test_is_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'High Card A')