"""
Automated Chess Playing Robot
Robotic Arm Calibration Tool

Author: Satyajit Panda

This utility allows manual calibration of the robotic arm.
The servo angles for every chess square are stored in
board_positions.json.
"""

from adafruit_servokit import ServoKit
import pygame
import time
import json
import os

# ---------------- Servo Configuration ---------------- #

kit = ServoKit(channels=16)

BASE = 0
SHOULDER = 1
ELBOW = 2
WRIST = 3
ROTATION = 4
GRIPPER = 5

SAVE_FILE = "board_positions.json"

MIN_ANGLE = {
    BASE: 0,
    SHOULDER: 0,
    ELBOW: 0,
    WRIST: 0,
    ROTATION: 0,
    GRIPPER: 0,
}

MAX_ANGLE = {
    BASE: 180,
    SHOULDER: 180,
    ELBOW: 180,
    WRIST: 180,
    ROTATION: 180,
    GRIPPER: 180,
}

GRIPPER_OPEN = 180
GRIPPER_CLOSE = 0

angles = {
    BASE: 126,
    SHOULDER: 180,
    ELBOW: 90,
    WRIST: 90,
    ROTATION: 90,
    GRIPPER: GRIPPER_OPEN,
}

for ch in angles:
    kit.servo[ch].set_pulse_width_range(500, 2500)


# ---------------- Utility Functions ---------------- #

def load_positions():
    if not os.path.exists(SAVE_FILE):
        return {}

    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

            if isinstance(data, dict):
                return data

    except (json.JSONDecodeError, OSError):
        return {}

    return {}


saved_positions = load_positions()


def saved_square_count():
    return sum(
        1
        for f in "abcdefgh"
        for r in "12345678"
        if f + r in saved_positions
    )


def save_current_position(square):
    square = square.lower().strip()

    saved_positions[square] = {
        "base": angles[BASE],
        "shoulder": angles[SHOULDER],
        "elbow": angles[ELBOW],
        "wrist": angles[WRIST],
        "rotation": angles[ROTATION],
        "gripper": angles[GRIPPER],
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(saved_positions, f, indent=4)

    percent = saved_square_count() / 64 * 100

    print("\nSaved:", square)
    print(saved_positions[square])
    print(f"Progress: {saved_square_count()}/64 ({percent:.1f}%)")


def move_servo(channel, delta):
    angles[channel] += delta

    angles[channel] = max(
        MIN_ANGLE[channel],
        min(MAX_ANGLE[channel], angles[channel]),
    )

    kit.servo[channel].angle = angles[channel]


def set_servo(channel, angle):
    angles[channel] = max(
        MIN_ANGLE[channel],
        min(MAX_ANGLE[channel], angle),
    )

    kit.servo[channel].angle = angles[channel]


# ---------------- Move to Home ---------------- #

print("\nMoving arm to HOME position...\n")

for ch, angle in angles.items():
    kit.servo[ch].angle = angle
    time.sleep(0.25)

# ---------------- Pygame ---------------- #

pygame.init()

screen = pygame.display.set_mode((620, 470))
pygame.display.set_caption("Chess Robot Arm Calibration")

font = pygame.font.SysFont(None, 24)

ARM_STEP = 2
GRIPPER_STEP = 15

ARM_DELAY = 0.03
GRIPPER_DELAY = 0.005

print("""
========= CHESS ARM CALIBRATION =========

Arrow Keys  -> Base & Shoulder
W/S         -> Elbow
A/D         -> Wrist
Q/E         -> Rotation
O/P         -> Gripper

SPACE       -> Fully Open Gripper
C           -> Fully Close Gripper

ENTER       -> Save Current Square
ESC         -> Exit

=========================================
""")

clock = pygame.time.Clock()
running = True

while running:

    screen.fill((25, 25, 25))

    info = [
        "Chess Robot Arm Calibration",
        f"Saved Squares : {saved_square_count()} / 64",
        "",
        "LEFT / RIGHT : Base",
        "UP / DOWN    : Shoulder",
        "W / S        : Elbow",
        "A / D        : Wrist",
        "Q / E        : Rotation",
        "O / P        : Gripper",
        "",
        "SPACE : Open Gripper",
        "C     : Close Gripper",
        "ENTER : Save Square",
        "ESC   : Exit",
        "",
        f"Base      : {angles[BASE]}",
        f"Shoulder  : {angles[SHOULDER]}",
        f"Elbow     : {angles[ELBOW]}",
        f"Wrist     : {angles[WRIST]}",
        f"Rotation  : {angles[ROTATION]}",
        f"Gripper   : {angles[GRIPPER]}",
    ]

    y = 20

    for line in info:
        screen.blit(
            font.render(line, True, (255, 255, 255)),
            (20, y),
        )
        y += 22

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_RETURN:

                square = input(
                    "\nEnter square name (example e2 or home): "
                )

                save_current_position(square)

            elif event.key == pygame.K_SPACE:
                set_servo(GRIPPER, GRIPPER_OPEN)

            elif event.key == pygame.K_c:
                set_servo(GRIPPER, GRIPPER_CLOSE)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        move_servo(BASE, -ARM_STEP)
        time.sleep(ARM_DELAY)

    if keys[pygame.K_RIGHT]:
        move_servo(BASE, ARM_STEP)
        time.sleep(ARM_DELAY)

    if keys[pygame.K_UP]:
        move_servo(SHOULDER, -ARM_STEP)
        time.sleep(ARM_DELAY)

    if keys[pygame.K_DOWN]:
        move_servo(SHOULDER, ARM_STEP)
        time.sleep(ARM_DELAY)

    if keys[pygame.K_w]:
        move_servo(ELBOW, -ARM_STEP)
        time.sleep(ARM_DELAY)

    if keys[pygame.K_s]:
        move_servo(ELBOW, ARM_STEP)
        time.sleep(ARM_DELAY)

    if keys[pygame.K_a]:
        move_servo(WRIST, -ARM_STEP)
        time.sleep(ARM_DELAY)

    if keys[pygame.K_d]:
        move_servo(WRIST, ARM_STEP)
        time.sleep(ARM_DELAY)

    if keys[pygame.K_q]:
        move_servo(ROTATION, -ARM_STEP)
        time.sleep(ARM_DELAY)

    if keys[pygame.K_e]:
        move_servo(ROTATION, ARM_STEP)
        time.sleep(ARM_DELAY)

    if keys[pygame.K_o]:
        move_servo(GRIPPER, GRIPPER_STEP)
        time.sleep(GRIPPER_DELAY)

    if keys[pygame.K_p]:
        move_servo(GRIPPER, -GRIPPER_STEP)
        time.sleep(GRIPPER_DELAY)

    clock.tick(30)

pygame.quit()

print("Calibration finished.")