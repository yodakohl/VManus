#!/usr/bin/env python3
"""Build concrete contextual bridges for GDT506's four open pair targets."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt507_contextual_pair_argument_bridge_atlas"
ART = BASE / "artifacts"
G416 = ROOT / "experiments/yolo/gdt416_owner_local_imperative_sentence_compiler/artifacts"
G425 = ROOT / "experiments/yolo/gdt425_complete_factorized_action_portability/artifacts"
G426 = ROOT / "experiments/yolo/gdt426_typed_action_family_prediction/artifacts"
G436 = ROOT / "experiments/yolo/gdt436_streaming_context_intake_driver/artifacts"
G506 = ROOT / "experiments/yolo/gdt506_target_pair_frame_compatibility_rank/artifacts"

CLAUSES_IN = G416 / "gdt416_4576_imperative_clauses.tsv"
FACTORS_IN = G425 / "gdt425_4576_event_factorized_action_replay.tsv"
PAIR_STATUS_IN = G426 / "gdt426_81_exact_action_pair_status.tsv"
STREAM_IN = G436 / "gdt436_4576_oracle_free_stream_readings.tsv"
TARGETS_IN = G506 / "gdt506_11_target_frame_compatibility_cards.tsv"

WITHIN_OUT = ART / "gdt507_65_within_event_chch_context_carriers.tsv"
ADJACENT_OUT = ART / "gdt507_13_adjacent_event_same_argument_bridges.tsv"
PAIR_SUMMARY_OUT = ART / "gdt507_2_pair_context_bridge_summary.tsv"
TARGET_OUT = ART / "gdt507_4_target_context_bridge_cards.tsv"
READABLE_OUT = ART / "GDT507_CONTEXTUAL_PAIR_ARGUMENT_BRIDGE_ATLAS.md"
RESULT_OUT = ART / "gdt507_result.json"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
TARGET_REGISTERS = ("SOURCE_SECTION_T", "PHARMA")
TARGET_PAIRS = ("CH+CH", "CH+SH")
STATUS = "FOUR_CONTEXTUAL_TARGETS_HAVE_CONCRETE_BRIDGES__THREE_LOCAL_ONE_CROSS"
GUARD = "WORKING_CONTEXT_BRIDGE_ONLY__TARGETS_REMAIN_COMPOSED_AND_UNOBSERVED"


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


def event_number(event_id: str) -> int:
    return int(event_id.rsplit("E", 1)[1])


def argument_mode(row: dict[str, str]) -> str:
    if row["explicit_argument_roots"] != "NONE":
        return "EXPLICIT_ARGUMENTS"
    if row["inherited_argument_root"] != "NONE":
        return "INHERITED_ARGUMENT"
    return "ARGUMENT_FREE"


def action_roots(row: dict[str, str]) -> list[str]:
    return [atom for atom in row["component_recipe"].split("+") if atom in ACTION_ROOTS]


def adjacent_action_positions(actions: list[str], left: str, right: str) -> list[int]:
    return [index for index, (a, b) in enumerate(zip(actions, actions[1:])) if (a, b) == (left, right)]


def component_pair_positions(recipe: list[str], left: str, right: str, action_pair_ordinal: int) -> tuple[int, int]:
    action_positions = [index for index, atom in enumerate(recipe) if atom in ACTION_ROOTS]
    left_pos = action_positions[action_pair_ordinal]
    right_pos = action_positions[action_pair_ordinal + 1]
    if recipe[left_pos] != left or recipe[right_pos] != right:
        raise ValueError("action/component alignment drift")
    return left_pos, right_pos


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    _clause_fields, clauses = read_tsv(CLAUSES_IN)
    _factor_fields, factor_rows = read_tsv(FACTORS_IN)
    _pair_fields, pair_rows = read_tsv(PAIR_STATUS_IN)
    _stream_fields, stream_rows = read_tsv(STREAM_IN)
    _target_fields, target_rows = read_tsv(TARGETS_IN)
    if (len(clauses), len(factor_rows), len(pair_rows), len(stream_rows), len(target_rows)) != (4576, 4576, 81, 4576, 11):
        raise ValueError("GDT416/GDT425/GDT426/GDT436/GDT506 source drift")

    clause_by_id = {row["global_running_event_id"]: row for row in clauses}
    factor_by_id = {row["global_running_event_id"]: row for row in factor_rows}
    stream_by_id = {row["event_id"]: row for row in stream_rows}
    pair_status = {row["ordered_pair"].replace(">", "+"): row for row in pair_rows}
    open_targets = [row for row in target_rows if row["compatibility_tier"] == "C_ACTION_HANDGRIP_ONLY__ARGUMENT_MODE_OPEN"]
    if len(open_targets) != 4 or {row["ordered_action_pair"] for row in open_targets} != set(TARGET_PAIRS):
        raise ValueError("expected four GDT506 Tier-C CH+CH/CH+SH targets")

    within_rows: list[dict[str, object]] = []
    for clause in clauses:
        actions = action_roots(clause)
        pair_positions = adjacent_action_positions(actions, "CH", "CH")
        for pair_position in pair_positions:
            recipe = clause["component_recipe"].split("+")
            left_component, right_component = component_pair_positions(recipe, "CH", "CH", pair_position)
            mode = argument_mode(clause)
            factor = factor_by_id[clause["global_running_event_id"]]
            stream = stream_by_id[clause["global_running_event_id"]]
            extra_actions = actions[:pair_position] + actions[pair_position + 2 :]
            nonactions = [atom for atom in recipe if atom not in ACTION_ROOTS]
            within_rows.append({
                "within_event_carrier_id": f"G507-W{len(within_rows) + 1:02d}",
                "global_running_event_id": clause["global_running_event_id"],
                "global_statement_id": clause["global_statement_id"],
                "card_ordinal_in_statement": clause["card_ordinal_in_statement"],
                "physical_page": clause["physical_page"],
                "register": clause["register"],
                "owner_class": clause["owner_class"],
                "owner_de": clause["owner_de"],
                "surface": clause["surface"],
                "component_recipe": clause["component_recipe"],
                "explicit_action_roots": clause["explicit_action_roots"],
                "chch_action_pair_ordinal": pair_position + 1,
                "left_component_position": left_component + 1,
                "right_component_position": right_component + 1,
                "between_component_atoms": "+".join(recipe[left_component + 1 : right_component]) if right_component > left_component + 1 else "NONE",
                "extra_action_roots": "+".join(extra_actions) if extra_actions else "NONE",
                "extra_action_count": len(extra_actions),
                "nonaction_frame_atoms": "+".join(nonactions) if nonactions else "NONE",
                "nonaction_frame_atom_count": len(nonactions),
                "explicit_argument_roots": clause["explicit_argument_roots"],
                "inherited_argument_root": clause["inherited_argument_root"],
                "argument_mode": mode,
                "context_compatible": "YES" if mode in {"INHERITED_ARGUMENT", "ARGUMENT_FREE"} else "NO",
                "stream_active_argument_before": stream["active_argument_before"],
                "stream_active_argument_after": stream["active_argument_after"],
                "stream_state_matches_reference": stream["state_matches_reference"],
                "stream_clause_matches_reference": stream["clause_matches_reference"],
                "factorized_action_replay_status": factor["factorized_action_replay_status"],
                "imperative_clause_de": clause["imperative_clause_de"],
                "guard": GUARD,
            })

    if len(within_rows) != 65:
        raise ValueError(f"expected 65 broader CH>CH carriers, got {len(within_rows)}")

    adjacent_rows: list[dict[str, object]] = []
    for left, right in zip(clauses, clauses[1:]):
        right_actions = right["explicit_action_roots"]
        if left["explicit_action_roots"] != "CH" or right_actions not in {"CH", "SH"}:
            continue
        if left["global_statement_id"] != right["global_statement_id"]:
            continue
        if int(right["card_ordinal_in_statement"]) != int(left["card_ordinal_in_statement"]) + 1:
            continue
        if (left["physical_page"], left["register"], left["owner_class"], left["owner_de"]) != (
            right["physical_page"], right["register"], right["owner_class"], right["owner_de"]
        ):
            continue
        if left["explicit_argument_roots"] != "NONE" or right["explicit_argument_roots"] != "NONE":
            continue
        inherited = left["inherited_argument_root"]
        if inherited == "NONE" or right["inherited_argument_root"] != inherited:
            continue
        left_stream = stream_by_id[left["global_running_event_id"]]
        right_stream = stream_by_id[right["global_running_event_id"]]
        left_factor = factor_by_id[left["global_running_event_id"]]
        right_factor = factor_by_id[right["global_running_event_id"]]
        left_nonactions = [atom for atom in left["component_recipe"].split("+") if atom not in ACTION_ROOTS]
        right_nonactions = [atom for atom in right["component_recipe"].split("+") if atom not in ACTION_ROOTS]
        pair = f"CH+{right_actions}"
        adjacent_rows.append({
            "adjacent_bridge_id": f"G507-A{len(adjacent_rows) + 1:02d}",
            "ordered_action_pair": pair,
            "global_statement_id": left["global_statement_id"],
            "physical_page": left["physical_page"],
            "register": left["register"],
            "owner_class": left["owner_class"],
            "owner_de": left["owner_de"],
            "shared_inherited_argument_root": inherited,
            "left_event_id": left["global_running_event_id"],
            "right_event_id": right["global_running_event_id"],
            "left_card_ordinal": left["card_ordinal_in_statement"],
            "right_card_ordinal": right["card_ordinal_in_statement"],
            "stream_ordinals_consecutive": "YES" if int(right_stream["stream_ordinal"]) == int(left_stream["stream_ordinal"]) + 1 else "NO",
            "left_surface": left["surface"],
            "right_surface": right["surface"],
            "left_component_recipe": left["component_recipe"],
            "right_component_recipe": right["component_recipe"],
            "left_nonaction_frame_atom_count": len(left_nonactions),
            "right_nonaction_frame_atom_count": len(right_nonactions),
            "left_stream_active_argument_before": left_stream["active_argument_before"],
            "left_stream_active_argument_after": left_stream["active_argument_after"],
            "right_stream_active_argument_before": right_stream["active_argument_before"],
            "right_stream_active_argument_after": right_stream["active_argument_after"],
            "left_stream_state_matches_reference": left_stream["state_matches_reference"],
            "right_stream_state_matches_reference": right_stream["state_matches_reference"],
            "left_factorized_action_replay_status": left_factor["factorized_action_replay_status"],
            "right_factorized_action_replay_status": right_factor["factorized_action_replay_status"],
            "left_imperative_clause_de": left["imperative_clause_de"],
            "right_imperative_clause_de": right["imperative_clause_de"],
            "context_bridge_reading_de": f"{left['imperative_clause_de']} {right['imperative_clause_de']}",
            "target_phrase_changed": "NO",
            "guard": GUARD,
        })

    if len(adjacent_rows) != 13:
        raise ValueError(f"expected 13 adjacent same-argument bridges, got {len(adjacent_rows)}")

    pair_summaries: list[dict[str, object]] = []
    for pair in TARGET_PAIRS:
        left, right = pair.split("+")
        within_pair_clauses: list[dict[str, str]] = []
        for clause in clauses:
            actions = action_roots(clause)
            if adjacent_action_positions(actions, left, right):
                within_pair_clauses.append(clause)
        mode_counts = Counter(argument_mode(row) for row in within_pair_clauses)
        compatible = [row for row in within_pair_clauses if argument_mode(row) != "EXPLICIT_ARGUMENTS"]
        adjacent_group = [row for row in adjacent_rows if row["ordered_action_pair"] == pair]
        profile = pair_status[pair]
        if int(profile["event_count"]) != len(within_pair_clauses):
            raise ValueError(f"GDT426 pair count drift for {pair}")
        pair_summaries.append({
            "ordered_action_pair": pair,
            "within_event_pair_event_count": len(within_pair_clauses),
            "within_event_explicit_argument_count": mode_counts["EXPLICIT_ARGUMENTS"],
            "within_event_inherited_argument_count": mode_counts["INHERITED_ARGUMENT"],
            "within_event_argument_free_count": mode_counts["ARGUMENT_FREE"],
            "within_event_context_compatible_count": len(compatible),
            "within_event_page_count": len({row["physical_page"] for row in within_pair_clauses}),
            "within_event_register_count": len({row["register"] for row in within_pair_clauses}),
            "within_event_context_registers": "|".join(sorted({row["register"] for row in compatible})) if compatible else "NONE",
            "adjacent_same_statement_context_chain_count": len(adjacent_group),
            "adjacent_context_page_count": len({str(row["physical_page"]) for row in adjacent_group}),
            "adjacent_context_register_count": len({str(row["register"]) for row in adjacent_group}),
            "adjacent_context_registers": "|".join(sorted({str(row["register"]) for row in adjacent_group})) if adjacent_group else "NONE",
            "source_target_local_context_bridge": "YES" if any(row["register"] == "SOURCE_SECTION_T" for row in compatible) or any(row["register"] == "SOURCE_SECTION_T" for row in adjacent_group) else "NO",
            "pharma_target_local_context_bridge": "YES" if any(row["register"] == "PHARMA" for row in compatible) or any(row["register"] == "PHARMA" for row in adjacent_group) else "NO",
            "pair_order_status": profile["pair_status"],
            "context_bridge_status": "DIRECT_WITHIN_EVENT_CONTEXT_OLD" if compatible else "ADJACENT_EVENT_CONTEXT_OLD__WITHIN_EVENT_PAIR_EXPLICIT_ONLY",
            "guard": GUARD,
        })

    adjacent_by_pair: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in adjacent_rows:
        adjacent_by_pair[str(row["ordered_action_pair"])].append(row)

    def rank_within(row: dict[str, object], target_register: str) -> tuple[object, ...]:
        return (
            str(row["register"]) != target_register,
            str(row["argument_mode"]) != "INHERITED_ARGUMENT",
            int(row["extra_action_count"]),
            int(row["nonaction_frame_atom_count"]),
            event_number(str(row["global_running_event_id"])),
        )

    def rank_adjacent(row: dict[str, object], target_register: str) -> tuple[object, ...]:
        return (
            str(row["register"]) != target_register,
            int(row["left_nonaction_frame_atom_count"]) + int(row["right_nonaction_frame_atom_count"]),
            event_number(str(row["left_event_id"])),
        )

    target_cards: list[dict[str, object]] = []
    for target in sorted(open_targets, key=lambda row: row["target_frame_card_id"]):
        pair = target["ordered_action_pair"]
        register = target["target_register"]
        compatible_within = [row for row in within_rows if str(row["context_compatible"]) == "YES"] if pair == "CH+CH" else []
        local_within = [row for row in compatible_within if row["register"] == register]
        adjacent_group = adjacent_by_pair[pair]
        local_adjacent = [row for row in adjacent_group if row["register"] == register]
        if pair == "CH+CH":
            selected_pair = min(compatible_within, key=lambda row: rank_within(row, register))
            selected_adjacent = min(adjacent_group, key=lambda row: rank_adjacent(row, register))
            if local_within and local_adjacent:
                tier = "A_LOCAL_WITHIN_AND_ADJACENT_CONTEXT_BRIDGE"
                locality = "LOCAL"
                mechanism = "Das Handlungspaar steht lokal in einer längeren Karte mit geerbtem Argument; zusätzlich folgen zwei einzelne CH-Karten lokal mit demselben geerbten Argument unmittelbar aufeinander."
            else:
                tier = "B_CROSS_REGISTER_WITHIN_AND_ADJACENT_CONTEXT_BRIDGE"
                locality = "CROSS_REGISTER"
                mechanism = "Das Handlungspaar und eine unmittelbar aufeinanderfolgende CH/CH-Kontextkette sind alt, aber nur in anderen Registern."
            pair_order_event_also_context_compatible = "YES"
        else:
            selected_clause = clause_by_id[target["selected_source_event_id"]]
            if not adjacent_action_positions(action_roots(selected_clause), "CH", "SH"):
                raise ValueError(f"selected GDT506 source does not carry CH>SH: {target['selected_source_event_id']}")
            selected_pair = {
                "global_running_event_id": selected_clause["global_running_event_id"],
                "register": selected_clause["register"],
                "component_recipe": selected_clause["component_recipe"],
                "argument_mode": argument_mode(selected_clause),
                "inherited_argument_root": selected_clause["inherited_argument_root"],
                "imperative_clause_de": selected_clause["imperative_clause_de"],
            }
            if not local_adjacent:
                raise ValueError(f"missing local adjacent CH>SH bridge for {target['target_frame_card_id']}")
            selected_adjacent = min(local_adjacent, key=lambda row: rank_adjacent(row, register))
            tier = "A_LOCAL_ADJACENT_CONTEXT_BRIDGE_PLUS_DIRECT_EXPLICIT_PAIR"
            locality = "LOCAL"
            mechanism = "Das Handlungspaar steht alt innerhalb einer Karte; im Zielregister folgen CH und SH außerdem als zwei unmittelbare Karten im selben Satz mit demselben geerbten Argument."
            pair_order_event_also_context_compatible = "NO"

        target_cards.append({
            "target_context_bridge_card_id": f"G507-T{len(target_cards) + 1:02d}",
            "source_gdt506_target_frame_card_id": target["target_frame_card_id"],
            "target_matrix_cell_id": target["target_matrix_cell_id"],
            "target_action_recipe": target["target_action_recipe"],
            "target_register": register,
            "ordered_action_pair": pair,
            "target_current_default_phrase_de": target["target_current_default_phrase_de"],
            "old_gdt506_compatibility_tier": target["compatibility_tier"],
            "new_context_bridge_tier": tier,
            "context_bridge_locality": locality,
            "within_event_pair_event_count": pair_status[pair]["event_count"],
            "within_event_context_compatible_count": len(compatible_within),
            "within_event_target_register_context_count": len(local_within),
            "adjacent_same_argument_chain_count": len(adjacent_group),
            "adjacent_target_register_chain_count": len(local_adjacent),
            "selected_pair_order_event_id": selected_pair["global_running_event_id"],
            "selected_pair_order_register": selected_pair["register"],
            "selected_pair_order_recipe": selected_pair["component_recipe"],
            "selected_pair_order_argument_mode": selected_pair["argument_mode"],
            "selected_pair_order_inherited_argument_root": selected_pair["inherited_argument_root"],
            "selected_pair_order_clause_de": selected_pair["imperative_clause_de"],
            "selected_context_bridge_id": selected_adjacent["adjacent_bridge_id"],
            "selected_context_left_event_id": selected_adjacent["left_event_id"],
            "selected_context_right_event_id": selected_adjacent["right_event_id"],
            "selected_context_register": selected_adjacent["register"],
            "selected_context_shared_argument_root": selected_adjacent["shared_inherited_argument_root"],
            "selected_context_left_recipe": selected_adjacent["left_component_recipe"],
            "selected_context_right_recipe": selected_adjacent["right_component_recipe"],
            "selected_context_reading_de": selected_adjacent["context_bridge_reading_de"],
            "pair_order_event_also_context_compatible": pair_order_event_also_context_compatible,
            "context_bridge_mechanism_de": mechanism,
            "target_bridge_status": "CONTEXT_BRIDGED_WORKING__TARGET_RECIPE_UNOBSERVED",
            "target_evidence_status_retained": target["target_evidence_status_retained"],
            "target_phrase_changed": "NO",
            "working_root_meaning_changed": "NO",
            "surface_prediction_made": "NO",
            "occurrence_prediction_made": "NO",
            "guard": GUARD,
        })

    if len(target_cards) != 4:
        raise ValueError("target-card count drift")

    write_tsv(WITHIN_OUT, within_rows)
    write_tsv(ADJACENT_OUT, adjacent_rows)
    write_tsv(PAIR_SUMMARY_OUT, pair_summaries)
    write_tsv(TARGET_OUT, target_cards)

    mode_counts = Counter(str(row["argument_mode"]) for row in within_rows)
    adjacent_pair_counts = Counter(str(row["ordered_action_pair"]) for row in adjacent_rows)
    tier_counts = Counter(str(row["new_context_bridge_tier"]) for row in target_cards)
    readable = [
        "# GDT507 — Kontextbrücken für die vier letzten Paarrahmen",
        "",
        f"Status: `{STATUS}`",
        "",
        "## Kernergebnis",
        "",
        "Die vier GDT506-Karten bleiben Arbeitskompositionen, aber keine besitzt mehr nur eine unverbundene Kontextannahme.",
        "",
        f"- `CH>CH` steht in {len(within_rows)} älteren Ereignissen; {mode_counts['INHERITED_ARGUMENT']} davon erben ihr Argument und {mode_counts['ARGUMENT_FREE']} nennt keines.",
        f"- Hinzu kommen {adjacent_pair_counts['CH+CH']} unmittelbare CH→CH-Kartenfolgen mit demselben geerbten Argument.",
        f"- `CH>SH` hat weiterhin drei innerhalb einer Karte ausdrücklich argumentierte Träger, aber {adjacent_pair_counts['CH+SH']} unmittelbare CH→SH-Kartenfolgen erben dasselbe Argument; sie liegen auf sieben Seiten in allen fünf Registern.",
        "- Für Pharma liegen beide Brücken lokal; für Source ist CH→SH lokal, während CH→CH registerübergreifend bleibt.",
        "",
        "## Vier Zielkarten",
        "",
        "| Ziel | Paar | Brücke | alter Satz / alte Folge |",
        "|---|---|---|---|",
    ]
    for row in target_cards:
        readable.append(
            f"| `{row['target_matrix_cell_id']}` {row['target_register']} | `{row['ordered_action_pair']}` | "
            f"`{row['new_context_bridge_tier']}` | `{row['selected_pair_order_event_id']}` + "
            f"`{row['selected_context_left_event_id']}→{row['selected_context_right_event_id']}` |"
        )
    readable.extend([
        "",
        "## Die zwei besonders klaren CH→SH-Folgen",
        "",
    ])
    for register in TARGET_REGISTERS:
        row = next(card for card in target_cards if card["ordered_action_pair"] == "CH+SH" and card["target_register"] == register)
        readable.extend([
            f"### {register}",
            "",
            f"`{row['selected_context_left_event_id']}→{row['selected_context_right_event_id']}` erbt `{row['selected_context_shared_argument_root']}`:",
            "",
            f"> {row['selected_context_reading_de']}",
            "",
        ])
    readable.extend([
        "## Grenze",
        "",
        "Keine der vier nackten Zielrezepte wird dadurch zu einem beobachteten Manuskriptereignis. Die Brücken erklären nur, warum die festen Handlungsfolgen ein aus dem laufenden Besitzerzustand geerbtes Argument tragen dürfen. Alle vier bisherigen deutschen Defaults, alle Wurzelwerte und alle `COMPOSED_WORKING`-Labels bleiben stehen.",
    ])
    READABLE_OUT.write_text("\n".join(readable) + "\n", encoding="utf-8")

    result = {
        "status": STATUS,
        "within_event_chch_carriers": len(within_rows),
        "within_event_chch_explicit_argument_carriers": mode_counts["EXPLICIT_ARGUMENTS"],
        "within_event_chch_inherited_argument_carriers": mode_counts["INHERITED_ARGUMENT"],
        "within_event_chch_argument_free_carriers": mode_counts["ARGUMENT_FREE"],
        "within_event_chch_context_compatible_carriers": mode_counts["INHERITED_ARGUMENT"] + mode_counts["ARGUMENT_FREE"],
        "adjacent_same_argument_bridge_chains": len(adjacent_rows),
        "adjacent_chch_bridge_chains": adjacent_pair_counts["CH+CH"],
        "adjacent_chsh_bridge_chains": adjacent_pair_counts["CH+SH"],
        "adjacent_bridge_pages": len({str(row["physical_page"]) for row in adjacent_rows}),
        "adjacent_bridge_registers": len({str(row["register"]) for row in adjacent_rows}),
        "target_context_bridge_cards": len(target_cards),
        "local_target_context_bridges": sum(row["context_bridge_locality"] == "LOCAL" for row in target_cards),
        "cross_register_target_context_bridges": sum(row["context_bridge_locality"] == "CROSS_REGISTER" for row in target_cards),
        "target_tier_counts": dict(sorted(tier_counts.items())),
        "target_phrases_changed": 0,
        "working_root_meanings_changed": 0,
        "surface_predictions": 0,
        "occurrence_predictions": 0,
        "guard": GUARD,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
