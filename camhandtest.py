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
            #gstStr = (f"nvarguscamerasrc sensor-id={self.sourceID} ! 'video/x-raw(memory:NVMM), width=1920, heigth=1080, framerate=30/1, format=NV12' ! nvv4l2h264enc insert-sps-pps=true bitrate={self.bitrate} ! rtph264pay ! udpsink host={self.multicastGroup} port={self.port} auto-multicast=true")
            gstStr = (f"videotestsrc ! 'video/x-raw(memory:NVMM), width=1920, heigth=1080, framerate=30/1, format=NV12' ! nvv4l2h264enc insert-sps-pps=true bitrate={self.bitrate} ! rtph264pay ! udpsink host={self.multicastGroup} port={self.port} auto-multicast=true")

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
    # Create instances of gstreamerPipe
    Gst.init([])
    stereo1_pipe = gstreamerPipe(pipeId="stereo1", port="5000")
    stereo2_pipe = gstreamerPipe(pipeId="stereo2", port="5001")
    bottom_pipe = gstreamerPipe(pipeId="test", port="5002")
    manipulator_pipe = gstreamerPipe(pipeId="test", port="5003")
    test_pipe = gstreamerPipe(pipeId="test", port="5004")
    
    # Start the pipes in separate threads
    stereo1_thread = Thread(target=stereo1_pipe.run)
    stereo2_thread = Thread(target=stereo2_pipe.run)
    bottom_thread = Thread(target=bottom_pipe.run)
    manipulator_thread = Thread(target=manipulator_pipe.run)
    test_thread = Thread(target=test_pipe.run)
    
    stereo1_thread.start()
    stereo2_thread.start()
    bottom_thread.start()
    manipulator_thread.start()
    test_thread.start()
    
    # Wait for keyboard input to start and stop cameras
    while True:
        try:
            camera = input("Enter camera ID (stereo1, stereo2, bottom, manipulator, test) or 'exit' to quit: ")
            if camera == "exit":
                break
            action = input("Enter action (start, stop): ")
            if action == "start":
                if camera == "stereo1":
                    stereo1_pipe.runPipe()
                elif camera == "stereo2":
                    stereo2_pipe.runPipe()
                elif camera == "bottom":
                    bottom_pipe.runPipe()
                elif camera == "manipulator":
                    manipulator_pipe.runPipe()
                elif camera == "test":
                    test_pipe.runPipe()
            elif action == "stop":
                if camera == "stereo1":
                    stereo1_pipe.stopPipe()
                elif camera == "stereo2":
                    stereo2_pipe.stopPipe()
                elif camera == "bottom":
                    bottom_pipe.stopPipe()
                elif camera == "manipulator":
                    manipulator_pipe.stopPipe()
                elif camera == "test":
                    test_pipe.stopPipe()
            else:
                print("Invalid action")
        except KeyboardInterrupt:
            break
        
    # Stop all pipes and wait for threads to finish
    stereo1_pipe.stopPipe()
    stereo2_pipe.stopPipe()
    bottom_pipe.stopPipe()
    manipulator_pipe.stopPipe()
    test_pipe.stopPipe()
    
    stereo1_thread.join()
    stereo2_thread.join()
    bottom_thread.join()
    manipulator_thread.join()
    test_thread.join()
