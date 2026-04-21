"""
Phase 3: Deep Analysis — Data Draft + AI Distillation Task Generator

Reads Phase 2 analysis JSON + original pages JSON.
Produces:
  1. {keyword}_data_draft.md     — structured data brief (for human review)
  2. {keyword}_AI_distill_task.md — self-contained AI task file with:
       - All data inlined
       - Precise HTML report spec (Archive Terminal design)
       - Precise Skill folder spec (8 chapters)
     AI only needs THIS file to produce final deliverables.

Design:
  - Script does 30% (deterministic stats, pattern matching)
  - AI does 70% (insight synthesis, strategy distillation, writing)

Usage:
    python deep_analyze.py ./data/{kw}_analysis.json "{keyword}" -o ./output
    python deep_analyze.py ./data/{kw}_analysis.json "{keyword}" -o ./output \
        --pages ./data/{kw}_pages.json --mode A
"""

import json
import os
import sys
import re
import argparse
from datetime import datetime
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.common import safe_filename, truncate


# ---------------------------------------------------------------------------
# Content gap detection (deterministic)
# ---------------------------------------------------------------------------

def detect_content_angles(top10: list[dict]) -> list[str]:
    """Identify the dominant angles / hooks used by top-ranking pages."""
    angles = []
    for p in top10:
        title = (p.get("title") or "").lower()
        headings = [h.lower() for h in p.get("headings_text", [])]
        text = title + " " + " ".join(headings[:8])

        if re.search(r"\bhow\s+to\b", text):
            angles.append("How-to / Tutorial")
        elif re.search(r"\bbest\b|\btop\b|\bleading\b", text):
            angles.append("Best-of / Roundup")
        elif re.search(r"\breview\b|\bvs\b|\bcompare", text):
            angles.append("Review / Comparison")
        elif re.search(r"\bwhat\s+is\b|\bdefinition\b|\bmeaning\b|\bguide\b", text):
            angles.append("Definition / Guide")
        elif re.search(r"\btips\b|\bways\b|\bsteps\b|\bstrategies\b|\bhacks\b", text):
            angles.append("Tips & Strategies")
        elif re.search(r"\bcase\s+study\b|\bexample\b|\bstory\b|\bresult\b", text):
            angles.append("Case Study / Story")
        else:
            angles.append("General / Informational")

    angle_counts = Counter(angles)
    return [f"{a} ({c})" for a, c in angle_counts.most_common()]


def analyze_cta_patterns(pages: list[dict]) -> dict:
    """Detect CTAs used in top-ranking content."""
    cta_patterns = {
        "Subscribe / Newsletter": [r"subscri", r"newsletter", r"sign.?up"],
        "Download / Free Resource": [r"download", r"free\s+(ebook|guide|pdf|checklist)", r"get\s+access"],
        "Try / Free Trial": [r"try\s+(for\s+free|now|it|free)", r"free\s+trial", r"start\s+for\s+free"],
        "Contact / Enquire": [r"contact\s+us", r"get\s+in\s+touch", r"enquire"],
        "Read More / Learn More": [r"learn\s+more", r"read\s+more", r"find\s+out\s+more"],
        "Share / Social": [r"\bshare\b", r"follow\s+us", r"join\s+us"],
        "Buy / Shop": [r"\bbuy\b|\bshop\b|\border\b|\bpurchase\b"],
        "Comment / Engage": [r"leave\s+a\s+comment", r"let\s+us\s+know", r"tell\s+us"],
    }
    results = {}
    for cta_type, patterns in cta_patterns.items():
        combined = "|".join(patterns)
        count = sum(1 for p in pages if p and re.search(combined, (p.get("content") or "")[:2000], re.IGNORECASE))
        if count > 0:
            results[cta_type] = {"count": count, "pct": round(count / len(pages) * 100, 1) if pages else 0}
    return results


