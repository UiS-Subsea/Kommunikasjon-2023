#!/usr/bin/python3

"""
    @file   fPacketDecodeParsing.py
    
    @brief  Decode CAN messages and parse to TCP messages
    @date   10.03.23 
    @author Thomas Matre
"""

from functions.fFormating import getBit, getByte, getNum, setBit, toJson

def canHBParse(canID, dataByte, ucFlags):
  pack = dataByte[0:6].decode('utf-8')
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
  return {canID: (pack)}
    

def canint16Parse(canID, dataByte, ucFlags):
  pack1 = getNum("int16", dataByte[0:2])
  pack2 = getNum("int16", dataByte[2:4])
  pack3 = getNum("int16", dataByte[4:6])
  pack4 = getNum("int16", dataByte[6:8])
  return {canID: (pack1, pack2, pack3, pack4)}

def canuint16Parse(canID, dataByte, ucFlags):
  pack1 = getNum("uint16", dataByte[0:2])
  pack2 = getNum("uint16", dataByte[2:4])
  pack3 = getNum("uint16", dataByte[4:6])
  pack4 = getNum("uint16", dataByte[6:8])
  return {canID: (pack1, pack2, pack3, pack4)}

def canint8Parse(canID, dataByte, ucFlags):
  pack1 = getNum("int8", dataByte[0])
  pack2 = getNum("int8", dataByte[1])
  pack3 = getNum("int8", dataByte[2])
  pack4 = getNum("int8", dataByte[3])
  pack5 = getNum("int8", dataByte[4])
  pack6 = getNum("int8", dataByte[5])
  pack7 = getNum("int8", dataByte[6])
  pack8 = getNum("int8", dataByte[7])
  return {canID: (pack1, pack2, pack3, pack4, pack5, pack6, pack7, pack8)}

def canuint8Parse(canID, dataByte, ucFlags):
  pack1 = getNum("uint8", dataByte[0])
  pack2 = getNum("uint8", dataByte[1])
  pack3 = getNum("uint8", dataByte[2])
  pack4 = getNum("uint8", dataByte[3])
  pack5 = getNum("uint8", dataByte[4])
  pack6 = getNum("uint8", dataByte[5])
  pack7 = getNum("uint8", dataByte[6])
  pack8 = getNum("uint8", dataByte[7])
  return {canID: (pack1, pack2, pack3, pack4, pack5, pack6, pack7, pack8)}

def canSensorAlarmsParse(canID, dataByte, ucFlags):
  imuErrors     = [False, False, False, False, False, False, False, False]
  tempErrors    = [False, False, False, False]
  pressureErrors= [False, False, False, False]
  lekageAlarms  = [False, False, False, False]
  for i, byte in enumerate(dataByte):
    if i == 0:
      for j in range(8):
        if getBit(byte, j):
          imuErrors[j] = True
        else:
          imuErrors[j] = False
    elif i == 1:
      for j in range(4):
        if getBit(byte, j):
          tempErrors[j] = True
        else:
          tempErrors[j] = False
    elif i == 2:
      for j in range(4):
        if getBit(byte, j):
          pressureErrors[j] = True
        else:
          pressureErrors[j] = False
    elif i == 3:
      for j in range(4):
        if getBit(byte, j):
          lekageAlarms[j] = True
        else:
          lekageAlarms[j] = False
  return {canID: (imuErrors, tempErrors, pressureErrors, lekageAlarms)}