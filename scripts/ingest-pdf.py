#!/usr/bin/env python3
"""
Ingest a PDF into the knowledge base raw/ directory.
Extracts text and creates markdown with frontmatter.

Usage: python ingest-pdf.py <pdf_path> [--output raw/papers/]

Requires: pip install pymupdf (or pypdf2 as fallback)
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:60]

def extract_text_pymupdf(pdf_path: str) -> str:
    """Extract text using PyMuPDF (fitz)."""
    import fitz
    doc = fitz.open(pdf_path)
    text = []
    for page in doc:
        text.append(page.get_text())
    return '\n\n---\n\n'.join(text)

def extract_text_pypdf2(pdf_path: str) -> str:
    """Extract text using PyPDF2 as fallback."""
    from PyPDF2 import PdfReader
    reader = PdfReader(pdf_path)
    text = []
    for page in reader.pages:
        text.append(page.extract_text() or '')
    return '\n\n---\n\n'.join(text)

def extract_text(pdf_path: str) -> str:
    """Try different PDF libraries to extract text."""
    try:
        return extract_text_pymupdf(pdf_path)
    except ImportError:
        pass
    
    try:
        return extract_text_pypdf2(pdf_path)
    except ImportError:
        pass
    
    return "[PDF text extraction failed - install pymupdf or pypdf2]"

def create_frontmatter(pdf_path: str, title: str, page_count: int = 0) -> str:
    """Create YAML frontmatter for the PDF."""
    now = datetime.now().strftime('%Y-%m-%d')
    return f"""---
source_file: {pdf_path}
title: "{title}"
pages: {page_count}
ingested: {now}
processed: false
type: paper
---

"""

def main():
    parser = argparse.ArgumentParser(description='Ingest PDF to knowledge base')
    parser.add_argument('pdf_path', help='Path to PDF file')
    parser.add_argument('--output', '-o', default='raw/papers/', help='Output directory')
    parser.add_argument('--title', '-t', help='Override title (default: filename)')
    args = parser.parse_args()

    pdf_path = Path(args.pdf_path)
    if not pdf_path.exists():
        print(f"Error: {pdf_path} not found", file=sys.stderr)
        sys.exit(1)

    # Generate filename
    date_prefix = datetime.now().strftime('%Y-%m-%d')
    title = args.title or pdf_path.stem
    slug = slugify(title)
    filename = f"{date_prefix}-{slug}.md"
    
    # Ensure output directory exists
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename
    
    # Extract text
    print(f"Extracting text from {pdf_path}...")
    content = extract_text(str(pdf_path))
    
    # Count pages (approximate from content)
    page_count = content.count('---') + 1
    
    # Create full content
    frontmatter = create_frontmatter(str(pdf_path), title, page_count)
    full_content = frontmatter + f"# {title}\n\n" + content
    
    # Write file
    output_path.write_text(full_content, encoding='utf-8')
    print(f"Created: {output_path}")
    return str(output_path)

if __name__ == '__main__':
    main()
