import datetime
import os
import time
import tkinter
from tkinter import Label, Tk, Button

import cv2
from PIL import Image, ImageTk

import capture
import config
import custom_ui
import main
import vlc_handler

WIN_WIDTH = 1240
WIN_HEIGHT = 600

BG = "#202331"
ACCENT = "#303754"

ui = None
conf = config.load_config()
rec_sec = conf["rec_sec"]
sensibility = conf["sensibility"]
s_map = {"Low": 20, "Medium": 10, "High": 2}


class Interface:
    def create_window(self):
        self.win = Tk()
        self.win.geometry(f"{WIN_WIDTH}x{WIN_HEIGHT}")
        self.win.config(bg=BG)
        self.win.resizable(False, False)
        self.win.title("Security Camera Interface")
        self.win.protocol("WM_DELETE_WINDOW", self.stop_capture)

        capture.main_ui = self

    def stop_capture(self):
        capture.set_stop_thread_event()
        time.sleep(0.2)
        if capture.thread is not None:
            capture.thread.join()
        self.win.destroy()

    def schedule_frame_update(self):
        if self.frame_buffer:
            self.update_frame(self.frame_buffer[0])
            self.frame_buffer = []

        self.win.after(33, self.schedule_frame_update)

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

        self.frame_container = custom_ui.CustomLabelFrame(self.win, width=900, height=WIN_HEIGHT - 30, bg=BG,
                                                          fill=ACCENT)
        self.frame_container.canvas.place(x=15, y=15)

        self.frame_label = Label(self.frame_container.canvas, bg=ACCENT, fg="white",
                                 text="Loading camera feed...", font=custom_ui.JET_FONT)
        self.frame_label.place(x=10, y=10)

        self.pause_stream_button = Button(self.frame_container.canvas, text="Pause", bg=ACCENT, fg="white", width=15,
                                          command=self.toggle_stream)
        self.pause_stream_button.place(x=20, y=500)

        global ui
        ui = self

        self.create_rec_sec_dropdown()
        self.create_precision_dropdown()
        self.create_history()

        # capture.run_capture_on_thread()
        self.win.after(32, self.schedule_frame_update)
        self.win.mainloop()

    def create_rec_sec_dropdown(self):
        options = ["2", "5", "10"]

        selected_option = tkinter.StringVar()
        selected_option.set(str(rec_sec))

        def on_option_change(selection):
            global rec_sec
            if int(selection) != rec_sec:
                rec_sec = int(selection)
                config.save_config(config.Settings(rec_sec=rec_sec, sensibility=sensibility))

        self.rec_sec_option_menu = tkinter.OptionMenu(self.frame_container.canvas, selected_option, *options,
                                                      command=on_option_change)
        self.rec_sec_option_menu.config(width=2, highlightbackground=BG)
        self.rec_sec_option_menu.place(x=870 - self.rec_sec_option_menu.winfo_reqwidth() - 20, y=15)

        self.rec_sec_label = Label(self.frame_container.canvas, text="Recording seconds:", bg=ACCENT, fg="white",
                                   justify="left")
        self.rec_sec_label.place(x=670, y=18)

    def create_precision_dropdown(self):
        options = ["Low", "Medium", "High"]
        selected_option = tkinter.StringVar()

        selected_option.set([key for key, value in s_map.items() if value == sensibility])

        def on_option_change(selection):
            global sensibility
            if selection != sensibility:
                sensibility = s_map[selection]
                config.save_config(config.Settings(rec_sec=rec_sec, sensibility=sensibility))

        self.sensibility_option_menu = tkinter.OptionMenu(self.frame_container.canvas, selected_option, *options,
                                                          command=on_option_change)
        self.sensibility_option_menu.config(width=8, highlightbackground=BG)
        self.sensibility_option_menu.place(x=870 - self.rec_sec_option_menu.winfo_reqwidth() - 20, y=55)

        self.sensibility_label = Label(self.frame_container.canvas, text="Sensibility:", bg=ACCENT, fg="white",
                                       justify="left")
        self.sensibility_label.place(x=670, y=58)

    def create_history(self):
        self.history_container = custom_ui.CustomLabelFrame(self.win, width=300, height=WIN_HEIGHT - 30, bg=BG,
                                                            fill=ACCENT, text="History")
        self.history_container.canvas.place(x=925, y=15)
        self.folders, self.folder_files = capture.get_history_list()
        self.folder_labels_list = []
        for i in range(len(self.folders)):
            if self.folder_files[i] is not None:
                # print("\n", self.folders[i])

                self.folder_labels_list.append(
                    Label(self.history_container.canvas, text=str(self.folders[i]), bg=ACCENT, fg="white"))
                full_files_path = [
                    f"{os.path.abspath(capture.output_path)}\\{self.folders[i]}\\{file}" for file
                    in
                    self.folder_files[i]]
                print(full_files_path)
                self.folder_labels_list[-1].bind("<Button-1>",
                                                 lambda event, files=full_files_path: self.play_vlc_playlist(
                                                     files))

                # for file in self.folder_files[i]:
                #     print(f"    └{file}")
            else:
                print(self.folders[i])

        for i in range(0, len(self.folder_labels_list)):
            self.folder_labels_list[i].place(x=10, y=i * 25 + 30)
            print(str(i * 20 + 30))

    def play_vlc_playlist(self, playlist):
        vlc_handler.open_video(playlist)
