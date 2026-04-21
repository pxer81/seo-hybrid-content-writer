"""
Phase 2: Content Analysis

Reads the fetched pages JSON and produces structured analysis data:
  - Basic stats (word count distribution, domain diversity)
  - Content category clustering (What angle do top pages take?)
  - Title pattern analysis (11 English headline formulas)
  - Keyword density & co-occurrence
  - Heading structure analysis
  - Readability signals
  - Top-N pages ranked by estimated quality
  - Cognitive-layer extraction: opinion sentences, value words

Output:
  {keyword}_analysis.json

Usage:
    python analyze.py ./data/{keyword}_pages.json
    python analyze.py ./data/{keyword}_pages.json -o ./data
"""

import json
import os
import sys
import re
import argparse
from collections import Counter
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.common import safe_filename, word_count, extract_domain


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def extract_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    if not text:
        return []
    sents = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sents if len(s.strip()) > 15]


def extract_headings_text(headings: list[dict]) -> list[str]:
    return [h.get("text", "") for h in (headings or []) if h.get("text")]


# ---------------------------------------------------------------------------
# Title pattern recognition (English-focused, 11 formulas)
# ---------------------------------------------------------------------------
TITLE_PATTERNS = {
    "Number / Listicle":     r"\b\d+\b",
    "How To":                r"\bhow\s+to\b",
    "Question":              r"\?$|\bwhat\b|\bwhy\b|\bwhich\b|\bwhere\b|\bwhen\b|\bwho\b",
    "Best / Top":            r"\b(best|top|leading|top-rated)\b",
    "Review / Vs":           r"\b(review|vs\.?|versus|compared?|comparison)\b",
    "Guide / Tutorial":      r"\b(guide|tutorial|walkthrough|beginner|step.by.step|complete)\b",
    "Secrets / Tips":        r"\b(secrets?|tips?|hacks?|tricks?|strategies|ways)\b",
    "Negative / Warning":    r"\b(don'?t|avoid|mistake|never|worst|warning|wrong)\b",
    "Urgency / Year":        r"\b(20\d{2}|updated|latest|new|now|today)\b",
    "Story / Case Study":    r"\b(story|case\s+study|i\s+(tried|tested|used|spent))\b",
    "Command / CTA":         r"^(get|try|use|start|build|create|discover|learn|find)",
}


def analyze_title_patterns(titles: list[str]) -> dict:
    results = {}
    n = len(titles)
    if not n:
        return results
    for name, pattern in TITLE_PATTERNS.items():
        matches = [t for t in titles if re.search(pattern, t, re.IGNORECASE)]
        if matches:
            results[name] = {
                "count": len(matches),
                "pct": round(len(matches) / n * 100, 1),
                "examples": matches[:3],
            }
    return results


# ---------------------------------------------------------------------------
# Content category clustering (English topics)
# ---------------------------------------------------------------------------
CATEGORY_PATTERNS = {
    "Tutorial / How-to":     ["how to", "step by step", "guide", "tutorial", "walkthrough"],
    "Review / Comparison":   ["review", "vs ", "compared", "best ", "pros and cons", "rating"],
    "News / Update":         ["2024", "2025", "2026", "new ", "launch", "update", "latest"],
    "Opinion / Analysis":    ["i think", "in my opinion", "analysis", "why ", "insight"],
    "List / Roundup":        ["top 10", "top 5", "best apps", "list of", "roundup"],
    "Case Study / Story":    ["case study", "i tried", "we tested", "success story", "example"],
    "Beginner / Basics":     ["beginner", "basics", "introduction", "101", "fundamentals", "for beginners"],
    "Expert / Advanced":     ["advanced", "expert", "in-depth", "deep dive", "technical", "professional"],
}


def classify_page(title: str, content: str) -> str:
    text = ((title or "") + " " + (content or "")[:500]).lower()
    for cat, kws in CATEGORY_PATTERNS.items():
        if any(kw in text for kw in kws):
            return cat
    return "General / Other"


# ---------------------------------------------------------------------------
# Opinion / insight sentence extraction
# ---------------------------------------------------------------------------
OPINION_SIGNALS = [
    r"\bwe (believe|recommend|suggest|found|discovered)\b",
    r"\bin our (experience|opinion|view|testing)\b",
    r"\b(the key|the secret|the truth|the reality|the fact) (is|about)\b",
    r"\bmake sure\b",
    r"\balways\b|\bnever\b",
    r"\bthe (best|worst|most important|biggest)\b",
    r"\byou (should|must|need to|have to)\b",
    r"\bif you (want|are|plan|need)\b",
    r"\bone of the\b",
    r"\bwhat (most|many) people\b",
]


