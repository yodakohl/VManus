#!/usr/bin/env python3
"""Build the score-blind capacity panel for a source-native stage grammar."""

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
BUILDER = Path(__file__).resolve()
PANEL = RESULTS / "source_native_within_group_stage_masked.tsv"
OUT = RESULTS / "source_native_within_group_stage_capacity.json"
REPORT = RESULTS / "source_native_within_group_stage_capacity_report.md"
FROZEN = {
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SOURCE_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
}
FIELDS = (
    "unit_id", "locus", "page", "physical_folio", "section", "currier",
    "hand", "kind", "symbol_count", "split",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def split_for(folio: str) -> str:
    value = int.from_bytes(hashlib.sha256(f"SNWG001|{folio}".encode()).digest()[:8], "little") % 5
    return "TEST" if value == 0 else ("CAL" if value == 1 else "TRAIN")


def render(rows: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode()


def parallel_capacity(source_rows: list[dict]) -> dict:
    by_locus: dict[str, list[dict]] = defaultdict(list)
    for row in source_rows:
        if row["strict_zero_alternative"] == "1":
            by_locus[row["locus"]].append(row)
    loci = []
    for locus, rows in by_locus.items():
        rows.sort(key=lambda row: int(row["consensus_group_index"]))
        match = re.match(r"f\d+", rows[0]["page"])
        if match is None or len(rows) != int(rows[0]["consensus_group_count"]):
            continue
        loci.append({
            "folio": match.group(),
            "families": tuple(row["family_surface"] for row in rows),
            "members": tuple((row["zl_sta_codes"], row["it_sta_codes"], row["rf_sta_codes"]) for row in rows),
        })

    def repeated_full(min_groups: int) -> int:
        values: dict[tuple, set[str]] = defaultdict(set)
        for locus in loci:
            if len(locus["families"]) >= min_groups:
                values[locus["families"]].add(locus["folio"])
        return sum(len(folios) >= 2 for folios in values.values())

    def repeated_ngrams(field: str, size: int) -> tuple[int, int]:
        values: dict[tuple, list[str]] = defaultdict(list)
        for locus in loci:
            sequence = locus[field]
            for index in range(len(sequence) - size + 1):
                values[sequence[index:index + size]].append(locus["folio"])
        retained = [folios for folios in values.values() if len(set(folios)) >= 2]
        return len(retained), sum(len(folios) for folios in retained)

    return {
        "strict_complete_loci": len(loci),
        "cross_folio_complete_sequence_types_min_3_groups": repeated_full(3),
        "family_ngram_4_types_events": list(repeated_ngrams("families", 4)),
        "family_ngram_5_types_events": list(repeated_ngrams("families", 5)),
        "exact_three_reading_member_ngram_3_types_events": list(repeated_ngrams("members", 3)),
        "exact_three_reading_member_ngram_4_types_events": list(repeated_ngrams("members", 4)),
    }


def main() -> None:
    if any(path.exists() for path in (PANEL, OUT, REPORT)):
        raise SystemExit("refusing to overwrite within-group stage capacity")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch: {path.name}")
    validation = json.loads(SOURCE_VALIDATION.read_text())
    if validation["status"] != "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":
        raise SystemExit("source-family validation is not PASS")
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    rows = []
    for source in source_rows:
        if source["strict_zero_alternative"] != "1" or source["grammar_scope"] != "CONFIRMED_PROSE":
            continue
        match = re.match(r"f\d+", source["page"])
        if match is None:
            continue
        rows.append({
            "unit_id": source["consensus_group_id"], "locus": source["locus"],
            "page": source["page"], "physical_folio": match.group(),
            "section": source["section"], "currier": source["currier"],
            "hand": source["hand"], "kind": source["kind"],
            "symbol_count": len(source["family_surface"]),
            "split": split_for(match.group()),
        })
    rows.sort(key=lambda row: row["unit_id"])
    if len(rows) != len({row["unit_id"] for row in rows}):
        raise ValueError("duplicate stage-capacity unit ID")
    PANEL.write_bytes(render(rows))
    group_counts = Counter(row["split"] for row in rows)
    folios = {split: sorted({row["physical_folio"] for row in rows if row["split"] == split}, key=lambda value: int(value[1:])) for split in ("TRAIN", "CAL", "TEST")}
    currier = {split: dict(sorted(Counter(row["currier"] for row in rows if row["split"] == split).items())) for split in ("TRAIN", "CAL", "TEST")}
    lengths = Counter(int(row["symbol_count"]) for row in rows)
    parallels = parallel_capacity(source_rows)
    forbidden = {"family_surface", "member_codes", "stage", "score", "english_gloss"}
    gates = {
        "exact_21899_groups": len(rows) == 21899,
        "exact_94_folios": len({row["physical_folio"] for row in rows}) == 94,
        "exact_split_group_counts": group_counts == {"TRAIN": 10753, "CAL": 5516, "TEST": 5630},
        "exact_split_folio_counts": {key: len(value) for key, value in folios.items()} == {"TRAIN": 47, "CAL": 23, "TEST": 24},
        "each_split_at_least_5000_groups_20_folios": all(group_counts[key] >= 5000 and len(folios[key]) >= 20 for key in folios),
        "both_curriers_at_least_1000_each_split": all(set(currier[key]) == {"A", "B"} and min(currier[key].values()) >= 1000 for key in currier),
        "length_range_1_to_11": min(lengths) == 1 and max(lengths) == 11,
        "target_sequence_fields_absent": not (forbidden & set(FIELDS)),
        "no_cross_folio_complete_parallel_min_3": parallels["cross_folio_complete_sequence_types_min_3_groups"] == 0,
        "no_exact_member_four_group_parallel": parallels["exact_three_reading_member_ngram_4_types_events"] == [0, 0],
    }
    result = {
        "experiment": "SOURCE_NATIVE_WITHIN_GROUP_STAGE_CAPACITY",
        "status": "PASS_SCORE_BLIND_WITHIN_GROUP_STAGE_CAPACITY",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, BUILDER)},
        "groups": len(rows), "physical_folios": len({row["physical_folio"] for row in rows}),
        "split_group_counts": dict(sorted(group_counts.items())),
        "split_folios": folios, "split_currier_counts": currier,
        "length_distribution": {str(key): lengths[key] for key in sorted(lengths)},
        "parallel_capacity": parallels, "panel_sha256": sha(PANEL),
        "schema": list(FIELDS), "gates": gates,
        "target_sequences_stored": 0, "stage_scores_computed": 0, "english_glosses": 0,
        "claim_ceiling": "Score-blind capacity and nonduplication for a new complete source-native within-group stage parser. No stage, morphology, sound, word, language, meaning, plaintext, or translation follows.",
    }
    if not all(gates.values()):
        raise ValueError("within-group stage capacity gate failure")
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Source-native within-group stage capacity

