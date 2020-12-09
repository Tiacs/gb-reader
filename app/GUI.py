# Copyright (c) 2017 Fabian Friedl
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from tkinter import *
from tkinter import ttk
from PIL import Image
from PIL import ImageTk as itk


class GUI:

    def __init__(self, loadHeader, loadGame, startGame, refreshCOMList, changeCOMDevice, saveFile):
        """
        Tkinter GUI object
        :param loadHeader: LoadHeader function which will be called after button click
        :param loadGame: LoadGame function which will be called after button click
        :param startGame: StartGame function which will be called after button
        :param refreshCOMList: RefrehCOMList function which will be called after menu entry click
        :param changeCOMDevice: ChangeCOMDevice function which will be called after menu entry click
        :param saveFile: SaveFile function which will be called after menu entry click
        """
        self._onLoadHeader = loadHeader
        self._onLoadGame = loadGame
        self._onStartGame = startGame
        self._onRefreshCOMList = refreshCOMList
        self._onChangeCOMDevice = changeCOMDevice
        self._onSaveFile = saveFile

        self._initWindow()

        self._buildGUI()

        self._createMenu()

    def _initWindow(self):
        self._root = Tk()
        self._root.geometry("547x504+30+30")
        self._root.iconbitmap(default='icon.ico')
        self._root.title("GBC - Reader")
        self._root.resizable(width=False, height=False)

    def _buildGUI(self):
        """
        Build whole GUI. Adds components to window.
        """
        w = Label(master=self._root, text="")  # Placeholder column 1
        w.grid(row=0, column=0, sticky="W", pady=0)

        w = Label(master=self._root, text="")  # Placeholder column 3
        w.grid(row=0, column=3, sticky="W", pady=0)


        self._titleTextLabel = Label(master=self._root, text="Game Title", fg="black", font=("Helvetica", "16"))
        self._titleTextLabel.grid(row=1, column=1, sticky="W")

        self._titleLabel = Label(master=self._root, text="...", fg="black", font=("Helvetica", "16"))
        self._titleLabel.grid(row=1, column=2, sticky="W")


        self._typeTextLabel = Label(master=self._root, text="Cartridge Type", fg="black", font=("Helvetica", "16"))
        self._typeTextLabel.grid(row=2, column=1, sticky="W")

        self._typeLabel = Label(master=self._root, text="...", fg="black", font=("Helvetica", "16"))
        self._typeLabel.grid(row=2, column=2, sticky="W")


        self._flagTextLabel = Label(master=self._root, text="CGBFlag", fg="black", font=("Helvetica", "16"))
        self._flagTextLabel.grid(row=3, column=1, sticky="W")

        self._flagLabel = Label(master=self._root, text="...", fg="black", font=("Helvetica", "16"))
        self._flagLabel.grid(row=3, column=2, sticky="W")


        self._sizeTextLabel = Label(master=self._root, text="ROM Size", fg="black", font=("Helvetica", "16"))
        self._sizeTextLabel.grid(row=4, column=1, sticky="W")

        self._sizeLabel = Label(master=self._root, text="...", fg="black", font=("Helvetica", "16"))
        self._sizeLabel.grid(row=4, column=2, sticky="W")


        self._banksTextLabel = Label(master=self._root, text="ROMBanks", fg="black", font=("Helvetica", "16"))
        self._banksTextLabel.grid(row=5, column=1, sticky="W")

        self._banksLabel = Label(master=self._root, text="...", fg="black", font=("Helvetica", "16"))
        self._banksLabel.grid(row=5, column=2, sticky="W")

        self._img = Image.new('RGB', (48 * 5, 8 * 5), "black")
        photo = itk.PhotoImage(self._img)
        self._nintendoLogo = Label(master=self._root, image=photo)
        self._nintendoLogo.image = photo

        self._nintendoLogo.grid(row=6, column=1, columnspan=2, sticky="WENS", padx=5, pady=5)


        w = Label(self._root, text="")
        w.grid(row=6, column=1, pady=40, sticky="W")

        self._infoButton = Button(master=self._root, text="Read Game Info", bg="grey", state="disabled", command=self._onLoadHeader, width=75, height=3)
        self._infoButton.grid(row=8, column=1, columnspan=2, sticky="W")

        self._readButton = Button(master=self._root, text="Read Game Data", bg="grey", state="disabled", command=self._onLoadGame, width=75, height=3)
        self._readButton.grid(row=9, column=1, columnspan=2, sticky="W")

        self._startButton = Button(master=self._root, text="Play Game", bg="grey", state="disabled", command=self._onStartGame, width=75, height=3)
        self._startButton.grid(row=10, column=1, columnspan=2, sticky="W")

        self._errorLabel = Label(master=self._root, text="", fg="red")
        self._errorLabel.grid(row=11, column=0, columnspan=4)

        w = Label(master=self._root, text="by Fabian Friedl & Tobias Haider", fg="gray")
        w.grid(row=12, column=0, columnspan=4)

        self._progress = ttk.Progressbar(master=self._root, orient="horizontal", max=100)
        self._progress.grid(row=13, column=0, columnspan=5, sticky="ESW")


    def _createMenu(self):
        """
        Create the menubar with all sub menus. (fileMenu, comMenu, etc...)
        """
        self._menubar = Menu(self._root, tearoff=False)
        self._root.config(menu=self._menubar)

        ###################### fileMenu ################################
        self._fileMenu = Menu(self._menubar, tearoff=False)
        self._fileMenu.add_command(label="Save File...", command=self._onSaveFile)
        self._fileMenu.add_command(label="Exit", underline=0, command=self.destroy)

        ######################### comMenu ###############################
        self._comMenu = Menu(self._menubar, tearoff=False)
        self._comMenu.add_command(label="Refresh", underline=0, command=self._onRefreshCOMList)
        self._comMenu.add_separator()

        #################################################################
        self._menubar.add_cascade(label="File", underline=0, menu=self._fileMenu)
        self._menubar.add_cascade(label="COM", underline=0, menu=self._comMenu)

    def mainloop(self):
        """
        Main loop of GUI. Starts GUI main loop in current thread.
        """
        self._root.mainloop()

    def destroy(self):
        """
        Destroy GUI.
        """
        self._root.destroy()

    def setTitle(self, title):
        """
        Set title label to given string.
        :param title: Text as string
        """
        self._titleLabel['text'] = str(title)

    def setSize(self, size):
        """
        Set size label to given string.
        :param size: Size as string
        """
        self._sizeLabel['text'] = str(size)

    def setType(self, type):
        """
        Set type label to given string.
        :param type: Type as string.
        """
        self._typeLabel['text'] = str(type)

    def setFlag(self, flag):
        """
        Set flag label to given string.
        :param flag: Flag as string.
        """
        self._flagLabel['text'] = str(flag)

    def setBanks(self, banks):
        """
        Set banks label to given string
        :param banks: Banks value as string
        """
        self._banksLabel['text'] = str(banks)

    def setInfoButtonEnabled(self, enabled):
        """
        Enable or disable the load info button.
        :param enabled: Enabled/disabled as boolean
        """
        if enabled:
            self._infoButton['state'] = 'normal'
        else:
            self._infoButton['state'] = 'disabled'

    def setReadButtonEnabled(self, enabled):
        """
        Enable or disable the read button.
        :param enabled: Enabled/disabled as boolean
        """
        if enabled:
            self._readButton['state'] = 'normal'
        else:
            self._readButton['state'] = 'disabled'

    def setStartButtonEnabled(self, enabled):
        """
        Enable or disable the start button.
        :param enabled: Enabled/disabled as boolean
        """
        if enabled:
            self._startButton['state'] = 'normal'
        else:
            self._startButton['state'] = 'disabled'

    def setProgress(self, current, max):
        """
        Set value of progressbar to specific value.
        :param current: Current value of progressbar as int
        """
        percent = int(current/max * 100)
        if percent != self._progress['value']:
            self._progress['value'] = percent

    def setImage(self, image):
        """
        Set nintendo logo image to given image
        :param image: Image as Image
        """
        image = image.resize((48 * 5, 8 * 5))
        photo = itk.PhotoImage(image)
        self._nintendoLogo['image'] = photo
        self._nintendoLogo.image = photo

    def setError(self, error):
        """
        Set error message in bottom of GUI.
        :param error: Error message as string
        """
        self._errorLabel['text'] = error

    def setCOMList(self, comList):
        """
        Set list of COM ports to the COM list submenu in menubar.
        :param comList: List of COM devices
        """
        self._comMenu.delete(2, END)
        for com in comList:
            self._comMenu.add_radiobutton(label=com.device+' - '+com.description, command=lambda: self._onChangeCOMDevice(com.device))
