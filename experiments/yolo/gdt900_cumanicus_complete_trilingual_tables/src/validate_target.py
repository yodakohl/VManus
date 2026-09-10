"""Independently enumerate every 18-group window in the admitted odd packet.

No primary builder import, source-cell input, fitting, mixed transcription or
inherited target-cache access. Frozen byte hashes precede target JSON parsing.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re

PACKET_SHA256 = "1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed"
TARGET_SHA256 = "dfb5f1981b609fadaf4c93c406ad86042d928f60296d8010a022fe303033df6a"
PARAGRAPHS = {"CONSENSUS": 1, "IT2a": 259, "RF1b": 11, "ZL3b": 14}
WINDOWS = {"CONSENSUS": 0, "IT2a": 6710, "RF1b": 73, "ZL3b": 142}
WINDOW_SIZE = 18


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def validate(target_packet, target_input):
    packet_blob = Path(target_packet).read_bytes()
    require(sha(packet_blob) == PACKET_SHA256, "frozen_odd_packet_hash")
    target_blob = Path(target_input).read_bytes()
    require(sha(target_blob) == TARGET_SHA256, "frozen_compact_target_hash")
    packet = json.loads(gzip.decompress(packet_blob))
    target = json.loads(target_blob)
    require(packet["schema"] == "GDT893_ODD_ONLY_FIT_PACKET_V1", "packet_schema")
    require(target["schema"] == "GDT900_COMPLETE_ODD_WINDOW_TARGET_V1", "target_schema")
    require(target["parent_packet_sha256"] == PACKET_SHA256, "parent_packet_binding")
    require(set(packet["panels"]) == set(PARAGRAPHS) == set(target["panels"]), "complete_panel_set")
    report = {}
    for panel in PARAGRAPHS:
        paragraphs = packet["panels"][panel]
        windows = target["panels"][panel]
        require(len(paragraphs) == PARAGRAPHS[panel], "inherited_paragraph_count:" + panel)
        expected, paragraph_ids, physical_leaves = [], set(), set()
        all_group_ids, eligible_paragraphs, parent_word_count = set(), 0, 0
        for paragraph in paragraphs:
            paragraph_id = paragraph["id"]
            require(paragraph_id not in paragraph_ids, "duplicate_parent_paragraph")
            paragraph_ids.add(paragraph_id)
            page, leaf = paragraph["page"], paragraph["physical_folio"]
            require(isinstance(page, str) and not page.startswith("f84"), "sealed_page")
            require(isinstance(leaf, str) and not leaf.startswith("f84"), "sealed_physical_leaf")
            match = re.fullmatch(r"f([0-9]+)[rv][0-9]*", page)
            require(match is not None, "page_schema")
            number = int(match.group(1))
            require(number % 2 == 1, "even_physical_leaf")
            require(leaf == "f" + str(number), "physical_leaf_binding")
            physical_leaves.add(leaf)
            words = paragraph["words"]
            source_ids = paragraph["source_group_ids"]
            require(isinstance(words, list) and isinstance(source_ids, list) and len(words) == len(source_ids) and bool(words), "word_id_alignment")
            require(all(isinstance(word, str) and re.fullmatch("[a-z]+", word) for word in words), "literal_eligible_raw_words")
            parent_word_count += len(words)
            previous = None
            for identifier in source_ids:
                require(identifier not in all_group_ids, "parent_group_overlap")
                all_group_ids.add(identifier)
                source_match = re.fullmatch(r"([^|]+)\|(f[0-9]+[rv][0-9]*)\.([0-9]+)\|G([0-9]+)", identifier)
                require(source_match is not None, "source_id_schema")
                edition, id_page, line, group = source_match.groups()
                require(edition == ("ZL3b" if panel == "CONSENSUS" else panel), "source_id_edition")
                require(id_page == page and not id_page.startswith("f84"), "source_id_page")
                position = (int(line), int(group))
                require(min(position) > 0 and (previous is None or previous < position), "source_id_order")
                if previous is not None and position[0] == previous[0]:
                    require(position[1] == previous[1] + 1, "internal_group_contiguity")
                previous = position
            if len(words) >= WINDOW_SIZE:
                eligible_paragraphs += 1
            # Iterate all possible END positions instead of the primary's start
            # windows; the entire range is fixed by the inherited paragraph.
            for end in range(WINDOW_SIZE, len(words) + 1):
                start = end - WINDOW_SIZE
                expected.append({
                    "id": paragraph_id + "@" + str(start),
                    "paragraph_id": paragraph_id, "page": page,
                    "physical_folio": leaf, "start": start,
                    "words": words[start:end],
                    "source_group_ids": source_ids[start:end],
                })
        formula_count = sum(max(0, len(p["words"]) - WINDOW_SIZE + 1) for p in paragraphs)
        require(len(expected) == formula_count == WINDOWS[panel], "complete_window_count:" + panel)
        require(windows == expected, "all_window_fields_and_order_exact:" + panel)
        require(len({row["id"] for row in windows}) == len(windows), "duplicate_window_id")
        require(all(len(row["words"]) == len(row["source_group_ids"]) == WINDOW_SIZE for row in windows), "whole_window_size")
        report[panel] = {
            "inherited_paragraphs": len(paragraphs),
            "paragraphs_with_at_least_18_groups": eligible_paragraphs,
            "inherited_raw_groups": parent_word_count,
            "physical_folios_in_inherited_panel": len(physical_leaves),
            "expected_windows": formula_count, "actual_windows": len(windows),
            "raw_group_occurrences_in_windows": WINDOW_SIZE * len(windows),
            "complete_exact_replay": True, "all_physical_leaves_odd": True,
            "sealed_prefixes_present": False,
        }
    return {
        "schema": "GDT900_INDEPENDENT_TARGET_VALIDATION_V1", "status": "PASS",
        "parent_packet_sha256": PACKET_SHA256, "target_input_sha256": TARGET_SHA256,
        "target_input_bytes": len(target_blob),
        "validator_sha256": sha(Path(__file__).read_bytes()),
        "inherited_target_cache_sha256": packet["input_lock"]["target_cache_sha256"],
        "panels": report, "total_windows": sum(WINDOWS.values()),
        "checks": [
            "Frozen parent and final compact target hashes verified before parsing",
            "Every inherited paragraph accounted for, including those shorter than 18 groups",
            "All windows independently regenerated using every eligible paragraph end position",
            "All raw words, source-group IDs, paragraph IDs, offsets, page selectors and physical folios agree exactly",
            "Complete list order and window IDs agree; no omitted or extra windows",
            "Every window has 18 consecutive inherited groups and stays inside one paragraph",
            "All source IDs match their panel edition and page, with strictly increasing native coordinates",
            "Only odd physical leaves; f84 and f84r prefixes excluded",
        ],
        "scope": "Projection/provenance audit only, without fitting. Candidate windows may overlap; selecting two nonoverlapping windows is a separate model constraint. Physical positions are inherited source-group pointers, not new native table certification. Alternate readings remain panels of one manuscript. No raw mixed transcription, even target, source forms or fitted results were opened.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-packet", required=True)
    parser.add_argument("--target-input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = validate(args.target_packet, args.target_input)
    output = Path(args.output)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n")
    temporary.replace(output)
    print(json.dumps({"status": result["status"], "window_counts": {panel: row["actual_windows"] for panel, row in result["panels"].items()}, "target_input_sha256": TARGET_SHA256}))


if __name__ == "__main__":
    main()
