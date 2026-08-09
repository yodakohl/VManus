#!/usr/bin/env python3
"""Inventory the positional structure of the literal UNPARSED_SURFACE layer."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
RESIDUAL = RESULTS / "pre_grounding_surface_residual_atlas.tsv"
OUTPUT_JSON = RESULTS / "unparsed_surface_structure.json"
OUTPUT_REPORT = RESULTS / "unparsed_surface_structure_report.md"
EXPECTED = {
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    RESIDUAL: "43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def position_class(position: int, length: int) -> str:
    if length == 1:
        return "SINGLETON"
    if position == 1:
        return "FIRST_ONLY"
    if position == length:
        return "LAST_ONLY"
    return "INTERNAL"


def top(counter: Counter[str], limit: int = 8) -> list[dict[str, object]]:
    return [{"value": value, "count": count} for value, count in counter.most_common(limit)]


def main() -> None:
    observed = {path: sha256(path) for path in EXPECTED}
    if observed != EXPECTED:
        raise RuntimeError("frozen residual-structure input drift")
    interlinear = load(INTERLINEAR)
    residuals = load(RESIDUAL)
    rows = {(row["edition"], row["locus"]): row for row in interlinear}
    if len(rows) != len(interlinear) or not interlinear:
        raise RuntimeError("duplicate interlinear edition/locus key")

    totals: Counter[str] = Counter()
    by_edition: dict[str, Counter[str]] = defaultdict(Counter)
    by_scope: Counter[str] = Counter()
    by_paragraph: Counter[str] = Counter()
    by_currier: Counter[str] = Counter()
    type_counts: dict[str, Counter[str]] = defaultdict(Counter)
    type_rows: dict[str, set[tuple[str, str]]] = defaultdict(set)
    type_loci: dict[str, set[str]] = defaultdict(set)
    previous: dict[str, Counter[str]] = defaultdict(Counter)
    following: dict[str, Counter[str]] = defaultdict(Counter)
    event_records: list[dict[str, object]] = []
    affected_loci: dict[str, list[dict[str, str]]] = defaultdict(list)

    for residual in residuals:
        key = (residual["edition"], residual["locus"])
        row = rows[key]
        surface = row["surface"].split()
        positions = [int(value) for value in residual["omitted_positions_1based"].split(";")]
        tokens = residual["omitted_tokens"].split()
        if not (
            len(positions) == len(tokens) == int(residual["omitted_token_count"]) > 0
        ):
            raise RuntimeError(f"residual event count drift at {key}")
        affected_loci[row["locus"]].append(residual)
        for position, token in zip(positions, tokens):
            category = position_class(position, len(surface))
            prev = surface[position - 2] if position > 1 else "<START>"
            nxt = surface[position] if position < len(surface) else "<END>"
            totals.update({"events": 1, category: 1})
            by_edition[row["edition"]].update({"events": 1, category: 1})
            by_scope[row["grammar_scope"]] += 1
            by_paragraph[row["paragraph_state"]] += 1
            by_currier[row["currier"] or "UNMARKED"] += 1
            type_counts[token].update({
                "events": 1,
                category: 1,
                f"scope:{row['grammar_scope']}": 1,
                f"paragraph:{row['paragraph_state']}": 1,
                f"currier:{row['currier'] or 'UNMARKED'}": 1,
            })
            type_rows[token].add(key)
            type_loci[token].add(row["locus"])
            previous[token][prev] += 1
            following[token][nxt] += 1
            event_records.append({
                "edition": row["edition"],
                "locus": row["locus"],
                "token": token,
                "position": position,
                "surface_length": len(surface),
                "position_class": category,
                "grammar_scope": row["grammar_scope"],
                "paragraph_state": row["paragraph_state"],
                "currier": row["currier"],
                "section": row["section"],
                "previous_surface": prev,
                "following_surface": nxt,
            })

    profiles = {}
    for token in sorted(type_counts):
        counts = type_counts[token]
        profiles[token] = {
            "events": counts["events"],
            "edition_rows": len(type_rows[token]),
            "physical_loci": len(type_loci[token]),
            "position": {
                name: counts[name]
                for name in ("SINGLETON", "FIRST_ONLY", "LAST_ONLY", "INTERNAL")
            },
            "scope": {
                name: counts[f"scope:{name}"]
                for name in ("CONFIRMED_PROSE", "DIAGNOSTIC_NONPROSE")
            },
            "paragraph": {
                name: counts[f"paragraph:{name}"] for name in ("OPEN", "CONT")
            },
            "currier": {
                name: counts[f"currier:{name}"] for name in ("A", "B", "UNMARKED")
            },
            "top_previous_surface": top(previous[token]),
            "top_following_surface": top(following[token]),
        }

    support_counts = Counter(len(values) for values in affected_loci.values())
    exact_token_sequence = Counter()
    exact_position_tokens = Counter()
    for values in affected_loci.values():
        reading_count = len(values)
        if reading_count < 2:
            continue
        exact_token_sequence[(reading_count, len({value["omitted_tokens"] for value in values}) == 1)] += 1
        exact_position_tokens[(reading_count, len({value["position_token_pairs"] for value in values}) == 1)] += 1

    ddy = [event for event in event_records if event["token"] == "ddy"]
    payload = {
        "status": "PASS_UNPARSED_SURFACE_POSITIONAL_INVENTORY",
        "decision": "NOT_EXCLUSIVELY_PHYSICAL_LINE_END_LAYOUT_PREFLIGHT_REQUIRED",
        "input_sha256": {str(path.relative_to(HERE.parents[1])): value for path, value in observed.items()},
        "totals": {
            "events": totals["events"],
            "affected_rows": len(residuals),
            "affected_physical_loci": len(affected_loci),
            "token_types": len(profiles),
            "position": {
                name: totals[name]
                for name in ("SINGLETON", "FIRST_ONLY", "LAST_ONLY", "INTERNAL")
            },
            "scope": dict(sorted(by_scope.items())),
            "paragraph": dict(sorted(by_paragraph.items())),
            "currier": dict(sorted(by_currier.items())),
        },
        "by_edition": {
            edition: {
                "events": counts["events"],
                "position": {
                    name: counts[name]
                    for name in ("SINGLETON", "FIRST_ONLY", "LAST_ONLY", "INTERNAL")
                },
            }
            for edition, counts in sorted(by_edition.items())
        },
        "token_profiles": profiles,
        "cross_reading": {
            "affected_loci_by_available_residual_readings": {
                str(key): value for key, value in sorted(support_counts.items())
            },
            "exact_token_sequence": {
                f"{readings}_readings_{str(exact).lower()}": count
                for (readings, exact), count in sorted(exact_token_sequence.items())
            },
            "exact_position_token_pairs": {
                f"{readings}_readings_{str(exact).lower()}": count
                for (readings, exact), count in sorted(exact_position_tokens.items())
            },
        },
        "ddy_profile": {
            "events": len(ddy),
            "physical_loci": sorted({str(event["locus"]) for event in ddy}),
            "readings_by_locus": {
                locus: sorted(str(event["edition"]) for event in ddy if event["locus"] == locus)
                for locus in sorted({str(event["locus"]) for event in ddy})
            },
            "all_internal": all(event["position_class"] == "INTERNAL" for event in ddy),
            "all_confirmed_prose": all(event["grammar_scope"] == "CONFIRMED_PROSE" for event in ddy),
            "all_continuation": all(event["paragraph_state"] == "CONT" for event in ddy),
            "all_currier_a_section_h": all(
                event["currier"] == "A" and event["section"] == "H" for event in ddy
            ),
            "events_detail": ddy,
        },
        "gates": {
            "residual_layer_is_exclusively_physical_line_end": totals["INTERNAL"] == 0,
            "majority_of_residual_events_are_physical_line_internal": totals["INTERNAL"] > totals["events"] / 2,
            "y_majority_physical_line_internal": profiles["y"]["position"]["INTERNAL"] > profiles["y"]["events"] / 2,
            "ddy_is_all_reading_at_two_loci": (
                len(ddy) == 6
                and {tuple(value) for value in {
                    locus: tuple(sorted(str(event["edition"]) for event in ddy if event["locus"] == locus))
                    for locus in {str(event["locus"]) for event in ddy}
                }.values()} == {("IT2a", "RF1b", "ZL3b")}
            ),
        },
        "next_test": (
            "Before any reset score, bind human/manual internal layout-gap annotations, quantify coverage, "
            "and require a powered physical-locus-clustered design that matches or excludes layout breaks. "
            "Only then may complete literal surfaces compare y-final residual contexts with ordinary spaces "
            "and genuine line endpoints; do not assign punctuation, clause, suffix, or lexical meanings."
        ),
        "claim_ceiling": (
            "UNPARSED_SURFACE is a transcription/segmentation-sensitive 28-type literal layer dominated by "
            "y and dy positions internal to flattened physical lines. It is not exclusively a physical-line-end "
            "layer, but internal layout boundaries remain unresolved. No token is established as a separator, "
            "suffix, number, word, sound, or meaning."
        ),
        "english_lexical_glosses": 0,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    pos = payload["totals"]["position"]
    y = profiles["y"]
    dy = profiles["dy"]
    report = f"""# UNPARSED_SURFACE positional inventory

