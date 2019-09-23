# import the necessary packages
from pyzbar import pyzbar
import argparse
import cv2
import threading
import time
import imutils
import numpy as np
import Shared

def store_qr():

    frame = np.copy(Shared.data.frame)
    ret = Shared.data.ret

    #cv2.putText(frame, 'Storing QR Data', (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
    #    1, (0, 255, 0), 2)

    if ret:

        image = frame

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


            if barcodeData not in Shared.data.barcode_list:
                Shared.data.barcode_list.append(barcodeData)
            else:
                #print(barcodeData)
                if barcodeData in Shared.data.barcode_list:

                    text = "Barcode {} in list".format(barcodeData)
                    cv2.putText(image, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                        1, (0, 255, 0), 2)

            frame = image

    Shared.data.frame_image_recognition = frame

def display_qr():

    frame = np.copy(Shared.data.frame)
    ret = Shared.data.ret

    text = "{}".format(Shared.data.barcode_list)
    cv2.putText(frame, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
        1, (0, 255, 0), 2)

    Shared.data.frame_image_recognition = frame

def detect_qr():

    frame = np.copy(Shared.data.frame)
    ret = Shared.data.ret

    if ret:

        #frame = imutils.resize(frame, width=400)
        # load the input image
        image = frame #cv2.imread(frame)

        text = "Detecting QR"
        cv2.putText(image, text, (400, 50), cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 255, 0), 2)

        # find the barcodes in the image and decode each of the barcodes
        barcodes = pyzbar.decode(image)
        pixel_data = []
        barcodeData = []
        # loop over the detected barcodes
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw the
            # bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            pixel_data.append((x, y, w, h))
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

            if Shared.data.find_shelf:
                if barcodeData==Shared.data.shelf_number[0]:
                    Shared.data.image_data = {
                        'data' : barcodeData, # List of values obtained from detection (e.g. qr code values)
                        'time' : time.time(),
                        'type' : 'QR',
                        'pixel' :  pixel_data# List of pixel width and height relative to frame size
                    }
                    break
            elif Shared.data.find_shelf_row:
                if barcodeData==Shared.data.shelf_row[0]:
                    Shared.data.image_data = {
                        'data' : barcodeData, # List of values obtained from detection (e.g. qr code values)
                        'time' : time.time(),
                        'type' : 'QR',
                        'pixel' :  pixel_data# List of pixel width and height relative to frame size
                    }
                    break
            """
            if barcodeData in Shared.data.barcode_list:

                text = "Barcode {} in list".format(barcodeData)
                cv2.putText(image, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2)
            """
            frame = image

    else:
        frame = np.zeros((480,640,3), np.uint8)

    Shared.data.frame_image_recognition = frame
    Shared.data.image_data = {
        'data' : barcodeData, # List of values obtained from detection (e.g. qr code values)
        'time' : time.time(),
        'type' : 'QR',
        'pixel' :  pixel_data# List of pixel width and height relative to frame size
    }
