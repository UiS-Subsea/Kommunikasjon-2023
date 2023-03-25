#!/usr/bin/python3

"""
    @file   commmunicationHandler.py
    
    @brief  
    @date   10.03.23 
    @author Thomas Matre
"""

import can
import struct
from functions.fFormating import getBit, getByte, getNum, setBit, toJson


def packetDecode(msg, ucFlags):
  canID = msg.arbitration_id
  dataByte = msg.data
  hbIds        = [155, 156, 157, 158, 159]
  int8Ids      = []
  uint8Ids     = []
  int16Ids     = [134,135,136]
  uint16Ids    = []
  try:
    if canID in hbIds:
      pack = dataByte[0:6].decode('utf-8')
      jsonDict = {canID: (pack)}
      if canID == 155:
        ucFlags['Reg'] = True
      elif canID == 156:
        ucFlags['Sensor'] = True
      elif canID == 157:
        ucFlags['12Vman'] = True
      elif canID == 158:
        ucFlags['12Vthr'] = True
      elif canID == 159:
        ucFlags['5V'] = True
    elif canID in int16Ids:
      pack1 = getNum("int16", dataByte[0:2])
      pack2 = getNum("int16", dataByte[2:4])
      pack3 = getNum("int16", dataByte[4:6])
      pack4 = getNum("int16", dataByte[6:8])
      jsonDict = {canID: (pack1, pack2, pack3, pack4)}
    elif canID in uint16Ids:
      pack1 = getNum("uint16", dataByte[0:2])
      pack2 = getNum("uint16", dataByte[2:4])
      pack3 = getNum("uint16", dataByte[4:6])
      pack4 = getNum("uint16", dataByte[6:8])
      jsonDict = {canID: (pack1, pack2, pack3, pack4)}
    elif canID in int8Ids:
      pack1 = getNum("int8", dataByte[0])
      pack2 = getNum("int8", dataByte[1])
      pack3 = getNum("int8", dataByte[2])
      pack4 = getNum("int8", dataByte[3])
      pack5 = getNum("int8", dataByte[4])
      pack6 = getNum("int8", dataByte[5])
      pack7 = getNum("int8", dataByte[6])
      pack8 = getNum("int8", dataByte[7])
      jsonDict = {canID: (pack1, pack2, pack3, pack4, pack5, pack6, pack7, pack8)}
    elif canID in uint8Ids:
      pack1 = getNum("uint8", dataByte[0])
      pack2 = getNum("uint8", dataByte[1])
      pack3 = getNum("uint8", dataByte[2])
      pack4 = getNum("uint8", dataByte[3])
      pack5 = getNum("uint8", dataByte[4])
      pack6 = getNum("uint8", dataByte[5])
      pack7 = getNum("uint8", dataByte[6])
      pack8 = getNum("uint8", dataByte[7])
      jsonDict = {canID: (pack1, pack2, pack3, pack4, pack5, pack6, pack7, pack8)}
    elif canID == 140:
      sensorAlarms = []
      print(f"in id150 with message: {dataByte}")
      #if not (dataByte[0], 0):
      #  OK = getBit(dataByte[0], 1)
      #  HAL_ERROR = getBit(dataByte[0], 1)
      #  HAL_BUSY = getBit(dataByte[0], 1)
      #  HAL_TIMEOUT = getBit(dataByte[0], 1)
      #  INIT_ERROR = getBit(dataByte[0], 1)
      #  HAL_ERROR = getBit(dataByte[0], 1)
      #  HAL_ERROR = getBit(dataByte[0], 1)
      for i, byte in dataByte:
        if i == 3:
          for j in range(4):
            if getBit(byte, j):
              sensorAlarms.append(f"Lekasje probe: {j+1}. ")
      print(sensorAlarms)
      jsonDict = {"Alarm": f"Sensor: {sensorAlarms}"}

    else:
      print(f"Unknown CanID: {canID} recived from ROV system")
      jsonDict = {"Error": f"Unknown CanID: {canID} recived from ROV system"}
  except TypeError as e:
     jsonDict = {"Error": e}
  return toJson(jsonDict)