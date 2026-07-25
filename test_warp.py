"""
Automated Chess Playing Robot
Perspective Transform Test

Author: Satyajit Panda

This script verifies that the camera calibration is correct
by generating a top-down (bird's-eye) view of the chessboard.
"""

import cv2
import json
import numpy as np

BOARD_SIZE = 800


def main():
    # Load calibration points
    with open("../camera_corners.json", "r") as f:
        points = json.load(f)

    src = np.array(points, dtype=np.float32)

    dst = np.array(
        [
            [0, 0],
            [BOARD_SIZE, 0],
            [BOARD_SIZE, BOARD_SIZE],
            [0, BOARD_SIZE],
        ],
        dtype=np.float32,
    )

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Unable to open camera.")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("Failed to capture frame.")

    transform = cv2.getPerspectiveTransform(src, dst)

    warped = cv2.warpPerspective(
        frame,
        transform,
        (BOARD_SIZE, BOARD_SIZE),
    )

    cv2.imwrite("warped_board.jpg", warped)

    print("Warped board saved as warped_board.jpg")

    cv2.imshow("Original Frame", frame)
    cv2.imshow("Warped Chessboard", warped)

    print("Press any key to exit...")

    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()