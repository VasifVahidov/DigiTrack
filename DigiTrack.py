from flask import Flask, render_template, Response, request, jsonify
import cv2
import mediapipe as mp
import time
import threading
import csv
import os

app = Flask(__name__)

# Initialize MediaPipe Hand Detector
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=6, min_detection_confidence=0.5)
mp_draw = mp.solutions.drawing_utils

# Global variables
hand_detected = False
start_time = None
total_time = 0
last_hand_time = 0
lock = threading.Lock()
production_order = None
detection_running = False
camera_thread = None
stop_event = threading.Event()  # Used to signal threads to stop
cap = None  # Global camera instance

def initialize_camera():
    global cap
    print("Initializing camera during server startup...")
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Camera could not be initialized.")
        cap = None
    else:
        # Set default resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("Camera initialized successfully.")


def release_camera():
    global cap
    if cap and cap.isOpened():
        cap.release()
        print("Camera released successfully.")


# Helper function to format time in HH:MM:SS
def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def save_to_csv(production_order, total_time, start_time, stop_time):
    csv_file = "detection_data.csv"
    file_exists = os.path.isfile(csv_file)

    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Production Order", "Total Time (HH:MM:SS)", "From", "To"])
        formatted_time = format_time(total_time)
        writer.writerow([production_order, formatted_time, start_time, stop_time])


def hand_detection():
    global hand_detected, start_time, total_time, last_hand_time, detection_running, production_order, cap

    print("Starting hand detection...")

    if not cap or not cap.isOpened():
        print("Error: Camera not initialized. Stopping detection.")
        detection_running = False
        return

    while detection_running and not stop_event.is_set():
        success, frame = cap.read()
        if not success:
            print("Error: Could not read from the camera. Stopping detection.")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(frame_rgb)

        current_time = time.time()
        hand_present = result.multi_hand_landmarks is not None

        with lock:
            if hand_present:
                if not hand_detected:
                    hand_detected = True
                    start_time = current_time
                last_hand_time = current_time
            else:
                time_since_last_hand = current_time - last_hand_time

                if time_since_last_hand > 10 and time_since_last_hand <= 30:
                    if hand_detected and start_time:
                        total_time += current_time - start_time
                        start_time = None
                        hand_detected = False
                        print("Time tracking paused.")

                elif time_since_last_hand > 30:
                    if hand_detected and start_time:
                        total_time += current_time - start_time
                        start_time = None
                        hand_detected = False

                    stop_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time))
                    start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time - total_time))
                    save_to_csv(production_order, total_time, start_time_str, stop_time)

                    print("Session stopped. Data saved to CSV.")

                    production_order = None
                    total_time = 0
                    start_time = None
                    hand_detected = False
                    detection_running = False
                    last_hand_time = 0

        if hand_present:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

    print("Hand detection stopped.")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/start_detection', methods=['POST'])
def start_detection():
    global production_order, detection_running, total_time, start_time, hand_detected, last_hand_time, camera_thread, stop_event

    data = request.json
    production_order = data.get("production_order")
    if not production_order:
        return jsonify({"error": "Production order is required"}), 400

    if camera_thread and camera_thread.is_alive():
        print("Stopping previous detection thread...")
        stop_event.set()
        camera_thread.join()

    with lock:
        total_time = 0
        start_time = None
        hand_detected = False
        last_hand_time = time.time()
        detection_running = True
        stop_event.clear()

    print(f"Starting detection for production order: {production_order}")
    camera_thread = threading.Thread(target=hand_detection)
    camera_thread.start()

    return jsonify({"message": "Detection started", "production_order": production_order})


@app.route('/stop_detection', methods=['POST'])
def stop_detection():
    global detection_running, total_time, hand_detected, start_time, production_order, stop_event, camera_thread

    with lock:
        detection_running = False
        stop_event.set()
        if hand_detected and start_time:
            elapsed_time = time.time() - start_time
            total_time += elapsed_time
            start_time = None
            hand_detected = False

    if camera_thread and camera_thread.is_alive():
        camera_thread.join()

    stop_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    start_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - total_time))

    save_to_csv(production_order, total_time, start_time_str, stop_time)

    response = {
        "message": "Detection stopped and data saved",
        "csv_file": "detection_data.csv",
        "total_time": format_time(total_time),
        "start_time": start_time_str,
        "stop_time": stop_time,
        "production_order": None
    }

    production_order = None
    total_time = 0

    return jsonify(response)


@app.route('/video_feed')
def video_feed():
    global detection_running
    if detection_running:
        return Response(hand_detection(), mimetype='multipart/x-mixed-replace; boundary=frame')
    return Response("")


@app.route('/total_time')
def get_total_time():
    global total_time, hand_detected, start_time, last_hand_time
    with lock:
        current_time = time.time()
        time_since_last_hand = current_time - last_hand_time
        status = "stopped"

        if hand_detected:
            status = "running"
            elapsed_time = current_time - start_time
            current_total = total_time + elapsed_time
        elif time_since_last_hand <= 30:
            status = "idle"
            current_total = total_time
        else:
            current_total = total_time

    return {
        "total_time": round(current_total, 0),
        "production_order": production_order,
        "status": status
    }


if __name__ == "__main__":
    initialize_camera()
    try:
        app.run(debug=True)
    finally:
        release_camera()
