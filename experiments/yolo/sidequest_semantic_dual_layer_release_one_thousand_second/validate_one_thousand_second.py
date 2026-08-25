#!/usr/bin/env python3
"""Validate the Pass 1002 dual-layer release."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def read_tsv(name: str) -> list[dict[str, str]]:
    with (OUT / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    codebook = read_tsv("PASS1002_175_CURRENT_CODEBOOK.tsv")
    events = read_tsv("PASS1002_2511_DUAL_EVENT_INTERLINEAR.tsv")
    clauses = read_tsv("PASS1002_354_DUAL_CLAUSE_EDITION.tsv")
    manifest = read_tsv("PASS1002_RELEASE_MANIFEST.tsv")
    summary = json.loads((OUT / "PASS1002_BUILD_SUMMARY.json").read_text(encoding="utf-8"))
    clause_event_ids = [event_id for row in clauses for event_id in row["event_ids"].split("|")]
    layer_counts = {layer: sum(row["primary_layer_revised"] == layer for row in events) for layer in {row["primary_layer_revised"] for row in events}}
    manifest_ok = all(sha256(ROOT / row["artifact"]) == row["sha256"] for row in manifest)
    checks = {
        "codebook_175": len(codebook) == 175,
        "events_2511": len(events) == 2511 and len({row["event_id"] for row in events}) == 2511,
        "clauses_354": len(clauses) == 354,
        "running_events_2010": len(clause_event_ids) == 2010 and len(set(clause_event_ids)) == 2010,
        "all_clause_events_exist": set(clause_event_ids).issubset({row["event_id"] for row in events}),
        "productive_events_1319": layer_counts.get("PRODUCTIVE_ROOT_COMPOSITION") == 1319,
        "formula_events_595": layer_counts.get("COMMON_FORMULA_CARD") == 595,
        "contextual_events_96": layer_counts.get("CONTEXTUAL_COMPOSITION_NOT_NEW_WORD") == 96,
        "addresses_485": layer_counts.get("LOCAL_ADDRESS_OR_KENNING") == 485,
        "drug_labels_16": layer_counts.get("DRUG_LABEL_NOMENCLATOR") == 16,
        "no_old_specialist_layers": not any("SPECIALIST" in row["primary_layer_revised"] for row in events),
        "no_old_specialist_ids": not any(row["primary_teaching_unit_ids_revised"].startswith(("W", "L")) for row in events),
        "all_portable_defaults_present": all(row["portable_default_de"].strip() for row in events),
        "all_local_expansions_present": all(row["local_contextual_expansion_de"].strip() for row in events),
        "formula_cards_30": sum(row["unit_type"] == "FORMULA_CARD" for row in codebook) == 30,
        "contextual_spellings_72": sum(row["unit_type"] == "CONTEXTUAL_COMPOSITION_NOT_NEW_WORD" for row in codebook) == 72,
        "manifest_12": len(manifest) == 12,
        "manifest_hashes_match": manifest_ok,
        "summary_matches": summary["events"] == 2511 and summary["running_text_events"] == 2010 and summary["local_addresses_and_labels"] == 501,
        "no_sealed_pages": not any("f84" in "\t".join(row.values()).lower() for rows in (codebook, events, clauses, manifest) for row in rows),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "passed": sum(checks.values()), "total": len(checks)}
    (OUT / "PASS1002_VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(result["status"], result["passed"], result["total"])
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
