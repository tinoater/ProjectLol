__author__ = 'Ahab'

import tkinter
import cardutils
import nlhutils
import constants as c

BIGBLIND = 2

class HeroFrame(tkinter.Frame):

    def __init__(self, parent, name, seat, cash, id):
        tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.id = id
        self.initUI(name, seat, cash)

    def initUI(self,name, seat, cash):
        self.nameVar = tkinter.StringVar()
        self.seatVar = tkinter.StringVar()
        self.cashVar = tkinter.StringVar()
        self.c1Var = tkinter.StringVar()
        self.c2Var = tkinter.StringVar()

        self.nameVar.set(name)
        self.seatVar.set(seat)
        self.cashVar.set(cash)

        f1=tkinter.Frame()
        f2=tkinter.Frame()

        nameLabel = tkinter.Label(f1, textvariable = self.nameVar)
        seatLabel = tkinter.Label(f1, textvariable = self.seatVar)
        cashLabel = tkinter.Label(f1, textvariable = self.cashVar)
        c1Entry = tkinter.Entry(f2, textvariable = self.c1Var, width = 4)
        c2Entry = tkinter.Entry(f2, textvariable = self.c2Var, width = 4)
        nameLabel.pack()
        seatLabel.pack(side = "left")
        cashLabel.pack(side = "left")
        c1Entry.pack(side = "left")
        c2Entry.pack(side = "left")
        f1.pack()
        f2.pack()

class PlayerFrame(tkinter.Frame):

    def __init__(self,parent, name, seat, cash, id):
        tkinter.Frame.__init__(self, parent)
        self.parent = parent
        self.id = id
        self.initUI(name, seat, cash)

    def initUI(self, name, seat, cash):
        f1 = tkinter.Frame(self)
        f2 = tkinter.Frame(self)
        f3 = tkinter.Frame(self)

        self.nameVar = tkinter.StringVar()
        self.seatVar = tkinter.StringVar()
        self.cashVar = tkinter.StringVar()
        self.bHistVar = tkinter.StringVar()

        self.nameVar.set(name)
        self.seatVar.set(seat)
        self.cashVar.set(cash)
        self.bHistVar.set("[]")

        self.nameLabel = tkinter.Label(f1, textvariable = self.nameVar)
        self.seatLabel = tkinter.Label(f1, textvariable = self.seatVar)
        self.cashLabel = tkinter.Label(f1, textvariable = self.cashVar)
        self.bHistLabel = tkinter.Label(f3, textvariable = self.bHistVar)

        self.betButton = tkinter.Button(f2, text = "R", command = self.raisebuttonClick)
        self.foldButton = tkinter.Button(f2, text = "X", command = self.foldbuttonClick)
        self.callButton = tkinter.Button(f2, text = "C", command = self.callbuttonClick)
        self.allinButton = tkinter.Button(f2, text = "A", command = self.allinbuttonClick)
        self.betAmountV = tkinter.StringVar()
        self.betAmountE = tkinter.Entry(f2, textvariable = self.betAmountV, width = 7)

        self.nameLabel.pack()
        self.seatLabel.pack(side = "left")
        self.cashLabel.pack(side = "left")
        self.betAmountE.pack(side = "left", padx = 10)
        self.foldButton.pack(side = "left")
        self.callButton.pack(side = "left")
        self.betButton.pack(side = "left")
        self.allinButton.pack(side = "left")
        self.bHistLabel.pack(side = "left")

        f1.pack()
        f2.pack()
        f3.pack()
        self.pack()

    def foldbuttonClick(self):
        self.foldButton['state'] = 'disabled'
        self.callButton['state'] = 'disabled'
        self.allinButton['state'] = 'disabled'
        self.betButton['state'] = 'disabled'
        self.betAmountE['state'] = 'disabled'

        foldbuttonButton(self.id)

    def callbuttonClick(self):
        callbuttonButton(self.id)
        self.cashVar.set(int(self.cashVar.get()) - currentGame.currBet)

    def raisebuttonClick(self):
        raisebuttonButton(self.id, int(self.betAmountV.get()))
        self.cashVar.set(int(self.cashVar.get()) - int(self.betAmountE.get()))

    def allinbuttonClick(self):
        raisebuttonButton(self.id, int(self.cashVar.get()))
        self.cashVar.set(0)

