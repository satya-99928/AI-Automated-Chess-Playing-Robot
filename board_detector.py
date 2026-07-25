"""
Automated Chess Playing Robot
Board Detection Module

Author: Satyajit Panda

This module captures an image from the USB camera and
applies a perspective transform to obtain a top-down
view of the chessboard.
"""

import cv2
import json
import numpy as np


class BoardDetector:
    BOARD_SIZE = 800

    def __init__(self, calibration_file="camera_corners.json"):
        with open(calibration_file, "r") as f:
            points = json.load(f)

        self.src = np.array(points, dtype=np.float32)

        self.dst = np.array(
            [
                [0, 0],
                [self.BOARD_SIZE, 0],
                [self.BOARD_SIZE, self.BOARD_SIZE],
                [0, self.BOARD_SIZE],
            ],
            dtype=np.float32,
        )

        self.transform = cv2.getPerspectiveTransform(
            self.src,
            self.dst,
        )

    def capture_frame(self, camera_index=0):
        """
        Capture a single frame from the USB camera.
        """

        cap = cv2.VideoCapture(camera_index)

        if not cap.isOpened():
            raise RuntimeError("Unable to open camera.")

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        ret, frame = cap.read()
        cap.release()

        if not ret:
            raise RuntimeError("Failed to capture frame.")

        return frame

    def detect_board(self, frame):
        """
        Warp the chessboard into a fixed 800x800 image.
        """

        return cv2.warpPerspective(
            frame,
            self.transform,
            (self.BOARD_SIZE, self.BOARD_SIZE),
        )


def main():
    detector = BoardDetector()

    frame = detector.capture_frame()
    board = detector.detect_board(frame)

    cv2.imshow("Original Frame", frame)
    cv2.imshow("Warped Chessboard", board)

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()