def extract_opinion_sentences(pages: list[dict]) -> list[dict]:
    candidates = []
    pattern = re.compile("|".join(OPINION_SIGNALS), re.IGNORECASE)
    for page in pages:
        content = page.get("content", "") or ""
        title = page.get("title", "") or ""
        domain = page.get("domain", "")
        for sent in extract_sentences(content):
            if 20 <= len(sent.split()) <= 60 and pattern.search(sent):
                candidates.append({
                    "sentence": sent[:200],
                    "source_domain": domain,
                    "source_title": title[:60],
                    "source_rank": page.get("rank", 0),
                })
    return candidates[:80]   # keep top 80


# ---------------------------------------------------------------------------
# High-frequency n-gram extraction (2-3 word phrases)
# ---------------------------------------------------------------------------
STOP_WORDS = set("""
a an the and or but if in on at to of for with by from as is was are were be been
being have has had do does did will would shall should may might must can could this
that these those it its i we you he she they them their our your his her my all
also just not so very more most some any no only also well one two three here there
when where which who what how why about up out over like
""".split())


def extract_ngrams(text: str, n: int = 2) -> list[str]:
    tokens = re.findall(r"\b[a-z][a-z\-']{1,}\b", text.lower())
    tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 2]
    if n == 1:
        return tokens
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)]


def get_top_phrases(pages: list[dict], top_n: int = 30) -> list[dict]:
    counter = Counter()
    for page in pages:
        content = page.get("content", "") or ""
        counter.update(extract_ngrams(content, 2))
        counter.update(extract_ngrams(content, 3))
    return [{"phrase": p, "count": c} for p, c in counter.most_common(top_n)]


# ---------------------------------------------------------------------------
# Content-length / structure analysis
# ---------------------------------------------------------------------------
def analyze_structure(pages: list[dict]) -> dict:
    word_counts = []
    has_numbers = 0
    has_lists = 0
    has_subheadings = 0
    avg_h2_count = 0

    for page in pages:
        content = page.get("content", "") or ""
        wc = page.get("word_count") or word_count(content)
        word_counts.append(wc)
        if re.search(r"\b\d+\b", content):
            has_numbers += 1
        if re.search(r"^\s*[-•*]\s", content, re.MULTILINE):
            has_lists += 1
        headings = page.get("headings", []) or []
        h2s = [h for h in headings if h.get("level") == "h2"]
        avg_h2_count += len(h2s)
        if h2s:
            has_subheadings += 1

    n = len(pages) or 1
    return {
        "avg_word_count": int(sum(word_counts) / n) if word_counts else 0,
        "min_word_count": min(word_counts) if word_counts else 0,
        "max_word_count": max(word_counts) if word_counts else 0,
        "short_pages": sum(1 for w in word_counts if w < 600),
        "medium_pages": sum(1 for w in word_counts if 600 <= w < 1500),
        "long_pages": sum(1 for w in word_counts if w >= 1500),
        "pages_with_numbers": has_numbers,
        "pages_with_lists": has_lists,
        "pages_with_subheadings": has_subheadings,
        "avg_h2_count": round(avg_h2_count / n, 1),
    }


# ---------------------------------------------------------------------------
# SERP intelligence — what domains dominate?
# ---------------------------------------------------------------------------
def analyze_domain_authority_signals(pages: list[dict]) -> dict:
    domain_ranks: dict[str, list[int]] = {}
    for page in pages:
        domain = page.get("domain", extract_domain(page.get("url", "")))
        rank = page.get("rank", 99)
        domain_ranks.setdefault(domain, []).append(rank)

    domain_stats = []
    for domain, ranks in domain_ranks.items():
        domain_stats.append({
            "domain": domain,
            "appearances": len(ranks),
            "best_rank": min(ranks),
            "avg_rank": round(sum(ranks) / len(ranks), 1),
        })
    domain_stats.sort(key=lambda x: x["best_rank"])
    return {"domains": domain_stats[:20]}


