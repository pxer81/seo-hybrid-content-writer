"""
Phase 1: DuckDuckGo SERP Crawler + Page Content Fetcher

Input : SEO keyword
Output:
  - {keyword}_serp.json   — SERP results (title, url, snippet, rank)
  - {keyword}_pages.json  — full page content for each result URL

Design principles:
  - DuckDuckGo HTML (html.duckduckgo.com) — no JS, no API key, scraping-friendly
  - Low-concurrency: 3-5 s between page fetches
  - Checkpoint every 5 pages — resume on interruption
  - readability-lxml for clean article text extraction
  - Proxy support: set HTTPS_PROXY env var, or edit PROXY_URL below

Usage:
    python crawl_serp.py "best rummy app india"
    python crawl_serp.py "best rummy app india" -o ./data --num 20
    python crawl_serp.py "best rummy app india" --num 30 --region in-en --proxy http://127.0.0.1:7890
"""

import json
import os
import sys
import time
import argparse
import re
from datetime import datetime
from urllib.parse import urlencode, unquote

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.common import safe_filename, clean_text, extract_domain

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_NUM_RESULTS = 20
MAX_RESULTS_CAP = 50
PAGE_FETCH_DELAY = 3.5      # seconds between page fetches
DDG_DELAY = 3.0             # seconds between DDG paginations
CHECKPOINT_EVERY = 5
MIN_CONTENT_WORDS = 80

DDG_URL = "https://html.duckduckgo.com/html/"

# ---------------------------------------------------------------------------
# Proxy configuration
# Priority: CLI --proxy arg > HTTPS_PROXY env var > HTTP_PROXY env var > none
# ---------------------------------------------------------------------------
def _get_proxy(cli_proxy: str = None) -> dict | None:
    """Return a requests-compatible proxies dict, or None."""
    p = (
        cli_proxy
        or os.environ.get("HTTPS_PROXY")
        or os.environ.get("HTTP_PROXY")
        or os.environ.get("https_proxy")
        or os.environ.get("http_proxy")
    )
    if p:
        print(f"  🔀 Proxy active: {p}")
        return {"http": p, "https": p}
    return None


# Module-level proxy (set once at startup, used everywhere)
_PROXIES: dict | None = None

# Domains to skip (social, video, app stores — not useful for content analysis)
SKIP_DOMAINS = {
    "youtube.com", "facebook.com", "twitter.com", "x.com",
    "instagram.com", "linkedin.com", "reddit.com", "pinterest.com",
    "amazon.com", "play.google.com", "apps.apple.com",
    "duckduckgo.com", "bing.com",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "DNT": "1",
    "Connection": "keep-alive",
}


# ---------------------------------------------------------------------------
# Step 1: Fetch DuckDuckGo SERP via `ddgs`
# ---------------------------------------------------------------------------
def fetch_serp_ddg(keyword: str, num: int = DEFAULT_NUM_RESULTS,
                   region: str = "in-en") -> list[dict]:
    """
    Search DuckDuckGo using the `ddgs` library.
    It elegantly bypasses Cloudflare/DDG captchas.
    """
    try:
        from ddgs import DDGS
    except ImportError:
        print("❌ `ddgs` not installed. Run: pip install ddgs")
        sys.exit(1)

    print(f"\n🔍 DuckDuckGo SERP: \"{keyword}\" (region={region}, num={num})")

    results = []
    rank = 0

    try:
        # DDGS needs a specific proxy format if using one, or just the URL.
        # It takes `proxy` param in the DDGS constructor.
        proxy_url = None
        if _PROXIES and "http" in _PROXIES:
            proxy_url = _PROXIES["http"]
            
        with DDGS(proxy=proxy_url, timeout=20) as ddgs:
            # use ddgs.text() to get organic results
            # Note: region codes for ddgs might map slightly differently, but "wt-wt" / "in-en" usually work
            generator = ddgs.text(keyword, region=region, max_results=num)
            for r in generator:
                rank += 1
                url = r.get("href", "")
                title = r.get("title", "")
                snippet = r.get("body", "")
                domain = extract_domain(url)
                
                results.append({
                    "rank": rank,
                    "url": url,
                    "domain": domain,
                    "title": title,
                    "snippet": snippet,
                })
                # Print avoiding Unicode errors in windows terminals
                safe_title = title.encode("ascii", "ignore").decode()[:40]
                print(f"  #{rank:2d}  [{safe_title}]  {domain}")

    except Exception as e:
        print(f"  ⚠️  DDG search error: {e}")

    print(f"\n  → {len(results)} total results from DuckDuckGo")
    return results


