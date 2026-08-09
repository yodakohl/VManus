#!/usr/bin/env python3
"""Post-result specificity audit for duplicated-zodiac candidates."""

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
FROZEN = R / "zodiac_duplicate_source_native_overlap.json"
METHOD = B / "ZODIAC_DUPLICATE_CANDIDATE_SPECIFICITY_METHOD.md"
OUT = R / "zodiac_duplicate_candidate_specificity.json"
REPORT = R / "zodiac_duplicate_candidate_specificity_report.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
TRUE = (("f70v1", "f71r"), ("f71v", "f72r1"))
MATCHINGS = (
    ("PUBLIC_ARIES_TAURUS", TRUE),
    ("CROSS_1", (("f70v1", "f71v"), ("f71r", "f72r1"))),
    ("CROSS_2", (("f70v1", "f72r1"), ("f71r", "f71v"))),
)
VIEWS = tuple([f"FAMILY_N{n}" for n in range(2, 6)] + [f"MEMBER_N{n}" for n in range(1, 4)] + ["FAMILY_GROUP"])
SIGN_RE = re.compile(r"\bemblem of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b", re.I)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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


def page_sort(page: str) -> tuple[int, str]:
    match = re.match(r"f(\d+)", page)
    return (int(match.group(1)), page) if match else (10_000, page)


