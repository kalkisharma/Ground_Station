import threading
import numpy as np
import time
from math import tan

class data:

    # audio data
    audio_lock = threading.Lock()
    listening = False
    audio_command = ('',time.time())

    #Package info
    package_type = "red"

    # mav messages and pose values from and to quad
    mav_lock = threading.Lock()

    initial_pos = [0, 0, 0]
    current_pos = [0, 0, 0]
    desired_pos = [0, 0, 0]
    initial_attitude = [0, 0, 0]
    current_attitude = [0, 0, 0]
    desired_attitude = [0, 0, 0]

    msg_payload_send = [0]*8
    msg_per_second = 5

    takeoff_altitude = -0.5
    PACKAGE_OFFSET = 0
    # tcp ip values
    ip = '104.39.142.243'
    port = 9999
    #ip = '192.168.10.13'
    #port = 9998

    # video frames obtained from the quad
    video_source = 0
    webcam_source = 0
    fpv_source = 0
    gstreamer_source = (0,0)
    video_lock = threading.Lock()
    frame_fpv = np.zeros((480,640,3), np.uint8)
    frame_gstreamer = np.zeros((480,640,3), np.uint8)
    frame_webcam = np.zeros((480,640,3), np.uint8)
    frame_QR = np.zeros((480,640,3), np.uint8)
    frame = np.ones((480,640,3), np.uint8)
    frame_image_recognition = np.zeros((480,640,3), np.uint8)
    frame_num = 0
    ret = None
    ret_fpv = None
    ret_gstreamer = None
    ret_webcam = None
    video_width = 320
    video_height = 240
    sensorU = 1280
    sensorV = 720
    FOVU = 0.840248046
    FOVV = 0.648415104
    focalLengthU = sensorU/(sensorU*tan(FOVU/2))
    focalLengthV = sensorV/(sensorU*tan(FOVV/2))
    pixel_pos = [0,0]
    image_data = {
                    'data' : [], # List of values obtained from detection (e.g. qr code values)
                    'time' : 0,
                    'type' : 'QR/AN/Package',
                    'pixel' : [] # List of pixel width and height relative to frame size
                }
    gui_video_width = 640
    gui_video_height = 480
    fpv_gui_width = 400
    fpv_gui_height = 300

    # EKF stuff
    ekfTime1 = 0
    ekfTime2 = 0
    ekf = None
    shelf_dist = -1
    est_shelf_dist = False

    # image recognition flags
    detect_qr_flag = False
    detect_an_flag = False
    detect_package_flag = False
    pickup_flag = False
    find_shelf = False
    find_shelf_row = False
    log_package_flag = False
    find_pickup_flag = False
    store_flag_flag = False
    GUI_STARTED_FLAG = False
    find_nation_flag = False
    nation = None
    find_land_flag = False
    found_initial_flag = False
    toggle_pickup_flag = False
    plot_QR = False
    
    # recognition values
    barcode_list = ['0000']
    an_list = ['1A']
    shelf_code = [
        '11A', '12A', '13A', '14A',
        '21A', '22A', '23A', '24A',
        '11B', '12B', '13A', '14B',
        '21B', '22B', '23B', '24B',
    ]
    shelf_number = ['1', '11']
    package_log = {}
    current_shelf = ''
    package_list = ['1000', '1005']#['V166D', '5419N', 'N4915', '1779F', 'B527C']
    npackages = len(package_list)
    found_packages = []
    current_package = []
    recorded_qr = []
    save_package = []

    # position flags
    initial_pos_flag = False
    initial_attitude_flag = False

    # task indicators
    task_canvas = None
    takeoff_indicator = None
    log_package_indicator = None
    pickup_indicator = None
    store_flag_indicator = None
    with_an = False