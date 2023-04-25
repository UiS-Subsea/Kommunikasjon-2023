#!/usr/bin/python3

"""
    @file   packetBuild.py
    
    @brief  Parse TCP messages to prepare for fPacketBuild
    @date   16.03.23 
    @author Thomas Matre
"""

#standard packs
def int8Parse(item):
  msg = [item[0], 
        ['int8', int(item[1][0])], 
        ['int8', int(item[1][1])], 
        ['int8', int(item[1][2])], 
        ['int8', int(item[1][3])],
        ['int8', int(item[1][4])],
        ['int8', int(item[1][5])],
        ['int8', int(item[1][6])],
        ['int8', int(item[1][7])]]
  return msg

def uint8Parse(item):
  msg = [item[0], 
        ['uint8', int(item[1][0])], 
        ['uint8', int(item[1][1])], 
        ['uint8', int(item[1][2])], 
        ['uint8', int(item[1][3])],
        ['uint8', int(item[1][4])],
        ['uint8', int(item[1][5])],
        ['uint8', int(item[1][6])],
        ['uint8', int(item[1][7])]]
  return msg    

def int16Parse(item):
  msg = [item[0], 
        ['int16', int(item[1][0])], 
        ['int16', int(item[1][1])], 
        ['int16', int(item[1][2])], 
        ['int16', int(item[1][3])]]
  return msg

def uint16Parse(item):
  msg = [item[0], 
        ['uint16', int(item[1][0])], 
        ['uint16', int(item[1][1])], 
        ['uint16', int(item[1][2])], 
        ['uint16', int(item[1][3])]]
  return msg

def int32Parse(item):
  msg = [item[0], 
        ['int32', int(item[1][0])], 
        ['int32', int(item[1][1])]], 
  return msg

def uint32Parse(item):
  msg = [item[0], 
        ['uint32', int(item[1][0])], 
        ['uint32', int(item[1][1])]]
  return msg

def int64Parse(item):
  msg = [item[0], 
        ['int64', int(item[1][0])]], 
  return msg

def uint64Parse(item):
  msg = [item[0], 
        ['uint64', int(item[1][0])]], 
  return msg

#custom packs
def fuselightParse(item):
  msg = [item[0],
        ['uint8', int(item[1][0])],        
        ['uint8', int(item[1][1])], 
        ['uint8', int(item[1][2])], 
        ['uint8', int(item[1][3])],
        ['uint8', int(item[1][4])],
        ['uint8', int(item[1][5])],
        ['uint8', int(item[1][6])],
        ['uint8', int(item[1][7])]]
  print(f"Sending fuse and light flags{item[1]}")
  return msg
def sensorflagsParse(item):
  msg = [item[0],
        ['uint8', int(item[1][0])],
        ['uint8', int(item[1][1])], 
        ['uint8', int(item[1][2])], 
        ['uint8', int(item[1][3])],
        ['uint8', int(item[1][4])],
        ['uint8', int(item[1][5])],
        ['uint8', int(item[1][6])],
        ['uint8', int(item[1][7])]]
  print(f"Sending Sensorflags:{item[1]}")
  return msg

def regParamsParse(item):
  msg = [item[0],
        ['int32', int(item[1][0])],
        ['float', float(item[1][1])]]
  print(f"Sending regParmas ID:{int(item[1][0])} Value:{float(item[1][1])}")
  return msg