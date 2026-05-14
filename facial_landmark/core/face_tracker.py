import cv2
import mediapipe as mp

from config import (
    MAX_NUM_FACES,
    MIN_FACE_DETECTION_CONFIDENCE,
    MIN_FACE_TRACKING_CONFIDENCE
)


class FaceTracker:

    def __init__(self):

        self.mp_face_mesh = mp.solutions.face_mesh

        self.face_mesh = (
            self.mp_face_mesh.FaceMesh(
                static_image_mode=False,
                max_num_faces=MAX_NUM_FACES,
                refine_landmarks=True,
                min_detection_confidence=(
                    MIN_FACE_DETECTION_CONFIDENCE
                ),
                min_tracking_confidence=(
                    MIN_FACE_TRACKING_CONFIDENCE
                )
            )
        )

    def process(self, frame):

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )

        results = self.face_mesh.process(
            rgb_frame
        )

        return results

    def close(self):
        self.face_mesh.close()