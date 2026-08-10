#!/usr/bin/env python3
"""Public-source and score-blind capacity audit for four repeated plants."""

from __future__ import annotations

import csv
import hashlib
import html
import itertools
import json
import math
import re
import urllib.request
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments" / "semantic_assumptions"
RESULTS = BASE / "results"
GROUPS = RESULTS / "source_sta_family_consensus_groups.tsv"
CROSSWALK = ROOT / "transcription" / "sources" / "Stolfi_loci_evmt16e6_ivtff.tbl"
OUT = RESULTS / "public_repeated_plant_source_native_capacity.json"
OUT_MD = RESULTS / "public_repeated_plant_source_native_capacity.md"
READINGS = {"ZL3b": "zl_sta_codes", "IT2a": "it_sta_codes", "RF1b": "rf_sta_codes"}
CATALOGUES = {
    "Q03": "https://www.voynich.nu/q03/index.html",
    "Q06": "https://www.voynich.nu/q06/index.html",
    "Q15": "https://www.voynich.nu/q15/index.html",
    "Q19": "https://www.voynich.nu/q19/index.html",
}
TRANSCRIPTIONS = {
    "f89v2": "https://www.voynich.nu/q15/f089v2_tr.txt",
    "f102r2": "https://www.voynich.nu/q19/f102r2_tr.txt",
    "f102v1": "https://www.voynich.nu/q19/f102v1_tr.txt",
}
RELATIONS = (
    {
        "target_page": "f48v", "pharma_page": "f89v2", "fragment": 54,
        "old_locus": "f89v2.L1.5", "label_locus": "f89v2.6",
        "catalogue": "Q15", "catalogue_phrase": "Fragment 54 appears to be the same plant as on f48v",
        "ownership_phrase": "This label lies partly under plant [1,4] and next to [1,5]",
        "ownership": "EXPLICIT_NEXT_TO_TARGET_WITH_NEIGHBOR_OVERLAP_AMBIGUITY",
    },
    {
        "target_page": "f18v", "pharma_page": "f102r2", "fragment": 212,
        "old_locus": "f102r2.L3.1", "label_locus": "f102r2.21",
        "catalogue": "Q19", "catalogue_phrase": "Fragment 212 appears to be the same plant as on f18v",
        "ownership_phrase": "above plant f102r2[3,1]",
        "ownership": "EXPLICIT_MANUAL_PLANT_POSITION",
    },
    {
        "target_page": "f23r", "pharma_page": "f102r2", "fragment": 213,
        "old_locus": "f102r2.L3.2", "label_locus": "f102r2.22",
        "catalogue": "Q19", "catalogue_phrase": "Fragment 213 appears to be the same plant as on f23r",
        "ownership_phrase": "above plant f102r2[3,2]",
        "ownership": "EXPLICIT_MANUAL_PLANT_POSITION",
    },
    {
        "target_page": "f19r", "pharma_page": "f102v1", "fragment": 240,
        "old_locus": "f102v1.L2.2", "label_locus": "f102v1.17",
        "catalogue": "Q19", "catalogue_phrase": "Fragment 240 appears to be the same plant as on f19r",
        "ownership_phrase": "plant [2,2] - squatting cone of mousetail roots",
        "ownership": "EXPLICIT_MANUAL_PLANT_POSITION",
    },
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "VManus-SNPL001/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def visible(data: bytes) -> str:
    value = data.decode("utf-8", "replace")
    value = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", value)
    value = re.sub(r"(?s)<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def compact_text(data: bytes) -> str:
    return re.sub(r"\s+", " ", data.decode("utf-8", "replace")).strip()


def read_crosswalk() -> dict[str, str]:
    mapping = {}
    pattern = re.compile(r"^<([^>]+)>\s+<([^>]+)>")
    for line in CROSSWALK.read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match:
            mapping[match.group(1)] = match.group(2)
    return mapping


def motifs(sequence: tuple[str, ...]) -> list[tuple[str, ...]]:
    values = set()
    for width in (4, 5):
        for start in range(max(0, len(sequence) - width + 1)):
            values.add(sequence[start:start + width])
    return sorted(values, key=lambda item: (len(item), item))


def contains(group: tuple[str, ...], motif: tuple[str, ...]) -> bool:
    width = len(motif)
    return any(group[start:start + width] == motif for start in range(len(group) - width + 1))


def report(result: dict) -> str:
    return (
        "# Public repeated-plant source-native capacity\n\n"
        "Decision: **GO_FREEZE_SOURCE_NATIVE_QUERY_BEFORE_TARGET**.\n\n"
        "Public catalogue pages independently recover all four repeated-drawing relations. "
        "Public manual transcription plus the old-to-current locus crosswalk bind all four "
        "label loci. Three ownership records name the plant position directly; f89v2.6 is "
        "explicitly next to the target plant but partly under its neighbor, so that ambiguity "
        "remains frozen.\n\n"
        f"The score-blind source-STA inventory retains {result['background']['A_hand1_pages']} "
        "A/hand-1 and "
        f"{result['background']['B_hand5_pages']} B/hand-5 non-target Herbal pages. Every "
        "label-reading has at least one non-universal contiguous four- or five-symbol motif "
        "in both strata. Four fixed relations provide 24 assignments and a minimum exact "
        "one-sided p-value of 1/24 = 0.041667.\n\n"
        "No target Herbal prose row or label-to-page score was opened. This authorizes only "
        "a separately frozen source-native query. It supplies no plant name, word meaning, "
        "sound, language, cipher, plaintext, or translation.\n"
    )


def main() -> None:
    catalogue_bytes = {key: fetch(url) for key, url in CATALOGUES.items()}
    transcription_bytes = {key: fetch(url) for key, url in TRANSCRIPTIONS.items()}
    catalogue_text = {key: visible(value) for key, value in catalogue_bytes.items()}
    transcription_text = {key: compact_text(value) for key, value in transcription_bytes.items()}
    crosswalk = read_crosswalk()

    for relation in RELATIONS:
        if relation["catalogue_phrase"] not in catalogue_text[relation["catalogue"]]:
            raise RuntimeError(("catalogue phrase", relation))
        if relation["ownership_phrase"] not in transcription_text[relation["pharma_page"]]:
            raise RuntimeError(("ownership phrase", relation))
        if crosswalk.get(relation["old_locus"]) != relation["label_locus"]:
            raise RuntimeError(("crosswalk", relation, crosswalk.get(relation["old_locus"])))

    target_pages = {relation["target_page"] for relation in RELATIONS}
    label_loci = {relation["label_locus"] for relation in RELATIONS}
    label_rows = {}
    background: dict[tuple[str, str], dict[str, dict[str, list[tuple[str, ...]]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    groups_data = GROUPS.read_bytes()
    with GROUPS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["locus"] in label_loci:
                if row["locus"] in label_rows:
                    raise RuntimeError(("duplicate label", row["locus"]))
                label_rows[row["locus"]] = row
                continue
            if row["page"] in target_pages:
                continue
            if not (
                row["section"] == "H"
                and row["grammar_scope"] == "CONFIRMED_PROSE"
                and row["strict_zero_alternative"] == "1"
            ):
                continue
            stratum = (row["currier"], row["hand"])
            for reading, column in READINGS.items():
                background[stratum][reading][row["page"]].append(tuple(row[column].split()))

    if set(label_rows) != label_loci:
        raise RuntimeError((set(label_rows), label_loci))
    relevant = {("A", "1"): "A_hand1", ("B", "5"): "B_hand5"}
    page_counts = {name: len(background[key]["ZL3b"]) for key, name in relevant.items()}
    if page_counts != {"A_hand1": 92, "B_hand5": 5}:
        raise RuntimeError(page_counts)

    inventory = {}
    nonuniversal = []
    for relation in RELATIONS:
        locus = relation["label_locus"]
        row = label_rows[locus]
        if not (
            row["kind"] == "L"
            and row["code"] == "@Lf"
            and row["grammar_scope"] == "DIAGNOSTIC_NONPROSE"
            and row["strict_zero_alternative"] == "1"
            and row["consensus_group_count"] == "1"
        ):
            raise RuntimeError(("label metadata", locus))
        readings = {}
        for reading, column in READINGS.items():
            sequence = tuple(row[column].split())
            motif_rows = []
            for motif in motifs(sequence):
                frequencies = {}
                for key, name in relevant.items():
                    pages = background[key][reading]
                    frequencies[name] = sum(
                        any(contains(group, motif) for group in page_groups)
                        for page_groups in pages.values()
                    )
                motif_rows.append({
                    "motif": " ".join(motif), "width": len(motif),
                    "page_document_frequency": frequencies,
                })
            for stratum_name, count in page_counts.items():
                passed = any(item["page_document_frequency"][stratum_name] < count for item in motif_rows)
                nonuniversal.append(passed)
            readings[reading] = {
                "sequence": " ".join(sequence), "symbol_count": len(sequence),
                "motifs": motif_rows,
            }
        inventory[locus] = {
            "family_surface": row["family_surface"], "readings": readings,
        }

    for reading in READINGS:
        sequences = [inventory[r["label_locus"]]["readings"][reading]["sequence"] for r in RELATIONS]
        if len(set(sequences)) != 4:
            raise RuntimeError(("label uniqueness", reading, sequences))

    assignments = math.factorial(len(RELATIONS))
    relation_records = [dict(item) for item in RELATIONS]
    for item in relation_records:
        item["catalogue_url"] = CATALOGUES[item.pop("catalogue")]
        item["transcription_url"] = TRANSCRIPTIONS[item["pharma_page"]]

    result = {
        "experiment": "SNPL001_PUBLIC_REPEATED_PLANT_SOURCE_NATIVE_CAPACITY",
        "status": "GO_FREEZE_SOURCE_NATIVE_QUERY_BEFORE_TARGET",
        "method": "PUBLIC_RELATIONS_PLUS_SCORE_BLIND_SOURCE_STA_MEMBER_MOTIF_CAPACITY",
        "public_catalogues": {
            key: {"url": CATALOGUES[key], "sha256": sha(value)}
            for key, value in catalogue_bytes.items()
        },
        "public_manual_transcriptions": {
            key: {"url": TRANSCRIPTIONS[key], "sha256": sha(value)}
            for key, value in transcription_bytes.items()
        },
        "inputs": {
            "consensus_groups": {"path": str(GROUPS.relative_to(ROOT)), "sha256": sha(groups_data)},
            "old_to_current_crosswalk": {"path": str(CROSSWALK.relative_to(ROOT)), "sha256": sha(CROSSWALK.read_bytes())},
        },
        "relations": relation_records,
        "background": {
            "target_pages_excluded": sorted(target_pages),
            "A_hand1_pages": page_counts["A_hand1"],
            "B_hand5_pages": page_counts["B_hand5"],
        },
        "label_inventory": inventory,
        "capacity": {
            "relations": len(RELATIONS), "fixed_assignments": assignments,
            "minimum_attainable_one_sided_p": 1 / assignments,
        },
        "gates": {
            "four_public_same_plant_relations_bound": True,
            "four_public_manual_label_mappings_bound": True,
            "f89_neighbor_overlap_ambiguity_preserved": True,
            "four_distinct_label_sequences_in_each_reading": True,
            "every_label_reading_has_nonuniversal_4_or_5_symbol_motif_in_both_strata": all(nonuniversal),
            "both_strata_have_at_least_5_background_pages": min(page_counts.values()) >= 5,
            "exact_assignment_can_attain_p_at_most_0_05": 1 / assignments <= 0.05,
            "target_herbal_prose_rows_accessed": False,
            "label_to_target_page_scores_computed": False,
            "ocr_or_automated_vision_used": False,
        },
        "decision": "GO_FREEZE_SOURCE_NATIVE_QUERY_BEFORE_TARGET",
        "claim_ceiling": (
            "Four public same-plant relations with publicly mapped pharmaceutical labels have "
            "enough source-native member-sequence rarity and a 24-assignment orbit to preregister "
            "one target-blind query. f89v2.6 retains explicit neighbor-overlap ownership ambiguity. "
            "No target page score, plant name, English word, sound, language, cipher, plaintext, or "
            "translation follows."
        ),
    }
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
    if not (
        all(result["gates"][name] for name in positive_gates)
        and not any(result["gates"][name] for name in exclusion_gates)
    ):
        raise RuntimeError(result["gates"])
    RESULTS.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUT_MD.write_text(report(result))


if __name__ == "__main__":
    main()
