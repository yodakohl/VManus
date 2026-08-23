#!/usr/bin/env python3
"""Validate the compact common-card workshop lexicon and full reader."""

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
READER = ROOT / "experiments/yolo/sidequest_semantic_ten_page_unified_reader"
PATHS = ROOT / "experiments/yolo/sidequest_semantic_selected_job_paths"
BUILDER = OUT / "build_common_44_lexicon.py"

CONTENT_NAMES = [
    "COMMON_44_CARD_LEXICON.tsv",
    "COMMON_20_FAMILY_GRAMMAR.tsv",
    "COMMON_187_OCCURRENCE_TRACE.tsv",
    "TEN_PAGE_776_COMMON_READER.tsv",
    "FOUR_JOB_HEADERS_COMMON_CARDS.md",
    "COMMON_44_POCKET_DICTIONARY.md",
    "COMMON_44_CARD_REPORT.md",
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

    bridge = read_tsv(READER / "CROSS_REGISTER_44_SURFACE_BRIDGE.tsv")
    source_trace = read_tsv(READER / "TEN_PAGE_776_READER_TRACE.tsv")
    selected_echoes = read_tsv(PATHS / "SELECTED_9_CROSS_REGISTER_ECHOS.tsv")
    selected_choices = read_tsv(PATHS / "SELECTED_13_ASTRO_CHOICES.tsv")
    selected_paths = read_tsv(PATHS / "FOUR_SELECTED_JOB_PATHS.tsv")
    lexicon = read_tsv(OUT / "COMMON_44_CARD_LEXICON.tsv")
    families = read_tsv(OUT / "COMMON_20_FAMILY_GRAMMAR.tsv")
    occurrences = read_tsv(OUT / "COMMON_187_OCCURRENCE_TRACE.tsv")
    common_reader = read_tsv(OUT / "TEN_PAGE_776_COMMON_READER.tsv")
    summary = json.loads((OUT / "BUILD_SUMMARY.json").read_text(encoding="utf-8"))

    bridge_surfaces = {row["visible_surface"] for row in bridge}
    lexicon_surfaces = {row["visible_surface"] for row in lexicon}
    selected_surfaces = {row["visible_surface"] for row in selected_echoes}
    member_surfaces = {
        surface
        for row in families
        for surface in row["visible_members"].split(";")
    }
    expected_selected = {"aiin", "cheey", "cho", "dal", "dy", "okeey", "okey", "oldy", "sheey"}
    expected_pages = {"f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"}

    check("lexicon_has_44_cards", len(lexicon) == 44, len(lexicon))
    check("lexicon_surface_ids_unique", len(lexicon_surfaces) == len(lexicon), len(lexicon_surfaces))
    check("lexicon_equals_source_bridge", lexicon_surfaces == bridge_surfaces, sorted(lexicon_surfaces ^ bridge_surfaces))
    check("family_inventory_has_20_rows", len(families) == 20, len(families))
    check("family_ids_unique", len({row["family_id"] for row in families}) == 20, len({row["family_id"] for row in families}))
    check("family_member_counts_sum_44", sum(int(row["member_count"]) for row in families) == 44, sum(int(row["member_count"]) for row in families))
    check("family_members_equal_lexicon", member_surfaces == lexicon_surfaces, sorted(member_surfaces ^ lexicon_surfaces))
    check("each_card_has_short_nucleus", all(row["common_nucleus_de"] and len(row["common_nucleus_de"].split()) <= 5 for row in lexicon), max(len(row["common_nucleus_de"].split()) for row in lexicon))
    check("all_lexicon_cells_nonempty", all(all(value != "" for value in row.values()) for row in lexicon), sum(any(value == "" for value in row.values()) for row in lexicon))
    fit_counts = Counter(row["fit_type"] for row in lexicon)
    check("fit_split_36_direct_8_metaphor", fit_counts == Counter({"DIRECT_SHARED_OPERATION": 36, "WORKSHOP_REGISTER_METAPHOR": 8}), dict(fit_counts))
    check("selected_echo_set_is_exact_nine", selected_surfaces == expected_selected, sorted(selected_surfaces))
    check("lexicon_marks_exact_selected_echoes", {row["visible_surface"] for row in lexicon if row["selected_path_echo"] == "YES"} == expected_selected, sorted(row["visible_surface"] for row in lexicon if row["selected_path_echo"] == "YES"))

    check("occurrence_trace_has_187_rows", len(occurrences) == 187, len(occurrences))
    check("occurrence_serial_is_complete", [row["common_occurrence_serial"] for row in occurrences] == [f"C{i:03d}" for i in range(1, 188)], occurrences[-1]["common_occurrence_serial"] if occurrences else "NONE")
    occurrence_registers = Counter(row["register"] for row in occurrences)
    check("occurrence_register_split_98_89", occurrence_registers == Counter({"PROSE": 98, "ASTRO": 89}), dict(occurrence_registers))
    check("occurrence_trace_has_86_units", len({(row["register"], row["reading_unit_id"]) for row in occurrences}) == 86, len({(row["register"], row["reading_unit_id"]) for row in occurrences}))
    source_common = [row for row in source_trace if row["visible_surface"] in lexicon_surfaces]
    source_keys = [
        (row["register"], row["page"], row["source_group_id"], row["reading_unit_id"], row["visible_owner"], row["visible_surface"], row["resolved_reading_de"])
        for row in source_common
    ]
    occurrence_keys = [
        (row["register"], row["page"], row["source_group_id"], row["reading_unit_id"], row["visible_owner"], row["visible_surface"], row["register_expansion_de"])
        for row in occurrences
    ]
    check("occurrence_trace_exactly_copies_shared_source_rows", occurrence_keys == source_keys, len(occurrence_keys))
    prose_counts = Counter(row["visible_surface"] for row in occurrences if row["register"] == "PROSE")
    astro_counts = Counter(row["visible_surface"] for row in occurrences if row["register"] == "ASTRO")
    check("per_card_occurrence_counts_match_trace", all(int(row["prose_occurrence_count"]) == prose_counts[row["visible_surface"]] and int(row["astro_occurrence_count"]) == astro_counts[row["visible_surface"]] for row in lexicon), sum(prose_counts.values()) + sum(astro_counts.values()))
    nucleus_by_surface = {row["visible_surface"]: row["common_nucleus_de"] for row in lexicon}
    family_by_surface = {row["visible_surface"]: row["family_id"] for row in lexicon}
    check("occurrence_nuclei_invariant", all(row["common_nucleus_de"] == nucleus_by_surface[row["visible_surface"]] for row in occurrences), len(occurrences))
    check("occurrence_families_invariant", all(row["family_id"] == family_by_surface[row["visible_surface"]] for row in occurrences), len(occurrences))

    check("complete_reader_has_776_rows", len(common_reader) == 776, len(common_reader))
    check("complete_reader_register_split", Counter(row["register"] for row in common_reader) == Counter({"ASTRO": 395, "PROSE": 381}), dict(Counter(row["register"] for row in common_reader)))
    check("complete_reader_has_exact_ten_pages", {row["page"] for row in common_reader} == expected_pages, sorted({row["page"] for row in common_reader}))
    source_fields = list(source_trace[0])
    check("complete_reader_preserves_source_rows", all(all(new[field] == old[field] for field in source_fields) for old, new in zip(source_trace, common_reader, strict=True)), len(common_reader))
    check("complete_reader_preserves_register_reading", all(row["final_register_reading_de"] == row["resolved_reading_de"] for row in common_reader), len(common_reader))
    check("all_shared_rows_are_marked", sum(row["shared_card_status"] == "COMMON_44_CARD" for row in common_reader) == 187, sum(row["shared_card_status"] == "COMMON_44_CARD" for row in common_reader))
    check("all_nonshared_rows_remain_local", sum(row["shared_card_status"] == "NOT_SHARED_ACROSS_REGISTERS" for row in common_reader) == 589, sum(row["shared_card_status"] == "NOT_SHARED_ACROSS_REGISTERS" for row in common_reader))
    check("shared_reader_values_are_invariant", all(row["common_nucleus_de"] == nucleus_by_surface[row["visible_surface"]] and row["common_family_id"] == family_by_surface[row["visible_surface"]] for row in common_reader if row["shared_card_status"] == "COMMON_44_CARD"), 187)
    check("local_reader_values_are_unchanged", all(row["common_nucleus_de"] == row["resolved_reading_de"] and row["common_family_id"] == "LOCAL_OR_REGISTER_CARD" for row in common_reader if row["shared_card_status"] != "COMMON_44_CARD"), 589)

    headers = (OUT / "FOUR_JOB_HEADERS_COMMON_CARDS.md").read_text(encoding="utf-8")
    check("four_work_orders_present", all(f"## {row['work_order_id']}" in headers for row in selected_paths), len(selected_paths))
    check("all_thirteen_choices_present", all(row["selection_id"] in headers for row in selected_choices), len(selected_choices))
    choice_group_ids = [group_id for row in selected_choices for group_id in row["source_group_ids"].split(";")]
    check("all_choice_groups_exist_in_reader", all(group_id in {row["source_group_id"] for row in common_reader} for group_id in choice_group_ids), len(choice_group_ids))
    pocket = (OUT / "COMMON_44_POCKET_DICTIONARY.md").read_text(encoding="utf-8")
    report = (OUT / "COMMON_44_CARD_REPORT.md").read_text(encoding="utf-8")
    check("pocket_dictionary_has_44_card_sections", len(re.findall(r"^### `", pocket, flags=re.MULTILINE)) == 44, len(re.findall(r"^### `", pocket, flags=re.MULTILINE)))
    check("report_states_correct_metaphor_count", "## Acht nützliche Metaphern" in report and "## Neun nützliche Metaphern" not in report, "Acht")
    check("report_states_core_counts", all(token in report for token in ("44 sichtbaren Formen", "20 lehrbare Familien", "187 sichtbare Vorkommen", "98 in der Prosa", "89 in den Diagrammen", "86 Aussagen")), "44/20/187/98/89/86")

    summary_expected = {
        "common_surfaces": 44,
        "common_families": 20,
        "direct_shared_operations": 36,
        "workshop_register_metaphors": 8,
        "common_occurrences": 187,
        "prose_common_occurrences": 98,
        "astro_common_occurrences": 89,
        "affected_reading_units": 86,
        "selected_path_echo_surfaces": 9,
        "complete_reader_groups": 776,
    }
    check("build_summary_counts_exact", all(summary.get(key) == value for key, value in summary_expected.items()), {key: summary.get(key) for key in summary_expected})
    check("build_summary_output_hashes_exact", all(summary["output_sha256"].get(name) == digest(OUT / name) for name in CONTENT_NAMES), len(CONTENT_NAMES))
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
        "counts": summary_expected,
        "checks": checks,
    }
    (OUT / "VALIDATION.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "checks_passed", "checks_total", "failed_checks", "counts")}, ensure_ascii=False, indent=2))
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
