"""
Context Manager - Persistent Project Knowledge System
Stores and retrieves project context across sessions for perfect continuity
"""
import json
import os
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib


@dataclass
class ProjectContext:
    """Complete project context for continuity"""
    project_id: str
    project_name: str
    project_path: str
    repository_url: Optional[str] = None
    
    # Analysis results
    analyzed_at: float = 0
    codebase_structure: Dict[str, Any] = field(default_factory=dict)
    features_found: List[Dict[str, Any]] = field(default_factory=list)
    gaps_identified: List[Dict[str, Any]] = field(default_factory=list)
    
    # Domain knowledge
    domain_knowledge: Dict[str, Any] = field(default_factory=dict)
    industry_standards: Dict[str, Any] = field(default_factory=dict)
    requirements: Dict[str, Any] = field(default_factory=dict)
    
    # Technical details
    tech_stack: List[str] = field(default_factory=list)
    dependencies: Dict[str, str] = field(default_factory=dict)
    database_schema: Dict[str, Any] = field(default_factory=dict)
    api_endpoints: List[Dict[str, Any]] = field(default_factory=list)
    
    # Completion tracking
    completion_percentage: float = 0.0
    total_features: int = 0
    completed_features: int = 0
    missing_features: List[str] = field(default_factory=list)
    
    # Metadata
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectContext':
        """Create from dictionary"""
        return cls(**data)


