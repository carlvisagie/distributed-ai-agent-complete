#!/usr/bin/env python3
"""
Test single task execution with fixed code
"""
import asyncio
import sys
import os

sys.path.insert(0, 'shared')

from autonomous.real_executor import RealExecutor

# Set API key
os.environ['ANTHROPIC_API_KEY'] = os.getenv('ANTHROPIC_API_KEY', '')

async def test_task():
    print("\n" + "="*70)
    print("🧪 TESTING SINGLE TASK EXECUTION")
    print("="*70 + "\n")
    
    # Initialize executor
    executor = RealExecutor(
        workspace_path='/home/ubuntu/just-talk-standalone',
        llm_api_key=os.environ['ANTHROPIC_API_KEY']
    )
    
    # Test task: Fix the trial banner display issue
    test_task = {
        'task_id': 'test_001',
        'title': 'Fix trial banner display issue',
        'description': '''The trial banner should show remaining messages but it's not displaying.

Current issue:
- Trial fields exist in database (trialMessagesRemaining, trialStartDate)
- Frontend has TrialBanner component
- But banner doesn't show up

Fix needed:
1. Check if trial data is being loaded in Chat.tsx
2. Verify the banner visibility logic
3. Make sure new users start with 100 trial messages
4. Test that banner appears and shows correct count

Files to check/modify:
- client/src/pages/Chat.tsx
- server/routers.ts (chat.send procedure)
- drizzle/schema.ts (verify trial fields)
''',
        'prompt': 'Fix the trial banner so it displays correctly and shows remaining messages'
    }
    
    print(f"Task: {test_task['title']}")
    print(f"Description: {test_task['description'][:200]}...")
    print("\n" + "="*70)
    print("🚀 EXECUTING...")
    print("="*70 + "\n")
    
    # Execute
    result = await executor.execute_task(test_task)
    
    # Show results
    print("\n" + "="*70)
    print("📊 RESULTS")
    print("="*70)
    print(f"Status: {result['status']}")
    print(f"Files modified: {result.get('files_modified', [])}")
    print(f"Execution time: {result.get('execution_time', 'unknown')}")
    print(f"Details: {result.get('details', 'N/A')}")
    
    if result['status'] == 'success':
        print("\n✅ Task completed successfully!")
        print("\nNext: Check git diff to verify quality")
    else:
        print(f"\n❌ Task failed: {result.get('error', 'Unknown error')}")
    
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        asyncio.run(test_task())
    except KeyboardInterrupt:
        print("\n\n⏸️  Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
