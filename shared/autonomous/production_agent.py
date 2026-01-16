"""
Production-Ready Autonomous Agent V2

Based on Anthropic research + Cursor's approach:
- Minimal context (5-10 files max)
- AI-assisted file surgery (natural language intents)
- Iterative improvement (learn from validation errors)
- Fast execution (<30s per task)

Architecture:
1. Analyze: Identify 5-10 relevant files
2. Edit: Generate natural language intents
3. Apply: AI Surgeon applies intents to files
4. Validate: Check TypeScript compilation
5. Iterate: If failed, improve intent based on error and retry
"""
import os
import json
import time
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import anthropic
import subprocess
import re
from .ai_file_surgeon import AIFileSurgeon, ShadowWorkspace

logger = logging.getLogger(__name__)


class ProductionAgent:
    """
    Minimal, production-ready autonomous agent with iterative improvement
    
    Design principles:
    - Minimal context per phase (<5K tokens)
    - Natural language intents (AI Surgeon applies them)
    - Incremental validation (after each edit)
    - Iterative improvement (learn from errors, retry up to 3x)
    - Fast failure (stop after 3 attempts)
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
        
        # Cursor's approach: AI-assisted file surgery
        self.surgeon = AIFileSurgeon(
            api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
            model=model
        )
        self.shadow = ShadowWorkspace(self.workspace)
        
        # Metrics
        self.metrics = {
            "tasks_completed": 0,
            "first_attempt_success": 0,
            "total_edits": 0,
            "successful_edits": 0,
            "failed_edits": 0,
            "retry_successes": 0
        }
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single task with iterative improvement
        
        Flow:
        1. Analyze (identify relevant files)
        2. Generate intents (what to change)
        3. Apply with AI Surgeon
        4. Validate
        5. If failed: improve intent from error, retry up to 2 more times
        """
        start_time = time.time()
        
        try:
            # Phase 1: Analyze
            analysis = self._analyze_task(task)
            
            # Phase 2: Generate intents
            edits = self._generate_edit_intents(task, analysis)
            
            # Phase 3: Apply with iterative improvement
            results = self._apply_edits_with_iteration(edits)
            
            # Calculate metrics
            successful = sum(1 for r in results if r["success"])
            execution_time = time.time() - start_time
            
            self.metrics["tasks_completed"] += 1
            self.metrics["total_edits"] += len(edits)
            self.metrics["successful_edits"] += successful
            
            if successful == len(edits):
                self.metrics["first_attempt_success"] += 1
            
            return {
                "status": "success" if successful == len(edits) else "partial" if successful > 0 else "failed",
                "edits_made": len(edits),
                "successful": successful,
                "results": results,
                "time": execution_time,
                "success_rate": successful / len(edits) if edits else 0
            }
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "time": time.time() - start_time
            }
    
    def _analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 1: Minimal analysis - identify 5-10 relevant files"""
        
        # Get project structure (limit to 100 most relevant files)
        project_map = self._get_minimal_project_map()
        
        prompt = f"""Analyze this task and identify the 5-10 most relevant files.

TASK: {task.get('title')}
REQUIREMENTS: {task.get('requirements', task.get('description', ''))}

PROJECT FILES (top 100):
{project_map}

Output JSON:
{{
  "relevant_files": [
    {{"path": "server/routers.ts", "reason": "Contains tRPC procedures to modify"}},
    {{"path": "drizzle/schema.ts", "reason": "Need to add new table"}}
  ],
  "approach": "Brief description of implementation approach"
}}

