import board
import busio
from digitalio import DigitalInOut
import binascii

from pygame import mixer
import pygame
import os
import glob
import random
import time
from pathlib import Path

lastcard = 0
currentcard = 1
CID = 0
introStarted = False
songs=[]

# Function to play MP3
def playfile(mixer, song, volume):
    if mixer.music.get_busy():
        mixer.music.stop()
    mixer.music.load(song)
    mixer.music.set_volume(volume)
    mixer.music.play()
        
# Function to stop MP3 playing
def stopfile():
    if mixer.music.get_busy():
        mixer.music.stop()
    
# Function to check if MP3 is playing
def isplaying():
    if mixer.music.get_busy(): return True; return False

#
# NOTE: pick the import that matches the interface being used
#
from adafruit_pn532.i2c import PN532_I2C

# from adafruit_pn532.spi import PN532_SPI
# from adafruit_pn532.uart import PN532_UART

# I2C connection:
i2c = busio.I2C(board.SCL, board.SDA)

# Non-hardware
# pn532 = PN532_I2C(i2c, debug=False)

# With I2C, we recommend connecting RSTPD_N (reset) to a digital pin for manual
# harware reset
reset_pin = DigitalInOut(board.D6)
# On Raspberry Pi, you must also connect a pin to P32 "H_Request" for hardware
# wakeup! this means we don't need to do the I2C clock-stretch thing
req_pin = DigitalInOut(board.D12)
pn532 = PN532_I2C(i2c, debug=False, reset=reset_pin, req=req_pin)

# SPI connection:
# spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
# cs_pin = DigitalInOut(board.D5)
# pn532 = PN532_SPI(spi, cs_pin, debug=False)

# UART connection
# uart = busio.UART(board.TX, board.RX, baudrate=115200, timeout=0.1)
# pn532 = PN532_UART(uart, debug=False)

ic, ver, rev, support = pn532.firmware_version
print("Found PN532 with firmware version: {0}.{1}".format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

#Instantiate single mixer object
mixer.init()

while True:
    # Check if a card is available to read
    uid = pn532.read_passive_target(timeout=0.5) 
    print(".", end="")
    # Try again if no card is available.
    if uid is None:
        print('Waiting for RFID/NFC card...')
        stopfile()
        lastcard = 999999999
        currentcard = 999999998
        introStarted = False
        #continue   
    # Debugging read card
    # print("Found card with UID:", [hex(i) for i in uid])
    # print("Character ID:", pn532.mifare_classic_read_block(21))
    
    try:
        uid_str = binascii.hexlify(bytearray(pn532.read_passive_target(timeout=0.5)))
        cardidentifier= uid_str.decode()
        #charid_str = binascii.hexlify(bytearray(pn532.mifare_classic_read_block(21)))
        #cardidentifier= charid_str.decode()
        
        # Sleep to get decoded UID
        #print('cardidentifier: ' + cardidentifier)
        #time.sleep(999999)
        
        # Play intro
        if introStarted != True:
            playfile(mixer, 'select_sound.mp3', 0.5)
            time.sleep(1)
            my_file = Path('/home/pi/'+cardidentifier+'.mp3')
            if my_file.is_file():
                playfile(mixer, '/home/pi/'+cardidentifier+'.mp3', 0.5) 
            if isplaying() == True:
                introStarted = True
        # Intro complete, play main song
        elif isplaying() != True:
            # Randomize character song
            songlist = os.listdir('/home/pi/'+cardidentifier)
            selected_song=random.choice(songlist)
            print(selected_song)
            # Play randomized song
            playfile(mixer, '/home/pi/'+cardidentifier+'/'+selected_song, 0.5)
    except:
        pass
    

