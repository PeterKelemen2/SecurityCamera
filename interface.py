import datetime
import time
from tkinter import Label, Tk, Button

import cv2
from PIL import Image, ImageTk

import capture
import custom_ui

WIN_WIDTH = 695
WIN_HEIGHT = 600

BG = "#202331"
ACCENT = "#303754"

ui = None


class Interface:
    def create_window(self):
        self.win = Tk()
        self.win.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
        self.win.config(bg=BG)
        self.win.resizable(False, False)
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

        # if capture.recording:
        #     self.rec_indicator.place(x=150, y=500)
        # else:
        #     self.rec_indicator.place_forget()
        self.win.after(32, self.schedule_frame_update)

    def toggle_stream(self):
        self.is_paused = not self.is_paused
        if self.is_paused is True:
            self.pause_stream_button.config(text="Resume")
        else:
            self.pause_stream_button.config(text="Pause")

    def update_frame(self, im=None):
        if self.frame_label is not None and im is not None:
            self.image_file = ImageTk.PhotoImage(Image.fromarray(cv2.cvtColor(im, cv2.COLOR_BGR2RGB)))
            self.frame_label.config(image=self.image_file)

    def __init__(self):
        self.win = None
        self.frame_buffer = []
        self.is_paused = False
        self.create_window()

        self.frame_container = custom_ui.CustomLabelFrame(self.win, width=665, height=WIN_HEIGHT - 30, bg=BG,
                                                          fill=ACCENT)
        self.frame_container.canvas.place(x=15, y=15)

        self.frame_label = Label(self.frame_container.canvas, bg=ACCENT, fg="white",
                                 text="Loading camera feed...")
        self.frame_label.place(x=10, y=10)

        self.pause_stream_button = Button(self.frame_container.canvas, text="Pause", bg=ACCENT, fg="white", width=15,
                                          command=self.toggle_stream)
        self.pause_stream_button.place(x=20, y=500)

        global ui
        ui = self

        capture.run_capture_on_thread()
        self.win.after(32, self.schedule_frame_update)
        self.win.mainloop()
