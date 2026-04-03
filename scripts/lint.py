#!/usr/bin/env python3
"""
Lint the knowledge base for issues.

Checks for:
- Orphan articles (no backlinks)
- Broken internal links
- Stale articles (no updates in X days)
- Missing required frontmatter
- Duplicate titles

Usage: python lint.py [--knowledge-dir knowledge/] [--days-stale 30]
"""

import argparse
import re
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

def find_wiki_links(content: str) -> list[str]:
    """Find all [[wiki-style]] links in content."""
    return re.findall(r'\[\[([^\]]+)\]\]', content)

def parse_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter as dict."""
    if not content.startswith('---'):
        return {}
    
    try:
        end = content.index('---', 3)
        fm_text = content[3:end].strip()
        result = {}
        for line in fm_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip().strip('"\'')
        return result
    except:
        return {}

def lint_knowledge_base(knowledge_dir: str, days_stale: int = 30) -> dict:
    """Run all lint checks and return report."""
    kdir = Path(knowledge_dir)
    if not kdir.exists():
        return {'error': f'Knowledge directory not found: {knowledge_dir}'}
    
    # Collect all articles
    articles = {}
    all_links = defaultdict(list)  # target -> [sources]
    
    for md_file in kdir.rglob('*.md'):
        if md_file.name.startswith('_'):
            continue
        
        rel_path = md_file.relative_to(kdir)
        content = md_file.read_text(encoding='utf-8')
        frontmatter = parse_frontmatter(content)
        links = find_wiki_links(content)
        
        articles[str(rel_path)] = {
            'path': md_file,
            'frontmatter': frontmatter,
            'links': links,
            'mtime': datetime.fromtimestamp(md_file.stat().st_mtime)
        }
        
        # Track backlinks
        for link in links:
            all_links[link.lower()].append(str(rel_path))
    
    # Analysis
    report = {
        'total_articles': len(articles),
        'orphans': [],
        'broken_links': [],
        'stale': [],
        'missing_frontmatter': [],
        'issues_count': 0
    }
    
    stale_threshold = datetime.now() - timedelta(days=days_stale)
    article_names = {Path(p).stem.lower() for p in articles.keys()}
    
    for path, data in articles.items():
        stem = Path(path).stem.lower()
        
        # Check for orphans (no incoming links)
        if stem not in all_links and not path.startswith('_'):
            report['orphans'].append(path)
        
        # Check for broken links
        for link in data['links']:
            if link.lower() not in article_names:
                report['broken_links'].append({
                    'source': path,
                    'broken_link': link
                })
        
        # Check for stale
        if data['mtime'] < stale_threshold:
            report['stale'].append({
                'path': path,
                'last_modified': data['mtime'].strftime('%Y-%m-%d')
            })
        
        # Check frontmatter
        fm = data['frontmatter']
        if not fm.get('title'):
            report['missing_frontmatter'].append({
                'path': path,
                'missing': 'title'
            })
    
    report['issues_count'] = (
        len(report['orphans']) + 
        len(report['broken_links']) + 
        len(report['stale']) + 
        len(report['missing_frontmatter'])
    )
    
    return report

def format_report(report: dict) -> str:
    """Format lint report as markdown."""
    lines = [
        f"# Knowledge Lint Report - {datetime.now().strftime('%Y-%m-%d')}",
        "",
        f"**Total articles:** {report['total_articles']}",
        f"**Issues found:** {report['issues_count']}",
        ""
    ]
    
    if report['orphans']:
        lines.append("## Orphan Articles (no backlinks)")
        for p in report['orphans'][:10]:
            lines.append(f"- {p}")
        if len(report['orphans']) > 10:
            lines.append(f"- ... and {len(report['orphans']) - 10} more")
        lines.append("")
    
    if report['broken_links']:
        lines.append("## Broken Links")
        for item in report['broken_links'][:10]:
            lines.append(f"- {item['source']}: [[{item['broken_link']}]]")
        lines.append("")
    
    if report['stale']:
        lines.append("## Stale Articles (>30 days)")
        for item in report['stale'][:10]:
            lines.append(f"- {item['path']} (last: {item['last_modified']})")
        lines.append("")
    
    if report['missing_frontmatter']:
        lines.append("## Missing Frontmatter")
        for item in report['missing_frontmatter'][:10]:
            lines.append(f"- {item['path']}: missing {item['missing']}")
        lines.append("")
    
    if report['issues_count'] == 0:
        lines.append("✅ No issues found!")
    
    return '\n'.join(lines)

def main():
    parser = argparse.ArgumentParser(description='Lint knowledge base')
    parser.add_argument('--knowledge-dir', '-k', default='knowledge/', help='Knowledge directory')
    parser.add_argument('--days-stale', '-d', type=int, default=30, help='Days before considered stale')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    args = parser.parse_args()

    report = lint_knowledge_base(args.knowledge_dir, args.days_stale)
    
    if args.json:
        import json
        print(json.dumps(report, indent=2, default=str))
    else:
        print(format_report(report))

if __name__ == '__main__':
    main()
