import cv2
import apriltag
import math
import time
import imutils
import logging
import numpy as np

class MAVImageRecognition:
    def __init__(self, server_):
        self.frame = None
        self.server = server_
        self.tag_name = ""
        self.target_name = ""

        self.width = int(self.server.video.width)
        self.height = int(self.server.video.height)
        self.quad_x = int(self.width/2)
        self.quad_y = int(self.height/2)

        self.theta = math.radians(62.2) # width angle of picam
        self.psi = math.radians(48.8) # height angle of picam
        self.pix_to_meter = 0
        self.altitude = 1

        options = apriltag.DetectorOptions(families='tag36h11',
                                           border=1,
                                           nthreads=1,
                                           quad_decimate=1.0,
                                           quad_blur=0.0,
                                           refine_edges=True,
                                           refine_decode=True,
                                           refine_pose=True,
                                           debug=False,
                                           quad_contours=True)

        self.detector = apriltag.Detector(options)

        self.x = 100
        self.y = 100

    def compute_pixel_dist(self):
        width = 2*self.altitude*math.tan(self.theta/2)
        self.pix_to_meter = width/self.width

    def detect_apriltag(self):

        name = self.tag_name
        frame = self.frame
        if name == "PICKUP":
            tag_numbers = [131, 132, 133, 134]
        elif name == "DROPOFF":
            tag_numbers = [127, 128, 129, 130]
        elif name == "FERRY":
            tag_numbers = [123, 124, 125, 126]
        elif name == "HOME":
            tag_numbers = [119, 120, 121, 122]
        else:
            self.x = 100
            self.y = 100
            return frame
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
        detections, dimg = self.detector.detect(gray, return_image=True)
        overlay = frame // 2 + dimg[:, :, None] // 2

        if len(detections) > 0:
            pixel_loc = []

            for i, tags in enumerate(detections):
                #print(tags[1])
                if tags[1] in tag_numbers:
                    break
                else:
                    return
            pixel_loc.append(tags.center)
            x = int(pixel_loc[0][0])
            y = int(pixel_loc[0][1])
            cv2.line(frame,(int(self.width/2),int(self.height/2)),(x,y),(255,0,0),5)
            cv2.rectangle(frame, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
            self.x = (self.quad_x - x)*self.pix_to_meter
            self.y = (self.quad_y - y)*self.pix_to_meter
            return frame

        self.x = 100
        self.y = 100
        return frame

    def detect_target(self):

        name = self.target_name
        frame = self.frame

        if name == "PICKUP":
            (x,y) = self.detect_pickup()
        elif name == "DROPOFF":
            (x,y) = self.detect_dropoff()
        elif name == "HOME":
            (x,y) = self.detect_home()
        else:
            return frame
        self.x = x
        self.y = y

        return frame

    def detect_border(self):
        ilowH = 21
        ihighH = 39
        ilowS = 157
        ihighS = 255
        ilowV = 111
        ihighV = 210
        width = self.width
        height = self.height
        frame = self.frame

        hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

        lower_hsv = np.array([ilowH, ilowS, ilowV])
        higher_hsv = np.array([ihighH, ihighS, ihighV])
        mask = cv2.inRange(hsv,lower_hsv,higher_hsv)

        location = cv2.findNonZero(mask)

        if location is not None:
            #total = location[0] * location[1]
            try:
                line = cv2.fitLine(location, cv2.DIST_L2,0,0.01,0.01)
                slope = line[1]/line[0] ;
                y_intercept = line[3] - slope * line[2];
                x_intercept = -1*(y_intercept/slope);
                y1 = slope*0+y_intercept
                y2 = slope*width+y_intercept
                cv2.line(frame,(0,y1),(width,y2),(255,0,0),5)

                slope_perp = -1/slope
                y_int_perp = height/2-slope_perp*width/2
                x_perp = int((y_int_perp-y_intercept) / (slope-slope_perp))
                y_perp = int(slope_perp*x_perp + y_int_perp)
                cv2.line(frame,(int(width/2),int(height/2)),(x_perp,y_perp),(255,0,0),5)
                cv2.rectangle(frame, (x_perp - 5, y_perp - 5), (x_perp + 5, y_perp + 5), (0, 128, 255), -1)
                self.x = (self.quad_x - x_perp)*self.pix_to_meter
                self.y = (self.quad_y - y_perp)*self.pix_to_meter
                return frame
            except (OverflowError, ValueError):
                return frame

        return frame

    def detect_dropoff(self):
        pass

    def detect_home(self):
        pass

    def detect_pickup():

        resized = imutils.resize(frame, width=300)
        ratio = frame.shape[0] / float(resized.shape[0])

        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        thresh = cv2.threshold(blurred, 100, 255, cv2.THRESH_BINARY_INV)[1]
        #return thresh, (x,y)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
    	   cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        sd = ShapeDetector()

        for c in cnts:
    	# compute the center of the contour, then detect the name of the
    	# shape using only the contour

            shape = sd.detect(c)

            if shape == 'square':
        	# multiply the contour (x, y)-coordinates by the resize ratio,
        	# then draw the contours and the name of the shape on the image
                M = cv2.moments(c)
                cX = int((M["m10"] / M["m00"]) * ratio)
                cY = int((M["m01"] / M["m00"]) * ratio)
                peri = cv2.arcLength(c, True)
                print(peri)
                c = c.astype("float")
                c *= ratio
                c = c.astype("int")
                cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
                cv2.circle(frame, (cX, cY), 3, (255, 255, 255), -1)
                """
                side = resolution*peri/4.0;
                side_world = alt*side/f_length

                if side_world < 10.0:
                    continue
                else:
                    print("HERE")
                    c = c.astype("float")
                    c *= ratio
                    c = c.astype("int")
                    cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
                    cv2.circle(frame, (cX, cY), 3, (255, 255, 255), -1)
                """
            else:
                continue

        return frame

def main(image):
    time.sleep(1)
    while True:
        image.server.lock.acquire()
        image.frame = image.server.get_frame()
        image.server.lock.release()

        image.compute_pixel_dist()
        #frame = image.detect_border()
        frame = image.detect_apriltag()
        frame = image.detect_target()

        cv2.imshow("Image", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
