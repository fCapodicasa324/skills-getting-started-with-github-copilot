"""
Tests for the POST /activities/{activity_name}/signup endpoint.
"""

import pytest


class TestSignupForActivity:
    """Test suite for signing up for activities."""
    
    def test_successful_signup(self, client):
        """Test successfully signing up a new student for an activity."""
        response = client.post(
            "/activities/Test Activity A/signup?email=newstudent@test.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@test.edu" in data["message"]
        assert "Test Activity A" in data["message"]
        
    def test_signup_adds_participant(self, client):
        """Test that signup actually adds the participant to the activity."""
        # Get initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data["Test Activity B"]["participants"])
        
        # Sign up
        client.post("/activities/Test Activity B/signup?email=newstudent@test.edu")
        
        # Verify participant was added
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        updated_count = len(updated_data["Test Activity B"]["participants"])
        
        assert updated_count == initial_count + 1
        assert "newstudent@test.edu" in updated_data["Test Activity B"]["participants"]
        
    def test_duplicate_signup_fails(self, client):
        """Test that signing up twice with the same email fails."""
        email = "existing@test.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/Test Activity B/signup?email={email}"
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            f"/activities/Test Activity B/signup?email={email}"
        )
        
        assert response2.status_code == 400
        data = response2.json()
        assert "already signed up" in data["detail"]
        
    def test_signup_nonexistent_activity(self, client):
        """Test that signing up for a non-existent activity fails."""
        response = client.post(
            "/activities/Nonexistent Activity/signup?email=student@test.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
        
    def test_signup_duplicate_from_initial_data(self, client):
        """Test that signing up with email already in activity fails."""
        response = client.post(
            "/activities/Test Activity A/signup?email=alice@test.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
        
    def test_signup_updates_availability(self, client):
        """Test that signup updates the availability count correctly."""
        # Test Activity A starts with 1 participant, max 5
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_participants = len(initial_data["Test Activity A"]["participants"])
        initial_max = initial_data["Test Activity A"]["max_participants"]
        
        # Sign up a new student
        client.post("/activities/Test Activity A/signup?email=new@test.edu")
        
        # Check updated count
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        updated_participants = len(updated_data["Test Activity A"]["participants"])
        
        assert updated_participants == initial_participants + 1
        assert updated_participants <= initial_max
        
    def test_signup_response_format(self, client):
        """Test that signup response has correct format."""
        response = client.post(
            "/activities/Test Activity B/signup?email=student@test.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)
