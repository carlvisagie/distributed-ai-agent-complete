"""
Knowledge Graph - Codebase Understanding and Relationship Mapping
Maps components, dependencies, and relationships for perfect continuity
"""
import json
import os
import re
from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field, asdict
from pathlib import Path
from enum import Enum


class ComponentType(Enum):
    """Types of code components"""
    PAGE = "page"
    COMPONENT = "component"
    API = "api"
    DATABASE = "database"
    UTILITY = "utility"
    CONFIG = "config"
    TEST = "test"


class ComponentStatus(Enum):
    """Component completion status"""
    COMPLETE = "complete"
    INCOMPLETE = "incomplete"
    BROKEN = "broken"
    DEPRECATED = "deprecated"


@dataclass
class Component:
    """Code component with relationships"""
    component_id: str
    name: str
    path: str
    component_type: str
    
    # Status
    status: str = ComponentStatus.INCOMPLETE.value
    completion_percentage: float = 0.0
    
    # Relationships
    depends_on: List[str] = field(default_factory=list)  # Component IDs this depends on
    used_by: List[str] = field(default_factory=list)     # Component IDs that use this
    imports: List[str] = field(default_factory=list)     # Import statements
    exports: List[str] = field(default_factory=list)     # Export statements
    
    # Metadata
    file_size: int = 0
    lines_of_code: int = 0
    last_modified: float = 0
    description: str = ""
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Component':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class Feature:
    """High-level feature with component mapping"""
    feature_id: str
    name: str
    description: str
    
    # Status
    status: str = ComponentStatus.INCOMPLETE.value
    priority: str = "medium"
    completion_percentage: float = 0.0
    
    # Components
    components: List[str] = field(default_factory=list)  # Component IDs
    missing_components: List[str] = field(default_factory=list)
    
    # Requirements
    requirements: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Feature':
        """Create from dictionary"""
        return cls(**data)


