#!/usr/bin/env python3
"""
Build script for generating help documentation.

@help.category Development Tools
@help.title Build Help Script
@help.description Main entry point for building help documentation from source code.
Run this script to generate the complete HTML help system.
"""
import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from help_parser import HelpParser
from help_generator import HelpGenerator


def main():
    """Main build function."""
    print("Parsing help tags from source code...")
    
    # Parse all help tags from both src and web directories
    parser_src = HelpParser(source_dir="src")
    parser_web = HelpParser(source_dir="web")
    
    topics_src = parser_src.parse_all()
    topics_web = parser_web.parse_all()
    
    # Combine topics
    topics = topics_src + topics_web
    
    if not topics:
        print("WARNING: No help topics found. Make sure help tags are present in source files.")
        return 1
    
    print(f"Found {len(topics)} help topics")
    
    # Generate HTML documentation
    print("Generating HTML help documentation...")
    generator = HelpGenerator(output_dir="docs/help")
    generator.generate(topics)
    
    print("\nHelp documentation generated successfully!")
    print(f"Open docs/help/index.html in your browser to view the help system.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