# ---------------------------------------------------------------------------
# Main analysis function
# ---------------------------------------------------------------------------
def analyze_pages(pages_path: str) -> dict:
    with open(pages_path, "r", encoding="utf-8") as f:
        raw_pages = json.load(f)

    # Split into valid / error pages
    valid_pages = [p for p in raw_pages if "_error" not in p]
    error_pages = [p for p in raw_pages if "_error" in p]

    print(f"  Total pages: {len(raw_pages)} | Valid: {len(valid_pages)} | Errors: {len(error_pages)}")

    # Remove very short pages (likely paywalls / JS-rendered)
    usable = [p for p in valid_pages if (p.get("word_count") or word_count(p.get("content", ""))) >= 80]
    print(f"  Usable pages (≥80 words): {len(usable)}")

    if not usable:
        print("❌ No usable pages. Check crawl output.")
        sys.exit(1)

    # Enrich each page with word_count & category
    for page in usable:
        if not page.get("word_count"):
            page["word_count"] = word_count(page.get("content", ""))
        page["category"] = classify_page(page.get("title", ""), page.get("content", ""))

    # Sort by rank (ascending = better)
    usable.sort(key=lambda p: p.get("rank", 99))

    # ---- Basic stats ----
    stats = {
        "total_crawled": len(raw_pages),
        "valid": len(valid_pages),
        "errors": len(error_pages),
        "usable": len(usable),
        "analyzed_at": datetime.utcnow().isoformat() + "Z",
    }

    # ---- Category distribution ----
    cat_counter = Counter(p["category"] for p in usable)
    cat_stats = {}
    for cat, count in cat_counter.most_common():
        cat_pages = [p for p in usable if p["category"] == cat]
        avg_wc = int(sum(p["word_count"] for p in cat_pages) / len(cat_pages))
        cat_stats[cat] = {
            "count": count,
            "pct": round(count / len(usable) * 100, 1),
            "avg_word_count": avg_wc,
            "top_page": cat_pages[0].get("title", cat_pages[0].get("url", ""))[:60],
        }

    # ---- Title analysis ----
    titles = [p.get("title") or p.get("serp_title") or "" for p in usable]
    title_patterns = analyze_title_patterns(titles)

    # ---- Structure ----
    structure = analyze_structure(usable)

    # ---- Domain signals ----
    domain_signals = analyze_domain_authority_signals(usable)

    # ---- Top phrases ----
    top_phrases = get_top_phrases(usable, top_n=40)

    # ---- Opinion sentences (cognitive layer raw material) ----
    opinion_candidates = extract_opinion_sentences(usable)

    # ---- TOP10 pages ----
    top10 = []
    for p in usable[:10]:
        headings_text = extract_headings_text(p.get("headings", []))
        top10.append({
            "rank": p.get("rank"),
            "url": p.get("url"),
            "domain": p.get("domain"),
            "title": p.get("title") or p.get("serp_title", ""),
            "meta_description": p.get("meta_description", ""),
            "word_count": p.get("word_count"),
            "category": p.get("category"),
            "headings_text": headings_text[:15],
            "content_excerpt": (p.get("content") or "")[:1500],
        })

    return {
        "stats": stats,
        "category_stats": cat_stats,
        "title_patterns": title_patterns,
        "structure": structure,
        "domain_signals": domain_signals,
        "top_phrases": top_phrases,
        "opinion_candidates": opinion_candidates,
        "top10": top10,
        # keep usable pages (without full content) for deep_analyze
        "pages_summary": [
            {
                "rank": p.get("rank"),
                "url": p.get("url"),
                "domain": p.get("domain"),
                "title": p.get("title") or p.get("serp_title", ""),
                "word_count": p.get("word_count"),
                "category": p.get("category"),
            }
            for p in usable
        ],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Phase 2: SERP content analysis")
    parser.add_argument("pages_path", help="Path to {keyword}_pages.json")
    parser.add_argument("-o", "--output", default=".", help="Output directory")
    args = parser.parse_args()

    print("📊 Analyzing pages …")
    result = analyze_pages(args.pages_path)

    # Print summary
    s = result["stats"]
    print(f"\n{'='*60}")
    print(f"  Pages analyzed: {s['usable']}/{s['total_crawled']}")
    print(f"\n  Content category distribution:")
    for cat, cs in result["category_stats"].items():
        print(f"    {cat}: {cs['count']} pages ({cs['pct']}%) | avg {cs['avg_word_count']} words")
    print(f"\n  Top title patterns:")
    for pat, data in sorted(result["title_patterns"].items(), key=lambda x: -x[1]["count"])[:5]:
        print(f"    {pat}: {data['count']} ({data['pct']}%)")
    print(f"\n  Avg word count: {result['structure']['avg_word_count']}")
    print(f"  Opinion sentences extracted: {len(result['opinion_candidates'])}")
    print(f"{'='*60}")

    # Save
    base = os.path.splitext(os.path.basename(args.pages_path))[0].replace("_pages", "_analysis")
    out_path = os.path.join(args.output, f"{base}.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Analysis saved: {out_path}\n")
