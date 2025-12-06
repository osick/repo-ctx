"""Tests for progress reporting module."""

import asyncio
import io
import pytest
from datetime import datetime

from repo_ctx.progress import (
    ProgressPhase,
    ProgressEvent,
    ProgressCallback,
    NoOpProgressCallback,
    PrintProgressCallback,
    JSONProgressCallback,
    CollectingProgressCallback,
    CompositeProgressCallback,
    ProgressReporter,
)


class TestProgressEvent:
    """Tests for ProgressEvent dataclass."""

    def test_create_event(self):
        """Test creating a progress event."""
        event = ProgressEvent(
            operation="test_op",
            phase=ProgressPhase.PROCESSING,
            current=5,
            total=10,
            message="Processing",
            detail="file.txt"
        )
        assert event.operation == "test_op"
        assert event.phase == ProgressPhase.PROCESSING
        assert event.current == 5
        assert event.total == 10
        assert event.message == "Processing"
        assert event.detail == "file.txt"
        assert isinstance(event.timestamp, datetime)

    def test_percent_calculation(self):
        """Test percentage calculation."""
        event = ProgressEvent(
            operation="test",
            phase=ProgressPhase.PROCESSING,
            current=25,
            total=100
        )
        assert event.percent == 25.0

    def test_percent_at_zero_total(self):
        """Test percentage when total is zero."""
        event = ProgressEvent(
            operation="test",
            phase=ProgressPhase.PROCESSING,
            current=0,
            total=0
        )
        assert event.percent == 0.0

    def test_percent_capped_at_100(self):
        """Test percentage doesn't exceed 100%."""
        event = ProgressEvent(
            operation="test",
            phase=ProgressPhase.PROCESSING,
            current=150,
            total=100
        )
        assert event.percent == 100.0

    def test_is_complete(self):
        """Test is_complete property."""
        processing_event = ProgressEvent(
            operation="test",
            phase=ProgressPhase.PROCESSING,
            current=5,
            total=10
        )
        complete_event = ProgressEvent(
            operation="test",
            phase=ProgressPhase.COMPLETE,
            current=10,
            total=10
        )
        assert not processing_event.is_complete
        assert complete_event.is_complete

    def test_to_dict(self):
        """Test converting event to dictionary."""
        event = ProgressEvent(
            operation="test_op",
            phase=ProgressPhase.PROCESSING,
            current=5,
            total=10,
            message="Processing",
            detail="file.txt",
            metadata={"key": "value"}
        )
        data = event.to_dict()
        assert data["operation"] == "test_op"
        assert data["phase"] == "processing"
        assert data["current"] == 5
        assert data["total"] == 10
        assert data["percent"] == 50.0
        assert data["message"] == "Processing"
        assert data["detail"] == "file.txt"
        assert data["metadata"] == {"key": "value"}
        assert "timestamp" in data


class TestNoOpProgressCallback:
    """Tests for NoOpProgressCallback."""

    @pytest.mark.asyncio
    async def test_does_nothing(self):
        """Test that NoOp callback does nothing."""
        callback = NoOpProgressCallback()
        event = ProgressEvent(
            operation="test",
            phase=ProgressPhase.PROCESSING,
            current=1,
            total=10
        )
        # Should not raise any exception
        await callback.on_progress(event)


class TestCollectingProgressCallback:
    """Tests for CollectingProgressCallback."""

    @pytest.mark.asyncio
    async def test_collects_events(self):
        """Test that callback collects events."""
        callback = CollectingProgressCallback()

        events = [
            ProgressEvent(operation="test", phase=ProgressPhase.INIT, current=0, total=3),
            ProgressEvent(operation="test", phase=ProgressPhase.PROCESSING, current=1, total=3),
            ProgressEvent(operation="test", phase=ProgressPhase.PROCESSING, current=2, total=3),
            ProgressEvent(operation="test", phase=ProgressPhase.COMPLETE, current=3, total=3),
        ]

        for event in events:
            await callback.on_progress(event)

        assert len(callback.events) == 4
        assert callback.events[0].phase == ProgressPhase.INIT
        assert callback.events[3].phase == ProgressPhase.COMPLETE

    @pytest.mark.asyncio
    async def test_clear_events(self):
        """Test clearing collected events."""
        callback = CollectingProgressCallback()
        event = ProgressEvent(operation="test", phase=ProgressPhase.INIT, current=0, total=1)
        await callback.on_progress(event)

        assert len(callback.events) == 1
        callback.clear()
        assert len(callback.events) == 0


