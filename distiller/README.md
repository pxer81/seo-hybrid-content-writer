<div align="center">

# SEO Keyword Distiller

> "You looked at 20 competitor articles. Can you explain *why* any one of them ranks #1?"

You opened 10 tabs, skimmed headers, took notes that felt vague. <br>
You asked AI to write a draft — it came out generic because it had no real strategy data. <br>
You moved to a new keyword and had to start from scratch. <br>

**Distill any keyword's top Google results into a reusable content strategy — in 30 minutes.**

Input a keyword → crawl top pages → distill → get two things:
- An **HTML report** to read (what works, why, and what to steal)
- A **Skill folder** to load into your AI (write like the top rankers, every time)

[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[30-Second Start](#30-second-start) · [Deliverables](#deliverables) · [Analysis Modes](#analysis-modes) · [Architecture](#architecture)

</div>

---

## What It Does

Turns "open 20 tabs and guess" into "run one command, get a strategy".

```
distill keyword: best rummy app india
```

Pipeline auto-runs:

```
Env check → SERP crawl → Page fetch → Content analysis → Data draft → AI distillation → Report + Skill
```

Two deliverables:

| Deliverable | For | Purpose |
|-------------|-----|---------|
| **HTML Distillation Report** | You (human) | Open in browser — understand the competitive landscape in 10 minutes |
| **Content Strategy Skill Folder** | Your AI | Load it, then say "write about X" — AI follows proven top-page strategy |

---

## Deliverables

### Content Strategy Skill Folder (for your AI)

A single installable folder:

```
.claude/skills/best_rummy_app_india_content_strategy.skill/
└── SKILL.md
```

After installing, tell your AI:

```
Using the best_rummy_app_india content strategy, write a 1500-word review article
```

The AI follows the distilled formula — not generic SEO advice, but patterns
extracted from the actual top-ranking pages.

**Three-Layer Distillation:**

| Layer | Answers | Example content |
|-------|---------|----------------|
| **Cognitive** | What do top pages *believe*? | "Top pages assume the reader is a mobile-first casual gamer" |
| **Strategy** | How is content *structured*? | "Average 1800 words, 6 H2s, always has a comparison table" |
| **Content** | How is it *written*? | "40% use 'Top N' titles; intro hooks lead with a user pain point" |

8 chapters: How to Use → Cognitive Layer → Strategy Layer → Content Layer →
Forbidden Zone → Before/After Examples → Topic Bank → Limitations

### HTML Distillation Report (for you)

Single-file HTML, open in any browser.

| # | Module | What's inside |
|---|--------|--------------|
| 1 | At-a-Glance | Keyword, pages analyzed, word-count range, dominant strategy formula |
| 2 | Persona Mapping | Who dominates the SERP? What site types / authors rank? |
| 3 | Cognitive Layer | Shared beliefs, implicit frames, worldview of top content |
| 4 | Strategy Layer | Length norms, depth signals, heading structure, CTA patterns |
| 5 | TOP 10 Breakdown | Per-page card: title, hook, structure, why it ranks, what to steal |
| 6 | Content Formula | Title formulas × intro hooks × H2 patterns × CTA templates |
| 7 | Topic Ideation | 15 angles ranked by difficulty × search intent potential |
| 8 | Data Panel | Full stats: title patterns, phrase frequency, E-E-A-T signals |
| 9 | SERP Trends | Category shifts, length evolution, content gaps |
| 10 | Core Conclusions | 3-sentence summary + 3 actionable next steps |

---

## Analysis Modes

| Mode | Use for | Output |
|------|---------|--------|
| **A — Competitor Analysis** | Learn their strategy | `{keyword}_content_strategy.skill/` + HTML report |
| **B — Own Content Audit** | Understand your content DNA | `{keyword}_content_dna.skill/` + HTML report |
| **C — Gap Analysis** | Compare you vs. competitors | *(v2.1 — coming soon)* |

Result count: 10 (quick) / 20 (recommended) / 30 (deep)

---

## 30-Second Start

```bash
git clone https://github.com/your-org/seo-keyword-distiller.git
cd seo-keyword-distiller
python install.py
python run.py "best rummy app india"
```

Or tell your AI assistant (with this SKILL.md loaded):

```
Distill keyword: best rummy app india
```

<details>
<summary>Manual step-by-step</summary>

```bash
python scripts/check_env.py
python scripts/crawl_serp.py "best rummy app india" -o ./data --num 20
python scripts/analyze.py ./data/best_rummy_app_india_pages.json -o ./data
python scripts/deep_analyze.py ./data/best_rummy_app_india_analysis.json \
    "best rummy app india" -o ./output \
    --pages ./data/best_rummy_app_india_pages.json --mode A
```

</details>

---

## Architecture

**"Scripts set the floor, AI raises the ceiling"**

| Role | % | Responsibility |
|------|---|---------------|
| **Scripts** | 30% | SERP crawl, page fetch, text extraction, statistical analysis, pattern matching |
| **AI** | 70% | Insight synthesis, cognitive framing, strategy writing, HTML + Skill generation |

**Key design features:**

- **No API key required** — uses public SERP scraping + page fetching
- **Checkpoint/resume** — saves every 5 pages; safe to interrupt
- **Low-concurrency** — 3.5 s between page fetches; Google-friendly
- **Domain dedup** — max 2 pages per domain; diverse result set
- **Readability-based extraction** — clean article text, not raw HTML soup
- **Cross-domain universal** — works for any English-language SEO keyword

---

## Project Structure

```
seo-keyword-distiller/
├── SKILL.md                  # Skill definition (AI reads this)
├── run.py                    # One-click pipeline entry
├── install.py                # Auto dependency installer
├── scripts/
│   ├── check_env.py          # Phase 0: env check + package install
│   ├── crawl_serp.py         # Phase 1: Google SERP + page content
│   ├── analyze.py            # Phase 2: content analysis + pattern mining
│   ├── deep_analyze.py       # Phase 3: data draft + AI distillation task
│   ├── verify.py             # Phase 4: output quality verification
│   └── utils/
│       ├── common.py         # Shared utilities
│       └── __init__.py
├── data/                     # Phase 1-2 JSON output (gitignored)
├── output/                   # Final HTML + Skill deliverables
└── references/
    ├── output_quality_benchmark.md
    └── example_content_strategy.skill/   # Installable example Skill
        └── SKILL.md
```

---

## Compared to blogger-distiller

| Dimension | blogger-distiller (Xiaohongshu) | seo-keyword-distiller (Google) |
|-----------|--------------------------------|-------------------------------|
| Input | Blogger name / user ID | SEO keyword |
| Data source | Xiaohongshu notes via MCP | Google SERP + public web pages |
| Login required | Yes (QR code scan) | No |
| Language | Chinese | English |
| Content unit | Notes (short-form social posts) | Articles (long-form web pages) |
| Metrics | Likes, collects, comments | Word count, heading structure, E-E-A-T |
| Output skill | Creator style guide | Content strategy guide |

---

## Version History

| Version | Milestone |
|---------|-----------|
| v0.1 | SKILL.md design + pipeline architecture |
| v0.5 | Phase 0-1: SERP crawl + page fetch with checkpoint |
| v1.0 | Phase 2: content analysis (11 title patterns, 8 categories) |
| v1.5 | Phase 3: data draft + AI distillation task generator |
| v1.8 | HTML report spec (Archive Terminal design) + Skill folder spec |
| **v2.0** | **Target: full Mode A pipeline verified end-to-end** |
| v2.1 | Mode C: gap analysis (planned) |

---

## License

MIT License

<div align="center">

**Let AI distill the best content strategy from your competitors — then use it as your own weapon.**

</div>
