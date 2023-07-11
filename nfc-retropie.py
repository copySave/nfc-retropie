"""
you may need to install python3 and adjust your tabs

This example shows connecting to the PN532 with I2C (requires clock

stretching support), SPI, or UART. SPI is best, it uses the most pins but

is the most reliable and universally supported.

After initialization, try waving various 13.56MHz RFID cards over it!

"""



import os,sys

import time

import psutil

import subprocess

import RPi.GPIO as GPIO



#get files for the NFC reader

#files can be downloaded here: https://www.waveshare.com/w/upload/6/67/Pn532-nfc-hat-code.7z

#then place the folder \Pn532-nfc-hat-code.7z\raspberrypi\python\pn532 in the same dir as this script

from pn532 import *



#setup the LED and turn on

GPIO.setmode(GPIO.BCM)

GPIO.setwarnings(False)

GPIO.setup(14,GPIO.OUT)

GPIO.output(14,GPIO.HIGH)



#load dictionary of games either with an external json file or in this script.
#Uncomment the loading method you want.
#The internal dictionary object can be used as a template for the external json file.

#--begin external dictionary json load file--
#f = open (os.path.join(sys.path[0],"games.json"), "r")

#games = json.loads(f.read())

#f.close()
#--end external json load file--

#--begin internal dictionary--
#games = { 

#   "0x0,0x18,0xeb,0xb5":"nes;nes-game-title-here.nes", 

#    "0x10,0xb7,0xe1,0xb":"atari7800;atari7800-game-title-here.a78"

#    }
#--end internal dictionary--


def killtasks(procnames):

    for proc in psutil.process_iter():

        if proc.name() in procnames:

            pid = str(proc.as_dict(attrs=['pid'])['pid'])

            name = proc.as_dict(attrs=['name'])['name']

            #print("stopping... " + name + " (pid:" + pid + ")")

            subprocess.call(["sudo", "kill", "-15", pid])



if __name__ == '__main__':

    try:

        pn532 = PN532_SPI(debug=False, reset=20, cs=4)



        # ic, ver, rev, support = pn532.get_firmware_version()

        # print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))



        # Configure PN532 to communicate with MiFare cards

        pn532.SAM_configuration()

        loaded = False

        gameCardUID = []

        os.system("clear")
        
        #load an optional "waiting for game"

        #subprocess.Popen(["fbi", "--noverbose", "/home/pi/RetroPie/splashscreens/pic01.jpg"])

        print('Please insert game card...')

        

        while True:

            # Check if a card is available to read

            uid = pn532.read_passive_target(timeout=0.5)

            

            # Try again if no card is available, and end process if removed

            if uid is None:

                  if loaded == True:

                        loaded = False

                        killtasks(["retroarch"])

                        time.sleep(2)

                        #subprocess.Popen(["fbi", "--noverbose", "/home/pi/RetroPie/splashscreens/pic01.jpg"])

                        #print('Please insert game card...')

                  else:

                        continue

            else:

                  gameCardUID = [hex(i) for i in uid]                  

                  if len(gameCardUID) > 0 and loaded == False:

                            #killtasks(["fbi"])

                            #os.system("clear")

                            loaded = True

                            UID = ','.join(gameCardUID)

                            if UID in games:

                                gameInfo = games[UID].split(";")

                                core = gameInfo[0]

                                rom = gameInfo[1]   

                                path = "/home/pi/RetroPie/roms/"+core+"/"+rom                            

                                subprocess.Popen(['/opt/retropie/supplementary/runcommand/runcommand.sh', '0', '_SYS_', core, path])

                            else:

                                print('Found unknown card with UID: ', gameCardUID)

                  elif loaded == True:

                        continue

                    

    except Exception as e:

        print(e)

    finally:

        GPIO.output(14,GPIO.LOW)

        GPIO.cleanup()

