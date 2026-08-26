#!/usr/bin/env python3
"""Validate the GDT460 hybrid edge-stem / learned-core atlas."""

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
BASE = ROOT / "experiments/yolo/gdt460_learned_label_edge_stem_atlas"
OUT = BASE / "artifacts"
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
SOURCE_PATH = ROOT / "experiments/yolo/gdt459_local_nomenclator_content_atlas/artifacts/gdt459_183_address_interlinear.tsv"
RUN_SCRIPT = BASE / "src/run.py"

EDGE_PATH = OUT / "gdt460_27_calibrated_edge_stems.tsv"
FAMILY_PATH = OUT / "gdt460_17_owner_class_family_stems.tsv"
LABEL_PATH = OUT / "gdt460_107_hybrid_label_dictionary.tsv"
PAGE_PATH = OUT / "gdt460_6_page_summary.tsv"
RESULT_PATH = OUT / "gdt460_result.json"
VALIDATION_PATH = OUT / "gdt460_validation.json"

EXPECTED_STATUS = {
    "FULL_EDGE_FORMULA": 5,
    "FUNCTION_EDGE_PLUS_LEARNED_CORE": 78,
    "OWNER_FAMILY_STEM_ONLY": 5,
    "WHOLE_LEARNED_LABEL": 19,
}
EXPECTED_FAMILY_STEMS = {
    "otora", "arar", "dara", "ala", "tal", "raii", "kar", "ota", "pa",
    "raiin", "alar", "kara", "okar", "opal", "otal", "otch", "sho",
}
EXPECTED_FULL = {"alcphy", "otalaiin", "otolam", "alaly", "otolaiin"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def main() -> int:
    checks: list[dict[str, object]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append({"name": name, "passed": bool(condition), "detail": detail})

    running = read_tsv(RUNNING_PATH)
    source = [row for row in read_tsv(SOURCE_PATH) if row["decision_tier"] == "D_OWNER_LEARNED_WHOLE_LABEL"]
    edges = read_tsv(EDGE_PATH)
    families = read_tsv(FAMILY_PATH)
    labels = read_tsv(LABEL_PATH)
    pages = read_tsv(PAGE_PATH)
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))

    check("source_label_count", len(source) == 107, f"observed={len(source)} expected=107")
    check("source_label_surfaces_unique", len({row["surface"] for row in source}) == 107, "107 singleton source surfaces")
    check("edge_channel_count", len(edges) == 27, f"observed={len(edges)} expected=27")
    check("edge_direction_counts", Counter(row["edge"] for row in edges) == {"PREFIX": 8, "SUFFIX": 19}, str(Counter(row["edge"] for row in edges)))
    check("family_stem_count", len(families) == 17, f"observed={len(families)} expected=17")
    check("family_stem_set", {row["surface_substring"] for row in families} == EXPECTED_FAMILY_STEMS, "exact 17 replicated family stems")
    check("label_output_count", len(labels) == 107, f"observed={len(labels)} expected=107")
    check("page_output_count", len(pages) == 6, f"observed={len(pages)} expected=6")
    check(
        "source_order_exact",
        [row["source_event_id"] for row in labels] == [row["source_event_id"] for row in source]
        and [row["surface"] for row in labels] == [row["surface"] for row in source],
        "all 107 source labels retained in order",
    )
    check(
        "source_bindings_exact",
        all(
            tuple(row[key] for key in ("physical_page", "register", "locus", "owner_de", "content_class", "image_object_id", "review_image_sha256"))
            == tuple(source_row[key] for key in ("physical_page", "register", "locus", "owner_de", "content_class", "image_object_id", "review_image_sha256"))
            for row, source_row in zip(labels, source)
        ),
        "page/register/locus/owner/content/image bindings retained",
    )

    running_recipe: dict[str, str] = {}
    running_rows: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in running:
        running_recipe.setdefault(row["surface"], row["component_recipe"])
        running_rows[row["surface"]].append(row)
    check("running_surface_invariance", all(len({row["component_recipe"] for row in rows}) == 1 for rows in running_rows.values()), "one recipe per running surface")

    edge_index = {(row["edge"], row["surface_stem"]): row for row in edges}
    check("edge_keys_unique", len(edge_index) == 27, "27 unique edge/stem channels")
    edge_recomputed = True
    for row in edges:
        stem = row["surface_stem"]
        recipe = row["component_recipe"]
        atoms = recipe.split("+")
        if row["edge"] == "PREFIX":
            extensions = [(surface, candidate) for surface, candidate in running_recipe.items() if surface != stem and surface.startswith(stem)]
            matches = [(surface, candidate) for surface, candidate in extensions if candidate.split("+")[:len(atoms)] == atoms]
        else:
            extensions = [(surface, candidate) for surface, candidate in running_recipe.items() if surface != stem and surface.endswith(stem)]
            matches = [(surface, candidate) for surface, candidate in extensions if candidate.split("+")[-len(atoms):] == atoms]
        edge_recomputed &= (
            running_recipe.get(stem) == recipe
            and len(extensions) == int(row["running_extension_type_count"])
            and len(matches) == int(row["running_matching_type_count"])
            and f"{len(matches) / len(extensions):.6f}" == row["running_type_precision"]
            and len(extensions) >= 4
            and len(matches) / len(extensions) >= 0.90
        )
    check("edge_calibration_recomputed", edge_recomputed, "all 27 channels reproduce >=4 extension types and >=0.90 edge precision")

    family_valid = True
    family_covered: set[str] = set()
    for family in families:
        listed = family["surfaces"].split("|")
        selected = [row for row in source if family["surface_substring"] in row["surface"]]
        family_valid &= (
            len(selected) == int(family["label_count"])
            and {row["surface"] for row in selected} == set(listed)
            and len({row["content_class"] for row in selected}) == 1
            and {row["content_class"] for row in selected} == {family["content_class"]}
            and len(selected) >= 3
            and len({row["physical_page"] for row in selected}) == 2
        )
        family_covered.update(listed)
    check("family_membership_recomputed", family_valid, "every family marker has >=3 pure labels on both class pages")
    check("family_label_union", len(family_covered) == 35, f"observed={len(family_covered)} expected=35")

    prefix_rows = [row for row in edges if row["edge"] == "PREFIX"]
    suffix_rows = [row for row in edges if row["edge"] == "SUFFIX"]
    hybrid_valid = True
    known_characters = 0
    family_label_count = 0
    union_structure_count = 0
    for row in labels:
        surface = row["surface"]
        prefixes = sorted((edge for edge in prefix_rows if surface.startswith(edge["surface_stem"])), key=lambda edge: (-len(edge["surface_stem"]), edge["surface_stem"]))
        expected_prefix = prefixes[0]["surface_stem"] if prefixes else "NONE"
        prefix_length = 0 if expected_prefix == "NONE" else len(expected_prefix)
        suffixes = sorted((edge for edge in suffix_rows if surface.endswith(edge["surface_stem"]) and prefix_length + len(edge["surface_stem"]) <= len(surface)), key=lambda edge: (-len(edge["surface_stem"]), edge["surface_stem"]))
        expected_suffix = suffixes[0]["surface_stem"] if suffixes else "NONE"
        suffix_length = 0 if expected_suffix == "NONE" else len(expected_suffix)
        expected_center = surface[prefix_length:len(surface) - suffix_length if suffix_length else len(surface)] or "NONE"
        family_hit = any(family["surface_substring"] in surface for family in families)
        known = prefix_length + suffix_length
        if known == len(surface) and known > 0:
            expected_status = "FULL_EDGE_FORMULA"
        elif known > 0:
            expected_status = "FUNCTION_EDGE_PLUS_LEARNED_CORE"
        elif family_hit:
            expected_status = "OWNER_FAMILY_STEM_ONLY"
        else:
            expected_status = "WHOLE_LEARNED_LABEL"
        hybrid_valid &= (
            row["prefix_stem"] == expected_prefix
            and row["suffix_stem"] == expected_suffix
            and row["learned_center_surface"] == expected_center
            and int(row["known_edge_character_count"]) == known
            and int(row["surface_character_count"]) == len(surface)
            and row["hybrid_status"] == expected_status
        )
        known_characters += known
        family_label_count += family_hit
        union_structure_count += known > 0 or family_hit
    check("hybrid_assignment_recomputed", hybrid_valid, "longest nonoverlapping calibrated edges and status reproduced for 107 labels")
    status_counts = Counter(row["hybrid_status"] for row in labels)
    check("hybrid_status_counts", dict(status_counts) == EXPECTED_STATUS, f"observed={dict(status_counts)}")
    check("full_formula_set", {row["surface"] for row in labels if row["hybrid_status"] == "FULL_EDGE_FORMULA"} == EXPECTED_FULL, "exact five fully edge-readable labels")
    check("known_edge_label_count", sum(int(row["known_edge_character_count"]) > 0 for row in labels) == 83, "83 labels carry a calibrated functional edge")
    check("known_edge_character_count", known_characters == 277 and sum(len(row["surface"]) for row in labels) == 713, "277/713 characters assigned by calibrated edges")
    check("known_edge_fraction", f"{known_characters / 713:.6f}" == "0.388499", "edge fraction 0.388499")
    check("family_label_count", family_label_count == 35, f"observed={family_label_count} expected=35")
    check("union_structure_count", union_structure_count == 88, f"observed={union_structure_count} expected=88")
    check(
        "defaults_nonempty_concrete",
        all(row["hybrid_short_default_de"].strip() and "UNKNOWN" not in row["hybrid_short_default_de"].upper() and "EXEMPLAR" not in row["hybrid_short_default_de"].upper() for row in labels),
        "107 nonempty hybrid defaults without placeholders",
    )
    check("page_set_exact", {row["physical_page"] for row in pages} == {"f17r", "f71v", "f72r", "f77r", "f88v", "f89r"}, "six already admitted pages only")
    check(
        "page_totals_reconcile",
        sum(int(row["label_count"]) for row in pages) == 107
        and sum(int(row["labels_with_any_known_edge"]) for row in pages) == 83
        and sum(int(row["labels_with_owner_family_stem"]) for row in pages) == 35
        and sum(int(row["known_edge_character_count"]) for row in pages) == 277
        and sum(int(row["surface_character_count"]) for row in pages) == 713,
        "six page rows reconcile with full label table",
    )
    check("result_status", result["status"] == "HYBRID_FUNCTION_EDGES_AND_LEARNED_NAME_CORES", result["status"])
    check(
        "result_counts",
        result["source_learned_label_count"] == 107
        and result["source_unique_surface_count"] == 107
        and result["calibrated_edge_channel_count"] == 27
        and result["calibrated_prefix_stem_count"] == 8
        and result["calibrated_suffix_stem_count"] == 19
        and result["hybrid_status_counts"] == EXPECTED_STATUS
        and result["labels_with_known_edge_count"] == 83
        and result["replicated_owner_family_stem_count"] == 17
        and result["labels_with_owner_family_stem_count"] == 35
        and result["labels_with_any_structure_count"] == 88
        and result["fully_unstructured_whole_label_count"] == 19
        and result["known_edge_character_count"] == 277
        and result["surface_character_count"] == 713
        and result["known_edge_character_fraction"] == "0.388499",
        "result JSON reconciles with all release tables",
    )
    check("claim_ceiling_zeroes", all(result[key] == 0 for key in ("core_meaning_revisions", "new_pages", "surface_predictions", "confirmed_lexemes")), "no core revision, page, surface prediction or confirmed lexeme")
    serialized = "\n".join(path.read_text(encoding="utf-8") for path in (EDGE_PATH, FAMILY_PATH, LABEL_PATH, PAGE_PATH, RESULT_PATH))
    check("sealed_pages_absent", "f84" not in serialized.lower(), "no sealed folio token")
    check("artifact_size_gate", all(path.stat().st_size < 5_000_000 for path in (EDGE_PATH, FAMILY_PATH, LABEL_PATH, PAGE_PATH, RESULT_PATH)), "all release artifacts below 5 MB")

    generated = (EDGE_PATH, FAMILY_PATH, LABEL_PATH, PAGE_PATH, RESULT_PATH)
    before = {path: path.read_bytes() for path in generated}
    completed = subprocess.run([sys.executable, str(RUN_SCRIPT)], cwd=ROOT, check=False, capture_output=True, text=True)
    after = {path: path.read_bytes() for path in generated}
    check("deterministic_rebuild_exit", completed.returncode == 0, f"returncode={completed.returncode}")
    check("deterministic_rebuild_bytes", before == after, "all five generated artifacts byte-identical")

    passed = sum(bool(row["passed"]) for row in checks)
    validation = {
        "status": "PASS" if passed == len(checks) else "FAIL",
        "checks_passed": passed,
        "checks_total": len(checks),
        "checks": checks,
    }
    VALIDATION_PATH.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
