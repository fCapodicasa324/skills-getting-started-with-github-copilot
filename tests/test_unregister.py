"""
Tests for the DELETE /activities/{activity_name}/unregister endpoint.
"""

import pytest


class TestUnregisterFromActivity:
    """Test suite for unregistering from activities."""
    
    def test_successful_unregister(self, client):
        """Test successfully unregistering a student from an activity."""
        response = client.delete(
            "/activities/Test Activity A/unregister?email=alice@test.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "alice@test.edu" in data["message"]
        assert "Test Activity A" in data["message"]
        
    def test_unregister_removes_participant(self, client):
        """Test that unregister actually removes the participant."""
        # Get initial state
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data["Test Activity A"]["participants"])
        assert "alice@test.edu" in initial_data["Test Activity A"]["participants"]
        
        # Unregister
        client.delete("/activities/Test Activity A/unregister?email=alice@test.edu")
        
        # Verify participant was removed
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        updated_count = len(updated_data["Test Activity A"]["participants"])
        
        assert updated_count == initial_count - 1
        assert "alice@test.edu" not in updated_data["Test Activity A"]["participants"]
        
    def test_unregister_nonexistent_activity(self, client):
        """Test that unregistering from a non-existent activity fails."""
        response = client.delete(
            "/activities/Nonexistent Activity/unregister?email=student@test.edu"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
        
    def test_unregister_not_registered_student(self, client):
        """Test that unregistering a student not in the activity fails."""
        response = client.delete(
            "/activities/Test Activity A/unregister?email=notregistered@test.edu"
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]
        
    def test_unregister_updates_availability(self, client):
        """Test that unregister updates availability correctly."""
        # Full Activity has 2 participants, max 2
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_participants = len(initial_data["Full Activity"]["participants"])
        assert initial_participants == 2
        
        # Unregister one student
        client.delete("/activities/Full Activity/unregister?email=bob@test.edu")
        
        # Check updated count
        updated_response = client.get("/activities")
        updated_data = updated_response.json()
        updated_participants = len(updated_data["Full Activity"]["participants"])
        
        assert updated_participants == 1
        assert "bob@test.edu" not in updated_data["Full Activity"]["participants"]
        assert "charlie@test.edu" in updated_data["Full Activity"]["participants"]
        
    def test_unregister_response_format(self, client):
        """Test that unregister response has correct format."""
        response = client.delete(
            "/activities/Test Activity A/unregister?email=alice@test.edu"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "message" in data
        assert isinstance(data["message"], str)
        
    def test_unregister_multiple_times_fails(self, client):
        """Test that unregistering the same student twice fails."""
        email = "alice@test.edu"
        
        # First unregister should succeed
        response1 = client.delete(
            f"/activities/Test Activity A/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            f"/activities/Test Activity A/unregister?email={email}"
        )
        
        assert response2.status_code == 400
        data = response2.json()
        assert "not signed up" in data["detail"]
