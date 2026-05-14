import cv2

from config import WINDOW_NAME

from core.camera import CameraStream
from core.face_tracker import FaceTracker
from core.renderer import MeshRenderer
from core.utils import FPSCounter


def main():

    camera = CameraStream()

    tracker = FaceTracker()

    renderer = MeshRenderer()

    fps_counter = FPSCounter()

    try:

        while True:

            frame = camera.read_frame()

            frame = cv2.flip(frame, 1)

            results = tracker.process(frame)

            if results.multi_face_landmarks:

                for face_landmarks in (
                    results.multi_face_landmarks
                ):

                    renderer.draw_mesh(
                        frame,
                        face_landmarks
                    )

            fps = fps_counter.calculate()

            renderer.draw_fps(
                frame,
                fps
            )

            cv2.imshow(
                WINDOW_NAME,
                frame
            )

            key = cv2.waitKey(1)

            if key == ord("q"):
                break

    finally:

        camera.release()

        tracker.close()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()