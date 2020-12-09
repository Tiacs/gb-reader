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

# Author: Fabian Friedl
# Date: 16.12.2016
# Description:
# 		Python module for converting NintendoLogo Data from the Nintendo GameBoy to image file.
#       NOTICE: This file needs Image library installed to work.
#                   ("python -m pip install Image")

from PIL import Image, ImageDraw


class NintendoLogo:
    def __init__(self, data):
        self._data = data
        if len(data) != 48:
            raise NoNintendoLogoException('Invalid length. Does not match length of 48!')

        self._drawImage()

    def saveImage(self, filename, format='PNG'):  # save image to specific file with specific format
        self._img.save(filename, format)

    def getImage(self):  # return PIL image object of drawn logo
        return self._img

    def _drawImage(self):  # draws image
        # bounds: 48x8
        self._img = Image.new('RGB', (48, 8), "white")
        self._draw = ImageDraw.Draw(self._img)

        # first half
        for i in range(0, 24, 2):
            self._drawByte(i * 2, 0, self._data[i])
            self._drawByte(i * 2, 2, self._data[i + 1])

        # second half
        for i in range(0, 24, 2):
            self._drawByte(i * 2, 4, self._data[i + 24])
            self._drawByte(i * 2, 6, self._data[i + 24 + 1])

    def _drawByte(self, x, y, byte):  # draw one byte to certain position
        for line in range(0, 2):  # go through each line of byte
            for n in range(0, 4):  # go through each n of byte
                if ord(byte) & 1 << n + (line * 4):  # check if bit is set (+line*4  -> offset for second line)
                    self._draw.rectangle([(x + 3 - n, y + 1 - line), (x + 3 - n, y + 1 - line)], fill="black")


class NoNintendoLogoException(Exception):
    pass
