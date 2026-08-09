#!/usr/bin/env python3
"""Build a parser-free capacity panel for exact-y spacing disagreements.

No context score is computed.  Candidate spans use complete literal surfaces
only.  Lines containing an explicit manual ZL3b ``<->`` interruption marker
are conservatively excluded as a whole.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
ZL_SOURCE = HERE.parents[1] / "transcription" / "sources" / "ZL3b-n.txt"
OUTPUT_TSV = RESULTS / "usr002_exact_y_capacity.tsv"
OUTPUT_JSON = RESULTS / "usr002_exact_y_capacity.json"
OUTPUT_REPORT = RESULTS / "usr002_exact_y_capacity_report.md"
EXPECTED = {
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    ZL_SOURCE: "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
}
READINGS = ("ZL3b", "IT2a", "RF1b")
LINE_RE = re.compile(r"^<(?P<locus>f[^,;>]+)[,;][^>]*>\s*(?P<raw>.*)$")
FOLIO_RE = re.compile(r"^(f\d+)")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def token_spans(tokens: list[str]) -> list[tuple[int, int]]:
    out = []
    start = 0
    for token in tokens:
        end = start + len(token)
        out.append((start, end))
        start = end
    return out


def internal_boundaries(tokens: list[str]) -> set[int]:
    return {end for _, end in token_spans(tokens)[:-1]}


def manual_interruption_loci(path: Path) -> set[str]:
    loci = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        match = LINE_RE.match(line)
        if match and "<->" in match.group("raw"):
            loci.add(match.group("locus"))
    return loci


def main() -> None:
    observed = {path: digest(path) for path in EXPECTED}
    if observed != EXPECTED:
        raise RuntimeError("USR002 capacity input drift")

    rows = load_tsv(INTERLINEAR)
    by_locus: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in rows:
        by_locus[row["locus"]][row["edition"]] = row
    interrupted = manual_interruption_loci(ZL_SOURCE)

    candidates = []
    for locus, reading_rows in sorted(by_locus.items()):
        if set(reading_rows) != set(READINGS):
            continue
        tokens = {reading: reading_rows[reading]["surface"].split() for reading in READINGS}
        compact = {reading: "".join(tokens[reading]) for reading in READINGS}
        if len(set(compact.values())) != 1:
            continue
        boundaries = {reading: internal_boundaries(tokens[reading]) for reading in READINGS}
        offsets = set()
        for reading in READINGS:
            for (start, end), token in zip(token_spans(tokens[reading]), tokens[reading]):
                if token == "y":
                    offsets.add((start, end))
        for start, end in sorted(offsets):
            if end - start != 1:
                raise RuntimeError("literal y span is not one character")
            if start == 0 or end == len(compact["ZL3b"]):
                continue
            isolated = {}
            internally_split = {}
            for reading in READINGS:
                all_boundaries = {0, len(compact[reading])} | boundaries[reading]
                isolated[reading] = start in all_boundaries and end in all_boundaries
                internally_split[reading] = any(start < value < end for value in all_boundaries)
            if any(internally_split.values()):
                raise RuntimeError("one-character y is internally split")
            isolated_count = sum(isolated.values())
            if isolated_count not in (1, 2):
                continue
            row = reading_rows["ZL3b"]
            all_confirmed_prose = all(
                reading_rows[reading]["grammar_scope"] == "CONFIRMED_PROSE"
                for reading in READINGS
            )
            folio_match = FOLIO_RE.match(row["page"])
            if not folio_match:
                raise RuntimeError(f"unresolved folio for {locus}")
            candidates.append({
                "candidate_id": f"{locus}@{start + 1}",
                "locus": locus,
                "page": row["page"],
                "physical_folio": folio_match.group(1),
                "section": row["section"],
                "currier": row["currier"],
                "character_offset_1based": str(start + 1),
                "isolated_reading_count": str(isolated_count),
                "ZL3b_isolated": str(int(isolated["ZL3b"])),
                "IT2a_isolated": str(int(isolated["IT2a"])),
                "RF1b_isolated": str(int(isolated["RF1b"])),
                "outcome_vector": "".join(str(int(isolated[reading])) for reading in READINGS),
                "manual_zl_line_has_interruption": str(int(locus in interrupted)),
                "eligible_after_manual_interruption_exclusion": str(int(locus not in interrupted)),
                "all_readings_confirmed_prose": str(int(all_confirmed_prose)),
                "eligible_for_context_power_preflight": str(
                    int(locus not in interrupted and all_confirmed_prose)
                ),
                "compact_character_length": str(len(compact["ZL3b"])),
            })

    fieldnames = list(candidates[0]) if candidates else []
    with OUTPUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(candidates)

    eligible = [row for row in candidates if row["eligible_after_manual_interruption_exclusion"] == "1"]
    context_eligible = [
        row for row in candidates if row["eligible_for_context_power_preflight"] == "1"
    ]
    counts = Counter(int(row["isolated_reading_count"]) for row in candidates)
    eligible_counts = Counter(int(row["isolated_reading_count"]) for row in eligible)
    vector_counts = Counter(row["outcome_vector"] for row in candidates)
    eligible_vector_counts = Counter(row["outcome_vector"] for row in eligible)
    context_counts = Counter(int(row["isolated_reading_count"]) for row in context_eligible)
    context_vector_counts = Counter(row["outcome_vector"] for row in context_eligible)
    payload = {
        "status": "PASS_USR002_PARSER_FREE_CAPACITY_INVENTORY",
        "decision": "POWER_PREFLIGHT_REQUIRED_BEFORE_CONTEXT_TEST",
        "input_sha256": {
            str(path.relative_to(HERE.parents[1])): value for path, value in observed.items()
        },
        "candidate_tsv_sha256": digest(OUTPUT_TSV),
        "all_candidates": {
            "spans": len(candidates),
            "physical_loci": len({row["locus"] for row in candidates}),
            "pages": len({row["page"] for row in candidates}),
            "physical_folios": len({row["physical_folio"] for row in candidates}),
            "isolated_reading_count": {str(key): value for key, value in sorted(counts.items())},
            "outcome_vectors": dict(sorted(vector_counts.items())),
        },
        "manual_interruption_exclusion": {
            "source_marker": "<->",
            "excluded_spans": len(candidates) - len(eligible),
            "excluded_loci": len({row["locus"] for row in candidates if row not in eligible}),
            "eligible_spans": len(eligible),
            "eligible_loci": len({row["locus"] for row in eligible}),
            "eligible_pages": len({row["page"] for row in eligible}),
            "eligible_physical_folios": len({row["physical_folio"] for row in eligible}),
            "eligible_isolated_reading_count": {
                str(key): value for key, value in sorted(eligible_counts.items())
            },
            "eligible_outcome_vectors": dict(sorted(eligible_vector_counts.items())),
        },
        "context_power_preflight_scope": {
            "eligible_spans": len(context_eligible),
            "eligible_loci": len({row["locus"] for row in context_eligible}),
            "eligible_pages": len({row["page"] for row in context_eligible}),
            "eligible_physical_folios": len({row["physical_folio"] for row in context_eligible}),
            "isolated_reading_count": {
                str(key): value for key, value in sorted(context_counts.items())
            },
            "outcome_vectors": dict(sorted(context_vector_counts.items())),
            "minority_k2_physical_folios": len({
                row["physical_folio"] for row in context_eligible
                if row["isolated_reading_count"] == "2"
            }),
        },
        "gates": {
            "exactly_three_readings_per_candidate": all(
                sum(int(row[f"{reading}_isolated"]) for reading in READINGS)
                == int(row["isolated_reading_count"])
                for row in candidates
            ),
            "all_candidates_are_spacing_only": True,
            "no_formal_root_role_or_residual_field_referenced": True,
            "manual_interruption_lines_excluded_whole": all(
                row["manual_zl_line_has_interruption"] == "0" for row in eligible
            ),
            "context_scope_is_confirmed_prose_and_manual_interruption_clean": all(
                row["all_readings_confirmed_prose"] == "1"
                and row["manual_zl_line_has_interruption"] == "0"
                for row in context_eligible
            ),
        },
        "next_test": (
            "Freeze and run a target-blind folio-level power calibration before any context score. "
            "If the minority isolated-reading state or matched folio orbit is too small, stop USR002 unscored."
        ),
        "claim_ceiling": (
            "This is capacity for a parser-free exact-y spacing-disagreement test only. Candidate readings "
            "are repeated transcriptions of one physical locus, not independent samples. No authorial space, "
            "separator, suffix, morphology, sound, word, number, plaintext, or meaning is established."
        ),
        "english_lexical_glosses": 0,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    clean = payload["manual_interruption_exclusion"]
    report = f"""# USR002 exact-y parser-free capacity

