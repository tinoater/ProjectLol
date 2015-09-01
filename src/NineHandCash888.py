__author__ = 'Ahab'

import logging
import logging.config
from PIL import Image, ImageFilter, ImageGrab, ImageEnhance, ImageChops
import time
import psycopg2
import fileinput
import linecache
import operator
import functools
import math


import constants as c
import cardutils
import screenutils
import nlhutils

def findcardrank(cardimage, suitInd):
    """
    Returns the card rank based on the card image passed in and the deck .bmp file
    :param cardimage: PIL image of the card
    :param suitInd:
    :return: Card Rank
    """
    deckfilename = c.MEDIA_DIR + "\\Deck1_" + c.SUIT_DICT[suitInd] + ".bmp"
    try:
        deckcard = Image.open(deckfilename)
    except:
        logging.critical("Unable to open deck")
        return

    xpoint = 2
    ypoint = 2
    width = 9
    height = 14
    xmove = 36
    res = []
    for i in range(0,14):
        cardbox = (xpoint, ypoint, xpoint + width, ypoint + height)
        deckcardtry = deckcard.convert("RGB")
        deckcardtry = ImageEnhance.Color(deckcardtry).enhance(0.0)
        deckcardtry = deckcardtry.filter(ImageFilter.CONTOUR)
        deckcardtry = deckcardtry.crop(cardbox)
        if c.DEBUGPRINT == True:
            deckcardtry.save("DECKCARDTRY "+ str(i+2) + c.SUIT_DICT[suitInd] +".jpg")

        rms = rmsdiff(deckcardtry, cardimage)
        #print("This is card number: " + str(i + 2) + " with difference: " + str(rms))
        res.append((i+2,rms))
        xpoint = xpoint + xmove
    res = sorted(res, key=lambda tup: tup[1])
    found = res[0][0]
    #print(res)
    return(found)

def rmsdiff(im1, im2):
    """
    Calculate the root-mean-square difference between two images
    :param im1:
    :param im2:
    :return:
    """

    h = ImageChops.difference(im1, im2).histogram()

    # calculate rms
    return math.sqrt(functools.reduce(operator.add,
        map(lambda h, i: h*(i**2), h, range(256))
    ) / (float(im1.size[0]) * im1.size[1]))

def findcardsuit(cardimage):
    """
    Return the card suit based off colour from the card image
    :param cardimage:
    :return:
    """
    sum = [[1,0],[4,0],[2,0]]
    for i, value in enumerate(cardimage.histogram()):
        j = i % 256
        if i <= 256:
            sum[0][1] = sum[0][1] + j * value
        elif i <= 512:
            sum[1][1] = sum[1][1] + j * value
        else:
            sum[2][1] = sum[2][1] + j * value

    #if all similar then a spade
    average = (sum[0][1] + sum[1][1] + sum[2][1])/3
    if abs(average - sum[0][1]) <= 500:
        if abs(average - sum[1][1]) <= 500:
            if abs(average - sum[2][1]) <= 500:
                return 3

    sum = sorted(sum, key=lambda tup:tup[1], reverse=True)
    return sum[0][0]

def findplayerpresent(box):
    """
    Returns an indicator if the player is present (non-folded)
    :param box: BBox of the players action bar
    :return:
    """
    playerim = ImageGrab.grab(box)
    sum = [[1,0],[4,0],[2,0]]
    for i, value in enumerate(playerim.histogram()):
        j = i % 256
        if i <= 256:
            sum[0][1] = sum[0][1] + j * value
        elif i <= 512:
            sum[1][1] = sum[1][1] + j * value
        else:
            sum[2][1] = sum[2][1] + j * value
    if (sum[0][1] > sum[1][1]) & (sum[0][1] > sum[2][1]):
        return 1
    else:
        return 0

