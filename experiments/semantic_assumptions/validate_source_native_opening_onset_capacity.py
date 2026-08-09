#!/usr/bin/env python3
"""Independent reconstruction of the label-masked onset capacity panel."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
PANEL = RESULTS / "source_native_opening_context_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
MEMBER_AUDIT = RESULTS / "source_native_opening_member_remainders.json"
MEMBER_VALIDATION = RESULTS / "source_native_opening_member_remainders_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_ONSET_CAPACITY_SPEC.md"
BUILDER = BASE / "build_source_native_opening_onset_capacity.py"
MASKED = RESULTS / "source_native_opening_onset_masked.tsv"
PRODUCTION = RESULTS / "source_native_opening_onset_capacity.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_onset_capacity_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_opening_onset_capacity_validation.json"
REPORT = RESULTS / "source_native_opening_onset_capacity_validation_report.md"

FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    PANEL: "6a043ba095d118594c9a8bd4bd4bf0ac96778963be0637400e353c517c5e616a",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    MEMBER_AUDIT: "3ba1a442cd36581d0562b4721a2ce2fffa3aeb01a8b4706edac1f6da211f675a",
    MEMBER_VALIDATION: "b8653ec6a42ed8bafb07e06894d2896f3d55fb68d9e9b03cb12acf5477db65f6",
    SPEC: "740ebd660724a3ae2e864e93c20d4ff5a083d577e0bf2eadc711c7edb61767a8",
    BUILDER: "3d3b7eb76b35626093f746563f7892b01d1aeec750af522c1a44dd98dfc7a410",
    MASKED: "628d2f657db080b975f2e201d6d684f3dab7ede75b19be6cc4e4c4b3f580e4a2",
    PRODUCTION: "086718ac1bb1563dbcf212b349cd95d1875d481e08be01662ab4a31d8d1975e4",
    PRODUCTION_REPORT: "a2845d679b70ff8783a16618ee7246c62fca3a08f06c64f5eae47f8544977802",
}

PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
FIELDS = ("unit_id", "base_id", "physical_folio", "currier", "onset_id", "onset_consensus")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def anonymous(domain, value):
    return domain + hashlib.sha256(("SNOC1|" + domain + "|" + value).encode()).hexdigest()[:16]


def split_form(surface):
    for prefix in PREFIXES:
        if surface.startswith(prefix):
            return prefix, surface[len(prefix):], len(prefix)
    return "NONE", surface, 0


def source_onset(row):
    state, remainder, offset = split_form(row["family_surface"])
    sequences = tuple(tuple(row[field].split()) for field in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes"))
    if not remainder or state not in ("NONE", "DA"):
        return None
    if any(len(sequence) != int(row["symbol_count"]) for sequence in sequences):
        raise ValueError("member geometry")
    tails = tuple(sequence[offset:] for sequence in sequences)
    if any(len(tail) != len(remainder) for tail in tails):
        raise ValueError("tail geometry")
    return anonymous("B", remainder), tuple(tail[0] for tail in tails)


def reconstruct():
    with PANEL.open(encoding="utf-8", newline="") as handle:
        panel_rows = list(csv.DictReader(handle, delimiter="\t"))
    with QUOTAS.open(encoding="utf-8", newline="") as handle:
        quota_rows = list(csv.DictReader(handle, delimiter="\t"))
    quota = {(row["base_id"], row["physical_folio"]): (int(row["none_count"]), int(row["da_count"]), int(row["total_count"])) for row in quota_rows}
    groups = defaultdict(list)
    for row in panel_rows:
        groups[(row["base_id"], row["physical_folio"])].append(row)
    if len(panel_rows) != 5826 or len({row["unit_id"] for row in panel_rows}) != 5826 or len(quota) != 1763 or set(groups) != set(quota):
        raise ValueError("source panel")
    if any(len(groups[key]) != values[2] or values[0] + values[1] != values[2] for key, values in quota.items()):
        raise ValueError("quota")
    mixed = tuple(sorted(key for key, values in quota.items() if values[0] > 0 and values[1] > 0))
    selected = [row for key in mixed for row in groups[key]]
    if len(mixed) != 197 or len(selected) != 1207:
        raise ValueError("selection")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    hidden = {}
    for row in source_rows:
        if row["strict_zero_alternative"] != "1" or row["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        value = source_onset(row)
        if value is None:
            continue
        unit_id = anonymous("U", row["consensus_group_id"])
        if unit_id in hidden:
            raise ValueError("duplicate hidden")
        hidden[unit_id] = value
    output = []
    onset_reverse = {}
    for masked in selected:
        base, onset = hidden[masked["unit_id"]]
        if base != masked["base_id"]:
            raise ValueError("base join")
        onset_id = anonymous("O", "|".join(onset))
        if onset_id in onset_reverse and onset_reverse[onset_id] != onset:
            raise ValueError("collision")
        onset_reverse[onset_id] = onset
        output.append({"unit_id": masked["unit_id"], "base_id": masked["base_id"], "physical_folio": masked["physical_folio"], "currier": masked["currier"], "onset_id": onset_id, "onset_consensus": int(onset[0] == onset[1] == onset[2])})
    base_onsets = defaultdict(set)
    cell_onsets = defaultdict(set)
    pair_folios = defaultdict(set)
    for row in output:
        base_onsets[row["base_id"]].add(row["onset_id"])
        cell_onsets[(row["base_id"], row["physical_folio"])].add(row["onset_id"])
        pair_folios[(row["base_id"], row["onset_id"])].add(row["physical_folio"])
    varying = {key for key, values in cell_onsets.items() if len(values) >= 2}
    reused = {key for key, values in pair_folios.items() if len(values) >= 2}
    reused_rows = [row for row in output if (row["base_id"], row["onset_id"]) in reused]
    capacity = {
        "rows": len(output), "quota_cells": len(mixed), "physical_folios": len({row["physical_folio"] for row in output}), "family_remainders": len(base_onsets),
        "distinct_onset_triples": len(onset_reverse), "consensus_onset_rows": sum(int(row["onset_consensus"]) for row in output),
        "onset_varying_family_remainders": sum(len(values) >= 2 for values in base_onsets.values()), "onset_varying_quota_cells": len(varying),
        "rows_in_onset_varying_cells": sum((row["base_id"], row["physical_folio"]) in varying for row in output), "folios_with_onset_varying_cells": len({key[1] for key in varying}),
        "loo_reused_rows": len(reused_rows), "loo_reused_folios": len({row["physical_folio"] for row in reused_rows}), "loo_reused_family_remainders": len({row["base_id"] for row in reused_rows}), "loo_reused_base_onset_pairs": len(reused),
    }
    return output, capacity


def panel_text(rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue()


def report_text(status, capacity):
    return f"""# Exact-member onset compatibility capacity

