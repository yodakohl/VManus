"""Independently replay the GDT899 projection of the frozen odd-only packet.

No mixed transcription, inherited cache, source corpus or fitted model is opened.
Only the three explicit input files are read, after their applicable hash gates.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re

PACKET_SHA256 = "1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed"
LOCK_SHA256 = "4de92f3728b46c9ecb67f98da34dfea85a36fcd83af8df1226978c9814520979"
COUNTS = {"ZL3b": 14, "IT2a": 259, "RF1b": 11, "CONSENSUS": 1}
FIELDS = {"id", "page", "physical_folio", "words", "source_group_ids"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def validate(packet_path, lock_path, target_path):
    # Fixed hashes are checked before any JSON target payload is materialized.
    packet_bytes = Path(packet_path).read_bytes()
    lock_bytes = Path(lock_path).read_bytes()
    require(sha(packet_bytes) == PACKET_SHA256, "frozen_packet_hash")
    require(sha(lock_bytes) == LOCK_SHA256, "frozen_input_lock_hash")
    lock = json.loads(lock_bytes)
    packet = json.loads(gzip.decompress(packet_bytes))
    require(packet["schema"] == "GDT893_ODD_ONLY_FIT_PACKET_V1", "packet_schema")
    require(packet["input_lock"] == lock, "packet_input_lock")
    require(set(packet["panels"]) == set(COUNTS), "packet_panel_set")
    target_bytes = Path(target_path).read_bytes()
    target = json.loads(target_bytes)
    require(target["schema"] == "GDT899_TARGET_INPUT_V1", "target_schema")
    require(target["inherited_packet_sha256"] == PACKET_SHA256, "target_packet_binding")
    require(target["inherited_input_lock"] == lock, "target_lock_binding")
    require(set(target["panels"]) == set(COUNTS), "target_panel_set")
    require(target["source_coverage_required"] == 24, "complete_register_coverage")
    summaries = {}
    for panel, expected_count in COUNTS.items():
        inherited = packet["panels"][panel]
        projected = target["panels"][panel]
        require(len(inherited) == len(projected) == expected_count, "panel_count:" + panel)
        paragraph_ids, group_ids, leaves, pages = set(), set(), set(), set()
        word_count = 0
        for old, new in zip(inherited, projected):
            require(set(old) == FIELDS, "inherited_row_schema:" + panel)
            require(set(new) == FIELDS | {"text"}, "projected_row_schema:" + panel)
            require(all(new[key] == old[key] for key in FIELDS), "row_exact_parity:" + panel)
            require(old["id"] not in paragraph_ids, "duplicate_paragraph:" + panel)
            paragraph_ids.add(old["id"])
            page = old["page"]
            physical = old["physical_folio"]
            require(isinstance(page, str) and not page.startswith("f84"), "sealed_page")
            require(isinstance(physical, str) and not physical.startswith("f84"), "sealed_physical_folio")
            match = re.fullmatch(r"f([0-9]+)[rv][0-9]*", page)
            require(match is not None, "page_schema:" + panel)
            leaf_number = int(match.group(1))
            require(leaf_number % 2 == 1, "even_leaf")
            require(physical == "f" + str(leaf_number), "physical_leaf_binding")
            leaves.add(physical)
            pages.add(page)
            words, identifiers = old["words"], old["source_group_ids"]
            require(isinstance(words, list) and bool(words), "empty_or_invalid_words")
            require(isinstance(identifiers, list) and len(words) == len(identifiers), "word_id_alignment")
            require(all(isinstance(word, str) and re.fullmatch(r"[a-z]+", word) for word in words), "literal_eligible_words")
            require(new["text"] == " ".join(words), "single_space_full_join")
            require(new["text"].split(" ") == words, "join_roundtrip")
            previous = None
            expected_edition = "ZL3b" if panel == "CONSENSUS" else panel
            for identifier in identifiers:
                require(isinstance(identifier, str), "source_id_type")
                id_match = re.fullmatch(r"([^|]+)\|(f[0-9]+[rv][0-9]*)\.([0-9]+)\|G([0-9]+)", identifier)
                require(id_match is not None, "source_id_schema")
                edition, id_page, line, group = id_match.groups()
                require(edition == expected_edition and id_page == page, "source_id_edition_page")
                require(not id_page.startswith("f84"), "sealed_source_id")
                position = (int(line), int(group))
                require(position[0] > 0 and position[1] > 0, "source_id_positive_position")
                require(previous is None or previous < position, "source_id_native_order")
                if previous is not None and previous[0] == position[0]:
                    require(position[1] == previous[1] + 1, "internal_group_contiguity")
                previous = position
                require(identifier not in group_ids, "overlapping_source_group:" + panel)
                group_ids.add(identifier)
            word_count += len(words)
        expected_capacity = "SUFFICIENT_COUNT_FOR_FIT" if expected_count >= 24 else "INSUFFICIENT_PARAGRAPH_COUNT"
        require(target["capacity"][panel] == expected_capacity, "capacity_label:" + panel)
        summaries[panel] = {
            "paragraphs": expected_count,
            "raw_groups": word_count,
            "distinct_source_group_ids": len(group_ids),
            "physical_folios": len(leaves),
            "page_selectors": len(pages),
            "all_rows_exact": True,
            "all_texts_exact_single_space_join": True,
            "all_source_ids_bound_and_ordered": True,
            "all_physical_leaves_odd": True,
            "sealed_prefixes_present": False,
        }
    return {
        "schema": "GDT899_INDEPENDENT_TARGET_VALIDATION_V1",
        "status": "PASS",
        "fit_packet_sha256": PACKET_SHA256,
        "inherited_input_lock_sha256": LOCK_SHA256,
        "target_input_sha256": sha(target_bytes),
        "validator_sha256": sha(Path(__file__).read_bytes()),
        "panels": summaries,
        "checks": [
            "Fixed frozen packet and lock byte hashes verified before target JSON parsing",
            "Both embedded input locks equal the independently read inherited lock",
            "All inherited paragraphs retained in exact panel order with no additions",
            "Every raw word, group ID, paragraph ID, page and physical folio unchanged",
            "Text is the exact reversible single-space join of complete raw groups",
            "Every source ID has matching edition/page and increasing line/group coordinates",
            "No duplicate paragraph IDs or overlapping group IDs within a panel",
            "Only odd physical leaves; f84 and f84r prefixes excluded throughout",
            "Capacity labels reproduce the mandatory 24-source-block count rule",
        ],
        "scope": "Independent projection replay of the already admitted odd-only GDT893 packet; inherited transcription eligibility is not re-adjudicated. Consensus retains the packet's ZL3b source-group pointers. No raw mixed source, even target, source corpus or fitted result read.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target-packet", required=True)
    parser.add_argument("--input-lock", required=True)
    parser.add_argument("--target-input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = validate(args.target_packet, args.input_lock, args.target_input)
    output = Path(args.output)
    temp = output.with_name(output.name + ".tmp")
    temp.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    temp.replace(output)
    print(json.dumps({"status": result["status"], "paragraph_counts": {p: r["paragraphs"] for p, r in result["panels"].items()}, "target_input_sha256": result["target_input_sha256"]}))


if __name__ == "__main__":
    main()
