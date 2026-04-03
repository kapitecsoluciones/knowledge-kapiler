# Knowledge Kapiler 🧠

An AgentSkill for building and maintaining personal knowledge bases with LLMs.

Inspired by [Andrej Karpathy's tweet](https://x.com/karpathy/status/1907839024712364360) on using LLMs to compile structured wikis from raw sources.

## What It Does

1. **Ingest** — Drop PDFs, URLs, screenshots, notes into `raw/`
2. **Compile** — LLM extracts knowledge into structured wiki articles
3. **Query** — Ask questions, get answers from your accumulated knowledge
4. **Lint** — Health checks find inconsistencies, stale data, missing links

## Quick Start

### For OpenClaw Users

1. Copy the `skills/knowledge-kapiler/` folder to your workspace
2. Create the directory structure:

```bash
mkdir -p raw/{articles,papers,screenshots,notes}
mkdir -p knowledge/{concepts,people,projects,decisions,resources}
```

3. Start dropping content into `raw/` and ask your agent to compile it

### Standalone Scripts

```bash
# Ingest a URL
python scripts/ingest-url.py https://example.com/article

# Ingest a PDF
python scripts/ingest-pdf.py document.pdf

# Run lint checks
python scripts/lint.py --knowledge-dir knowledge/
```

## Directory Structure

```
workspace/
├── raw/                      # Unprocessed sources
│   ├── articles/             # Web articles
│   ├── papers/               # PDFs, research
│   ├── screenshots/          # Images
│   └── notes/                # Raw text
├── knowledge/                # Compiled wiki
│   ├── _index.md             # Master index
│   ├── concepts/             # Topic articles
│   ├── people/               # Person profiles
│   ├── projects/             # Project docs
│   ├── decisions/            # Decision log
│   └── resources/            # Curated links
```

## Article Templates

The skill uses consistent templates for different article types:

- **Concept** — Topic articles with summary, details, related links
- **Person** — Contact profiles with notes and interaction history
- **Project** — Status, decisions, people, links
- **Decision** — Context, options, rationale, consequences

See `SKILL.md` for full templates.

## Cron Setup

For automatic maintenance, add a daily cron job:

```json
{
  "schedule": { "kind": "cron", "expr": "0 3 * * *", "tz": "America/Mexico_City" },
  "payload": { 
    "kind": "agentTurn", 
    "message": "Run knowledge-kapiler maintenance: compile unprocessed raw/, run lint, update indexes.",
    "model": "anthropic/claude-sonnet-4-6"
  },
  "sessionTarget": "isolated"
}
```

## Philosophy

- **Raw is forever** — Never delete original sources
- **Wiki is maintained** — The LLM writes and updates articles, you rarely edit directly
- **Everything traces back** — Facts cite their sources in `raw/`
- **Incremental** — Process new items only, don't recompile everything

## Requirements

- Python 3.9+
- For PDF ingestion: `pip install pymupdf` (optional)
- For OpenClaw: Any recent version with `memory_search`

## License

MIT — Use it, modify it, share it.

## Attribution

Concept by [Andrej Karpathy](https://x.com/karpathy). Implementation by [Kapitec](https://kapitec.pro).
