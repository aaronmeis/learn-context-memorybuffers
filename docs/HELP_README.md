# Help Documentation System

This directory contains the generated HTML help documentation for the Memory Buffer Comparison Application.

## Building the Help Documentation

To regenerate the help documentation from source code:

### Windows
```bash
build_help.bat
```

### Linux/Mac
```bash
chmod +x build_help.sh
./build_help.sh
```

### Direct Python
```bash
python scripts/build_help.py
```

## Viewing the Help

Open `docs/help/index.html` in your web browser to view the help documentation.

## Help Tag Format

The help system extracts documentation from `@help` tags in source code. Use these tags in docstrings and comments:

### Module/Class Level Tags
- `@help.category <Category Name>` - Categorizes the topic
- `@help.title <Title>` - Sets the topic title
- `@help.description <Description>` - Provides detailed description

### Additional Tags
- `@help.example <Code Example>` - Code examples
- `@help.performance <Performance Notes>` - Performance characteristics
- `@help.use_case <Use Case Description>` - When to use this feature
- `@help.requirements <Requirements>` - Dependencies or requirements

### Inline Comment Tags
- `# @help.description <Description>` - For field/attribute documentation

## Example Usage

```python
"""
My module documentation.

@help.category Configuration
@help.title My Module
@help.description This module does something useful.
@help.example
    from mymodule import MyClass
    obj = MyClass()
"""
class MyClass:
    """My class documentation."""
    
    def __init__(self):
        # @help.description This field stores important data
        self.data = None
```

## Features

- **Indexed Search**: Full-text search across all help topics
- **Category Navigation**: Browse by category
- **Modern UI**: Responsive design with modern styling
- **Code Examples**: Syntax-highlighted code examples
- **Cross-references**: Links between related topics

## File Structure

- `index.html` - Main help index page
- `category_*.html` - Category listing pages
- `topic_*.html` - Individual topic pages
- `search_index.json` - Search index data

## Customization

To customize the help system:

1. Edit `scripts/help_generator.py` to modify HTML templates
2. Edit CSS in `_get_css()` method for styling
3. Edit JavaScript in `_get_javascript()` method for search behavior
