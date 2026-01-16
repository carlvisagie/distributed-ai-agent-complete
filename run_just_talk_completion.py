#!/usr/bin/env python3
"""
Run autonomous completion of Just Talk
Parses todo.md and executes all incomplete tasks
"""
import asyncio
import sys
import os
import re
from pathlib import Path

sys.path.insert(0, 'shared')

from autonomous.autonomous_executor_v2 import AutonomousExecutorV2
from autonomous.task_state_manager import TaskState, TaskStatus, TaskPriority

# Set to use REAL execution
os.environ['USE_REAL_EXECUTION'] = 'true'
os.environ['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY', '')

def parse_todo_md(todo_path: str, project_id: str) -> list[TaskState]:
    """Parse todo.md and extract incomplete tasks"""
    tasks = []
    
    with open(todo_path, 'r') as f:
        content = f.read()
    
    # Find all incomplete tasks (lines with [ ])
    incomplete_pattern = r'- \[ \] (.+)'
    matches = re.findall(incomplete_pattern, content)
    
    # Also capture context (section headers)
    lines = content.split('\n')
    current_section = "General"
    
    for line in lines:
        # Check if it's a section header
        if line.startswith('##'):
            current_section = line.replace('#', '').strip()
            continue
        
        # Check if it's an incomplete task
        if '- [ ]' in line:
            task_text = line.split('- [ ]')[1].strip()
            
            # Determine priority from section
            priority = 'medium'
            if 'CRITICAL' in current_section or 'URGENT' in current_section:
                priority = 'critical'
            elif 'P0' in current_section:
                priority = 'high'
            elif 'P1' in current_section:
                priority = 'medium'
            
            # Create task
            task = TaskState(
                task_id=f"task_{len(tasks) + 1}",
                project_id=project_id,
                title=task_text[:100],  # Truncate long titles
                description=f"From section: {current_section}\n\n{task_text}",
                priority=priority,
                task_type='feature',
                estimated_duration=3600  # 1 hour in seconds
            )
            tasks.append(task)
    
    return tasks

async def main():
    print("\n" + "="*70)
    print("🤖 AUTONOMOUS AGENT - JUST TALK COMPLETION")
    print("="*70 + "\n")
    
    # Parse todo.md
    todo_path = '/home/ubuntu/just-talk-standalone/todo.md'
    project_id = 'just_talk_standalone'
    print(f"📋 Parsing {todo_path}...")
    tasks = parse_todo_md(todo_path, project_id)
    
    print(f"\n✅ Found {len(tasks)} incomplete tasks\n")
    
    # Show first 10 tasks
    print("📝 Tasks to complete:")
    for i, task in enumerate(tasks[:10], 1):
        print(f"   {i}. [{task.priority.upper()}] {task.title}")
    
    if len(tasks) > 10:
        print(f"   ... and {len(tasks) - 10} more\n")
    
    # Initialize executor
    print("\n🚀 Initializing autonomous executor...")
    executor = AutonomousExecutorV2(
        project_id='just_talk_standalone',
        project_path='/home/ubuntu/just-talk-standalone'
    )
    
    success = await executor.initialize()
    if not success:
        print("❌ Initialization failed")
        return
    print("✅ Executor initialized\n")
    
    # ITERATION 5: Pre-flight build check
    print("🔍 ITERATION 5: Pre-flight build verification...")
    import subprocess
    try:
        result = subprocess.run(
            ['pnpm', 'run', 'build'],
            cwd='/home/ubuntu/just-talk-standalone',
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode != 0:
            print("⚠️  BUILD FAILED! Foundation is broken!")
            print("🔧 Attempting automatic repair...")
            
            # Create repair task
            repair_task = TaskState(
                task_id="repair_foundation",
                project_id=project_id,
                title="Fix broken build before starting tasks",
                description=f"The build is currently failing. Fix all build errors before proceeding.\n\nBuild errors:\n{result.stderr}",
                priority='critical',
                task_type='bugfix',
                estimated_duration=1800
            )
            
            # Execute repair task
            repair_result = await executor.execute_tasks([repair_task])
            
            if repair_result.get('completed', 0) == 0:
                print("❌ Failed to repair foundation! Cannot proceed.")
                return
            
            print("✅ Foundation repaired! Proceeding with tasks...\n")
        else:
            print("✅ Build passes! Foundation is clean.\n")
    except Exception as e:
        print(f"⚠️  Could not verify build: {e}")
        print("Proceeding anyway...\n")
    
    # Ask for confirmation
    print("="*70)
    print(f"⚠️  READY TO EXECUTE {len(tasks)} TASKS")
    print("="*70)
    print(f"Mode: REAL EXECUTION (will modify actual code)")
    print(f"Project: Just Talk Standalone")
    print(f"Estimated time: {len(tasks) * 5} minutes ({len(tasks) * 5 / 60:.1f} hours)")
    print("="*70 + "\n")
    
    # Execute all tasks
    print("▶️  STARTING EXECUTION...\n")
    
    result = await executor.execute_tasks(
        tasks=tasks,
        auto_pr=True,  # Create PRs automatically
        checkpoint_interval=5  # Checkpoint every 5 tasks
    )
    
    # Show results
    print("\n" + "="*70)
    print("📊 EXECUTION COMPLETE")
    print("="*70)
    print(f"Total tasks: {result.get('total', 0)}")
    print(f"Completed: {result.get('completed', 0)}")
    print(f"Failed: {result.get('failed', 0)}")
    print(f"Success rate: {result.get('completion_percentage', 0):.1f}%")
    print("="*70 + "\n")
    
    if result.get('completed', 0) > 0:
        print("✅ Just Talk completion tasks executed!")
        print("📝 Check GitHub for PRs")
        print("🎉 Review and merge when ready!")
    else:
        print("⚠️  No tasks completed - check logs for errors")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏸️  Execution paused by user")
        print("   Progress has been saved - you can resume anytime!")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
