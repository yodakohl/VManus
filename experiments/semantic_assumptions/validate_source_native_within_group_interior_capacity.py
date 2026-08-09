#!/usr/bin/env python3
"""Independent reconstruction of the endpoint-free interior capacity."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
SOURCE = RESULTS / "source_native_within_group_stage_masked.tsv"
SOURCE_VALIDATION = RESULTS / "source_native_within_group_stage_capacity_validation.json"
SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_CAPACITY_SPEC.md"
BUILDER = BASE / "build_source_native_within_group_interior_capacity.py"
PANEL = RESULTS / "source_native_within_group_interior_masked.tsv"
PRODUCTION = RESULTS / "source_native_within_group_interior_capacity.json"
PRODUCTION_REPORT = RESULTS / "source_native_within_group_interior_capacity_report.md"
OUT = RESULTS / "source_native_within_group_interior_capacity_validation.json"
REPORT = RESULTS / "source_native_within_group_interior_capacity_validation_report.md"
FROZEN = {
    SOURCE: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    SOURCE_VALIDATION: "2a95ce3183b72540f39a8ef0f68129d1f7ccf2e688683a9f2989360f84c20007",
    SPEC: "d8473e91eb38865a53cb6979cf80a70e9c64668cbfee2cb6f199b21ad554b473",
    BUILDER: "bd94b535a6468ec8727b53211bfd5f21e08b91600f55202a29df405bef8200b1",
    PANEL: "0b6202641045ed11fd1ae4870353b4bec17adcc658c9687fd766f35bfbfe51ad",
    PRODUCTION: "27662ecab0654da36ead2abd681eafd8ea445ca04673f8f038ab54a0ad67af0d",
    PRODUCTION_REPORT: "100a347fc79d0892645a189948b9a0d181bf025ed587de73cbdcd32a38d028c1",
}
SOURCE_FIELDS = ("unit_id", "locus", "page", "physical_folio", "section", "currier", "hand", "kind", "symbol_count", "split")
FIELDS = ("unit_id", "locus", "page", "physical_folio", "section", "currier", "hand", "kind", "original_symbol_count", "interior_symbol_count", "split")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    return stream.getvalue().encode()


def derive(source_rows: list[dict]) -> list[dict]:
    if len(source_rows) != 21899 or len({row["unit_id"] for row in source_rows}) != 21899:
        raise ValueError("source identity")
    rows = []
    for source in source_rows:
        length = int(source["symbol_count"])
        if length < 3:
            continue
        rows.append({
            "unit_id": source["unit_id"], "locus": source["locus"], "page": source["page"],
            "physical_folio": source["physical_folio"], "section": source["section"],
            "currier": source["currier"], "hand": source["hand"], "kind": source["kind"],
            "original_symbol_count": str(length), "interior_symbol_count": str(length - 2), "split": source["split"],
        })
    if len(rows) != len({row["unit_id"] for row in rows}):
        raise ValueError("derived identity")
    return rows


def summarize(rows: list[dict]) -> dict:
    split_groups = Counter(row["split"] for row in rows)
    split_symbols = Counter()
    split_folios, split_currier = {}, {}
    for split in ("TRAIN", "CAL", "TEST"):
        selected = [row for row in rows if row["split"] == split]
        split_symbols[split] = sum(int(row["interior_symbol_count"]) for row in selected)
        split_folios[split] = len({row["physical_folio"] for row in selected})
        split_currier[split] = dict(sorted(Counter(row["currier"] for row in selected).items()))
    lengths = Counter(int(row["original_symbol_count"]) for row in rows)
    return {
        "groups": len(rows), "interior_symbols": sum(int(row["interior_symbol_count"]) for row in rows),
        "physical_folios": len({row["physical_folio"] for row in rows}),
        "split_group_counts": dict(sorted(split_groups.items())),
        "split_interior_symbol_counts": dict(sorted(split_symbols.items())),
        "split_folio_counts": split_folios, "split_currier_counts": split_currier,
        "original_length_distribution": {str(key): lengths[key] for key in sorted(lengths)},
    }


def expected_report(summary: dict, status: str) -> str:
    groups, symbols = summary["split_group_counts"], summary["split_interior_symbol_counts"]
    return f"""# Source-native within-group interior-position capacity

