#!/usr/bin/env python3
"""Descriptive source-native overlap audit for duplicated zodiac signs."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

B = Path(__file__).resolve().parent
R = B / "results"
ALIGN = R / "source_sta_group_alignment.tsv"
META = R / "source_separator_transcription.tsv"
PAGES = R / "public_voynich_nu_page_annotations_v2.tsv"
METHOD = B / "ZODIAC_DUPLICATE_SOURCE_NATIVE_OVERLAP_METHOD.md"
OUT = R / "zodiac_duplicate_source_native_overlap.json"
TSV = R / "zodiac_duplicate_source_native_overlap_candidates.tsv"
REPORT = R / "zodiac_duplicate_source_native_overlap_report.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
HALVES = ("f70v1", "f71r", "f71v", "f72r1")
TRUE = (("f70v1", "f71r"), ("f71v", "f72r1"))
MATCHINGS = (
    ("PUBLIC_ARIES_TAURUS", TRUE),
    ("CROSS_1", (("f70v1", "f71v"), ("f71r", "f72r1"))),
    ("CROSS_2", (("f70v1", "f72r1"), ("f71r", "f71v"))),
)
SIGN_RE = re.compile(r"\bemblem of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b", re.I)
VIEWS = tuple([f"FAMILY_N{n}" for n in range(2, 6)] + [f"MEMBER_N{n}" for n in range(1, 4)] + ["FAMILY_GROUP"])


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def page_key(page: str) -> tuple[int, str]:
    return int(re.match(r"f(\d+)", page).group(1)), page


def features(row: dict[str, str]) -> dict[str, list[str]]:
    families = list(row["primary_sta_families"])
    members = row["primary_sta_codes"].split()
    output: dict[str, list[str]] = {}
    for n in range(2, 6):
        output[f"FAMILY_N{n}"] = ["".join(families[i:i+n]) for i in range(len(families)-n+1)]
    for n in range(1, 4):
        output[f"MEMBER_N{n}"] = ["-".join(members[i:i+n]) for i in range(len(members)-n+1)]
    output["FAMILY_GROUP"] = [row["primary_sta_families"]]
    return output


def weighted_jaccard(left: Counter[str], right: Counter[str]) -> float:
    keys = sorted(set(left) | set(right))
    denominator = sum(max(left[key], right[key]) for key in keys)
    return sum(min(left[key], right[key]) for key in keys) / denominator if denominator else 0.0


def main() -> None:
    if any(path.exists() for path in (OUT, TSV, REPORT)):
        raise SystemExit("refusing overwrite")
    page_rows = read_tsv(PAGES)
    signs = {}
    for row in page_rows:
        match = SIGN_RE.search(row["illustrations"])
        if match:
            signs[row["page"]] = match.group(1).upper()
    if len(signs) != 12 or {page for page, sign in signs.items() if sign == "ARIES"} != {"f70v1", "f71r"} or {page for page, sign in signs.items() if sign == "TAURUS"} != {"f71v", "f72r1"}:
        raise AssertionError("public zodiac identity panel changed")
    if any(row["tentative_identifications_are_role_evidence"] != "0" for row in page_rows):
        raise AssertionError("tentative identity role gate changed")

    meta_rows = read_tsv(META)
    metadata = {row["source_group_id"]: row for row in meta_rows}
    if len(metadata) != len(meta_rows):
        raise AssertionError("duplicate metadata group IDs")
    counters: dict[tuple[str, str, str], Counter[str]] = {
        (page, edition, view): Counter()
        for page in signs for edition in EDITIONS for view in VIEWS
    }
    witnesses: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    total_zodiac_groups = 0
    excluded_alternative_groups = 0
    for row in read_tsv(ALIGN):
        info = metadata.get(row["source_group_id"])
        if info is None:
            raise AssertionError("alignment group absent from metadata")
        page = info["page"]
        if page not in signs:
            continue
        total_zodiac_groups += 1
        if int(row["alternative_site_count"]):
            excluded_alternative_groups += 1
            continue
        edition = row["edition"]
        for view, values in features(row).items():
            counters[(page, edition, view)].update(values)
            for value in set(values):
                witnesses[(page, edition, view, value)].append({
                    "source_group_id": row["source_group_id"],
                    "locus": row["locus"],
                    "kind": info["kind"],
                    "code": info["code"],
                    "family_surface": row["primary_sta_families"],
                    "member_codes": row["primary_sta_codes"],
                })

    matching_rows = []
    for edition in EDITIONS:
        for view in VIEWS:
            scored = []
            for name, matching in MATCHINGS:
                pair_scores = [weighted_jaccard(counters[(a, edition, view)], counters[(b, edition, view)]) for a, b in matching]
                scored.append({"matching": name, "sum_score": sum(pair_scores), "pair_scores": pair_scores})
            observed = scored[0]["sum_score"]
            inclusive_rank = 1 + sum(item["sum_score"] > observed for item in scored[1:])
            strict_rank = 1 + sum(item["sum_score"] >= observed for item in scored[1:])
            matching_rows.append({
                "edition": edition, "view": view, "matchings": scored,
                "public_inclusive_rank": inclusive_rank,
                "public_strict_rank": strict_rank,
                "public_tied_top": sum(item["sum_score"] == observed for item in scored),
            })

    candidates = []
    other_pages_by_sign = {
        sign: sorted(set(signs) - set(pair), key=page_key)
        for sign, pair in {"ARIES": TRUE[0], "TAURUS": TRUE[1]}.items()
    }
    for sign, pair in {"ARIES": TRUE[0], "TAURUS": TRUE[1]}.items():
        for view in VIEWS:
            shared = set(counters[(pair[0], EDITIONS[0], view)])
            for page in pair:
                for edition in EDITIONS:
                    shared &= set(counters[(page, edition, view)])
            for value in sorted(shared):
                if any(counters[(page, edition, view)][value] for page in other_pages_by_sign[sign] for edition in EDITIONS):
                    continue
                count_map = {
                    f"{page}|{edition}": counters[(page, edition, view)][value]
                    for page in pair for edition in EDITIONS
                }
                witness_map = {}
                role_map = {}
                for page in pair:
                    for edition in EDITIONS:
                        key = f"{page}|{edition}"
                        rows = witnesses[(page, edition, view, value)]
                        witness_map[key] = [row["source_group_id"] for row in rows]
                        role_map[key] = sorted({row["kind"] for row in rows})
                candidates.append({
                    "candidate_id": f"{sign}|{view}|{value}",
                    "sign": sign, "view": view, "feature": value,
                    "pair_pages": list(pair), "counts": count_map,
                    "roles": role_map, "witnesses": witness_map,
                })

    candidate_fields = ["candidate_id", "sign", "view", "feature", "pair_pages", "minimum_pair_reading_count", "role_profiles", "witness_group_ids"]
    with TSV.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=candidate_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for item in candidates:
            writer.writerow({
                "candidate_id": item["candidate_id"], "sign": item["sign"], "view": item["view"], "feature": item["feature"],
                "pair_pages": ";".join(item["pair_pages"]),
                "minimum_pair_reading_count": min(item["counts"].values()),
                "role_profiles": json.dumps(item["roles"], sort_keys=True, separators=(",", ":")),
                "witness_group_ids": json.dumps(item["witnesses"], sort_keys=True, separators=(",", ":")),
            })

    all_top = sum(row["public_inclusive_rank"] == 1 for row in matching_rows)
    unique_top = sum(row["public_strict_rank"] == 1 for row in matching_rows)
    status = "PROVISIONAL_SIGN_SPECIFIC_SOURCE_NATIVE_CANDIDATES" if candidates else "ZERO_SIGN_SPECIFIC_SOURCE_NATIVE_CANDIDATES"
    result = {
        "experiment": "ZODIAC_DUPLICATE_SOURCE_NATIVE_OVERLAP",
        "status": status,
        "decision": "DESCRIPTIVE_ONLY_MINIMUM_LAYOUT_P_ONE_THIRD",
        "inputs": {path.name: sha(path) for path in (ALIGN, META, PAGES, METHOD, Path(__file__))},
        "public_identity_source": "illustration descriptions only; tentative identities ignored",
        "zodiac_signs": {page: signs[page] for page in sorted(signs, key=page_key)},
        "fixed_true_matching": [[a, b] for a, b in TRUE],
        "counts": {
            "zodiac_pages": len(signs), "half_sign_pages": len(HALVES), "layout_preserving_matchings": len(MATCHINGS),
            "minimum_attainable_one_sided_p": 1 / len(MATCHINGS),
            "source_groups": total_zodiac_groups, "excluded_alternative_groups": excluded_alternative_groups,
            "matching_views": len(matching_rows), "public_matching_top_views": all_top,
            "public_matching_unique_top_views": unique_top, "sign_specific_candidates": len(candidates),
        },
        "matching_results": matching_rows,
        "candidates": candidates,
        "candidate_tsv_sha256": sha(TSV),
        "gates": {
            "exact_12_public_zodiac_pages": len(signs) == 12,
            "exact_two_aries_and_two_taurus_pages": True,
            "all_three_readings_scored_separately": {row["edition"] for row in matching_rows} == set(EDITIONS),
            "exact_three_layout_preserving_matchings": len(MATCHINGS) == 3,
            "confirmatory_power_insufficient": 1 / len(MATCHINGS) > 0.05,
            "tentative_identities_excluded": True,
            "no_label_proximity_or_day_order": True,
            "zero_english_glosses": True,
        },
        "claim_ceiling": "Descriptive all-reading source-native overlap across two duplicated public-icon sign identities; no candidate is a sign name, month, day, word, lexeme, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    by_sign = Counter(item["sign"] for item in candidates)
    REPORT.write_text(
        "# Duplicated-zodiac source-native overlap\n\n"
        f"Status: **{status}**\n\n"
        f"The public Aries/Taurus matching ranks top in **{all_top}/{len(matching_rows)}** reading-by-view comparisons and uniquely top in **{unique_top}/{len(matching_rows)}**. "
        "Only three layout-preserving matchings exist, so this is not a confirmatory test (minimum p = 1/3).\n\n"
        f"The frozen exact absence rule retains **{len(candidates)}** all-reading sign-specific candidates: Aries **{by_sign['ARIES']}**, Taurus **{by_sign['TAURUS']}**. "
        "Candidates, if any, are neutral source-native subword leads only. They are not sign names, months, days, words, meanings, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": status, "candidates": len(candidates), "top_views": all_top}, sort_keys=True))


if __name__ == "__main__":
    main()
