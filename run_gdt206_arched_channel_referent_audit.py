#!/usr/bin/env python3
"""Summarize the direct-visual f82v/f83r arched-channel acquisition audit."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "gdt206_arched_channel_visual_inventory.tsv"
PARENT = ROOT / "gdt202_result.json"
HUMAN = ROOT / "experiments/semantic_assumptions/results/public_voynich_nu_page_annotations_v2.tsv"
METHOD = ROOT / "GDT206_ARCHED_CHANNEL_REFERENT_AUDIT_METHOD.md"
REPORT = ROOT / "GDT206_ARCHED_CHANNEL_REFERENT_AUDIT_REPORT.md"
RESULT = ROOT / "gdt206_result.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def content_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def main():
    with MANIFEST.open(encoding="utf8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    assert len(rows) == 2 and {row["page"] for row in rows} == {"f82v", "f83r"}
    eligible = sum(row["bridge_eligible"] == "1" for row in rows)
    owned = sum(row["singular_text_owner"] == "1" for row in rows)
    assert eligible == 0 and owned == 0
    status = "ARCHED_CHANNEL_MOTIF_RECURS_SINGULAR_REFERENT_BRIDGE_ABSENT"
    result = {
        "schema": "GDT206_ARCHED_CHANNEL_REFERENT_AUDIT_RESULT_V1",
        "status": status,
        "counts": {
            "physical_folios": 2,
            "direct_visual_observations": 2,
            "broad_motif_recurrences": 1,
            "singular_text_owners": owned,
            "bridge_eligible_occurrences": eligible,
        },
        "formal_payload": {"queried": False, "joined": False, "scored": False},
        "interpretation": "The two pages share a broad arch motif but not one source-bound component with singular inscription ownership on each folio.",
        "claim_ceiling": "Visual acquisition result only; no object, relation, process, word, plaintext, meaning, or translation.",
        "f84": {"opened": False, "queried": False, "retained": False, "joined": False, "scored": False},
        "inputs": {MANIFEST.name: sha(MANIFEST), PARENT.name: sha(PARENT), str(HUMAN.relative_to(ROOT)): sha(HUMAN)},
        "implementation": {Path(__file__).name: sha(Path(__file__))},
        "documents": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
    }
    result["result_content_sha256"] = content_sha(result)
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(json.dumps({"status": status, **result["counts"]}, sort_keys=True))


if __name__ == "__main__":
    main()
