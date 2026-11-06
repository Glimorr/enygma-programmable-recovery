#!/usr/bin/env python3
"""Verify public research links and reject attribution/tracking contamination.

Runs in the hosted release-verification workflow before publication.
Checks the public repository's tracked source, metadata, and evidence files.
"""
from pathlib import Path
from urllib.parse import unquote
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
docs = [ROOT / "README.md", *(ROOT / "docs").glob("*.md")]
htmls = [ROOT / "index.html", ROOT / "site/index.html"]
errors = []

# Preserve established local Markdown and media link validation.
for p in docs:
    text = p.read_text(encoding="utf-8")
    for href in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)", text):
        if href.startswith(("http:", "https:", "mailto:", "#")):
            continue
        target = (p.parent / unquote(href.split("#", 1)[0])).resolve()
        if not target.is_relative_to(ROOT) or not target.exists():
            errors.append(f"{p.relative_to(ROOT)}: broken local link {href}")

for p in htmls:
    text = p.read_text(encoding="utf-8")
    for href in re.findall(r"""(?:href|src)=["']([^"']+)["']""", text):
        if href.startswith(("http:", "https:", "mailto:", "#")):
            continue
        target = (p.parent / unquote(href.split("#", 1)[0])).resolve()
        source_exists = target.exists() or (
            target.suffix == ".html" and target.with_suffix(".md").is_file()
        )
        if not target.is_relative_to(ROOT) or not source_exists:
            errors.append(f"{p.relative_to(ROOT)}: broken local link {href}")

# Match user-facing AI referrers even with separators, without embedding a
# full attribution term that would itself contaminate the public repository.
attribution = re.compile(r"chat[\s._-]*gpt|open[\s._-]*ai", re.IGNORECASE)

# No analytics or marketing tracking IDs should survive in any published link.
# A legitimate functional query (e.g., a font family) is not a tracking link.
tracking = re.compile(
    r"(?:[?&]|&amp;)(?:utm_[a-z0-9_-]+|gclid|fbclid|mc_cid|mc_eid|"
    r"ref_src|referrer|source)=[^\s\"'<>]*",
    re.IGNORECASE,
)

tracked = subprocess.run(
    ["git", "ls-files", "-z"],
    cwd=ROOT,
    capture_output=True,
    check=True,
).stdout.decode("utf-8").split("\0")
inspected = 0
for name in tracked:
    if not name:
        continue
    p = ROOT / name
    if not p.is_file():
        continue
    raw = p.read_bytes()
    if b"\0" in raw[:8192]:
        continue
    try:
        content = raw.decode("utf-8")
    except UnicodeDecodeError:
        continue
    inspected += 1
    for lineno, line in enumerate(content.splitlines(), 1):
        if attribution.search(line):
            errors.append(f"{name}:{lineno}: unapproved source attribution")
        if tracking.search(line):
            errors.append(f"{name}:{lineno}: tracking parameter in published content")

if errors:
    print("RESEARCH_LINKS_FAILED", len(errors), *errors, sep="\n", file=sys.stderr)
    sys.exit(1)

print(
    "RESEARCH_LINKS_PASSED",
    len(docs), "documents",
    len(htmls), "sites",
    inspected, "tracked text files",
    "attribution_and_tracking=0",
)
