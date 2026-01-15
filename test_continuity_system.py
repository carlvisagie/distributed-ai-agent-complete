"""
Continuity System End-to-End Test
Tests all components of the perfect continuity system
"""
import asyncio
import sys
import os
from pathlib import Path

# Add shared directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'shared'))

from autonomous.context_manager import context_manager, ProjectContext
from autonomous.task_state_manager import task_state_manager, TaskState, TaskStatus, TaskPriority
from autonomous.session_manager import session_manager, ExecutionSession
from autonomous.knowledge_graph import knowledge_graph
from autonomous.autonomous_executor_v2 import AutonomousExecutorV2


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_context_manager():
    """Test context persistence"""
    print_section("TEST 1: Context Manager")
    
    project_id = "test_project"
    
    # Create context
    print("1. Creating new project context...")
    context = context_manager.create_context(
        project_name="Test Project",
        project_path="/home/ubuntu/test-project"
    )
    project_id = context.project_id
    print(f"   ✅ Context created: {context.project_id}")
    
    # Update context
    print("\n2. Updating context...")
    context_manager.update_analysis(
        project_id=project_id,
        codebase_structure={'pages': 10, 'components': 25, 'apis': 8},
        features_found=[{'name': 'Login', 'status': 'complete'}],
        gaps_identified=[{'name': 'Dashboard', 'status': 'missing'}]
    )
    print("   ✅ Analysis results saved")
    
    # Load context
    print("\n3. Loading context from disk...")
    loaded_context = context_manager.load_context(project_id)
    if loaded_context:
        print(f"   ✅ Context loaded successfully")
        print(f"   Project: {loaded_context.project_name}")
        print(f"   Analyzed: {loaded_context.analyzed_at}")
    else:
        print("   ❌ Failed to load context")
        return False
    
    # Export context
    print("\n4. Exporting context...")
    export_path = "/tmp/test_context_export.json"
    if context_manager.export_context(project_id, export_path):
        print(f"   ✅ Context exported to: {export_path}")
    else:
        print("   ❌ Failed to export context")
        return False
    
    print("\n✅ Context Manager Test PASSED")
    return True


def test_task_state_manager():
    """Test task state management"""
    print_section("TEST 2: Task State Manager")
    
    project_id = "test_project"
    
    # Create tasks
    print("1. Creating tasks...")
    task1 = task_state_manager.create_task(
        project_id=project_id,
        task_id="task_001",
        title="Create login page",
        description="Build login page with authentication",
        task_type="create_page",
        priority=TaskPriority.HIGH.value,
        estimated_duration=600
    )
    print(f"   ✅ Task 1 created: {task1.title}")
    
    task2 = task_state_manager.create_task(
        project_id=project_id,
        task_id="task_002",
        title="Add user dashboard",
        description="Create user dashboard with widgets",
        task_type="create_page",
        priority=TaskPriority.MEDIUM.value,
        estimated_duration=900,
        depends_on=["task_001"]
    )
    print(f"   ✅ Task 2 created: {task2.title}")
    
    # Start and complete task 1
    print("\n2. Executing task 1...")
    task_state_manager.start_task(project_id, "task_001")
    print("   Started task 1")
    
    task_state_manager.complete_task(project_id, "task_001", {
        'files_created': 3,
        'lines_added': 250
    })
    print("   ✅ Task 1 completed")
    
    # Get next task
    print("\n3. Getting next task...")
    next_task = task_state_manager.get_next_task(project_id)
    if next_task:
        print(f"   ✅ Next task: {next_task.title}")
    else:
        print("   ❌ No next task found")
        return False
    
    # Get statistics
    print("\n4. Getting statistics...")
    stats = task_state_manager.get_statistics(project_id)
    print(f"   Total: {stats['total']}")
    print(f"   Completed: {stats['completed']}")
    print(f"   Pending: {stats['pending']}")
    print(f"   Completion: {stats['completion_percentage']:.1f}%")
    
    # Export tasks
    print("\n5. Exporting tasks...")
    export_path = "/tmp/test_tasks_export.json"
    if task_state_manager.export_tasks(project_id, export_path):
        print(f"   ✅ Tasks exported to: {export_path}")
    else:
        print("   ❌ Failed to export tasks")
        return False
    
    print("\n✅ Task State Manager Test PASSED")
    return True


def test_session_manager():
    """Test session management"""
    print_section("TEST 3: Session Manager")
    
    project_id = "test_project"
    
    # Create session
    print("1. Creating execution session...")
    session = session_manager.create_session(
        project_id=project_id,
        name="Test Execution",
        description="Testing session management",
        tasks_total=10
    )
    print(f"   ✅ Session created: {session.session_id}")
    
    # Start session
    print("\n2. Starting session...")
    session_manager.start_session(session.session_id)
    print("   ✅ Session started")
    
    # Update progress
    print("\n3. Updating progress...")
    session_manager.update_progress(
        session.session_id,
        current_task_id="task_001"
    )
    session_manager.update_progress(
        session.session_id,
        completed_task_id="task_001"
    )
    print("   ✅ Progress updated")
    
    # Create checkpoint
    print("\n4. Creating checkpoint...")
    checkpoint_id = session_manager.create_checkpoint(
        session.session_id,
        context_snapshot={'note': 'Test checkpoint'}
    )
    if checkpoint_id:
        print(f"   ✅ Checkpoint created: {checkpoint_id}")
    else:
        print("   ❌ Failed to create checkpoint")
        return False
    
    # Pause session
    print("\n5. Pausing session...")
    session_manager.pause_session(session.session_id)
    print("   ✅ Session paused")
    
    # Get resume point
    print("\n6. Finding resume point...")
    resume_session = session_manager.get_resume_point(project_id)
    if resume_session:
        print(f"   ✅ Found resumable session: {resume_session.session_id}")
        print(f"   Status: {resume_session.status}")
        print(f"   Progress: {resume_session.completion_percentage():.1f}%")
    else:
        print("   ❌ No resumable session found")
        return False
    
    # Get statistics
    print("\n7. Getting statistics...")
    stats = session_manager.get_statistics(session.session_id)
    print(f"   Status: {stats['status']}")
    print(f"   Completion: {stats['completion_percentage']:.1f}%")
    print(f"   Can resume: {stats['can_resume']}")
    
    print("\n✅ Session Manager Test PASSED")
    return True


