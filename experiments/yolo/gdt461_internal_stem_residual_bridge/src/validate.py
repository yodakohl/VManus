#!/usr/bin/env python3
"""Validate GDT461 internal stems and residual-family bridge."""

from __future__ import annotations

import csv
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
BASE = ROOT / "experiments/yolo/gdt461_internal_stem_residual_bridge"
OUT = BASE / "artifacts"
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
ADDRESS_PATH = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts/gdt459_183_address_interlinear.tsv"
SOURCE_PATH = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas/artifacts/gdt460_107_hybrid_label_dictionary.tsv"
RUN_SCRIPT = BASE / "src/run.py"

INTERNAL_PATH = OUT / "gdt461_9_calibrated_internal_stems.tsv"
OCCURRENCE_PATH = OUT / "gdt461_53_internal_occurrences.tsv"
BRIDGE_PATH = OUT / "gdt461_residual_owner_family_bridge.tsv"
LABEL_PATH = OUT / "gdt461_107_revised_hybrid_dictionary.tsv"
RESIDUAL_PATH = OUT / "gdt461_19_residual_audit.tsv"
PAGE_PATH = OUT / "gdt461_6_page_summary.tsv"
RESULT_PATH = OUT / "gdt461_result.json"
VALIDATION_PATH = OUT / "gdt461_validation.json"

