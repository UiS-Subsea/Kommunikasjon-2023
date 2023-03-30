#!/usr/bin/python3

"""
    @file   commmunicationHandler.py
    
    @brief  
    @date   10.03.23 
    @author Thomas Matre
"""

#todo test if all datatypes is converted correctly
import can, struct, time, json, threading, socket, statistics
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


def getNum(can_format:str, byt):
  if isinstance(byt, int):
    byt = byt.to_bytes(1, byteorder="big")
  return struct.unpack(can_types[can_format], byt)[0]

def toJson(input):
  packet_sep = json.dumps("*")
  return bytes(packet_sep + json.dumps(input) + packet_sep, "utf-8")

def packetBuild(tags):
  canID, *idData = tags
  idDataByte = []
  for data in idData:
    idDataByte += struct.pack(can_types[data[0]], *data[1:])
  return can.Message(arbitration_id=canID, data=idDataByte, is_extended_id=False)

def packetDecode(msg):
  canID = msg.arbitration_id
  dataByte = msg.data
  int8Ids      = [139]
  if canID in int8Ids:
      pack1 = getNum("int8", dataByte[0])
      pack2 = getNum("int8", dataByte[1])
      pack3 = getNum("int8", dataByte[2])
      pack4 = getNum("int8", dataByte[3])
      pack5 = getNum("int8", dataByte[4])
      pack6 = getNum("int8", dataByte[5])
      pack7 = getNum("int8", dataByte[6])
      pack8 = getNum("int8", dataByte[7])
      jsonDict = {canID: (pack1, pack2, pack3, pack4, pack5, pack6, pack7, pack8)}
  return canID


# Reads data from network port
def netThread(network, netCallback, flag):
  print("Server started\n")
  flag['Net'] = True
  while flag['Net']:
    try:
      msg = network.receive()
      if msg == b"" or msg is None:
        continue
      else:
        netCallback(msg)
    except ValueError as e:
      print(f'Feilkode i network thread feilmelding: {e}\n\t{msg}')
      break
  network.close()
  print(f'Network thread stopped')


class ComHandler:
  def __init__(self, 
               ip:str='0.0.0.0',
               port:int=6900,
               canifaceType:str='socketcan',
               canifaceName:str='can0') -> None:
    self.canifaceType  = canifaceType
    self.canifaceName  = canifaceName
    self.status    = {'Net': False, 
                      'Can': False
                     }
    self.canFilters= [{"can_id": 0x00, 
                       "can_mask": 0x00, 
                       "extended": False 
                      }]
    self.canInit()



  def canInit(self):
    self.bus = can.Bus(
      interface             = self.canifaceType,
      channel               = self.canifaceName,
      receive_own_messages  = False,
      fd                    = False)
    self.bus.set_filters(self.canFilters)

  def sendPacket(self, tag):
    packet = tag
    assert self.bus is not None
    try:
      self.bus.send(packet)
    except Exception as e:
      print(f'Feilkode i sendPacket, feilmelding: {e}\n\t{packet}')

  def readPacket(self):
    self.bus.socket.settimeout(0)
    msg = self.bus.recv()
    try:
      msg = packetDecode(msg)
      return msg
    except Exception as e:
      print(f'Feilkode i readPacket, feilmelding: {e}\n\t{msg}')

     

if __name__ == "__main__":
  time_list = []
  time_listms = []
  NoOfPacks = 1000
  msg_list = []
  i = 0
  buffermsg = can.Message(arbitration_id=9, data=[2,2,2,2,2,2,2,2], is_extended_id=False)
  msg_list.append(can.Message(arbitration_id=9, data=[1,2,3,4,5,6,7,8], is_extended_id=False))
  msg_list.append(can.Message(arbitration_id=9, data=[9,10,11,12,13,14,15,16], is_extended_id=False))
  msg_list.append(can.Message(arbitration_id=9, data=[17,18,19,20,21,22,23,24], is_extended_id=False))

  c = ComHandler()
  time.sleep(2)
  for __ in range(NoOfPacks):
    if i > 3:
      i = 0
    start = time.time()
    c.sendPacket(msg_list[0])
    recmsg = c.readPacket()
    if recmsg == 139:
      tid = time.time()-start
      time_list.append(tid)
    i = i+1
  time.sleep(1)
  for i, time_entry in enumerate(time_list):
     newtime = round(float(time_entry)  * (10**3), 2)
     if newtime >= 3:
       print(f"Entry:{i} with time: {newtime}")
     time_listms.append(newtime)
  print (f'Mean:{statistics.mean(time_listms)}\n Max:{max(time_listms)} \n Min:{min(time_listms)} \n Packets sent: {NoOfPacks} \n Packets recived: {len(time_listms)}')

