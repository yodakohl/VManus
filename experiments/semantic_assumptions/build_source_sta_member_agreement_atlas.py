#!/usr/bin/env python3
"""Build a descriptive STA member-code agreement/confusion atlas."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
SCAFFOLD_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
SPEC = BASE / "SOURCE_STA_MEMBER_AGREEMENT_ATLAS_SPEC.md"
BUILDER = Path(__file__).resolve()
OUT_JSON = RESULTS / "source_sta_member_agreement_atlas.json"
OUT_FAMILY = RESULTS / "source_sta_member_agreement_by_family.tsv"
OUT_TRIPLETS = RESULTS / "source_sta_member_disagreement_triplets.tsv"
REPORT = RESULTS / "source_sta_member_agreement_atlas_report.md"

FROZEN = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SCAFFOLD_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
}
PATTERNS = ("ALL3", "ZL_IT", "ZL_RF", "IT_RF", "ALL_DIFF")
FAMILY_FIELDS = ["family", "positions", *[f"pattern_{name}" for name in PATTERNS], "all3_fraction"]
TRIPLET_FIELDS = [
    "family", "zl_code", "it_code", "rf_code", "pattern", "positions",
    "currier_A", "currier_B", "currier_blank", "group_FIRST",
    "group_INTERNAL", "group_LAST", "group_SINGLE",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pattern(zl: str, it: str, rf: str) -> str:
    if zl == it == rf:
        return "ALL3"
    if zl == it:
        return "ZL_IT"
    if zl == rf:
        return "ZL_RF"
    if it == rf:
        return "IT_RF"
    return "ALL_DIFF"


def group_position(index: int, length: int) -> str:
    if length == 1:
        return "SINGLE"
    if index == 0:
        return "FIRST"
    if index == length - 1:
        return "LAST"
    return "INTERNAL"


def main() -> None:
    outputs = (OUT_JSON, OUT_FAMILY, OUT_TRIPLETS, REPORT)
    if any(path.exists() for path in outputs):
        raise SystemExit("refusing to overwrite member-agreement artifacts")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen input mismatch {path.name}")
    validation = json.loads(SCAFFOLD_VALIDATION.read_text(encoding="utf-8"))
    if validation["status"] != "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION":
        raise SystemExit("source scaffold validation is not PASS")

    with GROUPS.open(encoding="utf-8", newline="") as handle:
        source = list(csv.DictReader(handle, delimiter="\t"))
    strict = [row for row in source if row["strict_zero_alternative"] == "1"]
    patterns = Counter()
    by_family: dict[str, Counter] = defaultdict(Counter)
    by_currier: dict[str, Counter] = defaultdict(Counter)
    by_position: dict[str, Counter] = defaultdict(Counter)
    pair_agreement = Counter()
    pair_disagreement = Counter()
    triplet_count = Counter()
    triplet_currier = Counter()
    triplet_position = Counter()
    loci = set()
    positions = 0
    for row in strict:
        zl = row["zl_sta_codes"].split()
        it = row["it_sta_codes"].split()
        rf = row["rf_sta_codes"].split()
        families = row["family_surface"]
        if not (len(zl) == len(it) == len(rf) == len(families) == int(row["symbol_count"])):
            raise ValueError(f"group length drift {row['consensus_group_id']}")
        loci.add(row["locus"])
        for index, (family, zcode, icode, rcode) in enumerate(zip(families, zl, it, rf)):
            if zcode[0] != family or icode[0] != family or rcode[0] != family:
                raise ValueError(f"cross-family code triplet {row['consensus_group_id']}:{index}")
            positions += 1
            label = pattern(zcode, icode, rcode)
            position = group_position(index, len(zl))
            patterns[label] += 1
            by_family[family][label] += 1
            by_currier[row["currier"]][label] += 1
            by_position[position][label] += 1
            for edition_pair, left, right in (
                ("ZL_IT", zcode, icode), ("ZL_RF", zcode, rcode), ("IT_RF", icode, rcode)
            ):
                if left == right:
                    pair_agreement[edition_pair] += 1
                else:
                    pair_disagreement[edition_pair] += 1
            if label != "ALL3":
                key = (family, zcode, icode, rcode, label)
                triplet_count[key] += 1
                triplet_currier[(key, row["currier"])] += 1
                triplet_position[(key, position)] += 1
    if positions != 95451 or patterns["ALL3"] != 91916:
        raise ValueError("strict-position count drift")

    family_rows = []
    for family in sorted(by_family):
        counts = by_family[family]
        total = sum(counts.values())
        family_rows.append({
            "family": family,
            "positions": total,
            **{f"pattern_{name}": counts[name] for name in PATTERNS},
            "all3_fraction": counts["ALL3"] / total,
        })
    with OUT_FAMILY.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FAMILY_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(family_rows)

    triplet_rows = []
    for key, count in sorted(triplet_count.items(), key=lambda item: (-item[1], item[0])):
        family, zcode, icode, rcode, label = key
        triplet_rows.append({
            "family": family,
            "zl_code": zcode,
            "it_code": icode,
            "rf_code": rcode,
            "pattern": label,
            "positions": count,
            "currier_A": triplet_currier[(key, "A")],
            "currier_B": triplet_currier[(key, "B")],
            "currier_blank": triplet_currier[(key, "")],
            "group_FIRST": triplet_position[(key, "FIRST")],
            "group_INTERNAL": triplet_position[(key, "INTERNAL")],
            "group_LAST": triplet_position[(key, "LAST")],
            "group_SINGLE": triplet_position[(key, "SINGLE")],
        })
    with OUT_TRIPLETS.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRIPLET_FIELDS, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(triplet_rows)

    disagreement = positions - patterns["ALL3"]
    top = triplet_rows[:12]
    dominant = next(row for row in triplet_rows if (row["zl_code"], row["it_code"], row["rf_code"]) == ("B1", "B1", "Ba"))
    result = {
        "experiment": "SOURCE_STA_MEMBER_AGREEMENT_ATLAS",
        "status": "PASS_DESCRIPTIVE_FINE_CODE_AGREEMENT_ATLAS",
        "inputs": {path.name: sha(path) for path in (*FROZEN, SPEC, BUILDER)},
        "counts": {
            "strict_loci": len(loci),
            "strict_groups": len(strict),
            "aligned_positions": positions,
            "patterns": {name: patterns[name] for name in PATTERNS},
            "disagreement_positions": disagreement,
            "disagreement_triplet_types": len(triplet_rows),
            "families": len(family_rows),
            "majority_available_positions": positions - patterns["ALL_DIFF"],
        },
        "fractions": {
            "all_three_exact": patterns["ALL3"] / positions,
            "zl_it_of_all_disagreements": patterns["ZL_IT"] / disagreement,
            "dominant_B1_B1_Ba_of_all_disagreements": dominant["positions"] / disagreement,
            "all_three_exact_after_descriptive_B1_B1_Ba_exclusion": (patterns["ALL3"] + dominant["positions"]) / positions,
        },
        "pairwise": {
            pair: {
                "agreement": pair_agreement[pair],
                "disagreement": pair_disagreement[pair],
                "agreement_fraction": pair_agreement[pair] / positions,
            }
            for pair in ("ZL_IT", "ZL_RF", "IT_RF")
        },
        "by_currier": {
            currier if currier else "BLANK": {
                "positions": sum(counts.values()),
                "patterns": {name: counts[name] for name in PATTERNS},
                "all3_fraction": counts["ALL3"] / sum(counts.values()),
            }
            for currier, counts in sorted(by_currier.items())
        },
        "by_group_position": {
            position: {
                "positions": sum(counts.values()),
                "patterns": {name: counts[name] for name in PATTERNS},
                "all3_fraction": counts["ALL3"] / sum(counts.values()),
            }
            for position, counts in sorted(by_position.items())
        },
        "top_disagreement_triplets": top,
        "outputs": {
            OUT_FAMILY.name: sha(OUT_FAMILY),
            OUT_TRIPLETS.name: sha(OUT_TRIPLETS),
        },
        "gates": {
            "exact_95451_positions": positions == 95451,
            "all_positions_classified_once": sum(patterns.values()) == positions,
            "same_family_every_triplet": True,
            "family_rows_sum_exact": sum(row["positions"] for row in family_rows) == positions,
            "triplet_rows_sum_disagreements": sum(row["positions"] for row in triplet_rows) == disagreement,
            "pairwise_totals_exact": all(pair_agreement[pair] + pair_disagreement[pair] == positions for pair in ("ZL_IT", "ZL_RF", "IT_RF")),
            "no_member_codes_collapsed": True,
            "english_glosses_zero": True,
        },
        "english_glosses": 0,
        "claim_ceiling": (
            "Descriptive stability and transcription-policy differences among aligned STA member codes. "
            "No preferred or corrected reading, physical glyph identity, allography, sound, alphabet, "
            "cipher alphabet, word, meaning, plaintext, language, or translation follows."
        ),
    }
    if not all(result["gates"].values()):
        raise ValueError("member agreement gate failure")
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# Source-native STA member-code agreement atlas

Status: **{result['status']}**

Across **{positions:,}** strict aligned positions, all three readings use the
same fine STA code at **{patterns['ALL3']:,}** positions
(**{result['fractions']['all_three_exact']:.3%}**). Only **{disagreement:,}**
positions disagree. ZL and IT agree against RF at **{patterns['ZL_IT']:,}** of
those (**{result['fractions']['zl_it_of_all_disagreements']:.3%}**).

One exact policy difference, `(ZL,IT,RF) = (B1,B1,Ba)`, occurs at
**{dominant['positions']:,}** positions and alone accounts for
**{result['fractions']['dominant_B1_B1_Ba_of_all_disagreements']:.3%}** of all
fine-code disagreements. Pairwise exact agreement is
**{result['pairwise']['ZL_IT']['agreement_fraction']:.3%}** for ZL/IT,
**{result['pairwise']['ZL_RF']['agreement_fraction']:.3%}** for ZL/RF, and
**{result['pairwise']['IT_RF']['agreement_fraction']:.3%}** for IT/RF.

This means the fine layer is mostly stable, while a large share of its residual
variation is systematic transcription policy rather than arbitrary noise. It
does not say which code is physically correct and does not establish
allography, sound, alphabet, cipher, word, meaning, plaintext, language, or
translation.
"""
    REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({"status": result["status"], "positions": positions, "all3": patterns["ALL3"], "disagreements": disagreement}, sort_keys=True))


if __name__ == "__main__":
    main()
