import tkinter as tk
import audio_recorder as ar
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import cv2
import math
import time

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 800

DUAL_MONITOR = False

class MyVideoCapture:

    def __init__(self, video_source=0):
        self.vid = cv2.VideoCapture('udpsrc port=5000 caps = "application/x-rtp, media=(string)video, clock-rate=(int)90000, encoding-name=(string)H264, payload=(int)96" ! rtph264depay ! decodebin ! videoconvert ! appsink', cv2.CAP_GSTREAMER)
        #self.vid = cv2.VideoCapture(video_source)
        self.video_source = video_source
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            self.window.mainloop()

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (ret, None)

class GUI:
    def __init__(self, _server=None):
        self.start = True
        self.server = _server
        self.setpoint = [0,0,0]
        self.text = []

    def update_setpoint(self):
        self.server.x_desired = self.setpoint[0]
        self.server.y_desired = self.setpoint[1]
        self.server.z_desired = self.setpoint[2]
        self.server.yaw_desired = 0

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

        exit()

    def cycle_frames(self, container):

        frame = command_page(parent = container, controller = self)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()

class command_page(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.recorder = ar.AudioRecorder()
        self.create_listener_canvas()
        self.recorder.keyword_listener(keyword='hey baby')
        self.start_listening_check(controller)

        self.create_graph_canvas()
        self.start_plot_thread()
        self.start_video_thread()

    def start_video_thread(self):
        self.video_thread = threading.Thread(target=self._vide)
        self.video_thread.start()

    def _video(self):
        self.vid = MyVideoCapture()
        self.panel = None


        ret, frame = self.vid.get_frame()

        while not ret:
            ret, frame = self.vid.get_frame()

        image = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(frame))
        self.panel = tk.Label(self, image=image)
        self.panel.image = image
        self.panel.grid(row=0, column=5)#, rowspan=100, padx=15)

        while True:
            ret, frame = command_page.vid.get_frame()

            if ret:
                image = PIL.ImageTk.PhotoImage(PIL.Image.fromarray(frame))
                command_page.panel.configure(image=image)
                command_page.panel.image = image

    def start_plot_thread(self):
        self.plot_thread = threading.Thread(target=self._plot)
        self.plot_thread.start()

    def _plot(self):
        while True:
            time.sleep(1)
            self.ax.plot(
                self.server.current_x,
                self.server.current_y,
                color='blue',
                linestyle='--',
                marker='o'
            )

            self.ax.plot(
                self.server.x_desired,
                self.server.y_desired,
                color='green',
                linestyle='--',
                marker='o'
            )

            self.graph_canvas.draw()

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

        """
        textbox = tk.Text(self)#, width=100, height=100,)
        textbox.grid(row=1, column=0, rowspan=1, columnspan=1)
        textbox.insert(tk.END,'IF RED -> SPEAK KEYWORD.\nIF GREEN -> SPEAK COMMAND')
        """
    def start_listening_check(self, controller):
        self.listen_check_thread = threading.Thread(target=self._listen_check, args=(controller,))
        self.listen_check_thread.start()

    def _listen_check(self, controller):
        while True:
            if self.recorder.listening:
                self.listener_canvas.itemconfig(self.oval_listening, fill="green")
                if self.recorder.command!='':
                    self.send_command(controller)
                    self.command_label.configure(text=f'COMMAND: {self.recorder.command}')
            else:
                self.listener_canvas.itemconfig(self.oval_listening, fill="red")
                self.recorder.command = ''

    def send_command(self, controller):
        dist = 0.1
        text = self.recorder.command
        gui = controller.gui
        if 'for' in text:
            print(f"MOVE FORWARD {dist}m")
            gui.server.x_desired = gui.server.current_x + 0.1
        elif 'back' in text:
            print(f"MOVE BACKWARD {dist}m")
            gui.server.x_desired = gui.server.current_x - 0.1
        elif 'left' in text:
            print(f"MOVE LEFT {dist}m")
            gui.server.y_desired = gui.server.current_y - 0.1
        elif 'right' in text:
            print(f"MOVE RIGHT {dist}m")
            gui.server.y_desired = gui.server.current_y + 0.1
        elif 'take' in text:
            print(f"TAKEOFF {dist}m")
            gui.server.z_desired = gui.server.current_z + 1.0
        elif 'land' in text:
            print(f"LAND {dist}m")
            gui.server.z_desired = gui.server.current_z - 1.0
        elif 'up' in text:
            print(f"MOVE UP {dist}m")
            gui.server.z_desired = gui.server.current_z + 0.1
        elif 'down' in text:
            print(f"MOVE DOWN {dist}m")
            gui.server.z_desired = gui.server.current_z - 0.1
        elif 'disarm' in text:
            print("DISARMING")
            gui.server.msg_payload_send = [400, 0, 0, 0, 0, 0, 0, 0]
        elif 'arm' in text:
            print('ARMING')
            gui.server.msg_payload_send = [400, 1, 0, 0, 0, 0, 0, 0]
        elif 'disable' in text:
            print('DISABLING OFFBOARD')
            gui.server.msg_payload_send = [92, 0, 0, 0, 0, 0, 0, 0]
        elif 'enable' in text:
            print('ENABLING OFFBOARD')
            gui.server.msg_payload_send = [92, 1, 0, 0, 0, 0, 0, 0]
        else:
            print("YOU DID NOT ENTER A COMMAND!")

def main(gui):
    root = tk.Tk()
    app = Window(root, gui)
    root.mainloop()

if __name__=='__main__':
    root = tk.Tk()
    gui = GUI()
    app = Window(root, gui)
    root.mainloop()
