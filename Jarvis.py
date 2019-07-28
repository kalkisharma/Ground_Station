import time
import logging
import math

class Jarvis:
    def __init__(self, server_, audio_, image_=None):
        self.server = server_
        self.audio = audio_
        self.image = image_

        self.behavior = ""
        self.takeoff_altitude = -2
        self.pickup_altitude = -0.5
        self.setpoint = [0, 0, 0]
        self.setpoints = []

    def update_setpoint(self):
        self.server.x_desired = self.setpoint[0]
        self.server.y_desired = self.setpoint[1]
        self.server.z_desired = self.setpoint[2]
        self.server.yaw_desired = 0

    def enable_offboard(self):
        logging.info("ENABLING OFFBOARD")
        self.server.msg_payload_send = [92, 1, 0, 0, 0, 0, 0, 0]

    def arm_pixhawk(self):
        logging.info("ARMING PIXHAWK")
        self.server.msg_payload_send = [400, 1, 0, 0, 0, 0, 0, 0]

    def open_servo(self):
        logging.info("OPENING SERVO")
        self.server.msg_payload_send = [-1, 1, 0, 0, 0, 0, 0, 0]

    def close_servo(self):
        logging.info("CLOSING SERVO")
        self.server.msg_payload_send = [-2, 1, 0, 0, 0, 0, 0, 0]

    def dist_to_setpoint(self, setpoint):
        x = setpoint[0] - self.server.current_x
        y = setpoint[1] - self.server.current_y
        z = setpoint[2] - self.server.current_z
        return math.sqrt(x**2 + y**2 + z**2)

    def reset_image_data(self):
        self.image.tag_name = ""
        self.image.x = 100
        self.image.y = 100

    def takeoff(self):
        self.behavior = "TAKEOFF"
        logging.info("TAKING OFF")
        self.setpoint = [0, 0, self.takeoff_altitude]
        self.setpoints.append(self.setpoint)
        while self.dist_to_setpoint(self.setpoint) > 0.1:
            self.update_setpoint()

    def center_over_home(self):
        self.behavior = "GO TO HELIPAD"
        logging.info("GOING TO HELIPAD")
        self.image.tag_name = "HOME"
        while self.image.x == 100 or self.image.y == 100:
            pass
        logging.info(f"TAG LOCATED AT ({self.image.x},{self.image.y})")
        self.setpoint = [self.image.x, self.image.y, self.server.current_z]
        self.setpoints.append(self.setpoint)
        while self.dist_to_setpoint(self.setpoint) > 0.3:
            self.update_setpoint()
        self.reset_image_data()

    def center_over_drop(self):
        self.behavior = "GO TO DROPOFF"
        logging.info("GOING TO DROPOFF")
        self.image.tag_name = "DROPOFF"
        while self.image.x == 100 or self.image.y == 100:
            pass
        logging.info(f"TAG LOCATED AT ({self.image.x},{self.image.y})")
        self.setpoint = [self.image.x, self.image.y, self.server.current_z]
        self.setpoints.append(self.setpoint)
        while self.dist_to_setpoint(self.setpoint) > 0.3:
            self.update_setpoint()
        self.reset_image_data()

    def drop_package(self):
        self.behavior = "DROPPING PACKAGE"
        logging.info("DROPPING PACKAGE")
        self.open_servo()
        while jarvis.server.msg_payload_send[0] != 0:
            pass
        self.close_servo()
        while jarvis.server.msg_payload_send[0] != 0:
            pass

    def pickup_package(self):
        self.behavior = "PICKUP PACKAGE"
        logging.info("PICKUP PACKAGE")
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
        logging.info("GOING TO PICKUP")
        self.image.tag_name = "PICKUP"
        while self.image.x == 100 or self.image.y == 100:
            pass
        logging.info(f"TAG LOCATED AT ({self.image.x},{self.image.y})")
        self.setpoint = [self.image.x, self.image.y, self.server.current_z]
        self.setpoints.append(self.setpoint)
        while self.dist_to_setpoint(self.setpoint) > 0.3:
            self.update_setpoint()
        self.reset_image_data()

    def hover(self, start_time, timeout=5):
        self.behavior = "HOVER"
        logging.info("HOVERING")
        self.setpoint = [self.server.current_x, self.server.current_y, self.server.current_z]
        self.setpoints.append(self.setpoint)
        while time.time() < start_time + timeout:
            self.update_setpoint()

    def achieve_setpoint(self, setpoint):
        self.behavior = "ACHIEVE SETPOINT"
        logging.info(f"ACHIEVING SETPOINT: ({setpoint[0]},{setpoint[1]},{setpoint[2]})")
        self.setpoint = setpoint
        self.setpoints.append(setpoint)
        while self.dist_to_setpoint(self.setpoint) > 0.3:
            self.update_setpoint()

    def land(self):
        self.behavior = "LAND"
        logging.info("LAND")
        self.setpoint = [self.server.current_x, self.server.current_y, self.setpoints[0][2]]
        self.setpoints.append(self.setpoint)
        self.open_servo()
        while jarvis.server.msg_payload_send[0] != 0:
            pass
        while self.dist_to_setpoint(self.setpoint) > 0.1:
            self.update_setpoint()

    def start(self):

        self.start_cmd_thread()

    def stop(self):

        self.close_thread = True

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
        logging.info("ALL TASKS COMPLETED")

        break
