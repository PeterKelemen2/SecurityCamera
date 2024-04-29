import datetime
import os.path

import cv2
import numpy as np

output_path = "videos"
# Set the font, scale, color, and thickness
font = cv2.FONT_HERSHEY_SIMPLEX
font_scale = 0.5
font_color = (0, 255, 0)  # white color
line_type = 2


def add_text(frame):
    date_time = f"{datetime.datetime.now().strftime("%Y. %m. %d. %H:%M:%S")}"
    text_size, _ = cv2.getTextSize(date_time, font, font_scale, line_type)
    text_x = frame.shape[1] - text_size[0] - 10  # 10 pixels from the right edge
    text_y = frame.shape[0] - 10  # 10 pixels from the bottom

    cv2.putText(frame, date_time, (text_x, text_y), font, font_scale, font_color, line_type)
    return frame


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
    cap = cv2.VideoCapture(0)
    w, h, fps = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), 30.0
    codec = cv2.VideoWriter_fourcc(*'H264')

    print(w, h, fps)

    date = f"{datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")}"

    global output_path
    output_path = f"{output_path}/video-{date}.mp4"
    print(output_path)
    writer = cv2.VideoWriter(output_path, codec, fps, (w, h))
    frame_array = []
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

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break

        if os.path.exists(output_path):
            os.mkdir(output_path)

        frame = adjust_frame(frame)

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

        # print(f"{percent_change}")

        if float(percent_change) > 5.0:
            frame_array.append(frame)
            cv2.imshow('Frame Difference', frame_diff)
            cv2.imshow('Thresholded Difference', thresh_diff)
            if len(frame_array) > 5:
                for f in frame_array:
                    f = add_text(f)
                    writer.write(f)
                frame_array = []

        # Display the difference and the thresholded difference
        # cv2.imshow('Frame Difference', frame_diff)
        # cv2.imshow('Thresholded Difference', thresh_diff)

        # Update previous frame
        prev_frame = frame.copy()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            writer.release()
            break

    cap.release()
    # writer.release()
    cv2.destroyAllWindows()
