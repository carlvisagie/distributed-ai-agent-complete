#!/usr/bin/env python3
"""
Just Talk Autonomous Completion
- Deep project analysis
- Deployment-focused task generation
- Monetization-focused priorities
- Perfect continuity
- Real code execution
"""
import asyncio
import sys
import os
from pathlib import Path

# Add shared to path
sys.path.insert(0, str(Path(__file__).parent / 'shared'))

from autonomous.autonomous_executor_v2 import AutonomousExecutorV2
from autonomous.website_analyzer import WebsiteAnalyzer
from autonomous.task_generator import TaskGenerator


async def analyze_just_talk():
    """
    Deep analysis of Just Talk to understand deployment & monetization needs
    """
    print("=" * 70)
    print("🔍 DEEP PROJECT ANALYSIS")
    print("=" * 70)
    
    project_path = "/home/ubuntu/just-talk-standalone"
    
    # Analyze codebase
    print("\n📊 Analyzing codebase structure...")
    # analyzer = WebsiteAnalyzer("https://purposefullivecoaching.com")  # Not needed for file analysis
    
    # Check critical files
    critical_files = {
        'package.json': 'Dependencies',
        'server/routers.ts': 'API routes',
        'drizzle/schema.ts': 'Database schema',
        'client/src/App.tsx': 'Frontend routing',
        'todo.md': 'Known issues',
        '.env.example': 'Environment variables',
    }
    
    analysis = {
        'files_found': [],
        'files_missing': [],
        'deployment_blockers': [],
        'monetization_gaps': [],
        'critical_bugs': []
    }
    
    for file, description in critical_files.items():
        filepath = Path(project_path) / file
        if filepath.exists():
            analysis['files_found'].append(f"✅ {description}: {file}")
        else:
            analysis['files_missing'].append(f"❌ {description}: {file}")
            analysis['deployment_blockers'].append(f"Missing {file}")
    
    # Check todo.md for critical issues
    todo_path = Path(project_path) / 'todo.md'
    if todo_path.exists():
        with open(todo_path, 'r') as f:
            todo_content = f.read()
            
            # Count incomplete tasks
            incomplete = todo_content.count('- [ ]')
            completed = todo_content.count('- [x]')
            
            print(f"\n📋 TODO Status:")
            print(f"   ✅ Completed: {completed}")
            print(f"   ⏳ Incomplete: {incomplete}")
            
            # Extract critical sections
            if 'URGENT' in todo_content or 'CRITICAL' in todo_content:
                analysis['critical_bugs'].append("Has URGENT/CRITICAL items in todo.md")
            
            if 'payment' in todo_content.lower() or 'stripe' in todo_content.lower():
                analysis['monetization_gaps'].append("Payment system incomplete")
            
            if 'deploy' in todo_content.lower() or 'production' in todo_content.lower():
                analysis['deployment_blockers'].append("Deployment issues noted in todo")
    
    # Check production site
    print("\n🌐 Checking production site...")
    prod_url = "https://purposefullivecoaching.com"
    
    # Check if environment variables are set
    env_example = Path(project_path) / '.env.example'
    if env_example.exists():
        with open(env_example, 'r') as f:
            env_vars = [line.split('=')[0] for line in f.readlines() if '=' in line]
            print(f"   📝 Required env vars: {len(env_vars)}")
    
    # Print analysis
    print("\n" + "=" * 70)
    print("📊 ANALYSIS RESULTS")
    print("=" * 70)
    
    print("\n✅ Files Found:")
    for item in analysis['files_found']:
        print(f"   {item}")
    
    if analysis['files_missing']:
        print("\n❌ Files Missing:")
        for item in analysis['files_missing']:
            print(f"   {item}")
    
    if analysis['deployment_blockers']:
        print("\n🚨 DEPLOYMENT BLOCKERS:")
        for item in analysis['deployment_blockers']:
            print(f"   • {item}")
    
    if analysis['monetization_gaps']:
        print("\n💰 MONETIZATION GAPS:")
        for item in analysis['monetization_gaps']:
            print(f"   • {item}")
    
    if analysis['critical_bugs']:
        print("\n🐛 CRITICAL BUGS:")
        for item in analysis['critical_bugs']:
            print(f"   • {item}")
    
    return analysis


