import time
import cv2
import socket
from pymavlink import mavutil
#import Video_Capture
import logging
from enum import Enum
import threading
import numpy as np
import Shared


class MAVServer:
    def __init__(self):

        Shared.data.mav_lock.acquire()
        self.msg_per_second = Shared.data.msg_per_second
        self.ip = Shared.data.ip
        self.port = Shared.data.port
        Shared.data.mav_lock.release()

        self.socket_server = None
        self.server_started = False

        self.send_flag = False
        self.recv_flag = False
        self.video_flag = False
        self.close_threads = False

    def get_frame(self):
        return self.frame

    def conn_server(self):

        logging.info("SERVER IP -> {0}, SERVER PORT -> {1}".format(self.ip, self.port))
        server = mavutil.mavlink_connection('udpin:{0}:{1}'.format(self.ip, self.port), planner_format=False,
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
        logging.info(f"SENDING {self.msg_per_second} MESSAGES EVERY SECOND")
        while not self.close_threads:

            # Get latest update of data to be sent to the quad
            Shared.data.mav_lock.acquire()
            desired_pos = Shared.data.desired_pos
            desired_yaw = Shared.data.desired_yaw
            msg_payload_send = Shared.data.msg_payload_send

            # Vidullan: Kalki, do we need this anymore?
            #Shared.data.msg_payload_send[0] = 0

            Shared.data.mav_lock.release()

            # SETPOINTS
            self.server.mav.set_position_target_local_ned_send(
                int(time.time()),
                1, 1,
                1, #local
                0b000111111000, #take pos and yaw
                desired_pos[0], desired_pos[1], desired_pos[2], # x, y, z positions (not used)
                0, 0, 0, # x, y, z velocity in m/s
                0, 0, 0, # x, y, z acceleration (not used)
                desired_yaw, 0.
            )

            # LONG COMMANDS

            if msg_payload_send[0] != 0:
                mav_cmd_id = int(msg_payload_send[0])
                param1 = float(msg_payload_send[1])
                param2 = float(msg_payload_send[2])
                param3 = float(msg_payload_send[3])
                param4 = float(msg_payload_send[4])
                param5 = float(msg_payload_send[5])
                param6 = float(msg_payload_send[6])
                param7 = float(msg_payload_send[7])

                if msg_payload_send[0] > 0:
                    #send the command
                    logging.info("SENDING COMMAND")
                    self.server.mav.command_long_send(
                        1, # autopilot system id
                        1, # autopilot component id
                        mav_cmd_id, # command id
                        1, # confirmation
                        param1,
                        param2,
                        param3,
                        param4,
                        param5,
                        param6,
                        param7 # unused parameters for this command
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
                Shared.data.msg_payload_send[0] = 0
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
                    x = msg.x
                    y = msg.y
                    z = msg.z

                    Shared.data.mav_lock.acquire()
                    Shared.data.current_pos = [x,y,z]
                    Shared.data.mav_lock.release()

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
