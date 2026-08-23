#!/usr/bin/env python3
"""Validate the extended creative workshop component grammar."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FIRST = ROOT / "experiments/yolo/sidequest_semantic_portable_component_grammar"
UNIQUE = ROOT / "experiments/yolo/sidequest_semantic_unique_master_glosses"
BUILDER = OUT / "build_second_ring_grammar.py"

CONTENT_NAMES = [
    "SECOND_RING_14_ATOMS.tsv",
    "SECOND_RING_79_CARD_COMPOSITIONS.tsv",
    "REMAINING_19_LEARNED_WHOLE_CARDS.tsv",
    "COMPLETE_173_EXTENDED_CARD_DICTIONARY.tsv",
    "PROSE_381_EXTENDED_COMPONENT_READER.tsv",
    "TEN_PAGE_776_EXTENDED_COMPONENT_READER.tsv",
    "FOUR_SECOND_RING_PASSAGES.md",
    "SECOND_RING_GRAMMAR_REPORT.md",
    "SECOND_RING_POCKET_CARD.md",
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: object) -> None:
        checks.append({"name": name, "pass": bool(condition), "detail": detail})

    first_components = read_tsv(FIRST / "PORTABLE_17_ATOMS_AND_4_WHOLE_CARDS.tsv")
    first_seeds = read_tsv(FIRST / "SEED_29_MASTER_CARD_COMPOSITIONS.tsv")
    first_predictions = read_tsv(FIRST / "PREDICTED_ADDITIONAL_PROSE_CARDS.tsv")
    first_reader = read_tsv(FIRST / "TEN_PAGE_776_PORTABLE_COMPONENT_READER.tsv")
    atoms = read_tsv(OUT / "SECOND_RING_14_ATOMS.tsv")
    second = read_tsv(OUT / "SECOND_RING_79_CARD_COMPOSITIONS.tsv")
    remaining = read_tsv(OUT / "REMAINING_19_LEARNED_WHOLE_CARDS.tsv")
    complete_dictionary = read_tsv(OUT / "COMPLETE_173_EXTENDED_CARD_DICTIONARY.tsv")
    prose_reader = read_tsv(OUT / "PROSE_381_EXTENDED_COMPONENT_READER.tsv")
    unified = read_tsv(OUT / "TEN_PAGE_776_EXTENDED_COMPONENT_READER.tsv")
    source_dictionary = read_tsv(UNIQUE / "UNIQUE_173_MASTER_DICTIONARY.tsv")
    source_events = read_tsv(UNIQUE / "UNIQUE_381_EVENT_INTERLINEAR.tsv")
    source_statements = read_tsv(UNIQUE / "UNIQUE_116_STATEMENT_EDITION.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    expected_second_atoms = {"SHED", "L", "CTH", "CKH", "CKHE", "CHK", "SOLK", "WASH", "IIN", "TY", "AIR", "CHEO", "P", "PARTITION"}
    first_symbols = {row["symbol"] for row in first_components}
    second_symbols = {row["symbol"] for row in atoms}
    allowed_symbols = first_symbols | second_symbols
    first_seed_mcs = {row["master_card_id"] for row in first_seeds}
    first_prediction_mcs = {row["master_card_id"] for row in first_predictions}
    second_mcs = {row["master_card_id"] for row in second}
    remaining_mcs = {row["master_card_id"] for row in remaining}
    source_mcs = {row["master_card_id"] for row in source_dictionary}
    event_counts = Counter(row["master_card_id"] for row in source_events)
    expected_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}

    check("second_atom_table_has_14_rows", len(atoms) == 14, len(atoms))
    check("second_atom_ids_unique", len({row["component_id"] for row in atoms}) == 14, len({row["component_id"] for row in atoms}))
    check("second_atom_symbols_exact", second_symbols == expected_second_atoms, sorted(second_symbols))
    check("second_atom_cells_nonempty", all(all(value for value in row.values()) for row in atoms), len(atoms))
    check("second_ring_has_79_cards", len(second) == 79 and len(second_mcs) == 79, len(second_mcs))
    check("second_ring_heads_unique", len({row["master_head_form"] for row in second}) == 79, len({row["master_head_form"] for row in second}))
    check("second_ring_disjoint_from_first", not second_mcs & (first_seed_mcs | first_prediction_mcs), sorted(second_mcs & (first_seed_mcs | first_prediction_mcs)))
    check("second_sequences_use_known_atoms", all(set(row["atom_sequence"].split("+")) <= allowed_symbols for row in second), len(second))
    check("second_close_is_always_final", all("CLOSE" not in row["atom_sequence"].split("+") or row["atom_sequence"].split("+")[-1] == "CLOSE" for row in second), len(second))
    check("second_nuclei_are_short", all(1 <= len(row["portable_nucleus_de"].replace(";", "").split()) <= 6 for row in second), max(len(row["portable_nucleus_de"].replace(";", "").split()) for row in second))
    family_counts = Counter(row["second_ring_family"] for row in second)
    check("frame_cleanup_has_15_cards", family_counts["KNOWN_ATOMS_LOCAL_FRAME"] == 15, dict(family_counts))
    check("new_core_families_have_64_cards", len(second) - family_counts["KNOWN_ATOMS_LOCAL_FRAME"] == 64, len(second) - family_counts["KNOWN_ATOMS_LOCAL_FRAME"])

    check("remaining_table_has_19_cards", len(remaining) == 19 and len(remaining_mcs) == 19, len(remaining_mcs))
    check("remaining_is_disjoint", not remaining_mcs & (first_seed_mcs | first_prediction_mcs | second_mcs), sorted(remaining_mcs & (first_seed_mcs | first_prediction_mcs | second_mcs)))
    check("all_four_layers_partition_173_cards", first_seed_mcs | first_prediction_mcs | second_mcs | remaining_mcs == source_mcs and sum(map(len, (first_seed_mcs, first_prediction_mcs, second_mcs, remaining_mcs))) == 173, f"{len(first_seed_mcs)}/{len(first_prediction_mcs)}/{len(second_mcs)}/{len(remaining_mcs)}")
    check("remaining_cards_have_21_events", sum(event_counts[mc] for mc in remaining_mcs) == 21, sum(event_counts[mc] for mc in remaining_mcs))
    check("remaining_defaults_are_concrete", all(row["concrete_default_de"] and not re.search(r"UNKNOWN|EXEMPLAR|FORMAL", row["concrete_default_de"], re.IGNORECASE) for row in remaining), len(remaining))

    check("complete_dictionary_has_173_rows", len(complete_dictionary) == 173 and len({row["master_card_id"] for row in complete_dictionary}) == 173, len(complete_dictionary))
    dictionary_layers = Counter(row["composition_layer"] for row in complete_dictionary)
    expected_card_layers = Counter({"SECOND_RING_COMPOSED": 79, "FIRST_RING_PREDICTED": 46, "LEARNED_LOCAL_WHOLE": 19, "FIRST_RING_SHARED_SEED": 29})
    check("dictionary_layer_counts_exact", dictionary_layers == expected_card_layers, dict(dictionary_layers))
    check("dictionary_preserves_concrete_defaults", {row["master_card_id"]: row["concrete_default_de"] for row in complete_dictionary} == {row["master_card_id"]: row["unique_short_meaning_de"] for row in source_dictionary}, len(complete_dictionary))
    check("dictionary_has_no_empty_meaning", all(row["portable_nucleus_de"] and row["concrete_default_de"] for row in complete_dictionary), len(complete_dictionary))

    check("prose_reader_has_381_events", len(prose_reader) == 381, len(prose_reader))
    source_event_fields = list(source_events[0])
    check("prose_reader_preserves_source_events", all(all(new[field] == old[field] for field in source_event_fields) for old, new in zip(source_events, prose_reader, strict=True)), len(prose_reader))
    prose_layers = Counter(row["composition_layer"] for row in prose_reader)
    expected_prose_layers = Counter({"FIRST_RING_SHARED_SEED": 152, "FIRST_RING_PREDICTED": 89, "SECOND_RING_COMPOSED": 119, "LEARNED_LOCAL_WHOLE": 21})
    check("prose_layer_counts_exact", prose_layers == expected_prose_layers, dict(prose_layers))
    check("prose_has_360_composed_events", len(prose_reader) - prose_layers["LEARNED_LOCAL_WHOLE"] == 360, len(prose_reader) - prose_layers["LEARNED_LOCAL_WHOLE"])
    check("prose_final_reading_preserved", all(row["final_concrete_reading_de"] == row["unique_short_meaning_de"] for row in prose_reader), len(prose_reader))

    check("unified_reader_has_776_groups", len(unified) == 776, len(unified))
    check("unified_register_split", Counter(row["register"] for row in unified) == Counter({"PROSE": 381, "ASTRO": 395}), dict(Counter(row["register"] for row in unified)))
    check("unified_has_exact_ten_pages", {row["page"] for row in unified} == expected_pages, sorted({row["page"] for row in unified}))
    first_fields = list(first_reader[0])
    check("unified_preserves_first_reader", all(all(new[field] == old[field] for field in first_fields) for old, new in zip(first_reader, unified, strict=True)), len(unified))
    unified_layers = Counter(row["extended_composition_layer"] for row in unified)
    expected_unified_layers = Counter({"LOCAL_ASTRO_CARD": 306, "FIRST_RING_SHARED_SEED": 241, "SECOND_RING_COMPOSED": 119, "FIRST_RING_PREDICTED": 89, "LEARNED_LOCAL_WHOLE": 21})
    check("unified_layer_counts_exact", unified_layers == expected_unified_layers, dict(unified_layers))
    check("unified_has_449_composed_groups", len(unified) - unified_layers["LOCAL_ASTRO_CARD"] - unified_layers["LEARNED_LOCAL_WHOLE"] == 449, len(unified) - unified_layers["LOCAL_ASTRO_CARD"] - unified_layers["LEARNED_LOCAL_WHOLE"])
    check("unified_preserves_local_reading", all(row["extended_final_local_reading_de"] == row["final_local_expansion_de"] for row in unified), len(unified))

    passage_text = (OUT / "FOUR_SECOND_RING_PASSAGES.md").read_text(encoding="utf-8")
    passage_ids = {"H1-S001", "B2-S005", "B2-S016", "B3-S034"}
    statement_by_id = {row["statement_id"]: row for row in source_statements}
    check("four_passages_are_exact", len(re.findall(r"^## ", passage_text, flags=re.MULTILINE)) == 4 and all(f"## {sid}" in passage_text for sid in passage_ids), sorted(passage_ids))
    check("passage_surface_sequences_preserved", all(f"`{statement_by_id[sid]['surface_sequence']}`" in passage_text for sid in passage_ids), len(passage_ids))
    check("passages_have_new_and_previous_readings", passage_text.count("**Neue flüssige Lesung:**") == 4 and passage_text.count("**Bisherige Lesung:**") == 4, "4/4")

    report = (OUT / "SECOND_RING_GRAMMAR_REPORT.md").read_text(encoding="utf-8")
    pocket = (OUT / "SECOND_RING_POCKET_CARD.md").read_text(encoding="utf-8")
    check("report_has_core_counts", all(token in report for token in ("Vierzehn neue Sachkerne", "64 der verbliebenen 98", "Weitere 15 Karten", "154 von 173", "360 von 381", "19 Kartentypen", "21 Vorkommen", "449 von 776")), "14/64/15/154/360/19/21/449")
    check("pocket_lists_all_second_atoms", all(f"`{symbol}`" in pocket for symbol in expected_second_atoms), len(expected_second_atoms))

    expected_summary = {
        "first_ring_atoms": 17,
        "first_ring_bridge_cards": 4,
        "second_ring_atoms": 14,
        "first_ring_card_types": 75,
        "second_ring_card_types": 79,
        "composed_prose_card_types": 154,
        "remaining_learned_whole_card_types": 19,
        "first_ring_prose_events": 241,
        "second_ring_prose_events": 119,
        "composed_prose_events": 360,
        "remaining_learned_whole_events": 21,
        "astro_shared_events": 89,
        "composed_unified_groups": 449,
        "complete_unified_groups": 776,
        "rewritten_passages": 4,
    }
    check("summary_counts_exact", all(summary.get(key) == value for key, value in expected_summary.items()), {key: summary.get(key) for key in expected_summary})
    check("summary_hashes_exact", all(summary["output_sha256"].get(name) == digest(OUT / name) for name in CONTENT_NAMES), len(CONTENT_NAMES))
    sealed_pattern = re.compile(r"(?<![A-Za-z0-9])f84(?:r|v)?(?![A-Za-z0-9])", re.IGNORECASE)
    sealed_hits = [name for name in CONTENT_NAMES if sealed_pattern.search((OUT / name).read_text(encoding="utf-8"))]
    check("sealed_pages_absent_from_content", not sealed_hits, sealed_hits)

    before = {name: digest(OUT / name) for name in CONTENT_NAMES + ["BUILD_SUMMARY.json"]}
    rebuilt = subprocess.run([sys.executable, str(BUILDER)], cwd=ROOT, check=True, capture_output=True, text=True)
    after = {name: digest(OUT / name) for name in CONTENT_NAMES + ["BUILD_SUMMARY.json"]}
    check("deterministic_rebuild_is_byte_identical", before == after, "byte-identical" if before == after else sorted(name for name in before if before[name] != after[name]))
    check("builder_reports_built", '"status": "BUILT"' in rebuilt.stdout, rebuilt.stdout.splitlines()[0] if rebuilt.stdout else "NO_OUTPUT")

    failed = [item for item in checks if not item["pass"]]
    result = {
        "status": "PASS" if not failed else "FAIL",
        "checks_passed": len(checks) - len(failed),
        "checks_total": len(checks),
        "failed_checks": [item["name"] for item in failed],
        "counts": expected_summary,
        "checks": checks,
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "checks_passed", "checks_total", "failed_checks", "counts")}, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
