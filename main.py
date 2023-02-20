#!/usr/bin/python3.6.9
# -*- coding: UTF-8 -*-

import multiprocessing
from multiprocessing.dummy import Array
import time
import threading
import json
import os
import net_handler
os.chdir(os.path.dirname(os.path.abspath(__file__))) # Bytter working directory til den nåværende slik at programmet kan startes utenfra mappa

# Our main loop for both programs
def main_loop():
    #m = Mercury()
    c = net_handler.ComHandler()
    while(1):
        c.readPacket
        c.sendPacket

if __name__ == "__main__":
    main_loop()