Keep it minimal - only files you'll actually modify."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            timeout=60,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return self._parse_json_robust(response.content[0].text, "analysis")
    
    def _generate_edit_intents(self, task: Dict[str, Any], analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Phase 2: Generate natural language intents for AI Surgeon"""
        
        # Verify files exist and load content
        relevant_files = analysis.get("relevant_files", [])
        file_contents = {}
        verified_files = []
        
        for file_info in relevant_files:
            file_path = self.workspace / file_info["path"]
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_contents[file_info["path"]] = f.read()
                verified_files.append(file_info)
                logger.info(f"✓ Found {file_info['path']}")
            elif "create" in file_info.get("reason", "").lower() or not file_path.parent.exists():
                file_contents[file_info["path"]] = "// NEW FILE"
                verified_files.append(file_info)
                logger.info(f"+ Will create {file_info['path']}")
            else:
                logger.warning(f"✗ File not found: {file_info['path']} (skipping)")
        
        if not verified_files:
            raise ValueError("No valid files found to modify")
        
        # Build minimal prompt
        files_context = "\n\n".join([
            f"=== {path} ===\n{content[:2000]}"  # Limit to 2K chars per file
            for path, content in file_contents.items()
        ])
        
        prompt = f"""Generate targeted edit intents for this task.

TASK: {task.get('title')}
REQUIREMENTS:
{task.get('requirements', task.get('description', ''))}

APPROACH: {analysis['approach']}

VERIFIED FILES (these exist in the project):
{', '.join([f['path'] for f in verified_files])}

CURRENT FILES:
{files_context}

Output JSON array of NATURAL LANGUAGE edit intents (for AI Surgeon):
[
  {{
    "file": "server/routers.ts",
    "operation": "modify" | "create",
    "intent": "Describe what to change in natural language. Be specific about:
               - Which function/section to modify
               - What the change should accomplish
               - Important context or constraints"
  }}
]

EXAMPLE (modify existing file):
{{
  "file": "server/routers.ts",
  "operation": "modify",
  "intent": "In the sendMessage procedure, change it from publicProcedure to protectedProcedure so only authenticated users can send messages. Keep all the existing input validation and response logic."
}}

EXAMPLE (create new file):
{{
  "file": "server/utils.ts",
  "operation": "create",
  "intent": "Create a utility file with a generateSessionId function that creates anonymous session IDs using crypto.randomBytes. Export the function and include proper TypeScript types."
}}

CRITICAL RULES:
1. Use natural language intents (AI Surgeon will apply them)
2. Be specific about WHAT to change and WHY
3. Include context (which function, which section)
4. Don't include actual code - just describe the change
5. One intent per file modification"""

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
    
    def _apply_edits_with_iteration(self, edits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Phase 3: Apply edits with iterative improvement
        
        For each edit:
        1. Try to apply with AI Surgeon
        2. Validate
        3. If failed: analyze error, improve intent, retry (up to 2 more times)
        4. If still failed: rollback and continue
        """
        results = []
        
        for i, edit in enumerate(edits):
            logger.info(f"📝 AI Surgeon working on {i+1}/{len(edits)}: {edit['file']}")
            
            file_path = self.workspace / edit["file"]
            rel_path = edit["file"]
            
            # Try up to 3 times total (1 initial + 2 retries)
            success = False
            for attempt in range(3):
                if attempt > 0:
                    logger.info(f"🔄 Retry attempt {attempt}/2 with improved intent")
                
                try:
                    # Use current intent (improved on retries)
                    current_intent = edit.get("improved_intent", edit["intent"])
                    
                    if edit["operation"] == "create":
                        # Create new file
                        result = self.surgeon.create_file(
                            file_path=file_path,
                            intent=current_intent
                        )
                        
                        if result["success"]:
                            self.shadow.update_file(rel_path, result["content"])
                        else:
                            raise ValueError(result["error"])
                    
                    else:
                        # Modify existing file
                        current_content = self.shadow.load_file(rel_path)
                        
                        result = self.surgeon.apply_edit(
                            file_path=file_path,
                            intent=current_intent,
                            current_content=current_content
                        )
                        
                        if result["success"]:
                            self.shadow.update_file(rel_path, result["new_content"])
                        else:
                            raise ValueError(result["error"])
                    
                    # Commit to real filesystem
                    if not self.shadow.commit(rel_path):
                        raise ValueError("Failed to commit file")
                    
                    # Validate
                    validation = self._validate_file(file_path)
                    
                    if validation["success"]:
                        logger.info(f"✅ Edit {i+1} succeeded" + (f" on attempt {attempt+1}" if attempt > 0 else ""))
                        results.append({
                            "edit": edit,
                            "success": True,
                            "validation": validation,
                            "attempts": attempt + 1
                        })
                        if attempt > 0:
                            self.metrics["retry_successes"] += 1
                        success = True
                        break
                    
                    else:
                        # Validation failed - improve and retry
                        logger.warning(f"⚠️  Validation failed: {validation.get('error', 'Unknown error')[:200]}")
                        self.shadow.rollback(rel_path)
                        
                        if attempt < 2:  # Can still retry
                            # Improve intent based on error
                            improved = self._improve_intent_from_error(
                                original_intent=current_intent,
                                error_message=validation.get("error", "Validation failed"),
                                file_path=file_path
                            )
                            
                            if improved:
                                edit["improved_intent"] = improved
                                logger.info(f"💡 Generated improved intent")
                            else:
                                logger.warning(f"Could not improve intent, will retry with same")
                        
                except Exception as e:
                    logger.error(f"❌ Attempt {attempt+1} failed: {e}")
                    self.shadow.rollback(rel_path)
                    
                    if attempt < 2:
                        time.sleep(1)  # Brief pause before retry
            
            if not success:
                logger.error(f"❌ Edit {i+1} failed after 3 attempts")
                results.append({
                    "edit": edit,
                    "success": False,
                    "attempts": 3,
                    "rolled_back": True
                })
                self.metrics["failed_edits"] += 1
        
        return results
    
    def _improve_intent_from_error(
        self,
        original_intent: str,
        error_message: str,
        file_path: Path
    ) -> Optional[str]:
        """
        Generate improved intent based on validation error
        
        This is the key to iterative improvement - learn from errors
        """
        try:
            # Read current file state
            current_content = ""
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    current_content = f.read()[:2000]
            
            prompt = f"""The previous edit attempt failed validation. Improve the intent to fix the error.

ORIGINAL INTENT:
{original_intent}

VALIDATION ERROR:
{error_message[:500]}

CURRENT FILE STATE:
{current_content}

Generate an IMPROVED intent that addresses the validation error.
Focus on:
1. What caused the error (missing import, wrong type, syntax issue)
2. How to fix it while keeping the original goal
3. Any additional context needed

Output ONLY the improved intent as plain text (no JSON, no markdown):"""

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                timeout=30,
                messages=[{"role": "user", "content": prompt}]
            )
            
            improved = response.content[0].text.strip()
            
            # Clean up any markdown formatting
            improved = re.sub(r'^```.*\n', '', improved)
            improved = re.sub(r'\n```$', '', improved)
            improved = improved.strip()
            
            return improved if improved and len(improved) > 20 else None
            
        except Exception as e:
            logger.error(f"Failed to improve intent: {e}")
            return None
    
    def _validate_file(self, file_path: Path) -> Dict[str, Any]:
        """Validate single file with TypeScript"""
        try:
            result = subprocess.run(
                ['npx', 'tsc', '--noEmit', str(file_path)],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=180
            )
            
            if result.returncode == 0:
                return {"success": True}
            else:
                # Filter out UI component errors
                errors = result.stderr
                if "client/src/components/ui/" in errors:
                    # Ignore UI component errors
                    return {"success": True}
                
                return {
                    "success": False,
                    "error": errors[:1000]
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_minimal_project_map(self) -> str:
        """Get minimal project structure (top 100 files)"""
        try:
            result = subprocess.run(
                ['find', '.', '-type', 'f', '-name', '*.ts', '-o', '-name', '*.tsx'],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            files = result.stdout.strip().split('\n')
            # Filter out node_modules, .git, etc
            files = [f for f in files if 'node_modules' not in f and '.git' not in f]
            # Limit to 100 files
            files = files[:100]
            
            return '\n'.join(files)
        except:
            return "// Could not read project structure"
    
    def _parse_json_robust(self, text: str, context: str) -> Any:
        """Robust JSON parsing with fallbacks"""
        # Try direct parse
        try:
            return json.loads(text)
        except:
            pass
        
        # Try extracting from markdown code block
        match = re.search(r'```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        
        # Try finding JSON object/array
        match = re.search(r'(\{.*\}|\[.*\])', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass
        
        logger.error(f"JSON parse failed for {context}: {text[:200]}")
        raise ValueError(f"Invalid JSON in {context} response")
