"""
Code Executor - Actually writes code to files and executes commands
Parses LLM responses and performs real file operations
"""
import os
import re
import subprocess
from typing import Dict, Any, List, Tuple
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CodeExecutor:
    """
    Executes code from LLM responses
    - Parses code blocks
    - Writes files
    - Executes commands
    - Commits changes
    """
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
    
    def parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response for code blocks and commands
        
        Returns:
            {
                'files': [{'path': '...', 'content': '...', 'language': '...'}],
                'commands': ['command1', 'command2'],
                'summary': 'What was done'
            }
        """
        files = []
        commands = []
        
        # Extract code blocks with file paths
        # Pattern: ```language filename
        # code
        # ```
        code_block_pattern = r'```(\w+)\s+([^\n]+)\n(.*?)```'
        matches = re.findall(code_block_pattern, response, re.DOTALL)
        
        for language, filepath, content in matches:
            # Clean up filepath
            filepath = filepath.strip()
            
            # Skip if it's not a real file path
            if not ('/' in filepath or '.' in filepath):
                continue
            
            files.append({
                'path': filepath,
                'content': content.strip(),
                'language': language
            })
        
        # Extract shell commands
        # Pattern: $ command or `command`
        command_pattern = r'(?:^|\n)\$\s+([^\n]+)'
        command_matches = re.findall(command_pattern, response)
        commands.extend(command_matches)
        
        # Also look for explicit command blocks
        command_block_pattern = r'```(?:bash|shell|sh)\n(.*?)```'
        command_blocks = re.findall(command_block_pattern, response, re.DOTALL)
        for block in command_blocks:
            commands.extend([line.strip() for line in block.split('\n') if line.strip() and not line.strip().startswith('#')])
        
        # Extract summary (first paragraph or heading)
        summary_match = re.search(r'^#+\s+(.+)$|^(.+?)(?:\n\n|\n#)', response, re.MULTILINE)
        summary = summary_match.group(1) or summary_match.group(2) if summary_match else "Code changes applied"
        summary = summary.strip()[:200]  # Limit to 200 chars
        
        return {
            'files': files,
            'commands': commands,
            'summary': summary
        }
    
    def write_files(self, files: List[Dict[str, str]]) -> List[str]:
        """
        Write files to disk
        
        Args:
            files: List of {path, content, language}
        
        Returns:
            List of written file paths
        """
        written = []
        
        for file_info in files:
            filepath = file_info['path']
            content = file_info['content']
            
            # Make path absolute if relative
            if not filepath.startswith('/'):
                filepath = os.path.join(self.workspace_path, filepath)
            
            try:
                # Create directory if needed
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Write file
                with open(filepath, 'w') as f:
                    f.write(content)
                
                written.append(filepath)
                logger.info(f"✅ Wrote file: {filepath}")
            
            except Exception as e:
                logger.error(f"❌ Failed to write {filepath}: {e}")
        
        return written
    
    def execute_commands(self, commands: List[str]) -> List[Dict[str, Any]]:
        """
        Execute shell commands
        
        Args:
            commands: List of shell commands
        
        Returns:
            List of execution results
        """
        results = []
        
        for cmd in commands:
            # Skip dangerous commands
            if any(danger in cmd.lower() for danger in ['rm -rf /', 'dd if=', 'mkfs', ':(){:|:&};:']):
                logger.warning(f"⚠️  Skipped dangerous command: {cmd}")
                continue
            
            try:
                logger.info(f"🔧 Executing: {cmd}")
                
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=self.workspace_path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                results.append({
                    'command': cmd,
                    'returncode': result.returncode,
                    'stdout': result.stdout[:500],  # Limit output
                    'stderr': result.stderr[:500],
                    'success': result.returncode == 0
                })
                
                if result.returncode == 0:
                    logger.info(f"✅ Command succeeded")
                else:
                    logger.warning(f"⚠️  Command failed with code {result.returncode}")
            
            except subprocess.TimeoutExpired:
                logger.error(f"❌ Command timeout: {cmd}")
                results.append({
                    'command': cmd,
                    'error': 'timeout',
                    'success': False
                })
            
            except Exception as e:
                logger.error(f"❌ Command failed: {cmd} - {e}")
                results.append({
                    'command': cmd,
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    def commit_changes(self, message: str) -> bool:
        """
        Commit changes to git
        
        Args:
            message: Commit message
        
        Returns:
            True if successful
        """
        try:
            # Add all changes
            subprocess.run(
                ['git', 'add', '-A'],
                cwd=self.workspace_path,
                check=True,
                capture_output=True
            )
            
            # Check if there are changes to commit
            status = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True
            )
            
            if not status.stdout.strip():
                logger.info("No changes to commit")
                return True
            
            # Commit
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=self.workspace_path,
                check=True,
                capture_output=True
            )
            
            logger.info(f"✅ Committed: {message}")
            return True
        
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Git commit failed: {e}")
            return False
    
    def execute_task(self, llm_response: str, task_title: str) -> Dict[str, Any]:
        """
        Execute a complete task from LLM response
        
        Args:
            llm_response: Raw LLM response text
            task_title: Task title for commit message
        
        Returns:
            Execution result
        """
        start_time = datetime.utcnow()
        
        # Parse response
        parsed = self.parse_llm_response(llm_response)
        
        # Write files
        files_written = self.write_files(parsed['files'])
        
        # Execute commands
        command_results = self.execute_commands(parsed['commands'])
        
        # Commit changes
        commit_message = f"Task: {task_title}\n\n{parsed['summary']}"
        committed = self.commit_changes(commit_message)
        
        execution_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            'success': len(files_written) > 0 or any(r['success'] for r in command_results),
            'files_written': files_written,
            'files_count': len(files_written),
            'commands_executed': len(command_results),
            'commands_succeeded': sum(1 for r in command_results if r.get('success')),
            'committed': committed,
            'execution_time': f"{execution_time:.1f}s",
            'summary': parsed['summary']
        }
