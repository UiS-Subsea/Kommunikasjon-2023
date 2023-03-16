#!/usr/bin/python3

"""
    @file   packetBuild.py
    
    @brief  
    @date   16.03.23 
    @author Thomas Matre
"""
import can
import struct
from functions.fFormating import getBit
from functions.fFormating import getByte
from functions.fFormating import getNum
from functions.fFormating import setBit
from functions.fFormating import toJson

def packetBuild(tags):
  if tags in [63, 95, 125, 126, 127]: 
    canID = tags
    msg = bytearray('marco/n', 'utf-8')
  else:
    try:
      canID, *idData = tags
      idDataByte = []
      for data in idData:
        try:
          idDataByte += struct.pack(can_types[data[0]], *data[1:])
        except struct.error as e:
          print(f"Error: {e}")
          print(f"data={data}, format={data[0]}, value={data[1:]}")
          print(f"idDataByte={idDataByte}")
        msg = idDataByte
    except ValueError as error:
       return f"Error in building can message: {tags} "
    print(msg)
  return can.Message(arbitration_id=canID, data=msg, is_extended_id=False)