__author__ = 'Ahab'

import tkinter
import constants as c
import csv
import screenutils
import itertools
from PIL import Image, ImageTk
import base64
import io

WIN10PADDING = -7
#Display offset constants as the difference between the area of the whole screen and that of the window
#TODO Make this dynamic so I can easily redistribute
DISPLAYOFFSETY = -72
DISPLAYOFFSETX = -45
varlist = []
numvars = 0

currvar = 0
currvarname = ''
currvarvalues = []


def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)

class TransparentWindow(tkinter.Frame):
    """
    Transparent window that spans most of the screen to show positions of stuff
    """

    # TODO: Make this take an optional alpha parameter so I can reuse?
    def __init__(self, master):
        # Global variables
        global varlist
        global numvars

        # Transparent window
        self.root = master
        # Set the window size and make slightly transparent
        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight() * 0.8
        x = WIN10PADDING
        y = 0
        self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.root.attributes('-alpha', 0.2)

        # Load the constant variables from file
        c.updatePositionVariables('config.txt')

        # Load the constants into a local varlist for some reason
        try:
            con_file = open('config.txt', "r")
        except:
            raise Exception("Couldn't open constants text file")
        con_reader = csv.reader(con_file)
        varlist = []
        for row in con_reader:
            if '#' not in row[0]:
                if row[0] in ('PLAYERPOSLIST', 'PLAYERACTIONPOSLIST'):
                    l = row[1:]
                    o = [[l[i],l[i+1],l[i+2],l[i+3]] for i in range(0,len(l),4)]
                    for i, each in enumerate(o):
                        if i != 0:
                            varlist.append([row[0]+' '+str(i), [float(x) for x in each]])
                else:
                    varlist.append([row[0], [float(x) for x in row[1:]]])
        numvars = len(varlist)
        con_file.close()

        self.canvas = tkinter.Canvas(self.root, bg='red')


class ControlWindow(tkinter.Frame):
        """
        Control window to contain variable name and picture preview
        """

        def __init__(self, parent_win, master):
            # Control window
            self.root = master
            self.parent_win = parent_win
            w = self.root.winfo_screenwidth()
            h = self.root.winfo_screenheight() * 0.06
            x = WIN10PADDING
            y = self.root.winfo_screenheight() * 0.84
            self.root.geometry('%dx%d+%d+%d' % (w, h, x, y))

            self.controlVar = tkinter.StringVar()
            self.switchButton = tkinter.Button(self.root, text="Next Var", command=self.local_switchButtonClick)
            self.refreshButton = tkinter.Button(self.root, text="Refresh", command=self.local_refreshButtonClick)
            self.label = tkinter.Label(self.root, textvariable=self.controlVar)
            self.canvas = tkinter.Canvas(self.root, width=100, height=100)
            self.imageOnCanvas = self.canvas.create_image(0, 0)

            self.coordVar = tkinter.StringVar()
            self.coordLabel = tkinter.Label(self.root, textvariable = self.coordVar)

            self.leftCoordVar = tkinter.StringVar()
            self.topCoordVar = tkinter.StringVar()
            self.rightCoordVar = tkinter.StringVar()
            self.bottomCoordVar = tkinter.StringVar()

            self.leftText = tkinter.Entry(self.root, textvariable= self.leftCoordVar)
            self.topText = tkinter.Entry(self.root, textvariable= self.topCoordVar)
            self.rightText = tkinter.Entry(self.root, textvariable= self.rightCoordVar)
            self.bottomText = tkinter.Entry(self.root, textvariable= self.bottomCoordVar)

            self.moveButton = tkinter.Button(self.root, text="Move", command=self.local_moveButtonClick)

            self.switchButton.pack(side="left")
            self.refreshButton.pack(side="left")
            self.moveButton.pack(side="left")
            self.label.pack(side="left")
            self.canvas.pack(side="left")
            self.coordLabel.pack(side="left")
            self.leftText.pack(side="left")
            self.topText.pack(side="left")
            self.rightText.pack(side="left")
            self.bottomText.pack(side="left")

            self.local_setcurrvarvalues(0)

        def local_switchButtonClick(self):
            switchButtonClick(self)

        def local_refreshButtonClick(self):
            refreshButtonClick(self)

        def local_setcurrvarvalues(self, ind):
            setcurrvarvalues(self, self.parent_win, ind)

        def local_moveButtonClick(self):
            if self.rightText.get() == '-':
                moveButtonClick(self, [int(self.leftText.get()) - 10, int(self.topText.get()) - 10, int(self.leftText.get()) + 10, int(self.topText.get()) + 10], 'adj')
            else:
                moveButtonClick(self, [int(self.leftText.get()), int(self.topText.get()), int(self.rightText.get()), int(self.bottomText.get())], 'adj')


