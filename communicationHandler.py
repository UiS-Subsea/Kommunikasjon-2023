#!/usr/bin/python3

"""
    @file   commmunicationHandler.py
    
    @brief  
    @date   10.03.23 
    @author Thomas Matre
"""

#todo test if all datatypes is converted correctly
import can
import struct
import time
import json
import threading
import sys
import os
import subprocess
from network_handler import Network


can_types = {
    "int8": "<b",
    "uint8": "<B",
    "int16": "<h",
    "uint16": "<H",
    "int32": "<i",
    "uint32": "<I",
    "int64": "<q",
    "uint64": "<Q",
    "float": "<f"
}


def getByte(can_format:str, number):
    return list(struct.pack(can_types[can_format], number))

def getNum(can_format:str, byt):
    if isinstance(byt, int):
        byt = byt.to_bytes(1, byteorder="big")
    return struct.unpack(can_types[can_format], byt)[0]

def getBit(num, bit_nr):
    return (num >> bit_nr) & 1

def setBit(bits: tuple):
    return sum(bit << k for k, bit in enumerate(bits))
#formats to json
def toJson(input):
    packet_sep = json.dumps("*")
    return bytes(packet_sep + json.dumps(input) + packet_sep, "utf-8")

#builds packs for canbus
def packetBuild(tags):
  if tags == (63 or 95 or 125 or 126 or 127): 
    canID = tags
    msg = 'marco/n'
  else:
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
    print(msg)
  return can.Message(arbitration_id=canID, data=msg, is_extended_id=False)

#decodes packs
def packetDecode(msg):
  canID = msg.arbitration_id
  dataByte = msg.data
  try:
    if 155 <= canID <= 159:
       pack = dataByte[0:6].decode('utf-8')
       jsonDict = {canID: (pack)}
    elif 1 < canID < 150:
      pack1 = getNum("int16", dataByte[0:2])
      pack2 = getNum("int16", dataByte[2:4])
      pack3 = getNum("int16", dataByte[4:6])
      pack4 = getNum("int16", dataByte[6:8])
      jsonDict = {canID: (pack1, pack2, pack3, pack4)}
    elif canID == 52:
      pack1 = getNum("int32", dataByte[0:4])
      pack2 = getNum("int8",  dataByte[4])
      pack3 = getNum("uint8", dataByte[5])
      pack4 = getNum("uint16", dataByte[6:8])
      jsonDict = {canID: (pack1, pack2, pack3, pack4)}
    else:
      print(f"Unknown CanID: {canID} recived from ROV system")
      jsonDict = {"Error": f"Unknown CanID: {canID} recived from ROV system"}
  except TypeError as e:
     jsonDict = {"Error": e}
  print(jsonDict)
  return toJson(jsonDict)


# Reads data from network port
def netThread(netHandler, netCallback, flag):
    print("Server started\n")
    flag['Net'] = True
    while flag['Net']:
        try:
            msg = netHandler.receive()
            if msg == b"" or msg is None:
                continue
            else:
                netCallback(msg)
        except ValueError as e:
            print(f'Feilkode i network thread feilmelding: {e}\n\t{msg}')
            break
    netHandler.exit()
    print(f'Network thread stopped')

def hbThread(canSend, flag):
    print("Heartbeat thread started")
    while flag['Can']:
      canSend(63)
      time.sleep(0.1)
      canSend(95)
      time.sleep(0.1)
      canSend(125)
      time.sleep(0.1)
      canSend(126)
      time.sleep(0.1)
      canSend(127)
      time.sleep(2)
    print("Heartbeat thread stopped")

class ComHandler:
  def __init__(self, 
               ip:str='0.0.0.0',
               port:int=6900,
               canifaceType:str='socketcan',
               canifaceName:str='can0') -> None:
    self.canifaceType  = canifaceType
    self.canifaceName  = canifaceName
    self.status = {'Net': False, 'Can': False}
    #self.canFilters = [{"can_id" : 0x60 , "can_mask" : 0xF8, "extended" : False }]
    self.canFilters = [{"can_id" : 0x00 , "can_mask" : 0x00, "extended" : False }]
    #activate can in os sudo ip link set can0 type can bitrate 500000 etc.
    #check if can is in ifconfig then
    self.canInit()
    self.connectIp = ip
    self.connectPort = port
    self.netInit()
    self.heartBeat()

  def netInit(self):
    self.netHandler = Network(is_server=True, 
                              bind_addr=self.connectIp,
                              port     =self.connectPort)
    while self.netHandler.waiting_for_conn:
        time.sleep(1)
    self.toggleNet()

  def toggleNet(self):
    if self.status['Net']:
        # This will stop network thread
        self.status['Net'] = False
    else:
        self.netTrad = threading.Thread(name="Network_thread",target=netThread, daemon=True, args=(self.netHandler, self.netCallback, self.status))
        self.netTrad.start()

  def netCallback(self, data: bytes) -> None:
    data:str = bytes.decode(data, 'utf-8')
    for message in data.split(json.dumps("*")):
        try:
            if message == json.dumps('heartbeat') or message == "":
                if message is None:
                    message = ""
                continue
            else:
                message = json.loads(message)
                for item in message:
                    if item[0] < 200:
                        if self.status['Can']:
                            if item[0] == 100: 
                                msg = {item[0],
                                   {'int16', int(item[1])},
                                   {'int16', int(item[2])},
                                   {'int16', int(item[3])},
                                   {'int16', int(item[4])}
                                   }
                                self.sendPacket(msg)
                            elif item[0] == 64:
                                msg = {item[0],
                                   {'int16', int(item[1])}, {'int16', int(item[2])}, {'int16', int(item[3])}, {'int16', int(item[4])}
                                   }
                                self.sendPacket(msg)
                        else:
                            self.netHandler.send(toJson("Error: Canbus not initialised"))
        except Exception as e:
            print(f'Feilkode i netCallback, feilmelding: {e}\n\t{message}')

  def canInit(self):
    self.bus = can.Bus(
      interface             = self.canifaceType,
      channel               = self.canifaceName,
      receive_own_messages  = False,
      fd                    = False)
    self.bus.set_filters(self.canFilters)
    self.status['Can'] = True
    self.notifier = can.Notifier(self.bus, [self.readPacket])
    self.timeout = 0.1 # todo kan denne fjernes?

  
  def sendPacket(self, tag):
    packet = packetBuild(tag)
    assert self.bus is not None
    try:
      self.bus.send(packet)
    except Exception as e:
      raise e

  def readPacket(self, can):
        self.bus.socket.settimeout(0)
        try:
          msg = packetDecode(can)
          self.netHandler.send(msg)
        except Exception as e:
          raise e
        
  def heartBeat(self):
    print("Trying to start hb thread")
    self.heartBeatThread = threading.Thread(name="hbThread",target=hbThread, daemon=True, args=(self.sendPacket, self.status))
    self.heartBeatThread.start()


if __name__ == "__main__":
# tag = (type, value)
  tag0 = ("int16", 16550)
  tag1 = ("int8", 120)
  tag2 = ("uint8", 240)
  tag3 = ("uint16", 50000 )
  tag4 = ("int16", -20000)
# tags = (id, tag0
# tag1, tag2, tag3, tag4, tag5, tag6, tag7) ex. with int8 or uint8
  tags = (10, tag0, tag1, tag2, tag3, tag4)
  c = ComHandler()
  while True:
    time.sleep(0.1)
