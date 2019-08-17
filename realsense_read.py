import pyrealsense2 as rs
import Shared


class RealSenseRead:
    def __init__(self):
        self.pipe = rs.pipeline()
        self.cfg = rs.config()
        self.rsConnect: bool = False

    def start(self):
        self.cfg.enable_stream(rs.stream.pose)
        try:
            self.pipe.start(self.cfg)
            self.rsConnect = True
        except:
            print("Could not connect to RealSense")
            self.rsConnect = False


    def get_pose(self):
        if self.rsConnect:
            frames = self.pipe.wait_for_frames()

            pose = frames.get_pose_frame()

            if pose:
                data = pose.get_pose_data()
                position = data.translation
                Shared.data.current_pos = [position[0], posiiton[1], position[2]]

    def stop(self):
        self.pipe.stop()
