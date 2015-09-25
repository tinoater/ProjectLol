import unittest

import nlhutils
import cardutils

class AAsPFTestCase(unittest.TestCase):
    """
    Tests for AA Game class in cardutils.py
    """
    def setUp(self):
        herohand = cardutils.Hand(cardutils.Card(14,1), cardutils.Card(14,2))
        playerSB = cardutils.Player(1,"playerSB",100000,[])
        playerBB = cardutils.Player(2,"playerBB",100000,[])
        playerCO = cardutils.Player(8,"playerCO",100000,[])
        playerHero = cardutils.Player(9,"hero",10000,[])
        self.game = nlhutils.Game(herohand,[playerSB, playerBB, playerCO, playerHero])
        self.game.player[0].updatePlayerbHist(0,'SB')
        self.game.player[1].updatePlayerbHist(0,'BB')
        self.game.player[2].updatePlayerbHist(0,'R')
        self.game.setHeroPosition()
        self.game.setHeroPlayer("hero")
        self.game.updateNumPlayers()
        self.game.currbet = 10
        self.currbet0 = 10
        self.potamount0 = 13
        self.game.potamount = 13
        self.game.HeroCash = self.game.player[self.game.heroplayer].cash
        (self.action1, self.amount1, self.wait1, self.logstring1) = self.game.bet()

        self.game.player[0].updatePlayerbHist(0, 'X')
        self.game.player[1].updatePlayerbHist(0, 'X')
        self.game.player[2].updatePlayerbHist(0, 'R')
        self.game.currbet = 50
        self.currbet1 = 50
        self.game.potamount = 13 + 2*self.amount1 + 50
        (self.action2, self.amount2, self.wait2, self.logstring2) = self.game.bet()

        self.game.player[2].updatePlayerbHist(0, 'R')
        self.game.currbet = 200
        self.currbet2 = 200
        self.game.potamount = 13 + 2*self.amount1 + 2*self.amount2 + 200
        (self.action3, self.amount3, self.wait3, self.logstring3) = self.game.bet()

        self.game.player[2].updatePlayerbHist(0, 'R')
        self.game.currbet = 2000000
        self.currbet3 = 2000000
        self.game.potamount = 13 + 2*self.amount1 + 2*self.amount2 + 2*self.amount3 + 2000000
        (self.action4, self.amount4, self.wait4, self.logstring4) = self.game.bet()

    def test_initnumplayers(self):
        self.assertEqual(self.game.initnumplayers, 4)

    def test_BHInd(self):
        self.assertEqual(self.game.BHInd, 1)

    def test_updateNumPlayers(self):
        self.assertEqual(self.game.numplayers, 4)

    def test_heroposition(self):
        self.assertEqual(self.game.position, 4)
        self.assertEqual(self.game.player[3].seat, 9)

    def test_betamounts1(self):
        self.assertEqual(self.currbet0, 10)
        self.assertEqual(self.potamount0, 13)
        self.assertEqual(self.action1, 2)
        self.assertGreaterEqual(self.amount1, 2 * self.currbet0)
        self.assertLessEqual(self.amount1, 3 * self.currbet0)

    def test_betamounts2(self):
        self.assertEqual(self.action2, 2)
        self.assertGreaterEqual(self.amount2, 2 * self.currbet1)
        self.assertLessEqual(self.amount2, 3 * self.currbet1)

    def test_betamounts3(self):
        self.assertEqual(self.action3, 2)
        self.assertGreaterEqual(self.amount3, 2 * self.currbet2)
        self.assertLessEqual(self.amount3, 3 * self.currbet2)

    def test_betamounts4(self):
        self.assertEqual(self.action4, 3)

class PreFlopIndsTestCase(unittest.TestCase):
    """
    Test case for the PreFlopInds functions
    """
    def setUp(self):
        herohand = cardutils.Hand(cardutils.Card(14,1), cardutils.Card(14,2))
        playerSB = cardutils.Player(1,"playerSB",100000,[])
        playerBB = cardutils.Player(2,"playerBB",100000,[])
        playerCO = cardutils.Player(8,"playerCO",100000,[])
        playerHero = cardutils.Player(9,"hero",10000,[])
        self.game = nlhutils.Game(herohand,[playerSB, playerBB, playerCO, playerHero])
        self.game.player[0].updatePlayerbHist(0,'SB')
        self.game.player[1].updatePlayerbHist(0,'BB')
        self.game.player[2].updatePlayerbHist(0,'R')
        self.game.player[0].updatePlayerbHist(0,'X')
        self.game.player[1].updatePlayerbHist(0,'C')
        self.game.setHeroPosition()
        self.game.setHeroPlayer("hero")
        self.game.updateNumPlayers()
        self.game.setPreFlopInds()

        self.game2 = nlhutils.Game(herohand,[playerSB, playerBB, playerCO, playerHero])
        self.game2.player[0].updatePlayerbHist(0,'SB')
        self.game2.player[1].updatePlayerbHist(0,'BB')
        self.game2.player[2].updatePlayerbHist(0,'C')
        self.game2.player[3].updatePlayerbHist(0,'R')
        self.game2.player[0].updatePlayerbHist(0,'X')
        self.game2.player[1].updatePlayerbHist(0,'X')
        self.game2.player[2].updatePlayerbHist(0,'C')
        self.game2.setHeroPosition()
        self.game2.setHeroPlayer("hero")
        self.game2.updateNumPlayers()
        self.game2.setPreFlopInds()

        self.game3 = nlhutils.Game(herohand,[playerSB, playerBB, playerCO, playerHero])
        self.game3.player[0].updatePlayerbHist(0,'SB')
        self.game3.player[1].updatePlayerbHist(0,'BB')
        self.game3.player[2].updatePlayerbHist(0,'R')
        self.game3.player[0].updatePlayerbHist(0,'R')
        self.game3.player[1].updatePlayerbHist(0,'X')
        self.game3.player[2].updatePlayerbHist(0,'C')

        self.game3.setHeroPosition()
        self.game3.setHeroPlayer("hero")
        self.game3.updateNumPlayers()
        self.game3.setPreFlopInds()

    def test_simplePreFlopIndsTest(self):
        self.assertEqual(self.game.PFAggressor, 2)

    def test_simpleHeroPreFlopIndsTest(self):
        self.assertEqual(self.game2.PFAggressor, -1)

    def test_reraiseHeroPreFlopIndsTest(self):
        self.assertEqual(self.game3.PFAggressor, 0)