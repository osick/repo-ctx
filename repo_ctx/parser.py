"""Documentation parser."""
import re
from typing import Optional
from markdown_it import MarkdownIt


class Parser:
    def __init__(self):
        self.md = MarkdownIt()
    
    def should_include_file(self, path: str, config: Optional[dict] = None) -> bool:
        """Check if file should be included based on config."""
        # Default: include markdown and text files
        if not any(path.endswith(ext) for ext in ['.md', '.rst', '.txt', '.markdown']):
            return False
        
        if not config:
            return True
        
        # Check exclude patterns
        exclude_folders = config.get("excludeFolders", [])
        for folder in exclude_folders:
            if f"/{folder}/" in path or path.startswith(f"{folder}/"):
                return False
        
        exclude_files = config.get("excludeFiles", [])
        if any(path.endswith(f) for f in exclude_files):
            return False
        
        # Check include patterns
        folders = config.get("folders", [])
        if folders:
            return any(f"/{folder}/" in path or path.startswith(f"{folder}/") for folder in folders)
        
        return True
    
    def parse_markdown(self, content: str) -> str:
        """Parse markdown and return formatted content."""
        # For MVP, just return content as-is
        # Could enhance with better formatting later
        return content
    
    def extract_snippets(self, content: str) -> list[dict]:
        """Extract code snippets from markdown."""
        snippets = []
        # Match code blocks: ```language\ncode\n```
        pattern = r'```(\w+)?\n(.*?)```'
        matches = re.finditer(pattern, content, re.DOTALL)
        
        for match in matches:
            language = match.group(1) or "text"
            code = match.group(2).strip()
            snippets.append({
                "language": language,
                "code": code
            })
        
        return snippets
    
    def count_tokens(self, content: str) -> int:
        """Rough token count estimation."""
        # Simple estimation: ~4 chars per token
        return len(content) // 4
    
    def format_for_llm(self, documents: list, library_id: str) -> str:
        """Format documents for LLM consumption."""
        output = []
        for doc in documents:
            output.append(f"### {doc.file_path}\n")
            output.append(f"Source: {library_id}/{doc.file_path}\n\n")
            output.append(doc.content)
            output.append("\n\n" + "-" * 32 + "\n\n")
        
        return "".join(output)
