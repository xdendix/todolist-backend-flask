import pytest
import json
from datetime import datetime, date
from todo_app.models import Todo


@pytest.fixture
def sample_todo_data():
    """Sample data for creating a todo."""
    return {
        "judul": "Test Todo",
        "prioritas": "High",
        "status": False,
        "deadline": "2025-12-31"
    }


class TestTodoRoutes:
    """Test cases for Todo API routes."""

    def test_list_todos_empty(self, client):
        """Test listing todos when database is empty."""
        response = client.get("/api/todos/")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["count"] == 0
        assert data["data"] == []
        assert "pagination" in data

    def test_create_todo_success(self, client, sample_todo_data):
        """Test creating a todo successfully."""
        response = client.post(
            "/api/todos/",
            data=json.dumps(sample_todo_data),
            content_type="application/json"
        )
        assert response.status_code == 201

        data = json.loads(response.data)
        assert "id" in data
        assert data["judul"] == sample_todo_data["judul"]
        assert data["prioritas"] == sample_todo_data["prioritas"]
        assert data["status"] == sample_todo_data["status"]
        assert data["deadline"] == sample_todo_data["deadline"]

    def test_create_todo_duplicate_title(self, client, sample_todo_data):
        """Test creating a todo with duplicate title."""
        # Create first todo
        client.post(
            "/api/todos/",
            data=json.dumps(sample_todo_data),
            content_type="application/json"
        )

        # Try to create duplicate
        response = client.post(
            "/api/todos/",
            data=json.dumps(sample_todo_data),
            content_type="application/json"
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "message" in data
        assert "sudah ada" in data["message"]

    def test_create_todo_invalid_data(self, client):
        """Test creating a todo with invalid data."""
        invalid_data = {"judul": ""}  # Empty title

        response = client.post(
            "/api/todos/",
            data=json.dumps(invalid_data),
            content_type="application/json"
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "judul" in data

    def test_create_todo_no_data(self, client):
        """Test creating a todo with no data."""
        response = client.post("/api/todos/", content_type="application/json")
        assert response.status_code == 400

        # Our middleware converts the error to JSON response
        data = json.loads(response.data)
        assert data["success"] is False
        assert "Invalid JSON format" in data["message"] or "No input provided" in data["message"]

    def test_get_todo_by_id(self, client, sample_todo_data):
        """Test getting a todo by ID."""
        # Create a todo first
        create_response = client.post(
            "/api/todos/",
            data=json.dumps(sample_todo_data),
            content_type="application/json"
        )
        create_data = json.loads(create_response.data)
        todo_id = create_data["id"]

        # Get the todo
        response = client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["id"] == todo_id
        assert data["judul"] == sample_todo_data["judul"]

    def test_get_todo_not_found(self, client):
        """Test getting a non-existent todo."""
        response = client.get("/api/todos/999")
        assert response.status_code == 404

    def test_update_todo_success(self, client, sample_todo_data):
        """Test updating a todo successfully."""
        # Create a todo first
        create_response = client.post(
            "/api/todos/",
            data=json.dumps(sample_todo_data),
            content_type="application/json"
        )
        create_data = json.loads(create_response.data)
        todo_id = create_data["id"]

        # Update the todo
        update_data = {"judul": "Updated Title", "status": True}
        response = client.put(
            f"/api/todos/{todo_id}",
            data=json.dumps(update_data),
            content_type="application/json"
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["judul"] == "Updated Title"
        assert data["status"] is True

    def test_update_todo_no_data(self, client, sample_todo_data):
        """Test updating a todo with no data."""
        # Create a todo first
        create_response = client.post(
            "/api/todos/",
            data=json.dumps(sample_todo_data),
            content_type="application/json"
        )
        create_data = json.loads(create_response.data)
        todo_id = create_data["id"]

        # Try to update with empty data
        response = client.put(
            f"/api/todos/{todo_id}",
            data=json.dumps({}),
            content_type="application/json"
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert "message" in data

    def test_update_todo_not_found(self, client):
        """Test updating a non-existent todo."""
        update_data = {"judul": "Updated Title"}
        response = client.put(
            "/api/todos/999",
            data=json.dumps(update_data),
            content_type="application/json"
        )
        assert response.status_code == 404

    def test_delete_todo_success(self, client, sample_todo_data):
        """Test deleting a todo successfully."""
        # Create a todo first
        create_response = client.post(
            "/api/todos/",
            data=json.dumps(sample_todo_data),
            content_type="application/json"
        )
        create_data = json.loads(create_response.data)
        todo_id = create_data["id"]

        # Delete the todo
        response = client.delete(f"/api/todos/{todo_id}")
        assert response.status_code == 204

        # Verify it's deleted
        get_response = client.get(f"/api/todos/{todo_id}")
        assert get_response.status_code == 404

    def test_delete_todo_not_found(self, client):
        """Test deleting a non-existent todo."""
        response = client.delete("/api/todos/999")
        assert response.status_code == 404

    def test_search_todos_by_keyword(self, client):
        """Test searching todos by keyword."""
        # Create multiple todos
        todos_data = [
            {"judul": "Learn Python", "prioritas": "High", "status": False},
            {"judul": "Learn Flask", "prioritas": "Medium", "status": False},
            {"judul": "Learn JavaScript", "prioritas": "Low", "status": True},
        ]

        for todo_data in todos_data:
            client.post(
                "/api/todos/",
                data=json.dumps(todo_data),
                content_type="application/json"
            )

        # Search for "Learn"
        response = client.get("/api/todos/search?q=Learn")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["count"] == 3

    def test_search_todos_by_priority(self, client):
        """Test searching todos by priority."""
        # Create todos with different priorities
        todos_data = [
            {"judul": "High Priority Task", "prioritas": "High", "status": False},
            {"judul": "Medium Priority Task", "prioritas": "Medium", "status": False},
            {"judul": "Low Priority Task", "prioritas": "Low", "status": False},
        ]

        for todo_data in todos_data:
            client.post(
                "/api/todos/",
                data=json.dumps(todo_data),
                content_type="application/json"
            )

        # Search for High priority
        response = client.get("/api/todos/search?prioritas=High")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["count"] == 1
        assert data["data"][0]["prioritas"] == "High"

    def test_search_todos_by_status(self, client):
        """Test searching todos by status."""
        # Create todos with different statuses
        todos_data = [
            {"judul": "Completed Task", "prioritas": "High", "status": True},
            {"judul": "Pending Task 1", "prioritas": "Medium", "status": False},
            {"judul": "Pending Task 2", "prioritas": "Low", "status": False},
        ]

        for todo_data in todos_data:
            client.post(
                "/api/todos/",
                data=json.dumps(todo_data),
                content_type="application/json"
            )

        # Search for completed tasks
        response = client.get("/api/todos/search?status=selesai")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["count"] == 1
        assert data["data"][0]["status"] is True

    def test_search_todos_by_deadline_range(self, client):
        """Test searching todos by deadline range."""
        # Create todos with different deadlines
        todos_data = [
            {"judul": "Task 1", "prioritas": "High", "status": False, "deadline": "2025-01-15"},
            {"judul": "Task 2", "prioritas": "Medium", "status": False, "deadline": "2025-06-15"},
            {"judul": "Task 3", "prioritas": "Low", "status": False, "deadline": "2025-12-15"},
        ]

        for todo_data in todos_data:
            client.post(
                "/api/todos/",
                data=json.dumps(todo_data),
                content_type="application/json"
            )

        # Search for tasks between 2025-03-01 and 2025-09-01
        response = client.get("/api/todos/search?deadline_from=2025-03-01&deadline_to=2025-09-01")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["count"] == 1
        assert data["data"][0]["judul"] == "Task 2"

    def test_list_todos_pagination(self, client):
        """Test pagination in list todos."""
        # Create multiple todos
        for i in range(15):
            todo_data = {
                "judul": f"Todo {i+1}",
                "prioritas": "High",
                "status": False
            }
            client.post(
                "/api/todos/",
                data=json.dumps(todo_data),
                content_type="application/json"
            )

        # Get first page with 10 items per page
        response = client.get("/api/todos/?page=1&per_page=10")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["success"] is True
        assert data["count"] == 10
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 10
        assert data["pagination"]["total"] == 15
        assert data["pagination"]["pages"] == 2
        assert data["pagination"]["has_next"] is True
        assert data["pagination"]["has_prev"] is False

    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data["status"] == "ok"
