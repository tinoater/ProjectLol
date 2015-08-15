__author__ = 'Ahab'

LOG_FILE_DIR = "C:\\Users\\Ahab\\Desktop"
LOG_FILE_NAME = "\\PokerEnging.log"
HAND_HISTORY_DIR ="C:\\Users\\Ahab\\AppData\\Roaming\\PacificPoker\\HandHistory\\tinoater"
PF_ODDS_FILENAME = 'PreFlop.csv'
RANK_DICT = {2:'2',3:'3',4:'4',5:'5',6:'6',7:'7',8:'8',9:'9',10:'T',11:'J',12:'Q',13:'K',14:'A'}
SUIT_DICT = {1:'H',2:'D',3:'S',4:'C'}
PREM_PARIS = [14,13,12]
HAND_DICT = {1:'Royal Flush', 2:'Straight Flush', 3:'Four of a Kind', 4:'Full House', 5:'Flush', 6:'Straight'
             ,7:'Three of a Kind',8:'Two Pairs',9:'One Pair',10:'High Card'}
QUERY_DICT={'Name':0, 'NumHands':1, 'VPIP_Perc':2, 'PFR_Perc':3, 'Call_Perc':4, 'CBet_Perc':5, 'CBet_Fold_Perc':6
          , 'CBet_Call_Perc':7, 'CBet_Raise_Perc':8, 'CBet_Turn_Perc':9}
#These card positions are hardcoded
#Hero cards
CARD1POS = (215, 222, 245, 239)
CARD2POS = (245, 222, 278, 239)
#These cards are 1px too large, to be cropped after contour
STREET1POS = (169,121,180,137)
STREET2POS = (203,121,214,137)
STREET3POS = (236,121,247,137)
STREET4POS = (269,121,280,137)
STREET5POS = (302,121,313,137)
STREETBOXPOS = (170,123,335,135)
#Hero time bar
HEROBOXPOS = (220,270,288,271)
BETBOXPOS = (457,332)
HALFPOTBETBOXPOS = (349,318)
FULLPOTBETBOXPOS = (420,318)
ALLINPOTBETBOXPOS = (457,318)
RAISEBUTTONPOS = (444,298)
CALLBUTTONPOS = (344,298)
FOLDBUTTONPOS = (244,298)
#Player presence
PLAYERPOSLIST = [(0,0,0,0),(120, 232, 148, 244), (43, 164, 71, 176), (43 , 97, 71, 109), (163, 40, 191, 52)
    , (297, 40, 325, 52), (428, 97, 456, 109), (428, 164, 456, 176), (341, 232, 369, 244)]
PLAYERACTIONPOSLIST = [(0,0,0,0),(114,270,177,271),(37,200,101,201),(37,136,101,137),(157,79,221,80)
    ,(292,79,355,80),(422,136,486,137),(422,200,486,201),(334,270,397,271)]

PLAYERFOLDRGB = 34776
PLAYERCALLRGB = 54574
PLAYERRAISERGB = 32774
PLAYERALLINRGB = 65026
PLAYERSBRGB = 115
PLAYERBBRGB = 173
DEBUGPRINT = False
#Table config
BIGBLIND = 2
#Betting config
PF_PREM_RERAISE_PERC = 0.2 #How often reraise preflop curr bet >3BB
PF_PP_BELOW_9_RAISE =  0.3 #How often open raise preflop with PP <9
PF_PP_BELOW_9_CALL = 1 #How often open call with PF with PP <9
PF_SMALL_PAIR = 25 * BIGBLIND #Threshold to call PF with pocket pairs, per player
PF_FL_STR_DRAW = 20 * BIGBLIND #Threshold to call PF with suited or connected
RAISE_TO_ALLIN_THRESH = 0.2 #If 1+this * raise >= cash then go all in

PF_CALL_AFTER_RAISE_PERC = 0.8 #Perc of a PF call of a raise
PF_CALL_PERC = 0.3 #Perc of a PF open call
PF_STEAL = 0.3 #Perc of trying to steal from button or more
PF_OTHER_HANDS_OPEN = 0.8 #Perc of PF opening the pot with other hand > 10%
PF_OTHER_HANDS_CALL = 0.7 #Perc of PF callling into the pot with other hand > 10%

if __name__ == "__main__":
	pass