def findplayeraction(box):
    """
    Returns the action of the player based on their action bar
    :param box: BBox of the players action bar
    :return:
    """
    playerim = ImageGrab.grab(box)
    r, g, b = playerim.getpixel((30,0))
    rgbint = r*256^2 + g*256 + b

    if abs(rgbint - c.PLAYERFOLDRGB) <=1000:
        return c.BETSTRING_FOLD
    elif abs(rgbint - c.PLAYERCALLRGB) <=1000:
        return c.BETSTRING_CALL
    elif abs(rgbint - c.PLAYERRAISERGB) <=1000:
        return c.BETSTRING_RAISE
    elif abs(rgbint - c.PLAYERALLINRGB) <=1000:
        return c.BETSTRING_ALLIN
    elif abs(rgbint - c.PLAYERSBRGB) <=10:
        return c.BETSTRING_SB
    elif abs(rgbint - c.PLAYERBBRGB) <=10:
        return c.BETSTRING_BB
    else:
        return

def grabstreetcard(box):
    """
    Returns the Card object from the street Bbox input
    :param box: BBox
    :return: Cardimage
    """
    cardim = screenutils.grabcard(box)
    suit = findcardsuit(cardim)
    cardim = cardim.filter(ImageFilter.CONTOUR)
    (x,y) = cardim.size
    cardim = cardim.crop((1,1,x - 1,y - 1))
    cardim = ImageEnhance.Color(cardim).enhance(0.0)
    cardim = ImageEnhance.Sharpness(cardim).enhance(2)
    card = Card(findcardrank(cardim,suit),suit)
    return card

def findstreet(box):
    """
    Returns the street derived from the inputted BBox
    :param box:
    :return: Street
    """
    streetboxim = ImageGrab.grab(box)
    streetboxim = streetboxim.convert("RGB")
    streetboxim = ImageEnhance.Color(streetboxim).enhance(0.0)
    streetboxim = streetboxim.filter(ImageFilter.CONTOUR)

    #check for flop
    streetfilename = c.MEDIA_DIR + "\\0-PreFlop.jpg"
    try:
        streetim = Image.open(streetfilename)
    except:
        logging.critical("Unable to open preflop")
        return
    streetim = ImageEnhance.Color(streetim).enhance(0.0)
    streetim = streetim.filter(ImageFilter.CONTOUR)
    rms = rmsdiff(streetim, streetboxim)
    if rms <= 30:
        return 1

    #test for flop
    streetboxim = streetboxim.crop((101,0,165,12))
    streetfilename = c.MEDIA_DIR + "\\1-Flop.jpg"
    try:
        streetim = Image.open(streetfilename)
    except:
        logging.critical("Unable to open flop")
        return
    streetim = ImageEnhance.Color(streetim).enhance(0.0)
    streetim = streetim.filter(ImageFilter.CONTOUR)
    rms = rmsdiff(streetim, streetboxim)
    if rms <=30:
        return 2

    #test for turn
    streetboxim = streetboxim.crop((32,0,64,12))
    streetfilename = c.MEDIA_DIR + "\\2-Turn.jpg"
    try:
        streetim = Image.open(streetfilename)
    except:
        logging.critical("Unable to open preflop")
        return
    streetim = ImageEnhance.Color(streetim).enhance(0.0)
    streetim = streetim.filter(ImageFilter.CONTOUR)
    rms = rmsdiff(streetim, streetboxim)
    if rms <=60:
        return 3
    else:
        return 4

def pollforheroturn(box):
    """
    Polls every half second to check if the action is on the hero
    :param box:
    :return: Indicator, street
    """
    timeout = False
    count = 0
    while timeout == False:
        playerbarim = ImageGrab.grab(box)
        playerbarim = playerbarim.convert("RGB")

        #Poll until it is heros turn
        total = [0]*256
        for i, value in enumerate(playerbarim.histogram()):
            total[i % 256] = total[i % 256] + value

        if total[255] >= sum(total)*0.6:
            return 1, findstreet(c.STREETBOXPOS)

        count = count + 1
        if c.DEBUGPRINT == True:
            if count % 10 == 0:
                logging.debug("Poll for Hero Turn sleeping " + str(count))

        if count >= 600:
            if c.DEBUGPRINT == True:
                logging.critical("Timeout - exiting Poll for Hero Turn")
            return 0
        time.sleep(0.5)

