"""Tests for real-time progress reporting.

These tests verify:
- Progress tracker creation and management
- Progress updates and callbacks
- SSE endpoint for real-time updates
- Progress integration with services
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime


class TestProgressTracker:
    """Tests for ProgressTracker class."""

    def test_create_progress_tracker(self):
        """Test creating a progress tracker."""
        from repo_ctx.services.progress import ProgressTracker

        tracker = ProgressTracker(
            task_id="test-123",
            task_type="indexing",
            total_steps=10,
        )

        assert tracker.task_id == "test-123"
        assert tracker.task_type == "indexing"
        assert tracker.total_steps == 10
        assert tracker.current_step == 0
        assert tracker.progress == 0.0

    def test_progress_tracker_update(self):
        """Test updating progress."""
        from repo_ctx.services.progress import ProgressTracker

        tracker = ProgressTracker(
            task_id="test-123",
            task_type="indexing",
            total_steps=10,
        )

        tracker.update(step=5, message="Processing files")

        assert tracker.current_step == 5
        assert tracker.progress == 0.5
        assert tracker.message == "Processing files"

    def test_progress_tracker_increment(self):
        """Test incrementing progress."""
        from repo_ctx.services.progress import ProgressTracker

        tracker = ProgressTracker(
            task_id="test-123",
            task_type="indexing",
            total_steps=5,
        )

        tracker.increment()
        assert tracker.current_step == 1
        assert tracker.progress == 0.2

        tracker.increment()
        assert tracker.current_step == 2
        assert tracker.progress == 0.4

    def test_progress_tracker_complete(self):
        """Test marking progress as complete."""
        from repo_ctx.services.progress import ProgressTracker

        tracker = ProgressTracker(
            task_id="test-123",
            task_type="indexing",
            total_steps=10,
        )

        tracker.complete(result={"documents": 50})

        assert tracker.status == "completed"
        assert tracker.progress == 1.0
        assert tracker.result == {"documents": 50}

    def test_progress_tracker_fail(self):
        """Test marking progress as failed."""
        from repo_ctx.services.progress import ProgressTracker

        tracker = ProgressTracker(
            task_id="test-123",
            task_type="indexing",
            total_steps=10,
        )

        tracker.fail(error="Connection timeout")

        assert tracker.status == "failed"
        assert tracker.error == "Connection timeout"

    def test_progress_tracker_to_dict(self):
        """Test converting progress to dictionary."""
        from repo_ctx.services.progress import ProgressTracker

        tracker = ProgressTracker(
            task_id="test-123",
            task_type="indexing",
            total_steps=10,
        )
        tracker.update(step=5, message="In progress")

        data = tracker.to_dict()

        assert data["task_id"] == "test-123"
        assert data["task_type"] == "indexing"
        assert data["total_steps"] == 10
        assert data["current_step"] == 5
        assert data["progress"] == 0.5
        assert data["message"] == "In progress"
        assert data["status"] == "in_progress"


class TestProgressRegistry:
    """Tests for ProgressRegistry class."""

    def test_create_registry(self):
        """Test creating a progress registry."""
        from repo_ctx.services.progress import ProgressRegistry

        registry = ProgressRegistry()
        assert registry is not None

    def test_register_task(self):
        """Test registering a new task."""
        from repo_ctx.services.progress import ProgressRegistry

        registry = ProgressRegistry()
        tracker = registry.create_task(
            task_type="indexing",
            total_steps=10,
            metadata={"repository": "owner/repo"},
        )

        assert tracker.task_id is not None
        assert tracker.task_type == "indexing"
        assert tracker.total_steps == 10

    def test_get_task(self):
        """Test getting a task by ID."""
        from repo_ctx.services.progress import ProgressRegistry

        registry = ProgressRegistry()
        created = registry.create_task(task_type="indexing", total_steps=10)
        retrieved = registry.get_task(created.task_id)

        assert retrieved is not None
        assert retrieved.task_id == created.task_id

    def test_get_nonexistent_task(self):
        """Test getting a task that doesn't exist."""
        from repo_ctx.services.progress import ProgressRegistry

        registry = ProgressRegistry()
        retrieved = registry.get_task("nonexistent-id")

        assert retrieved is None

    def test_get_all_tasks(self):
        """Test getting all tasks."""
        from repo_ctx.services.progress import ProgressRegistry

        registry = ProgressRegistry()
        registry.create_task(task_type="indexing", total_steps=10)
        registry.create_task(task_type="analysis", total_steps=5)

        tasks = registry.get_all_tasks()

        assert len(tasks) == 2

    def test_remove_task(self):
        """Test removing a task."""
        from repo_ctx.services.progress import ProgressRegistry

        registry = ProgressRegistry()
        tracker = registry.create_task(task_type="indexing", total_steps=10)
        registry.remove_task(tracker.task_id)

        retrieved = registry.get_task(tracker.task_id)
        assert retrieved is None

    def test_cleanup_completed_tasks(self):
        """Test cleaning up completed tasks."""
        from repo_ctx.services.progress import ProgressRegistry

        registry = ProgressRegistry()
        tracker1 = registry.create_task(task_type="indexing", total_steps=10)
        tracker2 = registry.create_task(task_type="analysis", total_steps=5)

        tracker1.complete()
        tracker2.update(step=3)

        registry.cleanup_completed(max_age_seconds=0)

        assert registry.get_task(tracker1.task_id) is None
        assert registry.get_task(tracker2.task_id) is not None


