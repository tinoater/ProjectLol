import unittest
import os

import constants

# ----------------
#  Constants tests
# ----------------
class ConstantDefaultTestCase(unittest.TestCase):
    """Tests for the default constant values in constants.py."""

    def test_default_CARD1POS(self):
        """Is the default CARD1POS value correct?"""
        self.assertEqual(constants.CARD1POS, (215, 222, 245, 239))

    def test_default_BH_R_RERAISE(self):
        """Is the default BH_R_RERAISE value correct?"""
        self.assertEqual(constants.BH_R_RERAISE, 1)

    def test_default_LOG_FILE_DIR(self):
        """Is the default LOG_FILE_DIR value correct?"""
        self.assertEqual(constants.LOG_FILE_DIR, "C:\\Users\\Ahab\\Desktop")


class ConstantFileTestCase(unittest.TestCase):
    """Tests for constants after reading from a file"""

    def setUp(self):
        script_dir = os.path.dirname(__file__)
        dir = os.path.join(script_dir, "files//tests_constants.txt")
        constants.updatePositionVariables(dir)

    def test_file_CARD1POS(self):
        """Is the files CARD1POS value correct?"""
        self.assertEqual(constants.CARD1POS, (223, 208, 236, 225))

    def test_file_PLAYERACTIONPOSLIST_0(self):
        """Are the files PLAYERACTIONPOSLIST values correct?"""
        self.assertEqual(constants.PLAYERACTIONPOSLIST[0], (0, 0, 0, 0))

    def test_file_PLAYERACTIONPOSLIST_8(self):
        """Are the files PLAYERACTIONPOSLIST values correct?"""
        self.assertEqual(constants.PLAYERACTIONPOSLIST[8], (375, 269, 437, 270))

    def test_file_LOG_FILE_DIR(self):
        """Is the files LOG_FILE_DIR value correct?"""
        self.assertEqual(constants.LOG_FILE_DIR, "C:\\Users\\Ahab\Desktop\\NewDir")
