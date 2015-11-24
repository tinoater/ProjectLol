import unittest

import nlhutils
import cardutils
import constants as c

# --------------------------------
# Test Cases for the Game function
# --------------------------------
class SetHeroPlayerTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerCO = cardutils.Player(8,"playerCO",100000)
        playerHero = cardutils.Player(9,"hero",10000)
        self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])

    def tearDown(self):
        self.game = None

    def test_heroPlayer(self):
        self.assertEqual(self.game.heroPlayer, 3)

    def test_heroCash(self):
        self.assertEqual(self.game.heroCash, 10000)


class SetHeroPositionTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        player3 = cardutils.Player(3,"player3",100000)
        player4 = cardutils.Player(4,"player4",100000)
        player5 = cardutils.Player(5,"player5",100000)
        player6 = cardutils.Player(6,"player6",100000)
        player7 = cardutils.Player(7,"player7",100000)
        playerCO = cardutils.Player(8,"playerCO",100000)
        playerBU = cardutils.Player(9,"playerBU",100000)
        playerSB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        playerBB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])

        self.game = nlhutils.Game("playerSB", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game2 = nlhutils.Game("playerBB", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game3 = nlhutils.Game("player3", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game4 = nlhutils.Game("player4", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game5 = nlhutils.Game("player5", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game6 = nlhutils.Game("player6", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game7 = nlhutils.Game("player7", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game8 = nlhutils.Game("playerCO", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game9 = nlhutils.Game("playerBU", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])

        # Tests for the SB not in seat 1
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(7,"playerSB",100000)
        playerBB = cardutils.Player(8,"playerBB",100000)
        player3 = cardutils.Player(9,"player3",100000)
        player4 = cardutils.Player(1,"player4",100000)
        player5 = cardutils.Player(2,"player5",100000)
        player6 = cardutils.Player(3,"player6",100000)
        player7 = cardutils.Player(4,"player7",100000)
        playerCO = cardutils.Player(5,"playerCO",100000)
        playerBU = cardutils.Player(6,"playerBU",100000)
        playerSB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        playerBB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])

        self.game10 = nlhutils.Game("playerSB", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game11 = nlhutils.Game("playerBB", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game12 = nlhutils.Game("player3", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game13 = nlhutils.Game("player4", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game14 = nlhutils.Game("player5", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game15 = nlhutils.Game("player6", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game16 = nlhutils.Game("player7", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game17 = nlhutils.Game("playerCO", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])
        self.game18 = nlhutils.Game("playerBU", herohand,[playerSB, playerBB, player3, player4, player5, player6 ,player7,
                                                    playerCO, playerBU])

    def tearDown(self):
        self.game = None
        self.game2 = None
        self.game3 = None
        self.game4 = None
        self.game5 = None
        self.game6 = None
        self.game7 = None
        self.game8 = None
        self.game9 = None

        self.game10 = None
        self.game11 = None
        self.game12 = None
        self.game13 = None
        self.game14 = None
        self.game15 = None
        self.game16 = None
        self.game17 = None
        self.game18 = None

    def test_SetHeroPosition_FullTable_SB(self):
        self.assertEqual(self.game.position, 1)

    def test_SetHeroPosition_FullTable_BB(self):
        self.assertEqual(self.game2.position, 2)

    def test_SetHeroPosition_FullTable_3(self):
        self.assertEqual(self.game3.position, 3)

    def test_SetHeroPosition_FullTable_4(self):
        self.assertEqual(self.game4.position, 4)

    def test_SetHeroPosition_FullTable_5(self):
        self.assertEqual(self.game5.position, 5)

    def test_SetHeroPosition_FullTable_6(self):
        self.assertEqual(self.game6.position, 6)

    def test_SetHeroPosition_FullTable_7(self):
        self.assertEqual(self.game7.position, 7)

    def test_SetHeroPosition_FullTable_CO(self):
        self.assertEqual(self.game8.position, 8)

    def test_SetHeroPosition_FullTable_BU(self):
        self.assertEqual(self.game9.position, 9)

    def test_SetHeroPosition_FullTable_Shifted_SB(self):
        self.assertEqual(self.game10.position, 1)

    def test_SetHeroPosition_FullTable_Shifted_BB(self):
        self.assertEqual(self.game11.position, 2)

    def test_SetHeroPosition_FullTable_Shifted_3(self):
        self.assertEqual(self.game12.position, 3)

    def test_SetHeroPosition_FullTable_Shifted_4(self):
        self.assertEqual(self.game13.position, 4)

    def test_SetHeroPosition_FullTable_Shifted_5(self):
        self.assertEqual(self.game14.position, 5)

    def test_SetHeroPosition_FullTable_Shifted_6(self):
        self.assertEqual(self.game15.position, 6)

    def test_SetHeroPosition_FullTable_Shifted_7(self):
        self.assertEqual(self.game16.position, 7)

    def test_SetHeroPosition_FullTable_Shifted_CO(self):
        self.assertEqual(self.game17.position, 8)

    def test_SetHeroPosition_FullTable_Shifted_BU(self):
        self.assertEqual(self.game18.position, 9)


class GetUnMovedPlayersTestCase(unittest.TestCase):
    def setUp(self):
        # Button
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerCO = cardutils.Player(8,"playerCO",100000)
        playerHero = cardutils.Player(9,"hero",10000)
        self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])

        self.game.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        self.game.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
        self.game.players[2].updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])

        self.game.setHeroPosition()
        self.unMovedPlayers1 = self.game.getUnMovedPlayers()

        self.game.players[3].updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
        self.game.players[0].updatePlayerbHist(0, cardutils.BETSTRING_DICT['CALL'])
        self.game.players[1].updatePlayerbHist(0, cardutils.BETSTRING_DICT['CALL'])
        self.game.street += 1

        self.game.players[0].updatePlayerbHist(1,cardutils.BETSTRING_DICT['RAISE'])
        self.game.players[1].updatePlayerbHist(1,cardutils.BETSTRING_DICT['FOLD'])
        self.game.players[2].updatePlayerbHist(1,cardutils.BETSTRING_DICT['CALL'])
        self.unMovedPlayers2 = self.game.getUnMovedPlayers()

        # SB
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        heroSB = cardutils.Player(1,"hero",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerCO = cardutils.Player(8,"playerCO",100000)
        self.game2 = nlhutils.Game("hero", herohand,[heroSB, playerBB, playerCO])

        self.game2.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        self.game2.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
        self.game2.players[2].updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])

        self.game2.setHeroPosition()
        self.unMovedPlayers3 = self.game2.getUnMovedPlayers()

        self.game2.players[0].updatePlayerbHist(0, cardutils.BETSTRING_DICT['CALL'])
        self.game2.players[1].updatePlayerbHist(0, cardutils.BETSTRING_DICT['CALL'])
        self.game2.street += 1

        self.unMovedPlayers4 = self.game2.getUnMovedPlayers()

        # BB
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        heroBB = cardutils.Player(2,"hero",100000)
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerCO = cardutils.Player(8,"playerCO",100000)
        self.game3 = nlhutils.Game("hero", herohand,[heroBB, playerSB, playerCO])

        self.game3.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
        self.game3.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        self.game3.players[2].updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])

        self.game3.setHeroPosition()
        self.unMovedPlayers5 = self.game3.getUnMovedPlayers()

        self.game3.players[0].updatePlayerbHist(0, cardutils.BETSTRING_DICT['CALL'])
        self.game3.players[1].updatePlayerbHist(0, cardutils.BETSTRING_DICT['CALL'])
        self.game3.street += 1

        self.game3.players[1].updatePlayerbHist(1, cardutils.BETSTRING_DICT['RAISE'])
        self.unMovedPlayers6 = self.game3.getUnMovedPlayers()

    def tearDown(self):
        self.game = None
        self.game2 = None
        self.game3 = None
        self.unMovedPlayers1 = None
        self.unMovedPlayers2 = None
        self.unMovedPlayers3 = None
        self.unMovedPlayers4 = None
        self.unMovedPlayers5 = None
        self.unMovedPlayers6 = None

    def test_GetUnMovedPlayers_PreFlop_Include_Blinds(self):
        self.assertEqual(self.unMovedPlayers1, 2)

    def test_GetUnMovedPlayers_Flop(self):
        self.assertEqual(self.unMovedPlayers2, 0)

    def test_GetUnMovedPlayers_PreFlop_SB(self):
        self.assertEqual(self.unMovedPlayers3, 1)

    def test_GetUnMovedPlayers_Flop_SB(self):
        self.assertEqual(self.unMovedPlayers4, 2)

    def test_GetUnMovedPlayers_PreFlop_BB(self):
        self.assertEqual(self.unMovedPlayers5, 0)

    def test_GetUnMovedPlayers_Flop_BB(self):
        self.assertEqual(self.unMovedPlayers6, 1)


class SetAggressorIndsPreFlopTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerCO = cardutils.Player(8,"playerCO",100000)
        playerHero = cardutils.Player(9,"hero",10000)

        playerSB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        playerBB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
        playerCO.updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
        playerHero.updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
        playerSB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
        playerBB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
        playerCO.updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])

        self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])
        self.game.street += 1
        self.game.setAggressorInds()

    def tearDown(self):
        self.game = None

    def test_SetAgressorInds_PreFlop_PFAgressor(self):
        self.assertEqual(self.game.aggressor[0], -1)

    def test_SetAgressorInds_PreFlop_PFAggresActed(self):
        self.assertEqual(self.game.aggresActed[0], 0)


class SetAggressorIndsFlopTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerCO = cardutils.Player(8,"playerCO",100000)
        playerHero = cardutils.Player(9,"hero",10000)

        playerSB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        playerBB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
        playerCO.updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
        playerHero.updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
        playerSB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
        playerBB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
        playerCO.updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])

        self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])

        self.game.street += 1
        self.game.setAggressorInds()

        self.game.players[0].updatePlayerbHist(1,cardutils.BETSTRING_DICT['CALL'])
        self.game.players[1].updatePlayerbHist(1,cardutils.BETSTRING_DICT['RAISE'])
        self.game.players[2].updatePlayerbHist(1,cardutils.BETSTRING_DICT['FOLD'])
        self.game.players[3].updatePlayerbHist(1,cardutils.BETSTRING_DICT['CALL'])
        self.game.players[0].updatePlayerbHist(1,cardutils.BETSTRING_DICT['CALL'])

        self.game.street += 1
        self.game.setAggressorInds()

    def tearDown(self):
        self.game = None

    def test_SetAgressorInds_Flop_PFAgressor(self):
        self.assertEqual(self.game.aggressor[0], -1)

    def test_SetAgressorInds_Flop_PFAggresActed(self):
        self.assertEqual(self.game.aggresActed[0], 0)

    def test_SetAgressorInds_Flop_FLAgressor(self):
        self.assertEqual(self.game.aggressor[1], 1)

    def test_SetAgressorInds_Flop_FLAggresActed(self):
        self.assertEqual(self.game.aggresActed[1], 1)


class SetAggressorIndsTurnTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerCO = cardutils.Player(8,"playerCO",100000)
        playerHero = cardutils.Player(9,"hero",10000)

        playerSB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        playerBB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
        playerCO.updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
        playerHero.updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
        playerSB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
        playerBB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
        playerCO.updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])

        self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])

        self.game.street += 1
        self.game.setAggressorInds()

        self.game.players[0].updatePlayerbHist(1,cardutils.BETSTRING_DICT['CALL'])
        self.game.players[1].updatePlayerbHist(1,cardutils.BETSTRING_DICT['RAISE'])
        self.game.players[2].updatePlayerbHist(1,cardutils.BETSTRING_DICT['FOLD'])
        self.game.players[3].updatePlayerbHist(1,cardutils.BETSTRING_DICT['CALL'])
        self.game.players[0].updatePlayerbHist(1,cardutils.BETSTRING_DICT['CALL'])

        self.game.street += 1
        self.game.setAggressorInds()

        self.game.players[0].updatePlayerbHist(2,cardutils.BETSTRING_DICT['CALL'])
        self.game.players[1].updatePlayerbHist(2,cardutils.BETSTRING_DICT['CALL'])
        self.game.players[2].updatePlayerbHist(2,cardutils.BETSTRING_DICT['CALL'])
        self.game.players[3].updatePlayerbHist(2,cardutils.BETSTRING_DICT['RAISE'])

        self.game.street += 1
        self.game.setAggressorInds()

    def tearDown(self):
        self.game = None

    def test_SetAggressorInds_Flop_PFAgressor(self):
        self.assertEqual(self.game.aggressor[0], -1)

    def test_SetAggressorInds_Flop_PFAggresActed(self):
        self.assertEqual(self.game.aggresActed[0], 0)

    def test_SetAggressorInds_Flop_FLAgressor(self):
        self.assertEqual(self.game.aggressor[1], 1)

    def test_SetAggressorInds_Flop_FLAggresActed(self):
        self.assertEqual(self.game.aggresActed[1], 1)

    def test_SetAggressorInds_Turn_TAggressor(self):
        self.assertEqual(self.game.aggressor[2], -1)

    def test_SetAggressorInds_Turn_TAggresActed(self):
        self.assertEqual(self.game.aggresActed[2], 0)


class SetPotOddsTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerCO = cardutils.Player(8,"playerCO",100000)
        playerHero = cardutils.Player(9,"hero",10000)

        playerSB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        playerBB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
        playerCO.updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])

        self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])
        self.game.currBet = 100
        self.game.potAmount = 100
        self.game.setPotOdds()

    def tearDown(self):
        self.game = None

    def test_PotOdds_Simple(self):
        self.assertEqual(self.game.potOdds, 0.5)


class UpdateHeroBettingTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerCO = cardutils.Player(8,"playerCO",100000)
        playerHero = cardutils.Player(9,"hero",10000)

        playerSB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        playerBB.updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
        playerCO.updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])

        self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])
        self.game2 = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])
        self.game.potAmount = 45
        self.game.currBet = 30
        self.game.updateHeroBetting(cardutils.BETSTRING_DICT['CALL'], self.game.currBet)

        self.game2.potAmount = 45
        self.game2.currBet = 30
        self.game2.updateHeroBetting(cardutils.BETSTRING_DICT['RAISE'], self.game.currBet * 2)

    def tearDown(self):
        self.game = None
        self.game2 = None

    def test_UpdateHeroBetting_Call_TotalHandBet(self):
        self.assertEqual(self.game.totalHandBet, 30)

    def test_UpdateHeroBetting_Call_HeroCash(self):
        self.assertEqual(self.game.heroCash, 9970)

    def test_UpdateHeroBetting_Call_bHist(self):
        self.assertEqual(self.game.players[self.game.heroPlayer].bHist[0], [cardutils.BETSTRING_DICT['CALL']])

    def test_UpdateHeroBetting_Raise_TotalHandBet(self):
        self.assertEqual(self.game2.totalHandBet, 60)

    def test_UpdateHeroBetting_Raise_HeroCash(self):
        self.assertEqual(self.game2.heroCash, 9940)

    def test_UpdateHeroBetting_Raise_bHist(self):
        self.assertEqual(self.game2.players[self.game2.heroPlayer].bHist[0], [cardutils.BETSTRING_DICT['RAISE']])


class AnalyseBoardMovedPlayersTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerCO = cardutils.Player(8,"playerCO",100000)
        playerHero = cardutils.Player(9,"hero",10000)

        self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])
        self.game2 = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])

        self.game.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        self.game.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
        self.game.players[2].updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])

        self.game2.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
        self.game2.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
        self.game2.players[2].updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])

        self.game.analyseBoard()
        self.game2.analyseBoard()

    def tearDown(self):
        self.game = None
        self.game2 = None

    def test_AnalyseBoard_MovedPlayers(self):
        self.assertEqual(self.game.movedPlayers, 1)

    def test_AnalyseBoard_UnmovedPlayers(self):
        self.assertEqual(self.game.unmovedPlayers, 2)

    def test_AnalyseBoard_CheckedInd(self):
        self.assertEqual(self.game.checkedPot, 1)

    def test_AnalyseBoard_CheckedInd_2(self):
        self.assertEqual(self.game2.checkedPot, 0)


class AnalyseBoardFlushDrawTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(13,1)])
        herohand2 = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(13,3)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerHero = cardutils.Player(9,"hero",10000)

        self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerHero])
        self.game2 = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerHero])
        self.game3 = nlhutils.Game("hero", herohand2,[playerSB, playerBB, playerHero])
        self.game.hand.addSharedCards([cardutils.Card(12,1), cardutils.Card(7,1), cardutils.Card(9,3)])
        self.game2.hand.addSharedCards([cardutils.Card(12,1), cardutils.Card(7,3), cardutils.Card(9,3)])
        self.game3.hand.addSharedCards([cardutils.Card(12,1), cardutils.Card(7,1), cardutils.Card(9,1)])

        self.game.hand.postFlopOdds = 0
        self.game2.hand.postFlopOdds = 0
        self.game3.hand.postFlopOdds = 0
        self.game.street += 1
        self.game2.street += 1
        self.game3.street += 1

        self.game.analyseBoard()
        self.game2.analyseBoard()
        self.game3.analyseBoard()

    def tearDown(self):
        self.game = None
        self.game2 = None
        self.game3 = None

    def test_AnalyseBoard_DrawInd_Flush(self):
        self.assertEqual(self.game.drawInd, 1)

    def test_AnalyseBoard_DrawInd_Flush_NotFlush(self):
        self.assertEqual(self.game2.drawInd, 0)

    def test_AnalyseBoard_DrawInd_Flush_1HoleCard(self):
        self.assertEqual(self.game3.drawInd, 1, "This should pass, 1 card to flush in new variable" )


class AnalyseBoardStraightDrawTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(8,4), cardutils.Card(7,4)])
        herohand2 = cardutils.Hand([cardutils.Card(11,4), cardutils.Card(2,4)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerHero = cardutils.Player(9,"hero",10000)

        self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerHero])
        self.game2 = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerHero])
        self.game3 = nlhutils.Game("hero", herohand2,[playerSB, playerBB, playerHero])
        self.game.hand.addSharedCards([cardutils.Card(6,1), cardutils.Card(9,1), cardutils.Card(9,3)])
        self.game2.hand.addSharedCards([cardutils.Card(9,1), cardutils.Card(3,3), cardutils.Card(9,3)])
        self.game3.hand.addSharedCards([cardutils.Card(9,1), cardutils.Card(10,3), cardutils.Card(7,3)])

        self.game.hand.postFlopOdds = 0
        self.game2.hand.postFlopOdds = 0
        self.game3.hand.postFlopOdds = 0
        self.game.street += 1
        self.game2.street += 1
        self.game3.street += 1

        self.game.analyseBoard()
        self.game2.analyseBoard()
        self.game3.analyseBoard()

    def tearDown(self):
        self.game = None
        self.game2 = None
        self.game3 = None

    def test_AnalyseBoard_DrawInd_Straight(self):
        self.assertEqual(self.game.drawInd, 1)

    def test_AnalyseBoard_DrawInd_Straight_NotStraight(self):
        self.assertEqual(self.game2.drawInd, 0)

    def test_AnalyseBoard_DrawInd_Straight_1HoleCard(self):
        self.assertEqual(self.game3.drawInd, 1, "This should pass, 1 card to straight in new variable" )

    def test_AnalyseBoard_DrawStraightOdds_2WayStraight(self):
        self.assertEqual(self.game.drawStraightOdds, 0.16)

    def test_AnalyseBoard_DrawStraightOdds_1CardStraight(self):
        self.assertEqual(self.game3.drawStraightOdds, 0.08, "This should give 0.08 as only 1 card")


