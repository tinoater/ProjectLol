__author__ = 'Ahab'

import tkinter
import cardutils
import nlhutils

BIGBLIND = 2

class HeroFrame(tkinter.Frame):

    def __init__(self, parent, name, seat, cash, id):
        tkinter.Frame.__init__(self, parent, background = "white")
        self.parent = parent
        self.id = id
        self.initUI(name, seat, cash)

    def initUI(self,name, seat, cash):
        self.nameVar = tkinter.StringVar()
        self.seatVar = tkinter.StringVar()
        self.cashVar = tkinter.StringVar()
        self.c1rankVar = tkinter.StringVar()
        self.c1suitVar = tkinter.StringVar()
        self.c2rankVar = tkinter.StringVar()
        self.c2suitVar = tkinter.StringVar()

        self.nameVar.set(name)
        self.seatVar.set(seat)
        self.cashVar.set(cash)

        f1=tkinter.Frame()
        f2=tkinter.Frame()

        nameLabel = tkinter.Label(f1, textvariable = self.nameVar)
        seatLabel = tkinter.Label(f1, textvariable = self.seatVar)
        cashLabel = tkinter.Label(f1, textvariable = self.cashVar)
        c1rankEntry = tkinter.Entry(f2, textvariable = self.c1rankVar, width = 2)
        c1suitEntry = tkinter.Entry(f2, textvariable = self.c1suitVar, width = 2)
        c2rankEntry = tkinter.Entry(f2, textvariable = self.c2rankVar, width = 2)
        c2suitEntry = tkinter.Entry(f2, textvariable = self.c2suitVar, width = 2)
        nameLabel.pack()
        seatLabel.pack(side = "left")
        cashLabel.pack(side = "left")
        c1rankEntry.pack(side = "left")
        c1suitEntry.pack(side = "left")
        c2rankEntry.pack(side = "left")
        c2suitEntry.pack(side = "left")
        f1.pack()
        f2.pack()

class PlayerFrame(tkinter.Frame):

    def __init__(self,parent, name, seat, cash, id):
        tkinter.Frame.__init__(self, parent, background = "white")
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
        self.cashVar.set(int(self.cashVar.get()) - currentGame.currbet)

    def raisebuttonClick(self):
        raisebuttonButton(self.id, int(self.betAmountV.get()))
        self.cashVar.set(int(self.cashVar.get()) - int(self.betAmountE.get()))

    def allinbuttonClick(self):
        raisebuttonButton(self.id, int(self.cashVar.get()))
        self.cashVar.set(0)

class GameFrame(tkinter.Frame):

    def __init__(self,parent):
        tkinter.Frame.__init__(self, parent, background = "white", bd = 10)
        self.parent = parent
        self.initUI()

    def initUI(self):
        f1 = tkinter.Frame(self)
        f2 = tkinter.Frame(self)
        f3 = tkinter.Frame(self)
        f4 = tkinter.Frame(self)
        initButton = tkinter.Button(f1, text = "Init Game", command = self.initButtonclick)
        betgenButton = tkinter.Button(f2, text = "Generate Bet", command = self.betButtonclick)
        betButton = tkinter.Button(f2, text = "Bet", command = self.herobetButtonclick)
        moveseatButton = tkinter.Button(f1, text = "Move Seat", command = self.moveseatButtonclick)
        self.heroBetAmountV = tkinter.StringVar()
        heroBetAmountE = tkinter.Entry(f2, textvariable = self.heroBetAmountV, width = 7)
        self.logstr = tkinter.StringVar()
        self.msgstr = tkinter.StringVar()
        logstrLabel = tkinter.Label(f3, textvariable = self.logstr)
        msgLabel = tkinter.Label(f4, textvariable = self.msgstr)

        moveseatButton.pack(side = "left")
        initButton.pack(side = "left")
        betgenButton.pack(side = "left")
        heroBetAmountE.pack(side = "left", padx = 10)
        betButton.pack(side = "left")

        logstrLabel.pack(side = "left")
        msgLabel.pack(side = "left")

        f1.pack()
        f2.pack()
        f3.pack()
        f4.pack()
        self.pack()

    def initButtonclick(self):
        initButton()

    def betButtonclick(self):
        betButton()

    def moveseatButtonclick(self):
        moveseatButton()

    def herobetButtonclick(self):
        herobetButton(int(self.heroBetAmountV.get()))

def initButton():
    card1 = cardutils.Card(int(heroFrame.c1rankVar.get()), int(heroFrame.c1suitVar.get()))
    card2 = cardutils.Card(int(heroFrame.c2rankVar.get()), int(heroFrame.c2suitVar.get()))
    heroHand = cardutils.Hand(card1, card2)

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
                currentGame.player[count].updatePlayerbHist(0,'SB')
            elif int(each.seatVar.get()) == 1:
                currentGame.player[count].updatePlayerbHist(0,'BB')
        if count != 0:
            each.bHistVar.set(currentGame.player[count].bHist)

    currentGame.setHeroPosition()
    currentGame.setHeroPlayer("hero")
    currentGame.updateNumPlayers()

    currentGame.currbet = int(BIGBLIND)
    currentGame.potamount = int(1.5 * BIGBLIND)
    betting.msgstr.set("Game created")
    return

def betButton():
    action, amount, wait, logstr = currentGame.bet()
    logVar.set(logstr)
    return

def moveseatButton():
    player1.seatVar.set(str((int(player1.seatVar.get()) + 1) % 9))
    player2.seatVar.set(str((int(player2.seatVar.get()) + 1) % 9))
    player3.seatVar.set(str((int(player3.seatVar.get()) + 1) % 9))
    player4.seatVar.set(str((int(player4.seatVar.get()) + 1) % 9))
    player5.seatVar.set(str((int(player5.seatVar.get()) + 1) % 9))
    player6.seatVar.set(str((int(player6.seatVar.get()) + 1) % 9))
    player7.seatVar.set(str((int(player7.seatVar.get()) + 1) % 9))
    player8.seatVar.set(str((int(player8.seatVar.get()) + 1) % 9))
    heroFrame.seatVar.set(str((int(heroFrame.seatVar.get()) + 1) % 9))

    betting.msgstr.set("Players moved")
    return

def foldbuttonButton(id):
    currentGame.player[id].updatePlayerbHist(currentGame.street,'X')
    resetPlayerLabels()

def callbuttonButton(id):
    currentGame.player[id].updatePlayerbHist(currentGame.street,'C')
    currentpotVar.set(int(currentpotVar.get()) + currentGame.currbet)
    currentGame.potamount += currentGame.currbet
    resetPlayerLabels()

def raisebuttonButton(id, amount):
    currentGame.player[id].updatePlayerbHist(currentGame.street,'R')
    currentpotVar.set(int(currentpotVar.get()) + amount)
    currentGame.currbet = amount
    currentGame.potamount += currentGame.currbet
    resetPlayerLabels()

def herobetButton(amount):
    if amount == currentGame.currbet:
        currentGame.player[0].updatePlayerbHist(currentGame.street,'C')
    else:
        currentGame.player[0].updatePlayerbHist(currentGame.street,'R')

    currentGame.currbet = amount
    currentpotVar.set(int(currentpotVar.get()) + currentGame.currbet)
    currentGame.potamount += currentGame.currbet
    resetPlayerLabels()

def resetPlayerLabels():
    for count, each in enumerate(players):
        if count != 0:
            each.bHistVar.set(currentGame.player[count].bHist)

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
    logLabel = tkinter.Label(root, textvariable = logVar)
    logLabel.pack()

    root.mainloop()
