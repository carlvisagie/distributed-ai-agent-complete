"""
Autonomous Executor V2 - With Perfect Continuity
Integrates context manager, task state manager, session manager, and knowledge graph
"""
import asyncio
import json
import sys
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autonomous.error_handler import error_handler, AgentError
from autonomous.retry_decorator import retry, retry_on_network_error, retry_on_git_error
from autonomous.context_manager import context_manager, ProjectContext
from autonomous.task_state_manager import task_state_manager, TaskState, TaskStatus, TaskPriority
from autonomous.session_manager import session_manager, ExecutionSession, SessionStatus
from autonomous.knowledge_graph import knowledge_graph, Component, Feature
from autonomous.progress_tracker import progress_tracker


class AutonomousExecutorV2:
    """
    Autonomous executor with perfect continuity
    
    Features:
    - Context persistence across sessions
    - Task state management
    - Session checkpointing
    - Knowledge graph integration
    - Resume from any point
    - Progress tracking
    """
    
    def __init__(
        self,
        project_id: str,
        project_path: str,
        lenovo_api_url: str = "http://localhost:8088"
    ):
        self.project_id = project_id
        self.project_path = project_path
        self.lenovo_api_url = lenovo_api_url
        
        # Managers
        self.context_mgr = context_manager
        self.task_mgr = task_state_manager
        self.session_mgr = session_manager
        self.knowledge = knowledge_graph
        self.progress = progress_tracker
        
        # Current session
        self.session: Optional[ExecutionSession] = None
        self.session_id: Optional[str] = None
    
    async def initialize(self) -> bool:
        """
        Initialize executor with project context
        
        Returns:
            True if successful
        """
        try:
            print(f"\n🚀 Initializing Autonomous Executor V2...")
            print(f"   Project: {self.project_id}")
            print(f"   Path: {self.project_path}")
            
            # Load or create project context
            context = self.context_mgr.load_context(self.project_id)
            
            if not context:
                print("   Creating new project context...")
                context = self.context_mgr.create_context(
                    project_id=self.project_id,
                    project_name=self.project_id,
                    project_path=self.project_path
                )
            else:
                print(f"   Loaded existing context (analyzed: {context.analyzed_at})")
            
            # Build knowledge graph if not exists
            if not self.knowledge.components:
                print("   Building knowledge graph...")
                self.knowledge.build_from_codebase(self.project_path)
                stats = self.knowledge.get_statistics()
                print(f"   Found {stats['total_components']} components")
            
            # Check for resumable session
            resume_session = self.session_mgr.get_resume_point(self.project_id)
            
            if resume_session:
                print(f"\n⏸️  Found resumable session: {resume_session.name}")
                print(f"   Status: {resume_session.status}")
                print(f"   Progress: {resume_session.completion_percentage():.1f}%")
                print(f"   Completed: {resume_session.tasks_completed}/{resume_session.tasks_total}")
                
                # Ask to resume (in production, this could be automatic)
                print("\n   Will resume from this session...")
                self.session = resume_session
                self.session_id = resume_session.session_id
                self.session_mgr.resume_session(self.session_id)
            
            print("✅ Initialization complete\n")
            return True
        
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    async def analyze_and_generate_tasks(self) -> List[TaskState]:
        """
        Analyze project and generate completion tasks
        
        Returns:
            List of TaskState objects
        """
        try:
            print("\n🔍 Analyzing project and generating tasks...")
            
            # Load context
            context = self.context_mgr.load_context(self.project_id)
            
            if not context:
                print("❌ No project context found")
                return []
            
            # Get knowledge graph stats
            kg_stats = self.knowledge.get_statistics()
            
            print(f"\n📊 Project Analysis:")
            print(f"   Components: {kg_stats['total_components']}")
            print(f"   Features: {kg_stats['total_features']}")
            print(f"   Completion: {context.completion_percentage:.1f}%")
            
            # Generate tasks based on gaps
            tasks = []
            
            # Example: Create tasks for incomplete features
            for feature_id, feature in self.knowledge.features.items():
                if feature.status != "complete":
                    task = self.task_mgr.create_task(
                        project_id=self.project_id,
                        task_id=f"task_{feature_id}",
                        title=f"Complete {feature.name}",
                        description=feature.description,
                        task_type="feature",
                        priority=feature.priority,
                        estimated_duration=600
                    )
                    tasks.append(task)
            
            # Example: Create tasks for missing components
            for comp_id, comp in self.knowledge.components.items():
                if comp.status == "incomplete":
                    task = self.task_mgr.create_task(
                        project_id=self.project_id,
                        task_id=f"task_{comp_id}",
                        title=f"Complete {comp.name}",
                        description=f"Complete component: {comp.path}",
                        task_type="component",
                        priority=TaskPriority.MEDIUM.value,
                        estimated_duration=300
                    )
                    tasks.append(task)
            
            print(f"\n✅ Generated {len(tasks)} tasks")
            
            return tasks
        
        except Exception as e:
            print(f"❌ Task generation failed: {e}")
            return []
    
    async def execute_tasks(
        self,
        tasks: Optional[List[TaskState]] = None,
        auto_pr: bool = True,
        checkpoint_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Execute tasks with full continuity support
        
        Args:
            tasks: List of tasks (if None, will resume or generate)
            auto_pr: Automatically create PRs
            checkpoint_interval: Create checkpoint every N tasks
        
        Returns:
            Execution summary
        """
        try:
            # Initialize if not done
            if not self.session:
                await self.initialize()
            
            # Get tasks
            if not tasks:
                if self.session and self.session.can_resume():
                    # Resume existing session
                    print("\n▶️  Resuming existing session...")
                    tasks = self._get_remaining_tasks()
                else:
                    # Generate new tasks
                    tasks = await self.analyze_and_generate_tasks()
            
            if not tasks:
                print("❌ No tasks to execute")
                return {"error": "No tasks available"}
            
            # Create or resume session
            if not self.session:
                self.session = self.session_mgr.create_session(
                    project_id=self.project_id,
                    name=f"Complete {self.project_id}",
                    description="Autonomous completion execution",
                    tasks_total=len(tasks)
                )
                self.session_id = self.session.session_id
                self.session_mgr.start_session(self.session_id)
            
            # Initialize progress tracker
            self.progress.start_execution(
                total_tasks=len(tasks),
                project_name=self.project_id
            )
            
            print(f"\n🤖 Starting execution of {len(tasks)} tasks...")
            print(f"   Session: {self.session_id}")
            print(f"   Auto PR: {auto_pr}")
            print(f"   Checkpoint interval: {checkpoint_interval} tasks")
            
            # Execute tasks
            completed = 0
            failed = 0
            
            for i, task in enumerate(tasks):
                print(f"\n{'='*60}")
                print(f"Task {i+1}/{len(tasks)}: {task.title}")
                print(f"Priority: {task.priority} | Type: {task.task_type}")
                print(f"{'='*60}")
                
                try:
                    # Update progress
                    self.progress.update_task(
                        task_id=task.task_id,
                        status="running",
                        progress=0
                    )
                    
                    # Mark task as started
                    self.task_mgr.start_task(self.project_id, task.task_id)
                    self.session_mgr.update_progress(
                        self.session_id,
                        current_task_id=task.task_id
                    )
                    
                    # Execute task
                    result = await self._execute_single_task(task)
                    
                    if result['status'] == 'success':
                        # Mark as completed
                        self.task_mgr.complete_task(
                            self.project_id,
                            task.task_id,
                            result
                        )
                        self.session_mgr.update_progress(
                            self.session_id,
                            completed_task_id=task.task_id
                        )
                        self.progress.complete_task(task.task_id)
                        
                        completed += 1
                        print(f"✅ Task completed successfully")
                        
                        # Create PR if enabled
                        if auto_pr:
                            pr_result = await self._create_pr_for_task(task, result)
                            if pr_result['success']:
                                print(f"🔀 PR created: {pr_result.get('pr_url', 'N/A')}")
                    
                    else:
                        # Mark as failed
                        error_msg = result.get('error', 'Unknown error')
                        self.task_mgr.fail_task(
                            self.project_id,
                            task.task_id,
                            error_msg
                        )
                        self.session_mgr.update_progress(
                            self.session_id,
                            failed_task_id=task.task_id
                        )
                        self.progress.fail_task(task.task_id, error_msg)
                        
                        failed += 1
                        print(f"❌ Task failed: {error_msg}")
                    
                    # Create checkpoint periodically
                    if (i + 1) % checkpoint_interval == 0:
                        print(f"\n💾 Creating checkpoint...")
                        checkpoint_id = self.session_mgr.create_checkpoint(
                            self.session_id,
                            context_snapshot={
                                'completed': completed,
                                'failed': failed,
                                'progress': self.progress.get_progress()
                            }
                        )
                        print(f"   Checkpoint: {checkpoint_id}")
                    
                    # Small delay
                    await asyncio.sleep(2)
                
                except Exception as e:
                    print(f"💥 Exception: {str(e)}")
                    self.task_mgr.fail_task(self.project_id, task.task_id, str(e))
                    self.progress.fail_task(task.task_id, str(e))
                    failed += 1
            
            # Complete session
            result_summary = {
                'total': len(tasks),
                'completed': completed,
                'failed': failed,
                'completion_percentage': (completed / len(tasks) * 100) if tasks else 0
            }
            
            self.session_mgr.complete_session(self.session_id, result_summary)
            self.progress.complete_execution()
            
            # Final checkpoint
            final_checkpoint = self.session_mgr.create_checkpoint(
                self.session_id,
                context_snapshot={
                    'final_result': result_summary,
                    'progress': self.progress.get_progress()
                }
            )
            
            print(f"\n{'='*60}")
            print(f"🎉 Execution Complete!")
            print(f"   Completed: {completed}/{len(tasks)}")
            print(f"   Failed: {failed}/{len(tasks)}")
            print(f"   Success Rate: {result_summary['completion_percentage']:.1f}%")
            print(f"   Final Checkpoint: {final_checkpoint}")
            print(f"{'='*60}\n")
            
            return result_summary
        
        except Exception as e:
            print(f"❌ Execution failed: {e}")
            if self.session_id:
                self.session_mgr.fail_session(self.session_id, str(e))
            return {"error": str(e)}
    
    def _get_remaining_tasks(self) -> List[TaskState]:
        """Get remaining tasks from current session"""
        if not self.session:
            return []
        
        all_tasks = self.task_mgr.load_all_tasks(self.project_id)
        
        # Filter out completed tasks
        remaining = [
            t for t in all_tasks
            if t.task_id not in self.session.completed_task_ids
        ]
        
        return remaining
    
    @retry(max_attempts=3, base_delay=2.0, exponential_base=2.0)
    async def _execute_single_task(self, task: TaskState) -> Dict[str, Any]:
        """
        Execute a single task with retry logic
        
        Args:
            task: TaskState object
        
        Returns:
            Task result dictionary
        """
        try:
            # Simulate task execution
            # In production, this would call the actual execution API
            print(f"   Executing: {task.description}")
            
            # Update progress
            for progress in [25, 50, 75, 100]:
                await asyncio.sleep(0.5)
                self.progress.update_task(
                    task_id=task.task_id,
                    progress=progress
                )
            
            return {
                'status': 'success',
                'task_id': task.task_id,
                'result': 'Task completed successfully'
            }
        
        except Exception as e:
            return {
                'status': 'failed',
                'task_id': task.task_id,
                'error': str(e)
            }
    
    @retry_on_git_error(max_attempts=3)
    async def _create_pr_for_task(
        self,
        task: TaskState,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create GitHub PR for completed task
        
        Args:
            task: TaskState object
            result: Task execution result
        
        Returns:
            PR creation result
        """
        try:
            # Simulate PR creation
            # In production, this would call GitHub API
            print(f"   Creating PR for: {task.title}")
            
            await asyncio.sleep(1)
            
            pr_url = f"https://github.com/user/repo/pull/{task.task_id}"
            
            # Update task with PR info
            self.task_mgr.update_task(
                self.project_id,
                task.task_id,
                {
                    'pr_url': pr_url,
                    'branch_name': f"task-{task.task_id}"
                }
            )
            
            return {
                'success': True,
                'pr_url': pr_url,
                'branch': f"task-{task.task_id}"
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        if not self.session:
            return {"error": "No active session"}
        
        session_stats = self.session_mgr.get_statistics(self.session_id)
        task_stats = self.task_mgr.get_statistics(self.project_id)
        progress_stats = self.progress.get_progress()
        
        return {
            'session': session_stats,
            'tasks': task_stats,
            'progress': progress_stats
        }


# Example usage
async def main():
    """Example usage of AutonomousExecutorV2"""
    
    # Initialize executor
    executor = AutonomousExecutorV2(
        project_id="just_talk_standalone",
        project_path="/home/ubuntu/just-talk-standalone"
    )
    
    # Initialize
    if not await executor.initialize():
        print("Failed to initialize")
        return
    
    # Execute tasks
    result = await executor.execute_tasks(
        auto_pr=True,
        checkpoint_interval=5
    )
    
    print(f"\nFinal Result: {json.dumps(result, indent=2)}")
    
    # Get status
    status = executor.get_status()
    print(f"\nStatus: {json.dumps(status, indent=2)}")


if __name__ == "__main__":
    asyncio.run(main())
