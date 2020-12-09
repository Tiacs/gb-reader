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

import serial, time
from enum import Enum


class GBReader:
    cartridgeTypes = {0x00: "ROM ONLY", 0x01: "MBC1", 0x02: "MBC1+RAM", 0x03: "MBC1+RAM+BATTERY", 0x05: "MBC2",
                      0x06: "MBC2+BATTERY", 0x08: "ROM+RAM", 0x09: "ROM+RAM+BATTERY", 0x0B: "MMM01", 0x0C: "MMM01+RAM",
                      0x0D: "MMM01+RAM+BATTERY", 0x0F: "MBC3+TIMER+BATTERY", 0x10: "MBC3+TIMER+RAM+BATTERY",
                      0x11: "MBC3", 0x12: "MBC3+RAM", 0x13: "MBC3+RAM+BATTERY", 0x15: "MBC4", 0x16: "MBC4+RAM",
                      0x17: "MBC4+RAM+BATTERY", 0x19: "MBC5", 0x1A: "MBC5+RAM", 0x1B: "MBC5+RAM+BATTERY",
                      0x1C: "MBC5+RUMBLE", 0x1D: "MBC5+RUMBLE+RAM", 0x1E: "MBC5+RUMBLE+RAM+BATTERY",
                      0xFC: "POCKET CAMERA", 0xFD: "BANDAI TAMA5", 0xFE: "HUC3", 0xFF: "HUC1+RAM+BATTERY"}

    def __init__(self, port):
        try:
            self.port = port
            self.ser = serial.Serial(port, 76800, timeout=2) # 76800

            time.sleep(2)  # connection needs 2 seconds to be established
        except serial.serialutil.SerialException:
            raise NoGBReaderException()

        if not self._performHandshake():
            raise NoGBReaderException()

    def close(self):
        self.ser.close()

    def readCartridgeHeader(self):
        cartridgeType = self._parseCartridgeType(self._readCartridgeType())

        romSize = self._readROMSize()
        romSizeKB = self._parseROMSizeKB(romSize)
        romBankCount = self._parseROMBankCount(romSize)

        cgbFlag = self._parseCGBFlag(self._readCGBFlag())
        gameTitle = self._readGameTitle(cgbFlag)
        nintendoLogo = self._readNintendoLogo()
        globalChecksum = self._parseGlobalChecksum(self._readGlobalChecksum())

        return GBCartridge(cartridgeType, romSizeKB, romBankCount, cgbFlag, gameTitle, nintendoLogo, globalChecksum)

    def readGameData(self, cartridge, progressFunction):
        globalChecksum = self._parseGlobalChecksum(self._readGlobalChecksum())

        if globalChecksum != cartridge.globalChecksum:
            raise GBCartridgeChangedException('checksum_changed')

        romSize = self._readROMSize()
        cartridge.romSizeKB = self._parseROMSizeKB(romSize)
        cartridge.romBankCount = self._parseROMBankCount(romSize)

        cartridge.gameData = self._readGameData(cartridge.romSizeKB, progressFunction)
        return cartridge.gameData

    def saveROMFile(self, cartridge, file):
        for byte in cartridge.gameData:
            file.write(byte)

    def checkGlobalChecksum(self, cartridge):
        checksum = 0
        for address in range(0x0000, len(cartridge.gameData)):
            if not (address == 0x014E or address == 0x014F):
                checksum += ord(cartridge.gameData[address])

        return (checksum & 0xFFFF) == cartridge.globalChecksum

    #######################################################################################
    # Parsing methods
    #####
    def _parseCartridgeType(self, key):
        if key in self.cartridgeTypes:
            return self.cartridgeTypes[key]
        else:
            raise UnknownGBDataException('unknown_type')

    def _parseROMSizeKB(self, romSize):
        if romSize <= 7:
            return 2 ** romSize * 32
        elif romSize == 0x52:
            return 1126.4
        elif romSize == 0x53:
            return 1228.8
        elif romSize == 0x54:
            return 1536
        else:
            raise UnknownGBDataException('unknown_rom_size')

    def _parseROMBankCount(self, romSize):
        if romSize <= 7:
            return 2 ** (romSize + 1)
        elif romSize == 0x52:
            return 72
        elif romSize == 0x53:
            return 80
        elif romSize == 0x54:
            return 96
        else:
            raise UnknownGBDataException('unknown_bank_count')

    def _parseCGBFlag(self, cgbFlag):
        if cgbFlag == 0x80:
            return CGBFlag.CGB_SUPPORT
        elif cgbFlag == 0xC0:
            return CGBFlag.CGB_ONLY
        else:
            return CGBFlag.UNDEFINED

    def _parseGlobalChecksum(self, globalChecksum):
        return (ord(globalChecksum[0]) << 8) + ord(globalChecksum[1])

    ######################################################################################
    # Reading methods
    #####
    def _performHandshake(self):
        self.ser.write([0x01])
        c = self.ser.read(1)
        try:
            return ord(c) == 0xA0  # reader sbould return 0xA0 after receiving 0x01
        except TypeError:
            return False

    def _readCartridgeType(self):
        self.ser.write([0x02])
        c = self.ser.read(1)
        return ord(c)

    def _readROMSize(self):
        self.ser.write([0x03])
        c = self.ser.read(1)
        return ord(c)

    def _readCGBFlag(self):
        self.ser.write([0x04])
        c = self.ser.read(1)
        return ord(c)

    def _readGameTitle(self, cgbFlag):
        self.ser.write([0x05])
        title = ""
        for i in range(0x0134, 0x0143+1):
            byte = self.ser.read(1)
            try:
                title += byte.decode("ascii")
            except UnicodeDecodeError:
                continue

        if cgbFlag == CGBFlag.CGB_ONLY or cgbFlag == CGBFlag.CGB_SUPPORT:
            return title[:11]
        else:
            return title[:16]


    def _readNintendoLogo(self):
        self.ser.write([0x06])
        data = []
        for i in range(0x0104, 0x0133 + 1):
            byte = self.ser.read(1)
            data.append(byte)
        return data

    def _readGlobalChecksum(self):
        self.ser.write([0x08])
        data = []
        for i in range(0x014E, 0x014F + 1):
            byte = self.ser.read(1)
            data.append(byte)
        return data

    def _readGameData(self, romSizeKB, progressFunction):
        self.ser.write([0x07])
        data = []
        for i in range(0x0000, romSizeKB * 1024):
            byte = self.ser.read(1)
            data.append(byte)

            progressFunction(i+1, romSizeKB * 1024)

        return data


class NoGBReaderException(Exception):
    pass


class UnknownGBDataException(Exception):
    pass


class GBCartridgeChangedException(Exception):
    pass


class CGBFlag(Enum):
    CGB_SUPPORT = 0
    CGB_ONLY = 1
    UNDEFINED = 2


class GBCartridge:

    def __init__(self, cartridgeType, romSizeKB, romBankCount, cgbFlag, gameTitle, nintendoLogo, globalChecksum):
        self.cartridgeType = cartridgeType
        self.romSizeKB = romSizeKB
        self.romBankCount = romBankCount
        self.cgbFlag = cgbFlag
        self.gameTitle = gameTitle
        self.nintendoLogo = nintendoLogo
        self.globalChecksum = globalChecksum#
        self.gameData = None