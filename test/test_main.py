import pytest
from unittest.mock import patch, MagicMock
from main import get_camera, detect_hands, root, status, hand_count, start_detection


# Test the get_camera function
def test_get_camera():
    # Mock cv2.VideoCapture
    with patch("cv2.VideoCapture") as mock_capture:
        # Simulate first camera is not available
        mock_capture.return_value.isOpened.side_effect = [False, True]

        # Test that camera is detected after the second attempt
        camera = get_camera()
        assert camera is not None, "Camera should be detected"

        # Test when no camera is available
        mock_capture.return_value.isOpened.side_effect = [False, False]
        camera = get_camera()
        assert camera is None, "Camera should not be detected"


# Test hand detection logic
@patch("cv2.VideoCapture")
@patch("mediapipe.solutions.hands.Hands.process")
def test_detect_hands(mock_process, mock_capture):
    # Mock Mediapipe Hands process to simulate hand detection
    mock_result = MagicMock()
    mock_result.multi_hand_landmarks = [MagicMock(), MagicMock()]  # Simulating 2 hands detected
    mock_process.return_value = mock_result

    # Mock cv2.VideoCapture behavior
    mock_capture_instance = MagicMock()
    mock_capture.return_value = mock_capture_instance
    mock_capture_instance.read.return_value = (True, MagicMock())

    # Start detection in a controlled manner
    with patch("main.running", new=True):
        detect_hands()  # This would normally run in an infinite loop

        # Check if hand detection was processed
        assert mock_process.call_count > 0, "Hand detection function should process frames"


# Test the initial state of the Tkinter UI
def test_tkinter_ui_initial_state():
    assert status.get() == "Status: Waiting for detection"
    assert hand_count.get() == "Hands Detected: 0"
    assert time_active.get() == "Time Active: 0 seconds"
    assert last_inactive.get() == "Last Inactivity: None"
    assert total_time_spent.get() == "Total Time Spent: 0 seconds"
    assert start_time_display.get() == "Start Time: Not Started"
    assert people_count.get() == "People Detected: 0"
    assert barcode_value.get() == ""


# Test UI after clicking the "Start Detection" button
def test_tkinter_ui_start_detection():
    # Mock the start_detection function to avoid threading
    with patch("main.start_detection") as mock_start_detection:
        start_button = root.children["!button"]
        start_button.invoke()

        # Check if start_detection is called
        mock_start_detection.assert_called_once()


# Test if the status updates correctly during detection
@patch("cv2.VideoCapture")
@patch("mediapipe.solutions.hands.Hands.process")
def test_tkinter_ui_status_update(mock_process, mock_capture):
    # Mock the hand detection process
    mock_result = MagicMock()
    mock_result.multi_hand_landmarks = [MagicMock(), MagicMock()]  # Simulating 2 hands detected
    mock_process.return_value = mock_result

    # Mock cv2.VideoCapture behavior
    mock_capture_instance = MagicMock()
    mock_capture.return_value = mock_capture_instance
    mock_capture_instance.read.return_value = (True, MagicMock())

    # Start detection in a controlled manner
    with patch("main.running", new=True):
        detect_hands()  # Normally runs in an infinite loop

        # Simulate the UI update for hands detected
        assert status.get() == "Status: Active"
        assert hand_count.get() == "Hands Detected: 2"
        assert people_count.get() == "People Detected: 1"  # 2 hands, assuming 1 person
        assert time_active.get() != "Time Active: 0 seconds"
        assert total_time_spent.get() != "Total Time Spent: 0 seconds"


# Test if the status shows inactivity when no hands are detected
@patch("cv2.VideoCapture")
@patch("mediapipe.solutions.hands.Hands.process")
def test_tkinter_ui_inactivity(mock_process, mock_capture):
    # Mock no hands detected
    mock_result = MagicMock()
    mock_result.multi_hand_landmarks = []  # No hands detected
    mock_process.return_value = mock_result

    # Mock cv2.VideoCapture behavior
    mock_capture_instance = MagicMock()
    mock_capture.return_value = mock_capture_instance
    mock_capture_instance.read.return_value = (True, MagicMock())

    # Start detection in a controlled manner
    with patch("main.running", new=True):
        detect_hands()  # Normally runs in an infinite loop

        # Simulate the UI update for inactivity
        assert status.get() == "Status: Idle (No hands detected for 10 seconds)"
        assert hand_count.get() == "Hands Detected: 0"
        assert people_count.get() == "People Detected: 0"
        assert last_inactive.get() != "Last Inactivity: None"


# Test if the barcode field updates correctly
def test_barcode_field_update():
    barcode_value.set("1234567890")
    assert barcode_value.get() == "1234567890"