EXPECTED_INTERNAL = {
    "air": ("AIR", 8, 8),
    "cth": ("CH+T", 39, 39),
    "dar": ("D_ADDR+AR", 6, 6),
    "al": ("AL", 81, 74),
    "ar": ("AR", 38, 35),
    "ok": ("OK", 114, 107),
    "ol": ("OL", 107, 103),
    "ot": ("OT", 56, 55),
    "sh": ("SH", 131, 125),
}
EXPECTED_STATUS = {
    "FULL_FUNCTION_FORMULA": 12,
    "FUNCTION_SHELL_PLUS_LEARNED_CORE": 81,
    "OWNER_FAMILY_STEM_ONLY": 1,
    "WHOLE_LEARNED_LABEL": 13,
}
EXPECTED_FULL = {
    "okolar", "alcphy", "okaraiin", "otalaiin", "okalam", "sharam",
    "okaram", "otolam", "alaly", "otolaiin", "otokol", "otolarol",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def contains_atoms(needle: list[str], haystack: list[str]) -> bool:
    return any(haystack[index:index + len(needle)] == needle for index in range(len(haystack) - len(needle) + 1))


def strict_internal_positions(surface: str, stem: str) -> list[int]:
    return [index for index in range(1, len(surface) - len(stem)) if surface.startswith(stem, index)]


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    running = read_tsv(RUNNING_PATH)
    addresses = read_tsv(ADDRESS_PATH)
    source = read_tsv(SOURCE_PATH)
    internal = read_tsv(INTERNAL_PATH)
    occurrences = read_tsv(OCCURRENCE_PATH)
    bridges = read_tsv(BRIDGE_PATH)
    labels = read_tsv(LABEL_PATH)
    residual = read_tsv(RESIDUAL_PATH)
    pages = read_tsv(PAGE_PATH)
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    check("source_label_count", len(source) == 107, f"observed={len(source)} expected=107")
    check("source_address_count", len(addresses) == 183, f"observed={len(addresses)} expected=183")
    check("internal_stem_count", len(internal) == 9, f"observed={len(internal)} expected=9")
    check("internal_stem_set", {row["surface_stem"] for row in internal} == set(EXPECTED_INTERNAL), "exact nine internal stems")
    check("internal_occurrence_count", len(occurrences) == 53, f"observed={len(occurrences)} expected=53")
    check("internal_occurrence_ids_unique", len({row["internal_occurrence_id"] for row in occurrences}) == 53, "53 unique occurrence IDs")
    check("revised_label_count", len(labels) == 107, f"observed={len(labels)} expected=107")
    check("residual_audit_count", len(residual) == 19, f"observed={len(residual)} expected=19")
    check("page_count", len(pages) == 6, f"observed={len(pages)} expected=6")
    check(
        "source_order_exact",
        [row["source_event_id"] for row in labels] == [row["source_event_id"] for row in source]
        and [row["surface"] for row in labels] == [row["surface"] for row in source],
        "107 labels retained in source order",
    )
    check(
        "source_bindings_exact",
        all(
            tuple(row[key] for key in ("physical_page", "register", "locus", "owner_de", "content_class", "image_object_id", "review_image_sha256"))
            == tuple(old[key] for key in ("physical_page", "register", "locus", "owner_de", "content_class", "image_object_id", "review_image_sha256"))
            for row, old in zip(labels, source)
        ),
        "page/register/locus/owner/content/image retained",
    )

    running_recipe: dict[str, str] = {}
    for row in running:
        running_recipe.setdefault(row["surface"], row["component_recipe"])
    internal_recomputed = True
    for row in internal:
        stem = row["surface_stem"]
        recipe = row["component_recipe"]
        extensions = [
            (surface, candidate_recipe) for surface, candidate_recipe in running_recipe.items()
            if surface != stem and strict_internal_positions(surface, stem)
        ]
        matches = [
            (surface, candidate_recipe) for surface, candidate_recipe in extensions
            if contains_atoms(recipe.split("+"), candidate_recipe.split("+"))
        ]
        expected_recipe, expected_extensions, expected_matches = EXPECTED_INTERNAL[stem]
        internal_recomputed &= (
            running_recipe.get(stem) == recipe == expected_recipe
            and len(extensions) == int(row["running_internal_extension_type_count"]) == expected_extensions
            and len(matches) == int(row["running_matching_type_count"]) == expected_matches
            and f"{len(matches) / len(extensions):.6f}" == row["running_type_precision"]
            and len(extensions) >= 4
            and len(matches) / len(extensions) >= 0.90
        )
    check("internal_calibration_recomputed", internal_recomputed, "all nine internal channels reproduce support and >=0.90 precision")

    source_index = {row["source_event_id"]: row for row in source}
    occurrence_groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in occurrences:
        occurrence_groups[row["source_event_id"]].append(row)
    occurrence_valid = True
    for event_id, rows in occurrence_groups.items():
        old = source_index[event_id]
        surface = old["surface"]
        prefix_length = 0 if old["prefix_stem"] == "NONE" else len(old["prefix_stem"])
        suffix_length = 0 if old["suffix_stem"] == "NONE" else len(old["suffix_stem"])
        center_end = len(surface) - suffix_length if suffix_length else len(surface)
        intervals: list[tuple[int, int]] = []
        for row in rows:
            start = int(row["character_start_zero_based"])
            end = int(row["character_end_exclusive"])
            occurrence_valid &= (
                surface[start:end] == row["internal_stem"]
                and start > 0
                and end < len(surface)
                and start >= prefix_length
                and end <= center_end
                and row["internal_stem"] in EXPECTED_INTERNAL
                and row["component_recipe"] == EXPECTED_INTERNAL[row["internal_stem"]][0]
            )
            intervals.append((start, end))
        occurrence_valid &= all(right[0] >= left[1] for left, right in zip(sorted(intervals), sorted(intervals)[1:]))
    check("internal_occurrences_valid", occurrence_valid, "all 53 occurrences strict-internal, center-bound and nonoverlapping")
    check("internal_label_count", len(occurrence_groups) == 44, f"observed={len(occurrence_groups)} expected=44")
    check("internal_character_count", sum(len(row["internal_stem"]) for row in occurrences) == 114, "114 characters assigned internally")

    check("residual_bridge_count", len(bridges) == 1, f"observed={len(bridges)} expected=1")
    bridge = bridges[0]
    check(
        "residual_bridge_exact",
        bridge["surface_substring"] == "cheo"
        and bridge["working_family_value_de"] == "DROGENFAMILIE"
        and bridge["unique_address_surface_count"] == "4"
        and set(bridge["address_surfaces"].split("|")) == {"cheocthy", "cheody", "cheosdy", "opcheor"}
        and set(bridge["pages"].split("|")) == {"f88v", "f89r"}
        and bridge["old_whole_target_surfaces"] == "cheosdy",
        "cheo joins four pharmaceutical address surfaces on both pages",
    )

    revised_valid = True
    for row, old in zip(labels, source):
        selected = occurrence_groups.get(row["source_event_id"], [])
        known = int(old["known_edge_character_count"]) + sum(len(item["internal_stem"]) for item in selected)
        family = old["owner_family_stem_trace"] != "NONE" or "cheo" in row["surface"]
        if known == len(row["surface"]):
            expected_status = "FULL_FUNCTION_FORMULA"
        elif known > 0:
            expected_status = "FUNCTION_SHELL_PLUS_LEARNED_CORE"
        elif family:
            expected_status = "OWNER_FAMILY_STEM_ONLY"
        else:
            expected_status = "WHOLE_LEARNED_LABEL"
        revised_valid &= (
            int(row["internal_occurrence_count"]) == len(selected)
            and int(row["known_function_character_count"]) == known
            and int(row["remaining_learned_character_count"]) == len(row["surface"]) - known
            and row["revised_hybrid_status"] == expected_status
        )
    check("revised_assignment_recomputed", revised_valid, "known characters and revised status reproduced for 107 labels")
    status_counts = Counter(row["revised_hybrid_status"] for row in labels)
    check("revised_status_counts", dict(status_counts) == EXPECTED_STATUS, f"observed={dict(status_counts)}")
    check("full_formula_set", {row["surface"] for row in labels if row["revised_hybrid_status"] == "FULL_FUNCTION_FORMULA"} == EXPECTED_FULL, "exact twelve full function formulas")
    check("any_function_count", sum(int(row["known_function_character_count"]) > 0 for row in labels) == 93, "93 labels contain a calibrated function channel")
    check("any_structure_count", sum(int(row["known_function_character_count"]) > 0 or row["owner_family_stem_trace"] != "NONE" for row in labels) == 94, "94 labels have function or owner-family structure")
    check("known_character_count", sum(int(row["known_function_character_count"]) for row in labels) == 391, "391/713 characters assigned to calibrated functions")
    check("surface_character_count", sum(int(row["surface_character_count"]) for row in labels) == 713, "713 source characters")
    check("known_character_fraction", f"{391 / 713:.6f}" == "0.548387", "known function fraction 0.548387")
    check(
        "defaults_nonempty_concrete",
        all(row["revised_short_default_de"].strip() and "UNKNOWN" not in row["revised_short_default_de"].upper() and "EXEMPLAR" not in row["revised_short_default_de"].upper() for row in labels),
        "107 nonempty working defaults without placeholders",
    )

    residual_index = {row["surface"]: row for row in residual}
    old_whole = {row["surface"] for row in source if row["hybrid_status"] == "WHOLE_LEARNED_LABEL"}
    check("residual_source_set", set(residual_index) == old_whole and len(old_whole) == 19, "audit covers exact old 19-label tail")
    check("residual_internal_count", sum(row["internal_stem_trace"] != "NONE" for row in residual) == 5, "five old whole labels gain internal functions")
    check("residual_new_family_count", sum(row["new_owner_family_bridge"] != "NONE" for row in residual) == 1, "one old whole label gains cheo family")
    check("residual_remaining_whole", sum(row["revised_hybrid_status"] == "WHOLE_LEARNED_LABEL" for row in residual) == 13, "thirteen whole labels remain")
    check("page_set_exact", {row["physical_page"] for row in pages} == {"f17r", "f71v", "f72r", "f77r", "f88v", "f89r"}, "six admitted pages only")
    check(
        "page_totals_reconcile",
        sum(int(row["label_count"]) for row in pages) == 107
        and sum(int(row["full_function_formula_count"]) for row in pages) == 12
        and sum(int(row["function_shell_plus_core_count"]) for row in pages) == 81
        and sum(int(row["owner_family_only_count"]) for row in pages) == 1
        and sum(int(row["whole_learned_label_count"]) for row in pages) == 13
        and sum(int(row["labels_with_internal_stem"]) for row in pages) == 44
        and sum(int(row["internal_occurrence_count"]) for row in pages) == 53
        and sum(int(row["known_function_character_count"]) for row in pages) == 391,
        "page summary reconciles",
    )

    check("result_status", result["status"] == "INTERNAL_FUNCTION_STEMS_REDUCE_WHOLE_LABEL_TAIL_TO_THIRTEEN", result["status"])
    check(
        "result_counts",
        result["source_label_count"] == 107
        and result["calibrated_internal_stem_count"] == 9
        and result["labels_with_internal_stem_count"] == 44
        and result["internal_occurrence_count"] == 53
        and result["internal_assigned_character_count"] == 114
        and result["new_residual_owner_family_bridge_count"] == 1
        and result["revised_hybrid_status_counts"] == EXPECTED_STATUS
        and result["labels_with_any_function_count"] == 93
        and result["labels_with_any_structure_count"] == 94
        and result["known_function_character_count"] == 391
        and result["surface_character_count"] == 713
        and result["known_function_character_fraction"] == "0.548387"
        and result["old_whole_residual_count"] == 19
        and result["old_whole_residuals_with_internal_function"] == 5
        and result["old_whole_residuals_with_new_family_bridge"] == 1
        and result["remaining_whole_label_count"] == 13,
        "result JSON reconciles with all outputs",
    )
    check("claim_ceiling_zeroes", all(result[key] == 0 for key in ("core_meaning_revisions", "new_pages", "surface_predictions", "confirmed_lexemes")), "no core revision, page, generated surface or lexeme")
    generated = (INTERNAL_PATH, OCCURRENCE_PATH, BRIDGE_PATH, LABEL_PATH, RESIDUAL_PATH, PAGE_PATH, RESULT_PATH)
    serialized = "\n".join(path.read_text(encoding="utf-8") for path in generated)
    check("sealed_pages_absent", "f84" not in serialized.lower(), "no sealed folio token")
    check("artifact_size_gate", all(path.stat().st_size < 5_000_000 for path in generated), "all artifacts below 5 MB")
    before = {path: path.read_bytes() for path in generated}
    completed = subprocess.run([sys.executable, str(RUN_SCRIPT)], cwd=ROOT, check=False, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in generated}
    check("deterministic_rebuild_exit", completed.returncode == 0, f"returncode={completed.returncode}")
    check("deterministic_rebuild_bytes", before == after, "all seven generated artifacts byte-identical")

    passed = sum(bool(row["passed"]) for row in checks)
    validation = {"status": "PASS" if passed == len(checks) else "FAIL", "checks_passed": passed, "checks_total": len(checks), "checks": checks}
    VALIDATION_PATH.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
