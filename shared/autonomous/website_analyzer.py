"""
Website Analyzer Module
Analyzes websites to identify existing pages, features, and issues
"""
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set
import asyncio


class WebsiteAnalyzer:
    """Analyzes website structure and content"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.visited_urls: Set[str] = set()
        self.pages: List[Dict] = []
        self.broken_links: List[Dict] = []
        self.missing_features: List[str] = []
        
    async def analyze(self, max_pages: int = 50) -> Dict:
        """
        Perform comprehensive website analysis
        
        Returns:
            Dict containing analysis results
        """
        print(f"🔍 Analyzing website: {self.base_url}")
        
        # Crawl website
        await self._crawl_site(self.base_url, max_pages)
        
        # Analyze structure
        structure = self._analyze_structure()
        
        # Check for common features
        features = self._check_features()
        
        # Analyze performance
        performance = await self._check_performance()
        
        # Generate report
        report = {
            "url": self.base_url,
            "pages_found": len(self.pages),
            "pages": self.pages,
            "structure": structure,
            "features": features,
            "broken_links": self.broken_links,
            "performance": performance,
            "missing_features": self.missing_features
        }
        
        print(f"✅ Analysis complete: {len(self.pages)} pages found")
        return report
    
    async def _crawl_site(self, url: str, max_pages: int, depth: int = 0):
        """Recursively crawl website"""
        if depth > 3 or len(self.visited_urls) >= max_pages:
            return
        
        if url in self.visited_urls:
            return
        
        self.visited_urls.add(url)
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, follow_redirects=True)
                
                if response.status_code != 200:
                    self.broken_links.append({
                        "url": url,
                        "status": response.status_code
                    })
                    return
                
                # Parse page
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract page info
                page_info = {
                    "url": url,
                    "title": soup.title.string if soup.title else "No title",
                    "status": response.status_code,
                    "has_forms": len(soup.find_all('form')) > 0,
                    "has_images": len(soup.find_all('img')) > 0,
                    "word_count": len(response.text.split()),
                    "meta_description": self._get_meta_description(soup),
                    "headings": self._extract_headings(soup)
                }
                
                self.pages.append(page_info)
                
                # Find internal links
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    absolute_url = urljoin(url, href)
                    
                    # Only follow internal links
                    if self._is_internal_link(absolute_url):
                        await self._crawl_site(absolute_url, max_pages, depth + 1)
        
        except Exception as e:
            print(f"⚠️ Error crawling {url}: {str(e)}")
            self.broken_links.append({
                "url": url,
                "error": str(e)
            })
    
    def _is_internal_link(self, url: str) -> bool:
        """Check if URL is internal to the website"""
        parsed_base = urlparse(self.base_url)
        parsed_url = urlparse(url)
        return parsed_base.netloc == parsed_url.netloc
    
    def _get_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta['content'] if meta and meta.get('content') else "No description"
    
    def _extract_headings(self, soup: BeautifulSoup) -> Dict:
        """Extract heading structure"""
        return {
            "h1": len(soup.find_all('h1')),
            "h2": len(soup.find_all('h2')),
            "h3": len(soup.find_all('h3'))
        }
    
    def _analyze_structure(self) -> Dict:
        """Analyze website structure"""
        page_types = {
            "homepage": False,
            "about": False,
            "services": False,
            "contact": False,
            "blog": False,
            "testimonials": False,
            "pricing": False
        }
        
        for page in self.pages:
            url_lower = page['url'].lower()
            title_lower = page['title'].lower()
            
            if url_lower == self.base_url or url_lower == self.base_url + '/':
                page_types['homepage'] = True
            elif 'about' in url_lower or 'about' in title_lower:
                page_types['about'] = True
            elif 'service' in url_lower or 'service' in title_lower:
                page_types['services'] = True
            elif 'contact' in url_lower or 'contact' in title_lower:
                page_types['contact'] = True
            elif 'blog' in url_lower or 'blog' in title_lower:
                page_types['blog'] = True
            elif 'testimonial' in url_lower or 'testimonial' in title_lower or 'review' in url_lower:
                page_types['testimonials'] = True
            elif 'pricing' in url_lower or 'price' in url_lower:
                page_types['pricing'] = True
        
        return page_types
    
    def _check_features(self) -> Dict:
        """Check for common website features"""
        features = {
            "contact_form": False,
            "images": False,
            "responsive": "unknown",
            "ssl": self.base_url.startswith('https'),
            "meta_descriptions": 0,
            "total_pages": len(self.pages)
        }
        
        for page in self.pages:
            if page['has_forms']:
                features['contact_form'] = True
            if page['has_images']:
                features['images'] = True
            if page['meta_description'] != "No description":
                features['meta_descriptions'] += 1
        
        return features
    
    async def _check_performance(self) -> Dict:
        """Check basic performance metrics"""
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                import time
                start = time.time()
                response = await client.get(self.base_url)
                load_time = time.time() - start
                
                return {
                    "load_time_seconds": round(load_time, 2),
                    "page_size_kb": round(len(response.content) / 1024, 2),
                    "status": "good" if load_time < 3 else "needs_improvement"
                }
        except Exception as e:
            return {
                "error": str(e),
                "status": "error"
            }


async def analyze_website(url: str) -> Dict:
    """
    Convenience function to analyze a website
    
    Args:
        url: Website URL to analyze
        
    Returns:
        Analysis report dictionary
    """
    analyzer = WebsiteAnalyzer(url)
    return await analyzer.analyze()


if __name__ == "__main__":
    # Test the analyzer
    import sys
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://example.com"
    
    report = asyncio.run(analyze_website(url))
    
    print("\n" + "="*50)
    print("WEBSITE ANALYSIS REPORT")
    print("="*50)
    print(f"\nURL: {report['url']}")
    print(f"Pages Found: {report['pages_found']}")
    print(f"\nStructure:")
    for page_type, exists in report['structure'].items():
        status = "✅" if exists else "❌"
        print(f"  {status} {page_type.title()}")
    print(f"\nFeatures:")
    for feature, value in report['features'].items():
        print(f"  • {feature}: {value}")
    print(f"\nBroken Links: {len(report['broken_links'])}")
    if report['broken_links']:
        for link in report['broken_links'][:5]:
            print(f"  ❌ {link['url']}")
