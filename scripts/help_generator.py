"""
HTML help generator for creating indexed help documentation.

@help.category Development Tools
@help.title Help Generator
@help.description Generates modern, indexed HTML help documentation from parsed help tags.
"""
from pathlib import Path
from typing import List
import json
import sys

# Import HelpTopic from help_parser
sys.path.insert(0, str(Path(__file__).parent))
from help_parser import HelpTopic


class HelpGenerator:
    """Generates HTML help documentation."""
    
    def __init__(self, output_dir: str = "docs/help"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(self, topics: List[HelpTopic]):
        """Generate HTML help documentation from topics."""
        # Group topics by category
        categories = {}
        for topic in topics:
            category = topic.category or "General"
            if category not in categories:
                categories[category] = []
            categories[category].append(topic)
        
        # Generate index
        index_html = self._generate_index(categories, topics)
        
        # Generate category pages
        category_pages = {}
        for category, cat_topics in categories.items():
            category_html = self._generate_category_page(category, cat_topics)
            category_slug = self._slugify(category)
            category_pages[category_slug] = category_html
        
        # Generate individual topic pages
        topic_pages = {}
        for topic in topics:
            topic_html = self._generate_topic_page(topic, topics)
            topic_slug = self._slugify(topic.title or topic.file_path)
            topic_pages[topic_slug] = topic_html
        
        # Write index
        (self.output_dir / "index.html").write_text(index_html, encoding='utf-8')
        
        # Write category pages
        for slug, html in category_pages.items():
            (self.output_dir / f"category_{slug}.html").write_text(html, encoding='utf-8')
        
        # Write topic pages
        for slug, html in topic_pages.items():
            (self.output_dir / f"topic_{slug}.html").write_text(html, encoding='utf-8')
        
        # Generate search index JSON
        search_index = self._generate_search_index(topics)
        (self.output_dir / "search_index.json").write_text(
            json.dumps(search_index, indent=2), encoding='utf-8'
        )
        
        print(f"Generated help documentation in {self.output_dir}")
        print(f"  - {len(categories)} categories")
        print(f"  - {len(topics)} topics")
    
    def _generate_index(self, categories: dict, all_topics: List[HelpTopic]) -> str:
        """Generate main index page."""
        categories_html = ""
        for category, topics in sorted(categories.items()):
            category_slug = self._slugify(category)
            categories_html += f"""
            <div class="category-card">
                <h2><a href="category_{category_slug}.html">{category}</a></h2>
                <p>{len(topics)} topics</p>
                <ul class="topic-list">
            """
            for topic in topics[:5]:  # Show first 5
                topic_slug = self._slugify(topic.title or topic.file_path)
                categories_html += f'<li><a href="topic_{topic_slug}.html">{topic.title or "Untitled"}</a></li>'
            if len(topics) > 5:
                categories_html += f'<li><em>... and {len(topics) - 5} more</em></li>'
            categories_html += "</ul></div>"
        
        return self._get_base_html(f"""
            <div class="hero">
                <h1>🧠 Memory Buffer System Help</h1>
                <p class="subtitle">Complete documentation for the Memory Buffer Comparison Application</p>
                <div class="search-box">
                    <input type="text" id="searchInput" placeholder="Search help topics..." />
                    <div id="searchResults" class="search-results"></div>
                </div>
            </div>
            
            <div class="categories-grid">
                {categories_html}
            </div>
            
            <div class="quick-links">
                <h2>Quick Links</h2>
                <div class="links-grid">
                    <a href="category_Memory Strategies.html" class="quick-link">
                        <span class="icon">🧠</span>
                        <span>Memory Strategies</span>
                    </a>
                    <a href="category_Configuration.html" class="quick-link">
                        <span class="icon">⚙️</span>
                        <span>Configuration</span>
                    </a>
                    <a href="category_LLM Integration.html" class="quick-link">
                        <span class="icon">🤖</span>
                        <span>LLM Integration</span>
                    </a>
                    <a href="category_Application.html" class="quick-link">
                        <span class="icon">🌐</span>
                        <span>Web Application</span>
                    </a>
                </div>
            </div>
        """, "Help Index")
    
    def _generate_category_page(self, category: str, topics: List[HelpTopic]) -> str:
        """Generate category page."""
        topics_html = ""
        for topic in topics:
            topic_slug = self._slugify(topic.title or topic.file_path)
            topics_html += f"""
            <div class="topic-card">
                <h3><a href="topic_{topic_slug}.html">{topic.title or "Untitled"}</a></h3>
                <p class="description">{topic.description[:200]}...</p>
                <div class="meta">
                    <span class="file">{Path(topic.file_path).name}</span>
                    {f'<span class="context">{topic.context}</span>' if topic.context else ''}
                </div>
            </div>
            """
        
        return self._get_base_html(f"""
            <nav class="breadcrumb">
                <a href="index.html">Home</a> / <span>{category}</span>
            </nav>
            
            <h1>{category}</h1>
            <p class="category-description">Browse all topics in this category</p>
            
            <div class="topics-grid">
                {topics_html}
            </div>
        """, f"{category} - Help")
    
    def _generate_topic_page(self, topic: HelpTopic, all_topics: List[HelpTopic]) -> str:
        """Generate individual topic page."""
        examples_html = ""
        if topic.examples:
            examples_html = '<h3>Examples</h3><div class="examples">'
            for i, example in enumerate(topic.examples, 1):
                examples_html += f"""
                <div class="example">
                    <h4>Example {i}</h4>
                    <pre><code>{self._escape_html(example)}</code></pre>
                </div>
                """
            examples_html += "</div>"
        
        sections_html = ""
        if topic.performance:
            sections_html += f'<div class="info-box performance"><h3>⚡ Performance</h3><p>{topic.performance}</p></div>'
        if topic.use_case:
            sections_html += f'<div class="info-box use-case"><h3>🎯 Use Case</h3><p>{topic.use_case}</p></div>'
        if topic.requirements:
            sections_html += f'<div class="info-box requirements"><h3>📦 Requirements</h3><p>{topic.requirements}</p></div>'
        
        return self._get_base_html(f"""
            <nav class="breadcrumb">
                <a href="index.html">Home</a> / 
                <a href="category_{self._slugify(topic.category or 'General')}.html">{topic.category or 'General'}</a> / 
                <span>{topic.title}</span>
            </nav>
            
            <article class="topic-content">
                <header>
                    <h1>{topic.title or "Untitled Topic"}</h1>
                    <div class="topic-meta">
                        <span class="category-badge">{topic.category or "General"}</span>
                        <span class="file-path">{topic.file_path}</span>
                        {f'<span class="context">{topic.context}</span>' if topic.context else ''}
                    </div>
                </header>
                
                <div class="description">
                    <p>{topic.description.strip()}</p>
                </div>
                
                {examples_html}
                
                {sections_html}
            </article>
        """, f"{topic.title} - Help")
    
    def _generate_search_index(self, topics: List[HelpTopic]) -> dict:
        """Generate search index for client-side search."""
        index = {
            "topics": []
        }
        
        for topic in topics:
            index["topics"].append({
                "title": topic.title or "Untitled",
                "category": topic.category or "General",
                "description": topic.description,
                "file": topic.file_path,
                "slug": self._slugify(topic.title or topic.file_path)
            })
        
        return index
    
    def _get_base_html(self, content: str, title: str) -> str:
        """Get base HTML template with styles and scripts."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        {self._get_css()}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
    <script>
        {self._get_javascript()}
    </script>
</body>
</html>"""
    
    def _get_css(self) -> str:
        """Get CSS styles."""
        return """
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f7fa;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .hero {
            text-align: center;
            padding: 3rem 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 12px;
            margin-bottom: 3rem;
        }
        
        .hero h1 {
            font-size: 3rem;
            margin-bottom: 1rem;
        }
        
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
        }
        
        .search-box {
            margin-top: 2rem;
            position: relative;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }
        
        #searchInput {
            width: 100%;
            padding: 1rem;
            font-size: 1rem;
            border: none;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .search-results {
            position: absolute;
            top: 100%;
            left: 0;
            right: 0;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-top: 0.5rem;
            max-height: 400px;
            overflow-y: auto;
            display: none;
        }
        
        .search-results.active {
            display: block;
        }
        
        .search-result-item {
            padding: 1rem;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .search-result-item:hover {
            background: #f5f7fa;
        }
        
        .search-result-item h4 {
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .categories-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        
        .category-card {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .category-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        .category-card h2 {
            color: #667eea;
            margin-bottom: 1rem;
        }
        
        .category-card h2 a {
            text-decoration: none;
            color: inherit;
        }
        
        .topic-list {
            list-style: none;
        }
        
        .topic-list li {
            padding: 0.5rem 0;
            border-bottom: 1px solid #eee;
        }
        
        .topic-list li:last-child {
            border-bottom: none;
        }
        
        .topic-list a {
            color: #333;
            text-decoration: none;
            transition: color 0.2s;
        }
        
        .topic-list a:hover {
            color: #667eea;
        }
        
        .quick-links {
            margin-top: 3rem;
        }
        
        .links-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        
        .quick-link {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-decoration: none;
            color: #333;
            display: flex;
            align-items: center;
            gap: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .quick-link:hover {
            transform: translateY(-2px);
        }
        
        .quick-link .icon {
            font-size: 2rem;
        }
        
        .breadcrumb {
            margin-bottom: 2rem;
            color: #666;
        }
        
        .breadcrumb a {
            color: #667eea;
            text-decoration: none;
        }
        
        .topics-grid {
            display: grid;
            gap: 1.5rem;
        }
        
        .topic-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .topic-card h3 {
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        
        .topic-card h3 a {
            text-decoration: none;
            color: inherit;
        }
        
        .topic-card .meta {
            margin-top: 1rem;
            font-size: 0.9rem;
            color: #666;
        }
        
        .topic-card .meta span {
            margin-right: 1rem;
        }
        
        .topic-content {
            background: white;
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .topic-content header {
            margin-bottom: 2rem;
            padding-bottom: 1rem;
            border-bottom: 2px solid #eee;
        }
        
        .topic-content h1 {
            color: #333;
            margin-bottom: 1rem;
        }
        
        .topic-meta {
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }
        
        .category-badge {
            background: #667eea;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 0.9rem;
        }
        
        .file-path {
            color: #666;
            font-family: monospace;
            font-size: 0.9rem;
        }
        
        .description {
            margin: 2rem 0;
            font-size: 1.1rem;
            line-height: 1.8;
        }
        
        .examples {
            margin: 2rem 0;
        }
        
        .examples h3 {
            margin-bottom: 1rem;
            color: #333;
        }
        
        .example {
            margin-bottom: 1.5rem;
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .example h4 {
            margin-bottom: 0.5rem;
            color: #667eea;
        }
        
        .example pre {
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 1rem;
            border-radius: 4px;
            overflow-x: auto;
        }
        
        .example code {
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }
        
        .info-box {
            margin: 1.5rem 0;
            padding: 1.5rem;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .info-box.performance {
            background: #e8f5e9;
            border-color: #4caf50;
        }
        
        .info-box.use-case {
            background: #e3f2fd;
            border-color: #2196f3;
        }
        
        .info-box.requirements {
            background: #fff3e0;
            border-color: #ff9800;
        }
        
        .info-box h3 {
            margin-bottom: 0.5rem;
            color: #333;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1rem;
            }
            
            .hero h1 {
                font-size: 2rem;
            }
            
            .categories-grid {
                grid-template-columns: 1fr;
            }
        }
        """
    
    def _get_javascript(self) -> str:
        """Get JavaScript for search functionality."""
        return """
        // Load search index
        let searchIndex = null;
        
        fetch('search_index.json')
            .then(response => response.json())
            .then(data => {
                searchIndex = data;
            })
            .catch(err => console.error('Failed to load search index:', err));
        
        // Search functionality
        const searchInput = document.getElementById('searchInput');
        const searchResults = document.getElementById('searchResults');
        
        if (searchInput && searchResults) {
            searchInput.addEventListener('input', function(e) {
                const query = e.target.value.toLowerCase().trim();
                
                if (!query || !searchIndex) {
                    searchResults.classList.remove('active');
                    return;
                }
                
                const results = searchIndex.topics.filter(topic => {
                    return topic.title.toLowerCase().includes(query) ||
                           topic.description.toLowerCase().includes(query) ||
                           topic.category.toLowerCase().includes(query);
                }).slice(0, 10);
                
                if (results.length === 0) {
                    searchResults.innerHTML = '<div class="search-result-item"><p>No results found</p></div>';
                    searchResults.classList.add('active');
                    return;
                }
                
                searchResults.innerHTML = results.map(topic => `
                    <div class="search-result-item" onclick="window.location.href='topic_${topic.slug}.html'">
                        <h4>${topic.title}</h4>
                        <p>${topic.category} - ${topic.description.substring(0, 100)}...</p>
                    </div>
                `).join('');
                
                searchResults.classList.add('active');
            });
            
            // Close search results when clicking outside
            document.addEventListener('click', function(e) {
                if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                    searchResults.classList.remove('active');
                }
            });
        }
        """
    
    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug."""
        import re
        text = text.lower()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '_', text)
        return text.strip('_')
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
