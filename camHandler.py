
from threading import Thread
import gi
import time
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

class gstreamerPipe(Thread):
    def __init__(self, pipeId:str='test', multicastGroup:str = '224.1.1.1' , bitrate:str='8000000', port:str='5000') -> None:
        Thread.__init__(self)
        self.pipeId = pipeId
        self.multicastGroup = multicastGroup
        self.bitrate = bitrate
        if self.pipeId == "stereo1":
            self.port = "5000"
            self.sourceID = 0
        elif self.pipeId == "stereo2":
            self.port = "5001"
            self.sourceID = 1
        elif self.pipeId == "bottom":
            self.port = "5002"
            self.sourceID = 2
        elif self.pipeId == "manipulator":
            self.port = "5003"
            self.sourceID = 3
        else:
            self.port = port
        self.pipe = self.createPipe()
            
    def createPipe(self):
        if self.pipeId == "stereo1" or self.pipeId == "stereo2":
            gstStr = (f"nvarguscamerasrc sensor-id={self.sourceID} ! 'video/x-raw(memory:NVMM), width=1920, heigth=1080, framerate=30/1, format=NV12' ! nvv4l2h264enc insert-sps-pps=true bitrate={self.bitrate} ! rtph264pay ! udpsink host={self.multicastGroup} port={self.port} auto-multicast=true")
        elif self.pipeId == "bottom" or self.pipeId == "manipulator":
            gstStr = (f"v4l2src device=/dev/video{self.sourceID} io-mode=2 ! 'image/jpeg, format=MJPG, width=1920, heigth=1080, framerate=30/1' ! nvjpegdec ! 'video/x-raw' ! nvvidconv ! 'video/x-raw(memory:NVMM), format=NV12' ! nvv4l2h264enc insert-sps-pps=true bitrate={self.bitrate} ! rtph264pay ! udpsink host={self.multicastGroup} port={self.port} auto-multicast=true")
        else: 
            gstStr = (f"videotestsrc ! videoconvert ! x264enc ! rtph264pay ! udpsink host={self.multicastGroup} port={self.port} auto-multicast=true")
        return Gst.parse_launch(gstStr)
    
    def runPipe(self):
        self.pipe.set_state(Gst.State.PLAYING)
    
    def stopPipe(self):
        self.pipe.set_state(Gst.State.NULL)
        print(f"Pipe {self.pipeId} set to state null")
        self.mainLoop.quit()
        print(f"Pipe {self.pipeId} quit")
    
    def run(self):
        Gst.init([])
        self.mainLoop = GLib.MainLoop()
        pipeline = self.createPipe()
        thread = Thread(target=self.mainLoop.run)
        thread.start()
        self.runPipe()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stopPipe()

if __name__ == "__main__":
    Gst.init([])
    g1 = gstreamerPipe()
    g1.runPipe()
    g1.start()
    g2 = gstreamerPipe(port='5001')
    g2.runPipe()
    g2.start()
    while True:
        teststr = int(input('stop pipe 1 or 2: '))
        if teststr == 1:
            g1.stopPipe()
        elif teststr == 2:
            g2.stopPipe()
        elif teststr == 3:
            g1.runPipe()
        elif teststr == 4:
            g2.runPipe()




