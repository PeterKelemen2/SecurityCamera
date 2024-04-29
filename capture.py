import cv2
import numpy as np


def test_camera_properties(cap):
    # Try setting a property
    cap.set(cv2.CAP_PROP_AUTO_WB, 0)
    # Read back the property
    print("Auto White Balance:", cap.get(cv2.CAP_PROP_AUTO_WB))


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
    test_camera_properties(cap)
    # set_fixed_white_balance(cap)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame (stream end?). Exiting ...")
            break
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)

        sharpening_kernel = np.array([[-0.5, -0.5, -0.5],
                                      [-0.5, 5, -0.5],
                                      [-0.5, -0.5, -0.5]])

        # Apply the sharpening kernel using the filter2D function
        sharpened_image = cv2.filter2D(blurred, -1, sharpening_kernel)

        cv2.imshow('Video Feed', sharpened_image)
        # cv2.imshow('Video Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
