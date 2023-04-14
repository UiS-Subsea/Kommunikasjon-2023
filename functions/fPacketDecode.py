#!/usr/bin/python3

"""
    @file   commmunicationHandler.py
    
    @brief  Decode CAN messages and parse to TCP messages
    @date   10.03.23 
    @author Thomas Matre
"""

from functions.fFormating import getBit, getByte, getNum, setBit, toJson
from functions.fPackedDecodeParsing import canint16Parse, canint8Parse, canSensorAlarmsParse, canuint16Parse, canuint8Parse, canHBParse

#Packets recived from ROV over canbus to be parsed and sent to TOPSIDE
THRUSTPAADRAG = 129
AKSELERASJON  = 135
GYRO          = 136
MAGNETOMETER  = 137
VINKLER       = 138
TEMPDYBDE     = 139
SENSORERROR   = 140
HBREG         = 155
HBSENSOR      = 156
HB12VMAN      = 157
HB12VTHR      = 158
HB5V          = 159

canReciveDict = {
    THRUSTPAADRAG:  canint8Parse,
    AKSELERASJON:   canint16Parse,
    GYRO:           canint16Parse,
    MAGNETOMETER:   canint16Parse,
    VINKLER:        canint16Parse,
    TEMPDYBDE:      canint16Parse,
    SENSORERROR:    canSensorAlarmsParse,
    HBREG:          canHBParse,
    HBSENSOR:       canHBParse,
    HB12VMAN:       canHBParse,
    HB12VTHR:       canHBParse,
    HB5V:           canHBParse
  }

def packetDecode(msg, ucFlags):
  canID = msg.arbitration_id
  dataByte = msg.data
  try:
    if canID in canReciveDict:
      jsonDict = canReciveDict[canID](canID, dataByte, ucFlags)
    else:
      print(f"CanID: {canID} recived from ROV system not in parsing dict")
      jsonDict = {"Error": f"CanID: {canID} recived from ROV system not in parsing dict"}
  except TypeError as e:
     jsonDict = {"Error": e}
  return toJson(jsonDict)