class GameFrame(tkinter.Frame):

    def __init__(self,parent):
        tkinter.Frame.__init__(self, parent, bd = 10)
        self.parent = parent
        self.initUI()
        self.streetcount = 0

    def initUI(self):
        cardsFrame = tkinter.Frame(self)
        initFrame = tkinter.Frame(self)
        bettingFrame = tkinter.Frame(self)
        logstringFrame = tkinter.Frame(self)
        prgmsgFrame= tkinter.Frame(self)
        streetFrame = tkinter.Frame(self)

        self.cardstr = tkinter.StringVar()
        cardLabel = tkinter.Label(cardsFrame, textvariable = self.cardstr)
        initButton = tkinter.Button(initFrame, text = "Init Game", command = self.initButtonclick)
        betgenButton = tkinter.Button(bettingFrame, text = "Generate Bet", command = self.betButtonclick)
        betButton = tkinter.Button(bettingFrame, text = "Bet", command = self.herobetButtonclick)
        moveseatButton = tkinter.Button(initFrame, text = "Move Seat", command = self.moveseatButtonclick)
        self.heroBetAmountV = tkinter.StringVar()
        heroBetAmountE = tkinter.Entry(bettingFrame, textvariable = self.heroBetAmountV, width = 7)
        self.logstr = tkinter.StringVar()
        self.msgstr = tkinter.StringVar()
        logstrLabel = tkinter.Label(logstringFrame, textvariable = self.logstr, wraplength = 30)
        msgLabel = tkinter.Label(prgmsgFrame, textvariable = self.msgstr)
        nextstreetButton = tkinter.Button(streetFrame, text = "Next Street", command = self.nextstreetButtonclick)
        self.card3V = tkinter.StringVar()
        self.card4V = tkinter.StringVar()
        self.card5V = tkinter.StringVar()
        self.card3E = tkinter.Entry(streetFrame, textvariable = self.card3V, width = 4)
        self.card4E = tkinter.Entry(streetFrame, textvariable = self.card4V, width = 4)
        self.card5E = tkinter.Entry(streetFrame, textvariable = self.card5V, width = 4)
        nextstreetcountButton = tkinter.Button(streetFrame, text = "Next Bet", command = self.nextstreetcountButtonclick)

        cardLabel.pack(side = "left")

        moveseatButton.pack(side = "left")
        initButton.pack(side = "left")
        betgenButton.pack(side = "left")
        heroBetAmountE.pack(side = "left", padx = 10)
        betButton.pack(side = "left")

        logstrLabel.pack(side = "left")
        msgLabel.pack(side = "left")

        nextstreetButton.pack(side = "left")
        self.card3E.pack(side = "left")
        self.card4E.pack(side = "left")
        self.card5E.pack(side = "left")
        nextstreetcountButton.pack(side = "left")

        cardsFrame.pack()
        initFrame.pack()
        bettingFrame.pack()
        logstringFrame.pack()
        streetFrame.pack()
        prgmsgFrame.pack()
        self.pack()

    def initButtonclick(self):
        self.cardstr.set("")
        initButton()

    def betButtonclick(self):
        betButton()

    def moveseatButtonclick(self):
        moveseatButton()

    def herobetButtonclick(self):
        herobetButton(int(self.heroBetAmountV.get()))

    def nextstreetButtonclick(self):
        self.streetcount = 0
        nextstreetButton()

    def nextstreetcountButtonclick(self):
        self.streetcount += 1
        setplayerfocus()

def initButton():
    c1rank, c1suit = heroFrame.c1Var.get().split(",")
    c2rank, c2suit = heroFrame.c2Var.get().split(",")
    card1 = cardutils.Card(int(c1rank), int(c1suit))
    card2 = cardutils.Card(int(c2rank), int(c2suit))
    heroHand = cardutils.Hand([card1, card2])

    player1Player = cardutils.Player(player1.seatVar.get(), player1.nameVar.get(), player1.cashVar.get(), [])
    player2Player = cardutils.Player(player2.seatVar.get(), player2.nameVar.get(), player2.cashVar.get(), [])
    player3Player = cardutils.Player(player3.seatVar.get(), player3.nameVar.get(), player3.cashVar.get(), [])
    player4Player = cardutils.Player(player4.seatVar.get(), player4.nameVar.get(), player4.cashVar.get(), [])
    player5Player = cardutils.Player(player5.seatVar.get(), player5.nameVar.get(), player5.cashVar.get(), [])
    player6Player = cardutils.Player(player6.seatVar.get(), player6.nameVar.get(), player6.cashVar.get(), [])
    player7Player = cardutils.Player(player7.seatVar.get(), player7.nameVar.get(), player7.cashVar.get(), [])
    player8Player = cardutils.Player(player8.seatVar.get(), player8.nameVar.get(), player8.cashVar.get(), [])
    heroPlayer = cardutils.Player(heroFrame.seatVar.get(), heroFrame.nameVar.get(), heroFrame.cashVar.get(), [])

    global currentGame
    currentGame = nlhutils.Game(heroHand,[heroPlayer, player1Player, player2Player, player3Player, player4Player
                                          ,player5Player, player6Player, player7Player, player8Player])

    for count, each in enumerate(players):
        if int(each.seatVar.get()) in (0,1):
            if int(each.seatVar.get()) == 0:
                currentGame.players[count].updatePlayerbHist(0,c.BETSTRING_SB)
            elif int(each.seatVar.get()) == 1:
                currentGame.players[count].updatePlayerbHist(0,c.BETSTRING_BB)
        if count != 0:
            each.bHistVar.set(currentGame.players[count].bHist)

    currentGame.setHeroPosition()
    currentGame.setHeroPlayer("hero")
    currentGame.updateNumPlayers()

    currentGame.currBet = int(BIGBLIND)
    currentGame.potAmount = int(1.5 * BIGBLIND)

    setplayerfocus()

    betting.msgstr.set("Game created")
    return