Decision: **POWER PREFLIGHT REQUIRED BEFORE ANY CONTEXT TEST**.

Complete literal surfaces yield {len(candidates)} exact-character `y`
split/fused spans on {payload['all_candidates']['physical_loci']} loci,
{payload['all_candidates']['pages']} pages, and
{payload['all_candidates']['physical_folios']} physical folios.  One reading
isolates `y` at {counts[1]} spans and two readings isolate it at {counts[2]}.

Conservatively excluding every ZL3b line containing the explicit manual
`<->` interruption marker leaves {clean['eligible_spans']} spans on
{clean['eligible_loci']} loci and {clean['eligible_physical_folios']} folios:
{clean['eligible_isolated_reading_count'].get('1', 0)} with one isolating
reading and {clean['eligible_isolated_reading_count'].get('2', 0)} with two.

The confirmed-prose context-power scope contains
{payload['context_power_preflight_scope']['eligible_spans']} spans on
{payload['context_power_preflight_scope']['eligible_physical_folios']} folios,
with {payload['context_power_preflight_scope']['isolated_reading_count'].get('2', 0)}
minority two-reading spans on only
{payload['context_power_preflight_scope']['minority_k2_physical_folios']} folios.

No formal root/role field or residual label was referenced; the literal rows
were projected from the complete interlinear package.  This is only a capacity
inventory.  Alternate readings are not
independent samples, and spacing disagreement does not prove authorial spaces
or any linguistic function.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "all_spans": len(candidates),
        "eligible_spans": payload["context_power_preflight_scope"]["eligible_spans"],
        "eligible_folios": payload["context_power_preflight_scope"]["eligible_physical_folios"],
        "eligible_k1": payload["context_power_preflight_scope"]["isolated_reading_count"].get("1", 0),
        "eligible_k2": payload["context_power_preflight_scope"]["isolated_reading_count"].get("2", 0),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
