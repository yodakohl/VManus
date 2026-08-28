#!/usr/bin/env python3
"""Reconstruct the post-run identifiability and method diagnostics for GDT612."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ART = EXP / "artifacts"
PACKS = ART / "reference_packs"


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, fields, rows):
    with (ART / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=fields, delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def load_key(language: str, seed: str):
    directory = ART / f"keys/target/{language}/seed_{seed}"
    return read_tsv(directory / "primitive_mapping.tsv"), read_tsv(
        directory / "merge_overrides.tsv"
    )


def main():
    units = {int(row["unit_id"]): row for row in read_tsv(ART / "units.tsv")}
    primitive_unit = {
        int(row["primitive_id"]): int(row["unit_id"])
        for row in units.values()
        if row["is_primitive"] == "1"
    }
    truth_primitives = read_tsv(ART / "synthetic_truth_primitives.tsv")
    truth_overrides = read_tsv(ART / "synthetic_truth_overrides.tsv")

    train_counts = Counter()
    for row in read_tsv(ART / "synthetic_train_chunks.tsv"):
        for uid in map(int, row["units"].split(",")):
            train_counts[uid] += int(row["count"])
    held_counts = Counter()
    for row in read_tsv(ART / "synthetic_held.tsv"):
        held_counts.update(map(int, row["units"].split(",")))

    exposure = []
    for row in truth_primitives:
        uid = primitive_unit[int(row["primitive_id"])]
        exposure.append(
            {
                "truth_level": "primitive",
                "id": row["primitive_id"],
                "unit_id": uid,
                "unit": row["primitive"],
                "role_or_type": row["role"],
                "output": row["output"],
                "train_direct_events": train_counts[uid],
                "held_direct_events": held_counts[uid],
                "recoverable_from_train_directly": int(train_counts[uid] > 0),
            }
        )
    for row in truth_overrides:
        uid = int(row["unit_id"])
        exposure.append(
            {
                "truth_level": "override",
                "id": row["unit_id"],
                "unit_id": uid,
                "unit": row["unit"],
                "role_or_type": row["type"],
                "output": row["output"],
                "train_direct_events": train_counts[uid],
                "held_direct_events": held_counts[uid],
                "recoverable_from_train_directly": int(train_counts[uid] > 0),
            }
        )
    write_tsv("synthetic_truth_exposure.tsv", list(exposure[0]), exposure)

    by_output = defaultdict(list)
    for row in truth_primitives:
        if row["output"] != "<EMPTY>":
            by_output[row["output"]].append(
                (
                    "primitive",
                    row["primitive"],
                    row["role"],
                    primitive_unit[int(row["primitive_id"])],
                )
            )
    for row in truth_overrides:
        by_output[row["output"]].append(
            ("override", row["unit"], row["type"], int(row["unit_id"]))
        )
    collisions = []
    for output, members in sorted(by_output.items()):
        if len(members) < 2:
            continue
        whole = [
            item
            for item in members
            if item[2] in {"connector", "wholeform_logogram", "wholeform"}
        ]
        core = [
            item
            for item in members
            if item[2] in {"literal_carrier", "syllabic_carrier", "short"}
        ]
        if len(whole) > 1:
            winner = max(whole, key=lambda item: members.index(item))
            mechanism = "exact_whole_last_write"
        elif len(core) > 1:
            winner = min(core, key=lambda item: item[3])
            mechanism = "core_dp_equal_length_lower_unit_id"
        else:
            winner = ("NA", "NA", "NA", -1)
            mechanism = "cross_role_or_structural_collision"
        collisions.append(
            {
                "output": output,
                "members": ";".join(
                    f"{level}:{unit}:{role}:uid{uid}"
                    for level, unit, role, uid in members
                ),
                "generator_collision_mechanism": mechanism,
                "generator_winner": (
                    f"{winner[0]}:{winner[1]}:{winner[2]}:uid{winner[3]}"
                ),
            }
        )
    write_tsv("synthetic_truth_collisions.tsv", list(collisions[0]), collisions)

    metrics = read_tsv(ART / "held_run_metrics.tsv")
    orientation = []
    for language in sorted({row["language"] for row in metrics}):
        for kind in ("real", "destroyed"):
            selected = [
                row
                for row in metrics
                if row["language"] == language and row["kind"] == kind
            ]
            reported = [
                float(row["held_order_signal_bits_per_letter"]) for row in selected
            ]
            objectives = [
                float(row["train_objective_per_sqrt_weight"]) for row in selected
            ]
            orientation.append(
                {
                    "language": language,
                    "kind": kind,
                    "n": len(selected),
                    "reported_real_minus_destroyed_mean": (
                        f"{sum(reported) / len(reported):.12f}"
                    ),
                    "fit_oriented_mean": (
                        f"{sum(value if kind == 'real' else -value for value in reported) / len(reported):.12f}"
                    ),
                    "train_objective_mean": (
                        f"{sum(objectives) / len(objectives):.12f}"
                    ),
                }
            )
    write_tsv("orientation_audit.tsv", list(orientation[0]), orientation)

    top_rows = []
    for metric in metrics:
        if metric["kind"] != "real":
            continue
        primitive_rows, override_rows = load_key(metric["language"], metric["seed"])
        top = metric["top_token"]
        found = next(
            (
                ("primitive", row["primitive_id"], row["role"])
                for row in primitive_rows
                if row["output"] == top
            ),
            None,
        )
        if found is None:
            found = next(
                (
                    ("override", row["unit_id"], row["type"])
                    for row in override_rows
                    if row["output"] == top
                ),
                ("composed", "NA", "NA"),
            )
        candidates = read_tsv(
            PACKS / f"{metric['language']}_real_candidates.tsv"
        )
        categories = sorted(
            {row["category"] for row in candidates if row["value"] == top}
        )
        lexicon = set(
            (PACKS / f"{metric['language']}_real_words.txt")
            .read_text(encoding="ascii")
            .splitlines()
        )
        top_rows.append(
            {
                "language": metric["language"],
                "seed": metric["seed"],
                "top_token": top,
                "top_token_fraction": metric["top_token_fraction"],
                "mapping_level": found[0],
                "mapping_id": found[1],
                "mapping_role_or_type": found[2],
                "in_real_reference_lexicon": int(top in lexicon),
                "in_candidate_categories": ",".join(categories),
            }
        )
    write_tsv("top_token_injection.tsv", list(top_rows[0]), top_rows)

    count_rows = []
    candidate_fields = [
        "literal",
        "syllabic",
        "prefix",
        "suffix",
        "connector",
        "context",
        "whole",
        "override_short",
        "override_whole",
    ]
    for language in sorted({row["language"] for row in metrics}):
        for kind in ("real", "destroyed"):
            counts = Counter(
                row["category"]
                for row in read_tsv(PACKS / f"{language}_{kind}_candidates.tsv")
            )
            count_rows.append(
                {
                    "language": language,
                    "kind": kind,
                    **{field: counts[field] for field in candidate_fields},
                    "total": sum(counts.values()),
                }
            )
    write_tsv(
        "candidate_pool_counts.tsv",
        ["language", "kind", *candidate_fields, "total"],
        count_rows,
    )

    decoder = (EXP / "src/full/decoder.cpp").read_text(encoding="utf-8")
    model = json.loads((ART / "model_v1.json").read_text(encoding="utf-8"))
    zero_train = sorted(
        f"{row['truth_level']}:{row['unit']}"
        for row in exposure
        if row["train_direct_events"] == 0
    )
    summary = {
        "status": "METHOD_AUDIT_OK",
        "synthetic_zero_train_truth_items": zero_train,
        "synthetic_zero_train_truth_item_count": len(zero_train),
        "synthetic_collision_outputs": len(collisions),
        "destroyed_fit_oriented_means_positive": all(
            float(row["fit_oriented_mean"]) > 0 for row in orientation
        ),
        "real_runs_top_token_from_connector_or_whole": sum(
            row["mapping_role_or_type"]
            in {"connector", "wholeform_logogram"}
            for row in top_rows
        ),
        "real_runs_top_token_in_reference_and_candidate_pool": sum(
            row["in_real_reference_lexicon"] == 1
            and bool(row["in_candidate_categories"])
            for row in top_rows
        ),
        "real_runs": len(top_rows),
        "implementation": {
            "copied_model_id": model["model_id"],
            "decoder_parses_model_json": "model_v1.json" in decoder,
            "hard_role_counts_present": (
                "counts = {18, 4, 3, 3, 2, 2, 1, 1}" in decoder
            ),
            "lexicon_bonus_present": "double lexicon_bonus = 0.12" in decoder,
            "exact_qok_only_guard_present": (
                'units[uid].name == "qok"' in decoder
            ),
            "whole_and_connector_share_branch": (
                "piece.role == WHOLE || piece.role == CONNECTOR" in decoder
            ),
        },
    }

    expected_missing = {
        "primitive:F",
        "primitive:K",
        "primitive:f",
        "primitive:i",
        "override:dy",
    }
    assert expected_missing <= set(zero_train)
    assert summary["destroyed_fit_oriented_means_positive"]
    assert summary["real_runs"] == 18
    assert summary["real_runs_top_token_from_connector_or_whole"] == 18
    assert summary["real_runs_top_token_in_reference_and_candidate_pool"] == 18
    assert summary["implementation"] == {
        "copied_model_id": "HISTORICAL_MIXED_ABBREVIATION_FST_34_V1",
        "decoder_parses_model_json": False,
        "hard_role_counts_present": True,
        "lexicon_bonus_present": True,
        "exact_qok_only_guard_present": True,
        "whole_and_connector_share_branch": True,
    }
    (ART / "METHOD_AUDIT.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
