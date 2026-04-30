"""Integration tests for the Mergington High School Activities API.

All tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and state
- Act: Execute the API call
- Assert: Verify the response and state changes
"""

import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities with correct structure."""
        # Arrange
        expected_activity_names = set(activities.keys())

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        returned_activities = response.json()
        assert set(returned_activities.keys()) == expected_activity_names
        
        # Verify structure of an activity
        for activity_name, activity_data in returned_activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_returns_correct_participant_counts(self, client):
        """Test that returned activities show correct participant lists."""
        # Arrange
        chess_club_participants = activities["Chess Club"]["participants"]

        # Act
        response = client.get("/activities")

        # Assert
        returned_activities = response.json()
        assert returned_activities["Chess Club"]["participants"] == chess_club_participants


class TestRoot:
    """Tests for GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Test that GET / redirects to /static/index.html."""
        # Arrange & Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_success_adds_participant(self, client):
        """Test successful signup adds participant to activity."""
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
        assert email in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count + 1

    def test_signup_duplicate_returns_400(self, client):
        """Test signing up twice for same activity returns 400 error."""
        # Arrange
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]  # Use existing participant

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json() == {"detail": "Student already signed up for this activity"}

    def test_signup_nonexistent_activity_returns_404(self, client):
        """Test signing up for non-existent activity returns 404 error."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_signup_multiple_different_activities(self, client):
        """Test a student can sign up for multiple different activities."""
        # Arrange
        email = "student@mergington.edu"
        activities_to_join = ["Chess Club", "Programming Class", "Art Club"]

        # Act & Assert
        for activity_name in activities_to_join:
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
            assert email in activities[activity_name]["participants"]


class TestUnregisterFromActivity:
    """Tests for POST /activities/{activity_name}/unregister endpoint."""

    def test_unregister_success_removes_participant(self, client):
        """Test successful unregister removes participant from activity."""
        # Arrange
        activity_name = "Chess Club"
        email = activities[activity_name]["participants"][0]  # Use existing participant
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
        assert email not in activities[activity_name]["participants"]
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_not_signed_up_returns_400(self, client):
        """Test unregistering someone not signed up returns 400 error."""
        # Arrange
        activity_name = "Chess Club"
        email = "notstudent@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert response.json() == {"detail": "Student not signed up for this activity"}

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test unregistering from non-existent activity returns 404 error."""
        # Arrange
        activity_name = "Nonexistent Club"
        email = "student@mergington.edu"

        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert response.json() == {"detail": "Activity not found"}

    def test_signup_then_unregister_workflow(self, client):
        """Test complete signup and unregister workflow."""
        # Arrange
        activity_name = "Art Club"
        email = "newartstudent@mergington.edu"

        # Act - Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert signup successful
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]

        # Act - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert unregister successful
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]
