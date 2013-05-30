#!/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/local/games:/usr/games

# Set base path
if [ "$#" -eq 0 ]; then
    basePath=/home/brewpi/
else
    basePath=$1
fi

# Define config files
defaultConfigFile="${basePath}settings/defaults.cfg"
userConfigFile="${basePath}settings/config.cfg"

# Make sure config files exist
if [ ! -f $defaultConfigFile ]; then
    echo "ERROR: Config file \"${defaultConfigFile}\" does not exist."
    echo "Verify the file exists and/or specify the full path to a valid BrewPi directory by running:"
    echo "  check-running.sh <base directory full path>"
    exit 1
fi

if [ ! -f $userConfigFile ]; then
    echo "ERROR: Config file \"${userConfigFile}\" does not exist."
    echo "Verify the file exists and/or specify the full path to a valid BrewPi directory by running:"
    echo "  check-running.sh <base directory full path>"
    exit 1
fi

# Read in config files (defaults.cfg first, then config.cfg for user overrides)
while read line; do
    if [ -z "$line" ]; then continue; fi
    var=$(echo $line | cut -d '=' -f1)
    val=$(echo $line | cut -d '=' -f2)
    value=$(echo $val) # remove whitespace around =
    variable=$(echo $var) 
    eval "$variable=\"$value\""
done < $defaultConfigFile

while read line; do
    if [ -z "$line" ]; then continue; fi
    var=$(echo $line | cut -d '=' -f1)
    val=$(echo $line | cut -d '=' -f2)
    value=$(echo $val) # remove whitespace around =
    variable=$(echo $var) 
    eval "$variable=\"$value\""
done < $userConfigFile

if [ "$(ps ax | grep -v grep | grep brewpi.py | grep $basePath)" != "" ]; then
    echo "brewpi running, everything is fine"
    exit 0
else
    if [ -e "${wwwPath}do_not_run_brewpi" ]; then
        echo "do_not_run_brewpi file exists, not restarting"
    else
        # check if serial port exists
        if [ -e $port ]; then
            echo "Serial port found, but brewpi not running, restarting brewpi"
            echo "brewpi script not found running by CRON, restarting brewpi" >> ${scriptPath}logs/stderr.txt
            # overwrite stdout, append to stderr
            # -u flag causes stdout to write to file immediately and not cache output
            python -u ${scriptPath}brewpi.py $basePath 1> ${scriptPath}logs/stdout.txt 2>>${scriptPath}logs/stderr.txt &
        else
            uptime=$(cat /proc/uptime)
            uptime=${uptime%%.*}

            if [ $uptime -gt 600 ]; then
                echo "Serial port not found by CRON, restarting Raspberry Pi" >> ${scriptPath}logs/stderr.txt
                sudo reboot
            else
                echo "Serial port not found by CRON, but will not reboot in first 10 minutes after boot" >> ${scriptPath}logs/stderr.txt
            fi
        fi
    fi
fi

exit 0

# This script checks whether the python script is running. If it is not running, it starts the script.
# A dontrun file is written if the script is stopped manually, so CRON will not restart it.
# When the Raspberry Pi has lost it's serial port, it will restart the pi. But only after more then 10 minutes after booting.
# To disable this file, remove from the brewpi user's crontab or create the do_not_run_brewpi file: touch /var/www/do_not_run_brewpi
