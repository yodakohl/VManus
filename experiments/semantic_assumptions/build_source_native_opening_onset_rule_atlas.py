#!/usr/bin/env python3
"""Build the complete descriptive rule table behind the confirmed onset result."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
PANEL = RESULTS / "source_native_opening_onset_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
TARGET_VALIDATION = RESULTS / "source_native_opening_onset_target_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_ONSET_RULE_ATLAS_SPEC.md"
BUILDER = Path(__file__).resolve()
PAIR_TSV = RESULTS / "source_native_opening_onset_rule_pairs.tsv"
ONSET_TSV = RESULTS / "source_native_opening_onset_rule_states.tsv"
OUT = RESULTS / "source_native_opening_onset_rule_atlas.json"
REPORT = RESULTS / "source_native_opening_onset_rule_atlas_report.md"

FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    PANEL: "628d2f657db080b975f2e201d6d684f3dab7ede75b19be6cc4e4c4b3f580e4a2",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    TARGET_VALIDATION: "4de622cdb7e0d79466931ce6dfb49ec1d9ba062393575ffe91d9a8d1a2e4c812",
    SPEC: "ca880279bcc9cbdaf84dc4032b818dd59a2ab48e19849963fe23c5902b2e1825",
}

PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
PAIR_FIELDS = (
    "family_remainder", "onset_triplet", "onset_consensus", "rows", "folios",
    "none", "da", "raw_da_fraction", "expected_da_fraction",
    "residual_da_fraction", "positive_cells", "zero_cells", "negative_cells",
    "loo_reusable", "loo_rows",
)
ONSET_FIELDS = (
    "onset_triplet", "onset_consensus", "bases", "rows", "folios", "none",
    "da", "raw_da_fraction", "expected_da_fraction", "residual_da_fraction",
    "positive_bases", "zero_bases", "negative_bases",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def operation(surface: str) -> tuple[str, str, int]:
    for prefix in PREFIXES:
        if surface.startswith(prefix):
            return prefix, surface[len(prefix):], len(prefix)
    return "NONE", surface, 0


def ratio(value: Fraction) -> str:
    return f"{value.numerator}/{value.denominator}"


def sign_counts(values) -> tuple[int, int, int]:
    values = list(values)
    return sum(value > 0 for value in values), sum(value == 0 for value in values), sum(value < 0 for value in values)


def main() -> None:
    if any(path.exists() for path in (PAIR_TSV, ONSET_TSV, OUT, REPORT)):
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    validation = json.loads(TARGET_VALIDATION.read_text())
    if validation["status"] != "PASS_PRODUCTION_FREE_OPENING_ONSET_TARGET_RECONSTRUCTION" or not validation["summary"]["PASS"]:
        raise ValueError("confirmed predecessor")

    with PANEL.open(encoding="utf-8", newline="") as handle:
        panel_rows = list(csv.DictReader(handle, delimiter="\t"))
    with QUOTAS.open(encoding="utf-8", newline="") as handle:
        quota_rows = list(csv.DictReader(handle, delimiter="\t"))
    quota = {(row["base_id"], row["physical_folio"]): (int(row["da_count"]), int(row["total_count"])) for row in quota_rows if int(row["none_count"]) and int(row["da_count"])}
    if len(panel_rows) != 1207 or len({row["unit_id"] for row in panel_rows}) != 1207 or len(quota_rows) != 1763 or len(quota) != 197:
        raise ValueError("panel geometry")

    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(source_rows) != 26184 or len({row["consensus_group_id"] for row in source_rows}) != 26184:
        raise ValueError("source geometry")
    hidden = {}
    for row in source_rows:
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        state, remainder, strip = operation(row["family_surface"])
        if not remainder or state not in {"NONE", "DA"}:
            continue
        sequences = tuple(tuple(row[field].split()) for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes"))
        if any(len(sequence) != int(row["symbol_count"]) for sequence in sequences):
            raise ValueError("member geometry")
        tails = tuple(sequence[strip:] for sequence in sequences)
        if any(len(tail) != len(remainder) for tail in tails):
            raise ValueError("remainder geometry")
        onset = tuple(tail[0] for tail in tails)
        unit_id = opaque("U", row["consensus_group_id"])
        if unit_id in hidden:
            raise ValueError("hidden identity")
        hidden[unit_id] = {
            "state": state,
            "remainder": remainder,
            "base_id": opaque("B", remainder),
            "onset": onset,
            "onset_id": opaque("O", "|".join(onset)),
        }

    joined = []
    cell_rows: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in panel_rows:
        if row["unit_id"] not in hidden:
            raise ValueError("target join")
        value = hidden[row["unit_id"]]
        if value["base_id"] != row["base_id"] or value["onset_id"] != row["onset_id"] or str(int(len(set(value["onset"])) == 1)) != row["onset_consensus"]:
            raise ValueError("binding drift")
        record = {**row, **value, "folio": row["physical_folio"]}
        joined.append(record)
        cell_rows[(row["base_id"], row["physical_folio"])].append(record)
    if set(cell_rows) != set(quota) or Counter(row["state"] for row in joined) != Counter({"NONE": 892, "DA": 315}):
        raise ValueError("target geometry")
    for key, records in cell_rows.items():
        if len(records) != quota[key][1] or sum(record["state"] == "DA" for record in records) != quota[key][0]:
            raise ValueError("quota drift")

    pair_groups: dict[tuple[str, tuple[str, str, str]], list[dict]] = defaultdict(list)
    onset_groups: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for record in joined:
        pair_groups[(record["remainder"], record["onset"])].append(record)
        onset_groups[record["onset"]].append(record)
    if len(pair_groups) != 95 or len(onset_groups) != 25 or len({row["remainder"] for row in joined}) != 44:
        raise ValueError("rule inventory")

    pair_rows = []
    pair_residuals: dict[tuple[str, tuple[str, str, str]], Fraction] = {}
    for key in sorted(pair_groups, key=lambda value: (value[0], value[1])):
        records = pair_groups[key]
        by_cell: dict[tuple[str, str], list[dict]] = defaultdict(list)
        for record in records:
            by_cell[(record["base_id"], record["folio"])].append(record)
        cell_residuals = []
        expected = Fraction(0)
        for cell, cell_pair_rows in by_cell.items():
            cell_expected = Fraction(len(cell_pair_rows) * quota[cell][0], quota[cell][1])
            expected += cell_expected
            cell_residuals.append(Fraction(sum(row["state"] == "DA" for row in cell_pair_rows)) - cell_expected)
        da = sum(record["state"] == "DA" for record in records)
        residual = Fraction(da) - expected
        pair_residuals[key] = residual
        positive, zero, negative = sign_counts(cell_residuals)
        folios = len({record["folio"] for record in records})
        reusable = folios >= 2
        pair_rows.append({
            "family_remainder": key[0],
            "onset_triplet": "/".join(key[1]),
            "onset_consensus": str(int(len(set(key[1])) == 1)),
            "rows": str(len(records)),
            "folios": str(folios),
            "none": str(len(records) - da),
            "da": str(da),
            "raw_da_fraction": ratio(Fraction(da, len(records))),
            "expected_da_fraction": ratio(expected),
            "residual_da_fraction": ratio(residual),
            "positive_cells": str(positive),
            "zero_cells": str(zero),
            "negative_cells": str(negative),
            "loo_reusable": str(int(reusable)),
            "loo_rows": str(len(records) if reusable else 0),
        })

    onset_rows = []
    for onset in sorted(onset_groups):
        records = onset_groups[onset]
        keys = {(record["remainder"], onset) for record in records}
        expected = Fraction(0)
        for record in records:
            cell = record["base_id"], record["folio"]
            expected += Fraction(quota[cell][0], quota[cell][1])
        da = sum(record["state"] == "DA" for record in records)
        residual = Fraction(da) - expected
        base_residual = defaultdict(Fraction)
        for key in keys:
            base_residual[key[0]] += pair_residuals[key]
        positive, zero, negative = sign_counts(base_residual.values())
        onset_rows.append({
            "onset_triplet": "/".join(onset),
            "onset_consensus": str(int(len(set(onset)) == 1)),
            "bases": str(len({record["remainder"] for record in records})),
            "rows": str(len(records)),
            "folios": str(len({record["folio"] for record in records})),
            "none": str(len(records) - da),
            "da": str(da),
            "raw_da_fraction": ratio(Fraction(da, len(records))),
            "expected_da_fraction": ratio(expected),
            "residual_da_fraction": ratio(residual),
            "positive_bases": str(positive),
            "zero_bases": str(zero),
            "negative_bases": str(negative),
        })

    with PAIR_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PAIR_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(pair_rows)
    with ONSET_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=ONSET_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(onset_rows)

    base_directions = defaultdict(set)
    for (base, _), residual in pair_residuals.items():
        if residual:
            base_directions[base].add(1 if residual > 0 else -1)
    residual_signs = sign_counts(pair_residuals.values())
    strongest = sorted(pair_groups, key=lambda key: (-abs(pair_residuals[key]), key[0], key[1]))[:12]
    strongest_rows = [
        {"family_remainder": base, "onset_triplet": "/".join(onset), "residual_da_fraction": ratio(pair_residuals[(base, onset)])}
        for base, onset in strongest
    ]
    summary = {
        "rows": len(joined),
        "quota_cells": len(cell_rows),
        "family_remainders": len({row["remainder"] for row in joined}),
        "base_onset_pairs": len(pair_rows),
        "onset_triplets": len(onset_rows),
        "none_rows": sum(row["state"] == "NONE" for row in joined),
        "da_rows": sum(row["state"] == "DA" for row in joined),
        "loo_reusable_rows": sum(int(row["loo_rows"]) for row in pair_rows),
        "positive_pair_residuals": residual_signs[0],
        "zero_pair_residuals": residual_signs[1],
        "negative_pair_residuals": residual_signs[2],
        "bases_with_both_residual_directions": sum(values == {1, -1} for values in base_directions.values()),
        "deterministic_pair_states": sum(int(row["da"]) in {0, int(row["rows"])} for row in pair_rows),
        "onsets_shared_across_bases": sum(int(row["bases"]) >= 2 for row in onset_rows),
    }
    gates = {
        "exact_1207_rows_197_cells_44_bases": summary["rows"] == 1207 and summary["quota_cells"] == 197 and summary["family_remainders"] == 44,
        "exact_892_NONE_315_DA": summary["none_rows"] == 892 and summary["da_rows"] == 315,
        "exact_95_pairs_25_onsets": summary["base_onset_pairs"] == 95 and summary["onset_triplets"] == 25,
        "exact_1141_loo_reusable_rows": summary["loo_reusable_rows"] == 1141,
        "all_quotas_exact": all(len(records) == quota[key][1] and sum(record["state"] == "DA" for record in records) == quota[key][0] for key, records in cell_rows.items()),
        "no_event_identity_output": all("unit" not in field and "locus" not in field and "page" not in field for field in (*PAIR_FIELDS, *ONSET_FIELDS)),
    }
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_ONSET_RULE_ATLAS",
        "status": "PASS_COMPLETE_POST_CONFIRMATION_RULE_ATLAS" if all(gates.values()) else "STOP_RULE_ATLAS",
        "decision": "USE_COMPLETE_TABLE_FOR_MECHANISM_DESIGN_ONLY" if all(gates.values()) else "DO_NOT_USE_RULE_ATLAS",
        "inputs": {path.name: sha(path) for path in (*FROZEN, BUILDER)},
        "summary": summary,
        "strongest_absolute_pair_residuals": strongest_rows,
        "gates": gates,
        "pair_tsv_sha256": sha(PAIR_TSV),
        "onset_tsv_sha256": sha(ONSET_TSV),
        "unit_locus_page_identities_stored": 0,
        "english_glosses": 0,
        "claim_ceiling": "Complete post-confirmation descriptive decomposition of the confirmed within-base onset compatibility only; no new confirmation, allomorphy, harmony, orthography, morphology, pronunciation, wordhood, POS, syntax, language, cipher operation, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    strongest_text = ", ".join(f"`{row['family_remainder']} | {row['onset_triplet']}` ({row['residual_da_fraction']})" for row in strongest_rows)
    REPORT.write_text(f"""# Complete opening/onset rule atlas

Status: **{result['status']}**

All **{summary['rows']:,}** frozen rows decompose into
**{summary['base_onset_pairs']}** exact base/onset states and
**{summary['onset_triplets']}** onset triplets. Relative to exact base/folio
quotas, pair residuals are positive/zero/negative in
**{summary['positive_pair_residuals']} / {summary['zero_pair_residuals']} /
{summary['negative_pair_residuals']}** states; **{summary['bases_with_both_residual_directions']}**
bases contain both directions. **{summary['deterministic_pair_states']}** pair
states have raw `DA` rate zero or one, without a minimum-support claim.

The twelve largest absolute quota residuals are: {strongest_text}.

This is complete descriptive localization of the already confirmed formal
compatibility. It supplies no allomorphy, harmony, morphology, meaning,
plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "summary": summary, "strongest": strongest_rows}, sort_keys=True))


if __name__ == "__main__":
    main()
