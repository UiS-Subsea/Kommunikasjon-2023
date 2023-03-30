#!/usr/bin/python3
"""
    @file   latencyClient.py
    
    @brief  
    @date   30.03.23 
    @author Thomas Matre
"""
import socket, time, json, statistics

def toJson(input):
  packet_sep = json.dumps("*")
  return bytes(packet_sep + json.dumps(input) + packet_sep, "utf-8")

def netHandler(ip, port, meld):
  network_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  network_socket.settimeout(3)
  time_list = []
  time_listms = []
  message_list = []
  NoOfPacks = 100
  try:
    network_socket.connect((ip, port))
    print(f"Connected to IP:{ip} with PORT:{port}")
    for i in range(5):
        print(i)
        time.sleep(1)
    print("starting to send")
  except Exception as e:
    print(e)
    print("Could not connect to network")
    exit()
  #ping msg
  network_socket.sendall(meld)
  recmeld = network_socket.recv(1024)
  for __ in range(NoOfPacks):
    try:
      start = time.time_ns()
      network_socket.sendall(meld)
      recmeld = network_socket.recv(1024)
      data:str = bytes.decode(recmeld, 'utf-8')
      for message in data.split(json.dumps("*")):
        if "139" in message:
          tid = time.time_ns()-start
          time_list.append(tid)           
    except Exception as e:
            print(e)
            print("Connection lost")
            break
  time.sleep(1)
  print(time_list)
  network_socket.close()
  for i, time_entry in enumerate(time_list):
     newtime = round(float(time_entry)  * (10**-6), 2)
     if newtime >= 3:
       print(f"Entry:{i} with time: {newtime}")
     time_listms.append(newtime)
  print(time_listms)
  print (f'Mean:{statistics.mean(time_listms)}\n Max:{max(time_listms)} \n Min:{min(time_listms)} \n Packets sent: {NoOfPacks} \n Packets recived: {len(time_listms)}')
  return "ok"

if __name__ == "__main__":
    print("Main=client")
    msg = [[9, [0x43, 0x41, 0x4E, 0x42, 0x55, 0x53, 0x53, 0x12]]]
    meld = toJson(msg)
    ip = "10.0.0.2"
    port = 6900
    svar = print(netHandler(ip, port, meld))