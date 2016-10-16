__author__ = 'Ahab'

import unittest
import copy
import nlhutils
import nlhbetting
import cardutils
import mock

# --------------------------------
# Test Cases for betting functions
# --------------------------------
class BettingInitWithGameInstance(unittest.TestCase):
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
        self.game.postFlopOdds = 88.88
        self.bettingstrat = nlhbetting.BettingStrat(gameInstance=self.game)

    def tearDown(self):
        self.game = None
        self.bettingstrat = None

    def test_Betting_Init_Using_GameInstance_Players(self):
        self.assertEqual(len(self.bettingstrat.players), 4)
        self.assertIsInstance(self.bettingstrat.players[1], cardutils.Player)

    def test_Betting_Init_Using_GameInstance_Hand(self):
        self.assertIsInstance(self.bettingstrat.hand, cardutils.Hand)

    def test_Betting_Init_Using_GameInstance_PostFlopOdds(self):
        self.assertEqual(self.bettingstrat.postFlopOdds, 88.88)


class BettingInitWithoutGameInstance(unittest.TestCase):
    def setUp(self):
        herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
        playerSB = cardutils.Player(1,"playerSB",100000)
        playerBB = cardutils.Player(2,"playerBB",100000)
        self.bettingstrat = nlhbetting.BettingStrat()

        self.bettingstrat.hand = copy.deepcopy(herohand)
        self.bettingstrat.players = copy.deepcopy([playerSB, playerBB])
        self.bettingstrat.postFlopOdds = 66.66


    def tearDown(self):
        self.bettingstrat = None

    def test_Betting_Init_NotUsing_GameInstance_Players(self):
        self.assertEqual(len(self.bettingstrat.players), 2)
        self.assertIsInstance(self.bettingstrat.players[1], cardutils.Player)

    def test_Betting_Init_NotUsing_GameInstance_Hand(self):
        self.assertIsInstance(self.bettingstrat.hand, cardutils.Hand)

    def test_Betting_Init_NotUsing_GameInstance_PostFlopOdds(self):
        self.assertEqual(self.bettingstrat.postFlopOdds, 66.66)


class BettingAddLogging(unittest.TestCase):
    def setUp(self):
        self.bettingstrat = nlhbetting.BettingStrat()
        self.bettingstrat.addLogging("New log message")
        self.bettingstrat.addLogging("New error message", 1)
        self.bettingstrat.addLogging("New log message 2", 0)

    def tearDown(self):
        self.bettingstrat = None

    def test_betting_addLogging_error(self):
        self.assertEqual(self.bettingstrat.errorstr, "New error message\n")

    def test_betting_addLogging_log(self):
        self.assertEqual(self.bettingstrat.logstr, "New log message\nNew log message 2\n")


class BettingShouldDraw(unittest.TestCase):
    def setUp(self):
        self.bettingstrat = nlhbetting.BettingStrat()
        self.bettingstrat.drawStraightOdds = 60
        self.bettingstrat.drawFlushOdds = 60
        self.bettingstrat.potOdds = 50

        self.baddraws = nlhbetting.BettingStrat()
        self.baddraws.drawStraightOdds = 40
        self.baddraws.drawFlushOdds = 40
        self.baddraws.potOdds = 50

        self.mixeddraw = nlhbetting.BettingStrat()
        self.mixeddraw.drawStraightOdds = 60
        self.mixeddraw.drawFlushOdds = 40
        self.mixeddraw.potOdds = 50

        self.baddrawresult = self.baddraws.shouldDraw()
        self.gooddrawresult = self.bettingstrat.shouldDraw()
        self.mixeddrawresult = self.mixeddraw.shouldDraw()

    def tearDown(self):
        self.bettingstrat = None
        self.baddraws = None
        self.baddrawresult = None
        self.gooddrawresult = None
        self.mixeddraw = None
        self.mixeddrawresult = None

    def test_betting_shoulddraw_straight(self):
        self.assertEqual(self.gooddrawresult, 1)

    def test_betting_shoulddraw_flush(self):
        self.assertEqual(self.gooddrawresult, 1)

    def test_betting_shoulddraw_straightflush(self):
        self.assertEqual(self.mixeddrawresult, 1)

    def test_betting_shouldntdraw_straight(self):
        self.assertEqual(self.baddrawresult, 0)

    def test_betting_shouldntdraw_flush(self):
        self.assertEqual(self.baddrawresult, 0)


