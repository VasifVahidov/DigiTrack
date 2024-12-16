import cv2
import mediapipe as mp
import tkinter as tk
from tkinter import StringVar, Entry
import time
import threading
import math  # For rounding up the number of people

# Initialize Mediapipe Hand Detector
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=5,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# Global Variables
start_time = None
exit_time = None
active_time = 0
total_active_time = 0
last_activity_time = None
hands_detected = 0
total_hands_detected = 0
running = True
inactive_start_time = None
last_inactivity_start = None
last_inactivity_end = None

# Tkinter Dashboard
root = tk.Tk()
root.title("DigiTrack")
root.geometry("400x500")

# Tkinter Variables
status = StringVar()
status.set("Status: Waiting for detection")
hand_count = StringVar()
hand_count.set("Hands Detected: 0")
time_active = StringVar()
time_active.set("Time Active: 0 seconds")
last_inactive = StringVar()
last_inactive.set("Last Inactivity: None")
total_time_spent = StringVar()
total_time_spent.set("Total Time Spent: 0 seconds")
start_time_display = StringVar()
start_time_display.set("Start Time: Not Started")
people_count = StringVar()
people_count.set("People Detected: 0")
barcode_value = StringVar()  # For the barcode field

# UI Labels
tk.Label(root, text="DigiTrack", font=("Arial", 18, "bold")).pack(pady=10)
status_label = tk.Label(root, textvariable=status, font=("Arial", 12))
status_label.pack(pady=5)

time_label = tk.Label(root, textvariable=time_active, font=("Arial", 12))
time_label.pack(pady=5)

hand_count_label = tk.Label(root, textvariable=hand_count, font=("Arial", 12))
hand_count_label.pack(pady=5)

people_count_label = tk.Label(root, textvariable=people_count, font=("Arial", 12))
people_count_label.pack(pady=5)

last_inactive_label = tk.Label(root, textvariable=last_inactive, font=("Arial", 12))
last_inactive_label.pack(pady=5)

start_time_label = tk.Label(root, textvariable=start_time_display, font=("Arial", 12))
start_time_label.pack(pady=5)

# Barcode Entry Field
tk.Label(root, text="Barcode (Order/Article Number):", font=("Arial", 12)).pack(pady=5)
barcode_entry = Entry(root, textvariable=barcode_value, font=("Arial", 12))
barcode_entry.pack(pady=5)
barcode_entry.focus_set()  # Focus on the field to allow direct input from scanner or manual entry

# Loading Label (Initially hidden)
loading_label = tk.Label(root, text="Loading Camera...", font=("Arial", 12), fg="blue")
loading_label.pack(pady=10)
loading_label.pack_forget()

# Function to check for available cameras
def get_camera():
    cap = cv2.VideoCapture(1)
    if cap.isOpened():
        return cap
    else:
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            return cap
    return None

# Hand Detection Function
def detect_hands():
    global start_time, exit_time, active_time, last_activity_time, hands_detected, total_hands_detected, running, inactive_start_time
    global last_inactivity_start, last_inactivity_end, total_active_time

    loading_label.pack()
    root.update_idletasks()

    cap = get_camera()
    if cap is None:
        status.set("Status: Error: No camera detected.")
        loading_label.pack_forget()
        return

    loading_label.pack_forget()

    start_time = time.time()
    start_time_display.set(f"Start Time: {time.strftime('%H:%M:%S', time.gmtime(start_time))}")

    while running:
        ret, frame = cap.read()
        if not ret:
            status.set("Status: Failed to grab frame")
            break

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        if result.multi_hand_landmarks:
            hands_detected = len(result.multi_hand_landmarks)
            total_hands_detected += hands_detected
            hand_count.set(f"Hands Detected: {hands_detected}")
            people_estimate = math.ceil(hands_detected / 2)
            people_count.set(f"People Detected: {people_estimate}")
            status.set("Status: Active")
            active_time = int(time.time() - start_time)
            time_active.set(f"Time Active: {active_time} seconds")
            last_activity_time = time.time()
            total_active_time += active_time
            total_time_spent.set(f"Total Time Spent: {total_active_time} seconds")
            inactive_start_time = None

            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        else:
            hands_detected = 0
            hand_count.set("Hands Detected: 0")
            people_count.set("People Detected: 0")
            status.set("Status: No hands detected")
            if inactive_start_time is None:
                inactive_start_time = time.time()
            if time.time() - inactive_start_time >= 10:
                if last_inactivity_start is None:
                    last_inactivity_start = time.strftime('%H:%M:%S', time.gmtime(time.time()))
                last_inactivity_end = time.strftime('%H:%M:%S', time.gmtime(time.time()))
                last_inactive.set(f"Last Inactivity: {last_inactivity_start} - {last_inactivity_end}")
                status.set("Status: Idle (No hands detected for 10 seconds)")

        cv2.imshow("DigiTrack - Hand Movement Detection", frame)
        root.update_idletasks()
        root.update()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            running = False
            exit_time = time.time()
            exit_time_str = time.strftime('%H:%M:%S', time.gmtime(exit_time))
            status.set(f"Status: Closed at {exit_time_str}")
            break

    cap.release()
    cv2.destroyAllWindows()

def start_detection():
    detection_thread = threading.Thread(target=detect_hands)
    detection_thread.daemon = True
    detection_thread.start()

tk.Button(root, text="Start Detection", command=start_detection, font=("Arial", 12)).pack(pady=10)

root.mainloop()
