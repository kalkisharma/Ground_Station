import cv2
import threading
import time

class MyVideoCapture:

    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture(video_source)
        self.video_source = video_source
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            #self.window.mainloop()

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, frame) #cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

def capture_video(video):
    while True:
        ret, frame = video.get_frame()
        cv2.imshow("output", frame) #np.hstack([frame, output])) #np.hstack([frame, output]))
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

if __name__=='__main__':
    video = MyVideoCapture()

    video_thread = threading.Thread(target=capture_video, args=(video,))
    video_thread.start()
    time_start = time.time()
    timeout = 10
    while time.time() < time_start + timeout:
        pass
    video_thread.join()
