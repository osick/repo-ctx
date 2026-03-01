"""Generates consolidated codebase summary from enhanced symbol documentation."""
import asyncio
import json
import logging
from pathlib import Path
from typing import Optional, Literal, TYPE_CHECKING
from collections import defaultdict

if TYPE_CHECKING:
    from repo_ctx.services.llm import LLMService

logger = logging.getLogger("repo_ctx.analysis.codebase_summarizer")

# Type alias for summary types
SummaryType = Literal["business", "technical"]

# Technical summary prompt (original)
TECHNICAL_SUMMARY_PROMPT = """You are analyzing a codebase. Based on the following module and class information, generate a comprehensive technical summary.

## Project Structure

{modules_info}

## Instructions

Generate a Markdown document with the following sections:

1. **Architecture Overview** (2-3 paragraphs)
   - High-level architecture pattern (MVC, layered, microservices, etc.)
   - Key design decisions evident from the code structure
   - Main entry points and data flow

2. **Core Modules** (for each major module)
   - Purpose and responsibilities
   - Key classes and their roles
   - Dependencies on other modules

3. **Key Classes** (top 10-15 most important classes)
   - Class name and file location
   - Purpose and responsibilities
   - Key methods and what they do

4. **Design Patterns** (if any are evident)
   - Pattern name and where it's used
   - Brief explanation of why

5. **Technical Debt / Improvement Opportunities** (if any obvious)
   - Areas that could benefit from refactoring
   - Missing documentation or tests

Respond with Markdown only, no JSON wrapping.
"""

# Business summary prompt - focuses on value, not implementation
BUSINESS_SUMMARY_PROMPT = """You are a product analyst creating a comprehensive business overview of a software project.

## Project Name: {project_name}

## README / Project Description
{readme_content}

## Component Overview
{modules_info}

## Instructions

Generate a **business-focused** Markdown document that helps stakeholders understand what this software does and its value. Avoid technical jargon - write for product managers, executives, and non-technical stakeholders.

Include these sections:

1. **Executive Summary** (up to 4-5 paragraphs, comprehensive)
   - What is this product/tool?
   - What problem does it solve?
   - Who benefits from it?

2. **Key Capabilities** (main functions complete, bullet points)
   - Main features and what they enable users to do
   - Focus on outcomes, not implementation
   - Use action verbs (e.g., "Enables...", "Automates...", "Provides...")

3. **Target Users**
   - Who are the primary users?
   - What are their goals when using this software?
   - What workflows does this support?

4. **Business Value**
   - Time savings or efficiency gains
   - Problems eliminated or reduced
   - Competitive advantages

5. **Integration & Ecosystem**
   - What does this software connect with?
   - What workflows does it fit into?
   - Dependencies on other systems (in plain language)

6. **Maturity & Scope**
   - Is this a library, tool, service, or application?
   - Approximate scope (small utility vs. large platform)
   - Key limitations or boundaries


Keep the tone professional but accessible.
Respond with Markdown only, no JSON wrapping.
"""


