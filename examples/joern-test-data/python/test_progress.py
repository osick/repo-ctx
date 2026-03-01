"""Tests for docgen.progress module."""

import pytest
from io import StringIO
from unittest.mock import MagicMock, patch

from rich.console import Console

from docgen.progress import (
    ProgressReporter,
    SimpleProgressReporter,
    create_reporter,
)
from docgen.state import DocGenState, DocGenPhase, create_initial_state


@pytest.fixture
def sample_state() -> DocGenState:
    """Create a sample state for testing."""
    state = create_initial_state("/test/project")
    state["phase"] = DocGenPhase.COMPLETED.value
    state["symbols"] = [
        {"name": "User", "symbol_type": "class"},
        {"name": "Order", "symbol_type": "class"},
    ]
    state["dependencies"] = [
        {"source": "Order", "target": "User", "dependency_type": "uses"}
    ]
    state["domain_model"] = {
        "entities": [
            {"name": "User", "description": "A user"},
            {"name": "Order", "description": "An order"},
        ],
    }
    state["documentation"] = [
        {"title": "Overview", "content": "Overview", "section_type": "overview", "order": 0},
        {"title": "User", "content": "User doc", "section_type": "entity", "order": 1},
    ]
    state["review_feedback"] = {"is_approved": True, "issues": [], "suggestions": []}
    state["revision_count"] = 1
    state["is_complete"] = True
    return state


@pytest.fixture
def string_console():
    """Create a console that writes to a string."""
    output = StringIO()
    console = Console(file=output, force_terminal=True, width=80)
    return console, output


class TestProgressReporter:
    """Tests for ProgressReporter."""

    def test_init_creates_console(self):
        reporter = ProgressReporter()
        assert reporter.console is not None

    def test_init_with_console(self, string_console):
        console, _ = string_console
        reporter = ProgressReporter(console=console)
        assert reporter.console is console

    def test_init_verbose(self):
        reporter = ProgressReporter(verbose=True)
        assert reporter.verbose is True

    def test_start_displays_target(self, string_console):
        console, output = string_console
        reporter = ProgressReporter(console=console)

        reporter.start("/test/project")

        result = output.getvalue()
        assert "DocGen" in result
        assert "/test/project" in result

    def test_phase_started_analyzing(self, string_console):
        console, output = string_console
        reporter = ProgressReporter(console=console)

        reporter.phase_started(DocGenPhase.ANALYZING)

        result = output.getvalue()
        assert "Analyzing" in result

    def test_phase_started_completed(self, string_console):
        console, output = string_console
        reporter = ProgressReporter(console=console)

        reporter.phase_started(DocGenPhase.COMPLETED)

        result = output.getvalue()
        assert "complete" in result

    def test_phase_started_failed(self, string_console):
        console, output = string_console
        reporter = ProgressReporter(console=console)

        reporter.phase_started(DocGenPhase.FAILED)

        result = output.getvalue()
        assert "failed" in result

    def test_phase_completed_verbose(self, string_console):
        console, output = string_console
        reporter = ProgressReporter(console=console, verbose=True)

        reporter.phase_completed(DocGenPhase.ANALYZING, "Found 10 symbols")

        result = output.getvalue()
        # Rich adds escape codes, so check for parts of the message
        assert "Found" in result
        assert "10" in result
        assert "symbols" in result

    def test_phase_completed_not_verbose(self, string_console):
        console, output = string_console
        reporter = ProgressReporter(console=console, verbose=False)

        reporter.phase_completed(DocGenPhase.ANALYZING, "Found 10 symbols")

        result = output.getvalue()
        assert "Found 10 symbols" not in result

    def test_agent_activity_verbose(self, string_console):
        console, output = string_console
        reporter = ProgressReporter(console=console, verbose=True)

        reporter.agent_activity("Analyzer", "Extracting symbols")

        result = output.getvalue()
        assert "Analyzer" in result
        assert "Extracting symbols" in result

    def test_agent_activity_not_verbose(self, string_console):
        console, output = string_console
        reporter = ProgressReporter(console=console, verbose=False)

        reporter.agent_activity("Analyzer", "Extracting symbols")

        result = output.getvalue()
        assert result == ""

    def test_show_analysis_results_verbose(self, string_console, sample_state):
        console, output = string_console
        reporter = ProgressReporter(console=console, verbose=True)

        reporter.show_analysis_results(sample_state)

        result = output.getvalue()
        assert "Analysis Results" in result
        assert "Symbols Found" in result
        assert "2" in result  # Number of symbols

    def test_show_analysis_results_not_verbose(self, string_console, sample_state):
        console, output = string_console
        reporter = ProgressReporter(console=console, verbose=False)

        reporter.show_analysis_results(sample_state)

        result = output.getvalue()
        assert result == ""

    def test_show_review_feedback_approved(self, string_console, sample_state):
        console, output = string_console
        reporter = ProgressReporter(console=console)

        reporter.show_review_feedback(sample_state)

        result = output.getvalue()
        assert "Approved" in result

    def test_show_review_feedback_not_approved(self, string_console, sample_state):
        console, output = string_console
        reporter = ProgressReporter(console=console)

        sample_state["review_feedback"] = {
            "is_approved": False,
            "issues": ["Missing sections"],
            "suggestions": [],
        }

        reporter.show_review_feedback(sample_state)

        result = output.getvalue()
        assert "Needs revision" in result

    def test_show_summary(self, string_console, sample_state):
        console, output = string_console
        reporter = ProgressReporter(console=console)

        reporter.show_summary(sample_state)

        result = output.getvalue()
        assert "Summary" in result
        assert "/test/project" in result
        assert "completed" in result

    def test_show_summary_with_output_path(self, string_console, sample_state):
        console, output = string_console
        reporter = ProgressReporter(console=console)

        reporter.show_summary(sample_state, "/output/docs.md")

        result = output.getvalue()
        assert "/output/docs.md" in result

    def test_show_error(self, string_console):
        console, output = string_console
        reporter = ProgressReporter(console=console)

        reporter.show_error("Something went wrong")

        result = output.getvalue()
        assert "Error" in result
        assert "Something went wrong" in result

    def test_show_warning(self, string_console):
        console, output = string_console
        reporter = ProgressReporter(console=console)

        reporter.show_warning("This is a warning")

        result = output.getvalue()
        assert "Warning" in result
        assert "This is a warning" in result