# ---------------------------------------------------------------------------
# Step 2: Filter results
# ---------------------------------------------------------------------------
def filter_results(results: list[dict]) -> list[dict]:
    """Remove useless domains, dedup URLs, max 2 per domain."""
    seen_urls: set[str] = set()
    domain_counts: dict[str, int] = {}
    filtered = []

    for r in results:
        url = r["url"]
        domain = r["domain"]

        if not url or not domain:
            continue
        if any(domain == s or domain.endswith(f".{s}") for s in SKIP_DOMAINS):
            print(f"  ⏭️   Skip (blocked domain): {domain}")
            continue
        if url in seen_urls:
            print(f"  ⏭️   Skip (duplicate URL): {url[:60]}")
            continue
        if domain_counts.get(domain, 0) >= 2:
            print(f"  ⏭️   Skip (domain cap): {domain}")
            continue

        seen_urls.add(url)
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        filtered.append(r)

    print(f"\n  → {len(filtered)} URLs after filtering (was {len(results)})")
    return filtered


# ---------------------------------------------------------------------------
# Step 3: Fetch individual page content
# ---------------------------------------------------------------------------
def fetch_page_content(url: str) -> dict:
    """
    Fetch URL and extract clean body text + metadata.
    Primary: readability-lxml. Fallback: BeautifulSoup full-page.
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20,
                            allow_redirects=True, proxies=_PROXIES)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            return {"_error": f"Non-HTML: {content_type[:60]}", "url": url}

        html = resp.text

        # --- readability-lxml (best for articles) ---
        main_text = ""
        doc_title = ""
        try:
            from readability import Document
            doc = Document(html)
            doc_title = doc.title()
            content_html = doc.summary(html_partial=True)
            soup2 = BeautifulSoup(content_html, "lxml")
            main_text = soup2.get_text(separator=" ", strip=True)
        except Exception:
            pass

        # --- BeautifulSoup fallback ---
        soup = BeautifulSoup(html, "lxml")
        if not doc_title:
            t = soup.find("title")
            doc_title = t.get_text(strip=True) if t else ""

        if not main_text or len(main_text.split()) < MIN_CONTENT_WORDS:
            for tag in soup(["script", "style", "nav", "footer", "header",
                              "aside", "form", "noscript", "iframe"]):
                tag.decompose()
            body = soup.find("body")
            main_text = body.get_text(separator=" ", strip=True) if body else soup.get_text()

        main_text = clean_text(main_text)

        # Meta description
        meta_desc = ""
        mt = soup.find("meta", attrs={"name": "description"})
        if mt:
            meta_desc = mt.get("content", "")

        # Headings
        headings = []
        for h in soup.find_all(["h1", "h2", "h3"]):
            txt = h.get_text(strip=True)
            if txt:
                headings.append({"level": h.name, "text": txt})

        wc = len(main_text.split())

        return {
            "url": url,
            "title": doc_title,
            "meta_description": meta_desc,
            "headings": headings[:30],
            "word_count": wc,
            "content": main_text,
            "fetched_at": datetime.utcnow().isoformat() + "Z",
        }

    except Exception as e:
        return {"_error": str(e)[:200], "url": url}


# ---------------------------------------------------------------------------
# Step 4: Batch fetch with checkpoint
# ---------------------------------------------------------------------------
def fetch_all_pages(results: list[dict], output_dir: str,
                    keyword: str) -> list[dict]:
    """Fetch page content for each result; checkpoint every N pages."""
    safe_kw = safe_filename(keyword)
    checkpoint_path = os.path.join(output_dir, f"{safe_kw}_pages_partial.json")

    done_pages: list[dict] = []
    done_urls: set[str] = set()

    if os.path.exists(checkpoint_path):
        try:
            with open(checkpoint_path, "r", encoding="utf-8") as f:
                done_pages = json.load(f)
            done_urls = {p["url"] for p in done_pages if p.get("url")}
            print(f"\n🔄 Checkpoint found: resuming from {len(done_urls)} already-fetched pages")
        except Exception:
            done_pages, done_urls = [], set()

    to_fetch = [r for r in results if r["url"] not in done_urls]
    print(f"\n📄 Fetching {len(to_fetch)} pages (have {len(done_pages)} from checkpoint) …")
    print("=" * 60)

    ok = sum(1 for p in done_pages if "_error" not in p)
    err = len(done_pages) - ok

    for i, r in enumerate(to_fetch, start=1):
        url = r["url"]
        print(f"  [{i:2d}/{len(to_fetch)}] {r.get('domain', extract_domain(url))}", end=" … ", flush=True)

        page = fetch_page_content(url)
        page["rank"] = r["rank"]
        page["serp_title"] = r.get("title", "")
        page["serp_snippet"] = r.get("snippet", "")
        page["domain"] = r.get("domain", extract_domain(url))

        if "_error" in page:
            print(f"❌ {page['_error'][:60]}")
            err += 1
        else:
            print(f"✅ {page.get('word_count', 0)} words  |  {page.get('title', '')[:40]}")
            ok += 1

        done_pages.append(page)

        if len(done_pages) % CHECKPOINT_EVERY == 0:
            with open(checkpoint_path, "w", encoding="utf-8") as f:
                json.dump(done_pages, f, ensure_ascii=False, indent=2)
            print(f"  --- checkpoint: {ok}✅ {err}❌ ---")

        time.sleep(PAGE_FETCH_DELAY)

    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)

    print(f"\n  Done: {ok}✅ {err}❌ / {len(done_pages)} total")
    return done_pages


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def crawl_keyword(keyword: str, output_dir: str = "./data",
                  num: int = DEFAULT_NUM_RESULTS,
                  region: str = "in-en",
                  proxy: str = None) -> dict:
    global _PROXIES
    _PROXIES = _get_proxy(proxy)

    os.makedirs(output_dir, exist_ok=True)
    safe_kw = safe_filename(keyword)

    print(f"\n{'='*60}")
    print(f"🎯 Keyword : {keyword}")
    print(f"   Engine  : DuckDuckGo HTML (no API key)")
    print(f"   Region  : {region}")
    print(f"{'='*60}")

    # Step 1: SERP
    results = fetch_serp_ddg(keyword, num=num, region=region)
    if not results:
        print("❌ No SERP results. Check your network or try a different keyword.")
        sys.exit(1)

    # Save raw SERP
    serp_path = os.path.join(output_dir, f"{safe_kw}_serp.json")
    with open(serp_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n💾 SERP saved: {serp_path} ({len(results)} results)")

    # Step 2: Filter
    print("\n🔎 Filtering …")
    filtered = filter_results(results)
    if not filtered:
        print("❌ All results filtered out.")
        sys.exit(1)

    # Step 3: Fetch pages
    pages = fetch_all_pages(filtered, output_dir, keyword)

    # Step 4: Save
    pages_path = os.path.join(output_dir, f"{safe_kw}_pages.json")
    with open(pages_path, "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Pages saved: {pages_path}")

    return {"keyword": keyword, "serp": results, "pages": pages, "output_dir": output_dir}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Phase 1: DuckDuckGo SERP + page crawler")
    parser.add_argument("keyword", help="SEO keyword to research")
    parser.add_argument("-o", "--output", default="./data", help="Output directory")
    parser.add_argument("--num", type=int, default=DEFAULT_NUM_RESULTS,
                        help=f"Max SERP results (default: {DEFAULT_NUM_RESULTS}, max: {MAX_RESULTS_CAP})")
    parser.add_argument("--region", default="in-en",
                        help="DDG region code, e.g. in-en, us-en, wt-wt (default: in-en)")
    parser.add_argument("--proxy", default=None,
                        help="Proxy URL, e.g. http://127.0.0.1:7890 (overrides env vars)")
    args = parser.parse_args()
    args.num = min(args.num, MAX_RESULTS_CAP)

    start = time.time()
    result = crawl_keyword(keyword=args.keyword, output_dir=args.output,
                           num=args.num, region=args.region, proxy=args.proxy)
    elapsed = time.time() - start

    ok_pages = [p for p in result["pages"] if "_error" not in p]
    print(f"\n{'='*60}")
    print(f"🎉 Phase 1 complete! ({elapsed:.0f}s)")
    print(f"   Keyword : {result['keyword']}")
    print(f"   SERP    : {len(result['serp'])} results")
    print(f"   Pages   : {len(ok_pages)}/{len(result['pages'])} fetched OK")
    print(f"   Output  : {result['output_dir']}")
    print(f"{'='*60}\n")
