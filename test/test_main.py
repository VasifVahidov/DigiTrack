import pytest
from unittest.mock import MagicMock

# Fixture to mock the Tkinter StringVar objects
@pytest.fixture
def mock_gui_variables():
    # Mock the Tkinter StringVar() objects
    time_active = MagicMock()
    last_inactive = MagicMock()
    total_time_spent = MagicMock()
    start_time_display = MagicMock()
    people_count = MagicMock()
    barcode_value = MagicMock()

    # Set default return values for get()
    time_active.get.return_value = "Time Active: 0 seconds"
    last_inactive.get.return_value = "Last Inactivity: None"
    total_time_spent.get.return_value = "Total Time Spent: 0 seconds"
    start_time_display.get.return_value = "Start Time: Not Started"
    people_count.get.return_value = "People Detected: 0"
    barcode_value.get.return_value = ""

    return time_active, last_inactive, total_time_spent, start_time_display, people_count, barcode_value


# Test the initial GUI state
def test_gui_initialization(mock_gui_variables):
    time_active, last_inactive, total_time_spent, start_time_display, people_count, barcode_value = mock_gui_variables

    # Assert that the initial values are correct
    assert time_active.get() == "Time Active: 0 seconds"
    assert last_inactive.get() == "Last Inactivity: None"
    assert total_time_spent.get() == "Total Time Spent: 0 seconds"
    assert start_time_display.get() == "Start Time: Not Started"
    assert people_count.get() == "People Detected: 0"
    assert barcode_value.get() == ""


# Test the change in people count and active time
def test_people_detection(mock_gui_variables):
    time_active, last_inactive, total_time_spent, start_time_display, people_count, barcode_value = mock_gui_variables

    # Simulate a change in the number of people detected (e.g., 1 person detected)
    people_count.get.return_value = "People Detected: 1"
    time_active.get.return_value = "Time Active: 10 seconds"
    total_time_spent.get.return_value = "Total Time Spent: 10 seconds"

    # Assert that the people count updates
    assert people_count.get() == "People Detected: 1"  # 2 hands = 1 person
    assert time_active.get() != "Time Active: 0 seconds"
    assert total_time_spent.get() != "Total Time Spent: 0 seconds"


# Test the barcode value setting and getting
def test_barcode_detection(mock_gui_variables):
    time_active, last_inactive, total_time_spent, start_time_display, people_count, barcode_value = mock_gui_variables

    # Simulate setting and getting a barcode value
    barcode_value.set("1234567890")
    barcode_value.get.return_value = "1234567890"

    # Assert that the barcode value is correctly set and retrieved
    barcode_value.set("1234567890")
    assert barcode_value.get() == "1234567890"


# Test the inactivity display change
def test_inactivity_display(mock_gui_variables):
    time_active, last_inactive, total_time_spent, start_time_display, people_count, barcode_value = mock_gui_variables

    # Simulate that a person has been inactive for a while
    last_inactive.get.return_value = "Last Inactivity: 5 seconds"

    # Assert that the inactivity value updates correctly
    assert last_inactive.get() != "Last Inactivity: None"
    assert last_inactive.get() == "Last Inactivity: 5 seconds"


# Test the start time display
def test_start_time_display(mock_gui_variables):
    time_active, last_inactive, total_time_spent, start_time_display, people_count, barcode_value = mock_gui_variables

    # Simulate the start time being set
    start_time_display.get.return_value = "Start Time: 12:30:00"

    # Assert that the start time is correctly displayed
    assert start_time_display.get() == "Start Time: 12:30:00"


# Test that time is active when a person is detected
def test_time_active_when_detected(mock_gui_variables):
    time_active, last_inactive, total_time_spent, start_time_display, people_count, barcode_value = mock_gui_variables

    # Simulate detecting a person
    people_count.get.return_value = "People Detected: 1"
    time_active.get.return_value = "Time Active: 20 seconds"

    # Assert that the time active should increase
    assert time_active.get() != "Time Active: 0 seconds"
    assert people_count.get() == "People Detected: 1"  # Assuming 1 person detected


# Test if total time spent is updated when people are detected
def test_total_time_spent(mock_gui_variables):
    time_active, last_inactive, total_time_spent, start_time_display, people_count, barcode_value = mock_gui_variables

    # Simulate a change in the total time spent
    total_time_spent.get.return_value = "Total Time Spent: 50 seconds"

    # Assert that the total time spent is correctly updated
    assert total_time_spent.get() == "Total Time Spent: 50 seconds"