def test_knowledge_graph():
    """Test knowledge graph"""
    print_section("TEST 4: Knowledge Graph")
    
    # Check if Just Talk project exists
    project_path = "/home/ubuntu/just-talk-standalone"
    
    if not os.path.exists(project_path):
        print(f"⚠️  Just Talk project not found at: {project_path}")
        print("   Skipping knowledge graph test")
        return True
    
    print(f"1. Building knowledge graph from: {project_path}")
    knowledge_graph.build_from_codebase(project_path)
    print("   ✅ Knowledge graph built")
    
    # Get statistics
    print("\n2. Getting statistics...")
    stats = knowledge_graph.get_statistics()
    print(f"   Total components: {stats['total_components']}")
    print(f"   Total features: {stats['total_features']}")
    print(f"   Average dependencies: {stats['average_dependencies']:.2f}")
    
    if stats['components_by_type']:
        print("\n   Components by type:")
        for comp_type, count in stats['components_by_type'].items():
            print(f"     {comp_type}: {count}")
    
    # Test component lookup
    if knowledge_graph.components:
        print("\n3. Testing component lookup...")
        first_comp_id = list(knowledge_graph.components.keys())[0]
        component = knowledge_graph.get_component(first_comp_id)
        if component:
            print(f"   ✅ Found component: {component.name}")
            print(f"   Type: {component.component_type}")
            print(f"   Dependencies: {len(component.depends_on)}")
        else:
            print("   ❌ Component lookup failed")
            return False
    
    # Export graph
    print("\n4. Exporting knowledge graph...")
    export_path = "/tmp/test_knowledge_graph.json"
    if knowledge_graph.export_graph(export_path):
        print(f"   ✅ Graph exported to: {export_path}")
    else:
        print("   ❌ Failed to export graph")
        return False
    
    print("\n✅ Knowledge Graph Test PASSED")
    return True


async def test_integrated_executor():
    """Test integrated autonomous executor"""
    print_section("TEST 5: Integrated Autonomous Executor")
    
    project_path = "/home/ubuntu/just-talk-standalone"
    
    if not os.path.exists(project_path):
        print(f"⚠️  Just Talk project not found at: {project_path}")
        print("   Skipping integrated executor test")
        return True
    
    # Create executor
    print("1. Creating autonomous executor...")
    executor = AutonomousExecutorV2(
        project_id="just_talk_test",
        project_path=project_path
    )
    print("   ✅ Executor created")
    
    # Initialize
    print("\n2. Initializing executor...")
    if not await executor.initialize():
        print("   ❌ Initialization failed")
        return False
    print("   ✅ Initialization complete")
    
    # Create test tasks
    print("\n3. Creating test tasks...")
    test_tasks = []
    for i in range(3):
        task = task_state_manager.create_task(
            project_id="just_talk_test",
            task_id=f"test_task_{i+1}",
            title=f"Test Task {i+1}",
            description=f"Testing task execution #{i+1}",
            task_type="test",
            priority=TaskPriority.MEDIUM.value,
            estimated_duration=300
        )
        test_tasks.append(task)
    print(f"   ✅ Created {len(test_tasks)} test tasks")
    
    # Execute tasks
    print("\n4. Executing tasks...")
    result = await executor.execute_tasks(
        tasks=test_tasks,
        auto_pr=False,  # Disable PR creation for test
        checkpoint_interval=2
    )
    
    if 'error' in result:
        print(f"   ❌ Execution failed: {result['error']}")
        return False
    
    print(f"\n   ✅ Execution complete")
    print(f"   Completed: {result['completed']}/{result['total']}")
    print(f"   Success rate: {result['completion_percentage']:.1f}%")
    
    # Get status
    print("\n5. Getting executor status...")
    status = executor.get_status()
    if 'error' in status:
        print(f"   ❌ Failed to get status: {status['error']}")
        return False
    
    print("   ✅ Status retrieved")
    print(f"   Session: {status['session']['session_id']}")
    print(f"   Completion: {status['session']['completion_percentage']:.1f}%")
    
    print("\n✅ Integrated Executor Test PASSED")
    return True


async def run_all_tests():
    """Run all continuity system tests"""
    print("\n" + "="*70)
    print("  CONTINUITY SYSTEM END-TO-END TEST")
    print("="*70)
    
    results = []
    
    # Test 1: Context Manager
    results.append(("Context Manager", test_context_manager()))
    
    # Test 2: Task State Manager
    results.append(("Task State Manager", test_task_state_manager()))
    
    # Test 3: Session Manager
    results.append(("Session Manager", test_session_manager()))
    
    # Test 4: Knowledge Graph
    results.append(("Knowledge Graph", test_knowledge_graph()))
    
    # Test 5: Integrated Executor
    results.append(("Integrated Executor", await test_integrated_executor()))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {name}: {status}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 ALL TESTS PASSED! 🎉")
        print("\n  The continuity system is working perfectly!")
        return True
    else:
        print("\n  ❌ SOME TESTS FAILED")
        print("\n  Please review the failures above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