class TestPrintProgressCallback:
    """Tests for PrintProgressCallback."""

    @pytest.mark.asyncio
    async def test_init_phase_output(self):
        """Test output for INIT phase."""
        output = io.StringIO()
        callback = PrintProgressCallback(output=output)

        event = ProgressEvent(
            operation="index_repo",
            phase=ProgressPhase.INIT,
            current=0,
            total=10,
            message="Starting indexing"
        )
        await callback.on_progress(event)

        output_str = output.getvalue()
        assert "Starting index_repo" in output_str
        assert "Starting indexing" in output_str

    @pytest.mark.asyncio
    async def test_processing_phase_output(self):
        """Test output for PROCESSING phase."""
        output = io.StringIO()
        callback = PrintProgressCallback(output=output, show_bar=True)

        event = ProgressEvent(
            operation="index_repo",
            phase=ProgressPhase.PROCESSING,
            current=5,
            total=10,
            message="Processing files"
        )
        await callback.on_progress(event)

        output_str = output.getvalue()
        assert "50.0%" in output_str
        assert "(5/10)" in output_str

    @pytest.mark.asyncio
    async def test_complete_phase_output(self):
        """Test output for COMPLETE phase."""
        output = io.StringIO()
        callback = PrintProgressCallback(output=output)

        event = ProgressEvent(
            operation="index_repo",
            phase=ProgressPhase.COMPLETE,
            current=10,
            total=10,
            message="Indexed 10 files"
        )
        await callback.on_progress(event)

        output_str = output.getvalue()
        assert "Completed index_repo" in output_str
        assert "Indexed 10 files" in output_str

    @pytest.mark.asyncio
    async def test_error_phase_output(self):
        """Test output for ERROR phase."""
        output = io.StringIO()
        callback = PrintProgressCallback(output=output)

        event = ProgressEvent(
            operation="index_repo",
            phase=ProgressPhase.ERROR,
            current=5,
            total=10,
            message="Connection failed"
        )
        await callback.on_progress(event)

        output_str = output.getvalue()
        assert "Error in index_repo" in output_str
        assert "Connection failed" in output_str

    @pytest.mark.asyncio
    async def test_detail_truncation(self):
        """Test that long details are truncated."""
        output = io.StringIO()
        callback = PrintProgressCallback(output=output)

        long_detail = "a" * 100  # Very long detail
        event = ProgressEvent(
            operation="test",
            phase=ProgressPhase.PROCESSING,
            current=1,
            total=10,
            detail=long_detail
        )
        await callback.on_progress(event)

        output_str = output.getvalue()
        # Should contain truncated detail with "..."
        assert "..." in output_str


class TestJSONProgressCallback:
    """Tests for JSONProgressCallback."""

    @pytest.mark.asyncio
    async def test_json_output(self):
        """Test JSON output format."""
        import json

        output = io.StringIO()
        callback = JSONProgressCallback(output=output)

        event = ProgressEvent(
            operation="test_op",
            phase=ProgressPhase.PROCESSING,
            current=5,
            total=10,
            message="Processing"
        )
        await callback.on_progress(event)

        output_str = output.getvalue().strip()
        data = json.loads(output_str)

        assert data["operation"] == "test_op"
        assert data["phase"] == "processing"
        assert data["current"] == 5
        assert data["total"] == 10
        assert data["percent"] == 50.0


class TestCompositeProgressCallback:
    """Tests for CompositeProgressCallback."""

    @pytest.mark.asyncio
    async def test_delegates_to_all(self):
        """Test that composite delegates to all callbacks."""
        callback1 = CollectingProgressCallback()
        callback2 = CollectingProgressCallback()
        composite = CompositeProgressCallback([callback1, callback2])

        event = ProgressEvent(
            operation="test",
            phase=ProgressPhase.PROCESSING,
            current=1,
            total=10
        )
        await composite.on_progress(event)

        assert len(callback1.events) == 1
        assert len(callback2.events) == 1


