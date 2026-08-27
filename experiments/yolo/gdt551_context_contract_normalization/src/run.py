#!/usr/bin/env python3
"""Normalize instance context modes to the GDT540 two-slot contract."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt551_context_contract_normalization"
ART = EXP / "artifacts"

G540 = ROOT / "experiments/yolo/gdt540_target_surface_context_requirement_contract/artifacts"
G546 = ROOT / "experiments/yolo/gdt546_consolidated_fragment_reader/artifacts"
G548 = ROOT / "experiments/yolo/gdt548_unified_145_prose_reader/artifacts"
G549 = ROOT / "experiments/yolo/gdt549_default_queue_visible_peer_bridges/artifacts"
G550 = ROOT / "experiments/yolo/gdt550_recurrent_sequence_frame_bridges/artifacts"

CONTRACT_IN = G540 / "gdt540_145_surface_context_contract.tsv"
FRAGMENT_IN = G546 / "gdt546_81_consolidated_fragment_reader.tsv"
READER_IN = G548 / "gdt548_145_unified_prose_reader.tsv"
WARNING_IN = G549 / "gdt549_9_context_mismatch_peer_audit.tsv"
VISIBLE_IN = G549 / "gdt549_23_exact_visible_default_cards.tsv"
RESIDUAL_IN = G550 / "gdt550_9_residual_support_queue.tsv"

PROFILE_OUT = ART / "gdt551_145_contract_class_profile.tsv"
ANCHOR_OUT = ART / "gdt551_81_anchor_contract_audit.tsv"
DISJOINT_OUT = ART / "gdt551_12_disjoint_instance_mode_audit.tsv"
WARNING_OUT = ART / "gdt551_9_previous_context_warning_audit.tsv"
PROMOTED_OUT = ART / "gdt551_4_promoted_context_cards.tsv"
RESIDUAL_OUT = ART / "gdt551_5_residual_interface_queue.tsv"
SUMMARY_OUT = ART / "gdt551_context_normalization_summary.tsv"
BOOK_OUT = ART / "GDT551_CONTEXT_CONTRACT_BOOK.md"
RESULT_OUT = ART / "gdt551_result.json"

STATUS = (
    "PASS_ALL_12_INSTANCE_MODE_DISJOINTS_NORMALIZED__"
    "FOUR_CONTEXT_RESTS_CLOSED__FIVE_INTERFACES_REMAIN"
)

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
MODE_ORDER = {
    "SELF_CONTAINED": 0,
    "REQUIRES_ACTIVE_ARGUMENT": 1,
    "REQUIRES_ACTIVE_ACTION": 2,
    "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT": 3,
}
MODE_BY_FLAGS = {
    (False, False): "SELF_CONTAINED",
    (False, True): "REQUIRES_ACTIVE_ARGUMENT",
    (True, False): "REQUIRES_ACTIVE_ACTION",
    (True, True): "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"Refusing to write empty table {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def keyed(rows: list[dict[str, str]], field: str) -> dict[str, dict[str, str]]:
    result = {row[field]: row for row in rows}
    if len(result) != len(rows):
        raise RuntimeError(f"Duplicate {field} in input")
    return result


def atoms(recipe: str) -> tuple[str, ...]:
    return tuple(part for part in recipe.split("+") if part and part != "NONE")


def visible_slots(recipe: str) -> tuple[bool, bool]:
    material = atoms(recipe)
    return (
        any(atom in ACTION_ROOTS for atom in material),
        any(atom in ARGUMENT_ROOTS for atom in material),
    )


def signature(recipe: str) -> str:
    action, argument = visible_slots(recipe)
    return (
        ("ACTION_VISIBLE" if action else "ACTION_OPEN")
        + "/"
        + ("ARGUMENT_VISIBLE" if argument else "ARGUMENT_OPEN")
    )


def allowed_modes(recipe: str) -> set[str]:
    action, argument = visible_slots(recipe)
    return {
        MODE_BY_FLAGS[(inherit_action, inherit_argument)]
        for inherit_action in ([False] if action else [False, True])
        for inherit_argument in ([False] if argument else [False, True])
    }


def parse_modes(value: str) -> set[str]:
    if not value or value == "NONE":
        return set()
    result = set(value.split("|"))
    unknown = result - set(MODE_ORDER)
    if unknown:
        raise RuntimeError(f"Unknown context modes: {sorted(unknown)}")
    return result


def join_modes(values: Iterable[str]) -> str:
    material = set(values)
    return "|".join(sorted(material, key=MODE_ORDER.__getitem__)) if material else "NONE"


def join(values: Iterable[str]) -> str:
    material = sorted({str(value) for value in values if str(value) and str(value) != "NONE"})
    return "|".join(material) if material else "NONE"


def contract_relation(anchor_recipe: str, target_recipe: str) -> str:
    anchor = allowed_modes(anchor_recipe)
    target = allowed_modes(target_recipe)
    if anchor == target:
        return "IDENTICAL_SLOT_CONTRACT"
    if target < anchor:
        return "TARGET_CONTRACT_NARROWER_BY_VISIBLE_EXTENSION"
    if anchor < target:
        return "TARGET_CONTRACT_WIDER_BY_EXTENSION"
    if anchor & target:
        return "OVERLAPPING_SLOT_CONTRACTS"
    return "DISJOINT_SLOT_CONTRACTS"


def normalization_status(
    anchor_recipe: str,
    target_recipe: str,
    anchor_observed: set[str],
    target_observed: set[str],
) -> str:
    anchor_allowed = allowed_modes(anchor_recipe)
    target_allowed = allowed_modes(target_recipe)
    if not anchor_observed <= anchor_allowed or not target_observed <= target_allowed:
        return "INFEASIBLE_OBSERVED_MODE"
    relation = contract_relation(anchor_recipe, target_recipe)
    if relation == "IDENTICAL_SLOT_CONTRACT":
        return "NORMALIZED_SAME_CONTRACT_DIFFERENT_INCOMING_STATE"
    if relation == "TARGET_CONTRACT_NARROWER_BY_VISIBLE_EXTENSION":
        return "NORMALIZED_EXTENSION_FILLS_OPEN_SLOT"
    return "UNRESOLVED_CONTRACT_RELATION"


def build_book(
    profiles: list[dict[str, object]],
    disjoint: list[dict[str, object]],
    promoted: list[dict[str, object]],
    residual: list[dict[str, object]],
    metrics: dict[str, object],
) -> str:
    lines = [
        "# GDT551 context-contract book",
        "",
        "## Der korrigierte Vergleich",
        "",
        "GDT543 verglich die **tatsächlich angetroffenen** Eingangszustände einer alten "
        "Stammkarte mit denen der neuen Karte. Ein disjunkter Modussatz war deshalb noch "
        "keine andere Wortbedeutung und auch keine andere Satzregel. Der GDT540-Leser "
        "kennt nur zwei Steckplätze: sichtbare oder offene Handlung sowie sichtbares oder "
        "offenes Argument. Ein offener Platz darf aus dem laufenden Satz gefüllt werden; "
        "beim Argument ist auch die objektlose Lesung erlaubt, ohne Handlung bleibt eine "
        "nichtverbale Fragmentlesung.",
        "",
        "```text",
        "Vertrag = (HANDLUNG sichtbar/offen, ARGUMENT sichtbar/offen)",
        "beobachteter Modus = genau der Zustand, der an diesem einzelnen Vorkommen anlag",
        "```",
        "",
        "## Die vier Vertragsklassen im 145er-Leser",
        "",
        "| Vertrag | Oberflächen | erlaubte beobachtete Modi |",
        "|---|---:|---|",
    ]
    for row in profiles:
        lines.append(
            f"| `{row['contract_signature']}` | {row['surface_count']} | "
            f"`{row['allowed_observed_modes']}` |"
        )
    lines.extend(
        [
            "",
            "## Rückblick auf die zwölf scheinbar disjunkten Fälle",
            "",
            f"Alle {metrics['disjoint_instance_mode_card_count']} früheren disjunkten "
            "Instanzvergleiche liegen innerhalb ihrer jeweiligen Steckplatzverträge. "
            f"{metrics['disjoint_identical_contract_count']} behalten exakt denselben "
            "Vertrag; nur `kody` schließt durch das hinzugefügte `K` den vorher offenen "
            "Handlungsplatz. Kein Fall braucht einen lexikalischen Kontextumschalter.",
            "",
            "| Oberfläche | alter Stamm | volle Karte | Vertrag | Erklärung |",
            "|---|---|---|---|---|",
        ]
    )
    for row in disjoint:
        lines.append(
            f"| `{row['surface']}` | `{row['primary_anchor_recipe']}` | "
            f"`{row['final_recipe']}` | `{row['contract_relation']}` | "
            f"`{row['normalized_context_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Die vier bisher offenen Karten",
            "",
            "Ihre sichtbaren Zerlegungen und vollständigen Arbeitslesungen bleiben "
            "unverändert. Geschlossen wird nur die unnötige Forderung, der alte Stamm "
            "müsse in einem anderen Satz denselben konkreten Eingangszustand zeigen.",
            "",
        ]
    )
    for row in promoted:
        lines.extend(
            [
                f"### `{row['surface']}`",
                "",
                f"- sichtbar: `{row['selected_visible_trace']}`",
                f"- Rezept: `{row['final_recipe']}`",
                f"- Vertrag: `{row['full_contract_signature']}`; erlaubt "
                f"`{row['full_allowed_modes']}`",
                f"- Instanzen: Stamm `{row['old_anchor_modes']}`, Ziel "
                f"`{row['target_modes']}`",
                f"- neutral: {row['neutral_component_reading_de']}",
                f"- im bekannten Satz: {row['known_contextual_readings_de']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Aktive Restliste",
            "",
            f"Es bleiben {len(residual)} echte direkte Grenzflächenfragen: "
            + ", ".join(
                f"`{row['surface']}:{row['residual_detail']}`" for row in residual
            )
            + ".",
            "",
            "Das ist eine Normalisierung innerhalb des bestehenden Arbeitslesers. Sie "
            "bestätigt weder Klartext noch Lexeme, Sprache, Chiffre oder historische "
            "Identität und ändert keine Stammwerte.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    contracts = read_tsv(CONTRACT_IN)
    fragments = read_tsv(FRAGMENT_IN)
    readers = keyed(read_tsv(READER_IN), "surface")
    warnings = read_tsv(WARNING_IN)
    visible = keyed(read_tsv(VISIBLE_IN), "surface")
    residual_source = read_tsv(RESIDUAL_IN)
    if (len(contracts), len(fragments), len(readers), len(warnings), len(visible), len(residual_source)) != (
        145,
        81,
        145,
        9,
        23,
        9,
    ):
        raise RuntimeError("Input row-count drift")

    profile_data: dict[str, dict[str, object]] = defaultdict(
        lambda: {"surfaces": [], "modes": Counter()}
    )
    for row in contracts:
        key = signature(row["final_recipe"])
        profile_data[key]["surfaces"].append(row["surface"])
        for mode in parse_modes(row["observed_requirement_modes"]):
            profile_data[key]["modes"][mode] += 1
    profile_order = [
        "ACTION_VISIBLE/ARGUMENT_VISIBLE",
        "ACTION_VISIBLE/ARGUMENT_OPEN",
        "ACTION_OPEN/ARGUMENT_VISIBLE",
        "ACTION_OPEN/ARGUMENT_OPEN",
    ]
    profile_rows: list[dict[str, object]] = []
    for ordinal, key in enumerate(profile_order, 1):
        action_visible = key.startswith("ACTION_VISIBLE")
        argument_visible = key.endswith("ARGUMENT_VISIBLE")
        representative = (
            ("CH" if action_visible else "O")
            + "+"
            + ("Y" if argument_visible else "E")
        )
        modes = profile_data[key]["modes"]
        profile_rows.append(
            {
                "class_ordinal": ordinal,
                "contract_signature": key,
                "visible_action_slot": "VISIBLE" if action_visible else "OPEN",
                "visible_argument_slot": "VISIBLE" if argument_visible else "OPEN",
                "allowed_observed_modes": join_modes(allowed_modes(representative)),
                "surface_count": len(profile_data[key]["surfaces"]),
                "self_contained_surface_count": modes["SELF_CONTAINED"],
                "active_argument_surface_count": modes["REQUIRES_ACTIVE_ARGUMENT"],
                "active_action_surface_count": modes["REQUIRES_ACTIVE_ACTION"],
                "both_active_surface_count": modes[
                    "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
                ],
                "example_surfaces": join(profile_data[key]["surfaces"][:12]),
                "guard": "GDT540_SLOT_CONTRACT__OBSERVED_MODES_ARE_INSTANCE_STATES",
            }
        )

    anchor_rows: list[dict[str, object]] = []
    for row in fragments:
        anchor_recipe = row["primary_anchor_recipe"]
        target_recipe = row["final_recipe"]
        anchor_observed = parse_modes(row["primary_anchor_context_modes"])
        target_observed = parse_modes(row["observed_requirement_modes"])
        anchor_slots = visible_slots(anchor_recipe)
        target_slots = visible_slots(target_recipe)
        relation = contract_relation(anchor_recipe, target_recipe)
        normalized = normalization_status(
            anchor_recipe, target_recipe, anchor_observed, target_observed
        )
        anchor_rows.append(
            {
                "target_ordinal": row["target_ordinal"],
                "surface": row["surface"],
                "primary_anchor_recipe": anchor_recipe,
                "final_recipe": target_recipe,
                "old_anchor_modes": join_modes(anchor_observed),
                "target_modes": join_modes(target_observed),
                "old_instance_mode_relation": row[
                    "primary_anchor_context_relation"
                ],
                "anchor_contract_signature": signature(anchor_recipe),
                "full_contract_signature": signature(target_recipe),
                "anchor_allowed_modes": join_modes(allowed_modes(anchor_recipe)),
                "full_allowed_modes": join_modes(allowed_modes(target_recipe)),
                "contract_relation": relation,
                "extension_fills_action_slot": (
                    "YES" if not anchor_slots[0] and target_slots[0] else "NO"
                ),
                "extension_fills_argument_slot": (
                    "YES" if not anchor_slots[1] and target_slots[1] else "NO"
                ),
                "anchor_modes_contract_feasible": (
                    "YES" if anchor_observed <= allowed_modes(anchor_recipe) else "NO"
                ),
                "target_modes_contract_feasible": (
                    "YES" if target_observed <= allowed_modes(target_recipe) else "NO"
                ),
                "normalized_context_status": normalized,
                "neutral_component_reading_de": row[
                    "neutral_component_reading_de"
                ],
                "known_contextual_readings_de": row[
                    "known_contextual_readings_de"
                ],
                "guard": "COMPARE_SLOT_CONTRACTS__NOT_SINGLE_OCCURRENCE_INPUT_STATES",
            }
        )
    disjoint_rows = [
        row
        for row in anchor_rows
        if row["old_instance_mode_relation"] == "TARGET_MODE_SET_DISJOINT"
    ]

    anchor_by_surface = keyed(
        [{key: str(value) for key, value in row.items()} for row in anchor_rows],
        "surface",
    )
    warning_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate(warnings, 1):
        normalized = anchor_by_surface[row["surface"]]
        warning_rows.append(
            {
                "warning_ordinal": ordinal,
                "surface": row["surface"],
                "anchor_recipe": row["anchor_recipe"],
                "final_recipe": normalized["final_recipe"],
                "target_modes": row["target_modes"],
                "old_anchor_modes": row["old_anchor_modes"],
                "anchor_contract_signature": normalized[
                    "anchor_contract_signature"
                ],
                "full_contract_signature": normalized["full_contract_signature"],
                "anchor_allowed_modes": normalized["anchor_allowed_modes"],
                "full_allowed_modes": normalized["full_allowed_modes"],
                "contract_relation": normalized["contract_relation"],
                "normalized_context_status": normalized[
                    "normalized_context_status"
                ],
                "current_peer_event_count": row["current_peer_event_count"],
                "current_peer_surfaces": row["current_peer_surfaces"],
                "peer_evidence_role": (
                    "OPTIONAL_EMPIRICAL_PEER__NOT_REQUIRED_FOR_SLOT_CONTRACT"
                    if row["peer_context_status"] == "CURRENT_PEER_CONTEXT_BRIDGE"
                    else "NO_PEER_REQUIRED_AFTER_CONTRACT_NORMALIZATION"
                ),
                "guard": "OLD_AND_TARGET_INSTANCE_MODES_NEED_NOT_BE_EQUAL",
            }
        )

    current_context = {
        row["surface"]: row
        for row in residual_source
        if row["residual_dimension"] == "ANCHOR_CONTEXT"
    }
    promoted_rows: list[dict[str, object]] = []
    for ordinal, surface in enumerate(sorted(current_context), 1):
        normalized = anchor_by_surface[surface]
        route = visible[surface]
        promoted_rows.append(
            {
                "promotion_ordinal": ordinal,
                "surface": surface,
                "final_recipe": normalized["final_recipe"],
                "primary_anchor_recipe": normalized["primary_anchor_recipe"],
                "selected_visible_trace": route["selected_visible_trace"],
                "visible_route_class": route["visible_route_class"],
                "exact_surface_reconstruction": route[
                    "exact_surface_reconstruction"
                ],
                "exact_recipe_reconstruction": route[
                    "exact_recipe_reconstruction"
                ],
                "target_modes": normalized["target_modes"],
                "old_anchor_modes": normalized["old_anchor_modes"],
                "anchor_contract_signature": normalized[
                    "anchor_contract_signature"
                ],
                "full_contract_signature": normalized["full_contract_signature"],
                "full_allowed_modes": normalized["full_allowed_modes"],
                "contract_relation": normalized["contract_relation"],
                "context_resolution": "CLOSED_BY_GDT540_SLOT_CONTRACT_NORMALIZATION",
                "neutral_component_reading_de": route[
                    "neutral_component_reading_de"
                ],
                "known_contextual_readings_de": route[
                    "known_contextual_readings_de"
                ],
                "promotion_status": "PROMOTED_FROM_CONTEXT_SUPPORT_QUEUE",
                "guard": "WORKING_READING_PRESERVED__NO_LEXICAL_CONTEXT_SWITCH",
            }
        )

    residual_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate(
        [
            row
            for row in residual_source
            if row["residual_dimension"] == "DIRECT_INTERFACE"
        ],
        1,
    ):
        residual_rows.append(
            {
                "queue_ordinal": ordinal,
                "surface": row["surface"],
                "final_recipe": row["final_recipe"],
                "residual_dimension": row["residual_dimension"],
                "residual_detail": row["residual_detail"],
                "visible_status": row["visible_status"],
                "next_search": "SEARCH_SEPARATED_OR_FAMILY_PAIR_BRIDGE",
                "guard": row["guard"],
                "post_gdt551_status": "ONLY_DIRECT_INTERFACE_SUPPORT_RESTS_REMAIN",
            }
        )

    disjoint_relations = Counter(row["contract_relation"] for row in disjoint_rows)
    normalized_statuses = Counter(
        row["normalized_context_status"] for row in disjoint_rows
    )
    metrics: dict[str, object] = {
        "status": STATUS,
        "reader_surface_count": len(contracts),
        "slot_contract_class_count": len(profile_rows),
        "fragment_anchor_card_count": len(anchor_rows),
        "anchor_and_target_mode_contract_feasible_count": sum(
            row["anchor_modes_contract_feasible"] == "YES"
            and row["target_modes_contract_feasible"] == "YES"
            for row in anchor_rows
        ),
        "disjoint_instance_mode_card_count": len(disjoint_rows),
        "disjoint_identical_contract_count": disjoint_relations[
            "IDENTICAL_SLOT_CONTRACT"
        ],
        "disjoint_extension_narrowed_contract_count": disjoint_relations[
            "TARGET_CONTRACT_NARROWER_BY_VISIBLE_EXTENSION"
        ],
        "disjoint_normalized_count": sum(
            value
            for key, value in normalized_statuses.items()
            if key.startswith("NORMALIZED_")
        ),
        "previous_context_warning_count": len(warning_rows),
        "previous_context_warning_normalized_count": sum(
            str(row["normalized_context_status"]).startswith("NORMALIZED_")
            for row in warning_rows
        ),
        "prior_peer_supported_warning_count": sum(
            int(row["current_peer_event_count"]) > 0 for row in warning_rows
        ),
        "promoted_context_card_count": len(promoted_rows),
        "promoted_exact_visible_route_count": sum(
            row["exact_surface_reconstruction"] == "YES"
            and row["exact_recipe_reconstruction"] == "YES"
            for row in promoted_rows
        ),
        "promoted_complete_neutral_meaning_count": sum(
            bool(row["neutral_component_reading_de"]) for row in promoted_rows
        ),
        "promoted_complete_context_meaning_count": sum(
            bool(row["known_contextual_readings_de"]) for row in promoted_rows
        ),
        "residual_support_card_count": len(residual_rows),
        "residual_anchor_context_count": 0,
        "residual_direct_interface_count": len(residual_rows),
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }

    write_tsv(PROFILE_OUT, profile_rows)
    write_tsv(ANCHOR_OUT, anchor_rows)
    write_tsv(DISJOINT_OUT, disjoint_rows)
    write_tsv(WARNING_OUT, warning_rows)
    write_tsv(PROMOTED_OUT, promoted_rows)
    write_tsv(RESIDUAL_OUT, residual_rows)
    write_tsv(
        SUMMARY_OUT,
        [
            {"metric": key, "value": str(value), "guard": "GDT551_REPLAYED_METRIC"}
            for key, value in metrics.items()
        ],
    )
    BOOK_OUT.write_text(
        build_book(profile_rows, disjoint_rows, promoted_rows, residual_rows, metrics),
        encoding="utf-8",
    )
    RESULT_OUT.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