class TestProgressCallbacks:
    """Tests for progress callbacks."""

    @pytest.mark.asyncio
    async def test_progress_callback(self):
        """Test that progress callbacks are called."""
        from repo_ctx.services.progress import ProgressTracker

        callback_called = False
        callback_data = {}

        async def on_progress(progress_data):
            nonlocal callback_called, callback_data
            callback_called = True
            callback_data = progress_data

        tracker = ProgressTracker(
            task_id="test-123",
            task_type="indexing",
            total_steps=10,
            on_progress=on_progress,
        )

        await tracker.update_async(step=5, message="Processing")

        assert callback_called
        assert callback_data["current_step"] == 5
        assert callback_data["message"] == "Processing"

    @pytest.mark.asyncio
    async def test_multiple_callbacks(self):
        """Test multiple callbacks."""
        from repo_ctx.services.progress import ProgressTracker

        call_count = 0

        async def on_progress(progress_data):
            nonlocal call_count
            call_count += 1

        tracker = ProgressTracker(
            task_id="test-123",
            task_type="indexing",
            total_steps=5,
            on_progress=on_progress,
        )

        for i in range(5):
            await tracker.increment_async()

        assert call_count == 5


class TestProgressEvents:
    """Tests for progress event stream."""

    @pytest.mark.asyncio
    async def test_progress_event_generator(self):
        """Test progress event generator."""
        from repo_ctx.services.progress import ProgressTracker, ProgressRegistry

        registry = ProgressRegistry()
        tracker = registry.create_task(task_type="indexing", total_steps=3)

        # Collect events in background
        events = []

        async def collect_events():
            async for event in registry.stream_events(tracker.task_id, timeout=1.0):
                events.append(event)
                if event.get("status") == "completed":
                    break

        # Run collection task
        task = asyncio.create_task(collect_events())

        # Update progress
        await asyncio.sleep(0.1)
        tracker.update(step=1)
        await asyncio.sleep(0.1)
        tracker.update(step=2)
        await asyncio.sleep(0.1)
        tracker.complete()

        # Wait for collection
        try:
            await asyncio.wait_for(task, timeout=3.0)
        except asyncio.TimeoutError:
            pass

        # Verify we got events
        assert len(events) >= 1


