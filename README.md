# ♟️ AI Automated Chess Playing Robot

An AI-powered robotic chess system that detects human moves using computer vision, calculates the best response using the Stockfish chess engine, and physically moves chess pieces with a 6-DOF robotic arm controlled by a Raspberry Pi.

---

## 📌 Features

- ♟️ Automatic chess move detection using OpenCV
- 🤖 AI opponent powered by Stockfish
- 🎥 USB camera with perspective transformation
- 🦾 6-DOF robotic arm using servo motors
- 🎯 Manual calibration for camera and robotic arm
- 📷 Stable image capture for reliable move detection
- 📁 JSON-based calibration storage
- 🐍 Developed completely in Python

---

## 🛠️ Hardware Used

- Raspberry Pi 5
- USB Camera
- PCA9685 16-Channel Servo Driver
- 6 Servo Motors
- Robotic Arm with Gripper
- Chessboard and Chess Pieces
- External Power Supply

---

## 💻 Software Used

- Python 3
- OpenCV
- NumPy
- python-chess
- Stockfish Chess Engine
- Adafruit ServoKit
- Pygame

---

## 📂 Project Structure

```text
AI-Automated-Chess-Playing-Robot/
│
├── board_detector.py
├── calibrate_camera.py
├── calibrate_arm_save.py
├── move_piece.py
├── position.py
│
├── board_positions.json
├── camera_corners.json
│
├
├── test_warp.py
│── all_90.py
│
├
│
├── images/
├── docs/
├── stockfish/
│
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/satya-99928/AI-Automated-Chess-Playing-Robot.git
```

Go to the project folder:

```bash
cd AI-Automated-Chess-Playing-Robot
```

Install the required packages:

```bash
pip install -r requirements.txt
```

Install Stockfish and update the path inside `position.py`.

---

## 📷 Camera Calibration

Run:

```bash
python calibrate_camera.py
```

Click the board corners in the following order:

1. A8
2. H8
3. H1
4. A1

This generates:

```
camera_corners.json
```

---

## 🤖 Arm Calibration

Run:

```bash
python calibrate_arm_save.py
```

Move the robotic arm using the keyboard controls and save the servo angles for every chess square.

This generates:

```
board_positions.json
```

---

## ▶️ Running the Project

Start the chess robot:

```bash
python position.py
```

The robot will:

1. Capture the chessboard.
2. Detect the human move.
3. Validate the move using `python-chess`.
4. Calculate the best response using Stockfish.
5. Move the chess piece using the robotic arm.

---

## 🧪 Test Utilities

### Test Camera Warp

```bash
python tests/test_warp.py
```

### Move All Servos to 90°

```bash
python tests/all_90.py
```

---

## 🧠 Technologies Used

- Python
- OpenCV
- Computer Vision
- Robotics
- Raspberry Pi
- Servo Control
- PCA9685
- Stockfish
- JSON
- Pygame

---

## 🚀 Future Improvements

- Automatic piece recognition
- Captured piece handling
- Castling automation
- Pawn promotion support
- En passant support
- Inverse kinematics
- Web dashboard for monitoring
- Voice-controlled gameplay

---

## 📷 Project Images
<img width="1280" height="960" alt="calibration" src="https://github.com/user-attachments/assets/d4332786-ce37-4d97-8c59-43a5bf9c57ad" />

<img width="1280" height="960" alt="robot" src="https://github.com/user-attachments/assets/36190b7d-c477-4e4e-9f2e-bf6ac765a0bd" />


## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Satyajit Panda**

B.Tech Computer Science & Engineering (IoT)

Siksha 'O' Anusandhan (SOA) University

GitHub: [github-->](https://github.com/satya-99928)

LinkedIn: [*( LinkedIn profile link here.)*](https://www.linkedin.com/in/satyajit-panda-9b160624b/)
