# import the necessary packages
from pyzbar import pyzbar
import argparse
import cv2
import threading
import time
import imutils
import numpy as np
import logging
from playsound import playsound
from image_recognition.alpha_numeric import detect_OCR
import Image_Recognition
import Shared
import image_recognition.qrEKF as qrEKF

def log_package_v2():

    frame = np.copy(Shared.data.frame)
    ret = Shared.data.ret

    if ret:

        image = frame

        text = "Detecting QR"
        cv2.putText(image, text, (400, 50), cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 255, 0), 2)

        #Shared.data.frame_image_recognition = image

        # find the barcodes in the image and decode each of the barcodes
        barcodes = pyzbar.decode(image)
        pixel_data = []
        barcodeData_list = []
        fpMeasDB = []

        # loop over the detected barcodes
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw the
            # bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            pixel_data.append((x, y, w, h))

            # Get centre of barcode for EKF
            Cx = ((x + w) / 2 - 0.5 * Shared.data.gui_video_width) / (0.5 * Shared.data.gui_video_width) * (
                    Shared.data.sensorU / Shared.data.sensorU)
            Cy = ((x + h) / 2 - 0.5 * Shared.data.gui_video_height) / (0.5 * Shared.data.gui_video_height) * (
                    Shared.data.sensorV / Shared.data.sensorU)

            # the barcode data is a bytes object so if we want to draw it on
            # our output image we need to convert it to a string first
            barcodeData = str(barcode.data.decode("utf-8"))
            barcodeData_list.append(barcodeData)
            barcodeType = barcode.type

            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 0, 255), 2)
            Shared.data.frame_image_recognition = frame
            #print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

            if Shared.data.est_shelf_dist:
                tempFP = qrEKF.fpMeas(barcodeData, Cx, Cy)
                fpMeasDB.append(tempFP)

                rs_pos = Shared.data.current_pos
                rs_att = Shared.data.current_attitude
                Shared.data.ekf.measUpdate(rs_pos, rs_att, fpMeasDB)
                Shared.data.ekfTime2 = time.time()
                dt = Shared.data.ekfTime2 - Shared.data.ekfTime1
                Shared.data.ekf.procUpdate(dt)
                Shared.data.ekfTime1 = time.time()

            frame = image

            # Check if barcode cooresponds to a shelf id
            if barcodeData in Shared.data.shelf_code:

                if len(Shared.data.current_package)==0:
                    pass
                    #playsound('audio_files/ignore_shelf.mp3')

                else:

                    playsound('audio_files/append_to_shelf.mp3')

                    log_dict = Shared.data.package_log

                    for package in Shared.data.current_package:

                        Shared.data.save_package.append(package)

                        key = barcodeData
                        value = package

                        if key in log_dict:
                            if value in log_dict[key]:
                                pass
                            else:
                                log_dict[key].append(value)
                        else:
                            log_dict[key] = [value]

                    print(log_dict)
                    Shared.data.package_log = log_dict
                    Shared.data.current_package = []

                    if len(Shared.data.save_package)==Shared.data.npackages:

                        return

            else:

                if barcodeData in Shared.data.package_list:

                    Shared.data.current_package.append(barcodeData)
                    Shared.data.package_list.remove(barcodeData)
                    Shared.data.recorded_qr.append(barcodeData)

                    #playsound('audio_files/package_located.mp3')

                else:

                    if barcodeData not in Shared.data.recorded_qr:

                        Shared.data.recorded_qr.append(barcodeData)

                        #playsound('audio_files/not_package.mp3')

                    else:
                        pass
                        #playsound('audio_files/already_recorded.mp3')

        if len(barcodes)==0:

            Shared.data.frame_image_recognition = frame

    else:

        Shared.data.frame_image_recognition = frame

