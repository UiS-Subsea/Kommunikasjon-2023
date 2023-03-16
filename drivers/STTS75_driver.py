#!/usr/bin/python3

"""
    @file   STTS75.py
    
    @brief  Driver til STTS75M2F temperatursensor
    @date   10.03.23 
    @author Håvard Syslak
"""

from smbus2 import SMBus, i2c_msg
import time

class STTS75():
    def __init__(self):
        self.i2c_addr =  0x48
        self.bus = SMBus(0)

    def read_temp(self):
        self.bus.write_byte_data(self.i2c_addr, 0, 0)
        data = self.bus.read_i2c_block_data(self.i2c_addr, 0, 2)
        self.temp = float(((data[0] << 8) | data[1]) / 256)
        return self.temp

         
if __name__ == "__main__":
    t = STTS75()
    while True:
        print("1")
        print(t.read_temp())
        time.sleep(1)