"""Common utility functions for SEO Keyword Distiller."""

import re


def safe_filename(name: str) -> str:
    """Convert a string to a safe filename (removes/replaces illegal chars)."""
    name = re.sub(r'[\\/:*?"<>|]', "_", name)
    name = name.strip().strip(".")
    return name or "untitled"


def truncate(text: str, max_len: int = 200) -> str:
    """Truncate text to max_len characters, adding ellipsis if needed."""
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[:max_len] + "..."


def clean_text(text: str) -> str:
    """Remove excessive whitespace and normalize line endings."""
    if not text:
        return ""
    text = re.sub(r"\r\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def word_count(text: str) -> int:
    """Estimate English word count for a piece of text."""
    if not text:
        return 0
    return len(re.findall(r"\b\w+\b", text))


def extract_domain(url: str) -> str:
    """Extract the root domain from a URL."""
    match = re.match(r"https?://([^/]+)", url or "")
    if match:
        host = match.group(1)
        # Strip www.
        host = re.sub(r"^www\.", "", host)
        return host
    return url or ""
