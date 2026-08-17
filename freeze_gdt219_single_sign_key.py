#!/usr/bin/env python3
"""Freeze f76r label keys and the GDT219 empirical null before target reveal."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent
LABEL_SOURCE = ROOT / "gdt012_annotated_core_inventory.tsv"
DISCOVERY = ROOT / "gdt217_terminal_key_inventory.tsv"
METHOD = ROOT / "GDT219_SINGLE_SIGN_KEY_FREEZE_METHOD.md"
LABEL_KEYS = ROOT / "gdt219_f76_label_key_freeze.tsv"
NULL_TRAINING = ROOT / "gdt219_null_training_distribution.tsv"
RESULT = ROOT / "gdt219_prediction_freeze.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    labels = []
    for row in read(LABEL_SOURCE):
        if row["page"] != "f76r": continue
        assert row["kind"] == "L" and row["family_length"] == "1" and row["group_count"] == "1"
        labels.append({"page": "f76r", "physical_folio": "f76", "locus": row["locus"], "source_group_index": row["group_index"], "family_key": row["family_surface"], "family_length": 1, "claim_state": "FROZEN_SINGLE_SIGN_LABEL_KEY_NOT_VALUE_OR_MEANING"})
    labels.sort(key=lambda row: (int(row["locus"].split(".")[1]), row["locus"]))
    assert len(labels) == 9
    openings = [row["family_surface"][:1] for row in read(DISCOVERY) if row["side"] == "PARAGRAPH_INITIAL"]
    assert len(openings) == 42
    counts = Counter(openings)
    null_rows = [{"family_key": key, "discovery_paragraph_opening_occurrences": counts[key], "in_f76_label_key_set": int(key in {row["family_key"] for row in labels})} for key in sorted(counts)]
    write(LABEL_KEYS, labels); write(NULL_TRAINING, null_rows)
    result = {
        "experiment": "GDT219_SINGLE_SIGN_KEY_FREEZE",
        "status": "FROZEN_BEFORE_F76_PARAGRAPH_KEY_REVEAL",
        "target": {"page": "f76r", "physical_folio": "f76", "label_loci": 9, "paragraph_start_loci": 2, "paragraph_family_payload_opened": False},
        "label_key_set": sorted({row["family_key"] for row in labels}),
        "null": {"training_opening_occurrences": 42, "draw_size": 2, "without_replacement": True, "worlds": 42 * 41 // 2},
        "decision": {"required_hits": 2, "required_distinct_target_keys": 2, "maximum_exact_p": .05},
        "access_disclosure": {"raw_label_surfaces_previously_displayed": True, "label_family_keys_materialized_now": True, "target_paragraph_keys_displayed_or_retained": False},
        "f84r": {"accessed": False, "input": False, "output": False},
        "inputs_sha256": {LABEL_SOURCE.name: sha(LABEL_SOURCE), DISCOVERY.name: sha(DISCOVERY)},
        "outputs_sha256": {LABEL_KEYS.name: sha(LABEL_KEYS), NULL_TRAINING.name: sha(NULL_TRAINING)},
        "documents_sha256": {METHOD.name: sha(METHOD)},
        "implementation_sha256": sha(Path(__file__)),
        "validator_sha256": sha(ROOT / "validate_gdt219_single_sign_key_freeze.py"),
        "claim_ceiling": "Frozen f76r single-sign label key-set prediction only; no key value, paragraph pairing, word, language, plaintext, meaning, or translation.",
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":")); result["content_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__": main()
