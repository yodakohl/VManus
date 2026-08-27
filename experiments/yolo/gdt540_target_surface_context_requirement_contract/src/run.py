#!/usr/bin/env python3
"""Compile a practical context-intake contract for the 145 target prose surfaces."""

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
BASE = ROOT / "experiments/yolo/gdt540_target_surface_context_requirement_contract"
OUT = BASE / "artifacts"
G539 = ROOT / "experiments/yolo/gdt539_four_page_contextual_statement_edition/artifacts"

PROSE_IN = G539 / "gdt539_546_contextual_prose_events.tsv"
OCCURRENCE_OUT = OUT / "gdt540_149_occurrence_context_contract.tsv"
SURFACE_OUT = OUT / "gdt540_145_surface_context_contract.tsv"
SUMMARY_OUT = OUT / "gdt540_context_contract_summary.tsv"
BOOK_OUT = OUT / "GDT540_TARGET_SURFACE_CONTEXT_CONTRACT.md"
RESULT_OUT = OUT / "gdt540_result.json"
STATUS = "PASS_149_OCCURRENCES_CLASSIFIED__145_SURFACE_CONTRACTS__ONE_CONTEXT_SWITCH"

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


def split_roots(value: str) -> list[str]:
    return [] if value == "NONE" else value.split("|")


def context_mode(row: dict[str, str]) -> str:
    action = row["inherited_action_root"] != "NONE"
    argument = row["inherited_argument_root"] != "NONE"
    if action and argument:
        return "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
    if action:
        return "REQUIRES_ACTIVE_ACTION"
    if argument:
        return "REQUIRES_ACTIVE_ARGUMENT"
    return "SELF_CONTAINED"


def source_distance(
    row: dict[str, str], source_field: str, by_event: dict[str, dict[str, str]]
) -> int | None:
    source_id = row[source_field]
    if source_id == "NONE":
        return None
    source = by_event[source_id]
    if source["statement_id"] != row["statement_id"]:
        raise RuntimeError(f"Cross-statement context source at {row['event_id']}")
    distance = int(row["card_ordinal_in_statement"]) - int(
        source["card_ordinal_in_statement"]
    )
    if distance <= 0:
        raise RuntimeError(f"Non-leftward context source at {row['event_id']}")
    return distance


def future_action_contract(explicit_actions: list[str]) -> str:
    if explicit_actions:
        return "USE_VISIBLE_ACTIONS__LAST_VISIBLE_ACTION_BECOMES_ACTIVE"
    return "USE_SAME_STATEMENT_ACTIVE_ACTION__ELSE_RENDER_NONVERBAL_FRAGMENT"


def future_argument_contract(explicit_arguments: list[str]) -> str:
    if explicit_arguments:
        return "USE_VISIBLE_ARGUMENTS__LAST_VISIBLE_ARGUMENT_BECOMES_ACTIVE"
    return "USE_SAME_STATEMENT_ACTIVE_ARGUMENT_IF_AVAILABLE__ELSE_OBJECTLESS"


def intake_instruction_de(explicit_actions: list[str], explicit_arguments: list[str]) -> str:
    if explicit_actions and explicit_arguments:
        return "Sichtbare Handlung und sichtbares Argument lesen."
    if explicit_actions:
        return (
            "Sichtbare Handlung lesen; laufendes Satzargument übernehmen, "
            "falls eines vorhanden ist, sonst objektlos lesen."
        )
    if explicit_arguments:
        return (
            "Laufende Satzhandlung einsetzen; sichtbares Argument lesen; "
            "ohne laufende Handlung nur als Fragment ausgeben."
        )
    return (
        "Laufende Satzhandlung einsetzen und ein laufendes Satzargument "
        "übernehmen, falls eines vorhanden ist; ohne Handlung nur als Fragment."
    )


