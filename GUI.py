import tkinter as tk
import audio_recorder as ar
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import cv2
import math
import time
import PIL.Image, PIL.ImageTk

import Shared
import signal

WINDOW_WIDTH = 800
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
        self.create_video_canvas(_row=0, _column=0)
        self.create_video_textbox(_row=1, _column=0)
        self._video()
        #self._plot()
        #self._listen_check()


        #self.test()

    def create_video_canvas(self, _row=0, _column=0, _rowspan=1, _columnspan=1):

        width = Shared.data.video_width
        height = Shared.data.video_height
        self.video_canvas = tk.Canvas(self, bg='blue', width = width, height = height)#, width=1000, height=1000)
        self.video_canvas.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

    def create_video_textbox(self, _row=0, _column=0, _rowspan=1, _columnspan=1):

        self.pixel_label = tk.Label(self, text=f'x pixel: {Shared.data.pixel_pos[0]}\ny pixel: {Shared.data.pixel_pos[1]}')
        self.pixel_label.grid(row=_row, column=_column, rowspan=_rowspan, columnspan=_columnspan)

    def _video(self):

        self.panel = None

        Shared.data.video_lock.acquire()
        frame = np.copy(Shared.data.frame)
        ret = Shared.data.ret
        Shared.data.video_lock.release()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.video_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        # Update pixel location
        self.pixel_label.config(text=f'x pixel: {Shared.data.pixel_pos[0]}\ny pixel: {Shared.data.pixel_pos[1]}')

        self.controller.after(100, self._video)

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
