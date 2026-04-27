class TestGetActivities:

    def test_returns_all_activities(self, client):
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data

    def test_activities_include_required_fields(self, client):
        # Act
        response = client.get("/activities")

        # Assert
        for activity in response.json().values():
            assert "description" in activity
            assert "schedule" in activity
            assert "max_participants" in activity
            assert "participants" in activity


class TestSignupForActivity:

    def test_signup_adds_student_to_activity(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        participants = client.get("/activities").json()[activity]["participants"]
        assert email in participants

    def test_signup_returns_confirmation_message(self, client):
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]

    def test_signup_duplicate_is_rejected(self, client):
        # Arrange
        email = "michael@mergington.edu"  # already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_unknown_activity_returns_404(self, client):
        # Arrange
        email = "student@mergington.edu"
        activity = "Unknown Activity"

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_full_activity_is_rejected(self, client):
        # Arrange
        activity = "Tennis Club"  # max_participants: 10, currently has 2
        for i in range(8):
            client.post(f"/activities/{activity}/signup", params={"email": f"fill{i}@mergington.edu"})

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": "late@mergington.edu"})

        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_student_can_join_multiple_activities(self, client):
        # Arrange
        email = "active@mergington.edu"

        # Act
        response1 = client.post("/activities/Chess Club/signup", params={"email": email})
        response2 = client.post("/activities/Drama Club/signup", params={"email": email})

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        data = client.get("/activities").json()
        assert email in data["Chess Club"]["participants"]
        assert email in data["Drama Club"]["participants"]


class TestRemoveFromActivity:

    def test_remove_unenrolls_student(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/remove", params={"email": email})

        # Assert
        assert response.status_code == 200
        participants = client.get("/activities").json()[activity]["participants"]
        assert email not in participants

    def test_remove_returns_confirmation_message(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/remove", params={"email": email})

        # Assert
        assert "Removed" in response.json()["message"]
        assert email in response.json()["message"]

    def test_remove_unenrolled_student_returns_400(self, client):
        # Arrange
        email = "nothere@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(f"/activities/{activity}/remove", params={"email": email})

        # Assert
        assert response.status_code == 400
        assert "not enrolled" in response.json()["detail"].lower()

    def test_remove_unknown_activity_returns_404(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Unknown Activity"

        # Act
        response = client.post(f"/activities/{activity}/remove", params={"email": email})

        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_student_can_rejoin_after_removal(self, client):
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"
        client.post(f"/activities/{activity}/remove", params={"email": email})

        # Act
        response = client.post(f"/activities/{activity}/signup", params={"email": email})

        # Assert
        assert response.status_code == 200
        participants = client.get("/activities").json()[activity]["participants"]
        assert email in participants