class ContextManager:
    """
    Manages persistent project context for perfect continuity
    
    Features:
    - Save/load project knowledge
    - Track analysis results
    - Store domain understanding
    - Maintain completion state
    - Version control
    """
    
    def __init__(self, storage_dir: str = "context_storage"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self._cache: Dict[str, ProjectContext] = {}
    
    def _get_context_path(self, project_id: str) -> str:
        """Get file path for project context"""
        return os.path.join(self.storage_dir, f"{project_id}.json")
    
    def _generate_project_id(self, project_path: str) -> str:
        """Generate unique project ID from path"""
        return hashlib.md5(project_path.encode()).hexdigest()[:16]
    
    def save_context(self, context_or_id) -> bool:
        """
        Save project context to disk
        
        Args:
            context_or_id: ProjectContext object OR project_id string
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Handle both ProjectContext object and project_id string
            if isinstance(context_or_id, str):
                # It's a project_id, load from cache
                context = self._cache.get(context_or_id)
                if not context:
                    print(f"Warning: No context found for project_id: {context_or_id}")
                    return False
            else:
                # It's a ProjectContext object
                context = context_or_id
            
            context.last_updated = time.time()
            context.version += 1
            
            file_path = self._get_context_path(context.project_id)
            
            with open(file_path, 'w') as f:
                json.dump(context.to_dict(), f, indent=2)
            
            # Update cache
            self._cache[context.project_id] = context
            
            return True
        
        except Exception as e:
            print(f"Error saving context: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_context(self, project_id: str) -> Optional[ProjectContext]:
        """
        Load project context from disk
        
        Args:
            project_id: Unique project identifier
        
        Returns:
            ProjectContext if found, None otherwise
        """
        # Check cache first
        if project_id in self._cache:
            return self._cache[project_id]
        
        try:
            file_path = self._get_context_path(project_id)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            context = ProjectContext.from_dict(data)
            
            # Update cache
            self._cache[project_id] = context
            
            return context
        
        except Exception as e:
            print(f"Error loading context: {e}")
            return None
    
    def create_context(
        self,
        project_name: str,
        project_path: str,
        repository_url: Optional[str] = None
    ) -> ProjectContext:
        """
        Create new project context
        
        Args:
            project_name: Human-readable project name
            project_path: Absolute path to project
            repository_url: Optional GitHub repository URL
        
        Returns:
            New ProjectContext object
        """
        project_id = self._generate_project_id(project_path)
        
        context = ProjectContext(
            project_id=project_id,
            project_name=project_name,
            project_path=project_path,
            repository_url=repository_url
        )
        
        self.save_context(context)
        
        return context
    
    def update_context(
        self,
        project_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update specific fields in project context
        
        Args:
            project_id: Project identifier
            updates: Dictionary of fields to update
        
        Returns:
            True if successful, False otherwise
        """
        context = self.load_context(project_id)
        
        if not context:
            print(f"Context not found for project: {project_id}")
            return False
        
        # Update fields
        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
        
        return self.save_context(context)
    
    def update_analysis(
        self,
        project_id: str,
        codebase_structure: Dict[str, Any],
        features_found: List[Dict[str, Any]],
        gaps_identified: List[Dict[str, Any]]
    ) -> bool:
        """
        Update analysis results
        
        Args:
            project_id: Project identifier
            codebase_structure: Analyzed code structure
            features_found: List of existing features
            gaps_identified: List of missing features
        
        Returns:
            True if successful
        """
        return self.update_context(project_id, {
            'analyzed_at': time.time(),
            'codebase_structure': codebase_structure,
            'features_found': features_found,
            'gaps_identified': gaps_identified
        })
    
    def update_completion(
        self,
        project_id: str,
        completed_features: int,
        total_features: int
    ) -> bool:
        """
        Update completion tracking
        
        Args:
            project_id: Project identifier
            completed_features: Number of completed features
            total_features: Total number of features
        
        Returns:
            True if successful
        """
        completion_percentage = (completed_features / total_features * 100) if total_features > 0 else 0
        
        return self.update_context(project_id, {
            'completed_features': completed_features,
            'total_features': total_features,
            'completion_percentage': completion_percentage
        })
    
    def add_domain_knowledge(
        self,
        project_id: str,
        knowledge_type: str,
        knowledge: Dict[str, Any]
    ) -> bool:
        """
        Add domain knowledge to context
        
        Args:
            project_id: Project identifier
            knowledge_type: Type of knowledge (e.g., 'coaching', 'wellness')
            knowledge: Knowledge data
        
        Returns:
            True if successful
        """
        context = self.load_context(project_id)
        
        if not context:
            return False
        
        context.domain_knowledge[knowledge_type] = knowledge
        
        return self.save_context(context)
    
    def get_project_by_path(self, project_path: str) -> Optional[ProjectContext]:
        """
        Get project context by path
        
        Args:
            project_path: Project directory path
        
        Returns:
            ProjectContext if found
        """
        project_id = self._generate_project_id(project_path)
        return self.load_context(project_id)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all stored projects
        
        Returns:
            List of project summaries
        """
        projects = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                project_id = filename[:-5]  # Remove .json
                context = self.load_context(project_id)
                
                if context:
                    projects.append({
                        'project_id': context.project_id,
                        'project_name': context.project_name,
                        'project_path': context.project_path,
                        'completion_percentage': context.completion_percentage,
                        'last_updated': datetime.fromtimestamp(context.last_updated).isoformat(),
                        'version': context.version
                    })
        
        return sorted(projects, key=lambda x: x['last_updated'], reverse=True)
    
    def delete_context(self, project_id: str) -> bool:
        """
        Delete project context
        
        Args:
            project_id: Project identifier
        
        Returns:
            True if successful
        """
        try:
            file_path = self._get_context_path(project_id)
            
            if os.path.exists(file_path):
                os.remove(file_path)
            
            if project_id in self._cache:
                del self._cache[project_id]
            
            return True
        
        except Exception as e:
            print(f"Error deleting context: {e}")
            return False
    
    def export_context(self, project_id: str, output_path: str) -> bool:
        """
        Export context to external file
        
        Args:
            project_id: Project identifier
            output_path: Path to export file
        
        Returns:
            True if successful
        """
        context = self.load_context(project_id)
        
        if not context:
            return False
        
        try:
            with open(output_path, 'w') as f:
                json.dump(context.to_dict(), f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error exporting context: {e}")
            return False
    
    def import_context(self, input_path: str) -> Optional[str]:
        """
        Import context from external file
        
        Args:
            input_path: Path to import file
        
        Returns:
            Project ID if successful, None otherwise
        """
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
            
            context = ProjectContext.from_dict(data)
            
            if self.save_context(context):
                return context.project_id
            
            return None
        
        except Exception as e:
            print(f"Error importing context: {e}")
            return None


# Global context manager instance
context_manager = ContextManager()


if __name__ == "__main__":
    # Example usage
    manager = ContextManager()
    
    # Create new project context
    context = manager.create_context(
        project_name="Just Talk",
        project_path="/home/ubuntu/just-talk-standalone",
        repository_url="https://github.com/user/just-talk"
    )
    
    print(f"Created context for project: {context.project_name}")
    print(f"Project ID: {context.project_id}")
    
    # Update analysis
    manager.update_analysis(
        project_id=context.project_id,
        codebase_structure={
            "pages": ["Home", "Chat", "Admin"],
            "components": ["AIChatBox", "DashboardLayout"],
            "api": ["auth", "chat", "admin"]
        },
        features_found=[
            {"name": "AI Chat", "status": "complete"},
            {"name": "Admin Dashboard", "status": "complete"}
        ],
        gaps_identified=[
            {"name": "Voice AI", "priority": "high"},
            {"name": "Subscription Management", "priority": "high"}
        ]
    )
    
    # Update completion
    manager.update_completion(
        project_id=context.project_id,
        completed_features=8,
        total_features=10
    )
    
    # Add domain knowledge
    manager.add_domain_knowledge(
        project_id=context.project_id,
        knowledge_type="coaching",
        knowledge={
            "industry": "emotional_support",
            "target_audience": "individuals_seeking_support",
            "key_features": ["24/7_availability", "crisis_detection", "voice_support"]
        }
    )
    
    # Load context
    loaded_context = manager.load_context(context.project_id)
    print(f"\nLoaded context: {loaded_context.project_name}")
    print(f"Completion: {loaded_context.completion_percentage:.1f}%")
    print(f"Features: {loaded_context.completed_features}/{loaded_context.total_features}")
    
    # List all projects
    print("\nAll projects:")
    for project in manager.list_projects():
        print(f"  - {project['project_name']}: {project['completion_percentage']:.1f}%")
    
    # Export context
    export_path = "/tmp/just_talk_context.json"
    if manager.export_context(context.project_id, export_path):
        print(f"\nContext exported to: {export_path}")
