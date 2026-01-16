"""
Real Code Execution Module
Three-phase approach: Deep Understanding → Optimal Implementation → Verification
"""
import os
import asyncio
import subprocess
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from .code_executor import CodeExecutor
from .project_memory import ProjectMemory
from .research_engine import ResearchEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealExecutor:
    """
    Real code executor with three-phase approach:
    1. Deep project understanding
    2. Optimal implementation
    3. Verification and self-correction
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
        
        # Initialize project memory for cross-task continuity
        project_id = os.path.basename(workspace_path)
        self.project_memory = ProjectMemory(project_id)
        
        # Initialize research engine for evidence-based decisions
        self.research_engine = ResearchEngine(
            llm_api_key=self.llm_api_key,
            llm_model=self.llm_model
        )
        logger.info("🔬 Research engine initialized for evidence-based implementation")
        
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
    
    def _get_project_context(self) -> str:
        """
        Build comprehensive project context by reading key files
        """
        context_parts = []
        
        # Key files to read for understanding
        key_files = [
            'package.json',
            'README.md',
            'drizzle/schema.ts',
            'server/routers.ts',
            'server/db.ts',
            'client/src/App.tsx',
            'todo.md'
        ]
        
        for file_path in key_files:
            full_path = os.path.join(self.workspace_path, file_path)
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Limit size to avoid token overflow
                        if len(content) > 5000:
                            content = content[:5000] + "\n... (truncated)"
                        context_parts.append(f"\n### {file_path}\n```\n{content}\n```")
                except Exception as e:
                    logger.warning(f"Could not read {file_path}: {e}")
        
        # ITERATION 3: Comprehensive project structure mapping with import analysis
        context_parts.append("\n### 📁 COMPLETE PROJECT STRUCTURE MAP")
        
        # Map all TypeScript/JavaScript files with their exports and imports
        project_map = {}
        for directory in ['server', 'client/src', 'drizzle']:
            dir_path = os.path.join(self.workspace_path, directory)
            if os.path.exists(dir_path):
                for root, dirs, filenames in os.walk(dir_path):
                    for filename in filenames:
                        if filename.endswith(('.ts', '.tsx', '.js', '.jsx')):
                            file_path = os.path.join(root, filename)
                            rel_path = os.path.relpath(file_path, self.workspace_path)
                            
                            # Analyze file for imports and exports
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                    imports = []
                                    exports = []
                                    
                                    # Extract imports
                                    for line in content.split('\n')[:50]:  # First 50 lines
                                        if 'import' in line and 'from' in line:
                                            imports.append(line.strip())
                                        if line.startswith('export'):
                                            exports.append(line.strip()[:80])  # First 80 chars
                                    
                                    project_map[rel_path] = {
                                        'imports': imports[:10],  # First 10 imports
                                        'exports': exports[:5],   # First 5 exports
                                        'size': len(content)
                                    }
                            except Exception as e:
                                project_map[rel_path] = {'error': str(e)}
        
        # Format project map for LLM
        map_lines = []
        for file_path, info in sorted(project_map.items()):
            if 'error' in info:
                map_lines.append(f"  {file_path} (error reading)")
            else:
                map_lines.append(f"  {file_path} ({info['size']} bytes)")
                if info['imports']:
                    map_lines.append(f"    Imports: {len(info['imports'])} found")
                    for imp in info['imports'][:3]:  # Show first 3
                        map_lines.append(f"      {imp}")
                if info['exports']:
                    map_lines.append(f"    Exports: {len(info['exports'])} found")
        
        context_parts.append("\n".join(map_lines))
        
        # Add critical import paths guide
        context_parts.append("\n### 🎯 CRITICAL IMPORT PATHS GUIDE")
        context_parts.append("""EXISTING FILES - DO NOT CREATE NEW ONES:
