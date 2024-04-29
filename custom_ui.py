import time
import tkinter
from tkinter import PhotoImage, Canvas

import PIL.ImageOps
from PIL import Image, ImageTk

import custom_button

# import debug
# import interface

bg_path = "assets/rounded_frame.png"
circle = "assets/frame_circle.png"
rect = "assets/frame_square.png"
toggled_on = "assets/toggle_button/toggle_on.png"
toggled_off = "assets/toggle_button/toggle_off.png"

ACCENT = "#3a3a3a"
BGCOLOR = "#3a3a3a"
WHITE = "#ffffff"
BLACK = "#000000"

DARK_FONT_COLOR = "#ffffff"
LIGHT_FONT_COLOR = "#000000"
FONT_COLOR = "#ffffff"
TIME_FONT_SIZE = 12
BIG_FONT_SIZE = 14
FONT = ("Ubuntu", TIME_FONT_SIZE)
BOLD_FONT = ("Ubuntu", TIME_FONT_SIZE, "bold")
BIG_FONT = ("Ubuntu", BIG_FONT_SIZE)
BIG_FONT_BOLD = ("Ubuntu", BIG_FONT_SIZE, "bold")


class CardItem:
    def __init__(self, master, width, height, bg=BLACK, title="", img_path=None, video_path=None, result=None):
        self.diff_text = None
        self.diff_title = None
        self.path_text = None
        self.result = None
        self.text = None
        self.custom_path = video_path
        self.width = width
        self.height = height
        self.bg = bg
        self.title = title
        self.image_padding = 20
        self.canvas = Canvas(master, width=self.width, height=self.height, bg=self.bg, highlightthickness=0)
        self.canvas.pack()

        self.container = CustomLabelFrame(self.canvas, width=self.width, height=self.height, text="self.title",
                                          bg=self.bg, fill=ACCENT)
        self.container.canvas.place(x=0, y=0)

        self.photo = ImageTk.PhotoImage(self.create_photo(img_path))
        self.photo_label = (tkinter.Label(self.container.canvas, image=self.photo))
        self.photo_label.place(x=self.image_padding, y=self.image_padding)

        self.create_text(video_path, result)

        self.process_button = custom_button.CustomButton(self.container.canvas, text="Load video", bg=ACCENT,
                                                         button_type=custom_button.wide_button)
        self.process_button.canvas.place(
            x=self.width - self.process_button.canvas.winfo_reqwidth() - self.container.get_radius() * 2,
            y=self.height - self.process_button.canvas.winfo_reqheight() - self.container.get_radius() * 2)

    def create_photo(self, img_path):
        if img_path is None:
            image = Image.open("assets/no_photo.png")
        else:
            image = Image.open(img_path)
        width, height = image.size
        new_height = self.container.get_height() - 50
        aspect_ratio = new_height / height
        new_width = int(width * aspect_ratio)

        image = image.resize((new_width, new_height), Image.BILINEAR)

        self.image_padding = (self.container.get_height() - new_height) // 2
        return image

    def create_text(self, path=None, result=""):
        self.path_text, self.text, self.diff_text, self.diff_title = None, None, None, None
        title_x = self.photo.width() + self.image_padding * 2
        self.path_text = tkinter.Label(self.container.canvas, text="Path:", font=BOLD_FONT, fg=DARK_FONT_COLOR,
                                       bg=ACCENT)
        self.path_text.place(x=title_x, y=self.image_padding)
        text = ""
        if path is None:
            text = "Couldn't locate video."
        else:
            text = path
        self.text = tkinter.Label(self.container.canvas,
                                  text=text,
                                  justify="left",
                                  font=FONT,
                                  wraplength=self.width - self.image_padding * 3 - self.photo.width() - self.path_text.winfo_reqwidth(),
                                  fg=DARK_FONT_COLOR,
                                  bg=ACCENT)
        text_x = self.photo.width() + self.image_padding * 2 + self.path_text.winfo_reqwidth()
        self.text.place(x=text_x, y=self.image_padding)

        self.diff_title = tkinter.Label(self.container.canvas, text="Result:", font=BOLD_FONT, fg=DARK_FONT_COLOR,
                                        bg=ACCENT)

        # Binding y coordinate to self.text in case it becomes more lines than one
        self.diff_title.place(x=title_x, y=self.image_padding + self.text.winfo_reqheight() + 10)
        self.diff_text = tkinter.Label(self.container.canvas, text=result, font=FONT,
                                       fg=DARK_FONT_COLOR, bg=ACCENT)
        self.diff_text.place(x=self.photo.width() + self.image_padding * 2 + self.diff_title.winfo_reqwidth(),
                             y=self.image_padding + self.text.winfo_reqheight() + 10)


