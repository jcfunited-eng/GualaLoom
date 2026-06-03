"""
Intake Guard — gatekeeper on what text enters her world.

Harvested from Aurelion's guard.py / ingest.py / bridge_cli.
The guard PATTERN ports directly — it's not substrate-coupled,
it's a fence.

Rules:
  - Only whitelisted local paths feed her
  - PII scrubbed before ingestion
  - File-type allow list (text only)
  - Size limits per file
  - Rate limits per minute
  - HTTP fetch DISABLED by default (Joe's config)
  - robots.txt check (if HTTP ever enabled)

STRIPPED: nothing substrate-level in the guard.
EMOTION: not involved. The guard is a fence, not a feeling.
"""

import os
import re
from pathlib import Path
from typing import List, Optional, Set, Tuple


# ── Configuration ────────────────────────────────────────────

ALLOWED_EXTENSIONS: Set[str] = {".md", ".txt", ".csv"}
MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5 MB
MAX_INGEST_PER_MINUTE: int = 50  # files
HTTP_FETCH_ENABLED: bool = False  # Joe's standing config: disabled

# Default whitelist: only corpus/ and explicitly added paths
DEFAULT_WHITELIST: List[str] = ["corpus/"]


# ── PII patterns ─────────────────────────────────────────────
# Simple regex scrubbing. Not exhaustive — a starting point.

PII_PATTERNS = [
    # Email addresses
    (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
     "[EMAIL]"),
    # Phone numbers (US format)
    (re.compile(r'\b(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}\b'),
     "[PHONE]"),
    # SSN
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), "[SSN]"),
    # Credit card (basic)
    (re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'), "[CARD]"),
    # IP addresses
    (re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'), "[IP]"),
]


def scrub_pii(text: str) -> str:
    """Remove PII patterns from text before ingestion."""
    for pattern, replacement in PII_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class IntakeGuard:
    """Guards what text enters the substrate.

    Only whitelisted paths pass. PII is scrubbed. Size and rate
    are limited. HTTP is off.
    """

    def __init__(self, whitelist: Optional[List[str]] = None):
        self.whitelist = [os.path.abspath(p) for p in
                          (whitelist or DEFAULT_WHITELIST)]
        self._ingest_count = 0
        self._ingest_minute = 0

    def is_path_allowed(self, path: str) -> Tuple[bool, str]:
        """Check if a file path is allowed for ingestion."""
        abs_path = os.path.abspath(path)

        # Must exist
        if not os.path.exists(abs_path):
            return False, "file does not exist"

        # Must be a file
        if not os.path.isfile(abs_path):
            return False, "not a file"

        # Extension check
        ext = Path(abs_path).suffix.lower()
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"extension {ext} not allowed"

        # Size check
        size = os.path.getsize(abs_path)
        if size > MAX_FILE_SIZE:
            return False, f"file too large ({size} bytes, max {MAX_FILE_SIZE})"

        # Whitelist check
        allowed = False
        for wp in self.whitelist:
            if abs_path.startswith(wp) or abs_path == wp:
                allowed = True
                break
        if not allowed:
            return False, "path not in whitelist"

        return True, "ok"

    def ingest_file(self, path: str) -> Tuple[Optional[str], str]:
        """Read a file through the guard. Returns (text, status).

        Text is PII-scrubbed. Returns None if blocked.
        """
        allowed, reason = self.is_path_allowed(path)
        if not allowed:
            return None, f"blocked: {reason}"

        # Rate limit
        import time
        current_minute = int(time.time()) // 60
        if current_minute != self._ingest_minute:
            self._ingest_minute = current_minute
            self._ingest_count = 0
        self._ingest_count += 1
        if self._ingest_count > MAX_INGEST_PER_MINUTE:
            return None, "rate limit exceeded"

        try:
            with open(path, encoding="utf-8", errors="ignore") as f:
                text = f.read()
        except (IOError, OSError) as e:
            return None, f"read error: {e}"

        # PII scrub
        text = scrub_pii(text)

        return text, "ok"

    def fetch_url(self, url: str) -> Tuple[Optional[str], str]:
        """HTTP fetch — DISABLED by default per Joe's config.

        If ever enabled, must check robots.txt first.
        """
        if not HTTP_FETCH_ENABLED:
            return None, "HTTP fetch is disabled"
        # If enabled in future: robots.txt check goes here
        return None, "not implemented"

    def add_to_whitelist(self, path: str) -> None:
        """Add a path to the whitelist. Joe controls this."""
        self.whitelist.append(os.path.abspath(path))
