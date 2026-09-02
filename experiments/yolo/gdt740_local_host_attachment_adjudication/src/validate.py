#!/usr/bin/env python3
"""Independent scope, attachment, renderer, intake, and replay audit for GDT740."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = Path("experiments/yolo/gdt740_local_host_attachment_adjudication")
EXP = ROOT / BASE
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
G739 = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch"
G739_ART = G739 / "artifacts"
G739_RUN = G739 / "src/run.py"
STATUS = (
    "PARTIAL__103_BINDING_CONTACTS_PLUS_ONE_CONFLICT_CUE__62_DIRECT_CONTACTS_ON_58_TARGETS__"
    "39_RADIUS_TWO_HELD_PLUS_TWO_MANUAL_RELAYS__ONE_LOCAL_RESULT_MODE__"
    "BOUNDARY_AND_FLANK_FUSION_REPAIRED__ZERO_LEXEME_OR_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "TYPED_104_RING_EVIDENCE.tsv", "SELECTED_103_CONTACT_ATTACHMENT.tsv",
    "ORDERED_PAIR_100_RECURRENCE.tsv",
    "TARGET_95_ATTACHMENT_ADJUDICATION.tsv", "TARGET_202_RENDERER_PATCH_V2.tsv",
    "FORM_12_ATTACHMENT_PROFILE.tsv", "PASSAGE_20_ATTACHMENT_REVIEW.tsv",
    "GDT740_ATTACHMENT_READER.md", "GDT740_GDT388_EDGE_PACKET.tsv", "RESULT.json",
)
SCALAR_FORMS = {"lain", "lkaiin", "lkain", "lkar", "rain", "sain", "skaiin"}
STATE_FORMS = {"lcheedy", "lcheol", "lsheedy", "pcheol", "rsheedy"}
RETIRED = ("pulver", "samen", "saat", "wurzel", "holz")

spec = importlib.util.spec_from_file_location("gdt739_validator_helper", G739_RUN)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load GDT739 guarded cache helper")
g739 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g739)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--no-write", action="store_true")
    args = parser.parse_args()
    art = args.artifacts_dir.resolve()
    checks: list[str] = []

    def check(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def require(condition: bool, name: str) -> None:
        if not condition:
            raise AssertionError(name)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT740", "manifest experiment id")
    check(manifest["slug"] == "local_host_attachment_adjudication", "manifest slug")
    check(manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}, "sealed selectors forbidden")
    placeholder = (
        manifest["status"] == "REGISTERED_UNSCORED" and manifest["inputs"] == []
        and manifest["outputs"] == [] and manifest["validation"] == {"artifact": None, "status": "NOT_RUN"}
    )
    if placeholder:
        check(True, "manifest placeholder accepted before sealing")
    else:
        check(manifest["status"] == STATUS, "manifest status")
        check(manifest["validation"] == {"artifact": str(VALIDATION_REL), "status": "PASS"}, "manifest validation contract")
        check(bool(manifest["inputs"]) and bool(manifest["outputs"]), "sealed manifest has bindings")
        for binding in manifest["inputs"]:
            path = ROOT / binding["path"]
            require(not Path(binding["path"]).is_absolute(), f"absolute input: {binding['path']}")
            require(path.is_file() and sha256(path) == binding["sha256"], f"input mismatch: {binding['path']}")
        check(True, "all manifest inputs exist and hash-match")
        expected = {str(BASE / "artifacts" / name) for name in GENERATED} | {str(VALIDATION_REL)}
        check(expected <= {row["path"] for row in manifest["outputs"]}, "manifest binds generated outputs")
        for binding in manifest["outputs"]:
            if binding["path"] == str(VALIDATION_REL):
                continue
            path = ROOT / binding["path"]
            require(path.is_file() and sha256(path) == binding["sha256"], f"output mismatch: {binding['path']}")
        check(True, "all non-validation outputs hash-match")

    check(art.is_dir(), "artifact directory exists")
    check(all((art / name).is_file() for name in GENERATED), "all generated artifacts exist")
    source_dispatches = read_tsv(G739_ART / "DIMENSION_202_DISPATCH.tsv")
    source_windows = read_tsv(G739_ART / "WINDOW_202_TOKEN_AUDIT.tsv")
    dispatch_map = {row["dispatch_id"]: row for row in source_dispatches}
    window_map = {row["window_id"]: row for row in source_windows}
    compact_cells = g739.g738.compact_cells()
    check(len(source_dispatches) == 202 and len(dispatch_map) == 202, "source has 202 dispatches")
    check(sum(row["specific_local_dispatch"] == "1" for row in source_dispatches) == 95, "source has 95 specific targets")
    check(not any(row["page"].startswith("f84") for row in source_dispatches), "source excludes sealed pages")

    ring_evidence = read_tsv(art / "TYPED_104_RING_EVIDENCE.tsv")
    check(len(ring_evidence) == len({row["ring_evidence_id"] for row in ring_evidence}) == 104, "104 complete typed ring-evidence contacts")
    check(sum(row["role_bearing_binding_contact"] == "1" for row in ring_evidence) == 103, "103 ring rows carry binding roles")
    conflict_only = [row for row in ring_evidence if row["conflict_only_nonbinding_contact"] == "1"]
    check(len(conflict_only) == 1 and conflict_only[0]["window_id"] == "G739-N00627", "one explicit nonbinding conflict cue is preserved")
    check(all(row["window_id"] in window_map and row["plaintext_or_component_export"] == "0" for row in ring_evidence), "ring evidence preserves source and zero exports")

    contacts = read_tsv(art / "SELECTED_103_CONTACT_ATTACHMENT.tsv")
    check(len(contacts) == len({row["attachment_contact_id"] for row in contacts}) == 103, "103 unique binding contacts")
    check(len({row["patch_id"] for row in contacts}) == 90, "contacts cover 90 targets")
    check(Counter(row["selected_roles"] for row in contacts) == Counter({"AXIS+CARRIER": 43, "CARRIER": 33, "AXIS": 27}), "contact roles are 43 both, 33 carrier, 27 axis")
    check(Counter(int(row["distance"]) for row in contacts) == Counter({1: 62, 2: 41}), "contact distances are 62 direct and 41 radius two")
    check(Counter(row["attachment_decision"] for row in contacts) == Counter({
        "STRONG_REPEAT_EXPECTED": 4, "STRONG_REPEAT_REVERSE": 2,
        "SUPPORTED_DIRECTION_DIRECT": 38, "PROVISIONAL_REVERSE_DIRECT": 18,
        "NEAR_ONLY_HOLD": 41,
    }), "contact attachment tiers match")
    for row in contacts:
        source = dispatch_map[row["dispatch_id"]]
        window = window_map[row["window_id"]]
        require(row["patch_id"] == source["patch_id"] == window["patch_id"], f"contact source join: {row['attachment_contact_id']}")
        require(row["locus"] == source["locus"] == window["locus"], f"contact locus: {row['attachment_contact_id']}")
        require(row["target_surface"] == source["surface"] == window["target_surface"], f"contact target: {row['attachment_contact_id']}")
        require(row["neighbor_surface"] == window["neighbor_surface"], f"contact neighbor: {row['attachment_contact_id']}")
        require(int(row["target_ordinal"]) == int(source["token_ordinal"]) == int(window["target_ordinal"]), f"contact target ordinal: {row['attachment_contact_id']}")
        require(int(row["neighbor_ordinal"]) == int(window["neighbor_ordinal"]), f"contact neighbor ordinal: {row['attachment_contact_id']}")
        require(int(row["signed_offset"]) == int(window["signed_offset"]), f"contact source offset: {row['attachment_contact_id']}")
        require(int(row["distance"]) == int(window["distance"]), f"contact source distance: {row['attachment_contact_id']}")
        require(int(row["distance"]) == abs(int(row["signed_offset"])), f"contact geometry: {row['attachment_contact_id']}")
        require(int(row["neighbor_ordinal"]) - int(row["target_ordinal"]) == int(row["signed_offset"]), f"contact ordinal offset: {row['attachment_contact_id']}")
        require(row["side"] == ("L" if int(row["signed_offset"]) < 0 else "R"), f"contact side: {row['attachment_contact_id']}")
        require(int(row["renderer_role_retained"]) == int(int(row["axis_role_retained"]) or int(row["carrier_role_retained"])), f"retained role union: {row['attachment_contact_id']}")
        target_cell = compact_cells[(row["locus"], int(row["target_ordinal"]))]
        neighbor_cell = compact_cells[(row["locus"], int(row["neighbor_ordinal"]))]
        require(target_cell["surface"] == row["target_surface"], f"target cell surface: {row['attachment_contact_id']}")
        require(neighbor_cell["surface"] == row["neighbor_surface"], f"neighbor cell surface: {row['attachment_contact_id']}")
        for prefix, cell in (("target", target_cell), ("neighbor", neighbor_cell)):
            require(row[f"{prefix}_practical_unit_layer"] == cell["practical_unit_layer"], f"{prefix} unit layer: {row['attachment_contact_id']}")
            require(row[f"{prefix}_practical_unit_id"] == cell["practical_unit_id"], f"{prefix} unit id: {row['attachment_contact_id']}")
            require(row[f"{prefix}_practical_unit_role"] == cell["practical_unit_role"], f"{prefix} unit role: {row['attachment_contact_id']}")
        require(row["target_practical_unit_layer"] == row["neighbor_practical_unit_layer"] == "SINGLE_CELL_UNIT", f"single-cell contact units: {row['attachment_contact_id']}")
        require(row["shared_bound_practical_span"] == "0", f"no shared bound span: {row['attachment_contact_id']}")
        require(row["literal_plaintext_claimed"] == row["component_export_credit"] == "0", f"contact exports zero: {row['attachment_contact_id']}")
        ordered_cells = [target_cell, neighbor_cell]
        if row["distance"] == "2":
            middle_ordinal = int(row["target_ordinal"]) + (1 if int(row["signed_offset"]) > 0 else -1)
            middle_cell = compact_cells[(row["locus"], middle_ordinal)]
            require(row["intervening_surface"] == middle_cell["surface"], f"radius-two middle surface: {row['attachment_contact_id']}")
            require(row["intervening_practical_unit_role"] == middle_cell["practical_unit_role"], f"radius-two middle role: {row['attachment_contact_id']}")
            ordered_cells = [target_cell, middle_cell, neighbor_cell]
            require(row["intervening_practical_unit_role"] == "EMIT_CELL_ONCE", f"radius-two middle emits: {row['attachment_contact_id']}")
            require(row["intervening_emits_own_unit"] == "1", f"radius-two hold flag: {row['attachment_contact_id']}")
        if int(row["signed_offset"]) < 0:
            ordered_cells.reverse()
        require(row["manuscript_order_full_frame"] == " ".join(cell["surface"] for cell in ordered_cells), f"full manuscript frame: {row['attachment_contact_id']}")
    check(True, "all contact joins, source ordinals, full frames, unit geometry, middle barriers and exports are coherent")
    check(sum(row["distance"] == "2" and row["intervening_unknown_v99r7"] == "0" for row in contacts) == 35, "35 radius-two middle cells are known")
    check(sum(row["distance"] == "2" and row["intervening_strict_initial_head"] == "1" for row in contacts) == 2, "two radius-two middle cells are strict heads")
    check(not any(row["intervening_another_gdt738_target"] == "1" for row in contacts), "no radius-two middle cell is another target")
    check(Counter((row["distance"], row["renderer_role_retained"]) for row in contacts) == Counter({
        ("1", "1"): 55, ("1", "0"): 7, ("2", "1"): 2, ("2", "0"): 39,
    }), "55 direct and two relay contacts survive; seven direct and 39 radius-two contacts hold")

    # Independently recount every selected ordered pair on the inherited guarded cache.
    by_line, exact, guards = g739.g738.token_context()
    pair_counts: Counter[tuple[str, int, str]] = Counter()
    raw_pair_counts: Counter[tuple[str, int, str]] = Counter()
    triple_counts: Counter[tuple[str, int, str, str]] = Counter()
    for locus, line in by_line.items():
        for index, token in enumerate(line):
            for offset in (-2, -1, 1, 2):
                neighbor_index = index + offset
                if 0 <= neighbor_index < len(line):
                    neighbor = line[neighbor_index]
                    key = (token["eva"], offset, neighbor["eva"])
                    raw_pair_counts[key] += 1
                    if not exact[(locus, int(token["token_index"]))]:
                        continue
                    if exact[(locus, int(neighbor["token_index"]))]:
                        pair_counts[key] += 1
                        if abs(offset) == 2:
                            middle = line[index + (1 if offset > 0 else -1)]
                            if exact[(locus, int(middle["token_index"]))]:
                                triple_counts[(token["eva"], offset, middle["eva"], neighbor["eva"])] += 1
    for row in contacts:
        key = (row["target_surface"], int(row["signed_offset"]), row["neighbor_surface"])
        require(int(row["guarded_reader_exact_pair_occurrences"]) == pair_counts[key], f"pair recurrence: {row['attachment_contact_id']}")
        require(int(row["guarded_zl3b_pair_occurrences"]) == raw_pair_counts[key], f"raw pair recurrence: {row['attachment_contact_id']}")
        if row["distance"] == "2":
            triple = (row["target_surface"], int(row["signed_offset"]), row["intervening_surface"], row["neighbor_surface"])
            require(int(row["guarded_reader_exact_full_frame_occurrences"]) == triple_counts[triple], f"triple recurrence: {row['attachment_contact_id']}")
    check(True, "all contact recurrence counts independently match guarded cache")
    pairs = read_tsv(art / "ORDERED_PAIR_100_RECURRENCE.tsv")
    check(len(pairs) == len({row["pair_id"] for row in pairs}) == 100, "100 unique ordered pair keys")
    repeated = [row for row in pairs if int(row["guarded_reader_exact_pair_occurrences"]) >= 2]
    check(len(repeated) == 3 and sum(int(row["selected_contact_occurrences"]) for row in repeated) == 6, "three repeated exact pairs cover six contacts")
    check(sum(int(row["guarded_zl3b_pair_occurrences"]) >= 2 for row in pairs) == 4, "four raw repeated pair controls")
    check(sum(row["raw_only_repeat_control"] == "1" for row in contacts) == 1, "one selected raw-only repeat control")
    check(not any(row["distance"] == "2" and int(row["guarded_reader_exact_pair_occurrences"]) >= 2 for row in pairs), "no repeated radius-two pair")
    check(not any(row["distance"] == "2" and int(row["guarded_reader_exact_full_frame_occurrences"]) >= 2 for row in contacts), "no repeated exact radius-two triple frame")

    targets = read_tsv(art / "TARGET_95_ATTACHMENT_ADJUDICATION.tsv")
    check(len(targets) == len({row["adjudication_id"] for row in targets}) == 95, "95 unique target adjudications")
    check({row["gdt739_dispatch_id"] for row in targets} == {row["dispatch_id"] for row in source_dispatches if row["specific_local_dispatch"] == "1"}, "target deck equals GDT739 specific set")
    check(Counter(row["attachment_tier"] for row in targets) == Counter({
        "ATTACHED_STRONG": 6, "ATTACHED_SUPPORTED": 32,
        "ATTACHED_PROVISIONAL_REVERSE": 13, "NEAR_ONLY_HOLD": 30,
        "RELAY_R2_MANUAL": 2, "KEEP_CARRIER_ONLY": 3,
        "MODE_DOWNGRADED_OPEN": 5, "DIRECT_COMPONENT_CONFLICT_OPEN": 2,
        "DIRECT_BOUNDARY_HOLD": 1, "DIRECT_FLANK_CONFLICT_OPEN": 1,
    }), "target tiers include relay, boundary, mode and flank corrections")
    check(sum(int(row["selected_contacts"]) for row in targets) == 103, "target contacts sum to 103")
    check(sum(int(row["radius_two_relay_contacts"]) for row in targets) == 2, "two target relay contacts survive")
    target_by_dispatch = {row["gdt739_dispatch_id"]: row for row in targets}
    for dispatch_id in ("G739-D0064", "G739-D0076"):
        require(target_by_dispatch[dispatch_id]["attachment_tier"] == "DIRECT_COMPONENT_CONFLICT_OPEN", f"component-conflict tier: {dispatch_id}")
        require(target_by_dispatch[dispatch_id]["carrier_attachment_outcome"] == "DIRECT_COMPONENT_CONFLICT_OPEN", f"component-conflict carrier outcome: {dispatch_id}")
    require(target_by_dispatch["G739-D0158"]["carrier_attachment_outcome"] == "DIRECT_BOUNDARY_HOLD", "D0158 carrier outcome preserves closure boundary")
    require(target_by_dispatch["G739-D0195"]["axis_attachment_outcome"] == "DIRECT_FLANK_CONFLICT_OPEN", "D0195 axis outcome preserves flank conflict")
    require(target_by_dispatch["G739-D0195"]["carrier_attachment_outcome"] == "DIRECT_FLANK_CONFLICT_OPEN", "D0195 carrier outcome preserves flank conflict")
    check(True, "manual component, boundary and flank outcomes remain explicitly distinct")

    patches = read_tsv(art / "TARGET_202_RENDERER_PATCH_V2.tsv")
    check(len(patches) == len({row["gdt740_patch_id"] for row in patches}) == 202, "202 unique renderer patches")
    check({row["gdt739_dispatch_id"] for row in patches} == set(dispatch_map), "patches cover every source dispatch")
    for row in patches:
        source = dispatch_map[row["gdt739_dispatch_id"]]
        require(all(row[field] == source[field] for field in (
            "patch_id", "occurrence_id", "page", "locus", "token_index", "token_ordinal",
            "surface", "body", "opaque_head_id", "line_position", "family", "level",
        )), f"patch provenance: {row['gdt740_patch_id']}")
        require(row["gdt739_state_mode"] == source["state_mode"], f"source state mode: {row['gdt740_patch_id']}")
        require(all(row[field] == "0" for field in (
            "literal_patient_or_species_claimed", "literal_plaintext_claimed",
            "unconditional_global_export", "head_or_body_lexeme_credit",
            "component_export_credit", "unseen_form_export",
        )), f"patch exports zero: {row['gdt740_patch_id']}")
        require(not any(word in row["gdt740_working_render_de"].lower() for word in RETIRED), f"retired literal in render: {row['gdt740_patch_id']}")
    check(True, "all renderer patches preserve provenance and export ceiling")
    scalar = [row for row in patches if row["surface"] in SCALAR_FORMS]
    state = [row for row in patches if row["surface"] in STATE_FORMS]
    check(len(scalar) == 172 and len(state) == 30, "renderer partitions 172 scalar and 30 state")
    check(Counter(row["gdt740_dimension_dispatch"] for row in scalar) == Counter({
        "OPEN_SCALAR": 135, "OPEN_SCALAR_CONFLICT": 3, "QUALITY_DEGREE": 24,
        "AMOUNT_DOSE": 6, "PROCESS_PASS": 4,
    }), "adjudicated scalar dispatch counts")
    check(sum(int(row["axis_specific_dispatch_retained"]) for row in patches) == 36, "36 axis-specific occurrences remain")
    check(sum(int(row["carrier_locally_bound_retained"]) for row in patches) == 43, "43 carrier-bound occurrences remain")
    check(sum(int(row["specific_local_dispatch_retained"]) for row in patches) == 56, "56 occurrences retain a specific channel")
    check(sum(not int(row["specific_local_dispatch_retained"]) for row in patches) == 146, "146 occurrences are fully open")
    check(sum(int(row["renderer_changed_from_gdt739"]) for row in patches) == 49, "49 renders change from GDT739")
    check(sum(int(row["manual_override_applied"]) for row in patches) == 13, "thirteen explicit manual overrides applied")
    check(Counter(row["gdt739_state_mode"] for row in state) == Counter({"QUALITY_STATE": 22, "PROCESS_RESULT": 8}), "source state/result mode is 22/8")
    check(Counter(row["gdt740_state_mode"] for row in state) == Counter({"QUALITY_STATE": 29, "PROCESS_RESULT": 1}), "GDT740 state/result mode is 29/1")

    profiles = read_tsv(art / "FORM_12_ATTACHMENT_PROFILE.tsv")
    check(len(profiles) == len({row["surface"] for row in profiles}) == 12, "twelve form profiles")
    check(sum(int(row["occurrences"]) for row in profiles) == 202, "profile occurrences sum to 202")
    check(sum(int(row["fully_open_after_attachment"]) for row in profiles) == 146, "profile open sum is 146")
    passages = read_tsv(art / "PASSAGE_20_ATTACHMENT_REVIEW.tsv")
    check(len(passages) == len({row["passage_id"] for row in passages}) == 20, "twenty passage reviews")
    check(sum(len(row["focal_surfaces"].split("|")) for row in passages) == 23, "passages cover 23 focal patches")
    check(set(surface for row in passages for surface in row["focal_surfaces"].split("|")) == SCALAR_FORMS | STATE_FORMS, "passages cover all twelve forms")
    passage_map = {row["passage_id"]: row for row in passages}
    check("Zustandsstufe II der Zubereitung" in passage_map["G739-R03"]["gdt740_target_renders_de"] and "Resultat" not in passage_map["G739-R03"]["gdt740_target_renders_de"], "R03 result mode removed")
    check("Zustandsstufe II" in passage_map["G739-R11"]["gdt740_target_renders_de"] and "Resultat" not in passage_map["G739-R11"]["gdt740_target_renders_de"], "R11 mode-only result removed")
    check("Zustandsstufe II" in passage_map["G739-R16"]["gdt740_target_renders_de"] and "Resultat" not in passage_map["G739-R16"]["gdt740_target_renders_de"], "R16 held result removed")
    check(passage_map["G739-R18"]["gdt740_target_renders_de"].endswith("Skalarstufe II; Dimension offen"), "R18 closure boundary removes carrier")
    check(all("no clause or attachment is implied" in row["reader_note"] for row in passages), "cellwise displays disclaim clause and attachment")
    reader = (art / "GDT740_ATTACHMENT_READER.md").read_text(encoding="utf-8")
    check(all(row["passage_id"] in reader for row in passages), "reader contains every passage")

    edges = read_tsv(art / "GDT740_GDT388_EDGE_PACKET.tsv")
    check(len(edges) == 6 and all(row["eligibility_status"] == "INELIGIBLE_FORMAL_ATTACHMENT_EDGE" for row in edges), "six repeated contacts exposed as ineligible edges")
    intake = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(art / "GDT740_GDT388_EDGE_PACKET.tsv")],
        cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    intake_payload = json.loads(intake.stdout)
    check(intake.returncode == 1 and intake_payload["status"] == "INVALID_PACKET", "GDT388 intake rejects formal semantic edges")
    check(not intake_payload["score_ready"] and not intake_payload["capacity_gate_50_edges_5_folios"] and not intake_payload["holdout_gate"] and not intake_payload["mobile_null_gate"], "all score-readiness gates remain closed")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT740_LOCAL_HOST_ATTACHMENT_ADJUDICATION_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"]["inherited_allowlist_pages"] == 179 and result["scope"]["new_pages_used"] == 0, "result preserves inherited scope")
    check(result["scope"]["f84_used"] is False and result["scope"]["f84r_used"] is False, "result excludes sealed pages")
    check(result["source"] == {
        "complete_wholes": 12, "all_renderer_positions": 202,
        "gdt739_specific_targets": 95, "selected_contacts": 103,
        "selected_contact_targets": 90,
        "typed_ring_evidence_contacts_including_nonbinding_conflict": 104,
        "nonbinding_conflict_only_contacts": 1,
    }, "result source geometry")
    check(result["attachment"]["manual_radius_two_relay_contacts"] == 2 and result["attachment"]["held_radius_two_contacts"] == 39, "result separates two relays from 39 held radius-two contacts")
    check(result["attachment"]["renderer_retained_contact_rows"] == 57, "result records 57 retained contact rows")
    check(result["attachment"]["renderer_retained_role_flags"] == 80, "result records 80 retained role flags")
    check(result["attachment"]["renderer_retained_axis_role_flags"] == 36, "result records 36 retained axis-role flags")
    check(result["attachment"]["renderer_retained_carrier_role_flags"] == 44, "result records 44 retained carrier-role flags")
    check(result["renderer"]["axis_specific_occurrences"] == 36 and result["renderer"]["carrier_bound_occurrences"] == 43, "result retains adjudicated axis and carriers")
    check(result["renderer"]["fully_open_occurrences"] == 146 and result["renderer"]["changed_from_gdt739"] == 49, "result open and change counts")
    check(result["renderer"]["gdt740_state_modes"] == {"PROCESS_RESULT": 1, "QUALITY_STATE": 29}, "result keeps one local result mode")
    check(all(value == 0 for value in result["claims"].values()), "result claim ceiling remains zero")
    for name in GENERATED[:-1]:
        rel = str(BASE / "artifacts" / name)
        require(result["artifact_hashes"][rel] == sha256(art / name), f"result hash: {name}")
    check(True, "result artifact hashes match")

    with tempfile.TemporaryDirectory(prefix="gdt740-replay-") as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)], cwd=ROOT,
            check=True, capture_output=True, text=True,
        )
        require(completed.returncode == 0, "builder replay command")
        for name in GENERATED:
            require((replay / name).is_file(), f"replay output missing: {name}")
            require(sha256(replay / name) == sha256(art / name), f"replay identity: {name}")
    check(True, "builder replay is byte-identical")

    payload = {
        "schema": "GDT740_VALIDATION_V1", "status": "PASS",
        "checks_passed": len(checks), "checks": checks,
        "source_hashes": {
            str((G739_ART / "DIMENSION_202_DISPATCH.tsv").relative_to(ROOT)): sha256(G739_ART / "DIMENSION_202_DISPATCH.tsv"),
            str((G739_ART / "WINDOW_202_TOKEN_AUDIT.tsv").relative_to(ROOT)): sha256(G739_ART / "WINDOW_202_TOKEN_AUDIT.tsv"),
        },
        "artifact_hashes": {name: sha256(art / name) for name in GENERATED},
        "builder_replay": "BYTE_IDENTICAL",
        "edge_intake": intake_payload,
        "sealed_data": {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
    }
    if not args.no_write:
        (art / "VALIDATION.json").write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print(json.dumps({
        "status": "PASS", "checks_passed": len(checks),
        "builder_replay": "BYTE_IDENTICAL", "edge_intake": intake_payload["status"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