class CustomToggleButton:
    def __init__(self, master, width, height, text="", state=True, bg=None):
        self.width = width
        self.height = height
        self.bg = bg
        self.text = text
        self.disabled = False
        self.state = state
        self.text_item = None

        self.toggled_on_im_file = Image.open(toggled_on).convert("RGBA")
        self.toggled_off_im_file = Image.open(toggled_off).convert("RGBA")

        self.canvas = Canvas(master, width=self.width, height=self.height, bg=self.bg, highlightthickness=0)
        self.canvas.pack()

        self.t_on_im = self.toggled_on_im_file.resize((self.width, self.height))
        self.t_off_im = self.toggled_off_im_file.resize((self.width, self.height))

        self.toggled_on_image = ImageTk.PhotoImage(self.t_on_im)
        self.toggled_off_image = ImageTk.PhotoImage(self.t_off_im)

        self.text_item = tkinter.Label(self.canvas, text=self.text, height=0, anchor="center", fg=FONT_COLOR,
                                       font=FONT,
                                       bg=ACCENT)
        self.canvas.config(width=self.width + self.text_item.winfo_reqwidth() + 20)
        self.text_item.place(x=self.width + 10, y=5)

        if self.state:
            self.image_item = self.canvas.create_image(self.width // 2, self.height // 2, anchor="center",
                                                       image=self.toggled_on_image)
        else:
            self.image_item = self.canvas.create_image(self.width // 2, self.height // 2, anchor="center",
                                                       image=self.toggled_off_image)

        self.canvas.bind("<Button-1>", self.toggle)
        self.text_item.bind("<Button-1>", self.toggle)

    def toggle(self, event=None):
        if not self.disabled:
            self.state = not self.state
            self.canvas.delete(self.image_item)
            if self.state:
                self.image_item = self.canvas.create_image(self.width // 2, self.height // 2, anchor="center",
                                                           image=self.toggled_on_image)
            else:
                self.image_item = None
                self.image_item = self.canvas.create_image(self.width // 2, self.height // 2, anchor="center",
                                                           image=self.toggled_off_image)

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

    def get_state(self):
        return self.state

    def config(self, bg=None, fg=None, text=None):
        if bg is not None:
            self.canvas.config(bg=bg)
            if fg is not None and self.text is not None:
                self.text_item.config(bg=bg, fg=fg)
        if fg is not None and text is not None:
            self.text_item.config(fg=fg)
        if text is not None:
            self.text_item.config(text=text)
            self.text = text