def log_package_v3():

    frame = np.copy(Shared.data.frame)
    ret = Shared.data.ret

    if ret:

        image = frame

        text = "Detecting Packages"
        cv2.putText(image, text, (400, 50), cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 255, 0), 2)

        #Shared.data.frame_image_recognition = image

        # find the barcodes in the image and decode each of the barcodes
        barcodes = pyzbar.decode(image)
        pixel_data = []
        barcodeData_list = []
        fpMeasDB = []

        # Find shelf number
        if Shared.data.frame_num % 5 == 0:
            found_shelf = detect_OCR()

            if found_shelf:
                if len(Shared.data.current_package)==0:
                    pass
                    #playsound('audio_files/ignore_shelf.mp3')

                else:

                    playsound('audio_files/append_to_shelf.mp3')

                    log_dict = Shared.data.package_log

                    for package in Shared.data.current_package:

                        Shared.data.save_package.append(package)

                        key = Shared.data.image_data['data']
                        value = package

                        if key in log_dict:
                            if value in log_dict[key]:
                                pass
                            else:
                                log_dict[key].append(value)
                        else:
                            log_dict[key] = [value]

                    print(log_dict)
                    Shared.data.package_log = log_dict
                    Shared.data.current_package = []

                    if len(Shared.data.save_package) == Shared.data.npackages:

                        return


        # loop over the detected barcodes
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw the
            # bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            pixel_data.append((x, y, w, h))

            # Get centre of barcode for EKF
            Cx = ((x + w/2) - 0.5*Shared.data.gui_video_width)/(0.5*Shared.data.gui_video_width)*(Shared.data.sensorU/Shared.data.sensorU)
            Cy = ((y + h/2) - 0.5*Shared.data.gui_video_height)/(0.5*Shared.data.gui_video_height)*(Shared.data.sensorV/Shared.data.sensorU)

            # the barcode data is a bytes object so if we want to draw it on
            # our output image we need to convert it to a string first
            barcodeData = str(barcode.data.decode("utf-8"))
            barcodeData_list.append(barcodeData)
            barcodeType = barcode.type

            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 0, 255), 2)
            Shared.data.frame_image_recognition = frame
            #print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

            if Shared.data.est_shelf_dist:
                tempFP = qrEKF.fpMeas(barcodeData, Cx, Cy)
                fpMeasDB.append(tempFP)

                rs_pos = Shared.data.current_pos
                rs_att = Shared.data.current_attitude
                Shared.data.ekf.measUpdate(rs_pos, rs_att, fpMeasDB)
                Shared.data.ekfTime2 = time.time()
                dt = Shared.data.ekfTime2 - Shared.data.ekfTime1
                Shared.data.ekf.procUpdate(dt)
                Shared.data.ekfTime1 = time.time()

            frame = image

            # Check if barcode cooresponds to a shelf id
            """if barcodeData in Shared.data.shelf_code:

                if len(Shared.data.current_package)==0:

                    playsound('audio_files/ignore_shelf.mp3')

                else:

                    playsound('audio_files/append_to_shelf.mp3')

                    log_dict = Shared.data.package_log

                    for package in Shared.data.current_package:

                        Shared.data.save_package.append(package)

                        key = barcodeData
                        value = package

                        if key in log_dict:
                            if value in log_dict[key]:
                                pass
                            else:
                                log_dict[key].append(value)
                        else:
                            log_dict[key] = [value]

                    print(log_dict)
                    Shared.data.package_log = log_dict
                    Shared.data.current_package = []

                    if len(Shared.data.save_package)==Shared.data.npackages:

                        return

            else:"""
            if barcodeData not in Shared.data.shelf_code:
                if barcodeData in Shared.data.package_list:

                    Shared.data.current_package.append(barcodeData)
                    Shared.data.package_list.remove(barcodeData)
                    Shared.data.recorded_qr.append(barcodeData)

                    #playsound('audio_files/package_located.mp3')

                else:

                    if barcodeData not in Shared.data.recorded_qr:

                        Shared.data.recorded_qr.append(barcodeData)

                        #playsound('audio_files/not_package.mp3')

                    else:
                        pass
                        #playsound('audio_files/already_recorded.mp3')

        if len(barcodes)==0:

            Shared.data.frame_image_recognition = frame

    else:

        Shared.data.frame_image_recognition = frame

