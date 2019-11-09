import tkinter as tk
#import audio_recorder as ar
import threading
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot
import numpy as np
import cv2
import math
from math import sin, cos, tan
import time
import PIL.Image, PIL.ImageTk
import logging
from image_recognition.qrEKF import euler2dcm321

import Shared
import signal

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800

DUAL_MONITOR = False



class GUI:
    def __init__(self):

        self.text = []
        self.root = tk.Tk()

    def start(self):
        app = Window(self.root, self)
        self.root.mainloop()

    def stop(self):
        self.close_threads = True

class Window(tk.Tk):

    def __init__(self, master=None, gui=None):

        container = tk.Frame.__init__(self, master)
        self.master = master
        self.gui = gui
        self.init_window(container)

    def init_window(self, container):

        self.window_config()
        self.window_menu()
        self.cycle_frames(container)
        #curr_label = tk.Label(self, text="Set Desired State")
        #curr_label.grid(row=5, column=0, columnspan=3, sticky=tk.W)

    def window_config(self):

        self.master.title("Quadcopter GUI")

        #self.master.configure(background = '#000000')

        if (DUAL_MONITOR):
            screen_width = self.winfo_screenwidth()/2
        else:
            screen_width = self.winfo_screenwidth()

        screen_height = self.winfo_screenheight()
        x_coord = screen_width/2 - WINDOW_WIDTH/2
        y_coord = screen_height/2 - WINDOW_HEIGHT/2

        self.master.geometry("%dx%d+%d+%d" % (WINDOW_WIDTH, WINDOW_HEIGHT, x_coord, y_coord))

        #self.master.resizable(width = False, height = False)

    def window_menu(self):

        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        file = tk.Menu(menu)
        file.add_command(label="Exit", command=self.close_window, accelerator = "Esc")
        self.master.bind("<Escape>", self.close_window)
        self.master.bind("<Control-c>", self.close_window)
        menu.add_cascade(label="File", menu=file)

    def close_window(self, event = None):

        self.gui.stop()
        exit()

    def cycle_frames(self, container):

        frame = command_page(parent = container, controller = self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

class command_page(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.controller = controller

        #self.create_listener_canvas()

        #self.create_graph_canvas()
        self.create_video_canvas(_row=0, _column=0, _rowspan=10, _columnspan=10)
        self.create_video_textbox(_row=10, _column=10)
        self.create_image_buttons(_row=10, _column=15)
        self.create_checklist(_row=0, _column=20, _rowspan=10, _columnspan=10)
        self.create_qr_label(_row=11, _column=10)#, _rowspan=10, _columnspan=10)
        self.figure = matplotlib.pyplot.figure()
        self.plot = self.figure.add_subplot(111)
        #self.create_package_buttons(_row=5, _column=1)
        #self.create_movement_buttons(_row=0, _column=2)
        self._video()
        Shared.data.GUI_STARTED_FLAG = True
        #self._plot()
        #self._listen_check()


        #self.test()

    def create_qr_label(self, _row=1, _column=1, _rowspan=1, _columnspan=1):

        self.qr_label = tk.Label(self, text=f'Stored QR Codes: {Shared.data.package_list}')
        self.qr_label.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

    def create_checklist(self, _row=1, _column=1, _rowspan=1, _columnspan=1):

        self.task_canvas = tk.Canvas(self, bg='gray90')#, width = width, height = height)
        Shared.data.task_canvas = self.task_canvas
        self.task_canvas.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

        Shared.data.takeoff_indicator = self.task_canvas.create_oval(10, 10, 25, 25, outline="black",
            fill="white", width=1)
        self.task_canvas.create_text(30, 17.5, anchor=tk.W, font=("Times", 14),
            text="Takeoff")

        Shared.data.takeoff_flag_indicator = self.task_canvas.create_oval(10, 30, 25, 45, outline="black",
            fill="white", width=1)
        self.task_canvas.create_text(30, 37.5, anchor=tk.W, font=("Times", 14),
            text="Store Flag")

        Shared.data.log_package_indicator = self.task_canvas.create_oval(10, 50, 25, 65, outline="black",
            fill="white", width=1)
        self.task_canvas.create_text(30, 57.5, anchor=tk.W, font=("Times", 14),
            text="Logging Packages")

        Shared.data.pickup_indicator = self.task_canvas.create_oval(10, 70, 25, 85, outline="black",
            fill="white", width=1)
        self.task_canvas.create_text(30, 77.5, anchor=tk.W, font=("Times", 14),
            text="Searching for Pickup")

        Shared.data.land_flag_indicator = self.task_canvas.create_oval(10, 90, 25, 105, outline="black",
            fill="white", width=1)
        self.task_canvas.create_text(30, 97.5, anchor=tk.W, font=("Times", 14),
            text="Match Flag")

        Shared.data.land_indicator = self.task_canvas.create_oval(10, 110, 25, 125, outline="black",
            fill="white", width=1)
        self.task_canvas.create_text(30, 117.5, anchor=tk.W, font=("Times", 14),
            text="Land")

    def create_movement_buttons(self, _row=1, _column=1, _rowspan=1, _columnspan=1):

        self.takeoff_button = tk.Button(self, text='Takeoff', command=self.toggle_takeoff)
        self.takeoff_button.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

    def toggle_takeoff(self):

        Shared.data.desired_pos = Shared.data.current_pos
        Shared.data.desired_attitude = Shared.data.current_attitude
        Shared.data.desired_pos[2] = Shared.data.takeoff_altitude

    def create_package_buttons(self, _row=1, _column=1, _rowspan=1, _columnspan=1):

        self.package_button = tk.Button(self, text='Pickup', command=self.toggle_pickup)
        self.package_button.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

    def toggle_pickup(self):

        if Shared.data.pickup_flag:
            self.package_button.config(relief=tk.RAISED)
            Shared.data.msg_payload_send[0] = -1
            Shared.data.pickup_flag = False
        else:
            self.package_button.config(relief=tk.SUNKEN)
            Shared.data.msg_payload_send[0] = -2
            Shared.data.pickup_flag = True

    def create_image_buttons(self, _row=1, _column=1, _rowspan=1, _columnspan=1):

        self.toggle_pickup_button = tk.Button(self, text='SERVO CLOSED', command=self.toggle_pickup)
        self.toggle_pickup_button.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

        _row+=1
        self.qr_detect_button = tk.Button(self, text='QR', command=self.detect_qr)
        self.qr_detect_button.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

        _row+=1
        self.an_detect_button = tk.Button(self, text='AN', command=self.detect_an)
        self.an_detect_button.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

        _row+=1
        self.package_detect_button = tk.Button(self, text='Package', command=self.detect_package)
        self.package_detect_button.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

        _row+=1
        self.shelf_number_detect_button = tk.Button(self, text='Shelf Number', command=self.detect_shelf_number)
        self.shelf_number_detect_button.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

        _row+=1
        self.shelf_row_detect_button = tk.Button(self, text='Shelf Row', command=self.detect_shelf_row)
        self.shelf_row_detect_button.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

        _row+=1
        self.log_packages_button = tk.Button(self, text='Package Log', command=self.log_packages)
        self.log_packages_button.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

    def toggle_pickup(self):

        if Shared.data.toggle_pickup_flag:
            self.toggle_pickup_button.config(relief=tk.RAISED)
            self.toggle_pickup_button.config(text='SERVO CLOSED')
            Shared.data.toggle_pickup_flag = False
            print(f"INFO: SERVO CLOSED")
            Shared.data.msg_payload_send[0] = -2
        else:
            self.toggle_pickup_button.config(relief=tk.SUNKEN)
            self.toggle_pickup_button.config(text='SERVO OPENED')
            Shared.data.toggle_pickup_flag = True
            print(f"INFO: SERVO OPENED")
            Shared.data.msg_payload_send[0] = -1

    def log_packages(self):

        if Shared.data.log_package_flag:
            self.log_packages_button.config(relief=tk.RAISED)
            Shared.data.log_package_flag = False
            print(f"INFO: PACKAGE LOG VALUES: {Shared.data.package_log}")
        else:
            self.log_packages_button.config(relief=tk.SUNKEN)
            Shared.data.log_package_flag = True

    def detect_shelf_row(self):

        if Shared.data.find_shelf_row:
            self.shelf_row_detect_button.config(relief=tk.RAISED)
            Shared.data.find_shelf_row = False
        else:
            self.shelf_row_detect_button.config(relief=tk.SUNKEN)
            Shared.data.find_shelf_row = True

    def detect_shelf_number(self):

        if Shared.data.find_shelf:
            self.shelf_number_detect_button.config(relief=tk.RAISED)
            Shared.data.find_shelf = False
        else:
            self.shelf_number_detect_button.config(relief=tk.SUNKEN)
            Shared.data.find_shelf = True

    def detect_package(self):

        if Shared.data.detect_package_flag:
            self.package_detect_button.config(relief=tk.RAISED)
            Shared.data.detect_package_flag = False
        else:
            self.package_detect_button.config(relief=tk.SUNKEN)
            Shared.data.detect_package_flag = True

    def detect_an(self):

        if Shared.data.detect_an_flag:
            self.an_detect_button.config(relief=tk.RAISED)
            Shared.data.detect_an_flag = False
        else:
            self.an_detect_button.config(relief=tk.SUNKEN)
            Shared.data.detect_an_flag = True

    def detect_qr(self):

        if Shared.data.detect_qr_flag:
            self.qr_detect_button.config(relief=tk.RAISED)
            Shared.data.detect_qr_flag = False
        else:
            self.qr_detect_button.config(relief=tk.SUNKEN)
            Shared.data.detect_qr_flag = True

    def create_video_canvas(self, _row=0, _column=0, _rowspan=1, _columnspan=1):

        width = Shared.data.video_width
        height = Shared.data.video_height

        self.video_canvas = tk.Canvas(self, bg='blue', width = width, height = height)#, width=1000, height=1000)
        self.video_canvas.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

        _column+=10
        self.video_canvas_ir = tk.Canvas(self, bg='green', width = width, height = height)#, width=1000, height=1000)
        self.video_canvas_ir.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

        _row+=10
        _column-=10
        self.video_canvas_fpv = tk.Canvas(self, bg='red', width=Shared.data.fpv_gui_width, height=Shared.data.fpv_gui_height)  # , width=1000, height=1000)
        self.video_canvas_fpv.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

    def create_video_textbox(self, _row=0, _column=0, _rowspan=1, _columnspan=1):

        self.curr_pos_label = tk.Label(self, text=f'Current Position\tx: {round(Shared.data.current_pos[0],2)}\ty: {round(Shared.data.current_pos[1],2)}\tz: {round(Shared.data.current_pos[2],2)}')
        self.curr_pos_label.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

        #_row+=1
        #self.desired_pos_label = tk.Label(self, text=f'Desired Position\nx: {round(Shared.data.desired_pos[0],2)}\ny: {round(Shared.data.desired_pos[1],2)}\nz: {round(Shared.data.desired_pos[2],2)}')
        #self.desired_pos_label.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

    def _video(self):

        self.panel = None
        time_start = time.time()
        #Shared.data.video_lock.acquire()
        frame = cv2.cvtColor(Shared.data.frame, cv2.COLOR_BGR2RGB)
        ret = Shared.data.ret
        frame_ir = cv2.cvtColor(Shared.data.frame_image_recognition, cv2.COLOR_BGR2RGB)

        if Shared.data.log_package_flag and Shared.data.plot_QR and Shared.data.ekf != None:
            self.plot_QR()
            frame_fpv = cv2.imread("./QR_frame.png")
            frame_fpv = cv2.cvtColor(frame_fpv, cv2.COLOR_BGR2RGB)
            frame_fpv = cv2.resize(frame_fpv, (Shared.data.fpv_gui_width, Shared.data.fpv_gui_height))
            #w, h, d = buf.shape
            #self.photo_fpv = PIL.Image.frombytes("RGB", (w, h), buf.tostring())
        else:
            frame_fpv = cv2.cvtColor(Shared.data.frame_fpv, cv2.COLOR_BGR2RGB)
            frame_fpv = cv2.resize(frame_fpv, (Shared.data.fpv_gui_width, Shared.data.fpv_gui_height))

        #Shared.data.video_lock.release()


        self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
        self.video_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.photo_ir = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame_ir))
        self.video_canvas_ir.create_image(0, 0, image=self.photo_ir, anchor=tk.NW)

        self.photo_fpv = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame_fpv))
        self.video_canvas_fpv.create_image(0, 0, image=self.photo_fpv, anchor=tk.NW)


        # Update pixel location
        #self.desired_pos_label.config(text=f'Desired Position\nx: {round(Shared.data.desired_pos[0],2)}\ny: {round(Shared.data.desired_pos[1],2)}\nz: {round(Shared.data.desired_pos[2],2)}')

        # Update current position
        self.curr_pos_label.config(text=f'Current Position\tx: {round(Shared.data.current_pos[0],2)}\ty: {round(Shared.data.current_pos[1],2)}\tz: {round(Shared.data.current_pos[2],2)}')
        time_end = time.time()

        fps = 1/(time_end-time_start)
        logging.debug(f"FPS: {fps}")
        self.controller.after(100, self._video)

    def plot_QR(self):
        hPix = []
        vPix = []
        euler_att = Shared.data.current_attitude
        Li2c = euler2dcm321(euler_att[0], euler_att[1], euler_att[2])
        focalLengthU = Shared.data.focalLengthU
        focalLengthV = Shared.data.focalLengthV

        for fp in Shared.data.ekf.fpStateDB:
            vx = Shared.data.current_pos[0]
            vy = Shared.data.current_pos[1]
            vz = Shared.data.current_pos[2]
            px = fp.pos[0]
            py = fp.pos[1]
            pz = fp.pos[2]
            psi = fp.psi
            theta = fp.theta
            rho = fp.rho
            m = np.array([cos(psi)*cos(theta), sin(psi)*cos(theta), -sin(theta)])
            hin = np.array([rho*(px - vx) + m[0], rho*(py - vy) + m[1], rho*(pz - vz) + m[2]])
            hcam = np.matmul(Li2c, hin)
            if hcam[0] > 0.01:
                hPix.append(hcam[1]/hcam[0]*focalLengthU)
                vPix.append(-hcam[2]/hcam[0]*focalLengthV)

        self.plot.plot(hPix, vPix, 'bs', markersize=12)
        matplotlib.pyplot.xlim(-1, 1)
        matplotlib.pyplot.ylim(-0.8, 0.8)
        self.figure.savefig("./QR_frame.png")
        #matplotlib.pyplot.clf()
        #self.figure.canvas.draw()
        #w, h = self.figure.canvas.get_width_height()
        #buf = np.fromstring(self.figure.canvas.tostring_argb(), dtype=np.uint8)
        #buf.shape = (w, h, 4)
        #buf = np.roll(buf, 3, axis=2)
        #return buf

    def _plot(self):

        desired_pos = [0,0,0]
        current_pos = [0,0,0]

        Shared.data.mav_lock.acquire()
        desired_pos = Shared.data.desired_pos
        current_pos = Shared.data.current_pos
        Shared.data.mav_lock.release()

        self.ax.plot(
            current_pos[0],
            current_pos[1],
            color='blue',
            linestyle='--',
            marker='o'
        )

        self.ax.plot(
            desired_pos[0],
            desired_pos[1],
            color='green',
            linestyle='--',
            marker='o'
        )

        self.graph_canvas.draw()

        self.controller.after(100,self._plot)

    def create_graph_canvas(self):

        self.figure = Figure(figsize=(5,5))
        self.ax = self.figure.add_subplot(111)
        self.ax.grid()
        self.graph_canvas = FigureCanvasTkAgg(self.figure, self)
        self.graph_canvas.draw()
        self.graph_canvas.get_tk_widget().grid(row=0, column=3)

    def create_listener_canvas(self):

        listen_label = tk.Label(self, text='LISTENING')
        listen_label.grid(row=0, column=0, stick=tk.N)
        self.listener_canvas = tk.Canvas(self, width=25, height=25)
        self.listener_canvas.grid(row=0, column=1, rowspan=1, columnspan=1, stick=tk.N)
        self.oval_listening = self.listener_canvas.create_oval(5, 2, 20, 17, fill="red")
        self.command_label = tk.Label(self, text='COMMAND: ')
        self.command_label.grid(row=1, column=0, stick=tk.W+tk.N)

    def _listen_check(self):

        Shared.data.audio_lock.acquire()
        listening = Shared.data.listening
        command = Shared.data.audio_command
        Shared.data.audio_lock.release()

        if listening:
            self.listener_canvas.itemconfig(self.oval_listening, fill="green")
        else:
            self.listener_canvas.itemconfig(self.oval_listening, fill="red")

        self.command_label.configure(text=f'COMMAND: {command[0]}')

        self.controller.after(100,self._listen_check)
