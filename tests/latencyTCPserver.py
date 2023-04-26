#!/usr/bin/python3
"""
    @file   latencyClient.py
    
    @brief  
    @date   30.03.23 
    @author Thomas Matre
"""
import socket, json

def toJson(input):
  packet_sep = json.dumps("*")
  return bytes(packet_sep + json.dumps(input) + packet_sep, "utf-8")

def netHandler(ip, port, meld):
  network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  network_socket.bind((ip, port))
  network_socket.listen()
  conncection, network_address = network_socket.accept()
  while True:
    try:
      recmeld = conncection.recv(1024)
      data:str = bytes.decode(recmeld, 'utf-8')
      for message in data.split(json.dumps("*")):
        if message == "":
          if message is None:
            message = ""
            continue
        else:  
            output = message
      conncection.sendall(toJson(output))
    except Exception as e:
      break
  return "Test finished"


if __name__ == "__main__":
    print("Main=client")
    msg = [[9, [0, 1, 2, 3, 4, 5, 6, 7]]]
    meld = toJson(msg)
    ip = "0.0.0.0"
    port = 6900
    svar = print(netHandler(ip, port, meld))