def getQueryResults(names):
    """
    Returns the DB stats for a list of players. If no stats found then returns list of zeros
    """
    namelist = []
    for each in names:
       namelist.append(each)
    if len(namelist) == 1:
        singleind = 1
    else:
        singleind = 0
    try:
        conn = psycopg2.connect(dbname = "HoldemManager2", user="postgres", host="localhost", password="postgrespass", port=5432)
    except psycopg2.Error as e:
        logging.critical("Cannot connect to DB")
        logging.debug(e)

    query = """SELECT p.playername
     , SUM(totalhands) AS Total_Hands
     , (SUM(cpr.vpiphands) * 100 / SUM(cpr.totalhands)) AS VPIP_Perc
     , (SUM(cpr.pfrhands) * 100 / SUM(cpr.totalhands)) AS PFR_Perc
     , CASE WHEN SUM(cpr.couldcoldcall) = 0 THEN -1
            ELSE (SUM(cpr.didcoldcall) * 100 / SUM(cpr.couldcoldcall))
            END AS Call_Perc
     , CASE WHEN SUM(cpr.flopcontinuationbetpossible) = 0 THEN -1
            ELSE (SUM(cpr.flopcontinuationbetmade) * 100 / SUM(cpr.flopcontinuationbetpossible))
            END AS CBet_Perc
     , CASE WHEN SUM(cpr.facingflopcontinuationbet) = 0 THEN -1
            ELSE (SUM(cpr.foldedtoflopcontinuationbet) * 100 / SUM(cpr.facingflopcontinuationbet))
            END AS CBet_Fold_Perc
     , CASE WHEN SUM(cpr.facingflopcontinuationbet) = 0 THEN -1
            ELSE (SUM(cpr.calledflopcontinuationbet) * 100 / SUM(cpr.facingflopcontinuationbet))
            END AS CBet_Call_Perc
     , CASE WHEN SUM(cpr.facingflopcontinuationbet) = 0 THEN -1
            ELSE (SUM(cpr.raisedflopcontinuationbet) * 100 / SUM(cpr.facingflopcontinuationbet))
            END AS CBet_Raise_Perc
     , CASE WHEN SUM(cpr.turncontinuationbetpossible) = 0 THEN -1
            ELSE (SUM(cpr.turncontinuationbetmade) * 100 / SUM(cpr.turncontinuationbetpossible))
            END AS CBet_Turn_Perc
  FROM players p
  JOIN compiledplayerresults cpr
    ON p.player_id = cpr.player_id
  JOIN gametypes g
    ON cpr.gametype_id = g.gametype_id
  WHERE p.playername IN ("""
    for name in namelist:
        query += "'" + name + "',"
    query = query[:-1]
    query += """)
    --AND p.pokersite_id = 12
    --AND g.istourney = FALSE
    --AND g.bigblindincents <=10
    --AND g.tablesize <=10
    --AND g.pokergametype_id = 0 --NLH
  GROUP BY p.playername"""

    #Connect to DB and run query
    cur = conn.cursor()
    cur.execute(query)
    statlist = []
    for row in cur.fetchall():
        statlist += [list(row)]

    if singleind == 1:
        if len(statlist) == 0:
            #if no stats found then set to zeros
            statlist = [[0,0,0,0,0,0,0,0,0,0]]
        return(statlist[0][1:])
    else:
        return(statlist)

