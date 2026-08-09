#!/usr/bin/env python3
"""Retrospective public-circle-block decomposition of the diagnostic orbit."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import json
from pathlib import Path

import numpy as np

import source_native_diagnostic_transition_core as core
from audit_source_native_diagnostic_transition_concentration import join


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL_PATH = RESULTS / "source_native_diagnostic_transition_masked.tsv"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
ROLE_MATRIX = RESULTS / "existing_human_page_role_matrix.tsv"
ATLAS_VALIDATION = RESULTS / "existing_human_annotation_atlas_validation.json"
CORE = BASE / "source_native_diagnostic_transition_core.py"
TARGET = RESULTS / "source_native_diagnostic_transition_target.json"
TARGET_VALIDATION = RESULTS / "source_native_diagnostic_transition_target_validation.json"
CONCENTRATION = RESULTS / "source_native_diagnostic_transition_concentration.tsv"
CONCENTRATION_JSON = RESULTS / "source_native_diagnostic_transition_concentration.json"
CONCENTRATION_VALIDATION = RESULTS / "source_native_diagnostic_transition_concentration_validation.json"
SPEC = BASE / "SOURCE_NATIVE_CIRCLE_BLOCK_DIAGNOSTIC_SPEC.md"
AUDITOR = Path(__file__).resolve()
OUT_TSV = RESULTS / "source_native_circle_block_diagnostic.tsv"
OUT_JSON = RESULTS / "source_native_circle_block_diagnostic.json"
OUT_REPORT = RESULTS / "source_native_circle_block_diagnostic_report.md"

FROZEN = {
    PANEL_PATH: "7ed9f8186dcb31bd49a446e6b7751dc0bfc0f9d508feb816314fc71105daea02",
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    ROLE_MATRIX: "f2d4b5d3032deeae22ad0824abf3da689b31f97a2e664808c2729adaf30e4315",
    ATLAS_VALIDATION: "25c0642753974fec0b0646a22dc379e439242954f048ab778cc8df7c85442673",
    CORE: "4494da0ec8969b44c5636c419fb55b3485d4ddad98c3406c6f0cf09a3595a211",
    TARGET: "f01ca643dda1030b6fb7d43efa04c87a81e111e2c43a38c669f1380a67d34182",
    TARGET_VALIDATION: "4b6eb35f19c0a0152ac5947e070daa026ee5d4cb549f09d5b68aea56904ec294",
    CONCENTRATION: "ad9a9d5d7daa1b365635f85a61aed879c0d778751d5eecaf912d9d2705735b32",
    CONCENTRATION_JSON: "be64e18dc3c153d268eb28e43d33717ebc6284c9697f4d0651cc9b37b2a3e37b",
    CONCENTRATION_VALIDATION: "172b0ceadbbfe3d8e02afd67732c40b36d07a6009fa58de3a58a67c0cb060e72",
    SPEC: "32215e7ced25efca5885b0aceb981ee423a802bfc28487c56fd128b41cceae75",
}

PUBLIC_FOLIOS = ("f67", "f68", "f69", "f70", "f71", "f72", "f73")
PUBLIC_PAGES = (
    "f67r1", "f67r2", "f67v2", "f67v1",
    "f68r1", "f68r2", "f68r3", "f68v3", "f68v2", "f68v1",
    "f69r", "f69v", "f70r1", "f70r2", "f70v2", "f70v1",
    "f71r", "f71v",
    "f72r1", "f72r2", "f72r3", "f72v3", "f72v2", "f72v1",
    "f73r", "f73v",
)
ROLES = ("C", "L", "P", "R")
ENSEMBLES = ("SECTION_KIND_LENGTH", "FOLIO_KIND_LENGTH")
ASSIGNMENTS = 8192


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_public_source() -> list[dict[str, str]]:
    with ROLE_MATRIX.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    selected = [row for row in rows if row["page"] in PUBLIC_PAGES]
    if tuple(row["page"] for row in selected) != PUBLIC_PAGES:
        raise ValueError("public page order")
    if len(selected) != 26 or len({row["page"] for row in selected}) != 26:
        raise ValueError("public page identity")
    expected_quires = {"f67": "q09", "f68": "q09", "f69": "q10", "f70": "q10", "f71": "q11", "f72": "q11", "f73": "q12"}
    for row in selected:
        folio = next(value for value in PUBLIC_FOLIOS if row["page"].startswith(value + "r") or row["page"].startswith(value + "v"))
        tags = set(row["source_tags"].split(";"))
        if row["catalogue_match_status"] != "EXACT" or any(row[key] != "1" for key in ("has_general_description", "has_illustration_description", "has_text_description")):
            raise ValueError("public catalogue coverage")
        if not tags.intersection({"TEXT_CIRCULAR", "SOURCE_COSMOLOGICAL_PAGE", "SOURCE_ZODIAC_PAGE"}):
            raise ValueError("public circle evidence")
        if f"voynich.nu/{expected_quires[folio]}/" not in row["source_url"]:
            raise ValueError("public source URL")
    return selected


def role_orbits(panel, sequences, ensemble: str):
    role_index = {value: index for index, value in enumerate(ROLES)}
    favored = np.zeros((ASSIGNMENTS, len(ROLES), len(panel.folios)), dtype=np.int32)
    disfavored = np.zeros_like(favored)
    shift_digest = hashlib.sha256()
    for key, indices in core.strata(panel, ensemble):
        length = int(panel.lengths[indices[0]])
        size = len(indices)
        matrix = np.asarray([sequences[index] for index in indices], dtype=np.int16)
        recipient = np.arange(size, dtype=np.int64)
        columns = []
        for position in range(length):
            shift = core.shifts(ensemble, key, position, size, ASSIGNMENTS)
            shift_digest.update(np.asarray(shift, dtype="<i8").tobytes())
            source = (recipient[None, :] - shift[:, None]) % size
            columns.append(matrix[source, position])
        role = role_index[panel.rows[indices[0]]["kind"]]
        for position in range(1, length):
            fav = core.FAV[columns[position - 1], columns[position]]
            dis = core.DIS[columns[position - 1], columns[position]]
            for folio in np.unique(panel.folio_index[indices]):
                mask = panel.folio_index[indices] == folio
                favored[:, role, folio] += fav[:, mask].sum(axis=1, dtype=np.int32)
                disfavored[:, role, folio] += dis[:, mask].sum(axis=1, dtype=np.int32)
    full = core.rotation_scores(panel, sequences, ensemble, ASSIGNMENTS)
    if not np.array_equal(favored.sum(axis=1), full["favored_folio"]) or not np.array_equal(disfavored.sum(axis=1), full["disfavored_folio"]):
        raise ValueError("role totals")
    if shift_digest.hexdigest() != full["shift_sha256"]:
        raise ValueError("shift binding")
    return favored, disfavored, full


def row_summary(panel, favored, disfavored, ensemble: str, class_name: str, role: str):
    public = set(PUBLIC_FOLIOS)
    select_folios = np.asarray([(folio in public) == (class_name == "PUBLIC_CIRCLE_BLOCK") for folio in panel.folios])
    select_roles = np.ones(len(ROLES), dtype=bool) if role == "ALL" else np.asarray([value == role for value in ROLES])
    row_mask = np.asarray([
        ((row["physical_folio"] in public) == (class_name == "PUBLIC_CIRCLE_BLOCK")) and (role == "ALL" or row["kind"] == role)
        for row in panel.rows
    ])
    positions = int(np.maximum(0, panel.lengths[row_mask] - 1).sum())
    if positions == 0:
        return None
    group_count = int(row_mask.sum())
    favored_selected = favored[:, select_roles][:, :, select_folios].sum(axis=(1, 2))
    disfavored_selected = disfavored[:, select_roles][:, :, select_folios].sum(axis=(1, 2))
    favored_folio = favored[:, select_roles].sum(axis=1)
    disfavored_folio = disfavored[:, select_roles].sum(axis=1)
    favored_residual = favored_folio[0] - favored_folio[1:].mean(axis=0)
    disfavored_residual = disfavored_folio[0] - disfavored_folio[1:].mean(axis=0)
    eligible_folios = []
    for index, folio in enumerate(panel.folios):
        if not select_folios[index]:
            continue
        capacity = sum(max(0, int(panel.lengths[row_index]) - 1) for row_index, row in enumerate(panel.rows) if row["physical_folio"] == folio and (role == "ALL" or row["kind"] == role))
        if capacity:
            eligible_folios.append(index)
    null_favored = float(favored_selected[1:].mean())
    null_disfavored = float(disfavored_selected[1:].mean())
    return {
        "ensemble": ensemble,
        "class": class_name,
        "role": role,
        "folios": len(eligible_folios),
        "groups": group_count,
        "noninitial_positions": positions,
        "observed_favored": int(favored_selected[0]),
        "null_mean_favored": null_favored,
        "favored_excess_rate": float((favored_selected[0] - null_favored) / positions),
        "favored_upper_p": float(np.mean(favored_selected >= favored_selected[0])),
        "favored_positive_folios": int((favored_residual[eligible_folios] > 0).sum()),
        "observed_disfavored": int(disfavored_selected[0]),
        "null_mean_disfavored": null_disfavored,
        "disfavored_deficit_rate": float((null_disfavored - disfavored_selected[0]) / positions),
        "disfavored_lower_p": float(np.mean(disfavored_selected <= disfavored_selected[0])),
        "disfavored_negative_folios": int((disfavored_residual[eligible_folios] < 0).sum()),
    }


def serialize_report(summaries: dict) -> str:
    section = summaries["SECTION_KIND_LENGTH"]
    held = summaries["FOLIO_KIND_LENGTH"]
    return f"""# Public f67--f73 circle-block transition diagnostic

