#!/usr/bin/env python3
"""Test Iteration 3 improvements with task_1 (webhook) that failed before"""

import asyncio
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from shared.autonomous.real_executor import RealExecutor

async def main():
    # Initialize executor
    executor = RealExecutor(
        workspace_path="/home/ubuntu/just-talk-standalone",
        llm_api_key=os.getenv("ANTHROPIC_API_KEY")
    )
    
    # Test task_1 (webhook) that failed before
    task = {
        'task_id': 'task_1',
        'task_type': 'feature',
        'title': 'Create user account after successful payment (webhook needed)',
        'prompt': '''From section: 🚨 URGENT: Payment System

Task: Create user account after successful payment (webhook needed)

Context: The payment system is set up, but we need to create user accounts automatically when payment succeeds.

Requirements:
1. Create Stripe webhook endpoint to handle checkout.session.completed
2. Extract customer email and payment details from webhook
3. Create user account in database
4. Send welcome email (optional for now)
5. Handle errors gracefully

The webhook should integrate with existing Stripe setup and database schema.'''
    }
    
    print("🧪 TESTING ITERATION 3 WITH TASK_1 (webhook)")
    print("=" * 80)
    
    result = await executor.execute_task(task)
    
    print("\n" + "=" * 80)
    print(f"✅ Test complete!")
    print(f"Status: {result.get('status')}")
    print(f"Files modified: {result.get('files_modified', [])}")
    
    if result.get('status') == 'success':
        print("\n🎉 ITERATION 3 SUCCESS! Task_1 completed!")
    else:
        print(f"\n❌ Task failed: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
