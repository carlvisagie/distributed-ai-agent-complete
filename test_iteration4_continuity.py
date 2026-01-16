"""
Test Iteration 4: Project-Level Continuity

Tests that the agent maintains holistic understanding across multiple related tasks.
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.autonomous.real_executor import RealExecutor

async def test_project_continuity():
    """
    Test with 3 related tasks to verify project-level continuity:
    1. Create webhook handler
    2. Enhance webhook with error handling
    3. Add webhook logging
    
    Each task should build on previous work, not duplicate it.
    """
    
    print("🧪 TESTING ITERATION 4: PROJECT-LEVEL CONTINUITY")
    print("=" * 80)
    
    workspace = "/home/ubuntu/just-talk-standalone"
    executor = RealExecutor(workspace)
    
    # Task 1: Create webhook
    print("\n📋 TASK 1: Create webhook handler")
    print("-" * 80)
    task1 = {
        'task_id': 'test_task_1',
        'title': 'Create Stripe webhook handler',
        'prompt': 'Create a webhook handler in server/webhooks/stripeWebhook.ts that handles checkout.session.completed events'
    }
    
    result1 = await executor.execute_task(task1)
    print(f"✅ Task 1 result: {result1['status']}")
    print(f"   Files: {result1.get('files_modified', [])}")
    
    # Task 2: Enhance webhook (should MODIFY existing file, not create new one)
    print("\n📋 TASK 2: Add error handling to webhook")
    print("-" * 80)
    task2 = {
        'task_id': 'test_task_2',
        'title': 'Add comprehensive error handling to webhook',
        'prompt': 'Add try-catch blocks, error logging, and retry logic to the Stripe webhook handler'
    }
    
    result2 = await executor.execute_task(task2)
    print(f"✅ Task 2 result: {result2['status']}")
    print(f"   Files: {result2.get('files_modified', [])}")
    
    # Task 3: Add logging (should MODIFY existing file again)
    print("\n📋 TASK 3: Add detailed logging")
    print("-" * 80)
    task3 = {
        'task_id': 'test_task_3',
        'title': 'Add detailed logging to webhook',
        'prompt': 'Add structured logging to track webhook events, including timestamps, event types, and outcomes'
    }
    
    result3 = await executor.execute_task(task3)
    print(f"✅ Task 3 result: {result3['status']}")
    print(f"   Files: {result3.get('files_modified', [])}")
    
    # Verify project memory
    print("\n🧠 PROJECT MEMORY CHECK")
    print("=" * 80)
    memory = executor.project_memory.memory
    print(f"Tasks completed: {memory['tasks_completed']}")
    print(f"Architectural decisions: {len(memory['architectural_decisions'])}")
    print(f"Files tracked: {len(memory['file_ownership'])}")
    print(f"Lessons learned: {len(memory['learned_lessons'])}")
    
    # Check if tasks built on each other (not duplicates)
    print("\n📊 CONTINUITY VERIFICATION")
    print("=" * 80)
    
    files_task1 = set(result1.get('files_modified', []))
    files_task2 = set(result2.get('files_modified', []))
    files_task3 = set(result3.get('files_modified', []))
    
    # Task 2 and 3 should modify the SAME file created in task 1
    if files_task1 & files_task2:
        print("✅ Task 2 MODIFIED existing files from Task 1 (good!)")
    else:
        print("❌ Task 2 created NEW files instead of modifying (bad!)")
    
    if files_task2 & files_task3:
        print("✅ Task 3 MODIFIED existing files from Task 2 (good!)")
    else:
        print("❌ Task 3 created NEW files instead of modifying (bad!)")
    
    print("\n🎉 ITERATION 4 TEST COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_project_continuity())