class KnowledgeGraph:
    """
    Knowledge graph for codebase understanding
    
    Features:
    - Map all components
    - Track dependencies
    - Identify relationships
    - Find affected components
    - Analyze impact of changes
    """
    
    def __init__(self, storage_file: str = "knowledge_graph.json"):
        self.storage_file = storage_file
        self.components: Dict[str, Component] = {}
        self.features: Dict[str, Feature] = {}
        self.load()
    
    def save(self) -> bool:
        """Save knowledge graph to disk"""
        try:
            data = {
                'components': {
                    cid: comp.to_dict()
                    for cid, comp in self.components.items()
                },
                'features': {
                    fid: feat.to_dict()
                    for fid, feat in self.features.items()
                }
            }
            
            with open(self.storage_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error saving knowledge graph: {e}")
            return False
    
    def save_to_file(self, filepath: Optional[str] = None) -> bool:
        """Alias for save() for compatibility"""
        if filepath and filepath != self.storage_file:
            old_file = self.storage_file
            self.storage_file = filepath
            result = self.save()
            self.storage_file = old_file
            return result
        return self.save()
    
    def load(self) -> bool:
        """Load knowledge graph from disk"""
        if not os.path.exists(self.storage_file):
            return False
        
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
            
            self.components = {
                cid: Component.from_dict(comp_data)
                for cid, comp_data in data.get('components', {}).items()
            }
            
            self.features = {
                fid: Feature.from_dict(feat_data)
                for fid, feat_data in data.get('features', {}).items()
            }
            
            return True
        
        except Exception as e:
            print(f"Error loading knowledge graph: {e}")
            return False
    
    def add_component(self, component: Component) -> bool:
        """Add or update component"""
        self.components[component.component_id] = component
        return self.save()
    
    def get_component(self, component_id: str) -> Optional[Component]:
        """Get component by ID"""
        return self.components.get(component_id)
    
    def add_feature(self, feature: Feature) -> bool:
        """Add or update feature"""
        self.features[feature.feature_id] = feature
        return self.save()
    
    def get_feature(self, feature_id: str) -> Optional[Feature]:
        """Get feature by ID"""
        return self.features.get(feature_id)
    
    def build_from_codebase(self, project_path: str) -> bool:
        """
        Analyze codebase and build knowledge graph
        
        Args:
            project_path: Path to project directory
        
        Returns:
            True if successful
        """
        try:
            project_path = Path(project_path)
            
            # Find all source files
            source_files = []
            for ext in ['*.tsx', '*.ts', '*.jsx', '*.js', '*.py']:
                source_files.extend(project_path.rglob(ext))
            
            # Filter out ignored paths
            filtered_files = []
            ignore_patterns = [
                'node_modules', '.git', 'dist', 'build', '.next', 
                'coverage', '.cache', 'tmp', 'temp', '.venv', 'venv',
                '__pycache__', '.pytest_cache', '.mypy_cache'
            ]
            
            for file_path in source_files:
                # Check if any ignore pattern is in the path
                path_str = str(file_path)
                if not any(pattern in path_str for pattern in ignore_patterns):
                    filtered_files.append(file_path)
            
            print(f"   Found {len(source_files)} files, analyzing {len(filtered_files)} (filtered {len(source_files) - len(filtered_files)})")
            
            # Analyze each file
            for file_path in filtered_files:
                self._analyze_file(file_path, project_path)
            
            # Build dependency relationships
            self._build_relationships()
            
            return self.save()
        
        except Exception as e:
            print(f"Error building knowledge graph: {e}")
            return False
    
    def _analyze_file(self, file_path: Path, project_root: Path):
        """Analyze a single file"""
        try:
            relative_path = file_path.relative_to(project_root)
            component_id = str(relative_path).replace('/', '_').replace('\\', '_')
            
            # Determine component type
            component_type = self._determine_type(file_path)
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract imports
            imports = self._extract_imports(content, file_path.suffix)
            
            # Extract exports
            exports = self._extract_exports(content, file_path.suffix)
            
            # Get file stats
            stats = file_path.stat()
            lines = content.count('\n') + 1
            
            # Create component
            component = Component(
                component_id=component_id,
                name=file_path.stem,
                path=str(relative_path),
                component_type=component_type.value,
                imports=imports,
                exports=exports,
                file_size=stats.st_size,
                lines_of_code=lines,
                last_modified=stats.st_mtime
            )
            
            self.components[component_id] = component
        
        except Exception as e:
            print(f"Error analyzing file {file_path}: {e}")
    
    def _determine_type(self, file_path: Path) -> ComponentType:
        """Determine component type from path"""
        path_str = str(file_path).lower()
        
        if 'pages' in path_str or 'routes' in path_str:
            return ComponentType.PAGE
        elif 'components' in path_str:
            return ComponentType.COMPONENT
        elif 'api' in path_str or 'routers' in path_str:
            return ComponentType.API
        elif 'db' in path_str or 'database' in path_str or 'schema' in path_str:
            return ComponentType.DATABASE
        elif 'test' in path_str or 'spec' in path_str:
            return ComponentType.TEST
        elif 'config' in path_str or 'settings' in path_str:
            return ComponentType.CONFIG
        else:
            return ComponentType.UTILITY
    
    def _extract_imports(self, content: str, file_ext: str) -> List[str]:
        """Extract import statements"""
        imports = []
        
        if file_ext in ['.ts', '.tsx', '.js', '.jsx']:
            # JavaScript/TypeScript imports
            patterns = [
                r'import\s+.*\s+from\s+[\'"](.+)[\'"]',
                r'import\s+[\'"](.+)[\'"]',
                r'require\([\'"](.+)[\'"]\)'
            ]
            for pattern in patterns:
                imports.extend(re.findall(pattern, content))
        
        elif file_ext == '.py':
            # Python imports
            patterns = [
                r'from\s+(\S+)\s+import',
                r'import\s+(\S+)'
            ]
            for pattern in patterns:
                imports.extend(re.findall(pattern, content))
        
        return list(set(imports))  # Remove duplicates
    
    def _extract_exports(self, content: str, file_ext: str) -> List[str]:
        """Extract export statements"""
        exports = []
        
        if file_ext in ['.ts', '.tsx', '.js', '.jsx']:
            # JavaScript/TypeScript exports
            patterns = [
                r'export\s+(?:default\s+)?(?:const|let|var|function|class)\s+(\w+)',
                r'export\s+\{([^}]+)\}',
                r'export\s+default\s+(\w+)'
            ]
            for pattern in patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if isinstance(match, str):
                        exports.extend([m.strip() for m in match.split(',')])
        
        elif file_ext == '.py':
            # Python exports (functions and classes at module level)
            patterns = [
                r'^def\s+(\w+)',
                r'^class\s+(\w+)'
            ]
            for pattern in patterns:
                exports.extend(re.findall(pattern, content, re.MULTILINE))
        
        return list(set(exports))  # Remove duplicates
    
    def _build_relationships(self):
        """Build dependency relationships between components"""
        for comp_id, component in self.components.items():
            for import_path in component.imports:
                # Find matching component
                for other_id, other_comp in self.components.items():
                    if other_id != comp_id and self._matches_import(other_comp, import_path):
                        # Add dependency
                        if other_id not in component.depends_on:
                            component.depends_on.append(other_id)
                        
                        # Add reverse relationship
                        if comp_id not in other_comp.used_by:
                            other_comp.used_by.append(comp_id)
    
    def _matches_import(self, component: Component, import_path: str) -> bool:
        """Check if component matches import path"""
        # Simple matching - can be improved
        component_name = component.name.lower()
        import_name = import_path.split('/')[-1].lower()
        return component_name in import_name or import_name in component_name
    
    def get_dependencies(self, component_id: str, recursive: bool = False) -> List[Component]:
        """
        Get all dependencies of a component
        
        Args:
            component_id: Component identifier
            recursive: Include transitive dependencies
        
        Returns:
            List of Component objects
        """
        component = self.get_component(component_id)
        if not component:
            return []
        
        dependencies = []
        visited = set()
        
        def collect_deps(comp_id: str):
            if comp_id in visited:
                return
            visited.add(comp_id)
            
            comp = self.get_component(comp_id)
            if not comp:
                return
            
            for dep_id in comp.depends_on:
                dep = self.get_component(dep_id)
                if dep and dep not in dependencies:
                    dependencies.append(dep)
                    if recursive:
                        collect_deps(dep_id)
        
        collect_deps(component_id)
        return dependencies
    
    def get_dependents(self, component_id: str, recursive: bool = False) -> List[Component]:
        """
        Get all components that depend on this component
        
        Args:
            component_id: Component identifier
            recursive: Include transitive dependents
        
        Returns:
            List of Component objects
        """
        component = self.get_component(component_id)
        if not component:
            return []
        
        dependents = []
        visited = set()
        
        def collect_deps(comp_id: str):
            if comp_id in visited:
                return
            visited.add(comp_id)
            
            comp = self.get_component(comp_id)
            if not comp:
                return
            
            for dep_id in comp.used_by:
                dep = self.get_component(dep_id)
                if dep and dep not in dependents:
                    dependents.append(dep)
                    if recursive:
                        collect_deps(dep_id)
        
        collect_deps(component_id)
        return dependents
    
    def find_affected_components(self, component_id: str) -> List[Component]:
        """
        Find all components affected by changes to this component
        
        Args:
            component_id: Component identifier
        
        Returns:
            List of affected Component objects
        """
        # Get all components that depend on this one (recursively)
        return self.get_dependents(component_id, recursive=True)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge graph statistics"""
        total_components = len(self.components)
        total_features = len(self.features)
        
        # Count by type
        type_counts = {}
        for comp in self.components.values():
            type_counts[comp.component_type] = type_counts.get(comp.component_type, 0) + 1
        
        # Count by status
        status_counts = {}
        for comp in self.components.values():
            status_counts[comp.status] = status_counts.get(comp.status, 0) + 1
        
        # Calculate average dependencies
        total_deps = sum(len(comp.depends_on) for comp in self.components.values())
        avg_deps = total_deps / total_components if total_components > 0 else 0
        
        return {
            'total_components': total_components,
            'total_features': total_features,
            'components_by_type': type_counts,
            'components_by_status': status_counts,
            'average_dependencies': avg_deps,
            'total_dependencies': total_deps
        }
    
    def export_graph(self, output_path: str) -> bool:
        """Export knowledge graph to file"""
        try:
            with open(output_path, 'w') as f:
                json.dump({
                    'components': {cid: comp.to_dict() for cid, comp in self.components.items()},
                    'features': {fid: feat.to_dict() for fid, feat in self.features.items()}
                }, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting graph: {e}")
            return False


# Global knowledge graph instance
knowledge_graph = KnowledgeGraph()


if __name__ == "__main__":
    # Example usage
    graph = KnowledgeGraph("test_knowledge_graph.json")
    
    # Build from codebase
    project_path = "/home/ubuntu/just-talk-standalone"
    if os.path.exists(project_path):
        print("Building knowledge graph from codebase...")
        graph.build_from_codebase(project_path)
        
        # Get statistics
        stats = graph.get_statistics()
        print(f"\nKnowledge Graph Statistics:")
        print(f"  Total components: {stats['total_components']}")
        print(f"  Total features: {stats['total_features']}")
        print(f"  Average dependencies: {stats['average_dependencies']:.2f}")
        
        print(f"\nComponents by type:")
        for comp_type, count in stats['components_by_type'].items():
            print(f"  {comp_type}: {count}")
        
        # Find a component and its dependencies
        if graph.components:
            first_comp_id = list(graph.components.keys())[0]
            first_comp = graph.get_component(first_comp_id)
            print(f"\nExample component: {first_comp.name}")
            print(f"  Type: {first_comp.component_type}")
            print(f"  Path: {first_comp.path}")
            print(f"  Dependencies: {len(first_comp.depends_on)}")
            print(f"  Used by: {len(first_comp.used_by)}")
            
            # Get dependencies
            deps = graph.get_dependencies(first_comp_id)
            if deps:
                print(f"\n  Direct dependencies:")
                for dep in deps[:5]:  # Show first 5
                    print(f"    - {dep.name} ({dep.component_type})")
    else:
        print(f"Project path not found: {project_path}")
