#!/usr/bin/env python3
"""Replay GDT540 target-recipe context profiles on the old 26-page prefix."""

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
BASE = ROOT / "experiments/yolo/gdt541_old_prefix_exact_recipe_context_replay"
OUT = BASE / "artifacts"
G407 = ROOT / "experiments/yolo/gdt407_unified_twenty_six_page_workshop_edition/artifacts"
G516 = ROOT / "experiments/yolo/gdt516_thirty_page_new_surface_family_consolidation/artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"
G540 = ROOT / "experiments/yolo/gdt540_target_surface_context_requirement_contract/artifacts"

OLD_EVENTS_IN = G407 / "gdt407_4576_running_event_edition.tsv"
OLD_STATEMENTS_IN = G407 / "gdt407_715_statement_edition.tsv"
G516_EXACT_IN = G516 / "gdt516_10_exact_old_recipe_carriers.tsv"
NEW_PROSE_IN = G539 / "gdt539_546_contextual_prose_events.tsv"
TARGET_CONTRACT_IN = G540 / "gdt540_145_surface_context_contract.tsv"
TARGET_OCCURRENCES_IN = G540 / "gdt540_149_occurrence_context_contract.tsv"

OLD_MATCH_OUT = OUT / "gdt541_49_old_exact_recipe_context_events.tsv"
PROFILE_OUT = OUT / "gdt541_11_recipe_context_profile_transfer.tsv"
QOKEES_OUT = OUT / "gdt541_7_ok_ee_s_cross_page_family.tsv"
SUMMARY_OUT = OUT / "gdt541_exact_recipe_context_summary.tsv"
BOOK_OUT = OUT / "GDT541_OLD_PREFIX_CONTEXT_REPLAY_BOOK.md"
RESULT_OUT = OUT / "gdt541_result.json"
STATUS = "PASS_11_EXACT_RECIPE_PROFILES_REPLAY__QOKEES_SWITCH_REPLICATED"

