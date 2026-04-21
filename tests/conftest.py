"""
Pytest configuration and fixtures for the API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """
    Provide a TestClient for making HTTP requests to the API.
    """
    return TestClient(app)


@pytest.fixture
def test_activities():
    """
    Provide a clean copy of test activities data.
    Returns a fresh set of activities with minimal participants for testing.
    """
    return {
        "Test Activity A": {
            "description": "A test activity for testing",
            "schedule": "Mondays, 3:00 PM - 4:00 PM",
            "max_participants": 5,
            "participants": ["alice@test.edu"]
        },
        "Test Activity B": {
            "description": "Another test activity",
            "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
            "max_participants": 3,
            "participants": []
        },
        "Full Activity": {
            "description": "Activity at max capacity",
            "schedule": "Wednesdays, 2:00 PM - 3:00 PM",
            "max_participants": 2,
            "participants": ["bob@test.edu", "charlie@test.edu"]
        }
    }


@pytest.fixture(autouse=True)
def reset_activities(test_activities):
    """
    Reset the global activities dictionary before each test to ensure isolation.
    This prevents test data from contaminating other tests.
    """
    # Store the original state
    original_activities = dict(activities)
    
    # Clear and populate with test data
    activities.clear()
    activities.update(test_activities)
    
    yield  # Run the test
    
    # Restore original state
    activities.clear()
    activities.update(original_activities)
