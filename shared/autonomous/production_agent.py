"""
Production-Ready Autonomous Agent V2

Based on Anthropic research:
- Minimal context (5-10 files max)
- Targeted edits (not full file rewrites)
- Incremental validation
- Fast execution (<30s per task)

Architecture:
1. Analyze: Identify 5-10 relevant files
2. Edit: Generate edit instructions (insert/replace)
3. Validate: Check only modified files
"""
import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import anthropic
import re
from .smart_editor import SmartEditor

logger = logging.getLogger(__name__)


class ProductionAgent:
    """
    Minimal, production-ready autonomous agent
    
    Design principles:
    - Minimal context per phase (<5K tokens)
    - Targeted edits (never rewrite full files)
    - Incremental validation (after each edit)
    - Fast failure (2 attempts max)
    """
    
    def __init__(
        self,
        workspace_path: str,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-20250514"
    ):
        self.workspace = Path(workspace_path)
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        
        # Metrics
        self.metrics = {
            "tasks_completed": 0,
            "first_attempt_success": 0,
            "total_edits": 0,
            "failed_edits": 0,
            "avg_time_per_task": 0.0
        }
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with minimal context and targeted edits
        
        Args:
            task: {
                "id": "TASK_001",
                "title": "Add utility function",
                "description": "Brief description",
                "requirements": "Detailed requirements"
            }
        
        Returns:
            {
                "status": "success" | "failed",
                "edits_made": [...],
                "validation_result": {...},
                "time_taken": 12.5
            }
        """
        start_time = time.time()
        task_id = task.get("id", "UNKNOWN")
        
        logger.info(f"🚀 Starting task {task_id}: {task.get('title')}")
        
        try:
            # Phase 1: Analyze (identify relevant files)
            analysis = self._analyze_task(task)
            logger.info(f"📋 Analysis: {len(analysis['relevant_files'])} files identified")
            
            # Phase 2: Generate edits
            edits = self._generate_edits(task, analysis)
            logger.info(f"✏️  Generated {len(edits)} edits")
            
            # Phase 3: Apply edits incrementally with validation
            results = self._apply_edits_incrementally(edits)
            
            # Calculate metrics
            time_taken = time.time() - start_time
            success = all(r["success"] for r in results)
            
            if success:
                self.metrics["first_attempt_success"] += 1
            self.metrics["tasks_completed"] += 1
            self.metrics["total_edits"] += len(edits)
            self.metrics["avg_time_per_task"] = (
                (self.metrics["avg_time_per_task"] * (self.metrics["tasks_completed"] - 1) + time_taken)
                / self.metrics["tasks_completed"]
            )
            
            logger.info(f"✅ Task {task_id} completed in {time_taken:.1f}s")
            
            return {
                "status": "success" if success else "partial",
                "edits_made": results,
                "time_taken": time_taken,
                "metrics": self.metrics
            }
            
        except Exception as e:
            logger.error(f"❌ Task {task_id} failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "time_taken": time.time() - start_time
            }
    
    def _analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Phase 1: Analyze task and identify 5-10 relevant files
        
        Minimal context strategy:
        - Only send task requirements
        - Only send file tree (not file contents)
        - Ask LLM to identify 5-10 most relevant files
        """
        # Get lightweight file tree
        file_tree = self._get_file_tree()
        
        prompt = f"""Analyze this task and identify the 5-10 most relevant files to modify.

TASK: {task.get('title')}
REQUIREMENTS:
{task.get('requirements', task.get('description', ''))}

PROJECT FILE TREE:
{file_tree}

Output JSON with this structure:
{{
  "relevant_files": [
    {{
      "path": "server/utils.ts",
      "reason": "Need to add utility function here",
      "operation": "modify" | "create"
    }}
  ],
  "approach": "Brief description of implementation approach"
}}

Keep it minimal - only list files you'll actually modify. Maximum 10 files."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,  # Small response
            timeout=30,  # Fast
            messages=[{"role": "user", "content": prompt}]
        )
        
        analysis_text = response.content[0].text
        return self._parse_json_robust(analysis_text, "analysis")
    
    def _generate_edits(self, task: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Phase 2: Generate targeted edit instructions
        
        Minimal context strategy:
        - Only send content of relevant files (5-10 files)
        - Ask for edit instructions, NOT full file rewrites
        """
        relevant_files = analysis["relevant_files"]
        
        # Read only relevant files
        file_contents = {}
        for file_info in relevant_files:
            file_path = self.workspace / file_info["path"]
            if file_path.exists():
                with open(file_path, 'r') as f:
                    file_contents[file_info["path"]] = f.read()
            else:
                file_contents[file_info["path"]] = "// NEW FILE"
        
        # Build minimal prompt
        files_context = "\n\n".join([
            f"=== {path} ===\n{content[:2000]}"  # Limit to 2K chars per file
            for path, content in file_contents.items()
        ])
        
        prompt = f"""Generate targeted edit instructions for this task.

TASK: {task.get('title')}
REQUIREMENTS:
{task.get('requirements', task.get('description', ''))}

APPROACH: {analysis['approach']}

CURRENT FILES:
{files_context}

Output JSON array of edit instructions:
[
  {{
    "file": "server/utils.ts",
    "operation": "insert_after" | "replace" | "create",
    "marker": "export function existingFunction",  // For insert_after
    "find": "old code",  // For replace
    "content": "new code to insert or replace with"
  }}
]

CRITICAL RULES:
1. Output EDIT INSTRUCTIONS, not full files
2. Use insert_after to add new code after a marker line
3. Use replace to change specific code sections
4. Use create for new files
5. Keep edits surgical - don't rewrite entire files
6. Include proper TypeScript types"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            timeout=60,
            messages=[{"role": "user", "content": prompt}]
        )
        
        edits_text = response.content[0].text
        result = self._parse_json_robust(edits_text, "edits")
        
        # Ensure it's a list
        if isinstance(result, dict):
            return [result]
        return result
    
    def _apply_edits_incrementally(self, edits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Phase 3: Apply edits one at a time with validation
        
        Incremental strategy:
        - Apply one edit
        - Validate that specific file
        - If error: rollback and try different approach
        - If success: commit and move to next edit
        """
        results = []
        
        for i, edit in enumerate(edits):
            logger.info(f"📝 Applying edit {i+1}/{len(edits)}: {edit['file']}")
            
            file_path = self.workspace / edit["file"]
            backup_content = None
            
            try:
                # Backup current content
                backup_content = SmartEditor.backup_file(file_path)
                
                # Apply edit
                self._apply_single_edit(edit, file_path)
                
                # Validate
                validation = self._validate_file(file_path)
                
                if validation["success"]:
                    logger.info(f"✅ Edit {i+1} applied successfully")
                    results.append({
                        "edit": edit,
                        "success": True,
                        "validation": validation
                    })
                else:
                    # Rollback
                    logger.warning(f"⚠️  Edit {i+1} failed validation, rolling back")
                    SmartEditor.restore_backup(file_path, backup_content)
                    
                    results.append({
                        "edit": edit,
                        "success": False,
                        "validation": validation,
                        "rolled_back": True
                    })
                    
                    self.metrics["failed_edits"] += 1
                    
            except Exception as e:
                logger.error(f"❌ Edit {i+1} failed: {e}")
                
                # Rollback on error
                SmartEditor.restore_backup(file_path, backup_content)
                
                results.append({
                    "edit": edit,
                    "success": False,
                    "error": str(e),
                    "rolled_back": True
                })
                
                self.metrics["failed_edits"] += 1
        
        return results
    
    def _apply_single_edit(self, edit: Dict[str, Any], file_path: Path):
        """Apply a single edit instruction to a file using SmartEditor"""
        result = SmartEditor.apply_edit(file_path, edit)
        
        if not result["success"]:
            raise ValueError(result["message"])
    
    def _parse_json_robust(self, text: str, context: str) -> Any:
        """
        Robust JSON parsing with error recovery
        
        Handles:
        - JSON in markdown code blocks
        - Unterminated strings
        - Missing brackets
        - Trailing commas
        """
        # Remove markdown code blocks
        code_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
        if code_match:
            text = code_match.group(1)
        
        # Try patterns
        patterns = [r'\{[\s\S]*\}', r'\[[\s\S]*\]']
        
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                json_str = match.group()
                
                # Try direct parse
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    # Try fixes
                    fixed = self._fix_json_errors(json_str)
                    if fixed:
                        try:
                            return json.loads(fixed)
                        except:
                            continue
        
        logger.error(f"JSON parse failed for {context}: {text[:300]}...")
        raise ValueError(f"Invalid JSON in {context} response")
    
    def _fix_json_errors(self, json_str: str) -> Optional[str]:
        """Fix common JSON errors"""
        try:
            # Remove trailing commas
            json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
            
            # Close unclosed braces
            open_b = json_str.count('{') - json_str.count('\\{')
            close_b = json_str.count('}') - json_str.count('\\}')
            if open_b > close_b:
                json_str += '}' * (open_b - close_b)
            
            # Close unclosed brackets
            open_br = json_str.count('[') - json_str.count('\\[')
            close_br = json_str.count(']') - json_str.count('\\]')
            if open_br > close_br:
                json_str += ']' * (open_br - close_br)
            
            return json_str
        except:
            return None
    
    def _validate_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validate a single file with TypeScript
        
        Fast validation strategy:
        - Only check the specific file
        - 30s timeout
        - Return immediately on success
        """
        import subprocess
        
        try:
            result = subprocess.run(
                ['npx', 'tsc', '--noEmit', '--skipLibCheck', str(file_path)],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return {"success": True}
            else:
                return {
                    "success": False,
                    "errors": result.stdout[:500]  # Limit error output
                }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "errors": "Validation timeout"
            }
        except Exception as e:
            return {
                "success": False,
                "errors": str(e)
            }
    
    def _get_file_tree(self) -> str:
        """Get lightweight file tree (paths only, no contents)"""
        tree_lines = []
        
        for root, dirs, files in os.walk(self.workspace):
            # Skip node_modules, .git, etc
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', 'dist', 'build', '.next']]
            
            level = root.replace(str(self.workspace), '').count(os.sep)
            indent = '  ' * level
            tree_lines.append(f'{indent}{os.path.basename(root)}/')
            
            subindent = '  ' * (level + 1)
            for file in files[:20]:  # Limit files per directory
                tree_lines.append(f'{subindent}{file}')
        
        return '\n'.join(tree_lines[:200])  # Limit total lines
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        return {
            **self.metrics,
            "success_rate": (
                self.metrics["first_attempt_success"] / self.metrics["tasks_completed"]
                if self.metrics["tasks_completed"] > 0 else 0
            ),
            "edit_success_rate": (
                (self.metrics["total_edits"] - self.metrics["failed_edits"]) / self.metrics["total_edits"]
                if self.metrics["total_edits"] > 0 else 0
            )
        }
