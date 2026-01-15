"""
Task State Manager - Persistent Task Tracking System
Stores and retrieves task states across sessions for perfect continuity
"""
import json
import os
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"


class TaskPriority(Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class TaskState:
    """Complete task state for continuity"""
    task_id: str
    project_id: str
    
    # Task details
    title: str
    description: str
    task_type: str  # create_page, add_feature, fix, security, optimize
    priority: str = TaskPriority.MEDIUM.value
    
    # Execution state
    status: str = TaskStatus.PENDING.value
    progress: float = 0.0  # 0-100
    current_step: str = ""
    
    # Timing
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    estimated_duration: int = 300  # seconds
    
    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    # GitHub integration
    branch_name: Optional[str] = None
    pr_url: Optional[str] = None
    pr_number: Optional[int] = None
    commit_sha: Optional[str] = None
    
    # Dependencies
    depends_on: List[str] = field(default_factory=list)
    blocks: List[str] = field(default_factory=list)
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_updated: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskState':
        """Create from dictionary"""
        return cls(**data)
    
    def is_complete(self) -> bool:
        """Check if task is complete"""
        return self.status == TaskStatus.COMPLETED.value
    
    def is_failed(self) -> bool:
        """Check if task failed"""
        return self.status == TaskStatus.FAILED.value
    
    def is_running(self) -> bool:
        """Check if task is running"""
        return self.status == TaskStatus.RUNNING.value
    
    def can_retry(self) -> bool:
        """Check if task can be retried"""
        return self.retry_count < self.max_retries
    
    def duration(self) -> Optional[float]:
        """Get task duration in seconds"""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None


class TaskStateManager:
    """
    Manages persistent task states for perfect continuity
    
    Features:
    - Save/load task states
    - Track execution progress
    - Handle retries
    - Manage dependencies
    - Resume from any point
    """
    
    def __init__(self, storage_dir: str = "task_storage"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self._cache: Dict[str, Dict[str, TaskState]] = {}  # project_id -> {task_id -> TaskState}
    
    def _get_project_dir(self, project_id: str) -> str:
        """Get directory for project tasks"""
        project_dir = os.path.join(self.storage_dir, project_id)
        os.makedirs(project_dir, exist_ok=True)
        return project_dir
    
    def _get_task_path(self, project_id: str, task_id: str) -> str:
        """Get file path for task state"""
        project_dir = self._get_project_dir(project_id)
        return os.path.join(project_dir, f"{task_id}.json")
    
    def _get_index_path(self, project_id: str) -> str:
        """Get path for task index file"""
        project_dir = self._get_project_dir(project_id)
        return os.path.join(project_dir, "index.json")
    
    def save_task(self, task: TaskState) -> bool:
        """
        Save task state to disk
        
        Args:
            task: TaskState object to save
        
        Returns:
            True if successful
        """
        try:
            task.last_updated = time.time()
            
            file_path = self._get_task_path(task.project_id, task.task_id)
            
            with open(file_path, 'w') as f:
                json.dump(task.to_dict(), f, indent=2)
            
            # Update cache
            if task.project_id not in self._cache:
                self._cache[task.project_id] = {}
            self._cache[task.project_id][task.task_id] = task
            
            # Update index
            self._update_index(task.project_id)
            
            return True
        
        except Exception as e:
            print(f"Error saving task: {e}")
            return False
    
    def load_task(self, project_id: str, task_id: str) -> Optional[TaskState]:
        """
        Load task state from disk
        
        Args:
            project_id: Project identifier
            task_id: Task identifier
        
        Returns:
            TaskState if found, None otherwise
        """
        # Check cache first
        if project_id in self._cache and task_id in self._cache[project_id]:
            return self._cache[project_id][task_id]
        
        try:
            file_path = self._get_task_path(project_id, task_id)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            task = TaskState.from_dict(data)
            
            # Update cache
            if project_id not in self._cache:
                self._cache[project_id] = {}
            self._cache[project_id][task_id] = task
            
            return task
        
        except Exception as e:
            print(f"Error loading task: {e}")
            return None
    
    def save_tasks(self, project_id: str) -> bool:
        """
        Save all tasks for a project from cache to disk
        
        Args:
            project_id: Project identifier
        
        Returns:
            True if successful
        """
        try:
            if project_id not in self._cache:
                return True  # No tasks to save
            
            for task_id, task in self._cache[project_id].items():
                self.save_task(task)
            
            return True
        except Exception as e:
            print(f"Error saving tasks: {e}")
            return False
    
    def load_all_tasks(self, project_id: str) -> List[TaskState]:
        """
        Load all tasks for a project
        
        Args:
            project_id: Project identifier
        
        Returns:
            List of TaskState objects
        """
        tasks = []
        project_dir = self._get_project_dir(project_id)
        
        for filename in os.listdir(project_dir):
            if filename.endswith('.json') and filename != 'index.json':
                task_id = filename[:-5]  # Remove .json
                task = self.load_task(project_id, task_id)
                if task:
                    tasks.append(task)
        
        return tasks
    
    def create_task(
        self,
        project_id: str,
        task_id: str,
        title: str,
        description: str,
        task_type: str,
        priority: str = TaskPriority.MEDIUM.value,
        estimated_duration: int = 300,
        depends_on: List[str] = None
    ) -> TaskState:
        """
        Create new task
        
        Args:
            project_id: Project identifier
            task_id: Unique task identifier
            title: Task title
            description: Task description
            task_type: Type of task
            priority: Task priority
            estimated_duration: Estimated duration in seconds
            depends_on: List of task IDs this depends on
        
        Returns:
            New TaskState object
        """
        task = TaskState(
            task_id=task_id,
            project_id=project_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            estimated_duration=estimated_duration,
            depends_on=depends_on or []
        )
        
        self.save_task(task)
        
        return task
    
    def update_task(
        self,
        project_id: str,
        task_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update task fields
        
        Args:
            project_id: Project identifier
            task_id: Task identifier
            updates: Dictionary of fields to update
        
        Returns:
            True if successful
        """
        task = self.load_task(project_id, task_id)
        
        if not task:
            print(f"Task not found: {task_id}")
            return False
        
        # Update fields
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)
        
        return self.save_task(task)
    
    def start_task(self, project_id: str, task_id: str) -> bool:
        """Mark task as started"""
        return self.update_task(project_id, task_id, {
            'status': TaskStatus.RUNNING.value,
            'started_at': time.time()
        })
    
    def complete_task(
        self,
        project_id: str,
        task_id: str,
        result: Dict[str, Any]
    ) -> bool:
        """Mark task as completed"""
        return self.update_task(project_id, task_id, {
            'status': TaskStatus.COMPLETED.value,
            'completed_at': time.time(),
            'progress': 100.0,
            'result': result
        })
    
    def fail_task(
        self,
        project_id: str,
        task_id: str,
        error: str
    ) -> bool:
        """Mark task as failed"""
        task = self.load_task(project_id, task_id)
        
        if not task:
            return False
        
        task.retry_count += 1
        
        if task.can_retry():
            status = TaskStatus.RETRYING.value
        else:
            status = TaskStatus.FAILED.value
        
        return self.update_task(project_id, task_id, {
            'status': status,
            'error': error,
            'retry_count': task.retry_count
        })
    
    def get_next_task(self, project_id: str) -> Optional[TaskState]:
        """
        Get next task to execute
        
        Args:
            project_id: Project identifier
        
        Returns:
            Next TaskState to execute, or None if all done
        """
        tasks = self.load_all_tasks(project_id)
        
        # Filter pending/retrying tasks
        available_tasks = [
            t for t in tasks
            if t.status in [TaskStatus.PENDING.value, TaskStatus.RETRYING.value]
        ]
        
        if not available_tasks:
            return None
        
        # Check dependencies
        completed_task_ids = {
            t.task_id for t in tasks
            if t.status == TaskStatus.COMPLETED.value
        }
        
        ready_tasks = [
            t for t in available_tasks
            if all(dep in completed_task_ids for dep in t.depends_on)
        ]
        
        if not ready_tasks:
            return None
        
        # Sort by priority
        priority_order = {
            TaskPriority.CRITICAL.value: 0,
            TaskPriority.HIGH.value: 1,
            TaskPriority.MEDIUM.value: 2,
            TaskPriority.LOW.value: 3
        }
        
        ready_tasks.sort(key=lambda t: priority_order.get(t.priority, 999))
        
        return ready_tasks[0]
    
    def get_statistics(self, project_id: str) -> Dict[str, Any]:
        """
        Get task statistics for project
        
        Args:
            project_id: Project identifier
        
        Returns:
            Dictionary of statistics
        """
        tasks = self.load_all_tasks(project_id)
        
        total = len(tasks)
        completed = sum(1 for t in tasks if t.is_complete())
        failed = sum(1 for t in tasks if t.is_failed())
        running = sum(1 for t in tasks if t.is_running())
        pending = total - completed - failed - running
        
        # Calculate average duration
        durations = [t.duration() for t in tasks if t.duration()]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Calculate ETA
        remaining_tasks = pending + running
        eta = remaining_tasks * avg_duration if avg_duration > 0 else 0
        
        return {
            'total': total,
            'completed': completed,
            'failed': failed,
            'running': running,
            'pending': pending,
            'completion_percentage': (completed / total * 100) if total > 0 else 0,
            'average_duration': avg_duration,
            'eta_seconds': eta
        }
    
    def _update_index(self, project_id: str):
        """Update task index for quick lookups"""
        try:
            tasks = self.load_all_tasks(project_id)
            
            index = {
                'project_id': project_id,
                'total_tasks': len(tasks),
                'last_updated': time.time(),
                'tasks': [
                    {
                        'task_id': t.task_id,
                        'title': t.title,
                        'status': t.status,
                        'priority': t.priority
                    }
                    for t in tasks
                ]
            }
            
            index_path = self._get_index_path(project_id)
            
            with open(index_path, 'w') as f:
                json.dump(index, f, indent=2)
        
        except Exception as e:
            print(f"Error updating index: {e}")
    
    def export_tasks(self, project_id: str, output_path: str) -> bool:
        """Export all tasks to file"""
        try:
            tasks = self.load_all_tasks(project_id)
            
            data = {
                'project_id': project_id,
                'exported_at': time.time(),
                'tasks': [t.to_dict() for t in tasks]
            }
            
            with open(output_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        
        except Exception as e:
            print(f"Error exporting tasks: {e}")
            return False
    
    def import_tasks(self, input_path: str) -> Optional[str]:
        """Import tasks from file"""
        try:
            with open(input_path, 'r') as f:
                data = json.load(f)
            
            project_id = data['project_id']
            
            for task_data in data['tasks']:
                task = TaskState.from_dict(task_data)
                self.save_task(task)
            
            return project_id
        
        except Exception as e:
            print(f"Error importing tasks: {e}")
            return None


# Global task state manager instance
task_state_manager = TaskStateManager()


if __name__ == "__main__":
    # Example usage
    manager = TaskStateManager()
    
    project_id = "just_talk_test"
    
    # Create tasks
    task1 = manager.create_task(
        project_id=project_id,
        task_id="task_001",
        title="Fix broken contact form",
        description="Contact form not submitting properly",
        task_type="fix",
        priority=TaskPriority.CRITICAL.value,
        estimated_duration=600
    )
    
    task2 = manager.create_task(
        project_id=project_id,
        task_id="task_002",
        title="Add services page",
        description="Create new services page with pricing",
        task_type="create_page",
        priority=TaskPriority.HIGH.value,
        estimated_duration=1200,
        depends_on=["task_001"]
    )
    
    task3 = manager.create_task(
        project_id=project_id,
        task_id="task_003",
        title="Optimize images",
        description="Compress and optimize all images",
        task_type="optimize",
        priority=TaskPriority.LOW.value,
        estimated_duration=300
    )
    
    print(f"Created {len(manager.load_all_tasks(project_id))} tasks")
    
    # Start and complete task 1
    manager.start_task(project_id, "task_001")
    time.sleep(1)  # Simulate work
    manager.complete_task(project_id, "task_001", {
        'pr_url': 'https://github.com/user/repo/pull/123',
        'files_changed': 3
    })
    
    # Get next task (should be task_002 since task_001 is complete)
    next_task = manager.get_next_task(project_id)
    print(f"\nNext task: {next_task.title if next_task else 'None'}")
    
    # Get statistics
    stats = manager.get_statistics(project_id)
    print(f"\nStatistics:")
    print(f"  Total: {stats['total']}")
    print(f"  Completed: {stats['completed']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  Completion: {stats['completion_percentage']:.1f}%")
    
    # Export tasks
    export_path = "/tmp/tasks_export.json"
    if manager.export_tasks(project_id, export_path):
        print(f"\nTasks exported to: {export_path}")
