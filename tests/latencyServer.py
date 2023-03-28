#!/usr/bin/python3

"""
    @file   commmunicationHandler.py
    
    @brief  
    @date   10.03.23 
    @author Thomas Matre
"""

#todo test if all datatypes is converted correctly
import can, struct, time, json, threading, socket
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
  return toJson(jsonDict)

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
      #This will stop network thread
      self.status['Net'] = False
    else:
      self.netTrad = threading.Thread(name="Network_thread",target=netThread, daemon=True, args=(self.netHandler, self.netCallback, self.status))
      self.netTrad.start()


  def netCallback(self, data: bytes) -> None:
    int8Ids   = [9, 10]
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
            if self.status['Can']:
              if item[0] in int8Ids:
                  msg = int8Parse(item)
                  self.sendPacket(msg)
              else: 
                self.netHandler.send(toJson(f'Error: canId: {message[0]} not in Parsing list'))
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
    self.timeout = 0.1

  def sendPacket(self, tag):
    packet = packetBuild(tag)
    assert self.bus is not None
    try:
      self.bus.send(packet)
    except Exception as e:
      print(f'Feilkode i sendPacket, feilmelding: {e}\n\t{packet}')

  def readPacket(self, can):
    self.bus.socket.settimeout(0)
    try:
      msg = packetDecode(can)
      self.netHandler.send(msg)
    except Exception as e:
      print(f'Feilkode i readPacket, feilmelding: {e}\n\t{can.data}')

     

if __name__ == "__main__":
  c = ComHandler()
  while True:
    time.sleep(0.1)
