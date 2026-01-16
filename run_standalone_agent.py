#!/usr/bin/env python3
"""
Standalone AI Agent System - Universal Project Completion Tool

This script runs the autonomous agent on ANY project with perfect continuity.
Configure your project in standalone_config.json and run.
"""
import asyncio
import sys
import os
import json
import re
from pathlib import Path

sys.path.insert(0, 'shared')

from autonomous.autonomous_executor_v2 import AutonomousExecutorV2
from autonomous.task_state_manager import TaskState, TaskStatus, TaskPriority

def load_config():
    """Load configuration from standalone_config.json"""
    config_path = Path(__file__).parent / 'standalone_config.json'
    
    if not config_path.exists():
        print("❌ Configuration file not found: standalone_config.json")
        print("\n📝 Create standalone_config.json with:")
        print("""
{
  "project_id": "my_project",
  "project_path": "/path/to/your/project",
  "project_name": "My Project Name",
  "auto_pr": true,
  "checkpoint_interval": 5,
  "todo_file": "todo.md"
}
        """)
        sys.exit(1)
    
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Validate required fields
    required = ['project_id', 'project_path', 'project_name']
    for field in required:
        if field not in config:
            print(f"❌ Missing required field in config: {field}")
            sys.exit(1)
    
    # Set defaults
    config.setdefault('auto_pr', True)
    config.setdefault('checkpoint_interval', 5)
    config.setdefault('todo_file', 'todo.md')
    
    return config

def parse_todo_md(todo_path: str, project_id: str) -> list[TaskState]:
    """Parse todo.md and extract incomplete tasks"""
    if not Path(todo_path).exists():
        print(f"⚠️  TODO file not found: {todo_path}")
        print("   Agent will analyze project and generate tasks automatically")
        return []
    
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
            elif 'P0' in current_section or 'HIGH' in current_section:
                priority = 'high'
            elif 'P1' in current_section:
                priority = 'medium'
            elif 'LOW' in current_section:
                priority = 'low'
            
            # Determine task type from keywords
            task_type = 'feature'
            task_lower = task_text.lower()
            if 'fix' in task_lower or 'bug' in task_lower:
                task_type = 'bugfix'
            elif 'test' in task_lower:
                task_type = 'testing'
            elif 'document' in task_lower or 'doc' in task_lower:
                task_type = 'documentation'
            elif 'refactor' in task_lower:
                task_type = 'refactor'
            
            # Create task
            task = TaskState(
                task_id=f"task_{len(tasks) + 1}",
                project_id=project_id,
                title=task_text[:100],  # Truncate long titles
                description=f"From section: {current_section}\n\n{task_text}",
                priority=priority,
                task_type=task_type,
                estimated_duration=3600  # 1 hour in seconds
            )
            tasks.append(task)
    
    return tasks

async def main():
    print("\n" + "="*70)
    print("🤖 STANDALONE AI AGENT SYSTEM")
    print("="*70 + "\n")
    
    # Load configuration
    print("📋 Loading configuration...")
    config = load_config()
    
    project_id = config['project_id']
    project_path = config['project_path']
    project_name = config['project_name']
    auto_pr = config['auto_pr']
    checkpoint_interval = config['checkpoint_interval']
    todo_file = config['todo_file']
    
    print(f"   Project: {project_name}")
    print(f"   Path: {project_path}")
    print(f"   ID: {project_id}\n")
    
    # Verify project path exists
    if not Path(project_path).exists():
        print(f"❌ Project path does not exist: {project_path}")
        sys.exit(1)
    
    # Parse todo.md if it exists
    todo_path = Path(project_path) / todo_file
    print(f"📋 Checking for TODO file: {todo_path}...")
    tasks = parse_todo_md(str(todo_path), project_id)
    
    if tasks:
        print(f"\n✅ Found {len(tasks)} incomplete tasks\n")
        
        # Show first 10 tasks
        print("📝 Tasks to complete:")
        for i, task in enumerate(tasks[:10], 1):
            print(f"   {i}. [{task.priority.upper()}] {task.title}")
        
        if len(tasks) > 10:
            print(f"   ... and {len(tasks) - 10} more\n")
    else:
        print("   No TODO file found - agent will analyze and generate tasks\n")
    
    # Initialize executor
    print("🚀 Initializing autonomous executor...")
    executor = AutonomousExecutorV2(
        project_id=project_id,
        project_path=project_path
    )
    
    success = await executor.initialize()
    if not success:
        print("❌ Initialization failed")
        return
    print("✅ Executor initialized\n")
    
    # Show execution plan
    print("="*70)
    if tasks:
        print(f"⚠️  READY TO EXECUTE {len(tasks)} TASKS")
    else:
        print("⚠️  READY TO ANALYZE PROJECT AND GENERATE TASKS")
    print("="*70)
    print(f"Mode: REAL EXECUTION (will modify actual code)")
    print(f"Project: {project_name}")
    print(f"Auto PR: {'Enabled' if auto_pr else 'Disabled'}")
    print(f"Checkpoint interval: Every {checkpoint_interval} tasks")
    if tasks:
        print(f"Estimated time: {len(tasks) * 5} minutes ({len(tasks) * 5 / 60:.1f} hours)")
    print("="*70 + "\n")
    
    # Check for API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("❌ ANTHROPIC_API_KEY environment variable not set")
        print("\n   Set it with:")
        print("   export ANTHROPIC_API_KEY='your-api-key-here'\n")
        sys.exit(1)
    
    # Execute
    print("▶️  STARTING EXECUTION...\n")
    
    result = await executor.execute_tasks(
        tasks=tasks if tasks else None,  # None = auto-generate tasks
        auto_pr=auto_pr,
        checkpoint_interval=checkpoint_interval
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
        print("✅ Tasks executed successfully!")
        if auto_pr:
            print("📝 Check GitHub for PRs")
            print("🎉 Review and merge when ready!")
        else:
            print("📝 Changes committed to local repository")
            print("🎉 Review and push when ready!")
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
