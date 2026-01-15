"""
Real Code Execution Module
Integrates OpenHands SDK for actual code generation and execution
"""
import os
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from .code_executor import CodeExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealExecutor:
    """
    Real code executor using OpenHands SDK
    Replaces mock execution with actual code generation and file modification
    """
    
    def __init__(
        self,
        workspace_path: str,
        llm_api_key: Optional[str] = None,
        llm_model: Optional[str] = None,
        llm_base_url: Optional[str] = None
    ):
        """
        Initialize real executor
        
        Args:
            workspace_path: Path to project workspace
            llm_api_key: LLM API key (defaults to env var)
            llm_model: LLM model name (defaults to env var)
            llm_base_url: LLM base URL (defaults to env var)
        """
        self.workspace_path = workspace_path
        self.llm_api_key = llm_api_key or os.getenv("LLM_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.llm_model = llm_model or os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")
        self.llm_base_url = llm_base_url or os.getenv("LLM_BASE_URL")
        
        # Initialize code executor for actual file writing
        self.code_executor = CodeExecutor(workspace_path)
        
        # Check if OpenHands is available
        self.openhands_available = self._check_openhands()
        
        if not self.openhands_available:
            logger.warning("OpenHands SDK not available, will use fallback execution")
    
    def _check_openhands(self) -> bool:
        """Check if OpenHands SDK is available"""
        try:
            import openhands
            return True
        except ImportError:
            return False
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with real code generation
        
        Args:
            task: Task dictionary with id, type, title, description, prompt
        
        Returns:
            Execution result dictionary
        """
        task_id = task.get('task_id', task.get('id', 'unknown'))
        task_type = task.get('task_type', task.get('type', 'generic'))
        title = task.get('title', 'Unknown task')
        prompt = task.get('prompt', task.get('description', ''))
        
        logger.info(f"Executing task {task_id}: {title}")
        
        try:
            if self.openhands_available and self.llm_api_key:
                # Use OpenHands for real execution
                result = await self._execute_with_openhands(task_id, prompt)
            else:
                # Fallback to direct LLM call
                result = await self._execute_with_direct_llm(task_id, prompt)
            
            return {
                'task_id': task_id,
                'status': 'success',
                'type': task_type,
                'title': title,
                'result': result,
                'execution_time': result.get('execution_time', 'unknown'),
                'files_modified': result.get('files_modified', []),
                'details': result.get('details', f"Completed {title}")
            }
        
        except Exception as e:
            logger.error(f"Task {task_id} failed: {str(e)}")
            return {
                'task_id': task_id,
                'status': 'failed',
                'type': task_type,
                'title': title,
                'error': str(e)
            }
    
    async def _execute_with_openhands(self, task_id: str, prompt: str) -> Dict[str, Any]:
        """
        Execute task using OpenHands SDK
        
        Args:
            task_id: Task identifier
            prompt: Task prompt/instructions
        
        Returns:
            Execution result
        """
        try:
            from openhands.sdk import LLM, Agent, Conversation, Tool
            from openhands.tools.terminal import TerminalTool
            from openhands.tools.file_editor import FileEditorTool
            from openhands.tools.task_tracker import TaskTrackerTool
            
            start_time = datetime.utcnow()
            
            # Create LLM instance
            llm = LLM(
                model=self.llm_model,
                api_key=self.llm_api_key,
                base_url=self.llm_base_url
            )
            
            # Create agent with tools
            agent = Agent(
                llm=llm,
                tools=[
                    Tool(name=TerminalTool.name),
                    Tool(name=FileEditorTool.name),
                    Tool(name=TaskTrackerTool.name)
                ]
            )
            
            # Create conversation
            conversation = Conversation(
                agent=agent,
                workspace=self.workspace_path
            )
            
            # Send task prompt
            conversation.send_message(prompt)
            
            # Run agent
            conversation.run()
            
            # Get results
            messages = conversation.get_messages()
            artifacts = conversation.get_artifacts()
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Extract files modified
            files_modified = []
            for artifact in artifacts:
                if artifact.get('type') == 'file':
                    files_modified.append(artifact.get('path', 'unknown'))
            
            return {
                'mode': 'openhands',
                'execution_time': f"{execution_time:.1f} seconds",
                'files_modified': files_modified,
                'messages': len(messages),
                'artifacts': len(artifacts),
                'details': f"Task completed via OpenHands SDK"
            }
        
        except Exception as e:
            logger.error(f"OpenHands execution failed: {str(e)}")
            raise
    
    async def _execute_with_direct_llm(self, task_id: str, prompt: str) -> Dict[str, Any]:
        """
        Execute task using direct LLM API call (fallback)
        
        Args:
            task_id: Task identifier
            prompt: Task prompt/instructions
        
        Returns:
            Execution result
        """
        try:
            import anthropic
            
            start_time = datetime.utcnow()
            
            # Create Anthropic client
            client = anthropic.Anthropic(api_key=self.llm_api_key)
            
            # Enhanced prompt with execution context
            enhanced_prompt = f"""You are an autonomous coding agent working on a project.

