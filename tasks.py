import time
import tkinter as tk
import logging
import threading

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

        while not self.close_thread:

            self.takeoff()
            self.detect_aisle()

        return

    def takeoff(self):

        """First Task: Takeoff

        """

        logging.info("TAKING OFF!")
        while Shared.data.current_pos[2] - Shared.data.initial_pos[2] < Shared.data.takeoff_altitude:
            if self.close_thread:
                return
            time.sleep(0.1)
        logging.info("TAKEOFF ACHIEVED!")
        Shared.data.task_canvas.itemconfig(Shared.data.takeoff_indicator, fill='green2')

    def detect_aisle(self):

        """Second Taks: Detect Aisle

        """

        logging.info("SEARCHING FOR AISLE")