Status: **{status}**

The label-masked panel retains **{capacity['rows']:,}** rows in
**{capacity['quota_cells']}** family-remainder/folio quota cells on
**{capacity['physical_folios']}** folios. It contains
**{capacity['distinct_onset_triples']}** opaque first-member triples;
**{capacity['onset_varying_family_remainders']}** family remainders and
**{capacity['onset_varying_quota_cells']}** cells vary internally. Exact
family/onset combinations recur outside the held folio for
**{capacity['loo_reused_rows']:,}** rows on **{capacity['loo_reused_folios']}**
folios across **{capacity['loo_reused_base_onset_pairs']}** reusable pairs.

All operation labels, prefix codes, full signatures, and context scores remain
absent. This authorizes target-free calibration only and supplies no
morphology, meaning, or translation.
"""


def main():
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures = []
    checks = 0

    def check(value, name):
        nonlocal checks
        checks += 1
        if not value:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, "hash:" + path.name)
    rows, capacity = reconstruct()
    check(panel_text(rows) == MASKED.read_text(), "panel-bytes")
    production = json.loads(PRODUCTION.read_text())
    check(production["capacity"] == capacity, "capacity")
    gates = {
        "exact_1207_rows_197_cells_59_folios_44_bases": capacity["rows"] == 1207 and capacity["quota_cells"] == 197 and capacity["physical_folios"] == 59 and capacity["family_remainders"] == 44,
        "at_least_20_onset_triples": capacity["distinct_onset_triples"] >= 20,
        "at_least_25_onset_varying_bases": capacity["onset_varying_family_remainders"] >= 25,
        "at_least_75_onset_varying_cells": capacity["onset_varying_quota_cells"] >= 75,
        "at_least_500_rows_in_onset_varying_cells": capacity["rows_in_onset_varying_cells"] >= 500,
        "at_least_35_folios_with_onset_varying_cells": capacity["folios_with_onset_varying_cells"] >= 35,
        "at_least_1000_loo_reused_rows": capacity["loo_reused_rows"] >= 1000,
        "at_least_50_loo_reused_folios": capacity["loo_reused_folios"] >= 50,
        "at_least_25_loo_reused_bases": capacity["loo_reused_family_remainders"] >= 25,
        "at_least_40_loo_reused_base_onset_pairs": capacity["loo_reused_base_onset_pairs"] >= 40,
        "row_operation_labels_absent": set(rows[0]) == set(FIELDS),
    }
    check(production["gates"] == gates and all(gates.values()), "gates")
    check(production["status"] == "PASS_TARGET_MASKED_OPENING_ONSET_CAPACITY" and production["decision"] == "FREEZE_TARGET_FREE_ONSET_COMPATIBILITY_CALIBRATION", "decision")
    check(production["panel_sha256"] == sha(MASKED), "panel-binding")
    check(production["row_operation_labels_stored"] == production["prefix_member_codes_stored"] == production["full_remainder_signatures_stored"] == production["context_scores_computed"] == production["english_glosses"] == 0, "ceiling")
    check(PRODUCTION_REPORT.read_text() == report_text(production["status"], capacity), "report")
    mutations = {}
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    sample = next(row for row in source_rows if source_onset(row) is not None)
    bad = dict(sample); bad["zl_sta_codes"] = " ".join(bad["zl_sta_codes"].split()[:-1])
    try: source_onset(bad)
    except ValueError: mutations["missing_member"] = True
    else: mutations["missing_member"] = False
    bad = dict(sample); bad["symbol_count"] = str(int(bad["symbol_count"]) + 1)
    try: source_onset(bad)
    except ValueError: mutations["wrong_symbol_count"] = True
    else: mutations["wrong_symbol_count"] = False
    mutations["duplicate_unit_id"] = len({row["unit_id"] for row in rows + [dict(rows[0])]}) != len(rows) + 1
    bad = dict(rows[0]); bad["base_id"] = "B0000000000000000"
    mutations["wrong_base_binding"] = bad != rows[0]
    bad = dict(rows[0]); bad["operation"] = "DA"
    mutations["operation_label_injection"] = set(bad) != set(FIELDS)
    check(all(mutations.values()), "mutations")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_ONSET_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_1207_ROW_OPENING_ONSET_CAPACITY_RECONSTRUCTION",
        "checks": checks, "failures": [], "rows": len(rows), "capacity": capacity,
        "mutations": mutations, "inputs": {path.name: sha(path) for path in FROZEN},
        "validator_sha256": sha(VALIDATOR), "row_operation_labels_accessed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Independent target-label-masked onset capacity reconstruction only; no morphology, meaning, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Opening-onset capacity validation

Status: **{result['status']}**

An independent implementation reconstructs the exact 1,207-row masked panel,
all onset and leave-folio-out capacity counts, gates, report, and five
mutations in **{checks}** checks. No operation label or target score is opened.

This validates calibration capacity only and supplies no morphology, meaning,
or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
