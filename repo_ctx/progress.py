"""Progress reporting for long-running operations.

This module provides a callback-based progress reporting system
for operations like repository indexing and code analysis.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Optional
import sys


class ProgressPhase(str, Enum):
    """Phases of progress for an operation."""
    INIT = "init"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"


@dataclass
class ProgressEvent:
    """Represents a progress update event."""
    operation: str
    phase: ProgressPhase
    current: int
    total: int
    message: str = ""
    detail: str = ""
    metadata: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def percent(self) -> float:
        """Get progress as percentage (0-100)."""
        if self.total == 0:
            return 0.0
        return min(100.0, (self.current / self.total) * 100)

    @property
    def is_complete(self) -> bool:
        """Check if operation is complete."""
        return self.phase == ProgressPhase.COMPLETE

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "operation": self.operation,
            "phase": self.phase.value,
            "current": self.current,
            "total": self.total,
            "percent": round(self.percent, 1),
            "message": self.message,
            "detail": self.detail,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
        }


class ProgressCallback(ABC):
    """Abstract base class for progress callbacks."""

    @abstractmethod
    async def on_progress(self, event: ProgressEvent) -> None:
        """Called when progress is updated.

        Args:
            event: The progress event with current state
        """
        pass

    async def report(
        self,
        operation: str,
        phase: ProgressPhase,
        current: int,
        total: int,
        message: str = "",
        detail: str = "",
        **metadata
    ) -> None:
        """Convenience method to report progress.

        Args:
            operation: Name of the operation (e.g., "index_repo", "analyze")
            phase: Current phase (init, processing, complete, error)
            current: Current item number (0-based or 1-based)
            total: Total number of items
            message: Human-readable status message
            detail: Additional detail (e.g., file name being processed)
            **metadata: Additional key-value metadata
        """
        event = ProgressEvent(
            operation=operation,
            phase=phase,
            current=current,
            total=total,
            message=message,
            detail=detail,
            metadata=metadata,
        )
        await self.on_progress(event)


class NoOpProgressCallback(ProgressCallback):
    """Progress callback that does nothing (default)."""

    async def on_progress(self, event: ProgressEvent) -> None:
        """Silently ignore progress events."""
        pass


class PrintProgressCallback(ProgressCallback):
    """Progress callback that prints to console with progress bar."""

    def __init__(
        self,
        output=None,
        show_bar: bool = True,
        bar_width: int = 30,
        show_percent: bool = True,
        show_count: bool = True,
    ):
        """Initialize the print progress callback.

        Args:
            output: Output stream (defaults to sys.stderr)
            show_bar: Whether to show progress bar
            bar_width: Width of progress bar in characters
            show_percent: Whether to show percentage
            show_count: Whether to show item count
        """
        self.output = output or sys.stderr
        self.show_bar = show_bar
        self.bar_width = bar_width
        self.show_percent = show_percent
        self.show_count = show_count
        self._last_operation = None
        self._last_line_length = 0

    def _format_bar(self, percent: float) -> str:
        """Format a progress bar string."""
        filled = int(self.bar_width * percent / 100)
        empty = self.bar_width - filled
        return f"[{'=' * filled}{' ' * empty}]"

    def _clear_line(self) -> None:
        """Clear the current line."""
        if self._last_line_length > 0:
            self.output.write('\r' + ' ' * self._last_line_length + '\r')

    async def on_progress(self, event: ProgressEvent) -> None:
        """Print progress to console."""
        # New operation - print header
        if event.operation != self._last_operation:
            if self._last_operation is not None:
                self.output.write('\n')
            self._last_operation = event.operation
            self._last_line_length = 0

        # Build progress line
        parts = []

        if event.phase == ProgressPhase.INIT:
            parts.append(f"Starting {event.operation}")
            if event.message:
                parts.append(f": {event.message}")
            line = "".join(parts)
            self.output.write(line + '\n')
            self.output.flush()
            return

        if event.phase == ProgressPhase.ERROR:
            self._clear_line()
            line = f"Error in {event.operation}: {event.message}"
            self.output.write(line + '\n')
            self.output.flush()
            return

        if event.phase == ProgressPhase.COMPLETE:
            self._clear_line()
            line = f"Completed {event.operation}"
            if event.message:
                line += f": {event.message}"
            self.output.write(line + '\n')
            self.output.flush()
            self._last_operation = None
            return

        # Processing phase - show progress
        if self.show_bar:
            parts.append(self._format_bar(event.percent))

        if self.show_percent:
            parts.append(f" {event.percent:5.1f}%")

        if self.show_count and event.total > 0:
            parts.append(f" ({event.current}/{event.total})")

        if event.message:
            parts.append(f" {event.message}")

        if event.detail:
            # Truncate detail if too long
            max_detail = 40
            detail = event.detail
            if len(detail) > max_detail:
                detail = "..." + detail[-(max_detail - 3):]
            parts.append(f" - {detail}")

        line = "".join(parts)

        # Clear previous line and write new one
        self._clear_line()
        self.output.write('\r' + line)
        self.output.flush()
        self._last_line_length = len(line)


class JSONProgressCallback(ProgressCallback):
    """Progress callback that outputs JSON lines."""

    def __init__(self, output=None):
        """Initialize JSON progress callback.

        Args:
            output: Output stream (defaults to sys.stderr)
        """
        import json
        self.output = output or sys.stderr
        self._json = json

    async def on_progress(self, event: ProgressEvent) -> None:
        """Output progress as JSON line."""
        self.output.write(self._json.dumps(event.to_dict()) + '\n')
        self.output.flush()


class CollectingProgressCallback(ProgressCallback):
    """Progress callback that collects events for testing."""

    def __init__(self):
        self.events: list[ProgressEvent] = []

    async def on_progress(self, event: ProgressEvent) -> None:
        """Collect progress event."""
        self.events.append(event)

    def clear(self) -> None:
        """Clear collected events."""
        self.events.clear()


class CompositeProgressCallback(ProgressCallback):
    """Progress callback that delegates to multiple callbacks."""

    def __init__(self, callbacks: list[ProgressCallback]):
        """Initialize with list of callbacks.

        Args:
            callbacks: List of callbacks to delegate to
        """
        self.callbacks = callbacks

    async def on_progress(self, event: ProgressEvent) -> None:
        """Delegate to all callbacks."""
        for callback in self.callbacks:
            await callback.on_progress(event)


class ProgressReporter:
    """Helper class to report progress with context.

    Provides a simpler interface for reporting progress within a specific operation.
    """

    def __init__(
        self,
        callback: Optional[ProgressCallback],
        operation: str,
        total: int = 0
    ):
        """Initialize progress reporter.

        Args:
            callback: Progress callback (can be None)
            operation: Name of the operation
            total: Total number of items (can be updated later)
        """
        self._callback = callback or NoOpProgressCallback()
        self._operation = operation
        self._total = total
        self._current = 0

    @property
    def total(self) -> int:
        return self._total

    @total.setter
    def total(self, value: int) -> None:
        self._total = value

    async def start(self, message: str = "", **metadata) -> None:
        """Report operation start."""
        await self._callback.report(
            operation=self._operation,
            phase=ProgressPhase.INIT,
            current=0,
            total=self._total,
            message=message,
            **metadata
        )

    async def update(
        self,
        current: Optional[int] = None,
        message: str = "",
        detail: str = "",
        **metadata
    ) -> None:
        """Report progress update.

        Args:
            current: Current item number (increments by 1 if not provided)
            message: Status message
            detail: Detail like file name
            **metadata: Additional metadata
        """
        if current is not None:
            self._current = current
        else:
            self._current += 1

        await self._callback.report(
            operation=self._operation,
            phase=ProgressPhase.PROCESSING,
            current=self._current,
            total=self._total,
            message=message,
            detail=detail,
            **metadata
        )

    async def complete(self, message: str = "", **metadata) -> None:
        """Report operation complete."""
        await self._callback.report(
            operation=self._operation,
            phase=ProgressPhase.COMPLETE,
            current=self._total,
            total=self._total,
            message=message,
            **metadata
        )

    async def error(self, message: str, **metadata) -> None:
        """Report error."""
        await self._callback.report(
            operation=self._operation,
            phase=ProgressPhase.ERROR,
            current=self._current,
            total=self._total,
            message=message,
            **metadata
        )
