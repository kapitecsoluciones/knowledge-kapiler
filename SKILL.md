# Knowledge Kapiler

Build and maintain a personal knowledge base from raw sources. Inspired by [Andrej Karpathy's LLM Knowledge Bases workflow](https://x.com/karpathy/status/1907839024712364360).

## When to Use

- User drops a PDF, article link, screenshot, or raw notes
- User asks to "add this to the knowledge base" or "remember this"
- User asks questions that should be answered from accumulated knowledge
- Scheduled maintenance (daily lint, compile, index)

## Directory Structure

```
workspace/
├── raw/                      # Unprocessed sources (user drops files here)
│   ├── articles/             # Web articles, blog posts
│   ├── papers/               # PDFs, research papers
│   ├── screenshots/          # Images with text/diagrams
│   └── notes/                # Raw pastes, voice transcripts
├── knowledge/                # Compiled wiki (LLM maintains this)
│   ├── _index.md             # Master index, auto-maintained
│   ├── _backlinks.md         # Backlink registry
│   ├── concepts/             # Topic articles
│   ├── people/               # Person profiles
│   ├── projects/             # Project status & history
│   ├── decisions/            # Decision log with context
│   └── resources/            # Curated external links
└── memory/                   # Session dailies (unchanged)
```

## Workflow

### 1. Ingest (raw/ → processing)

When user provides source material:

1. **Identify type**: PDF, URL, image, or text
2. **Extract content**:
   - PDF: Use `scripts/ingest-pdf.py` or read directly if text-based
   - URL: Use `scripts/ingest-url.py` or `web_fetch`
   - Image: Use `image` tool to extract text/concepts
   - Text: Use directly
3. **Save to raw/**: Preserve original with metadata header
4. **Trigger compile**: Process into knowledge/

### 2. Compile (raw/ → knowledge/)

For each unprocessed item in raw/:

1. **Analyze content**: Extract key concepts, entities, facts
2. **Find or create articles**: Match to existing knowledge/ articles or create new
3. **Update articles**: Add new information with source attribution
4. **Update indexes**: Refresh _index.md and _backlinks.md
5. **Mark processed**: Add `processed: true` to raw file frontmatter

### 3. Query (knowledge/ → response)

When user asks a question:

1. **Search knowledge/**: Use `memory_search` or grep for relevant articles
2. **Load context**: Read relevant articles (respect token limits)
3. **Synthesize answer**: Combine knowledge with reasoning
4. **Cite sources**: Reference which articles informed the answer

### 4. Lint (health check)

Run periodically via cron:

1. **Find orphans**: Articles with no backlinks
2. **Find contradictions**: Conflicting facts across articles
3. **Find stale data**: Old info that may need refresh
4. **Suggest connections**: Potential links between unconnected concepts
5. **Report**: Create lint-report.md or notify user

## Article Templates

### Concept (`knowledge/concepts/*.md`)

```markdown
---
title: [Concept Name]
aliases: [alternative names]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [list of raw/ files]
---

# [Concept Name]

## Summary
[2-3 sentence overview]

## Details
[Main content]

## Related
- [[other-concept]]
- [[relevant-person]]

## Sources
- raw/articles/source-file.md
```

### Person (`knowledge/people/*.md`)

```markdown
---
title: [Full Name]
role: [Role/Title]
company: [Company]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---

# [Full Name]

## Overview
[Who they are, relationship to user]

## Contact
- Email: 
- Phone:
- LinkedIn:

## Notes
[Relevant context, preferences, history]

## Interactions
- YYYY-MM-DD: [Note about interaction]

## Related
- [[company]]
- [[project]]
```

### Project (`knowledge/projects/*.md`)

```markdown
---
title: [Project Name]
status: [active|paused|completed|abandoned]
started: YYYY-MM-DD
updated: YYYY-MM-DD
---

# [Project Name]

## Status
[Current state in 1-2 sentences]

## Overview
[What it is, goals]

## Key Decisions
- YYYY-MM-DD: [Decision and rationale]

## People
- [[person]]: [role in project]

## Links
- Repo: 
- Live:
- Docs:

## History
[Timeline of major events]
```

### Decision (`knowledge/decisions/*.md`)

```markdown
---
title: [Decision Title]
date: YYYY-MM-DD
status: [proposed|decided|superseded]
superseded_by: [link if applicable]
---

# [Decision Title]

## Context
[Why this decision was needed]

## Options Considered
1. [Option A]: [pros/cons]
2. [Option B]: [pros/cons]

## Decision
[What was decided]

## Rationale
[Why this option was chosen]

## Consequences
[What changed as a result]
```

## Commands

The skill responds to these patterns:

| Trigger | Action |
|---------|--------|
| "Add this to knowledge base" + content | Ingest and compile |
| "What do I know about X?" | Query knowledge/ |
| "Update [article] with..." | Edit specific article |
| "Knowledge lint" / "Check knowledge health" | Run lint |
| "Show knowledge index" | Display _index.md |
| "Compile knowledge" | Process all unprocessed raw/ |

## Cron Setup

Add to HEARTBEAT.md or create dedicated cron:

```
# Daily at 3 AM - knowledge maintenance (Sonnet)
{
  "schedule": { "kind": "cron", "expr": "0 3 * * *", "tz": "America/Mexico_City" },
  "payload": { 
    "kind": "agentTurn", 
    "message": "Run knowledge-kapiler maintenance: compile any unprocessed raw/, run lint, update indexes. Report issues only.",
    "model": "anthropic/claude-sonnet-4-6"
  },
  "sessionTarget": "isolated"
}
```

## Constraints

- **Never delete raw/**: Original sources are preserved forever
- **Atomic updates**: One article per edit, avoid bulk rewrites
- **Source attribution**: Every fact should trace to a raw/ file
- **Token budget**: Keep individual articles under 4K tokens
- **Incremental**: Process new items only, don't recompile everything

## Examples

### Ingesting a web article

User: "Add this to knowledge base: https://example.com/article-about-topic"

1. Fetch URL with `web_fetch`
2. Save to `raw/articles/YYYY-MM-DD-article-title.md` with frontmatter
3. Extract concepts → update/create `knowledge/concepts/topic.md`
4. Update `knowledge/_index.md`
5. Confirm: "Added to knowledge base. Created/updated: [[topic]]"

### Answering a question

User: "What do I know about Rogelio's business?"

1. Search: `grep -r "Rogelio" knowledge/`
2. Find: `knowledge/people/rogelio-rendon.md`, `knowledge/projects/food-trailers.md`
3. Read articles, synthesize answer
4. Respond with citations

### Lint report

```markdown
# Knowledge Lint Report - 2026-04-03

## Orphan Articles (no backlinks)
- concepts/old-topic.md — consider linking or archiving

## Potential Contradictions
- projects/safetravel.md says "launched March 2026"
- decisions/safetravel-launch.md says "planned April 2026"

## Stale (>30 days no update)
- people/old-contact.md — still relevant?

## Suggested Connections
- concepts/llm-agents.md could link to projects/openclaw.md
```

## Attribution

Inspired by Andrej Karpathy's tweet on LLM Knowledge Bases (April 2026).