class AnalyseBoardDrawPresentTestCase(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(13,4), cardutils.Card(12,4)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        playerHero = cardutils.Player(9,"hero",10000)

        self.game_flushdrawpresent = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerHero])
        self.game_straightdrawpresent = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerHero])
        self.game_3cardflushflop = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerHero])
        self.game_nodrawpresent = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerHero])
        self.game_flushdrawpresent.hand.addSharedCards([cardutils.Card(6,1), cardutils.Card(9,1), cardutils.Card(9,3)])
        self.game_straightdrawpresent.hand.addSharedCards([cardutils.Card(9,1), cardutils.Card(8,3), cardutils.Card(7,3)])
        self.game_3cardflushflop.hand.addSharedCards([cardutils.Card(9,1), cardutils.Card(10,1), cardutils.Card(7,1)])
        self.game_nodrawpresent.hand.addSharedCards([cardutils.Card(9,2), cardutils.Card(10,3), cardutils.Card(7,1)])

        self.game_flushdrawpresent.hand.postFlopOdds = 0
        self.game_straightdrawpresent.hand.postFlopOdds = 0
        self.game_3cardflushflop.hand.postFlopOdds = 0
        self.game_nodrawpresent.hand.postFlopOdds = 0
        self.game_flushdrawpresent.street += 1
        self.game_straightdrawpresent.street += 1
        self.game_3cardflushflop.street += 1
        self.game_nodrawpresent.street += 1

        self.game_flushdrawpresent.analyseBoard()
        self.game_straightdrawpresent.analyseBoard()
        self.game_3cardflushflop.analyseBoard()
        self.game_nodrawpresent.analyseBoard()

    def tearDown(self):
        self.game_flushdrawpresent = None
        self.game_straightdrawpresent = None
        self.game_3cardflushflop = None
        self.game_nodrawpresent = None

    def test_AnalyseBoard_FlushDrawPresent(self):
        self.assertEqual(self.game_flushdrawpresent.drawPresentInd, 1)

    def test_AnalyseBoard_StraightDrawPresent(self):
        self.assertEqual(self.game_straightdrawpresent.drawPresentInd, 1)

    def test_AnalyseBoard_3CardFlushDrawPresent(self):
        self.assertEqual(self.game_3cardflushflop.drawPresentInd, 1)

    def test_AnalyseBoard_NoDrawPresent(self):
        self.assertEqual(self.game_nodrawpresent.drawPresentInd, 0)

# ----------------------------
# Test Cases for the functions
# ----------------------------
class PlayOddsHandTestCase(unittest.TestCase):
    def setUp(self):
        self.result = nlhutils.PlayOddsHand(4,[cardutils.Card(13,1), cardutils.Card(12,1)], [cardutils.Card(11,1),
                                cardutils.Card(10,1), cardutils.Card(14,1)])

    def tearDown(self):
        self.result = None

    def test_PlayOddsHand_CertainWin(self):
        self.assertEqual(self.result, 1)


class GenerateProbabilitiesTestCase(unittest.TestCase):
    def setUp(self):
        self.result = nlhutils.GenerateProbabilities(4,[cardutils.Card(13,1), cardutils.Card(12,1)], [cardutils.Card(11,1),
                                cardutils.Card(10,1), cardutils.Card(14,1)])

    def tearDown(self):
        self.result = None

    def test_GenerateProbabilities_CertainWin(self):
        self.assertGreater(self.result, 99)