class BettingBetOutput(unittest.TestCase):
    def setUp(self):
        self.strat = nlhbetting.BettingStrat()
        self.strat.heroCash = 100
        self.strat.currBet = 20

        self.foldaction, self.foldbet = self.strat.betOutput(0)
        self.callaction, self.callbet = self.strat.betOutput(1)
        self.raiseaction, self.raisebet = self.strat.betOutput(2, 40)
        self.raiseallinaction, self.raiseallinbet = self.strat.betOutput(2, 120)
        self.roundtoallinaction, self.roundtoallinbet = self.strat.betOutput(2,99)
        self.allinaction, self.allinbet = self.strat.betOutput(3, 0)

    def tearDown(self):
        self.strat = None
        self.foldaction, self.foldbet = None, None
        self.callaction, self.callbet = None, None
        self.raiseaction, self.raisebet = None, None
        self.raiseallinaction, self.raiseallinbet = None, None
        self.roundtoallinaction, self.roundtoallinbet = None, None
        self.allinaction, self.allinbet = None, None

    def test_betting_betoutput_fold(self):
        self.assertEqual(self.foldaction, 0)
        self.assertEqual(self.foldbet, 0)

    def test_betting_betoutput_call(self):
        self.assertEqual(self.callaction, 1)
        self.assertEqual(self.callbet, 20)

    def test_betting_betoutput_raise(self):
        self.assertEqual(self.raiseaction, 2)
        self.assertEqual(self.raisebet, 40)

    def test_betting_betoutput_round_to_allin(self):
        self.assertEqual(self.roundtoallinaction, 3)
        self.assertEqual(self.roundtoallinbet, 0)

    def test_betting_betouput_raise_to_allin(self):
        self.assertEqual(self.raiseallinaction, 3)
        self.assertEqual(self.raiseallinbet, 0)

    def test_betting_betoutput_allin(self):
        self.assertEqual(self.allinaction, 3)
        self.assertEqual(self.allinbet, 0)


class BettingBHPreFlop(unittest.TestCase):
    def setUp(self):
        self.strat = nlhbetting.BettingStrat()
        self.strat.currBet = 10

    def tearDown(self):
        self.strat = None

    @mock.patch('random.uniform')
    def test_betting_BH_PF(self, random_call):
        random_call.return_value = 2
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet0()
        self.strat.betOutput.assert_called_with(2, 20)


