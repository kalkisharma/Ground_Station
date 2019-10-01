import threading
import logging
import cv2
import time
from playsound import playsound

import TCP_Server
import Image_Recognition
import Jarvis
import GUI
import Video_Capture
import audio_recorder
import tasks
import Shared
from qr_data.read_qr import obtain_qr_from_file

def main():

    # Set Global flags
    CSV_FILE = './qr_data/qr_data.csv' # .csv file which contains qr data
    NROW = 1 # Row id for qr package recognition
    RUN_CSVREADER_FLAG = True
    RUN_TASK_FLAG = True
    RUN_SERVER_FLAG = True
    RUN_WEBCAM_FLAG = False
    RUN_GSTREAMER_FLAG = True
    RUN_FPV_FLAG = True
    RUN_RECOGNITION_FLAG = True
    RUN_GUI_FLAG = True

    # Set case variables
    Shared.data.gstreamer_source = ['udpsrc port=9999 caps = "application/x-rtp, '
                                'media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, '
                                'payload=(int)96" ! rtph264depay ! h264parse ! avdec_h264 ! queue ! '
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

    if RUN_CSVREADER_FLAG:

        playsound('audio_files/store_qr.mp3')
        print(f"INFO: READING CSV FILE {CSV_FILE}, AT ROW {NROW}")
        Shared.data.package_list = obtain_qr_from_file(CSV_FILE, NROW)
        Shared.data.npackages = len(Shared.data.package_list)
        print(f"INFO: QR CODES: {Shared.data.package_list}")

    if RUN_TASK_FLAG:

        scheduler = tasks.TaskScheduler()
        print("INFO: RUNNING TASK SCHEDULER")
        scheduler.start()

    if RUN_SERVER_FLAG:

        server = TCP_Server.MAVServer()
        print("INFO: RUNNING SERVER")
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
        print("INFO: RUNNING WEBCAM")
        video_webcam.start()

    elif RUN_GSTREAMER_FLAG:

        video_gsteamer = Video_Capture.MyVideoCapture(
            Shared.data.gstreamer_source,
            show_video=False,
            type_source='gstreamer'
        )
        print("INFO: RUNNING GSTREAMER")
        video_gsteamer.start()

    if RUN_FPV_FLAG:

        video_fpv = Video_Capture.MyVideoCapture(
            Shared.data.fpv_source,
            show_video=False,
            type_source='fpv'
        )
        print("INFO: RUNNING FPV")
        video_fpv.start()

    if RUN_RECOGNITION_FLAG:

        image = Image_Recognition.MAVImageRecognition()
        print("INFO: RUNNING IMAGE RECOGNITION")
        image.start()

    if RUN_GUI_FLAG:

        gui = GUI.GUI()
        print("INFO: RUNNING GUI")
        gui.start()

    #audio = audio_recorder.AudioRecorder('machine.pmdl', 0.5)
    #jarvis = Jarvis.Jarvis()

    #print("INFO: RUNNING AUDIO")
    #audio.start()

    #print("INFO: RUNNING JARVIS")
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
