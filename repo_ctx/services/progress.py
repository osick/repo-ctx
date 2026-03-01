"""Progress tracking service for real-time progress reporting.

This module provides progress tracking for long-running operations
like indexing and analysis, with support for callbacks and event streaming.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Callable, Optional

logger = logging.getLogger("repo_ctx.services.progress")


@dataclass
class ProgressTracker:
    """Tracks progress of a long-running task.

    Supports synchronous and asynchronous updates, callbacks, and event streaming.
    """

    task_id: str
    task_type: str
    total_steps: int
    current_step: int = 0
    message: str = ""
    status: str = "pending"  # pending, in_progress, completed, failed
    error: Optional[str] = None
    result: Optional[dict[str, Any]] = None
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    on_progress: Optional[Callable] = None
    _event_queue: asyncio.Queue = field(default_factory=lambda: asyncio.Queue())

    @property
    def progress(self) -> float:
        """Get progress as a float between 0.0 and 1.0."""
        if self.status == "completed":
            return 1.0
        if self.total_steps == 0:
            return 0.0
        return min(1.0, self.current_step / self.total_steps)

    def update(
        self,
        step: Optional[int] = None,
        message: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Update progress synchronously.

        Args:
            step: New current step (or None to keep current).
            message: Progress message.
            metadata: Additional metadata to merge.
        """
        if step is not None:
            self.current_step = step
        if message is not None:
            self.message = message
        if metadata is not None:
            self.metadata.update(metadata)

        self.status = "in_progress"
        self.updated_at = datetime.now()

        # Queue event for streaming
        try:
            self._event_queue.put_nowait(self.to_dict())
        except asyncio.QueueFull:
            pass  # Drop event if queue is full

    async def update_async(
        self,
        step: Optional[int] = None,
        message: Optional[str] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Update progress asynchronously with callback.

        Args:
            step: New current step (or None to keep current).
            message: Progress message.
            metadata: Additional metadata to merge.
        """
        self.update(step=step, message=message, metadata=metadata)

        # Call callback if provided
        if self.on_progress is not None:
            try:
                result = self.on_progress(self.to_dict())
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.warning(f"Progress callback error: {e}")

    def increment(self, message: Optional[str] = None) -> None:
        """Increment progress by one step.

        Args:
            message: Optional progress message.
        """
        self.update(step=self.current_step + 1, message=message)

    async def increment_async(self, message: Optional[str] = None) -> None:
        """Increment progress by one step asynchronously.

        Args:
            message: Optional progress message.
        """
        await self.update_async(step=self.current_step + 1, message=message)

    def complete(
        self,
        result: Optional[dict[str, Any]] = None,
        message: str = "Completed",
    ) -> None:
        """Mark task as completed.

        Args:
            result: Result data.
            message: Completion message.
        """
        self.status = "completed"
        self.current_step = self.total_steps
        self.message = message
        self.result = result
        self.updated_at = datetime.now()

        # Queue final event
        try:
            self._event_queue.put_nowait(self.to_dict())
        except asyncio.QueueFull:
            pass

    def fail(self, error: str, message: str = "Failed") -> None:
        """Mark task as failed.

        Args:
            error: Error description.
            message: Failure message.
        """
        self.status = "failed"
        self.error = error
        self.message = message
        self.updated_at = datetime.now()

        # Queue final event
        try:
            self._event_queue.put_nowait(self.to_dict())
        except asyncio.QueueFull:
            pass

    def to_dict(self) -> dict[str, Any]:
        """Convert progress to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "total_steps": self.total_steps,
            "current_step": self.current_step,
            "progress": self.progress,
            "message": self.message,
            "status": self.status,
            "error": self.error,
            "result": self.result,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }


class ProgressRegistry:
    """Registry for managing progress trackers.

    Provides task creation, retrieval, and event streaming.
    """

    def __init__(self) -> None:
        """Initialize the progress registry."""
        self._tasks: dict[str, ProgressTracker] = {}

    def create_task(
        self,
        task_type: str,
        total_steps: int,
        metadata: Optional[dict[str, Any]] = None,
        on_progress: Optional[Callable] = None,
    ) -> ProgressTracker:
        """Create a new progress task.

        Args:
            task_type: Type of task (e.g., "indexing", "analysis").
            total_steps: Total number of steps.
            metadata: Additional metadata.
            on_progress: Optional callback for progress updates.

        Returns:
            Created ProgressTracker.
        """
        task_id = str(uuid.uuid4())
        tracker = ProgressTracker(
            task_id=task_id,
            task_type=task_type,
            total_steps=total_steps,
            metadata=metadata or {},
            on_progress=on_progress,
        )
        self._tasks[task_id] = tracker
        return tracker

    def get_task(self, task_id: str) -> Optional[ProgressTracker]:
        """Get a task by ID.

        Args:
            task_id: Task identifier.

        Returns:
            ProgressTracker or None if not found.
        """
        return self._tasks.get(task_id)

    def get_all_tasks(self) -> list[ProgressTracker]:
        """Get all tasks.

        Returns:
            List of all progress trackers.
        """
        return list(self._tasks.values())

    def remove_task(self, task_id: str) -> bool:
        """Remove a task.

        Args:
            task_id: Task identifier.

        Returns:
            True if removed, False if not found.
        """
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def cleanup_completed(self, max_age_seconds: int = 3600) -> int:
        """Remove completed and failed tasks older than max_age.

        Args:
            max_age_seconds: Maximum age in seconds (default 1 hour).

        Returns:
            Number of tasks removed.
        """
        now = datetime.now()
        to_remove = []

        for task_id, tracker in self._tasks.items():
            if tracker.status in ("completed", "failed"):
                age = (now - tracker.updated_at).total_seconds()
                if age > max_age_seconds:
                    to_remove.append(task_id)

        for task_id in to_remove:
            del self._tasks[task_id]

        return len(to_remove)

    async def stream_events(
        self,
        task_id: str,
        timeout: float = 30.0,
        poll_interval: float = 0.5,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stream progress events for a task.

        Args:
            task_id: Task identifier.
            timeout: Maximum time to wait between events.
            poll_interval: Interval for polling task state.

        Yields:
            Progress update dictionaries.
        """
        tracker = self.get_task(task_id)
        if tracker is None:
            return

        # Yield initial state
        yield tracker.to_dict()

        # Stream updates until completed/failed
        while tracker.status not in ("completed", "failed"):
            try:
                # Try to get event from queue
                event = await asyncio.wait_for(
                    tracker._event_queue.get(),
                    timeout=poll_interval,
                )
                yield event
            except asyncio.TimeoutError:
                # Poll current state
                yield tracker.to_dict()


# Global registry instance
_global_registry: Optional[ProgressRegistry] = None


def get_progress_registry() -> ProgressRegistry:
    """Get the global progress registry.

    Returns:
        Global ProgressRegistry instance.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ProgressRegistry()
    return _global_registry


def reset_progress_registry() -> None:
    """Reset the global progress registry (for testing)."""
    global _global_registry
    _global_registry = None
