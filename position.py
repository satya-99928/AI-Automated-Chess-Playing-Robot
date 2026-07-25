import cv2
import chess
import chess.engine
import numpy as np
import os
import time

from board_detector import BoardDetector
from move_piece import move_piece

STOCKFISH_PATH = "/usr/games/stockfish"
STORAGE_DIR = "game_storage"
FILES = "abcdefgh"

HUMAN_COLOR = chess.BLACK
ROBOT_COLOR = chess.WHITE

os.makedirs(STORAGE_DIR, exist_ok=True)
os.makedirs(STORAGE_DIR + "/baselines", exist_ok=True)


def idx_to_square(idx):
    row = idx // 8
    col = idx % 8
    return FILES[col] + str(8 - row)


def chess_sq_to_idx(sq):
    file = chess.square_file(sq)
    rank = chess.square_rank(sq)
    row = 7 - rank
    return row * 8 + file


def extract_squares(warped):
    squares = []
    h, w = warped.shape[:2]
    sw = w // 8
    sh = h // 8

    mx = int(sw * 0.16)
    my = int(sh * 0.16)

    for r in range(8):
        for c in range(8):
            x1 = c * sw + mx
            x2 = (c + 1) * sw - mx
            y1 = r * sh + my
            y2 = (r + 1) * sh - my
            squares.append(warped[y1:y2, x1:x2])

    return squares


def square_score(before, after):
    before = cv2.resize(before, (90, 90))
    after = cv2.resize(after, (90, 90))

    g1 = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    g2 = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    g1 = cv2.GaussianBlur(g1, (5, 5), 0)
    g2 = cv2.GaussianBlur(g2, (5, 5), 0)

    diff = cv2.absdiff(g1, g2)

    center = diff[20:70, 20:70]
    inner = diff[10:80, 10:80]

    return float(
        np.mean(diff) * 0.20 +
        np.mean(center) * 0.60 +
        np.mean(inner) * 0.20
    )


class PositionDB:
    def __init__(self):
        self.baseline = None

    def set_baseline(self, warped, name):
        self.baseline = extract_squares(warped)
        cv2.imwrite(f"{STORAGE_DIR}/baselines/{name}.jpg", warped)
        print("Baseline saved:", name)

    def get_changes(self, warped):
        current = extract_squares(warped)
        scores = []

        for i in range(64):
            score = square_score(self.baseline[i], current[i])
            scores.append((i, score, idx_to_square(i)))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores, current


