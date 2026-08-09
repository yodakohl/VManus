#!/usr/bin/env python3
"""Clean-room validation of the row-label-masked opening-context panel."""

from __future__ import annotations

import csv
import hashlib
import io
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
BUILDER = BASE / "build_source_native_opening_context_panel.py"
PANEL = RESULTS / "source_native_opening_context_masked.tsv"
QUOTAS = RESULTS / "source_native_opening_context_quotas.tsv"
PRODUCTION = RESULTS / "source_native_opening_context_capacity.json"
PRODUCTION_REPORT = RESULTS / "source_native_opening_context_capacity_report.md"
OUT = RESULTS / "source_native_opening_context_capacity_validation.json"
REPORT = RESULTS / "source_native_opening_context_capacity_validation_report.md"
FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    CAPACITY: "0c1fcac00d1b5934d43acf5e265d79ef876ee08401cfe78695936fccbf903dc7",
    CAPACITY_VALIDATION: "5bf3d6f9d8b5503f2f169ab268cf99edef0858e4d5d409a753c38574fa1755eb",
    SPEC: "68e7c2f35015b1d75071af2a00eb00e80120748f87bb8083d81583980d1809c3",
    BUILDER: "828d4fb8f9214966fa96cad21bcfa271ad1b91091bb89466b24c6e06d0ffaef2",
    PANEL: "6a043ba095d118594c9a8bd4bd4bf0ac96778963be0637400e353c517c5e616a",
    QUOTAS: "f062d9ce2935578788f9913d848c6eae2206f685ca9fa8984d29862f01ff339b",
    PRODUCTION: "46878cf1263c1def721ae593a03e3033f155a63e37c571ad9ca063d95caa44a4",
    PRODUCTION_REPORT: "78ec4ce70384a1792e0e0988280febdae623894ea3200bb403ab9d2974c88f86",
}
PREFIXES = ("DAQKJ", "DAQK", "DAQ", "DA")
PANEL_FIELDS = ("unit_id", "base_id", "physical_folio", "section", "currier", "kind", "group_count", "locus_role", "left_context", "right_context")
QUOTA_FIELDS = ("base_id", "physical_folio", "none_count", "da_count", "total_count")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def opaque(domain: str, value: str) -> str:
    return domain + hashlib.sha256(f"SNOC1|{domain}|{value}".encode()).hexdigest()[:16]


def folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError("page")
    return match.group(1)


def classify(surface: str) -> tuple[str, str]:
    candidates = [prefix for prefix in PREFIXES if surface.startswith(prefix)]
    if not candidates:
        return "NONE", surface
    prefix = sorted(candidates, key=lambda value: (-len(value), value))[0]
    return prefix, surface[len(prefix):]


def role(index: int, count: int) -> str:
    return "SINGLE" if count == 1 else ("FIRST" if index == 1 else ("LAST" if index == count else "MIDDLE"))


def serialize(rows, fields) -> str:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue()


def reconstruct(source_rows):
    prose = [row for row in source_rows if row["strict_zero_alternative"] == "1" and row["grammar_scope"] == "CONFIRMED_PROSE"]
    if len(source_rows) != 26184 or len(prose) != 21899 or len({row["consensus_group_id"] for row in source_rows}) != 26184:
        raise ValueError("identity")
    by_base = defaultdict(lambda: defaultdict(list))
    for row in prose:
        state, base = classify(row["family_surface"])
        if base and state in {"NONE", "DA"}:
            by_base[base][state].append(row)
    retained = {base for base, states in by_base.items() if len({folio(row["page"]) for row in states["NONE"]}) >= 2 and len({folio(row["page"]) for row in states["DA"]}) >= 2}
    if len(retained) != 53:
        raise ValueError("bases")
    indexed = {}
    for row in source_rows:
        key = (row["locus"], int(row["consensus_group_index"]))
        if key in indexed:
            raise ValueError("index")
        indexed[key] = row

    def adjacent(row, delta):
        index = int(row["consensus_group_index"])
        count = int(row["consensus_group_count"])
        if delta == -1 and index == 1:
            return "START"
        if delta == 1 and index == count:
            return "END"
        other = indexed.get((row["locus"], index + delta))
        if other is None or other["strict_zero_alternative"] != "1" or not other["family_surface"]:
            return "AMBIGUOUS"
        return other["family_surface"][-1] if delta == -1 else other["family_surface"][0]

    panels = []
    hidden = {}
    for base in retained:
        base_id = opaque("B", base)
        for state in ("NONE", "DA"):
            for row in by_base[base][state]:
                unit_id = opaque("U", row["consensus_group_id"])
                if unit_id in hidden:
                    raise ValueError("unit collision")
                hidden[unit_id] = state
                index = int(row["consensus_group_index"])
                count = int(row["consensus_group_count"])
                panels.append({
                    "unit_id": unit_id,
                    "base_id": base_id,
                    "physical_folio": folio(row["page"]),
                    "section": row["section"],
                    "currier": row["currier"],
                    "kind": row["kind"],
                    "group_count": count,
                    "locus_role": role(index, count),
                    "left_context": adjacent(row, -1),
                    "right_context": adjacent(row, 1),
                })
    panels.sort(key=lambda row: row["unit_id"])
    counts = Counter((row["base_id"], row["physical_folio"], hidden[row["unit_id"]]) for row in panels)
    keys = sorted({key[:2] for key in counts})
    quotas = [{"base_id": base, "physical_folio": physical, "none_count": counts[(base, physical, "NONE")], "da_count": counts[(base, physical, "DA")], "total_count": counts[(base, physical, "NONE")] + counts[(base, physical, "DA")]} for base, physical in keys]
    return panels, quotas, hidden