class BettingBHFlop(unittest.TestCase):
    def setUp(self):
        self.strat = nlhbetting.BettingStrat()
        self.strat.currBet = 10
        self.strat.potAmount = 20
        self.postFlopOdds = 0
        self.strat.streetCount = 0
        self.strat.street = 1

    def tearDown(self):
        self.strat = None

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_PFaggressor_CheckedPot(self, random_call):
        random_call.return_value = 0.5
        self.strat.aggressor[0] = -1
        self.strat.checkedPot = 1
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 10)

    @mock.patch('random.uniform')
    @mock.patch('constants.BH_RERAISE',[100, 100, 100])
    def test_betting_BH_Flop_PFaggressor_UnCheckedPot_Raise(self, random_call):
        random_call.return_value = 2
        self.strat.aggressor[0] = -1
        self.strat.checkedPot = 0
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 20)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_PFaggressor_UnCheckedPot_Call(self, random_call):
        random_call.return_value = 2
        self.strat.aggressor[0] = -1
        self.strat.checkedPot = 0
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 10)

    @mock.patch('random.uniform')
    @mock.patch('constants.BH_RERAISE',[100, 100, 100])
    def test_betting_BH_Flop_Not_PFaggressor_PFAggressNotActed_UnCheckedPot_Raise(self, random_call):
        random_call.return_value = 2
        self.strat.aggressor[0] = 5
        self.strat.checkedPot = 0
        self.strat.aggresActed[0] = 0
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 20)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFaggressor_PFAggressNotActed_UnCheckedPot_Call(self, random_call):
        random_call.return_value = 1
        self.strat.aggressor[0] = 5
        self.strat.checkedPot = 0
        self.strat.aggresActed[0] = 0
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 10)

    def test_betting_BH_Flop_Not_PFaggressor_PFAggressNotActed_CheckedPot(self):
        self.strat.aggressor[0] = 5
        self.strat.checkedPot = 1
        self.strat.aggresActed[0] = 0
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 10)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Fold_CheckedPot(self, random_call):
        self.strat.aggressor[0] = 5
        self.strat.aggresActed[0] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['FOLD']
        self.strat.checkedPot = 1
        random_call.return_value = 0.5
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 10)

    @mock.patch('random.uniform')
    @mock.patch('constants.BH_RERAISE',[100, 100, 100])
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Fold_UnCheckedPot_Raise(self, random_call):
        self.strat.aggressor[0] = 5
        self.strat.aggresActed[0] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['FOLD']
        self.strat.checkedPot = 0
        random_call.return_value = 2
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 20)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Fold_UnCheckedPot_Call(self, random_call):
        self.strat.aggressor[0] = 5
        self.strat.aggresActed[0] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['FOLD']
        self.strat.checkedPot = 0
        random_call.return_value = 1
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 10)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Check(self, random_call):
        self.strat.aggressor[0] = 5
        self.strat.aggresActed[0] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['CALL']
        self.strat.checkedPot = 1
        random_call.return_value = 0.5
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 10)

    @mock.patch('random.uniform')
    @mock.patch('constants.BH_RERAISE',[100, 100, 100])
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Call_Reraise(self, random_call):
        self.strat.aggressor[0] = 5
        self.strat.aggresActed[0] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['CALL']
        self.strat.checkedPot = 0
        random_call.return_value = 2
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 20)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Call_Call(self, random_call):
        self.strat.aggressor[0] = 5
        self.strat.aggresActed[0] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['CALL']
        self.strat.checkedPot = 0
        random_call.return_value = 1
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 10)

    @mock.patch('random.uniform')
    @mock.patch('constants.BH_RERAISE',[100, 100, 100])
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Raise_Reraise(self, random_call):
        self.strat.aggressor[0] = 5
        self.strat.aggresActed[0] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['RAISE']
        self.strat.checkedPot = 0
        random_call.return_value = 2
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 20)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Raise_Call(self, random_call):
        self.strat.aggressor[0] = 5
        self.strat.aggresActed[0] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['RAISE']
        self.strat.checkedPot = 0
        random_call.return_value = 1
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 10)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_FurtherStreet(self, random_call):
        self.strat.streetCount += 1
        random_call.return_value = 3
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 30)