class CustomLabelFrame:
    def __init__(self, master, width, height, text="", fill=BLACK, fg=WHITE, bg=BGCOLOR, radius=10, id=None):
        self.width = width
        self.height = height
        self.fill = fill
        self.fg = fg
        self.bg = bg
        self.text = text
        self.radius = radius
        self.id = id
        self.canvas = Canvas(master, width=width, height=height, bg=bg, highlightthickness=0)
        self.canvas.pack()

        self.item_list = list()
        self.rect_im = None
        self.circle_im = None
        self.rect_im_hor = None
        self.overlay = None
        self.rect_im_ver = None
        self.text_item = None
        self.center = None
        self.cir_im = None
        self.rec_im_hor = None
        self.rec_im_ver = None
        self.center_rec = None

        self.create_images()
        self.create_labelframe()

    def load_images(self):
        # Load the images using PIL
        self.circle_im = None
        self.rect_im = None
        self.circle_im = Image.open(circle).convert("RGBA")
        self.rect_im = Image.open(rect).convert("RGBA")

    def create_images(self):
        """
        Creates images for circle and rectangle shapes.

        This method loads the images for circle and rectangle shapes, composites them with a specified overlay color,
        and resizes them to the desired dimensions. The circle image is resized to twice the radius for both width and
        height. The rectangle images are resized to match the canvas dimensions, with adjustments made for the circle's
        presence.

        Returns:
            None
        """
        self.load_images()

        self.overlay = Image.new("RGBA", self.circle_im.size, self.fill)
        self.circle_im = Image.composite(self.overlay, self.circle_im, self.circle_im)
        self.rect_im = Image.composite(self.overlay, self.rect_im, self.rect_im)

        # Resize the image (width, height)
        self.circle_im = self.circle_im.resize((self.radius * 2, self.radius * 2))
        self.rect_im_hor = self.rect_im.resize((self.width, self.height - self.radius * 2))
        self.rect_im_ver = self.rect_im.resize((self.width - self.radius * 2, self.height))

    def create_labelframe(self):
        """
        Creates a label frame on the canvas with circle and rectangle images along with text.

        This method creates a label frame on the canvas and populates it with circle and rectangle images
        along with text. The circle images are positioned at four corners of the canvas, while the rectangle
        images are positioned at the center of the canvas. Text is added at a specified position
        with the given fill color, anchor point, and font.

        Note:
            Ensure that the `circle_im`, `rect_im_hor`, and `rect_im_ver` attributes are set with the appropriate
            image files before calling this method.

        Returns:
            None
        """
        self.item_list = list()
        self.cir_im = ImageTk.PhotoImage(self.circle_im)
        self.rec_im_hor = ImageTk.PhotoImage(self.rect_im_hor)
        self.rec_im_ver = ImageTk.PhotoImage(self.rect_im_ver)

        # Creating circles (x,y)
        self.item_list.append(self.canvas.create_image(self.radius, self.radius, anchor="center", image=self.cir_im))
        self.item_list.append(
            self.canvas.create_image(self.width - self.radius, self.radius, anchor="center", image=self.cir_im))
        self.item_list.append(
            self.canvas.create_image(self.radius, self.height - self.radius, anchor="center", image=self.cir_im))
        self.item_list.append(
            self.canvas.create_image(self.width - self.radius, self.height - self.radius, anchor="center",
                                     image=self.cir_im))

        # Creating rectangles
        self.item_list.append(self.canvas.create_image(self.width // 2, self.height // 2, image=self.rec_im_hor))
        self.item_list.append(
            self.canvas.create_image(self.radius, self.height // 2, anchor="w", image=self.rec_im_ver))

        self.text_item = self.canvas.create_text(self.radius, self.radius, text=self.text, fill=self.fg, anchor="w",
                                                 font=BOLD_FONT)

    def config(self, text=None, fg=None, bg=None, fill=None):
        if text is not None:
            self.text = text
            self.canvas.itemconfig(self.text_item, text=self.text)
        if fg is not None:
            self.fg = fg
            self.canvas.itemconfig(self.text_item, fill=self.fg)
        if bg is not None:
            self.bg = bg
            self.canvas.config(bg=self.bg)
        if fill is not None:
            self.change_fill_color(fill)

    def change_width(self, new_width):
        pass

    def switch_theme(self, new_fill=None, new_text_color=None, new_bg=None, buttons=None, labels=None):
        """
        Switches the theme of the user interface.

        Args:
            new_fill (str): The new fill color for elements like buttons.
            new_text_color (str): The new text color for elements like buttons and labels.
            new_bg (str): The new background color for the canvas.
            buttons (list): A list of button widgets to apply the new fill color.
            labels (list): A list of label widgets to apply the new fill and text colors.
        """
        if new_fill is not None: self.change_fill_color(new_fill)
        if new_text_color is not None: self.change_text_color(new_text_color)
        if new_bg is not None: self.canvas.config(bg=new_bg)
        if self.canvas.winfo_children():
            for child in self.canvas.winfo_children():
                if "text" in child.keys():
                    child.config(fg=new_text_color)
        if buttons is not None:
            for button in buttons:
                if button is not None:
                    button.config(bg=new_fill)
        if labels is not None:
            for label in labels:
                if label is not None:
                    label.config(bg=new_fill, fg=new_text_color)

    def change_fill_color(self, new_color):
        self.fill = new_color
        self.create_images()
        self.create_labelframe()

    def change_text_color(self, new_color):
        self.fg = new_color
        self.canvas.itemconfig(self.text_item, fill=self.fg)

    def change_bg_color(self, new_bg):
        self.canvas.config(bg=new_bg)

    def get_id(self):
        return self.id

    def get_label_width(self):
        bbox = self.canvas.bbox(self.text_item)
        width = bbox[2] - bbox[0]
        return width

    def set_label_text(self, new_text):
        if self.canvas is not None:
            self.canvas.itemconfig(self.text_item, text=new_text)

    def get_label_height(self):
        bbox = self.canvas.bbox(self.text_item)
        height = bbox[3] - bbox[1]
        return height

    def set_width(self, new_width):
        self.width = new_width
        self.create_labelframe()

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_radius(self):
        return self.radius

    def destroy(self):
        self.canvas.destroy()

    def get_fill(self):
        return self.fill


bar_height = 0
pg_bar_width = 0
pg_bar_height = 0


class CustomProgressBar:

    def __init__(self, master, width, height,
                 bg=BLACK, pr_bar=BLACK, pr_bar_bg=WHITE, bar_bg=WHITE, bar_bg_accent=BGCOLOR,
                 radius=10, padding=4):
        self.new_progress_bar_fg = None
        global bar_height, pg_bar_width, pg_bar_height

        self.bg = bg
        self.bar_bg_accent = bar_bg_accent
        self.bar_bg = bar_bg
        self.pr_bar_bg = pr_bar_bg
        self.pr_bar = pr_bar
        self.width = width
        self.height = height
        self.fg = FONT_COLOR
        self.radius = radius
        self.padding = padding
        self.canvas = Canvas(master, width=width, height=height, bg=bg, highlightthickness=0)

        # Calculating progress bar foreground dimensions
        bar_height = self.height - self.padding * 2
        pg_bar_width = self.width - self.padding * 2
        pg_bar_height = self.height - self.padding * 2
        self.canvas.pack()

        self.progress_bar_fg = None
        self.progress_bar_bg = None

        self.create_pbar()

    def create_pbar(self):
        # Creating progress bar foreground
        self.progress_bar_bg = CustomLabelFrame(self.canvas,
                                                width=self.width,
                                                height=self.height,
                                                radius=self.radius,
                                                fill=self.bar_bg_accent,
                                                bg=self.bg)
        self.create_pbar_fg(width=self.radius + 1, height=pg_bar_height)

    def create_pbar_fg(self, width, height=30):
        # Creating progress bar background
        global bar_height
        self.progress_bar_fg = CustomLabelFrame(self.canvas,
                                                width=width,
                                                height=height,
                                                radius=self.radius // 2,
                                                fill=self.pr_bar,
                                                bg=self.bar_bg_accent)
        self.progress_bar_fg.canvas.place(x=self.padding, y=self.padding)

    def set_percentage(self, percentage):
        # Settings progress bar width based on percentage
        new_width = int(round(pg_bar_width * (percentage / 100)))
        if new_width > self.radius:
            self.create_pbar_fg(width=new_width, height=self.height - self.padding * 2)

    def config(self, bg):
        self.bg = bg
        self.canvas.config(bg=bg)
        self.progress_bar_bg.change_bg_color(bg)

    def change_pb_color(self, new_color):
        # Changing progress bar fill color
        self.progress_bar_fg.change_fill_color(new_color)

    def change_pb_bg_color(self, new_color):
        # Changing progress bar background fill color
        self.progress_bar_bg.change_fill_color(new_color)

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width