def getplayersfor9table888(filename,heroname = c.HERONAME):
    """
    Returns the players and cash of the table, using the handhistory file. Hero at 0
    """

    pointer = 0
    GAMESTRING = '#Game No'
    filename = c.HAND_HISTORY_DIR + filename
    for line in fileinput.input(filename):
        if line[0:len(GAMESTRING)] == GAMESTRING:
            pointer = fileinput.lineno()
    pointer += 6

    lines = []
    for i in range(0,10):
        line = linecache.getline(filename,pointer + i)
        if line[:5] == "Seat ":
            if line[6] == ":":
                seat = int(line[5])
                name = line[8:]
            else:
                seat = int(line[5:7])
                name = line[9:]
            a = 0
            flag = True
            while flag == True:
                if name[a] == " ":
                    name = name[:a]
                    flag = False
                else:
                    a += 1
            flag = True
            i = 0
            while flag == True:
                if line[i] == "$":
                    cash = line[i+1:]
                    flag = False
                else:
                    i += 1
            flag = True
            i = 0
            while flag == True:
                if cash[i] == ")":
                    cash = cash[:i-1]
                    flag = False
                else:
                    i += 1
            lines.append([seat,name,cash])


    #For 9 people tables there is no Seat 8 for some reason
    for i in range(0,len(lines)):
        if lines[i][0] > 8:
            lines[i][0] -= 1

    maxi = max([e1 for [e1,e2,e3] in lines])
    #Now rearrange around hero
    for each in lines:
        if each[1] == heroname:
            heronum = each[0]
    for each in lines:
        if each[0] >= heronum:
            each[0] -= heronum
        else:
            each[0] += maxi - heronum

    #TODO - Look through the betting to derive current cash amounts

    lines.sort(key=lambda x: x[0])
    p=[]
    logging.debug("Beginning queries to DB")
    for i in range(0,len(lines)):
        p.append(Player(lines[i][0], lines[i][1], lines[i][2]
                        , Stats(*tuple(getQueryResults([lines[i][1]])))))
    logging.debug("DB queries finished")
    return p