class BettingBHTurn(unittest.TestCase):
    def setUp(self):
        self.strat = nlhbetting.BettingStrat()
        self.strat.currBet = 25
        self.strat.potAmount = 50
        self.strat.postFlopOdds = 0
        self.strat.streetCount = 0
        self.strat.street = 2

    def tearDown(self):
        self.strat = None

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_PFaggressor_CheckedPot(self, random_call):
        random_call.return_value = 0.5
        self.strat.aggressor[1] = -1
        self.strat.checkedPot = 1
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 25)

    @mock.patch('random.uniform')
    @mock.patch('constants.BH_RERAISE',[100, 100, 100])
    def test_betting_BH_Flop_PFaggressor_UnCheckedPot_Raise(self, random_call):
        random_call.return_value = 2
        self.strat.aggressor[1] = -1
        self.strat.checkedPot = 0
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 50)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_PFaggressor_UnCheckedPot_Call(self, random_call):
        random_call.return_value = 2
        self.strat.aggressor[1] = -1
        self.strat.checkedPot = 0
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 25)

    @mock.patch('random.uniform')
    @mock.patch('constants.BH_RERAISE',[100, 100, 100])
    def test_betting_BH_Flop_Not_PFaggressor_PFAggressNotActed_UnCheckedPot_Raise(self, random_call):
        random_call.return_value = 2
        self.strat.aggressor[1] = 5
        self.strat.checkedPot = 0
        self.strat.aggresActed[1] = 0
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 50)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFaggressor_PFAggressNotActed_UnCheckedPot_Call(self, random_call):
        random_call.return_value = 1
        self.strat.aggressor[1] = 5
        self.strat.checkedPot = 0
        self.strat.aggresActed[1] = 0
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 25)

    def test_betting_BH_Flop_Not_PFaggressor_PFAggressNotActed_CheckedPot(self):
        self.strat.aggressor[1] = 5
        self.strat.checkedPot = 1
        self.strat.aggresActed[1] = 0
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 25)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Fold_CheckedPot(self, random_call):
        self.strat.aggressor[1] = 5
        self.strat.aggresActed[1] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['FOLD']
        self.strat.checkedPot = 1
        random_call.return_value = 0.5
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 25)

    @mock.patch('random.uniform')
    @mock.patch('constants.BH_RERAISE',[100, 100, 100])
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Fold_UnCheckedPot_Raise(self, random_call):
        self.strat.aggressor[1] = 5
        self.strat.aggresActed[1] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['FOLD']
        self.strat.checkedPot = 0
        random_call.return_value = 2
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 50)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Fold_UnCheckedPot_Call(self, random_call):
        self.strat.aggressor[1] = 5
        self.strat.aggresActed[1] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['FOLD']
        self.strat.checkedPot = 0
        random_call.return_value = 1
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 25)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Check(self, random_call):
        self.strat.aggressor[1] = 5
        self.strat.aggresActed[1] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['CALL']
        self.strat.checkedPot = 1
        random_call.return_value = 0.5
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 25)

    @mock.patch('random.uniform')
    @mock.patch('constants.BH_RERAISE',[100, 100, 100])
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Call_Reraise(self, random_call):
        self.strat.aggressor[1] = 5
        self.strat.aggresActed[1] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['CALL']
        self.strat.checkedPot = 0
        random_call.return_value = 2
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 50)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Call_Call(self, random_call):
        self.strat.aggressor[1] = 5
        self.strat.aggresActed[1] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['CALL']
        self.strat.checkedPot = 0
        random_call.return_value = 1
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 25)

    @mock.patch('random.uniform')
    @mock.patch('constants.BH_RERAISE',[100, 100, 100])
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Raise_Reraise(self, random_call):
        self.strat.aggressor[1] = 5
        self.strat.aggresActed[1] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['RAISE']
        self.strat.checkedPot = 0
        random_call.return_value = 2
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 50)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_Not_PFagressor_PFAggresActed_Raise_Call(self, random_call):
        self.strat.aggressor[1] = 5
        self.strat.aggresActed[1] = 1
        self.strat.aggressorAction = cardutils.BETSTRING_DICT['RAISE']
        self.strat.checkedPot = 0
        random_call.return_value = 1
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(1, 25)

    @mock.patch('random.uniform')
    def test_betting_BH_Flop_FurtherStreet(self, random_call):
        self.strat.streetCount += 1
        random_call.return_value = 3
        self.strat.betOutput = mock.MagicMock()
        self.strat.betBHStreet1()
        self.strat.betOutput.assert_called_with(2, 75)


