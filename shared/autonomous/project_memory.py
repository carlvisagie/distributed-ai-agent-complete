"""
Project-Level Memory System for Autonomous Agent

Maintains holistic understanding across all tasks in a project.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

class ProjectMemory:
    """
    Persistent knowledge graph that tracks:
    - Architectural decisions made
    - Implementation patterns established
    - Files created/modified and their ownership
    - Lessons learned from successes and failures
    - Feature boundaries and integration points
    """
    
    def __init__(self, project_id: str, storage_dir: str = "session_storage"):
        self.project_id = project_id
        self.storage_dir = storage_dir
        self.memory_file = os.path.join(storage_dir, f"{project_id}_knowledge_graph.json")
        
        # Initialize or load memory
        self.memory = self._load_or_initialize()
    
    def _load_or_initialize(self) -> Dict[str, Any]:
        """Load existing memory or create new one"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Warning: Could not load memory file: {e}")
        
        # Initialize new memory
        return {
            "project_id": self.project_id,
            "created_at": datetime.utcnow().timestamp(),
            "last_updated": datetime.utcnow().timestamp(),
            "tasks_completed": 0,
            "architectural_decisions": [],
            "implementation_patterns": {},
            "file_ownership": {},
            "learned_lessons": [],
            "feature_map": {},
            "integration_points": []
        }
    
    def save(self):
        """Persist memory to disk"""
        self.memory["last_updated"] = datetime.utcnow().timestamp()
        
        os.makedirs(self.storage_dir, exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=2)
    
    def record_task_completion(self, task_id: str, task_data: Dict[str, Any]):
        """
        Record what was accomplished in a task
        
        Args:
            task_id: Task identifier
            task_data: {
                'title': str,
                'files_created': List[str],
                'files_modified': List[str],
                'patterns_used': List[str],
                'decisions': List[Dict],
                'lessons': List[str]
            }
        """
        self.memory["tasks_completed"] += 1
        
        # Record architectural decisions
        if task_data.get('decisions'):
            for decision in task_data['decisions']:
                self.memory["architectural_decisions"].append({
                    "task_id": task_id,
                    "decision": decision.get('decision'),
                    "rationale": decision.get('rationale'),
                    "files_affected": decision.get('files', []),
                    "timestamp": datetime.utcnow().timestamp()
                })
        
        # Update file ownership
        for file_path in task_data.get('files_created', []):
            self.memory["file_ownership"][file_path] = {
                "created_by": task_id,
                "purpose": task_data.get('title', 'Unknown'),
                "last_modified_by": task_id,
                "dependencies": task_data.get('dependencies', [])
            }
        
        for file_path in task_data.get('files_modified', []):
            if file_path in self.memory["file_ownership"]:
                self.memory["file_ownership"][file_path]["last_modified_by"] = task_id
            else:
                self.memory["file_ownership"][file_path] = {
                    "created_by": "unknown",
                    "purpose": "Modified by " + task_id,
                    "last_modified_by": task_id,
                    "dependencies": []
                }
        
        # Record patterns
        for pattern in task_data.get('patterns_used', []):
            if pattern not in self.memory["implementation_patterns"]:
                self.memory["implementation_patterns"][pattern] = {
                    "established_by": task_id,
                    "usage_count": 1,
                    "examples": [task_id]
                }
            else:
                self.memory["implementation_patterns"][pattern]["usage_count"] += 1
                self.memory["implementation_patterns"][pattern]["examples"].append(task_id)
        
        # Record lessons
        for lesson in task_data.get('lessons', []):
            self.memory["learned_lessons"].append({
                "task_id": task_id,
                "lesson": lesson,
                "timestamp": datetime.utcnow().timestamp()
            })
        
        self.save()
    
    def get_context_for_task(self, task_id: str, task_title: str) -> str:
        """
        Generate project memory context for a new task
        
        Returns formatted string with:
        - What has been built so far
        - Patterns to follow
        - Files that exist and their purposes
        - Lessons learned
        """
        context_parts = []
        
        context_parts.append(f"### 🧠 PROJECT MEMORY (Tasks Completed: {self.memory['tasks_completed']})")
        
        # Architectural decisions
        if self.memory["architectural_decisions"]:
            context_parts.append("\n**Key Architectural Decisions:**")
            for decision in self.memory["architectural_decisions"][-10:]:  # Last 10
                context_parts.append(f"  - [{decision['task_id']}] {decision['decision']}")
                if decision.get('rationale'):
                    context_parts.append(f"    Rationale: {decision['rationale']}")
        
        # Implementation patterns
        if self.memory["implementation_patterns"]:
            context_parts.append("\n**Established Patterns (FOLLOW THESE):**")
            for pattern_name, pattern_info in self.memory["implementation_patterns"].items():
                context_parts.append(f"  - {pattern_name}")
                context_parts.append(f"    Used {pattern_info['usage_count']} times")
                context_parts.append(f"    Examples: {', '.join(pattern_info['examples'][:3])}")
        
        # File ownership
        if self.memory["file_ownership"]:
            context_parts.append("\n**File Ownership Map (MODIFY EXISTING, DON'T DUPLICATE):**")
            for file_path, ownership in list(self.memory["file_ownership"].items())[:20]:  # First 20
                context_parts.append(f"  - {file_path}")
                context_parts.append(f"    Created by: {ownership['created_by']}")
                context_parts.append(f"    Purpose: {ownership['purpose']}")
        
        # Lessons learned
        if self.memory["learned_lessons"]:
            context_parts.append("\n**Lessons Learned (AVOID PAST MISTAKES):**")
            for lesson in self.memory["learned_lessons"][-10:]:  # Last 10
                context_parts.append(f"  - [{lesson['task_id']}] {lesson['lesson']}")
        
        # Feature map
        if self.memory["feature_map"]:
            context_parts.append("\n**Feature Map (UNDERSTAND RELATIONSHIPS):**")
            for feature_name, feature_info in self.memory["feature_map"].items():
                context_parts.append(f"  - {feature_name}: {feature_info.get('status', 'unknown')}")
                context_parts.append(f"    Tasks: {', '.join(feature_info.get('tasks', []))}")
                context_parts.append(f"    Files: {', '.join(feature_info.get('files', [])[:3])}")
        
        return "\n".join(context_parts)
    
    def check_for_conflicts(self, proposed_files: List[str]) -> List[str]:
        """
        Check if proposed files conflict with existing ownership
        
        Returns list of warnings
        """
        warnings = []
        
        for file_path in proposed_files:
            if file_path in self.memory["file_ownership"]:
                owner = self.memory["file_ownership"][file_path]
                warnings.append(
                    f"⚠️ {file_path} already exists (created by {owner['created_by']}, "
                    f"last modified by {owner['last_modified_by']}). "
                    f"Consider MODIFYING instead of creating new file."
                )
        
        return warnings
    
    def suggest_similar_implementations(self, task_description: str) -> List[str]:
        """
        Suggest similar implementations from past tasks
        
        Returns list of relevant task IDs
        """
        # Simple keyword matching for now
        # Could be enhanced with embeddings/semantic search
        suggestions = []
        
        keywords = task_description.lower().split()
        
        for decision in self.memory["architectural_decisions"]:
            decision_text = (decision.get('decision', '') + ' ' + decision.get('rationale', '')).lower()
            if any(keyword in decision_text for keyword in keywords):
                suggestions.append(decision['task_id'])
        
        return list(set(suggestions))[:5]  # Top 5 unique
