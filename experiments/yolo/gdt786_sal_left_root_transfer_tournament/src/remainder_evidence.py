#!/usr/bin/env python3
"""Independent remainder-lineage evidence for the twelve GDT786 ``sal+X`` wholes.

The data in this module are an audit input, not a renderer dictionary.  In
particular, a role observed for a complete remainder surface is not exported
as an EVA character, suffix, sound, or lexeme.  ``compute`` checks its fixed
cohort against both ``TARGET_12_SPECS.tsv`` and GDT785's reader-stable family
census before returning any records.
"""

from __future__ import annotations

import csv
import sys
from copy import deepcopy
from pathlib import Path

sys.dont_write_bytecode = True


TARGET_SPECS = Path(
    "experiments/yolo/gdt786_sal_left_root_transfer_tournament/src/"
    "TARGET_12_SPECS.tsv"
)
GDT785_FAMILY = Path(
    "experiments/yolo/gdt785_sal_exact_whole_field_census/artifacts/"
    "GDT785_23_SAL_STRING_FAMILY.tsv"
)
EXPERIMENT_INDEX = Path("experiments/EXPERIMENT_INDEX.tsv")


# ``rank`` is a deterministic practical-strength order within this twelve-form
# audit.  It is not a probability and does not establish a plaintext word.
_AUDIT_ROWS: tuple[dict[str, object], ...] = (
    {
        "surface": "salal",
        "remainder": "al",
        "reader_stable_n": 167,
        "current_independent_role": "MATERIAL_I_WHOLE_ROLE",
        "evidence_report_ids": ["GDT655", "GDT712", "GDT761", "GDT785"],
        "provenance_class": "FAMILY_BORN_LATER_ROLE_CARRIED",
        "retired_interpretations": [
            "Rohstoffklasse I or Rohdroge as an identified substance",
            "free A|L component split",
        ],
        "default_de": "Drogenmaterial I",
        "rivals_de": [
            "Arzneizutat, Materialstufe I",
            "eigenständiger Drogenname",
        ],
        "rank": 5,
        "rank_label": "MEDIUM",
        "compositional_candidate": True,
    },
    {
        "surface": "salar",
        "remainder": "ar",
        "reader_stable_n": 242,
        "current_independent_role": "PART_SHARE_I_WHOLE_ROLE",
        "evidence_report_ids": ["GDT693", "GDT758", "GDT759", "GDT785"],
        "provenance_class": "LATER_MULTIWHOLE_ROLE_CARRIED",
        "retired_interpretations": [
            "Drogenfraktion as a necessarily separated product",
            "Droge supplied independently by ar; circular inside sal+ar",
        ],
        "default_de": "Drogenanteil I",
        "rivals_de": ["Drogenfraktion I", "Drogenklasse I"],
        "rank": 2,
        "rank_label": "MEDIUM_HIGH",
        "compositional_candidate": True,
    },
    {
        "surface": "saldal",
        "remainder": "dal",
        "reader_stable_n": 147,
        "current_independent_role": "MEASURED_MATERIAL_I_WHOLE_ROLE",
        "evidence_report_ids": ["GDT655", "GDT711", "GDT764", "GDT785"],
        "provenance_class": "FAMILY_BORN_LATER_ROLE_CARRIED",
        "retired_interpretations": [
            "Rohdroge as an identified material",
            "Dosis or a named historical unit",
            "free D|AL component split",
        ],
        "default_de": "abgemessenes Drogenmaterial I",
        "rivals_de": [
            "Drogenposten mit Messwert I",
            "Drogenmaterial I ohne Messbehauptung",
        ],
        "rank": 4,
        "rank_label": "MEDIUM",
        "compositional_candidate": True,
    },
    {
        "surface": "saldam",
        "remainder": "dam",
        "reader_stable_n": 37,
        "current_independent_role": "MEASURE_I_FAMILY_ROLE_ONLY",
        "evidence_report_ids": ["GDT661", "GDT711", "GDT785"],
        "provenance_class": "SOURCE_COMPOSED_WEAK",
        "retired_interpretations": [
            "Dosis I",
            "identified historical measure unit",
            "portable D+AM component semantics",
        ],
        "default_de": "abgemessene Drogenmenge I",
        "rivals_de": ["Drogenmaß I", "eigenständiger Drogenname"],
        "rank": 7,
        "rank_label": "LOW",
        "compositional_candidate": False,
    },
    {
        "surface": "saldy",
        "remainder": "dy",
        "reader_stable_n": 149,
        "current_independent_role": "STRUCTURAL_BOUNDARY_OR_ENDPOINT_ONLY",
        "evidence_report_ids": ["GDT687", "GDT725", "GDT785"],
        "provenance_class": "STRUCTURAL_ONLY_NOT_SUFFIX_EXPORTABLE",
        "retired_interpretations": [
            "free dy as a spoken closing command",
            "owner-local S+AL+DY target-and-close composition as a portable word",
        ],
        "default_de": "Drogenposten, abgeschlossen",
        "rivals_de": ["Fertigdroge", "lokales Ziel- oder Abschlusskennzeichen"],
        "rank": 9,
        "rank_label": "LOW",
        "compositional_candidate": False,
    },
    {
        "surface": "salf",
        "remainder": "f",
        "reader_stable_n": 4,
        "current_independent_role": "NONE",
        "evidence_report_ids": ["GDT515", "GDT539", "GDT734", "GDT785"],
        "provenance_class": "RETIRED_OWNER_LOCAL_MARK",
        "retired_interpretations": [
            "LOCAL_CHAR_F equals hier",
            "LOCAL_CHAR_F equals Feinform",
            "S+AL+LOCAL_CHAR_F address composition as portable semantics",
        ],
        "default_de": "Drogenkennzeichen",
        "rivals_de": ["Drogenname", "fein zerkleinerte Droge"],
        "rank": 11,
        "rank_label": "VERY_LOW",
        "compositional_candidate": False,
    },
    {
        "surface": "salkeedy",
        "remainder": "keedy",
        "reader_stable_n": 22,
        "current_independent_role": "HOT_END_STAGE_CLOSED_EXACT_WHOLE_ROLE",
        "evidence_report_ids": ["GDT647", "GDT785"],
        "provenance_class": "STRONG_LEARNED_WHOLE_FAMILY_ROLE",
        "retired_interpretations": [
            "global dy, edy, or eedy suffix export",
            "specific preparation or substance identity supplied by keedy",
        ],
        "default_de": "heiße Fertigdroge am Gradende",
        "rivals_de": [
            "heiße Droge am Gradende, noch nicht fertig",
            "heißes Fertigpräparat",
        ],
        "rank": 1,
        "rank_label": "HIGH",
        "compositional_candidate": True,
    },
    {
        "surface": "salo",
        "remainder": "o",
        "reader_stable_n": 33,
        "current_independent_role": "NO_PORTABLE_ROLE__LOW_PREPARATION_FRAME_RIVAL",
        "evidence_report_ids": ["GDT664", "GDT737", "GDT738", "GDT785"],
        "provenance_class": "RETIRED_IDENTITY_WEAK_ROLE_RIVAL",
        "retired_interpretations": [
            "Ansatzwasser",
            "water or liquid identity",
            "unconditional preparation-carrier transfer",
        ],
        "default_de": "Drogenansatz",
        "rivals_de": ["Drogenposten", "flüssige Drogenzubereitung"],
        "rank": 8,
        "rank_label": "LOW",
        "compositional_candidate": False,
    },
    {
        "surface": "salol",
        "remainder": "ol",
        "reader_stable_n": 376,
        "current_independent_role": "PREPARATION_CONTENT_RECORD_HEAD_OR_LINKER",
        "evidence_report_ids": [
            "GDT683", "GDT711", "GDT762", "GDT769", "GDT773", "GDT774", "GDT785"
        ],
        "provenance_class": "LATER_CONTEXTUAL_ROLE_CARRIED",
        "retired_interpretations": [
            "universal Ansatz head",
            "oil, water, wine, vinegar, or other specific medium identity",
            "free ol suffix semantics",
        ],
        "default_de": "Drogenzubereitung",
        "rivals_de": [
            "Drogenansatz",
            "Drogenposten mit Mengen- oder Feldanschluss",
        ],
        "rank": 3,
        "rank_label": "MEDIUM_HIGH",
        "compositional_candidate": True,
    },
    {
        "surface": "salshcthdy",
        "remainder": "shcthdy",
        "reader_stable_n": 1,
        "current_independent_role": "NONE",
        "evidence_report_ids": ["GDT631", "GDT632", "GDT633", "GDT748", "GDT785"],
        "provenance_class": "RETIRED_SOURCE_COMPOSITION_REOPENED",
        "retired_interpretations": [
            "SH+CTH+DY as a portable moist plant-part or material expression",
            "bound dy automatically supplying completion",
        ],
        "default_de": "feuchte Fertigdroge",
        "rivals_de": ["getrocknete Fertigdroge", "opaker Drogenname"],
        "rank": 12,
        "rank_label": "VERY_LOW",
        "compositional_candidate": False,
    },
    {
        "surface": "saltar",
        "remainder": "tar",
        "reader_stable_n": 33,
        "current_independent_role": "COLD_SHARE_I_PARTIAL_WHOLE_ROLE",
        "evidence_report_ids": ["GDT693", "GDT758", "GDT759", "GDT785"],
        "provenance_class": "PARTIALLY_LATER_CARRIED",
        "retired_interpretations": [
            "Droge supplied independently by tar; circular inside sal+tar",
            "Fraktion as a necessarily separated product",
            "cold or share value exported from individual EVA characters",
        ],
        "default_de": "kalter Drogenanteil I",
        "rivals_de": ["Drogenanteil I ohne Kälte", "kalte Drogenklasse I"],
        "rank": 6,
        "rank_label": "MEDIUM_LOW",
        "compositional_candidate": True,
    },
    {
        "surface": "saly",
        "remainder": "y",
        "reader_stable_n": 84,
        "current_independent_role": "STRUCTURAL_LINK_OR_STOP_ONLY",
        "evidence_report_ids": ["GDT687", "GDT725", "GDT738", "GDT785"],
        "provenance_class": "STRUCTURAL_ONLY_NOT_SUFFIX_EXPORTABLE",
        "retired_interpretations": [
            "global y as a base-form or final-state suffix",
            "owner-local S+AL+Y select-target-item composition as portable semantics",
            "naked y as a universal spoken word",
        ],
        "default_de": "Drogenposten",
        "rivals_de": ["Fertigdroge", "Anschluss- oder Zieldrogenposten"],
        "rank": 10,
        "rank_label": "LOW",
        "compositional_candidate": False,
    },
)