def json_sha(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")

    page_rows = read_tsv(PAGES)
    signs: dict[str, str] = {}
    for row in page_rows:
        match = SIGN_RE.search(row["illustrations"])
        if match:
            signs[row["page"]] = match.group(1).upper()
    if len(signs) != 12:
        raise AssertionError("public zodiac panel changed")
    if {page for page, sign in signs.items() if sign == "ARIES"} != set(TRUE[0]):
        raise AssertionError("public Aries pair changed")
    if {page for page, sign in signs.items() if sign == "TAURUS"} != set(TRUE[1]):
        raise AssertionError("public Taurus pair changed")
    if any(row["tentative_identifications_are_role_evidence"] != "0" for row in page_rows):
        raise AssertionError("tentative identification gate changed")

    meta_rows = read_tsv(META)
    metadata = {row["source_group_id"]: row for row in meta_rows}
    if len(metadata) != len(meta_rows):
        raise AssertionError("duplicate metadata group ID")
    align_rows = read_tsv(ALIGN)
    if len({row["source_group_id"] for row in align_rows}) != len(align_rows):
        raise AssertionError("duplicate alignment group ID")

    counters: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    occurrences: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    family_page_editions: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    family_page_roles: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for row in align_rows:
        info = metadata.get(row["source_group_id"])
        if info is None:
            raise AssertionError("alignment group missing metadata")
        if int(row["alternative_site_count"]):
            continue
        page, edition = info["page"], row["edition"]
        row_features = features(row)
        for view, values in row_features.items():
            counters[(page, edition, view)].update(values)
            for value, multiplicity in Counter(values).items():
                occurrences[(view, value)].append({
                    "edition": edition,
                    "page": page,
                    "locus": row["locus"],
                    "source_group_id": row["source_group_id"],
                    "role": info["kind"],
                    "multiplicity": multiplicity,
                    "family_surface": row["primary_sta_families"],
                    "member_codes": row["primary_sta_codes"],
                    "nearest_basic_eva": row["nearest_basic_eva_primary"],
                })
        family = row["primary_sta_families"]
        family_page_editions[family][page].add(edition)
        family_page_roles[(family, page, edition)].add(info["kind"])

    matching_diagnostics = []
    for name, matching in MATCHINGS:
        by_view = Counter()
        details = []
        for pair_index, pair in enumerate(matching):
            for view in VIEWS:
                shared = set(counters[(pair[0], EDITIONS[0], view)])
                for page in pair:
                    for edition in EDITIONS:
                        shared &= set(counters[(page, edition, view)])
                retained = []
                for value in sorted(shared):
                    if any(counters[(page, edition, view)][value] for page in signs if page not in pair for edition in EDITIONS):
                        continue
                    retained.append(value)
                by_view[view] += len(retained)
                for value in retained:
                    details.append({"pair_index": pair_index, "pages": list(pair), "view": view, "feature": value})
        matching_diagnostics.append({
            "matching": name,
            "pairs": [list(pair) for pair in matching],
            "candidate_count": sum(by_view.values()),
            "counts_by_view": {view: by_view[view] for view in VIEWS},
            "candidates": details,
        })

    frozen = json.loads(FROZEN.read_text())
    frozen_ids = {item["candidate_id"] for item in frozen["candidates"]}
    rebuilt_public_ids = {
        f"{('ARIES' if item['pair_index'] == 0 else 'TAURUS')}|{item['view']}|{item['feature']}"
        for item in matching_diagnostics[0]["candidates"]
    }
    if frozen_ids != rebuilt_public_ids:
        raise AssertionError("frozen candidate inventory does not reconstruct")

    candidate_support = []
    for candidate in frozen["candidates"]:
        rows = occurrences[(candidate["view"], candidate["feature"])]
        editions = Counter()
        pages_seen, loci_seen, roles_seen, eva_seen = set(), set(), set(), set()
        for row in rows:
            editions[str(row["edition"])] += int(row["multiplicity"])
            pages_seen.add(str(row["page"]))
            loci_seen.add(str(row["locus"]))
            roles_seen.add(str(row["role"]))
            eva_seen.add(str(row["nearest_basic_eva"]))
        page_values = sorted(pages_seen, key=page_sort)
        locus_values = sorted(loci_seen, key=lambda value: (page_sort(value.split(".")[0]), value))
        eva_values = sorted(eva_seen)
        ordered_rows = sorted(rows, key=lambda row: (str(row["edition"]), page_sort(str(row["page"])), str(row["source_group_id"])))
        pair_witnesses = [row for row in ordered_rows if row["page"] in candidate["pair_pages"]]
        candidate_support.append({
            "candidate_id": candidate["candidate_id"],
            "occurrences_by_edition": {edition: editions[edition] for edition in EDITIONS},
            "page_count": len(page_values), "pages_sha256": json_sha(page_values), "page_sample": page_values[:12],
            "physical_locus_count": len(locus_values), "physical_loci_sha256": json_sha(locus_values), "physical_locus_sample": locus_values[:12],
            "source_group_count": len(rows),
            "roles": sorted(roles_seen),
            "nearest_basic_eva_count": len(eva_values), "nearest_basic_eva_sha256": json_sha(eva_values), "nearest_basic_eva_sample": eva_values[:12],
            "witnesses_sha256": json_sha(ordered_rows), "candidate_pair_witnesses": pair_witnesses,
        })

    pair_counts: Counter[tuple[str, str]] = Counter()
    pair_features: dict[tuple[str, str], list[str]] = defaultdict(list)
    circular_pair_counts: Counter[tuple[str, str]] = Counter()
    circular_pair_features: dict[tuple[str, str], list[str]] = defaultdict(list)
    for family, page_editions in family_page_editions.items():
        pages_any = set(page_editions)
        if len(pages_any) != 2 or any(page_editions[page] != set(EDITIONS) for page in pages_any):
            continue
        pair = tuple(sorted(pages_any))
        pair_counts[pair] += 1
        pair_features[pair].append(family)
        if all("C" in family_page_roles[(family, page, edition)] for page in pair for edition in EDITIONS):
            circular_pair_counts[pair] += 1
            circular_pair_features[pair].append(family)

    zodiac_pages = sorted(signs, key=page_sort)
    zodiac_pairs = [tuple(sorted((left, right))) for i, left in enumerate(zodiac_pages) for right in zodiac_pages[i+1:]]
    taurus_pair = tuple(sorted(TRUE[1]))
    taurus_count = pair_counts[taurus_pair]
    taurus_circular_count = circular_pair_counts[taurus_pair]
    zodiac_exact_rows = [
        {"pages": list(pair), "count": pair_counts[pair], "features": sorted(pair_features[pair])}
        for pair in zodiac_pairs if pair_counts[pair]
    ]
    all_circular_rows = [
        {"pages": list(pair), "count": circular_pair_counts[pair], "features": sorted(circular_pair_features[pair])}
        for pair in sorted(circular_pair_counts) if circular_pair_counts[pair]
    ]

    result = {
        "experiment": "ZODIAC_DUPLICATE_CANDIDATE_SPECIFICITY",
        "status": "POSTHOC_CANDIDATE_NOT_PRIVILEGED_BY_PAIR_CONTROLS",
        "decision": "RETAIN_WEAK_TAURUS_SCENE_CIRCULAR_REPEAT_NO_LEXICAL_GLOSS",
        "inputs": {path.name: sha(path) for path in (ALIGN, META, PAGES, FROZEN, METHOD, Path(__file__))},
        "public_identity_source": "illustration descriptions only; tentative identities ignored",
        "matching_diagnostics": matching_diagnostics,
        "candidate_support": candidate_support,
        "globally_two_page_exclusive_family_groups": {
            "qualified_features": sum(pair_counts.values()),
            "nonzero_page_pairs": len(pair_counts),
            "maximum_features_on_one_pair": max(pair_counts.values()),
            "count_histogram": {str(key): value for key, value in sorted(Counter(pair_counts.values()).items())},
            "zodiac_nonzero_pairs": zodiac_exact_rows,
            "zodiac_nonzero_pair_count": len(zodiac_exact_rows),
            "taurus_pair_count": taurus_count,
            "taurus_inclusive_rank_among_66_zodiac_pairs": 1 + sum(pair_counts[pair] > taurus_count for pair in zodiac_pairs),
            "taurus_tied_pairs_among_66_zodiac_pairs": sum(pair_counts[pair] == taurus_count for pair in zodiac_pairs),
        },
        "globally_two_page_exclusive_circular_family_groups": {
            "qualified_features": sum(circular_pair_counts.values()),
            "nonzero_page_pairs": len(circular_pair_counts),
            "page_pairs": all_circular_rows,
            "taurus_pair_count": taurus_circular_count,
            "taurus_tied_pairs": sum(value == taurus_circular_count for value in circular_pair_counts.values()),
        },
        "gates": {
            "frozen_candidate_inventory_reconstructed": frozen_ids == rebuilt_public_ids,
            "member_ngram_candidate_is_manuscript_common": next(item for item in candidate_support if "MEMBER_N3" in item["candidate_id"])["page_count"] > 50,
            "family_group_candidate_is_globally_two_page_exclusive": next(item for item in candidate_support if "FAMILY_GROUP" in item["candidate_id"])["page_count"] == 2,
            "public_matching_has_more_candidates_than_each_alternative": matching_diagnostics[0]["candidate_count"] > max(item["candidate_count"] for item in matching_diagnostics[1:]),
            "taurus_pair_is_unique_among_zodiac_pair_exclusive_groups": len(zodiac_exact_rows) == 1,
            "confirmatory_evidence_available": False,
            "zero_english_glosses": True,
        },
        "claim_ceiling": "Post-result specificity of source-native repeats only; no sign name, month, day, word, morpheme, sound, language, plaintext, or translation.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    match_counts = {item["matching"]: item["candidate_count"] for item in matching_diagnostics}
    family_support = next(item for item in candidate_support if "FAMILY_GROUP" in item["candidate_id"])
    member_support = next(item for item in candidate_support if "MEMBER_N3" in item["candidate_id"])
    other_zodiac = next(item for item in zodiac_exact_rows if set(item["pages"]) != set(TRUE[1]))
    REPORT.write_text(
        "# Duplicated-zodiac candidate specificity\n\n"
        "Status: **POSTHOC_CANDIDATE_NOT_PRIVILEGED_BY_PAIR_CONTROLS**\n\n"
        f"The frozen rule yields {match_counts['PUBLIC_ARIES_TAURUS']} candidates for the public pairing, versus "
        f"{match_counts['CROSS_1']} and {match_counts['CROSS_2']} for the two alternative half-page matchings. "
        "The public pairing therefore does not produce an exceptional number of rare candidates.\n\n"
        f"The member trigram candidate spans {member_support['page_count']} pages and {member_support['physical_locus_count']} physical loci, so it is not sign-specific manuscript-wide. "
        f"The whole-group family surface `AQJABABA` (nearest basic EVA `{family_support['nearest_basic_eva_sample'][0]}`) is stronger descriptively: it occurs only on f71v and f72r1, once per reading on each page, and every witness is circular text. "
        f"But the same globally two-page-exclusive pattern occurs for `{other_zodiac['features'][0]}` on {other_zodiac['pages'][0]} and {other_zodiac['pages'][1]}, and four circular page pairs manuscript-wide have one such family repeat.\n\n"
        "Retain `AQJABABA`/`okeodaly` only as a weak Taurus-scene circular-text lead. The controls do not privilege it as TAURUS, a sign name, a word, or a translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "matching_counts": match_counts, "zodiac_pair_repeats": len(zodiac_exact_rows)}, sort_keys=True))


if __name__ == "__main__":
    main()
