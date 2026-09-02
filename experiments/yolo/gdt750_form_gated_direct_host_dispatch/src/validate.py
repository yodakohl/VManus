#!/usr/bin/env python3
"""Invariant, edge-gate and byte-replay validation for GDT750."""

from __future__ import annotations

import argparse
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
BASE = Path("experiments/yolo/gdt750_form_gated_direct_host_dispatch")
EXP = ROOT / BASE
ART = EXP / "artifacts"
RUN = EXP / "src/run.py"
ROUTE_DIAGNOSTIC = EXP / "src/route_diagnostic.py"
MANIFEST = EXP / "experiment.json"
VALIDATION_REL = BASE / "artifacts/VALIDATION.json"
STATUS = (
    "PARTIAL__1134_KNOWN_OCCURRENCE_CALIBRATION__D1_R1_19_TP_0_FP_"
    "15_POSITIONS__19_ACTIVE_OUTSIDE_POSITIONS__5_FORMS__32_AXIS_CARDS__"
    "RADIUS2_DISCOVERY_ONLY__DISTANCE2_SENSITIVITY_ONLY__"
    "QOCHEY_OKECHY_NO_ACTIVE_HOST__ZERO_LITERAL_IDENTITIES__"
    "ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
)
GENERATED = (
    "RULE_VARIANT_CALIBRATION.tsv",
    "KNOWN_1134_OCCURRENCE_CALIBRATION.tsv",
    "FORM_17_PRIOR_DECK.tsv",
    "TARGET_1684_HOST_DISPATCH_AUDIT.tsv",
    "ACTIVE_OCCURRENCE_CARDS.tsv",
    "ACTIVE_HOST_CONTACTS.tsv",
    "FORM_17_DISPATCH_PROFILE.tsv",
    "GDT750_FORM_GATED_HOST_READER.md",
    "GDT750_GDT388_HOST_EDGE_PACKET.tsv",
    "GDT750_GDT388_EDGE_INTAKE.json",
    "RESULT.json",
)
TARGETS = {
    "chdy", "cheey", "cheky", "cheol", "kchdy", "lkeey", "okal",
    "okechy", "okedy", "okeey", "olkaiin", "olkar", "oty", "qokaiin",
    "qokedy", "sheey", "qochey",
}
EXPECTED_VARIANTS = {
    "V0_DIRECT_RAW_R1": (342, 65, 277, 203, 371, 1748, "0.353659", "0.104049", "REJECT_DIRECT_HOST_TRANSFER"),
    "V1_DIRECT_NO_CLOSE_R1": (310, 61, 249, 186, 331, 1765, "0.359768", "0.095336", "REJECT_DIRECT_HOST_TRANSFER"),
    "V2_D1_MULTI_FORM_R1_NO_CLOSE_ACTIVE": (15, 15, 0, 19, 0, 1932, "1.000000", "0.009739", "ACTIVE_OCCURRENCE_RENDERER"),
    "V3_D1_MULTI_FORM_R2_NO_CLOSE_DISCOVERY": (24, 24, 0, 28, 0, 1923, "1.000000", "0.014352", "DISCOVERY_ONLY_RADIUS_TWO"),
    "V4_D2_MULTI_FORM_R1_NO_CLOSE_SENSITIVITY": (64, 44, 20, 67, 21, 1884, "0.761364", "0.034341", "SENSITIVITY_ONLY_DISTANCE_TWO"),
    "V5_D2_MULTI_FORM_R2_NO_CLOSE_SENSITIVITY": (97, 69, 28, 101, 30, 1850, "0.770992", "0.051768", "SENSITIVITY_ONLY_DISTANCE_TWO"),
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


def axes(text: str) -> set[str]:
    return set() if text in {"", "NONE", "OPEN"} else set(text.split("|"))


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_value in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_value in enumerate(right, start=1):
            current.append(min(
                current[-1] + 1,
                previous[right_index] + 1,
                previous[right_index - 1] + (left_value != right_value),
            ))
        previous = current
    return previous[-1]


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

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    check(manifest["experiment_id"] == "GDT750", "manifest id")
    check(manifest["slug"] == "form_gated_direct_host_dispatch", "manifest slug")
    check(manifest["status"] == STATUS, "manifest status")
    check(
        manifest["dependencies"]
        == ["GDT388", "GDT734", "GDT739", "GDT740", "GDT745", "GDT746", "GDT748", "GDT749"],
        "manifest dependencies",
    )
    check(
        manifest["sealed_data"] == {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"},
        "sealed data",
    )
    check(bool(manifest["question"]), "manifest question")
    check(bool(manifest["claim_ceiling"]), "manifest ceiling")
    check(
        manifest["validation"]
        == {"artifact": str(VALIDATION_REL), "status": "PASS"},
        "validation contract",
    )
    for binding in manifest["inputs"]:
        path = ROOT / binding["path"]
        check(path.is_file(), f"input exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"input hash {binding['path']}")

    variants = read_tsv(art / GENERATED[0])
    calibration = read_tsv(art / GENERATED[1])
    priors = read_tsv(art / GENERATED[2])
    dispatch = read_tsv(art / GENERATED[3])
    active = read_tsv(art / GENERATED[4])
    contacts = read_tsv(art / GENERATED[5])
    profiles = read_tsv(art / GENERATED[6])

    check(len(variants) == 6, "six variants")
    check(len(calibration) == 1134, "1134 calibration occurrences")
    check(len(priors) == 17, "17 form priors")
    check(len(dispatch) == 1684, "1684 target occurrences")
    check(len(active) == 19, "19 active occurrence cards")
    check(len(contacts) == 19, "19 active host contacts")
    check(len(profiles) == 17, "17 dispatch profiles")
    check(len({row["gdt750_calibration_occurrence_id"] for row in calibration}) == 1134, "unique calibration ids")
    check(len({row["gdt750_dispatch_id"] for row in dispatch}) == 1684, "unique dispatch ids")
    check(len({row["gdt750_active_card_id"] for row in active}) == 19, "unique active ids")
    check(len({row["gdt750_contact_id"] for row in contacts}) == 19, "unique contact ids")
    check({row["target_surface"] for row in priors} == TARGETS, "fixed prior surfaces")
    check({row["target_surface"] for row in profiles} == TARGETS, "fixed profile surfaces")

    variant_map = {row["gdt750_variant_id"]: row for row in variants}
    check(set(variant_map) == set(EXPECTED_VARIANTS), "variant ids")
    for name, expected in EXPECTED_VARIANTS.items():
        row = variant_map[name]
        actual = (
            int(row["predicted_positions"]),
            int(row["all_predictions_subset_of_true_positions"]),
            int(row["contradiction_positions"]),
            int(row["true_positive_axis_labels"]),
            int(row["false_positive_axis_labels"]),
            int(row["false_negative_axis_labels"]),
            row["axis_precision"], row["axis_recall"], row["disposition"],
        )
        check(actual == expected, f"variant result {name}")
        check(row["known_occurrences"] == "1134", f"variant universe {name}")
        check(row["literal_identity_credit"] == "0", f"variant literal {name}")
        check(row["confirmed_lexeme"] == "0", f"variant lexeme {name}")
        check(row["component_export_credit"] == "0", f"variant component {name}")

    active_prefix = "V2_D1_MULTI_FORM_R1_NO_CLOSE_ACTIVE"
    check(len({row["known_surface"] for row in calibration}) == 43, "43 occurring calibration forms")
    check(sum(row[f"{active_prefix}_predicted_axes"] != "NONE" for row in calibration) == 15, "15 active calibration positions")
    for row in calibration:
        occurrence = row["gdt750_calibration_occurrence_id"]
        predicted = axes(row[f"{active_prefix}_predicted_axes"])
        truth = axes(row["true_quality_stage_axes"])
        check(predicted <= truth, f"active subset truth {occurrence}")
        check(row[f"{active_prefix}_false_axes"] == "NONE", f"active no false {occurrence}")
        check(not row["page"].startswith("f84"), f"sealed calibration {occurrence}")
        check(row["literal_identity_credit"] == "0", f"calibration literal {occurrence}")
        check(row["confirmed_lexeme"] == "0", f"calibration lexeme {occurrence}")
        check(row["component_export_credit"] == "0", f"calibration component {occurrence}")

    prior_map = {row["target_surface"]: row for row in priors}
    check(prior_map["okeey"]["distance1_reference_surfaces"] == "okeedy|ykeey", "okeey two d1 references")
    check(prior_map["okeey"]["distance1_multi_reference_prior_axes"] == "HOT|END_STAGE", "okeey hot end prior")
    check(prior_map["qochey"]["distance1_multi_reference_prior_axes"] == "DRY|MIDDLE_STAGE", "qochey dry middle prior")
    check(prior_map["sheey"]["distance1_multi_reference_prior_axes"] == "MOIST|END_STAGE", "sheey moist end prior")
    for row in priors:
        surface = row["target_surface"]
        check(row["literal_identity"] == "OPEN", f"prior literal {surface}")
        check(row["confirmed_lexeme"] == "0", f"prior lexeme {surface}")
        check(row["component_export_credit"] == "0", f"prior component {surface}")

    check(sum(int(row["reader_exact"]) for row in dispatch) == 1353, "1353 exact target occurrences")
    check(sum(int(row["gdt748_discovery_position"]) for row in dispatch) == 57, "57 discovery positions")
    check(sum(int(row["outside_discovery_primary"]) for row in dispatch) == 1311, "1311 exact outside positions")
    check(sum(int(row["active_outside_card"]) for row in dispatch) == 19, "19 dispatch activations")
    dispatch_coordinates: dict[tuple[str, str, str], dict[str, str]] = {}
    for row in dispatch:
        occurrence = row["gdt750_dispatch_id"]
        coordinate = (row["target_surface"], row["locus"], row["token_ordinal"])
        dispatch_coordinates[coordinate] = row
        check(not row["page"].startswith("f84"), f"sealed dispatch {occurrence}")
        check(row["written_line_eva"].split()[int(row["token_ordinal"]) - 1] == row["target_surface"], f"dispatch line coordinate {occurrence}")
        if row["active_outside_card"] == "1":
            check(row["outside_discovery_primary"] == "1", f"active outside {occurrence}")
            check(row["reader_exact"] == "1", f"active exact {occurrence}")
            check(row["active_selected_ring"] == "1", f"active radius one {occurrence}")
            check(row["active_emitted_axes"] != "NONE", f"active axes {occurrence}")
            check(row["active_contributing_hosts"] != "NONE", f"active host {occurrence}")
            check(row["active_conflicts"] == "NONE", f"active no conflict {occurrence}")
        check(row["literal_identity"] == "OPEN", f"dispatch literal {occurrence}")
        check(row["confirmed_lexeme"] == "0", f"dispatch lexeme {occurrence}")
        check(row["component_export_credit"] == "0", f"dispatch component {occurrence}")

    form_counts = Counter(row["target_surface"] for row in active)
    check(form_counts == Counter({"okeey": 14, "cheol": 2, "cheey": 1, "cheky": 1, "sheey": 1}), "active form counts")
    axis_sets = Counter(row["emitted_axes"] for row in active)
    check(axis_sets == Counter({"HOT|END_STAGE": 12, "DRY": 3, "END_STAGE": 2, "HOT": 1, "MOIST|END_STAGE": 1}), "active axis combinations")
    check(len({row["page"] for row in active}) == 14, "14 active pages overall")
    check(len({row["page"] for row in active if row["target_surface"] == "okeey"}) == 10, "okeey ten active pages")
    check(len({row["page"] for row in active if row["target_surface"] == "cheol"}) == 2, "cheol two active pages")
    for row in active:
        card = row["gdt750_active_card_id"]
        coordinate = (row["target_surface"], row["locus"], row["token_ordinal"])
        check(coordinate in dispatch_coordinates, f"active dispatch join {card}")
        check(dispatch_coordinates[coordinate]["active_outside_card"] == "1", f"active flag join {card}")
        check(row["written_line_eva"].split()[int(row["token_ordinal"]) - 1] == row["target_surface"], f"active line coordinate {card}")
        check(row["working_render_de"] != "", f"active render {card}")
        check(row["literal_identity"] == "OPEN", f"active literal {card}")
        check(row["confirmed_lexeme"] == "0", f"active lexeme {card}")
        check(row["component_export_credit"] == "0", f"active component {card}")

    check(Counter(row["gdt750_active_card_id"] for row in contacts) == Counter(row["gdt750_active_card_id"] for row in active), "one contact per active card")
    for row in contacts:
        contact = row["gdt750_contact_id"]
        check(row["page"] == row["target_locus"].split(".")[0], f"contact target page {contact}")
        check(row["target_locus"] == row["host_locus"], f"contact same line {contact}")
        check(abs(int(row["signed_offset"])) == 1, f"contact immediate {contact}")
        check(int(row["host_ordinal"]) - int(row["target_ordinal"]) == int(row["signed_offset"]), f"contact offset {contact}")
        check(row["whole_edit_distance"] == "1", f"contact recorded d1 {contact}")
        check(levenshtein(row["target_surface"], row["host_surface"]) == 1, f"contact replay d1 {contact}")
        check(axes(row["supported_emitted_axes"]) <= axes(row["host_axes"]), f"contact supported subset {contact}")
        check(row["relation_scope"] == "COMPLETE_WHOLE_DIRECT_HOST_AXIS_ONLY", f"contact relation scope {contact}")
        check(row["literal_identity_credit"] == "0", f"contact literal {contact}")
        check(row["confirmed_lexeme"] == "0", f"contact lexeme {contact}")
        check(row["component_export_credit"] == "0", f"contact component {contact}")

    status_counts = Counter(row["dispatch_status"] for row in profiles)
    check(status_counts == Counter({
        "A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST": 12,
        "A1_ACTIVE_SINGLE_OCCURRENCE_FORM_GATED_HOST": 3,
        "A3_ACTIVE_CROSS_PAGE_FORM_GATED_HOST": 2,
    }), "profile status counts")
    profile_map = {row["target_surface"]: row for row in profiles}
    check(profile_map["okeey"]["active_axis_counts"] == "HOT:13|END_STAGE:13", "okeey profile axes")
    check(profile_map["cheol"]["active_axis_counts"] == "DRY:2", "cheol profile axes")
    check(profile_map["qochey"]["active_outside_positions"] == "0", "qochey silent")
    check(profile_map["okechy"]["active_outside_positions"] == "0", "okechy silent")
    check(sum(int(row["radius2_additional_discovery_positions"]) for row in profiles) == 0, "radius two adds no target card")
    check(sum(int(row["distance2_additional_sensitivity_positions"]) for row in profiles) == 0, "distance two adds no target card")
    for row in profiles:
        surface = row["target_surface"]
        check(row["literal_identity"] == "OPEN", f"profile literal {surface}")
        check(row["confirmed_lexeme"] == "0", f"profile lexeme {surface}")
        check(row["component_export_credit"] == "0", f"profile component {surface}")
        check(row["unseen_form_export"] == "0", f"profile unseen {surface}")

    reader = (art / "GDT750_FORM_GATED_HOST_READER.md").read_text(encoding="utf-8")
    check("heißer Zustand an der End-/Vollstufe" in reader, "reader hot end rendering")
    check("qochey` — A0_NO_ACTIVE_FORM_GATED_DIRECT_HOST" in reader, "reader qochey silent")

    packet_path = art / "GDT750_GDT388_HOST_EDGE_PACKET.tsv"
    packet = read_tsv(packet_path)
    intake = json.loads((art / "GDT750_GDT388_EDGE_INTAKE.json").read_text(encoding="utf-8"))
    check(len(packet) == 19, "nineteen relation rows")
    check(len({row["edge_id"] for row in packet}) == 19, "unique relation rows")
    for row in packet:
        edge = row["edge_id"]
        check(row["page"] == row["pivot_locus"].split(".")[0].split("@")[0], f"edge pivot same page {edge}")
        check(row["page"] == row["target_locus"].split(".")[0].split("@")[0], f"edge target same page {edge}")
        check(row["relation_type"] == "FORM_GATED_DIRECT_COMPLETE_WHOLE_HOST", f"edge relation type {edge}")
        check(row["eligibility_status"] == "INELIGIBLE_FORMAL_CONTEXT_RELATION", f"edge ineligible {edge}")
    expected_errors = [f"edge row {number}: formal access is not sealed" for number in range(2, 21)]
    check(intake["status"] == "INVALID_PACKET" and not intake["score_ready"], "edge invalid not ready")
    check(intake["errors"] == expected_errors, "edge sole formal errors")
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT, check=False, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    check(completed.returncode == 1, "edge checker expected return")
    check(json.loads(completed.stdout) == intake, "edge checker replay")

    result = json.loads((art / "RESULT.json").read_text(encoding="utf-8"))
    check(result["schema"] == "GDT750_RESULT_V1", "result schema")
    check(result["status"] == STATUS, "result status")
    check(result["scope"] == {
        "active_axis_cards": 32,
        "active_forms": 5,
        "active_host_contacts": 19,
        "active_outside_positions": 19,
        "allowed_pages": 179,
        "known_calibration_occurrences": 1134,
        "outside_reader_exact_occurrences": 1311,
        "target_occurrences": 1684,
    }, "result scope")
    check(result["variant_calibration"]["V2_D1_MULTI_FORM_R1_NO_CLOSE_ACTIVE"] == {
        "disposition": "ACTIVE_OCCURRENCE_RENDERER",
        "fn": 1932, "fp": 0, "positions": 15,
        "precision": 1.0, "recall": 0.009739, "tp": 19,
    }, "result active calibration")
    check(result["form_profiles"]["okeey"]["active_positions"] == 14, "result okeey positions")
    check(result["form_profiles"]["qochey"]["active_positions"] == 0, "result qochey silent")
    check(result["inherited_guard"]["allowed_pages"] == 179, "result allowed pages")
    check(result["edge_intake"]["errors"] == expected_errors, "result edge errors")
    check("No language" in result["claim_ceiling"], "result claim ceiling")

    route = json.loads((art / "ROUTE_FEASIBILITY.json").read_text(encoding="utf-8"))
    check(route["schema"] == "GDT750_ROUTE_FEASIBILITY_V1", "route diagnostic schema")
    check(route["status"] == "OPEN_EXPANSION_ZERO_NEW__BROAD_CARRIER_RULE_FAILS__Q_BASE_SHELL_ROUTE_LIVE", "route diagnostic status")
    check(route["open_quality_stage_expansion"] == {
        "active_cards": [{
            "axes": "DRY|MIDDLE_STAGE", "locus": "f104v.23",
            "surface": "qochey", "token_ordinal": 3,
        }],
        "active_outside_prior_discovery_positions": 0,
        "active_positions": 1,
        "active_surfaces": 1,
        "disposition": "DO_NOT_OPEN_NAIVE_ALL_RECURRENT_ROUTE",
        "distance1_multi_prior_positions": 112,
        "distance1_multi_prior_surfaces": 28,
        "open_surfaces": 3447,
        "reader_exact_open_positions": 5007,
        "recurrent_open_positions": 2298,
        "recurrent_open_surfaces": 738,
    }, "route open expansion exact result")
    broad = route["broad_axis_sensitivity"]
    check((broad["known_occurrences"], broad["predicted_positions"], broad["tp"], broad["fp"], broad["fn"]) == (1158, 24, 19, 14, 2590), "route broad axis totals")
    check(broad["false_axis_surfaces"] == {"chol": 14}, "route broad failures all chol")
    check(broad["axis_results"]["MATERIAL"] == {"fn": 229, "fp": 14, "tp": 0}, "route material failure")
    q_shell = route["q_base_shell_feasibility"]
    check(q_shell["q_base_pairs"] == 51, "route 51 q base pairs")
    check(q_shell["quality_stage_exactly_preserved_pairs"] == 47, "route 47 quality-stage pairs")
    check(q_shell["unprefixed_preparation_q_not_pairs"] == 41, "route 41 inherited preparation asymmetries")
    check(q_shell["q_preparation_unprefixed_not_pairs"] == 0, "route zero reverse preparation asymmetries")
    check((q_shell["reader_exact_q_occurrences"], q_shell["reader_exact_unprefixed_occurrences"]) == (2060, 1701), "route q base occurrence counts")
    check((q_shell["q_earlier_pairs"], q_shell["q_later_pairs"]) == (33, 18), "route pair position direction")
    check(q_shell["pair_balanced_mean_normalized_position_delta_q_minus_unprefixed"] == -0.066507, "route mean position delta")
    check((q_shell["direct_reader_exact_q_base_contacts"], q_shell["direct_contact_pair_types"], q_shell["direct_contact_pages"]) == (44, 12, 27), "route direct q base contacts")
    check("No q character" in route["claim_ceiling"], "route claim ceiling")

    for binding in manifest["outputs"]:
        if binding["path"] == str(VALIDATION_REL):
            continue
        path = ROOT / binding["path"]
        check(path.is_file(), f"output exists {binding['path']}")
        check(sha256(path) == binding["sha256"], f"output hash {binding['path']}")

    with tempfile.TemporaryDirectory(prefix=".gdt750_replay_", dir=EXP) as temporary:
        replay = Path(temporary)
        completed = subprocess.run(
            [sys.executable, str(RUN), "--output-dir", str(replay)],
            cwd=ROOT, check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "builder replay return")
        for name in GENERATED:
            check((replay / name).is_file(), f"replay exists {name}")
            check((replay / name).read_bytes() == (art / name).read_bytes(), f"byte replay {name}")
        route_replay = replay / "ROUTE_FEASIBILITY.json"
        completed = subprocess.run(
            [sys.executable, str(ROUTE_DIAGNOSTIC), "--output", str(route_replay)],
            cwd=ROOT, check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        check(completed.returncode == 0, "route diagnostic replay return")
        check(route_replay.read_bytes() == (art / "ROUTE_FEASIBILITY.json").read_bytes(), "route diagnostic byte replay")

    validation = {
        "schema": "GDT750_VALIDATION_V1",
        "status": "PASS",
        "checks": len(checks),
        "byte_identical_replay": True,
        "scope": result["scope"],
        "active_form_counts": dict(sorted(form_counts.items())),
        "profile_status_counts": dict(sorted(status_counts.items())),
        "active_variant": result["variant_calibration"]["V2_D1_MULTI_FORM_R1_NO_CLOSE_ACTIVE"],
        "route_feasibility_status": route["status"],
        "claim_ceiling": result["claim_ceiling"],
    }
    if not args.no_write:
        (art / "VALIDATION.json").write_text(
            json.dumps(validation, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(validation, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
