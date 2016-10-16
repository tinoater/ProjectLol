__author__ = 'Ahab'

import csv

#TODO read this from a csv file instead of being hardcoded
LOG_FILE_DIR = "C:\\Users\\Ahab\\Desktop"
LOG_FILE_NAME = "\\PokerEnging.log"
HAND_HISTORY_DIR ="C:\\Users\\Ahab\\AppData\\Roaming\\PacificPoker\\HandHistory\\tinoater"
MEDIA_DIR = "Media"
PF_ODDS_FILENAME = '\\PreFlop.csv'
QUERY_DICT={'Name':0, 'NumHands':1, 'VPIP_Perc':2, 'PFR_Perc':3, 'Call_Perc':4, 'CBet_Perc':5, 'CBet_Fold_Perc':6
          , 'CBet_Call_Perc':7, 'CBet_Raise_Perc':8, 'CBet_Turn_Perc':9}

HERONAME = 'tinoater'
CARDCROP_BBOX = (1,1,10,15)

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
PF_FL_DRAW = 2 #Amount the pot will scale by from PF to SD for flush draw
PF_STR_DRAW = 2 #Amount the pot will scale by from PF to SD for straight draw
PF_STRFL_DRAW = 2 #Amount the pot will scale by from PF to SD for straight draw
PF_FL_ODDS = 10 #Threshold for how often try to draw for a flush
PF_STR_ODDS = 13 #Threshold for how often try to draw for a flush
PF_STRFL_ODDS = 7 #Threshold for how often try to draw with straightflush draw
RAISE_TO_ALLIN_THRESH = 0.2 #If 1+this * raise >= cash then go all in

PF_CALL_AFTER_RAISE_PERC = 0.8 #Perc of a PF call of a raise
PF_CALL_PERC = 0.3 #Perc of a PF open call
PF_STEAL = 0.3 #Perc of trying to steal from button or more
PF_OTHER_HANDS_OPEN = 0.2 #Perc of PF opening the pot with other hand > 10%
PF_OTHER_HANDS_CALL = 0.7 #Perc of PF callling into the pot with other hand > 10%
BH_THRESHOLD = 0.85 #Odds of winning threshold to assume best hand
BH_FP_RERAISE = 0.2 #When reraise a bet on flop when have BH
FLOP_CBET = 0.5 #How often CBet the flop
TURN_CBET = 0.1 #How often CBet the turn
RIVER_CBET = 0.1 #How often CBet the river
FLOP_STEAL = 0.2 #How often try to steal a flop
TURN_STEAL = 0.1 #How often try to steal a turn
RIVER_STEAL = 0.1 #How often try to steal a river
BH_T_RERAISE = 0.1 #When reraise a bet on the turn when have BH
BH_R_RERAISE = 1 #When reraise a bet on the turn when have BH

# Lists used by betting program
BH_RERAISE = [BH_FP_RERAISE, BH_T_RERAISE, BH_R_RERAISE]

ODDSRUNCOUNT = 10000 #Number of runs for the odds calc program. Should get to nearest percent in ~4s

def updatePositionVariables(txtfile):
    """
    Set the constant values from reading from the input text file

    Lines of length 3 or 5 get set up as tuples
    :param txtfile:
    :return:
    """
    try:
        con_file = open(txtfile, "r")
    except:
        raise Exception("Couldn't open constants text file")
    con_reader = csv.reader(con_file)

    for row in con_reader:
        if row[0] in ('PLAYERPOSLIST','PLAYERACTIONPOSLIST'):
            if len(row) != 37:
                raise Exception("Constant " + row[0] + " in file " + txtfile + "has incorrect length")
            globals()[row[0]] = [(float(row[1]), float(row[2]), float(row[3]), float(row[4])), (float(row[5]), float(row[6]), float(row[7]), float(row[8])),
                                 (float(row[9]), float(row[10]), float(row[11]), float(row[12])), (float(row[13]), float(row[14]), float(row[15]), float(row[16])),
                                 (float(row[17]), float(row[18]), float(row[19]), float(row[20])), (float(row[21]), float(row[22]), float(row[23]), float(row[24])),
                                 (float(row[25]), float(row[26]), float(row[27]), float(row[28])), (float(row[29]), float(row[30]), float(row[31]), float(row[32])),
                                 (float(row[33]), float(row[34]), float(row[35]), float(row[36]))]
        else:
            if len(row) == 5:
                globals()[row[0]] = (float(row[1]), float(row[2]), float(row[3]), float(row[4]))
            elif len(row) == 3:
                globals()[row[0]] = (float(row[1]), float(row[2]))

    con_file.close()

if __name__ == "__main__":
    updatePositionVariables('pokerpositions.txt')