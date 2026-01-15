"""
Session Manager - Execution Continuity and Resume System
Manages execution sessions with checkpoint/restore capability for perfect continuity
"""
import json
import os
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum


class SessionStatus(Enum):
    """Session execution status"""
    CREATED = "created"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SessionCheckpoint:
    """Session checkpoint for resume capability"""
    checkpoint_id: str
    session_id: str
    created_at: float
    
    # Execution state
    current_task_id: Optional[str] = None
    completed_task_ids: List[str] = field(default_factory=list)
    failed_task_ids: List[str] = field(default_factory=list)
    
    # Progress
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_total: int = 0
    
    # Context
    context_snapshot: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SessionCheckpoint':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class ExecutionSession:
    """Complete execution session state"""
    session_id: str
    project_id: str
    
    # Session details
    name: str
    description: str = ""
    status: str = SessionStatus.CREATED.value
    
    # Timing
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    last_active: float = field(default_factory=time.time)
    
    # Execution state
    current_task_id: Optional[str] = None
    completed_task_ids: List[str] = field(default_factory=list)
    failed_task_ids: List[str] = field(default_factory=list)
    skipped_task_ids: List[str] = field(default_factory=list)
    
    # Progress
    tasks_completed: int = 0
    tasks_failed: int = 0
    tasks_skipped: int = 0
    tasks_total: int = 0
    
    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    # Checkpoints
    checkpoints: List[str] = field(default_factory=list)  # List of checkpoint IDs
    last_checkpoint_id: Optional[str] = None
    
    # Metadata
    tags: List[str] = field(default_factory=list)
    notes: str = ""
    version: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExecutionSession':
        """Create from dictionary"""
        return cls(**data)
    
    def is_active(self) -> bool:
        """Check if session is active"""
        return self.status in [SessionStatus.RUNNING.value, SessionStatus.PAUSED.value]
    
    def is_complete(self) -> bool:
        """Check if session is complete"""
        return self.status == SessionStatus.COMPLETED.value
    
    def can_resume(self) -> bool:
        """Check if session can be resumed"""
        return self.status in [SessionStatus.PAUSED.value, SessionStatus.FAILED.value]
    
    def completion_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.tasks_total == 0:
            return 0.0
        return (self.tasks_completed / self.tasks_total) * 100
    
    def duration(self) -> Optional[float]:
        """Get session duration in seconds"""
        if self.started_at:
            end_time = self.completed_at or time.time()
            return end_time - self.started_at
        return None


