#!/usr/bin/python3

"""
    @file   commmunicationHandler.py
    
    @brief  
    @date   10.03.23 
    @author Thomas Matre
"""

#todo test if all datatypes is converted correctly
from canHandler import Canbus
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
  canID, *idData = tags
  idDataByte = []
  for data in idData:
    try:
      idDataByte += struct.pack(can_types[data[0]], *data[1:])
    except struct.error as e:
      print(f"Error: {e}")
      print(f"data={data}, format={data[0]}, value={data[1:]}")
      print(f"idDataByte={idDataByte}")
  return can.Message(arbitration_id=canID, data=idDataByte, is_extended_id=False)

#decodes packs
def packetDecode(msg):
  canID = msg.arbitration_id
  dataByte = msg.data
  try:
    if canID == 100:
      pack1 = getNum("int16", dataByte[0:2])
      pack2 = getNum("int16", dataByte[2:4])
      pack3 = getNum("int16", dataByte[4:6])
      pack4 = getNum("int16", dataByte[6:8])
      jsonDict = {"name10": (pack1, pack2, pack3, pack4)}
    elif canID == 52:
      pack1 = getNum("int32", dataByte[0:4])
      pack2 = getNum("int8",  dataByte[4])
      pack3 = getNum("uint8", dataByte[5])
      pack4 = getNum("uint16", dataByte[6:8])
      jsonDict = {"name52": (pack1, pack2, pack3, pack4)}
    else:
      print(f"Unknown CanID: {canID} recived from ROV system")
      jsonDict = {"Error": f"Unknown CanID: {canID} recived from ROV system"}
  except TypeError as e:
     jsonDict = {"Error": e}
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
                #print(melding)
                netCallback(msg)
        except ValueError as e:
            print(f'Feilkode i network thread feilmelding: {e}\n\t{msg}')
            break
    netHandler.exit()
    print(f'Network thread stopped')


class ComHandler:
  def __init__(self, 
               ip:str='0.0.0.0',
               port:int=6900
               ) -> None:

    self.status = {'Net': False, 'Can': False}
    self.canFilters = [{"can_id" : 0x60 , "can_mask" : 0xF8, "extended" : False }]
    #activate can in os sudo ip link set can0 type can bitrate 500000 etc.
    #check if can is in ifconfig then
    self.Can = Canbus()
    self.connectIp = ip
    self.connectPort = port
    self.netInit()

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
                            self.netHandler.send(to_json("Error: Canbus not initialised"))
        except Exception as e:
            print(f'Feilkode i netCallback, feilmelding: {e}\n\t{message}')

  
  def sendPacket(self, tag):
    packet = packetBuild(tag)
    assert self.bus is not None
    try:    #self.listner = can.Listener()
      self.bus.send(packet)
    except Exception as e:
      raise e

  def readPacket(self, can):

        try:
          msg = packetDecode(can)
          self.netHandler.send(msg)
        except Exception as e:
          raise e


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
