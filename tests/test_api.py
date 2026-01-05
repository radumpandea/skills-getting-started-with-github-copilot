import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for the /activities endpoint"""

    def test_get_activities_returns_list(self):
        """Test that /activities returns a list of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_contains_expected_fields(self):
        """Test that activities have required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_has_chess_club(self):
        """Test that Chess Club is in the activities list"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data


class TestSignup:
    """Tests for the signup endpoint"""

    def test_signup_for_available_activity(self):
        """Test signing up for an activity with available spots"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=test@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "test@mergington.edu" in data["message"]

    def test_signup_for_nonexistent_activity(self):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_signup_duplicate_registration(self):
        """Test that duplicate signup is rejected"""
        email = "duplicate@mergington.edu"
        activity = "Soccer%20Club"
        
        # First signup
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Attempt duplicate signup
        response2 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]

    def test_signup_updates_participant_list(self):
        """Test that signup adds participant to the activity"""
        email = "newstudent@mergington.edu"
        activity = "Art%20Club"
        
        # Get initial participant count
        response_before = client.get("/activities")
        participants_before = response_before.json()["Art Club"]["participants"]
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Get updated participant count
        response_after = client.get("/activities")
        participants_after = response_after.json()["Art Club"]["participants"]
        
        assert len(participants_after) == len(participants_before) + 1
        assert email in participants_after


class TestRoot:
    """Tests for the root endpoint"""

    def test_root_redirects(self):
        """Test that / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
