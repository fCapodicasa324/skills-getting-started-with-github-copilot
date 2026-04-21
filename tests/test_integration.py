"""
Integration tests for complete workflows across multiple endpoints.
"""

import pytest


class TestSignupWorkflow:
    """Integration tests for signup workflows."""
    
    def test_view_activities_then_signup(self, client):
        """Test complete workflow: view activities, then sign up for one."""
        # Step 1: Get all activities
        get_response = client.get("/activities")
        assert get_response.status_code == 200
        initial_data = get_response.json()
        
        activity_name = "Test Activity B"
        initial_count = len(initial_data[activity_name]["participants"])
        
        # Step 2: Sign up for an activity
        email = "participant@test.edu"
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Step 3: Verify the signup by checking activities again
        verify_response = client.get("/activities")
        assert verify_response.status_code == 200
        updated_data = verify_response.json()
        
        # Verify participant count increased and email is in list
        updated_count = len(updated_data[activity_name]["participants"])
        assert updated_count == initial_count + 1
        assert email in updated_data[activity_name]["participants"]
        
    def test_signup_multiple_students(self, client):
        """Test signing up multiple students for the same activity."""
        activity_name = "Test Activity B"
        emails = ["student1@test.edu", "student2@test.edu", "student3@test.edu"]
        
        # Get initial count
        initial_response = client.get("/activities")
        initial_data = initial_response.json()
        initial_count = len(initial_data[activity_name]["participants"])
        
        # Sign up multiple students
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all students were added
        final_response = client.get("/activities")
        final_data = final_response.json()
        
        assert len(final_data[activity_name]["participants"]) == initial_count + len(emails)
        for email in emails:
            assert email in final_data[activity_name]["participants"]


class TestUnregisterWorkflow:
    """Integration tests for unregister workflows."""
    
    def test_signup_then_unregister(self, client):
        """Test complete workflow: sign up, then unregister."""
        activity_name = "Test Activity B"
        email = "temporary@test.edu"
        
        # Step 1: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        check_response = client.get("/activities")
        check_data = check_response.json()
        assert email in check_data[activity_name]["participants"]
        
        # Step 2: Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Step 3: Verify unregister
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        assert email not in verify_data[activity_name]["participants"]
        
    def test_signup_and_unregister_multiple(self, client):
        """Test signing up and unregistering multiple students."""
        activity_name = "Test Activity B"
        emails = ["user1@test.edu", "user2@test.edu"]
        
        # Sign up multiple students
        for email in emails:
            client.post(f"/activities/{activity_name}/signup?email={email}")
        
        # Verify all signed up
        check_response = client.get("/activities")
        check_data = check_response.json()
        for email in emails:
            assert email in check_data[activity_name]["participants"]
        
        # Unregister first student
        client.delete(f"/activities/{activity_name}/unregister?email={emails[0]}")
        
        # Verify first student removed but second still registered
        verify_response = client.get("/activities")
        verify_data = verify_response.json()
        assert emails[0] not in verify_data[activity_name]["participants"]
        assert emails[1] in verify_data[activity_name]["participants"]


class TestConcurrentOperations:
    """Integration tests for multiple concurrent-like operations."""
    
    def test_signup_across_multiple_activities(self, client):
        """Test signing up the same student for multiple activities."""
        email = "versatile@test.edu"
        activities = ["Test Activity A", "Test Activity B"]
        
        # Sign up for multiple activities
        for activity in activities:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify registration in all activities
        get_response = client.get("/activities")
        data = get_response.json()
        
        for activity in activities:
            assert email in data[activity]["participants"]
            
    def test_full_activity_lifecycle(self, client):
        """Test a complete lifecycle: sign up multiple, then unregister all."""
        activity_name = "Test Activity B"  # Empty activity
        emails = ["person1@test.edu", "person2@test.edu", "person3@test.edu"]
        
        # Step 1: Sign up all students
        for email in emails:
            response = client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Step 2: Verify all signed up
        check1 = client.get("/activities").json()
        for email in emails:
            assert email in check1[activity_name]["participants"]
        initial_count = len(check1[activity_name]["participants"])
        
        # Step 3: Unregister all students
        for email in emails:
            response = client.delete(
                f"/activities/{activity_name}/unregister?email={email}"
            )
            assert response.status_code == 200
        
        # Step 4: Verify all unregistered
        check2 = client.get("/activities").json()
        final_count = len(check2[activity_name]["participants"])
        
        assert final_count == initial_count - len(emails)
        for email in emails:
            assert email not in check2[activity_name]["participants"]


class TestEdgeCases:
    """Integration tests for edge cases and error handling."""
    
    def test_signup_then_invalid_unregister(self, client):
        """Test attempting to unregister with wrong email after signup."""
        activity = "Test Activity B"
        correct_email = "correct@test.edu"
        wrong_email = "wrong@test.edu"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={correct_email}")
        
        # Try to unregister with wrong email
        response = client.delete(
            f"/activities/{activity}/unregister?email={wrong_email}"
        )
        
        assert response.status_code == 400
        
        # Verify correct email still registered
        check = client.get("/activities").json()
        assert correct_email in check[activity]["participants"]
        
    def test_unregister_then_reregister(self, client):
        """Test unregistering and then re-registering for the same activity."""
        activity = "Test Activity B"
        email = "flaky@test.edu"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Unregister
        response1 = client.delete(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert response1.status_code == 200
        
        # Re-register
        response2 = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert response2.status_code == 200
        
        # Verify re-registered
        check = client.get("/activities").json()
        assert email in check[activity]["participants"]