class TestProgressAPI:
    """Tests for progress API endpoints."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits
        from fastapi.testclient import TestClient

        configure_auth(api_key=None, rate_limit_enabled=False)
        reset_rate_limits()

        return TestClient(app)

    def test_progress_endpoints_in_openapi(self, client):
        """Test that progress endpoints are in OpenAPI schema."""
        response = client.get("/openapi.json")
        data = response.json()

        assert "/v1/progress/tasks" in data["paths"]
        assert "/v1/progress/tasks/{task_id}" in data["paths"]

    def test_list_progress_tasks(self, client):
        """Test listing progress tasks."""
        response = client.get("/v1/progress/tasks")

        assert response.status_code == 200
        data = response.json()
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

    def test_get_progress_task_not_found(self, client):
        """Test getting nonexistent task."""
        response = client.get("/v1/progress/tasks/nonexistent-id")

        assert response.status_code == 404

    def test_create_progress_task(self, client):
        """Test creating a progress task."""
        response = client.post(
            "/v1/progress/tasks",
            json={
                "task_type": "indexing",
                "total_steps": 10,
                "metadata": {"repository": "owner/repo"},
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        assert data["task_type"] == "indexing"
        assert data["total_steps"] == 10

    def test_update_progress_task(self, client):
        """Test updating a progress task."""
        # Create task
        create_response = client.post(
            "/v1/progress/tasks",
            json={"task_type": "indexing", "total_steps": 10},
        )
        task_id = create_response.json()["task_id"]

        # Update task
        response = client.patch(
            f"/v1/progress/tasks/{task_id}",
            json={"current_step": 5, "message": "Processing"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["current_step"] == 5
        assert data["message"] == "Processing"

    def test_complete_progress_task(self, client):
        """Test completing a progress task."""
        # Create task
        create_response = client.post(
            "/v1/progress/tasks",
            json={"task_type": "indexing", "total_steps": 10},
        )
        task_id = create_response.json()["task_id"]

        # Complete task
        response = client.post(
            f"/v1/progress/tasks/{task_id}/complete",
            json={"result": {"documents": 50}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"

    def test_fail_progress_task(self, client):
        """Test failing a progress task."""
        # Create task
        create_response = client.post(
            "/v1/progress/tasks",
            json={"task_type": "indexing", "total_steps": 10},
        )
        task_id = create_response.json()["task_id"]

        # Fail task
        response = client.post(
            f"/v1/progress/tasks/{task_id}/fail",
            json={"error": "Connection timeout"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "failed"
        assert data["error"] == "Connection timeout"

    def test_delete_progress_task(self, client):
        """Test deleting a progress task."""
        # Create task
        create_response = client.post(
            "/v1/progress/tasks",
            json={"task_type": "indexing", "total_steps": 10},
        )
        task_id = create_response.json()["task_id"]

        # Delete task
        response = client.delete(f"/v1/progress/tasks/{task_id}")

        assert response.status_code == 200

        # Verify deleted
        get_response = client.get(f"/v1/progress/tasks/{task_id}")
        assert get_response.status_code == 404


class TestProgressSSE:
    """Tests for Server-Sent Events endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        from repo_ctx.api import app
        from repo_ctx.api.auth import configure_auth, reset_rate_limits
        from fastapi.testclient import TestClient

        configure_auth(api_key=None, rate_limit_enabled=False)
        reset_rate_limits()

        return TestClient(app)

    def test_sse_endpoint_in_openapi(self, client):
        """Test that SSE endpoint is documented."""
        response = client.get("/openapi.json")
        data = response.json()

        # SSE endpoint should be in paths
        assert "/v1/progress/stream/{task_id}" in data["paths"]

    def test_sse_stream_invalid_task(self, client):
        """Test SSE stream for invalid task returns 404."""
        # Note: TestClient doesn't support streaming well,
        # so we just test that the endpoint exists
        response = client.get("/v1/progress/stream/nonexistent-id")

        # Should return 404 for nonexistent task
        assert response.status_code == 404


class TestProgressIntegration:
    """Tests for progress integration with services."""

    def test_indexing_with_progress(self):
        """Test that indexing can report progress."""
        from repo_ctx.services.progress import ProgressTracker

        tracker = ProgressTracker(
            task_id="indexing-123",
            task_type="indexing",
            total_steps=100,
        )

        # Simulate indexing steps
        tracker.update(step=0, message="Starting indexing")
        tracker.update(step=10, message="Fetching repository info")
        tracker.update(step=30, message="Processing files")
        tracker.update(step=80, message="Generating embeddings")
        tracker.complete(result={"files": 50, "embeddings": 50})

        assert tracker.status == "completed"
        assert tracker.progress == 1.0

    def test_analysis_with_progress(self):
        """Test that analysis can report progress."""
        from repo_ctx.services.progress import ProgressTracker

        tracker = ProgressTracker(
            task_id="analysis-456",
            task_type="analysis",
            total_steps=50,
        )

        # Simulate analysis steps
        tracker.update(step=0, message="Starting analysis")
        for i in range(1, 51):
            tracker.update(step=i, message=f"Analyzing file {i}/50")

        tracker.complete(result={"symbols": 200, "dependencies": 150})

        assert tracker.status == "completed"
        assert tracker.result["symbols"] == 200