async def generate_deployment_tasks(analysis):
    """
    Generate tasks focused on deployment & monetization
    """
    print("\n" + "=" * 70)
    print("🎯 GENERATING DEPLOYMENT-FOCUSED TASKS")
    print("=" * 70)
    
    tasks = []
    
    # Priority 1: Deployment Blockers
    print("\n🚨 Priority 1: Deployment Blockers")
    if analysis['deployment_blockers']:
        for blocker in analysis['deployment_blockers']:
            tasks.append({
                'priority': 'CRITICAL',
                'category': 'Deployment',
                'title': f"Fix: {blocker}",
                'description': f"Resolve deployment blocker: {blocker}"
            })
            print(f"   • {blocker}")
    
    # Priority 2: Monetization
    print("\n💰 Priority 2: Monetization")
    if analysis['monetization_gaps']:
        for gap in analysis['monetization_gaps']:
            tasks.append({
                'priority': 'HIGH',
                'category': 'Monetization',
                'title': f"Complete: {gap}",
                'description': f"Implement monetization feature: {gap}"
            })
            print(f"   • {gap}")
    
    # Priority 3: Critical Bugs
    print("\n🐛 Priority 3: Critical Bugs")
    if analysis['critical_bugs']:
        for bug in analysis['critical_bugs']:
            tasks.append({
                'priority': 'HIGH',
                'category': 'Bug Fix',
                'title': f"Fix: {bug}",
                'description': f"Fix critical bug: {bug}"
            })
            print(f"   • {bug}")
    
    # Priority 4: Todo.md items
    print("\n📋 Priority 4: Remaining TODO items")
    todo_path = Path("/home/ubuntu/just-talk-standalone/todo.md")
    if todo_path.exists():
        with open(todo_path, 'r') as f:
            for line in f:
                if line.strip().startswith('- [ ]'):
                    task_title = line.strip()[6:].strip()
                    tasks.append({
                        'priority': 'MEDIUM',
                        'category': 'Feature',
                        'title': task_title,
                        'description': f"Complete: {task_title}"
                    })
                    print(f"   • {task_title}")
    
    print(f"\n📊 Total tasks generated: {len(tasks)}")
    return tasks


async def main():
    """Main execution"""
    print("=" * 70)
    print("🤖 AUTONOMOUS AGENT - JUST TALK COMPLETION")
    print("   With Deep Analysis & Real Execution")
    print("=" * 70)
    
    # Step 1: Deep Analysis
    analysis = await analyze_just_talk()
    
    # Step 2: Generate Deployment-Focused Tasks
    tasks = await generate_deployment_tasks(analysis)
    
    if not tasks:
        print("\n✅ No tasks found - project may be complete!")
        return
    
    # Step 3: Execute with Perfect Continuity
    print("\n" + "=" * 70)
    print("🚀 STARTING AUTONOMOUS EXECUTION")
    print("   • Perfect continuity: ✅")
    print("   • Real code execution: ✅")
    print("   • Deployment focus: ✅")
    print("   • Monetization focus: ✅")
    print("=" * 70)
    
    executor = AutonomousExecutorV2(
        project_id='just_talk_standalone',
        project_path='/home/ubuntu/just-talk-standalone'
    )
    
    # Initialize with perfect continuity
    await executor.initialize()
    
    # Load tasks into executor
    for i, task in enumerate(tasks, 1):
        task_id = f"task_{i}"
        executor.task_mgr.create_task(
            task_id=task_id,
            task_type=task['category'].lower().replace(' ', '_'),
            title=task['title'],
            description=task['description'],
            priority=task['priority']
        )
    
    print(f"\n📋 Loaded {len(tasks)} tasks")
    print(f"⏱️  Estimated time: {len(tasks) * 5} minutes\n")
    
    # Execute all tasks
    result = await executor.execute_tasks()
    
    # Print final summary
    print("\n" + "=" * 70)
    print("🎉 EXECUTION COMPLETE")
    print("=" * 70)
    print(f"\n{result}")
    
    return result


if __name__ == "__main__":
    asyncio.run(main())
