#!/usr/bin/python3

"""
    @file   commmunicationHandler.py
    
    @brief  
    @date   10.03.23 
    @author Thomas Matre
"""

#todo test if all datatypes is converted correctly
import can; import struct; import time; import json; import threading; import sys; import os; import subprocess
from drivers.network_handler import Network 
from drivers.STTS75_driver import STTS75; 
from drivers.camPWM import ServoPWM; 
from drivers.camHandler import gstreamerPipe
from functions.fFormating import getBit, getByte, getNum, setBit, toJson
from functions.fPacketBuild import packetBuild; from functions.fPacketDecode import packetDecode
import gi 
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib


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

def hbThread(netHandler, canSend, systemFlag, ucFlags):
    print("Heartbeat thread started")
    hbIds = [63, 95 ,125, 126, 127]
    while systemFlag['Can']:
      for flag in ucFlags:
         ucFlags[flag] = False
      for id in hbIds:
         canSend(id)
         time.sleep(0.1)
      time.sleep(1)
      for flag in ucFlags:
        if not ucFlags[flag]:
          msg = toJson({"Alarm": f"uC {flag} not responding on CANBus"})
          netHandler.send(msg)
          time.sleep(0.2)
    print("Heartbeat thread stopped")

def i2cThread(netHandler, STTS75, systemFlag):
    print("i2c Thread started")
    while systemFlag['Net']:
       temp = STTS75.read_temp()
       msg = toJson({"Temp on Jetson": temp})
       netHandler.send(msg)
       time.sleep(2)
    print("i2c Thread stopped")

