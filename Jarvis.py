import time
import logging
import math
import Shared
import numpy as np
import threading

class Jarvis:
    def __init__(self, server_=None, audio_=None, image_=None):
        self.server = server_
        self.audio = audio_
        self.image = image_

        self.behavior = ""
        self.takeoff_altitude = -2
        self.pickup_altitude = -0.5
        self.setpoint = [0, 0, 0]
        self.setpoints = []

        self.close_thread = False

    def set_desired_pos_yaw(self, pos, yaw):
        Shared.data.mav_lock.acquire()
        Shared.data.desired_pos = pos
        Shared.data.desired_yaw = yaw
        Shared.data.mav_lock.release()

    def get_desired_pos_yaw(self):
        Shared.data.mav_lock.acquire()
        pos = Shared.data.desired_pos
        yaw = Shared.data.desired_yaw
        Shared.data.mav_lock.release()
        return pos, yaw

    def get_current_pos_yaw(self):
        Shared.data.mav_lock.acquire()
        pos = Shared.data.current_pos
        yaw = Shared.data.current_yaw
        Shared.data.mav_lock.release()
        return pos, yaw

    def set_msg_payload_send(self,cmd_id,p1,p2,p3,p4,p5,p6,p7):
        Shared.data.mav_lock.acquire()
        Shared.data.msg_payload_send = [cmd_id,p1,p2,p3,p4,p5,p6,p7]
        Shared.data.mav_lock.release()

    def hover(self):
        self.behavior = "HOVER"
        print("INFO: HOVER")

        #current_pos, current_yaw = self.get_current_pos_yaw()
        desired_pos, desired_yaw = self.get_current_pos_yaw()

        while not Shared.data.listening: # and np.linalg.norm(current_pos - desired_pos) > 0.1:
            self.set_desired_pos_yaw(desired_pos, desired_yaw)

    def takeoff(self):
        self.behavior = "TAKEOFF"
        print("INFO: TAKING OFF")

        desired_pos = [0, 0, self.takeoff_altitude]
        desired_yaw = 0

        current_pos, current_yaw = self.get_current_pos_yaw()

        while not Shared.data.listening and self.dist_to_setpoint(current_pos, desired_pos) > 0.1:
            self.set_desired_pos_yaw(desired_pos, desired_yaw)
            current_pos, current_yaw = self.get_current_pos_yaw()

    def land(self):
        self.behavior = "LANDING"
        print("INFO: LANDING")

        current_pos, current_yaw = self.get_current_pos_yaw()
        desired_pos = [current_pos[0], current_pos[1], 0]
        desired_yaw = current_yaw

        current_pos, current_yaw = self.get_current_pos_yaw()
        while not Shared.data.listening and self.dist_to_setpoint(current_pos, desired_pos) > 0.1:
            self.set_desired_pos_yaw(desired_pos, desired_yaw)
            current_pos, current_yaw = self.get_current_pos_yaw()

    def enable_offboard(self):
        print("INFO: ENABLING OFFBOARD")
        self.set_msg_payload_send(92, 1, 0, 0, 0, 0, 0, 0)
        Shared.data.audio_command = ('', time.time())

    def disable_offboard(self):
        print("INFO: DISALBING OFFBOARD")
        self.set_msg_payload_send(92, 0, 0, 0, 0, 0, 0, 0)
        Shared.data.audio_command = ('', time.time())

    def arm_pixhawk(self):
        print("INFO: ARMING PIXHAWK")
        self.set_msg_payload_send(400, 1, 0, 0, 0, 0, 0, 0)
        Shared.data.audio_command = ('', time.time())

    def disarm_pixhawk(self):
        print("INFO: DISARMING PIXHAWK")
        self.set_msg_payload_send(400, 0, 0, 0, 0, 0, 0, 0)
        Shared.data.audio_command = ('', time.time())

    def dist_to_setpoint(self, desired_pos, current_pos):
        x = desired_pos[0] - current_pos[0]
        y = desired_pos[1] - current_pos[1]
        z = desired_pos[2] - current_pos[2]
        return math.sqrt(x**2 + y**2 + z**2)
    """
    def reset_image_data(self):
        self.image.tag_name = ""
        self.image.x = 100
        self.image.y = 100

    def takeoff(self):
        self.behavior = "TAKEOFF"
        print("INFO: TAKING OFF")
        self.setpoint = [0, 0, self.takeoff_altitude]
        self.setpoints.append(self.setpoint)
        while not self.audio.listening and self.dist_to_setpoint(self.setpoint) > 0.1:
            self.update_setpoint()

    def center_over_home(self):
        self.behavior = "GO TO HELIPAD"
        print("INFO: GOING TO HELIPAD")
        self.image.tag_name = "HOME"
        while self.image.x == 100 or self.image.y == 100:
            pass
        print(f"INFO: TAG LOCATED AT ({self.image.x},{self.image.y})")
        self.setpoint = [self.image.x, self.image.y, self.server.current_z]
        self.setpoints.append(self.setpoint)
        while self.dist_to_setpoint(self.setpoint) > 0.3:
            self.update_setpoint()
        self.reset_image_data()

    def center_over_drop(self):
        self.behavior = "GO TO DROPOFF"
        print("INFO: GOING TO DROPOFF")
        self.image.tag_name = "DROPOFF"
        while self.image.x == 100 or self.image.y == 100:
            pass
        print(f"INFO: TAG LOCATED AT ({self.image.x},{self.image.y})")
        self.setpoint = [self.image.x, self.image.y, self.server.current_z]
        self.setpoints.append(self.setpoint)
        while self.dist_to_setpoint(self.setpoint) > 0.3:
            self.update_setpoint()
        self.reset_image_data()

    def drop_package(self):
        self.behavior = "DROPPING PACKAGE"
        print("INFO: DROPPING PACKAGE")
        self.open_servo()
        while jarvis.server.msg_payload_send[0] != 0:
            pass
        self.close_servo()
        while jarvis.server.msg_payload_send[0] != 0:
            pass

    def pickup_package(self):
        self.behavior = "PICKUP PACKAGE"
        print("INFO: PICKUP PACKAGE")
        self.setpoint = [self.server.current_x, self.server.current_y, self.pickup_altitude]
        self.setpoints.append(self.setpoint)
        while self.dist_to_setpoint(self.setpoint) > 0.1:
            self.update_setpoint()
        self.close_servo()
        while jarvis.server.msg_payload_send[0] != 0:
            pass
        self.setpoint = [self.server.current_x, self.server.current_y, self.takeoff_altitude]
        self.setpoints.append(self.setpoint)
        while self.dist_to_setpoint(self.setpoint) > 0.1:
            self.update_setpoint()

    def center_over_pickup(self):
        self.behavior = "GO TO PICKUP"
        print("INFO: GOING TO PICKUP")
        self.image.tag_name = "PICKUP"
        while self.image.x == 100 or self.image.y == 100:
            pass
        print(f"INFO: TAG LOCATED AT ({self.image.x},{self.image.y})")
        self.setpoint = [self.image.x, self.image.y, self.server.current_z]
        self.setpoints.append(self.setpoint)
        while self.dist_to_setpoint(self.setpoint) > 0.3:
            self.update_setpoint()
        self.reset_image_data()

    def hover(self, start_time, timeout=5):
        self.behavior = "HOVER"
        print("INFO: HOVERING")
        self.setpoint = [self.server.current_x, self.server.current_y, self.server.current_z]
        self.setpoints.append(self.setpoint)
        while not self.audio.listening and time.time() < start_time + timeout:
            self.update_setpoint()

    def achieve_setpoint(self, setpoint):
        self.behavior = "ACHIEVE SETPOINT"
        print(f"INFO: ACHIEVING SETPOINT: ({setpoint[0]},{setpoint[1]},{setpoint[2]})")
        self.setpoint = setpoint
        self.setpoints.append(setpoint)
        while not self.audio.listening and self.dist_to_setpoint(self.setpoint) > 0.3:
            self.update_setpoint()

    def land(self):
        self.behavior = "LAND"
        print("INFO: LAND")
        self.setpoint = [self.server.current_x, self.server.current_y, self.setpoints[0][2]]
        self.setpoints.append(self.setpoint)
        #self.open_servo()
        #while jarvis.server.msg_payload_send[0] != 0:
        #    pass
        while not self.audio.listening and self.dist_to_setpoint(self.setpoint) > 0.1:
            self.update_setpoint()
    """
    def start(self):

        self.start_cmd_thread()

    def start_cmd_thread(self):

        self.cmd_thread = threading.Thread(target=self.start_cmd)
        self.cmd_thread.start()

    def start_cmd(self):

        while not self.close_thread:

            #Shared.data.audio_lock.acquire()
            listening = Shared.data.listening
            command = Shared.data.audio_command
            #Shared.data.audio_lock.release()

            #if listening:
                #print(command)
            if command[0]!='':
                print(command[0].split()[0])
                self.select_command(command[0].split())

            time.sleep(0.1)
        return

    def stop(self):

        self.close_thread = True

    def select_command(self, command):

        command_dict = {
            'HOVER':self.hover,
            'TAKEOFF':self.takeoff,
            'LAND':self.land,
            'ENABLE':self.enable_offboard,
            'DISABLE':self.disable_offboard,
            'ARM':self.arm_pixhawk,
            'DISARM':self.disarm_pixhawk
        }

        cmd = command[0].upper()
        if cmd in command_dict:
            command_dict[cmd]()
        else:
            logging.info(f'COMMAND "{cmd}" NOT PART OF COMMAND DICT')
        return

def main(jarvis):
    jarvis.enable_offboard()
    while jarvis.server.msg_payload_send[0] != 0:
        pass
    jarvis.arm_pixhawk()
    while jarvis.server.msg_payload_send[0] != 0:
        pass

    while True:

        jarvis.takeoff()
        jarvis.land()

        """
        jarvis.takeoff()
        jarvis.center_over_home()
        jarvis.hover(time.time(), 5)
        jarvis.pickup_package()
        jarvis.achieve_setpoint([0, 0, 0]) # Fly down path
        jarvis.achieve_setpoint([0, 0, 0]) # Cross ferry and go to drop off
        jarvis.center_over_drop()
        jarvis.hover(time.time(), 5)
        jarvis.drop_package()
        jarvis.achieve_setpoint([0, 0, 0]) # Go to pickup
        jarvis.center_over_pickup()
        jarvis.hover(time.time(), 5)
        jarvis.pickup_package()
        jarvis.reverse_path()
        jarvis.hover(time.time(), 5)
        jarvis.land()
        """
        print("INFO: ALL TASKS COMPLETED")

        break
