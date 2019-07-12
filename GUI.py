import tkinter as tk
import audio_recorder as ar

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600

DUAL_MONITOR = False

class GUI:
    def __init__(self, _server):
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
        #label = tk.Label(self, text="Command Page")
        #label.grid(row=0, column=0, columnspan=4, sticky=tk.W, padx=15)



        self.text = ''
        self.recorder = ar.AudioRecorder()

        self.record_btn = tk.Button(
            self,
            text="Record",
            bg = "gray"
        )

        self.record_btn.bind("<Button-1>", self.recorder.start_recording)
        self.record_btn.bind("<ButtonRelease-1>", self.recorder.stop_recording)
        self.record_btn.grid(row=0, column=0)

        self.playsound_btn = tk.Button(
            self,
            text="Play Recording",
            command=lambda: self.recorder.play_recording(),
            bg="gray"
        )
        self.playsound_btn.grid(row=0, column=1)

        self.speechrecognition_btn = tk.Button(
            self,
            text="Audio-to-Text",
            command=lambda: self.translate_command(),
            bg="gray"
        )
        self.speechrecognition_btn.grid(row=0, column=2)

        self.sendcommand_btn = tk.Button(
            self,
            text="Send Command",
            command=lambda: self.send_command(),
            bg="gray"
        )
        self.sendcommand_btn.grid(row=0, column=3)

        textbox = tk.Text(self)
        textbox.grid(row=1, column=0, rowspan=3, columnspan=100)
        textbox.insert(tk.END,'AWWW SHIT! YOU WANNA USE THIS?!\n1)HOLD DOWN Record AND SAY THINGS\n2)PRESS Play Recording TO HEAR YOUR BEAUTIFUL VOICE\n3)PRESS Audio-to-Text TO TRANSLATE\n4)SEND THE COMMAND (ONLY WORKS FOR FORWARD/BACKWARD/LEFT/RIGHT)')

    def translate_command(self):

        audio_to_text = self.recorder.recognize_recording()
        print(audio_to_text)

        self.text = audio_to_text.split()[0]


    def send_command(self):
        dist = 0.1
        text = self.text
        if 'for' in text:
            print(f"MOVE FORWARD {dist}m")
        elif 'back' in text:
            print(f"MOVE BACKWARD {dist}m")
        elif 'left' in text:
            print(f"MOVE LEFT {dist}m")
        elif 'right' in text:
            print(f"MOVE RIGHT {dist}m")
        else:
            print("NAHHHH\nSAY EITHER LEFT/RIGHT/BACK/FORWARD YOU SILLY GOOSE!")
        #self.update_setpoint()

def main(gui):
    root = tk.Tk()
    app = Window(root, gui)
    root.mainloop()

if __name__=='__main__':
    root = tk.Tk()
    app = Window(root)
    root.mainloop()
