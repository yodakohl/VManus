#!/usr/bin/env python3
"""Validate GDT462's bounded ar-prefix exception audit."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt462_near_threshold_ar_edge_exception_audit"
OUT = BASE / "artifacts"
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
ATTACHMENT_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_5051_attachment_edition.tsv"
SOURCE_PATH = ROOT / "experiments/yolo/gdt461_internal_stem_residual_bridge/artifacts/gdt461_107_revised_hybrid_dictionary.tsv"
RUN_SCRIPT = BASE / "src/run.py"

INVENTORY_PATH = OUT / "gdt462_residual_edge_channel_inventory.tsv"
EXTENSION_PATH = OUT / "gdt462_ar_complete_running_extensions.tsv"
PACKAGE_PATH = OUT / "gdt462_ar_repeated_relation_package.tsv"
TARGET_PATH = OUT / "gdt462_two_promoted_residual_labels.tsv"
LABEL_PATH = OUT / "gdt462_107_revised_hybrid_dictionary.tsv"
PAGE_PATH = OUT / "gdt462_6_page_summary.tsv"
RESULT_PATH = OUT / "gdt462_result.json"
VALIDATION_PATH = OUT / "gdt462_validation.json"

EXPECTED_STATUS = {
    "FULL_FUNCTION_FORMULA": 12,
    "FUNCTION_SHELL_PLUS_LEARNED_CORE": 83,
    "OWNER_FAMILY_STEM_ONLY": 1,
    "WHOLE_LEARNED_LABEL": 11,
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    running = read_tsv(RUNNING_PATH)
    attachments = read_tsv(ATTACHMENT_PATH)
    source = read_tsv(SOURCE_PATH)
    inventory = read_tsv(INVENTORY_PATH)
    extensions = read_tsv(EXTENSION_PATH)
    packages = read_tsv(PACKAGE_PATH)
    targets = read_tsv(TARGET_PATH)
    labels = read_tsv(LABEL_PATH)
    pages = read_tsv(PAGE_PATH)
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    check("source_label_count", len(source) == 107, f"observed={len(source)} expected=107")
    check("source_whole_count", sum(row["revised_hybrid_status"] == "WHOLE_LEARNED_LABEL" for row in source) == 13, "exact GDT461 thirteen-label tail")
    check("inventory_count", len(inventory) == 11, f"observed={len(inventory)} expected=11")
    near = [row for row in inventory if row["audit_band"] == "NEAR_THRESHOLD_REVIEW"]
    check("near_threshold_exact", len(near) == 1 and near[0]["edge"] == "PREFIX" and near[0]["surface_stem"] == "ar", "sole 0.75-0.90 channel is prefix ar")
    check("ar_inventory_counts", near[0]["component_recipe"] == "AR" and near[0]["running_extension_type_count"] == "7" and near[0]["running_matching_type_count"] == "6" and near[0]["running_type_precision"] == "0.857143", "ar reproduces 6/7")
    check("ar_target_set", set(near[0]["residual_surfaces"].split("|")) == {"arom", "arody"}, "ar touches exactly two residuals")
    check("no_other_promotion", sum(row["decision"] == "PROMOTE_AFTER_PACKAGE_EXCEPTION" for row in inventory) == 1, "only ar promoted")

    running_recipe: dict[str, str] = {}
    invariant = True
    for row in running:
        previous = running_recipe.setdefault(row["surface"], row["component_recipe"])
        invariant &= previous == row["component_recipe"]
    check("running_surfaces_invariant", invariant, "every running surface has one recipe")
    ar_extensions = [(surface, recipe) for surface, recipe in running_recipe.items() if surface != "ar" and surface.startswith("ar")]
    ar_matches = [(surface, recipe) for surface, recipe in ar_extensions if recipe.split("+")[0] == "AR"]
    check("extension_count_recomputed", len(ar_extensions) == 7 and len(ar_matches) == 6, "running dictionary independently gives 6/7")
    check("extension_table_count", len(extensions) == 7, "seven complete extension rows")
    check("extension_surface_set", {row["surface"] for row in extensions} == {surface for surface, _ in ar_extensions}, "all and only ar extensions")
    mismatches = [row for row in extensions if row["prefix_alignment"] == "MISMATCH"]
    check("sole_mismatch_exact", len(mismatches) == 1 and mismatches[0]["surface"] == "arary" and mismatches[0]["component_recipe"] == "P+AR+AR", "sole mismatch is arary P+AR+AR")
    check("sole_mismatch_explained", mismatches[0]["mismatch_disposition"] == "EXPLAINED_EXACT_PACKAGE", "mismatch has bounded package disposition")

    check("package_row_count", len(packages) == 2, "two exact package surfaces")
    check("package_surface_set", {row["surface"] for row in packages} == {"arary", "parar"}, "arary and parar")
    check("package_page_set", {row["physical_page"] for row in packages} == {"f71v", "f72r"}, "package replicated on two pages")
    check("package_recipe_invariant", {row["component_recipe"] for row in packages} == {"P+AR+AR"}, "same exact package recipe")
    check(
        "package_two_ar_peers",
        all(
            row["action_head"] == "P"
            and row["ar_attachment_count"] == "2"
            and row["focus_atom_ordinals"] == "2|3"
            and row["duplicate_modes"] == "FREE_PLURAL_OR_REPEAT"
            and set(row["duplicate_roles"].split("|")) == {"FREE_PEER_1", "FREE_PEER_2"}
            for row in packages
        ),
        "both exact cards have two AR peers attached to P",
    )
    package_event_ids = {row["global_running_event_id"] for row in packages}
    check("package_attachment_source_count", sum(row["global_running_event_id"] in package_event_ids and row["focus_core"] == "AR" for row in attachments) == 4, "four source AR attachments")

    check("target_count", len(targets) == 2, "two promoted labels")
    check("target_surface_set", {row["surface"] for row in targets} == {"arom", "arody"}, "exact two ar residuals")
    check(
        "target_defaults",
        {row["surface"]: row["new_default_de"] for row in targets}
        == {"arom": "AUSGANG · [STERNSTELLENNAME:om]", "arody": "AUSGANG · [DROGENNAME:ody]"},
        "bounded new defaults",
    )

    check("revised_label_count", len(labels) == 107, "107 revised labels")
    check("source_order_exact", [row["source_event_id"] for row in labels] == [row["source_event_id"] for row in source] and [row["surface"] for row in labels] == [row["surface"] for row in source], "source order and surfaces unchanged")
    check(
        "source_bindings_exact",
        all(
            tuple(new[key] for key in ("physical_page", "register", "locus", "owner_de", "content_class", "image_object_id", "review_image_sha256"))
            == tuple(old[key] for key in ("physical_page", "register", "locus", "owner_de", "content_class", "image_object_id", "review_image_sha256"))
            for new, old in zip(labels, source)
        ),
        "page/register/locus/owner/content/image retained",
    )
    changed = [row for row in labels if row["gdt462_change"] != "UNCHANGED"]
    check("changed_exact_two", len(changed) == 2 and {row["surface"] for row in changed} == {"arom", "arody"}, "only two source rows change")
    unchanged_exact = all(
        new["gdt462_hybrid_status"] == old["revised_hybrid_status"]
        and new["prefix_stem"] == old["prefix_stem"]
        and new["prefix_recipe"] == old["prefix_recipe"]
        and new["ordered_function_recipe_trace"] == old["ordered_function_recipe_trace"]
        and new["revised_short_default_de"] == old["revised_short_default_de"]
        and new["known_function_character_count"] == old["known_function_character_count"]
        for new, old in zip(labels, source)
        if new["gdt462_change"] == "UNCHANGED"
    )
    check("unchanged_rows_exact", unchanged_exact, "105 rows retain function/status/default fields")
    check(
        "changed_fields_valid",
        all(
            row["prefix_stem"] == "ar"
            and row["prefix_recipe"] == "AR"
            and row["ordered_function_recipe_trace"] == "AR"
            and row["gdt462_hybrid_status"] == "FUNCTION_SHELL_PLUS_LEARNED_CORE"
            and row["known_function_character_count"] == "2"
            for row in changed
        ),
        "two rows gain only ar prefix",
    )
    status_counts = Counter(row["gdt462_hybrid_status"] for row in labels)
    check("status_counts", dict(status_counts) == EXPECTED_STATUS, f"observed={dict(status_counts)}")
    check(
        "remaining_whole_set",
        {row["surface"] for row in labels if row["gdt462_hybrid_status"] == "WHOLE_LEARNED_LABEL"}
        == {"oiil", "ofaom", "chdaiirdainy", "ofchdamy", "opoiiinoin", "opoeey", "of", "ykyd", "ykocfhy", "yddy", "korainy"},
        "exact eleven whole labels remain",
    )
    check("known_character_count", sum(int(row["known_function_character_count"]) for row in labels) == 395, "395/713 function characters")
    check("surface_character_count", sum(int(row["surface_character_count"]) for row in labels) == 713, "713 source characters")
    check("function_label_count", sum(int(row["known_function_character_count"]) > 0 for row in labels) == 95, "95 labels with function")
    check("structure_label_count", sum(int(row["known_function_character_count"]) > 0 or row["owner_family_stem_trace"] != "NONE" for row in labels) == 96, "96 labels with any structure")
    check("page_count", len(pages) == 6 and {row["physical_page"] for row in pages} == {"f17r", "f71v", "f72r", "f77r", "f88v", "f89r"}, "six admitted pages only")
    check("page_totals", sum(int(row["label_count"]) for row in pages) == 107 and sum(int(row["function_shell_plus_core_count"]) for row in pages) == 83 and sum(int(row["whole_learned_label_count"]) for row in pages) == 11 and sum(int(row["gdt462_promoted_ar_prefix_count"]) for row in pages) == 2 and sum(int(row["known_function_character_count"]) for row in pages) == 395, "page summary reconciles")

    check("result_status", result["status"] == "NEAR_THRESHOLD_AR_PREFIX_PROMOTED_BY_EXACT_REPEATED_RELATION_PACKAGE", result["status"])
    check(
        "result_counts",
        result["source_label_count"] == 107
        and result["source_whole_label_count"] == 13
        and result["residual_edge_channel_inventory_count"] == 11
        and result["near_threshold_channel_count"] == 1
        and result["promoted_channel_count"] == 1
        and result["ar_running_extension_type_count"] == 7
        and result["ar_running_matching_type_count"] == 6
        and result["ar_running_mismatch_type_count"] == 1
        and result["ar_explained_mismatch_type_count"] == 1
        and result["repeated_relation_package_surface_count"] == 2
        and result["promoted_residual_label_count"] == 2
        and result["revised_hybrid_status_counts"] == EXPECTED_STATUS
        and result["remaining_whole_label_count"] == 11
        and result["labels_with_any_function_count"] == 95
        and result["labels_with_any_structure_count"] == 96
        and result["known_function_character_count"] == 395
        and result["surface_character_count"] == 713
        and result["known_function_character_fraction"] == "0.553997",
        "result JSON reconciles",
    )
    check("claim_ceiling_zeroes", all(result[key] == 0 for key in ("core_meaning_revisions", "new_pages", "surface_predictions", "confirmed_lexemes")), "no meaning revision, page, generated surface or lexeme")
    generated = (INVENTORY_PATH, EXTENSION_PATH, PACKAGE_PATH, TARGET_PATH, LABEL_PATH, PAGE_PATH, RESULT_PATH)
    serialized = "\n".join(path.read_text(encoding="utf-8") for path in generated)
    check("sealed_pages_absent", "f84" not in serialized.lower(), "no sealed folio token")
    check("artifact_size_gate", all(path.stat().st_size < 5_000_000 for path in generated), "all artifacts below 5 MB")
    before = {path: path.read_bytes() for path in generated}
    completed = subprocess.run([sys.executable, str(RUN_SCRIPT)], cwd=ROOT, check=False, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in generated}
    check("deterministic_rebuild_exit", completed.returncode == 0, f"returncode={completed.returncode}")
    check("deterministic_rebuild_bytes", before == after, "all generated artifacts byte-identical")

    passed = sum(bool(row["passed"]) for row in checks)
    validation = {"status": "PASS" if passed == len(checks) else "FAIL", "checks_passed": passed, "checks_total": len(checks), "checks": checks}
    VALIDATION_PATH.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
