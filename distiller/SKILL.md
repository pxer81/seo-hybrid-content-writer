---
name: seo-keyword-distiller
description: >
  Use when the user wants to research a keyword, analyze Google SERP competition,
  distill what makes top-ranking content work, or build a content strategy guide
  for any English-language SEO keyword.
  Trigger on requests like "distill keyword", "analyze SERP for", "research keyword",
  "what do top pages do for", "build a content strategy for", "SEO content plan for".
---

# SEO Keyword Distiller

## What You Are

An automated SEO content intelligence tool.
**Input one keyword → get two deliverables:**

1. **HTML Distillation Report** — for humans. Open in browser. Understand the
   full competitive landscape: top pages, content structure, cognitive frames,
   and proven formulas.
2. **Content Strategy Skill Folder** — for AI. Install in your AI tool and say
   "write an article about X". The AI will follow the distilled strategy from
   top-ranking pages — not generic SEO advice.

Mode A: analyze competitor content (learn from them).
Mode B: analyze your own site content (understand your DNA, fix gaps).

Core philosophy: **Scripts set the floor, AI raises the ceiling.**
Scripts handle deterministic work (fetch, parse, count, pattern-match).
AI handles insight (synthesize, frame, recommend, write).

---

## Capability Scope

Crawl the top N Google results for a keyword (10 / 20 / 30), produce
three-layer distillation:

### Three-Layer Distillation Structure

| Layer | Answers | Examples |
|-------|---------|---------|
| **Cognitive Layer** | What do top pages *believe*? | Core assumptions, shared frames, implicit worldview |
| **Strategy Layer** | How is content *structured*? | Length, depth, heading patterns, E-E-A-T signals, CTAs |
| **Content Layer** | How is it *written*? | Title formulas, intro hooks, H2 patterns, tone, CTAs |

### Deliverable 1: HTML Distillation Report (10 Modules)

1. At-a-Glance (summary card)
2. Persona Mapping (who ranks?)
3. Cognitive Layer (what they believe)
4. Strategy Layer (how they structure content)
5. TOP 10 Page Breakdown (card per page)
6. Content Formula Cheat Sheet
7. Topic Ideation Bank (15 ranked angles)
8. Data Panel (stats, title patterns, phrase co-occurrence)
9. SERP Trends (category shifts, length evolution, gaps)
10. Core Conclusions (3-sentence summary + action steps)

### Deliverable 2: Content Strategy Skill Folder

- Mode A: `{keyword}_content_strategy.skill/SKILL.md`
- Mode B: `{keyword}_content_dna.skill/SKILL.md`
- 8 chapters: How to Use → Cognitive Layer → Strategy Layer → Content Layer →
  Forbidden Zone → Before/After Examples → Topic Bank → Limitations & Checklist

### Division of Labor

**Scripts (30% — floor)**:
- Environment check, dependency install
- Google SERP fetch (advanced: title + snippet; basic: URL only)
- Page content extraction (readability-lxml + bs4 fallback)
- Statistical analysis: title patterns (11 formulas), category clustering,
  phrase co-occurrence, E-E-A-T signals, CTA detection
- Data draft + AI distillation task generation

**AI (70% — ceiling)**:
- HTML Distillation Report (all 10 modules)
- Content Strategy Skill Folder (all 8 chapters)
- Cognitive layer synthesis (beliefs, frames, tensions)
- Strategy recommendations, before/after examples, topic bank

---

## Prerequisites

- Python 3.8+
- Network access to google.com (direct or via proxy)
- Local desktop (no headless server limitations)
- No API key required — uses public SERP scraping

### Proxy Setup (if needed)

```bash
# Windows PowerShell
$env:HTTP_PROXY  = "http://127.0.0.1:7890"
$env:HTTPS_PROXY = "http://127.0.0.1:7890"

# macOS / Linux
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890
```

---

## Execution Flow

### Phase 0: Environment Auto-Setup

Run `python scripts/check_env.py`

Auto-checks and installs:
1. **requests** — HTTP client
2. **beautifulsoup4** — HTML parser
3. **lxml** — fast parser backend
4. **readability-lxml** — article text extractor
5. **googlesearch-python** — Google SERP scraper

### Phase 0.5: Interactive Mode Selection

Must display this interaction before proceeding:

```text
───────────────────────────────────────────────────────
Welcome to SEO Keyword Distiller!

Please choose analysis mode:

  🔍 A — Analyze competitor content
     Crawl top Google results → distill their strategy
     → Generates {keyword}_content_strategy.skill/
     Load the Skill in your AI: "Write an article about X"
     AI follows the proven structure from top-ranking pages.

  🪞 B — Analyze your own site / content
     Crawl your own pages → find content DNA & gaps
     → Generates {keyword}_content_dna.skill/
     AI writes in your style, fixes weak spots automatically.

  ⚡ C — Competitor gap analysis (v2.1, not yet available)

Enter A or B:

How many SERP results to crawl?
  ① 10 results — Quick scan (~5–10 min)
  ② 20 results — Recommended (~15–25 min)
  ③ 30 results — Deep analysis (~30–45 min)

💡 Checkpoint every 5 pages — interrupt-safe.
───────────────────────────────────────────────────────
```

Record: `user_mode` (A or B) and `num_results` (10 / 20 / 30).

### Phase 1: SERP Crawl + Page Fetch

Run `python scripts/crawl_serp.py "<keyword>" -o ./data --num <num_results>`

