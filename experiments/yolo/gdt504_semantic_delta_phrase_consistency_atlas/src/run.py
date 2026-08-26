#!/usr/bin/env python3
"""Turn the 46 GDT502 comparisons into explicit semantic phrase deltas."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt504_semantic_delta_phrase_consistency_atlas"
ART = BASE / "artifacts"
G413 = ROOT / "experiments/yolo/gdt413_twenty_six_page_semantic_working_edition/artifacts"
G415 = ROOT / "experiments/yolo/gdt415_owner_local_semantic_expansion_atlas/artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G502 = ROOT / "experiments/yolo/gdt502_supported_frontier_comparison_cards/artifacts"

CARDS_IN = G502 / "gdt502_46_supported_frontier_cards.tsv"
CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
DICTIONARY_IN = G413 / "gdt413_46_component_working_dictionary.tsv"
EXPANSIONS_IN = G415 / "gdt415_95_register_expansion_atlas.tsv"
CARDS_OUT = ART / "gdt504_46_semantic_delta_cards.tsv"
EFFECTS_OUT = ART / "gdt504_59_token_effect_checks.tsv"
OPERATIONS_OUT = ART / "gdt504_14_delta_operation_summary.tsv"
ATOMS_OUT = ART / "gdt504_10_atom_effect_summary.tsv"
REGISTERS_OUT = ART / "gdt504_5_register_delta_coverage.tsv"
DEPTH_OUT = ART / "gdt504_3_support_depth_summary.tsv"
READABLE_OUT = ART / "GDT504_SEMANTIC_DELTA_PHRASE_ATLAS.md"
RESULT_OUT = ART / "gdt504_result.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
REGISTERS = ("SOURCE_SECTION_T", "HERBAL", "BIOLOGICAL", "CELESTIAL", "PHARMA")
PAIR_CHANNELS = {"ORDERED_PAIR_TARGET_REGISTER", "ORDERED_PAIR_OTHER_REGISTER"}
STATUS = "FORTY_SIX_PHRASE_DELTAS_RESOLVE_WITH_FIXED_VALUES__PAIR_FRAME_EDITS_REMAIN_SEPARATE"
GUARD = "EDITORIAL_SEMANTIC_DELTA_ONLY__NO_TARGET_OBSERVATION_OR_SURFACE_PREDICTION"

OPERATION_ORDER = (
    "ADD_DESTINATION",
    "ADD_UNIT_ARGUMENT",
    "ADD_SECOND_POST_ARGUMENT",
    "EXPLICITIZE_INHERITED_POST",
    "ADD_SERIAL_ACTION",
    "ADD_SERIAL_ACTION_AND_GRADE",
    "COUNTED_REPEAT",
    "COUNTED_REPEAT_AND_EXPLICITIZE_POST",
    "PAIR_REPLACE_CARRIER_CONTEXT_WITH_POST",
    "PAIR_REPLACE_CARRIER_CONTEXT_WITH_GRADE",
    "PAIR_DROP_CONTINUATION",
    "PAIR_DROP_ORIGIN",
    "PAIR_CONTEXTUALIZE_REPEAT_ARGUMENTS",
    "PAIR_CONTEXTUALIZE_AND_DROP_ADDRESS",
)

OPERATION_EFFECT_DE = {
    "ADD_DESTINATION": "Der Zielsatz ergänzt genau die owner-lokale Zielangabe.",
    "ADD_UNIT_ARGUMENT": "Der Zielsatz ergänzt die owner-lokale Einheit als zweites Argument.",
    "ADD_SECOND_POST_ARGUMENT": "Der Zielsatz ergänzt den owner-lokalen Posten neben der Einheit.",
    "EXPLICITIZE_INHERITED_POST": "Der schon sprachlich geerbte Posten wird im Rezept ausdrücklich gesetzt.",
    "ADD_SERIAL_ACTION": "Der Zielsatz ergänzt genau eine weitere Handlung in sichtbarer Reihenfolge.",
    "ADD_SERIAL_ACTION_AND_GRADE": "Der Zielsatz ergänzt eine weitere Handlung samt Grad I.",
    "COUNTED_REPEAT": "Der zweite gleiche Handlungskopf wird flüssig als zweimal realisiert.",
    "COUNTED_REPEAT_AND_EXPLICITIZE_POST": "Zweimal realisiert die Wiederholung; der zuvor geerbte Posten wird explizit.",
    "PAIR_REPLACE_CARRIER_CONTEXT_WITH_POST": "Das alte Handlungspaar bleibt; Ausführung/Fortsetzung weichen dem expliziten Posten.",
    "PAIR_REPLACE_CARRIER_CONTEXT_WITH_GRADE": "Das alte Handlungspaar bleibt; Ausführung/Ausgang weichen Grad I.",
    "PAIR_DROP_CONTINUATION": "Das alte Handlungspaar bleibt; nur die fremde Fortsetzungsangabe fällt weg.",
    "PAIR_DROP_ORIGIN": "Das alte Handlungspaar bleibt; nur die fremde Ausgangsangabe fällt weg.",
    "PAIR_CONTEXTUALIZE_REPEAT_ARGUMENTS": "Das wiederholte Handlungspaar bleibt; fremde Einheit und Posten werden zum Vorbezug.",
    "PAIR_CONTEXTUALIZE_AND_DROP_ADDRESS": "Das Handlungspaar bleibt; Fortsetzung, Adresse und fremder Posten werden nicht übertragen.",
}


def read_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        if reader.fieldnames is None:
            raise ValueError(f"missing header: {path}")
        return list(reader.fieldnames), list(reader)


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"refusing to write empty table: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def split_recipe(recipe: str) -> list[str]:
    return recipe.split("+") if recipe and recipe != "NONE" else []


def join_tokens(tokens: list[str]) -> str:
    return "+".join(tokens) if tokens else "NONE"


def lcs_alignment(target: list[str], support: list[str]) -> list[tuple[int, int]]:
    lengths = [[0] * (len(support) + 1) for _ in range(len(target) + 1)]
    for i in range(len(target) - 1, -1, -1):
        for j in range(len(support) - 1, -1, -1):
            lengths[i][j] = (
                1 + lengths[i + 1][j + 1]
                if target[i] == support[j]
                else max(lengths[i + 1][j], lengths[i][j + 1])
            )
    alignment: list[tuple[int, int]] = []
    i = j = 0
    while i < len(target) and j < len(support):
        if target[i] == support[j] and lengths[i][j] == 1 + lengths[i + 1][j + 1]:
            alignment.append((i, j))
            i += 1
            j += 1
        elif lengths[i + 1][j] >= lengths[i][j + 1]:
            i += 1
        else:
            j += 1
    return alignment


def semantic_values(tokens: list[str], values: dict[str, str]) -> str:
    return " · ".join(values[token] for token in tokens) if tokens else "NONE"


def owner_values(
    tokens: list[str],
    register: str,
    values: dict[str, str],
    expansions: dict[tuple[str, str], str],
) -> str:
    return " · ".join(expansions.get((token, register), values[token]) for token in tokens) if tokens else "NONE"


def marker_for(
    atom: str,
    register: str,
    expansions: dict[tuple[str, str], str],
    *,
    duplicate_action: bool = False,
) -> str:
    if duplicate_action:
        return "zweimal"
    fixed = {
        "CHD": "bearbeite",
        "E": "grad i",
        "O": "ausführung",
        "OL": "weiter",
        "AR": "ausgang",
        "D_ADDR": "bezeichneten stelle",
    }
    if atom == "CH":
        return "entnimm" if register in {"SOURCE_SECTION_T", "BIOLOGICAL"} else "nimm"
    if atom == "Y" and register == "SOURCE_SECTION_T":
        return "laufenden eintrag"
    return fixed.get(atom, expansions.get((atom, register), "")).casefold()


def contains_marker(phrase: str, marker: str) -> bool:
    return bool(marker) and marker.casefold() in phrase.casefold()


def classify_operation(
    *,
    pair_mode: bool,
    added: list[str],
    removed: list[str],
    support_tokens: list[str],
    inherited_argument: str,
) -> str:
    if pair_mode:
        pair_map = {
            (("Y",), ("O", "OL")): "PAIR_REPLACE_CARRIER_CONTEXT_WITH_POST",
            (("E",), ("O", "AR")): "PAIR_REPLACE_CARRIER_CONTEXT_WITH_GRADE",
            ((), ("OL",)): "PAIR_DROP_CONTINUATION",
            ((), ("AR",)): "PAIR_DROP_ORIGIN",
            ((), ("OR", "Y")): "PAIR_CONTEXTUALIZE_REPEAT_ARGUMENTS",
            ((), ("OL", "D_ADDR", "Y")): "PAIR_CONTEXTUALIZE_AND_DROP_ADDRESS",
        }
        key = (tuple(added), tuple(removed))
        if key not in pair_map:
            raise ValueError(f"unclassified pair-frame edit: added={added}, removed={removed}")
        return pair_map[key]
    if added == ["AL"]:
        return "ADD_DESTINATION"
    if added == ["OR"]:
        return "ADD_UNIT_ARGUMENT"
    if added == ["Y"]:
        return "EXPLICITIZE_INHERITED_POST" if inherited_argument == "Y" else "ADD_SECOND_POST_ARGUMENT"
    added_actions = [token for token in added if token in ACTION_ROOTS]
    repeated = any(token in support_tokens for token in added_actions)
    if repeated and added == ["CH", "Y"]:
        return "COUNTED_REPEAT_AND_EXPLICITIZE_POST"
    if repeated and len(added) == 1:
        return "COUNTED_REPEAT"
    if added_actions and "E" in added:
        return "ADD_SERIAL_ACTION_AND_GRADE"
    if len(added_actions) == 1 and len(added) == 1:
        return "ADD_SERIAL_ACTION"
    raise ValueError(f"unclassified exact partial delta: added={added}, support={support_tokens}")


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _card_fields, source_cards = read_tsv(CARDS_IN)
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _dict_fields, dictionary = read_tsv(DICTIONARY_IN)
    _expansion_fields, expansion_rows = read_tsv(EXPANSIONS_IN)
    if (len(source_cards), len(clauses), len(dictionary), len(expansion_rows)) != (46, 4576, 46, 95):
        raise ValueError("GDT413/GDT415/GDT416/GDT502 source drift")

    values = {row["atom"]: row["working_value_de"] for row in dictionary}
    expansions = {(row["root"], row["register"]): row["owner_local_expansion_de"] for row in expansion_rows}
    clauses_by_key: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in clauses:
        clauses_by_key[(row["component_recipe"], row["register"], row["imperative_clause_de"])].append(row)

    cards: list[dict[str, object]] = []
    effects: list[dict[str, object]] = []
    for source in source_cards:
        target_tokens = split_recipe(source["target_action_recipe"])
        support_tokens = split_recipe(source["support_recipe"])
        alignment = lcs_alignment(target_tokens, support_tokens)
        target_matched = {i for i, _j in alignment}
        support_matched = {j for _i, j in alignment}
        shared = [target_tokens[i] for i, _j in alignment]
        added = [token for i, token in enumerate(target_tokens) if i not in target_matched]
        removed = [token for j, token in enumerate(support_tokens) if j not in support_matched]
        added_positions = [str(i + 1) for i in range(len(target_tokens)) if i not in target_matched]
        removed_positions = [str(j + 1) for j in range(len(support_tokens)) if j not in support_matched]
        pair_mode = source["support_channel"] in PAIR_CHANNELS
        if not pair_mode and removed:
            raise ValueError(f"partial support is not a target subsequence: {source['comparison_card_id']}")

        source_rows = clauses_by_key[(source["support_recipe"], source["support_register"], source["selected_old_clause_de"])]
        if not source_rows:
            raise ValueError(f"selected GDT416 clause not found: {source['comparison_card_id']}")
        source_rows.sort(key=lambda row: row["global_running_event_id"])
        witness = source_rows[0]
        inherited_arguments = {row["inherited_argument_root"] for row in source_rows}
        if len(inherited_arguments) != 1:
            raise ValueError(f"selected clause has mixed inherited arguments: {source['comparison_card_id']}")
        inherited_argument = next(iter(inherited_arguments))
        pair_actions = witness["explicit_action_roots"].replace("|", "+")
        if pair_mode and pair_actions != source["ordered_action_pair"]:
            raise ValueError(f"pair carrier action drift: {source['comparison_card_id']}")

        operation = classify_operation(
            pair_mode=pair_mode,
            added=added,
            removed=removed,
            support_tokens=support_tokens,
            inherited_argument=inherited_argument,
        )
        if pair_mode:
            support_depth = "PAIR_BACKBONE_FRAME_EDIT"
            alignment_mode = "ORDERED_PAIR_CARRIER_ALIGNMENT"
        elif source["support_register_relation"] == "SAME_REGISTER":
            support_depth = "DIRECT_LOCAL_DELTA"
            alignment_mode = "EXACT_PARTIAL_RECIPE_EXTENSION"
        else:
            support_depth = "CROSS_REGISTER_NORMALIZED_DELTA"
            alignment_mode = "EXACT_PARTIAL_RECIPE_EXTENSION"

        card_effects: list[dict[str, object]] = []
        for atom in added:
            duplicate_action = atom in ACTION_ROOTS and atom in shared
            marker = marker_for(atom, source["target_register"], expansions, duplicate_action=duplicate_action)
            target_has = contains_marker(source["target_current_default_phrase_de"], marker)
            source_has = contains_marker(source["selected_old_clause_de"], marker)
            inherited_explicitization = atom == "Y" and inherited_argument == "Y"
            expectation = (
                "TARGET_COUNT_WORD_ZWEIMAL"
                if duplicate_action
                else "TARGET_REALIZATION_PRESENT__SOURCE_ARGUMENT_WAS_INHERITED"
                if inherited_explicitization
                else "TARGET_REALIZATION_PRESENT"
            )
            passed = target_has and (not inherited_explicitization or inherited_argument == "Y")
            card_effects.append({
                "token_effect_id": f"G504-E{len(effects) + len(card_effects) + 1:03d}",
                "source_comparison_card_id": source["comparison_card_id"],
                "effect_side": "TARGET_ADD",
                "atom": atom,
                "portable_value_de": values[atom],
                "realization_register": source["target_register"],
                "owner_local_value_de": expansions.get((atom, source["target_register"]), values[atom]),
                "phrase_marker_de": marker,
                "source_phrase_contains_marker": "YES" if source_has else "NO",
                "target_phrase_contains_marker": "YES" if target_has else "NO",
                "source_inherited_argument_root": inherited_argument,
                "expectation": expectation,
                "effect_check_passed": "YES" if passed else "NO",
                "guard": GUARD,
            })
        for atom in removed:
            marker = marker_for(atom, source["support_register"], expansions)
            source_has = contains_marker(source["selected_old_clause_de"], marker)
            target_has = contains_marker(source["target_current_default_phrase_de"], marker)
            card_effects.append({
                "token_effect_id": f"G504-E{len(effects) + len(card_effects) + 1:03d}",
                "source_comparison_card_id": source["comparison_card_id"],
                "effect_side": "CARRIER_REMOVE",
                "atom": atom,
                "portable_value_de": values[atom],
                "realization_register": source["support_register"],
                "owner_local_value_de": expansions.get((atom, source["support_register"]), values[atom]),
                "phrase_marker_de": marker,
                "source_phrase_contains_marker": "YES" if source_has else "NO",
                "target_phrase_contains_marker": "YES" if target_has else "NO",
                "source_inherited_argument_root": inherited_argument,
                "expectation": "SOURCE_REALIZATION_PRESENT__TARGET_REALIZATION_ABSENT",
                "effect_check_passed": "YES" if source_has and not target_has else "NO",
                "guard": GUARD,
            })
        effects.extend(card_effects)

        cards.append({
            "semantic_delta_card_id": f"G504-D{len(cards) + 1:02d}",
            "source_comparison_card_id": source["comparison_card_id"],
            "target_matrix_cell_id": source["target_matrix_cell_id"],
            "target_action_recipe": source["target_action_recipe"],
            "target_register": source["target_register"],
            "support_recipe": source["support_recipe"],
            "support_register": source["support_register"],
            "support_register_relation": source["support_register_relation"],
            "support_channel": source["support_channel"],
            "alignment_mode": alignment_mode,
            "support_depth": support_depth,
            "aligned_shared_tokens": join_tokens(shared),
            "aligned_shared_portable_values_de": semantic_values(shared, values),
            "target_only_positions": ",".join(added_positions) if added_positions else "NONE",
            "target_only_tokens": join_tokens(added),
            "target_only_portable_values_de": semantic_values(added, values),
            "target_only_owner_values_de": owner_values(added, source["target_register"], values, expansions),
            "carrier_only_positions": ",".join(removed_positions) if removed_positions else "NONE",
            "carrier_only_tokens": join_tokens(removed),
            "carrier_only_portable_values_de": semantic_values(removed, values),
            "carrier_only_owner_values_de": owner_values(removed, source["support_register"], values, expansions),
            "delta_operation": operation,
            "sentence_effect_de": OPERATION_EFFECT_DE[operation],
            "source_inherited_argument_root": inherited_argument,
            "source_template": witness["template"],
            "selected_old_clause_de": source["selected_old_clause_de"],
            "target_current_default_phrase_de": source["target_current_default_phrase_de"],
            "token_effect_checks": len(card_effects),
            "token_effect_checks_passed": sum(row["effect_check_passed"] == "YES" for row in card_effects),
            "semantic_phrase_delta_consistent": "YES" if all(row["effect_check_passed"] == "YES" for row in card_effects) else "NO",
            "source_roundtrip_exact": source["support_roundtrip_exact"],
            "target_phrase_changed": "NO",
            "target_evidence_status_retained": source["target_evidence_status_retained"],
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        })

    if len(cards) != 46 or len(effects) != 59:
        raise ValueError(f"unexpected card/effect totals: {len(cards)}/{len(effects)}")
    failed = [row["token_effect_id"] for row in effects if row["effect_check_passed"] != "YES"]
    if failed:
        raise ValueError(f"phrase-effect marker failures: {failed}")

    operation_rows: list[dict[str, object]] = []
    for operation in OPERATION_ORDER:
        group = [row for row in cards if row["delta_operation"] == operation]
        if not group:
            raise ValueError(f"empty expected operation: {operation}")
        operation_rows.append({
            "delta_operation": operation,
            "card_count": len(group),
            "card_ids": "|".join(str(row["semantic_delta_card_id"]) for row in group),
            "target_registers": "|".join(register for register in REGISTERS if any(row["target_register"] == register for row in group)),
            "support_depths": "|".join(sorted({str(row["support_depth"]) for row in group})),
            "target_only_patterns": "|".join(sorted({str(row["target_only_tokens"]) for row in group})),
            "carrier_only_patterns": "|".join(sorted({str(row["carrier_only_tokens"]) for row in group})),
            "sentence_effect_de": OPERATION_EFFECT_DE[operation],
            "all_phrase_deltas_consistent": "YES" if all(row["semantic_phrase_delta_consistent"] == "YES" for row in group) else "NO",
            "guard": GUARD,
        })

    atom_rows: list[dict[str, object]] = []
    for atom in sorted({row["atom"] for row in effects}):
        group = [row for row in effects if row["atom"] == atom]
        additions = [row for row in group if row["effect_side"] == "TARGET_ADD"]
        removals = [row for row in group if row["effect_side"] == "CARRIER_REMOVE"]
        atom_rows.append({
            "atom": atom,
            "portable_value_de": values[atom],
            "target_add_effect_count": len(additions),
            "carrier_remove_effect_count": len(removals),
            "total_effect_count": len(group),
            "target_add_card_count": len({row["source_comparison_card_id"] for row in additions}),
            "carrier_remove_card_count": len({row["source_comparison_card_id"] for row in removals}),
            "realization_registers": "|".join(register for register in REGISTERS if any(row["realization_register"] == register for row in group)),
            "all_effect_checks_passed": "YES" if all(row["effect_check_passed"] == "YES" for row in group) else "NO",
            "guard": GUARD,
        })

    register_rows: list[dict[str, object]] = []
    for register in REGISTERS:
        group = [row for row in cards if row["target_register"] == register]
        card_ids = {row["source_comparison_card_id"] for row in group}
        register_effects = [row for row in effects if row["source_comparison_card_id"] in card_ids]
        register_rows.append({
            "target_register": register,
            "semantic_delta_card_count": len(group),
            "direct_local_delta_count": sum(row["support_depth"] == "DIRECT_LOCAL_DELTA" for row in group),
            "cross_register_normalized_delta_count": sum(row["support_depth"] == "CROSS_REGISTER_NORMALIZED_DELTA" for row in group),
            "pair_backbone_frame_edit_count": sum(row["support_depth"] == "PAIR_BACKBONE_FRAME_EDIT" for row in group),
            "token_effect_check_count": len(register_effects),
            "token_effect_checks_passed": sum(row["effect_check_passed"] == "YES" for row in register_effects),
            "all_target_phrases_retained": "YES",
            "guard": GUARD,
        })

    depth_rows: list[dict[str, object]] = []
    depth_notes = {
        "DIRECT_LOCAL_DELTA": "Altes Teilrezept und Ziel liegen im selben Register.",
        "CROSS_REGISTER_NORMALIZED_DELTA": "Das exakte Teilrezept liegt in einem anderen Register; verglichen wird über portable Werte.",
        "PAIR_BACKBONE_FRAME_EDIT": "Nur das alte Handlungspaar wird übertragen; fremde Trägerkomponenten bleiben als Entfernung sichtbar.",
    }
    for depth in depth_notes:
        group = [row for row in cards if row["support_depth"] == depth]
        depth_rows.append({
            "support_depth": depth,
            "card_count": len(group),
            "target_added_token_count": sum(len(split_recipe(str(row["target_only_tokens"]))) for row in group),
            "carrier_removed_token_count": sum(len(split_recipe(str(row["carrier_only_tokens"]))) for row in group),
            "operation_class_count": len({row["delta_operation"] for row in group}),
            "all_phrase_deltas_consistent": "YES" if all(row["semantic_phrase_delta_consistent"] == "YES" for row in group) else "NO",
            "interpretation_de": depth_notes[depth],
            "guard": GUARD,
        })

    write_tsv(CARDS_OUT, cards)
    write_tsv(EFFECTS_OUT, effects)
    write_tsv(OPERATIONS_OUT, operation_rows)
    write_tsv(ATOMS_OUT, atom_rows)
    write_tsv(REGISTERS_OUT, register_rows)
    write_tsv(DEPTH_OUT, depth_rows)

    lines = [
        "# GDT504 — semantische Deltas der 46 Vergleichskarten",
        "",
        f"Status: `{STATUS}`",
        "",
        "Jede Karte wird als geordnete Differenz aus altem Klauselträger und",
        "aktuellem Arbeitssatz gelesen. Zielzusätze und fremde Trägerreste",
        "bleiben getrennt; die Wörterbuchwerte werden nicht verändert.",
        "",
        "## Drei Stützentiefen",
        "",
    ]
    for row in depth_rows:
        lines.append(f'- **{row["support_depth"]}:** {row["card_count"]} Karten. {row["interpretation_de"]}')
    lines.extend(["", "## Die 46 Deltakarten", ""])
    for row in cards:
        lines.extend([
            f'### {row["semantic_delta_card_id"]} · `{row["target_action_recipe"]}` · {row["target_register"]}',
            "",
            f'- Alter Satz: {row["selected_old_clause_de"]}',
            f'- Aktueller Satz: **{row["target_current_default_phrase_de"]}**',
            f'- Gemeinsam: `{row["aligned_shared_tokens"]}`; hinzu: `{row["target_only_tokens"]}`; nicht übertragen: `{row["carrier_only_tokens"]}`.',
            f'- Operation: `{row["delta_operation"]}` — {row["sentence_effect_de"]}',
            f'- Stützentiefe: `{row["support_depth"]}`; Effektprüfungen: {row["token_effect_checks_passed"]}/{row["token_effect_checks"]}.',
            "",
        ])
    lines.extend([
        "## Arbeitslesart",
        "",
        "Die 35 Teilrezeptkarten sind echte Erweiterungen: 22 lokal und dreizehn",
        "registerübergreifend normalisiert. Die elf Paarkarten bleiben eine",
        "eigene schwächere Schublade, weil nur das Handlungspaar alt ist und",
        "Trägerkontext entfernt oder ersetzt wird. Alle 59 sichtbaren",
        "Token-Effekte passen zur aktuellen deutschen Phrase; das ist eine",
        "Konsistenzprüfung der Arbeitssprache, keine neue Manuskriptbeobachtung.",
        "",
        f"`{GUARD}`",
        "",
    ])
    READABLE_OUT.write_text("\n".join(lines), encoding="utf-8")

    result = {
        "status": STATUS,
        "semantic_delta_cards": len(cards),
        "exact_partial_extension_cards": sum(row["alignment_mode"] == "EXACT_PARTIAL_RECIPE_EXTENSION" for row in cards),
        "direct_local_delta_cards": sum(row["support_depth"] == "DIRECT_LOCAL_DELTA" for row in cards),
        "cross_register_normalized_delta_cards": sum(row["support_depth"] == "CROSS_REGISTER_NORMALIZED_DELTA" for row in cards),
        "pair_backbone_frame_edit_cards": sum(row["support_depth"] == "PAIR_BACKBONE_FRAME_EDIT" for row in cards),
        "pair_carrier_context_replacement_cards": sum(row["target_only_tokens"] != "NONE" and row["carrier_only_tokens"] != "NONE" for row in cards if row["support_depth"] == "PAIR_BACKBONE_FRAME_EDIT"),
        "pair_carrier_context_stripping_cards": sum(row["target_only_tokens"] == "NONE" and row["carrier_only_tokens"] != "NONE" for row in cards if row["support_depth"] == "PAIR_BACKBONE_FRAME_EDIT"),
        "aligned_shared_tokens": sum(len(split_recipe(str(row["aligned_shared_tokens"]))) for row in cards),
        "target_added_token_effects": sum(row["effect_side"] == "TARGET_ADD" for row in effects),
        "carrier_removed_token_effects": sum(row["effect_side"] == "CARRIER_REMOVE" for row in effects),
        "token_effect_checks": len(effects),
        "token_effect_checks_passed": sum(row["effect_check_passed"] == "YES" for row in effects),
        "semantic_phrase_delta_consistent_cards": sum(row["semantic_phrase_delta_consistent"] == "YES" for row in cards),
        "delta_operation_classes": len(operation_rows),
        "atom_effect_families": len(atom_rows),
        "target_added_atom_families": len({row["atom"] for row in effects if row["effect_side"] == "TARGET_ADD"}),
        "carrier_removed_atom_families": len({row["atom"] for row in effects if row["effect_side"] == "CARRIER_REMOVE"}),
        "inherited_argument_explicitization_cards": sum(row["delta_operation"] in {"EXPLICITIZE_INHERITED_POST", "COUNTED_REPEAT_AND_EXPLICITIZE_POST"} for row in cards),
        "counted_repeat_cards": sum(row["delta_operation"] in {"COUNTED_REPEAT", "COUNTED_REPEAT_AND_EXPLICITIZE_POST"} for row in cards),
        "source_clause_roundtrips_exact": sum(row["source_roundtrip_exact"] == "YES" for row in cards),
        "nonempty_target_registers": sum(int(row["semantic_delta_card_count"]) > 0 for row in register_rows),
        "target_phrase_changes": 0,
        "working_root_meaning_changes": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
