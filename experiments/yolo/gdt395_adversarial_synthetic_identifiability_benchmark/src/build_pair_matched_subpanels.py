#!/usr/bin/env python3
"""Freeze record-local, truth-blind adversarial pair selections.

The main corpora remain authentic.  This selector chooses complete records only,
never reads oracle fields, and matches exact within-record carrier structure.
Page/paragraph/register/hand/layout channels are deliberately unavailable in the
separate pair view produced later by ``build_pair_blind_views.py``.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from normalize_bundle import normalize_bundle, validate_canonical
from world_api import validate_rows

ROOT = Path(__file__).resolve().parents[4]
EXP = ROOT / "experiments/yolo/gdt395_adversarial_synthetic_identifiability_benchmark"
INTERFACE = EXP / "artifacts/gdt395_interface_freeze.json"
MATCHES = EXP / "artifacts/gdt395_pair_matched_records.tsv"
AUDIT = EXP / "artifacts/gdt395_pair_matching_audit.tsv"
PAIRS = (("PAIR_CODEBOOK", "W02", "W03"), ("PAIR_SEMANTIC", "W09", "W10"))
RECORDS_PER_WORLD_SEED = 10
RECURRENCE_GATE = 0.10
SEARCH_WORLDS = 10_000


def stable(*parts: object) -> str:
    return hashlib.sha256("\x1f".join(map(str, parts)).encode()).hexdigest()


def load(wid: str):
    if str(EXP) not in sys.path:
        sys.path.insert(0, str(EXP))
    path = next((EXP / "worlds").glob(f"{wid.lower()}_*/generator.py"))
    spec = importlib.util.spec_from_file_location(f"match_{wid}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def records(rows: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["record_id"]].append(row)
    for rid in grouped:
        grouped[rid].sort(key=lambda row: row["event_index"])
    return grouped


def record_key(rows: list[dict]) -> tuple:
    line_groups: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        line_groups[row["line_id"]].append(row)
    ordered_lines = sorted(line_groups.values(), key=lambda q: min(r["event_index"] for r in q))
    line_profile = tuple(len(q) for q in ordered_lines)
    separators = Counter(
        "RECORD" if index == 0 else row["separator_before"]
        for index, row in enumerate(rows)
    )
    return (
        len(rows),
        line_profile,
        sum(row["ambiguous_boundary"] == "TRUE" for row in rows),
        tuple(sorted(separators.items())),
    )


def recurrence(rows: list[dict]) -> tuple[float, float, float]:
    counts = Counter(row["visible_group"] for row in rows)
    n = len(rows)
    return (
        len(counts) / n,
        max(counts.values()) / n,
        sum(value == 1 for value in counts.values()) / len(counts),
    )


def recurrence_delta(left: list[dict], right: list[dict]) -> tuple[float, float, float]:
    a, b = recurrence(left), recurrence(right)
    return tuple(abs(x - y) for x, y in zip(a, b))


def sampled_pairs(
    pair_id: str,
    seed: int,
    attempt: int,
    left_strata: dict[tuple, list[str]],
    right_strata: dict[tuple, list[str]],
) -> list[tuple[str, str]]:
    rng = random.Random(int(stable("GDT395_PAIR_SEARCH_V2", pair_id, seed, attempt)[:16], 16))
    pool: list[tuple[str, str]] = []
    for key in sorted(set(left_strata) & set(right_strata), key=repr):
        left = left_strata[key][:]
        right = right_strata[key][:]
        rng.shuffle(left)
        rng.shuffle(right)
        pool.extend(zip(left, right))
    rng.shuffle(pool)
    return pool[:RECORDS_PER_WORLD_SEED]


def select(pair_id: str, seed: int, left: dict[str, list[dict]], right: dict[str, list[dict]]):
    strata = []
    for panel in (left, right):
        grouped: dict[tuple, list[str]] = defaultdict(list)
        for rid, rows in panel.items():
            grouped[record_key(rows)].append(rid)
        strata.append(grouped)
    best = None
    for attempt in range(SEARCH_WORLDS):
        chosen = sampled_pairs(pair_id, seed, attempt, strata[0], strata[1])
        if len(chosen) != RECORDS_PER_WORLD_SEED:
            continue
        left_rows = [row for lr, _ in chosen for row in left[lr]]
        right_rows = [row for _, rr in chosen for row in right[rr]]
        delta = recurrence_delta(left_rows, right_rows)
        objective = (max(delta), sum(delta), stable(pair_id, seed, attempt))
        if best is None or objective < best[0]:
            best = (objective, chosen, delta, attempt)
        if max(delta) <= RECURRENCE_GATE:
            break
    if best is None or max(best[2]) > RECURRENCE_GATE:
        raise RuntimeError(f"{pair_id}/{seed}: no recurrence-balanced selection; best={best}")
    return best[1], best[2], best[3]


def main() -> None:
    frozen = json.loads(INTERFACE.read_text())
    modules = {wid: load(wid) for _, left, right in PAIRS for wid in (left, right)}
    match_rows = []
    audit_rows = []
    for pair_id, left_id, right_id in PAIRS:
        for seed in frozen["corpus_seeds"]:
            panels = {}
            for wid in (left_id, right_id):
                bundle = normalize_bundle(modules[wid].generate(seed, frozen["target_events_per_seed"]))
                validate_rows(modules[wid].WORLD_META, bundle, frozen["target_events_per_seed"])
                validate_canonical(bundle)
                panels[wid] = records(bundle["observations"])
            chosen, delta, attempts = select(pair_id, seed, panels[left_id], panels[right_id])
            for ordinal, (left_record, right_record) in enumerate(chosen):
                key = record_key(panels[left_id][left_record])
                if key != record_key(panels[right_id][right_record]):
                    raise AssertionError("matched record keys differ")
                match_rows.append({
                    "pair_id": pair_id,
                    "corpus_seed": seed,
                    "pair_ordinal": ordinal,
                    "record_key_sha256": hashlib.sha256(repr(key).encode()).hexdigest(),
                    "left_world": left_id,
                    "left_record_id": left_record,
                    "left_events": len(panels[left_id][left_record]),
                    "right_world": right_id,
                    "right_record_id": right_record,
                    "right_events": len(panels[right_id][right_record]),
                })
            audit_rows.append({
                "pair_id": pair_id,
                "corpus_seed": seed,
                "matched_records": len(chosen),
                "left_matched_events": sum(len(panels[left_id][lr]) for lr, _ in chosen),
                "right_matched_events": sum(len(panels[right_id][rr]) for _, rr in chosen),
                "record_length_tv": "0.000000",
                "ordered_line_profile_tv": "0.000000",
                "within_record_separator_tv": "0.000000",
                "ambiguity_tv": "0.000000",
                "ttr_difference": f"{delta[0]:.6f}",
                "top_type_rate_difference": f"{delta[1]:.6f}",
                "hapax_fraction_difference": f"{delta[2]:.6f}",
                "search_attempt": attempts,
                "gate": "PASS" if max(delta) <= RECURRENCE_GATE else "FAIL",
                "excluded_pair_channels": "PAGE|PARAGRAPH|REGISTER|HAND|LAYOUT|GLYPH_INTERNAL",
            })
    with MATCHES.open("w", newline="") as handle:
        fields = (
            "pair_id", "corpus_seed", "pair_ordinal", "record_key_sha256",
            "left_world", "left_record_id", "left_events", "right_world",
            "right_record_id", "right_events",
        )
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(match_rows)
    with AUDIT.open("w", newline="") as handle:
        fields = (
            "pair_id", "corpus_seed", "matched_records", "left_matched_events",
            "right_matched_events", "record_length_tv", "ordered_line_profile_tv",
            "within_record_separator_tv", "ambiguity_tv", "ttr_difference",
            "top_type_rate_difference", "hapax_fraction_difference", "search_attempt",
            "gate", "excluded_pair_channels",
        )
        writer = csv.DictWriter(handle, fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(audit_rows)
    failed = [row for row in audit_rows if row["gate"] != "PASS"]
    print(json.dumps({
        "matched_rows": len(match_rows),
        "audit_rows": len(audit_rows),
        "records_per_world_seed": RECORDS_PER_WORLD_SEED,
        "failed": len(failed),
        "status": "PASS" if not failed else "FAIL",
    }))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
