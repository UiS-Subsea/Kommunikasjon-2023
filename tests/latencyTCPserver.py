#!/usr/bin/python3
"""
    @file   latencyServer.py
    
    @brief  
    @date   30.03.23 
    @author Thomas Matre
"""
import can, struct, time, json, threading, socket

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


# Reads data from network port
def netThread(network, netCallback, flag):
  print("Server started\n")
  flag['Net'] = True
  while flag['Net']:
    try:
      msg = network.recv(1024)
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
  def __init__(self, ip:str='0.0.0.0',port:int=6900,) -> None:
    self.status    = {'Net': False}
    self.connectIp = ip
    self.connectPort = port
    self.netInit()

  def netInit(self):
    self.netSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.netSocket.bind((self.connectIp, self.connectPort))
    self.netSocket.listen()
    self.netHandler, self.network_address = self.netSocket.accept()
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
              if item[0] in int8Ids:
                  msg = [[item[0], [item[1][0],item[1][1],item[1][2],item[1][3],item[1][4],item[1][5],item[1][6],item[1][7]]]]
                  self.netSocket.sendall(toJson(msg))
              else: 
                self.netHandler.sendall(toJson(f'Error: canId: {message[0]} not in Parsing list'))                          
      except Exception as e:
            print(f'Feilkode i netCallback, feilmelding: {e}\n\t{message}')


     

if __name__ == "__main__":
  c = ComHandler()
  while True:
    pass
