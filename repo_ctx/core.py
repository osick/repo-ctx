"""Core business logic."""
from typing import Optional
from .config import Config
from .gitlab_client import GitLabClient
from .storage import Storage
from .parser import Parser
from .models import Library, Version, Document, SearchResult


class GitLabContext:
    def __init__(self, config: Config):
        self.gitlab = GitLabClient(config.gitlab_url, config.gitlab_token)
        self.storage = Storage(config.storage_path)
        self.parser = Parser()
    
    async def init(self):
        """Initialize storage."""
        await self.storage.init_db()
    
    async def search_libraries(self, query: str) -> list[SearchResult]:
        """Search for libraries by name."""
        results = await self.storage.search(query)
        # Simple ranking: exact matches first
        for result in results:
            if query.lower() in result.name.lower():
                result.score = 2.0
            if query.lower() == result.name.lower():
                result.score = 3.0
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    async def fuzzy_search_libraries(self, query: str, limit: int = 10) -> list:
        """Fuzzy search for libraries."""
        return await self.storage.fuzzy_search(query, limit)
    
    async def get_documentation(
        self, 
        library_id: str, 
        topic: Optional[str] = None,
        page: int = 1
    ) -> dict:
        """Get documentation for a library."""
        # Parse library_id: /group/project or /group/subgroup/project or /group/project/version
        parts = library_id.strip("/").split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid library_id: {library_id}")
        
        # Check if last part is a version (exists in versions table)
        # For now, assume last part is project, second-to-last might be version
        # Simple heuristic: if we have more than 2 parts, last could be version
        project = parts[-1]
        group = "/".join(parts[:-1])
        version = None
        
        # Try to get library with full path first
        library = await self.storage.get_library(group, project)
        
        # If not found and we have 3+ parts, try treating last as version
        if not library and len(parts) >= 3:
            version = parts[-1]
            project = parts[-2]
            group = "/".join(parts[:-2])
            library = await self.storage.get_library(group, project)
        if not library:
            raise ValueError(f"Library not found: {group}/{project}")
        
        # Use default version if not specified
        if not version:
            version = library.default_version
        
        # Get version_id
        version_id = await self.storage.get_version_id(library.id, version)
        if not version_id:
            raise ValueError(f"Version not found: {version}")
        
        # Get documents
        documents = await self.storage.get_documents(version_id, topic, page)
        
        # Format for LLM
        content = self.parser.format_for_llm(documents, library_id)
        
        return {
            "content": [{"type": "text", "text": content}],
            "metadata": {
                "library": f"{group}/{project}",
                "version": version,
                "page": page,
                "documents_count": len(documents)
            }
        }
    
    async def index_repository(self, group: str, project: str):
        """Index a GitLab repository."""
        # Get project
        proj = self.gitlab.get_project(group, project)
        
        # Get default branch
        default_branch = self.gitlab.get_default_branch(proj)
        
        # Read git_context.json if exists
        config = self.gitlab.read_config(proj, default_branch)
        
        # Get project description
        description = config.get("description", proj.description) if config else proj.description
        
        # Save library
        library = Library(
            group_name=group,
            project_name=project,
            description=description or "",
            default_version=default_branch
        )
        library_id = await self.storage.save_library(library)
        
        # Index default branch
        await self._index_version(proj, library_id, default_branch, config)
        
        # Index tags
        tags = self.gitlab.get_tags(proj)
        for tag in tags[:5]:  # Limit to 5 most recent tags for MVP
            await self._index_version(proj, library_id, tag, config)
    
    async def index_group(self, group_path: str, include_subgroups: bool = True) -> dict:
        """Index all projects in a GitLab group."""
        projects = self.gitlab.list_group_projects(group_path, include_subgroups)
        
        results = {
            "total": len(projects),
            "indexed": [],
            "failed": []
        }
        
        for proj_info in projects:
            path = proj_info["path"]
            parts = path.split("/")
            if len(parts) < 2:
                continue
            
            project = parts[-1]
            group = "/".join(parts[:-1])
            
            try:
                await self.index_repository(group, project)
                results["indexed"].append(path)
            except Exception as e:
                results["failed"].append({"path": path, "error": str(e)})
        
        return results
    
    async def _index_version(self, project, library_id: int, ref: str, config: Optional[dict]):
        """Index a specific version."""
        # Get commit SHA
        commit = project.commits.get(ref)
        
        # Save version
        version = Version(
            library_id=library_id,
            version_tag=ref,
            commit_sha=commit.id
        )
        version_id = await self.storage.save_version(version)
        
        # Get file tree
        tree = self.gitlab.get_file_tree(project, ref)
        
        # Filter and process files
        for item in tree:
            if item['type'] != 'blob':
                continue
            
            path = item['path']
            if not self.parser.should_include_file(path, config):
                continue
            
            # Read file content
            try:
                content = self.gitlab.read_file(project, path, ref)
                parsed_content = self.parser.parse_markdown(content)
                tokens = self.parser.count_tokens(parsed_content)
                
                # Save document
                doc = Document(
                    version_id=version_id,
                    file_path=path,
                    content=parsed_content,
                    tokens=tokens
                )
                await self.storage.save_document(doc)
            except Exception as e:
                # Skip files that can't be read
                print(f"Warning: Could not read {path}: {e}")
                continue
