"""
Auto-installer for SEO Keyword Distiller.

Run once after cloning:
    python install.py

What it does:
  1. Checks Python version (3.8+ required)
  2. Installs all required pip packages
  3. Verifies network connectivity (Google)
  4. Prints a quick-start guide
"""

import sys
import os
import subprocess
import importlib


# ---------------------------------------------------------------------------
# Package manifest
# ---------------------------------------------------------------------------
PACKAGES = [
    # (import_name, pip_name, description)
    ("requests",    "requests",              "HTTP client"),
    ("bs4",         "beautifulsoup4",        "HTML parser"),
    ("lxml",        "lxml",                  "Fast XML/HTML parser backend"),
    ("readability", "readability-lxml",      "Article text extractor"),
    ("ddgs",        "ddgs",                  "DuckDuckGo SERP scraper"),
    ("urllib3",     "urllib3",               "HTTP library (requests dependency)"),
]

PYTHON_MIN = (3, 8)


def banner(text: str):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def check_python():
    major, minor = sys.version_info[:2]
    if (major, minor) < PYTHON_MIN:
        print(f"  ❌ Python {PYTHON_MIN[0]}.{PYTHON_MIN[1]}+ required. "
              f"You have {major}.{minor}.")
        print("     Download from https://python.org/downloads/")
        sys.exit(1)
    print(f"  ✅ Python {major}.{minor}.{sys.version_info[2]}")


def install_package(import_name: str, pip_name: str, desc: str) -> bool:
    try:
        importlib.import_module(import_name)
        print(f"  ✅ {pip_name:28s} — {desc} (already installed)")
        return True
    except ImportError:
        print(f"  ⚙️  Installing {pip_name} ({desc}) …", end="", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_name, "-q"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("  ✅")
            return True
        else:
            print(f"\n     ❌ FAILED: {result.stderr.strip()[:200]}")
            return False


def check_network():
    print("\n  Checking network (Google) …", end="", flush=True)
    try:
        import urllib.request
        urllib.request.urlopen("https://www.google.com", timeout=8)
        print("  ✅  Reachable")
    except Exception as e:
        print(f"\n  ⚠️  Cannot reach Google: {e}")
        print("     Set HTTP_PROXY / HTTPS_PROXY if you need a proxy.")


def create_dirs():
    dirs = ["data", "output"]
    for d in dirs:
        path = os.path.join(os.path.dirname(__file__), d)
        os.makedirs(path, exist_ok=True)
    print(f"  ✅ Directories ready: {', '.join(dirs)}")


def print_quickstart():
    banner("Quick-Start Guide")
    print("""
  1. Run the full pipeline (interactive):
       python run.py "your seo keyword"

  2. Step by step:
       python scripts/check_env.py
       python scripts/crawl_serp.py "your keyword" -o ./data --num 20
       python scripts/analyze.py ./data/your_keyword_pages.json -o ./data
       python scripts/deep_analyze.py ./data/your_keyword_analysis.json "your keyword" -o ./output

  3. Have your AI assistant read the distillation task:
       ./output/_process_files/raw_materials/your_keyword_AI_distill_task.md

  4. The AI will produce:
       ./output/your_keyword_distill_report.html   ← open in browser
       ./output/your_keyword_content_strategy.skill/SKILL.md   ← install in AI tool

  Tips:
    • If Google rate-limits you (429 error), wait 5-10 minutes and retry
    • Set HTTP_PROXY / HTTPS_PROXY env vars if you need a proxy
    • Use --num 10 for a quick test run first
""")


def main():
    banner("SEO Keyword Distiller — Installer")

    print("\n[1/4] Python version:")
    check_python()

    print("\n[2/4] Installing packages:")
    failed = []
    for import_name, pip_name, desc in PACKAGES:
        ok = install_package(import_name, pip_name, desc)
        if not ok:
            failed.append(pip_name)

    if failed:
        print(f"\n  ❌ {len(failed)} package(s) failed to install: {', '.join(failed)}")
        print("     Try manually: pip install " + " ".join(failed))
        sys.exit(1)

    print("\n[3/4] Network:")
    check_network()

    print("\n[4/4] Creating directories:")
    create_dirs()

    banner("✅  Installation complete!")
    print_quickstart()


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
