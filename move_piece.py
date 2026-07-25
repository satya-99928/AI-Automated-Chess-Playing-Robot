"""
Automated Chess Playing Robot
Robotic Arm Movement Module

Author: Satyajit Panda

This module moves a chess piece from one square to another
using the calibrated servo positions stored in
board_positions.json.
"""

from adafruit_servokit import ServoKit
import json
import time
import os

# ---------------- Servo Configuration ---------------- #

kit = ServoKit(channels=16)

BASE = 0
SHOULDER = 1
ELBOW = 2
WRIST = 3
ROTATION = 4
GRIPPER = 5

CHANNELS = [
    BASE,
    SHOULDER,
    ELBOW,
    WRIST,
    ROTATION,
    GRIPPER,
]

NAMES = [
    "base",
    "shoulder",
    "elbow",
    "wrist",
    "rotation",
    "gripper",
]

POSITION_FILE = "board_positions.json"

OPEN = 180
CLOSE = 0

HOME = {
    "base": 126,
    "shoulder": 180,
    "elbow": 90,
    "wrist": 90,
    "rotation": 90,
    "gripper": OPEN,
}

STEP_DELAY = 0.025
GRIPPER_DELAY = 0.01

current = HOME.copy()

for ch in CHANNELS:
    kit.servo[ch].set_pulse_width_range(500, 2500)

# ---------------- Utility Functions ---------------- #

def clamp(value):
    return max(0, min(180, int(value)))


def write_servo(name, angle):
    channel = NAMES.index(name)
    kit.servo[channel].angle = clamp(angle)


def load_positions():
    if not os.path.exists(POSITION_FILE):
        raise FileNotFoundError(
            "board_positions.json not found"
        )

    with open(POSITION_FILE, "r") as f:
        return json.load(f)


positions = load_positions()

# ---------------- Servo Motion ---------------- #

def smooth_move(target, delay=STEP_DELAY):
    global current

    target = {
        k: clamp(target[k])
        for k in NAMES
    }

    max_steps = max(
        abs(target[k] - current[k])
        for k in NAMES
    )

    if max_steps == 0:
        return

    for step in range(1, max_steps + 1):

        for name in NAMES:

            start = current[name]
            end = target[name]

            value = start + (
                end - start
            ) * step / max_steps

            write_servo(name, value)

        time.sleep(delay)

    current = target.copy()


def set_gripper(angle):
    global current

    angle = clamp(angle)

    start = current["gripper"]

    if start == angle:
        return

    step = 1 if angle > start else -1

    for a in range(start, angle, step):
        write_servo("gripper", a)
        time.sleep(GRIPPER_DELAY)

    write_servo("gripper", angle)

    current["gripper"] = angle


# ---------------- Robot Positions ---------------- #

def hover(position):
    """
    Lift arm slightly above a square.
    """

    h = position.copy()

    h["shoulder"] = clamp(
        position["shoulder"] + 18
    )

    h["elbow"] = clamp(
        position["elbow"] - 12
    )

    h["gripper"] = current["gripper"]

    return h


def go_home():
    home = HOME.copy()
    home["gripper"] = OPEN
    smooth_move(home)


# ---------------- Pick and Place ---------------- #

def move_piece(from_square, to_square):

    from_square = from_square.lower()
    to_square = to_square.lower()

    if from_square not in positions:
        raise ValueError(
            f"{from_square} not found."
        )

    if to_square not in positions:
        raise ValueError(
            f"{to_square} not found."
        )

    source = positions[from_square].copy()
    destination = positions[to_square].copy()

    source["gripper"] = OPEN
    destination["gripper"] = CLOSE

    print(
        f"\nMoving piece: "
        f"{from_square} -> {to_square}"
    )

    # Return to home position
    go_home()

    # Move above source square
    smooth_move(hover(source))

    # Lower arm
    smooth_move(source)

    time.sleep(0.2)

    # Pick piece
    set_gripper(CLOSE)

    time.sleep(0.3)

    # Lift
    smooth_move(hover(source))

    # Travel above destination
    smooth_move(hover(destination))

    # Lower
    smooth_move(destination)

    time.sleep(0.2)

    # Release piece
    set_gripper(OPEN)

    time.sleep(0.3)

    # Lift away
    smooth_move(hover(destination))

    # Return home
    go_home()

    print("Move completed.\n")


# ---------------- Standalone Test ---------------- #

if __name__ == "__main__":

    move = input(
        "Enter move (example: e2e4): "
    ).strip().lower()

    if len(move) == 4:
        move_piece(
            move[:2],
            move[2:]
        )
    else:
        print("Invalid move format.")