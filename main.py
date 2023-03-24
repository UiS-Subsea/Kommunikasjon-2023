#!/usr/bin/python3.6.9
# -*- coding: UTF-8 -*-

import multiprocessing
from multiprocessing.dummy import Array
import time, os , communicationHandler, threading, json
os.chdir(os.path.dirname(os.path.abspath(__file__))) # Bytter working directory til den nåværende slik at programmet kan startes utenfra mappa

# main loop
def main_loop():
  c = communicationHandler.ComHandler()
  while True:
    time.sleep(1)
        

if __name__ == "__main__":
  main_loop()
