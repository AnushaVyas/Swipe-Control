import cv2
import mediapipe as mp
import time
import numpy as np
import pyautogui
from collections import deque

pyautogui.FAILSAFE = False

WINDOW_NAME = "Unified Gesture Controller"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# ----- TAP PARAMETERS ----- #
PINCH_THRESHOLD = 0.045
HOLD_TIME = 0.55
DOUBLE_TAP_WINDOW = 0.45

last_tap_time = 0
pinch_active = False
holding = False
pinch_start = 0

# ----- SWIPE PARAMETERS ----- #
HISTORY = deque(maxlen=12)
SCROLL_AMOUNT = 1100
SWIPE_MOVE = 250  # pixels for drag movement

# ----- STATE ----- #
mode_text = ""


def pinch_distance(hand):
    ix, iy, iz = hand.landmark[8].x, hand.landmark[8].y, hand.landmark[8].z
    tx, ty, tz = hand.landmark[4].x, hand.landmark[4].y, hand.landmark[4].z
    return np.sqrt((ix - tx) ** 2 + (iy - ty) ** 2 + (iz - tz) ** 2)


def detect_swipe():
    """Detect directional swipe — returns left/right/up/down or None"""
    if len(HISTORY) < HISTORY.maxlen:
        return None

    x0, y0 = HISTORY[0]
    x1, y1 = HISTORY[-1]

    dx = x1 - x0
    dy = y1 - y0

    if abs(dx) > abs(dy) * 1.6 and abs(dx) > 0.06:
        return "right" if dx > 0 else "left"

    if abs(dy) > abs(dx) * 1.6 and abs(dy) > 0.06:
        return "down" if dy > 0 else "up"

    return None


def run():
    global pinch_active, holding, pinch_start, last_tap_time, mode_text

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ Camera unavailable")
        return

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.78,
        min_tracking_confidence=0.78
    ) as hands:

        print("\n✅ Unified Gesture Control Running")
        print("👉 Tap = Click")
        print("👉 Double Tap = Double Click")
        print("👉 Hold Pinch = Drag")
        print("👉 Swipe = Scroll/Tab Move")
        print("👉 Swipe While Dragging = Move Object")
        print("❌ Press Q to quit\n")

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            mode_text = ""

            if results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                d = pinch_distance(hand)
                now = time.time()

                # Track fingertip for swipe detection
                HISTORY.append((hand.landmark[8].x, hand.landmark[8].y))

                # ---- PINCH START ---- #
                if d < PINCH_THRESHOLD and not pinch_active:
                    pinch_active = True
                    pinch_start = now

                # ---- PINCH RELEASE ---- #
                elif d >= PINCH_THRESHOLD and pinch_active:
                    pinch_active = False

                    # Drop if dragging
                    if holding:
                        pyautogui.mouseUp()
                        holding = False
                        mode_text = "DROP"

                    else:
                        # Click or double click
                        if now - last_tap_time <= DOUBLE_TAP_WINDOW:
                            pyautogui.doubleClick()
                            mode_text = "DOUBLE CLICK"
                        else:
                            pyautogui.click()
                            mode_text = "CLICK"

                        last_tap_time = now

                # ---- DRAG START ---- #
                if pinch_active and not holding and now - pinch_start >= HOLD_TIME:
                    pyautogui.mouseDown()
                    holding = True
                    mode_text = "DRAG START"

                # ---- SWIPE GESTURES ---- #
                direction = detect_swipe()

                if direction:
                    if holding:
                        # Move dragged item
                        if direction == "right":
                            pyautogui.moveRel(SWIPE_MOVE, 0)
                            mode_text = "MOVE RIGHT"
                        elif direction == "left":
                            pyautogui.moveRel(-SWIPE_MOVE, 0)
                            mode_text = "MOVE LEFT"
                        elif direction == "up":
                            pyautogui.moveRel(0, -SWIPE_MOVE)
                            mode_text = "MOVE UP"
                        elif direction == "down":
                            pyautogui.moveRel(0, SWIPE_MOVE)
                            mode_text = "MOVE DOWN"

                    else:
                        # Standard swipe actions
                        if direction == "right":
                            pyautogui.hotkey("ctrl", "pgdn")
                            mode_text = "NEXT TAB"
                        elif direction == "left":
                            pyautogui.hotkey("ctrl", "pgup")
                            mode_text = "PREVIOUS TAB"
                        elif direction == "up":
                            pyautogui.scroll(SCROLL_AMOUNT)
                            mode_text = "SCROLL UP"
                        elif direction == "down":
                            pyautogui.scroll(-SCROLL_AMOUNT)
                            mode_text = "SCROLL DOWN"

                    HISTORY.clear()

            # ---- UI FEEDBACK ---- #
            if mode_text:
                cv2.putText(frame, mode_text, (40, 120),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            1.6, (0, 255, 0), 4)

            cv2.imshow(WINDOW_NAME, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
