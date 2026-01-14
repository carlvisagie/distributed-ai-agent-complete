"""
Coaching Industry Standards and Best Practices
Knowledge base for what a professional coaching website should have
"""
from typing import Dict, List


class CoachingStandards:
    """Industry standards for coaching websites"""
    
    @staticmethod
    def get_required_pages() -> Dict[str, Dict]:
        """
        Get list of required pages for a professional coaching website
        
        Returns:
            Dictionary of page requirements
        """
        return {
            "homepage": {
                "priority": "critical",
                "elements": [
                    "Hero section with clear value proposition",
                    "Coach photo and brief intro",
                    "Services overview",
                    "Client testimonials",
                    "Clear call-to-action (Book Now/Contact)",
                    "Trust indicators (certifications, experience)",
                    "Social proof (client count, success stories)"
                ],
                "content_guidelines": "Focus on transformation and results"
            },
            "about": {
                "priority": "critical",
                "elements": [
                    "Professional coach bio",
                    "Credentials and certifications",
                    "Coaching philosophy",
                    "Personal story/journey",
                    "Professional photo",
                    "Why you became a coach"
                ],
                "content_guidelines": "Build trust and connection"
            },
            "services": {
                "priority": "critical",
                "elements": [
                    "Detailed service descriptions",
                    "Coaching packages/programs",
                    "What's included in each package",
                    "Duration and format",
                    "Pricing (or 'Contact for pricing')",
                    "Who it's for",
                    "Expected outcomes"
                ],
                "content_guidelines": "Be specific about deliverables"
            },
            "contact": {
                "priority": "critical",
                "elements": [
                    "Contact form (name, email, message)",
                    "Email address",
                    "Phone number (optional)",
                    "Booking calendar integration",
                    "Response time expectation",
                    "Privacy policy link"
                ],
                "content_guidelines": "Make it easy to reach you"
            },
            "testimonials": {
                "priority": "high",
                "elements": [
                    "Client testimonials with names",
                    "Before/after stories",
                    "Specific results achieved",
                    "Client photos (if available)",
                    "Video testimonials (bonus)",
                    "Case studies"
                ],
                "content_guidelines": "Show real transformation"
            },
            "blog": {
                "priority": "medium",
                "elements": [
                    "Coaching tips and insights",
                    "Client success stories",
                    "Industry trends",
                    "Personal development content",
                    "SEO-optimized articles"
                ],
                "content_guidelines": "Demonstrate expertise"
            },
            "faq": {
                "priority": "medium",
                "elements": [
                    "Common questions answered",
                    "Coaching process explained",
                    "Payment and cancellation policies",
                    "What to expect",
                    "How coaching works"
                ],
                "content_guidelines": "Address objections"
            },
            "pricing": {
                "priority": "medium",
                "elements": [
                    "Clear pricing structure",
                    "Package comparisons",
                    "Payment options",
                    "Money-back guarantee (if offered)",
                    "Value justification"
                ],
                "content_guidelines": "Be transparent"
            }
        }
    
    @staticmethod
    def get_required_features() -> Dict[str, Dict]:
        """
        Get list of required features for a professional coaching website
        
        Returns:
            Dictionary of feature requirements
        """
        return {
            "responsive_design": {
                "priority": "critical",
                "description": "Mobile-first, works on all devices",
                "test": "Check on phone, tablet, desktop"
            },
            "fast_loading": {
                "priority": "critical",
                "description": "Page loads in under 3 seconds",
                "test": "Use PageSpeed Insights"
            },
            "ssl_certificate": {
                "priority": "critical",
                "description": "HTTPS enabled for security",
                "test": "URL starts with https://"
            },
            "contact_form": {
                "priority": "critical",
                "description": "Working contact form with validation",
                "test": "Submit form and verify email received"
            },
            "booking_system": {
                "priority": "high",
                "description": "Online booking/scheduling",
                "test": "Can book a session online"
            },
            "seo_optimization": {
                "priority": "high",
                "description": "Meta tags, descriptions, keywords",
                "test": "Check meta tags in page source"
            },
            "social_proof": {
                "priority": "high",
                "description": "Testimonials, reviews, case studies",
                "test": "Testimonials visible on site"
            },
            "clear_cta": {
                "priority": "high",
                "description": "Prominent call-to-action buttons",
                "test": "CTA visible above fold"
            },
            "professional_design": {
                "priority": "high",
                "description": "Clean, modern, trustworthy aesthetic",
                "test": "Visual inspection"
            },
            "accessibility": {
                "priority": "medium",
                "description": "WCAG 2.1 compliance",
                "test": "Use accessibility checker"
            },
            "analytics": {
                "priority": "medium",
                "description": "Google Analytics or similar",
                "test": "Check for tracking code"
            },
            "email_integration": {
                "priority": "medium",
                "description": "Email marketing integration",
                "test": "Newsletter signup form"
            }
        }
    
    @staticmethod
    def get_content_guidelines() -> Dict[str, List[str]]:
        """
        Get content writing guidelines for coaching websites
        
        Returns:
            Dictionary of content guidelines
        """
        return {
            "tone": [
                "Professional yet warm",
                "Empathetic and understanding",
                "Confident but not arrogant",
                "Inspiring and motivational",
                "Authentic and genuine"
            ],
            "messaging": [
                "Focus on client transformation",
                "Use 'you' language (client-focused)",
                "Avoid jargon and buzzwords",
                "Be specific about results",
                "Address pain points directly",
                "Show empathy for struggles",
                "Demonstrate expertise subtly"
            ],
            "calls_to_action": [
                "Book a free consultation",
                "Schedule a discovery call",
                "Get started today",
                "Contact me to learn more",
                "Download free resource",
                "Join my mailing list"
            ],
            "trust_building": [
                "Display certifications prominently",
                "Show years of experience",
                "Include client testimonials",
                "Mention number of clients helped",
                "Share success metrics",
                "Link to social media profiles",
                "Include professional photos"
            ]
        }
    
    @staticmethod
    def get_design_principles() -> Dict[str, str]:
        """
        Get design principles for coaching websites
        
        Returns:
            Dictionary of design principles
        """
        return {
            "color_scheme": "Calming, professional colors (blues, greens, earth tones)",
            "typography": "Clean, readable fonts (16px+ body text)",
            "whitespace": "Generous spacing, not cluttered",
            "imagery": "Professional photos, authentic (not stock)",
            "layout": "Clear hierarchy, easy navigation",
            "mobile": "Mobile-first design approach",
            "speed": "Optimized images, minimal scripts",
            "consistency": "Consistent branding throughout"
        }
    
    @staticmethod
    def analyze_gaps(website_structure: Dict) -> List[Dict]:
        """
        Analyze gaps between current website and industry standards
        
        Args:
            website_structure: Dictionary of existing pages (from analyzer)
            
        Returns:
            List of gaps/missing elements
        """
        gaps = []
        required_pages = CoachingStandards.get_required_pages()
        
        for page_name, requirements in required_pages.items():
            if not website_structure.get(page_name, False):
                gaps.append({
                    "type": "missing_page",
                    "page": page_name,
                    "priority": requirements["priority"],
                    "elements": requirements["elements"],
                    "guidelines": requirements["content_guidelines"]
                })
        
        return gaps
    
    @staticmethod
    def generate_recommendations(analysis_report: Dict) -> List[Dict]:
        """
        Generate specific recommendations based on website analysis
        
        Args:
            analysis_report: Full website analysis report
            
        Returns:
            List of prioritized recommendations
        """
        recommendations = []
        
        # Check structure
        structure = analysis_report.get('structure', {})
        gaps = CoachingStandards.analyze_gaps(structure)
        
        for gap in gaps:
            recommendations.append({
                "priority": gap["priority"],
                "category": "structure",
                "title": f"Add {gap['page'].title()} Page",
                "description": f"Create a professional {gap['page']} page with required elements",
                "elements": gap["elements"],
                "guidelines": gap["guidelines"]
            })
        
        # Check features
        features = analysis_report.get('features', {})
        required_features = CoachingStandards.get_required_features()
        
        if not features.get('contact_form'):
            recommendations.append({
                "priority": "critical",
                "category": "feature",
                "title": "Add Contact Form",
                "description": "Implement working contact form with validation",
                "elements": ["Name field", "Email field", "Message field", "Submit button", "Validation", "Email notification"]
            })
        
        if not features.get('ssl'):
            recommendations.append({
                "priority": "critical",
                "category": "security",
                "title": "Enable SSL/HTTPS",
                "description": "Secure the website with SSL certificate",
                "elements": ["SSL certificate", "HTTPS redirect", "Security headers"]
            })
        
        # Check performance
        performance = analysis_report.get('performance', {})
        if performance.get('load_time_seconds', 0) > 3:
            recommendations.append({
                "priority": "high",
                "category": "performance",
                "title": "Optimize Page Speed",
                "description": "Improve loading time to under 3 seconds",
                "elements": ["Optimize images", "Minify CSS/JS", "Enable caching", "Use CDN"]
            })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: priority_order.get(x['priority'], 4))
        
        return recommendations


if __name__ == "__main__":
    # Test the standards
    print("="*50)
    print("COACHING WEBSITE STANDARDS")
    print("="*50)
    
    print("\n📄 REQUIRED PAGES:")
    for page, details in CoachingStandards.get_required_pages().items():
        print(f"\n{page.upper()} ({details['priority']})")
        for element in details['elements']:
            print(f"  • {element}")
    
    print("\n\n🎨 REQUIRED FEATURES:")
    for feature, details in CoachingStandards.get_required_features().items():
        print(f"\n{feature.upper()} ({details['priority']})")
        print(f"  {details['description']}")
