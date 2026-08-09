#!/usr/bin/env python3
"""Clean-room validation of the duplicated-zodiac overlap and specificity audits."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

B = Path(__file__).resolve().parent
R = B / "results"
ALIGN = R / "source_sta_group_alignment.tsv"
META = R / "source_separator_transcription.tsv"
PAGES = R / "public_voynich_nu_page_annotations_v2.tsv"
METHOD1 = B / "ZODIAC_DUPLICATE_SOURCE_NATIVE_OVERLAP_METHOD.md"
PRODUCER1 = B / "audit_zodiac_duplicate_source_native_overlap.py"
RESULT1 = R / "zodiac_duplicate_source_native_overlap.json"
TSV1 = R / "zodiac_duplicate_source_native_overlap_candidates.tsv"
REPORT1 = R / "zodiac_duplicate_source_native_overlap_report.md"
METHOD2 = B / "ZODIAC_DUPLICATE_CANDIDATE_SPECIFICITY_METHOD.md"
PRODUCER2 = B / "audit_zodiac_duplicate_candidate_specificity.py"
RESULT2 = R / "zodiac_duplicate_candidate_specificity.json"
REPORT2 = R / "zodiac_duplicate_candidate_specificity_report.md"
OUT = R / "zodiac_duplicate_source_native_overlap_validation.json"
REPORT = R / "zodiac_duplicate_source_native_overlap_validation_report.md"
EDITIONS = ("ZL3b", "IT2a", "RF1b")
TRUE = (("f70v1", "f71r"), ("f71v", "f72r1"))
MATCHINGS = (
    ("PUBLIC_ARIES_TAURUS", TRUE),
    ("CROSS_1", (("f70v1", "f71v"), ("f71r", "f72r1"))),
    ("CROSS_2", (("f70v1", "f72r1"), ("f71r", "f71v"))),
)
VIEWS = tuple([f"FAMILY_N{n}" for n in range(2, 6)] + [f"MEMBER_N{n}" for n in range(1, 4)] + ["FAMILY_GROUP"])
SIGN_RE = re.compile(r"\bemblem of (Pisces|Aries|Taurus|Gemini|Cancer|Leo|Virgo|Libra|Scorpius|Sagittarius)\b", re.I)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def natural_page(page: str) -> tuple[int, str]:
    match = re.match(r"f(\d+)", page)
    return (int(match.group(1)), page) if match else (10_000, page)


def json_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def extract(row: dict[str, str]) -> dict[str, list[str]]:
    f = list(row["primary_sta_families"])
    m = row["primary_sta_codes"].split()
    result = {}
    for size in range(2, 6):
        result[f"FAMILY_N{size}"] = ["".join(f[start:start+size]) for start in range(len(f)-size+1)]
    for size in range(1, 4):
        result[f"MEMBER_N{size}"] = ["-".join(m[start:start+size]) for start in range(len(m)-size+1)]
    result["FAMILY_GROUP"] = [row["primary_sta_families"]]
    return result


def jaccard(a: Counter[str], b: Counter[str]) -> float:
    inventory = sorted(set(a).union(b))
    denominator = sum(max(a[item], b[item]) for item in inventory)
    return sum(min(a[item], b[item]) for item in inventory) / denominator if denominator else 0.0


def exact_candidates(counters: dict[tuple[str, str, str], Counter[str]], signs: dict[str, str], matching: tuple[tuple[str, str], tuple[str, str]]) -> list[dict[str, object]]:
    output = []
    for pair_index, pair in enumerate(matching):
        for view in VIEWS:
            common = set(counters[(pair[0], EDITIONS[0], view)])
            for page in pair:
                for edition in EDITIONS:
                    common.intersection_update(counters[(page, edition, view)])
            for value in sorted(common):
                if any(counters[(page, edition, view)][value] for page in signs if page not in pair for edition in EDITIONS):
                    continue
                output.append({"pair_index": pair_index, "pages": list(pair), "view": view, "feature": value})
    return output


def main() -> None:
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    page_rows = rows(PAGES)
    signs = {}
    for row in page_rows:
        match = SIGN_RE.search(row["illustrations"])
        if match:
            signs[row["page"]] = match.group(1).upper()
    check(len(signs) == 12, "exact_12_public_zodiac_pages")
    check({page for page, sign in signs.items() if sign == "ARIES"} == set(TRUE[0]), "public_aries_pair")
    check({page for page, sign in signs.items() if sign == "TAURUS"} == set(TRUE[1]), "public_taurus_pair")
    check(all(row["tentative_identifications_are_role_evidence"] == "0" for row in page_rows), "tentative_ids_excluded")

    meta_rows = rows(META)
    metadata = {row["source_group_id"]: row for row in meta_rows}
    check(len(metadata) == len(meta_rows), "metadata_group_ids_unique")
    align_rows = rows(ALIGN)
    check(len({row["source_group_id"] for row in align_rows}) == len(align_rows), "alignment_group_ids_unique")

    counters: dict[tuple[str, str, str], Counter[str]] = defaultdict(Counter)
    witness: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    occurrence: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    family_page_editions: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    family_page_roles: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    source_groups = 0
    excluded = 0
    for row in align_rows:
        info = metadata.get(row["source_group_id"])
        check(info is not None, f"metadata_present:{row['source_group_id']}")
        page, edition = info["page"], row["edition"]
        if page in signs:
            source_groups += 1
        if int(row["alternative_site_count"]):
            if page in signs:
                excluded += 1
            continue
        got = extract(row)
        for view, values in got.items():
            counters[(page, edition, view)].update(values)
            for value in set(values):
                witness[(page, edition, view, value)].append({
                    "source_group_id": row["source_group_id"], "locus": row["locus"],
                    "kind": info["kind"], "code": info["code"],
                    "family_surface": row["primary_sta_families"], "member_codes": row["primary_sta_codes"],
                })
            for value, multiplicity in Counter(values).items():
                occurrence[(view, value)].append({
                    "edition": edition, "page": page, "locus": row["locus"],
                    "source_group_id": row["source_group_id"], "role": info["kind"],
                    "multiplicity": multiplicity, "family_surface": row["primary_sta_families"],
                    "member_codes": row["primary_sta_codes"], "nearest_basic_eva": row["nearest_basic_eva_primary"],
                })
        family = row["primary_sta_families"]
        family_page_editions[family][page].add(edition)
        family_page_roles[(family, page, edition)].add(info["kind"])
    check(source_groups == 3914 and excluded == 41, "zodiac_group_counts")

    matching_rows = []
    for edition in EDITIONS:
        for view in VIEWS:
            scored = []
            for name, matching in MATCHINGS:
                pair_scores = [jaccard(counters[(a, edition, view)], counters[(b, edition, view)]) for a, b in matching]
                scored.append({"matching": name, "sum_score": sum(pair_scores), "pair_scores": pair_scores})
            observed = scored[0]["sum_score"]
            matching_rows.append({
                "edition": edition, "view": view, "matchings": scored,
                "public_inclusive_rank": 1 + sum(item["sum_score"] > observed for item in scored[1:]),
                "public_strict_rank": 1 + sum(item["sum_score"] >= observed for item in scored[1:]),
                "public_tied_top": sum(item["sum_score"] == observed for item in scored),
            })
    check(all(row["public_inclusive_rank"] == row["public_strict_rank"] == 1 for row in matching_rows), "public_matching_24_of_24_unique_top")

    candidates = []
    for sign, pair in (("ARIES", TRUE[0]), ("TAURUS", TRUE[1])):
        for item in exact_candidates(counters, signs, (pair, pair)):
            if item["pair_index"] != 0:
                continue
            view, value = str(item["view"]), str(item["feature"])
            counts = {f"{page}|{edition}": counters[(page, edition, view)][value] for page in pair for edition in EDITIONS}
            roles, witnesses = {}, {}
            for page in pair:
                for edition in EDITIONS:
                    key = f"{page}|{edition}"
                    selected = witness[(page, edition, view, value)]
                    roles[key] = sorted({row["kind"] for row in selected})
                    witnesses[key] = [row["source_group_id"] for row in selected]
            candidates.append({
                "candidate_id": f"{sign}|{view}|{value}", "sign": sign, "view": view,
                "feature": value, "pair_pages": list(pair), "counts": counts,
                "roles": roles, "witnesses": witnesses,
            })
    # exact_candidates duplicated each pair argument; keep the first instance only.
    dedup = {item["candidate_id"]: item for item in candidates}
    candidates = [dedup[key] for key in sorted(dedup, key=lambda key: (0 if "ARIES" in key else 1, list(VIEWS).index(key.split("|")[1]), key))]
    check(len(candidates) == 2, "exact_two_public_pair_candidates")

    fields = ["candidate_id", "sign", "view", "feature", "pair_pages", "minimum_pair_reading_count", "role_profiles", "witness_group_ids"]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    for item in candidates:
        writer.writerow({
            "candidate_id": item["candidate_id"], "sign": item["sign"], "view": item["view"], "feature": item["feature"],
            "pair_pages": ";".join(item["pair_pages"]), "minimum_pair_reading_count": min(item["counts"].values()),
            "role_profiles": json.dumps(item["roles"], sort_keys=True, separators=(",", ":")),
            "witness_group_ids": json.dumps(item["witnesses"], sort_keys=True, separators=(",", ":")),
        })
    expected_tsv = stream.getvalue()
    check(TSV1.read_text() == expected_tsv, "candidate_tsv_exact_bytes")

    primary = {
        "experiment": "ZODIAC_DUPLICATE_SOURCE_NATIVE_OVERLAP",
        "status": "PROVISIONAL_SIGN_SPECIFIC_SOURCE_NATIVE_CANDIDATES",
        "decision": "DESCRIPTIVE_ONLY_MINIMUM_LAYOUT_P_ONE_THIRD",
        "inputs": {path.name: digest(path) for path in (ALIGN, META, PAGES, METHOD1, PRODUCER1)},
        "public_identity_source": "illustration descriptions only; tentative identities ignored",
        "zodiac_signs": {page: signs[page] for page in sorted(signs, key=natural_page)},
        "fixed_true_matching": [[a, b] for a, b in TRUE],
        "counts": {
            "zodiac_pages": 12, "half_sign_pages": 4, "layout_preserving_matchings": 3,
            "minimum_attainable_one_sided_p": 1 / 3, "source_groups": source_groups,
            "excluded_alternative_groups": excluded, "matching_views": 24,
            "public_matching_top_views": 24, "public_matching_unique_top_views": 24,
            "sign_specific_candidates": 2,
        },
        "matching_results": matching_rows,
        "candidates": candidates,
        "candidate_tsv_sha256": hashlib.sha256(expected_tsv.encode()).hexdigest(),
        "gates": {
            "exact_12_public_zodiac_pages": True, "exact_two_aries_and_two_taurus_pages": True,
            "all_three_readings_scored_separately": True, "exact_three_layout_preserving_matchings": True,
            "confirmatory_power_insufficient": True, "tentative_identities_excluded": True,
            "no_label_proximity_or_day_order": True, "zero_english_glosses": True,
        },
        "claim_ceiling": "Descriptive all-reading source-native overlap across two duplicated public-icon sign identities; no candidate is a sign name, month, day, word, lexeme, plaintext, or translation.",
    }
    check(json.loads(RESULT1.read_text()) == primary, "primary_json_complete_reconstruction")
    primary_report = (
        "# Duplicated-zodiac source-native overlap\n\n"
        "Status: **PROVISIONAL_SIGN_SPECIFIC_SOURCE_NATIVE_CANDIDATES**\n\n"
        "The public Aries/Taurus matching ranks top in **24/24** reading-by-view comparisons and uniquely top in **24/24**. Only three layout-preserving matchings exist, so this is not a confirmatory test (minimum p = 1/3).\n\n"
        "The frozen exact absence rule retains **2** all-reading sign-specific candidates: Aries **0**, Taurus **2**. Candidates, if any, are neutral source-native subword leads only. They are not sign names, months, days, words, meanings, or translation.\n"
    )
    check(REPORT1.read_text() == primary_report, "primary_report_exact_bytes")

    matching_diagnostics = []
    for name, matching in MATCHINGS:
        got = exact_candidates(counters, signs, matching)
        by_view = Counter(item["view"] for item in got)
        matching_diagnostics.append({
            "matching": name, "pairs": [list(pair) for pair in matching], "candidate_count": len(got),
            "counts_by_view": {view: by_view[view] for view in VIEWS}, "candidates": got,
        })
    check([item["candidate_count"] for item in matching_diagnostics] == [2, 4, 6], "matching_candidate_counts_2_4_6")

    support = []
    for candidate in primary["candidates"]:
        selected = occurrence[(candidate["view"], candidate["feature"])]
        by_edition = Counter()
        pages_seen, loci_seen, roles_seen, evas = set(), set(), set(), set()
        for row in selected:
            by_edition[str(row["edition"])] += int(row["multiplicity"])
            pages_seen.add(str(row["page"])); loci_seen.add(str(row["locus"])); roles_seen.add(str(row["role"])); evas.add(str(row["nearest_basic_eva"]))
        page_values = sorted(pages_seen, key=natural_page)
        locus_values = sorted(loci_seen, key=lambda value: (natural_page(value.split(".")[0]), value))
        eva_values = sorted(evas)
        ordered_rows = sorted(selected, key=lambda row: (str(row["edition"]), natural_page(str(row["page"])), str(row["source_group_id"])))
        support.append({
            "candidate_id": candidate["candidate_id"],
            "occurrences_by_edition": {edition: by_edition[edition] for edition in EDITIONS},
            "page_count": len(page_values), "pages_sha256": json_digest(page_values), "page_sample": page_values[:12],
            "physical_locus_count": len(locus_values), "physical_loci_sha256": json_digest(locus_values), "physical_locus_sample": locus_values[:12],
            "source_group_count": len(selected), "roles": sorted(roles_seen),
            "nearest_basic_eva_count": len(eva_values), "nearest_basic_eva_sha256": json_digest(eva_values), "nearest_basic_eva_sample": eva_values[:12],
            "witnesses_sha256": json_digest(ordered_rows),
            "candidate_pair_witnesses": [row for row in ordered_rows if row["page"] in candidate["pair_pages"]],
        })

    pair_counts: Counter[tuple[str, str]] = Counter()
    pair_features: dict[tuple[str, str], list[str]] = defaultdict(list)
    circular_counts: Counter[tuple[str, str]] = Counter()
    circular_features: dict[tuple[str, str], list[str]] = defaultdict(list)
    for family, by_page in family_page_editions.items():
        pages_any = set(by_page)
        if len(pages_any) != 2 or any(by_page[page] != set(EDITIONS) for page in pages_any):
            continue
        pair = tuple(sorted(pages_any)); pair_counts[pair] += 1; pair_features[pair].append(family)
        if all("C" in family_page_roles[(family, page, edition)] for page in pair for edition in EDITIONS):
            circular_counts[pair] += 1; circular_features[pair].append(family)
    zodiac_pages = sorted(signs, key=natural_page)
    zodiac_pairs = [tuple(sorted((left, right))) for i, left in enumerate(zodiac_pages) for right in zodiac_pages[i+1:]]
    taurus = tuple(sorted(TRUE[1])); taurus_count = pair_counts[taurus]; taurus_circular = circular_counts[taurus]
    zodiac_rows = [{"pages": list(pair), "count": pair_counts[pair], "features": sorted(pair_features[pair])} for pair in zodiac_pairs if pair_counts[pair]]
    circular_rows = [{"pages": list(pair), "count": circular_counts[pair], "features": sorted(circular_features[pair])} for pair in sorted(circular_counts) if circular_counts[pair]]
    check(sum(pair_counts.values()) == 286 and len(pair_counts) == 278, "global_pair_exclusive_286_on_278")
    check(sum(circular_counts.values()) == len(circular_counts) == 4, "four_circular_pair_exclusive_repeats")

    member_support = next(item for item in support if "MEMBER_N3" in item["candidate_id"])
    family_support = next(item for item in support if "FAMILY_GROUP" in item["candidate_id"])
    specificity = {
        "experiment": "ZODIAC_DUPLICATE_CANDIDATE_SPECIFICITY",
        "status": "POSTHOC_CANDIDATE_NOT_PRIVILEGED_BY_PAIR_CONTROLS",
        "decision": "RETAIN_WEAK_TAURUS_SCENE_CIRCULAR_REPEAT_NO_LEXICAL_GLOSS",
        "inputs": {path.name: digest(path) for path in (ALIGN, META, PAGES, RESULT1, METHOD2, PRODUCER2)},
        "public_identity_source": "illustration descriptions only; tentative identities ignored",
        "matching_diagnostics": matching_diagnostics, "candidate_support": support,
        "globally_two_page_exclusive_family_groups": {
            "qualified_features": sum(pair_counts.values()), "nonzero_page_pairs": len(pair_counts),
            "maximum_features_on_one_pair": max(pair_counts.values()),
            "count_histogram": {str(key): value for key, value in sorted(Counter(pair_counts.values()).items())},
            "zodiac_nonzero_pairs": zodiac_rows, "zodiac_nonzero_pair_count": len(zodiac_rows),
            "taurus_pair_count": taurus_count,
            "taurus_inclusive_rank_among_66_zodiac_pairs": 1 + sum(pair_counts[pair] > taurus_count for pair in zodiac_pairs),
            "taurus_tied_pairs_among_66_zodiac_pairs": sum(pair_counts[pair] == taurus_count for pair in zodiac_pairs),
        },
        "globally_two_page_exclusive_circular_family_groups": {
            "qualified_features": sum(circular_counts.values()), "nonzero_page_pairs": len(circular_counts),
            "page_pairs": circular_rows, "taurus_pair_count": taurus_circular,
            "taurus_tied_pairs": sum(value == taurus_circular for value in circular_counts.values()),
        },
        "gates": {
            "frozen_candidate_inventory_reconstructed": True,
            "member_ngram_candidate_is_manuscript_common": member_support["page_count"] > 50,
            "family_group_candidate_is_globally_two_page_exclusive": family_support["page_count"] == 2,
            "public_matching_has_more_candidates_than_each_alternative": False,
            "taurus_pair_is_unique_among_zodiac_pair_exclusive_groups": False,
            "confirmatory_evidence_available": False, "zero_english_glosses": True,
        },
        "claim_ceiling": "Post-result specificity of source-native repeats only; no sign name, month, day, word, morpheme, sound, language, plaintext, or translation.",
    }
    check(json.loads(RESULT2.read_text()) == specificity, "specificity_json_complete_reconstruction")
    other = next(item for item in zodiac_rows if set(item["pages"]) != set(TRUE[1]))
    specificity_report = (
        "# Duplicated-zodiac candidate specificity\n\n"
        "Status: **POSTHOC_CANDIDATE_NOT_PRIVILEGED_BY_PAIR_CONTROLS**\n\n"
        "The frozen rule yields 2 candidates for the public pairing, versus 4 and 6 for the two alternative half-page matchings. The public pairing therefore does not produce an exceptional number of rare candidates.\n\n"
        f"The member trigram candidate spans {member_support['page_count']} pages and {member_support['physical_locus_count']} physical loci, so it is not sign-specific manuscript-wide. "
        f"The whole-group family surface `AQJABABA` (nearest basic EVA `{family_support['nearest_basic_eva_sample'][0]}`) is stronger descriptively: it occurs only on f71v and f72r1, once per reading on each page, and every witness is circular text. "
        f"But the same globally two-page-exclusive pattern occurs for `{other['features'][0]}` on {other['pages'][0]} and {other['pages'][1]}, and four circular page pairs manuscript-wide have one such family repeat.\n\n"
        "Retain `AQJABABA`/`okeodaly` only as a weak Taurus-scene circular-text lead. The controls do not privilege it as TAURUS, a sign name, a word, or a translation.\n"
    )
    check(REPORT2.read_text() == specificity_report, "specificity_report_exact_bytes")

    # Mutations demonstrate that the absence and all-reading gates are live.
    mutated = defaultdict(Counter, {key: Counter(value) for key, value in counters.items()})
    mutated[("f73r", "IT2a", "FAMILY_GROUP")]["AQJABABA"] = 1
    check(not any(item["feature"] == "AQJABABA" for item in exact_candidates(mutated, signs, TRUE)), "third_zodiac_page_mutation_rejects_candidate")
    mutated2 = defaultdict(Counter, {key: Counter(value) for key, value in counters.items()})
    mutated2[("f72r1", "RF1b", "FAMILY_GROUP")].pop("AQJABABA", None)
    check(not any(item["feature"] == "AQJABABA" for item in exact_candidates(mutated2, signs, TRUE)), "missing_reading_mutation_rejects_candidate")

    validation = {
        "experiment": "ZODIAC_DUPLICATE_SOURCE_NATIVE_OVERLAP_VALIDATION",
        "status": "PASS",
        "checks": len(checks), "failures": 0,
        "reconstructed": {
            "zodiac_pages": 12, "matching_views": 24, "primary_candidates": 2,
            "matching_candidate_counts": [2, 4, 6], "global_pair_exclusive_features": 286,
            "circular_pair_exclusive_features": 4,
        },
        "bindings": {path.name: digest(path) for path in (ALIGN, META, PAGES, METHOD1, PRODUCER1, RESULT1, TSV1, REPORT1, METHOD2, PRODUCER2, RESULT2, REPORT2)},
        "claim_ceiling": specificity["claim_ceiling"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# Duplicated-zodiac overlap validation\n\n"
        f"Status: **PASS** ({len(checks)} checks, zero failures).\n\n"
        "A production-free reconstruction verifies the complete primary and post-result JSON objects, exact candidate TSV and both reports. It reconstructs 24 matching views, the 2/4/6 candidate counts, both frozen candidates, 286 globally two-page-exclusive family surfaces on 278 page pairs, and four circular-role pair repeats. Two input mutations confirm that a third zodiac page or one missing reading rejects `AQJABABA`.\n\n"
        "This validates the descriptive limitation only. It supplies no sign name, word, meaning, plaintext, or translation.\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": "PASS", "checks": len(checks)}, sort_keys=True))


if __name__ == "__main__":
    main()
