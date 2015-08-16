import unittest

from cardutils import Card

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
        self.hand = Hand(Card(14,1),Card(13,1))

    def tearDown(self):
        self.hand.dispose()
        self.hand = None

    def test_shared_cards_are_zero(self):
        """Is share cards zero when only 2 cards in hand?"""
        self.assertEqual(len(self.hand.sharedCards), 0)

    def test_numcards_is_two(self):
        """Is the number of cards two for two cards in hand?"""
        self.assertEqual(self.hand.numCards, 2)

    def test_is_AKs_Premium(self):
        """Is AKs considered premium?"""
        self.assertEqual(self.hand.PremInd, 1)

    def test_is_AKs_Connected(self):
        """Is AKs considered connected?"""
        self.assertEqual(self.hand.ConnectedInd, 1)

    def test_is_AKs_Suited(self):
        """Is AKs considered suited?"""
        self.assertEqual(self.hand.SuitedInd, 1)

    def test_AKs_correct_preflop_odds(self):
        """Is AKs preflop 10 player odds the correct value"""
        self.assertEqual(self.hand.preFlopOdds10, 20.1)

    def test_is_AKs_preHandSimple_correct(self):
        """Does AKs have the correct preHandSimple expression?"""
        self.assertEqual(self.hand.getPreHandSimple(), 'AKs')

class PocketNineHandTestCase(unittest.TestCase):
    """Tests for 99 Hand class in cardutils.py"""

    def setUp(self):
        self.hand = Hand(Card(9,1),Card(9,2))

    def tearDown(self):
        self.hand.dispose()
        self.hand = None

    def test_is_99_Premium(self):
        """Is 99 considered premium?"""
        self.assertEqual(self.hand.PremInd, 0)

    def test_is_99_Connected(self):
        """Is 99 considered connected?"""
        self.assertEqual(self.hand.ConnectedInd, 0)

    def test_is_99_1SpaceConnected(self):
        """Is 99 considered 1spaceconnected?"""
        self.assertEqual(self.hand.oneSpaceConnectedInd, 0)

    def test_is_99_Suited(self):
        """Is 99 considered suited?"""
        self.assertEqual(self.hand.SuitedInd, 0)

    def test_99_correct_preflop_odds(self):
        """Is 99 preflop 10 player odds the correct value"""
        self.assertEqual(self.hand.preFlopOdds10, 20.1)

    def test_is_99_a_PockedPair(self):
        """Is 99 considered a pocket pair?"""
        self.assertEqual(self.hand.PPInd, 1)

    def test_does_99_have_Pair_card_9(self):
        """Does 99 have pair card 9?"""
        self.assertEqual(self.hand.PPCard, 9)

    def test_is_99_preHandSimple_correct(self):
        """Does 99 have the correct preHandSimple expression?"""
        self.assertEqual(self.hand.getPreHandSimple(), '99')

class FiveSevenOffHandTestCase(unittest.TestCase):
    """Tests for 57o Hand class in cardutils.py"""

    def setUp(self):
        self.hand = Hand(Card(5,1),Card(7,2))

    def tearDown(self):
        self.hand.dispose()
        self.hand = None

    def test_is_57o_Premium(self):
        """Is 57o considered premium?"""
        self.assertEqual(self.hand.PremInd, 0)

    def test_is_57o_Connected(self):
        """Is 57o considered connected?"""
        self.assertEqual(self.hand.ConnectedInd, 0)

    def test_is_57o_1SpaceConnected(self):
        """Is 57o considered 1spaceconnected?"""
        self.assertEqual(self.hand.oneSpaceConnectedInd, 1)

    def test_is_57o_Suited(self):
        """Is 57o considered suited?"""
        self.assertEqual(self.hand.SuitedInd, 0)

    def test_57o_correct_preflop_odds(self):
        """Is 57o preflop 10 player odds the correct value"""
        self.assertEqual(self.hand.preFlopOdds10, 20.1)

    def test_is_57o_a_PockedPair(self):
        """Is 57o considered a pocket pair?"""
        self.assertEqual(self.hand.PPInd, 0)

    def test_does_57o_have_Pair_card_0(self):
        """Does 57o have pair card 0?"""
        self.assertEqual(self.hand.PPCard, 0)

    def test_is_57o_preHandSimple_correct(self):
        """Does 57o have the correct preHandSimple expression?"""
        self.assertEqual(self.hand.getPreHandSimple(), '57o')
