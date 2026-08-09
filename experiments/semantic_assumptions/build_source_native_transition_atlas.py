#!/usr/bin/env python3
"""Build the frozen held-folio source-family transition atlas."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL = RESULTS / "source_native_within_group_stage_masked.tsv"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
SOURCE_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
TARGET = RESULTS / "source_native_within_group_exact_position_markov_target.json"
TARGET_VALIDATION = RESULTS / "source_native_within_group_exact_position_markov_target_validation.json"
RULES = BASE.parent.parent / "transcription" / "sources" / "sta" / "STA-Eva_def.bit"
SPEC = BASE / "SOURCE_NATIVE_TRANSITION_ATLAS_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_TSV = RESULTS / "source_native_transition_atlas.tsv"
OUT_JSON = RESULTS / "source_native_transition_atlas.json"
OUT_REPORT = RESULTS / "source_native_transition_atlas_report.md"
FROZEN = {
    PANEL: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    TARGET: "5c59e783919dc35046ad8f941f4ad28e4f272d3e062773a783a6f048c3d8ec33",
    TARGET_VALIDATION: "9f621e977e0640f9f2104e6b0133c898a2802f7ae063ce396e6cb746b6f96282",
    RULES: "7f37853510144fb3e2dc3ee9458d634f41e6d95bc1fbf1c4b8f479a53a021f81",
    SPEC: "06c9145eb362ae42be5e47f0ab87c2da3f6553e12a9b133d6bb985e8a43f70f2",
}
ALPHABET = tuple("ABCDEFGHJKLMNPQRSTUVWXYZ")
INDEX = {value: index for index, value in enumerate(ALPHABET)}
PANEL_FIELDS = ("unit_id", "locus", "page", "physical_folio", "section", "currier", "hand", "kind", "symbol_count", "split")
SOURCE_FIELDS = ("consensus_group_id", "locus", "page", "section", "currier", "hand", "code", "kind", "grammar_scope", "strict_zero_alternative", "consensus_group_index", "consensus_group_count", "start_symbol_1based", "end_symbol_1based", "symbol_count", "family_surface", "zl_sta_codes", "it_sta_codes", "rf_sta_codes", "left_boundary_profile", "right_boundary_profile")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def family_members() -> dict[str, list[str]]:
    result = defaultdict(list)
    for raw in RULES.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(None, 1)
        if len(parts) == 2 and re.fullmatch(r"[A-Z][0-9A-Za-z]", parts[0]):
            result[parts[0][0]].append(f"{parts[0]}={parts[1].strip()}")
    if set(result) != set(ALPHABET):
        raise ValueError("official family inventory")
    return dict(result)


def load_joined() -> tuple[list[dict], list[tuple[int, ...]]]:
    with PANEL.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != PANEL_FIELDS:
            raise ValueError("panel schema")
        panel = list(reader)
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if tuple(reader.fieldnames or ()) != SOURCE_FIELDS:
            raise ValueError("source schema")
        groups = list(reader)
    if len(panel) != 21899 or len(groups) != 26184 or len({row["unit_id"] for row in panel}) != 21899:
        raise ValueError("input cardinality")
    source = {row["consensus_group_id"]: row for row in groups}
    if len(source) != len(groups):
        raise ValueError("duplicate source")
    eligible = {
        row["consensus_group_id"]
        for row in groups
        if row["strict_zero_alternative"] == "1"
        and row["grammar_scope"] == "CONFIRMED_PROSE"
        and re.fullmatch(r"f\d+[rv]\d*", row["page"])
    }
    if eligible != {row["unit_id"] for row in panel}:
        raise ValueError("eligible identity")
    sequences = []
    for masked in panel:
        row = source[masked["unit_id"]]
        surface = row["family_surface"]
        if len(surface) != int(masked["symbol_count"]) or int(row["symbol_count"]) != len(surface) or any(value not in INDEX for value in surface):
            raise ValueError("surface")
        if any(masked[key] != row[key] for key in ("locus", "page", "section", "currier", "hand", "kind")):
            raise ValueError("metadata")
        sequences.append(tuple(INDEX[value] for value in surface))
    return panel, sequences


def orientation_metrics(panel: list[dict], sequences: list[tuple[int, ...]], reverse: bool) -> dict[tuple[int, int], dict]:
    folios = sorted({row["physical_folio"] for row in panel}, key=lambda value: int(value[1:]))
    folio_index = {value: index for index, value in enumerate(folios)}
    currier_index = {"A": 0, "B": 1}
    total = np.zeros((2, 12, 11, 24), dtype=np.int64)
    held = np.zeros((len(folios), 2, 12, 11, 24), dtype=np.int64)
    events = []
    for row, original in zip(panel, sequences):
        sequence = tuple(reversed(original)) if reverse else original
        length = len(sequence)
        f = folio_index[row["physical_folio"]]
        c = currier_index[row["currier"]]
        for position in range(1, length):
            previous, current = sequence[position - 1], sequence[position]
            total[c, length, position, current] += 1
            held[f, c, length, position, current] += 1
            events.append((f, c, length, position, previous, current))
    observed = np.zeros((24, 24), dtype=np.int64)
    expected = np.zeros((24, 24), dtype=np.float64)
    opportunities = np.zeros(24, dtype=np.int64)
    folio_observed = np.zeros((len(folios), 24, 24), dtype=np.int64)
    folio_expected = np.zeros((len(folios), 24, 24), dtype=np.float64)
    folio_opportunities = np.zeros((len(folios), 24), dtype=np.int64)
    currier_observed = np.zeros((2, 24, 24), dtype=np.int64)
    currier_expected = np.zeros((2, 24, 24), dtype=np.float64)
    currier_opportunities = np.zeros((2, 24), dtype=np.int64)
    for f, c, length, position, previous, current in events:
        training = total[c, length, position] - held[f, c, length, position]
        probabilities = (training + 0.5) / (training.sum() + 12.0)
        observed[previous, current] += 1
        expected[previous] += probabilities
        opportunities[previous] += 1
        folio_observed[f, previous, current] += 1
        folio_expected[f, previous] += probabilities
        folio_opportunities[f, previous] += 1
        currier_observed[c, previous, current] += 1
        currier_expected[c, previous] += probabilities
        currier_opportunities[c, previous] += 1
    output = {}
    for previous in range(24):
        eligible = folio_opportunities[:, previous] >= 5
        for current in range(24):
            residual = folio_observed[:, previous, current] - folio_expected[:, previous, current]
            positive = int(((residual > 0) & eligible).sum())
            negative = int(((residual < 0) & eligible).sum())
            eligible_count = int(eligible.sum())
            record = {
                "observed": int(observed[previous, current]),
                "expected": float(expected[previous, current]),
                "opportunities": int(opportunities[previous]),
                "log_observed_expected": float(math.log((observed[previous, current] + 0.5) / (expected[previous, current] + 0.5))),
                "eligible_folios": eligible_count,
                "positive_folios": positive,
                "negative_folios": negative,
                "zero_folios": eligible_count - positive - negative,
                "positive_fraction": positive / eligible_count if eligible_count else 0.0,
                "negative_fraction": negative / eligible_count if eligible_count else 0.0,
            }
            for currier, c in currier_index.items():
                record[f"currier_{currier}_observed"] = int(currier_observed[c, previous, current])
                record[f"currier_{currier}_expected"] = float(currier_expected[c, previous, current])
                record[f"currier_{currier}_opportunities"] = int(currier_opportunities[c, previous])
                record[f"currier_{currier}_log_observed_expected"] = float(math.log((currier_observed[c, previous, current] + 0.5) / (currier_expected[c, previous, current] + 0.5)))
            output[(previous, current)] = record
    return {"metrics": output, "events": len(events), "folios": len(folios)}


def favored(record: dict) -> bool:
    return (
        record["observed"] >= 30
        and record["expected"] >= 10
        and record["log_observed_expected"] >= math.log(2)
        and record["eligible_folios"] >= 12
        and record["positive_fraction"] >= 0.75
        and all(
            record[f"currier_{currier}_opportunities"] >= 30
            and record[f"currier_{currier}_expected"] >= 5
            and record[f"currier_{currier}_log_observed_expected"] >= math.log(1.3)
            for currier in "AB"
        )
    )


def disfavored(record: dict) -> bool:
    return (
        record["expected"] >= 30
        and record["log_observed_expected"] <= -math.log(2)
        and record["eligible_folios"] >= 12
        and record["negative_fraction"] >= 0.75
        and all(
            record[f"currier_{currier}_opportunities"] >= 30
            and record[f"currier_{currier}_expected"] >= 10
            and record[f"currier_{currier}_log_observed_expected"] <= -math.log(1.3)
            for currier in "AB"
        )
    )


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing to overwrite transition-atlas artifacts")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    if json.loads(TARGET.read_text())["decision"] != "RETAIN_POSITION_INDEPENDENT_LOCAL_TRANSITION_GRAMMAR":
        raise SystemExit("confirmed target missing")
    if json.loads(TARGET_VALIDATION.read_text())["status"] != "PASS_PRODUCTION_FREE_EXACT_POSITION_MARKOV_CONFIRMATION_RECONSTRUCTION":
        raise SystemExit("target validation missing")
    if json.loads(SOURCE_VALIDATION.read_text())["status"] != "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":
        raise SystemExit("source validation missing")
    panel, sequences = load_joined()
    forward = orientation_metrics(panel, sequences, False)
    reversed_view = orientation_metrics(panel, sequences, True)
    if forward["events"] != reversed_view["events"] or forward["folios"] != 94:
        raise ValueError("orientation capacity")
    members = family_members()
    rows = []
    prefixes = ("forward", "reversed")
    metric_fields = tuple(next(iter(forward["metrics"].values())).keys())
    for left in range(24):
        for right in range(24):
            first = forward["metrics"][(left, right)]
            second = reversed_view["metrics"][(right, left)]
            if first["observed"] != second["observed"]:
                raise ValueError("physical pair count")
            if favored(first) and favored(second):
                label = "FAVORED_ADJACENCY"
            elif disfavored(first) and disfavored(second):
                label = "DISFAVORED_ADJACENCY"
            else:
                label = "UNRESOLVED"
            row = {
                "pair_id": ALPHABET[left] + ALPHABET[right],
                "left_family": ALPHABET[left],
                "right_family": ALPHABET[right],
                "observed_physical_count": first["observed"],
                "structural_label": label,
                "left_member_examples": ";".join(members[ALPHABET[left]][:4]),
                "right_member_examples": ";".join(members[ALPHABET[right]][:4]),
            }
            for prefix, values in zip(prefixes, (first, second)):
                for field in metric_fields:
                    row[f"{prefix}_{field}"] = values[field]
            rows.append(row)
    fields = tuple(rows[0].keys())
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    label_counts = Counter(row["structural_label"] for row in rows)
    selected = [row for row in rows if row["structural_label"] != "UNRESOLVED"]
    favored_rows = sorted(
        (row for row in selected if row["structural_label"] == "FAVORED_ADJACENCY"),
        key=lambda row: (-min(float(row["forward_log_observed_expected"]), float(row["reversed_log_observed_expected"])), row["pair_id"]),
    )
    disfavored_rows = sorted(
        (row for row in selected if row["structural_label"] == "DISFAVORED_ADJACENCY"),
        key=lambda row: (max(float(row["forward_log_observed_expected"]), float(row["reversed_log_observed_expected"])), row["pair_id"]),
    )
    compact = lambda row: {
        "pair_id": row["pair_id"],
        "observed": row["observed_physical_count"],
        "forward_log_observed_expected": row["forward_log_observed_expected"],
        "reversed_log_observed_expected": row["reversed_log_observed_expected"],
        "forward_positive_fraction": row["forward_positive_fraction"],
        "reversed_positive_fraction": row["reversed_positive_fraction"],
        "forward_negative_fraction": row["forward_negative_fraction"],
        "reversed_negative_fraction": row["reversed_negative_fraction"],
    }
    result = {
        "experiment": "SOURCE_NATIVE_HELD_FOLIO_TRANSITION_ATLAS",
        "status": "PASS_DESCRIPTIVE_CONFIRMED_TRANSITION_DECOMPOSITION",
        "inputs": {path.name: sha(path) for path in (*FROZEN, BUILDER)},
        "counts": {
            "complete_groups": len(sequences),
            "physical_folios": forward["folios"],
            "transition_events_per_orientation": forward["events"],
            "family_pairs": len(rows),
            "labels": dict(sorted(label_counts.items())),
        },
        "classification": {
            "minimum_context_opportunities_per_eligible_folio": 5,
            "minimum_eligible_folios": 12,
            "minimum_direction_fraction": 0.75,
            "favored_minimum_observed": 30,
            "favored_minimum_expected": 10,
            "favored_minimum_log_ratio": math.log(2),
            "disfavored_minimum_expected": 30,
            "disfavored_maximum_log_ratio": -math.log(2),
            "minimum_currier_opportunities": 30,
            "favored_minimum_currier_expected": 5,
            "disfavored_minimum_currier_expected": 10,
            "minimum_absolute_currier_log_ratio": math.log(1.3),
            "both_orientations_required": True,
            "separately_confirmatory": False,
        },
        "strongest_favored": [compact(row) for row in favored_rows[:16]],
        "strongest_disfavored": [compact(row) for row in disfavored_rows[:16]],
        "tsv_sha256": sha(OUT_TSV),
        "english_glosses": 0,
        "claim_ceiling": "Held-folio descriptive decomposition of the already confirmed exact-position-controlled family dependency. Labels are neutral physical-adjacency constraints, not sounds, letters, syllables, morphemes, words, syntax labels, language, cipher operations, meanings, plaintext, or translation.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    favored_text = ", ".join(row["pair_id"] for row in favored_rows[:12]) or "none"
    disfavored_text = ", ".join(row["pair_id"] for row in disfavored_rows[:12]) or "none"
    OUT_REPORT.write_text(f"""# Held-folio source-family transition atlas

Status: **{result['status']}**

Across **{forward['events']:,}** noninitial family events on **94** physical
folios, the frozen two-orientation rules classify
**{label_counts['FAVORED_ADJACENCY']}** of 576 physical pairs as favored and
**{label_counts['DISFAVORED_ADJACENCY']}** as disfavored; the rest are
unresolved. Strongest favored pairs: {favored_text}. Strongest disfavored
pairs: {disfavored_text}.

Every label requires leave-folio-out exact-position baselines, the same sign in
both physical orientations, broad folio support, and the same direction in
Currier A and B. This is a descriptive decomposition of an already confirmed
aggregate model, not 576 new confirmatory tests. Family letters are neutral STA
classes; no sound, letter, syllable, morpheme, prefix, root, suffix, word,
syntax label, language, cipher operation, meaning, plaintext, or translation
follows.
""")
    print(json.dumps({"status": result["status"], "counts": result["counts"], "favored": favored_text, "disfavored": disfavored_text}, sort_keys=True))


if __name__ == "__main__":
    main()
