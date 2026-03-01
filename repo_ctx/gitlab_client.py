"""GitLab API client."""
import gitlab
import base64
from typing import Optional
import json


class GitLabClient:
    def __init__(self, url: str, token: str):
        self.gl = gitlab.Gitlab(url, private_token=token)
    
    def get_project(self, group: str, project: str):
        """Get project by group/project path."""
        return self.gl.projects.get(f"{group}/{project}")
    
    def get_group(self, group_path: str):
        """Get group by path."""
        return self.gl.groups.get(group_path)
    
    def list_group_projects(self, group_path: str, include_subgroups: bool = True) -> list[dict]:
        """List all projects in a group."""
        group = self.get_group(group_path)
        projects = group.projects.list(all=True, include_subgroups=include_subgroups)
        return [{"path": p.path_with_namespace} for p in projects]
    
    def get_file_tree(self, project, ref: str = "main") -> list[dict]:
        """Get repository file tree."""
        try:
            return project.repository_tree(ref=ref, recursive=True, all=True)
        except gitlab.exceptions.GitlabGetError:
            # Try master if main doesn't exist
            return project.repository_tree(ref="master", recursive=True, all=True)
    
    def read_file(self, project, path: str, ref: str) -> str:
        """Read file content."""
        file_data = project.files.get(file_path=path, ref=ref)
        content = file_data.content
        if file_data.encoding == 'base64':
            content = base64.b64decode(content).decode('utf-8')
        return content
    
    def get_tags(self, project) -> list[str]:
        """Get repository tags."""
        return [tag.name for tag in project.tags.list(all=True)]
    
    def get_default_branch(self, project) -> str:
        """Get default branch."""
        return project.default_branch
    
    def read_config(self, project, ref: str) -> Optional[dict]:
        """Read git_context.json if exists."""
        try:
            content = self.read_file(project, "git_context.json", ref)
            return json.loads(content)
        except:
            return None
