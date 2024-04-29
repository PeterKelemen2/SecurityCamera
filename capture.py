import cv2
import numpy as np


def adjust_frame(frame):
    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
    sharpening_kernel = np.array([[-0.5, -0.5, -0.5],
                                  [-0.5, 5, -0.5],
                                  [-0.5, -0.5, -0.5]])

    # Apply the sharpening kernel using the filter2D function
    sharpened_image = cv2.filter2D(blurred, -1, sharpening_kernel)
    return sharpened_image


def set_fixed_white_balance(cap):
    # Check if the camera can handle manual white balance settings
    # '17' is generally the property id for white balance in VideoCaptureProperties
    # The exact property ID can be different based on the camera driver
    if cap.get(cv2.CAP_PROP_AUTO_WB) is not None:
        # Turn off auto white balance
        cap.set(cv2.CAP_PROP_AUTO_WB, 0)
        # Set a specific white balance value
        # This value is an example; you'll need to modify it according to your needs/environment
        cap.set(cv2.CAP_PROP_WB_TEMPERATURE, 4500)  # Example for setting white balance to 4500K
    else:
        print("This camera does not support manual white balance settings.")


def capture_image():
    cap = cv2.VideoCapture(0)
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

        print(f"{percent_change}")

        # Display the difference and the thresholded difference
        cv2.imshow('Frame Difference', frame_diff)
        cv2.imshow('Thresholded Difference', thresh_diff)

        # Update previous frame
        prev_frame = frame.copy()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
