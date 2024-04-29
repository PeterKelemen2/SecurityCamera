import datetime
import os.path
import threading

import cv2
import numpy as np

import interface

output_path = "videos"
# Set the font, scale, color, and thickness
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
font_color = (0, 255, 0)  # white color
line_type = 2

main_ui = None

thread = None

stop_thread_event: threading.Event = None


def add_text(frame):
    new_frame = np.copy(frame)
    date_time = f"{datetime.datetime.now().strftime("%Y. %m. %d. %H:%M:%S")}"
    text_size, _ = cv2.getTextSize(date_time, font, font_scale, line_type)
    text_x = new_frame.shape[1] - text_size[0] - 10  # 10 pixels from the right edge
    text_y = new_frame.shape[0] - 10  # 10 pixels from the bottom

    cv2.putText(new_frame, date_time, (text_x, text_y), font, font_scale, font_color, line_type)
    return new_frame


def adjust_frame(frame):
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    sharpening_kernel = np.array([[-0.5, -0.5, -0.5],
                                  [-0.5, 5, -0.5],
                                  [-0.5, -0.5, -0.5]])

    # Apply the sharpening kernel using the filter2D function
    sharpened_image = cv2.filter2D(blurred, -1, sharpening_kernel)
    return sharpened_image


def set_fixed_white_balance(cap):
    if cap.get(cv2.CAP_PROP_AUTO_WB) is not None:
        cap.set(cv2.CAP_PROP_AUTO_WB, 0)
        cap.set(cv2.CAP_PROP_WB_TEMPERATURE, 4500)
    else:
        print("This camera does not support manual white balance settings.")


def capture_image():
    global main_ui, stop_thread_event
    main_ui = interface.ui
    stop_thread_event = threading.Event()

    cap = cv2.VideoCapture(0)
    w, h, fps = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), 30.0
    codec = cv2.VideoWriter_fourcc(*'H264')

    print(w, h, fps)

    date = f"{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}"

    global output_path
    output_path = f"{output_path}/video-{date}.mp4"
    print(output_path)
    writer = cv2.VideoWriter(output_path, codec, fps, (w, h))

    if not cap.isOpened():
        print("Unable to open camera")
        return

    ret, prev_frame = cap.read()
    prev_frame = adjust_frame(prev_frame)
    if not ret:
        print("Failed to capture initial frame")
        cap.release()
        return

    set_fixed_white_balance(cap)

    while not stop_thread_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break

        if not os.path.exists(output_path):
            os.mkdir(output_path)

        frame = adjust_frame(frame)
        if not main_ui.is_paused:
            main_ui.frame_buffer.append(frame)
        # Convert frames to grayscale for easier difference calculation
        gray_prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Calculate the absolute difference between current frame and previous frame
        frame_diff = cv2.absdiff(gray_prev_frame, gray_frame)

        # Threshold to keep only significant differences
        _, thresh_diff = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

        # Calculate the percentage of different pixels
        significant_changes = np.count_nonzero(thresh_diff)
        total_pixels = thresh_diff.size
        percent_change = f"{((significant_changes / total_pixels) * 100):.2f}"

        if float(percent_change) > 5.0:
            writer.write(add_text(frame))

        # Update previous frame
        prev_frame = frame.copy()

    cap.release()
    writer.release()


def run_capture_on_thread():
    global thread
    thread = threading.Thread(target=capture_image)
    thread.start()


def set_stop_thread_event():
    global stop_thread_event
    stop_thread_event.set()
