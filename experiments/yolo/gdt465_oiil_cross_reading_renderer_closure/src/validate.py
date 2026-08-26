#!/usr/bin/env python3
"""Validate GDT465 and verify a byte-identical deterministic rebuild."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt465_oiil_cross_reading_renderer_closure"
OUT = BASE / "artifacts"
RUN = BASE / "src/run.py"
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
CROSS_PATH = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
SOURCE_PATH = ROOT / "experiments/yolo/gdt464_residual_exact_package_bridge/artifacts/gdt464_107_revised_hybrid_dictionary.tsv"

CROSS_OUT = OUT / "gdt465_cross_reading_target.tsv"
SEQUENCE_OUT = OUT / "gdt465_6_component_sequence_tests.tsv"
RENDERER_OUT = OUT / "gdt465_13_renderer_neighbours.tsv"
DECISION_OUT = OUT / "gdt465_oiil_segmentation_decision.tsv"
DICTIONARY_OUT = OUT / "gdt465_107_final_hybrid_dictionary.tsv"
RESULT_OUT = OUT / "gdt465_result.json"
VALIDATION_OUT = OUT / "gdt465_validation.json"
GENERATED = (CROSS_OUT, SEQUENCE_OUT, RENDERER_OUT, DECISION_OUT, DICTIONARY_OUT, RESULT_OUT)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains_atoms(needle: list[str], haystack: list[str]) -> bool:
    return any(haystack[index:index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1))


def guarded_f17r_rows() -> tuple[dict[str, object], list[dict[str, str]]]:
    columns = "page,locus,all_three_present,all_present_exact,zl3b_it2a_similarity,zl3b_rf1b_similarity,zl3b_clean,it2a_clean,rf1b_clean"
    command = [
        str(ROOT / "vmanus-exp"), "query-tsv", str(CROSS_PATH),
        "--selector", "page", "--allow", "f17r", "--columns", columns,
        "--forbid-prefix", "f84", "--forbid-prefix", "f84r",
    ]
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError("guarded query did not emit exactly one stats row")
    stats = json.loads(stats_lines[0].removeprefix("GUARD_STATS "))
    rows = list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t"))
    return stats, rows


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "status": "PASS" if condition else "FAIL", "detail": detail})

    running = read_tsv(RUNNING_PATH)
    source = read_tsv(SOURCE_PATH)
    cross_artifact = read_tsv(CROSS_OUT)
    sequences = read_tsv(SEQUENCE_OUT)
    renderer = read_tsv(RENDERER_OUT)
    decisions = read_tsv(DECISION_OUT)
    labels = read_tsv(DICTIONARY_OUT)
    result = json.loads(RESULT_OUT.read_text(encoding="utf-8"))
    guard_stats, cross_rows = guarded_f17r_rows()

    running_recipe: dict[str, str] = {}
    running_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    invariant = True
    for row in running:
        previous = running_recipe.setdefault(row["surface"], row["component_recipe"])
        invariant &= previous == row["component_recipe"]
        running_events[row["surface"]].append(row)

    def recipe_surfaces(sequence: str) -> list[str]:
        atoms = sequence.split("+")
        return sorted(surface for surface, recipe in running_recipe.items() if contains_atoms(atoms, recipe.split("+")))

    def page_count(surfaces: list[str]) -> int:
        return len({row["physical_page"] for surface in surfaces for row in running_events[surface]})

    check("running_source_count", len(running) == 4576, f"observed={len(running)}")
    check("running_surface_invariance", invariant, "one recipe per running surface")
    check("source_label_count", len(source) == 107, f"observed={len(source)}")
    check("source_whole_tail", [row["surface"] for row in source if row["gdt464_hybrid_status"] == "WHOLE_LEARNED_LABEL"] == ["oiil"], "oiil only")

    check("guard_selected_count", guard_stats.get("selected") == 13 and len(cross_rows) == 13, str(guard_stats))
    check("guard_forbidden_count", guard_stats.get("skipped_forbidden") == 98, str(guard_stats))
    check("guard_allowed_page_only", {row["page"] for row in cross_rows} == {"f17r"}, "f17r only")
    target_cross = [row for row in cross_rows if row["locus"] == "f17r.13"]
    check("target_cross_row_unique", len(target_cross) == 1, f"observed={len(target_cross)}")
    if target_cross:
        target = target_cross[0]
        check("target_manual_readings", target["zl3b_clean"] == target["rf1b_clean"] == "oteeeon oiil" and target["it2a_clean"] == "", str(target))
        check("target_present_pair_exact", target["all_three_present"] == "0" and target["all_present_exact"] == "1", str(target))

    check("cross_artifact_count", len(cross_artifact) == 1, f"observed={len(cross_artifact)}")
    cross = cross_artifact[0]
    check("cross_artifact_identity", (cross["physical_page"], cross["locus"], cross["surface"], cross["source_event_id"]) == ("f17r", "f17r.13", "oiil", "P1003-E0080"), str(cross))
    check("cross_artifact_readings", cross["zl3b_reading"] == cross["rf1b_reading"] == "oteeeon oiil" and cross["it2a_reading"] == "MISSING", "two exact present readings")
    check("cross_artifact_token_flags", (cross["target_token_in_zl3b"], cross["target_token_in_it2a"], cross["target_token_in_rf1b"]) == ("YES", "MISSING_LOCUS", "YES"), "target token exact")
    check("cross_artifact_guard_counts", cross["guard_selected_locus_count"] == "13" and cross["guard_forbidden_skip_count"] == "98", "guard stats retained")
    check("cross_artifact_image_owner", cross["image_object_id"] == "1006106" and cross["manual_image_result"] == "ONE_OWNER_BOUND_LABEL__NO_VISIBLE_INTERNAL_OBJECT_SPLIT", "one pictured owner")
    check("cross_artifact_image_hash", cross["review_image_sha256"] == "eccb822a72a8c27045aefa4f19d558dba29ef046c1d8e3772c715a99ee7113b9", cross["review_image_sha256"])

    check("sequence_row_count", len(sequences) == 6, f"observed={len(sequences)}")
    expected_sequence_metrics = {
        "O+IIN": (16, 28, 13),
        "IIN+L": (0, 0, 0),
        "O+IIN+L": (0, 0, 0),
        "AIIN+L": (1, 1, 1),
        "O+AIIN+L": (0, 0, 0),
        "L+O+IIN": (1, 1, 1),
    }
    sequence_map = {row["component_sequence"]: row for row in sequences}
    check("sequence_key_set", set(sequence_map) == set(expected_sequence_metrics), str(sorted(sequence_map)))
    for sequence, expected in expected_sequence_metrics.items():
        surfaces = recipe_surfaces(sequence)
        recomputed = (len(surfaces), sum(len(running_events[surface]) for surface in surfaces), page_count(surfaces))
        row = sequence_map[sequence]
        observed = (int(row["carrier_surface_type_count"]), int(row["carrier_event_count"]), int(row["carrier_page_count"]))
        key = sequence.replace("+", "_")
        check(f"sequence_metrics_{key}", observed == recomputed == expected, f"observed={observed}; recomputed={recomputed}")
        check(f"sequence_surfaces_{key}", row["carrier_surfaces"] == ("|".join(surfaces) or "NONE"), row["carrier_surfaces"])
    check("full_hypothesis_rejected", sequence_map["O+IIN+L"]["role_in_oiil_test"] == "FULL_TARGET_HYPOTHESIS" and sequence_map["O+IIN+L"]["decision"] == "REJECT_ZERO_CARRIERS", str(sequence_map["O+IIN+L"]))

    expected_oii = sorted(surface for surface in running_recipe if "oii" in surface)
    expected_iil = sorted(surface for surface in running_recipe if "iil" in surface)
    check("renderer_row_count", len(renderer) == 13, f"observed={len(renderer)}")
    check("renderer_pattern_counts", Counter(row["pattern"] for row in renderer) == Counter({"oii": 12, "iil": 1}), str(Counter(row["pattern"] for row in renderer)))
    check("renderer_surface_inventory", sorted(row["running_surface"] for row in renderer if row["pattern"] == "oii") == expected_oii and sorted(row["running_surface"] for row in renderer if row["pattern"] == "iil") == expected_iil, f"oii={len(expected_oii)} iil={len(expected_iil)}")
    check("renderer_rows_exact", all(row["component_recipe"] == running_recipe[row["running_surface"]] and int(row["event_count"]) == len(running_events[row["running_surface"]]) for row in renderer), "all tied to running source")
    check("renderer_no_target", all(row["exact_target_surface"] == "NO" for row in renderer), "oiil absent from running inventory")
    check("renderer_no_license", all(row["licenses_oiil_split"] == "NO" for row in renderer), "no neighbour licenses split")
    iil_rows = [row for row in renderer if row["pattern"] == "iil"]
    check("renderer_iil_control", len(iil_rows) == 1 and iil_rows[0]["running_surface"] == "cphodaiils" and iil_rows[0]["component_recipe"] == "CH+P+O+D_ADDR+AIIN+L+S", str(iil_rows))

    check("decision_row_count", len(decisions) == 1, f"observed={len(decisions)}")
    decision = decisions[0]
    check("decision_candidate", decision["surface"] == "oiil" and decision["candidate_segmentation"] == "o|ii|l" and decision["candidate_recipe"] == "O+IIN+L", str(decision))
    check("decision_exact_cards", (decision["exact_card_o"], decision["exact_card_ii_or_oii"], decision["exact_card_iil"], decision["exact_card_l"], decision["exact_full_surface"]) == ("O", "ABSENT", "ABSENT", "L", "ABSENT"), "edges only")
    check("decision_no_complete_parse", decision["complete_exact_card_segmentation_count"] == "0" and decision["full_recipe_carrier_type_count"] == "0", "zero complete support")
    check("decision_no_family_bridge", decision["strict_owner_family_bridge"] == "NONE", decision["strict_owner_family_bridge"])
    check("decision_retains_default", decision["selected_status"] == "WHOLE_LEARNED_LABEL" and decision["selected_default_de"] == "[PFLANZENNAME:oiil]", decision["selected_default_de"])
    check("exact_surface_card_audit", running_recipe.get("o") == "O" and running_recipe.get("l") == "L" and all(surface not in running_recipe for surface in ("oii", "iil", "oiil")), "o/l present; middle/full absent")

    check("final_dictionary_count", len(labels) == 107, f"observed={len(labels)}")
    check("final_dictionary_order", [row["source_event_id"] for row in labels] == [row["source_event_id"] for row in source], "source order exact")
    check("final_dictionary_surfaces", [row["surface"] for row in labels] == [row["surface"] for row in source], "surface order exact")
    source_fields = list(source[0])
    check("final_dictionary_source_values", all(all(row[field] == old[field] for field in source_fields) for row, old in zip(labels, source)), "all GDT464 fields unchanged")
    check("final_dictionary_status_copy", all(row["gdt465_hybrid_status"] == old["gdt464_hybrid_status"] for row, old in zip(labels, source)), "all statuses copied")
    changed = [row for row in labels if row["gdt465_change"] != "UNCHANGED_FROM_GDT464"]
    check("final_dictionary_one_audit", len(changed) == 1 and changed[0]["surface"] == "oiil" and changed[0]["gdt465_change"] == "OIIL_AUDITED_AND_RETAINED_WHOLE", str([(row["surface"], row["gdt465_change"]) for row in changed]))
    check("final_dictionary_status_counts", Counter(row["gdt465_hybrid_status"] for row in labels) == Counter({"FULL_FUNCTION_FORMULA": 18, "FUNCTION_SHELL_PLUS_LEARNED_CORE": 87, "OWNER_FAMILY_STEM_ONLY": 1, "WHOLE_LEARNED_LABEL": 1}), str(Counter(row["gdt465_hybrid_status"] for row in labels)))
    check("final_dictionary_whole_tail", [row["surface"] for row in labels if row["gdt465_hybrid_status"] == "WHOLE_LEARNED_LABEL"] == ["oiil"], "oiil only")
    check("final_dictionary_character_totals", sum(int(row["known_function_character_count"]) for row in labels) == 440 and sum(int(row["surface_character_count"]) for row in labels) == 713, "440/713")
    check("final_dictionary_character_reconciliation", all(int(row["known_function_character_count"]) + int(row["remaining_learned_character_count"]) == len(row["surface"]) == int(row["surface_character_count"]) for row in labels), "all rows reconcile")

    check("result_status", result["status"] == "OIIL_REMAINS_SINGLE_WHOLE_LABEL__NOMENCLATOR_TAIL_CLOSED", result["status"])
    check("result_source_counts", result["source_label_count"] == 107 and result["running_event_count"] == 4576 and result["guarded_f17r_locus_count"] == 13, str(result))
    check("result_reading_counts", result["target_present_reading_count"] == 2 and result["target_present_readings_exact"] is True and result["target_missing_readings"] == ["IT2a"], str(result["target_missing_readings"]))
    check("result_package_counts", result["complete_exact_card_segmentation_count"] == 0 and result["o_iin_l_recipe_carrier_type_count"] == 0 and result["iin_l_recipe_carrier_type_count"] == 0, "all zero")
    check("result_tail", result["remaining_whole_label_count"] == 1 and result["remaining_whole_labels"] == ["oiil"], str(result["remaining_whole_labels"]))
    check("result_character_counts", result["known_function_character_count"] == 440 and result["surface_character_count"] == 713, "440/713")
    check("result_claim_ceiling", result["new_core_meanings"] == result["new_pages"] == result["confirmed_lexemes"] == 0, "no expanded claim")
    check("sealed_pages_absent", all(not row.get("physical_page", row.get("page", "")).startswith("f84") for table in (running, source, cross_artifact, labels) for row in table), "no sealed page in source or outputs")

    before = {path.name: sha256(path) for path in GENERATED}
    completed = subprocess.run([sys.executable, str(RUN)], cwd=ROOT, capture_output=True, text=True, check=False)
    check("deterministic_rebuild_exit", completed.returncode == 0, completed.stderr[-500:] or "exit 0")
    after = {path.name: sha256(path) for path in GENERATED}
    check("deterministic_rebuild_bytes", before == after, "all generated artifact hashes unchanged")

    passed = sum(row["status"] == "PASS" for row in checks)
    failed = len(checks) - passed
    payload = {
        "status": "PASS" if failed == 0 else "FAIL",
        "check_count": len(checks),
        "passed": passed,
        "failed": failed,
        "checks": checks,
    }
    VALIDATION_OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": payload["status"], "checks": len(checks), "passed": passed, "failed": failed}, ensure_ascii=False))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
