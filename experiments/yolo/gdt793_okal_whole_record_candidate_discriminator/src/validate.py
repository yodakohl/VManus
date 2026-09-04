#!/usr/bin/env python3
"""Validate GDT793, including two byte-identical guarded builder replays."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt793_okal_whole_record_candidate_discriminator"
ART = BASE / "artifacts"
SRC = BASE / "src"
RUN = SRC / "run.py"
LOCK = SRC / "SOURCE_LOCK.tsv"
OUTPUT_NAMES = (
    "GDT793_41_OKAL_PREFIX_FAMILY_OCCURRENCE_ATLAS.tsv",
    "GDT793_17_RUNNING_WHOLE_CONTEXTS.tsv",
    "GDT793_15_LOCAL_COMPONENT_POSITION_ATLAS.tsv",
    "GDT793_3_TARGET_MASKED_OWNER_FINGERPRINTS.tsv",
    "GDT793_3_MEMBER_IDENTIFIABILITY_CASES.tsv",
    "GDT793_ORDERED_ARRAY_DIAGNOSTICS.tsv",
    "GDT793_5_OUTER_SLOT4_SERIES.tsv",
    "GDT793_UPPER_ZONE_SENSITIVITY.tsv",
    "GDT793_CANDIDATE_ADJUDICATION.tsv",
    "GDT793_20_EXACT_OKAL_WORKING_RENDERER.tsv",
    "GDT793_GUARDED_SOURCE_STATS.tsv",
    "RESULT.json",
)
REQUIRED_LOCK_PATHS = {
    "experiments/yolo/gdt793_okal_whole_record_candidate_discriminator/PREREGISTRATION.md",
    "experiments/yolo/gdt793_okal_whole_record_candidate_discriminator/METHOD.md",
    "experiments/yolo/gdt793_okal_whole_record_candidate_discriminator/src/OWNER_FINGERPRINT_CASES.tsv",
    "experiments/yolo/gdt793_okal_whole_record_candidate_discriminator/src/CANDIDATE_MODEL_SPECS.tsv",
    "experiments/yolo/gdt793_okal_whole_record_candidate_discriminator/src/run.py",
    "experiments/yolo/gdt793_okal_whole_record_candidate_discriminator/src/validate.py",
    "experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv",
    "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv",
    "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv",
    "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_744_local_card_hosts.tsv",
    "experiments/yolo/gdt790_panel_owner_image_grammar_overlay/artifacts/GDT790_27_LABEL_OWNER_ATLAS.tsv",
    "experiments/yolo/gdt790_panel_owner_image_grammar_overlay/artifacts/GDT790_13_PANEL_RECORD_BINDINGS.tsv",
    "experiments/yolo/gdt792_target_masked_image_form_host_transfer/artifacts/GDT792_20_OKAL_EXACT_SCOPE_STRUCTURAL_OVERLAY.tsv",
    "experiments/semantic_assumptions/results/special_circle_text_blind_array_inventory.tsv",
    "transcription/voynich_cross_transcription_lines.tsv",
    "vmanus-exp",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: bool, label: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(label)


def main() -> int:
    audit = Audit()
    audit.check(LOCK.is_file(), "source lock exists")
    if LOCK.is_file():
        lock_rows = read_tsv(LOCK)
        audit.check({row["path"] for row in lock_rows} == REQUIRED_LOCK_PATHS, "source lock exact path set")
        audit.check(len({row["path"] for row in lock_rows}) == len(lock_rows), "source lock unique")
        for row in lock_rows:
            relative = Path(row["path"])
            audit.check(not relative.is_absolute() and ".." not in relative.parts, f"contained lock path {row['path']}")
            path = ROOT / relative
            audit.check(path.is_file(), f"locked source exists {row['path']}")
            if path.is_file():
                audit.check(sha256(path) == row["sha256"], f"locked source hash {row['path']}")

    for name in OUTPUT_NAMES:
        audit.check((ART / name).is_file(), f"artifact exists {name}")
    if audit.failures:
        payload = {"status": "FAIL", "checks": audit.checks, "failures": audit.failures}
        (ART / "VALIDATION.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 1

    for replay_index in (1, 2):
        with tempfile.TemporaryDirectory(prefix=f".gdt793_replay_{replay_index}_", dir=BASE) as tmp:
            completed = subprocess.run(
                [sys.executable, str(RUN), "--output-dir", tmp], cwd=ROOT,
                text=True, capture_output=True, check=False,
            )
            audit.check(completed.returncode == 0, f"builder replay {replay_index} exits zero")
            audit.check(completed.stdout.startswith("PARTIAL__41_OKAL_PREFIX_OCCURRENCES"), f"builder replay {replay_index} status")
            for name in OUTPUT_NAMES:
                replay = Path(tmp) / name
                audit.check(replay.is_file(), f"replay {replay_index} artifact {name}")
                if replay.is_file():
                    audit.check(replay.read_bytes() == (ART / name).read_bytes(), f"byte replay {replay_index} {name}")

    occurrence = read_tsv(ART / OUTPUT_NAMES[0])
    contexts = read_tsv(ART / OUTPUT_NAMES[1])
    local = read_tsv(ART / OUTPUT_NAMES[2])
    fingerprints = read_tsv(ART / OUTPUT_NAMES[3])
    members = read_tsv(ART / OUTPUT_NAMES[4])
    order = read_tsv(ART / OUTPUT_NAMES[5])
    slot4 = read_tsv(ART / OUTPUT_NAMES[6])
    upper = read_tsv(ART / OUTPUT_NAMES[7])
    candidates = read_tsv(ART / OUTPUT_NAMES[8])
    renderer = read_tsv(ART / OUTPUT_NAMES[9])
    guards = read_tsv(ART / OUTPUT_NAMES[10])
    result = json.loads((ART / OUTPUT_NAMES[11]).read_text(encoding="utf-8"))

    audit.check(len(occurrence) == 41, "41 prefix-family occurrences")
    audit.check(len({row["occurrence_id"] for row in occurrence}) == 41, "occurrence IDs unique")
    audit.check(Counter(row["occurrence_kind"] for row in occurrence) == Counter({"RUNNING_EVENT": 26, "LOCAL_ADDRESS_OR_LABEL": 15}), "26/15 scope split")
    audit.check(len({row["surface"] for row in occurrence}) == 14, "14 complete prefix forms")
    audit.check(sum(row["surface"] == "okal" for row in occurrence) == 20, "20 exact okal occurrences")
    audit.check(sum(row["surface"] == "okal" and row["occurrence_kind"] == "RUNNING_EVENT" for row in occurrence) == 16, "16 exact running")
    audit.check(sum(row["surface"] == "okal" and row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL" for row in occurrence) == 4, "four exact local")
    audit.check(all(row["family_definition"] == "COMPLETE_ZL3B_SURFACE_STARTS_WITH_OKAL" for row in occurrence), "literal family definition")
    audit.check(all(row["component_export_credit"] == "ZERO" for row in occurrence), "occurrence component ceiling")
    audit.check(not any(row["physical_page"].startswith("f84") or row["source_selector"].startswith("f84") for row in occurrence), "no sealed occurrence")

    audit.check(len(contexts) == 17 and len({row["paragraph_id"] for row in contexts}) == 17, "17 whole contexts")
    audit.check(sum(int(row["family_occurrence_count"]) for row in contexts) == 26, "contexts cover 26 running occurrences")
    audit.check(sum(int(row["exact_okal_occurrence_count"]) for row in contexts) == 16, "contexts cover 16 exact okal")
    audit.check(all(row["translation_status"] == "UNTRANSLATED__TARGET_CANDIDATE_ONLY" for row in contexts), "contexts are not fake translations")
    audit.check(sum(row["page_local_family_label_count"] == "0" for row in contexts) >= 10, "most contexts lack local family labels")

    audit.check(len(local) == 15 and len({row["occurrence_id"] for row in local}) == 15, "15 unique local family labels")
    audit.check(Counter(row["visual_source"] for row in local) == Counter({"SPECIAL_CIRCLE_TEXT_BLIND_ARRAY": 12, "GDT790_DEEP_PANEL_COMPONENT": 2, "GDT581_LOCAL_MATERIAL_OWNER": 1}), "local visual-source split")
    audit.check(Counter(row["alternate_reader_status"] for row in local) == Counter({"ALL_THREE_EXACT_WHOLE": 11, "ONE_ALTERNATE_DIFFERS": 1, "BOTH_ALTERNATES_DIFFER": 3}), "local alternate-reader status")
    audit.check(all(row["alternate_reader_credit"] == "SAME_MANUSCRIPT_READING_ONLY" for row in local), "reader evidence is nonindependent")
    audit.check(all(row["component_export_credit"] == "ZERO" for row in local), "local component ceiling")

    audit.check(len(fingerprints) == 3, "three target-masked owner cases")
    audit.check(all(row["source_owner_recovered"] == "NO" for row in fingerprints), "zero source-owner recoveries")
    audit.check(all(row["target_masked_source_overlap"] == "NONE" and row["target_masked_source_score"] == "0.000000" for row in fingerprints), "all source fingerprints vanish after mask")
    audit.check(fingerprints[0]["unmasked_source_overlap"] == "okal|okaly", "f72 evidence is only target-family self-reuse")
    audit.check(Counter(row["unmasked_source_overlap"] for row in fingerprints) == Counter({"okal": 2, "okal|okaly": 1}), "unmasked overlap census")

    audit.check(len(members) == 3, "three member cases")
    audit.check(Counter(row["single_member_forced_in_every_assignment"] for row in members) == Counter({"YES": 2, "NO": 1}), "two of three member cases forced")
    f72_member = next(row for row in members if row["case_id"] == "F72_RING_E_TO_D")
    audit.check(f72_member["maximum_exact_member_assignments"] == "4" and f72_member["member_model_result"].startswith("FAIL"), "f72 has four ambiguous mappings")
    audit.check(f72_member["label_member_counts"] == "okal:2|okaly:2", "f72 two duplicate label forms")

    audit.check(len(order) == 10, "ten local owner-array diagnostics")
    f72_order = next(row for row in order if row["visible_owner_id"] == "SCARR029|f72r2|S1")
    audit.check(f72_order["ordered_positions"] == "2:okalar|3:okal|4:okaly|5:okal|12:okaly", "f72 visible family order")
    audit.check(f72_order["same_surface_collision_forms"] == "okal|okaly", "f72 collision forms")
    audit.check(f72_order["bidirectional_constraint_pairs"] == "okal<>okaly" and f72_order["strict_ordinal_status"].startswith("FAIL"), "f72 strict ordinal cycle")
    f82_order = next(row for row in order if row["visible_owner_id"] == "F82_BOTTOM_COMMUNAL")
    audit.check(f82_order["ordered_positions"] == "2:okal|3:okaldy" and f82_order["strict_ordinal_status"].startswith("ORDERABLE_SINGLE"), "f82 pair alone has no transfer key")

    audit.check(len(slot4) == 5, "five homologous outer-slot rows")
    audit.check(Counter(row["okal_prefix_family"] for row in slot4) == Counter({"YES": 4, "NO": 1}), "four of five slot4 family hits")
    audit.check([row["surface"] for row in slot4] == ["okalal", "okala", "okalam", "okaly", "oraiinam"], "slot4 surface series")
    audit.check(all(row["interpretation"].endswith("NOT_NUMBER_FOUR") for row in slot4), "slot4 is not translated as four")

    audit.check(len(upper) == 5, "five upper-zone windows")
    audit.check(all(row["timed_local_label_population"] == "158" and row["exact_okal_timed_count"] == "3" for row in upper), "upper-zone capacity")
    window15 = next(row for row in upper if row["half_width_hours_around_twelve"] == "1.5")
    audit.check((window15["population_window_hits"], window15["exact_okal_window_hits"], window15["unadjusted_all_hit_probability"]) == ("58", "3", "0.047842"), "posthoc ±1.5h diagnostic")
    audit.check(all(row["held_f82_exact_okal_top_row"] == "YES" and row["status"].startswith("POSTHOC") for row in upper), "upper-zone stays posthoc")

    audit.check(len(candidates) == 7 and len({row["model_id"] for row in candidates}) == 7, "seven distinct candidates")
    selected = [row for row in candidates if row["renderer_license"] != "NO"]
    audit.check(len(selected) == 1 and selected[0]["model_id"] == "CLASS_SLOT_ENTRY_CODE", "only class/slot C0 renderer selected")
    audit.check(selected[0]["gate_result"] == "PASS" and selected[0]["confidence"] == "C0_SELECTED_WORKING", "selected C0 gate")
    audit.check(next(row for row in candidates if row["model_id"] == "PAGE_LOCAL_ADDRESS")["gate_result"] == "FAIL", "address fails")
    audit.check(next(row for row in candidates if row["model_id"] == "UNIQUE_MEMBER_OR_NAME")["gate_result"] == "FAIL", "member/name fails")
    audit.check(next(row for row in candidates if row["model_id"] == "STRICT_NUMBER_OR_ORDINAL")["gate_result"] == "FAIL", "strict ordinal fails")
    audit.check(next(row for row in candidates if row["model_id"] == "OPAQUE_PRODUCTIVE_RENDERER")["gate_result"] == "SURVIVES", "opaque null survives")
    audit.check(all(row["component_export_credit"] == "ZERO" for row in candidates), "candidate component ceiling")

    audit.check(len(renderer) == 20 and len({row["occurrence_id"] for row in renderer}) == 20, "20 exact renderer rows")
    audit.check(Counter(row["occurrence_kind"] for row in renderer) == Counter({"RUNNING_EVENT": 16, "LOCAL_ADDRESS_OR_LABEL": 4}), "renderer 16/4 split")
    audit.check(all(row["surface"] == "okal" and row["selected_working_role"] == "SYSTEM_ENTRY_CLASS_CODE" for row in renderer), "renderer exact whole only")
    audit.check(all(row["previous_structural_display"] == "⟦okal:CROSS_SCOPE_LABEL_PROSE_WHOLE⟧" for row in renderer), "renderer supersedes exact GDT792 structural tag")
    audit.check(all(row["working_display"].startswith("⟦okal:") and "Systemeintragscode" in row["working_display"] for row in renderer), "working display is informative and scoped")
    audit.check(all(row["semantic_confidence"] == "C0_SELECTED_WORKING_NOT_PLAINTEXT" and row["lexeme_confirmed"] == "NO" and row["component_export_credit"] == "ZERO" for row in renderer), "renderer claim ceiling")

    audit.check(len(guards) == 1 and guards[0]["selected_rows"] == "1007", "guarded crosswalk scope")
    audit.check((guards[0]["selector_count"], guards[0]["physical_page_count"]) == ("35", "30"), "35 selectors and 30 pages")
    audit.check(guards[0]["skipped_forbidden_rows"] == "98" and guards[0]["materialized_f84_rows"] == guards[0]["materialized_f84r_rows"] == "0", "98 sealed rows rejected before materialization")
    audit.check(guards[0]["scratch_raw_scan_values_used"].startswith("NO__EXCLUDED"), "scratch scan values excluded")

    audit.check(result["experiment_id"] == "GDT793" and result["status"].startswith("PARTIAL__41_OKAL_PREFIX_OCCURRENCES"), "result identity/status")
    audit.check(result["counts"] == {
        "component_exports": 0,
        "confirmed_lexemes": 0,
        "exact_okal_local": 4,
        "exact_okal_renderer_patches": 20,
        "exact_okal_running": 16,
        "exact_running_without_same_page_exact_label": 13,
        "f72_distinct_collision_forms": 2,
        "family_running_without_same_page_family_label": 18,
        "local_topologies": 3,
        "member_cases_forced": 2,
        "outer_slot4_okal_family_hits": 4,
        "prefix_family_forms": 14,
        "prefix_family_local": 15,
        "prefix_family_occurrences": 41,
        "prefix_family_running": 26,
        "running_contexts": 17,
        "target_masked_owner_recoveries": 0,
    }, "result exact counts")
    audit.check(result["decision"]["selected_working_model"] == "CLASS_SLOT_ENTRY_CODE", "result selects class/slot model")
    audit.check(result["decision"]["opaque_renderer"].startswith("SURVIVES"), "result retains opaque null")
    audit.check(result["scope"] == {"new_pages_or_images_opened": 0, "released_physical_pages": 30, "sealed_rows_materialized": 0, "source_selectors": 35}, "result scope")
    audit.check(result["scratch_source_incident"]["raw_scan_values_retained_or_used"] == 0 and result["scratch_source_incident"]["sealed_rows_displayed"] == 0, "incident repaired without retained values")

    payload = {
        "status": "PASS" if not audit.failures else "FAIL",
        "checks": audit.checks,
        "failures": audit.failures,
        "builder_byte_replay": not any(item.startswith("byte replay") for item in audit.failures),
        "sealed_rows_materialized": 0,
    }
    (ART / "VALIDATION.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, indent=2))
    return 0 if not audit.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
