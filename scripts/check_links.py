#!/usr/bin/env python3
"""Check every relative Markdown/media link in the public research presentation."""
from pathlib import Path
from urllib.parse import unquote
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
docs=[ROOT/"README.md",*(ROOT/"docs").glob("*.md")]
htmls=[ROOT/"index.html",ROOT/"site/index.html"]
errors=[]
for p in docs:
    text=p.read_text()
    for href in re.findall(r"\[[^\]]+\]\(([^)\s]+)\)",text):
        if href.startswith(("http:","https:","mailto:","#")):continue
        target=(p.parent/unquote(href.split("#",1)[0])).resolve()
        if not target.is_relative_to(ROOT) or not target.exists():
            errors.append(f"{p.relative_to(ROOT)}: {href}")
for p in htmls:
    text=p.read_text()
    for href in re.findall(r"(?:href|src)=[\"']([^\"']+)[\"']",text):
        if href.startswith(("http:","https:","mailto:","#")):continue
        target=(p.parent/unquote(href.split("#",1)[0])).resolve()
        if not target.is_relative_to(ROOT) or not target.exists():
            errors.append(f"{p.relative_to(ROOT)}: {href}")
if errors:
    print("RESEARCH_LINKS_FAILED",len(errors),*errors,sep="\n",file=sys.stderr)
    sys.exit(1)
print("RESEARCH_LINKS_PASSED",len(docs),"documents",len(htmls),"sites")
