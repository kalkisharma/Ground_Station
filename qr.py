# import the necessary packages
from pyzbar import pyzbar
import argparse
import cv2
import threading
import time
import imutils
import numpy as np
#import Shared

class MyVideoCapture:

    def __init__(self, video_source=0, show_video=True):
        self.close_thread = False
        self.show_video = show_video
        #self.vid = cv2.VideoCapture('udpsrc port=5000 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink', cv2.CAP_GSTREAMER)
        self.vid = cv2.VideoCapture(video_source)
        self.video_source = video_source
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        #Shared.data.video_width = self.width
        #Shared.data.video_height = self.height

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

    def start(self):
        #return
        self.start_video_thread()

    def start_video_thread(self):

        self.video_thread = threading.Thread(target=self.start_video)
        self.video_thread.start()

    def start_video(self):

        while not self.close_thread:
            ret, frame = self.get_frame()
            #Shared.data.frame = frame
            #Shared.data.ret = ret
            if self.show_video:
                cv2.imshow("output", frame) #np.hstack([frame, output])) #np.hstack([frame, output]))
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
    store_flag = False
    video = MyVideoCapture(4, False)
    barcode_list = []
    time_storage = 15
    #video.start()

    # construct the argument parser and parse the arguments
    #ap = argparse.ArgumentParser()
    #ap.add_argument("-i", "--image", required=True,
    #    help="path to input image")
    #args = vars(ap.parse_args())

    time_start = time.time()

    while True:

        ret, frame = video.get_frame()
        #print(frame)

        if time.time() < time_start + time_storage:

            store_flag = True
            text = "Storage Time: {}".format(round(time_storage - (time.time() - time_start), 1))
            cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2)

        if time.time() > time_start + time_storage and time.time() < time_start + time_storage + 5:

            text = "{}".format(barcode_list)
            cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                1, (0, 255, 0), 2)

        if time.time() > time_start + time_storage + 5:

            store_flag = False

        if ret:

            #frame = imutils.resize(frame, width=400)
            # load the input image
            image = frame #cv2.imread(frame)

            # find the barcodes in the image and decode each of the barcodes
            barcodes = pyzbar.decode(image)

            # loop over the detected barcodes
            for barcode in barcodes:
                # extract the bounding box location of the barcode and draw the
                # bounding box surrounding the barcode on the image
                (x, y, w, h) = barcode.rect
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # the barcode data is a bytes object so if we want to draw it on
                # our output image we need to convert it to a string first
                barcodeData = barcode.data.decode("utf-8")
                barcodeType = barcode.type

                # draw the barcode data and barcode type on the image
                text = "{} ({})".format(barcodeData, barcodeType)
                cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 255), 2)

                # print the barcode type and data to the terminal
                #print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

                if store_flag:
                    if barcodeData not in barcode_list:
                        barcode_list.append(barcodeData)
                else:
                    #print(barcodeData)
                    if barcodeData in barcode_list:

                        text = "Barcode {} in list".format(barcodeData)
                        cv2.putText(image, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)

                frame = image

        else:
            frame = np.zeros([480,640,3], dtype=np.float32)

        cv2.imshow("output", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
