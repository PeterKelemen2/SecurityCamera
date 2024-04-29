import datetime
import time
from tkinter import Label, Tk

import cv2
from PIL import Image, ImageTk

import capture
import custom_ui

WIN_WIDTH = 690
WIN_HEIGHT = 530

BG = "#202331"
ACCENT = "#303754"
PALENIGHT_PB = "#78408f"

ui = None


class Interface:
    def create_window(self):
        self.win = Tk()
        self.win.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
        self.win.config(bg=BG)
        self.win.title("Security Camera Interface")
        self.win.protocol("WM_DELETE_WINDOW", self.stop_capture)

    def stop_capture(self):
        capture.set_stop_thread_event()
        time.sleep(0.2)
        capture.thread.join()
        self.win.destroy()

    def schedule_frame_update(self):
        if self.frame_buffer:
            self.update_frame(self.frame_buffer[0])
            self.frame_buffer = []
        self.win.after(32, self.schedule_frame_update)

    def update_frame(self, im=None):
        if self.frame_label is not None:
            # date = f"{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}"
            # self.frame_label.config(text=date)
            self.frame_rgb = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
            self.image = Image.fromarray(self.frame_rgb)
            self.image_file = ImageTk.PhotoImage(self.image)
            self.frame_label.config(image=self.image_file)

    def __init__(self):
        self.win = None
        self.frame_buffer = []
        self.create_window()

        self.frame_container = custom_ui.CustomLabelFrame(self.win, width=660, height=500, bg=BG, fill=ACCENT)
        self.frame_container.canvas.place(x=15, y=15)

        self.frame_label = Label(self.frame_container.canvas, bg="black", fg="white",
                                 text="Security Camera Interface")
        self.frame_label.place(x=10, y=10)

        global ui
        ui = self

        capture.run_capture_on_thread()
        self.win.after(32, self.schedule_frame_update)
        self.win.mainloop()
