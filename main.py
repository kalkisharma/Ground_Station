import threading
import logging
import cv2
import time

import TCP_Server
import Image_Recognition
import Jarvis
import GUI
import Video_Capture
import audio_recorder
import tasks
import Shared

def main():

    # Set Global flags
    RUN_TASK_FLAG = False
    RUN_SERVER_FLAG = False
    RUN_WEBCAM_FLAG = True
    RUN_GSTREAMER_FLAG = False
    RUN_FPV_FLAG = False
    RUN_RECOGNITION_FLAG = True
    RUN_GUI_FLAG = True

    # Set case variables
    Shared.data.video_source = ['udpsrc port=9999 caps = "application/x-rtp, '
                                'media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, '
                                'payload=(int)96" ! rtph264depay ! h264parse ! avdec_h264 ! '
                                'videoconvert ! appsink sync=false',cv2.CAP_GSTREAMER]
    Shared.data.fpv_source = 1
    Shared.data.webcam_source = 0
    Shared.data.ip = "192.168.1.2" # Server IP
    Shared.data.port = 9999 # Server Port

    """
    Shared.data.ip = "192.168.1.2" # Server IP
    Shared.data.port = 9999 # Server Port
    Shared.data.video_source = ('udpsrc port=9999 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, ' \
                               'encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! queue ! ' \
                               'videoconvert ! appsink sync=false', cv2.CAP_GSTREAMER)
    Shared.data.ip = "localhost" # Server IP
    Shared.data.port = 9999 # Server Port
    Shared.data.video_source = 'udpsrc port=5000 caps = "application/x-rtp, ' \
                               'media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, ' \
                               'payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink', cv2.CAP_GSTREAMER
    Shared.data.video_source = 0

    Shared.data.video_source = ['udpsrc port=9999 caps = "application/x-rtp, '
                                'media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, '
                                'payload=(int)96" ! rtph264depay ! decodebin ! queue ! '
                                'videoconvert ! appsink sync=false',cv2.CAP_GSTREAMER]

    Shared.data.gstreamer_source = ['udpsrc port=9999 caps = "application/x-rtp, '
                                'media=(string)video, clock-rate=(int)90000, encoding-name=(string)JPEG, '
                                'payload=(int)26" ! rtpjpegdepay ! jpegdec ! queue ! '
                                'appsink sync=false', cv2.CAP_GSTREAMER]

    """

    if RUN_TASK_FLAG:

        scheduler = tasks.TaskScheduler()
        logging.info("RUNNING TASK SCHEDULER")
        scheduler.start()

    if RUN_SERVER_FLAG:

        server = TCP_Server.MAVServer()
        logging.info("RUNNING SERVER")
        server.start()
        # Catch to ensure server has started and registered heartbeat
        while not server.server_started:
            time.sleep(0.1)

    if RUN_WEBCAM_FLAG:

        video_webcam = Video_Capture.MyVideoCapture(
            Shared.data.webcam_source,
            show_video=False,
            type_source='webcam'
        )
        logging.info("RUNNING WEBCAM")
        video_webcam.start()

    elif RUN_GSTREAMER_FLAG:

        video_gsteamer = Video_Capture.MyVideoCapture(
            Shared.data.gstreamer_source,
            show_video=False,
            type_source='gstreamer'
        )
        logging.info("RUNNING GSTREAMER")
        video_gsteamer.start()

    if RUN_FPV_FLAG:

        video_fpv = Video_Capture.MyVideoCapture(
            Shared.data.fpv_source,
            show_video=False,
            type_source='fpv'
        )
        logging.info("RUNNING FPV")
        video_fpv.start()

    if RUN_RECOGNITION_FLAG:

        image = Image_Recognition.MAVImageRecognition()
        logging.info("RUNNING IMAGE RECOGNITION")
        image.start()

    if RUN_GUI_FLAG:

        gui = GUI.GUI()
        logging.info("RUNNING GUI")
        gui.start()

    #audio = audio_recorder.AudioRecorder('machine.pmdl', 0.5)
    #jarvis = Jarvis.Jarvis()

    #logging.info("RUNNING AUDIO")
    #audio.start()

    #logging.info("RUNNING JARVIS")
    #jarvis.start()

    # Stop
    if RUN_TASK_FLAG:
        scheduler.stop()
    if RUN_SERVER_FLAG:
        server.stop()
    if RUN_WEBCAM_FLAG:
        video_webcam.stop()
    if RUN_GSTREAMER_FLAG:
        video_gsteamer.stop()
    if RUN_FPV_FLAG:
        video_fpv.stop()
    if RUN_RECOGNITION_FLAG:
        image.stop()
    #audio.stop()
    #jarvis.stop()

if __name__ == "__main__":
    # logging.basicConfig(filename="log.log", filemode="w", format='%(levelname)s:%(message)s', level=logging.INFO)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    main()
