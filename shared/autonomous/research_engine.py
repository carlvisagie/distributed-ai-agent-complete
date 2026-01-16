"""
MVP Research Engine for Evidence-Based Decision Making
Searches for empirical research and applies findings to implementation
"""
import logging
from typing import Dict, Any, Optional
from anthropic import Anthropic

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResearchEngine:
    """
    Lightweight research engine that finds empirical evidence
    and applies it to implementation decisions
    """
    
    def __init__(self, llm_api_key: str, llm_model: str = "claude-sonnet-4-20250514"):
        """
        Initialize research engine
        
        Args:
            llm_api_key: Anthropic API key
            llm_model: LLM model to use
        """
        self.client = Anthropic(api_key=llm_api_key)
        self.model = llm_model
        self.research_cache = {}  # Cache research findings
    
    def research_and_recommend(
        self,
        feature_name: str,
        feature_description: str,
        context: str = ""
    ) -> Dict[str, Any]:
        """
        Research empirical evidence for a feature and provide implementation recommendations
        
        Args:
            feature_name: Name of the feature to research
            feature_description: Description of what the feature should do
            context: Additional context about the project
        
        Returns:
            {
                'recommendations': str,  # Evidence-based implementation guidance
                'key_findings': list[str],  # Key research findings
                'best_practices': list[str]  # Evidence-based best practices
            }
        """
        # Check cache first
        cache_key = f"{feature_name}:{feature_description}"
        if cache_key in self.research_cache:
            logger.info(f"📚 Using cached research for: {feature_name}")
            return self.research_cache[cache_key]
        
        logger.info(f"🔬 Researching empirical evidence for: {feature_name}")
        
        try:
            # Use Claude to search for and synthesize research
            prompt = f"""You are a research assistant helping implement evidence-based software features.

FEATURE TO RESEARCH:
Name: {feature_name}
Description: {feature_description}

PROJECT CONTEXT:
{context if context else "General software development"}

YOUR TASK:
1. Search your knowledge for empirical research, peer-reviewed studies, and evidence-based best practices related to this feature
2. Focus on:
   - Proven approaches from research
   - Evidence-based design patterns
   - Validated user experience principles
   - Scientific findings relevant to the feature
3. Synthesize findings into actionable implementation guidance

IMPORTANT:
- Only cite evidence-based, proven approaches
- Avoid speculation or unproven methods
- Focus on what research demonstrates works
- Provide specific, actionable recommendations

OUTPUT FORMAT:
Provide your response in this exact format:

RECOMMENDATIONS:
[Detailed implementation guidance based on research]

KEY FINDINGS:
- [Finding 1]
- [Finding 2]
- [Finding 3]

BEST PRACTICES:
- [Practice 1]
- [Practice 2]
- [Practice 3]
"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            content = response.content[0].text
            
            # Parse response
            result = self._parse_research_response(content)
            
            # Cache the result
            self.research_cache[cache_key] = result
            
            logger.info(f"✅ Research completed for: {feature_name}")
            logger.info(f"   - {len(result['key_findings'])} key findings")
            logger.info(f"   - {len(result['best_practices'])} best practices")
            
            return result
        
        except Exception as e:
            logger.error(f"Research failed: {e}")
            return {
                'recommendations': f"Research unavailable. Implement using standard best practices for {feature_name}.",
                'key_findings': [],
                'best_practices': []
            }
    
    def _parse_research_response(self, content: str) -> Dict[str, Any]:
        """Parse the research response into structured format"""
        result = {
            'recommendations': '',
            'key_findings': [],
            'best_practices': []
        }
        
        # Split content into sections
        sections = content.split('\n')
        current_section = None
        
        for line in sections:
            line = line.strip()
            
            if 'RECOMMENDATIONS:' in line:
                current_section = 'recommendations'
                continue
            elif 'KEY FINDINGS:' in line:
                current_section = 'key_findings'
                continue
            elif 'BEST PRACTICES:' in line:
                current_section = 'best_practices'
                continue
            
            if not line:
                continue
            
            if current_section == 'recommendations':
                result['recommendations'] += line + '\n'
            elif current_section == 'key_findings' and line.startswith('-'):
                result['key_findings'].append(line[1:].strip())
            elif current_section == 'best_practices' and line.startswith('-'):
                result['best_practices'].append(line[1:].strip())
        
        result['recommendations'] = result['recommendations'].strip()
        
        return result
    
    def get_implementation_guidance(
        self,
        task_description: str,
        project_context: str = ""
    ) -> str:
        """
        Get quick implementation guidance based on research
        
        Args:
            task_description: Description of the task to implement
            project_context: Project context
        
        Returns:
            Implementation guidance string
        """
        # Extract feature name from task
        feature_name = task_description.split(':')[0] if ':' in task_description else task_description
        
        research = self.research_and_recommend(
            feature_name=feature_name,
            feature_description=task_description,
            context=project_context
        )
        
        # Format guidance for inclusion in prompts
        guidance = f"""
🔬 EVIDENCE-BASED IMPLEMENTATION GUIDANCE:

{research['recommendations']}

KEY RESEARCH FINDINGS:
{chr(10).join(f'  • {finding}' for finding in research['key_findings'])}

BEST PRACTICES TO FOLLOW:
{chr(10).join(f'  • {practice}' for practice in research['best_practices'])}
"""
        
        return guidance.strip()