def updatetablebetting(game, street, poslist):
    """
    Updates the Game instances betting history list and sets heros position
    """
    for each in game.player:
        position = each.seat
        if position == 0:
            continue
        betstring = cardutils.findplayeraction(c.PLAYERACTIONPOSLIST[position])
        if betstring != None:
            each.updatePlayerbHist(street,betstring)

    if street == 0 and game.player[0].bHist[0] == []:
        if game.player[len(game.player)-1].bHist[0] == c.BETSTRING_SB:
            game.player[0].updatePlayerbHist(0,c.BETSTRING_BB)

    game.setHeroPosition()
    game.updateNumPlayers()
    return


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, filename=c.LOG_FILE_DIR + c.LOG_FILE_NAME
                        ,format='%(asctime)s %(levelname)s:%(message)s')
    logging.info("\n \n")
    logging.info("POKER ENGINE PROGRAM STARTED")

    #potamount = getpotamount(FULLPOTBETBOXPOS, BETBOXPOS)
    logging.debug("Moving the window")
    screenutils.setwindowposition()
    #Get latest table information
    tablename = screenutils.getwindownameofNLH()
    date = time.strftime("%Y%m%d")
    SB = c.BIGBLIND / 200
    BB = c.BIGBLIND / 100
    logging.debug("Waiting for heros turn pre flop")
    logging.debug("-" * 20)
    #Wait until it's heros turn
    if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
        logging.debug("Poll for hero turn timeout!")
    logging.debug("PreFlop")
    logging.debug("-" * 20)
    logging.debug("Grabbing cards for hero")
    print("Grabbing cards")
    #grab the hero cards and create them as a hand
    #TODO clean this up a bit?
    herocardim1 = cardutils.grabcard(c.CARD1POS)
    herocard1suit = cardutils.findcardsuit(herocardim1)
    herocardim1 = cardutils.processflopcard(herocardim1)
    herocardim2 = cardutils.grabcard(c.CARD2POS)
    herocard2suit = cardutils.findcardsuit(herocardim2)
    herocardim2 = cardutils.processflopcard(herocardim2)
    herocard1rank = cardutils.findcardrank(herocardim1, herocard1suit)
    herocard2rank = cardutils.findcardrank(herocardim2, herocard2suit)
    logging.debug("Card 1 is " + str(herocard1rank) + " of " + c.SUIT_DICT[herocard1suit])
    logging.debug("Card 2 is " + str(herocard2rank) + " of " + c.SUIT_DICT[herocard2suit])
    herohand = cardutils.Hand([cardutils.Card(herocard1rank,herocard1suit),cardutils.Card(herocard2rank,herocard2suit)])

    #TODO - this won't work if you play around midnight, which is pretty shit. THink it goes off GMT? Test at 1am
    filename = "\\888poker" + date + " " + tablename + " $" + str(SB) + "-$" + str(BB) + " No Limit Holdem.txt"
    logging.debug("Using file " + filename)
    logging.debug("Get data from file")
    CurrentGame = cardutils.Game(herohand,players = getplayersfor9table888(filename))
    logging.debug("Data read from file")

    print("Entering street loop")

    isstreet = True
    while isstreet == True:
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")

        print("Start sleep")
        time.sleep(2.5)
        cardutils.updatetablebetting(CurrentGame, 0, c.PLAYERPOSLIST)
        print("Done updated table")
        CurrentGame.currbet = screenutils.getbetamount(c.BETBOXPOS) / 2
        CurrentGame.potamount = screenutils.getpotamount(c.FULLPOTBETBOXPOS, c.BETBOXPOS)
        if CurrentGame.currbet != c.BIGBLIND:
            CurrentGame.potamount = CurrentGame.potamount - 2*CurrentGame.currbet
        else:
            CurrentGame.potamount = CurrentGame.potamount - CurrentGame.currbet
        CurrentGame.herocash = float(CurrentGame.player[0].cash)

        logging.debug("We have this many players " + str(CurrentGame.numplayers))
        logging.debug("Hero has " + herohand.getPreHandSimple() + " with odds "
              + str(herohand.getPreHandOdds(CurrentGame.numplayers)))
        for each in CurrentGame.player:
            if each.FoldedInd != 1:
                logging.debug(each.debugPlayerInfo())
        logging.debug("Current bet is " + str(CurrentGame.currbet))
        logging.debug("Current pot size is " + str(CurrentGame.potamount))
        logging.debug("Hero has cash " + str(CurrentGame.herocash))

        print("Start betting funct")
        #MAIN BETTING FUNCTION
        action, amount, wait = CurrentGame.betPreFlop()
        logging.info("We will do action " + str(action) + " with amount " + str(amount) +
                     " and wait " + str(wait))
        logging.info("----Beginning bet wait----")
        screenutils.bettingAction(action, amount, wait)
        logging.info("----Bet complete----")

        time.sleep(1)
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        time.sleep(2.5)
        #Check if we have a flop or if is still pre-flop
        if cardutils.findstreet(c.STREETBOXPOS) == 1:
            logging.debug("Still pre-flop")
        else:
            isstreet = False

    logging.debug("Flop")
    logging.debug("-" * 20)
    streetcard1 = cardutils.grabstreetcard(c.STREET1POS)
    streetcard2 = cardutils.grabstreetcard(c.STREET2POS)
    streetcard3 = cardutils.grabstreetcard(c.STREET3POS)
    herohand.addSharedCards([streetcard1, streetcard2, streetcard3])
    logging.info("Flop Cards are: " + streetcard1.__str__() + " " + streetcard2.__str__()
                 + " " + streetcard3.__str__())
    logging.info("Hero has " + herohand.getPostCurrentHandString())
    CurrentGame.streetcount = -1
    isstreet = True
    while isstreet == True:
        #HERO WILL ACT HERE FLOP
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        cardutils.updatetablebetting(CurrentGame, 1, c.PLAYERPOSLIST)
        CurrentGame.currbet = screenutils.getbetamount(c.BETBOXPOS) / 2
        CurrentGame.potamount = screenutils.getpotamount(c.FULLPOTBETBOXPOS, c.BETBOXPOS)
        if CurrentGame.currbet != c.BIGBLIND:
            CurrentGame.potamount -= 2*CurrentGame.currbet
        else:
            CurrentGame.potamount -= CurrentGame.currbet
        CurrentGame.herocash = float(CurrentGame.player[0].cash)

        for each in CurrentGame.player:
            if each.FoldedInd != 1:
                logging.debug(each.debugPlayerInfo())
        logging.debug("Current bet is " + str(CurrentGame.currbet))
        logging.debug("Current pot size is " + str(CurrentGame.potamount))
        logging.debug("Hero has cash " + str(CurrentGame.herocash))
        logging.debug("Beginning odds function")
        CurrentGame.PostFlopOdds = cardutils.GenerateProbabilities(CurrentGame.numplayers, cardutils.Card(herocard1rank,herocard1suit)
                                         ,cardutils.Card(herocard2rank,herocard2suit),streetcard1, streetcard2
                                         ,streetcard3)
        logging.debug("Exiting odds function")
        logging.info("Players post flop odds are :" + str(CurrentGame.PostFlopOdds))
        action, amount, wait = CurrentGame.betFlop()
        logging.info("We will do action " + str(action) + " with amount " + str(amount) +
                     " and wait " + str(wait))
        logging.info("----Beginning bet wait----")
        screenutils.bettingAction(action, amount, wait)
        logging.info("----Bet complete----")

        time.sleep(1)
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        time.sleep(2.5)
        #Check if we have a turn or if is flop
        if cardutils.findstreet(c.STREETBOXPOS) == 2:
            logging.debug("Still flop")
        else:
            isstreet = False

