"""
Joern CLI wrapper for subprocess-based integration.

This module provides a Python interface to Joern's command-line tools:
- joern-parse: Generate CPG from source code
- joern: Run CPGQL queries via scripts
- joern-export: Export CPG to various formats
"""

import logging
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class JoernError(Exception):
    """Base exception for Joern-related errors."""

    pass


class JoernNotFoundError(JoernError):
    """Raised when Joern installation is not found."""

    pass


class JoernParseError(JoernError):
    """Raised when joern-parse fails."""

    pass


class JoernQueryError(JoernError):
    """Raised when a CPGQL query fails."""

    pass


class JoernExportError(JoernError):
    """Raised when joern-export fails."""

    pass


@dataclass
class JoernResult:
    """Result from a Joern CLI command."""

    success: bool
    stdout: str
    stderr: str
    return_code: int
    command: list[str]
    duration_ms: int = 0


@dataclass
class ParseResult:
    """Result from joern-parse command."""

    cpg_path: str
    success: bool
    files_processed: int = 0
    errors: list[str] | None = None


@dataclass
class QueryResult:
    """Result from a CPGQL query."""

    output: str
    success: bool
    query: str
    execution_time_ms: int = 0


@dataclass
class ExportResult:
    """Result from joern-export command."""

    output_dir: str
    format: str
    representation: str
    files_created: list[str]
    success: bool


