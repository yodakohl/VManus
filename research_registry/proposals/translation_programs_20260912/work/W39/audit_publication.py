#!/usr/bin/env python3
"""Retrospective privacy/scope check of the exact W39 published blobs."""
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
sys.path.insert(0, str(ROOT))
from tools import work_preflight as preflight
COMMIT = "84b0acbd2a7d3e38a3c13a7cb77e511adcb3d896"
PREFIX = "research_registry/proposals/translation_programs_20260912/work/W39/"
GLOBALS = ["VOYNICH_ACTIVE_STATE.md", "VOYNICH_CURRENT_ROUTE.md", "experiments/semantic_assumptions/ACTIVE_EXPERIMENT_LEDGER.tsv", "research_registry/SOURCE_MANIFEST.json", "research_registry/curation.jsonl", "research_registry/imported.jsonl", "research_registry/ideas.jsonl"]
FILES = ["ALL_PAIRS.tsv", "ALL_STATES.tsv", "DECISION.md", "READING.md", "RECORDS.tsv", "REPORT.md", "RESULT.json", "REVIEW.json", "SPEC.json", "VALIDATION.json", "build.py", "validate.py"]
class CommittedTree(preflight.StagedTree):
    def __init__(self, root):
        super().__init__(root)
        self.entries = {}
        for row in self.git("ls-tree", "-r", "-z", COMMIT).split(b"\0"):
            if row:
                metadata, path = row.split(b"\t", 1)
                mode, kind, oid = metadata.decode().split()
                self.entries[path.decode()] = (mode, oid)
        self.changed = sorted(p.decode() for p in self.git("diff-tree", "--no-commit-id", "--no-renames", "--name-only", "-r", "-z", COMMIT).split(b"\0") if p)
preflight.StagedTree = CommittedTree
result = preflight.run(root=ROOT, includes=tuple(GLOBALS + [PREFIX + f for f in FILES]))
result["audit_timing"] = "RETROSPECTIVE_AFTER_PUBLICATION; not a pre-push pass"
result["commit"] = COMMIT
result["unchanged_allowlist_paths"] = sorted(set(result["explicit_includes"]) - set(result["staged_paths"]))
result["limitation"] = "Repository pattern and explicit scope checks, not a guarantee of absence of every possible secret. Scientific claims unchanged."
Path(__file__).with_name("PUBLICATION_AUDIT.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"status": result["status"], "changed_files": len(result["staged_paths"]), "errors": result["errors"], "unchanged_allowlist_paths": result["unchanged_allowlist_paths"]}))
raise SystemExit(bool(result["errors"]))
