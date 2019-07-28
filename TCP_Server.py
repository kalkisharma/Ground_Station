import time
import cv2
import socket
from pymavlink import mavutil
#import Video_Capture
import logging
from enum import Enum
import threading
import numpy as np

from main import SharedMAVLink

class MAVServer:
    def __init__(self,ip_="localhost",port_=9999):
        self.ip = ip_
        self.port = port_

        self.socket_server = None
        self.server_started = False
        self.msg_payload_send = [0]*8
        self.current_x = 0
        self.current_y = 0
        self.current_z = 0
        self.x_desired = 0
        self.y_desired = 0
        self.z_desired = 0
        self.yaw_desired = 0
        self.msg_per_second = 4

        self.send_flag = False
        self.recv_flag = False
        self.video_flag = False
        self.close_threads = False
        self.lock = threading.Lock()

    def get_frame(self):
        return self.frame

    def conn_server(self):

        logging.info("SERVER IP -> {0}, SERVER PORT -> {1}".format(self.ip, self.port))
        server = mavutil.mavlink_connection('tcpin:{0}:{1}'.format(self.ip, self.port), planner_format=False,
                                            notimestamps=True, robust_parsing=True)
        logging.info("SERVER CREATED")
        self.server = server

        return

    def wait_for_heartbeat(self):

        # Wait for a heartbeat so we know the target system IDs
        logging.info("WAITING FOR APM HEARTBEAT")
        try:
            msg = self.server.recv_match(type='HEARTBEAT', blocking=True)
            logging.info(f"HEARTBEAT FROM APM ({self.server.target_system}, {self.server.target_system})")
        except KeyboardInterrupt:
            logging.info("USER EXIT WITHOUT FINDING HEARTBEAT")
        self.server_started = True
        return

    def run_server(self):

        self.wait_for_heartbeat()
        self.start_recv_thread()
        self.start_send_thread()

    def start_recv_thread(self):

        logging.info("SPAWNING RECV THREAD")

        self.recv_flag = True
        self.recv_thread = threading.Thread(target=self.recv_msg)
        self.recv_thread.start()

        return

    def start_send_thread(self):

        logging.info("SPAWNING SEND THREAD")

        self.send_flag = True
        self.send_thread = threading.Thread(target=self.send_msg)
        self.send_thread.start()

        return

    def close_recv_thread(self):

        return
        #self.recv_thread.join()

    def close_send_thread(self):

        return
        #self.send_thread.join()

    def send_msg(self):
        logging.info("STARTING SEND THREAD")
        while not self.close_threads:

            # SETPOINTS
            self.server.mav.set_position_target_local_ned_send(
                int(time.time()),
                1, 1,
                1, #local
                0b000111111000, #take pos and yaw
                self.x_desired, self.y_desired, self.z_desired, # x, y, z positions (not used)
                0, 0, 0, # x, y, z velocity in m/s
                0, 0, 0, # x, y, z acceleration (not used)
                self.yaw_desired, 0.
            )

            # LONG COMMANDS
            msg_payload_send = self.msg_payload_send

            if msg_payload_send[0] != 0:
                self.lock.acquire()
                self.mav_cmd_id = int(msg_payload_send[0])
                self.param1 = float(msg_payload_send[1])
                self.param2 = float(msg_payload_send[2])
                self.param3 = float(msg_payload_send[3])
                self.param4 = float(msg_payload_send[4])
                self.param5 = float(msg_payload_send[5])
                self.param6 = float(msg_payload_send[6])
                self.param7 = float(msg_payload_send[7])
                self.lock.release()

                if msg_payload_send[0] > 0:
                    #send the command
                    print("SENDING COMMAND")
                    self.server.mav.command_long_send(
                        1, # autopilot system id
                        1, # autopilot component id
                        self.mav_cmd_id, # command id
                        1, # confirmation
                        self.param1,
                        self.param2,
                        self.param3,
                        self.param4,
                        self.param5,
                        self.param6,
                        self.param7 # unused parameters for this command
                    )
                elif msg_payload_send[0] == -1:
                    self.server.mav.scaled_pressure_send(
                        int(time.time()),
                        1,
                        1,
                        1
                    )
                elif msg_payload_send[0] == -2:
                    self.server.mav.raw_pressure_send(
                        int(time.time()),
                        1,
                        1,
                        1,
                        1
                    )
                self.msg_payload_send[0] = 0
            time.sleep(1/self.msg_per_second)

        self.close_send_thread()

        return

    def recv_msg(self):

        while not self.close_threads:

            try:
                msg = self.server.recv_match()
                if not msg:
                    continue
                else:
                    pass

                if msg.get_type() == 'LOCAL_POSITION_NED':
                    #logging.info(f"X: {msg.x} \t Y: {msg.y} Z: {msg.z}")
                    self.current_x = msg.x
                    self.current_y = msg.y
                    self.current_z = msg.z
            except KeyboardInterrupt:
                self.close_recv_thread()
                return
            (time.sleep(0.1))

        self.close_recv_thread()

        return

    def stop(self):

        logging.info("CLOSING SERVER")
        self.close_threads = True

    def start(self):

        self.conn_server()
        self.run_server()

def main(server):

    try:
        server.conn_server()
        server.run_server()
    except KeyboardInterrupt:

        server.stop()
