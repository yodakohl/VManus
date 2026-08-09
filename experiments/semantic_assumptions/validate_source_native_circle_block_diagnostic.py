#!/usr/bin/env python3
"""Auditor-free reconstruction of the public circle-block diagnostic."""

from __future__ import annotations

import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

import csv
import hashlib
import io
import json
from pathlib import Path

import numpy as np

import validate_source_native_diagnostic_transition_preflight as independent
import validate_source_native_diagnostic_transition_target as target_validator


BASE = Path(__file__).resolve().parent
RESULTS = BASE / "results"
PANEL = RESULTS / "source_native_diagnostic_transition_masked.tsv"
SOURCE = RESULTS / "source_sta_family_consensus_groups.tsv"
ROLE_MATRIX = RESULTS / "existing_human_page_role_matrix.tsv"
ATLAS_VALIDATION = RESULTS / "existing_human_annotation_atlas_validation.json"
SPEC = BASE / "SOURCE_NATIVE_CIRCLE_BLOCK_DIAGNOSTIC_SPEC.md"
AUDITOR = BASE / "audit_source_native_circle_block_diagnostic.py"
TARGET = RESULTS / "source_native_diagnostic_transition_target.json"
TARGET_VALIDATION = RESULTS / "source_native_diagnostic_transition_target_validation.json"
CONCENTRATION = RESULTS / "source_native_diagnostic_transition_concentration.tsv"
CONCENTRATION_JSON = RESULTS / "source_native_diagnostic_transition_concentration.json"
CONCENTRATION_VALIDATION = RESULTS / "source_native_diagnostic_transition_concentration_validation.json"
TSV = RESULTS / "source_native_circle_block_diagnostic.tsv"
PRODUCTION = RESULTS / "source_native_circle_block_diagnostic.json"
PRODUCTION_REPORT = RESULTS / "source_native_circle_block_diagnostic_report.md"
VALIDATOR = Path(__file__).resolve()
OUT = RESULTS / "source_native_circle_block_diagnostic_validation.json"
REPORT = RESULTS / "source_native_circle_block_diagnostic_validation_report.md"

FROZEN = {
    PANEL: "7ed9f8186dcb31bd49a446e6b7751dc0bfc0f9d508feb816314fc71105daea02",
    SOURCE: "a202d93498e8a350a5d7e0ca46e831dcc37ea5c0182dc404d63cb797a98b1225",
    ROLE_MATRIX: "f2d4b5d3032deeae22ad0824abf3da689b31f97a2e664808c2729adaf30e4315",
    ATLAS_VALIDATION: "25c0642753974fec0b0646a22dc379e439242954f048ab778cc8df7c85442673",
    SPEC: "32215e7ced25efca5885b0aceb981ee423a802bfc28487c56fd128b41cceae75",
    AUDITOR: "2418b33d21d2366fe5f12bc7b3b34f9a36db97b07436cd9f3b0dc4fb703cc7a4",
    TARGET: "f01ca643dda1030b6fb7d43efa04c87a81e111e2c43a38c669f1380a67d34182",
    TARGET_VALIDATION: "4b6eb35f19c0a0152ac5947e070daa026ee5d4cb549f09d5b68aea56904ec294",
    CONCENTRATION: "ad9a9d5d7daa1b365635f85a61aed879c0d778751d5eecaf912d9d2705735b32",
    CONCENTRATION_JSON: "be64e18dc3c153d268eb28e43d33717ebc6284c9697f4d0651cc9b37b2a3e37b",
    CONCENTRATION_VALIDATION: "172b0ceadbbfe3d8e02afd67732c40b36d07a6009fa58de3a58a67c0cb060e72",
    TSV: "162e316bfe176161aaad042d87ef750b5e3de6e4f25f85c948edbf41029ab33d",
    PRODUCTION: "72c5f85616898256746b72f1d88bbad4dfb5edb2b2711bd660285b7a0ebea2a8",
    PRODUCTION_REPORT: "7cb48f17ec00f87a3211935436d76b1bafcff4fd6b18c8c606ba981a030efb1e",
}

