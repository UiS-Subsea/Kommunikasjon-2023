from threading import Thread
import gi
import time


#teststring gst-launch-1.0 videotestsrc ! videoconvert ! autovideosink
gi.require_version("Gst", "1.0")
from gi.repository import Gst, GLib

def create_pipeline(multicast_group:str='224.1.1.1', port:str='5000'):
    return Gst.parse_launch(
        f"videotestsrc ! videoconvert ! x264enc ! rtph264pay ! udpsink host={multicast_group} port={port} auto-multicast=true"
        )

def run_pipeline(pipeline, main_loop):
    pipeline.set_state(Gst.State.PLAYING)
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        pipeline.set_state(Gst.State.NULL)
        main_loop.quit()

def run_camera_stream(multicast_group, port):
    Gst.init([])
    main_loop = GLib.MainLoop()
    pipeline = create_pipeline(multicast_group, port)
    thread = Thread(target=main_loop.run)
    thread.start()
    run_pipeline(pipeline, main_loop)

camera1_info = ("224.1.1.1", 5000)
#camera2_info = ("224.1.1.1", 5001)

thread1 = Thread(target=run_camera_stream, args=camera1_info)
#thread2 = Thread(target=run_camera_stream, args=camera2_info)

thread1.start()
#thread2.start()

thread1.join()
#thread2.join()