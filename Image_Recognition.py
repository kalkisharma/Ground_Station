# MERGE OLLIE! MERGE!
import cv2
import apriltag
import math
import time
import imutils
import logging
import numpy as np
import Shared
import threading
from realsense_read import RealSenseRead as rsRead
from PIL import Image
import pytesseract
import Video_Capture



class MAVImageRecognition:
    def __init__(self):

        self.close_threads = False
        self.test_ImgRec = True

        self.outImg = np.zeros([480,640,3], dtype=np.float32)

    def compute_pixel_dist(self):
        width = 2*self.altitude*math.tan(self.theta/2)
        self.pix_to_meter = width/self.width

    def get_size(self, sidea, sideb, height):
        height = abs(height)
        if height < 0.3:
            return Shared.data.video_height * Shared.data.video_width
        else:
            img_v = 2 * height * math.tan(Shared.data.FOVV / 2)
            side_pixela = sidea * Shared.data.video_height / img_v
            side_pixelb = sideb * Shared.data.video_height / img_v
            return side_pixela * side_pixelb

    def detect_OCR(self):
        frame = np.copy(Shared.data.frame)
        output = {'data': [], 'time':time.time(),'type':"AN",'imgSize':[frame.shape[0],frame.shape[1]]}
        tag_width = 130
        tag_height = 65

        # Preprocess image
        Gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(Gray)

        # Detect edges in the image
        edges = cv2.Canny(gray, 0, 255)

        # Close gaps in detected edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
        edges = cv2.GaussianBlur(edges, (3, 3), 0)

        # Find contours in the image
        (cnts, hierarchy) = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # We are looking for a rectangular label, hence we only look at contours with four corners
        for i in range(len(cnts)):
            cnt = cnts[i]
            # Initialise corners of tag
            bot = []
            top = []
            bl = [-1, -1]
            br = [-1, -1]
            tl = [-1, -1]
            tr = [-1, -1]
            # Approximate the contour shape
            peri = cv2.arcLength(cnt, True)
            approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

            # Are there only four corners - i.e. a quadrilateral?
            isConvex = cv2.isContourConvex(approx)
            if len(approx) == 4 and isConvex == True:
                # Here we assume that we are seeing the label front on, so will likely be seeing a rectangle
                # (this seems to improve ocr performance when we dewarp
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                approx = np.int0(box)

                # Does the area have approximately the right size? And aspect ratio?
                (x, y), (rectW, rectH), angle = rect
                aspect_ratio = min(rectH, rectW) / max(rectH, rectW)
                if 1.2 * 0.5 > aspect_ratio > 0.8 * (0.05 / 0.15):
                    # We're pretty sure now we have the shelf label corners. Now we need to rotate and extract text
                    # We then first need to extract label corners (from approx) by identifying top-left, top-right,
                    # bottom-left, bottom-right
                    M = cv2.moments(approx)
                    cY = int(M["m01"] / M["m00"])
                    for i in approx:
                        if i[1] < cY:
                            top.append(i)
                        else:
                            bot.append(i)
                    if len(top) == 2 and len(bot) == 2:
                        tl = top[0] if top[0][0] < top[1][0] else top[1]
                        tr = top[1] if top[0][0] < top[1][0] else top[0]
                        bl = bot[0] if bot[0][0] < bot[1][0] else bot[1]
                        br = bot[1] if bot[0][0] < bot[1][0] else bot[0]
                    else:
                        continue

                    # De-rotate/warp to straighten sign
                    pts1 = np.float32([tl, bl, br, tr])
                    pts2 = np.float32([[0, 0], [0, tag_height], [tag_width, tag_height], [tag_width, 0]])
                    warp, mask = cv2.findHomography(pts1, pts2)
                    straight = cv2.warpPerspective(Gray.copy(), warp, (130, 65))

                    # Convert the image to binary and remove boarders
                    straight = cv2.threshold(straight, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
                    straight = straight[np.int0(tag_height * 0.12):np.int0(tag_height * 0.88),
                               np.int0(tag_width * 0.12):np.int0(tag_width * 0.88)]

                    # Is box likely to have text in it? (image_to_string is expensive, and we should avoid using it where possible)
                    kernel = np.array([[0, 0, 0, 0, 0],
                                       [0, 0, 0, 0, 0],
                                       [1, 1, 1, 1, 1],
                                       [0, 0, 0, 0, 0],
                                       [0, 0, 0, 0, 0]],
                                      dtype=np.uint8)
                    dilated = cv2.morphologyEx(straight, cv2.MORPH_ERODE, kernel, iterations=3)
                    dilated = cv2.bitwise_not(dilated)
                    (conts, _) = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    isText = False
                    for cont in conts:
                        minrect = cv2.minAreaRect(cont)
                        (Cx, Cy), (w, h), angle = minrect
                        textarea = w * h
                        if 0.7 * (dilated.shape[0] * dilated.shape[1]) > textarea > 0.3 * (
                                dilated.shape[0] * dilated.shape[1]) \
                                and ((Cx - 0.5 * dilated.shape[1]) ** 2 + (Cy - 0.5 * dilated.shape[0]) ** 2) ** (
                        0.5) < 0.25 * dilated.shape[0] \
                                and 0.8 > h / w > 0.3:
                            isText = True
                            break

                    if isText:
                        # Sharpen the image
                        blur = cv2.GaussianBlur(straight, (3, 3), 3)
                        straight = cv2.addWeighted(straight, 1.7, blur, -0.7, 0)
                        drc = cv2.copyMakeBorder(straight, top=10, bottom=10, left=10, right=10,
                                                 borderType=cv2.BORDER_CONSTANT,
                                                 value=(255, 255, 255))
                        # Extract text from image
                        PILimg = Image.fromarray(drc)
                        text = pytesseract.image_to_string(PILimg,
                                                           config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')

                        if len(text) == 3:
                            output['data'].append([text, np.array([x, y, rectH/frame.shape[0], rectW/frame.shape[1]])])
        return output

    def detect_package(self):

        current_pos = Shared.data.current_pos
        frame = np.copy(Shared.data.frame)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # HSV range for red box
        lower_red = np.array([114, 90, 100])
        upper_red = np.array([180, 255, 255])

        # only find pixels in image which fall into specified colour range
        maskhsv = cv2.inRange(hsv, lower_red, upper_red)
        # Gaussian to remove noisy region
        mask = cv2.medianBlur(maskhsv, 5)
        # Connect pixels
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        maskBGR = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        # 8-way pixel connectivity - centre pixel connected to its 8 neighbours
        connectivity = 8
        # Finds all connected pixels within binary maskhsv image
        output = cv2.connectedComponentsWithStats(mask, connectivity, cv2.CV_8U)
        # number of blobs in image seen with required colour
        num_labels = output[0]
        # Labels of blobs
        labels = output[1]
        # The location and size of bounding box of blobs
        stats = output[2]
        # The centroid of each bounding box
        centroids = output[3]
        max_area = 0
        index = -1
        max_centroid = [-1,-1]

        # Find the maximum blob in image
        for i in range(1, num_labels):
            statarea = stats[i, cv2.CC_STAT_AREA]
            if statarea > max_area:
                max_area = statarea
                index = i

        if index > -1:
            # Mask out everything outside box which bounds blob
            x_left = stats[index, cv2.CC_STAT_LEFT]
            y_top = stats[index, cv2.CC_STAT_TOP]
            width = stats[index, cv2.CC_STAT_WIDTH]
            height = stats[index, cv2.CC_STAT_HEIGHT]
            statarea = stats[index, cv2.CC_STAT_AREA]
            centroid = centroids[index]
            ROI = mask[y_top:y_top+height,x_left:x_left+width]
            mask = np.zeros_like(mask)
            mask[y_top:y_top+height,x_left:x_left+width] = ROI

            # Find bounding shape around collection of pixels.
            cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cont_sorted = sorted(cnts[0], key=lambda z: cv2.contourArea(z), reverse=True)
            peri = cv2.arcLength(cont_sorted[0], True)
            approx = cv2.approxPolyDP(cont_sorted[0], 0.04 * peri, True)
            area = cv2.contourArea(approx)

            alt = current_pos[2]
            box_area_small = self.get_size(0.15, 0.155, alt)
            box_area_large = self.get_size(0.21, 0.270, alt)
            if area > 0.5 * box_area_small and area < 1.8 * box_area_large:
                # Draw polygon around blob
                cv2.drawContours(maskBGR, [approx], -1, (0, 0, 255), 3)
                # Only send pixel centroid if area of blob is the right size
                max_centroid = centroid

        Shared.data.pixel_pos[0] = max_centroid[0]
        Shared.data.pixel_pos[1] = max_centroid[1]

        return

    def process_image(self):

        while not self.close_threads:

            self.detect_package()

        return

    def start_process_thread(self):

        self.process_thread = threading.Thread(target=self.process_image)
        self.process_thread.start()

        return

    def start(self):

        self.start_process_thread()

        return

    def stop(self):

        self.close_threads = True

        return

if __name__=='__main__':

    image = MAVImageRecognition()

    # Thread to display image
    video = Video_Capture.MyVideoCapture(0, show_video=True)
    video.start()

    # Loop to recognize images
    image.start()
    
    # Start realsense
    rs = rsRead()
    rs.start()

    # Loop while realsense connected
    while rs.rsConnect:
        pos = rs.get_pose()
        #Shared.data.current_pos[0] =
        #Shared.data.current_pos[0] =
        #Shared.data.current_pos[0] =
        #Shared.data.current_yaw =

    rs.stop()
    image.stop()
    video.stop()