class TestProgressReporter:
    """Tests for ProgressReporter helper class."""

    @pytest.mark.asyncio
    async def test_start_phase(self):
        """Test reporting start phase."""
        callback = CollectingProgressCallback()
        reporter = ProgressReporter(callback, "test_op", total=10)

        await reporter.start("Starting operation", key="value")

        assert len(callback.events) == 1
        event = callback.events[0]
        assert event.operation == "test_op"
        assert event.phase == ProgressPhase.INIT
        assert event.message == "Starting operation"
        assert event.metadata.get("key") == "value"

    @pytest.mark.asyncio
    async def test_update_phase(self):
        """Test reporting update phase."""
        callback = CollectingProgressCallback()
        reporter = ProgressReporter(callback, "test_op", total=10)

        await reporter.update(current=5, message="Processing", detail="file.txt")

        assert len(callback.events) == 1
        event = callback.events[0]
        assert event.phase == ProgressPhase.PROCESSING
        assert event.current == 5
        assert event.message == "Processing"
        assert event.detail == "file.txt"

    @pytest.mark.asyncio
    async def test_update_increments_current(self):
        """Test that update without current increments counter."""
        callback = CollectingProgressCallback()
        reporter = ProgressReporter(callback, "test_op", total=10)

        await reporter.update()
        await reporter.update()
        await reporter.update()

        assert callback.events[-1].current == 3

    @pytest.mark.asyncio
    async def test_complete_phase(self):
        """Test reporting complete phase."""
        callback = CollectingProgressCallback()
        reporter = ProgressReporter(callback, "test_op", total=10)

        await reporter.complete("Done!", count=10)

        assert len(callback.events) == 1
        event = callback.events[0]
        assert event.phase == ProgressPhase.COMPLETE
        assert event.message == "Done!"
        assert event.metadata.get("count") == 10

    @pytest.mark.asyncio
    async def test_error_phase(self):
        """Test reporting error phase."""
        callback = CollectingProgressCallback()
        reporter = ProgressReporter(callback, "test_op", total=10)

        await reporter.error("Something went wrong")

        assert len(callback.events) == 1
        event = callback.events[0]
        assert event.phase == ProgressPhase.ERROR
        assert event.message == "Something went wrong"

    @pytest.mark.asyncio
    async def test_total_property(self):
        """Test total property getter and setter."""
        callback = CollectingProgressCallback()
        reporter = ProgressReporter(callback, "test_op", total=10)

        assert reporter.total == 10
        reporter.total = 20
        assert reporter.total == 20

    @pytest.mark.asyncio
    async def test_with_none_callback(self):
        """Test that reporter works with None callback (uses NoOp)."""
        reporter = ProgressReporter(None, "test_op", total=10)

        # Should not raise any exceptions
        await reporter.start("Starting")
        await reporter.update(current=5)
        await reporter.complete("Done")

    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """Test a full workflow with start, updates, and complete."""
        callback = CollectingProgressCallback()
        reporter = ProgressReporter(callback, "index_files", total=3)

        await reporter.start("Indexing files")
        await reporter.update(current=1, message="Processing", detail="file1.md")
        await reporter.update(current=2, message="Processing", detail="file2.md")
        await reporter.update(current=3, message="Processing", detail="file3.md")
        await reporter.complete("Indexed 3 files")

        assert len(callback.events) == 5
        assert callback.events[0].phase == ProgressPhase.INIT
        assert callback.events[1].phase == ProgressPhase.PROCESSING
        assert callback.events[4].phase == ProgressPhase.COMPLETE


class TestProgressCallbackReport:
    """Tests for the ProgressCallback.report convenience method."""

    @pytest.mark.asyncio
    async def test_report_method(self):
        """Test the report convenience method."""
        callback = CollectingProgressCallback()

        await callback.report(
            operation="test_op",
            phase=ProgressPhase.PROCESSING,
            current=5,
            total=10,
            message="Processing",
            detail="file.txt",
            custom_key="custom_value"
        )

        assert len(callback.events) == 1
        event = callback.events[0]
        assert event.operation == "test_op"
        assert event.phase == ProgressPhase.PROCESSING
        assert event.current == 5
        assert event.total == 10
        assert event.message == "Processing"
        assert event.detail == "file.txt"
        assert event.metadata.get("custom_key") == "custom_value"


class TestProgressPhase:
    """Tests for ProgressPhase enum."""

    def test_phase_values(self):
        """Test phase enum values."""
        assert ProgressPhase.INIT.value == "init"
        assert ProgressPhase.PROCESSING.value == "processing"
        assert ProgressPhase.COMPLETE.value == "complete"
        assert ProgressPhase.ERROR.value == "error"

    def test_phase_string_conversion(self):
        """Test phase string conversion."""
        # The .value property returns the string value
        assert ProgressPhase.INIT.value == "init"
        # str() gives the enum member name
        assert "INIT" in str(ProgressPhase.INIT)
