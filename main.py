import threading
import logging
import TCP_Server
#import Image_Recognition
import Jarvis
import GUI
import cv2
import time
import Video_Capture
import audio_recorder
import Shared

# ollies-branch

def main():

    # Initialize shared constants
    Shared.data.ip = "localhost" # Server IP
    Shared.data.port = 9999 # Server Port
    Shared.data.video_source = 'udpsrc port=5000 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink', cv2.CAP_GSTREAMER
    Shared.data.video_source = 0

    # Initialize class objects
    server = TCP_Server.MAVServer()

    video = Video_Capture.MyVideoCapture(Shared.data.video_source)
    audio = audio_recorder.AudioRecorder('machine.pmdl', 0.5)
    image = Image_Recognition.MAVImageRecognition()
    jarvis = Jarvis.Jarvis()
    gui = GUI.GUI()

    # Start
    logging.info("RUNNING SERVER")
    server.start()

    logging.info("RUNNING VIDEO")
    video.start()

    logging.info("RUNNING AUDIO")
    audio.start()

    logging.info("RUNNING IMAGE RECOGNITION")
    image.start()

    logging.info("RUNNING JARVIS")
    jarvis.start()

    while not server.server_started:
        time.sleep(0.1)

    logging.info("RUNNING GUI")
    gui.start()

    # Stop
    server.stop()
    video.stop()
    audio.stop()
    jarvis.stop()

if __name__ == "__main__":
    # logging.basicConfig(filename="log.log", filemode="w", format='%(levelname)s:%(message)s', level=logging.INFO)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    main()
