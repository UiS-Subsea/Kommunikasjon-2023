from threading import Thread
import gi
import time
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib
from drivers.camHandler import gstreamerPipe


if __name__ == "__main__":
    # Create instances of gstreamerPipe
    Gst.init([])
    stereo1_pipe = gstreamerPipe(pipeId="stereo1", port="5000")
    stereo2_pipe = gstreamerPipe(pipeId="stereo2", port="5001")
    bottom_pipe = gstreamerPipe(pipeId="bottom", port="5002")
    manipulator_pipe = gstreamerPipe(pipeId="manipulator", port="5003")
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
    stereo1_pipe.quitLoop()
    stereo2_pipe.stopPipe()
    stereo1_pipe.quitLoop()
    bottom_pipe.stopPipe()
    stereo1_pipe.quitLoop()
    manipulator_pipe.stopPipe()
    stereo1_pipe.quitLoop()
    test_pipe.stopPipe()
    stereo1_pipe.quitLoop()
    
    stereo1_thread.join()
    stereo2_thread.join()
    bottom_thread.join()
    manipulator_thread.join()
    test_thread.join()
