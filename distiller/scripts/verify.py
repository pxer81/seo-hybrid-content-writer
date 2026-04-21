"""
Phase 4: Output Verification

Checks that final deliverables (HTML report + Skill folder) meet acceptance criteria.
Also detects junk / partial files left in the output directory.

Usage:
    python verify.py ./output "best budget mechanical keyboard"
"""

import os
import sys
import re
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.common import safe_filename


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_html_report(output_dir: str, safe_kw: str) -> tuple[bool, str]:
    """Verify the HTML report exists and contains all 10 modules."""
    html_path = os.path.join(output_dir, f"{safe_kw}_distill_report.html")
    if not os.path.exists(html_path):
        return False, f"❌ V1 FAIL: HTML report not found: {html_path}"

    size = os.path.getsize(html_path)
    if size < 5000:
        return False, f"❌ V1 FAIL: HTML report is suspiciously small ({size} bytes) — likely empty or placeholder"

    with open(html_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    missing_modules = []
    required_signals = [
        ("At-a-Glance", [r"at.a.glance|module.?1|overview", r"<h[12]"]),
        ("Cognitive Layer", [r"cognitive|belief|frame|mindset"]),
        ("Strategy Layer", [r"strategy|structure|content.length|depth"]),
        ("Content Formula", [r"formula|title.pattern|heading.pattern|hook"]),
        ("TOP 10", [r"top.?10|rank.?(#|no\.?|number)?\s*1\b"]),
        ("Topic Ideation", [r"topic\s+(idea|angle|bank|ideation)"]),
        ("Data Panel", [r"data\s+panel|statistics|word.count"]),
        ("Core Conclusions", [r"conclusion|summary|next.step|action"]),
    ]
    for name, patterns in required_signals:
        found = any(re.search(p, content, re.IGNORECASE) for p in patterns)
        if not found:
            missing_modules.append(name)

    if missing_modules:
        return False, (
            f"⚠️  V1 PARTIAL: HTML report exists but may be missing modules: "
            + ", ".join(missing_modules)
        )

    # Check no CDN tailwind
    if "cdn.tailwindcss" in content or "tailwind.min.css" in content:
        return False, "❌ V1 FAIL: HTML uses Tailwind CDN (not allowed)"

    return True, f"✅ V1 PASS: HTML report OK ({size // 1024}KB, {len(content.splitlines())} lines)"


def check_skill_folder(output_dir: str, safe_kw: str) -> tuple[bool, str]:
    """Verify the Skill folder exists with valid SKILL.md."""
    skill_dir = os.path.join(output_dir, f"{safe_kw}_content_strategy.skill")
    skill_md = os.path.join(skill_dir, "SKILL.md")

    # Also check for flat file anti-pattern
    flat_skill = os.path.join(output_dir, f"{safe_kw}_content_strategy.skill.md")
    if os.path.exists(flat_skill) and not os.path.isdir(skill_dir):
        return False, (
            f"❌ V2 FAIL: Skill output as flat file ({os.path.basename(flat_skill)}) — "
            f"must be a FOLDER ({os.path.basename(skill_dir)}/SKILL.md)"
        )

    if not os.path.isdir(skill_dir):
        return False, f"❌ V2 FAIL: Skill folder not found: {skill_dir}"

    if not os.path.exists(skill_md):
        return False, f"❌ V2 FAIL: SKILL.md not found inside {skill_dir}"

    size = os.path.getsize(skill_md)
    if size < 1000:
        return False, f"❌ V2 FAIL: SKILL.md is too small ({size} bytes)"

    with open(skill_md, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    required_chapters = [
        "Cognitive Layer",
        "Strategy Layer",
        "Content Layer",
        "Forbidden",
        "Topic",
        "Limitations",
    ]
    missing = [c for c in required_chapters if not re.search(c, content, re.IGNORECASE)]
    if missing:
        return False, f"⚠️  V2 PARTIAL: SKILL.md missing chapters: {', '.join(missing)}"

    return True, f"✅ V2 PASS: Skill folder OK — {skill_md} ({size // 1024}KB)"


def check_junk_files(output_dir: str) -> str:
    """Warn about leftover partial / temp files."""
    junk_patterns = [
        r"_partial\.json$",
        r"_tmp\.",
        r"\.bak$",
        r"checkpoint",
    ]
    junk = []
    for root, _, files in os.walk(output_dir):
        for fn in files:
            if any(re.search(p, fn) for p in junk_patterns):
                junk.append(os.path.join(root, fn))

    if junk:
        return "⚠️  WARNING: Leftover temp files detected:\n" + "\n".join(f"   - {j}" for j in junk)
    return "✅ V3 PASS: No leftover temp files"


def check_process_files(output_dir: str, safe_kw: str) -> str:
    """Verify process files exist."""
    process_dir = os.path.join(output_dir, "_process_files", "raw_materials")
    draft = os.path.join(process_dir, f"{safe_kw}_data_draft.md")
    task = os.path.join(process_dir, f"{safe_kw}_AI_distill_task.md")
    msgs = []
    if os.path.exists(draft):
        msgs.append(f"  ✅ Data draft: {draft}")
    else:
        msgs.append(f"  ⚠️  Data draft missing: {draft}")
    if os.path.exists(task):
        msgs.append(f"  ✅ AI distill task: {task}")
    else:
        msgs.append(f"  ⚠️  AI distill task missing: {task}")
    return "\n".join(msgs)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Phase 4: Output verification")
    parser.add_argument("output_dir", help="Output directory to verify")
    parser.add_argument("keyword", help="The SEO keyword used in filenames")
    args = parser.parse_args()

    safe_kw = safe_filename(args.keyword)
    output_dir = args.output_dir

    print(f"\n{'='*60}")
    print(f"Phase 4: Output Verification")
    print(f"  Keyword : {args.keyword}")
    print(f"  Dir     : {output_dir}")
    print(f"{'='*60}\n")

    all_pass = True

    # V1: HTML
    ok, msg = check_html_report(output_dir, safe_kw)
    print(msg)
    if not ok:
        all_pass = False

    # V2: Skill
    ok, msg = check_skill_folder(output_dir, safe_kw)
    print(msg)
    if not ok:
        all_pass = False

    # V3: Junk files
    print(check_junk_files(output_dir))

    # V4: Process files
    print("\nProcess files:")
    print(check_process_files(output_dir, safe_kw))

    print(f"\n{'='*60}")
    if all_pass:
        print("🎉 All checks passed. Deliverables are ready.")
    else:
        print("❌ Some checks failed. See above for details.")
    print(f"{'='*60}\n")

    sys.exit(0 if all_pass else 1)


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
