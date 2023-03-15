#!/usr/bin/python3.6.9
# -*- coding: UTF-8 -*-

import multiprocessing
from multiprocessing.dummy import Array
import time
import threading
import json
import os
import communicationHandler
from STTS75_driver import STTS75
os.chdir(os.path.dirname(os.path.abspath(__file__))) # Bytter working directory til den nåværende slik at programmet kan startes utenfra mappa

# Our main loop for both programs
def main_loop():
    c = communicationHandler.ComHandler()
    while True:
        c.readPacket()
        c.sendPacket()

if __name__ == "__main__":
    main_loop()
