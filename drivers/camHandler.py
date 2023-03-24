#!/usr/bin/python3

"""
    @file   camHandler.py
    
    @brief  Class to start and stop gstreamer pipelines
    @date   10.03.23 
    @author Thomas Matre
"""

from threading import Thread
import gi, time
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

class gstreamerPipe(Thread):
  def __init__(self, pipeId:str='test', multicastGroup:str = '224.1.1.1' , bitrate:str='8000000', port:str='5000') -> None:
    Thread.__init__(self)
    self.pipeId = pipeId
    self.multicastGroup = multicastGroup
    self.bitrate = bitrate
    if self.pipeId == "stereo1":
      self.port = '5000'
      self.sourceID = '0'
    elif self.pipeId == "stereo2":
      self.port = '5001'
      self.sourceID = '1'
    elif self.pipeId == "bottom":
      self.port = '5002'
      self.sourceID = '2'
    elif self.pipeId == "manipulator":
      self.port = '5003'
      self.sourceID = '3'
    else:
      self.port = port
    self.pipe = self.createPipe()
            
  def createPipe(self):
    if self.pipeId == "stereo1" or self.pipeId == "stereo2":
      gstStr = (f"nvarguscamerasrc sensor-id={self.sourceID} ! video/x-raw(memory:NVMM), width=1920, heigth=1080, framerate=30/1, format=NV12 ! nvv4l2h264enc insert-sps-pps=true bitrate={self.bitrate} ! rtph264pay ! udpsink host={self.multicastGroup} port={self.port} auto-multicast=true")
      print(f"Creating stereo pipeId:{self.pipeId} with port: {self.port}")
    elif self.pipeId == "bottom" or self.pipeId == "manipulator":
      gstStr = (f"v4l2src device=/dev/video{self.sourceID} io-mode=2 ! image/jpeg, format=MJPG, width=1280, heigth=720, framerate=30/1 ! nvjpegdec ! video/x-raw ! nvvidconv ! video/x-raw(memory:NVMM), format=NV12 ! nvv4l2h264enc insert-sps-pps=true bitrate={self.bitrate} ! rtph264pay ! udpsink host={self.multicastGroup} port={self.port} auto-multicast=true")
      print(f"Creating usb pipeId:{self.pipeId} with port: {self.port}")           
    else: 
      gstStr = (f"videotestsrc ! videoconvert ! x264enc ! rtph264pay ! udpsink host={self.multicastGroup} port={self.port} auto-multicast=true")
    return Gst.parse_launch(gstStr)
    
  def runPipe(self):
    self.pipe.set_state(Gst.State.PLAYING)
    print(f"Pipe {self.pipeId} set to state playing")
  
  def stopPipe(self):
    self.pipe.set_state(Gst.State.NULL)
    print(f"Pipe {self.pipeId} set to state null")
        
  def quitLoop(self):
    self.mainLoop.quit()
    print(f"Pipe {self.pipeId} main loop quit")
    
  def runThread(self):
    Gst.init([])
    self.mainLoop = GLib.MainLoop()
    thread = Thread(target=self.mainLoop.run)
    thread.start()
    try:
      while True:
        time.sleep(0.1)
    except KeyboardInterrupt:
      pass
    finally:
      self.stopPipe()