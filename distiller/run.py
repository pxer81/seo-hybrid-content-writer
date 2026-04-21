"""
SEO Keyword Distiller — One-click entry point

Orchestrates the full pipeline:
  Phase 0  : Environment check
  Phase 0.5: Interactive mode/count selection
  Phase 1  : Google SERP + page crawl
  Phase 2  : Content analysis
  Phase 3  : Data draft + AI distillation task generation
  (Phase 3B): AI reads task → produces HTML report + Skill folder
  Phase 4  : Output verification

Usage:
    python run.py "best rummy app india"
    python run.py "best rummy app india" --num 20 --lang en --country in
    python run.py "best rummy app india" --skip-env
"""

import sys
import os
import argparse
import subprocess

SKILL_ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(SKILL_ROOT, "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from utils.common import safe_filename


MODE_OPTIONS = {"A", "B"}
COUNT_OPTIONS = {"1": 10, "2": 20, "3": 30}


# ---------------------------------------------------------------------------
# Phase runner
# ---------------------------------------------------------------------------

def run_phase(phase_name: str, cmd: list, cwd: str = None):
    """Run a subprocess phase; exit on failure."""
    print()
    print("=" * 60)
    print(f"▶  {phase_name}")
    print("=" * 60)

    result = subprocess.run(cmd, cwd=cwd or SKILL_ROOT)

    if result.returncode != 0:
        print(f"\n❌ {phase_name} failed (exit code {result.returncode})")
        print("   Check the error above, fix it, then re-run.")
        sys.exit(result.returncode)

    print(f"✅ {phase_name} complete")


# ---------------------------------------------------------------------------
# Phase 0.5 — Interactive prompts
# ---------------------------------------------------------------------------

def prompt_phase_0_5() -> tuple[str, int]:
    """Ask user for mode (A/B) and result count. Returns (mode, num_results)."""
    print()
    print("─" * 55)
    print("🎯  Welcome to SEO Keyword Distiller!")
    print()
    print("  Please choose analysis mode:")
    print()
    print("  🔍 A — Analyze competitor content")
    print("     Crawl top Google results → distill their strategy")
    print("     → Generates  {keyword}_content_strategy.skill/")
    print("     Load the Skill in your AI: 'Write an article about X'")
    print("     AI follows the proven structure from top-ranking pages.")
    print()
    print("  🪞 B — Analyze your own site / content")
    print("     Crawl your own pages → find content DNA & gaps")
    print("     → Generates  {keyword}_content_dna.skill/")
    print("     AI writes in your style, fixes weak spots automatically.")
    print()
    print("  ⚡ C — Competitor gap analysis (v2.1, not yet available)")
    print()

    while True:
        user_mode = input("Enter A or B: ").strip().upper()
        if user_mode in MODE_OPTIONS:
            break
        if user_mode == "C":
            print("⚡ C is not yet available. Please choose A or B.")
        else:
            print("Please enter A or B.")

    print()
    print("📊 How many SERP results to crawl?")
    print("  ① 10 results — Quick scan (~5–10 min)")
    print("  ② 20 results — Recommended (~15–25 min)")
    print("  ③ 30 results — Deep analysis (~30–45 min)")
    print()
    print("💡 Checkpoint every 5 pages — safe to interrupt and resume.")
    print("─" * 55)

    while True:
        choice = input("Enter 1 / 2 / 3: ").strip()
        if choice in COUNT_OPTIONS:
            num_results = COUNT_OPTIONS[choice]
            break
        print("Please enter 1, 2, or 3.")

    return user_mode, num_results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="SEO Keyword Distiller — one-click pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py "best rummy app india"
  python run.py "top online casino us" --num 20 --lang en --country us
  python run.py "best rummy app india" --skip-env
        """,
    )
    parser.add_argument("keyword", help="SEO keyword to research")
    parser.add_argument("--skip-env", action="store_true", help="Skip Phase 0 environment check")
    parser.add_argument("--num", type=int, default=None,
                        help="Override SERP result count (skips interactive prompt for count)")
    parser.add_argument("--mode", type=str, default=None, choices=["A", "B", "C"],
                        help="Override analysis mode (A/B/C)")
    parser.add_argument("--region", default="in-en",
                        help="DDG region code, e.g. in-en, us-en, wt-wt (default: in-en)")
    parser.add_argument("--proxy", default=None,
                        help="Proxy URL, e.g. http://127.0.0.1:7890 (overrides env vars)")
    parser.add_argument("--data-dir", default="./data", help="Data directory (default: ./data)")
    parser.add_argument("--output-dir", default="./output", help="Output directory (default: ./output)")
    args = parser.parse_args()

    keyword = args.keyword
    python = sys.executable
    safe_kw = safe_filename(keyword)

    print()
    print("🚀  SEO Keyword Distiller — Pipeline Start")
    print(f"    Keyword    : {keyword}")
    print(f"    Engine     : DuckDuckGo HTML")
    print(f"    Region     : {args.region}")
    if args.proxy:
        print(f"    Proxy      : {args.proxy}")
    print(f"    Data dir   : {args.data_dir}")
    print(f"    Output dir : {args.output_dir}")
    print()

    # ------------------------------------------------------------------ #
    # Phase 0: Environment
    # ------------------------------------------------------------------ #
    if not args.skip_env:
        run_phase(
            "Phase 0: Environment Check",
            [python, os.path.join(SCRIPTS_DIR, "check_env.py")],
        )
    else:
        print("\n⏭️   Skipping Phase 0 (--skip-env)")

    # ------------------------------------------------------------------ #
    # Phase 0.5: Interactive
    # ------------------------------------------------------------------ #
    if args.mode and args.num:
        user_mode = args.mode.upper()
        num_results = args.num
    else:
        user_mode, num_results = prompt_phase_0_5()
        if args.mode:
            user_mode = args.mode.upper()
        if args.num:
            num_results = args.num

    print()
    print(f"✅  Mode    : {user_mode}")
    print(f"✅  Results : {num_results}")

    # ------------------------------------------------------------------ #
    # Phase 1: SERP crawl + page fetch
    # ------------------------------------------------------------------ #
    crawl_cmd = [
        python, os.path.join(SCRIPTS_DIR, "crawl_serp.py"),
        keyword,
        "-o", args.data_dir,
        "--num", str(num_results),
        "--region", args.region,
    ]
    if args.proxy:
        crawl_cmd.extend(["--proxy", args.proxy])

    run_phase("Phase 1: DuckDuckGo SERP + Page Crawl", crawl_cmd)

    # Check pages file exists
    pages_file = os.path.join(args.data_dir, f"{safe_kw}_pages.json")
    if not os.path.isfile(pages_file):
        print(f"\n❌ Pages file not found: {pages_file}")
        print("   Phase 1 may not have completed correctly.")
        sys.exit(1)

    # ------------------------------------------------------------------ #
    # Phase 2: Content analysis
    # ------------------------------------------------------------------ #
    run_phase(
        "Phase 2: Content Analysis",
        [python, os.path.join(SCRIPTS_DIR, "analyze.py"),
         pages_file, "-o", args.data_dir],
    )

    analysis_file = os.path.join(args.data_dir, f"{safe_kw}_analysis.json")
    if not os.path.isfile(analysis_file):
        print(f"\n❌ Analysis file not found: {analysis_file}")
        print("   Phase 2 may not have completed correctly.")
        sys.exit(1)

    # ------------------------------------------------------------------ #
    # Phase 3: Data draft + AI distillation task
    # ------------------------------------------------------------------ #
    deep_cmd = [
        python, os.path.join(SCRIPTS_DIR, "deep_analyze.py"),
        analysis_file, keyword,
        "-o", args.output_dir,
        "--pages", pages_file,
        "--mode", user_mode,
    ]
    run_phase("Phase 3: Data Draft + AI Distillation Task", deep_cmd)

    # ------------------------------------------------------------------ #
    # Done — hand off to AI
    # ------------------------------------------------------------------ #
    task_path = os.path.join(
        args.output_dir, "_process_files", "raw_materials",
        f"{safe_kw}_AI_distill_task.md"
    )

    print()
    print("=" * 60)
    print("🎉  Step A complete!")
    print(f"    Output dir : {os.path.abspath(args.output_dir)}")
    print("=" * 60)
    print()
    print("Next — have the AI read the distillation task to produce final deliverables:")
    print(f"  📋  AI Distillation Task : {task_path}")
    print()
    print("The AI will generate:")
    print(f"  🌐  HTML Report  : {safe_kw}_distill_report.html")
    print(f"  🧠  Skill Folder : {safe_kw}_content_strategy.skill/SKILL.md")
    print()


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
