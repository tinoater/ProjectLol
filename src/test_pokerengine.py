import unittest

import cardutils

class CardTestCase(unittest.TestCase):
    """Tests for cardutils.py."""

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