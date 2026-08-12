#!/usr/bin/env python3
"""Check whether the registered S104 visual panel can be recovered exactly."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
OUT = BASE / "results/s104_visual_panel_recovery_check.json"
REPORT = BASE / "results/s104_visual_panel_recovery_check_report.md"

REGISTERED = (
    "component_relation_family/build_s104_source_inventory.py",
    "results/s104_component_relation_family_inventory.json",
    "results/s104_component_relation_family_inventory.tsv",
    "results/s104_component_relation_family_inventory_report.md",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    present = [rel for rel in REGISTERED if (BASE / rel).exists()]
    history = subprocess.run(
        ["git", "log", "--all", "--name-only", "--pretty=format:"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    historical = sorted({line for line in history if line in REGISTERED})
    archive_hits = []
    archive = ROOT / "archive_pre_reset_2026-08-06"
    for path in archive.rglob("*"):
        if path.is_file() and any(path.name == Path(rel).name for rel in REGISTERED):
            archive_hits.append(str(path.relative_to(ROOT)))
    decision = "STOP_UNRECOVERABLE_REGISTERED_PANEL_ARTIFACTS"
    result = {
        "experiment": "S104_NATIVE_VISUAL_PANEL_RECOVERY_CHECK",
        "status": decision,
        "decision": decision,
        "registered_paths": list(REGISTERED),
        "present_registered_paths": present,
        "reachable_git_history_paths": historical,
        "retained_archive_paths": sorted(archive_hits),
        "counts": {
            "registered_paths": len(REGISTERED),
            "present_registered_paths": len(present),
            "reachable_git_history_paths": len(historical),
            "retained_archive_paths": len(archive_hits),
        },
        "gates": {
            "exact_panel_artifact_recoverable": bool(present or historical or archive_hits),
            "narrative_summary_used_as_page_identity_source": False,
            "image_or_voynich_text_opened": False,
        },
        "inputs": {
            "active_ledger_sha256": sha(BASE / "ACTIVE_EXPERIMENT_LEDGER.tsv"),
            "active_state_sha256": sha(ROOT / "VOYNICH_ACTIVE_STATE.md"),
        },
        "claim_ceiling": (
            "The registered S104 visual panel cannot be reconstructed exactly from retained artifacts. This is a "
            "provenance stop, not evidence about Herbal ownership, any label, word, meaning, plaintext, or translation."
        ),
    }
    if result["gates"]["exact_panel_artifact_recoverable"]:
        raise SystemExit("registered panel appears recoverable; audit expectation changed")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# S104 visual-panel recovery check\n\n"
        f"Status: **{decision}**\n\n"
        "The four registered S104 inventory/builder paths are absent from the compact workspace, retained archive, "
        "and reachable Git filename history. Only narrative ledger summaries survive, which are not sufficient to "
        "recreate exact page identities or relation families. No image or Voynich text was opened.\n\n"
        f"Claim ceiling: {result['claim_ceiling']}\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
