#!/usr/bin/env python3
"""Reveal and score the frozen f76r paragraph keys for GDT219."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FREEZE = ROOT / "gdt219_prediction_freeze.json"
LABELS = ROOT / "gdt219_f76_label_key_freeze.tsv"
TRAINING = ROOT / "gdt219_null_training_distribution.tsv"
PROSE = ROOT / "gdt016_group_state_inventory.tsv"
ROLES = ROOT / "experiments/semantic_assumptions/results/existing_human_locus_roles.tsv"
METHOD = ROOT / "GDT219_SINGLE_SIGN_KEY_FREEZE_METHOD.md"
REPORT = ROOT / "GDT219_SINGLE_SIGN_KEY_TEST_REPORT.md"
TARGET = ROOT / "gdt219_f76_paragraph_keys.tsv"
NULLS = ROOT / "gdt219_null_results.tsv"
COUNTER = ROOT / "gdt219_counterexamples.tsv"
RESULT = ROOT / "gdt219_result.json"


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(rows)


def main() -> None:
    freeze = json.loads(FREEZE.read_text(encoding="utf-8")); label_keys = set(freeze["label_key_set"])
    assert freeze["target"]["paragraph_family_payload_opened"] is False and freeze["null"]["worlds"] == 861
    roles = {row["locus"]: row for row in read(ROLES) if row["page"] == "f76r"}
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    with PROSE.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            if row["page"].startswith("f84") or row["locus"].startswith("f84") or row["page"] != "f76r": continue
            role = roles.get(row["locus"], {})
            if role.get("kind") == "P" and role.get("paragraph_start") == "1": groups[row["locus"]].append(row)
    assert len(groups) == 2
    target_rows = []
    for locus in sorted(groups, key=lambda value: int(value.split(".")[1])):
        row = min(groups[locus], key=lambda value: int(value["group_index"])); family_key = row["family_surface"][:1]
        target_rows.append({"page": "f76r", "physical_folio": "f76", "paragraph_start_locus": locus, "first_group_index": row["group_index"], "first_group_family_surface": row["family_surface"], "single_family_key": family_key, "in_frozen_label_key_set": int(family_key in label_keys), "claim_state": "PROSPECTIVE_SINGLE_SIGN_SET_MEMBERSHIP_NOT_LABEL_PAIRING_OR_MEANING"})

    expanded = []
    for row in read(TRAINING): expanded.extend([row["family_key"]] * int(row["discovery_paragraph_opening_occurrences"]))
    assert len(expanded) == 42
    distribution = Counter()
    for left, right in itertools.combinations(range(42), 2): distribution[int(expanded[left] in label_keys) + int(expanded[right] in label_keys)] += 1
    assert sum(distribution.values()) == 861
    hits = sum(int(row["in_frozen_label_key_set"]) for row in target_rows)
    exact_p = sum(count for value, count in distribution.items() if value >= hits) / 861
    distinct = len({row["single_family_key"] for row in target_rows})
    supported = hits == freeze["decision"]["required_hits"] and distinct >= freeze["decision"]["required_distinct_target_keys"] and exact_p <= freeze["decision"]["maximum_exact_p"]
    status = "SINGLE_SIGN_KEY_SET_PROVISIONAL_LEAD" if supported else "SINGLE_SIGN_KEY_SET_NOT_SUPPORTED"

    null_rows = [{"hit_count": value, "worlds": distribution[value], "probability": f"{distribution[value]/861:.12f}", "inclusive_upper_tail": f"{sum(count for v, count in distribution.items() if v >= value)/861:.12f}"} for value in range(3)]
    counter = [
        {"counterexample_id": "C01", "observation": "The f76r key set contains five of the source-family identities represented by nine labels.", "impact": "set membership has substantial chance coverage"},
        {"counterexample_id": "C02", "observation": "Only two paragraph starts are available on one physical folio.", "impact": "no independent replication or pairing"},
        {"counterexample_id": "C03", "observation": "The null uses the global GDT217 opening distribution because no other section-T page exists.", "impact": "register mismatch limits inference"},
        {"counterexample_id": "C04", "observation": "The GDT217 one-family positional channel was nonconfirming.", "impact": "any f76 hit cannot rescue the broader coarse channel"},
    ]
    write(TARGET, target_rows); write(NULLS, null_rows); write(COUNTER, counter)
    report = f"""# GDT219 — f76r single-sign key-set test

## Result

Status: **{status}**.

Before target reveal, f76r was frozen as the only untouched page with both
labels and confirmed-prose paragraph starts.  Its nine one-sign labels carry
five source-family identities: `{', '.join(sorted(label_keys))}`.

The two paragraph-initial keys are `{target_rows[0]['single_family_key']}` and
`{target_rows[1]['single_family_key']}`.  {hits}/2 belong to the frozen label
set and the target contains {distinct} distinct key identities.  Against all
861 unordered draws of two GDT217 discovery openings, the exact inclusive tail
is `p={exact_p:.4f}`.

The conjunctive gate {'passes' if supported else 'does not pass'}.  {'Retain a page-local single-sign set-level reference lead, without pairing any label to either paragraph.' if supported else 'The overt single-sign label inventory does not provide an unusual paragraph-key bridge.'}

This outcome does not alter GDT218: f76r still has no capacity for the
two-family rule, and the coarse one-family GDT217 channel remains
nonconfirming.  The null is global rather than section-T matched, and two
paragraphs on one folio cannot establish a reference system.

No family is identified as a numeral, letter, ordinal, word, sound, language,
plaintext, meaning, or translation.  No f84r source or artifact was accessed.
"""
    REPORT.write_text(report, encoding="utf-8")
    result = {
        "experiment": "GDT219_SINGLE_SIGN_KEY_TEST", "status": status,
        "target": {"page": "f76r", "paragraph_keys": [row["single_family_key"] for row in target_rows], "hits": hits, "distinct_target_keys": distinct},
        "null": {"worlds": 861, "exact_inclusive_p": exact_p, "distribution": {str(key): distribution[key] for key in range(3)}},
        "decision_gates": {"two_of_two_hits": hits == 2, "two_distinct_target_keys": distinct >= 2, "exact_p_at_most_05": exact_p <= .05, "all_pass": supported},
        "access_chronology": {"label_side_frozen_before_target": True, "paragraph_side_first_opened_by_this_scorer": True, "prior_raw_label_display_disclosed": True},
        "f84r": {"accessed": False, "input": False, "output": False},
        "f84v": {"rows_present_in_global_prose_input": 228, "retained": False, "parsed": False, "output": False},
        "inputs_sha256": {path.name: sha(path) for path in (FREEZE, LABELS, TRAINING, PROSE)},
        "selected_source_inputs_sha256": {ROLES.name: sha(ROLES)},
        "outputs_sha256": {path.name: sha(path) for path in (TARGET, NULLS, COUNTER)},
        "documents_sha256": {METHOD.name: sha(METHOD), REPORT.name: sha(REPORT)},
        "implementation_sha256": sha(Path(__file__)), "validator_sha256": sha(ROOT / "validate_gdt219_single_sign_key_test.py"),
        "claim_ceiling": "Prospective f76r single-sign set membership only; no label-paragraph pairing, key value, word, language, plaintext, meaning, or translation.",
    }
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":")); result["content_sha256"] = hashlib.sha256(canonical.encode()).hexdigest()
    RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(status, result["target"], result["null"])


if __name__ == "__main__": main()