def betButton():
    currentGame.updateNumPlayers()
    FlopCards = []

    if currentGame.street != 0:
        FlopCards = currentGame.hand.sharedCards
        currentGame.hand.PostFlopOdds = nlhutils.GenerateProbabilities(currentGame.numPlayers,
                                                                  [currentGame.hand._cards[0], currentGame.hand._cards[1]],
                                                                  FlopCards)
    action, amount, wait, logstr = currentGame.bet()
    logVar.set(logstr)

    return

def moveseatButton():
    player1.seatVar.set(str((int(player1.seatVar.get()) - 1) % 9))
    #currentGame.player[1].seat = (int(player1.seatVar.get()) + 1) % 9
    player2.seatVar.set(str((int(player2.seatVar.get()) - 1) % 9))
    #currentGame.player[2].seat = (int(player2.seatVar.get()) + 1) % 9
    player3.seatVar.set(str((int(player3.seatVar.get()) - 1) % 9))
    #currentGame.player[3].seat = (int(player3.seatVar.get()) + 1) % 9
    player4.seatVar.set(str((int(player4.seatVar.get()) - 1) % 9))
    #currentGame.player[4].seat = (int(player4.seatVar.get()) + 1) % 9
    player5.seatVar.set(str((int(player5.seatVar.get()) - 1) % 9))
    #currentGame.player[5].seat = (int(player5.seatVar.get()) + 1) % 9
    player6.seatVar.set(str((int(player6.seatVar.get()) - 1) % 9))
    #currentGame.player[6].seat = (int(player6.seatVar.get()) + 1) % 9
    player7.seatVar.set(str((int(player7.seatVar.get()) - 1) % 9))
    #currentGame.player[7].seat = (int(player7.seatVar.get()) + 1) % 9
    player8.seatVar.set(str((int(player8.seatVar.get()) - 1) % 9))
    #currentGame.player[8].seat = (int(player8.seatVar.get()) + 1) % 9
    heroFrame.seatVar.set(str((int(heroFrame.seatVar.get()) - 1) % 9))
    #currentGame.player[0].seat = (int(heroFrame.seatVar.get()) + 1) % 9

    betting.msgstr.set("Players moved")
    return

def foldbuttonButton(id):
    currentGame.players[id].updatePlayerbHist(currentGame.street,c.BETSTRING_FOLD)
    resetPlayerLabels()
    setplayerfocus()

def callbuttonButton(id):
    currentGame.players[id].updatePlayerbHist(currentGame.street,c.BETSTRING_CALL)
    currentpotVar.set(int(currentpotVar.get()) + currentGame.currBet)
    currentGame.potAmount += currentGame.currBet
    resetPlayerLabels()
    setplayerfocus()

def raisebuttonButton(id, amount):
    currentGame.players[id].updatePlayerbHist(currentGame.street,c.BETSTRING_RAISE)
    currentpotVar.set(int(currentpotVar.get()) + amount)
    currentGame.currBet = amount
    currentGame.potAmount += currentGame.currBet
    resetPlayerLabels()
    setplayerfocus()

def herobetButton(amount):
    if amount == currentGame.currBet:
        currentGame.players[0].updatePlayerbHist(currentGame.street,c.BETSTRING_CALL)
    else:
        currentGame.players[0].updatePlayerbHist(currentGame.street,c.BETSTRING_RAISE)

    currentGame.currBet = amount
    currentpotVar.set(int(currentpotVar.get()) + currentGame.currBet)
    currentGame.potAmount += currentGame.currBet
    resetPlayerLabels()
    setplayerfocus()