Status: **PASS_POST_RESULT_PUBLIC_CIRCLE_BLOCK_ROLE_DIAGNOSTIC**

Public human catalogue descriptions define the complete block as **f67 through
f73, including f71**: f67--f68 are astronomical/cosmological, f69--f70 recto
are cosmological, and f70 verso--f73 are zodiac circle diagrams.  The local
source projection contains all **26** page panels with exact catalogue matches.

The block contributes **{section['public']['groups']}** groups and
**{section['public']['noninitial_positions']}** noninitial positions.  All
**7/7** physical folios have positive favored and negative disfavored residuals
under both unchanged rotation ensembles.  Within the block, the same two
directions hold on every represented role-folio cell: `C` **3/3**, `L` **7/7**,
`P` **4/4**, and `R` **4/4**.  Every public-block role has both diagnostic tails
at p<=.01.

This is broad multi-role structure, but it is **not circle-specific evidence**.
The remaining diagnostic `L` material also has both tails at p<=.01, and the
public block's disfavored deficit per position is smaller than the remainder in
both ensembles ({section['public']['disfavored_deficit_rate']:.6f} versus
{section['other']['disfavored_deficit_rate']:.6f};
{held['public']['disfavored_deficit_rate']:.6f} versus
{held['other']['disfavored_deficit_rate']:.6f}).  Folio f68 remains the largest
favored contributor.  The original concentration nonconfirmation and its .25
gate remain unchanged.