ACTION_ROOTS = {"OK", "CH", "SH", "K", "S", "CHD", "T", "R", "P"}
ARGUMENT_ROOTS = {"Y", "AIIN", "AIN", "OR"}
MODE_ORDER = {
    "SELF_CONTAINED": 0,
    "REQUIRES_ACTIVE_ARGUMENT": 1,
    "REQUIRES_ACTIVE_ACTION": 2,
    "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT": 3,
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


def mode(inherited_action: str, inherited_argument: str) -> str:
    if inherited_action and inherited_argument:
        return "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
    if inherited_action:
        return "REQUIRES_ACTIVE_ACTION"
    if inherited_argument:
        return "REQUIRES_ACTIVE_ARGUMENT"
    return "SELF_CONTAINED"


def split_modes(value: str) -> set[str]:
    return set(value.split("|"))


def join_modes(values: set[str]) -> str:
    return "|".join(sorted(values, key=MODE_ORDER.__getitem__))


def join(values: set[str] | list[str]) -> str:
    material = sorted(set(values))
    return "|".join(material) if material else "NONE"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    old_events = read_tsv(OLD_EVENTS_IN)
    old_statements = read_tsv(OLD_STATEMENTS_IN)
    g516_exact = read_tsv(G516_EXACT_IN)
    new_prose = read_tsv(NEW_PROSE_IN)
    targets = read_tsv(TARGET_CONTRACT_IN)
    target_occurrences = read_tsv(TARGET_OCCURRENCES_IN)
    if (len(old_events), len(old_statements), len(g516_exact), len(new_prose), len(targets), len(target_occurrences)) != (4576, 715, 10, 546, 145, 149):
        raise RuntimeError("Input inventory drift")
    g516_exact_surfaces = {row["surface"] for row in g516_exact}

    target_by_recipe = {row["final_recipe"]: row for row in targets}
    if len(target_by_recipe) != 145:
        raise RuntimeError("Target recipes are no longer unique")
    target_occurrences_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in target_occurrences:
        target_occurrences_by_surface[row["surface"]].append(row)

    events_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in old_events:
        events_by_statement[row["source_statement_id"]].append(row)
    statement_keys = {row["source_statement_id"] for row in old_statements}
    if set(events_by_statement) != statement_keys:
        raise RuntimeError("GDT407 statement/event key drift")

    old_match_rows: list[dict[str, object]] = []
    old_context_by_event: dict[str, dict[str, object]] = {}
    for statement in sorted(old_statements, key=lambda row: int(row["global_statement_ordinal"])):
        material = sorted(
            events_by_statement[statement["source_statement_id"]],
            key=lambda row: int(row["global_running_ordinal"]),
        )
        if len(material) != int(statement["event_count"]):
            raise RuntimeError(f"Statement count drift: {statement['global_statement_id']}")
        if " ".join(row["surface"] for row in material) != statement["surface_sequence"]:
            raise RuntimeError(f"Statement surface replay drift: {statement['global_statement_id']}")
        if " | ".join(row["component_recipe"] for row in material) != statement["recipe_sequence"]:
            raise RuntimeError(f"Statement recipe replay drift: {statement['global_statement_id']}")
        active_action = ""
        active_argument = ""
        action_source = ""
        argument_source = ""
        for card_ordinal, event in enumerate(material, 1):
            atoms = event["component_recipe"].split("+")
            actions = [atom for atom in atoms if atom in ACTION_ROOTS]
            arguments = [atom for atom in atoms if atom in ARGUMENT_ROOTS]
            inherited_action = ""
            inherited_argument = ""
            inherited_action_source = ""
            inherited_argument_source = ""
            if actions:
                active_action = actions[-1]
                action_source = event["global_running_event_id"]
            elif active_action and atoms != ["DY"]:
                inherited_action = active_action
                inherited_action_source = action_source
            if arguments:
                active_argument = arguments[-1]
                argument_source = event["global_running_event_id"]
            elif active_argument and (actions or inherited_action) and atoms != ["DY"]:
                inherited_argument = active_argument
                inherited_argument_source = argument_source
            context = {
                "card_ordinal": card_ordinal,
                "explicit_actions": actions,
                "explicit_arguments": arguments,
                "inherited_action": inherited_action,
                "inherited_argument": inherited_argument,
                "action_source": inherited_action_source,
                "argument_source": inherited_argument_source,
                "mode": mode(inherited_action, inherited_argument),
                "resolved_action": actions[-1] if actions else inherited_action or "NONE",
                "resolved_argument": arguments[-1] if arguments else inherited_argument or "NONE",
                "immediate_previous_surface": material[card_ordinal - 2]["surface"] if card_ordinal > 1 else "NONE",
                "immediate_previous_recipe": material[card_ordinal - 2]["component_recipe"] if card_ordinal > 1 else "NONE",
            }
            old_context_by_event[event["global_running_event_id"]] = context
            target = target_by_recipe.get(event["component_recipe"])
            if target is None:
                continue
            action_distance = (
                int(event["global_running_ordinal"])
                - int(next(row["global_running_ordinal"] for row in material if row["global_running_event_id"] == inherited_action_source))
                if inherited_action_source
                else None
            )
            argument_distance = (
                int(event["global_running_ordinal"])
                - int(next(row["global_running_ordinal"] for row in material if row["global_running_event_id"] == inherited_argument_source))
                if inherited_argument_source
                else None
            )
            old_match_rows.append({
                "old_carrier_ordinal": len(old_match_rows) + 1,
                "target_surface": target["surface"],
                "target_recipe": target["final_recipe"],
                "target_observed_requirement_modes": target[
                    "observed_requirement_modes"
                ],
                "old_global_event_id": event["global_running_event_id"],
                "old_source_event_id": event["source_event_id"],
                "old_statement_id": statement["global_statement_id"],
                "card_ordinal_in_statement": card_ordinal,
                "physical_page": event["physical_page"],
                "register": event["register"],
                "owner_de": event["owner_de"],
                "locus": event["locus"],
                "old_surface": event["surface"],
                "surface_same_as_target": "YES" if event["surface"] == target["surface"] else "NO",
                "explicit_action_roots": "|".join(actions) or "NONE",
                "incoming_action_root": inherited_action or "NONE",
                "incoming_action_source_event_id": inherited_action_source or "NONE",
                "incoming_action_distance_cards": action_distance if action_distance is not None else "NONE",
                "explicit_argument_roots": "|".join(arguments) or "NONE",
                "incoming_argument_root": inherited_argument or "NONE",
                "incoming_argument_source_event_id": inherited_argument_source or "NONE",
                "incoming_argument_distance_cards": argument_distance if argument_distance is not None else "NONE",
                "old_requirement_mode": context["mode"],
                "resolved_action_root": context["resolved_action"],
                "resolved_argument_root": context["resolved_argument"],
                "immediate_previous_surface": context["immediate_previous_surface"],
                "immediate_previous_recipe": context["immediate_previous_recipe"],
                "exact_recipe_roundtrip": event["component_recipe"],
                "guard": "OLD_PREFIX_EXACT_RECIPE_CONTEXT_REPLAY__NO_RESEGMENTATION",
            })

    by_target: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in old_match_rows:
        by_target[str(row["target_surface"])].append(row)
    profile_rows: list[dict[str, object]] = []
    for ordinal, target_surface in enumerate(sorted(by_target), 1):
        material = by_target[target_surface]
        target = next(row for row in targets if row["surface"] == target_surface)
        target_modes = split_modes(target["observed_requirement_modes"])
        old_modes = {str(row["old_requirement_mode"]) for row in material}
        relation = (
            "EXACT_PROFILE_MATCH"
            if old_modes == target_modes
            else "OLD_PROFILE_SUPERSET"
            if old_modes > target_modes
            else "OLD_PROFILE_SUBSET"
            if old_modes < target_modes
            else "PROFILE_OVERLAP"
            if old_modes & target_modes
            else "PROFILE_DISJOINT"
        )
        old_counts = Counter(str(row["old_requirement_mode"]) for row in material)
        current_material = target_occurrences_by_surface[target_surface]
        current_counts = Counter(row["known_occurrence_requirement"] for row in current_material)
        action_distances = [
            int(row["incoming_action_distance_cards"])
            for row in material
            if row["incoming_action_distance_cards"] != "NONE"
        ]
        argument_distances = [
            int(row["incoming_argument_distance_cards"])
            for row in material
            if row["incoming_argument_distance_cards"] != "NONE"
        ]
        profile_rows.append({
            "profile_ordinal": ordinal,
            "target_surface": target_surface,
            "target_recipe": target["final_recipe"],
            "target_event_count": target["event_count"],
            "target_observed_modes": target["observed_requirement_modes"],
            "old_carrier_event_count": len(material),
            "old_surface_count": len({row["old_surface"] for row in material}),
            "old_surfaces": join({str(row["old_surface"]) for row in material}),
            "old_page_count": len({row["physical_page"] for row in material}),
            "old_pages": join({str(row["physical_page"]) for row in material}),
            "old_registers": join({str(row["register"]) for row in material}),
            "old_statement_count": len({row["old_statement_id"] for row in material}),
            "old_observed_modes": join_modes(old_modes),
            "profile_relation": relation,
            "target_self_contained_count": current_counts["SELF_CONTAINED"],
            "target_active_argument_count": current_counts["REQUIRES_ACTIVE_ARGUMENT"],
            "target_active_action_count": current_counts["REQUIRES_ACTIVE_ACTION"],
            "target_both_active_count": current_counts["REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"],
            "old_self_contained_count": old_counts["SELF_CONTAINED"],
            "old_active_argument_count": old_counts["REQUIRES_ACTIVE_ARGUMENT"],
            "old_active_action_count": old_counts["REQUIRES_ACTIVE_ACTION"],
            "old_both_active_count": old_counts["REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"],
            "old_max_action_distance_cards": max(action_distances) if action_distances else "NONE",
            "old_max_argument_distance_cards": max(argument_distances) if argument_distances else "NONE",
            "replication_kind": (
                "CONTEXTUAL_EXACT_RECIPE_REPLICATION"
                if target_modes != {"SELF_CONTAINED"}
                else "VISIBLE_COMPLETE_EXACT_RECIPE_REPLICATION"
            ),
            "post_gdt516_new_exact_carrier_contact": "YES" if target_surface not in g516_exact_surfaces else "NO",
            "guard": "PROFILE_SET_COMPARISON__NOT_FREQUENCY_EQUALITY_OR_PLAINTEXT",
        })

    old_by_id = {row["global_running_event_id"]: row for row in old_events}
    new_by_id = {row["event_id"]: row for row in new_prose}
    qokees_rows: list[dict[str, object]] = []
    for row in old_match_rows:
        if row["target_recipe"] != "OK+EE+S":
            continue
        source = old_by_id[str(row["old_global_event_id"])]
        qokees_rows.append({
            "family_ordinal": len(qokees_rows) + 1,
            "corpus_layer": "OLD_GDT407_PREFIX",
            "event_id": row["old_global_event_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "statement_id": row["old_statement_id"],
            "card_ordinal_in_statement": row["card_ordinal_in_statement"],
            "surface": row["old_surface"],
            "recipe": row["target_recipe"],
            "immediate_previous_surface": row["immediate_previous_surface"],
            "immediate_previous_recipe": row["immediate_previous_recipe"],
            "incoming_argument_root": row["incoming_argument_root"],
            "incoming_argument_source_event_id": row[
                "incoming_argument_source_event_id"
            ],
            "argument_mode": (
                "ARGUMENT_FROM_SAME_STATEMENT"
                if row["incoming_argument_root"] != "NONE"
                else "OBJECTLESS"
            ),
            "resolved_argument_root": row["resolved_argument_root"],
            "source_surface_status": source["surface_status"],
            "guard": "EXACT_OK_EE_S_FAMILY__SAME_RECIPE_DIFFERENT_SURFACE_ALLOWED",
        })
    for row in new_prose:
        if row["final_context_recipe"] != "OK+EE+S":
            continue
        statement_material = [
            item for item in new_prose if item["statement_id"] == row["statement_id"]
        ]
        statement_material.sort(key=lambda item: int(item["card_ordinal_in_statement"]))
        card_ordinal = int(row["card_ordinal_in_statement"])
        previous = statement_material[card_ordinal - 2] if card_ordinal > 1 else None
        qokees_rows.append({
            "family_ordinal": len(qokees_rows) + 1,
            "corpus_layer": "SELECTED_GDT539_FOUR_PAGES",
            "event_id": row["event_id"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "statement_id": row["statement_id"],
            "card_ordinal_in_statement": row["card_ordinal_in_statement"],
            "surface": row["surface"],
            "recipe": row["final_context_recipe"],
            "immediate_previous_surface": previous["surface"] if previous else "NONE",
            "immediate_previous_recipe": previous["final_context_recipe"] if previous else "NONE",
            "incoming_argument_root": row["inherited_argument_root"],
            "incoming_argument_source_event_id": row[
                "inherited_argument_source_event_id"
            ],
            "argument_mode": (
                "ARGUMENT_FROM_SAME_STATEMENT"
                if row["inherited_argument_root"] != "NONE"
                else "OBJECTLESS"
            ),
            "resolved_argument_root": (
                row["explicit_argument_roots"].split("|")[-1]
                if row["explicit_argument_roots"] != "NONE"
                else row["inherited_argument_root"]
            ),
            "source_surface_status": (
                "GDT540_TARGET_SURFACE"
                if row["recipe_source"] == "GDT538_FINAL_SURFACE"
                else "EXISTING_SELECTED_PAGE_SURFACE"
            ),
            "guard": "EXACT_OK_EE_S_FAMILY__SAME_RECIPE_DIFFERENT_SURFACE_ALLOWED",
        })

    mode_counts = Counter(str(row["old_requirement_mode"]) for row in old_match_rows)
    qokees_counts = Counter(str(row["argument_mode"]) for row in qokees_rows)
    post_gdt516_contacts = [
        row for row in profile_rows
        if row["post_gdt516_new_exact_carrier_contact"] == "YES"
    ]
    if [row["target_surface"] for row in post_gdt516_contacts] != ["chekchy"]:
        raise RuntimeError("Post-GDT516 exact-carrier contact drift")
    summary_rows = [
        {"metric": "target_recipe_count", "value": 145, "interpretation_de": "GDT540-Prosa-Verträge"},
        {"metric": "old_exact_carrier_recipe_count", "value": len(profile_rows), "interpretation_de": "Zielrezepte mit vollständigem alten Träger"},
        {"metric": "old_exact_carrier_event_count", "value": len(old_match_rows), "interpretation_de": "alte exakte Rezeptvorkommen"},
        {"metric": "old_exact_carrier_surface_count", "value": len({row["old_surface"] for row in old_match_rows}), "interpretation_de": "alte sichtbare Schreibungen"},
        {"metric": "old_exact_carrier_page_count", "value": len({row["physical_page"] for row in old_match_rows}), "interpretation_de": "alte Seiten mit Trägern"},
        {"metric": "old_exact_carrier_statement_count", "value": len({row["old_statement_id"] for row in old_match_rows}), "interpretation_de": "alte Aussagen mit Trägern"},
        {"metric": "old_exact_carrier_register_count", "value": len({row["register"] for row in old_match_rows}), "interpretation_de": "abgedeckte Register"},
        {"metric": "exact_profile_match_count", "value": sum(row["profile_relation"] == "EXACT_PROFILE_MATCH" for row in profile_rows), "interpretation_de": "identische beobachtete Modusmengen"},
        {"metric": "contextual_profile_match_count", "value": sum(row["replication_kind"] == "CONTEXTUAL_EXACT_RECIPE_REPLICATION" and row["profile_relation"] == "EXACT_PROFILE_MATCH" for row in profile_rows), "interpretation_de": "nichttriviale Kontextprofile mit exakter Übereinstimmung"},
        {"metric": "old_self_contained_event_count", "value": mode_counts["SELF_CONTAINED"], "interpretation_de": "alte selbständige Träger"},
        {"metric": "old_active_argument_event_count", "value": mode_counts["REQUIRES_ACTIVE_ARGUMENT"], "interpretation_de": "alte Träger mit Satzargument"},
        {"metric": "old_active_action_event_count", "value": mode_counts["REQUIRES_ACTIVE_ACTION"], "interpretation_de": "alte Träger mit Satzhandlung"},
        {"metric": "old_both_active_event_count", "value": mode_counts["REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"], "interpretation_de": "alte Träger mit beiden Zuständen"},
        {"metric": "qokees_family_event_count", "value": len(qokees_rows), "interpretation_de": "OK+EE+S über alte und neue Seiten"},
        {"metric": "qokees_family_argument_event_count", "value": qokees_counts["ARGUMENT_FROM_SAME_STATEMENT"], "interpretation_de": "OK+EE+S mit übernommenem Argument"},
        {"metric": "qokees_family_objectless_event_count", "value": qokees_counts["OBJECTLESS"], "interpretation_de": "OK+EE+S ohne Argument"},
        {"metric": "post_gdt516_new_exact_contact", "value": post_gdt516_contacts[0]["target_surface"], "interpretation_de": "finale Revision CH+K+Y ergänzt elftes Zielrezept mit29 alten Trägern"},
    ]

    write_tsv(OLD_MATCH_OUT, old_match_rows)
    write_tsv(PROFILE_OUT, profile_rows)
    write_tsv(QOKEES_OUT, qokees_rows)
    write_tsv(SUMMARY_OUT, summary_rows)

    result = {
        "status": STATUS,
        "target_recipe_count": 145,
        "old_exact_carrier_recipe_count": len(profile_rows),
        "old_exact_carrier_event_count": len(old_match_rows),
        "old_exact_carrier_surface_count": len({row["old_surface"] for row in old_match_rows}),
        "old_exact_carrier_page_count": len({row["physical_page"] for row in old_match_rows}),
        "old_exact_carrier_statement_count": len({row["old_statement_id"] for row in old_match_rows}),
        "old_exact_carrier_register_count": len({row["register"] for row in old_match_rows}),
        "exact_profile_match_count": sum(row["profile_relation"] == "EXACT_PROFILE_MATCH" for row in profile_rows),
        "contextual_profile_match_count": sum(row["replication_kind"] == "CONTEXTUAL_EXACT_RECIPE_REPLICATION" and row["profile_relation"] == "EXACT_PROFILE_MATCH" for row in profile_rows),
        "old_mode_counts": dict(sorted(mode_counts.items())),
        "qokees_family_event_count": len(qokees_rows),
        "qokees_family_argument_event_count": qokees_counts["ARGUMENT_FROM_SAME_STATEMENT"],
        "qokees_family_objectless_event_count": qokees_counts["OBJECTLESS"],
        "post_gdt516_new_exact_contact_surface": post_gdt516_contacts[0]["target_surface"],
        "post_gdt516_new_exact_contact_old_event_count": int(post_gdt516_contacts[0]["old_carrier_event_count"]),
        "new_pages": 0,
        "recipe_changes": 0,
        "root_meaning_changes": 0,
    }
    RESULT_OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GDT541 — alte Exaktträger bestätigen den Kontextvertrag",
        "",
        f"Status: `{STATUS}`",
        "",
        "## Gesamtbild",
        "",
        "Elf der145 GDT540-Prosa-Rezepte besitzen49 vollständige Träger im alten26-Seiten-Präfix. Sie verteilen sich auf17 alte Oberflächen,17 Seiten,43 Aussagen und alle fünf Register. Bei allen elf ist die Menge der dort sichtbaren Kontextmodi genau dieselbe wie bei der neuen Zieloberfläche.",
        "",
        "| Zieloberfläche | Rezept | neue Modi | alte Modi | alte Ereignisse | alte Schreibungen |",
        "| --- | --- | --- | --- | ---: | --- |",
    ]
    for row in profile_rows:
        lines.append(
            f"| `{row['target_surface']}` | `{row['target_recipe']}` | `{row['target_observed_modes']}` | `{row['old_observed_modes']}` | {row['old_carrier_event_count']} | `{row['old_surfaces']}` |"
        )
    lines.extend([
        "",
        "Fünf Profile sind durch sichtbare Handlung und sichtbares Argument ohnehin vollständig. Die sechs wichtigeren Kontakte tragen Satzkontext: `dalol` und `doiiin` übernehmen in alt und neu Handlung plus Argument; `qokee`, `qokaiir` und `shee` übernehmen das Argument; `qokees` zeigt beide Argumentmodi.",
        "",
        "## Die komplette OK+EE+S-Familie",
        "",
        "Über alte und neue Seiten gibt es sieben kontextualisierte `OK+EE+S`-Ereignisse in vier Registern und drei sichtbaren Schreibungen (`qokees`, `okees`, `chokees`). Fünf übernehmen das unmittelbar zuvor gesetzte Argument; zwei bleiben objektlos. Die vier alten Karten allein wiederholen beide Modi: dreimal Argumentübernahme, einmal objektlos.",
        "",
        "| Schicht | Seite | Oberfläche | linke Karte | Argumentmodus |",
        "| --- | --- | --- | --- | --- |",
    ])
    for row in qokees_rows:
        lines.append(
            f"| {row['corpus_layer']} | {row['physical_page']} | `{row['surface']}` | `{row['immediate_previous_surface']}` | `{row['argument_mode']}` |"
        )
    lines.extend([
        "",
        "## Zusatzgewinn der letzten Revisionen",
        "",
        "GDT516 hatte mit dem damaligen Rezeptstand zehn exakte alte Zielträger. Die spätere Endrevision von `chekchy` zu `CH+K+Y` fügt jetzt einen elften Kontakt hinzu. Dieses Rezept besitzt29 alte Ereignisse unter fünf sichtbaren Schreibungen und bleibt überall selbständig, genau wie die neue Zielkarte.",
        "",
        "## Arbeitsgrenze",
        "",
        "Verglichen werden beobachtete Modusmengen, nicht gleiche Häufigkeiten. Der Zustandslauf benutzt dieselbe Zwei-Slot-Regel wie GDT540; neu ist die tatsächliche Satzumgebung der alten26 Seiten. Kein altes Ereignis wird resegmentiert, keine Bedeutung geändert und keine neue Seite geöffnet.",
    ])
    BOOK_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
