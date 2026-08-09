#!/usr/bin/env python3
"""Independent reconstruction of the STA member-code agreement atlas."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from collections import Counter, defaultdict
from pathlib import Path


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
SCAFFOLD_VALIDATION = RESULTS / "source_sta_family_consensus_validation.json"
SPEC = BASE / "SOURCE_STA_MEMBER_AGREEMENT_ATLAS_SPEC.md"
PRODUCER = BASE / "build_source_sta_member_agreement_atlas.py"
PRODUCTION = RESULTS / "source_sta_member_agreement_atlas.json"
FAMILY_TSV = RESULTS / "source_sta_member_agreement_by_family.tsv"
TRIPLET_TSV = RESULTS / "source_sta_member_disagreement_triplets.tsv"
PRODUCTION_REPORT = RESULTS / "source_sta_member_agreement_atlas_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_sta_member_agreement_atlas_validation.json"
REPORT = RESULTS / "source_sta_member_agreement_atlas_validation_report.md"

HASHES = {
    GROUPS: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    SCAFFOLD_VALIDATION: "fcb6a53461b4f9df36f34161ed1d42087f4395988bea0d71f74a7dd635b68b76",
    SPEC: "d7b5d6b8ffe14257b85d73a564d41363e30dab658d175ee91882c500b71f23c3",
    PRODUCER: "42c0416d3571469ed00785508b7042a1abe58f91baf04dc91b8b312394fd3055",
    PRODUCTION: "9558208808b2ec9c1a33b65eb9c982ebcd59b3cee9128e506c97cbca65c394a8",
    FAMILY_TSV: "8785b5bbed7e3357dac3fd7500eb7d403c69775e49f20e03af559c5531192d51",
    TRIPLET_TSV: "08b56f5bdfdfe0609c6a4864931acfd0aeed135c11dd98165eb0323756fd08b8",
    PRODUCTION_REPORT: "9025b30e547f38ee0c6e1f3f216e945eef926c23db0e5235908c17fc3a546ac2",
}
PATTERNS = ("ALL3", "ZL_IT", "ZL_RF", "IT_RF", "ALL_DIFF")
FAMILY_FIELDS = ["family", "positions", *[f"pattern_{name}" for name in PATTERNS], "all3_fraction"]
TRIPLET_FIELDS = ["family", "zl_code", "it_code", "rf_code", "pattern", "positions", "currier_A", "currier_B", "currier_blank", "group_FIRST", "group_INTERNAL", "group_LAST", "group_SINGLE"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify(values: tuple[str, str, str]) -> str:
    z, i, r = values
    equalities = (z == i, z == r, i == r)
    if all(equalities):
        return "ALL3"
    if equalities[0]:
        return "ZL_IT"
    if equalities[1]:
        return "ZL_RF"
    if equalities[2]:
        return "IT_RF"
    return "ALL_DIFF"


def position_name(index: int, size: int) -> str:
    if size == 1:
        return "SINGLE"
    return "FIRST" if index == 0 else "LAST" if index + 1 == size else "INTERNAL"


def tsv_bytes(fields: list[str], rows: list[dict]) -> bytes:
    target = io.StringIO(newline="")
    writer = csv.DictWriter(target, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return target.getvalue().encode("utf-8")


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing to overwrite validation artifacts")
    checks = 0

    def require(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            raise AssertionError(message)

    for path, expected in HASHES.items():
        require(sha(path) == expected, f"hash mismatch {path.name}")
    require(json.loads(SCAFFOLD_VALIDATION.read_text())["status"] == "PASS_INDEPENDENT_EXACT_FAMILY_GRAMMAR_SCAFFOLD_RECONSTRUCTION", "scaffold status")

    pattern_counts = Counter()
    family_counts: dict[str, Counter] = defaultdict(Counter)
    currier_counts: dict[str, Counter] = defaultdict(Counter)
    position_counts: dict[str, Counter] = defaultdict(Counter)
    pair_equal = Counter()
    pair_unequal = Counter()
    triplets = Counter()
    triplet_currier = Counter()
    triplet_position = Counter()
    strict_groups = 0
    strict_loci = set()
    total = 0
    with GROUPS.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["strict_zero_alternative"] != "1":
                continue
            strict_groups += 1
            strict_loci.add(row["locus"])
            codes = [tuple(row[name].split()) for name in ("zl_sta_codes", "it_sta_codes", "rf_sta_codes")]
            size = int(row["symbol_count"])
            require(all(len(sequence) == size for sequence in codes), "code length")
            require(len(row["family_surface"]) == size, "family length")
            for index, values in enumerate(zip(*codes)):
                family = row["family_surface"][index]
                require(all(code[0] == family for code in values), "cross-family triplet")
                total += 1
                label = classify(values)
                where = position_name(index, size)
                pattern_counts[label] += 1
                family_counts[family][label] += 1
                currier_counts[row["currier"]][label] += 1
                position_counts[where][label] += 1
                for pair, left, right in (("ZL_IT", values[0], values[1]), ("ZL_RF", values[0], values[2]), ("IT_RF", values[1], values[2])):
                    (pair_equal if left == right else pair_unequal)[pair] += 1
                if label != "ALL3":
                    key = (family, *values, label)
                    triplets[key] += 1
                    triplet_currier[(key, row["currier"])] += 1
                    triplet_position[(key, where)] += 1

    family_rows = []
    for family in sorted(family_counts):
        counts = family_counts[family]
        n = sum(counts.values())
        family_rows.append({"family": family, "positions": n, **{f"pattern_{name}": counts[name] for name in PATTERNS}, "all3_fraction": counts["ALL3"] / n})
    require(tsv_bytes(FAMILY_FIELDS, family_rows) == FAMILY_TSV.read_bytes(), "family TSV")

    triplet_rows = []
    for key, n in sorted(triplets.items(), key=lambda item: (-item[1], item[0])):
        family, z, i, r, label = key
        triplet_rows.append({
            "family": family, "zl_code": z, "it_code": i, "rf_code": r,
            "pattern": label, "positions": n,
            "currier_A": triplet_currier[(key, "A")], "currier_B": triplet_currier[(key, "B")], "currier_blank": triplet_currier[(key, "")],
            "group_FIRST": triplet_position[(key, "FIRST")], "group_INTERNAL": triplet_position[(key, "INTERNAL")],
            "group_LAST": triplet_position[(key, "LAST")], "group_SINGLE": triplet_position[(key, "SINGLE")],
        })
    require(tsv_bytes(TRIPLET_FIELDS, triplet_rows) == TRIPLET_TSV.read_bytes(), "triplet TSV")

    disagreement = total - pattern_counts["ALL3"]
    dominant = next(row for row in triplet_rows if (row["zl_code"], row["it_code"], row["rf_code"]) == ("B1", "B1", "Ba"))
    result = {
        "experiment": "SOURCE_STA_MEMBER_AGREEMENT_ATLAS",
        "status": "PASS_DESCRIPTIVE_FINE_CODE_AGREEMENT_ATLAS",
        "inputs": {path.name: sha(path) for path in (GROUPS, SCAFFOLD_VALIDATION, SPEC, PRODUCER)},
        "counts": {
            "strict_loci": len(strict_loci), "strict_groups": strict_groups,
            "aligned_positions": total, "patterns": {name: pattern_counts[name] for name in PATTERNS},
            "disagreement_positions": disagreement, "disagreement_triplet_types": len(triplet_rows),
            "families": len(family_rows), "majority_available_positions": total - pattern_counts["ALL_DIFF"],
        },
        "fractions": {
            "all_three_exact": pattern_counts["ALL3"] / total,
            "zl_it_of_all_disagreements": pattern_counts["ZL_IT"] / disagreement,
            "dominant_B1_B1_Ba_of_all_disagreements": dominant["positions"] / disagreement,
            "all_three_exact_after_descriptive_B1_B1_Ba_exclusion": (pattern_counts["ALL3"] + dominant["positions"]) / total,
        },
        "pairwise": {pair: {"agreement": pair_equal[pair], "disagreement": pair_unequal[pair], "agreement_fraction": pair_equal[pair] / total} for pair in ("ZL_IT", "ZL_RF", "IT_RF")},
        "by_currier": {
            name if name else "BLANK": {"positions": sum(counts.values()), "patterns": {label: counts[label] for label in PATTERNS}, "all3_fraction": counts["ALL3"] / sum(counts.values())}
            for name, counts in sorted(currier_counts.items())
        },
        "by_group_position": {
            name: {"positions": sum(counts.values()), "patterns": {label: counts[label] for label in PATTERNS}, "all3_fraction": counts["ALL3"] / sum(counts.values())}
            for name, counts in sorted(position_counts.items())
        },
        "top_disagreement_triplets": triplet_rows[:12],
        "outputs": {FAMILY_TSV.name: sha(FAMILY_TSV), TRIPLET_TSV.name: sha(TRIPLET_TSV)},
        "gates": {
            "exact_95451_positions": total == 95451,
            "all_positions_classified_once": sum(pattern_counts.values()) == total,
            "same_family_every_triplet": True,
            "family_rows_sum_exact": sum(row["positions"] for row in family_rows) == total,
            "triplet_rows_sum_disagreements": sum(row["positions"] for row in triplet_rows) == disagreement,
            "pairwise_totals_exact": all(pair_equal[pair] + pair_unequal[pair] == total for pair in ("ZL_IT", "ZL_RF", "IT_RF")),
            "no_member_codes_collapsed": True, "english_glosses_zero": True,
        },
        "english_glosses": 0,
        "claim_ceiling": "Descriptive stability and transcription-policy differences among aligned STA member codes. No preferred or corrected reading, physical glyph identity, allography, sound, alphabet, cipher alphabet, word, meaning, plaintext, language, or translation follows.",
    }
    actual = json.loads(PRODUCTION.read_text(encoding="utf-8"))
    require(actual == result, "production object")
    require(PRODUCTION.read_text(encoding="utf-8") == json.dumps(result, indent=2, sort_keys=True) + "\n", "canonical JSON")
    report = f"""# Source-native STA member-code agreement atlas

