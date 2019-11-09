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
        self.store_flag()
        self.log_packages()
        #self.locate_pickup()
        self.match_flag()
        self.land()

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
        playsound('audio_files/initial_flag.mp3')
        Shared.data.store_flag_flag = True

        time_start = time.time()

        while Shared.data.store_flag_flag and not self.close_thread and time.time() < time_start + 90:
            try:
                Shared.data.task_canvas.itemconfig(Shared.data.store_flag_indicator, fill='red')
            except AttributeError:
                print("INFO: WAITING FOR GUI")
                time.sleep(0.5)

            if self.close_thread:
                return

        if time.time() < time_start + 90:
            print("INFO: FLAG RECONGIZED!")
            playsound('audio_files/initial_flag_recognized.mp3')
            print("INFO: FLAG RECONGIZED!")
            Shared.data.task_canvas.itemconfig(Shared.data.store_flag_indicator, fill='green2')
            Shared.data.found_initial_flag = True
        else:
            playsound('audio_files/inital_flag_not_recognized.mp3')
            Shared.data.task_canvas.itemconfig(Shared.data.takeoff_flag_indicator, fill='yellow')
            Shared.data.found_initial_flag = False
            Shared.data.store_flag_flag = False

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
        print("INFO: {Shared.data.package_log}}")
        playsound('audio_files/logging_end.mp3')
        Shared.data.task_canvas.itemconfig(Shared.data.log_package_indicator, fill='green2')

    def locate_pickup(self):

        """Fourth Task: Locate Pick-Up Item

        """

        print("INFO: SEARCHING FOR PICKUP!")
        playsound('audio_files/pickup_search.mp3')
        Shared.data.find_pickup_flag = True

        time_start = time.time()

        while Shared.data.find_pickup_flag and not self.close_thread and time.time() < time_start + 360:
            try:
                Shared.data.task_canvas.itemconfig(Shared.data.pickup_indicator, fill='red')
            except AttributeError:
                print("INFO: WAITING FOR GUI")
                time.sleep(0.5)

            if self.close_thread:
                return

        if time.time() < time_start + 360:
            print("INFO: PICKUP FOUND!")
            playsound('audio_files/pickup_located.mp3')
            Shared.data.task_canvas.itemconfig(Shared.data.pickup_indicator, fill='green2')
        else:
            playsound('audio_files/pickup_not_located.mp3')
            Shared.data.task_canvas.itemconfig(Shared.data.pickup_indicator, fill='yellow')
            Shared.data.find_pickup_flag = False

    def match_flag(self):

        """Fifth Task: Match Flag

        """

        if not Shared.data.found_initial_flag:
            Shared.data.task_canvas.itemconfig(Shared.data.land_flag_indicator, fill='yellow')
            playsound('audio_files/no_initial_flag.mp3')

            return

        print("INFO: MATCHING FLAG!")

        Shared.data.find_land_flag = True

        time_start = time.time()

        playsound('audio_files/match_flag.mp3')
        while Shared.data.find_land_flag and not self.close_thread and time.time() < time_start + 90:
            try:
                Shared.data.task_canvas.itemconfig(Shared.data.land_flag_indicator, fill='red')
            except AttributeError:
                print("INFO: WAITING FOR GUI")
                time.sleep(0.5)

            if self.close_thread:
                return

        if time.time() < time_start + 90:
            print("INFO: FLAG MATHCED!")
            playsound('audio_files/flag_matched.mp3')
            Shared.data.task_canvas.itemconfig(Shared.data.land_flag_indicator, fill='green2')
        else:
            playsound('audio_files/flag_not_matched.mp3')
            Shared.data.task_canvas.itemconfig(Shared.data.land_flag_indicator, fill='yellow')
            Shared.data.find_land_flag = False

    def land(self):

        """Sixth Task: Land

        """

        print("INFO: Landing!")

        altitude = Shared.data.current_pos[2]
        playsound('audio_files/begin_landing.mp3')
        while abs(Shared.data.current_pos[2]) > 0.5 and not self.close_thread:
            try:
                Shared.data.task_canvas.itemconfig(Shared.data.land_indicator, fill='red')
            except AttributeError:
                print("INFO: WAITING FOR GUI")
                time.sleep(0.5)

            if self.close_thread:
                return

        print("INFO: Landed!")
        playsound('audio_files/landed.mp3')
        Shared.data.task_canvas.itemconfig(Shared.data.land_indicator, fill='green2')
