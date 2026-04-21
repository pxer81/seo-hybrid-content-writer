"""
Phase 0: Environment check & dependency auto-install.

Checks for required Python packages and installs missing ones automatically.
"""

import sys
import os
import subprocess
import importlib
import argparse


REQUIRED_PACKAGES = {
    "requests": "requests",
    "bs4": "beautifulsoup4",
    "lxml": "lxml",
    "ddgs": "ddgs",
    "readability": "readability-lxml",
    "urllib3": "urllib3",
}


def check_and_install(import_name: str, pip_name: str) -> bool:
    """Try to import; install via pip if missing. Returns True if available."""
    try:
        importlib.import_module(import_name)
        print(f"  ✅ {pip_name}")
        return True
    except ImportError:
        print(f"  ⚙️  Installing {pip_name} ...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pip_name, "--quiet"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"  ✅ {pip_name} installed")
            return True
        else:
            print(f"  ❌ Failed to install {pip_name}: {result.stderr[:200]}")
            return False


def check_python_version():
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"❌ Python 3.8+ required. Current: {major}.{minor}")
        sys.exit(1)
    print(f"  ✅ Python {major}.{minor}")


def check_network():
    """Quick connectivity check to google.com."""
    try:
        import urllib.request
        urllib.request.urlopen("https://www.google.com", timeout=8)
        print("  ✅ Network (Google reachable)")
        return True
    except Exception as e:
        print(f"  ⚠️  Network check failed: {e}")
        print("     If you need a proxy, set HTTP_PROXY / HTTPS_PROXY env vars.")
        return False


def main():
    parser = argparse.ArgumentParser(description="SEO Keyword Distiller — Environment Check")
    parser.add_argument("--skip-network", action="store_true", help="Skip network connectivity check")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("Phase 0: Environment Check")
    print("=" * 60)

    # Python version
    print("\n[1/3] Python version:")
    check_python_version()

    # Dependencies
    print("\n[2/3] Python packages:")
    all_ok = True
    for import_name, pip_name in REQUIRED_PACKAGES.items():
        ok = check_and_install(import_name, pip_name)
        if not ok:
            all_ok = False

    if not all_ok:
        print("\n❌ Some packages failed to install. Please fix manually and re-run.")
        sys.exit(1)

    # Network
    if not args.skip_network:
        print("\n[3/3] Network:")
        check_network()

    print("\n" + "=" * 60)
    print("✅ Phase 0 complete — environment ready")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    main()
