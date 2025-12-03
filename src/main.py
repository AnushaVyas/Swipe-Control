import tkinter as tk
import subprocess
import sys
import os

# Gesture script paths (customize as needed)
GESTURE_DIR = os.path.join(os.path.dirname(__file__), "gestures")
BRIGHTNESS_PY = os.path.join(GESTURE_DIR, "brightness.py")
SWIPE_PY = os.path.join(GESTURE_DIR, "swipe.py")

process = None  # Track child process

def run_brightness():
    global process
    if process: process.terminate()
    process = subprocess.Popen([sys.executable, BRIGHTNESS_PY])

def run_swipe():
    global process
    if process: process.terminate()
    process = subprocess.Popen([sys.executable, CONTROL_PY])

def exit_app():
    if process:
        try:
            process.terminate()
        except Exception:
            pass
    root.destroy()
    sys.exit(0)  # Ensures full shutdown

root = tk.Tk()
root.title("Gesture Controller")
root.geometry("700x1000")
root.configure(bg="#EEF7FA")

title = tk.Label(root, text="Choose Gesture Mode", font=("Segoe UI", 22, "bold"), bg="#F3F8FE", fg="#2187E7")
title.pack(pady=(40, 8))


brightness_info = (
    "Brightness Control Gesture:\n"
    "Bring your thumb and index finger together to decrease brightness.\n"
    "Spread them apart to increase brightness.\n"
)

swipe_info = (
    "Swipe Gesture Directions (Correct Physical Motions):\n"
    "Swipe Right\n"
    "Move your index finger from left → to right\n"
    "Swipe Left\n"
    "Move your index finger from right → to left\n"
    "Swipe Up\n"
    "Move your index finger from bottom → upward\n"
    "Swipe Down\n"
    "Move your index finger from top → downward\n"
    "Drag Mode Swiping (While Pinching)\n"
    "Pinch & hold → start drag\n"
    "Move left → drag item left\n"
    "Move right → drag item right\n"
    "Move up → drag item upward\n"
    "Move down → drag item downward\n"
    "Release pinch→drop")


# Custom button style
button_style = dict(
    font=("Segoe UI", 16, "bold"),
    bg="#166C97",
    fg="white",
    activebackground="#E7EFF4",
    activeforeground="#E3F8FF",
    # relief="flat",
    bd=0,
    padx=18, pady=10,
    cursor="hand2",
    width=20,
    height=1
)


info_label = tk.Label(root, text=brightness_info, font=("Segoe UI", 12),fg="#176CA6", justify="left" , anchor="w")
info_label.pack(pady=(5,5))

brightness_btn = tk.Button(root, text="Brightness Control", command=run_brightness, **button_style)
brightness_btn.pack(pady=9, padx=40)

info_label = tk.Label(root, text=swipe_info, font=("Segoe UI", 12),fg="#176CA6", justify="left",  anchor="w")
info_label.pack(pady=(5,5))

swipe_btn = tk.Button(root, text="Window Scrolling & Tapping", command=run_swipe, **button_style)
swipe_btn.pack(pady=9, padx=40)

exit_btn = tk.Button(root, text="Exit", command=exit_app,
                     font=("Segoe UI", 12, "bold"), bg="#DC3545", fg="white",
                     activebackground="#FF4056", activeforeground="white", relief="flat", bd=0, padx=18, pady=9, cursor="hand2")
exit_btn.pack(pady=(5,5), fill="x", padx=40)

# Handle window close (clicking the 'X')
root.protocol("WM_DELETE_WINDOW", exit_app)

root.mainloop()