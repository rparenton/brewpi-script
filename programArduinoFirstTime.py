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

import os
import sys
from configobj import ConfigObj

import programArduino as programmer
import BrewPiUtil as util

# Read in command line arguments
if len(sys.argv) < 2:
        print >> sys.stderr, 'Using default base directory ./, to override use:  %s <base directory full path>' % sys.argv[0]
        basePath = './'
else:
        basePath = sys.argv[1]

defaultConfigFile = basePath + 'settings/defaults.cfg'
userConfigFile = basePath + 'settings/config.cfg'

if not os.path.exists(defaultConfigFile):
        sys.exit('ERROR: Config file "%s" was not found!' % defaultConfigFile)
if not os.path.exists(userConfigFile):
        sys.exit('ERROR: Config file "%s" was not found!' % userConfigFile)

defaultConfig = ConfigObj(defaultConfigFile)
userConfig = ConfigObj(userConfigFile)
config = defaultConfig
config.merge(userConfig)

hexFile = config['wwwPath'] + 'uploads/brewpi-leonardo-revA.hex'
boardType = config['boardType']

result = programmer.programArduino(config, boardType, hexFile, {'settings': False, 'devices': False})

print result
