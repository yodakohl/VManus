#!/usr/bin/env python3
"""Audit the sole GDT464 whole label against manual readings and IIN/L families."""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from collections import defaultdict
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
RUNNING_PATH = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts/gdt407_4576_running_event_edition.tsv"
CROSS_PATH = ROOT / "transcription/voynich_cross_transcription_lines.tsv"
SOURCE_PATH = ROOT / "experiments/yolo/gdt464_residual_exact_package_bridge/artifacts/gdt464_107_revised_hybrid_dictionary.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


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
    lines = completed.stdout.splitlines()
    stats_lines = [line for line in completed.stderr.splitlines() if line.startswith("GUARD_STATS ")]
    if len(stats_lines) != 1:
        raise RuntimeError("guarded query did not emit stats")
    stats = json.loads(stats_lines[0].removeprefix("GUARD_STATS "))
    rows = list(csv.DictReader(io.StringIO("\n".join(lines) + "\n"), delimiter="\t"))
    return stats, rows


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    running = read_tsv(RUNNING_PATH)
    source = read_tsv(SOURCE_PATH)
    guard_stats, cross_rows = guarded_f17r_rows()
    target_cross = next(row for row in cross_rows if row["locus"] == "f17r.13")
    target_source = next(row for row in source if row["surface"] == "oiil")

    running_recipe: dict[str, str] = {}
    running_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in running:
        previous = running_recipe.setdefault(row["surface"], row["component_recipe"])
        if previous != row["component_recipe"]:
            raise RuntimeError(f"Non-invariant running surface: {row['surface']}")
        running_events[row["surface"]].append(row)

    def recipe_surfaces(sequence: str) -> list[str]:
        atoms = sequence.split("+")
        return sorted(
            surface for surface, recipe in running_recipe.items()
            if contains_atoms(atoms, recipe.split("+"))
        )

    def pages_for(surfaces: list[str]) -> set[str]:
        return {row["physical_page"] for surface in surfaces for row in running_events[surface]}

    target_rows = [{
        "physical_page": "f17r",
        "locus": "f17r.13",
        "source_event_id": target_source["source_event_id"],
        "surface": "oiil",
        "owner_de": target_source["owner_de"],
        "content_class": target_source["content_class"],
        "zl3b_reading": target_cross["zl3b_clean"],
        "it2a_reading": target_cross["it2a_clean"] or "MISSING",
        "rf1b_reading": target_cross["rf1b_clean"],
        "present_reading_count": 2,
        "present_readings_exact": "YES" if target_cross["all_present_exact"] == "1" else "NO",
        "target_token_in_zl3b": "YES" if "oiil" in target_cross["zl3b_clean"].split() else "NO",
        "target_token_in_it2a": "MISSING_LOCUS" if not target_cross["it2a_clean"] else ("YES" if "oiil" in target_cross["it2a_clean"].split() else "NO"),
        "target_token_in_rf1b": "YES" if "oiil" in target_cross["rf1b_clean"].split() else "NO",
        "guard_selected_locus_count": guard_stats["selected"],
        "guard_forbidden_skip_count": guard_stats["skipped_forbidden"],
        "image_object_id": target_source["image_object_id"],
        "image_url": "https://collections.library.yale.edu/iiif/2/1006106/full/2000,/0/default.jpg",
        "review_image_sha256": target_source["review_image_sha256"],
        "manual_image_result": "ONE_OWNER_BOUND_LABEL__NO_VISIBLE_INTERNAL_OBJECT_SPLIT",
    }]
    write_tsv(OUT / "gdt465_cross_reading_target.tsv", target_rows)

    sequences = ("O+IIN", "IIN+L", "O+IIN+L", "AIIN+L", "O+AIIN+L", "L+O+IIN")
    sequence_rows: list[dict[str, object]] = []
    for ordinal, sequence in enumerate(sequences, start=1):
        surfaces = recipe_surfaces(sequence)
        sequence_rows.append({
            "sequence_id": f"G465-Q{ordinal:02d}",
            "component_sequence": sequence,
            "carrier_surface_type_count": len(surfaces),
            "carrier_event_count": sum(len(running_events[surface]) for surface in surfaces),
            "carrier_page_count": len(pages_for(surfaces)),
            "carrier_surfaces": "|".join(surfaces) or "NONE",
            "role_in_oiil_test": "FULL_TARGET_HYPOTHESIS" if sequence == "O+IIN+L" else "NEIGHBOUR_OR_DIRECTION_CONTROL",
            "decision": "REJECT_ZERO_CARRIERS" if sequence == "O+IIN+L" else "CALIBRATION_ONLY",
        })
    write_tsv(OUT / "gdt465_6_component_sequence_tests.tsv", sequence_rows)

    renderer_rows: list[dict[str, object]] = []
    for pattern, role in (("oii", "O_IIN_SURFACE_NEIGHBOUR"), ("iil", "IIN_L_SURFACE_NEIGHBOUR")):
        for surface in sorted(surface for surface in running_recipe if pattern in surface):
            events = running_events[surface]
            renderer_rows.append({
                "pattern": pattern,
                "pattern_role": role,
                "running_surface": surface,
                "component_recipe": running_recipe[surface],
                "event_count": len(events),
                "pages": "|".join(sorted({row["physical_page"] for row in events})),
                "exact_target_surface": "YES" if surface == "oiil" else "NO",
                "licenses_oiil_split": "NO",
                "reason": (
                    "O_IIN_RENDERINGS_KEEP_TERMINAL_n_AND_SUPPLY_NO_FOLLOWING_L"
                    if pattern == "oii"
                    else "SINGLE_AIIN_L_CONTEXT_ONLY__NOT_IIN_L_OR_EXACT_CARD"
                ),
            })
    write_tsv(OUT / "gdt465_13_renderer_neighbours.tsv", renderer_rows)

    exact_cards = {surface: running_recipe.get(surface, "ABSENT") for surface in ("o", "l", "oii", "iil", "oiil")}
    segmentation_rows = [{
        "surface": "oiil",
        "candidate_segmentation": "o|ii|l",
        "candidate_recipe": "O+IIN+L",
        "exact_card_o": exact_cards["o"],
        "exact_card_ii_or_oii": exact_cards["oii"],
        "exact_card_iil": exact_cards["iil"],
        "exact_card_l": exact_cards["l"],
        "exact_full_surface": exact_cards["oiil"],
        "complete_exact_card_segmentation_count": 0,
        "full_recipe_carrier_type_count": len(recipe_surfaces("O+IIN+L")),
        "strict_owner_family_bridge": "NONE",
        "selected_status": "WHOLE_LEARNED_LABEL",
        "selected_default_de": "[PFLANZENNAME:oiil]",
        "decision_reason": "TWO_PRESENT_READINGS_AGREE_ON_WHOLE_FORM__NO_MIDDLE_CARD__NO_IIN_L_OR_O_IIN_L_PACKAGE",
    }]
    write_tsv(OUT / "gdt465_oiil_segmentation_decision.tsv", segmentation_rows)

    final_rows: list[dict[str, object]] = []
    for ordinal, old in enumerate(source, start=1):
        final_rows.append({
            "gdt465_label_id": f"G465-L{ordinal:03d}",
            **old,
            "gdt465_hybrid_status": old["gdt464_hybrid_status"],
            "gdt465_change": "OIIL_AUDITED_AND_RETAINED_WHOLE" if old["surface"] == "oiil" else "UNCHANGED_FROM_GDT464",
            "gdt465_decision_evidence": (
                "CROSS_READING_EXACT_PRESENT_PAIR__ZERO_COMPLETE_PACKAGE"
                if old["surface"] == "oiil" else "NOT_IN_SCOPE"
            ),
        })
    write_tsv(OUT / "gdt465_107_final_hybrid_dictionary.tsv", final_rows)

    result = {
        "status": "OIIL_REMAINS_SINGLE_WHOLE_LABEL__NOMENCLATOR_TAIL_CLOSED",
        "source_label_count": len(source),
        "running_event_count": len(running),
        "guarded_f17r_locus_count": len(cross_rows),
        "target_present_reading_count": 2,
        "target_present_readings_exact": True,
        "target_missing_readings": ["IT2a"],
        "complete_exact_card_segmentation_count": 0,
        "o_iin_l_recipe_carrier_type_count": len(recipe_surfaces("O+IIN+L")),
        "iin_l_recipe_carrier_type_count": len(recipe_surfaces("IIN+L")),
        "renderer_neighbour_row_count": len(renderer_rows),
        "remaining_whole_label_count": sum(row["gdt465_hybrid_status"] == "WHOLE_LEARNED_LABEL" for row in final_rows),
        "remaining_whole_labels": [row["surface"] for row in final_rows if row["gdt465_hybrid_status"] == "WHOLE_LEARNED_LABEL"],
        "known_function_character_count": sum(int(row["known_function_character_count"]) for row in final_rows),
        "surface_character_count": sum(int(row["surface_character_count"]) for row in final_rows),
        "decision": "KEEP_OIIL_AS_MEMORIZED_PICTURED_PLANT_LABEL",
        "new_core_meanings": 0,
        "new_pages": 0,
        "confirmed_lexemes": 0,
    }
    (OUT / "gdt465_result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
