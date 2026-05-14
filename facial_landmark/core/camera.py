import cv2

from config import (
    CAMERA_INDEX,
    FRAME_WIDTH,
    FRAME_HEIGHT
)


class CameraStream:

    def __init__(self):
        self.capture = cv2.VideoCapture(CAMERA_INDEX)

        if not self.capture.isOpened():
            raise RuntimeError(
                "Failed to open webcam."
            )

        self.capture.set(
            cv2.CAP_PROP_FRAME_WIDTH,
            FRAME_WIDTH
        )

        self.capture.set(
            cv2.CAP_PROP_FRAME_HEIGHT,
            FRAME_HEIGHT
        )

    def read_frame(self):

        success, frame = self.capture.read()

        if not success:
            raise RuntimeError(
                "Failed to read frame from webcam."
            )

        return frame

    def release(self):
        self.capture.release()