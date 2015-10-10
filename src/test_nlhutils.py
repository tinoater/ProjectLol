import unittest

import nlhutils
import cardutils
import constants as c

class AAsPFTestCase(unittest.TestCase):
    """
    Tests for AA Game class in cardutils.py
    """
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000,[])
        playerBB = cardutils.Player(2,"playerBB",100000,[])
        playerCO = cardutils.Player(8,"playerCO",100000,[])
        playerHero = cardutils.Player(9,"hero",10000,[])
        self.game = nlhutils.Game(herohand,[playerSB, playerBB, playerCO, playerHero])
        self.game.players[0].updatePlayerbHist(0,c.BETSTRING_SB)
        self.game.players[1].updatePlayerbHist(0,c.BETSTRING_BB)
        self.game.players[2].updatePlayerbHist(0,c.BETSTRING_RAISE)
        self.game.setHeroPosition()
        self.game.setHeroPlayer("hero")
        self.game.updateNumPlayers()
        self.game.currBet = 10
        self.currbet0 = 10
        self.potamount0 = 13
        self.game.potAmount = 13
        self.game.HeroCash = self.game.players[self.game.heroPlayer].cash
        (self.action1, self.amount1, self.wait1, self.logstring1) = self.game.bet()

        self.game.players[0].updatePlayerbHist(0, c.BETSTRING_FOLD)
        self.game.players[1].updatePlayerbHist(0, c.BETSTRING_FOLD)
        self.game.players[2].updatePlayerbHist(0, c.BETSTRING_RAISE)
        self.game.currBet = 50
        self.currbet1 = 50
        self.game.potAmount = 13 + 2*self.amount1 + 50
        (self.action2, self.amount2, self.wait2, self.logstring2) = self.game.bet()

        self.game.players[2].updatePlayerbHist(0, c.BETSTRING_RAISE)
        self.game.currBet = 200
        self.currbet2 = 200
        self.game.potAmount = 13 + 2*self.amount1 + 2*self.amount2 + 200
        (self.action3, self.amount3, self.wait3, self.logstring3) = self.game.bet()

        self.game.players[2].updatePlayerbHist(0, c.BETSTRING_RAISE)
        self.game.currBet = 2000000
        self.currbet3 = 2000000
        self.game.potAmount = 13 + 2*self.amount1 + 2*self.amount2 + 2*self.amount3 + 2000000
        (self.action4, self.amount4, self.wait4, self.logstring4) = self.game.bet()

    def test_initnumplayers(self):
        self.assertEqual(self.game.initNumPlayers, 4)

    def test_BHInd(self):
        self.assertEqual(self.game.BHInd, 1)

    def test_updateNumPlayers(self):
        self.assertEqual(self.game.numPlayers, 4)

    def test_heroposition(self):
        self.assertEqual(self.game.position, 4)
        self.assertEqual(self.game.players[3].seat, 9)

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
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000,[])
        playerBB = cardutils.Player(2,"playerBB",100000,[])
        playerCO = cardutils.Player(8,"playerCO",100000,[])
        playerHero = cardutils.Player(9,"hero",10000,[])
        self.game = nlhutils.Game(herohand,[playerSB, playerBB, playerCO, playerHero], heroName="hero")
        self.game.players[0].updatePlayerbHist(0,c.BETSTRING_SB)
        self.game.players[1].updatePlayerbHist(0,c.BETSTRING_BB)
        self.game.players[2].updatePlayerbHist(0,c.BETSTRING_RAISE)
        self.game.players[0].updatePlayerbHist(0,c.BETSTRING_FOLD)
        self.game.players[1].updatePlayerbHist(0,c.BETSTRING_CALL)
        self.game.street += 1
        self.game.setHeroPosition()
        self.game.updateNumPlayers()
        self.game.setAggressorInds()

        self.game2 = nlhutils.Game(herohand,[playerSB, playerBB, playerCO, playerHero], heroName="hero")
        self.game2.players[0].updatePlayerbHist(0,c.BETSTRING_SB)
        self.game2.players[1].updatePlayerbHist(0,c.BETSTRING_BB)
        self.game2.players[2].updatePlayerbHist(0,c.BETSTRING_CALL)
        self.game2.players[3].updatePlayerbHist(0,c.BETSTRING_RAISE)
        self.game2.players[0].updatePlayerbHist(0,c.BETSTRING_FOLD)
        self.game2.players[1].updatePlayerbHist(0,c.BETSTRING_FOLD)
        self.game2.players[2].updatePlayerbHist(0,c.BETSTRING_CALL)
        self.game2.street += 1
        self.game2.setHeroPosition()
        self.game2.updateNumPlayers()
        self.game2.setAggressorInds()

        self.game3 = nlhutils.Game(herohand,[playerSB, playerBB, playerCO, playerHero], heroName="hero")
        self.game3.players[0].updatePlayerbHist(0,c.BETSTRING_SB)
        self.game3.players[1].updatePlayerbHist(0,c.BETSTRING_BB)
        self.game3.players[2].updatePlayerbHist(0,c.BETSTRING_RAISE)
        self.game3.players[0].updatePlayerbHist(0,c.BETSTRING_RAISE)
        self.game3.players[1].updatePlayerbHist(0,c.BETSTRING_FOLD)
        self.game3.players[2].updatePlayerbHist(0,c.BETSTRING_CALL)
        self.game3.street += 1
        self.game3.setHeroPosition()
        self.game3.updateNumPlayers()
        self.game3.setAggressorInds()

    def test_simplePreFlopIndsTest(self):
        self.assertEqual(self.game.PFAggressor, 2)

    def test_simpleHeroPreFlopIndsTest(self):
        self.assertEqual(self.game2.PFAggressor, -1)

    def test_reraiseHeroPreFlopIndsTest(self):
        self.assertEqual(self.game3.PFAggressor, 0)

class HeroNameTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000,[])
        playerBB = cardutils.Player(2,"playerBB",100000,[])
        playerCO = cardutils.Player(8,"playerCO",100000,[])
        playerHero = cardutils.Player(9,"hero",10000,[])
        self.game = nlhutils.Game(herohand,[playerSB, playerBB, playerCO, playerHero],heroName="hero")

    def test_heroPlayer(self):
        self.assertEqual(self.game.heroPlayer, 3)