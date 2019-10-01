import time
import tkinter as tk
import logging
import threading
from playsound import playsound

import Shared

class TaskScheduler:

    def __init__(self):

        self.close_thread = False

    def start(self):

        self.task_thread = threading.Thread(target=self.checklist)
        self.task_thread.start()

    def stop(self):

        self.close_thread = True

    def checklist(self):

        while not Shared.data.GUI_STARTED_FLAG:
            time.sleep(0.5)

        self.takeoff()
        #self.store_flag()
        self.log_packages()
        #self.locate_pickup()

        return

    def takeoff(self):

        """First Task: Takeoff

        """

        print("INFO: TAKING OFF!")
        playsound('audio_files/takeoff_begin')
        while Shared.data.current_pos[2] - Shared.data.initial_pos[2] > Shared.data.takeoff_altitude:

            try:
                Shared.data.task_canvas.itemconfig(Shared.data.takeoff_indicator, fill='red')
            except AttributeError:
               # print("INFO: WAITING FOR GUI")
                time.sleep(0.5)

            if self.close_thread:
                return

        playsound('audio_files/takeoff_end')
        print("INFO: TAKEOFF ACHIEVED!")
        Shared.data.task_canvas.itemconfig(Shared.data.takeoff_indicator, fill='green2')


    def store_flag(self):

        """Second Task: Store the Flag

        """

        print("INFO: RECOGNIZING FLAG!")

        Shared.data.store_flag_flag = True

        while Shared.data.store_flag_flag and not self.close_thread:
            try:
                Shared.data.task_canvas.itemconfig(Shared.data.store_flag_indicator, fill='red')
            except AttributeError:
                print("INFO: WAITING FOR GUI")
                time.sleep(0.5)

            if self.close_thread:
                return

        print("INFO: FLAG RECONGIZED!")
        Shared.data.task_canvas.itemconfig(Shared.data.store_flag_indicator, fill='green2')

    def log_packages(self):

        """Third Task: Log Package Shelf

        """

        print("INFO: LOGGING PACKAGES!")
        playsound('audio_files/logging_start.mp3')
        Shared.data.log_package_flag = True

        while Shared.data.log_package_flag and not self.close_thread:
            try:
                Shared.data.task_canvas.itemconfig(Shared.data.log_package_indicator, fill='red')
            except AttributeError:
                #print("INFO: WAITING FOR GUI")
                time.sleep(0.5)

            if self.close_thread:
                return

        print("INFO: PACKAGES LOGGED!")
        playsound('audio_files/logging_end.mp3')
        Shared.data.task_canvas.itemconfig(Shared.data.log_package_indicator, fill='green2')

    def locate_pickup(self):

        """Fourth Task: Locate Pick-Up Item

        """

        print("INFO: SEARCHING FOR PACKAGE!")

        Shared.data.find_pickup_flag = True

        while Shared.data.find_pickup_flag and not self.close_thread:
            try:
                Shared.data.task_canvas.itemconfig(Shared.data.pickup_indicator, fill='red')
            except AttributeError:
                print("INFO: WAITING FOR GUI")
                time.sleep(0.5)

            if self.close_thread:
                return

        print("INFO: PICKUP FOUND!")
        Shared.data.task_canvas.itemconfig(Shared.data.pickup_indicator, fill='green2')