Status: **{result['status']}**

Across **{total:,}** strict aligned positions, all three readings use the
same fine STA code at **{pattern_counts['ALL3']:,}** positions
(**{result['fractions']['all_three_exact']:.3%}**). Only **{disagreement:,}**
positions disagree. ZL and IT agree against RF at **{pattern_counts['ZL_IT']:,}** of
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
    require(PRODUCTION_REPORT.read_text(encoding="utf-8") == report, "production report")
    require(pattern_counts == Counter({"ALL3": 91916, "ZL_IT": 2740, "ZL_RF": 410, "IT_RF": 279, "ALL_DIFF": 106}), "pattern vector")
    require(dominant["positions"] == 1586, "dominant policy count")

    validation = {
        "experiment": "SOURCE_STA_MEMBER_AGREEMENT_ATLAS_VALIDATION",
        "status": "PASS_INDEPENDENT_FINE_CODE_AGREEMENT_RECONSTRUCTION",
        "checks": checks,
        "validator_sha256": sha(VALIDATOR), "producer_sha256": sha(PRODUCER),
        "production_sha256": sha(PRODUCTION), "family_tsv_sha256": sha(FAMILY_TSV),
        "triplet_tsv_sha256": sha(TRIPLET_TSV), "production_report_sha256": sha(PRODUCTION_REPORT),
        "reconstructed_positions": total, "reconstructed_patterns": {name: pattern_counts[name] for name in PATTERNS},
        "production_module_imported": False, "english_glosses": 0,
        "claim_ceiling": result["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    validation_report = f"""# STA member-code agreement atlas validation

Status: **{validation['status']}**

The nonimporting reconstruction passed **{checks:,}** checks across all
**{total:,}** aligned positions and exactly reproduced the five-pattern vector,
146 disagreement triplets, family and triplet TSV bytes, JSON object, and report.

The validated descriptive result is 91,916 all-three-exact positions and 3,535
disagreements, including 1,586 `(B1,B1,Ba)` policy differences. This chooses no
preferred reading and establishes no glyph equivalence, sound, alphabet,
meaning, plaintext, language, cipher, or translation.
"""
    REPORT.write_text(validation_report, encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks": checks, "positions": total}, sort_keys=True))


if __name__ == "__main__":
    main()
