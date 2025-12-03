import tkinter as tk
import subprocess
import sys
import os

# Gesture script paths (customize as needed)
GESTURE_DIR = os.path.join(os.path.dirname(__file__), "gestures")
BRIGHTNESS_PY = os.path.join(GESTURE_DIR, "brightness.py")
CONTROL_PY = os.path.join(GESTURE_DIR, "control.py")

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
root.geometry("800x500")
root.configure(bg="#EEF7FA")

# Custom button style
button_style = dict(
    font=("Segoe UI", 14, "bold"),
    bg="#166C97",
    fg="white",
    activebackground="#E7EFF4",
    activeforeground="#E3F8FF",
    relief="flat",
    bd=0,
    padx=18, pady=10,
    cursor="hand2",
)

title = tk.Label(root, text="Select Function:", font=("Segoe UI", 16, "bold"), bg="#EEF7FA", fg="#27A6E6")
title.pack(pady=(18,10))

brightness_btn = tk.Button(root, text="Brightness Control", command=run_brightness, **button_style)
brightness_btn.pack(pady=9, fill="x", padx=40)

swipe_btn = tk.Button(root, text="Window Scrolling", command=run_swipe, **button_style)
swipe_btn.pack(pady=9, fill="x", padx=40)

exit_btn = tk.Button(root, text="Exit", command=exit_app,
                     font=("Segoe UI", 12, "bold"), bg="#DC3545", fg="white",
                     activebackground="#A92232", activeforeground="white", relief="flat", bd=0, padx=18, pady=9, cursor="hand2")
exit_btn.pack(pady=(18,5), fill="x", padx=90)

# Handle window close (clicking the 'X')
root.protocol("WM_DELETE_WINDOW", exit_app)

root.mainloop()