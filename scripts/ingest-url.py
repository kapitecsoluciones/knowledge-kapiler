#!/usr/bin/env python3
"""
Ingest a URL into the knowledge base raw/ directory.
Converts web page to markdown with frontmatter.

Usage: python ingest-url.py <url> [--output raw/articles/]
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:60]

def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    parsed = urlparse(url)
    return parsed.netloc.replace('www.', '')

def create_frontmatter(url: str, title: str) -> str:
    """Create YAML frontmatter for the article."""
    now = datetime.now().strftime('%Y-%m-%d')
    domain = extract_domain(url)
    return f"""---
source_url: {url}
source_domain: {domain}
title: "{title}"
ingested: {now}
processed: false
type: article
---

"""

def main():
    parser = argparse.ArgumentParser(description='Ingest URL to knowledge base')
    parser.add_argument('url', help='URL to ingest')
    parser.add_argument('--output', '-o', default='raw/articles/', help='Output directory')
    parser.add_argument('--title', '-t', help='Override title')
    parser.add_argument('--content', '-c', help='Pre-fetched content (markdown)')
    args = parser.parse_args()

    # Generate filename
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    title = args.title or extract_domain(args.url)
    slug = slugify(title)
    filename = f"{date_prefix}-{slug}.md"
    
    # Ensure output directory exists
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    
    # Create content
    frontmatter = create_frontmatter(args.url, title)
    
    if args.content:
        content = args.content
    else:
        content = f"# {title}\n\n> Source: {args.url}\n\n[Content not yet fetched - use web_fetch tool]"
    
    full_content = frontmatter + content
    
    # Write file
    output_path.write_text(full_content, encoding='utf-8')
    print(f"Created: {output_path}")
    return str(output_path)

if __name__ == '__main__':
    main()