def resetPlayerLabels():
    for count, each in enumerate(players):
        if count != 0:
            each.bHistVar.set(currentGame.players[count].bHist)

def nextstreetButton():
    cardslabel = betting.cardstr.get()
    if betting.card3V.get() != "":
        c1rank, c1suit = betting.card3V.get().split(",")
        cardslabel += betting.card3V.get() + " "
        card1 = cardutils.Card(int(c1rank), int(c1suit))
        betting.card3V.set("")
    if betting.card4V.get() != "":
        c2rank, c2suit = betting.card4V.get().split(",")
        cardslabel += betting.card4V.get() + " "
        card2 = cardutils.Card(int(c2rank), int(c2suit))
        betting.card4V.set("")
    if betting.card5V.get() != "":
        c3rank, c3suit = betting.card5V.get().split(",")
        cardslabel += betting.card5V.get() + " "
        card3 = cardutils.Card(int(c3rank), int(c3suit))
        betting.card5V.set("")

    betting.cardstr.set(cardslabel)

    if currentGame.street == 0:
        currentGame.hand.addSharedCards([card1])
        currentGame.hand.addSharedCards([card2])
        currentGame.hand.addSharedCards([card3])
    elif currentGame.street == 1:
        currentGame.hand.addSharedCards([card1])
    elif currentGame.street == 2:
        currentGame.hand.addSharedCards([card1])
    elif currentGame.street == 3:
        pass

    currentGame.street += 1
    currentGame.streetCount = 0
    currentGame.currBet = 0

    setplayerfocus()

    betting.card4E["state"] = "disabled"
    betting.card5E["state"] = "disabled"

def setplayerfocus():
    try:
        playerlist = [player for player in currentGame.players if player.FoldedInd == 0]
    except:
        pass

    try:
        focus = min([player.seat for player in playerlist if len(player.bHist[currentGame.street]) <= betting.streetcount])
    except:
        try:
            focus = min([player.seat for player in playerlist if player.bHist[currentGame.street][betting.streetcount] not in ("A","R","X")])
        except:
            focus = -1

    heroFrame.configure(bg = "systembuttonface")
    for each in players:
        if each.seatVar.get() == str(focus):
            if each.nameVar.get() == 'hero':
                heroFrame.configure(bg = "black")
            else:
                each.configure(bg = "black")
        else:
            each.configure(background = "systembuttonface")

if __name__ == "__main__":
    root = tkinter.Tk()
    mainlabel = tkinter.Label(root, text = "Test program for Poker Engine")
    mainlabel.pack()

    currentpotVar = tkinter.StringVar()
    currentpotVar.set(int(1.5 * BIGBLIND))
    currentpotLabel = tkinter.Label(root, textvariable = currentpotVar)
    currentpotLabel.pack()

    heroFrame = HeroFrame(root, "hero", 0, 200, 0)
    heroFrame.pack()

    f1 = tkinter.Frame()
    f2 = tkinter.Frame()
    f3 = tkinter.Frame()
    f4 = tkinter.Frame()

    player1 = PlayerFrame(f1, "Player1", 1, 200, 1)
    player1.pack(side = "left")
    player2 = PlayerFrame(f2, "Player2", 2, 200, 2)
    player2.pack(side = "left")
    player3 = PlayerFrame(f3, "Player3", 3, 200, 3)
    player3.pack(side = "left")
    player4 = PlayerFrame(f4, "Player4", 4, 200, 4)
    player4.pack(side = "left")
    player5 = PlayerFrame(f1, "Player5", 5, 200, 5)
    player5.pack(side = "left")
    player6 = PlayerFrame(f2, "Player6", 6, 200, 6)
    player6.pack(side = "left")
    player7 = PlayerFrame(f3, "Player7", 7, 200, 7)
    player7.pack(side = "left")
    player8 = PlayerFrame(f4, "Player8", 8, 200, 8)
    player8.pack(side = "left")

    players = [heroFrame, player1, player2, player3, player4, player5, player6, player7, player8]

    f1.pack()
    f2.pack()
    f3.pack()
    f4.pack()

    betting = GameFrame(root)
    betting.pack()

    logVar = tkinter.StringVar()
    logLabel = tkinter.Label(root, textvariable = logVar, font=("Helvetica", 8))
    logLabel.pack()

    #Set the window position
    root.update()
    w = root.winfo_width()
    h = root.winfo_screenheight() * 0.95
    x = root.winfo_screenwidth() - w*1.05
    y = 0

    root.geometry('%dx%d+%d+%d' % (w,h,x,y))

    root.mainloop()
