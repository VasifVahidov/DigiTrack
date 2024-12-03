
markdown
Code kopieren
# DigiTrack - Hand Movement Detection System

DigiTrack is a hand movement detection application built using Python, OpenCV, MediaPipe, and Tkinter. The application tracks hand movements via a webcam and displays real-time statistics on the detected hands, estimated number of people, active time, and idle time.

## Features

- Detects hands using the MediaPipe library.
- Displays real-time statistics including:
  - Number of hands detected.
  - Estimated number of people based on the number of hands.
  - Time active (time since hand detection started).
  - Time spent active in total.
  - Last period of inactivity.
- Displays a simple GUI with Tkinter for visual feedback.
- Ability to enter a barcode number.
- Camera feed displayed on the main window.

## Libraries Required

- `opencv-python`: For video capture and frame manipulation.
- `mediapipe`: For hand detection and processing.
- `tkinter`: For the GUI.
- `time`: For managing timestamps.
- `threading`: For running the hand detection function in a separate thread.
- `math`: For rounding up the number of people detected.

## Installation

To get started with DigiTrack, follow these steps:

1. Install Python 3.x from [python.org](https://www.python.org/).
2. Install required dependencies using `pip`:

```bash
pip install opencv-python mediapipe tk
Clone or download this repository to your local machine.
How to Run
Ensure that a webcam is connected to your computer.
Navigate to the directory where you saved the project.
Run the script:
bash
Code kopieren
python digitrack.py
The Tkinter interface will appear, and the application will start detecting hands via the webcam.
Click the Start Detection button to begin tracking.
The real-time statistics will update as the application detects hands.
GUI Overview
Status: Displays whether the system is waiting for detection, detecting hands, or idle.
Hands Detected: Shows the number of hands detected in the camera feed.
People Detected: Displays an estimate of the number of people based on the number of hands detected (rounded up).
Time Active: Shows how long the hands have been actively detected.
Last Inactivity: Displays the start and end times of the last inactivity period (if no hands are detected for 10 seconds).
Total Time Spent: Shows the total time the system has been active since the start.
Barcode: Input field for entering a barcode number.
Loading Label: Displays when the camera is being initialized.
Code Explanation
Libraries
OpenCV (cv2): Used for video capture and frame processing.
MediaPipe (mediapipe): Provides pre-built models for detecting hands in video frames.
Tkinter (tk): The GUI library used to display information and allow user interaction.
Time (time): Used for tracking timestamps such as start time, active time, and inactivity duration.
Threading: Used to run the hand detection function in a separate thread, allowing for real-time UI updates.
Key Functions
get_camera(): Attempts to open a webcam and return the video capture object.
detect_hands(): Main function for hand detection. It processes each video frame to detect hands, update statistics, and handle inactivity.
start_detection(): Starts the hand detection process in a separate thread.
Global Variables
start_time: Stores the timestamp when the hand detection starts.
exit_time: Stores the timestamp when the program is closed.
active_time: Tracks how long the system has been actively detecting hands.
hands_detected: Number of hands detected in the current frame.
total_hands_detected: Cumulative number of hands detected since the start.
running: A flag to control the ongoing detection loop.
inactive_start_time: The time when the system first detects inactivity (no hands detected).
last_inactivity_start / last_inactivity_end: Track the time period when inactivity occurs.
Tkinter Elements
root: The main Tkinter window.
status, hand_count, time_active, people_count, last_inactive, start_time_display, total_time_spent: String variables to dynamically update the UI with the latest information.
barcode_value: A string variable for the barcode entry field.
Notes
The application supports up to 5 hands being detected simultaneously.
If no hands are detected for 10 seconds, the system considers it idle and updates the UI accordingly.
Press 'q' to quit the application.
License
This project is open-source and available under the MIT License. Feel free to use, modify, and contribute!

Contact
For any questions or issues, feel free to open an issue or contact the repository owner.

bash
Code kopieren

This `README.md` provides an overview of the project, installation instructions, explanation of ke