class BettingPPPreFlop(unittest.TestCase):
    def setUp(self):
        self.strat = nlhbetting.BettingStrat()
        self.strat.currBet = 10
        self.strat.potAmount = 20
        self.strat.postFlopOdds = 0
        self.strat.streetCount = 0
        self.strat.street = 0
        self.strat.hand = cardutils.Hand([cardutils.Card(9,1), cardutils.Card(9,2)])

    def tearDown(self):
        self.strat = None

    @mock.patch('random.uniform')
    def test_betting_PP_PF_Unmoved_BigPair(self, random_call):
        self.strat.movedPlayers = 0
        random_call.return_value = 2
        self.strat.hand.PPCard = 9
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPPStreet0()
        self.strat.betOutput.assert_called_with(2, 4)

    @mock.patch('random.uniform')
    @mock.patch('constants.PF_PP_BELOW_9_RAISE', 5)
    def test_betting_PP_PF_Unmoved_SmallPair_Raise(self, random_call):
        self.strat.movedPlayers = 0
        random_call.return_value = 2
        self.strat.hand.PPCard = 8
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPPStreet0()
        self.strat.betOutput.assert_called_with(2, 4)

    @mock.patch('constants.PF_PP_BELOW_9_RAISE', 0)
    @mock.patch('constants.PF_PP_BELOW_9_CALL', 1)
    def test_betting_PP_PF_Unmoved_SmallPair_Call(self):
        self.strat.movedPlayers = 0
        self.strat.hand.PPCard = 8
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPPStreet0()
        self.strat.betOutput.assert_called_with(1, 10)

    @mock.patch('constants.PF_PP_BELOW_9_RAISE', 0)
    @mock.patch('constants.PF_PP_BELOW_9_CALL', 0)
    def test_betting_PP_PF_Unmoved_SmallPair_Fold(self):
        self.strat.movedPlayers = 0
        self.strat.hand.PPCard = 8
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPPStreet0()
        self.strat.betOutput.assert_called_with(0, 0)

    def test_betting_PP_PF_Moved_CallWorthIt(self):
        self.strat.movedPlayers = 3
        self.strat.unmovedPlayers = 0
        self.strat.hand.PPCard = 8
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPPStreet0()
        self.strat.betOutput.assert_called_with(1, 10)

    def test_betting_PP_PF_Moved_CallNotWorthIt(self):
        self.strat.movedPlayers = 1
        self.strat.unmovedPlayers = 0
        self.strat.hand.PPCard = 8
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPPStreet0()
        self.strat.betOutput.assert_called_with(0, 0)


class BettingPremMadePreFlop(unittest.TestCase):
    def setUp(self):
        self.strat = nlhbetting.BettingStrat()
        self.strat.currBet = 10
        self.strat.potAmount = 20
        self.strat.postFlopOdds = 0
        self.strat.streetCount = 0
        self.strat.street = 0

    def tearDown(self):
        self.strat = None

    @mock.patch('random.uniform')
    def test_betting_PremMade_PF_CheckedPot(self, random_call):
        self.strat.checkedPot = 1
        self.strat.currBet = 2
        random_call.return_value = 2
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPremMadeHandStreet0()
        self.strat.betOutput.assert_called_with(2, 4)

    @mock.patch('random.uniform')
    def test_betting_PremMade_PF_OpenedPot_Small(self, random_call):
        self.strat.checkedPot = 0
        self.strat.currBet = 2
        random_call.return_value = 3
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPremMadeHandStreet0()
        self.strat.betOutput.assert_called_with(2, 6)

    @mock.patch('random.uniform')
    @mock.patch('constants.PF_PREM_RERAISE_PERC',5)
    def test_betting_PremMade_PF_OpenedPot_Large_Raise(self, random_call):
        self.strat.checkedPot = 0
        self.strat.currBet = 10
        random_call.return_value = 3
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPremMadeHandStreet0()
        self.strat.betOutput.assert_called_with(2, 30)

    @mock.patch('random.uniform')
    @mock.patch('constants.PF_PREM_RERAISE_PERC',0)
    def test_betting_PremMade_PF_OpenedPot_Large_Call(self, random_call):
        self.strat.checkedPot = 0
        self.strat.currBet = 10
        random_call.return_value = 3
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPremMadeHandStreet0()
        self.strat.betOutput.assert_called_with(1, 10)


