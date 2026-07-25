"""
Automated Chess Playing Robot
Servo Test Utility

Author: Satyajit Panda

Moves all six servo motors to 90 degrees.
Useful for:
- Initial testing
- Servo horn alignment
- Checking PCA9685 connections
"""

from adafruit_servokit import ServoKit
import time

kit = ServoKit(channels=16)

SERVO_CHANNELS = [0, 1, 2, 3, 4, 5]

ANGLE = 90
DELAY = 0.5


def initialize_servos():
    """Configure pulse width range for all servos."""
    for ch in SERVO_CHANNELS:
        kit.servo[ch].set_pulse_width_range(500, 2500)


def move_all(angle):
    """Move all servos to the specified angle."""
    print(f"\nMoving all servos to {angle}°...\n")

    for ch in SERVO_CHANNELS:
        print(f"Servo {ch} → {angle}°")
        kit.servo[ch].angle = angle
        time.sleep(DELAY)

    print("\nAll servos positioned successfully.")


if __name__ == "__main__":
    initialize_servos()
    move_all(ANGLE)