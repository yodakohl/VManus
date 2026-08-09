#!/usr/bin/env python3
"""Build a row-label-masked context panel for exact NONE/DA remainder pairs."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
CAPACITY = RESULTS / "source_native_opening_operation_capacity.json"
CAPACITY_VALIDATION = RESULTS / "source_native_opening_operation_capacity_validation.json"
SPEC = BASE / "SOURCE_NATIVE_OPENING_CONTEXT_PANEL_SPEC.md"
BUILDER = Path(__file__).resolve()
PANEL = RESULTS / "source_native_opening_context_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
OUT = RESULTS / "source_native_opening_context_capacity.json"
REPORT = RESULTS / "source_native_opening_context_capacity_report.md"
FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    CAPACITY: "0c1fcac00d1b5934d43acf5e265d79ef876ee08401cfe78695936fccbf903dc7",
    CAPACITY_VALIDATION: "5bf3d6f9d8b5503f2f169ab268cf99edef0858e4d5d409a753c38574fa1755eb",
    SPEC: "68e7c2f35015b1d75071af2a00eb00e80120748f87bb8083d81583980d1809c3",
}
PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
PANEL_FIELDS = ("unit_id", "base_id", "physical_folio", "section", "currier", "kind", "group_count", "locus_role", "left_context", "right_context")
QUOTA_FIELDS = ("base_id", "physical_folio", "none_count", "da_count", "total_count")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError("page")
    return match.group(1)


def operation(surface: str) -> tuple[str, str]:
    for prefix in PREFIXES:
        if surface.startswith(prefix):
            return prefix, surface[len(prefix):]
    return "NONE", surface


def locus_role(index: int, count: int) -> str:
    if count == 1:
        return "SINGLE"
    if index == 1:
        return "FIRST"
    if index == count:
        return "LAST"
    return "MIDDLE"


def main() -> None:
    if any(path.exists() for path in (PANEL, QUOTAS, OUT, REPORT)):
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    capacity = json.loads(CAPACITY.read_text())
    validation = json.loads(CAPACITY_VALIDATION.read_text())
    if capacity["selected_operation_pair"] != "NONE__DA" or validation["status"] != "PASS_INDEPENDENT_10_PAIR_OPENING_CAPACITY_RECONSTRUCTION":
        raise SystemExit("capacity binding")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(source_rows) != 26184 or len({row["consensus_group_id"] for row in source_rows}) != 26184:
        raise SystemExit("source identity")
    prose = [row for row in source_rows if row["strict_zero_alternative"] == "1" and row["grammar_scope"] == "CONFIRMED_PROSE"]
    by_base = defaultdict(lambda: defaultdict(list))
    classified = {}
    for row in prose:
        state, base = operation(row["family_surface"])
        classified[row["consensus_group_id"]] = (state, base)
        if base and state in {"NONE", "DA"}:
            by_base[base][state].append(row)
    retained_bases = {
        base for base, states in by_base.items()
        if len({physical_folio(row["page"]) for row in states["NONE"]}) >= 2
        and len({physical_folio(row["page"]) for row in states["DA"]}) >= 2
    }
    if len(retained_bases) != 53:
        raise SystemExit("retained bases")
    base_ids = {base: opaque("B", base) for base in retained_bases}
    if len(set(base_ids.values())) != len(base_ids):
        raise SystemExit("base hash collision")
    by_locus_index = {}
    for row in source_rows:
        key = (row["locus"], int(row["consensus_group_index"]))
        if key in by_locus_index:
            raise SystemExit("duplicate locus index")
        by_locus_index[key] = row

    def neighbor(row, offset):
        index = int(row["consensus_group_index"])
        count = int(row["consensus_group_count"])
        if offset < 0 and index == 1:
            return "START"
        if offset > 0 and index == count:
            return "END"
        adjacent = by_locus_index.get((row["locus"], index + offset))
        if adjacent is None or adjacent["strict_zero_alternative"] != "1" or not adjacent["family_surface"]:
            return "AMBIGUOUS"
        return adjacent["family_surface"][-1] if offset < 0 else adjacent["family_surface"][0]

    panel_rows = []
    labels = {}
    for base in retained_bases:
        for state in ("NONE", "DA"):
            for row in by_base[base][state]:
                unit_id = opaque("U", row["consensus_group_id"])
                if unit_id in labels:
                    raise SystemExit("unit hash collision")
                labels[unit_id] = state
                index = int(row["consensus_group_index"])
                count = int(row["consensus_group_count"])
                panel_rows.append({
                    "unit_id": unit_id,
                    "base_id": base_ids[base],
                    "physical_folio": physical_folio(row["page"]),
                    "section": row["section"],
                    "currier": row["currier"],
                    "kind": row["kind"],
                    "group_count": count,
                    "locus_role": locus_role(index, count),
                    "left_context": neighbor(row, -1),
                    "right_context": neighbor(row, 1),
                })
    panel_rows.sort(key=lambda row: row["unit_id"])
    quotas = Counter((row["base_id"], row["physical_folio"], labels[row["unit_id"]]) for row in panel_rows)
    quota_keys = sorted({(base, folio) for base, folio, _ in quotas})
    quota_rows = [{
        "base_id": base,
        "physical_folio": folio,
        "none_count": quotas[(base, folio, "NONE")],
        "da_count": quotas[(base, folio, "DA")],
        "total_count": quotas[(base, folio, "NONE")] + quotas[(base, folio, "DA")],
    } for base, folio in quota_keys]
    mixed = [row for row in quota_rows if row["none_count"] and row["da_count"]]
    movable = sum(row["total_count"] for row in mixed)
    folios = {row["physical_folio"] for row in panel_rows}
    label_counts = Counter(labels.values())
    register_counts = {currier: sum(row["currier"] == currier for row in panel_rows) for currier in ("A", "B")}
    gates = {
        "at_least_500_rows": len(panel_rows) >= 500,
        "at_least_40_remainders": len(retained_bases) >= 40,
        "at_least_50_folios": len(folios) >= 50,
        "at_least_20_mixed_quota_strata": len(mixed) >= 20,
        "at_least_200_movable_rows": movable >= 200,
        "row_labels_absent_from_panel": set(panel_rows[0]) == set(PANEL_FIELDS),
    }
    status = "PASS_TARGET_MASKED_OPENING_CONTEXT_CAPACITY" if all(gates.values()) else "STOP_OPENING_CONTEXT_PANEL_CAPACITY"
    with PANEL.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=PANEL_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(panel_rows)
    with QUOTAS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=QUOTA_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(quota_rows)
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_CONTEXT_PANEL",
        "status": status,
        "decision": "FREEZE_TARGET_FREE_CONTEXT_CALIBRATION" if all(gates.values()) else "DO_NOT_CALIBRATE_CONTEXT_TEST",
        "inputs": {path.name: sha(path) for path in (*FROZEN, BUILDER)},
        "rows": len(panel_rows),
        "exact_remainders": len(retained_bases),
        "physical_folios": len(folios),
        "label_totals_only": {"DA": label_counts["DA"], "NONE": label_counts["NONE"]},
        "currier_row_counts": register_counts,
        "quota_strata": len(quota_rows),
        "mixed_quota_strata": len(mixed),
        "movable_rows": movable,
        "left_context_counts": dict(sorted(Counter(row["left_context"] for row in panel_rows).items())),
        "right_context_counts": dict(sorted(Counter(row["right_context"] for row in panel_rows).items())),
        "locus_role_counts": dict(sorted(Counter(row["locus_role"] for row in panel_rows).items())),
        "gates": gates,
        "panel_sha256": sha(PANEL),
        "quotas_sha256": sha(QUOTAS),
        "row_operation_labels_stored": 0,
        "context_scores_computed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Target-masked geometry and label quotas for synthetic calibration only; no detachment, wordhood, prefix function, syntax, sound, language, cipher, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUTCOME = "passing" if all(gates.values()) else "stopped"
    REPORT.write_text(f"""# Opening-context masked panel

Status: **{status}**

The 53 replicated exact remainders retain **{len(panel_rows):,}** anonymous rows
on **{len(folios)}** folios: **{label_counts['NONE']:,}** `NONE` and
**{label_counts['DA']:,}** `DA` labels in aggregate only. The separate quota
table has **{len(quota_rows):,}** base-folio strata, of which **{len(mixed):,}**
are mixed and contain **{movable:,}** movable rows. All capacity gates are
**{OUTCOME}**.

No row operation label or context score is stored. This authorizes synthetic
calibration only and supplies no detachment, wordhood, prefix function, syntax,
sound, language, cipher, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": status, "rows": len(panel_rows), "mixed_strata": len(mixed), "movable_rows": movable}, sort_keys=True))


if __name__ == "__main__":
    main()
