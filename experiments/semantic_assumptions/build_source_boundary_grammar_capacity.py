#!/usr/bin/env python3
"""Build the score-blind source-boundary grammar capacity audit."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
LOCI = RESULTS / "source_sta_family_consensus_loci.tsv"
BOUNDARIES = RESULTS / "source_sta_family_consensus_boundaries.tsv"
CONSENSUS = RESULTS / "source_sta_family_consensus.json"
SPEC = HERE / "SOURCE_BOUNDARY_GRAMMAR_CAPACITY_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_JSON = RESULTS / "source_boundary_grammar_capacity.json"
OUT_REPORT = RESULTS / "source_boundary_grammar_capacity_report.md"

EXPECTED = {
    LOCI: "84354a9e5d291ab00f45c9bfe161f62d8cbd8c39db7511ff263cd9fcfe9d9e77",
    BOUNDARIES: "b32aa0a197f9a09eb19087ca80fcc0346601576d49429c346a5df23826ef3974",
    CONSENSUS: "193ac76bd14b3967844035e8c3997f402d556c7aecf3190145c5295b4eeab3f7",
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def physical_folio(page: str) -> str:
    match = re.fullmatch(r"(f\d+)[rv]\d*", page)
    if match is None:
        raise ValueError(f"invalid page identifier: {page}")
    return match.group(1)


def sorted_counts(values) -> dict[str, int]:
    counts = Counter(values)
    return {str(key): counts[key] for key in sorted(counts, key=str)}


def main() -> None:
    if OUT_JSON.exists() or OUT_REPORT.exists():
        raise SystemExit("refusing to overwrite capacity artifacts")
    for path, expected in EXPECTED.items():
        actual = sha(path)
        if actual != expected:
            raise SystemExit(f"input hash mismatch: {path.name}: {actual}")

    loci_rows = load_tsv(LOCI)
    boundary_rows = load_tsv(BOUNDARIES)
    strict = {row["locus"]: row for row in loci_rows if row["strict_zero_alternative"] == "1"}
    if len(strict) != 3572:
        raise SystemExit(f"unexpected strict-locus count: {len(strict)}")

    boundary_map: dict[tuple[str, int], dict[str, str]] = {}
    for row in boundary_rows:
        if row["strict_zero_alternative"] != "1":
            continue
        key = (row["locus"], int(row["position_after_symbol"]))
        if key in boundary_map:
            raise SystemExit(f"duplicate boundary key: {key}")
        locus = strict.get(row["locus"])
        if locus is None:
            raise SystemExit(f"strict boundary lacks strict locus: {key}")
        sequence = locus["family_sequence"]
        position = key[1]
        if not 0 < position < len(sequence):
            raise SystemExit(f"noninternal boundary: {key}")
        for field in ("page", "section", "currier", "hand", "code", "kind", "grammar_scope"):
            if row[field] != locus[field]:
                raise SystemExit(f"metadata drift at {key}: {field}")
        if row["left_family"] != sequence[position - 1] or row["right_family"] != sequence[position]:
            raise SystemExit(f"family drift at {key}")
        support = int(row["support_count"])
        if support not in (1, 2, 3):
            raise SystemExit(f"invalid support at {key}: {support}")
        boundary_map[key] = row

    gaps: list[dict[str, object]] = []
    seen_boundary_keys: set[tuple[str, int]] = set()
    for locus_id in sorted(strict):
        locus = strict[locus_id]
        sequence = locus["family_sequence"]
        folio = physical_folio(locus["page"])
        for position in range(1, len(sequence)):
            key = (locus_id, position)
            source = boundary_map.get(key)
            support = int(source["support_count"]) if source else 0
            if source:
                seen_boundary_keys.add(key)
            gaps.append({
                "locus": locus_id,
                "folio": folio,
                "page": locus["page"],
                "section": locus["section"],
                "currier": locus["currier"],
                "kind": locus["kind"],
                "grammar_scope": locus["grammar_scope"],
                "position": position,
                "pair": sequence[position - 1:position + 1],
                "support": support,
            })
    if seen_boundary_keys != set(boundary_map):
        raise SystemExit("not every strict boundary was reconstructed")

    support_counts = Counter(int(row["support"]) for row in gaps)
    folio_support: dict[str, Counter] = defaultdict(Counter)
    for row in gaps:
        folio_support[str(row["folio"])][int(row["support"])] += 1
    target_folios = {
        str(support): len({str(row["folio"]) for row in gaps if row["support"] == support})
        for support in (1, 2)
    }
    both_target_folios = sum(1 for counts in folio_support.values() if counts[1] and counts[2])

    training_pair_by_folio = Counter()
    training_pair_total = Counter()
    for row in gaps:
        if row["support"] in (0, 3):
            pair = str(row["pair"])
            folio = str(row["folio"])
            training_pair_by_folio[(folio, pair)] += 1
            training_pair_total[pair] += 1
    loo_covered = {}
    for support in (1, 2):
        targets = [row for row in gaps if row["support"] == support]
        covered = sum(
            training_pair_total[str(row["pair"])]
            - training_pair_by_folio[(str(row["folio"]), str(row["pair"]))] > 0
            for row in targets
        )
        loo_covered[str(support)] = {
            "covered": covered,
            "total": len(targets),
            "fraction": covered / len(targets),
        }

    remaining_training = {}
    for folio in sorted(folio_support):
        remaining_training[folio] = {
            "support_0": support_counts[0] - folio_support[folio][0],
            "support_3": support_counts[3] - folio_support[folio][3],
        }
    training_minima = {
        "support_0": min(row["support_0"] for row in remaining_training.values()),
        "support_3": min(row["support_3"] for row in remaining_training.values()),
    }

    metadata_overlap = {}
    for field in ("section", "currier", "kind", "grammar_scope"):
        values = {
            str(support): sorted({str(row[field]) for row in gaps if row["support"] == support})
            for support in (1, 2)
        }
        metadata_overlap[field] = {
            "support_1": values["1"],
            "support_2": values["2"],
            "exact_set_match": values["1"] == values["2"],
        }

    gates = {
        "exact_strict_loci_and_gap_counts": len(strict) == 3572 and len(gaps) == 91879,
        "exact_support_counts": [support_counts[i] for i in range(4)] == [71356, 814, 668, 19041],
        "at_least_600_each_target": min(support_counts[1], support_counts[2]) >= 600,
        "at_least_80_folios_with_both_targets": both_target_folios >= 80,
        "at_least_90_folios_each_target": min(target_folios.values()) >= 90,
        "loo_pair_coverage": loo_covered["2"]["fraction"] == 1.0 and loo_covered["1"]["fraction"] >= 0.99,
        "held_training_minima": training_minima["support_0"] >= 68000 and training_minima["support_3"] >= 18000,
        "target_metadata_category_sets_match": all(row["exact_set_match"] for row in metadata_overlap.values()),
        "score_and_lexical_fields_absent": True,
    }
    passed = all(gates.values())
    decision = "GO_FREEZE_SOURCE_BOUNDARY_GRAMMAR_TEST" if passed else "STOP_INSUFFICIENT_BOUNDARY_TRANSFER_CAPACITY"

    result = {
        "experiment": "SOURCE_BOUNDARY_GRAMMAR_CAPACITY",
        "status": "PASS_SCORE_BLIND_CAPACITY" if passed else "STOP_CAPACITY_GATE_FAILURE",
        "decision": decision,
        "inputs": {path.name: sha(path) for path in (*EXPECTED, SPEC, BUILDER)},
        "counts": {
            "strict_loci": len(strict),
            "internal_gaps": len(gaps),
            "physical_folios": len(folio_support),
            "support": {str(i): support_counts[i] for i in range(4)},
            "target_folios": target_folios,
            "folios_with_both_targets": both_target_folios,
            "family_alphabet": sorted({character for row in strict.values() for character in row["family_sequence"]}),
            "observed_training_pairs": len(training_pair_total),
        },
        "loo_target_pair_coverage": loo_covered,
        "held_training_minima": training_minima,
        "target_metadata_overlap": metadata_overlap,
        "target_metadata_counts": {
            field: {
                str(support): sorted_counts(row[field] for row in gaps if row["support"] == support)
                for support in (1, 2)
            }
            for field in ("section", "currier", "kind", "grammar_scope")
        },
        "gates": gates,
        "prohibited_outputs": {
            "model_fitted": False,
            "target_contrast_computed": False,
            "p_value_computed": False,
            "english_glosses": 0,
        },
        "claim_ceiling": (
            "Capacity for a preregistered physical-folio-held source-boundary grammar test only; "
            "no authorial word boundary, corrected reading, grammar role, sound, morpheme, lexeme, "
            "plaintext, language, or translation."
        ),
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Source-boundary grammar transfer capacity

Status: **{result['status']}**

The strict exact-family panel contains **{len(gaps):,}** internal gaps on
**{len(folio_support)}** physical folios. Support counts are
**{support_counts[0]:,} / {support_counts[1]:,} / {support_counts[2]:,} /
{support_counts[3]:,}** for zero/one/two/three readings.

The unopened support-1/support-2 comparison has **{support_counts[1]:,}** and
**{support_counts[2]:,}** positions. Both occur on **{both_target_folios}**
physical folios. Leave-folio-out family-pair coverage is
**{loo_covered['1']['covered']}/{loo_covered['1']['total']}** for support 1 and
**{loo_covered['2']['covered']}/{loo_covered['2']['total']}** for support 2.
Holding out the largest folio still leaves at least
**{training_minima['support_3']:,}** unanimous boundaries and
**{training_minima['support_0']:,}** unanimous nonboundaries.

Decision: **{decision}**. This is a score-blind capacity result, not a boundary
model result. It supplies no authorial word boundary, corrected reading,
grammar role, sound, morpheme, lexeme, plaintext, language, or translation.
"""
    OUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "decision": decision, "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
