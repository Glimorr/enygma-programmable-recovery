#!/usr/bin/env python3
"""Fail closed if any public research artifact is missing, altered or undeclared.

Also accounts for all 289 original evidence-manifest records as either publicly
released (hash-identified) or explicitly withheld from this disclosure-safe copy.
No network, credentials or private-chain writes.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"audit/public-file-index.json"
DISPOSITION=ROOT/"audit/archive-disposition.json"
ORIGINAL=ROOT/"audit/novw1-private-evidence-manifest.json"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def files():
    return {p.relative_to(ROOT).as_posix():p for p in ROOT.rglob("*")
        if p.is_file() and ".git" not in p.relative_to(ROOT).parts
           and "__pycache__" not in p.relative_to(ROOT).parts
           and p.suffix not in (".pyc",".pyo")}

def check():
    declared=json.loads(INDEX.read_text())
    disposition=json.loads(DISPOSITION.read_text())
    original=json.loads(ORIGINAL.read_text())
    assert declared["schema"]=="enygma-public-release-files/v1"
    assert disposition["schema"]=="enygma-archive-disposition/v1"
    artifacts=declared["files"]
    assert len(artifacts)==len(set(x["path"] for x in artifacts))
    current=files()
    assert set(current)-{INDEX.relative_to(ROOT).as_posix()}==set(x["path"] for x in artifacts),(
       "release file missing or undeclared",
       sorted((set(current)-{INDEX.relative_to(ROOT).as_posix()})-set(x["path"] for x in artifacts))[:12],
       sorted(set(x["path"] for x in artifacts)-set(current))[:12])
    for x in artifacts:
        f=current[x["path"]]
        assert f.stat().st_size==x["size"],x["path"]
        assert sha(f)==x["sha256"],x["path"]
    assert sha(ORIGINAL)==disposition["original_manifest_sha256"]
    assert sha(ORIGINAL)=="3cf97ce8a4ea2f8b4248ea39e4b3f94b05abb96e8998ca9f7372d9c593859349"
    original_files=original["files"]
    status=disposition["files"]
    assert len(original_files)==len(status)==289
    assert {x["path"] for x in original_files}=={x["path"] for x in status}
    assert len({x["path"] for x in status})==289
    src={x["path"]:x for x in original_files}
    published_n=0
    for item in status:
        key=item["path"]
        assert item["sha256"]==src[key]["sha256"] and item["size"]==src[key]["size"],key
        if item["disposition"]=="released":
            assert key in current and sha(current[key])==item["sha256"],key
            published_n+=1
        else:
            assert item["disposition"]=="withheld",key
            assert key not in current,key
            assert item["reason"] in ("security_review","internal_protocol","nonpublic_operational_context"),key
    assert published_n+sum(x["disposition"]=="withheld" for x in status)==289
    prohibited_file_terms=("nov_fi_api.cjs","fault_session.cjs","run_measured_trial.py")
    assert not any(x in current for x in prohibited_file_terms)
    assert not any("native-logs/" in name or "/fi-" in name for name in current),\
        "fault controller or raw relayer/CTS logs must remain private"
    patterns=[
        re.compile(rb"-----BEGIN (?:[A-Z ]+)?PRIVATE KEY-----"),
        re.compile(rb"gh[pousr]_[A-Za-z0-9]{25,}"),
        re.compile(rb"(?im)^\s*(?:PRIVATE_KEY|MNEMONIC|SECRET_KEY|AUTH_TOKEN)\s*[:=]")
    ]
    for name,p in current.items():
        if p.suffix.lower() not in (".json",".txt",".md",".py",".cjs",".yml",".yaml",".sol",".go",".html",".svg",".csv"):
            continue
        data=p.read_bytes()
        if any(pattern.search(data) for pattern in patterns):
            raise ValueError("possible credential in "+name)
    return {"public_release":"PASS","files":len(artifacts),
        "original_archive_files":len(status),"released_original_files":published_n,
        "withheld_original_files":len(status)-published_n,
        "original_sealed_manifest_sha256":sha(ORIGINAL)}

if __name__=="__main__":
    try:print(json.dumps(check(),sort_keys=True))
    except Exception as e:
        print("PUBLIC_RELEASE_GATE_FAILED:",str(e),file=sys.stderr)
        raise SystemExit(1)