class JoernCLI:
    """
    Wrapper for Joern command-line tools.

    Provides methods to:
    - Check if Joern is installed
    - Parse source code into CPG
    - Run CPGQL queries
    - Export CPG to various formats
    """

    # Default paths to search for Joern
    DEFAULT_PATHS = [
        "~/bin/joern",
        "/usr/local/bin/joern",
        "/opt/joern",
    ]

    # Default timeout for commands (5 minutes)
    DEFAULT_TIMEOUT = 300

    def __init__(
        self,
        joern_path: str | None = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        """
        Initialize the Joern CLI wrapper.

        Args:
            joern_path: Custom path to Joern installation directory.
                       If None, will search in default locations.
            timeout: Default timeout for commands in seconds.
        """
        self._joern_path = joern_path
        self._timeout = timeout
        self._resolved_path: str | None = None

    @property
    def joern_path(self) -> str | None:
        """Get the resolved Joern installation path."""
        if self._resolved_path is None:
            self._resolved_path = self._find_joern_path()
        return self._resolved_path

    def _find_joern_path(self) -> str | None:
        """
        Find the Joern installation directory.

        Returns:
            Path to Joern installation or None if not found.
        """
        # Check custom path first
        if self._joern_path:
            expanded = os.path.expanduser(self._joern_path)
            if os.path.isdir(expanded):
                return expanded

        # Check if joern is in PATH
        joern_bin = shutil.which("joern")
        if joern_bin:
            # joern binary is usually in joern-cli/bin/joern
            bin_dir = os.path.dirname(joern_bin)
            if os.path.basename(bin_dir) == "bin":
                parent = os.path.dirname(bin_dir)
                if os.path.basename(parent) == "joern-cli":
                    return os.path.dirname(parent)
            return bin_dir

        # Search default paths
        for path in self.DEFAULT_PATHS:
            expanded = os.path.expanduser(path)
            if os.path.isdir(expanded):
                return expanded

        return None

    def _get_command_path(self, command: str) -> str:
        """
        Get the full path to a Joern command.

        Args:
            command: Command name (e.g., 'joern-parse', 'joern', 'joern-export')

        Returns:
            Full path to the command.

        Raises:
            JoernNotFoundError: If Joern is not installed.
        """
        # First check if command is directly available in PATH
        which_result = shutil.which(command)
        if which_result:
            return which_result

        # Check in Joern installation directory
        if self.joern_path:
            # Try joern-cli/bin/<command>
            cli_path = os.path.join(self.joern_path, "joern-cli", "bin", command)
            if os.path.isfile(cli_path) and os.access(cli_path, os.X_OK):
                return cli_path

            # Try bin/<command>
            bin_path = os.path.join(self.joern_path, "bin", command)
            if os.path.isfile(bin_path) and os.access(bin_path, os.X_OK):
                return bin_path

            # Try <command> directly
            direct_path = os.path.join(self.joern_path, command)
            if os.path.isfile(direct_path) and os.access(direct_path, os.X_OK):
                return direct_path

        raise JoernNotFoundError(
            f"Joern command '{command}' not found. "
            "Please install Joern from https://github.com/joernio/joern"
        )

    def is_available(self) -> bool:
        """
        Check if Joern is installed and accessible.

        Returns:
            True if Joern is available, False otherwise.
        """
        try:
            self._get_command_path("joern-parse")
            return True
        except JoernNotFoundError:
            return False

    def get_version(self) -> str | None:
        """
        Get the Joern version.

        Returns:
            Version string or None if unable to determine.
        """
        try:
            result = self._run_command(["joern", "--version"])
            if result.success:
                return result.stdout.strip()
        except (JoernNotFoundError, JoernError):
            pass
        return None

    def _run_command(
        self,
        args: list[str],
        timeout: int | None = None,
        cwd: str | None = None,
        env: dict[str, str] | None = None,
    ) -> JoernResult:
        """
        Run a Joern command.

        Args:
            args: Command and arguments (first element is the command name).
            timeout: Timeout in seconds (uses default if None).
            cwd: Working directory for the command.
            env: Additional environment variables.

        Returns:
            JoernResult with command output.
        """
        import time

        # Resolve command path
        command = args[0]
        full_path = self._get_command_path(command)
        full_args = [full_path] + args[1:]

        # Prepare environment
        run_env = os.environ.copy()
        if env:
            run_env.update(env)

        # Set memory limit if not already set
        if "JAVA_OPTS" not in run_env:
            run_env["JAVA_OPTS"] = "-Xmx4g"

        timeout = timeout or self._timeout

        logger.debug(f"Running Joern command: {' '.join(full_args)}")
        start_time = time.time()

        try:
            result = subprocess.run(
                full_args,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=run_env,
            )
            duration_ms = int((time.time() - start_time) * 1000)

            return JoernResult(
                success=result.returncode == 0,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                command=full_args,
                duration_ms=duration_ms,
            )

        except subprocess.TimeoutExpired as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return JoernResult(
                success=False,
                stdout=e.stdout or "" if hasattr(e, "stdout") else "",
                stderr=f"Command timed out after {timeout} seconds",
                return_code=-1,
                command=full_args,
                duration_ms=duration_ms,
            )

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return JoernResult(
                success=False,
                stdout="",
                stderr=str(e),
                return_code=-1,
                command=full_args,
                duration_ms=duration_ms,
            )

    def parse(
        self,
        input_path: str,
        output_path: str | None = None,
        language: str | None = None,
        timeout: int | None = None,
    ) -> ParseResult:
        """
        Parse source code and generate a CPG.

        Args:
            input_path: Path to source file or directory.
            output_path: Path for output CPG file (auto-generated if None).
            language: Language hint (auto-detected if None).
            timeout: Command timeout in seconds.

        Returns:
            ParseResult with CPG file path.

        Raises:
            JoernParseError: If parsing fails.
        """
        # Validate input path
        if not os.path.exists(input_path):
            raise JoernParseError(f"Input path does not exist: {input_path}")

        # Generate output path if not provided
        if output_path is None:
            output_path = tempfile.mktemp(suffix=".bin", prefix="cpg_")

        # Build command
        args = ["joern-parse", input_path, "--output", output_path]

        if language:
            # Map language to Joern's language identifier
            lang_map = {
                "c": "C",
                "cpp": "CPP",
                "java": "JAVASRC",
                "javascript": "JSSRC",
                "typescript": "JSSRC",
                "python": "PYTHONSRC",
                "kotlin": "KOTLIN",
                "go": "GOSRC",
                "php": "PHP",
                "ruby": "RUBYSRC",
                "swift": "SWIFTSRC",
                "csharp": "CSHARPSRC",
            }
            joern_lang = lang_map.get(language.lower())
            if joern_lang:
                args.extend(["--language", joern_lang])

        result = self._run_command(args, timeout=timeout)

        if not result.success:
            raise JoernParseError(
                f"joern-parse failed: {result.stderr or result.stdout}"
            )

        # Verify CPG was created
        if not os.path.exists(output_path):
            raise JoernParseError(f"CPG file was not created: {output_path}")

        return ParseResult(
            cpg_path=output_path,
            success=True,
            errors=None,
        )

    def run_script(
        self,
        script_path: str,
        params: dict[str, str] | None = None,
        cpg_path: str | None = None,
        timeout: int | None = None,
    ) -> QueryResult:
        """
        Run a CPGQL script.

        Args:
            script_path: Path to the .sc script file.
            params: Parameters to pass to the script (--param key=value).
            cpg_path: Path to CPG file (can also be passed as param).
            timeout: Command timeout in seconds.

        Returns:
            QueryResult with script output.

        Raises:
            JoernQueryError: If script execution fails.
        """
        if not os.path.exists(script_path):
            raise JoernQueryError(f"Script file does not exist: {script_path}")

        args = ["joern", "--script", script_path]

        # Add CPG path if provided
        if cpg_path:
            if params is None:
                params = {}
            params["cpgFile"] = cpg_path

        # Add parameters
        if params:
            for key, value in params.items():
                args.extend(["--param", f"{key}={value}"])

        result = self._run_command(args, timeout=timeout)

        if not result.success:
            raise JoernQueryError(
                f"Script execution failed: {result.stderr or result.stdout}"
            )

        return QueryResult(
            output=result.stdout,
            success=True,
            query=f"script:{script_path}",
            execution_time_ms=result.duration_ms,
        )

    def run_query(
        self,
        cpg_path: str,
        query: str,
        output_file: str | None = None,
        timeout: int | None = None,
    ) -> QueryResult:
        """
        Run a CPGQL query on a CPG.

        Creates a temporary script to execute the query.

        Args:
            cpg_path: Path to the CPG file.
            query: CPGQL query string.
            output_file: Optional file to write results to.
            timeout: Command timeout in seconds.

        Returns:
            QueryResult with query output.

        Raises:
            JoernQueryError: If query execution fails.
        """
        if not os.path.exists(cpg_path):
            raise JoernQueryError(f"CPG file does not exist: {cpg_path}")

        # Create temporary script
        script_content = f'''@main def exec(cpgFile: String, outFile: String) = {{
  importCpg(cpgFile)
  val result = {query}
  result.mkString("\\n") #> outFile
}}
'''

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".sc", delete=False
        ) as script_file:
            script_file.write(script_content)
            script_path = script_file.name

        try:
            # Create output file
            if output_file is None:
                output_file = tempfile.mktemp(suffix=".txt", prefix="joern_query_")

            result = self.run_script(
                script_path=script_path,
                params={"cpgFile": cpg_path, "outFile": output_file},
                timeout=timeout,
            )

            # Read output from file
            output = ""
            if os.path.exists(output_file):
                with open(output_file, "r") as f:
                    output = f.read()

            return QueryResult(
                output=output,
                success=True,
                query=query,
                execution_time_ms=result.execution_time_ms,
            )

        finally:
            # Cleanup temporary files
            if os.path.exists(script_path):
                os.unlink(script_path)
            if output_file and os.path.exists(output_file):
                try:
                    os.unlink(output_file)
                except Exception:
                    pass

    def export(
        self,
        cpg_path: str,
        output_dir: str,
        representation: str = "all",
        format: str = "dot",
        timeout: int | None = None,
    ) -> ExportResult:
        """
        Export CPG to a visualization format.

        Args:
            cpg_path: Path to the CPG file.
            output_dir: Directory for exported files.
            representation: Graph representation (all, ast, cfg, cdg, ddg, pdg, cpg14).
            format: Output format (dot, graphml, graphson, neo4jcsv).
            timeout: Command timeout in seconds.

        Returns:
            ExportResult with export information.

        Raises:
            JoernExportError: If export fails.
        """
        if not os.path.exists(cpg_path):
            raise JoernExportError(f"CPG file does not exist: {cpg_path}")

        # Create output directory if needed
        os.makedirs(output_dir, exist_ok=True)

        args = [
            "joern-export",
            f"--repr={representation}",
            f"--format={format}",
            f"--out={output_dir}",
            cpg_path,
        ]

        result = self._run_command(args, timeout=timeout)

        if not result.success:
            raise JoernExportError(
                f"joern-export failed: {result.stderr or result.stdout}"
            )

        # Find created files
        files_created = []
        for root, _, files in os.walk(output_dir):
            for file in files:
                files_created.append(os.path.join(root, file))

        return ExportResult(
            output_dir=output_dir,
            format=format,
            representation=representation,
            files_created=files_created,
            success=True,
        )
