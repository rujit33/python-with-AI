import cv2
import mediapipe as mp

from config import (
    MESH_COLOR,
    MESH_THICKNESS,
    TEXT_COLOR,
    FONT_SCALE,
    FONT_THICKNESS
)


class MeshRenderer:

    def __init__(self):

        self.mp_drawing = mp.solutions.drawing_utils

        self.mp_drawing_styles = (
            mp.solutions.drawing_styles
        )

        self.mp_face_mesh = mp.solutions.face_mesh

    def draw_mesh(
        self,
        frame,
        face_landmarks
    ):

        self.mp_drawing.draw_landmarks(
            image=frame,
            landmark_list=face_landmarks,
            connections=(
                self.mp_face_mesh.FACEMESH_TESSELATION
            ),
            landmark_drawing_spec=None,
            connection_drawing_spec=(
                self.mp_drawing.DrawingSpec(
                    color=MESH_COLOR,
                    thickness=MESH_THICKNESS,
                    circle_radius=1
                )
            )
        )

    def draw_fps(
        self,
        frame,
        fps
    ):

        cv2.putText(
            frame,
            f"FPS: {int(fps)}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            FONT_SCALE,
            TEXT_COLOR,
            FONT_THICKNESS
        )