class BettingPremMadeFlop(unittest.TestCase):
    def setUp(self):
        self.strat = nlhbetting.BettingStrat()
        self.strat.currBet = 10
        self.strat.potAmount = 20
        self.strat.postFlopOdds = 0
        self.strat.streetCount = 0
        self.strat.street = 1

    def tearDown(self):
        self.strat = None

    @mock.patch('random.uniform')
    def test_betting_PremMade_PF_CheckedPot(self, random_call):
        self.strat.checkedPot = 1
        self.strat.currBet = 2
        self.strat.potAmount = 20
        random_call.return_value = 0.5
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPremMadeHandStreet1()
        self.strat.betOutput.assert_called_with(2, 10)

    def test_betting_PremMade_PF_OpenedPot(self):
        self.strat.checkedPot = 0
        self.strat.currBet = 8
        self.strat.potAmount = 20
        self.strat.betOutput = mock.MagicMock()
        self.strat.betPremMadeHandStreet0()
        self.strat.betOutput.assert_called_with(1, 8)

class BettingDrawPreFlop(unittest.TestCase):
    def setUp(self):
        self.strat = nlhbetting.BettingStrat()
        self.strat.hand = cardutils.Hand([cardutils.Card(6,1), cardutils.Card(7,1)])
        self.strat.currBet = 10
        self.strat.potAmount = 20
        self.strat.postFlopOdds = 0
        self.strat.streetCount = 0
        self.strat.street = 0

    def tearDown(self):
        self.strat = None

    def test_betting_Draw_PF_StrFlush_CallWorthIt(self):
        self.strat.hand.suitedInd = 1
        self.strat.hand.connectedInd = 1
        self.strat.movedPlayers = 5
        self.strat.unmovedPlayers = 0
        self.strat.potAmount = 80

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(1,10)

    def test_betting_Draw_PF_StrFlush_CallNotWorthIt(self):
        self.strat.hand.suitedInd = 1
        self.strat.hand.connectedInd = 1
        self.strat.movedPlayers = 1
        self.strat.unmovedPlayers = 0
        self.strat.potAmount = 10

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(0,0)

    def test_betting_Draw_PF_Flush_CallWorthIt(self):
        self.strat.hand.suitedInd = 1
        self.strat.hand.connectedInd = 0
        self.strat.movedPlayers = 5
        self.strat.unmovedPlayers = 0
        self.strat.potAmount = 80

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(1,10)

    def test_betting_Draw_PF_Flush_CallNotWorthIt(self):
        self.strat.hand.suitedInd = 1
        self.strat.hand.connectedInd = 0
        self.strat.movedPlayers = 1
        self.strat.unmovedPlayers = 0
        self.strat.potAmount = 10

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(0,0)

    def test_betting_Draw_PF_Straight_CallWorthIt(self):
        self.strat.hand.suitedInd = 0
        self.strat.hand.connectedInd = 1
        self.strat.movedPlayers = 5
        self.strat.unmovedPlayers = 0
        self.strat.potAmount = 100

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(1,10)

    def test_betting_Draw_PF_Straight_CallNotWorthIt(self):
        self.strat.hand.suitedInd = 0
        self.strat.hand.connectedInd = 1
        self.strat.movedPlayers = 1
        self.strat.unmovedPlayers = 0
        self.strat.potAmount = 10

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(0,0)