def analyze_content_depth_signals(pages: list[dict]) -> dict:
    """Signals that correlate with content depth / E-E-A-T."""
    n = len(pages) or 1
    has_stats = sum(1 for p in pages if re.search(r"\b\d+%|\b\d{4,}\b", p.get("content", "") or ""))
    has_quotes = sum(1 for p in pages if re.search(r'[""]|according\s+to|says?\s+\w+', p.get("content", "") or "", re.I))
    has_author = sum(1 for p in pages if re.search(r"written\s+by|by\s+[A-Z][a-z]+|author", p.get("content", "") or "", re.I))
    has_date = sum(1 for p in pages if re.search(r"(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}|updated\s+\d{4}", p.get("content", "") or "", re.I))
    return {
        "pages_with_statistics": has_stats,
        "pages_with_quotes_citations": has_quotes,
        "pages_with_author_byline": has_author,
        "pages_with_dates": has_date,
        "stats_pct": round(has_stats / n * 100, 1),
        "quotes_pct": round(has_quotes / n * 100, 1),
    }


# ---------------------------------------------------------------------------
# Data Draft generator
# ---------------------------------------------------------------------------

def gen_data_draft(keyword: str, analysis: dict, pages: list[dict] = None) -> str:
    stats = analysis["stats"]
    cat_stats = analysis.get("category_stats", {})
    title_patterns = analysis.get("title_patterns", {})
    structure = analysis.get("structure", {})
    domain_signals = analysis.get("domain_signals", {})
    top_phrases = analysis.get("top_phrases", [])
    top10 = analysis.get("top10", [])
    opinion_candidates = analysis.get("opinion_candidates", [])

    angles = detect_content_angles(top10)

    usable_pages = [p for p in (pages or []) if "_error" not in p and p.get("word_count", 0) >= 80]
    cta_info = analyze_cta_patterns(usable_pages) if usable_pages else {}
    depth_signals = analyze_content_depth_signals(usable_pages) if usable_pages else {}

    lines = [
        f"# {keyword} — Data Draft",
        f"\n> Auto-generated by deep_analyze.py | {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC",
        f"> ⚠️  This file is raw material for the AI Distillation Task — not for end users",
        f"\n---",
        f"\n## Basic Stats",
        f"\n| Metric | Value |",
        f"|--------|-------|",
        f"| Pages crawled | {stats['total_crawled']} |",
        f"| Usable pages | {stats['usable']} |",
        f"| Avg word count | {structure.get('avg_word_count', 'N/A')} |",
        f"| Short (<600w) | {structure.get('short_pages', 0)} |",
        f"| Medium (600–1500w) | {structure.get('medium_pages', 0)} |",
        f"| Long (>1500w) | {structure.get('long_pages', 0)} |",
        f"| Pages with numbered lists | {structure.get('pages_with_lists', 0)} |",
        f"| Pages with subheadings | {structure.get('pages_with_subheadings', 0)} |",
        f"| Avg H2 count | {structure.get('avg_h2_count', 0)} |",
    ]

    lines.append(f"\n## Content Category Distribution")
    lines.append(f"\n| Category | Count | % | Avg Words | Top Page |")
    lines.append(f"|----------|-------|---|-----------|----------|")
    for cat, cs in cat_stats.items():
        lines.append(f"| {cat} | {cs['count']} | {cs['pct']}% | {cs['avg_word_count']} | {cs['top_page'][:50]} |")

    lines.append(f"\n## Dominant Content Angles (TOP 10 pages)")
    for a in angles:
        lines.append(f"- {a}")

    lines.append(f"\n## Title Pattern Analysis")
    lines.append(f"\n| Pattern | Count | % | Examples |")
    lines.append(f"|---------|-------|---|---------|")
    for pat, data in sorted(title_patterns.items(), key=lambda x: -x[1]["count"]):
        ex = " / ".join(f'"{e[:35]}"' for e in data["examples"][:2])
        lines.append(f"| {pat} | {data['count']} | {data['pct']}% | {ex} |")

    lines.append(f"\n## Domain Landscape (TOP 20)")
    lines.append(f"\n| Domain | Appearances | Best Rank |")
    lines.append(f"|--------|------------|-----------|")
    for d in domain_signals.get("domains", [])[:20]:
        lines.append(f"| {d['domain']} | {d['appearances']} | #{d['best_rank']} |")

    lines.append(f"\n## Top Bigrams / Trigrams (co-occurring phrases)")
    lines.append(f"\n| Phrase | Count |")
    lines.append(f"|--------|-------|")
    for item in top_phrases[:30]:
        lines.append(f"| {item['phrase']} | {item['count']} |")

    lines.append(f"\n## CTA Patterns (across usable pages)")
    if cta_info:
        lines.append(f"\n| CTA Type | Count | Usage % |")
        lines.append(f"|----------|-------|---------|")
        for cta_type, data in sorted(cta_info.items(), key=lambda x: -x[1]["count"]):
            lines.append(f"| {cta_type} | {data['count']} | {data['pct']}% |")
    else:
        lines.append("\n_No CTA data available._")

    lines.append(f"\n## E-E-A-T / Depth Signals")
    lines.append(f"\n| Signal | Count | % |")
    lines.append(f"|--------|-------|---|")
    for k, label in [
        ("pages_with_statistics", "Pages with statistics/numbers"),
        ("pages_with_quotes_citations", "Pages with quotes/citations"),
        ("pages_with_author_byline", "Pages with author byline"),
        ("pages_with_dates", "Pages with publication dates"),
    ]:
        val = depth_signals.get(k, 0)
        pct = depth_signals.get(f"{k.replace('pages_with_', '')}s_pct", round(val / (stats.get("usable", 1) or 1) * 100, 1))
        lines.append(f"| {label} | {val} | {pct}% |")

    lines.append(f"\n## TOP 10 Page Data Packages")
    for i, p in enumerate(top10[:10]):
        lines.append(f"\n### Rank #{p.get('rank', i+1)}: {p.get('title', p.get('url', ''))[:70]}")
        lines.append(f"- **URL**: {p.get('url', '')}")
        lines.append(f"- **Domain**: {p.get('domain', '')}")
        lines.append(f"- **Category**: {p.get('category', '')}")
        lines.append(f"- **Word count**: {p.get('word_count', 'N/A')}")
        lines.append(f"- **Meta desc**: {p.get('meta_description', '')[:120]}")
        headings = p.get("headings_text", [])
        if headings:
            lines.append(f"- **Headings**: {' > '.join(headings[:8])}")
        excerpt = p.get("content_excerpt", "")
        if excerpt:
            lines.append(f"\n**Content excerpt (first 1500 chars)**:\n\n```\n{excerpt[:1500]}\n```")

    lines.append(f"\n---")
    lines.append(f"\n## Opinion / Insight Sentences ({len(opinion_candidates)} extracted)")
    lines.append(f"\n> Raw material for AI cognitive-layer distillation\n")
    if opinion_candidates:
        lines.append(f"| # | Sentence | Source Domain | SERP Rank |")
        lines.append(f"|---|----------|--------------|-----------|")
        for i, c in enumerate(opinion_candidates[:50]):
            sent = c["sentence"].replace("|", "｜")
            title = c["source_title"][:40].replace("|", "｜")
            lines.append(f"| {i+1} | {sent} | [{c['source_domain']}] ({title}) | #{c['source_rank']} |")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# AI Distillation Task generator (the "SKILL.md equivalent" driver)