def setcurrvarvalues(cntrl_win, trans_win, index):
    global currvar
    global currvarname
    global currvarvalues
    global varlist

    currvar = index
    currvarname = varlist[currvar][0]
    currvarvalues = varlist[currvar][1:][0]
    currvarvalues = [int(x) for x in currvarvalues]

    if len(currvarvalues) == 4:
        trans_win.canvas.place(x=currvarvalues[0], y=currvarvalues[1])
        trans_win.canvas.configure(width=(currvarvalues[2] - currvarvalues[0]),
                                   height=(currvarvalues[3] - currvarvalues[1]))
        cntrl_win.leftCoordVar.set(currvarvalues[0])
        cntrl_win.topCoordVar.set(currvarvalues[1])
        cntrl_win.rightCoordVar.set(currvarvalues[2])
        cntrl_win.bottomCoordVar.set(currvarvalues[3])

    elif len(currvarvalues) == 2:

        cntrl_win.leftCoordVar.set(currvarvalues[0])
        cntrl_win.topCoordVar.set(currvarvalues[1])
        cntrl_win.rightCoordVar.set('-')
        cntrl_win.bottomCoordVar.set('-')

        currvarvalues[0] -= 10
        currvarvalues[1] -= 10
        currvarvalues.append(currvarvalues[0] + 10)
        currvarvalues.append(currvarvalues[1] + 10)
        trans_win.canvas.place(x=currvarvalues[0], y=currvarvalues[1])
        trans_win.canvas.configure(width=5, height=5)

    currvarvalues[0] -= DISPLAYOFFSETX
    currvarvalues[1] -= DISPLAYOFFSETY
    currvarvalues[2] -= DISPLAYOFFSETX
    currvarvalues[3] -= DISPLAYOFFSETY

    setCanvasImage(cntrl_win, currvarvalues, currvarname)

def setCanvasImage(window, values, name):
    screenGrab = screenutils.grabcard(values)

    #TODO To be used instead of the temp file solution at some point
    #fp = io.StringIO()
    #screenGrab.save(fp, format='GIF')
    #screenGrabPhotoIm = ImageTk.PhotoImage(data=base64.encodebytes(fp.getvalue()))

    screenGrab.save("temp.jpg")
    screenGrabPhotoIm = ImageTk.PhotoImage(file="temp.jpg")

    window.canvas.create_image(0, 0, image = screenGrabPhotoIm, anchor = 'nw')
    window.canvas.photo = screenGrabPhotoIm
    #cntrl_win.canvas.itemconfig(cntrl_win.imageOnCanvas, image=screenGrabPhotoIm)
    #cntrl_win.canvas.config(width = screenGrabPhotoIm._PhotoImage__size[0], height = screenGrabPhotoIm._PhotoImage__size[1])

    window.controlVar.set(name)
    window.coordVar.set(str(values[0]) + ',' + str(values[1]) + ',' + str(values[2]) + ',' + str(values[3]) + ',')

def switchButtonClick(cntr_win):
    global currvar

    if currvar == numvars:
        currvar = 0
    else:
        currvar += 1
    setcurrvarvalues(cntr_win, cntr_win.parent_win, currvar)


def refreshButtonClick(cntr_win):
    global currvar

    setcurrvarvalues(cntr_win, cntr_win.parent_win, currvar)


def moveButtonClick(cntr_win, values, name):

    values[0] -= DISPLAYOFFSETX
    values[1] -= DISPLAYOFFSETY
    values[2] -= DISPLAYOFFSETX
    values[3] -= DISPLAYOFFSETY

    setCanvasImage(cntr_win, values, name)

if __name__ == "__main__":
    screenutils.setwindowposition()
    master = tkinter.Tk()
    trans_app = TransparentWindow(master)
    child = tkinter.Toplevel()
    cntrl_app = ControlWindow(trans_app, child)

    cntrl_app.root.mainloop()
