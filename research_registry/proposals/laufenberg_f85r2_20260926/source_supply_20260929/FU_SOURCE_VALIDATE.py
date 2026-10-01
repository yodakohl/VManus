#!/usr/bin/env python3
"""Validate FU root source receipts and replay exact metadata capacity; no meaning claim."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
DOSSIER = Path(__file__).resolve().parent
review = json.loads((DOSSIER / "FU_SOURCE_RESULT.json").read_text())
errors = []
checks = []
for packet in review["source_packets"]:
    for item in packet["input_artifacts"]:
        data = (ROOT / item["path"]).read_bytes()
        ok = len(data) == item["bytes"] and hashlib.sha256(data).hexdigest() == item["sha256"]
        checks.append({"path": item["path"], "hash_and_length_match": ok})
        if not ok:
            errors.append("changed source artifact: " + item["path"])
        if item["path"].endswith(".json"):
            json.loads(data)
capacity = json.loads((DOSSIER / "FU_CHOICE_CAPACITY.json").read_text())
replay = subprocess.run([sys.executable, str(DOSSIER / "FU_CHOICE_CAPACITY.py")], cwd=ROOT, text=True, capture_output=True, check=True)
capacity_match = json.loads(replay.stdout) == capacity
if not capacity_match:
    errors.append("capacity replay differs")
assert review["manuscript_science"]["confirmed_words"] == 0
assert review["manuscript_science"]["significance_claim"] is False
print(json.dumps({"status": "SOURCE_RECEIPTS_AND_EXACT_CAPACITY_PASS" if not errors else "FAIL", "source_receipts_checked": len(checks), "checks": checks, "capacity_replay_matches": capacity_match, "groups_examined": capacity["groups_examined"], "reader_matches": capacity["reader_matches"], "physical_loci": capacity["physical_loci"], "errors": errors, "scope": "bytes and metadata conservation only; not native transcription, grammar, source efficacy or meaning validation", "confirmed_words": 0}, ensure_ascii=False, indent=2))
if errors:
    raise SystemExit(1)
