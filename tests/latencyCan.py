#!/usr/bin/python3
"""
    @file   latencyCan.py
    
    @brief  
    @date   30.03.23 
    @author Thomas Matre
"""
import can, time, statistics

class ComHandler:
  def __init__(self, 
               canifaceType:str='socketcan',
               canifaceName:str='can0') -> None:
    self.canifaceType  = canifaceType
    self.canifaceName  = canifaceName
    self.canInit()

  def canInit(self):
    self.bus = can.Bus(
      interface             = self.canifaceType,
      channel               = self.canifaceName,
      receive_own_messages  = False,
      fd                    = False)

  def sendPacket(self, tag):
    assert self.bus is not None
    try:
      self.bus.send(tag)
    except Exception as e:
      print(f'Feilkode i sendPacket, feilmelding: {e}\n\t{tag}')

  def readPacket(self):
    return self.bus.recv()
     

if __name__ == "__main__":
  time_list = []
  time_listms = []
  NoOfPacks = 5000
  msg = can.Message(arbitration_id=9, data=[0,1,2,3,4,5,6,7], is_extended_id=False)
  c = ComHandler()
  for i in range(5):
    print(i)
    time.sleep(1)

  for __ in range(NoOfPacks):
    start = time.time()
    c.sendPacket(msg)
    recmsg = c.readPacket()
    if recmsg.arbitration_id == 139:
      tid = time.time()-start
      time_list.append(tid)

  time.sleep(1)

  for i, time_entry in enumerate(time_list):
     newtime = round(float(time_entry)  * (10**3), 2)
     if newtime >= 3:
       print(f"Entry:{i} with time: {newtime}")
     time_listms.append(newtime)
  print (f'Mean:{statistics.mean(time_listms)}\n Max:{max(time_listms)} \n Min:{min(time_listms)} \n Packets sent: {NoOfPacks} \n Packets recived: {len(time_listms)}')

