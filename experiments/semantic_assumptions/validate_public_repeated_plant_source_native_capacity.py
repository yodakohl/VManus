#!/usr/bin/env python3
"""Independent reconstruction of SNPL001; imports no producer module."""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
import re
import urllib.request
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "experiments" / "semantic_assumptions" / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
CROSSWALK = ROOT / "transcription" / "sources" / "Stolfi_loci_evmt16e6_ivtff.tbl"
PROD = RESULTS / "public_repeated_plant_source_native_capacity.json"
PROD_MD = RESULTS / "public_repeated_plant_source_native_capacity.md"
OUT = RESULTS / "public_repeated_plant_source_native_capacity_validation.json"
OUT_MD = RESULTS / "public_repeated_plant_source_native_capacity_validation.md"
READINGS = {"ZL3b": "zl_sta_codes", "IT2a": "it_sta_codes", "RF1b": "rf_sta_codes"}
TARGETS = {"f48v", "f18v", "f23r", "f19r"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-SNPL001-validator/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def normalized(data: bytes, html_input: bool) -> str:
    value = data.decode("utf-8", "replace")
    if html_input:
        value = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
        value = re.sub(r"(?s)<[^>]+>", " ", value)
        value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def windows(seq: tuple[str, ...]) -> set[tuple[str, ...]]:
    return {
        seq[start:start + width]
        for width in (4, 5)
        for start in range(max(0, len(seq) - width + 1))
    }


def has(group: tuple[str, ...], motif: tuple[str, ...]) -> bool:
    return any(group[index:index + len(motif)] == motif for index in range(len(group) - len(motif) + 1))


def main() -> None:
    prod = json.loads(PROD.read_text())
    checks = 0

    def check(value: bool, label: str) -> None:
        nonlocal checks
        if not value:
            raise AssertionError(label)
        checks += 1

    check(prod["experiment"] == "SNPL001_PUBLIC_REPEATED_PLANT_SOURCE_NATIVE_CAPACITY", "experiment")
    check(prod["status"] == "GO_FREEZE_SOURCE_NATIVE_QUERY_BEFORE_TARGET", "status")
    check(prod["decision"] == prod["status"], "decision")
    check(prod["inputs"]["consensus_groups"]["sha256"] == sha(GROUPS.read_bytes()), "groups hash")
    check(prod["inputs"]["old_to_current_crosswalk"]["sha256"] == sha(CROSSWALK.read_bytes()), "crosswalk hash")

    live_catalogues = {}
    for key, record in prod["public_catalogues"].items():
        data = fetch(record["url"])
        check(sha(data) == record["sha256"], f"catalogue hash {key}")
        live_catalogues[record["url"]] = normalized(data, True)
    live_manuals = {}
    for key, record in prod["public_manual_transcriptions"].items():
        data = fetch(record["url"])
        check(sha(data) == record["sha256"], f"manual hash {key}")
        live_manuals[record["url"]] = normalized(data, False)

    crosswalk = {}
    pattern = re.compile(r"^<([^>]+)>\s+<([^>]+)>")
    for line in CROSSWALK.read_text().splitlines():
        match = pattern.match(line)
        if match:
            check(crosswalk.setdefault(match.group(1), match.group(2)) == match.group(2), "crosswalk unique")
    check(len(prod["relations"]) == 4, "four relations")
    check({row["target_page"] for row in prod["relations"]} == TARGETS, "targets")
    check(len({row["label_locus"] for row in prod["relations"]}) == 4, "labels")
    for relation in prod["relations"]:
        check(relation["catalogue_phrase"] in live_catalogues[relation["catalogue_url"]], "catalogue claim")
        check(relation["ownership_phrase"] in live_manuals[relation["transcription_url"]], "ownership claim")
        check(crosswalk[relation["old_locus"]] == relation["label_locus"], "locus mapping")
    f89 = next(row for row in prod["relations"] if row["label_locus"] == "f89v2.6")
    check("AMBIGUITY" in f89["ownership"], "f89 ambiguity retained")

    label_loci = {row["label_locus"] for row in prod["relations"]}
    labels = {}
    bg = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    with GROUPS.open(newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in label_loci:
                check(row["locus"] not in labels, "one consensus label row")
                labels[row["locus"]] = row
                continue
            if row["page"] in TARGETS:
                continue
            if row["section"] != "H" or row["grammar_scope"] != "CONFIRMED_PROSE" or row["strict_zero_alternative"] != "1":
                continue
            key = (row["currier"], row["hand"])
            for reading, column in READINGS.items():
                bg[key][reading][row["page"]].append(tuple(row[column].split()))
    check(set(labels) == label_loci, "all labels found")
    strata = {("A", "1"): "A_hand1", ("B", "5"): "B_hand5"}
    counts = {name: len(bg[key]["ZL3b"]) for key, name in strata.items()}
    check(counts == {"A_hand1": 92, "B_hand5": 5}, "background counts")
    check(prod["background"]["target_pages_excluded"] == sorted(TARGETS), "target exclusions")
    check(prod["background"]["A_hand1_pages"] == 92, "A count stored")
    check(prod["background"]["B_hand5_pages"] == 5, "B count stored")

    for locus, stored in prod["label_inventory"].items():
        row = labels[locus]
        check(stored["family_surface"] == row["family_surface"], "family surface")
        check(row["kind"] == "L" and row["code"] == "@Lf", "label metadata")
        for reading, column in READINGS.items():
            sequence = tuple(row[column].split())
            check(stored["readings"][reading]["sequence"] == " ".join(sequence), "sequence")
            reconstructed = []
            for motif in sorted(windows(sequence), key=lambda item: (len(item), item)):
                freq = {}
                for key, name in strata.items():
                    freq[name] = sum(
                        any(has(group, motif) for group in page_groups)
                        for page_groups in bg[key][reading].values()
                    )
                reconstructed.append({"motif": " ".join(motif), "width": len(motif), "page_document_frequency": freq})
            check(reconstructed == stored["readings"][reading]["motifs"], "motif reconstruction")
            for name, count in counts.items():
                check(any(item["page_document_frequency"][name] < count for item in reconstructed), "nonuniversal motif")

    for reading in READINGS:
        check(len({prod["label_inventory"][locus]["readings"][reading]["sequence"] for locus in label_loci}) == 4, "distinct sequences")
    check(prod["capacity"]["fixed_assignments"] == math.factorial(4), "assignment orbit")
    check(prod["capacity"]["minimum_attainable_one_sided_p"] == 1 / 24, "p floor")
    positive_gates = (
        "four_public_same_plant_relations_bound",
        "four_public_manual_label_mappings_bound",
        "f89_neighbor_overlap_ambiguity_preserved",
        "four_distinct_label_sequences_in_each_reading",
        "every_label_reading_has_nonuniversal_4_or_5_symbol_motif_in_both_strata",
        "both_strata_have_at_least_5_background_pages",
        "exact_assignment_can_attain_p_at_most_0_05",
    )
    exclusion_gates = (
        "target_herbal_prose_rows_accessed",
        "label_to_target_page_scores_computed",
        "ocr_or_automated_vision_used",
    )
    check(all(prod["gates"][name] for name in positive_gates), "positive gates")
    check(not any(prod["gates"][name] for name in exclusion_gates), "exclusion gates")
    check("No target Herbal prose row" in PROD_MD.read_text(), "report isolation")
    check("neighbor-overlap ownership ambiguity" in prod["claim_ceiling"], "claim ceiling ambiguity")

    validation = {
        "status": "PASS_INDEPENDENT_PUBLIC_SOURCE_AND_SCORE_BLIND_CAPACITY_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "production_sha256": sha(PROD.read_bytes()),
        "production_report_sha256": sha(PROD_MD.read_bytes()),
        "public_sources_refetched": True,
        "target_herbal_prose_rows_accessed": False,
        "label_to_target_page_scores_computed": False,
        "ocr_or_automated_vision_used": False,
        "decision": prod["decision"],
    }
    OUT.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(
        "# SNPL001 independent validation\n\n"
        f"PASS: **{checks}** checks independently refetch and bind the public catalogue and "
        "manual sources, reconstruct all four old-to-current label mappings, all source-STA "
        "member motifs and both background strata, the 24-assignment orbit, target isolation, "
        "and the ownership-ambiguity ceiling.\n\n"
        "This is a score-blind capacity result. It supplies no plant name, English word, "
        "sound, language, cipher, plaintext, or translation.\n"
    )


if __name__ == "__main__":
    main()
