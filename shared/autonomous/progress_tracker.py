"""
Progress Tracker for Autonomous Agent
Tracks task progress, completion status, and execution metrics in real-time
"""

import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import threading


class TaskStatus(str, Enum):
    """Task execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRYING = "retrying"


class ProgressTracker:
    """Tracks progress of autonomous task execution"""
    
    def __init__(self):
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.execution_id: Optional[str] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.lock = threading.Lock()
        
        # Metrics
        self.metrics = {
            "total_tasks": 0,
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "retrying": 0,
            "running": 0,
            "pending": 0
        }
    
    def start_execution(self, execution_id: str, tasks: List[Dict]) -> None:
        """
        Start tracking a new execution
        
        Args:
            execution_id: Unique identifier for this execution
            tasks: List of tasks to track
        """
        with self.lock:
            self.execution_id = execution_id
            self.start_time = time.time()
            self.end_time = None
            
            # Initialize tasks
            self.tasks = {}
            for task in tasks:
                task_id = task.get('id', f"task_{len(self.tasks)}")
                self.tasks[task_id] = {
                    "id": task_id,
                    "title": task.get('title', 'Untitled'),
                    "type": task.get('type', 'generic'),
                    "priority": task.get('priority', 'medium'),
                    "status": TaskStatus.PENDING,
                    "progress": 0,
                    "start_time": None,
                    "end_time": None,
                    "duration": None,
                    "error": None,
                    "retry_count": 0,
                    "current_step": None,
                    "steps_completed": 0,
                    "total_steps": task.get('estimated_steps', 5)
                }
            
            # Update metrics
            self.metrics["total_tasks"] = len(self.tasks)
            self.metrics["pending"] = len(self.tasks)
            self._update_metrics()
    
    def start_task(self, task_id: str) -> None:
        """Mark task as started"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = TaskStatus.RUNNING
                self.tasks[task_id]["start_time"] = time.time()
                self.tasks[task_id]["progress"] = 0
                self._update_metrics()
    
    def update_task_progress(
        self,
        task_id: str,
        progress: int,
        current_step: Optional[str] = None
    ) -> None:
        """
        Update task progress
        
        Args:
            task_id: Task identifier
            progress: Progress percentage (0-100)
            current_step: Description of current step
        """
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["progress"] = min(100, max(0, progress))
                if current_step:
                    self.tasks[task_id]["current_step"] = current_step
                    self.tasks[task_id]["steps_completed"] += 1
    
    def complete_task(self, task_id: str, result: Optional[Dict] = None) -> None:
        """Mark task as completed"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = TaskStatus.COMPLETED
                self.tasks[task_id]["end_time"] = time.time()
                self.tasks[task_id]["progress"] = 100
                
                if self.tasks[task_id]["start_time"]:
                    self.tasks[task_id]["duration"] = (
                        self.tasks[task_id]["end_time"] - 
                        self.tasks[task_id]["start_time"]
                    )
                
                if result:
                    self.tasks[task_id]["result"] = result
                
                self._update_metrics()
    
    def fail_task(self, task_id: str, error: str) -> None:
        """Mark task as failed"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = TaskStatus.FAILED
                self.tasks[task_id]["end_time"] = time.time()
                self.tasks[task_id]["error"] = error
                
                if self.tasks[task_id]["start_time"]:
                    self.tasks[task_id]["duration"] = (
                        self.tasks[task_id]["end_time"] - 
                        self.tasks[task_id]["start_time"]
                    )
                
                self._update_metrics()
    
    def retry_task(self, task_id: str) -> None:
        """Mark task as retrying"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = TaskStatus.RETRYING
                self.tasks[task_id]["retry_count"] += 1
                self._update_metrics()
    
    def skip_task(self, task_id: str, reason: str) -> None:
        """Mark task as skipped"""
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = TaskStatus.SKIPPED
                self.tasks[task_id]["end_time"] = time.time()
                self.tasks[task_id]["error"] = reason
                self._update_metrics()
    
    def end_execution(self) -> None:
        """Mark execution as ended"""
        with self.lock:
            self.end_time = time.time()
    
    def complete_execution(self) -> None:
        """Alias for end_execution() for compatibility"""
        self.end_execution()
    
    def update_task(self, task_id: str, **kwargs) -> None:
        """Alias for update_task_progress() for compatibility"""
        progress = kwargs.get('progress', None)
        current_step = kwargs.get('current_step', None)
        if progress is not None:
            self.update_task_progress(task_id, progress, current_step)
    
    def _update_metrics(self) -> None:
        """Update metrics based on current task statuses"""
        self.metrics = {
            "total_tasks": len(self.tasks),
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "retrying": 0,
            "running": 0,
            "pending": 0
        }
        
        for task in self.tasks.values():
            status = task["status"]
            if status == TaskStatus.COMPLETED:
                self.metrics["completed"] += 1
            elif status == TaskStatus.FAILED:
                self.metrics["failed"] += 1
            elif status == TaskStatus.SKIPPED:
                self.metrics["skipped"] += 1
            elif status == TaskStatus.RETRYING:
                self.metrics["retrying"] += 1
            elif status == TaskStatus.RUNNING:
                self.metrics["running"] += 1
            elif status == TaskStatus.PENDING:
                self.metrics["pending"] += 1
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress summary"""
        with self.lock:
            total = self.metrics["total_tasks"]
            completed = self.metrics["completed"]
            
            # Calculate overall progress
            if total > 0:
                overall_progress = int((completed / total) * 100)
            else:
                overall_progress = 0
            
            # Calculate ETA
            eta = None
            if self.start_time and completed > 0:
                elapsed = time.time() - self.start_time
                avg_time_per_task = elapsed / completed
                remaining_tasks = total - completed
                eta_seconds = avg_time_per_task * remaining_tasks
                eta = {
                    "seconds": int(eta_seconds),
                    "formatted": self._format_duration(eta_seconds)
                }
            
            # Get elapsed time
            elapsed = None
            if self.start_time:
                elapsed_seconds = (self.end_time or time.time()) - self.start_time
                elapsed = {
                    "seconds": int(elapsed_seconds),
                    "formatted": self._format_duration(elapsed_seconds)
                }
            
            return {
                "execution_id": self.execution_id,
                "overall_progress": overall_progress,
                "metrics": self.metrics.copy(),
                "elapsed": elapsed,
                "eta": eta,
                "is_complete": self.end_time is not None,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_task_details(self, task_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed task information
        
        Args:
            task_id: Specific task ID, or None for all tasks
            
        Returns:
            Task details
        """
        with self.lock:
            if task_id:
                return self.tasks.get(task_id, {})
            else:
                return {
                    "tasks": list(self.tasks.values()),
                    "count": len(self.tasks)
                }
    
    def get_current_task(self) -> Optional[Dict[str, Any]]:
        """Get currently running task"""
        with self.lock:
            for task in self.tasks.values():
                if task["status"] == TaskStatus.RUNNING:
                    return task
            return None
    
    def get_summary(self) -> Dict[str, Any]:
        """Get complete execution summary"""
        progress = self.get_progress()
        current_task = self.get_current_task()
        
        return {
            "progress": progress,
            "current_task": current_task,
            "tasks": list(self.tasks.values())
        }
    
    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            minutes = int(seconds / 60)
            secs = int(seconds % 60)
            return f"{minutes}m {secs}s"
        else:
            hours = int(seconds / 3600)
            minutes = int((seconds % 3600) / 60)
            return f"{hours}h {minutes}m"
    
    def export_to_json(self, filepath: str) -> None:
        """Export progress to JSON file"""
        with self.lock:
            data = self.get_summary()
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)


# Global progress tracker instance
progress_tracker = ProgressTracker()