def capture_stable(detector, frames=7):
    warped_list = []

    for _ in range(frames):
        frame = detector.capture_frame(camera_index=0)
        warped = detector.detect_board(frame)

        if warped is not None:
            warped_list.append(warped)

        time.sleep(0.12)

    if not warped_list:
        raise RuntimeError("Camera board detection failed")

    return warped_list[len(warped_list) // 2]


def expand_scores(raw):
    expanded = {}

    for idx, score in raw.items():
        r = idx // 8
        c = idx % 8

        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr = r + dr
                nc = c + dc

                if 0 <= nr < 8 and 0 <= nc < 8:
                    nidx = nr * 8 + nc

                    if dr == 0 and dc == 0:
                        weight = 1.0
                    elif abs(dc) == 1 and dr == 0:
                        weight = 0.45
                    elif abs(dr) == 1 and dc == 0:
                        weight = 0.35
                    else:
                        weight = 0.15

                    expanded[nidx] = max(
                        expanded.get(nidx, 0),
                        score * weight
                    )

    return expanded


def detect_human_move(db, warped, board):
    scores, current_squares = db.get_changes(warped)

    print("\nChanged squares:")
    for idx, score, name in scores[:16]:
        print(name, round(score, 1))

    raw = {idx: score for idx, score, name in scores[:16]}
    expanded = expand_scores(raw)

    candidates = []

    for move in board.legal_moves:
        fi = chess_sq_to_idx(move.from_square)
        ti = chess_sq_to_idx(move.to_square)

        fs = expanded.get(fi, 0)
        ts = expanded.get(ti, 0)

        rfs = raw.get(fi, 0)
        rts = raw.get(ti, 0)

        total = fs * 1.4 + ts * 1.6

        if rfs > 0:
            total += 40

        if rts > 0:
            total += 40

        if fs > 6 and ts > 6:
            total += 50

        if fs < 3:
            total -= 25

        if ts < 3:
            total -= 25

        candidates.append((move, total, fs, ts, rfs, rts))

    candidates.sort(key=lambda x: x[1], reverse=True)

    print("\nTop candidates:")
    for i, item in enumerate(candidates[:10], 1):
        move, total, fs, ts, rfs, rts = item
        print(
            f"{i}) {move.uci()} score={round(total,1)} "
            f"from={round(fs,1)} to={round(ts,1)} "
            f"raw_from={round(rfs,1)} raw_to={round(rts,1)}"
        )

    best = candidates[0]
    second = candidates[1]

    best_move, best_score, fs, ts, rfs, rts = best
    second_score = second[1]

    if best_score > 40 and best_score - second_score > 10:
        print("\nDetected move:", best_move.uci())
        return best_move, current_squares

    print("\nBest guess:", best_move.uci())
    ok = input("Use this move? (y/n): ").strip().lower()

    if ok == "y":
        return best_move, current_squares

    while True:
        move_text = input("Enter correct move, example c7c5: ").strip().lower()

        try:
            move = chess.Move.from_uci(move_text)

            if move in board.legal_moves:
                return move, current_squares

            print("Illegal move.")

        except:
            print("Invalid format.")


class ChessRobot:
    def __init__(self):
        self.detector = BoardDetector()
        self.board = chess.Board()
        self.engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        self.db = PositionDB()
        self.move_no = 0

        print("Chess Robot initialized")
        print("Human = BLACK")
        print("Robot = WHITE")

    def capture(self):
        return capture_stable(self.detector)

    def robot_turn(self):
        print("\nRobot WHITE thinking...")

        result = self.engine.play(
            self.board,
            chess.engine.Limit(depth=10)
        )

        move = result.move
        move_uci = move.uci()

        print("Robot move:", move_uci)

        move_piece(move_uci[:2], move_uci[2:4])

        self.board.push(move)

        time.sleep(1)

        warped = self.capture()
        self.db.set_baseline(warped, f"move_{self.move_no}_robot")

    def human_turn(self):
        print("\nHuman BLACK turn")
        input("Make BLACK move, remove hand, then press ENTER...")

        time.sleep(1.2)

        warped = self.capture()

        move, current_squares = detect_human_move(
            self.db,
            warped,
            self.board
        )

        print("Accepted human move:", move.uci())

        self.board.push(move)
        self.db.baseline = current_squares

        cv2.imwrite(
            f"{STORAGE_DIR}/baselines/move_{self.move_no}_human.jpg",
            warped
        )

    def run(self):
        print("\nCHESS ROBOT POSITION DETECTION")
        print("Human BLACK | Robot WHITE")

        input("\nSet starting chess position and press ENTER...")

        warped = self.capture()
        self.db.set_baseline(warped, "start")

        print(self.board)
        print("FEN:", self.board.fen())

        while not self.board.is_game_over():
            self.move_no += 1

            print("\n" + "=" * 40)
            print("MOVE", self.move_no)
            print("=" * 40)

            if self.board.turn == ROBOT_COLOR:
                self.robot_turn()
            else:
                self.human_turn()

            print(self.board)
            print("FEN:", self.board.fen())

        print("Game over:", self.board.result())
        self.engine.quit()


if __name__ == "__main__":
    try:
        bot = ChessRobot()
        bot.run()

    except Exception as e:
        print("ERROR:", e)
        import traceback
        traceback.print_exc()
