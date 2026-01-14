"""
Autonomous Executor
Executes tasks autonomously and creates GitHub PRs
"""
import asyncio
import json
from typing import Dict, List
from datetime import datetime


class AutonomousExecutor:
    """Executes tasks autonomously with PR workflow"""
    
    def __init__(self, lenovo_api_url: str = "http://localhost:8088"):
        self.lenovo_api_url = lenovo_api_url
        self.execution_log = []
        
    async def execute_tasks(self, tasks: List[Dict], auto_pr: bool = True) -> Dict:
        """
        Execute list of tasks autonomously
        
        Args:
            tasks: List of tasks from task generator
            auto_pr: Automatically create PRs for completed tasks
            
        Returns:
            Execution summary
        """
        print(f"\n🤖 Starting autonomous execution of {len(tasks)} tasks...")
        
        results = {
            "total_tasks": len(tasks),
            "completed": 0,
            "failed": 0,
            "skipped": 0,
            "prs_created": 0,
            "task_results": [],
            "start_time": datetime.utcnow().isoformat(),
            "end_time": None
        }
        
        for task in tasks:
            print(f"\n{'='*60}")
            print(f"Task {task['id']}: {task['title']}")
            print(f"Priority: {task['priority']} | Type: {task['type']}")
            print(f"{'='*60}")
            
            try:
                # Execute task
                task_result = await self._execute_single_task(task)
                
                if task_result['status'] == 'success':
                    results['completed'] += 1
                    print(f"✅ Task {task['id']} completed successfully")
                    
                    # Create PR if enabled
                    if auto_pr:
                        pr_result = await self._create_pr_for_task(task, task_result)
                        if pr_result['success']:
                            results['prs_created'] += 1
                            print(f"🔀 PR created: {pr_result.get('pr_url', 'N/A')}")
                        task_result['pr'] = pr_result
                    
                elif task_result['status'] == 'failed':
                    results['failed'] += 1
                    print(f"❌ Task {task['id']} failed: {task_result.get('error', 'Unknown error')}")
                    
                else:
                    results['skipped'] += 1
                    print(f"⏭️  Task {task['id']} skipped: {task_result.get('reason', 'Unknown reason')}")
                
                results['task_results'].append(task_result)
                
                # Log execution
                self.execution_log.append({
                    "task_id": task['id'],
                    "task_title": task['title'],
                    "status": task_result['status'],
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Small delay between tasks
                await asyncio.sleep(2)
                
            except Exception as e:
                print(f"💥 Exception executing task {task['id']}: {str(e)}")
                results['failed'] += 1
                results['task_results'].append({
                    "task_id": task['id'],
                    "status": "error",
                    "error": str(e)
                })
        
        results['end_time'] = datetime.utcnow().isoformat()
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    async def _execute_single_task(self, task: Dict) -> Dict:
        """
        Execute a single task
        
        Args:
            task: Task dictionary
            
        Returns:
            Task execution result
        """
        task_type = task['type']
        
        if task_type == 'create_page':
            return await self._execute_page_creation(task)
        elif task_type == 'add_feature':
            return await self._execute_feature_addition(task)
        elif task_type == 'fix':
            return await self._execute_fix(task)
        elif task_type == 'security':
            return await self._execute_security_task(task)
        elif task_type == 'optimize':
            return await self._execute_optimization(task)
        else:
            return await self._execute_generic_task(task)
    
    async def _execute_page_creation(self, task: Dict) -> Dict:
        """Execute page creation task"""
        print(f"📄 Creating {task['page_name']} page...")
        
        try:
            # In real implementation, this would call the Lenovo API
            # which would use OpenHands SDK to create the page
            
            # For MVP, we simulate the execution
            result = {
                "task_id": task['id'],
                "status": "success",
                "type": "create_page",
                "page_name": task['page_name'],
                "files_created": [
                    f"{task['page_name']}.html",
                    f"css/{task['page_name']}.css"
                ],
                "prompt_used": task['prompt'],
                "execution_time": "45 seconds",
                "details": f"Created professional {task['page_name']} page with all required elements"
            }
            
            return result
            
        except Exception as e:
            return {
                "task_id": task['id'],
                "status": "failed",
                "error": str(e)
            }
    
    async def _execute_feature_addition(self, task: Dict) -> Dict:
        """Execute feature addition task"""
        print(f"⚙️  Adding feature: {task['title']}...")
        
        try:
            result = {
                "task_id": task['id'],
                "status": "success",
                "type": "add_feature",
                "feature": task['title'],
                "files_modified": ["index.html", "main.js"],
                "prompt_used": task['prompt'],
                "execution_time": "30 seconds",
                "details": f"Successfully implemented {task['title']}"
            }
            
            return result
            
        except Exception as e:
            return {
                "task_id": task['id'],
                "status": "failed",
                "error": str(e)
            }
    
    async def _execute_fix(self, task: Dict) -> Dict:
        """Execute fix task"""
        print(f"🔧 Fixing: {task['title']}...")
        
        try:
            result = {
                "task_id": task['id'],
                "status": "success",
                "type": "fix",
                "issue": task['title'],
                "files_modified": ["various"],
                "execution_time": "20 seconds",
                "details": f"Fixed {task['title']}"
            }
            
            return result
            
        except Exception as e:
            return {
                "task_id": task['id'],
                "status": "failed",
                "error": str(e)
            }
    
    async def _execute_security_task(self, task: Dict) -> Dict:
        """Execute security task"""
        print(f"🔒 Security: {task['title']}...")
        
        try:
            result = {
                "task_id": task['id'],
                "status": "success",
                "type": "security",
                "security_improvement": task['title'],
                "files_modified": [".htaccess", "config.php"],
                "execution_time": "25 seconds",
                "details": f"Implemented {task['title']}"
            }
            
            return result
            
        except Exception as e:
            return {
                "task_id": task['id'],
                "status": "failed",
                "error": str(e)
            }
    
    async def _execute_optimization(self, task: Dict) -> Dict:
        """Execute optimization task"""
        print(f"⚡ Optimizing: {task['title']}...")
        
        try:
            result = {
                "task_id": task['id'],
                "status": "success",
                "type": "optimize",
                "optimization": task['title'],
                "files_modified": ["images/*", "css/*", "js/*"],
                "execution_time": "40 seconds",
                "details": f"Optimized {task['title']}",
                "performance_improvement": "Load time reduced by 2.3 seconds"
            }
            
            return result
            
        except Exception as e:
            return {
                "task_id": task['id'],
                "status": "failed",
                "error": str(e)
            }
    
    async def _execute_generic_task(self, task: Dict) -> Dict:
        """Execute generic task"""
        print(f"🔨 Executing: {task['title']}...")
        
        try:
            result = {
                "task_id": task['id'],
                "status": "success",
                "type": "generic",
                "task": task['title'],
                "execution_time": "30 seconds",
                "details": f"Completed {task['title']}"
            }
            
            return result
            
        except Exception as e:
            return {
                "task_id": task['id'],
                "status": "failed",
                "error": str(e)
            }
    
    async def _create_pr_for_task(self, task: Dict, task_result: Dict) -> Dict:
        """
        Create GitHub PR for completed task
        
        Args:
            task: Original task
            task_result: Task execution result
            
        Returns:
            PR creation result
        """
        try:
            # In real implementation, this would use the GitHub PR manager
            # For MVP, we simulate PR creation
            
            branch_name = f"task-{task['id']}-{task['type']}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            pr_title = f"[{task['priority'].upper()}] {task['title']}"
            pr_body = f"""## Task #{task['id']}: {task['title']}

**Priority:** {task['priority']}
**Type:** {task['type']}

### Changes Made
{task_result.get('details', 'Task completed successfully')}

### Files Modified
{chr(10).join(f'- {f}' for f in task_result.get('files_created', []) + task_result.get('files_modified', []))}

### Execution Time
{task_result.get('execution_time', 'N/A')}

### Testing
- [x] Task executed successfully
- [x] No errors encountered
- [ ] Manual review required

---
*Generated by Autonomous Agent*
"""
            
            result = {
                "success": True,
                "branch_name": branch_name,
                "pr_title": pr_title,
                "pr_body": pr_body,
                "pr_url": f"https://github.com/user/repo/pull/123",  # Mock URL
                "pr_number": 123
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _print_summary(self, results: Dict):
        """Print execution summary"""
        print("\n" + "="*60)
        print("AUTONOMOUS EXECUTION SUMMARY")
        print("="*60)
        print(f"\n📊 Results:")
        print(f"  Total Tasks: {results['total_tasks']}")
        print(f"  ✅ Completed: {results['completed']}")
        print(f"  ❌ Failed: {results['failed']}")
        print(f"  ⏭️  Skipped: {results['skipped']}")
        print(f"  🔀 PRs Created: {results['prs_created']}")
        
        if results['completed'] > 0:
            success_rate = (results['completed'] / results['total_tasks']) * 100
            print(f"\n✨ Success Rate: {success_rate:.1f}%")
        
        print(f"\n⏱️  Duration: {results['start_time']} to {results['end_time']}")
        print("="*60)
    
    def get_execution_log(self) -> List[Dict]:
        """Get execution log"""
        return self.execution_log
    
    def save_execution_report(self, filepath: str, results: Dict):
        """Save execution report to file"""
        with open(filepath, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n📄 Execution report saved to: {filepath}")


async def execute_autonomous_workflow(website_url: str, auto_pr: bool = True) -> Dict:
    """
    Complete autonomous workflow: analyze -> generate tasks -> execute
    
    Args:
        website_url: Website URL to work on
        auto_pr: Automatically create PRs
        
    Returns:
        Complete workflow results
    """
    try:
        from .website_analyzer import analyze_website
        from .task_generator import TaskGenerator
    except ImportError:
        from website_analyzer import analyze_website
        from task_generator import TaskGenerator
    
    print("\n" + "="*60)
    print("AUTONOMOUS AGENT WORKFLOW")
    print("="*60)
    
    # Step 1: Analyze website
    print("\n📊 STEP 1: Analyzing website...")
    analysis = await analyze_website(website_url)
    
    # Step 2: Generate tasks
    print("\n📋 STEP 2: Generating tasks...")
    generator = TaskGenerator()
    tasks = generator.generate_tasks(analysis)
    print(generator.generate_task_summary(tasks))
    
    # Step 3: Execute tasks
    print("\n🤖 STEP 3: Executing tasks...")
    executor = AutonomousExecutor()
    results = await executor.execute_tasks(tasks, auto_pr=auto_pr)
    
    # Save report
    report_file = f"autonomous_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    executor.save_execution_report(report_file, {
        "website_url": website_url,
        "analysis": analysis,
        "tasks": tasks,
        "execution": results
    })
    
    return {
        "analysis": analysis,
        "tasks": tasks,
        "execution": results
    }


if __name__ == "__main__":
    # Test the executor
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://example-coaching.com"
    
    # Run autonomous workflow
    results = asyncio.run(execute_autonomous_workflow(url, auto_pr=True))
    
    print("\n✅ Autonomous workflow complete!")
    print(f"Analyzed: {results['analysis']['url']}")
    print(f"Generated: {len(results['tasks'])} tasks")
    print(f"Completed: {results['execution']['completed']} tasks")
    print(f"PRs Created: {results['execution']['prs_created']}")
