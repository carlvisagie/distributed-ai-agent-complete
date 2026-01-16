"""
AI File Surgeon - Cursor's Approach to File Editing

Uses a SECOND AI model to apply edits with high accuracy.
The first AI generates INTENT, the second AI does the actual file surgery.

Based on research: https://fabianhertwig.com/blog/coding-assistants-file-edits/
Cursor achieves 95%+ success rate with this approach.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import anthropic

logger = logging.getLogger(__name__)


class AIFileSurgeon:
    """
    AI-assisted file application using Cursor's approach
    
    Key Principles:
    1. First AI generates INTENT (what to change and why)
    2. Second AI (this class) applies the change to actual file
    3. Second AI sees CURRENT file state (no stale context)
    4. Uses natural language instructions, not rigid JSON
    5. Validates result before committing
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def apply_edit(self, 
                   file_path: Path, 
                   intent: str,
                   current_content: str) -> Dict[str, Any]:
        """
        Apply an edit to a file using AI-assisted surgery
        
        Args:
            file_path: Path to file
            intent: Natural language description of what to change
            current_content: Current file content
        
        Returns:
            {
                "success": bool,
                "new_content": str (if success),
                "error": str (if failure)
            }
        """
        logger.info(f"AI Surgeon applying edit to {file_path}")
        logger.info(f"Intent: {intent[:100]}...")
        
        # Build prompt for surgical AI
        prompt = f"""You are a precise code surgeon. Apply the requested change to the file.

FILE: {file_path}

CURRENT CONTENT:
```
{current_content}
```

REQUESTED CHANGE:
{intent}

OUTPUT THE COMPLETE MODIFIED FILE CONTENT.

Rules:
1. Output ONLY the file content (no explanations, no markdown fences)
2. Preserve all formatting, indentation, and style
3. Make ONLY the requested change
4. If the change is ambiguous or impossible, output "ERROR: " followed by explanation

Begin output now:"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0,  # Deterministic for code surgery
                messages=[{"role": "user", "content": prompt}]
            )
            
            output = response.content[0].text.strip()
            
            # Check for error
            if output.startswith("ERROR:"):
                return {
                    "success": False,
                    "error": output[7:].strip()
                }
            
            # Validate output is reasonable
            if len(output) < len(current_content) * 0.5:
                return {
                    "success": False,
                    "error": "Output too short - likely truncated or malformed"
                }
            
            # Success
            return {
                "success": True,
                "new_content": output
            }
        
        except Exception as e:
            logger.error(f"AI Surgeon failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def apply_multiple_edits(self,
                            file_path: Path,
                            intents: List[str],
                            current_content: str) -> Dict[str, Any]:
        """
        Apply multiple edits to a file sequentially
        
        Each edit is applied to the result of the previous edit.
        If any edit fails, returns the last successful state.
        
        Args:
            file_path: Path to file
            intents: List of natural language edit descriptions
            current_content: Current file content
        
        Returns:
            {
                "success": bool,
                "new_content": str,
                "edits_applied": int,
                "errors": List[str]
            }
        """
        content = current_content
        errors = []
        
        for i, intent in enumerate(intents, 1):
            result = self.apply_edit(file_path, intent, content)
            
            if result["success"]:
                content = result["new_content"]
                logger.info(f"✓ Edit {i}/{len(intents)} applied")
            else:
                errors.append(f"Edit {i}: {result['error']}")
                logger.warning(f"✗ Edit {i}/{len(intents)} failed: {result['error']}")
                break
        
        return {
            "success": len(errors) == 0,
            "new_content": content,
            "edits_applied": len(intents) - len(errors),
            "errors": errors
        }
    
    def create_file(self,
                   file_path: Path,
                   intent: str) -> Dict[str, Any]:
        """
        Create a new file using AI-assisted generation
        
        Args:
            file_path: Path to new file
            intent: Natural language description of what to create
        
        Returns:
            {
                "success": bool,
                "content": str (if success),
                "error": str (if failure)
            }
        """
        logger.info(f"AI Surgeon creating {file_path}")
        
        prompt = f"""You are a code generator. Create the requested file.

FILE: {file_path}

REQUIREMENTS:
{intent}

OUTPUT THE COMPLETE FILE CONTENT.

Rules:
1. Output ONLY the file content (no explanations, no markdown fences)
2. Follow best practices for the file type
3. Include proper imports, types, and documentation
4. Make it production-ready

Begin output now:"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text.strip()
            
            if len(content) < 10:
                return {
                    "success": False,
                    "error": "Generated content too short"
                }
            
            return {
                "success": True,
                "content": content
            }
        
        except Exception as e:
            logger.error(f"AI Surgeon file creation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


class ShadowWorkspace:
    """
    Shadow workspace for safe edit application (Cursor's approach)
    
    Apply edits to a copy first, validate, then commit to real files.
    """
    
    def __init__(self, workspace_path: Path):
        self.workspace = workspace_path
        self.shadow_files: Dict[str, str] = {}  # path -> content
    
    def load_file(self, rel_path: str) -> str:
        """Load file into shadow workspace"""
        if rel_path in self.shadow_files:
            return self.shadow_files[rel_path]
        
        file_path = self.workspace / rel_path
        if file_path.exists():
            with open(file_path, 'r') as f:
                content = f.read()
            self.shadow_files[rel_path] = content
            return content
        else:
            return ""
    
    def update_file(self, rel_path: str, content: str):
        """Update file in shadow workspace"""
        self.shadow_files[rel_path] = content
    
    def commit(self, rel_path: str) -> bool:
        """Commit shadow file to real filesystem"""
        if rel_path not in self.shadow_files:
            return False
        
        file_path = self.workspace / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(file_path, 'w') as f:
                f.write(self.shadow_files[rel_path])
            return True
        except Exception as e:
            logger.error(f"Failed to commit {rel_path}: {e}")
            return False
    
    def commit_all(self) -> Dict[str, bool]:
        """Commit all shadow files"""
        results = {}
        for rel_path in self.shadow_files:
            results[rel_path] = self.commit(rel_path)
        return results
    
    def rollback(self, rel_path: str):
        """Rollback shadow file to original state"""
        if rel_path in self.shadow_files:
            del self.shadow_files[rel_path]
    
    def rollback_all(self):
        """Rollback all shadow files"""
        self.shadow_files.clear()