Auto-completes:
1. **Advanced SERP fetch** — scrapes Google results page for title + snippet + URL
2. **Domain filtering** — removes social media, app stores, video platforms
3. **Deduplication** — max 2 pages per domain
4. **Batch page fetch** — extracts clean body text via readability-lxml (bs4 fallback)
5. **Checkpoint** — saves partial results every 5 pages; resumes on interruption

Output files (JSON):
- `{keyword}_serp.json` — raw SERP results
- `{keyword}_pages.json` — full page content per URL

**⚠️  Constraints:**
- Do NOT rewrite `crawl_serp.py` — call the existing script
- Do NOT change `--num` from the user's selection
- If Google returns a 429, wait 60 s and retry

### Phase 2: Content Analysis

Run `python scripts/analyze.py ./data/{keyword}_pages.json -o ./data`

Auto-completes:
1. Page filtering (skip < 80 words)
2. Content category clustering (8 categories, no pre-set domain)
3. Title pattern analysis (11 English formulas)
4. Top bigram/trigram extraction
5. E-E-A-T / depth signals
6. Opinion sentence extraction (cognitive layer raw material)

Output: `{keyword}_analysis.json`

### Phase 3: Distillation Task

Run:
```bash
python scripts/deep_analyze.py ./data/{keyword}_analysis.json "{keyword}" \
  -o ./output --pages ./data/{keyword}_pages.json --mode <user_mode>
```

Script auto-produces:
1. `{keyword}_data_draft.md` — structured data brief
2. `{keyword}_AI_distill_task.md` — **self-contained AI task file**
   (all data inlined; HTML spec + Skill spec embedded)

### Phase 3B: AI Generates Final Deliverables

AI reads `{keyword}_AI_distill_task.md` and produces:

1. **HTML Report** `{keyword}_distill_report.html`
   - Single-file, no external JS/CSS
   - Google Fonts: Space Mono + Inter
   - Design: Archive Terminal (bg `#CCCBC8`, accent `#1A3A5C`, text `#1A1A1A`)
   - No rounded corners, no box shadows, no white cards
   - Modules 1, 8, 10: navy inverted (`#1A3A5C`)
   - Animations: scroll fadeInUp, number counter, draw-in dividers (vanilla JS)
   - Collapsibles: native `<details><summary>`
   - Mobile responsive at 768 px

2. **Skill Folder** `{keyword}_content_strategy.skill/SKILL.md`
   - **It is a FOLDER, not a flat `.skill.md` file**
   - 8 chapters as specified in the AI distillation task

### Phase 4: Quality Check

Run `python scripts/verify.py ./output "{keyword}"`

Pass criteria:
- HTML report exists, > 5 KB, contains all 10 modules
- Skill folder exists, `SKILL.md` inside, > 1 KB, contains all 8 chapters
- No leftover `_partial.json` checkpoint files

---

## MCP / API Notes

This tool uses **no paid API**. All data is scraped from public Google SERPs
and public web pages. Rate limits:
- 2 s between SERP pagination calls
- 3.5 s between individual page fetches
- If blocked (429), wait 5–10 minutes

---

## File Structure

```text
seo-keyword-distiller/
├── SKILL.md                  ← This file (AI assistant reads it)
├── run.py                    ← One-click pipeline entry
├── install.py                ← Auto dependency installer
├── scripts/
│   ├── check_env.py          ← Phase 0: environment check
│   ├── crawl_serp.py         ← Phase 1: SERP + page crawl
│   ├── analyze.py            ← Phase 2: content analysis
│   ├── deep_analyze.py       ← Phase 3: data draft + AI task
│   ├── verify.py             ← Phase 4: output quality check
│   └── utils/
│       ├── common.py         ← Shared utility functions
│       └── __init__.py
├── data/                     ← Phase 1-2 output (JSON)
├── output/                   ← Final deliverables (HTML + Skill)
└── references/
    ├── output_quality_benchmark.md
    └── example_content_strategy.skill/
        └── SKILL.md
```

---

## Usage

### Natural Language Trigger (recommended)

Tell your AI assistant:

```
Distill the keyword: best budget mechanical keyboard
```

The AI must run Phase 0.5 interaction first, then follow the pipeline.

### One-click CLI

```bash
python run.py "best budget mechanical keyboard"
python run.py "best budget mechanical keyboard" --num 20 --lang en --country in
python run.py "best budget mechanical keyboard" --skip-env
```

### Manual Step-by-Step

```bash
python scripts/check_env.py
python scripts/crawl_serp.py "best budget mechanical keyboard" -o ./data --num 20
python scripts/analyze.py ./data/best_budget_mechanical_keyboard_pages.json -o ./data
python scripts/deep_analyze.py \
    ./data/best_budget_mechanical_keyboard_analysis.json "best budget mechanical keyboard" \
    -o ./output --pages ./data/best_budget_mechanical_keyboard_pages.json --mode A
```

---

## Platform Compatibility

| Platform | Local run | HTTP | Python | File I/O | Status |
|----------|-----------|------|--------|----------|--------|
| Claude Code | ✅ | ✅ | ✅ | ✅ | ✅ Verified |
| Cursor / VS Code AI | ✅ | ✅ | ✅ | ✅ | ✅ Verified |
| OpenClaw (local) | ✅ | ✅ | ✅ | ✅ | Testing |
| Codex / GitHub Copilot | ✅ | ✅ | ✅ | ✅ | Testing |
| Cloud / headless server | ✅ | ✅ | ✅ | ⚠️ | No interactive prompt |

---

## Reference Documents

- `references/output_quality_benchmark.md` — gold-standard examples of what
  a high-quality HTML report and Skill file look like
- If this SKILL.md conflicts with the AI distillation task file, the
  **AI distillation task file takes precedence** (it contains keyword-specific specs)