def _read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise AssertionError(f"TSV has no header: {path}")
        return list(reader)


def _unique_by_surface(
    rows: list[dict[str, str]], path: Path
) -> tuple[list[str], dict[str, dict[str, str]]]:
    order: list[str] = []
    result: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        surface = row.get("surface", "").strip()
        if not surface:
            raise AssertionError(f"blank surface at {path}:{row_number}")
        if surface in result:
            raise AssertionError(f"duplicate surface {surface!r} in {path}")
        order.append(surface)
        result[surface] = row
    return order, result


def _assert_same_surface_set(
    label: str, observed: set[str], expected: set[str]
) -> None:
    if observed == expected:
        return
    missing = sorted(expected - observed)
    unexpected = sorted(observed - expected)
    raise AssertionError(
        f"{label} surface-set mismatch: missing={missing}, unexpected={unexpected}"
    )


def compute(repo_root: Path) -> dict[str, object]:
    """Validate and return the independent twelve-form remainder audit.

    The function intentionally fails before returning partial data when the
    target specification, fixed audit, or GDT785 family census disagree about
    the surface set, a remainder, or a reader-stable remainder count.
    """

    root = Path(repo_root).resolve()
    target_path = root / TARGET_SPECS
    family_path = root / GDT785_FAMILY
    index_path = root / EXPERIMENT_INDEX

    fixed_by_surface = {str(row["surface"]): row for row in _AUDIT_ROWS}
    if len(fixed_by_surface) != len(_AUDIT_ROWS):
        raise AssertionError("duplicate surface in fixed remainder audit")
    if len(fixed_by_surface) != 12:
        raise AssertionError(
            "fixed remainder audit must have 12 surfaces, "
            f"got {len(fixed_by_surface)}"
        )
    if sorted(int(row["rank"]) for row in _AUDIT_ROWS) != list(range(1, 13)):
        raise AssertionError("fixed remainder ranks must be the unique integers 1..12")
    if any(len(list(row["rivals_de"])) != 2 for row in _AUDIT_ROWS):
        raise AssertionError("every remainder audit row must have exactly two rivals")

    target_rows = _read_tsv(target_path)
    target_order, target_by_surface = _unique_by_surface(target_rows, target_path)
    expected = set(fixed_by_surface)
    _assert_same_surface_set(
        "TARGET_12_SPECS", set(target_by_surface), expected
    )

    for surface in target_order:
        target_remainder = target_by_surface[surface].get("remainder", "").strip()
        fixed_remainder = str(fixed_by_surface[surface]["remainder"])
        if target_remainder != fixed_remainder:
            raise AssertionError(
                f"remainder mismatch for {surface}: "
                f"TARGET_12_SPECS={target_remainder!r}, audit={fixed_remainder!r}"
            )

    family_rows = _read_tsv(family_path)
    selected_family_rows = [
        row for row in family_rows if row.get("surface", "").strip() in expected
    ]
    _, family_by_surface = _unique_by_surface(selected_family_rows, family_path)
    _assert_same_surface_set(
        "GDT785 family target subset", set(family_by_surface), expected
    )

    for surface in target_order:
        audit = fixed_by_surface[surface]
        family = family_by_surface[surface]
        family_remainder = family.get("outer_remainder", "").strip()
        if family_remainder != audit["remainder"]:
            raise AssertionError(
                f"GDT785 remainder mismatch for {surface}: "
                f"family={family_remainder!r}, audit={audit['remainder']!r}"
            )
        count_text = family.get(
            "outer_remainder_reader_exact_occurrences", ""
        ).strip()
        try:
            family_count = int(count_text)
        except ValueError as exc:
            raise AssertionError(
                f"invalid GDT785 reader-stable count for {surface}: {count_text!r}"
            ) from exc
        if family_count != audit["reader_stable_n"]:
            raise AssertionError(
                f"GDT785 count mismatch for {surface}: "
                f"family={family_count}, audit={audit['reader_stable_n']}"
            )

    index_rows = _read_tsv(index_path)
    report_ids = {
        row.get("experiment_id", "").strip()
        for row in index_rows
        if row.get("experiment_id", "").strip()
    }
    cited_ids = {
        str(report_id)
        for row in _AUDIT_ROWS
        for report_id in list(row["evidence_report_ids"])
    }
    missing_report_ids = sorted(cited_ids - report_ids)
    if missing_report_ids:
        raise AssertionError(
            f"remainder audit cites report IDs absent from EXPERIMENT_INDEX: {missing_report_ids}"
        )

    # Preserve TARGET_12_SPECS row order so downstream joins never silently
    # acquire the independent confidence ranking as a new document order.
    records = [deepcopy(fixed_by_surface[surface]) for surface in target_order]
    by_surface = {str(row["surface"]): deepcopy(row) for row in records}
    compositional = [
        surface
        for surface in target_order
        if bool(fixed_by_surface[surface]["compositional_candidate"])
    ]

    return {
        "records": records,
        "by_surface": by_surface,
        "surface_order": target_order,
        "surface_count": len(records),
        "compositional_candidates": compositional,
        "compositional_candidate_count": len(compositional),
        "qa": {
            "target_surface_set_exact": True,
            "gdt785_surface_set_exact": True,
            "target_remainders_exact": True,
            "gdt785_remainders_exact": True,
            "gdt785_reader_stable_counts_exact": True,
            "evidence_report_ids_in_index": True,
            "fixed_rank_permutation_1_to_12": True,
            "individual_eva_character_export": False,
            "confirmed_lexemes": 0,
        },
    }


__all__ = ["compute"]