Status: **{result['status']}**

The target-masked panel contains **{len(rows):,}** complete confirmed-prose
source groups on **94** physical folios. TRAIN/CAL/TEST contain
**{group_counts['TRAIN']:,}/{group_counts['CAL']:,}/{group_counts['TEST']:,}**
groups on **{len(folios['TRAIN'])}/{len(folios['CAL'])}/{len(folios['TEST'])}**
folios; both Currier registers exceed 1,000 groups in every split.

The cheap parallel-passage gate finds zero complete cross-folio repeats of at
least three groups. Only **{parallels['family_ngram_4_types_events'][0]}**
four-group family n-gram types recur across folios and none reaches five
groups; exact three-reading member codes retain
**{parallels['exact_three_reading_member_ngram_3_types_events'][0]}** recurring
three-group types and zero four-group types. The sparse exact-parallel route is
therefore not expanded.

The public panel contains length and metadata only: zero family sequences,
member codes, stages, scores, or glosses. This authorizes only a separately
frozen monotone-stage parser and target-free controls. It supplies no
morphology, sound, word, language, meaning, plaintext, or translation.
""")
    print(json.dumps({"status": result["status"], "groups": len(rows), "folios": 94, "splits": dict(group_counts)}, sort_keys=True))


if __name__ == "__main__":
    main()
