import os.path
# Copyright 2012 BrewPi/Elco Jacobs.
# This file is part of BrewPi.

# BrewPi is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# BrewPi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with BrewPi.  If not, see <http://www.gnu.org/licenses/>.

import subprocess as sub
import serial
from time import sleep
import pprint

def fetchBoardSettings(boardsFile, boardType):
    boardSettings = {}
    for line in boardsFile:
        if(line.startswith(boardType)):
              # strip board name, period and \n
            setting = line.replace(boardType + '.', '', 1).strip()
            [key, sign, val] = setting.rpartition('=')
            boardSettings[key] = val
    return boardSettings

def loadBoardsFile(arduinohome):
    return open(arduinohome+'hardware/arduino/boards.txt', 'rb').readlines()

def programArduino(config, boardType, hexFile, port, eraseEEPROM):
    arduinohome = config.get('arduinoHome', '/usr/share/arduino/')  # location of Arduino sdk
    avrdudehome = config.get('avrdudeHome', arduinohome + 'hardware/tools/')  # location of avr tools
    avrsizehome = config.get('avrsizeHome', '')  # default to empty string because avrsize is on path
    avrconf = config.get('avrConf', avrdudehome + 'avrdude.conf')  # location of global avr conf
    returnString = ""

    boardsFile = loadBoardsFile(arduinohome)
    boardSettings = fetchBoardSettings(boardsFile, boardType)

    for line in boardsFile:
        if(line.startswith(boardType)):
              # strip board name, period and \n
            setting = line.replace(boardType + '.', '', 1).strip()
            [key, sign, val] = setting.rpartition('=')
            boardSettings[key] = val

    avrsizeCommand = avrsizehome + 'avr-size ' + hexFile
    returnString = returnString + avrsizeCommand + '\n'
    # check program size against maximum size
    p = sub.Popen(avrsizeCommand, stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
    output, errors = p.communicate()
    if errors != "":
        returnString = returnString + 'avr-size error: ' + errors + '\n'
        return returnString

    returnString = returnString + ('Progam size: ' + output.split()[7] +
        ' bytes out of max ' + boardSettings['upload.maximum_size'] + '\n')

    hexFileDir = os.path.dirname(hexFile)
    hexFileLocal = os.path.basename(hexFile)

    programCommand = (avrdudehome + 'avrdude' +
                ' -F ' +
                ' -p ' + boardSettings['build.mcu'] +
                ' -c ' + boardSettings['upload.protocol'] +
                ' -b ' + boardSettings['upload.speed'] +
                ' -P ' + port +
                ' -U ' + 'flash:w:' + hexFileLocal +
                ' -C ' + avrconf)

    if(eraseEEPROM):
        programCommand = programCommand + ' -e'

    returnString = returnString + programCommand + '\n'

    # open and close serial port at 1200 baud. This resets the Arduino Leonardo
    if(boardType == 'leonardo'):
        ser = serial.Serial(port, 1200)
        ser.close()
        sleep(1)  # give the bootloader time to start up

    p = sub.Popen(programCommand, stdout=sub.PIPE, stderr=sub.PIPE, shell=True,cwd=hexFileDir)
    output, errors = p.communicate()
    # avrdude only uses stderr, append it
    returnString = returnString + errors
    return returnString
