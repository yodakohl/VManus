#!/usr/bin/env python3
"""Independent reconstruction of the UNPARSED_SURFACE positional inventory."""

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
RESULT = RESULTS / "unparsed_surface_structure.json"
REPORT = RESULTS / "unparsed_surface_structure_report.md"
OUTPUT = RESULTS / "unparsed_surface_structure_validation.json"
EXPECTED = {
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    RESIDUAL: "43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3",
    RESULT: "148188ec9511f7b369dcde49f1bf7b3d26ce51bb8181674f15522f9e8e39441d",
    REPORT: "f78985d808c7acd073e7b00d604a5bed82f1b9bdb81e1fec218e33a8e1913087",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def category(position: int, length: int) -> str:
    if length == 1:
        return "SINGLETON"
    if position == 1:
        return "FIRST_ONLY"
    if position == length:
        return "LAST_ONLY"
    return "INTERNAL"


def main() -> None:
    checks = 0

    def check(condition: bool, message: str) -> None:
        nonlocal checks
        if not condition:
            raise AssertionError(message)
        checks += 1

    observed_hashes = {path: digest(path) for path in EXPECTED}
    check(observed_hashes == EXPECTED, "frozen hash mismatch")
    rows = load(INTERLINEAR)
    residuals = load(RESIDUAL)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    index = {(row["edition"], row["locus"]): row for row in rows}
    check(len(index) == len(rows) == 15_960, "interlinear key mismatch")
    check(len(residuals) == 2_833, "residual row mismatch")

    totals: Counter[str] = Counter()
    editions: dict[str, Counter[str]] = defaultdict(Counter)
    scopes: Counter[str] = Counter()
    paragraphs: Counter[str] = Counter()
    curriers: Counter[str] = Counter()
    profiles: dict[str, Counter[str]] = defaultdict(Counter)
    profile_rows: dict[str, set[tuple[str, str]]] = defaultdict(set)
    profile_loci: dict[str, set[str]] = defaultdict(set)
    previous: dict[str, Counter[str]] = defaultdict(Counter)
    following: dict[str, Counter[str]] = defaultdict(Counter)
    physical: dict[str, list[dict[str, str]]] = defaultdict(list)
    ddy = []

    for residual in residuals:
        row = index[(residual["edition"], residual["locus"])]
        surface = row["surface"].split()
        positions = [int(value) for value in residual["omitted_positions_1based"].split(";")]
        tokens = residual["omitted_tokens"].split()
        check(len(positions) == len(tokens) == int(residual["omitted_token_count"]), "event mismatch")
        physical[row["locus"]].append(residual)
        for position, token in zip(positions, tokens):
            pos_class = category(position, len(surface))
            prev = surface[position - 2] if position > 1 else "<START>"
            nxt = surface[position] if position < len(surface) else "<END>"
            totals.update({"events": 1, pos_class: 1})
            editions[row["edition"]].update({"events": 1, pos_class: 1})
            scopes[row["grammar_scope"]] += 1
            paragraphs[row["paragraph_state"]] += 1
            curriers[row["currier"] or "UNMARKED"] += 1
            profiles[token].update({
                "events": 1,
                pos_class: 1,
                f"scope:{row['grammar_scope']}": 1,
                f"paragraph:{row['paragraph_state']}": 1,
                f"currier:{row['currier'] or 'UNMARKED'}": 1,
            })
            profile_rows[token].add((row["edition"], row["locus"]))
            profile_loci[token].add(row["locus"])
            previous[token][prev] += 1
            following[token][nxt] += 1
            if token == "ddy":
                ddy.append({
                    "edition": row["edition"],
                    "locus": row["locus"],
                    "token": token,
                    "position": position,
                    "surface_length": len(surface),
                    "position_class": pos_class,
                    "grammar_scope": row["grammar_scope"],
                    "paragraph_state": row["paragraph_state"],
                    "currier": row["currier"],
                    "section": row["section"],
                    "previous_surface": prev,
                    "following_surface": nxt,
                })

    check(sum(totals[name] for name in ("SINGLETON", "FIRST_ONLY", "LAST_ONLY", "INTERNAL")) == totals["events"], "position partition")
    expected_totals = {
        "events": totals["events"],
        "affected_rows": len(residuals),
        "affected_physical_loci": len(physical),
        "token_types": len(profiles),
        "position": {name: totals[name] for name in ("SINGLETON", "FIRST_ONLY", "LAST_ONLY", "INTERNAL")},
        "scope": dict(sorted(scopes.items())),
        "paragraph": dict(sorted(paragraphs.items())),
        "currier": dict(sorted(curriers.items())),
    }
    check(result["totals"] == expected_totals, "total reconstruction")
    check(expected_totals["position"] == {"SINGLETON": 61, "FIRST_ONLY": 172, "LAST_ONLY": 787, "INTERNAL": 2818}, "position constants")
    check(expected_totals["scope"] == {"CONFIRMED_PROSE": 3316, "DIAGNOSTIC_NONPROSE": 522}, "scope constants")

    expected_editions = {
        edition: {
            "events": counts["events"],
            "position": {name: counts[name] for name in ("SINGLETON", "FIRST_ONLY", "LAST_ONLY", "INTERNAL")},
        }
        for edition, counts in sorted(editions.items())
    }
    check(result["by_edition"] == expected_editions, "edition reconstruction")

    def top(counter: Counter[str]) -> list[dict[str, object]]:
        return [{"value": value, "count": count} for value, count in counter.most_common(8)]

    expected_profiles = {}
    for token in sorted(profiles):
        counts = profiles[token]
        expected_profiles[token] = {
            "events": counts["events"],
            "edition_rows": len(profile_rows[token]),
            "physical_loci": len(profile_loci[token]),
            "position": {name: counts[name] for name in ("SINGLETON", "FIRST_ONLY", "LAST_ONLY", "INTERNAL")},
            "scope": {name: counts[f"scope:{name}"] for name in ("CONFIRMED_PROSE", "DIAGNOSTIC_NONPROSE")},
            "paragraph": {name: counts[f"paragraph:{name}"] for name in ("OPEN", "CONT")},
            "currier": {name: counts[f"currier:{name}"] for name in ("A", "B", "UNMARKED")},
            "top_previous_surface": top(previous[token]),
            "top_following_surface": top(following[token]),
        }
    check(result["token_profiles"] == expected_profiles, "profile reconstruction")
    check(len(expected_profiles) == 28, "type count")
    check(expected_profiles["y"]["events"] == 2463 and expected_profiles["y"]["position"]["INTERNAL"] == 1995, "y constants")
    check(expected_profiles["dy"]["events"] == 774 and expected_profiles["dy"]["position"]["LAST_ONLY"] == 285, "dy constants")

    support = Counter(len(values) for values in physical.values())
    seq = Counter()
    pos = Counter()
    for values in physical.values():
        count = len(values)
        if count >= 2:
            seq[(count, len({value["omitted_tokens"] for value in values}) == 1)] += 1
            pos[(count, len({value["position_token_pairs"] for value in values}) == 1)] += 1
    expected_cross = {
        "affected_loci_by_available_residual_readings": {str(key): value for key, value in sorted(support.items())},
        "exact_token_sequence": {f"{count}_readings_{str(exact).lower()}": value for (count, exact), value in sorted(seq.items())},
        "exact_position_token_pairs": {f"{count}_readings_{str(exact).lower()}": value for (count, exact), value in sorted(pos.items())},
    }
    check(result["cross_reading"] == expected_cross, "cross-reading reconstruction")
    check(expected_cross["affected_loci_by_available_residual_readings"] == {"1": 1197, "2": 197, "3": 414}, "support constants")

    expected_ddy = {
        "events": 6,
        "physical_loci": ["f11v.6", "f18v.8"],
        "readings_by_locus": {
            locus: sorted(str(event["edition"]) for event in ddy if event["locus"] == locus)
            for locus in ("f11v.6", "f18v.8")
        },
        "all_internal": all(event["position_class"] == "INTERNAL" for event in ddy),
        "all_confirmed_prose": all(event["grammar_scope"] == "CONFIRMED_PROSE" for event in ddy),
        "all_continuation": all(event["paragraph_state"] == "CONT" for event in ddy),
        "all_currier_a_section_h": all(event["currier"] == "A" and event["section"] == "H" for event in ddy),
        "events_detail": ddy,
    }
    check(result["ddy_profile"] == expected_ddy, "ddy reconstruction")
    check(all(expected_ddy[name] for name in ("all_internal", "all_confirmed_prose", "all_continuation", "all_currier_a_section_h")), "ddy gates")
    check(result["gates"] == {
        "residual_layer_is_exclusively_physical_line_end": False,
        "majority_of_residual_events_are_physical_line_internal": True,
        "y_majority_physical_line_internal": True,
        "ddy_is_all_reading_at_two_loci": True,
    }, "decision gates")
    check(result["status"] == "PASS_UNPARSED_SURFACE_POSITIONAL_INVENTORY", "status")
    check(result["decision"] == "NOT_EXCLUSIVELY_PHYSICAL_LINE_END_LAYOUT_PREFLIGHT_REQUIRED", "decision")
    check(result["english_lexical_glosses"] == 0, "gloss ceiling")
    check(result["claim_ceiling"] == (
        "UNPARSED_SURFACE is a transcription/segmentation-sensitive 28-type literal layer dominated by "
        "y and dy positions internal to flattened physical lines. It is not exclusively a physical-line-end "
        "layer, but internal layout boundaries remain unresolved. No token is established as a separator, "
        "suffix, number, word, sound, or meaning."
    ), "claim ceiling")
    check(result["input_sha256"] == {
        "experiments/semantic_assumptions/results/pre_grounding_interlinear.tsv": EXPECTED[INTERLINEAR],
        "experiments/semantic_assumptions/results/pre_grounding_surface_residual_atlas.tsv": EXPECTED[RESIDUAL],
    }, "input binding")

    output = {
        "status": "PASS_INDEPENDENT_UNPARSED_SURFACE_POSITIONAL_RECONSTRUCTION",
        "checks": checks,
        "events": totals["events"],
        "internal_events": totals["INTERNAL"],
        "affected_rows": len(residuals),
        "affected_physical_loci": len(physical),
        "token_types": len(profiles),
        "ddy_events": len(ddy),
        "input_sha256": {str(path.relative_to(HERE.parents[1])): value for path, value in EXPECTED.items()},
        "english_lexical_glosses": 0,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
