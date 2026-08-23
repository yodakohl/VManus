#!/usr/bin/env python3
"""Validate the creative portable component grammar and complete reader."""

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
COMMON = ROOT / "experiments/yolo/sidequest_semantic_common_44_card_lexicon"
UNIQUE = ROOT / "experiments/yolo/sidequest_semantic_unique_master_glosses"
BUILDER = OUT / "build_portable_component_grammar.py"

CONTENT_NAMES = [
    "PORTABLE_17_ATOMS_AND_4_WHOLE_CARDS.tsv",
    "SEED_29_MASTER_CARD_COMPOSITIONS.tsv",
    "PREDICTED_ADDITIONAL_PROSE_CARDS.tsv",
    "TEN_PAGE_776_PORTABLE_COMPONENT_READER.tsv",
    "FOUR_REWRITTEN_COMPONENT_PASSAGES.md",
    "PORTABLE_COMPONENT_GRAMMAR_REPORT.md",
    "PORTABLE_COMPONENT_POCKET_CARD.md",
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

    components = read_tsv(OUT / "PORTABLE_17_ATOMS_AND_4_WHOLE_CARDS.tsv")
    seeds = read_tsv(OUT / "SEED_29_MASTER_CARD_COMPOSITIONS.tsv")
    predictions = read_tsv(OUT / "PREDICTED_ADDITIONAL_PROSE_CARDS.tsv")
    reader = read_tsv(OUT / "TEN_PAGE_776_PORTABLE_COMPONENT_READER.tsv")
    common_lexicon = read_tsv(COMMON / "COMMON_44_CARD_LEXICON.tsv")
    common_reader = read_tsv(COMMON / "TEN_PAGE_776_COMMON_READER.tsv")
    dictionary = read_tsv(UNIQUE / "UNIQUE_173_MASTER_DICTIONARY.tsv")
    events = read_tsv(UNIQUE / "UNIQUE_381_EVENT_INTERLINEAR.tsv")
    statements = read_tsv(UNIQUE / "UNIQUE_116_STATEMENT_EDITION.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    atom_symbols = {row["symbol"] for row in components if row["component_class"] != "LEARNED_WHOLE_CARD"}
    whole_symbols = {row["symbol"] for row in components if row["component_class"] == "LEARNED_WHOLE_CARD"}
    expected_atoms = {"AIIN", "AIN", "AR", "AL", "Y", "OK", "OL", "OT", "E", "EE", "EEE", "CHD", "OR", "HO", "KCH", "SH", "CLOSE"}
    expected_wholes = {"CHEEY", "DAIN", "ODY", "OS"}
    seed_mcs = {row["master_card_id"] for row in seeds}
    prediction_mcs = {row["master_card_id"] for row in predictions}
    source_shared_mcs = {row["prose_master_card_id"] for row in common_lexicon}
    dictionary_mcs = {row["master_card_id"] for row in dictionary}
    event_counts = Counter(row["master_card_id"] for row in events)
    expected_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}

    check("component_table_has_21_rows", len(components) == 21, len(components))
    check("component_ids_unique", len({row["component_id"] for row in components}) == 21, len({row["component_id"] for row in components}))
    check("exact_17_atom_inventory", atom_symbols == expected_atoms, sorted(atom_symbols))
    check("exact_four_whole_bridge_cards", whole_symbols == expected_wholes, sorted(whole_symbols))
    check("all_component_cells_nonempty", all(all(value for value in row.values()) for row in components), len(components))
    check("seed_table_has_29_master_cards", len(seeds) == 29 and len(seed_mcs) == 29, len(seed_mcs))
    check("seed_cards_equal_shared_master_inventory", seed_mcs == source_shared_mcs, sorted(seed_mcs ^ source_shared_mcs))
    shared_surface_union = {surface for row in seeds for surface in row["shared_visible_surfaces"].split(";")}
    check("seed_cards_cover_exact_44_shared_surfaces", shared_surface_union == {row["visible_surface"] for row in common_lexicon}, len(shared_surface_union))
    check("seed_atom_sequences_use_only_portable_units", all(set(row["atom_sequence"].split("+")) <= atom_symbols | whole_symbols for row in seeds), len(seeds))
    check("seed_close_is_always_final", all("CLOSE" not in row["atom_sequence"].split("+") or row["atom_sequence"].split("+")[-1] == "CLOSE" for row in seeds), len(seeds))

    check("prediction_table_has_46_cards", len(predictions) == 46 and len(prediction_mcs) == 46, len(prediction_mcs))
    check("predictions_are_new_master_cards", not (prediction_mcs & seed_mcs), sorted(prediction_mcs & seed_mcs))
    check("predictions_exist_in_173_dictionary", prediction_mcs <= dictionary_mcs, len(prediction_mcs))
    check("prediction_heads_unique", len({row["master_head_form"] for row in predictions}) == 46, len({row["master_head_form"] for row in predictions}))
    check("prediction_sequences_use_only_17_atoms", all(set(row["atom_sequence"].split("+")) <= atom_symbols for row in predictions), len(predictions))
    check("prediction_close_is_always_final", all("CLOSE" not in row["atom_sequence"].split("+") or row["atom_sequence"].split("+")[-1] == "CLOSE" for row in predictions), len(predictions))
    check("prediction_values_are_short", all(1 <= len(row["predicted_nucleus_de"].replace(";", "").split()) <= 6 for row in predictions), max(len(row["predicted_nucleus_de"].replace(";", "").split()) for row in predictions))
    check("portable_card_inventory_is_75_of_173", len(seed_mcs | prediction_mcs) == 75 and len(dictionary_mcs) == 173, f"{len(seed_mcs | prediction_mcs)}/173")
    seed_event_count = sum(event_counts[mc] for mc in seed_mcs)
    prediction_event_count = sum(event_counts[mc] for mc in prediction_mcs)
    check("seed_event_count_is_152", seed_event_count == 152, seed_event_count)
    check("prediction_event_count_is_89", prediction_event_count == 89, prediction_event_count)
    check("portable_prose_event_count_is_241", seed_event_count + prediction_event_count == 241, seed_event_count + prediction_event_count)

    check("reader_has_776_rows", len(reader) == 776, len(reader))
    check("reader_register_split_381_395", Counter(row["register"] for row in reader) == Counter({"PROSE": 381, "ASTRO": 395}), dict(Counter(row["register"] for row in reader)))
    check("reader_has_exact_ten_pages", {row["page"] for row in reader} == expected_pages, sorted({row["page"] for row in reader}))
    source_fields = list(common_reader[0])
    check("reader_preserves_all_common_reader_fields", all(all(new[field] == old[field] for field in source_fields) for old, new in zip(common_reader, reader, strict=True)), len(reader))
    check("reader_preserves_final_local_expansions", all(row["final_local_expansion_de"] == row["final_register_reading_de"] for row in reader), len(reader))
    status_counts = Counter(row["portable_component_status"] for row in reader)
    expected_status = Counter({"LOCAL_ASTRO_CARD": 306, "SHARED_SEED_CARD": 241, "LOCAL_LEARNED_CARD": 140, "PREDICTED_FROM_PORTABLE_ATOMS": 89})
    check("reader_status_counts_exact", status_counts == expected_status, dict(status_counts))
    check("reader_has_330_portable_groups", status_counts["SHARED_SEED_CARD"] + status_counts["PREDICTED_FROM_PORTABLE_ATOMS"] == 330, status_counts["SHARED_SEED_CARD"] + status_counts["PREDICTED_FROM_PORTABLE_ATOMS"])
    prose_rows = [row for row in reader if row["register"] == "PROSE"]
    astro_rows = [row for row in reader if row["register"] == "ASTRO"]
    check("prose_has_241_portable_events", sum(row["portable_component_status"] in {"SHARED_SEED_CARD", "PREDICTED_FROM_PORTABLE_ATOMS"} for row in prose_rows) == 241, sum(row["portable_component_status"] in {"SHARED_SEED_CARD", "PREDICTED_FROM_PORTABLE_ATOMS"} for row in prose_rows))
    check("astro_has_89_shared_seed_events", sum(row["portable_component_status"] == "SHARED_SEED_CARD" for row in astro_rows) == 89, sum(row["portable_component_status"] == "SHARED_SEED_CARD" for row in astro_rows))

    passage_text = (OUT / "FOUR_REWRITTEN_COMPONENT_PASSAGES.md").read_text(encoding="utf-8")
    passage_ids = {"H2-S002", "H5-S001", "B1-S002", "B3-S032"}
    check("four_passage_ids_are_exact", all(f"## {sid}" in passage_text for sid in passage_ids) and len(re.findall(r"^## ", passage_text, flags=re.MULTILINE)) == 4, sorted(passage_ids))
    statement_by_id = {row["statement_id"]: row for row in statements}
    check("all_passage_surfaces_are_preserved", all(f"`{statement_by_id[sid]['surface_sequence']}`" in passage_text for sid in passage_ids), len(passage_ids))
    check("every_passage_has_new_and_previous_reading", passage_text.count("**Neue flüssige Lesung:**") == 4 and passage_text.count("**Bisherige Lesung:**") == 4, "4/4")
    report = (OUT / "PORTABLE_COMPONENT_GRAMMAR_REPORT.md").read_text(encoding="utf-8")
    pocket = (OUT / "PORTABLE_COMPONENT_POCKET_CARD.md").read_text(encoding="utf-8")
    check("report_has_correct_core_counts", all(token in report for token in ("17 kurzen Atomen", "vier gelernten Ganzkarten", "29 gemeinsamen Meisterkarten", "weitere 46", "75 von 173", "241 von 381", "330 von 776")), "17/4/29/46/75/241/330")
    check("pocket_lists_all_21_symbols", all(f"`{symbol}`" in pocket for symbol in atom_symbols | whole_symbols), len(atom_symbols | whole_symbols))
    check("report_avoids_sentence_sized_shey", "`shey` als ganzen Satz" in report and "FREIGEGEBENER WERT" in pocket, "short bridge value")

    expected_summary = {
        "portable_atoms": 17,
        "learned_bridge_cards": 4,
        "shared_visible_surfaces": 44,
        "shared_master_seed_cards": 29,
        "predicted_additional_prose_cards": 46,
        "portable_prose_card_types": 75,
        "seed_prose_events": 152,
        "predicted_prose_events": 89,
        "portable_prose_events": 241,
        "astro_seed_events": 89,
        "portable_unified_groups": 330,
        "complete_reader_groups": 776,
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