FOLIOS = ("f67", "f68", "f69", "f70", "f71", "f72", "f73")
PAGES = (
    "f67r1", "f67r2", "f67v2", "f67v1",
    "f68r1", "f68r2", "f68r3", "f68v3", "f68v2", "f68v1",
    "f69r", "f69v", "f70r1", "f70r2", "f70v2", "f70v1",
    "f71r", "f71v", "f72r1", "f72r2", "f72r3", "f72v3", "f72v2", "f72v1",
    "f73r", "f73v",
)
ROLES = ("C", "L", "P", "R")
ENSEMBLES = ("SECTION_KIND_LENGTH", "FOLIO_KIND_LENGTH")
ASSIGNMENTS = 8192


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_projection(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected = [row for row in rows if row["page"] in PAGES]
    if tuple(row["page"] for row in selected) != PAGES or len({row["page"] for row in selected}) != 26:
        raise ValueError("page identity")
    quire = {"f67": "q09", "f68": "q09", "f69": "q10", "f70": "q10", "f71": "q11", "f72": "q11", "f73": "q12"}
    for row in selected:
        folio = next(value for value in FOLIOS if row["page"].startswith(value + "r") or row["page"].startswith(value + "v"))
        tags = set(row["source_tags"].split(";"))
        if row["catalogue_match_status"] != "EXACT" or {row["has_general_description"], row["has_illustration_description"], row["has_text_description"]} != {"1"}:
            raise ValueError("coverage")
        if not ({"TEXT_CIRCULAR", "SOURCE_COSMOLOGICAL_PAGE", "SOURCE_ZODIAC_PAGE"} & tags):
            raise ValueError("classification")
        if f"voynich.nu/{quire[folio]}/" not in row["source_url"]:
            raise ValueError("URL")
    return selected


def compute_role_orbits(panel, sequences, ensemble: str):
    role_to_index = {value: index for index, value in enumerate(ROLES)}
    favored = np.zeros((ASSIGNMENTS, 4, 26), dtype=np.int32)
    disfavored = np.zeros((ASSIGNMENTS, 4, 26), dtype=np.int32)
    digest = hashlib.sha256()
    for key, indices in independent.grouped(panel, ensemble):
        width = int(panel.lengths[indices[0]])
        count = len(indices)
        symbols = np.asarray([sequences[index] for index in indices], dtype=np.int16)
        destinations = np.arange(count, dtype=np.int64)
        placed = []
        for position in range(width):
            values = np.arange(ASSIGNMENTS, dtype=np.uint64) ^ np.uint64(independent.stable("SNWGDX1|" + ensemble + "|" + "|".join(key) + "|" + str(position)))
            offsets = (independent.splitmix(values) % np.uint64(count)).astype(np.int64)
            offsets[0] = 0
            digest.update(np.asarray(offsets, dtype="<i8").tobytes())
            placed.append(symbols[(destinations[None, :] - offsets[:, None]) % count, position])
        role_index = role_to_index[panel.rows[indices[0]]["kind"]]
        for position in range(1, width):
            fav = independent.FAV[placed[position - 1], placed[position]]
            dis = independent.DIS[placed[position - 1], placed[position]]
            for folio_index in np.unique(panel.folio_index[indices]):
                recipient_mask = panel.folio_index[indices] == folio_index
                favored[:, role_index, folio_index] += np.sum(fav[:, recipient_mask], axis=1, dtype=np.int32)
                disfavored[:, role_index, folio_index] += np.sum(dis[:, recipient_mask], axis=1, dtype=np.int32)
    all_favored, all_disfavored, folio_favored, folio_disfavored, reference_digest = independent.compute(panel, sequences, ensemble, ASSIGNMENTS)
    if not np.array_equal(favored.sum(1), folio_favored) or not np.array_equal(disfavored.sum(1), folio_disfavored):
        raise ValueError("orbit partition")
    if not np.array_equal(favored.sum((1, 2)), all_favored) or not np.array_equal(disfavored.sum((1, 2)), all_disfavored):
        raise ValueError("orbit total")
    if digest.hexdigest() != reference_digest:
        raise ValueError("shift digest")
    return favored, disfavored, reference_digest


def summarize(panel, favored, disfavored, ensemble: str, class_name: str, role_name: str):
    circle = set(FOLIOS)
    in_class = np.asarray([(folio in circle) == (class_name == "PUBLIC_CIRCLE_BLOCK") for folio in panel.folios])
    role_indices = range(4) if role_name == "ALL" else (ROLES.index(role_name),)
    event_rows = [
        index for index, row in enumerate(panel.rows)
        if ((row["physical_folio"] in circle) == (class_name == "PUBLIC_CIRCLE_BLOCK")) and (role_name == "ALL" or row["kind"] == role_name)
    ]
    positions = sum(max(0, int(panel.lengths[index]) - 1) for index in event_rows)
    if positions == 0:
        return None
    selected_favored = favored[:, role_indices, :][:, :, in_class].sum((1, 2))
    selected_disfavored = disfavored[:, role_indices, :][:, :, in_class].sum((1, 2))
    by_folio_favored = favored[:, role_indices, :].sum(1)
    by_folio_disfavored = disfavored[:, role_indices, :].sum(1)
    residual_favored = by_folio_favored[0] - by_folio_favored[1:].mean(0)
    residual_disfavored = by_folio_disfavored[0] - by_folio_disfavored[1:].mean(0)
    eligible = []
    for folio_index, folio in enumerate(panel.folios):
        if not in_class[folio_index]:
            continue
        capacity = sum(max(0, int(panel.lengths[index]) - 1) for index, row in enumerate(panel.rows) if row["physical_folio"] == folio and (role_name == "ALL" or row["kind"] == role_name))
        if capacity > 0:
            eligible.append(folio_index)
    expected_favored = float(selected_favored[1:].mean())
    expected_disfavored = float(selected_disfavored[1:].mean())
    return {
        "ensemble": ensemble,
        "class": class_name,
        "role": role_name,
        "folios": len(eligible),
        "groups": len(event_rows),
        "noninitial_positions": positions,
        "observed_favored": int(selected_favored[0]),
        "null_mean_favored": expected_favored,
        "favored_excess_rate": float((selected_favored[0] - expected_favored) / positions),
        "favored_upper_p": float(np.count_nonzero(selected_favored >= selected_favored[0]) / ASSIGNMENTS),
        "favored_positive_folios": int(np.count_nonzero(residual_favored[eligible] > 0)),
        "observed_disfavored": int(selected_disfavored[0]),
        "null_mean_disfavored": expected_disfavored,
        "disfavored_deficit_rate": float((expected_disfavored - selected_disfavored[0]) / positions),
        "disfavored_lower_p": float(np.count_nonzero(selected_disfavored <= selected_disfavored[0]) / ASSIGNMENTS),
        "disfavored_negative_folios": int(np.count_nonzero(residual_disfavored[eligible] < 0)),
    }


def reconstruct(panel, sequences):
    rows = []
    summaries = {}
    role_cell_direction = True
    digests = {}
    for ensemble in ENSEMBLES:
        favored, disfavored, digest = compute_role_orbits(panel, sequences, ensemble)
        digests[ensemble] = digest
        for class_name in ("PUBLIC_CIRCLE_BLOCK", "OTHER_DIAGNOSTIC"):
            for role_name in ("ALL", *ROLES):
                item = summarize(panel, favored, disfavored, ensemble, class_name, role_name)
                if item is not None:
                    rows.append(item)
        public = next(row for row in rows if row["ensemble"] == ensemble and row["class"] == "PUBLIC_CIRCLE_BLOCK" and row["role"] == "ALL")
        other = next(row for row in rows if row["ensemble"] == ensemble and row["class"] == "OTHER_DIAGNOSTIC" and row["role"] == "ALL")
        public_roles = [row for row in rows if row["ensemble"] == ensemble and row["class"] == "PUBLIC_CIRCLE_BLOCK" and row["role"] != "ALL"]
        label_other = next(row for row in rows if row["ensemble"] == ensemble and row["class"] == "OTHER_DIAGNOSTIC" and row["role"] == "L")
        role_cell_direction = role_cell_direction and all(row["favored_positive_folios"] == row["folios"] and row["disfavored_negative_folios"] == row["folios"] for row in public_roles)
        summaries[ensemble] = {
            "public": public,
            "other": other,
            "public_roles": {row["role"]: row for row in public_roles},
            "all_public_folios_expected_direction": public["favored_positive_folios"] == 7 and public["disfavored_negative_folios"] == 7,
            "all_public_roles_both_tails_p_at_most_01": all(row["favored_upper_p"] <= 0.01 and row["disfavored_lower_p"] <= 0.01 for row in public_roles),
            "outside_label_both_tails_p_at_most_01": label_other["favored_upper_p"] <= 0.01 and label_other["disfavored_lower_p"] <= 0.01,
            "both_metrics_stronger_per_position_than_other": public["favored_excess_rate"] > other["favored_excess_rate"] and public["disfavored_deficit_rate"] > other["disfavored_deficit_rate"],
        }
    return rows, summaries, role_cell_direction, digests


def tsv_text(rows) -> str:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return handle.getvalue()


def report_text(summaries) -> str:
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
    if OUT.exists() or REPORT.exists():
        raise SystemExit("refusing overwrite")
    failures = []
    checks = 0

    def check(condition, name):
        nonlocal checks
        checks += 1
        if not condition:
            failures.append(name)

    for path, expected in FROZEN.items():
        check(sha(path) == expected, f"hash:{path.name}")
    with ROLE_MATRIX.open(encoding="utf-8", newline="") as handle:
        page_rows = list(csv.DictReader(handle, delimiter="\t"))
    selected = source_projection(page_rows)
    check(len(selected) == 26, "public-source-26")
    check("f71r" in PAGES and "f71v" in PAGES, "f71-mandatory")
    panel = independent.load_panel()
    with SOURCE.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle, delimiter="\t"))
    sequences, _ = target_validator.join(panel, source_rows)
    rows, summaries, role_cell_direction, digests = reconstruct(panel, sequences)
    check(len(rows) == 18, "rows-18")
    check(tsv_text(rows) == TSV.read_text(), "tsv-bytes")
    stored = json.loads(PRODUCTION.read_text())
    check(stored["summaries"] == summaries, "summaries")
    check(stored["tsv_sha256"] == sha(TSV), "tsv-binding")
    check(stored["public_folios"] == list(FOLIOS) and stored["public_pages"] == list(PAGES), "public-membership")
    check(stored["public_page_rows"] == 26 and stored["rows"] == 18, "sizes")
    check(stored["status"] == "PASS_POST_RESULT_PUBLIC_CIRCLE_BLOCK_ROLE_DIAGNOSTIC", "status")
    check(stored["decision"] == "RETAIN_BROAD_PUBLIC_CIRCLE_BLOCK_MULTIROLE_STRUCTURE_NOT_CIRCLE_SPECIFICITY", "decision")
    check(stored["circle_specific_confirmed"] is False and stored["original_gate_changed"] is False, "claim-lock")
    check(stored["original_target_status"] == "NONCONFIRM_PROSE_GRAPH_TRANSFER_TO_DIAGNOSTIC_TEXT" and stored["original_target_decision"] == "RETAIN_PROSE_LOCAL_TRANSITION_GRAMMAR_ONLY", "target-lock")
    check(stored["member_codes_accessed"] == 0 and stored["english_glosses"] == 0, "ceiling")
    gates = {
        "public_26_page_source_projection_exact": len(selected) == 26,
        "public_complete_f67_f73_including_f71": FOLIOS == ("f67", "f68", "f69", "f70", "f71", "f72", "f73"),
        "public_block_exact_960_groups_3416_positions": summaries["SECTION_KIND_LENGTH"]["public"]["groups"] == 960 and summaries["SECTION_KIND_LENGTH"]["public"]["noninitial_positions"] == 3416,
        "all_seven_public_folios_expected_direction_both_ensembles": all(summaries[value]["all_public_folios_expected_direction"] for value in ENSEMBLES),
        "all_public_role_folio_cells_expected_direction": role_cell_direction,
        "all_public_roles_both_tails_p_at_most_01": all(summaries[value]["all_public_roles_both_tails_p_at_most_01"] for value in ENSEMBLES),
        "outside_label_also_has_both_tails_p_at_most_01": all(summaries[value]["outside_label_both_tails_p_at_most_01"] for value in ENSEMBLES),
        "circle_specific_both_metrics_stronger": all(summaries[value]["both_metrics_stronger_per_position_than_other"] for value in ENSEMBLES),
        "original_target_decision_unchanged": True,
    }
    check(stored["gates"] == gates, "gates")
    check(gates["all_seven_public_folios_expected_direction_both_ensembles"] and gates["all_public_role_folio_cells_expected_direction"], "broad-block")
    check(not gates["circle_specific_both_metrics_stronger"] and gates["outside_label_also_has_both_tails_p_at_most_01"], "not-specific")
    target = json.loads(TARGET.read_text())
    check(all(digests[value] == target["evaluation"][value]["shift_sha256"] for value in ENSEMBLES), "target-orbits")
    concentration = json.loads(CONCENTRATION_JSON.read_text())
    check(all(value["maximum_favored_folio"] == "f68" for value in concentration["ensembles"].values()), "f68-source")
    check(PRODUCTION_REPORT.read_text() == report_text(summaries), "report-bytes")

    mutations = {}
    for name, mutate in (
        ("missing_f71", lambda rows: [row for row in rows if row["page"] != "f71r"]),
        ("duplicate_page", lambda rows: rows + [dict(rows[0])]),
        ("bad_catalogue_status", lambda rows: [dict(row, catalogue_match_status="UNKNOWN") if row["page"] == "f67r1" else row for row in rows]),
        ("missing_circle_evidence", lambda rows: [dict(row, source_tags="TEXT_LABELS") if row["page"] == "f70v2" else row for row in rows]),
        ("wrong_source_url", lambda rows: [dict(row, source_url="https://www.voynich.nu/q09/index.html#f73v") if row["page"] == "f73v" else row for row in rows]),
    ):
        try:
            source_projection(mutate(selected))
        except ValueError:
            mutations[name] = True
        else:
            mutations[name] = False
    check(all(mutations.values()), "mutations")
    if failures:
        raise SystemExit("validation failed: " + failures[0])
    result = {
        "experiment": "SOURCE_NATIVE_CIRCLE_BLOCK_DIAGNOSTIC_VALIDATION",
        "status": "PASS_AUDITOR_FREE_18_ROW_PUBLIC_CIRCLE_BLOCK_RECONSTRUCTION",
        "checks": checks,
        "failures": [],
        "reconstructed_rows": len(rows),
        "public_page_rows": len(selected),
        "public_folios": list(FOLIOS),
        "all_seven_folios_expected_direction_both_ensembles": True,
        "all_role_folio_cells_expected_direction": True,
        "circle_specific_confirmed": False,
        "mutations": mutations,
        "inputs": {path.name: sha(path) for path in FROZEN},
        "validator_sha256": sha(VALIDATOR),
        "english_glosses": 0,
        "claim_ceiling": "Auditor-free reconstruction of the retrospective public circle-block localization only; no circle-specific grammar, ownership, parameter, word, sound, language, cipher, plaintext, meaning, or translation follows.",
    }
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(f"""# Public circle-block diagnostic validation

Status: **{result['status']}**

An auditor-free implementation reconstructs the exact 26-page public source
projection, both complete 8,192-assignment orbits, all **18** output rows, role
and folio support, gates, TSV bytes, and report in **{checks}** checks.  All five
source-membership mutations stop.  Folio f71 is mandatory.

The validation confirms broad multi-role structure across f67--f73 but no
circle-specific effect.  The original diagnostic-transfer nonconfirmation is
unchanged, and no meaning or translation follows.
""")
    print(json.dumps({"status": result["status"], "checks": checks}, sort_keys=True))


if __name__ == "__main__":
    main()
