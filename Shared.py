import threading
import numpy as np
import time

class data:

    # audio data
    audio_lock = threading.Lock()
    listening = False
    audio_command = ('',time.time())

    # mav messages and pose values from and to quad
    mav_lock = threading.Lock()

    current_pos = [0, 0, 0]
    desired_pos = [0, 0, 0]
    current_yaw = 0
    desired_yaw = 0

    msg_payload_send = [0]*8
    msg_per_second = 4

    # tcp ip values
    ip = 'localhost'
    port = 9999
    #ip = '192.168.10.13'
    #port = 9998

    # video frames obtained from the quad
    video_source = 0
    video_lock = threading.Lock()
    frame = np.zeros((480,640,3), np.uint8)
    frame_image_recognition = np.zeros((480,640,3), np.uint8)
    ret = None
    video_width = 640
    video_height = 480
    FOVU = 0.840248046
    FOVV = 0.648415104
    pixel_pos = [0,0]
    barcode_list = []

    # image recognition flags
    detect_qr_flag = False
    detect_an_flag = False
    detect_package_flag = False
