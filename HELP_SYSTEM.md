# Help System Documentation

## Overview

A comprehensive help documentation system has been implemented for the Memory Buffer Comparison Application. The system extracts documentation from `@help` tags embedded in source code and generates a modern, indexed HTML help system.

## Quick Start

### Generate Help Documentation

**Windows:**
```bash
build_help.bat
```

**Linux/Mac:**
```bash
chmod +x build_help.sh
./build_help.sh
```

**Direct Python:**
```bash
python scripts/build_help.py
```

### View Help

Open `docs/help/index.html` in your web browser.

## Help Tag System

### Tag Format

Help tags are embedded in Python docstrings and comments using the format:
```
@help.<tag_type> <content>
```

### Available Tags

#### Required Tags
- **`@help.category`** - Categorizes the topic (e.g., "Memory Strategies", "Configuration")
- **`@help.title`** - Sets the topic title
- **`@help.description`** - Provides detailed description

#### Optional Tags
- **`@help.example`** - Code examples (can be used multiple times)
- **`@help.performance`** - Performance characteristics
- **`@help.use_case`** - When to use this feature
- **`@help.requirements`** - Dependencies or requirements

### Usage Examples

#### Module-Level Documentation
```python
"""
Module description.

@help.category Memory Strategies
@help.title FIFO Memory Strategy
@help.description First-In-First-Out sliding window memory buffer.
@help.example
    memory = FIFOMemory(window_size=5)
    memory.add_message(Message(role="user", content="Hello"))
@help.performance O(1) add and retrieve operations.
@help.use_case Best for short conversations.
"""
```

#### Class Documentation
```python
class MyClass:
    """
    Class description.
    
    @help.title My Class
    @help.description This class does something useful.
    """
    def __init__(self):
        # @help.description This field stores important data
        self.data = None
```

#### Function Documentation
```python
def my_function():
    """
    Function description.
    
    @help.title My Function
    @help.description This function performs an operation.
    @help.example
        result = my_function()
        print(result)
    """
    pass
```

## Generated Help Structure

The help system generates:

1. **Index Page** (`index.html`) - Main entry point with search and category overview
2. **Category Pages** (`category_*.html`) - Lists all topics in a category
3. **Topic Pages** (`topic_*.html`) - Individual topic documentation
4. **Search Index** (`search_index.json`) - JSON index for client-side search

## Features

### Search Functionality
- Full-text search across all topics
- Real-time results as you type
- Highlights matching topics by title, description, or category

### Navigation
- Breadcrumb navigation
- Category-based browsing
- Quick links to common topics
- Cross-references between related topics

### Modern UI
- Responsive design (mobile-friendly)
- Clean, modern styling
- Syntax-highlighted code examples
- Color-coded information boxes

## File Locations

- **Parser**: `scripts/help_parser.py` - Extracts help tags from source
- **Generator**: `scripts/help_generator.py` - Generates HTML documentation
- **Build Script**: `scripts/build_help.py` - Main build entry point
- **Output**: `docs/help/` - Generated HTML files
- **Documentation**: `docs/HELP_README.md` - This file

## Customization

### Styling
Edit the `_get_css()` method in `scripts/help_generator.py` to customize:
- Colors and themes
- Layout and spacing
- Typography
- Responsive breakpoints

### Functionality
Edit the `_get_javascript()` method in `scripts/help_generator.py` to customize:
- Search behavior
- Navigation logic
- Interactive features

### Templates
Modify the HTML generation methods in `scripts/help_generator.py`:
- `_generate_index()` - Main index page
- `_generate_category_page()` - Category listing pages
- `_generate_topic_page()` - Individual topic pages

## Current Help Topics

The system currently documents:

1. **Configuration** - Application settings and configuration
2. **Memory Strategies** - FIFO, Priority, and Hybrid memory implementations
3. **Memory System** - Base memory interface and data models
4. **LLM Integration** - LLM provider and embedding model wrappers
5. **Utilities** - Token counting and utility functions
6. **Application** - Web application interface

## Best Practices

1. **Always include category and title** - Makes topics easy to find
2. **Write clear descriptions** - Explain what, why, and how
3. **Provide examples** - Code examples help users understand usage
4. **Document parameters** - Use inline comments for field documentation
5. **Keep it concise** - Focus on essential information

## Troubleshooting

### No topics found
- Ensure `@help.category` and `@help.title` tags are present
- Check that source files are in the `src/` directory
- Verify Python files are valid (no syntax errors)

### Missing topics
- Check that docstrings contain help tags
- Verify tag format is correct (`@help.tag content`)
- Ensure tags are in triple-quoted docstrings

### Build errors
- Check Python version (3.7+ required)
- Verify all dependencies are installed
- Check file permissions for output directory

## Future Enhancements

Potential improvements:
- PDF export functionality
- Multi-language support
- Version-specific documentation
- API reference generation
- Integration with CI/CD pipelines
