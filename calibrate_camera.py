"""
Automated Chess Playing Robot
Camera Calibration Tool

Author: Satyajit Panda

This script captures one frame from the USB camera and
allows the user to click the four outer corners of the
chessboard.

Click Order:
1. A8
2. H8
3. H1
4. A1

The selected points are saved in camera_corners.json.
"""

import cv2
import json

points = []


def click(event, x, y, flags, param):
    """Mouse callback to record board corner points."""
    if event == cv2.EVENT_LBUTTONDOWN:
        if len(points) < 4:
            points.append([x, y])
            print(f"Point {len(points)}: ({x}, {y})")


def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("Unable to open camera.")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    ret, frame = cap.read()
    cap.release()

    if not ret:
        raise RuntimeError("Failed to capture image.")

    print("\n========== CAMERA CALIBRATION ==========\n")
    print("Click the chessboard corners in this order:\n")
    print("1. A8 (Top Left)")
    print("2. H8 (Top Right)")
    print("3. H1 (Bottom Right)")
    print("4. A1 (Bottom Left)")
    print("\nPress ESC to cancel.\n")

    cv2.namedWindow("Camera Calibration")
    cv2.setMouseCallback("Camera Calibration", click)

    while True:
        display = frame.copy()

        for i, p in enumerate(points):
            cv2.circle(display, tuple(p), 8, (0, 0, 255), -1)

            cv2.putText(
                display,
                str(i + 1),
                (p[0] + 10, p[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2,
            )

        cv2.imshow("Camera Calibration", display)

        key = cv2.waitKey(1)

        if len(points) == 4:
            break

        if key == 27:
            print("Calibration cancelled.")
            cv2.destroyAllWindows()
            return

    cv2.destroyAllWindows()

    with open("camera_corners.json", "w") as f:
        json.dump(points, f, indent=4)

    print("\nCalibration completed successfully.")
    print("Saved as camera_corners.json")
    print(points)


if __name__ == "__main__":
    main()