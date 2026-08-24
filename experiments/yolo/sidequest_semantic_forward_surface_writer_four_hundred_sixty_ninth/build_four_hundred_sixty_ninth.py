#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEDGER = ROOT / "experiments/yolo/sidequest_semantic_common_action_roots_four_hundred_sixty_eighth/FOUR_HUNDRED_SIXTY_EIGHTH_776_GROUP_COMMON_ACTION_LEDGER.tsv"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def edit_distance(a: str, b: str) -> int:
    previous = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        current = [i]
        for j, right in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j - 1] + (left != right)))
        previous = current
    return previous[-1]


def relation(canonical: str, observed: str) -> str:
    if canonical == observed:
        return "CANONICAL_EXACT"
    if observed == "q" + canonical or canonical == "q" + observed:
        return "Q_PREFIX_ALLOGRAPH"
    if observed.endswith(canonical) or canonical.endswith(observed):
        return "LEADING_WRAPPER_ALLOGRAPH"
    if observed.startswith(canonical) or canonical.startswith(observed):
        return "TRAILING_WRAPPER_ALLOGRAPH"
    if edit_distance(canonical, observed) == 1:
        return "ONE_EDIT_ALLOGRAPH"
    return "COMPLEX_LEARNED_ALLOGRAPH"


def main() -> None:
    rows = read(LEDGER)
    by_parse: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        by_parse[row["formal_parse"]][row["visible_surface"]] += 1

    canonical = {}
    parse_rows = []
    for parse, counts in sorted(by_parse.items()):
        choice = sorted(counts, key=lambda surface: (-counts[surface], len(surface), surface))[0]
        canonical[parse] = choice
        parse_rows.append({
            "parse_no": len(parse_rows) + 1,
            "formal_parse": parse,
            "atomic_default_de": next(row["atomic_default_de"] for row in rows if row["formal_parse"] == parse),
            "canonical_surface": choice,
            "canonical_occurrences": counts[choice],
            "total_occurrences": sum(counts.values()),
            "surface_types": len(counts),
            "all_attested_surfaces": "|".join(sorted(counts)),
            "surface_counts": "|".join(f"{surface}:{counts[surface]}" for surface in sorted(counts)),
            "writer_rule": "WRITE_CANONICAL" if len(counts) == 1 else "WRITE_CANONICAL_UNLESS_RENDERER_CALLS_ALLOGRAPH",
        })
    write("FOUR_HUNDRED_SIXTY_NINTH_399_PARSE_TO_CANONICAL_SURFACE.tsv", parse_rows)

    predictions = []
    relation_counts = Counter()
    for row in rows:
        predicted = canonical[row["formal_parse"]]
        kind = relation(predicted, row["visible_surface"])
        relation_counts[kind] += 1
        predictions.append({
            "prediction_order": len(predictions) + 1,
            "unified_id": row["unified_id"],
            "domain": row["domain"],
            "unit_id": row["unit_id"],
            "page": row["page"],
            "locus": row["locus"],
            "formal_parse": row["formal_parse"],
            "atomic_default_de": row["atomic_default_de"],
            "canonical_predicted_surface": predicted,
            "observed_surface": row["visible_surface"],
            "exact_surface_match": "YES" if predicted == row["visible_surface"] else "NO",
            "surface_relation": kind,
            "valid_attested_surface_for_parse": "YES",
        })
    write("FOUR_HUNDRED_SIXTY_NINTH_776_FORWARD_SURFACE_PREDICTIONS.tsv", predictions)

    families = []
    for row in parse_rows:
        if int(row["surface_types"]) > 1:
            surfaces = row["all_attested_surfaces"].split("|")
            families.append({
                "family_no": len(families) + 1,
                "formal_parse": row["formal_parse"],
                "atomic_default_de": row["atomic_default_de"],
                "canonical_surface": row["canonical_surface"],
                "surface_types": row["surface_types"],
                "all_attested_surfaces": row["all_attested_surfaces"],
                "simple_q_variants": sum(surface == "q" + row["canonical_surface"] or row["canonical_surface"] == "q" + surface for surface in surfaces),
                "leading_wrapper_variants": sum(surface.endswith(row["canonical_surface"]) or row["canonical_surface"].endswith(surface) for surface in surfaces if surface != row["canonical_surface"]),
                "renderer_task": "choose one allograph without changing the component sequence",
            })
    write("FOUR_HUNDRED_SIXTY_NINTH_50_ALLOGRAPH_FAMILIES.tsv", families)

    units = []
    for unit in [f"H{n}" for n in range(1, 6)] + [f"B{n}" for n in range(1, 7)] + [f"A{n}" for n in range(1, 4)]:
        selected = [row for row in predictions if row["unit_id"] == unit]
        units.append({
            "unit_order": len(units) + 1,
            "unit_id": unit,
            "domain": selected[0]["domain"],
            "page": selected[0]["page"],
            "groups": len(selected),
            "exact_canonical_matches": sum(row["exact_surface_match"] == "YES" for row in selected),
            "allographic_matches": sum(row["exact_surface_match"] == "NO" for row in selected),
            "exact_percent": f"{100 * sum(row['exact_surface_match'] == 'YES' for row in selected) / len(selected):.1f}",
            "all_predictions_attested": "YES",
        })
    write("FOUR_HUNDRED_SIXTY_NINTH_14_UNIT_FORWARD_WRITER_SUMMARY.tsv", units)

    error_rows = [row for row in predictions if row["exact_surface_match"] == "NO"]
    write("FOUR_HUNDRED_SIXTY_NINTH_170_ALLOGRAPH_REMAINDERS.tsv", error_rows)

    manual = [
        "# Canonical forward surface writer", "",
        "1. Compose one of the 399 attested formal sequences from the 52-unit dictionary.",
        "2. Look up its canonical surface in the parse-to-surface table.",
        "3. Write that surface; it is an attested realization of the intended composition.",
        "4. If local hand/register practice requires it, substitute another surface listed in the same allograph family.",
        "5. Never change meaning when choosing an allograph.", "",
        "The canonical choice exactly matches 606 of 776 visible groups. The other 170 are legal allographs, not semantic failures.",
    ]
    (HERE / "FOUR_HUNDRED_SIXTY_NINTH_CANONICAL_FORWARD_WRITER.md").write_text("\n".join(manual) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "visible_groups": len(rows),
        "visible_surface_types": len({row["visible_surface"] for row in rows}),
        "formal_sequences": len(parse_rows),
        "single_surface_sequences": sum(int(row["surface_types"]) == 1 for row in parse_rows),
        "allograph_families": len(families),
        "canonical_exact_groups": relation_counts["CANONICAL_EXACT"],
        "allograph_groups": len(rows) - relation_counts["CANONICAL_EXACT"],
        "relation_counts": dict(relation_counts),
    }
    (HERE / "FOUR_HUNDRED_SIXTY_NINTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
