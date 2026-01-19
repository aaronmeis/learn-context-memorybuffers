"""
Help tag parser for extracting documentation from source code.

@help.category Development Tools
@help.title Help Parser
@help.description Extracts @help tags from source code and builds structured documentation.
"""
import re
import ast
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class HelpTag:
    """Represents a help tag found in source code."""
    tag_type: str  # e.g., "category", "title", "description", "example"
    content: str
    line_number: int
    file_path: str
    context: str = ""  # Class/function name this tag belongs to


@dataclass
class HelpTopic:
    """Represents a complete help topic with all its tags."""
    file_path: str
    category: str = ""
    title: str = ""
    description: str = ""
    examples: List[str] = field(default_factory=list)
    performance: str = ""
    use_case: str = ""
    requirements: str = ""
    line_number: int = 0
    context: str = ""
    fields: List[Dict[str, str]] = field(default_factory=list)  # For class fields/attributes


class HelpParser:
    """Parser for extracting help tags from Python source files."""
    
    def __init__(self, source_dir: str = "src"):
        self.source_dir = Path(source_dir)
        self.help_pattern = re.compile(r'@help\.(\w+)\s+(.+?)(?=\n|@help|$)')
        self.comment_pattern = re.compile(r'#\s*@help\.(\w+)\s+(.+?)(?=\n|#\s*@help|$)')
    
    def parse_file(self, file_path: Path) -> List[HelpTopic]:
        """Parse a single Python file and extract all help topics."""
        topics = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Warning: Could not read {file_path}: {e}")
            return topics
        
        # Find all help tags in docstrings
        docstring_tags = self._extract_docstring_tags(content, str(file_path))
        
        # Find all help tags in comments
        comment_tags = self._extract_comment_tags(content, str(file_path))
        
        # Group tags by context (module, class, function)
        all_tags = docstring_tags + comment_tags
        
        # Parse AST to get context information
        try:
            tree = ast.parse(content)
            context_map = self._build_context_map(tree)
        except SyntaxError:
            context_map = {}
        
        # Group tags into topics
        current_topic = None
        for tag in sorted(all_tags, key=lambda t: t.line_number):
            # Check if this starts a new topic (module-level or class/function docstring)
            if tag.tag_type == "category" or (current_topic is None):
                if current_topic and current_topic.title:
                    topics.append(current_topic)
                current_topic = HelpTopic(
                    file_path=str(file_path),
                    line_number=tag.line_number,
                    context=context_map.get(tag.line_number, "")
                )
            
            # Add tag to current topic
            if current_topic:
                self._add_tag_to_topic(current_topic, tag)
        
        # Add last topic
        if current_topic and current_topic.title:
            topics.append(current_topic)
        
        return topics
    
    def _extract_docstring_tags(self, content: str, file_path: str) -> List[HelpTag]:
        """Extract help tags from docstrings."""
        tags = []
        lines = content.split('\n')
        
        in_docstring = False
        docstring_content = []
        docstring_start_line = 0
        
        for i, line in enumerate(lines, 1):
            # Check for docstring start
            if '"""' in line or "'''" in line:
                if not in_docstring:
                    in_docstring = True
                    docstring_start_line = i
                    docstring_content = [line]
                else:
                    # End of docstring
                    docstring_content.append(line)
                    docstring_text = '\n'.join(docstring_content)
                    
                    # Extract tags from docstring
                    for match in self.help_pattern.finditer(docstring_text):
                        tag_type = match.group(1)
                        tag_content = match.group(2).strip()
                        tags.append(HelpTag(
                            tag_type=tag_type,
                            content=tag_content,
                            line_number=docstring_start_line,
                            file_path=file_path
                        ))
                    
                    in_docstring = False
                    docstring_content = []
            elif in_docstring:
                docstring_content.append(line)
        
        return tags
    
    def _extract_comment_tags(self, content: str, file_path: str) -> List[HelpTag]:
        """Extract help tags from inline comments."""
        tags = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Look for comment-based help tags
            for match in self.comment_pattern.finditer(line):
                tag_type = match.group(1)
                tag_content = match.group(2).strip()
                tags.append(HelpTag(
                    tag_type=tag_type,
                    content=tag_content,
                    line_number=i,
                    file_path=file_path
                ))
        
        return tags
    
    def _build_context_map(self, tree: ast.AST) -> Dict[int, str]:
        """Build a map of line numbers to context (class/function names)."""
        context_map = {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                context_name = node.name
                if isinstance(node, ast.ClassDef):
                    context_name = f"class {context_name}"
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    context_name = f"function {context_name}"
                
                # Map all lines in this node to its context
                for line_no in range(node.lineno, getattr(node, 'end_lineno', node.lineno) + 1):
                    context_map[line_no] = context_name
        
        return context_map
    
    def _add_tag_to_topic(self, topic: HelpTopic, tag: HelpTag):
        """Add a help tag to a topic."""
        if tag.tag_type == "category":
            topic.category = tag.content
        elif tag.tag_type == "title":
            topic.title = tag.content
        elif tag.tag_type == "description":
            topic.description += tag.content + " "
        elif tag.tag_type == "example":
            topic.examples.append(tag.content)
        elif tag.tag_type == "performance":
            topic.performance = tag.content
        elif tag.tag_type == "use_case":
            topic.use_case = tag.content
        elif tag.tag_type == "requirements":
            topic.requirements = tag.content
    
    def parse_all(self) -> List[HelpTopic]:
        """Parse all Python files in source directory."""
        all_topics = []
        
        for py_file in self.source_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            
            topics = self.parse_file(py_file)
            all_topics.extend(topics)
        
        return all_topics


if __name__ == "__main__":
    parser = HelpParser()
    topics = parser.parse_all()
    
    print(f"Found {len(topics)} help topics")
    for topic in topics:
        print(f"\n{topic.category} - {topic.title}")
        print(f"  File: {topic.file_path}")
        print(f"  Description: {topic.description[:100]}...")