def log_package_v4(ekf=None):

    frame = np.copy(Shared.data.frame)
    ret = Shared.data.ret

    if ret:

        image = frame

        text = "Detecting Packages"
        cv2.putText(image, text, (400, 50), cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 255, 0), 2)

        #Shared.data.frame_image_recognition = image

        # find the barcodes in the image and decode each of the barcodes
        barcodes = pyzbar.decode(image)
        pixel_data = []
        barcodeData_list = []

        # Find shelf number
        if Shared.data.frame_num % 5 == 0:
            found_shelf = detect_OCR()

            if found_shelf:
                if len(Shared.data.current_package)==0:
                    pass
                    #playsound('audio_files/ignore_shelf.mp3')

                else:

                    playsound('audio_files/append_to_shelf.mp3')

                    log_dict = Shared.data.package_log

                    for package in Shared.data.current_package:

                        Shared.data.save_package.append(package)

                        key = Shared.data.image_data['data']
                        value = package

                        if key in log_dict:
                            if value in log_dict[key]:
                                pass
                            else:
                                log_dict[key].append(value)
                        else:
                            log_dict[key] = [value]

                    print(log_dict)
                    Shared.data.package_log = log_dict
                    Shared.data.current_package = []

                    if len(Shared.data.save_package) == Shared.data.npackages:

                        return


        # loop over the detected barcodes
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw the
            # bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            pixel_data.append((x, y, w, h))
            # the barcode data is a bytes object so if we want to draw it on
            # our output image we need to convert it to a string first
            barcodeData = str(barcode.data.decode("utf-8"))
            barcodeData_list.append(barcodeData)
            barcodeType = barcode.type

            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 0, 255), 2)
            Shared.data.frame_image_recognition = frame
            #print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

            frame = image

            # Check if barcode cooresponds to a shelf id
            """if barcodeData in Shared.data.shelf_code:

                if len(Shared.data.current_package)==0:

                    playsound('audio_files/ignore_shelf.mp3')

                else:

                    playsound('audio_files/append_to_shelf.mp3')

                    log_dict = Shared.data.package_log

                    for package in Shared.data.current_package:

                        Shared.data.save_package.append(package)

                        key = barcodeData
                        value = package

                        if key in log_dict:
                            if value in log_dict[key]:
                                pass
                            else:
                                log_dict[key].append(value)
                        else:
                            log_dict[key] = [value]

                    print(log_dict)
                    Shared.data.package_log = log_dict
                    Shared.data.current_package = []

                    if len(Shared.data.save_package)==Shared.data.npackages:

                        return

            else:"""
            if barcodeData not in Shared.data.shelf_code:
                if barcodeData in Shared.data.package_list:

                    Shared.data.current_package.append(barcodeData)
                    Shared.data.package_list.remove(barcodeData)
                    Shared.data.recorded_qr.append(barcodeData)

                    #playsound('audio_files/package_located.mp3')

                else:

                    if barcodeData not in Shared.data.recorded_qr:

                        Shared.data.recorded_qr.append(barcodeData)

                        #playsound('audio_files/not_package.mp3')

                    else:
                        pass
                        #playsound('audio_files/already_recorded.mp3')

        if len(barcodes)==0:

            Shared.data.frame_image_recognition = frame

    else:

        Shared.data.frame_image_recognition = frame


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
            print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

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
            elif Shared.data.log_package_flag:
                if barcodeData not in Shared.data.package_log:
                    Shared.data.package_log.append(barcodeData)
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