class BettingDrawFlop(unittest.TestCase):
    def setUp(self):
        self.strat = nlhbetting.BettingStrat()
        self.strat.hand = cardutils.Hand([cardutils.Card(6,1), cardutils.Card(7,1)])
        self.strat.currBet = 10
        self.strat.potAmount = 30
        self.strat.postFlopOdds = 0
        self.strat.streetCount = 0
        self.strat.street = 1

    def tearDown(self):
        self.strat = None

    @mock.patch('nlhbetting.shouldCBet')
    @mock.patch('random.uniform')
    def test_betting_Draw_Flop_CheckedPot_PFAgg_ShouldCBet(self,random_call,cBet_call):
        self.checkedPot = 1
        self.PFAggressor = -1
        random_call.return_value = 0.5
        cBet_call.return_value = 1

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(2,15)

    @mock.patch('nlhbetting.shouldCBet')
    def test_betting_Draw_Flop_CheckedPot_PFAgg_ShouldntCBet(self,cBet_call):
        self.checkedPot = 1
        self.PFAggressor = -1
        cBet_call.return_value = 0

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(1,10)

    @mock.patch('random.uniform')
    @mock.patch('nlhbetting.shouldSteal')
    def test_betting_Draw_Flop_CheckedPot_NotPFAgg_Steal(self,random_call,steal_call):
        self.checkedPot = 1
        self.PFAggressor = 0
        random_call.return_value = 0.5
        steal_call.return_value = 1

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(2,15)

    @mock.patch('nlhbetting.shouldSteal')
    def test_betting_Draw_Flop_CheckedPot_NotPFAgg_Check(self, steal_call):
        self.checkedPot = 1
        self.PFAggressor = 0
        steal_call.return_value = 0

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(1,10)

    @mock.patch('nlhbetting.shouldDraw')
    def test_betting_Draw_Flop_NotCheckedPot_Draw(self,draw_call):
        self.checkedPot = 0
        draw_call.return_value = 1

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(1,10)

    @mock.patch('nlhbetting.shouldDraw')
    def test_betting_Draw_Flop_NotCheckedPot_Fold(self,draw_call):
        self.checkedPot = 0
        draw_call.return_value = 0

        self.strat.betOutput = mock.MagicMock()
        self.strat.betDrawStreet0()
        self.strat.betOutput.assert_called_with(0,0)

