#!/usr/bin/env python3
"""Validate GDT792, including byte replay and relation-packet intake."""

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
BASE = ROOT / "experiments/yolo/gdt792_target_masked_image_form_host_transfer"
ART = BASE / "artifacts"
SRC = BASE / "src"
RUN = SRC / "run.py"
LOCK = SRC / "SOURCE_LOCK.tsv"
OUTPUT_NAMES = (
    "GDT792_58_TARGET_OCCURRENCE_HOST_ATLAS.tsv",
    "GDT792_4_TARGET_TRANSFER_SCORECARD.tsv",
    "GDT792_27_DECLARED_CONTROL_PROFILES.tsv",
    "GDT792_64_DETERMINISTIC_CONTROL_DECK.tsv",
    "GDT792_COMPLETE_WHOLE_CROSS_SCOPE_RANKING.tsv",
    "GDT792_CANDIDATE_GLOSS_ADJUDICATION.tsv",
    "GDT792_20_OKAL_EXACT_SCOPE_STRUCTURAL_OVERLAY.tsv",
    "GDT792_4_OKAL_SAME_PAGE_CROSS_OWNER_EDGES.tsv",
    "GDT792_GDT388_2_NEW_F72_EDGE_PACKET.tsv",
    "GDT792_GUARDED_SOURCE_STATS.tsv",
    "GDT792_24_TARGET_CONTROL_CONTRASTS.tsv",
    "RELATION_PACKET_INTAKE.json",
    "RESULT.json",
)
REQUIRED_LOCK_PATHS = {
    "experiments/yolo/gdt792_target_masked_image_form_host_transfer/PREREGISTRATION.md",
    "experiments/yolo/gdt792_target_masked_image_form_host_transfer/METHOD.md",
    "experiments/yolo/gdt792_target_masked_image_form_host_transfer/src/FORM_CONTROL_SPECS.tsv",
    "experiments/yolo/gdt792_target_masked_image_form_host_transfer/src/CANDIDATE_GLOSS_SPECS.tsv",
    "experiments/yolo/gdt792_target_masked_image_form_host_transfer/src/run.py",
    "experiments/yolo/gdt791_thirty_page_visual_owner_spine/src/PAGE_SELECTOR_SPECS.tsv",
    "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_5866_OCCURRENCE_SPINE.tsv",
    "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_1007_LINE_OWNER_ATLAS.tsv",
    "experiments/yolo/gdt791_thirty_page_visual_owner_spine/artifacts/GDT791_240_RECORD_LOCAL_STATEMENT_FRAGMENTS.tsv",
    "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_5122_content_ready_event_edition.tsv",
    "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_793_content_ready_statement_edition.tsv",
    "experiments/yolo/gdt581_grammar_content_boundary_audit/artifacts/gdt581_744_local_card_hosts.tsv",
    "experiments/yolo/gdt790_panel_owner_image_grammar_overlay/artifacts/GDT790_13_PANEL_RECORD_BINDINGS.tsv",
    "experiments/yolo/gdt790_panel_owner_image_grammar_overlay/artifacts/GDT790_27_LABEL_OWNER_ATLAS.tsv",
    "experiments/yolo/gdt790_panel_owner_image_grammar_overlay/artifacts/GDT790_10_EXACT_LABEL_PROSE_BRIDGES.tsv",
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv",
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv",
    "transcription/voynich_zl3b_lines.tsv",
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
        audit.check({row["path"] for row in lock_rows} == REQUIRED_LOCK_PATHS, "source lock has exact required path set")
        audit.check(len({row["path"] for row in lock_rows}) == len(lock_rows), "source lock paths unique")
        for row in lock_rows:
            relative = Path(row["path"])
            audit.check(not relative.is_absolute() and ".." not in relative.parts, f"locked source path is relative and contained: {row['path']}")
            path = ROOT / relative
            audit.check(path.is_file(), f"locked source exists: {row['path']}")
            if path.is_file():
                audit.check(sha256(path) == row["sha256"], f"locked source hash: {row['path']}")

    for name in OUTPUT_NAMES:
        audit.check((ART / name).is_file(), f"artifact exists: {name}")
    if audit.failures:
        payload = {"status": "FAIL", "checks": audit.checks, "failures": audit.failures}
        (ART / "VALIDATION.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(payload, indent=2))
        return 1

    # Two independent repo-local builder replays: every canonical output must
    # be byte-identical, including relation-packet intake.
    for replay_index in (1, 2):
        with tempfile.TemporaryDirectory(prefix=f".gdt792_replay_{replay_index}_", dir=BASE) as tmp:
            completed = subprocess.run(
                [sys.executable, str(RUN), "--output-dir", tmp], cwd=ROOT,
                text=True, capture_output=True, check=False,
            )
            audit.check(completed.returncode == 0, f"builder replay {replay_index} exits zero")
            audit.check(completed.stdout.startswith("PARTIAL__58_TARGET_OCCURRENCES"), f"builder replay {replay_index} status")
            for name in OUTPUT_NAMES:
                replay = Path(tmp) / name
                audit.check(replay.is_file(), f"replay {replay_index} artifact exists: {name}")
                if replay.is_file():
                    audit.check(replay.read_bytes() == (ART / name).read_bytes(), f"byte replay {replay_index}: {name}")

    target = read_tsv(ART / OUTPUT_NAMES[0])
    score = read_tsv(ART / OUTPUT_NAMES[1])
    declared = read_tsv(ART / OUTPUT_NAMES[2])
    deck = read_tsv(ART / OUTPUT_NAMES[3])
    ranking = read_tsv(ART / OUTPUT_NAMES[4])
    glosses = read_tsv(ART / OUTPUT_NAMES[5])
    patches = read_tsv(ART / OUTPUT_NAMES[6])
    edges = read_tsv(ART / OUTPUT_NAMES[7])
    packet = read_tsv(ART / OUTPUT_NAMES[8])
    guards = read_tsv(ART / OUTPUT_NAMES[9])
    contrasts = read_tsv(ART / OUTPUT_NAMES[10])
    intake = json.loads((ART / OUTPUT_NAMES[11]).read_text(encoding="utf-8"))
    result = json.loads((ART / OUTPUT_NAMES[12]).read_text(encoding="utf-8"))

    audit.check(len(target) == 58, "58 target occurrences")
    audit.check(len({row["occurrence_id"] for row in target}) == 58, "target occurrence IDs unique")
    audit.check(len({(row["locus"], row["token_ordinal_in_line"], row["surface"], row["occurrence_kind"]) for row in target}) == 58, "target occurrence coordinates unique")
    audit.check(Counter(row["surface"] for row in target) == Counter({"okal": 20, "otedy": 19, "olaiin": 14, "otchdy": 5}), "target surface counts")
    audit.check(Counter(row["occurrence_kind"] for row in target) == Counter({"RUNNING_EVENT": 48, "LOCAL_ADDRESS_OR_LABEL": 10}), "running/local target split")
    audit.check(Counter(row["mask_partition"] for row in target) == Counter({"OUTSIDE_27_PAGE_TRAIN": 45, "HELD_DEEP_IMAGE_PAGE": 13}), "outside/held total split")
    audit.check(sum(row["mask_partition"] == "OUTSIDE_27_PAGE_TRAIN" and row["occurrence_kind"] == "RUNNING_EVENT" for row in target) == 39, "39 outside running")
    audit.check(sum(row["mask_partition"] == "HELD_DEEP_IMAGE_PAGE" and row["occurrence_kind"] == "RUNNING_EVENT" for row in target) == 9, "nine held running")
    audit.check(sum(row["mask_partition"] == "OUTSIDE_27_PAGE_TRAIN" and row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL" for row in target) == 6, "six outside local")
    audit.check(sum(row["mask_partition"] == "HELD_DEEP_IMAGE_PAGE" and row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL" for row in target) == 4, "four held local")
    audit.check(not any(row["physical_page"].startswith("f84") or row["source_selector"].startswith("f84") for row in target), "no sealed target selector")
    audit.check(all(row["component_export_credit"] == "ZERO" for row in target), "target atlas has zero component export")
    audit.check(all(row["parser_channel_credit"].startswith("ZERO_INDEPENDENT") for row in target), "parser channel is circularity-marked")
    audit.check(all(row["reader_diagnostic_credit"] == "SAME_MANUSCRIPT_ALTERNATE_READING_ONLY" for row in target), "alternate readers not independent witnesses")
    audit.check(all(row["reader_alignment_method"] == "ALL_MAXIMUM_SAME_LINE_EXACT_TOKEN_LCS__UNIQUE_FORCED_REFERENCE_OCCURRENCE" for row in target), "reader alignment uses all-optimum exact-token LCS")
    reader_statuses = [row[f"{reader}_target_alignment_status"] for row in target for reader in ("it2a", "rf1b")]
    audit.check(Counter(reader_statuses) == Counter({"UNIQUE_FORCED_EXACT": 95, "NO_EXACT_ALIGNMENT": 21}), "reader alignment status counts")
    audit.check(all((row[f"{reader}_aligned_token_ordinal"] != "NA") == (row[f"{reader}_target_alignment_status"] == "UNIQUE_FORCED_EXACT") for row in target for reader in ("it2a", "rf1b")), "aligned ordinals only for unique forced matches")
    audit.check(all(row[f"{reader}_aligned_token_ordinal"] == "NA" or 1 <= int(row[f"{reader}_aligned_token_ordinal"]) <= int(row[f"{reader}_line_token_count"]) for row in target for reader in ("it2a", "rf1b")), "aligned ordinals lie inside alternate lines")
    audit.check(all(0 <= int(row[f"{reader}_exact_token_lcs_length"]) <= min(int(row["token_count_in_line"]), int(row[f"{reader}_line_token_count"])) for row in target for reader in ("it2a", "rf1b")), "reader LCS lengths are bounded")
    audit.check(all((row["all_three_unique_forced_exact_alignment"] == "YES") == all(row[f"{reader}_target_alignment_status"] == "UNIQUE_FORCED_EXACT" for reader in ("it2a", "rf1b")) for row in target), "all-three alignment flag replays reader statuses")

    otedy = [row for row in target if row["surface"] == "otedy" and row["occurrence_kind"] == "RUNNING_EVENT"]
    audit.check(len(otedy) == 18 and all(row["parser_statement_final"] == "YES" for row in otedy), "otedy 18/18 parser-final")
    audit.check(Counter(row["physical_line_role"] for row in otedy) == Counter({"LINE_INTERNAL": 15, "LINE_INITIAL": 2, "LINE_FINAL": 1}), "otedy physical line roles")
    audit.check(sum(row["all_three_unique_forced_exact_alignment"] == "YES" for row in otedy) == 10, "otedy ten of eighteen uniquely forced all-reader alignments")
    audit.check(Counter(row["language"] for row in otedy) == Counter({"B": 18}), "otedy all Currier B")
    audit.check(Counter(row["hand"] for row in otedy) == Counter({"2": 17, "3": 1}), "otedy hand split")
    deep_otedy = [row for row in otedy if row["mask_partition"] == "HELD_DEEP_IMAGE_PAGE"]
    audit.check(Counter(row["physical_record_role"] for row in deep_otedy) == Counter({"RECORD_INTERNAL": 4, "RECORD_FIRST": 1}), "otedy deep record position")
    audit.check(sum(row["record_local_fragment_role"] == "FRAGMENT_SINGLETON" for row in deep_otedy) == 2, "two deep corrected singleton otedy fragments")
    audit.check(sum(row["parser_statement_role"] == "STATEMENT_SINGLETON" for row in otedy if row["mask_partition"] == "OUTSIDE_27_PAGE_TRAIN") == 7, "seven outside singleton otedy statements")
    f77_otedy = [row for row in target if row["surface"] == "otedy" and row["locus"] in {"f77r.3", "f77r.25"}]
    audit.check(len(f77_otedy) == 2 and all(row["all_three_unique_forced_exact_alignment"] == "YES" for row in f77_otedy), "f77 label/prose otedy is uniquely forced in both alternate-reader alignments")

    okal = [row for row in target if row["surface"] == "okal"]
    okal_running = [row for row in okal if row["occurrence_kind"] == "RUNNING_EVENT"]
    okal_local = [row for row in okal if row["occurrence_kind"] == "LOCAL_ADDRESS_OR_LABEL"]
    audit.check(len(okal_running) == 16 and len(okal_local) == 4, "okal 16 running and four local")
    audit.check(Counter(row["physical_line_role"] for row in okal_running) == Counter({"LINE_INTERNAL": 15, "LINE_FINAL": 1}), "okal physical running roles")
    audit.check(all(row["parser_statement_final"] == "NO" for row in okal_running), "okal zero parser-final")
    audit.check(all(row["physical_line_role"] == "LINE_SINGLETON" for row in okal_local), "okal four singleton labels")
    audit.check(len({row["physical_page"] for row in okal_local}) == 3 and len({row["topology_family"] for row in okal_local}) == 2, "okal local breadth")
    audit.check(sum(row["all_three_unique_forced_exact_alignment"] == "YES" for row in okal) == 18, "okal eighteen of twenty uniquely forced all-reader alignments")

    audit.check(len(score) == 4 and {row["target_surface"] for row in score} == set(("otedy", "okal", "otchdy", "olaiin")), "four target score rows")
    audit.check(Counter(row["physical_role_transfer"] for row in score) == Counter({"PASS": 2, "FAIL": 1, "NOT_TESTABLE": 1}), "physical transfer outcomes")
    audit.check(Counter(row["local_scope_transfer"] for row in score) == Counter({"PASS": 3, "NOT_TESTABLE": 1}), "local transfer outcomes")
    audit.check(Counter(row["cross_topology_label_transfer"] for row in score) == Counter({"PASS": 3, "NOT_TESTABLE": 1}), "topology transfer outcomes")
    okal_score = next(row for row in score if row["target_surface"] == "okal")
    audit.check((okal_score["physical_role_transfer"], okal_score["local_scope_transfer"], okal_score["cross_topology_label_transfer"]) == ("PASS", "PASS", "PASS"), "okal passes three transfer channels")
    audit.check(okal_score["outside_majority_physical_role"] == "LINE_INTERNAL" and okal_score["held_role_share"] == "1.000000", "okal outside internal role transfers 2/2")
    olaiin_score = next(row for row in score if row["target_surface"] == "olaiin")
    audit.check(olaiin_score["physical_role_transfer"] == "FAIL" and olaiin_score["local_scope_transfer"] == "PASS", "olaiin mixed result")

    audit.check(len(declared) == 27, "27 declared target/control profiles")
    audit.check(Counter(row["comparison_kind"] for row in declared)["TARGET"] == 4, "four declared target profiles")
    audit.check(all(row["component_export_credit"] == "ZERO" for row in declared), "declared profiles whole-only")
    audit.check(len(deck) == 64, "64 deterministic control rows")
    for surface in ("otedy", "okal", "otchdy", "olaiin"):
        for deck_name in ("LANGUAGE_FREQUENCY", "PARSER_SHAPE"):
            rows = [row for row in deck if row["target_surface"] == surface and row["deck"] == deck_name]
            audit.check(len(rows) == 8 and len({row["control_surface"] for row in rows}) == 8, f"eight unique {deck_name} controls for {surface}")
            audit.check([int(row["control_rank"]) for row in rows] == list(range(1, 9)), f"control ranks for {surface}/{deck_name}")
            audit.check(all(row["control_component_export_credit"] == "ZERO__WHOLE_ONLY_COMPARISON" for row in rows), f"whole-only deck {surface}/{deck_name}")

    audit.check(len(contrasts) == 24, "24 target/control contrasts")
    audit.check(all(int(row["strictly_beaten_controls"]) + int(row["tied_controls"]) + int(row["higher_controls"]) == 8 for row in contrasts), "every contrast accounts for eight controls")
    audit.check(Counter(row["evidence_channel"] for row in contrasts) == Counter({"PRIMARY_PHYSICAL": 8, "MIXED_PHYSICAL_PLUS_PARSER": 8, "PARSER_COUPLED_NEIGHBOR_STATE": 8}), "contrast evidence channels")
    audit.check(all(row["semantic_credit"].startswith("ZERO_INDEPENDENT") for row in contrasts if row["evidence_channel"] != "PRIMARY_PHYSICAL"), "nonphysical contrasts have zero independent credit")
    okal_physical = [row for row in contrasts if row["target_surface"] == "okal" and row["metric"] == "PHYSICAL_LINE_INTERNAL"]
    audit.check(len(okal_physical) == 2 and all(row["seven_of_eight_control_gate"] == "PASS" for row in okal_physical), "okal physical rate beats both control decks")
    audit.check(all(row["held_deep_rate"] == "1.000000" for row in okal_physical), "okal physical rate holds deep")
    otedy_physical = [row for row in contrasts if row["target_surface"] == "otedy" and row["metric"] == "PHYSICAL_LINE_INTERNAL"]
    audit.check(Counter(row["seven_of_eight_control_gate"] for row in otedy_physical) == Counter({"PASS": 1, "FAIL": 1}), "otedy physical distinctiveness is mixed")

    audit.check(len(ranking) >= 100, "broad recurrent complete-whole ranking")
    audit.check([int(row["cross_scope_rank"]) for row in ranking] == list(range(1, len(ranking) + 1)), "ranking ordinals contiguous")
    rank1 = ranking[0]
    audit.check(rank1["comparison_surface"] == "okal", "okal ranks first")
    audit.check((rank1["singleton_local_count"], rank1["singleton_local_page_count"], rank1["singleton_local_topology_count"]) == ("4", "3", "2"), "okal rank metrics")
    okal_rank = next(row for row in ranking if row["comparison_surface"] == "okal")
    audit.check((okal_rank["outside_train_cross_scope_rank"], okal_rank["outside_train_multichar_rank"]) == ("4", "2"), "okal all-30 and training-only ranks remain separated")
    outside_rank_values = sorted(int(row["outside_train_cross_scope_rank"]) for row in ranking if row["outside_train_cross_scope_rank"] != "NA")
    audit.check(outside_rank_values == list(range(1, len(outside_rank_values) + 1)), "training-only ranks contiguous")
    baseline = Counter()
    for row in ranking:
        outside_n, held_n = int(row["outside_running_count"]), int(row["held_running_count"])
        if not outside_n or not held_n:
            continue
        counts = {
            "LINE_INITIAL": int(row["outside_line_initial_count"]),
            "LINE_INTERNAL": int(row["outside_line_internal_count"]),
            "LINE_FINAL": int(row["outside_line_final_count"]),
        }
        role, role_count = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[0]
        if role_count / outside_n < 0.60:
            continue
        baseline["testable"] += 1
        held_hits = int(row[f"held_line_{role.removeprefix('LINE_').lower()}_count"])
        passed = held_hits / held_n >= 0.60
        baseline["passing"] += int(passed)
        if role == "LINE_INTERNAL":
            baseline["internal_testable"] += 1
            baseline["internal_passing"] += int(passed)
    audit.check(baseline == Counter({"testable": 139, "internal_testable": 119, "passing": 105, "internal_passing": 95}), "60-percent transfer base rate independently replays")

    selected = [row for row in glosses if row["status_after_scoring"].startswith("SELECTED")]
    audit.check(not selected, "zero selected semantic glosses")
    triggered = [row for row in glosses if row["status_after_scoring"].startswith("PREREGISTERED_TRIGGER_PASS")]
    audit.check(len(triggered) == 1 and (triggered[0]["target_surface"], triggered[0]["candidate_gloss_de"]) == ("okal", "Ziel-/Bezugsstelle"), "address candidate raw trigger passes but stays unselected")
    audit.check(all(row["confidence"] == "C0_EXPLORATORY_HYPOTHESIS" and row["renderer_license"] == "NO" and row["semantic_credit"] == "ZERO" and row["lexeme_confirmed"] == "NO" and row["component_export_credit"] == "ZERO" for row in glosses), "glosses have no renderer or semantic credit")
    otedy_glosses = [row for row in glosses if row["target_surface"] == "otedy"]
    audit.check(otedy_glosses[0]["candidate_role"] == "BOUNDED_E_FIELD" and otedy_glosses[0]["status_after_scoring"].endswith("NOT_SELECTED"), "bounded E field remains unselected rival")
    audit.check(otedy_glosses[1]["candidate_role"] == "PORT_OR_CONDUIT_STATUS_REFERENCE" and "F77_SPECIFIC" in otedy_glosses[1]["status_after_scoring"], "port-status rival remains f77-specific")

    audit.check(len(patches) == 20 and len({row["occurrence_id"] for row in patches}) == 20, "twenty unique okal structural overlays")
    audit.check({row["occurrence_id"] for row in patches} == {row["occurrence_id"] for row in okal}, "overlays exactly cover okal target occurrences")
    audit.check(Counter(row["occurrence_kind"] for row in patches) == Counter({"RUNNING_EVENT": 16, "LOCAL_ADDRESS_OR_LABEL": 4}), "overlay running/local split")
    audit.check(Counter(row["predecessor_presence"] for row in patches) == Counter({"PRESENT_IN_GDT734_CACHE": 15, "ABSENT__NEW_30_PAGE_OVERLAY": 5}), "fifteen predecessor quarantines and five new overlays")
    present = [row for row in patches if row["predecessor_presence"] == "PRESENT_IN_GDT734_CACHE"]
    absent = [row for row in patches if row["predecessor_presence"] == "ABSENT__NEW_30_PAGE_OVERLAY"]
    audit.check(all(row["superseded_dictionary_card"] == "Rohstoffklasse I im heißen Ansatz, Gradanfang" and row["superseded_cache_display"] != "NONE" for row in present), "present overlays preserve exact predecessor provenance")
    audit.check(all(row["superseded_dictionary_card"] == row["superseded_cache_display"] == "NONE" for row in absent), "new overlays do not claim a predecessor")
    audit.check(all(row["surface"] == "okal" and row["structural_tag"] == "CROSS_SCOPE_LABEL_PROSE_WHOLE" for row in patches), "overlay is exact-whole structural tag")
    audit.check(all(row["selected_semantic_gloss"] == "NONE" and row["renderer_action"] == "STRUCTURAL_TAG_ONLY__NO_SEMANTIC_DISPLAY" for row in patches), "overlay has zero semantic display")
    audit.check(all(row["structural_display"] == "⟦okal:CROSS_SCOPE_LABEL_PROSE_WHOLE⟧" and "Ziel-/Bezugsstelle" not in row["structural_display"] for row in patches), "structural display is not address prose")
    audit.check(all(row["scope"] == "EXACT_OCCURRENCE_ON_RELEASED_30_PAGE_SPINE_ONLY" and row["component_export_credit"] == "ZERO" for row in patches), "overlay scope and component ceiling")

    audit.check(len(edges) == 4 and Counter(row["source_experiment"] for row in edges) == Counter({"GDT792_NEW": 2, "GDT790_RETAINED": 2}), "four okal edges split 2+2")
    audit.check(all(row["label_surface"] == "okal" and row["same_page"] == "YES" and row["cross_owner"] == "YES" for row in edges), "exact same-page cross-owner edges")
    audit.check(all(row["edge_class"] == "EXACT_COMPLETE_WHOLE_CROSS_OWNER_REUSE" for row in edges), "edges are reuse observations, not references")
    audit.check(len({row["physical_page"] for row in edges}) == 2 and Counter(row["physical_page"] for row in edges) == Counter({"f72r": 2, "f82r": 2}), "four edges form two page clusters")
    audit.check(all(row["semantic_credit"].startswith("ZERO__") for row in edges), "edge semantic credit zero")
    audit.check(len(packet) == 2 and all(row["eligibility_status"].startswith("INELIGIBLE") for row in packet), "two ineligible new relation rows")
    audit.check(all(row["relation_type"] == "EXACT_COMPLETE_WHOLE_CROSS_OWNER_REUSE_CANDIDATE" and row["direction_basis"] == "NONE__TRANSCRIPTION_ORDER_IS_NOT_REFERENCE_DIRECTION" for row in packet), "packet does not invent reference direction")
    completed = subprocess.run([str(ROOT / "vmanus-exp"), "check-edge-packet", str(ART / OUTPUT_NAMES[8])], cwd=ROOT, text=True, capture_output=True, check=False)
    audit.check(completed.returncode == 0, "relation packet CLI succeeds")
    if completed.returncode == 0:
        audit.check(json.loads(completed.stdout) == intake, "relation intake CLI byte-content equality")
    audit.check(intake["status"] == "VALID_ACQUISITION_NOT_SCORE_READY" and intake["packet_rows"] == 2 and intake["eligible_edges"] == 0 and not intake["score_ready"] and not intake["errors"], "relation packet valid but not score-ready")

    audit.check(len(guards) == 2 and {row["source"] for row in guards} == {"transcription/voynich_zl3b_lines.tsv", "transcription/voynich_cross_transcription_lines.tsv"}, "two guarded sources")
    audit.check(all((row["selector_count"], row["physical_page_count"], row["selected_rows"]) == ("35", "30", "1007") for row in guards), "guarded scope counts")
    audit.check(all(row["skipped_forbidden_rows"] == "98" and row["materialized_f84_rows"] == row["materialized_f84r_rows"] == "0" for row in guards), "sealed rows skipped before materialization")

    audit.check(result["experiment_id"] == "GDT792" and result["status"].startswith("PARTIAL__58_TARGET_OCCURRENCES"), "result identity/status")
    audit.check(result["decision"]["okal"].startswith("SELECT_CROSS_SCOPE_LABEL_PROSE_WHOLE_STRUCTURAL_TAG"), "result selects only okal structural role")
    audit.check(result["decision"]["otedy"].endswith("DO_NOT_SELECT"), "result does not select otedy")
    audit.check(result["okal_preregistered_raw_observable_trigger"]["result"] == "PASS" and all(result["okal_preregistered_raw_observable_trigger"]["conditions"].values()) and len(result["okal_preregistered_raw_observable_trigger"]["conditions"]) == 6, "all six raw okal trigger observations")
    audit.check(result["okal_semantic_selection"]["result"].startswith("WITHHELD") and all(result["okal_semantic_selection"]["vetoes"].values()), "okal semantic selection withheld")
    audit.check((result["okal_semantic_selection"]["all_30_rank"], result["okal_semantic_selection"]["outside_train_rank"], result["okal_semantic_selection"]["outside_train_multichar_rank"]) == (1, 4, 2), "result separates all-30 and training ranks")
    audit.check((result["control_deck_dependence"]["overlap"], result["control_deck_dependence"]["unique_union"]) == (7, 9), "okal control decks are overlapping sensitivity checks")
    okal_decks = {
        name: {row["control_surface"] for row in deck if row["target_surface"] == "okal" and row["deck"] == name}
        for name in ("LANGUAGE_FREQUENCY", "PARSER_SHAPE")
    }
    audit.check((len(okal_decks["LANGUAGE_FREQUENCY"] & okal_decks["PARSER_SHAPE"]), len(okal_decks["LANGUAGE_FREQUENCY"] | okal_decks["PARSER_SHAPE"])) == (7, 9), "okal deck overlap independently replays")
    audit.check(result["physical_transfer_baseline"] == {
        "cohort": "complete wholes with 3-25 running occurrences and a testable outside-to-held 60-percent role",
        "testable_forms": 139, "passing_forms": 105,
        "predicted_line_internal_testable_forms": 119,
        "predicted_line_internal_passing_forms": 95,
    }, "result records common transfer baseline")
    audit.check(result["counts"]["selected_semantic_glosses"] == result["counts"]["semantic_renderer_patches"] == 0, "zero selected glosses and semantic patches")
    audit.check((result["counts"]["okal_gdt734_predecessor_quarantines"], result["counts"]["okal_new_structural_overlays"]) == (15, 5), "result records predecessor/new overlay split")
    audit.check(result["counts"]["otedy_corrected_singleton_fields"] == result["counts"]["otedy_corrected_attached_fields"] == 9, "otedy corrected 9/9 cell split")
    audit.check(result["counts"]["confirmed_lexemes"] == result["counts"]["component_exports"] == result["counts"]["sealed_rows_materialized"] == 0, "result claim ceiling counts")

    payload = {
        "status": "PASS" if not audit.failures else "FAIL",
        "checks": audit.checks,
        "failures": audit.failures,
        "builder_byte_replay": not any(item.startswith("byte replay") for item in audit.failures),
        "relation_packet_replayed": completed.returncode == 0 and not intake["score_ready"],
    }
    (ART / "VALIDATION.json").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if not audit.failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