class CodebaseSummarizer:
    """Generates consolidated codebase summary from symbol documentation."""

    MAX_CONTEXT_CHARS = 100000  # ~25000 tokens for context
    MAX_README_CHARS = 8000  # Limit README to ~2000 tokens
    MAX_RETRIES = 3  # Maximum attempts for empty LLM responses
    RETRY_DELAY = 1.0  # Seconds to wait between retries

    def __init__(
        self,
        llm_service: Optional["LLMService"] = None,
    ):
        """Initialize the summarizer.

        Args:
            llm_service: LLM service for generating summary.
        """
        self.llm_service = llm_service

    def _read_readme(self, repo_ctx_path: Path) -> str:
        """Read README.md from the repository root.

        Args:
            repo_ctx_path: Path to .repo-ctx directory.

        Returns:
            README content or placeholder if not found.
        """
        # .repo-ctx is inside the repo, so parent is repo root
        repo_root = repo_ctx_path.parent

        # Try common README names
        readme_names = ["README.md", "readme.md", "README.rst", "README.txt", "README"]
        for name in readme_names:
            readme_path = repo_root / name
            if readme_path.exists():
                try:
                    content = readme_path.read_text(encoding="utf-8")
                    if len(content) > self.MAX_README_CHARS:
                        content = content[:self.MAX_README_CHARS] + "\n\n... [truncated]"
                    logger.debug(f"Read README from {readme_path}")
                    return content
                except Exception as e:
                    logger.debug(f"Failed to read {readme_path}: {e}")

        return "(No README found)"

    def _format_modules_for_business(self, modules_data: dict) -> str:
        """Format module data for business summary (simplified, less technical).

        Args:
            modules_data: Dict of module -> file data.

        Returns:
            Formatted string focusing on capabilities, not implementation.
        """
        lines = []

        for module, files in sorted(modules_data.items()):
            # Skip test and example modules for business summary
            if any(skip in module.lower() for skip in ["test", "example", "__pycache__"]):
                continue

            lines.append(f"### {module}")

            # Collect unique file descriptions (skip technical details)
            descriptions = []
            for file_data in files[:5]:  # Limit files per module
                doc = file_data.get("documentation")
                if doc and len(doc) > 10:
                    # Take first sentence only
                    first_sentence = doc.split(".")[0] + "."
                    if first_sentence not in descriptions:
                        descriptions.append(first_sentence[:150])

            if descriptions:
                for desc in descriptions[:3]:
                    lines.append(f"- {desc}")
            else:
                lines.append("- (Component functionality)")

            lines.append("")

        return "\n".join(lines)

    async def generate_summary(
        self,
        repo_ctx_path: Path,
        project_name: str = "Project",
        summary_type: SummaryType = "business",
    ) -> Optional[str]:
        """Generate consolidated codebase summary.

        Args:
            repo_ctx_path: Path to .repo-ctx directory.
            project_name: Name of the project.
            summary_type: Type of summary - "business" (default) or "technical".

        Returns:
            Markdown summary string or None if generation fails.
        """
        if not self.llm_service:
            logger.warning("No LLM service - cannot generate summary")
            return None

        # Try to load enhanced file data from by-file directory
        by_file_dir = repo_ctx_path / "symbols" / "by-file"
        if by_file_dir.exists():
            modules_data = self._collect_module_data(by_file_dir)
        else:
            # Fallback: use symbols/index.json
            logger.info("Using symbols/index.json for codebase summary (by-file not available)")
            index_file = repo_ctx_path / "symbols" / "index.json"
            if index_file.exists():
                modules_data = self._collect_module_data_from_index(index_file)
            else:
                logger.warning("No symbol data found - neither by-file nor index.json")
                return None

        if not modules_data:
            logger.warning("No module data collected")
            return None

        # Build context for LLM based on summary type
        if summary_type == "business":
            modules_info = self._format_modules_for_business(modules_data)
            readme_content = self._read_readme(repo_ctx_path)
            prompt = BUSINESS_SUMMARY_PROMPT.format(
                project_name=project_name,
                readme_content=readme_content,
                modules_info=modules_info,
            )
            header_subtitle = "_Business overview generated from codebase analysis._"
        else:
            modules_info = self._format_modules_info(modules_data)
            # Truncate if too long
            if len(modules_info) > self.MAX_CONTEXT_CHARS:
                modules_info = modules_info[:self.MAX_CONTEXT_CHARS] + "\n\n... [truncated]"
            prompt = TECHNICAL_SUMMARY_PROMPT.format(modules_info=modules_info)
            header_subtitle = "_Technical summary generated from symbol analysis._"

        # Log verbose info for debugging
        num_modules = len(modules_data)
        prompt_chars = len(prompt)
        estimated_tokens = prompt_chars // 4  # Rough estimate: 4 chars per token
        model_name = getattr(self.llm_service, 'model', 'unknown')

        logger.info(
            f"Generating {summary_type} codebase summary: {num_modules} modules, "
            f"{prompt_chars} chars (~{estimated_tokens} tokens), "
            f"model={model_name}"
        )

        # Retry loop for empty LLM responses
        last_error_msg = ""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await self.llm_service._complete(prompt)

                # Log response details
                if hasattr(response, 'prompt_tokens') and response.prompt_tokens:
                    logger.info(
                        f"LLM response: prompt_tokens={response.prompt_tokens}, "
                        f"completion_tokens={response.completion_tokens}, "
                        f"content_length={len(response.content) if response.content else 0}"
                    )

                if response.content:
                    # Success - add header and return
                    header = f"# {project_name} - Codebase Summary\n\n"
                    header += f"{header_subtitle}\n\n"
                    header += "---\n\n"
                    return header + response.content.strip()

                # Empty response - check for error details
                if hasattr(response, "metadata") and response.metadata:
                    last_error_msg = response.metadata.get("error", "")

                if attempt < self.MAX_RETRIES:
                    if last_error_msg:
                        logger.warning(f"Empty LLM response for codebase summary: {last_error_msg} (attempt {attempt}/{self.MAX_RETRIES}, retrying...)")
                    else:
                        logger.warning(f"Empty LLM response for codebase summary (attempt {attempt}/{self.MAX_RETRIES}, retrying...)")
                    await asyncio.sleep(self.RETRY_DELAY)
                else:
                    # Final attempt failed
                    if last_error_msg:
                        logger.warning(f"Empty LLM response for codebase summary: {last_error_msg} (all {self.MAX_RETRIES} attempts failed)")
                    else:
                        logger.warning(
                            f"Empty LLM response for codebase summary (all {self.MAX_RETRIES} attempts failed). "
                            f"Prompt size: {prompt_chars} chars (~{estimated_tokens} tokens). "
                            f"Model: {model_name}. Check API key, rate limits, or token limits."
                        )

            except Exception as e:
                if attempt < self.MAX_RETRIES:
                    logger.warning(f"Failed to generate codebase summary: {e} (attempt {attempt}/{self.MAX_RETRIES}, retrying...)")
                    await asyncio.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"Failed to generate codebase summary: {e} (all {self.MAX_RETRIES} attempts failed)", exc_info=True)

        # All retries exhausted
        return None

    def _collect_module_data(self, by_file_dir: Path) -> dict:
        """Collect and organize module data from by-file JSONs.

        Args:
            by_file_dir: Path to symbols/by-file directory.

        Returns:
            Dict mapping module path to file data.
        """
        modules = defaultdict(list)

        for json_file in by_file_dir.glob("*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                file_path = data.get("file", "")
                if not file_path:
                    continue

                # Determine module from file path
                parts = file_path.split("/")
                if len(parts) > 1:
                    # Use first directory as module
                    module = parts[0]
                    if len(parts) > 2:
                        # Include submodule
                        module = "/".join(parts[:2])
                else:
                    module = "(root)"

                modules[module].append({
                    "file": file_path,
                    "documentation": data.get("documentation"),
                    "classes": [
                        {
                            "name": s.get("name"),
                            "documentation": s.get("documentation"),
                        }
                        for s in data.get("symbols", [])
                        if s.get("type") == "class"
                    ],
                    "functions": [
                        {
                            "name": s.get("name"),
                            "documentation": s.get("documentation"),
                        }
                        for s in data.get("symbols", [])
                        if s.get("type") in ("function", "method")
                        and not s.get("name", "").startswith("_")
                    ][:5],  # Limit functions per file
                })

            except Exception as e:
                logger.debug(f"Error reading {json_file}: {e}")

        return dict(modules)

    def _collect_module_data_from_index(self, index_file: Path) -> dict:
        """Collect and organize module data from symbols/index.json.

        This is a fallback for when by-file directory doesn't exist.

        Args:
            index_file: Path to symbols/index.json file.

        Returns:
            Dict mapping module path to file data.
        """
        modules = defaultdict(list)

        try:
            with open(index_file) as f:
                data = json.load(f)

            symbols = data.get("symbols", [])

            # Group symbols by file
            files_data = defaultdict(lambda: {"classes": [], "functions": []})

            for sym in symbols:
                file_path = sym.get("file", "")
                if not file_path:
                    continue

                sym_type = sym.get("type", "")
                sym_name = sym.get("name", "")

                if sym_type == "class":
                    files_data[file_path]["classes"].append({
                        "name": sym_name,
                        "documentation": None,  # No documentation in index
                    })
                elif sym_type in ("function", "method") and not sym_name.startswith("_"):
                    files_data[file_path]["functions"].append({
                        "name": sym_name,
                        "documentation": None,
                    })

            # Organize by module
            for file_path, file_data in files_data.items():
                # Determine module from file path
                parts = file_path.split("/")
                if len(parts) > 1:
                    module = parts[0]
                    if len(parts) > 2:
                        module = "/".join(parts[:2])
                else:
                    module = "(root)"

                modules[module].append({
                    "file": file_path,
                    "documentation": None,
                    "classes": file_data["classes"][:5],  # Limit
                    "functions": file_data["functions"][:5],  # Limit
                })

        except Exception as e:
            logger.error(f"Error reading index.json: {e}")

        return dict(modules)

    def _format_modules_info(self, modules_data: dict) -> str:
        """Format module data for LLM prompt.

        Args:
            modules_data: Dict of module -> file data.

        Returns:
            Formatted string for prompt.
        """
        lines = []

        for module, files in sorted(modules_data.items()):
            lines.append(f"### Module: {module}")
            lines.append(f"Files: {len(files)}")
            lines.append("")

            for file_data in files[:10]:  # Limit files per module
                file_path = file_data["file"]
                file_doc = file_data.get("documentation") or "No documentation"
                lines.append(f"**{file_path}**")
                lines.append(f"  {file_doc[:200]}..." if len(file_doc) > 200 else f"  {file_doc}")

                # Add classes
                for cls in file_data.get("classes", [])[:5]:
                    cls_name = cls.get("name", "")
                    cls_doc = cls.get("documentation") or "No documentation"
                    cls_doc_short = cls_doc[:100] + "..." if len(cls_doc) > 100 else cls_doc
                    lines.append(f"  - class **{cls_name}**: {cls_doc_short}")

                # Add key functions
                funcs = file_data.get("functions", [])[:3]
                if funcs:
                    func_names = [f.get("name", "") for f in funcs]
                    lines.append(f"  - functions: {', '.join(func_names)}")

                lines.append("")

            lines.append("")

        return "\n".join(lines)

    async def generate_and_save(
        self,
        repo_ctx_path: Path,
        project_name: str = "Project",
        output_filename: str = "CODEBASE_SUMMARY.md",
        summary_type: SummaryType = "business",
    ) -> Optional[Path]:
        """Generate summary and save to file.

        Args:
            repo_ctx_path: Path to .repo-ctx directory.
            project_name: Name of the project.
            output_filename: Output filename.
            summary_type: Type of summary - "business" (default) or "technical".

        Returns:
            Path to generated file or None.
        """
        summary = await self.generate_summary(
            repo_ctx_path,
            project_name,
            summary_type=summary_type,
        )
        if not summary:
            return None

        output_path = repo_ctx_path / output_filename
        output_path.write_text(summary, encoding="utf-8")
        logger.info(f"Generated {summary_type} codebase summary: {output_path}")
        return output_path

    async def generate_raw_summary(
        self,
        repo_ctx_path: Path,
        project_name: str = "Project",
        summary_type: SummaryType = "business",
    ) -> Optional[str]:
        """Generate summary content without header (for embedding in llms.txt).

        Args:
            repo_ctx_path: Path to .repo-ctx directory.
            project_name: Name of the project.
            summary_type: Type of summary - "business" (default) or "technical".

        Returns:
            Raw summary content from LLM or None if generation fails.
        """
        if not self.llm_service:
            logger.warning("No LLM service - cannot generate summary")
            return None

        # Try to load enhanced file data from by-file directory
        by_file_dir = repo_ctx_path / "symbols" / "by-file"
        if by_file_dir.exists():
            modules_data = self._collect_module_data(by_file_dir)
        else:
            # Fallback: use symbols/index.json
            logger.info("Using symbols/index.json for codebase summary (by-file not available)")
            index_file = repo_ctx_path / "symbols" / "index.json"
            if index_file.exists():
                modules_data = self._collect_module_data_from_index(index_file)
            else:
                logger.warning("No symbol data found - neither by-file nor index.json")
                return None

        if not modules_data:
            logger.warning("No module data collected")
            return None

        # Build context for LLM based on summary type
        if summary_type == "business":
            modules_info = self._format_modules_for_business(modules_data)
            readme_content = self._read_readme(repo_ctx_path)
            prompt = BUSINESS_SUMMARY_PROMPT.format(
                project_name=project_name,
                readme_content=readme_content,
                modules_info=modules_info,
            )
        else:
            modules_info = self._format_modules_info(modules_data)
            if len(modules_info) > self.MAX_CONTEXT_CHARS:
                modules_info = modules_info[:self.MAX_CONTEXT_CHARS] + "\n\n... [truncated]"
            prompt = TECHNICAL_SUMMARY_PROMPT.format(modules_info=modules_info)

        # Log verbose info
        num_modules = len(modules_data)
        prompt_chars = len(prompt)
        estimated_tokens = prompt_chars // 4
        model_name = getattr(self.llm_service, 'model', 'unknown')

        logger.info(
            f"Generating {summary_type} codebase summary for llms.txt: {num_modules} modules, "
            f"{prompt_chars} chars (~{estimated_tokens} tokens), model={model_name}"
        )

        # Retry loop for empty LLM responses
        last_error_msg = ""
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                response = await self.llm_service._complete(prompt)

                if response.content:
                    return response.content.strip()

                # Empty response - check for error details
                if hasattr(response, "metadata") and response.metadata:
                    last_error_msg = response.metadata.get("error", "")

                if attempt < self.MAX_RETRIES:
                    if last_error_msg:
                        logger.warning(f"Empty LLM response for codebase summary: {last_error_msg} (attempt {attempt}/{self.MAX_RETRIES}, retrying...)")
                    else:
                        logger.warning(f"Empty LLM response for codebase summary (attempt {attempt}/{self.MAX_RETRIES}, retrying...)")
                    await asyncio.sleep(self.RETRY_DELAY)
                else:
                    if last_error_msg:
                        logger.warning(f"Empty LLM response for codebase summary: {last_error_msg} (all {self.MAX_RETRIES} attempts failed)")
                    else:
                        logger.warning(f"Empty LLM response for codebase summary (all {self.MAX_RETRIES} attempts failed)")

            except Exception as e:
                if attempt < self.MAX_RETRIES:
                    logger.warning(f"Failed to generate codebase summary: {e} (attempt {attempt}/{self.MAX_RETRIES}, retrying...)")
                    await asyncio.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"Failed to generate codebase summary: {e} (all {self.MAX_RETRIES} attempts failed)")

        return None

    def update_llms_txt(
        self,
        llms_txt_path: Path,
        business_summary: str,
    ) -> bool:
        """Update llms.txt with business summary section.

        Inserts the business summary after the git info/header section.

        Args:
            llms_txt_path: Path to llms.txt file.
            business_summary: Business summary content to insert.

        Returns:
            True if updated successfully, False otherwise.
        """
        if not llms_txt_path.exists():
            logger.warning(f"llms.txt not found: {llms_txt_path}")
            return False

        try:
            content = llms_txt_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            # Find insertion point (after git info, before first major section)
            insert_idx = 0
            for i, line in enumerate(lines):
                # Skip header and git info lines
                if line.startswith("> ") or line.startswith("# ") or not line.strip():
                    insert_idx = i + 1
                    continue
                # Stop at first content section
                if line.startswith("## ") or (line.strip() and not line.startswith(">")):
                    break

            # Build the business summary section
            summary_section = [
                "## Business Summary",
                "",
                "_LLM-generated overview for stakeholders._",
                "",
                business_summary,
                "",
                "---",
                "",
            ]

            # Insert the summary
            new_lines = lines[:insert_idx] + summary_section + lines[insert_idx:]
            new_content = "\n".join(new_lines)

            llms_txt_path.write_text(new_content, encoding="utf-8")
            logger.info("Updated llms.txt with business summary")
            return True

        except Exception as e:
            logger.error(f"Failed to update llms.txt: {e}")
            return False