class ComHandler:
  def __init__(self, 
               ip:str='0.0.0.0',
               port:int=6900,
               canifaceType:str='socketcan',
               canifaceName:str='can0') -> None:
    self.canifaceType  = canifaceType
    self.canifaceName  = canifaceName
    self.status = {'Net': False, 'Can': False}
    self.uCstatus = {'Reg': False, 'Sensor': False, '12Vman': False, '12Vthr': False, '5V': False}
    self.camStatus = {'Threads': False, 'S1': False, 'S2': False, 'Bottom': False, 'Manipulator': False}
    #self.canFilters = [{"can_id" : 0x60 , "can_mask" : 0xF8, "extended" : False }]
    self.canFilters = [{"can_id" : 0x00 , "can_mask" : 0x00, "extended" : False }]
    #activate can in os sudo ip link set can0 type can bitrate 500000 etc.
    #check if can is in ifconfig then
    self.canInit()
    self.connectIp = ip
    self.connectPort = port
    self.netInit()
    self.heartBeat()
    self.i2cInit()
    self.camInit()

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
                print(message)
                for item in message:
                    if item[0] < 200:
                        print(f"recived netdata: {message}")
                        if self.status['Can']:
                            if item[0] == 100:
                                print(item[0])
                                print[item[1]] 
                                msg = {item[0],
                                   {'int16', int(item[1][0])},
                                   {'int16', int(item[1][1])},
                                   {'int16', int(item[1][2])},
                                   {'int16', int(item[1][3])}}
                                self.sendPacket(msg)
                            elif item[0] == 64:
                                msg = {item[0],
                                   {'int16', int(item[1])}, {'int16', int(item[2])}, {'int16', int(item[3])}, {'int16', int(item[4])}
                                   }
                                self.sendPacket(msg)
                            elif item[0] == 40 or item[0] == 41:
                                print(item[0])
                                print(item[1])
                                msg = {item[0],
                                   {'int8', int(item[1][0])},
                                    {'int8', int(item[1][1])}, 
                                    {'int8', int(item[1][2])}, 
                                    {'int8', int(item[1][3])},
                                    {'int8', int(item[1][4])},
                                    {'int8', int(item[1][5])},
                                    {'int8', int(item[1][6])},
                                    {'int8', int(item[1][7])}
                                   }                               
                            else: 
                               self.netHandler.send(toJson('Error: Unknow can id'))
                    elif item[0] == 200:
                        if item[1] == 'tilt':
                          if item[2] == 1:
                            if not self.camStatus['S1']:
                                self.camStart('stereo1')
                            elif self.camStatus['S1']:
                                self.camStop('stereo1')
                          elif item[2] == 2:
                            if not self.camStatus['S2']:
                                self.camStart('stereo2')
                            elif self.camStatus['S2']:
                                self.camStop('stereo2')
                          elif item[2] == 3:
                            if not self.camStatus['Bottom']:
                                self.camStart('bottom')
                            elif self.camStatus['Bottom']:
                                self.camStop('bottom')                        
                          elif item[2] == 4:
                            if not self.camStatus['Manipulator']:
                                self.camStart('manipulator')
                            elif self.camStatus['Manupulator']:
                                self.camStop('manipulator')                                
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
    #self.timeout = 0.1 # todo kan denne fjernes?

  
  def sendPacket(self, tag):
    packet = packetBuild(tag)
    assert self.bus is not None
    try:
      #print(packet)
      self.bus.send(packet)
    except Exception as e:
      raise e

  def readPacket(self, can):
        self.bus.socket.settimeout(0)
        try:
          msg = packetDecode(can, self.uCstatus)
          self.netHandler.send(msg)
        except Exception as e:
          raise e
        
  def heartBeat(self):
    self.heartBeatThread = threading.Thread(name="hbThread",target=hbThread, daemon=True, args=(self.netHandler, self.sendPacket, self.status, self.uCstatus))
    self.heartBeatThread.start()
  
  def i2cInit(self):
     self.STTS75 = STTS75() 
     self.i2cThread = threading.Thread(name="i2cThread" ,target=i2cThread,daemon=True, args=(self.netHandler, self.STTS75, self.status))
     self.i2cThread.start()

  def camInit(self):
     Gst.init([])
     self.stereo1Pipe = gstreamerPipe(pipeId="stereo1", port="5000")
     self.stereo1Thread = threading.Thread(target=self.stereo1Pipe.run)
     self.stereo1Thread.start()
     self.stereo2Pipe = gstreamerPipe(pipeId="stereo2", port="5001")
     self.stereo2Thread = threading.Thread(target=self.stereo2Pipe.run)
     self.stereo2Thread.start()
     self.bottomPipe = gstreamerPipe(pipeId="bottom", port="5002")
     self.bottomThread = threading.Thread(target=self.bottomPipe.run)
     self.bottomThread.start()
     self.manipulatorPipe = gstreamerPipe(pipeId="manipulator", port="5003")
     #self.manipulatorThread = gstreamerPipe(target=self.manipulatorPipe.run)
     #self.manipulatorThread.start()
     self.camStatus['Threads'] = True

  def camStart(self, pipeId):
     if pipeId == 'stereo1':
        self.stereo1Pipe.runPipe()
        self.camStatus['S1'] = True
     elif pipeId == 'stereo2':
        self.stereo2Pipe.runPipe()
        self.camStatus['S2'] = True
     elif pipeId == 'bottom' and self.camStatus['S1'] or self.camStatus['S2']: #freak bug where one of stereo cams must be running to start usb cams.
        self.bottomPipe.runPipe()
        self.camStatus['bottom'] = True
     elif pipeId == 'manipulator' and self.camStatus['S1'] or self.camStatus['S2']: #freak bug where one of stereo cams must be running to start usb cams.
        self.manipulatorPipe.runPipe()
        self.camStatus['manipulator'] = True
     self.netHandler.send(toJson(f"Camera: {pipeId} started"))
     
  def camStop(self, pipeId):
     if pipeId == 'stereo1':
        self.stereo1Pipe.stopPipe()
        self.camStatus['S1'] = False
     elif pipeId == 'stereo2':
        self.stereo2Pipe.stopPipe()
        self.camStatus['S2'] = False
     elif pipeId == 'bottom':
        self.bottomPipe.stopPipe()
        self.camStatus['bottom'] = False
     elif pipeId == 'manipulator':
        self.manipulatorPipe.stopPipe()
        self.camStatus['manipulator'] = False
     self.netHandler.send(toJson(f"Camera: {pipeId} stopped"))
     

if __name__ == "__main__":
# tag = (type, value)
# tags = (id, tag0, tag1, tag2, tag3, tag4, tag5, tag6, tag7) ex. with int8 or uint8
  c = ComHandler()
  while True:
    time.sleep(0.1)
