"""
Proper File Editor for Autonomous Agent
Reads existing files before modifying them to avoid breaking code
"""
import os
import re
from typing import Dict, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class FileEditor:
    """
    Smart file editor that:
    1. Reads existing file content
    2. Makes targeted modifications
    3. Preserves existing code structure
    """
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Read file content, return None if doesn't exist"""
        full_path = os.path.join(self.workspace_path, file_path)
        
        if not os.path.exists(full_path):
            return None
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return None
    
    def write_file(self, file_path: str, content: str) -> bool:
        """Write content to file, creating directories if needed"""
        full_path = os.path.join(self.workspace_path, file_path)
        
        # Create directory if needed
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        try:
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✅ Wrote file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write {file_path}: {e}")
            return False
    
    def file_exists(self, file_path: str) -> bool:
        """Check if file exists"""
        full_path = os.path.join(self.workspace_path, file_path)
        return os.path.exists(full_path)
    
    def insert_after_pattern(
        self,
        file_path: str,
        pattern: str,
        content_to_insert: str
    ) -> bool:
        """
        Insert content after first occurrence of pattern
        
        Example:
            insert_after_pattern(
                'server/routers.ts',
                'export const appRouter = router({',
                '  myNewProcedure: publicProcedure.query(() => {...}),'
            )
        """
        current_content = self.read_file(file_path)
        
        if current_content is None:
            logger.error(f"Cannot insert - file doesn't exist: {file_path}")
            return False
        
        # Find pattern
        if pattern not in current_content:
            logger.error(f"Pattern not found in {file_path}: {pattern}")
            return False
        
        # Insert after pattern
        parts = current_content.split(pattern, 1)
        new_content = parts[0] + pattern + '\n' + content_to_insert + parts[1]
        
        return self.write_file(file_path, new_content)
    
    def insert_before_pattern(
        self,
        file_path: str,
        pattern: str,
        content_to_insert: str
    ) -> bool:
        """Insert content before first occurrence of pattern"""
        current_content = self.read_file(file_path)
        
        if current_content is None:
            logger.error(f"Cannot insert - file doesn't exist: {file_path}")
            return False
        
        if pattern not in current_content:
            logger.error(f"Pattern not found in {file_path}: {pattern}")
            return False
        
        parts = current_content.split(pattern, 1)
        new_content = parts[0] + content_to_insert + '\n' + pattern + parts[1]
        
        return self.write_file(file_path, new_content)
    
    def replace_pattern(
        self,
        file_path: str,
        old_pattern: str,
        new_content: str
    ) -> bool:
        """Replace first occurrence of pattern with new content"""
        current_content = self.read_file(file_path)
        
        if current_content is None:
            logger.error(f"Cannot replace - file doesn't exist: {file_path}")
            return False
        
        if old_pattern not in current_content:
            logger.error(f"Pattern not found in {file_path}: {old_pattern}")
            return False
        
        new_file_content = current_content.replace(old_pattern, new_content, 1)
        
        return self.write_file(file_path, new_file_content)
    
    def append_to_file(self, file_path: str, content: str) -> bool:
        """Append content to end of file"""
        current_content = self.read_file(file_path)
        
        if current_content is None:
            # File doesn't exist, create it
            return self.write_file(file_path, content)
        
        new_content = current_content + '\n' + content
        return self.write_file(file_path, new_content)
    
    def add_import(self, file_path: str, import_statement: str) -> bool:
        """
        Add import statement to file (smart positioning)
        
        Example:
            add_import('server/routers.ts', "import { z } from 'zod';")
        """
        current_content = self.read_file(file_path)
        
        if current_content is None:
            logger.error(f"Cannot add import - file doesn't exist: {file_path}")
            return False
        
        # Check if import already exists
        if import_statement in current_content:
            logger.info(f"Import already exists in {file_path}")
            return True
        
        lines = current_content.split('\n')
        
        # Find last import statement
        last_import_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('import '):
                last_import_index = i
        
        if last_import_index >= 0:
            # Insert after last import
            lines.insert(last_import_index + 1, import_statement)
        else:
            # No imports found, add at top
            lines.insert(0, import_statement)
        
        new_content = '\n'.join(lines)
        return self.write_file(file_path, new_content)
    
    def get_file_info(self, file_path: str) -> Dict:
        """
        Get information about a file for LLM context
        
        Returns:
            {
                'exists': bool,
                'line_count': int,
                'imports': List[str],
                'exports': List[str],
                'first_50_lines': str
            }
        """
        content = self.read_file(file_path)
        
        if content is None:
            return {
                'exists': False,
                'line_count': 0,
                'imports': [],
                'exports': [],
                'first_50_lines': ''
            }
        
        lines = content.split('\n')
        
        # Extract imports
        imports = [line for line in lines if line.strip().startswith('import ')]
        
        # Extract exports (simple detection)
        exports = [line for line in lines if 'export' in line]
        
        return {
            'exists': True,
            'line_count': len(lines),
            'imports': imports[:10],  # First 10 imports
            'exports': exports[:10],  # First 10 exports
            'first_50_lines': '\n'.join(lines[:50])
        }
    
    def parse_llm_file_operations(self, llm_response: str) -> List[Dict]:
        """
        Parse LLM response for file operations
        
        Supports formats:
        - CREATE server/utils.ts
        - MODIFY server/routers.ts INSERT_AFTER "export const appRouter"
        - MODIFY server/routers.ts REPLACE "old code" WITH "new code"
        """
        operations = []
        
        # Pattern 1: CREATE file
        create_pattern = r'CREATE\s+([^\s]+)\s*\n```[\w]*\n(.*?)```'
        for match in re.finditer(create_pattern, llm_response, re.DOTALL):
            operations.append({
                'action': 'create',
                'file': match.group(1),
                'content': match.group(2).strip()
            })
        
        # Pattern 2: Standard code blocks (backward compatibility)
        code_block_pattern = r'```(\w+)\s+([^\n]+)\n(.*?)```'
        for match in re.finditer(code_block_pattern, llm_response, re.DOTALL):
            file_path = match.group(2).strip()
            content = match.group(3).strip()
            
            # Check if file exists to determine create vs modify
            if self.file_exists(file_path):
                operations.append({
                    'action': 'overwrite',
                    'file': file_path,
                    'content': content
                })
            else:
                operations.append({
                    'action': 'create',
                    'file': file_path,
                    'content': content
                })
        
        return operations
    
    def execute_operations(self, operations: List[Dict]) -> Dict:
        """
        Execute list of file operations
        
        Returns:
            {
                'success': bool,
                'files_written': List[str],
                'errors': List[str]
            }
        """
        files_written = []
        errors = []
        
        for op in operations:
            action = op.get('action')
            file_path = op.get('file')
            
            try:
                if action == 'create':
                    if self.write_file(file_path, op['content']):
                        files_written.append(file_path)
                    else:
                        errors.append(f"Failed to create {file_path}")
                
                elif action == 'overwrite':
                    if self.write_file(file_path, op['content']):
                        files_written.append(file_path)
                    else:
                        errors.append(f"Failed to overwrite {file_path}")
                
                elif action == 'append':
                    if self.append_to_file(file_path, op['content']):
                        files_written.append(file_path)
                    else:
                        errors.append(f"Failed to append to {file_path}")
                
                else:
                    errors.append(f"Unknown action: {action}")
            
            except Exception as e:
                errors.append(f"Error processing {file_path}: {str(e)}")
        
        return {
            'success': len(errors) == 0,
            'files_written': files_written,
            'errors': errors
        }
