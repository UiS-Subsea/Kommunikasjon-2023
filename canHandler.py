#!/usr/bin/python3

"""
    @file   canHandler.py
    
    @brief  
    @date   13.03.23 
    @author Thomas Matre
"""

import can

#class for esatblishing canbus interface, sending and reciving messages
#initialise with Canbus()
#method .sendPacket(tag) to send
#method .readPacket() to read 
class Canbus:
  def __init__(self,
               canifaceType:str='socketcan',
               canifaceName:str='can0',
               canifaceFd:bool=False,
               canifaceSetFilter:bool=True
               ) -> None:
    self.canifaceType = canifaceType
    self.canifaceName = canifaceName
    self.canifaceFd   = canifaceFd
    self.canifaceSetFilter = canifaceSetFilter
    #self.canFilters = [{"can_id" : 0x60 , "can_mask" : 0xF8, "extended" : False }]
    self.canInit()

  def canInit(self):
    self.bus = can.Bus(
      interface             = self.canifaceType,
      channel               = self.canifaceName,
      receive_own_messages  = False,
      fd                    = self.canifaceFd)
    if self.canifaceSetFilter:
      self.bus.set_filters(self.canFilters)
    self.status['Can'] = True
    self.notifier = can.Notifier(self.bus, [self.readPacket])
    self.timeout = 0.1 # todo kan denne fjernes?
  
  def sendPacket(self, tag):
    packet = tag
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

if __name__ == "__main__":
# tag = (type, value)
  tag0 = ("int16", 16550)
  tag1 = ("int8", 120)
  tag2 = ("uint8", 240)
  tag3 = ("uint16", 50000 )
  tag4 = ("int16", -20000)
# tags = (id, tag0, tag1, tag2, tag3, tag4, tag5, tag6, tag7) ex. with int8 or uint8
  tags = (10, tag0, tag1, tag2, tag3, tag4)
  c = Canbus()
  while True:
    c.sendPacket(tags)