Status: **{status}**

After removing groups too short to have an interior, the masked panel retains
**{summary['groups']:,} groups**, **{summary['interior_symbols']:,} interior symbols**,
and all **94** physical folios. TRAIN/CAL/TEST contain
**{groups['TRAIN']:,}/{groups['CAL']:,}/{groups['TEST']:,}**
groups and **{symbols['TRAIN']:,}/{symbols['CAL']:,}/{symbols['TEST']:,}**
interior symbols.

The panel contains identity, metadata, original/interior length, and split
only. It stores zero endpoint or interior family values, scores, stages, or
glosses. This authorizes only target-free calibration of an endpoint-free,
exact-length-conditioned positional model.
"""


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite interior capacity validation")
    failures, checks = [], 0
    def check(condition: bool, name: str) -> None:
        nonlocal checks
        checks += 1
        if not condition: failures.append(name)
    for path, expected in FROZEN.items(): check(sha(path) == expected, f"hash:{path.name}")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t"); check(tuple(reader.fieldnames or ()) == SOURCE_FIELDS, "source schema"); source_rows = list(reader)
    rows = derive(source_rows); summary = summarize(rows); panel_bytes = render(rows)
    check(panel_bytes == PANEL.read_bytes(), "panel bytes")
    check(summary["groups"] == 19203 and summary["interior_symbols"] == 45867 and summary["physical_folios"] == 94, "capacity")
    check(summary["split_group_counts"] == {"CAL": 4887, "TEST": 4952, "TRAIN": 9364}, "group splits")
    check(summary["split_interior_symbol_counts"] == {"CAL": 11693, "TEST": 11914, "TRAIN": 22260}, "symbol splits")
    check(summary["split_folio_counts"] == {"TRAIN": 47, "CAL": 23, "TEST": 24}, "folio splits")
    check(all(set(values) == {"A", "B"} and min(values.values()) >= 1000 for values in summary["split_currier_counts"].values()), "Currier capacity")
    check((min(map(int, summary["original_length_distribution"])), max(map(int, summary["original_length_distribution"]))) == (3, 11), "length range")
    production = json.loads(PRODUCTION.read_text())
    for key, value in summary.items(): check(production[key] == value, f"production:{key}")
    check(production["panel_sha256"] == hashlib.sha256(panel_bytes).hexdigest(), "panel digest")
    check(production["schema"] == list(FIELDS), "schema")
    check(all(production["gates"].values()), "gates")
    check(production["target_sequences_stored"] == 0 and production["target_scores_computed"] == 0 and production["english_glosses"] == 0, "target isolation")
    check(PRODUCTION_REPORT.read_text() == expected_report(summary, production["status"]), "report bytes")
    mutated = [dict(row) for row in source_rows]; mutated[0]["unit_id"] = mutated[1]["unit_id"]
    try: derive(mutated)
    except ValueError: mutation_rejected = True
    else: mutation_rejected = False
    check(mutation_rejected, "duplicate mutation")
    if failures: raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_WITHIN_GROUP_INTERIOR_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_SCORE_BLIND_INTERIOR_CAPACITY_RECONSTRUCTION",
        "checks": checks, "failures": [], **summary,
        "panel_sha256": hashlib.sha256(panel_bytes).hexdigest(),
        "target_sequences_accessed": 0, "target_scores_computed": 0, "english_glosses": 0,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "claim_ceiling": "Independent score-blind capacity reconstruction only; no interior family value, morphology, sound, word, language, meaning, plaintext, cipher, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Source-native within-group interior capacity validation

Status: **{result['status']}**

An independent implementation reconstructs all **{summary['groups']:,}** rows,
**{summary['interior_symbols']:,}** interior-symbol slots, split and Currier
capacities, exact TSV bytes, report bytes, bindings, and a duplicate-ID
mutation in **{checks} checks**. It accesses zero family values or scores.

This validates endpoint-free capacity only and supplies no morphology, sound,
word, language, meaning, plaintext, cipher, or translation.
""")
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__": main()
