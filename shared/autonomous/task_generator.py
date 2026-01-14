"""
Autonomous Task Generator
Generates prioritized tasks based on website analysis and industry standards
"""
from typing import Dict, List
try:
    from .coaching_standards import CoachingStandards
except ImportError:
    from coaching_standards import CoachingStandards


class TaskGenerator:
    """Generates tasks for autonomous execution"""
    
    def __init__(self):
        self.standards = CoachingStandards()
    
    def generate_tasks(self, analysis_report: Dict) -> List[Dict]:
        """
        Generate prioritized list of tasks based on website analysis
        
        Args:
            analysis_report: Website analysis report from analyzer
            
        Returns:
            List of tasks with priorities and details
        """
        tasks = []
        
        # Get recommendations from standards
        recommendations = self.standards.generate_recommendations(analysis_report)
        
        # Convert recommendations to executable tasks
        for i, rec in enumerate(recommendations, 1):
            task = self._create_task_from_recommendation(rec, i)
            tasks.append(task)
        
        # Add additional tasks based on specific issues
        tasks.extend(self._generate_fix_tasks(analysis_report))
        
        # Sort by priority
        tasks = self._prioritize_tasks(tasks)
        
        return tasks
    
    def _create_task_from_recommendation(self, recommendation: Dict, task_id: int) -> Dict:
        """Convert recommendation to executable task"""
        category = recommendation['category']
        
        if category == 'structure':
            return self._create_page_task(recommendation, task_id)
        elif category == 'feature':
            return self._create_feature_task(recommendation, task_id)
        elif category == 'security':
            return self._create_security_task(recommendation, task_id)
        elif category == 'performance':
            return self._create_performance_task(recommendation, task_id)
        else:
            return self._create_generic_task(recommendation, task_id)
    
    def _create_page_task(self, rec: Dict, task_id: int) -> Dict:
        """Create task for building a page"""
        page_name = rec['title'].replace('Add ', '').replace(' Page', '').lower()
        
        return {
            "id": task_id,
            "type": "create_page",
            "priority": rec['priority'],
            "title": rec['title'],
            "description": rec['description'],
            "page_name": page_name,
            "elements": rec.get('elements', []),
            "guidelines": rec.get('guidelines', ''),
            "estimated_time": "30-60 minutes",
            "dependencies": [],
            "prompt": self._generate_page_prompt(page_name, rec)
        }
    
    def _create_feature_task(self, rec: Dict, task_id: int) -> Dict:
        """Create task for implementing a feature"""
        return {
            "id": task_id,
            "type": "add_feature",
            "priority": rec['priority'],
            "title": rec['title'],
            "description": rec['description'],
            "elements": rec.get('elements', []),
            "estimated_time": "20-40 minutes",
            "dependencies": [],
            "prompt": self._generate_feature_prompt(rec)
        }
    
    def _create_security_task(self, rec: Dict, task_id: int) -> Dict:
        """Create task for security improvements"""
        return {
            "id": task_id,
            "type": "security",
            "priority": rec['priority'],
            "title": rec['title'],
            "description": rec['description'],
            "elements": rec.get('elements', []),
            "estimated_time": "15-30 minutes",
            "dependencies": [],
            "prompt": self._generate_security_prompt(rec)
        }
    
    def _create_performance_task(self, rec: Dict, task_id: int) -> Dict:
        """Create task for performance optimization"""
        return {
            "id": task_id,
            "type": "optimize",
            "priority": rec['priority'],
            "title": rec['title'],
            "description": rec['description'],
            "elements": rec.get('elements', []),
            "estimated_time": "30-45 minutes",
            "dependencies": [],
            "prompt": self._generate_performance_prompt(rec)
        }
    
    def _create_generic_task(self, rec: Dict, task_id: int) -> Dict:
        """Create generic task"""
        return {
            "id": task_id,
            "type": "generic",
            "priority": rec['priority'],
            "title": rec['title'],
            "description": rec['description'],
            "estimated_time": "20-40 minutes",
            "dependencies": [],
            "prompt": f"{rec['title']}: {rec['description']}"
        }
    
    def _generate_page_prompt(self, page_name: str, rec: Dict) -> str:
        """Generate detailed prompt for page creation"""
        elements = rec.get('elements', [])
        guidelines = rec.get('guidelines', '')
        
        prompt = f"""Create a professional {page_name} page for a coaching website.

REQUIREMENTS:
{chr(10).join(f'- {element}' for element in elements)}

CONTENT GUIDELINES:
{guidelines}

DESIGN PRINCIPLES:
- Clean, modern, professional aesthetic
- Mobile-first responsive design
- Clear hierarchy and easy navigation
- Calming, professional colors
- Generous whitespace
- Professional imagery
- Clear call-to-action

TECHNICAL REQUIREMENTS:
- Semantic HTML5
- Modern CSS (Flexbox/Grid)
- Responsive (mobile, tablet, desktop)
- Fast loading (<3s)
- Accessible (WCAG 2.1)
- SEO optimized (meta tags, headings)

Create the page with placeholder content that follows coaching industry best practices.
"""
        return prompt
    
    def _generate_feature_prompt(self, rec: Dict) -> str:
        """Generate prompt for feature implementation"""
        elements = rec.get('elements', [])
        
        prompt = f"""{rec['title']}

{rec['description']}

REQUIREMENTS:
{chr(10).join(f'- {element}' for element in elements)}

IMPLEMENTATION:
- Use modern, clean code
- Follow best practices
- Add proper validation
- Include error handling
- Make it user-friendly
- Test functionality

Implement this feature professionally and ensure it works correctly.
"""
        return prompt
    
    def _generate_security_prompt(self, rec: Dict) -> str:
        """Generate prompt for security improvements"""
        elements = rec.get('elements', [])
        
        prompt = f"""{rec['title']}

{rec['description']}

SECURITY REQUIREMENTS:
{chr(10).join(f'- {element}' for element in elements)}

IMPLEMENTATION:
- Follow security best practices
- Use HTTPS everywhere
- Implement proper headers
- Validate all inputs
- Sanitize outputs
- Add CSRF protection

Ensure the website is secure and follows industry standards.
"""
        return prompt
    
    def _generate_performance_prompt(self, rec: Dict) -> str:
        """Generate prompt for performance optimization"""
        elements = rec.get('elements', [])
        
        prompt = f"""{rec['title']}

{rec['description']}

OPTIMIZATION TASKS:
{chr(10).join(f'- {element}' for element in elements)}

IMPLEMENTATION:
- Optimize images (compress, lazy load)
- Minify CSS and JavaScript
- Enable browser caching
- Use CDN for static assets
- Reduce HTTP requests
- Implement code splitting

Target: Page load time under 3 seconds.
"""
        return prompt
    
    def _generate_fix_tasks(self, analysis_report: Dict) -> List[Dict]:
        """Generate tasks for fixing broken elements"""
        tasks = []
        task_id = 1000  # Start fix tasks at 1000
        
        # Fix broken links
        broken_links = analysis_report.get('broken_links', [])
        if broken_links:
            tasks.append({
                "id": task_id,
                "type": "fix",
                "priority": "high",
                "title": "Fix Broken Links",
                "description": f"Fix {len(broken_links)} broken links on the website",
                "broken_links": broken_links[:10],  # Limit to first 10
                "estimated_time": "15-30 minutes",
                "dependencies": [],
                "prompt": f"Fix the following broken links:\n" + 
                         "\n".join(f"- {link['url']}" for link in broken_links[:10])
            })
            task_id += 1
        
        return tasks
    
    def _prioritize_tasks(self, tasks: List[Dict]) -> List[Dict]:
        """Sort tasks by priority and dependencies"""
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        
        # Sort by priority
        tasks.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return tasks
    
    def generate_task_summary(self, tasks: List[Dict]) -> str:
        """Generate human-readable summary of tasks"""
        if not tasks:
            return "No tasks generated. Website appears complete!"
        
        summary = f"Generated {len(tasks)} tasks:\n\n"
        
        # Group by priority
        by_priority = {}
        for task in tasks:
            priority = task['priority']
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(task)
        
        # Format summary
        for priority in ['critical', 'high', 'medium', 'low']:
            if priority in by_priority:
                summary += f"\n{priority.upper()} PRIORITY ({len(by_priority[priority])} tasks):\n"
                for task in by_priority[priority]:
                    summary += f"  {task['id']}. {task['title']}\n"
        
        # Estimate total time
        total_time = sum(self._parse_time_estimate(t.get('estimated_time', '30 minutes')) 
                        for t in tasks)
        hours = total_time // 60
        minutes = total_time % 60
        
        summary += f"\nEstimated total time: {hours}h {minutes}m\n"
        
        return summary
    
    def _parse_time_estimate(self, time_str: str) -> int:
        """Parse time estimate string to minutes"""
        # Simple parser for "30-60 minutes" format
        try:
            if '-' in time_str:
                parts = time_str.split('-')
                return int(parts[0])
            else:
                return int(time_str.split()[0])
        except:
            return 30  # Default to 30 minutes


if __name__ == "__main__":
    # Test the task generator
    print("="*50)
    print("TASK GENERATOR TEST")
    print("="*50)
    
    # Mock analysis report
    mock_report = {
        "url": "https://example-coaching.com",
        "pages_found": 2,
        "structure": {
            "homepage": True,
            "about": False,
            "services": False,
            "contact": True,
            "blog": False,
            "testimonials": False
        },
        "features": {
            "contact_form": False,
            "ssl": True,
            "responsive": "unknown"
        },
        "broken_links": [
            {"url": "https://example.com/broken1"},
            {"url": "https://example.com/broken2"}
        ],
        "performance": {
            "load_time_seconds": 4.5
        }
    }
    
    generator = TaskGenerator()
    tasks = generator.generate_tasks(mock_report)
    
    print(generator.generate_task_summary(tasks))
    
    print("\n" + "="*50)
    print("FIRST TASK DETAIL:")
    print("="*50)
    if tasks:
        task = tasks[0]
        print(f"\nID: {task['id']}")
        print(f"Type: {task['type']}")
        print(f"Priority: {task['priority']}")
        print(f"Title: {task['title']}")
        print(f"Description: {task['description']}")
        print(f"\nPrompt:\n{task['prompt']}")
