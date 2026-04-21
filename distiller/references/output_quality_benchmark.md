# Output Quality Benchmark

> This document defines what "excellent" looks like for each deliverable.
> Use it to self-check AI output before considering a run complete.
> If the AI distillation task conflicts with this file, the task file takes precedence.

---

## Benchmark 1: HTML Distillation Report

### Visual & Technical Requirements

| Requirement | Pass Condition |
|-------------|----------------|
| Single-file HTML | No external JS/CSS CDN links |
| Google Fonts | Space Mono + Inter loaded via `@import` or `<link>` |
| Color palette | bg `#CCCBC8`, accent `#1A3A5C`, text `#1A1A1A` |
| Design feel | Archive Terminal — industrial, data-archive aesthetic |
| Module 1, 8, 10 | Navy inverted (`#1A3A5C` bg, `#F5F2EE` text) |
| No rounded corners | `border-radius: 0` throughout |
| No box shadows | No `box-shadow` declarations |
| Animations | fadeInUp on scroll, number counter, draw-in dividers (vanilla JS only) |
| Collapsibles | Native `<details><summary>` — no JS accordion hacks |
| Mobile responsive | 768 px breakpoint; readable on phone |
| File size | > 30 KB (thin files indicate missing content) |

### Content Requirements per Module

| Module | Minimum Content Bar |
|--------|-------------------|
| 1 At-a-Glance | Keyword visible; pages analyzed count; avg word count; dominant content strategy formula in 1 sentence |
| 2 Persona Mapping | At least 3 named site/author types with evidence (e.g., "Gaming blogs at rank 1–4 with 2000+ words") |
| 3 Cognitive Layer | ≥ 3 specific beliefs/assumptions with quoted evidence from actual pages |
| 4 Strategy Layer | Word count norms (min/avg/max); heading count; E-E-A-T signals; at least 1 CTA pattern |
| 5 TOP 10 Breakdown | One card per page with: title, hook sentence, H2 list, "why it ranks" analysis |
| 6 Content Formula | ≥ 3 title formulas with fill-in-the-blank templates; ≥ 2 intro hook patterns |
| 7 Topic Ideation | 15 topic angles; each labeled with intent (Info/Trans/Nav) and difficulty (Easy/Med/Hard) |
| 8 Data Panel | Full title pattern table; top phrases; word count distribution; fully collapsed by default |
| 9 SERP Trends | Category distribution; length trends; ≥ 1 content gap identified |
| 10 Core Conclusions | ≤ 3 sentences; 3 numbered action steps specific to the keyword |

### What "Thin" Looks Like (Fail Conditions)

- Module content is generic ("write good content", "use keywords naturally") → ❌
- TOP 10 cards show only URL + title with no analysis → ❌
- Cognitive layer lists obvious facts ("people search for this keyword") → ❌
- Topic ideation bank has < 10 topics or they are all variations of the same idea → ❌
- HTML uses Tailwind CDN or Bootstrap → ❌
- File < 10 KB → ❌ (almost certainly placeholder)

---

## Benchmark 2: Content Strategy Skill Folder

### Structure Requirements

```
{keyword}_content_strategy.skill/
└── SKILL.md                  ← The only required file
```

**Critical**: Must be a FOLDER. A flat `{keyword}_content_strategy.skill.md` file is a failure.

### SKILL.md Front-matter

```yaml
---
name: {keyword}-content-strategy
description: >
  Use when [specific trigger conditions related to the keyword].
---
```

### Content Requirements per Chapter

| Chapter | Minimum Content Bar |
|---------|-------------------|
| 1 How to Use | When to load this skill; how to reference it; 2 example prompts |
| 2 Cognitive Layer | 3–5 core beliefs specific to this keyword's SERP landscape |
| 3 Strategy Layer | Word count target; heading count; 3 structural rules with rationale |
| 4 Content Layer | ≥ 3 fill-in-the-blank title formulas; ≥ 2 intro hook patterns; tone descriptor |
| 5 Forbidden Zone | ≥ 5 specific things to avoid, each with a brief reason |
| 6 Before/After | 2 pairs showing: weak draft snippet → improved version using the strategy |
| 7 Topic Bank | 15 topics with intent label (Info/Trans/Nav) and difficulty rating |
| 8 Limitations | Confidence caveats; what the data can't tell you; 5-item self-check list |

### What "Thin" Looks Like (Fail Conditions)

- Any chapter contains generic SEO advice not tied to the specific keyword → ❌
- Before/After examples are invented (not based on actual page data) → ❌
- Topic bank has < 10 topics or none with difficulty ratings → ❌
- Forbidden zone is < 3 items or is generic ("don't write bad content") → ❌
- SKILL.md < 1500 words → ❌ (almost certainly placeholder/incomplete)
- Skill output as a flat file instead of folder → ❌

---

## Gold Standard Example: What Good Output Reads Like

### Cognitive Layer — Good Example

> **Belief 1**: The reader is a mobile-first casual gamer who has already downloaded
> 2–3 apps and is looking to switch. They are NOT a complete beginner.
> Evidence: 8/10 top pages assume prior app experience; none explain what rummy is.
>
> **Belief 2**: "Real money" is a positive signal, not a concern to address.
> Evidence: 9/10 pages lead with earning potential; only 1 page mentions responsible gaming.
>
> **Belief 3**: Bonuses/promotions are the primary differentiator.
> Evidence: 10/10 pages feature bonus comparisons in the first 500 words.

### Cognitive Layer — Bad Example (Generic)

> Top-ranking content is high quality and provides value to users.
> Pages use keywords naturally and have good content.

---

## Scoring Rubric (self-check)

| Dimension | 0 (Fail) | 1 (Pass) | 2 (Excellent) |
|-----------|----------|----------|---------------|
| Keyword specificity | Generic SEO advice | Tied to keyword | Uses specific examples from actual pages |
| Data grounding | No data cited | Stats mentioned | Quotes specific numbers/examples from data |
| Actionability | Vague ("write better") | Specific rules | Fill-in-the-blank templates ready to use |
| Cognitive depth | Surface observations | Identifies patterns | Names the underlying belief/frame |
| Visual execution (HTML) | Missing modules | All modules present | Design matches Archive Terminal spec exactly |

**Minimum passing score: all dimensions at 1 or above.**
**Target: all dimensions at 2.**