# ---------------------------------------------------------------------------

def gen_ai_distill_task(keyword: str, analysis: dict,
                        pages: list[dict] = None, mode: str = "A") -> str:
    """
    Self-contained AI task file.
    AI reads this ALONE and produces:
      1. HTML distillation report
      2. Skill folder  {keyword}_content_strategy.skill/SKILL.md
    """
    stats = analysis["stats"]
    cat_stats = analysis.get("category_stats", {})
    title_patterns = analysis.get("title_patterns", {})
    structure = analysis.get("structure", {})
    top10 = analysis.get("top10", [])
    top_phrases = analysis.get("top_phrases", [])
    opinion_candidates = analysis.get("opinion_candidates", [])
    safe_kw = safe_filename(keyword)

    skill_dirname = f"{safe_kw}_content_strategy.skill"
    skill_desc = "content strategy guide" if mode == "A" else "my own content DNA"

    lines = [
        f"# AI Distillation Task — \"{keyword}\"",
        f"\n> Auto-generated by deep_analyze.py | {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC",
        f"> This file is SELF-CONTAINED. The AI does NOT need to open any other file.",
        f"> After reading this file, the AI must produce BOTH final deliverables below.",
        f"\n---",
        f"\n## 🎯 Your Mission",
        f"\nYou are a senior SEO content strategist. Based on the data below (scraped from",
        f"Google's top {stats['usable']} results for **\"{keyword}\"**), you must:",
        f"\n1. **Generate an HTML Distillation Report** (`{safe_kw}_distill_report.html`)",
        f"2. **Generate a Content Strategy Skill folder** (`{skill_dirname}/SKILL.md`)",
        f"\nDo NOT ask clarifying questions. Execute both deliverables in full.",
        f"\n---",
        f"\n## 📊 Data: Basic Stats",
        f"\n| Metric | Value |",
        f"|--------|-------|",
        f"| Keyword | **{keyword}** |",
        f"| Pages analyzed | {stats['usable']} |",
        f"| Avg word count | {structure.get('avg_word_count', 'N/A')} |",
        f"| Short pages (<600w) | {structure.get('short_pages', 0)} |",
        f"| Medium pages (600-1500w) | {structure.get('medium_pages', 0)} |",
        f"| Long pages (>1500w) | {structure.get('long_pages', 0)} |",
        f"| Avg H2 headings | {structure.get('avg_h2_count', 0)} |",
    ]

    lines.append(f"\n## 📊 Data: Content Categories")
    lines.append(f"\n| Category | Pages | % | Avg Words |")
    lines.append(f"|----------|-------|---|-----------|")
    for cat, cs in cat_stats.items():
        lines.append(f"| {cat} | {cs['count']} | {cs['pct']}% | {cs['avg_word_count']} |")

    lines.append(f"\n## 📊 Data: Title Patterns")
    lines.append(f"\n| Pattern | Count | % | Example |")
    lines.append(f"|---------|-------|---|---------|")
    for pat, data in sorted(title_patterns.items(), key=lambda x: -x[1]["count"]):
        ex = data["examples"][0][:50] if data["examples"] else ""
        lines.append(f"| {pat} | {data['count']} | {data['pct']}% | \"{ex}\" |")

    lines.append(f"\n## 📊 Data: Top Keyword Phrases")
    lines.append(f"\n(These are the 2-3 word phrases that appear most across all top-ranking pages)\n")
    lines.append(" / ".join(f'"{item["phrase"]}"({item["count"]})' for item in top_phrases[:20]))

    lines.append(f"\n\n## 📊 Data: TOP 10 Ranking Pages")
    for i, p in enumerate(top10[:10]):
        lines.append(f"\n### #{p.get('rank', i+1)}: {p.get('title', p.get('url', ''))[:80]}")
        lines.append(f"- **URL**: {p.get('url', '')}")
        lines.append(f"- **Domain**: {p.get('domain', '')} | **Category**: {p.get('category', '')} | **Words**: {p.get('word_count', 'N/A')}")
        lines.append(f"- **Meta**: {p.get('meta_description', '')[:120]}")
        headings = p.get("headings_text", [])
        if headings:
            lines.append("- **Headings (H1→H3)**: " + " > ".join(headings[:10]))
        excerpt = p.get("content_excerpt", "")
        if excerpt:
            lines.append(f"\n**Full content excerpt**:\n```\n{excerpt[:1500]}\n```")

    lines.append(f"\n## 📊 Data: Opinion / Insight Sentences")
    lines.append(f"\n> These are sentences that contain opinion signals. Use them as raw material for the Cognitive Layer.\n")
    if opinion_candidates:
        for i, c in enumerate(opinion_candidates[:40]):
            lines.append(f"{i+1}. [{c['source_domain']}] \"{c['sentence'][:180]}\"")

    # =========================================================================
    lines.append(f"\n---")
    lines.append(f"\n## 📋 Deliverable 1: HTML Distillation Report")
    lines.append(f"\n**File name**: `{safe_kw}_distill_report.html`")
    lines.append(f"\n### Technical Requirements")
    lines.append("""
- Single-file HTML — zero external JS/CSS dependencies (no CDN, no Tailwind)
- Google Fonts: `Space Mono` + `Inter` (via @import or link tag)
- Design style: **Archive Terminal** — industrial data-archive aesthetic
  - Background: `#CCCBC8`  |  Primary accent: `#1A3A5C`  |  Text: `#1A1A1A`
  - No rounded corners, no box shadows, no white card backgrounds
  - Modules 1, 8, 10 use navy inverted background (`#1A3A5C`, text `#F5F2EE`)
- Animations (vanilla JS, no libraries):
  - Scroll-triggered `fadeInUp` on all major sections
  - Number `counter` animation for large statistics
  - `draw-in` animation on horizontal dividers
- Collapsible sections: use native `<details><summary>` HTML
- Responsive: mobile breakpoint at `768px`
- Font size system:
  - Labels / metadata layer: 11–13px
  - Body content: 14–16px
  - Large stat numbers: 20–28px
""")

    lines.append(f"\n### 10 Required Modules")
    lines.append("""
| # | Module | Content |
|---|--------|---------|
| 1 | At-a-Glance | Keyword, pages analyzed, word count range, dominant strategy — navy card |
| 2 | Persona Mapping | Who is ranking? What kind of sites / authors dominate? |
| 3 | Cognitive Layer | What beliefs / assumptions underlie top content? What frame do they use? |
| 4 | Strategy Layer | How do they structure content? Length, depth, CTA, freshness signals |
| 5 | TOP 10 Page Breakdown | Card per page: title, hook, structure, why it ranks, what to steal |
| 6 | Content Formula Cheat Sheet | Title formulas, intro hooks, H2 patterns, CTA templates |
| 7 | Topic Ideation | 15 topic angles ranked by difficulty × search intent potential |
| 8 | Data Panel | Stats table, full title patterns, phrase co-occurrence — navy inverted |
| 9 | SERP Trends | Category shifts, content length evolution, gaps & opportunities |
| 10 | Core Conclusions | 3-sentence summary + 3 actionable next steps — navy inverted |
""")

    lines.append(f"\n---")
    lines.append(f"\n## 📋 Deliverable 2: Content Strategy Skill Folder")
    lines.append(f"\n**Folder**: `{skill_dirname}/`")
    lines.append(f"**File inside**: `{skill_dirname}/SKILL.md`")
    lines.append(f"\n> ⚠️  CRITICAL CONTRACT: The output is a FOLDER, not a single `.skill.md` file.")
    lines.append(f"> The folder must contain at least `SKILL.md`.")
    lines.append(f"\n### SKILL.md Front-matter")
    lines.append(f"""
```yaml
---
name: {safe_kw}-content-strategy
description: >
  Use when writing SEO content targeting "{keyword}".
  Trigger on requests like "write an article about {keyword}",
  "create content for {keyword}", "optimize for {keyword}".
---
```
""")

    lines.append(f"\n### 8 Required Chapters in SKILL.md")
    lines.append("""
| Chapter | Title | What to write |
|---------|-------|---------------|
| 1 | How to Use This Skill | Explain what this skill does; when to load it; how to reference it |
| 2 | Cognitive Layer — What the Top Pages Believe | 3–5 core beliefs / frames that top-ranking content shares |
| 3 | Strategy Layer — How Top Content is Structured | Content length, depth, heading structure, freshness signals, E-E-A-T moves |
| 4 | Content Layer — How They Write | Title formulas, intro hooks, H2 patterns, CTA types, tone |
| 5 | Creation Forbidden Zone | What NOT to do (thin content, generic advice, missing signals, etc.) |
| 6 | Before vs After Examples | 2 pairs: weak draft → improved draft, showing the strategy in action |
| 7 | Topic Ideation Bank | 15 ranked topic ideas with intent label and difficulty rating |
| 8 | Limitations & Self-check | Confidence caveats; what the data cannot tell you; checklist |

Every chapter must be based on the actual data in this file, not generic SEO advice.
Use specific examples from the TOP 10 pages.
""")

    lines.append(f"\n---")
    lines.append(f"\n## ✅ Acceptance Criteria")
    lines.append(f"""
The following must be true before you consider the task complete:

- [ ] `{safe_kw}_distill_report.html` exists and has all 10 modules
- [ ] `{skill_dirname}/SKILL.md` exists and has all 8 chapters
- [ ] HTML uses no Tailwind CDN, no external JS libraries
- [ ] Skill is a **folder**, not a flat `.skill.md` file
- [ ] All content is specific to "{keyword}" — no generic filler
- [ ] HTML renders properly in a browser (valid HTML5)
""")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase 3: Data draft + AI distillation task")
    parser.add_argument("analysis_path", help="Path to {keyword}_analysis.json")
    parser.add_argument("keyword", help="The SEO keyword (used in output filenames & report titles)")
    parser.add_argument("-o", "--output", default="./output", help="Output directory")
    parser.add_argument("--pages", help="Path to {keyword}_pages.json (for richer inline data)")
    parser.add_argument("--mode", choices=["A", "B"], default="A",
                        help="A=analyze competitor content (default), B=analyze own content")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    process_dir = os.path.join(args.output, "_process_files", "raw_materials")
    os.makedirs(process_dir, exist_ok=True)

    # Load analysis
    with open(args.analysis_path, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    # Load pages (optional, for richer inline data)
    pages = []
    if args.pages and os.path.exists(args.pages):
        with open(args.pages, "r", encoding="utf-8") as f:
            pages_raw = json.load(f)
        pages = [p for p in pages_raw if "_error" not in p and p.get("word_count", 0) >= 80]
        print(f"  Loaded {len(pages)} usable pages from {args.pages}")

    safe_kw = safe_filename(args.keyword)

    print(f"\n{'='*60}")
    print(f"Phase 3: Generating outputs for \"{args.keyword}\"")
    print(f"{'='*60}")

    # Data draft
    print("\n[1/2] Generating data draft …")
    draft = gen_data_draft(args.keyword, analysis, pages)
    draft_path = os.path.join(process_dir, f"{safe_kw}_data_draft.md")
    with open(draft_path, "w", encoding="utf-8") as f:
        f.write(draft)
    print(f"  💾 Data draft: {draft_path}")

    # AI distillation task
    print("\n[2/2] Generating AI distillation task …")
    task = gen_ai_distill_task(args.keyword, analysis, pages, mode=args.mode)
    task_path = os.path.join(process_dir, f"{safe_kw}_AI_distill_task.md")
    with open(task_path, "w", encoding="utf-8") as f:
        f.write(task)
    print(f"  💾 AI distillation task: {task_path}")

    print(f"\n{'='*60}")
    print(f"✅ Phase 3 Step A complete!")
    print(f"   Output dir : {os.path.abspath(args.output)}")
    print(f"{'='*60}")
    print(f"\nNext — have the AI read the distillation task:")
    print(f"  📋 {task_path}")
    print(f"\nThe AI will produce:")
    print(f"  🌐 {safe_kw}_distill_report.html")
    print(f"  🧠 {safe_kw}_content_strategy.skill/SKILL.md\n")


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
