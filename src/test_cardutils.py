import unittest

import cardutils

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
        self.assertIsInstance(cardutils.Card(10,1).getRank(), int)

    def test_is_suit_integer(self):
        """Is suit returned as integer?"""
        self.assertIsInstance(cardutils.Card(10,1).getSuit(), int)

    def test_is_str_rep_string(self):
        """Is the string representation of type string?"""
        self.assertIsInstance(cardutils.Card(10,1).__str__(), str)

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
        self.assertEqual(self.hand.PremInd, 1)
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
        self.assertEqual(self.hand.PremInd, 0)
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
        self.assertEqual(self.hand.PremInd, 0)
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
        self.assertEqual(self.hand.FlushInd, 1)
        self.assertEqual(self.hand.StraightInd, 0)

class RoyalFlushTestCase(unittest.TestCase):
    """Tests for a royal flush in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(14,1),cardutils.Card(13,1)])
        self.hand.addSharedCards([cardutils.Card(12,1),cardutils.Card(11,1),cardutils.Card(10,1)])

    def tearDown(self):
        self.hand = None

    def test_royal_flush_properties(self):
        """Are the hand properties correct?"""
        self.assertEqual(self.hand.FlushInd, 1)
        self.assertEqual(self.hand.StraightInd, 1)
        self.assertEqual(self.hand.StraightHead, 14)
        self.assertEqual(self.hand.PostHandType, 1)
        self.assertEqual(self.hand.PostHandValue, 1)

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
        self.assertEqual(self.hand.FlushInd, 1)
        self.assertEqual(self.hand.StraightInd, 1)
        self.assertEqual(self.hand.StraightHead, 10)
        self.assertEqual(self.hand.PostHandType, 2)
        self.assertEqual(self.hand.PostHandValue, 5)

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
        self.assertEqual(self.hand.FlushInd, 0)
        self.assertEqual(self.hand.StraightInd, 0)
        self.assertEqual(self.hand.StraightHead, 0)
        self.assertEqual(self.hand.QuadRank, 10)
        self.assertEqual(self.hand.QuadInd, 1)
        self.assertEqual(self.hand.PostHandType, 3)
        self.assertEqual(self.hand.PostHandValue, 15)

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
        self.assertEqual(self.hand.FlushInd, 0)
        self.assertEqual(self.hand.StraightInd, 0)
        self.assertEqual(self.hand.StraightHead, 0)
        self.assertEqual(self.hand.PostHandType, 4)
        self.assertEqual(self.hand.PostHandValue, 171)

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
        self.assertEqual(self.hand.FlushInd, 1)
        self.assertEqual(self.hand.StraightInd, 0)
        self.assertEqual(self.hand.HighCard, 10)
        self.assertEqual(self.hand.PostHandType, 5)
        self.assertEqual(self.hand.PostHandValue, 183)

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
        self.assertEqual(self.hand.FlushInd, 0)
        self.assertEqual(self.hand.StraightInd, 1)
        self.assertEqual(self.hand.StraightHead, 5)
        self.assertEqual(self.hand.PostHandType, 6)
        self.assertEqual(self.hand.PostHandValue, 196)

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
        self.assertEqual(self.hand.FlushInd, 0)
        self.assertEqual(self.hand.TripInd, 1)
        self.assertEqual(self.hand.TripRank, 14)
        self.assertEqual(self.hand.PostHandType, 7)
        self.assertEqual(self.hand.PostHandValue, 197)

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
        self.assertEqual(self.hand.Pair1Rank, 14)
        self.assertEqual(self.hand.Pair2Rank, 4)
        self.assertEqual(self.hand.PostHandType, 8)
        self.assertEqual(self.hand.PostHandValue, 219)

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
        self.assertEqual(self.hand.Pair1Rank, 4)
        self.assertEqual(self.hand.Pair2Rank, 0)
        self.assertEqual(self.hand.PostHandType, 9)
        self.assertEqual(self.hand.PostHandValue, 243)

    def test_is_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'One Pair 4s')

class HighCardTestCase(unittest.TestCase):
    """Tests for high cards in Hand class in cardutils.py"""

    def setUp(self):
        self.hand = cardutils.Hand([cardutils.Card(14,1),cardutils.Card(13,2)])
        self.hand.addSharedCards([cardutils.Card(4,1),cardutils.Card(6,2),cardutils.Card(5,1)])

    def tearDown(self):
        self.hand = None

    def test_highcard_properties(self):
        """Are the hand properties correct?"""
        self.assertEqual(self.hand.Pair1Rank, 0)
        self.assertEqual(self.hand.HighCard, 14)
        self.assertEqual(self.hand.PostHandType, 10)
        self.assertEqual(self.hand.PostHandValue, 247)

    def test_is_hand_string_correct(self):
        """Is the full hand string correct?"""
        self.assertEqual(self.hand.getPostCurrentHandString(), 'High Card A')

class DeckTestCase(unittest.TestCase):
    """Tests for Card class in cardutils.py."""
    def test_deck_has_52_cards(self):
        """Does a new deck have 52 cards?"""
        self.assertEqual(len(cardutils.Deck()._Deck), 52)

class PlayerTestCase(unittest.TestCase):
    """Tests for Player class in cardutils"""
    def test_add_player(self):
        dummyPlayer = cardutils.Player(10,"name",3.11,[1,10])

class StatsTestCase(unittest.TestCase):
    """Tests for Stats class in cardutils"""
    def test_add_player(self):
        dummyStats = cardutils.Stats(100,10,3,10,10,10,10,10,10)