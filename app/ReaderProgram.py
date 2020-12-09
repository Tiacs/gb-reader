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

from tkinter.filedialog import asksaveasfile
from tkinter.messagebox import showerror, showinfo

import subprocess
import sys
import os
import serial.tools.list_ports as list_ports

from GUI import GUI
from GBReader import *
from NintendoLogo import NintendoLogo
from threading import Thread


class ReaderProgram:

    def __init__(self):
        self.gui = GUI(self.readHeader, self.readGame, self.startGame, self.refreshCOMList, self.changeCOMDevice, self.saveFile)

        self._reader = None
        self._cartridge = None

    def run(self):
        self._reader = None
        #self.initReader("COM1")
        self.gui.mainloop()

    def initReader(self, com):
        self.gui.setError("")
        self.gui.setInfoButtonEnabled(False)
        self.gui.setReadButtonEnabled(False)
        self.gui.setStartButtonEnabled(False)
        try:
            if self._reader is not None:
                self._reader.close()
            self._reader = GBReader(com)

            self.gui.setInfoButtonEnabled(True)
        except NoGBReaderException as e:
            self.gui.setError("No GBC Reader connected at " + com + "!")
            sys.stdout.write("\033[31mNo GBC Reader connected at" + com + "!\n")
            sys.stdout.write("\033[31mFurther information:\n")
            print(e)

    def readHeader(self):
        self.gui.setError("")
        self.gui.setInfoButtonEnabled(True)
        self.gui.setReadButtonEnabled(False)
        self.gui.setStartButtonEnabled(False)

        try:
            self._cartridge = self._reader.readCartridgeHeader()
            self.gui.setTitle(self._cartridge.gameTitle)
            self.gui.setFlag(self._cartridge.cgbFlag)
            self.gui.setSize(str(self._cartridge.romSizeKB) + " KB")
            self.gui.setType(self._cartridge.cartridgeType)
            self.gui.setBanks(self._cartridge.romBankCount)

            logo = NintendoLogo(self._cartridge.nintendoLogo)  # create nintendo logo from data
            self.gui.setImage(logo.getImage())

            self.gui.setReadButtonEnabled(True)
        except serial.serialutil.SerialException:
            self.gui.setError("No GBC Reader connected!")
            sys.stdout.write("\033[31mNo GBC Reader connected!\n")
        except UnknownGBDataException as e:
            self.gui.setError("Undefined data read from the cartridge! Are you sure a cartridge is connected?")
            sys.stdout.write("\033[31mError loading CartridgeHeader! Unknown Data!\n")
            sys.stdout.write("\033[31mFurther information:\n")
            print(e)



    def readGame(self):
        self.gui.setError("")
        self.gui.setInfoButtonEnabled(False)
        self.gui.setReadButtonEnabled(False)
        self.gui.setStartButtonEnabled(False)

        thread = Thread(target=self._readGame)
        thread.start()

    def _readGame(self):
        try:
            self._reader.readGameData(self._cartridge, self.gui.setProgress)
            self.gui.setInfoButtonEnabled(True)
            self.gui.setReadButtonEnabled(True)
            self.gui.setStartButtonEnabled(True)

            if self._reader.checkGlobalChecksum(self._cartridge):
                print('Checksum correct!')
            else:
                self.gui.setError("Checksum incorrect! A real Game Boy would not care.")
                print('Checksum incorrect!')
        except GBCartridgeChangedException as e:
            self.gui.setError("Error loading Cartridge! Cartridge has changed since reading header information! Please try again!")
            sys.stdout.write("\033[31mError loading Cartridge! Cartridge has changed since reading header information!\n")
            sys.stdout.write("\033[31mPlease try again!\n")

    def startGame(self):
        self.gui.setError("")
        self.gui.setInfoButtonEnabled(False)
        self.gui.setReadButtonEnabled(False)
        self.gui.setStartButtonEnabled(False)

        thread = Thread(target=self._startGame)
        thread.start()


    def _startGame(self):
        filename = "temp.gb"
        file = open(filename, 'wb')
        self._reader.saveROMFile(self._cartridge, file)
        file.close()

        p = subprocess.Popen("./emulator/bgb.exe run " + filename)
        p.wait()

        os.remove(filename)

        self.gui.setInfoButtonEnabled(True)
        self.gui.setReadButtonEnabled(True)
        self.gui.setStartButtonEnabled(True)

    def saveFile(self):
        if self._cartridge is None or self._cartridge.gameData is None:
            showerror("GameBoy Reader - Error", "You have to read a cartridge first!")
            return

        file = asksaveasfile(mode='wb', initialfile=self._cartridge.gameTitle + '.gbc', filetypes=[('gbc roms', '.gbc')])
        self._reader.saveROMFile(self._cartridge, file)
        showinfo("GameBoy Reader - Done", "Game Boy ROM saved!")

    def refreshCOMList(self):
        ports = list(list_ports.comports())
        self.gui.setCOMList(ports)

    def changeCOMDevice(self, comDevice):
        self.initReader(comDevice)