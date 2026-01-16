"""
Active Learning & Evolution Engine
Extracts patterns, lessons, and improvements from agent execution
"""
import re
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class LearningEngine:
    """
    Extracts actionable knowledge from agent execution:
    - Patterns that worked (for reuse)
    - Errors and their fixes (for prevention)
    - Performance metrics (for optimization)
    """
    
    def extract_patterns_from_code(self, code_response: str, task_title: str) -> List[str]:
        """
        Extract reusable patterns from successful code implementation
        
        Args:
            code_response: LLM's code implementation
            task_title: What the task was trying to accomplish
        
        Returns:
            List of pattern descriptions
        """
        patterns = []
        
        # Pattern 1: tRPC procedure patterns
        if 'publicProcedure' in code_response or 'protectedProcedure' in code_response:
            if '.query(' in code_response:
                patterns.append("tRPC query procedure pattern")
            if '.mutation(' in code_response:
                patterns.append("tRPC mutation procedure pattern")
            if '.input(z.' in code_response:
                patterns.append("tRPC Zod input validation pattern")
        
        # Pattern 2: Database patterns
        if 'db.select()' in code_response or 'db.insert()' in code_response:
            patterns.append("Drizzle ORM database query pattern")
        
        if 'db.transaction' in code_response:
            patterns.append("Database transaction pattern")
        
        # Pattern 3: React patterns
        if 'trpc.' in code_response and '.useQuery' in code_response:
            patterns.append("tRPC React query hook pattern")
        
        if 'trpc.' in code_response and '.useMutation' in code_response:
            patterns.append("tRPC React mutation hook pattern")
        
        if 'onMutate:' in code_response and 'onError:' in code_response:
            patterns.append("Optimistic update pattern with rollback")
        
        # Pattern 4: Authentication patterns
        if 'ctx.user' in code_response and 'protectedProcedure' in code_response:
            patterns.append("Protected route with user context pattern")
        
        # Pattern 5: Error handling patterns
        if 'try {' in code_response and 'catch' in code_response:
            patterns.append("Try-catch error handling pattern")
        
        if 'TRPCError' in code_response:
            patterns.append("tRPC error throwing pattern")
        
        # Pattern 6: Schema patterns
        if 'sqliteTable' in code_response or 'mysqlTable' in code_response:
            patterns.append("Drizzle schema definition pattern")
        
        # Pattern 7: Component patterns
        if 'export default function' in code_response and 'return (' in code_response:
            patterns.append("React functional component pattern")
        
        if 'useState' in code_response or 'useEffect' in code_response:
            patterns.append("React hooks pattern")
        
        logger.info(f"📊 Extracted {len(patterns)} patterns from implementation")
        return patterns
    
    def extract_lessons_from_errors(
        self,
        initial_errors: List[str],
        fix_attempts: List[Dict[str, Any]],
        final_success: bool
    ) -> List[str]:
        """
        Extract lessons from error recovery process
        
        Args:
            initial_errors: Errors from first implementation
            fix_attempts: List of fix attempts with their errors
            final_success: Whether fixes ultimately succeeded
        
        Returns:
            List of lesson descriptions
        """
        lessons = []
        
        if not initial_errors:
            return lessons
        
        # Analyze error types
        error_types = set()
        for error in initial_errors:
            if 'TypeScript' in error or 'error TS' in error:
                error_types.add('typescript')
            if 'Cannot find module' in error or 'import' in error.lower():
                error_types.add('import')
            if 'tRPC' in error or 'router' in error.lower():
                error_types.add('trpc')
            if 'undefined' in error.lower() or 'null' in error.lower():
                error_types.add('null_safety')
            if 'type' in error.lower() and 'assignable' in error.lower():
                error_types.add('type_mismatch')
        
        # Generate specific lessons based on error patterns
        if 'typescript' in error_types:
            lessons.append(
                "TypeScript validation: Always check type compatibility before implementing. "
                "Use 'npx tsc --noEmit' to catch type errors early."
            )
        
        if 'import' in error_types:
            lessons.append(
                "Import path errors: Always verify file exists in project structure before importing. "
                "Use relative paths correctly based on file location."
            )
        
        if 'trpc' in error_types:
            lessons.append(
                "tRPC router issues: Avoid reserved names (useContext, useUtils, Provider). "
                "Always check existing router structure before adding procedures."
            )
        
        if 'null_safety' in error_types:
            lessons.append(
                "Null safety: Add proper null checks and optional chaining (?.) "
                "when accessing potentially undefined properties."
            )
        
        if 'type_mismatch' in error_types:
            lessons.append(
                "Type mismatches: Ensure function return types match expected types. "
                "Use type assertions carefully and prefer proper typing."
            )
        
        # Lesson from fix attempts
        if fix_attempts and final_success:
            lessons.append(
                f"Self-correction successful after {len(fix_attempts)} attempts. "
                f"Error recovery process works - continue using iterative fixes."
            )
        elif fix_attempts and not final_success:
            lessons.append(
                f"Failed after {len(fix_attempts)} fix attempts. "
                f"May need human intervention or different approach for this error type."
            )
        
        logger.info(f"📚 Extracted {len(lessons)} lessons from error recovery")
        return lessons
    
    def extract_decisions_from_understanding(
        self,
        understanding_text: str,
        task_title: str
    ) -> List[Dict[str, str]]:
        """
        Extract architectural decisions from understanding phase
        
        Args:
            understanding_text: LLM's understanding analysis
            task_title: What the task is about
        
        Returns:
            List of decision dictionaries with 'decision' and 'rationale'
        """
        decisions = []
        
        # Look for explicit decision markers
        decision_patterns = [
            r'(?:I will|I\'ll|Decision:|Approach:)\s*([^.!?\n]+[.!?])',
            r'(?:The best way|Optimal approach|Strategy):\s*([^.!?\n]+[.!?])',
            r'(?:Should|Must|Will)\s+(use|implement|create|modify)\s+([^.!?\n]+[.!?])'
        ]
        
        for pattern in decision_patterns:
            matches = re.findall(pattern, understanding_text, re.IGNORECASE)
            for match in matches[:3]:  # Top 3 decisions
                if isinstance(match, tuple):
                    decision_text = ' '.join(match)
                else:
                    decision_text = match
                
                decisions.append({
                    'decision': decision_text.strip()[:200],  # Limit length
                    'rationale': f"From understanding phase for: {task_title}"
                })
        
        # If no explicit decisions found, extract key points
        if not decisions and understanding_text:
            # Look for bullet points or numbered lists
            lines = understanding_text.split('\n')
            for line in lines:
                if line.strip().startswith(('-', '*', '1.', '2.', '3.')):
                    clean_line = re.sub(r'^[-*\d.]+\s*', '', line.strip())
                    if len(clean_line) > 20:  # Meaningful content
                        decisions.append({
                            'decision': clean_line[:200],
                            'rationale': f"Key point from {task_title} analysis"
                        })
                        if len(decisions) >= 3:
                            break
        
        logger.info(f"🎯 Extracted {len(decisions)} decisions from understanding phase")
        return decisions
    
    def calculate_performance_metrics(
        self,
        execution_time: float,
        fix_attempts: int,
        final_success: bool
    ) -> Dict[str, Any]:
        """
        Calculate performance metrics for this task execution
        
        Returns:
            Dictionary with performance metrics
        """
        return {
            'execution_time_seconds': round(execution_time, 2),
            'fix_attempts_needed': fix_attempts,
            'first_attempt_success': fix_attempts == 0,
            'final_success': final_success,
            'efficiency_score': 1.0 if fix_attempts == 0 else max(0.0, 1.0 - (fix_attempts * 0.2))
        }