def log_package():

    frame = np.copy(Shared.data.frame)
    ret = Shared.data.ret

    if ret:

        image = frame

        text = "Detecting QR"
        cv2.putText(image, text, (400, 50), cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 255, 0), 2)

        #Shared.data.frame_image_recognition = image

        # find the barcodes in the image and decode each of the barcodes
        barcodes = pyzbar.decode(image)
        pixel_data = []
        barcodeData_list = []

        # loop over the detected barcodes
        for barcode in barcodes:
            # extract the bounding box location of the barcode and draw the
            # bounding box surrounding the barcode on the image
            (x, y, w, h) = barcode.rect
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 0, 255), 2)
            pixel_data.append((x, y, w, h))
            # the barcode data is a bytes object so if we want to draw it on
            # our output image we need to convert it to a string first
            barcodeData = str(barcode.data.decode("utf-8"))
            barcodeData_list.append(barcodeData)
            barcodeType = barcode.type

            # draw the barcode data and barcode type on the image
            text = "{} ({})".format(barcodeData, barcodeType)
            cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
            0.5, (0, 0, 255), 2)
            Shared.data.frame_image_recognition = frame
            #print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

            frame = image

            if barcodeData in Shared.data.package_list:

                print("INFO: FOUND {} BARCODE: {}".format(barcodeType, barcodeData))
                Shared.data.package_list.remove(barcodeData)
                Shared.data.found_packages.append(barcodeData)
                Shared.data.recorded_qr.append(barcodeData)
                print(Shared.data.found_packages)
                #playsound('audio_files/package_located.mp3')

            elif barcodeData not in Shared.data.recorded_qr and barcodeData not in Shared.data.shelf_code:

                Shared.data.recorded_qr.append(barcodeData)
                print("INFO: {} NOT IN PACKAGE LIST".format(barcodeData))
                #playsound('audio_files/not_package.mp3')

            elif barcodeData in Shared.data.shelf_code:

                Shared.data.current_shelf = barcodeData

                if len(Shared.data.found_packages) > 0:

                    key = Shared.data.current_shelf
                    log_dict = Shared.data.package_log
                    values = Shared.data.found_packages

                    if key in log_dict:
                        for value in values:
                            if value in log_dict[key]:
                                pass
                            else:
                                log_dict[key].append(value)
                    else:
                        log_dict[key] = values

                    Shared.data.package_log = log_dict

                    print(f"INFO: LOG DICT: {Shared.data.package_log}")

                    #playsound('audio_files/save_package.mp3')

                    if len(Shared.data.current_package)==0:

                        Shared.data.current_package = Shared.data.found_packages
                    else:

                        Shared.data.current_package += Shared.data.found_packages
                    #print(Shared.data.current_package)
                    Shared.data.current_shelf = ''
                    Shared.data.found_packages = []

                return

            else:

                print("INFO: {} REPEATED".format(barcodeData))
                #playsound('audio_files/already_recorded.mp3')
            #Shared.data.frame_image_recognition = frame
        """
        for barcode_text in Shared.data.barcode_list:
            print(barcode_text)
            if barcode_text in Shared.data.shelf_code:

                Shared.data.current_shelf = barcode_text

                return
        """
        if len(barcodes)==0:

            Shared.data.frame_image_recognition = frame

    else:

        Shared.data.frame_image_recognition = frame

def log_shelf():

    frame = np.copy(Shared.data.frame)
    ret = Shared.data.ret

    if ret:

        image = frame

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
            print("INFO: FOUND {} BARCODE: {}".format(barcodeType, barcodeData))
            barcodeData = str(barcodeData)
            if barcodeData in Shared.data.shelf_code:

                print("INFO: FOUND SHELF: {}".format(barcodeData))
                Shared.data.current_shelf = barcodeData
                Shared.data.shelf_code.remove(barcodeData)

            frame = image

            Shared.data.frame_image_recognition = frame

    Shared.data.frame_image_recognition = frame
