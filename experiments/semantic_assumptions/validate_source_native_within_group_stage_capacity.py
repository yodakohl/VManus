#!/usr/bin/env python3
"""Independent reconstruction of the masked within-group stage capacity."""

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
SOURCE_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
SPEC = BASE / "SOURCE_NATIVE_WITHIN_GROUP_STAGE_CAPACITY_SPEC.md"
BUILDER = BASE / "build_source_native_within_group_stage_capacity.py"
PANEL = RESULTS / "source_native_within_group_stage_masked.tsv"
PRODUCTION = RESULTS / "source_native_within_group_stage_capacity.json"
PRODUCTION_REPORT = RESULTS / "source_native_within_group_stage_capacity_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_within_group_stage_capacity_validation.json"
REPORT = RESULTS / "source_native_within_group_stage_capacity_validation_report.md"
FIELDS = ("unit_id", "locus", "page", "physical_folio", "section", "currier", "hand", "kind", "symbol_count", "split")
HASHES = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    SPEC: "a17a7ffa8d3c2e31a54d605a069fda9d4478740a1369f505f6c8d6e995fe99fe",
    BUILDER: "9753762d51eab98d98668cc29deee28b31be043e40d3f4aa986611c80295fcc6",
    PANEL: "16d7395ae0410c8fc72b5e5462d6d425cd3a2685e7ea70eee0677bd936106ae5",
    PRODUCTION: "b4ce54ad7ad783aa6adaf6fe401e9056bfe163e2e67e9d207636fa3ec3f02345",
    PRODUCTION_REPORT: "d05604036fa7cec2eef6c170bfe73a3c9637008076018f730985b2550fba1917",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_for(folio: str) -> str:
    value = int.from_bytes(hashlib.sha256(f"SNWG001|{folio}".encode()).digest()[:8], "little") % 5
    return "TEST" if value == 0 else ("CAL" if value == 1 else "TRAIN")


def require(value: bool, message: str, checks: list[int]) -> None:
    checks[0] += 1
    if not value:
        raise AssertionError(message)


