import cv2
import threading
import time
import Shared

class MyVideoCapture:

    def __init__(self, video_source=0, show_video=True, type_source='cam'):
        self.video_source = video_source
        self.close_thread = False
        self.show_video = show_video
        self.type = type_source
        if self.type=='gstreamer':

            self.vid = cv2.VideoCapture(video_source[0], video_source[1])
        else:

            self.vid = cv2.VideoCapture(video_source)


        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", self.video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        Shared.data.video_width = self.width
        Shared.data.video_height = self.height
    """
    def __init__(self, video_source=[0,0], show_video=False):
        self.close_thread = False
        self.show_video = show_video
        #self.video_source = ['udpsrc port=9999 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink', cv2.CAP_GSTREAMER]

        self.video_source = video_source

    def __initialise__(self):
        #self.vid = cv2.VideoCapture(0)
        self.vid = cv2.VideoCapture(self.video_source[0], self.video_source[1])
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", self.video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        Shared.data.video_width = self.width
        Shared.data.video_height = self.height
    """
    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            #self.window.mainloop()

    def get_frame(self):

        ret = None

        ret = False

        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, frame) #cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

    def start(self):
        #self.__initialise__()
        self.start_video_thread()

    def start_video_thread(self):

        self.video_thread = threading.Thread(target=self.start_video)
        self.video_thread.start()

    def start_video(self):

        while not self.close_thread:

            ret, frame = self.get_frame()
            if self.type=='fpv':
                Shared.data.frame_fpv = frame
                Shared.data.ret_fpv = ret
            else:
                Shared.data.frame = frame
                Shared.data.ret = ret
            if self.show_video:
                cv2.imshow("output", Shared.data.frame) #np.hstack([frame, output])) #np.hstack([frame, output]))
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        return

    def stop(self):

        self.close_thread = True


def capture_video(video):
    while True:
        ret, frame = video.get_frame()
        cv2.imshow("output", frame) #np.hstack([frame, output])) #np.hstack([frame, output]))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__=='__main__':
    video = MyVideoCapture(4, True)
    video.start()
    """
    video_thread = threading.Thread(target=capture_video, args=(video,))
    video_thread.start()
    time_start = time.time()
    timeout = 10
    while time.time() < time_start + timeout:
        pass
    video_thread.join()
    """
    while True:
        pass
