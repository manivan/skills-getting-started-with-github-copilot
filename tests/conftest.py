"""Pytest configuration and shared fixtures for API tests."""

import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
from src.app import app, activities


# Store the initial state of activities
INITIAL_ACTIVITIES = deepcopy(activities)


@pytest.fixture
def client():
    """Provide a TestClient instance for making requests to the app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test.
    
    This fixture runs automatically before each test to ensure test isolation.
    """
    # Clear current activities
    activities.clear()
    # Restore initial state
    activities.update(deepcopy(INITIAL_ACTIVITIES))
    yield
    # Cleanup after test (optional, but good practice)
    activities.clear()
    activities.update(deepcopy(INITIAL_ACTIVITIES))