Decision: **NOT EXCLUSIVELY PHYSICAL-LINE-END; LAYOUT PREFLIGHT REQUIRED**.

The corrected literal residual layer contains {totals['events']:,} complete
space-delimited groups of 28 surface types on {len(residuals):,}
reading-specific rows / {len(affected_loci):,} physical loci. Positions are:

| exclusive position | events |
|---|---:|
| singleton line | {pos['SINGLETON']:,} |
| first only | {pos['FIRST_ONLY']:,} |
| last only | {pos['LAST_ONLY']:,} |
| internal | {pos['INTERNAL']:,} |

Thus {pos['INTERNAL'] / totals['events']:.1%} are internal to the flattened
physical line. The former “detached line-edge carrier” shorthand is false if it
means only physical line ends. It remains possible that some positions mark
manual internal layout gaps around drawings or interruptions. This inventory
does not establish punctuation or clause boundaries.

`y` contributes {y['events']:,} events, including
{y['position']['INTERNAL']:,} internal ({y['position']['INTERNAL']/y['events']:.1%}).
`dy` contributes {dy['events']:,}, including {dy['position']['LAST_ONLY']:,}
last-only and {dy['position']['INTERNAL']:,} internal events. RF1b supplies
{by_edition['RF1b']['events']:,} residual events versus
{by_edition['ZL3b']['events']:,} ZL3b and {by_edition['IT2a']['events']:,} IT2a,
so the layer is strongly transcription/segmentation-sensitive. The editions
are alternate readings, not independent samples.

The rare `ddy` is independently clear: six events at exactly f11v.6 and
f18v.8, present in all three readings. Every event is physical-line-internal,
continuation prose, Currier A, section H. This is a reading-stable literal
two-locus case, not an independently replicated or powered structural target.
It does not decide whether the f11 margin is `dd`, `88`, a copy, a reference,
or later writing.

## Next falsifiable test

First bind the human/manual internal layout-gap annotations to this exact
residual inventory and determine whether enough non-gap physical loci remain
for synchronous, alternate-reading-aware inference. Any later reset test must
match or exclude layout gaps, cluster physical loci, and pass power and
exchangeability controls before scoring. Neither outcome may assign punctuation,
suffix, number, word, sound, or English meaning.

Inputs are hash-bound manual-transcription artifacts. No OCR, image recognition,
or lexical gloss was used.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "events": totals["events"],
        "internal": totals["INTERNAL"],
        "token_types": len(profiles),
        "ddy_loci": payload["ddy_profile"]["physical_loci"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