###########################################################################
    logging.debug("Turn")
    logging.debug("-" * 20)
    streetcard4 = cardutils.grabstreetcard(c.STREET4POS)
    if c.DEBUGPRINT:
        logging.debug(herohand.getPostCurrentHandString())
    herohand.addSharedCards([streetcard4])
    isstreet = True
    streetcount = 0
    while isstreet == True:
        #HERO WILL ACT HERE TURN
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        numplayers = cardutils.updatetablebetting(c.PLAYERPOSLIST)
        CurrentGame.currbet = screenutils.getbetamount(c.BETBOXPOS) / 2
        CurrentGame.potamount = screenutils.getpotamount(c.FULLPOTBETBOXPOS, c.BETBOXPOS)
        if CurrentGame.currbet != c.BIGBLIND:
            CurrentGame.potamount -= 2*CurrentGame.currbet
        else:
            CurrentGame.potamount -= CurrentGame.currbet
        CurrentGame.herocash = float(CurrentGame.player[0].cash)

        for each in CurrentGame.player:
            if each.FoldedInd != 1:
                logging.debug(each.debugPlayerInfo())
        logging.debug("Current bet is " + str(CurrentGame.currbet))
        logging.debug("Current pot size is " + str(CurrentGame.potamount))
        logging.debug("Hero has cash " + str(CurrentGame.herocash))
        logging.debug("Beginning odds function")
        CurrentGame.PostFlopOdds = cardutils.GenerateProbabilities(CurrentGame.numplayers, cardutils.Card(herocard1rank,herocard1suit)
                                         ,cardutils.Card(herocard2rank,herocard2suit),streetcard1, streetcard2
                                         ,streetcard3,streetcard4)
        logging.debug("Exiting odds function")
        logging.info("Players post flop odds are :" + str(CurrentGame.PostFlopOdds))
        action, amount, wait = CurrentGame.betTurn()
        logging.info("We will do action " + str(action) + " with amount " + str(amount) +
                     " and wait " + str(wait))
        logging.info("----Beginning bet wait----")
        screenutils.bettingAction(action, amount, wait)
        logging.info("----Bet complete----")

        time.sleep(1)
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        time.sleep(2.5)
        #Check if we have a river or if is turn
        if cardutils.findstreet(c.STREETBOXPOS) == 3:
            logging.debug("Still turn")
        else:
            isstreet = False

    logging.debug("River")
    logging.debug("-" * 20)
    streetcard5 = cardutils.grabstreetcard(c.STREET5POS)
    herohand = herohand + streetcard5
    if c.DEBUGPRINT:
        logging.debug(herohand.getPostCurrentHandString())
    isstreet = True
    streetcount = 0
    while isstreet == True:
        #HERO WILL ACT HERE FLOP
        logging.debug("-" * 20)
        logging.debug("Waiting for heros turn")
        logging.debug("-" * 20)
        if cardutils.pollforheroturn(c.HEROBOXPOS) == 0:
            logging.debug("Poll for hero turn timeout!")
        numplayers = cardutils.updatetablebetting(c.PLAYERPOSLIST)

        #Check if it is still river
        if cardutils.findstreet(c.STREETBOXPOS) == 4:
            logging.debug("Still river")
            streetcount = streetcount + 1
        else:
            break

    logging.info("POKER ENGINE PROGRAM EXITED")