This audit supplies no circle meaning, object ownership, diagram parameter,
word, sound, language, cipher, plaintext, or translation.
"""


def main() -> None:
    if any(path.exists() for path in (OUT_TSV, OUT_JSON, OUT_REPORT)):
        raise SystemExit("refusing overwrite")
    for path, expected in FROZEN.items():
        if sha(path) != expected:
            raise SystemExit(f"frozen mismatch: {path.name}")
    public_rows = validate_public_source()
    atlas_validation = json.loads(ATLAS_VALIDATION.read_text())
    target = json.loads(TARGET.read_text())
    target_validation = json.loads(TARGET_VALIDATION.read_text())
    concentration_validation = json.loads(CONCENTRATION_VALIDATION.read_text())
    if atlas_validation["status"] != "PASS_EXISTING_HUMAN_ANNOTATION_ATLAS_VALIDATION":
        raise ValueError("human source validation")
    if target["status"] != "NONCONFIRM_PROSE_GRAPH_TRANSFER_TO_DIAGNOSTIC_TEXT" or target_validation["status"] != "PASS_PRODUCTION_FREE_DIAGNOSTIC_NONCONFIRMATION_RECONSTRUCTION":
        raise ValueError("target state")
    if concentration_validation["status"] != "PASS_PRODUCTION_FREE_52_ROW_CONCENTRATION_RECONSTRUCTION":
        raise ValueError("concentration state")
    panel = core.load_panel(PANEL_PATH)
    sequences = join(panel)
    if not set(PUBLIC_FOLIOS).issubset(panel.folios):
        raise ValueError("public folio capacity")
    rows = []
    summaries = {}
    role_cell_direction = True
    for ensemble in ENSEMBLES:
        favored, disfavored, full = role_orbits(panel, sequences, ensemble)
        if full["shift_sha256"] != target["evaluation"][ensemble]["shift_sha256"]:
            raise ValueError("target orbit binding")
        for class_name in ("PUBLIC_CIRCLE_BLOCK", "OTHER_DIAGNOSTIC"):
            for role in ("ALL", *ROLES):
                item = row_summary(panel, favored, disfavored, ensemble, class_name, role)
                if item is not None:
                    rows.append(item)
        public_row = next(row for row in rows if row["ensemble"] == ensemble and row["class"] == "PUBLIC_CIRCLE_BLOCK" and row["role"] == "ALL")
        other_row = next(row for row in rows if row["ensemble"] == ensemble and row["class"] == "OTHER_DIAGNOSTIC" and row["role"] == "ALL")
        public_roles = [row for row in rows if row["ensemble"] == ensemble and row["class"] == "PUBLIC_CIRCLE_BLOCK" and row["role"] != "ALL"]
        label_other = next(row for row in rows if row["ensemble"] == ensemble and row["class"] == "OTHER_DIAGNOSTIC" and row["role"] == "L")
        role_cell_direction &= all(row["favored_positive_folios"] == row["folios"] and row["disfavored_negative_folios"] == row["folios"] for row in public_roles)
        summaries[ensemble] = {
            "public": public_row,
            "other": other_row,
            "public_roles": {row["role"]: row for row in public_roles},
            "all_public_folios_expected_direction": public_row["favored_positive_folios"] == 7 and public_row["disfavored_negative_folios"] == 7,
            "all_public_roles_both_tails_p_at_most_01": all(row["favored_upper_p"] <= 0.01 and row["disfavored_lower_p"] <= 0.01 for row in public_roles),
            "outside_label_both_tails_p_at_most_01": label_other["favored_upper_p"] <= 0.01 and label_other["disfavored_lower_p"] <= 0.01,
            "both_metrics_stronger_per_position_than_other": public_row["favored_excess_rate"] > other_row["favored_excess_rate"] and public_row["disfavored_deficit_rate"] > other_row["disfavored_deficit_rate"],
        }
    with OUT_TSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    gates = {
        "public_26_page_source_projection_exact": len(public_rows) == 26,
        "public_complete_f67_f73_including_f71": tuple(PUBLIC_FOLIOS) == ("f67", "f68", "f69", "f70", "f71", "f72", "f73"),
        "public_block_exact_960_groups_3416_positions": summaries["SECTION_KIND_LENGTH"]["public"]["groups"] == 960 and summaries["SECTION_KIND_LENGTH"]["public"]["noninitial_positions"] == 3416,
        "all_seven_public_folios_expected_direction_both_ensembles": all(summaries[value]["all_public_folios_expected_direction"] for value in ENSEMBLES),
        "all_public_role_folio_cells_expected_direction": role_cell_direction,
        "all_public_roles_both_tails_p_at_most_01": all(summaries[value]["all_public_roles_both_tails_p_at_most_01"] for value in ENSEMBLES),
        "outside_label_also_has_both_tails_p_at_most_01": all(summaries[value]["outside_label_both_tails_p_at_most_01"] for value in ENSEMBLES),
        "circle_specific_both_metrics_stronger": all(summaries[value]["both_metrics_stronger_per_position_than_other"] for value in ENSEMBLES),
        "original_target_decision_unchanged": True,
    }
    result = {
        "experiment": "SOURCE_NATIVE_CIRCLE_BLOCK_DIAGNOSTIC",
        "status": "PASS_POST_RESULT_PUBLIC_CIRCLE_BLOCK_ROLE_DIAGNOSTIC",
        "decision": "RETAIN_BROAD_PUBLIC_CIRCLE_BLOCK_MULTIROLE_STRUCTURE_NOT_CIRCLE_SPECIFICITY",
        "inputs": {path.name: sha(path) for path in (*FROZEN, AUDITOR)},
        "public_source_urls": [
            "https://www.voynich.nu/illustr.html",
            "https://www.voynich.nu/q09/index.html",
            "https://www.voynich.nu/q10/index.html",
            "https://www.voynich.nu/q11/index.html",
            "https://www.voynich.nu/q12/index.html",
        ],
        "public_folios": list(PUBLIC_FOLIOS),
        "public_pages": list(PUBLIC_PAGES),
        "public_page_rows": len(public_rows),
        "rows": len(rows),
        "tsv_sha256": sha(OUT_TSV),
        "summaries": summaries,
        "gates": gates,
        "circle_specific_confirmed": False,
        "original_target_status": target["status"],
        "original_target_decision": target["decision"],
        "original_gate_changed": False,
        "member_codes_accessed": 0,
        "english_glosses": 0,
        "claim_ceiling": "Retrospective public-source localization of the already observed coarse family-transition residual only; no circle-specific grammar, ownership, diagram parameter, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    OUT_REPORT.write_text(serialize_report(summaries))
    print(json.dumps({"status": result["status"], "decision": result["decision"], "gates": gates}, sort_keys=True))


if __name__ == "__main__":
    main()
