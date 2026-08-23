#!/usr/bin/env python3
"""Validate the complete reduced creative prose edition."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
GRAMMAR = ROOT / "experiments/yolo/sidequest_semantic_second_ring_grammar"
UNIQUE = ROOT / "experiments/yolo/sidequest_semantic_unique_master_glosses"
BUILDER = OUT / "build_reduced_complete_edition.py"

CONTENT_NAMES = [
    "IMPERATIVE_173_CARD_DICTIONARY.tsv",
    "IMPERATIVE_381_EVENT_TRACE.tsv",
    "COMPLETE_116_RETRANSLATED_STATEMENTS.tsv",
    "ELEVEN_RECORD_REDUCED_SUMMARY.tsv",
    "ELEVEN_RECORD_COMPLETE_READING.md",
    "REDUCED_COMPLETE_EDITION_REPORT.md",
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

    source_cards = read_tsv(GRAMMAR / "COMPLETE_173_EXTENDED_CARD_DICTIONARY.tsv")
    source_events = read_tsv(GRAMMAR / "PROSE_381_EXTENDED_COMPONENT_READER.tsv")
    source_statements = read_tsv(UNIQUE / "UNIQUE_116_STATEMENT_EDITION.tsv")
    cards = read_tsv(OUT / "IMPERATIVE_173_CARD_DICTIONARY.tsv")
    events = read_tsv(OUT / "IMPERATIVE_381_EVENT_TRACE.tsv")
    statements = read_tsv(OUT / "COMPLETE_116_RETRANSLATED_STATEMENTS.tsv")
    records = read_tsv(OUT / "ELEVEN_RECORD_REDUCED_SUMMARY.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    source_card_fields = list(source_cards[0])
    source_event_fields = list(source_events[0])
    check("dictionary_has_173_unique_cards", len(cards) == 173 and len({row["master_card_id"] for row in cards}) == 173, len(cards))
    check(
        "dictionary_preserves_source_bytes_by_cell",
        all(all(new[field] == old[field] for field in source_card_fields) for old, new in zip(source_cards, cards, strict=True)),
        len(cards),
    )
    check("every_card_has_short_imperative", all(1 <= len(row["imperative_phrase_de"].split()) <= 9 for row in cards), max(len(row["imperative_phrase_de"].split()) for row in cards))
    check("every_imperative_starts_uppercase", all(row["imperative_phrase_de"][:1].isupper() for row in cards), len(cards))
    check("no_fallback_imperative_remains", all("Führe aus:" not in row["imperative_phrase_de"] for row in cards), sum("Führe aus:" in row["imperative_phrase_de"] for row in cards))
    check("no_doubled_conjunction_in_imperatives", all(" und und" not in row["imperative_phrase_de"] for row in cards), len(cards))
    layer_counts = Counter(row["composition_layer"] for row in cards)
    check("dictionary_layers_exact", layer_counts == Counter({"SECOND_RING_COMPOSED": 79, "FIRST_RING_PREDICTED": 46, "FIRST_RING_SHARED_SEED": 29, "LEARNED_LOCAL_WHOLE": 19}), dict(layer_counts))

    check("event_trace_has_381_rows", len(events) == 381 and len({row["event_id"] for row in events}) == 381, len(events))
    check(
        "event_trace_preserves_source_bytes_by_cell",
        all(all(new[field] == old[field] for field in source_event_fields) for old, new in zip(source_events, events, strict=True)),
        len(events),
    )
    card_by_id = {row["master_card_id"]: row for row in cards}
    check("event_imperatives_match_dictionary", all(row["imperative_phrase_de"] == card_by_id[row["master_card_id"]]["imperative_phrase_de"] for row in events), len(events))
    prose_layers = Counter(row["composition_layer"] for row in events)
    expected_prose_layers = Counter({"FIRST_RING_SHARED_SEED": 152, "FIRST_RING_PREDICTED": 89, "SECOND_RING_COMPOSED": 119, "LEARNED_LOCAL_WHOLE": 21})
    check("event_layers_exact", prose_layers == expected_prose_layers, dict(prose_layers))
    check("event_composition_split_is_360_plus_21", len(events) - prose_layers["LEARNED_LOCAL_WHOLE"] == 360, f"{len(events) - prose_layers['LEARNED_LOCAL_WHOLE']}+{prose_layers['LEARNED_LOCAL_WHOLE']}")

    source_statement_by_id = {row["statement_id"]: row for row in source_statements}
    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
    check("statement_edition_has_116_unique_rows", len(statements) == 116 and len({row["statement_id"] for row in statements}) == 116, len(statements))
    check("statement_order_is_preserved", [row["statement_id"] for row in statements] == [row["statement_id"] for row in source_statements], len(statements))
    preserved_fields = ("record_unit_id", "page", "loci", "event_count", "surface_sequence")
    check(
        "statement_source_fields_preserved",
        all(all(row[field] == source_statement_by_id[row["statement_id"]][field] for field in preserved_fields) for row in statements),
        len(statements),
    )
    check("previous_fluent_column_is_exact", all(row["previous_fluent_reading_de"] == source_statement_by_id[row["statement_id"]]["fluent_workshop_sentence_de"] for row in statements), len(statements))
    check("statement_event_counts_exact", all(int(row["event_count"]) == len(events_by_statement[row["statement_id"]]) for row in statements), sum(int(row["event_count"]) for row in statements))
    check("all_events_partition_statements_once", sum(len(rows) for rows in events_by_statement.values()) == 381 and set(events_by_statement) == {row["statement_id"] for row in statements}, len(events_by_statement))
    check("atom_chains_reconstruct_exactly", all(row["atom_sequence_chain"] == " | ".join(event["atom_sequence"] for event in events_by_statement[row["statement_id"]]) for row in statements), len(statements))
    check("nucleus_chains_reconstruct_exactly", all(row["portable_nucleus_chain_de"] == " → ".join(event["portable_nucleus_de"] for event in events_by_statement[row["statement_id"]]) for row in statements), len(statements))
    check("imperative_chains_reconstruct_exactly", all(row["card_imperative_chain_de"] == "; ".join(event["imperative_phrase_de"] for event in events_by_statement[row["statement_id"]]) for row in statements), len(statements))
    check("all_reduced_readings_are_sentences", all(row["reduced_fluent_reading_de"] and row["reduced_fluent_reading_de"][-1] in ".!?" for row in statements), len(statements))
    check("statement_composition_split_exact", Counter(row["composition_status"] for row in statements) == Counter({"FULLY_COMPOSED": 98, "COMPOSED_WITH_LOCAL_WHOLE_WORDS": 18}), dict(Counter(row["composition_status"] for row in statements)))
    check("local_whole_counts_reconstruct_exactly", all(int(row["local_whole_word_events"]) == sum(event["composition_layer"] == "LEARNED_LOCAL_WHOLE" for event in events_by_statement[row["statement_id"]]) for row in statements), sum(int(row["local_whole_word_events"]) for row in statements))
    check("line_spanning_count_exact", sum(row["crosses_physical_line"] == "YES" for row in statements) == 18, sum(row["crosses_physical_line"] == "YES" for row in statements))
    check("revision_split_exact", Counter(row["revision_status"] for row in statements) == Counter({"REPHRASED": 111, "RETAINED_ALREADY_CONCISE": 5}), dict(Counter(row["revision_status"] for row in statements)))

    reduced_text = "\n".join(row["reduced_fluent_reading_de"] for row in statements)
    malformed = re.compile(r"das Vorgabewert|sein Vorgabewert|eine weiteren Anteil|das Folgewert|Zutatenmass|Führe aus:| und und|Postenportion|die Anteil")
    check("known_automatic_grammar_errors_absent", not malformed.search(reduced_text), malformed.findall(reduced_text))
    ascii_residue = re.compile(r"fuehr|ueber|zurueck|Staengel|vollstaendig|gekuehlt|abgekuehlt|giesse")
    check("known_ascii_transliteration_residue_absent", not ascii_residue.search(reduced_text), ascii_residue.findall(reduced_text))

    expected_records = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    check("record_summary_has_eleven_ordered_records", [row["record_unit_id"] for row in records] == expected_records, [row["record_unit_id"] for row in records])
    check("record_summary_totals_exact", sum(int(row["statement_count"]) for row in records) == 116 and sum(int(row["event_count"]) for row in records) == 381, f"{sum(int(row['statement_count']) for row in records)}/{sum(int(row['event_count']) for row in records)}")
    check("record_composition_totals_exact", sum(int(row["composed_event_count"]) for row in records) == 360 and sum(int(row["local_whole_word_events"]) for row in records) == 21, f"{sum(int(row['composed_event_count']) for row in records)}/{sum(int(row['local_whole_word_events']) for row in records)}")
    check("record_line_span_total_exact", sum(int(row["line_spanning_statements"]) for row in records) == 18, sum(int(row["line_spanning_statements"]) for row in records))
    check("record_continuous_text_reconstructs", all(row["continuous_reduced_reading_de"] == " ".join(statement["reduced_fluent_reading_de"] for statement in statements if statement["record_unit_id"] == row["record_unit_id"]) for row in records), len(records))

    readable = (OUT / "ELEVEN_RECORD_COMPLETE_READING.md").read_text(encoding="utf-8")
    check("readable_edition_contains_all_statements", all(f"**{row['statement_id']} · {row['loci']}**" in readable for row in statements), len(statements))
    check("readable_edition_contains_all_surfaces", all(f"`{row['surface_sequence']}`" in readable for row in statements), len(statements))
    check("readable_edition_has_eleven_sections", len(re.findall(r"^## [HB][1-6] —", readable, flags=re.MULTILINE)) == 11, len(re.findall(r"^## [HB][1-6] —", readable, flags=re.MULTILINE)))

    expected_summary = {
        "status": "BUILT",
        "master_cards": 173,
        "prose_events": 381,
        "statements": 116,
        "records": 11,
        "composed_events": 360,
        "local_whole_word_events": 21,
        "fully_composed_statements": 98,
        "mixed_statements": 18,
        "rephrased_statements": 111,
        "retained_concise_statements": 5,
        "line_spanning_statements": 18,
    }
    check("summary_counts_exact", all(summary.get(key) == value for key, value in expected_summary.items()), {key: summary.get(key) for key in expected_summary})
    check("summary_output_hashes_exact", all(summary["output_sha256"].get(name) == digest(OUT / name) for name in CONTENT_NAMES), len(CONTENT_NAMES))

    sealed_pattern = re.compile(r"(?<![A-Za-z0-9])f" + "84" + r"(?:r|v)?(?![A-Za-z0-9])", re.IGNORECASE)
    sealed_hits = [name for name in CONTENT_NAMES if sealed_pattern.search((OUT / name).read_text(encoding="utf-8"))]
    check("sealed_pages_absent_from_outputs", not sealed_hits, sealed_hits)

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
