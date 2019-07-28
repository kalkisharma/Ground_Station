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

class SharedMAVLink:

    LOCK = threading.Lock()

class SharedVideo:

    LOCK = threading.Lock()

def main():

    # Initialize class objects
    server = TCP_Server.MAVServer("localhost", 9999)
    video_source = 'udpsrc port=5000 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink', cv2.CAP_GSTREAMER
    video_source = 0
    video = Video_Capture.MyVideoCapture(video_source)
    audio = audio_recorder.AudioRecorder('machine')
    #image = Image_Recognition.MAVImageRecognition(server)
    #jarvis = Jarvis.Jarvis(server, audio, image)
    gui = GUI.GUI(server, video, audio)

    # Start
    logging.info("RUNNING SERVER")
    server.start()

    logging.info("RUNNING VIDEO")
    video.start()

    logging.info("RUNNING AUDIO")
    audio.start()

    while not server.server_started:
        time.sleep(0.1)

    logging.info("RUNNING GUI")
    gui.start()

    # Stop
    server.stop()
    video.stop()

if __name__ == "__main__":
    # logging.basicConfig(filename="log.log", filemode="w", format='%(levelname)s:%(message)s', level=logging.INFO)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
    main()