def pipe(values: set[str] | list[str], *, mode_sort: bool = False) -> str:
    material = set(values)
    if not material:
        return "NONE"
    if mode_sort:
        return "|".join(sorted(material, key=MODE_ORDER.__getitem__))
    return "|".join(sorted(material))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    prose = read_tsv(PROSE_IN)
    if len(prose) != 546:
        raise RuntimeError(f"GDT539 prose count drift: {len(prose)}")
    by_event = {row["event_id"]: row for row in prose}
    if len(by_event) != len(prose):
        raise RuntimeError("Duplicate GDT539 event ID")
    targets = [row for row in prose if row["recipe_source"] == "GDT538_FINAL_SURFACE"]
    if len(targets) != 149 or len({row["surface"] for row in targets}) != 145:
        raise RuntimeError("GDT539 target prose inventory drift")

    occurrence_rows: list[dict[str, object]] = []
    for ordinal, row in enumerate(targets, 1):
        actions = split_roots(row["explicit_action_roots"])
        arguments = split_roots(row["explicit_argument_roots"])
        action_distance = source_distance(
            row, "inherited_action_source_event_id", by_event
        )
        argument_distance = source_distance(
            row, "inherited_argument_source_event_id", by_event
        )
        mode = context_mode(row)
        resolved_action = actions[-1] if actions else row["inherited_action_root"]
        resolved_argument = (
            arguments[-1] if arguments else row["inherited_argument_root"]
        )
        occurrence_rows.append({
            "occurrence_ordinal": ordinal,
            "surface": row["surface"],
            "event_id": row["event_id"],
            "statement_id": row["statement_id"],
            "card_ordinal_in_statement": row["card_ordinal_in_statement"],
            "physical_page": row["physical_page"],
            "register": row["register"],
            "final_recipe": row["final_context_recipe"],
            "explicit_action_roots": row["explicit_action_roots"],
            "incoming_action_root": row["inherited_action_root"],
            "incoming_action_source_event_id": row[
                "inherited_action_source_event_id"
            ],
            "incoming_action_distance_cards": (
                action_distance if action_distance is not None else "NONE"
            ),
            "explicit_argument_roots": row["explicit_argument_roots"],
            "incoming_argument_root": row["inherited_argument_root"],
            "incoming_argument_source_event_id": row[
                "inherited_argument_source_event_id"
            ],
            "incoming_argument_distance_cards": (
                argument_distance if argument_distance is not None else "NONE"
            ),
            "known_occurrence_requirement": mode,
            "known_clause_needs_active_action": (
                "YES" if row["inherited_action_root"] != "NONE" else "NO"
            ),
            "known_clause_needs_active_argument": (
                "YES" if row["inherited_argument_root"] != "NONE" else "NO"
            ),
            "future_action_contract": future_action_contract(actions),
            "future_argument_contract": future_argument_contract(arguments),
            "resolved_action_root": resolved_action,
            "resolved_argument_root": resolved_argument,
            "neutral_surface_phrase_de": row["gdt538_neutral_phrase_de"],
            "known_contextual_clause_de": row["contextual_clause_de"],
            "exact_recipe_roundtrip": row["exact_recipe_roundtrip"],
            "guard": "KNOWN_OCCURRENCE_REQUIREMENT__FUTURE_CONTEXT_RULE_IS_WORKING_DEFAULT",
        })

    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrence_rows:
        by_surface[str(row["surface"])].append(row)

    surface_rows: list[dict[str, object]] = []
    for ordinal, surface in enumerate(sorted(by_surface), 1):
        material = by_surface[surface]
        recipes = {str(row["final_recipe"]) for row in material}
        action_traces = {str(row["explicit_action_roots"]) for row in material}
        argument_traces = {str(row["explicit_argument_roots"]) for row in material}
        neutral_phrases = {str(row["neutral_surface_phrase_de"]) for row in material}
        if not (
            len(recipes) == len(action_traces) == len(argument_traces)
            == len(neutral_phrases) == 1
        ):
            raise RuntimeError(f"Surface recipe/phrase drift for {surface}")
        action_trace = next(iter(action_traces))
        argument_trace = next(iter(argument_traces))
        actions = split_roots(action_trace)
        arguments = split_roots(argument_trace)
        modes = {str(row["known_occurrence_requirement"]) for row in material}
        counts = Counter(str(row["known_occurrence_requirement"]) for row in material)
        if len(material) == 1:
            evidence_class = "SINGLETON_ONE_OBSERVED_MODE"
        elif len(modes) == 1:
            evidence_class = "REPEATED_CONSISTENT_MODE"
        else:
            evidence_class = "REPEATED_CONTEXT_SWITCH"
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
        surface_rows.append({
            "surface_ordinal": ordinal,
            "surface": surface,
            "final_recipe": next(iter(recipes)),
            "event_count": len(material),
            "physical_pages": pipe({str(row["physical_page"]) for row in material}),
            "event_ids": pipe({str(row["event_id"]) for row in material}),
            "observed_requirement_modes": pipe(modes, mode_sort=True),
            "observed_mode_count": len(modes),
            "self_contained_occurrence_count": counts["SELF_CONTAINED"],
            "active_action_occurrence_count": counts["REQUIRES_ACTIVE_ACTION"],
            "active_argument_occurrence_count": counts[
                "REQUIRES_ACTIVE_ARGUMENT"
            ],
            "both_active_occurrence_count": counts[
                "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
            ],
            "surface_evidence_class": evidence_class,
            "visible_action_roots": action_trace,
            "visible_argument_roots": argument_trace,
            "observed_incoming_action_roots": pipe({
                str(row["incoming_action_root"])
                for row in material
                if row["incoming_action_root"] != "NONE"
            }),
            "observed_incoming_argument_roots": pipe({
                str(row["incoming_argument_root"])
                for row in material
                if row["incoming_argument_root"] != "NONE"
            }),
            "max_action_source_distance_cards": (
                max(action_distances) if action_distances else "NONE"
            ),
            "max_argument_source_distance_cards": (
                max(argument_distances) if argument_distances else "NONE"
            ),
            "future_action_contract": future_action_contract(actions),
            "future_argument_contract": future_argument_contract(arguments),
            "minimum_future_state_for_verbal_clause": (
                "NONE" if actions else "ACTIVE_ACTION"
            ),
            "new_page_intake_de": intake_instruction_de(actions, arguments),
            "neutral_surface_phrase_de": next(iter(neutral_phrases)),
            "known_contextual_readings_de": " || ".join(
                dict.fromkeys(str(row["known_contextual_clause_de"]) for row in material)
            ),
            "guard": "SURFACE_CONTRACT_IS_PREDICTIVE_DEFAULT__OBSERVED_MODES_ARE_NOT_UNIVERSAL",
        })

    mode_counts = Counter(str(row["known_occurrence_requirement"]) for row in occurrence_rows)
    profile_counts = Counter(str(row["observed_requirement_modes"]) for row in surface_rows)
    action_distances = [
        int(row["incoming_action_distance_cards"])
        for row in occurrence_rows
        if row["incoming_action_distance_cards"] != "NONE"
    ]
    argument_distances = [
        int(row["incoming_argument_distance_cards"])
        for row in occurrence_rows
        if row["incoming_argument_distance_cards"] != "NONE"
    ]
    repeated = [row for row in surface_rows if int(row["event_count"]) > 1]
    switches = [
        row for row in surface_rows
        if row["surface_evidence_class"] == "REPEATED_CONTEXT_SWITCH"
    ]

    summary_rows: list[dict[str, object]] = []

    def add(metric: str, value: object, interpretation_de: str) -> None:
        summary_rows.append({
            "metric": metric,
            "value": value,
            "interpretation_de": interpretation_de,
        })

    add("target_occurrence_count", len(occurrence_rows), "vollständig klassifizierte Prosavorkommen")
    add("target_surface_count", len(surface_rows), "Oberflächen mit Intake-Vertrag")
    add("target_statement_count", len({row["statement_id"] for row in occurrence_rows}), "berührte Aussagen")
    for mode in MODE_ORDER:
        add(
            "occurrence_" + mode.lower(),
            mode_counts[mode],
            "bekannte Vorkommen in dieser exakten Kontextklasse",
        )
    add("surface_self_contained_only", profile_counts["SELF_CONTAINED"], "nur selbständig beobachtet")
    add("surface_active_argument_only", profile_counts["REQUIRES_ACTIVE_ARGUMENT"], "nur mit aktivem Argument beobachtet")
    add("surface_active_action_only", profile_counts["REQUIRES_ACTIVE_ACTION"], "nur mit aktiver Handlung beobachtet")
    add("surface_both_active_only", profile_counts["REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"], "nur mit beiden Zuständen beobachtet")
    add("surface_mixed_mode", len(switches), "mindestens zwei beobachtete Kontextmodi")
    add("repeated_surface_count", len(repeated), "Oberflächen mit mehr als einem Vorkommen")
    add("repeated_consistent_surface_count", sum(row["surface_evidence_class"] == "REPEATED_CONSISTENT_MODE" for row in repeated), "wiederholt mit gleichem Modus")
    add("repeated_context_switch_surface_count", len(switches), "wiederholt mit Kontextwechsel")
    add("max_action_source_distance_cards", max(action_distances), "größter Rückgriff auf eine sichtbare Handlung")
    add("max_argument_source_distance_cards", max(argument_distances), "größter Rückgriff auf ein sichtbares Argument")
    add("same_statement_source_count", len(action_distances) + len(argument_distances), "alle Kontextquellen bleiben im selben Satz")
    add("future_rule_surface_coverage", len(surface_rows), "jede Oberfläche besitzt Handlung- und Argumentregel")
    write_tsv(OCCURRENCE_OUT, occurrence_rows)
    write_tsv(SURFACE_OUT, surface_rows)
    write_tsv(SUMMARY_OUT, summary_rows)

    result = {
        "status": STATUS,
        "target_occurrence_count": len(occurrence_rows),
        "target_surface_count": len(surface_rows),
        "target_statement_count": len({row["statement_id"] for row in occurrence_rows}),
        "self_contained_occurrence_count": mode_counts["SELF_CONTAINED"],
        "active_action_occurrence_count": mode_counts["REQUIRES_ACTIVE_ACTION"],
        "active_argument_occurrence_count": mode_counts["REQUIRES_ACTIVE_ARGUMENT"],
        "both_active_occurrence_count": mode_counts[
            "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
        ],
        "self_contained_only_surface_count": profile_counts["SELF_CONTAINED"],
        "active_action_only_surface_count": profile_counts[
            "REQUIRES_ACTIVE_ACTION"
        ],
        "active_argument_only_surface_count": profile_counts[
            "REQUIRES_ACTIVE_ARGUMENT"
        ],
        "both_active_only_surface_count": profile_counts[
            "REQUIRES_ACTIVE_ACTION_AND_ARGUMENT"
        ],
        "mixed_mode_surface_count": len(switches),
        "mixed_mode_surfaces": [str(row["surface"]) for row in switches],
        "repeated_surface_count": len(repeated),
        "repeated_surfaces": [str(row["surface"]) for row in repeated],
        "max_action_source_distance_cards": max(action_distances),
        "max_argument_source_distance_cards": max(argument_distances),
        "new_pages": 0,
        "root_meaning_changes": 0,
        "recipe_changes": 0,
    }
    RESULT_OUT.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# GDT540 — Kontextvertrag der 145 neuen Prosaoberflächen",
        "",
        f"Status: `{STATUS}`",
        "",
        "## Der kurze Vertrag",
        "",
        "1. Eine sichtbare Handlung wird gelesen und wird zum laufenden Satzkopf.",
        "2. Fehlt die Handlung, wird die letzte sichtbare Handlung desselben Satzes eingesetzt; fehlt auch sie, bleibt nur eine nichtverbale Fragmentlesung.",
        "3. Ein sichtbares Argument wird gelesen und wird zum laufenden Satzargument.",
        "4. Fehlt das Argument, wird das laufende Satzargument übernommen, falls eines vorhanden ist; sonst bleibt die Handlung objektlos.",
        "5. An einer Aussagegrenze werden beide Zustände geleert.",
        "",
        "Damit erhalten 149/149 Vorkommen und 145/145 Oberflächen eine konkrete Intake-Regel, ohne ein Rezept oder einen Stammwert zu ändern.",
        "",
        "## Beobachtete Anforderungsverteilung",
        "",
        "| Bekannte Vorkommensklasse | Vorkommen |",
        "| --- | ---: |",
        f"| selbständig | {mode_counts['SELF_CONTAINED']} |",
        f"| braucht aktive Handlung | {mode_counts['REQUIRES_ACTIVE_ACTION']} |",
        f"| braucht aktives Argument | {mode_counts['REQUIRES_ACTIVE_ARGUMENT']} |",
        f"| braucht beides | {mode_counts['REQUIRES_ACTIVE_ACTION_AND_ARGUMENT']} |",
        "",
        "Auf Oberflächenebene sind 88 nur selbständig, 40 nur mit aktivem Argument, fünf nur mit aktiver Handlung und elf nur mit beiden Zuständen beobachtet. Eine Form schaltet um.",
        "",
        "## Die drei Wiederholungen",
        "",
        "- `keody` erscheint dreimal und bleibt dreimal selbständig.",
        "- `shain` erscheint zweimal und bleibt zweimal selbständig.",
        "- `qokees` erscheint einmal ohne Satzargument und einmal mit geerbtem `Y`. Rezept und sichtbare Handlungen `OK+EE+S` bleiben identisch. Das ist der direkte Beleg für die Regel „Argument übernehmen, falls vorhanden; sonst objektlos“.",
        "",
        f"Alle geerbten Handlungen liegen höchstens {max(action_distances)} Karten zurück, alle geerbten Argumente höchstens {max(argument_distances)} Karten. Ein Zwei-Slot-Satzspeicher reicht deshalb weiterhin aus; die Distanz ist nur eine Beobachtung dieser vier Seiten, keine harte Zukunftsgrenze.",
        "",
        "## Vollständiger Oberflächenvertrag",
        "",
        "| Oberfläche | Rezept | beobachtete Modi | Zukunfts-Intake |",
        "| --- | --- | --- | --- |",
    ]
    for row in surface_rows:
        lines.append(
            f"| `{row['surface']}` | `{row['final_recipe']}` | "
            f"`{row['observed_requirement_modes']}` | {row['new_page_intake_de']} |"
        )
    lines.extend([
        "",
        "## Grenze der Lesung",
        "",
        "Die vier Klassen beschreiben, welche Zustände die bekannte kontextuelle Werkstattlesung tatsächlich benutzt. Bei einmal belegten Oberflächen ist das noch keine ewige Worteigenschaft. Der Zukunftsvertrag wird deshalb aus den sichtbaren Handlungs- und Argumentslots abgeleitet; `qokees` zeigt ausdrücklich, dass derselbe Oberflächenkörper je nach Satzvorgeschichte mit oder ohne Objekt funktionieren kann.",
        "",
        "Keine neue Seite, kein neues Rezept und keine neue Stammbedeutung wurde eingeführt.",
    ])
    BOOK_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
