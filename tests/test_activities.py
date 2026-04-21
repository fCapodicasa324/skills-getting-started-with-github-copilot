"""
Tests for the GET /activities endpoint.
"""

import pytest


class TestGetActivities:
    """Test suite for retrieving activities."""
    
    def test_get_all_activities(self, client):
        """Test that GET /activities returns all activities."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify we get a dict of activities
        assert isinstance(data, dict)
        assert len(data) == 3
        
    def test_activities_structure(self, client):
        """Test that activities have the correct structure."""
        response = client.get("/activities")
        data = response.json()
        
        # Check each activity has required fields
        for activity_name, activity_details in data.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            
    def test_participants_format(self, client):
        """Test that participants are stored as a list of emails."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            participants = activity_details["participants"]
            assert isinstance(participants, list)
            
            # If there are participants, verify they look like emails
            for participant in participants:
                assert isinstance(participant, str)
                assert "@" in participant
                
    def test_activity_details_types(self, client):
        """Test that activity fields have correct data types."""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_details in data.items():
            assert isinstance(activity_details["description"], str)
            assert isinstance(activity_details["schedule"], str)
            assert isinstance(activity_details["max_participants"], int)
            assert activity_details["max_participants"] > 0
            assert isinstance(activity_details["participants"], list)
