import cv2
import mediapipe as mp
import time
import pyautogui
import numpy as np

pyautogui.FAILSAFE = False

WINDOW_NAME = "Tap Gesture Control"
cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(WINDOW_NAME, cv2.WND_PROP_TOPMOST, 1)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# gesture parameters
PINCH_THRESHOLD = 0.045           # smaller → more sensitive
HOLD_TIME = 0.55                  # seconds before treating as drag
DOUBLE_TAP_WINDOW = 0.45          # seconds allowed for double-tap
DEBOUNCE = 0.25                   # prevents repeated triggers

last_pinch_time = 0
holding = False
pinch_active = False


def get_pinch_distance(hand):
    """Distance between index fingertip & thumb tip"""
    ix, iy, iz = hand.landmark[8].x, hand.landmark[8].y, hand.landmark[8].z
    tx, ty, tz = hand.landmark[4].x, hand.landmark[4].y, hand.landmark[4].z
    return np.sqrt((ix - tx) ** 2 + (iy - ty) ** 2 + (iz - tz) ** 2)


def run():
    global last_pinch_time, holding, pinch_active

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        print("❌ ERROR: Cannot access camera")
        return

    with mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.75,
        min_tracking_confidence=0.75
    ) as hands:

        print("\n✅ Tap Gesture Mode Running")
        print("👉 Tap fingers together = Left Click")
        print("👉 Tap twice quickly = Double Click")
        print("👉 Hold pinch = Drag/Click Hold")
        print("❌ Press Q to quit\n")

        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb)

            gesture_text = ""

            if results.multi_hand_landmarks:
                hand = results.multi_hand_landmarks[0]
                mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

                pinch_distance = get_pinch_distance(hand)
                now = time.time()

                # detect pinch start
                if pinch_distance < PINCH_THRESHOLD and not pinch_active:
                    pinch_active = True
                    pinch_start = now

                # detect release
                elif pinch_distance >= PINCH_THRESHOLD and pinch_active:
                    pinch_active = False

                    # how long were we holding?
                    duration = now - pinch_start

                    if duration >= HOLD_TIME:
                        pyautogui.mouseUp()
                        holding = False
                        gesture_text = "RELEASE DRAG"

                    else:
                        # double tap?
                        if now - last_pinch_time <= DOUBLE_TAP_WINDOW:
                            pyautogui.doubleClick()
                            gesture_text = "DOUBLE CLICK"
                        else:
                            pyautogui.click()
                            gesture_text = "CLICK"

                        last_pinch_time = now

                # detect drag hold
                if pinch_active:
                    if not holding and now - pinch_start >= HOLD_TIME:
                        pyautogui.mouseDown()
                        holding = True
                        gesture_text = "DRAGGING"

            if gesture_text:
                cv2.putText(
                    frame, gesture_text,
                    (40, 120),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.6, (0, 255, 0), 4
                )

            cv2.imshow(WINDOW_NAME, frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