class TestSimpleProgressReporter:
    """Tests for SimpleProgressReporter."""

    def test_init(self):
        reporter = SimpleProgressReporter()
        assert reporter.verbose is False

    def test_init_verbose(self):
        reporter = SimpleProgressReporter(verbose=True)
        assert reporter.verbose is True

    def test_start(self, capsys):
        reporter = SimpleProgressReporter()
        reporter.start("/test/project")

        captured = capsys.readouterr()
        assert "DocGen" in captured.out
        assert "/test/project" in captured.out

    def test_phase_started(self, capsys):
        reporter = SimpleProgressReporter()
        reporter.phase_started(DocGenPhase.ANALYZING)

        captured = capsys.readouterr()
        assert "Analyzing" in captured.out

    def test_show_summary(self, capsys, sample_state):
        reporter = SimpleProgressReporter()
        reporter.show_summary(sample_state)

        captured = capsys.readouterr()
        assert "Summary" in captured.out
        assert "/test/project" in captured.out

    def test_show_error(self, capsys):
        reporter = SimpleProgressReporter()
        reporter.show_error("Test error")

        captured = capsys.readouterr()
        assert "Error" in captured.out
        assert "Test error" in captured.out

    def test_show_warning(self, capsys):
        reporter = SimpleProgressReporter()
        reporter.show_warning("Test warning")

        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "Test warning" in captured.out


class TestCreateReporter:
    """Tests for create_reporter function."""

    def test_creates_progress_reporter_by_default(self):
        reporter = create_reporter()
        assert isinstance(reporter, ProgressReporter)

    def test_creates_simple_reporter_when_simple_true(self):
        reporter = create_reporter(simple=True)
        assert isinstance(reporter, SimpleProgressReporter)

    def test_passes_verbose_to_reporter(self):
        reporter = create_reporter(verbose=True)
        assert reporter.verbose is True

    def test_passes_console_to_reporter(self, string_console):
        console, _ = string_console
        reporter = create_reporter(console=console)
        assert reporter.console is console


class TestProgressReporterProgressContext:
    """Tests for progress context manager."""

    def test_progress_context_yields(self, string_console):
        console, _ = string_console
        reporter = ProgressReporter(console=console)

        with reporter.progress_context("Testing...") as progress:
            assert progress is not None

    def test_progress_context_cleans_up(self, string_console):
        console, _ = string_console
        reporter = ProgressReporter(console=console)

        with reporter.progress_context("Testing..."):
            assert reporter._progress is not None

        assert reporter._progress is None

    def test_update_progress(self, string_console):
        console, _ = string_console
        reporter = ProgressReporter(console=console)

        with reporter.progress_context("Testing...", total=100):
            reporter.update_progress(advance=10)
            # Should not raise

    def test_update_progress_without_context(self, string_console):
        console, _ = string_console
        reporter = ProgressReporter(console=console)

        # Should not raise when no progress context
        reporter.update_progress(advance=10)


class TestPhaseDescriptions:
    """Tests for phase descriptions."""

    def test_all_phases_have_descriptions(self):
        reporter = ProgressReporter()

        for phase in DocGenPhase:
            assert phase in reporter.PHASE_DESCRIPTIONS, f"Missing description for {phase}"

    def test_phase_order_covers_main_phases(self):
        reporter = ProgressReporter()

        assert DocGenPhase.INITIALIZING in reporter.PHASE_ORDER
        assert DocGenPhase.ANALYZING in reporter.PHASE_ORDER
        assert DocGenPhase.EXTRACTING in reporter.PHASE_ORDER
        assert DocGenPhase.WRITING in reporter.PHASE_ORDER
        assert DocGenPhase.REVIEWING in reporter.PHASE_ORDER
        assert DocGenPhase.COMPLETED in reporter.PHASE_ORDER
