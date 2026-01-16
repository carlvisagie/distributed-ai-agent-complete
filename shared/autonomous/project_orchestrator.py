"""
Project Orchestrator - Integrates Project Architect with Task Executor

Handles end-to-end project development from requirements to deployment:
1. Project Architect analyzes requirements (6 layers deep)
2. Generates execution plan with proper sequencing
3. Task Executor implements each task
4. Tracks progress and handles dependencies
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
from .project_architect import ProjectArchitect
from .real_executor import RealExecutor
from .session_manager import SessionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ProjectOrchestrator:
    """
    Master orchestrator for complete project development
    
    Workflow:
    1. Analyze project requirements (6-layer deep)
    2. Generate execution plan
    3. Execute tasks in proper sequence
    4. Handle dependencies and parallelization
    5. Track progress and checkpoints
    """
    
    def __init__(
        self,
        workspace_path: str,
        project_name: str,
        llm_api_key: Optional[str] = None,
        llm_model: Optional[str] = None
    ):
        self.workspace_path = workspace_path
        self.project_name = project_name
        self.llm_api_key = llm_api_key or os.getenv("LLM_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.llm_model = llm_model or os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
        
        # Initialize components
        self.architect = ProjectArchitect(
            llm_api_key=self.llm_api_key,
            llm_model=self.llm_model
        )
        
        self.executor = RealExecutor(
            workspace_path=workspace_path,
            llm_api_key=self.llm_api_key,
            llm_model=self.llm_model
        )
        
        self.session_manager = SessionManager(project_name)
        
        # State tracking
        self.architectural_analysis = None
        self.execution_plan = None
        self.completed_tasks = []
        self.failed_tasks = []
        
    def develop_project(
        self,
        requirements: str,
        additional_context: Optional[Dict[str, Any]] = None,
        start_from_task: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete project development from requirements to implementation
        
        Args:
            requirements: Project requirements (can be high-level or detailed)
            additional_context: Additional context (tech stack preferences, constraints, etc.)
            start_from_task: Resume from specific task ID (for checkpointing)
        
        Returns:
            Development summary with results
        """
        logger.info(f"🚀 Starting project development: {self.project_name}")
        start_time = datetime.now()
        
        try:
            # PHASE 1: Architectural Analysis (if not resuming)
            if not start_from_task:
                logger.info("=" * 80)
                logger.info("PHASE 1: ARCHITECTURAL ANALYSIS (6 Layers Deep)")
                logger.info("=" * 80)
                
                self.architectural_analysis = self.architect.analyze_project(
                    project_requirements=requirements,
                    project_name=self.project_name,
                    additional_context=additional_context
                )
                
                # Save analysis
                analysis_path = os.path.join(
                    self.workspace_path,
                    f".architect/{self.project_name}_analysis.json"
                )
                self.architect.save_analysis(self.architectural_analysis, analysis_path)
                
                logger.info("✅ Architectural analysis complete")
                self._print_analysis_summary()
                
                # PHASE 2: Execution Plan Generation
                logger.info("=" * 80)
                logger.info("PHASE 2: EXECUTION PLAN GENERATION")
                logger.info("=" * 80)
                
                self.execution_plan = self.architect.generate_execution_plan(
                    self.architectural_analysis
                )
                
                # Save execution plan
                plan_path = os.path.join(
                    self.workspace_path,
                    f".architect/{self.project_name}_plan.json"
                )
                os.makedirs(os.path.dirname(plan_path), exist_ok=True)
                with open(plan_path, 'w') as f:
                    json.dump({
                        "execution_plan": self.execution_plan,
                        "generated_at": datetime.now().isoformat()
                    }, f, indent=2)
                
                logger.info(f"✅ Execution plan generated: {len(self.execution_plan)} tasks")
                self._print_plan_summary()
            
            else:
                # Load existing analysis and plan
                logger.info(f"📂 Resuming from task: {start_from_task}")
                analysis_path = os.path.join(
                    self.workspace_path,
                    f".architect/{self.project_name}_analysis.json"
                )
                plan_path = os.path.join(
                    self.workspace_path,
                    f".architect/{self.project_name}_plan.json"
                )
                
                self.architectural_analysis = self.architect.load_analysis(analysis_path)
                with open(plan_path, 'r') as f:
                    plan_data = json.load(f)
                    self.execution_plan = plan_data["execution_plan"]
            
            # PHASE 3: Task Execution
            logger.info("=" * 80)
            logger.info("PHASE 3: TASK EXECUTION")
            logger.info("=" * 80)
            
            self._execute_tasks(start_from_task)
            
            # PHASE 4: Summary
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            summary = {
                "project_name": self.project_name,
                "status": "completed" if not self.failed_tasks else "partial",
                "total_tasks": len(self.execution_plan),
                "completed_tasks": len(self.completed_tasks),
                "failed_tasks": len(self.failed_tasks),
                "duration_seconds": duration,
                "completed_at": end_time.isoformat(),
                "failed_task_ids": [t["task_id"] for t in self.failed_tasks]
            }
            
            logger.info("=" * 80)
            logger.info("PROJECT DEVELOPMENT SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Status: {summary['status']}")
            logger.info(f"Tasks: {summary['completed_tasks']}/{summary['total_tasks']} completed")
            logger.info(f"Duration: {duration/60:.1f} minutes")
            
            if self.failed_tasks:
                logger.warning(f"⚠️  {len(self.failed_tasks)} tasks failed:")
                for task in self.failed_tasks:
                    logger.warning(f"   - {task['task_id']}: {task['title']}")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Project development failed: {e}")
            raise
    
    def _execute_tasks(self, start_from: Optional[str] = None):
        """Execute tasks in proper sequence"""
        # Find starting index
        start_idx = 0
        if start_from:
            for i, task in enumerate(self.execution_plan):
                if task["task_id"] == start_from:
                    start_idx = i
                    break
        
        # Execute tasks sequentially (respecting dependencies)
        for i in range(start_idx, len(self.execution_plan)):
            task = self.execution_plan[i]
            
            # Check if dependencies are met
            if not self._dependencies_met(task):
                logger.warning(f"⏭️  Skipping {task['task_id']} - dependencies not met")
                continue
            
            logger.info("=" * 80)
            logger.info(f"TASK {i+1}/{len(self.execution_plan)}: {task['task_id']}")
            logger.info(f"Title: {task['title']}")
            logger.info(f"Type: {task['type']} | Complexity: {task['complexity']}")
            logger.info("=" * 80)
            
            try:
                # Execute task
                result = self.executor.execute_task(
                    task_id=task["task_id"],
                    title=task["title"],
                    prompt=self._build_task_prompt(task)
                )
                
                if result.get("status") == "completed":
                    self.completed_tasks.append(task)
                    logger.info(f"✅ Task {task['task_id']} completed")
                else:
                    self.failed_tasks.append(task)
                    logger.error(f"❌ Task {task['task_id']} failed")
                
                # Checkpoint after each task
                self._save_checkpoint(i)
                
            except Exception as e:
                logger.error(f"❌ Task {task['task_id']} failed with exception: {e}")
                self.failed_tasks.append(task)
                
                # Decide whether to continue or stop
                if task.get("critical", False):
                    logger.error("🛑 Critical task failed - stopping execution")
                    break
    
    def _dependencies_met(self, task: Dict[str, Any]) -> bool:
        """Check if task dependencies are met"""
        dependencies = task.get("dependencies", [])
        if not dependencies:
            return True
        
        completed_ids = [t["task_id"] for t in self.completed_tasks]
        return all(dep in completed_ids for dep in dependencies)
    
    def _build_task_prompt(self, task: Dict[str, Any]) -> str:
        """Build detailed prompt for task execution"""
        prompt = f"""
{task['description']}

**Files to Create:**
{chr(10).join(f"- {f}" for f in task.get('files_to_create', []))}

**Files to Modify:**
{chr(10).join(f"- {f}" for f in task.get('files_to_modify', []))}

**Acceptance Criteria:**
{chr(10).join(f"- {c}" for c in task.get('acceptance_criteria', []))}

**Context from Architecture:**
- Phase: {task.get('phase', 'N/A')}
- Type: {task['type']}
- Complexity: {task['complexity']}

{f"**Risks:** {chr(10).join(f'- {r}' for r in task.get('risks', []))}" if task.get('risks') else ""}

{f"**Notes:** {task.get('notes', '')}" if task.get('notes') else ""}
"""
        return prompt
    
    def _save_checkpoint(self, task_index: int):
        """Save progress checkpoint"""
        checkpoint_path = os.path.join(
            self.workspace_path,
            f".architect/{self.project_name}_checkpoint.json"
        )
        
        checkpoint = {
            "last_completed_index": task_index,
            "completed_tasks": [t["task_id"] for t in self.completed_tasks],
            "failed_tasks": [t["task_id"] for t in self.failed_tasks],
            "checkpoint_time": datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    
    def _print_analysis_summary(self):
        """Print summary of architectural analysis"""
        if not self.architectural_analysis:
            return
        
        logger.info("\n📊 ARCHITECTURAL ANALYSIS SUMMARY:")
        
        # Layer 1: Strategic
        strategic = self.architectural_analysis.get("layer_1_strategic", {})
        logger.info(f"\n🎯 Business Purpose: {strategic.get('business_purpose', 'N/A')[:100]}...")
        
        # Layer 2: Architecture
        arch = self.architectural_analysis.get("layer_2_architecture", {})
        logger.info(f"\n🏗️  System Pattern: {arch.get('system_pattern', 'N/A')}")
        
        # Layer 3: Modules
        modules = self.architectural_analysis.get("layer_3_modules", {})
        core_modules = modules.get("core_modules", [])
        logger.info(f"\n📦 Core Modules ({len(core_modules)}):")
        for mod in core_modules[:5]:  # Show first 5
            logger.info(f"   - {mod.get('name', 'N/A')}: {mod.get('purpose', 'N/A')[:60]}...")
        
        # Layer 5: Execution
        execution = self.architectural_analysis.get("layer_5_execution", {})
        phases = execution.get("phases", [])
        logger.info(f"\n📋 Development Phases ({len(phases)}):")
        for phase in phases:
            logger.info(f"   Phase {phase.get('phase', '?')}: {phase.get('name', 'N/A')}")
    
    def _print_plan_summary(self):
        """Print summary of execution plan"""
        if not self.execution_plan:
            return
        
        logger.info("\n📋 EXECUTION PLAN SUMMARY:")
        
        # Count by type
        by_type = {}
        by_complexity = {}
        total_hours = 0
        
        for task in self.execution_plan:
            task_type = task.get("type", "unknown")
            complexity = task.get("complexity", "unknown")
            hours = task.get("estimated_hours", 0)
            
            by_type[task_type] = by_type.get(task_type, 0) + 1
            by_complexity[complexity] = by_complexity.get(complexity, 0) + 1
            total_hours += hours
        
        logger.info(f"\n📊 Tasks by Type:")
        for task_type, count in by_type.items():
            logger.info(f"   - {task_type}: {count}")
        
        logger.info(f"\n📊 Tasks by Complexity:")
        for complexity, count in by_complexity.items():
            logger.info(f"   - {complexity}: {count}")
        
        logger.info(f"\n⏱️  Estimated Total: {total_hours} hours ({total_hours/8:.1f} days)")