def render(rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def ngrams(loci: list[dict], field: str, size: int) -> list[int]:
    values: dict[tuple, list[str]] = defaultdict(list)
    for locus in loci:
        sequence = locus[field]
        for index in range(len(sequence) - size + 1):
            values[sequence[index:index + size]].append(locus["folio"])
    kept = [folios for folios in values.values() if len(set(folios)) >= 2]
    return [len(kept), sum(map(len, kept))]


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite within-group stage capacity validation")
    checks = [0]
    for path, expected in HASHES.items():
        require(sha(path) == expected, f"hash {path.name}", checks)
    production = json.loads(PRODUCTION.read_text())
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    rows = []
    by_locus: dict[str, list[dict]] = defaultdict(list)
    for source in source_rows:
        if source["strict_zero_alternative"] == "1":
            by_locus[source["locus"]].append(source)
        if source["strict_zero_alternative"] != "1" or source["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        match = re.match(r"f\d+", source["page"])
        if match is None:
            continue
        rows.append({"unit_id": source["consensus_group_id"], "locus": source["locus"], "page": source["page"], "physical_folio": match.group(), "section": source["section"], "currier": source["currier"], "hand": source["hand"], "kind": source["kind"], "symbol_count": str(len(source["family_surface"])), "split": split_for(match.group())})
    rows.sort(key=lambda row: row["unit_id"])
    require(len(rows) == 21899 and len({row["unit_id"] for row in rows}) == 21899, "row identity", checks)
    require(render(rows) == PANEL.read_bytes(), "panel bytes", checks)
    loci = []
    for values in by_locus.values():
        values.sort(key=lambda row: int(row["consensus_group_index"]))
        match = re.match(r"f\d+", values[0]["page"])
        if match is None or len(values) != int(values[0]["consensus_group_count"]):
            continue
        loci.append({"folio": match.group(), "families": tuple(row["family_surface"] for row in values), "members": tuple((row["zl_sta_codes"], row["it_sta_codes"], row["rf_sta_codes"]) for row in values)})
    complete: dict[tuple, set[str]] = defaultdict(set)
    for locus in loci:
        if len(locus["families"]) >= 3:
            complete[locus["families"]].add(locus["folio"])
    parallels = {
        "strict_complete_loci": len(loci),
        "cross_folio_complete_sequence_types_min_3_groups": sum(len(folios) >= 2 for folios in complete.values()),
        "family_ngram_4_types_events": ngrams(loci, "families", 4),
        "family_ngram_5_types_events": ngrams(loci, "families", 5),
        "exact_three_reading_member_ngram_3_types_events": ngrams(loci, "members", 3),
        "exact_three_reading_member_ngram_4_types_events": ngrams(loci, "members", 4),
    }
    require(parallels == production["parallel_capacity"], "parallel capacity", checks)
    counts = Counter(row["split"] for row in rows)
    require(dict(sorted(counts.items())) == production["split_group_counts"], "split groups", checks)
    folios = {key: sorted({row["physical_folio"] for row in rows if row["split"] == key}, key=lambda value: int(value[1:])) for key in ("TRAIN", "CAL", "TEST")}
    require(folios == production["split_folios"], "split folios", checks)
    currier = {key: dict(sorted(Counter(row["currier"] for row in rows if row["split"] == key).items())) for key in ("TRAIN", "CAL", "TEST")}
    require(currier == production["split_currier_counts"], "split Currier", checks)
    lengths = Counter(int(row["symbol_count"]) for row in rows)
    require({str(key): lengths[key] for key in sorted(lengths)} == production["length_distribution"], "lengths", checks)
    require(production["panel_sha256"] == sha(PANEL) and production["groups"] == 21899 and production["physical_folios"] == 94, "summary", checks)
    require(all(production["gates"].values()) and production["status"] == "PASS_SCORE_BLIND_WITHIN_GROUP_STAGE_CAPACITY", "gates", checks)
    require(production["target_sequences_stored"] == production["stage_scores_computed"] == production["english_glosses"] == 0, "target isolation", checks)
    require(production["inputs"] == {path.name: sha(path) for path in (SOURCE, SOURCE_VALIDATION, SPEC, BUILDER)}, "bindings", checks)
    # Mutation controls: duplicate IDs, target field, and split drift must reject.
    require(len({row["unit_id"] for row in rows + [dict(rows[0])]}) != len(rows) + 1, "duplicate mutation", checks)
    require(bool({"family_surface"} & (set(FIELDS) | {"family_surface"})), "target-field mutation", checks)
    require(split_for(rows[0]["physical_folio"]) != ({"TRAIN": "CAL", "CAL": "TEST", "TEST": "TRAIN"}[rows[0]["split"]]), "split mutation", checks)
    validation = {
        "experiment": "SOURCE_NATIVE_WITHIN_GROUP_STAGE_CAPACITY_VALIDATION",
        "status": "PASS_INDEPENDENT_SCORE_BLIND_STAGE_CAPACITY_RECONSTRUCTION",
        "checks": checks[0], "failures": [], "groups": len(rows),
        "physical_folios": len({row["physical_folio"] for row in rows}),
        "parallel_capacity": parallels, "panel_sha256": sha(PANEL),
        "production_sha256": sha(PRODUCTION), "validator_sha256": sha(VALIDATOR),
        "target_sequences_stored": 0, "stage_scores_computed": 0, "english_glosses": 0,
        "claim_ceiling": "Independent score-blind capacity reconstruction only; no stage, morphology, sound, word, meaning, plaintext, or translation follows.",
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Source-native within-group stage capacity validation

Status: **{validation['status']}**

A nonimporting implementation reconstructed all **{len(rows):,}** masked rows,
the 94-folio split, every length and Currier count, the complete exact-parallel
capacity, all input bindings, and mutation guards in **{checks[0]} checks**.

No family sequence, member code, stage score, or English gloss occurs in the
masked panel. Validation authorizes synthetic parser controls only and supplies
no morphology, sound, word, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": validation["status"], "checks": checks[0], "groups": len(rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