WORKSPACE: {self.workspace_path}

TASK:
{prompt}

INSTRUCTIONS:
1. Analyze the task requirements
2. Generate the necessary code
3. Provide clear implementation steps
4. List all files that need to be created or modified
5. Include complete, production-ready code

Respond with a structured plan and implementation."""
            
            # Call Claude
            response = client.messages.create(
                model=self.llm_model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": enhanced_prompt
                }]
            )
            
            # Extract response
            content = response.content[0].text if response.content else ""
            
            # 🔥 ACTUALLY EXECUTE THE CODE!
            logger.info("📝 Parsing LLM response and executing code...")
            exec_result = self.code_executor.execute_task(content, task_id)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'mode': 'direct_llm',
                'execution_time': f"{execution_time:.1f} seconds",
                'files_modified': exec_result['files_written'],
                'files_count': exec_result['files_count'],
                'commands_executed': exec_result['commands_executed'],
                'commands_succeeded': exec_result['commands_succeeded'],
                'committed': exec_result['committed'],
                'success': exec_result['success'],
                'details': exec_result['summary'],
                'llm_response_length': len(content)
            }
        
        except Exception as e:
            logger.error(f"Direct LLM execution failed: {str(e)}")
            raise
    
    async def execute_batch(self, tasks: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """
        Execute multiple tasks
        
        Args:
            tasks: List of task dictionaries
        
        Returns:
            List of execution results
        """
        results = []
        
        for task in tasks:
            result = await self.execute_task(task)
            results.append(result)
            
            # Small delay between tasks
            await asyncio.sleep(1)
        
        return results
    
    def get_status(self) -> Dict[str, Any]:
        """Get executor status"""
        return {
            'workspace_path': self.workspace_path,
            'openhands_available': self.openhands_available,
            'llm_configured': bool(self.llm_api_key),
            'llm_model': self.llm_model,
            'execution_mode': 'openhands' if self.openhands_available else 'direct_llm'
        }


# Example usage
async def test_real_executor():
    """Test the real executor"""
    
    # Create executor
    executor = RealExecutor(
        workspace_path="/home/ubuntu/test-workspace"
    )
    
    # Check status
    status = executor.get_status()
    print(f"Executor Status: {status}")
    
    # Test task
    test_task = {
        'task_id': 'test_001',
        'task_type': 'create_page',
        'title': 'Create About Page',
        'description': 'Create a professional about page',
        'prompt': """Create an about page (about.html) with the following:
- Professional header with company name
- Mission statement section
- Team section with 3 team members
- Contact information
- Modern, clean design with CSS
- Responsive layout

Generate complete HTML and CSS code."""
    }
    
    # Execute
    result = await executor.execute_task(test_task)
    
    print(f"\nExecution Result:")
    print(f"Status: {result['status']}")
    print(f"Files Modified: {result.get('files_modified', [])}")
    print(f"Execution Time: {result.get('execution_time', 'unknown')}")
    print(f"Details: {result.get('details', 'N/A')}")


if __name__ == "__main__":
    asyncio.run(test_real_executor())