# --------------------------------------
# Test Cases for specific Game instances
# --------------------------------------
# class AAsPFTestCase(unittest.TestCase):
#     """
#     Tests for AA Game class in cardutils.py
#     """
#     def setUp(self):
#         herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
#         playerSB = cardutils.Player(1,"playerSB",100000)
#         playerBB = cardutils.Player(2,"playerBB",100000)
#         playerCO = cardutils.Player(8,"playerCO",100000)
#         playerHero = cardutils.Player(9,"hero",10000)
#         self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])
#         self.game.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
#         self.game.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
#         self.game.players[2].updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
#         self.game.setHeroPosition()
#         self.game.setHeroPlayer("hero")
#         self.game.updateNumPlayers()
#         self.game.currBet = 10
#         self.currbet0 = 10
#         self.potamount0 = 13
#         self.game.potAmount = 13
#         self.game.HeroCash = self.game.players[self.game.heroPlayer].cash
#         (self.action1, self.amount1, self.wait1, self.logstring1) = self.game.bet()
#
#         self.game.players[0].updatePlayerbHist(0, cardutils.BETSTRING_DICT['FOLD'])
#         self.game.players[1].updatePlayerbHist(0, cardutils.BETSTRING_DICT['FOLD'])
#         self.game.players[2].updatePlayerbHist(0, cardutils.BETSTRING_DICT['RAISE'])
#         self.game.currBet = 50
#         self.currbet1 = 50
#         self.game.potAmount = 13 + 2*self.amount1 + 50
#         (self.action2, self.amount2, self.wait2, self.logstring2) = self.game.bet()
#
#         self.game.players[2].updatePlayerbHist(0, cardutils.BETSTRING_DICT['RAISE'])
#         self.game.currBet = 200
#         self.currbet2 = 200
#         self.game.potAmount = 13 + 2*self.amount1 + 2*self.amount2 + 200
#         (self.action3, self.amount3, self.wait3, self.logstring3) = self.game.bet()
#
#         self.game.players[2].updatePlayerbHist(0, cardutils.BETSTRING_DICT['RAISE'])
#         self.game.currBet = 2000000
#         self.currbet3 = 2000000
#         self.game.potAmount = 13 + 2*self.amount1 + 2*self.amount2 + 2*self.amount3 + 2000000
#         (self.action4, self.amount4, self.wait4, self.logstring4) = self.game.bet()
#
#     def test_initnumplayers(self):
#         self.assertEqual(self.game.initNumPlayers, 4)
#
#     def test_BHInd(self):
#         self.assertEqual(self.game.BHInd, 1)
#
#     def test_updateNumPlayers(self):
#         self.assertEqual(self.game.numPlayers, 4)
#
#     def test_heroposition(self):
#         self.assertEqual(self.game.position, 4)
#         self.assertEqual(self.game.players[3].seat, 9)
#
#     def test_betamounts1(self):
#         self.assertEqual(self.currbet0, 10)
#         self.assertEqual(self.potamount0, 13)
#         self.assertEqual(self.action1, 2)
#         self.assertGreaterEqual(self.amount1, 2 * self.currbet0)
#         self.assertLessEqual(self.amount1, 3 * self.currbet0)
#
#     def test_betamounts2(self):
#         self.assertEqual(self.action2, 2)
#         self.assertGreaterEqual(self.amount2, 2 * self.currbet1)
#         self.assertLessEqual(self.amount2, 3 * self.currbet1)
#
#     def test_betamounts3(self):
#         self.assertEqual(self.action3, 2)
#         self.assertGreaterEqual(self.amount3, 2 * self.currbet2)
#         self.assertLessEqual(self.amount3, 3 * self.currbet2)
#
#     def test_betamounts4(self):
#         self.assertEqual(self.action4, 3)
#
# class PreFlopIndsTestCase(unittest.TestCase):
#     """
#     Test case for the PreFlopInds functions
#     """
#     def setUp(self):
#         herohand = cardutils.Hand([cardutils.Card(14,1), cardutils.Card(14,2)])
#         playerSB = cardutils.Player(1,"playerSB",100000)
#         playerBB = cardutils.Player(2,"playerBB",100000)
#         playerCO = cardutils.Player(8,"playerCO",100000)
#         playerHero = cardutils.Player(9,"hero",10000)
#         self.game = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])
#         self.game.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
#         self.game.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
#         self.game.players[2].updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
#         self.game.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['FOLD'])
#         self.game.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
#         self.game.street += 1
#         self.game.setHeroPosition()
#         self.game.updateNumPlayers()
#         self.game.setAggressorInds()
#
#         self.game2 = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])
#         self.game2.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
#         self.game2.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
#         self.game2.players[2].updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
#         self.game2.players[3].updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
#         self.game2.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['FOLD'])
#         self.game2.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['FOLD'])
#         self.game2.players[2].updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
#         self.game2.street += 1
#         self.game2.setHeroPosition()
#         self.game2.updateNumPlayers()
#         self.game2.setAggressorInds()
#
#         self.game3 = nlhutils.Game("hero", herohand,[playerSB, playerBB, playerCO, playerHero])
#         self.game3.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['SB'])
#         self.game3.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['BB'])
#         self.game3.players[2].updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
#         self.game3.players[0].updatePlayerbHist(0,cardutils.BETSTRING_DICT['RAISE'])
#         self.game3.players[1].updatePlayerbHist(0,cardutils.BETSTRING_DICT['FOLD'])
#         self.game3.players[2].updatePlayerbHist(0,cardutils.BETSTRING_DICT['CALL'])
#         self.game3.street += 1
#         self.game3.setHeroPosition()
#         self.game3.updateNumPlayers()
#         self.game3.setAggressorInds()
#
#     def test_simplePreFlopIndsTest(self):
#         self.assertEqual(self.game.PFAggressor, 2)
#
#     def test_simpleHeroPreFlopIndsTest(self):
#         self.assertEqual(self.game2.PFAggressor, -1)
#
#     def test_reraiseHeroPreFlopIndsTest(self):
#         self.assertEqual(self.game3.PFAggressor, 0)