- drizzle/schema.ts - Database schema (import from '../drizzle/schema')
- server/db.ts - Database helpers (import from './db')
- server/routers.ts - Main router (import from './routers')
- server/_core/* - Core utilities (import from './_core/...')

WHEN ADDING CODE:
1. Check if file EXISTS in project map above
2. If EXISTS: MODIFY the existing file (show complete modified version)
3. If NOT EXISTS: Create new file in appropriate directory
4. ALWAYS use correct relative import paths based on file location
5. NEVER create duplicate files (e.g., server/schema.ts when drizzle/schema.ts exists)
""")
        
        result = "\n".join(context_parts)
        logger.info(f"📊 Project map generated: {len(project_map)} files analyzed")
        return result
    
    def _run_build(self) -> Dict[str, Any]:
        """
        Run comprehensive build validation including TypeScript type checking
        
        Returns:
            {
                'success': bool,
                'stdout': str,
                'stderr': str,
                'errors': list[str]
            }
        """
        all_errors = []
        all_stdout = []
        all_stderr = []
        
        # Step 1: TypeScript type checking (CRITICAL - catches type errors)
        try:
            logger.info("🔍 Running TypeScript type check...")
            ts_result = subprocess.run(
                ['npx', 'tsc', '--noEmit'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            all_stdout.append("=== TypeScript Check ===")
            all_stdout.append(ts_result.stdout)
            all_stderr.append(ts_result.stderr)
            
            # TypeScript errors are CRITICAL
            if ts_result.returncode != 0:
                for line in (ts_result.stdout + ts_result.stderr).split('\n'):
                    if 'error TS' in line or ': error' in line:
                        all_errors.append(f"[TypeScript] {line.strip()}")
                
                logger.warning(f"❌ TypeScript check failed with {len(all_errors)} errors")
                return {
                    'success': False,
                    'stdout': '\n'.join(all_stdout),
                    'stderr': '\n'.join(all_stderr),
                    'errors': all_errors
                }
            else:
                logger.info("✅ TypeScript check passed")
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '',
                'stderr': 'TypeScript check timeout after 60 seconds',
                'errors': ['TypeScript check timeout']
            }
        except Exception as e:
            logger.warning(f"TypeScript check failed: {e}")
            all_errors.append(f"TypeScript check error: {str(e)}")
        
        # Step 2: Vite build (catches runtime issues)
        try:
            logger.info("🏗️  Running Vite build...")
            build_result = subprocess.run(
                ['pnpm', 'run', 'build'],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            all_stdout.append("\n=== Vite Build ===")
            all_stdout.append(build_result.stdout)
            all_stderr.append(build_result.stderr)
            
            # Parse build errors
            for line in (build_result.stdout + build_result.stderr).split('\n'):
                if 'ERROR' in line or 'error' in line.lower():
                    if 'error TS' not in line:  # Already caught by TypeScript check
                        all_errors.append(f"[Build] {line.strip()}")
            
            if build_result.returncode != 0:
                logger.warning("❌ Vite build failed")
                return {
                    'success': False,
                    'stdout': '\n'.join(all_stdout),
                    'stderr': '\n'.join(all_stderr),
                    'errors': all_errors
                }
            else:
                logger.info("✅ Vite build passed")
        
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'stdout': '\n'.join(all_stdout),
                'stderr': 'Build timeout after 120 seconds',
                'errors': all_errors + ['Build timeout']
            }
        except Exception as e:
            all_errors.append(f"Build error: {str(e)}")
        
        # Step 3: tRPC router validation (if applicable)
        trpc_errors = self._validate_trpc_routers()
        if trpc_errors:
            all_errors.extend(trpc_errors)
            logger.warning(f"❌ tRPC validation failed: {len(trpc_errors)} issues")
            return {
                'success': False,
                'stdout': '\n'.join(all_stdout),
                'stderr': '\n'.join(all_stderr),
                'errors': all_errors
            }
        
        # All checks passed
        logger.info("✅ All build validations passed!")
        return {
            'success': len(all_errors) == 0,
            'stdout': '\n'.join(all_stdout)[-2000:],
            'stderr': '\n'.join(all_stderr)[-2000:],
            'errors': all_errors
        }
    
    def _validate_trpc_routers(self) -> list[str]:
        """
        Validate tRPC router structure to prevent naming collisions
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        routers_path = os.path.join(self.workspace_path, 'server', 'routers.ts')
        
        if not os.path.exists(routers_path):
            return errors  # No tRPC routers to validate
        
        try:
            with open(routers_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for reserved tRPC method names in router definitions
            reserved_names = ['useContext', 'useUtils', 'Provider', 'createClient']
            
            for reserved in reserved_names:
                # Check if reserved name is used as a router key
                if f'{reserved}:' in content or f'"{reserved}"' in content or f"'{reserved}'" in content:
                    errors.append(
                        f"[tRPC] Router uses reserved name '{reserved}' which collides with tRPC built-in methods. "
                        f"Rename this router to avoid conflicts."
                    )
            
            # Check that router is properly exported
            if 'export const appRouter' not in content and 'export default' not in content:
                errors.append(
                    "[tRPC] Router must export 'appRouter' or use default export"
                )
            
            logger.info(f"🔍 tRPC validation: {len(errors)} issues found")
        
        except Exception as e:
            logger.warning(f"Could not validate tRPC routers: {e}")
        
        return errors
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task with three-phase approach
        
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
        
        # PHASE 0: Research evidence-based approaches
        logger.info(f"🔬 Researching evidence-based approaches for: {title}")
        research_guidance = self.research_engine.get_implementation_guidance(
            task_description=f"{title}: {prompt}",
            project_context=self._get_project_context()[:1000]  # Brief context
        )
        
        # Enhance prompt with research findings
        enhanced_prompt = f"{prompt}\n\n{research_guidance}"
        
        try:
            if self.openhands_available and self.llm_api_key:
                # Use OpenHands for real execution
                result = await self._execute_with_openhands(task_id, enhanced_prompt)
            else:
                # Fallback to three-phase LLM approach
                result = await self._execute_with_three_phase_llm(task_id, title, enhanced_prompt)
            
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
        """Execute task using OpenHands SDK"""
        raise NotImplementedError("OpenHands not available")
    
    async def _execute_with_three_phase_llm(self, task_id: str, title: str, prompt: str) -> Dict[str, Any]:
        """
        Execute task using THREE-PHASE approach:
        Phase 1: Deep Understanding
        Phase 2: Optimal Implementation
        Phase 3: Verification & Self-Correction
        
        Args:
            task_id: Task identifier
            title: Task title
            prompt: Task prompt/instructions
        
        Returns:
            Execution result
        """
        try:
            import anthropic
            
            start_time = datetime.utcnow()
            
            # Create Anthropic client
            client = anthropic.Anthropic(api_key=self.llm_api_key)
            
            # Get project context
            logger.info("📚 Building project context...")
            project_context = self._get_project_context()
            
            # ITERATION 4: Get project memory for cross-task continuity
            project_memory_context = self.project_memory.get_context_for_task(task_id, title)
            
            # 🎯 PHASE 1: DEEP UNDERSTANDING (Three-Step Framework)
            logger.info("🔍 Phase 1: Deep Understanding (Job → Outcome → Method)...")
            understanding_prompt = f"""You are an ENTERPRISE-LEVEL senior software engineer analyzing a codebase.

PROJECT WORKSPACE: {self.workspace_path}

PROJECT CONTEXT (Key Files):
{project_context}

{project_memory_context}

TASK TO UNDERSTAND: {title}
{prompt}

PHASE 1 OBJECTIVE: THREE-STEP DEEP UNDERSTANDING
You MUST complete these three steps IN ORDER before any implementation:

═══════════════════════════════════════════════════════════════
STEP 1: UNDERSTAND THE JOB COMPLETELY
═══════════════════════════════════════════════════════════════
What exactly needs to be done?

1.1 **Exact Requirements**
   - What is being asked for? (Be specific)
   - What are the explicit requirements?
   - What are the implicit requirements?
   - What constraints exist?

1.2 **Current State Analysis**
   - What exists now in the codebase?
   - What files are relevant?
   - What patterns are currently used?
   - What similar features already exist?
   - CRITICAL: Use PROJECT STRUCTURE MAP to identify EXISTING files

1.3 **Context & Dependencies**
   - What is the architecture? (React + tRPC + Express + Drizzle ORM)
   - What will this interact with?
   - What database tables are involved?
   - What imports/exports are needed?
   - CRITICAL: Use IMPORT PATHS GUIDE for correct paths

═══════════════════════════════════════════════════════════════
STEP 2: UNDERSTAND THE INTENDED OUTCOME
═══════════════════════════════════════════════════════════════
What should the result look like?

2.1 **Success Criteria**
   - What does "done" mean for this task?
   - What should work when complete?
   - What should the user experience be?
   - What are the acceptance criteria?

2.2 **Problem Being Solved**
   - What problem does this solve?
   - Why is this needed?
   - What value does it provide?
   - What pain point does it address?

2.3 **Integration Requirements**
   - How should this integrate with existing code?
   - What files need modification vs creation?
   - What patterns should be followed?
   - What could break if done wrong?

═══════════════════════════════════════════════════════════════
STEP 3: UNDERSTAND THE BEST RELIABLE WAY
═══════════════════════════════════════════════════════════════
What is the proven, evidence-based approach?

3.1 **Research-Backed Approach**
   - What does research say works? (see research guidance below)
   - What are proven patterns for this?
   - What are evidence-based best practices?
   - What approaches have been validated?

3.2 **Optimal Implementation Strategy**
   - Should I modify existing files or create new ones? (Prefer modify)
   - What is the most reliable implementation path?
   - What patterns from the codebase should I follow?
   - What utilities/helpers are available?

3.3 **Risk Mitigation**
   - What could go wrong?
   - What edge cases need handling?
   - What validation is needed?
   - How do I ensure production quality?

═══════════════════════════════════════════════════════════════

OUTPUT REQUIREMENTS:
Provide a detailed analysis covering ALL THREE STEPS above.

MUST INCLUDE:
- STEP 1 SUMMARY: Complete job understanding
- STEP 2 SUMMARY: Clear intended outcome
- STEP 3 SUMMARY: Best reliable approach with justification
- List of EXISTING files to MODIFY (from project map)
- List of NEW files to CREATE (if any)
- EXACT import paths for each file
- Explanation of WHY this approach is most reliable

Be thorough, specific, and evidence-based.
"""

            understanding_response = client.messages.create(
                model=self.llm_model,
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": understanding_prompt
                }]
            )
            
            understanding = understanding_response.content[0].text if understanding_response.content else ""
            logger.info(f"✅ Understanding complete ({len(understanding)} chars)")
            
            # 🎯 PHASE 2: OPTIMAL IMPLEMENTATION
            logger.info("🚀 Phase 2: Optimal Implementation...")
            implementation_prompt = f"""You are an ENTERPRISE-LEVEL senior software engineer implementing a feature.

PROJECT WORKSPACE: {self.workspace_path}

YOUR UNDERSTANDING (from Phase 1):
{understanding}

TASK: {title}
{prompt}

PHASE 2 OBJECTIVE: OPTIMAL IMPLEMENTATION
Now that you deeply understand the project, implement this task with EXCELLENCE.

CRITICAL REQUIREMENTS:
1. **Follow Existing Patterns** - Match the style and architecture of existing code
2. **Complete Implementation** - No TODOs, no placeholders, no "// implement later"
3. **Production Quality** - Error handling, logging, validation, edge cases
4. **Seamless Integration** - Works perfectly with existing code
5. **Enterprise Standards** - Clean, maintainable, documented
6. **NEVER BREAK EXISTING CODE** - When modifying files, preserve ALL existing imports, exports, and functionality
7. **ADD, DON'T REPLACE** - Add new code alongside existing code, don't delete working code
8. **VERIFY MENTALLY** - Before outputting, verify all imports/exports still work
9. **MODIFY EXISTING FILES** - If a file already exists (like stripeRouter.ts), MODIFY it, don't create a new one
10. **CHECK FILE STRUCTURE** - Based on Phase 1, use EXISTING file paths, don't invent new ones

OUTPUT FORMAT - You MUST use this exact format for ALL code files:

```language path/to/file.ext
// Complete, production-ready code
// Follows existing patterns
// Handles all edge cases
```

EXAMPLES:

```typescript server/routers.ts
import {{ router, publicProcedure, protectedProcedure }} from './_core/trpc';
import {{ z }} from 'zod';
// ... complete implementation following existing pattern
```

```typescript client/src/pages/Feature.tsx
import React from 'react';
import {{ trpc }} from '@/lib/trpc';
// ... complete implementation following existing pattern
```

RULES:
- ALWAYS specify the full file path after the language
- Write COMPLETE implementations (no "// TODO" comments)
- Follow the EXACT patterns you observed in Phase 1
- Include proper TypeScript types
- Add error handling and validation
- Test your logic mentally before outputting
- If modifying existing files, show the COMPLETE modified version
- NEVER delete existing imports - only add new ones
- NEVER remove existing router definitions - only add new ones
- When adding to routers.ts, ADD to the existing router object, don't replace it
- Preserve ALL existing functionality - your changes should be ADDITIVE only
- If a file like server/stripeRouter.ts already exists, MODIFY that file, don't create server/routers/stripe.ts

Now implement this task with ENTERPRISE QUALITY based on your deep understanding:"""

            implementation_response = client.messages.create(
                model=self.llm_model,
                max_tokens=8192,  # More tokens for complete implementations
                messages=[{
                    "role": "user",
                    "content": implementation_prompt
                }]
            )
            
            implementation = implementation_response.content[0].text if implementation_response.content else ""
            logger.info(f"✅ Implementation complete ({len(implementation)} chars)")
            
            # 🔥 EXECUTE THE CODE (WITHOUT COMMITTING YET)!
            logger.info("📝 Parsing and executing code...")
            exec_result = self.code_executor.execute_task(implementation, task_id, skip_commit=True)
            
            # 🎯 PHASE 3: VERIFICATION & SELF-CORRECTION (MULTI-ATTEMPT)
            logger.info("🔍 Phase 3: Verification & Self-Correction...")
            logger.info("📊 Running build to verify code quality...")
            build_result = self._run_build()
            logger.info(f"📊 Build result: {'✅ PASSED' if build_result['success'] else '❌ FAILED'}")
            if not build_result['success']:
                logger.warning(f"⚠️  Build errors detected: {len(build_result.get('errors', []))} errors")
                for i, err in enumerate(build_result.get('errors', [])[:3], 1):
                    logger.warning(f"   Error {i}: {err[:100]}...")
            
            max_fix_attempts = 5
            fix_attempt = 0
            previous_errors = []
            
            while not build_result['success'] and fix_attempt < max_fix_attempts:
                fix_attempt += 1
                logger.warning(f"⚠️  Build failed! Starting self-correction attempt {fix_attempt}/{max_fix_attempts}...")
                logger.info(f"🧠 Analyzing errors and generating fix..." )
                
                # Build fix prompt with learning from previous attempts
                error_history = ""
                if previous_errors:
                    error_history = "\n\nPREVIOUS FIX ATTEMPTS THAT FAILED:\n" + "\n".join(
                        f"Attempt {i+1}: {err}" for i, err in enumerate(previous_errors)
                    )
                
                fix_prompt = f"""The code has build errors. Fix them now.

ORIGINAL TASK: {title} - {prompt[:200]}

CURRENT BUILD ERRORS:
{chr(10).join(build_result['errors'])}

BUILD OUTPUT:
{build_result['stderr']}{error_history}

IMPORTANT:
- Analyze what went wrong
- Fix ONLY the errors shown above
- Do NOT break existing working code
- Provide complete, working files
- Use the EXACT format: ```language path/to/file.ext

Provide the corrected code now:"""

                fix_response = client.messages.create(
                    model=self.llm_model,
                    max_tokens=8192,
                    messages=[{
                        "role": "user",
                        "content": fix_prompt
                    }]
                )
                
                fix_implementation = fix_response.content[0].text if fix_response.content else ""
                logger.info(f"🔧 Fix attempt {fix_attempt} generated ({len(fix_implementation)} chars)")
                
                # Execute the fix (without committing yet)
                logger.info(f"📝 Executing fix attempt {fix_attempt}...")
                fix_result = self.code_executor.execute_task(fix_implementation, f"{task_id}_fix_{fix_attempt}", skip_commit=True)
                logger.info(f"✅ Fix executed, wrote {fix_result.get('files_count', 0)} files")
                
                # Verify fix worked
                logger.info(f"📊 Re-running build to verify fix...")
                build_result = self._run_build()
                logger.info(f"📊 Build result after fix: {'✅ PASSED' if build_result['success'] else '❌ FAILED'}")
                
                if build_result['success']:
                    logger.info(f"✅ Self-correction successful on attempt {fix_attempt}!")
                    break
                else:
                    # Store this attempt's errors for next iteration
                    previous_errors.append(chr(10).join(build_result['errors'][:3]))  # First 3 errors
                    logger.warning(f"❌ Fix attempt {fix_attempt} failed, trying again...")
            
            # If all attempts failed, DISCARD CHANGES (git reset --hard)
            if not build_result['success']:
                logger.error(f"❌ All {max_fix_attempts} self-correction attempts failed! DISCARDING CHANGES...")
                # Discard uncommitted changes
                result = subprocess.run(
                    ['git', 'reset', '--hard', 'HEAD'],
                    cwd=self.workspace_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    logger.info("✅ Changes discarded, back to clean state")
                    build_result['success'] = False
                else:
                    logger.error("❌ Failed to discard changes!")
            else:
                # BUILD PASSED! NOW COMMIT!
                logger.info("✅ Build passed! Committing changes...")
                commit_message = f"Task: {task_id}\n\n{prompt[:200]}"
                committed = self.code_executor.commit_changes(commit_message)
                if committed:
                    logger.info("✅ Changes committed successfully!")
                    
                    # ITERATION 4: Record task completion in project memory
                    self.project_memory.record_task_completion(task_id, {
                        'title': title,
                        'files_created': [f for f in exec_result['files_written'] if 'created' in str(f).lower()],
                        'files_modified': exec_result['files_written'],
                        'patterns_used': [],  # Could extract from understanding phase
                        'decisions': [{'decision': f"Completed {title}", 'rationale': prompt[:200]}],
                        'lessons': []  # Could extract from self-correction attempts
                    })
                    logger.info("🧠 Project memory updated!")
                else:
                    logger.error("❌ Commit failed!")
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            return {
                'mode': 'three_phase_llm',
                'execution_time': f"{execution_time:.1f} seconds",
                'files_modified': exec_result['files_written'],
                'files_count': exec_result['files_count'],
                'commands_executed': exec_result['commands_executed'],
                'commands_succeeded': exec_result['commands_succeeded'],
                'committed': exec_result['committed'],
                'success': exec_result['success'] and build_result['success'],
                'build_passed': build_result['success'],
                'details': exec_result['summary'],
                'understanding_length': len(understanding),
                'implementation_length': len(implementation)
            }
        
        except Exception as e:
            logger.error(f"Three-phase LLM execution failed: {str(e)}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
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
            'execution_mode': 'three_phase_llm'
        }