class SessionManager:
    """
    Manages execution sessions with checkpoint/restore capability
    
    Features:
    - Create/manage sessions
    - Checkpoint current state
    - Resume from checkpoints
    - Track execution history
    - Handle interruptions
    """
    
    def __init__(self, storage_dir: str = "session_storage"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        self._cache: Dict[str, ExecutionSession] = {}
    
    def _get_session_path(self, session_id: str) -> str:
        """Get file path for session"""
        return os.path.join(self.storage_dir, f"{session_id}.json")
    
    def _get_checkpoint_path(self, checkpoint_id: str) -> str:
        """Get file path for checkpoint"""
        checkpoints_dir = os.path.join(self.storage_dir, "checkpoints")
        os.makedirs(checkpoints_dir, exist_ok=True)
        return os.path.join(checkpoints_dir, f"{checkpoint_id}.json")
    
    def _generate_session_id(self, project_id: str) -> str:
        """Generate unique session ID"""
        timestamp = int(time.time() * 1000)
        return f"{project_id}_session_{timestamp}"
    
    def _generate_checkpoint_id(self, session_id: str) -> str:
        """Generate unique checkpoint ID"""
        timestamp = int(time.time() * 1000)
        return f"{session_id}_checkpoint_{timestamp}"
    
    def save_session(self, session: ExecutionSession) -> bool:
        """
        Save session to disk
        
        Args:
            session: ExecutionSession object to save
        
        Returns:
            True if successful
        """
        try:
            session.last_active = time.time()
            session.version += 1
            
            file_path = self._get_session_path(session.session_id)
            
            with open(file_path, 'w') as f:
                json.dump(session.to_dict(), f, indent=2)
            
            # Update cache
            self._cache[session.session_id] = session
            
            return True
        
        except Exception as e:
            print(f"Error saving session: {e}")
            return False
    
    def load_session(self, session_id: str) -> Optional[ExecutionSession]:
        """
        Load session from disk
        
        Args:
            session_id: Session identifier
        
        Returns:
            ExecutionSession if found, None otherwise
        """
        # Check cache first
        if session_id in self._cache:
            return self._cache[session_id]
        
        try:
            file_path = self._get_session_path(session_id)
            
            if not os.path.exists(file_path):
                return None
            
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            session = ExecutionSession.from_dict(data)
            
            # Update cache
            self._cache[session_id] = session
            
            return session
        
        except Exception as e:
            print(f"Error loading session: {e}")
            return None
    
    def create_session(
        self,
        project_id: str,
        name: str,
        description: str = "",
        tasks_total: int = 0
    ) -> ExecutionSession:
        """
        Create new execution session
        
        Args:
            project_id: Project identifier
            name: Session name
            description: Session description
            tasks_total: Total number of tasks
        
        Returns:
            New ExecutionSession object
        """
        session_id = self._generate_session_id(project_id)
        
        session = ExecutionSession(
            session_id=session_id,
            project_id=project_id,
            name=name,
            description=description,
            tasks_total=tasks_total
        )
        
        self.save_session(session)
        
        return session
    
    def start_session(self, session_id: str) -> bool:
        """Mark session as started"""
        session = self.load_session(session_id)
        
        if not session:
            return False
        
        session.status = SessionStatus.RUNNING.value
        session.started_at = time.time()
        
        return self.save_session(session)
    
    def pause_session(self, session_id: str) -> bool:
        """Pause session execution"""
        session = self.load_session(session_id)
        
        if not session:
            return False
        
        session.status = SessionStatus.PAUSED.value
        
        return self.save_session(session)
    
    def resume_session(self, session_id: str) -> bool:
        """Resume paused session"""
        session = self.load_session(session_id)
        
        if not session or not session.can_resume():
            return False
        
        session.status = SessionStatus.RUNNING.value
        
        return self.save_session(session)
    
    def complete_session(
        self,
        session_id: str,
        result: Dict[str, Any]
    ) -> bool:
        """Mark session as completed"""
        session = self.load_session(session_id)
        
        if not session:
            return False
        
        session.status = SessionStatus.COMPLETED.value
        session.completed_at = time.time()
        session.result = result
        
        return self.save_session(session)
    
    def fail_session(
        self,
        session_id: str,
        error: str
    ) -> bool:
        """Mark session as failed"""
        session = self.load_session(session_id)
        
        if not session:
            return False
        
        session.status = SessionStatus.FAILED.value
        session.error = error
        
        return self.save_session(session)
    
    def update_progress(
        self,
        session_id: str,
        current_task_id: Optional[str] = None,
        completed_task_id: Optional[str] = None,
        failed_task_id: Optional[str] = None,
        skipped_task_id: Optional[str] = None
    ) -> bool:
        """
        Update session progress
        
        Args:
            session_id: Session identifier
            current_task_id: ID of currently executing task
            completed_task_id: ID of completed task
            failed_task_id: ID of failed task
            skipped_task_id: ID of skipped task
        
        Returns:
            True if successful
        """
        session = self.load_session(session_id)
        
        if not session:
            return False
        
        if current_task_id:
            session.current_task_id = current_task_id
        
        if completed_task_id:
            if completed_task_id not in session.completed_task_ids:
                session.completed_task_ids.append(completed_task_id)
                session.tasks_completed += 1
        
        if failed_task_id:
            if failed_task_id not in session.failed_task_ids:
                session.failed_task_ids.append(failed_task_id)
                session.tasks_failed += 1
        
        if skipped_task_id:
            if skipped_task_id not in session.skipped_task_ids:
                session.skipped_task_ids.append(skipped_task_id)
                session.tasks_skipped += 1
        
        return self.save_session(session)
    
    def create_checkpoint(
        self,
        session_id: str,
        context_snapshot: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Create checkpoint of current session state
        
        Args:
            session_id: Session identifier
            context_snapshot: Optional context data to save
        
        Returns:
            Checkpoint ID if successful, None otherwise
        """
        session = self.load_session(session_id)
        
        if not session:
            return None
        
        try:
            checkpoint_id = self._generate_checkpoint_id(session_id)
            
            checkpoint = SessionCheckpoint(
                checkpoint_id=checkpoint_id,
                session_id=session_id,
                created_at=time.time(),
                current_task_id=session.current_task_id,
                completed_task_ids=session.completed_task_ids.copy(),
                failed_task_ids=session.failed_task_ids.copy(),
                tasks_completed=session.tasks_completed,
                tasks_failed=session.tasks_failed,
                tasks_total=session.tasks_total,
                context_snapshot=context_snapshot or {}
            )
            
            # Save checkpoint
            checkpoint_path = self._get_checkpoint_path(checkpoint_id)
            with open(checkpoint_path, 'w') as f:
                json.dump(checkpoint.to_dict(), f, indent=2)
            
            # Update session
            session.checkpoints.append(checkpoint_id)
            session.last_checkpoint_id = checkpoint_id
            self.save_session(session)
            
            return checkpoint_id
        
        except Exception as e:
            print(f"Error creating checkpoint: {e}")
            return None
    
    def load_checkpoint(self, checkpoint_id: str) -> Optional[SessionCheckpoint]:
        """
        Load checkpoint data
        
        Args:
            checkpoint_id: Checkpoint identifier
        
        Returns:
            SessionCheckpoint if found, None otherwise
        """
        try:
            checkpoint_path = self._get_checkpoint_path(checkpoint_id)
            
            if not os.path.exists(checkpoint_path):
                return None
            
            with open(checkpoint_path, 'r') as f:
                data = json.load(f)
            
            return SessionCheckpoint.from_dict(data)
        
        except Exception as e:
            print(f"Error loading checkpoint: {e}")
            return None
    
    def restore_from_checkpoint(self, checkpoint_id: str) -> Optional[str]:
        """
        Restore session from checkpoint
        
        Args:
            checkpoint_id: Checkpoint identifier
        
        Returns:
            Session ID if successful, None otherwise
        """
        checkpoint = self.load_checkpoint(checkpoint_id)
        
        if not checkpoint:
            return None
        
        session = self.load_session(checkpoint.session_id)
        
        if not session:
            return None
        
        # Restore state from checkpoint
        session.current_task_id = checkpoint.current_task_id
        session.completed_task_ids = checkpoint.completed_task_ids.copy()
        session.failed_task_ids = checkpoint.failed_task_ids.copy()
        session.tasks_completed = checkpoint.tasks_completed
        session.tasks_failed = checkpoint.tasks_failed
        session.tasks_total = checkpoint.tasks_total
        session.status = SessionStatus.PAUSED.value
        
        if self.save_session(session):
            return session.session_id
        
        return None
    
    def get_resume_point(self, project_id: str) -> Optional[ExecutionSession]:
        """
        Find session that can be resumed for project
        
        Args:
            project_id: Project identifier
        
        Returns:
            ExecutionSession that can be resumed, or None
        """
        sessions = self.list_sessions(project_id)
        
        # Find most recent resumable session
        resumable = [s for s in sessions if s.can_resume()]
        
        if not resumable:
            return None
        
        # Sort by last active
        resumable.sort(key=lambda s: s.last_active, reverse=True)
        
        return resumable[0]
    
    def list_sessions(self, project_id: Optional[str] = None) -> List[ExecutionSession]:
        """
        List all sessions, optionally filtered by project
        
        Args:
            project_id: Optional project filter
        
        Returns:
            List of ExecutionSession objects
        """
        sessions = []
        
        for filename in os.listdir(self.storage_dir):
            if filename.endswith('.json'):
                session_id = filename[:-5]  # Remove .json
                session = self.load_session(session_id)
                
                if session and (not project_id or session.project_id == project_id):
                    sessions.append(session)
        
        return sorted(sessions, key=lambda s: s.last_active, reverse=True)
    
    def get_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        Get session statistics
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dictionary of statistics
        """
        session = self.load_session(session_id)
        
        if not session:
            return {}
        
        return {
            'session_id': session.session_id,
            'status': session.status,
            'completion_percentage': session.completion_percentage(),
            'tasks_completed': session.tasks_completed,
            'tasks_failed': session.tasks_failed,
            'tasks_skipped': session.tasks_skipped,
            'tasks_total': session.tasks_total,
            'duration_seconds': session.duration(),
            'checkpoints_count': len(session.checkpoints),
            'last_checkpoint': session.last_checkpoint_id,
            'can_resume': session.can_resume()
        }


# Global session manager instance
session_manager = SessionManager()


if __name__ == "__main__":
    # Example usage
    manager = SessionManager()
    
    project_id = "just_talk_test"
    
    # Create session
    session = manager.create_session(
        project_id=project_id,
        name="Complete Just Talk",
        description="Autonomous completion of Just Talk module",
        tasks_total=10
    )
    
    print(f"Created session: {session.session_id}")
    
    # Start session
    manager.start_session(session.session_id)
    
    # Simulate progress
    manager.update_progress(session.session_id, current_task_id="task_001")
    time.sleep(1)
    manager.update_progress(session.session_id, completed_task_id="task_001")
    
    manager.update_progress(session.session_id, current_task_id="task_002")
    time.sleep(1)
    manager.update_progress(session.session_id, completed_task_id="task_002")
    
    # Create checkpoint
    checkpoint_id = manager.create_checkpoint(
        session.session_id,
        context_snapshot={'note': 'Completed 2 tasks successfully'}
    )
    print(f"Created checkpoint: {checkpoint_id}")
    
    # Continue progress
    manager.update_progress(session.session_id, current_task_id="task_003")
    time.sleep(1)
    manager.update_progress(session.session_id, failed_task_id="task_003")
    
    # Pause session
    manager.pause_session(session.session_id)
    print("Session paused")
    
    # Get statistics
    stats = manager.get_statistics(session.session_id)
    print(f"\nStatistics:")
    print(f"  Status: {stats['status']}")
    print(f"  Completion: {stats['completion_percentage']:.1f}%")
    print(f"  Completed: {stats['tasks_completed']}")
    print(f"  Failed: {stats['tasks_failed']}")
    print(f"  Can resume: {stats['can_resume']}")
    
    # Find resume point
    resume_session = manager.get_resume_point(project_id)
    if resume_session:
        print(f"\nCan resume session: {resume_session.session_id}")
        print(f"Last active: {datetime.fromtimestamp(resume_session.last_active).isoformat()}")
    
    # Restore from checkpoint
    restored_session_id = manager.restore_from_checkpoint(checkpoint_id)
    if restored_session_id:
        print(f"\nRestored session from checkpoint: {restored_session_id}")
        restored_session = manager.load_session(restored_session_id)
        print(f"Restored state: {restored_session.tasks_completed} tasks completed")