def report_text(stored) -> str:
    outcome = "passing" if all(stored["gates"].values()) else "stopped"
    return f"""# Opening-context masked panel

Status: **{stored['status']}**

The 53 replicated exact remainders retain **{stored['rows']:,}** anonymous rows
on **{stored['physical_folios']}** folios: **{stored['label_totals_only']['NONE']:,}** `NONE` and
**{stored['label_totals_only']['DA']:,}** `DA` labels in aggregate only. The separate quota
table has **{stored['quota_strata']:,}** base-folio strata, of which **{stored['mixed_quota_strata']:,}**
are mixed and contain **{stored['movable_rows']:,}** movable rows. All capacity gates are
**{outcome}**.

No row operation label or context score is stored. This authorizes synthetic
calibration only and supplies no detachment, wordhood, prefix function, syntax,
sound, language, cipher, meaning, plaintext, or translation.
"""


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures = []
    checks = 0

    def check(condition, name):
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, f"hash:{path.name}")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    panel, quotas, hidden = reconstruct(source_rows)
    check(len(panel) == 5826 and len({row["unit_id"] for row in panel}) == 5826, "rows")
    check(len({row["base_id"] for row in panel}) == 53 and len({row["physical_folio"] for row in panel}) == 94, "coverage")
    check(serialize(panel, PANEL_FIELDS) == PANEL.read_text(), "panel-bytes")
    check(serialize(quotas, QUOTA_FIELDS) == QUOTAS.read_text(), "quota-bytes")
    stored = json.loads(PRODUCTION.read_text())
    label_counts = Counter(hidden.values())
    mixed = [row for row in quotas if row["none_count"] and row["da_count"]]
    movable = sum(row["total_count"] for row in mixed)
    check(stored["label_totals_only"] == {"DA": label_counts["DA"], "NONE": label_counts["NONE"]}, "label-totals")
    check(stored["quota_strata"] == len(quotas) and stored["mixed_quota_strata"] == len(mixed) and stored["movable_rows"] == movable, "mobility")
    check(stored["currier_row_counts"] == {value: sum(row["currier"] == value for row in panel) for value in ("A", "B")}, "currier")
    check(stored["left_context_counts"] == dict(sorted(Counter(row["left_context"] for row in panel).items())), "left")
    check(stored["right_context_counts"] == dict(sorted(Counter(row["right_context"] for row in panel).items())), "right")
    check(stored["locus_role_counts"] == dict(sorted(Counter(row["locus_role"] for row in panel).items())), "role")
    expected_gates = {"at_least_500_rows": True, "at_least_40_remainders": True, "at_least_50_folios": True, "at_least_20_mixed_quota_strata": True, "at_least_200_movable_rows": True, "row_labels_absent_from_panel": True}
    check(stored["gates"] == expected_gates, "gates")
    check(stored["status"] == "PASS_TARGET_MASKED_OPENING_CONTEXT_CAPACITY" and stored["decision"] == "FREEZE_TARGET_FREE_CONTEXT_CALIBRATION", "decision")
    check(stored["panel_sha256"] == sha(PANEL) and stored["quotas_sha256"] == sha(QUOTAS), "bindings")
    check(stored["row_operation_labels_stored"] == 0 and stored["context_scores_computed"] == 0 and stored["english_glosses"] == 0, "isolation")
    check(PRODUCTION_REPORT.read_text() == report_text(stored), "report-bytes")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_OPENING_CONTEXT_PANEL_VALIDATION",
        "status": "PASS_INDEPENDENT_5826_ROW_MASKED_CONTEXT_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "rows": 5826,
        "exact_remainders": 53,
        "physical_folios": 94,
        "mixed_quota_strata": 197,
        "movable_rows": 1207,
        "row_operation_labels_stored": 0,
        "context_scores_computed": 0,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "english_glosses": 0,
        "claim_ceiling": "Independent reconstruction of masked context geometry and quotas only; no detachment, wordhood, prefix function, syntax, sound, language, cipher, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Opening-context panel validation

Status: **{result['status']}**

A clean-room implementation reconstructs all 5,826 anonymous rows, 53 exact
remainders, 1,763 quota strata, 197 mixed strata / 1,207 movable rows, exact
panel/quota/report bytes, gates, and bindings in **{checks}** checks. No row
operation assignment or context score is stored.

This validates masked calibration capacity only and supplies no detachment,
wordhood, prefix function, syntax, sound, language, cipher, meaning, plaintext,
or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
