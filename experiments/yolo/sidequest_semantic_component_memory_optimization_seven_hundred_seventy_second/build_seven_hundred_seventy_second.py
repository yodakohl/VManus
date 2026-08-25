#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P759 = ROOT / "experiments/yolo/sidequest_semantic_forward_teaching_compiler_seven_hundred_fifty_ninth"
P760 = ROOT / "experiments/yolo/sidequest_semantic_parameterized_apprentice_rules_seven_hundred_sixtieth"
P763 = ROOT / "experiments/yolo/sidequest_semantic_workshop_curriculum_seven_hundred_sixty_third"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def sequence_components(sequence: str) -> set[str]:
    result: set[str] = set()
    for recipe in sequence.split(" | "):
        for component in recipe.split("+"):
            match = re.fullmatch(r"UNPACKED\(([^)]+)\)", component)
            result.add(match.group(1) if match else component)
    return result


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read(P763 / "SEVEN_HUNDRED_SIXTY_THIRD_39_COMPONENT_LESSONS.tsv")
    cards = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_173_CARD_DICTIONARY.tsv")
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    rules = read(P760 / "SEVEN_HUNDRED_SIXTIETH_9_PARAMETERIZED_RULES.tsv")
    variants = {row["rule_id"]: row for row in read(P759 / "SEVEN_HUNDRED_FIFTY_NINTH_25_CONTEXT_RULES.tsv")}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    rule_needs: dict[str, set[str]] = {}
    rule_union: set[str] = set()
    for row in rules:
        needed: set[str] = set()
        for variant_id in row["variant_ids"].split(","):
            variant = variants[variant_id]
            needed |= sequence_components(variant["trigger_recipe_sequence"])
            needed |= sequence_components(variant["replacement_recipe_sequence"])
        rule_needs[row["meta_rule_id"]] = needed
        rule_union |= needed
    all_components = {row["component"] for row in components}
    fast = {row["component"] for row in components[:12]}
    model_only = all_components - rule_union
    assert model_only == {"LSH", "CFH", "DA", "LD", "OS", "TALAM"}

    assignments = []
    for row in components:
        component = row["component"]
        if component in fast:
            tier = "FAST_12_ORAL_CORE"
            method = "memorize and answer without looking"
        elif component in rule_union:
            tier = "WALL_21_RULE_STRIP"
            method = "point to wall strip while composing a licensed rule"
        else:
            tier = "MODEL_ONLY_6_RARE_VALUES"
            method = "copy only inside its registered whole-card model"
        assignments.append({
            "rank": row["rank"],
            "component": component,
            "short_value_de": row["short_value_de"],
            "events": row["events"],
            "exact_cards": row["exact_cards"],
            "new_tier": tier,
            "learning_method": method,
            "needed_by_parameterized_rules": sum(component in needed for needed in rule_needs.values()),
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_SECOND_39_COMPONENT_ASSIGNMENT.tsv",
        assignments,
        ["rank", "component", "short_value_de", "events", "exact_cards", "new_tier", "learning_method", "needed_by_parameterized_rules"],
    )

    rule_rows = []
    for row in rules:
        needed = rule_needs[row["meta_rule_id"]]
        rule_rows.append({
            "meta_rule_id": row["meta_rule_id"],
            "name_de": row["name_de"],
            "components_needed": ",".join(sorted(needed)),
            "component_count": len(needed),
            "fast_components": len(needed & fast),
            "wall_components": len(needed & (rule_union - fast)),
            "model_only_components": len(needed & model_only),
            "usable_with_33_rule_vocabulary": "YES" if needed <= rule_union else "NO",
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_SECOND_9_RULE_COMPONENT_NEEDS.tsv",
        rule_rows,
        ["meta_rule_id", "name_de", "components_needed", "component_count", "fast_components", "wall_components", "model_only_components", "usable_with_33_rule_vocabulary"],
    )

    card_access = []
    card_access_map: dict[str, str] = {}
    for row in cards:
        recipe_components = set(row["component_recipe"].split("+"))
        if recipe_components <= fast:
            access = "FAST_ORAL_COMPOSITION"
        elif recipe_components <= rule_union:
            access = "WALL_STRIP_COMPOSITION"
        else:
            access = "REGISTERED_WHOLE_CARD_MODEL_LOOKUP"
        card_access_map[row["exact_card_id"]] = access
        card_access.append({
            "exact_card_id": row["exact_card_id"],
            "registered_surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"],
            "rebuilt_reading_de": row["rebuilt_reading_de"],
            "events": row["events"],
            "access_mode": access,
            "model_only_components": ",".join(sorted(recipe_components & model_only)) or "NONE",
            "reading_changed": "NO",
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_SECOND_173_CARD_RECIPE_ACCESS.tsv",
        card_access,
        ["exact_card_id", "registered_surfaces", "component_recipe", "rebuilt_reading_de", "events", "access_mode", "model_only_components", "reading_changed"],
    )

    statement_access = []
    for statement_id, rows in by_statement.items():
        modes = [card_access_map[row["card_no"]] for row in rows]
        if all(mode == "FAST_ORAL_COMPOSITION" for mode in modes):
            access = "FAST_ONLY"
        elif "REGISTERED_WHOLE_CARD_MODEL_LOOKUP" in modes:
            access = "USES_RARE_MODEL_CARD"
        else:
            access = "FAST_PLUS_WALL_STRIP"
        statement_access.append({
            "statement_id": statement_id,
            "page": rows[0]["page"],
            "record": rows[0]["record"],
            "events": len(rows),
            "access_mode": access,
            "fast_cards": sum(mode == "FAST_ORAL_COMPOSITION" for mode in modes),
            "wall_cards": sum(mode == "WALL_STRIP_COMPOSITION" for mode in modes),
            "model_cards": sum(mode == "REGISTERED_WHOLE_CARD_MODEL_LOOKUP" for mode in modes),
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_SECOND_116_STATEMENT_ACCESS.tsv",
        statement_access,
        ["statement_id", "page", "record", "events", "access_mode", "fast_cards", "wall_cards", "model_cards"],
    )

    options = []
    for label, vocabulary in (
        ("TOP_8", {row["component"] for row in components[:8]}),
        ("TOP_12", fast),
        ("TOP_18", {row["component"] for row in components[:18]}),
        ("TOP_27", {row["component"] for row in components[:27]}),
        ("RULE_33", rule_union),
        ("ALL_39", all_components),
    ):
        composable_cards = {row["exact_card_id"] for row in cards if set(row["component_recipe"].split("+")) <= vocabulary}
        options.append({
            "option": label,
            "components": len(vocabulary),
            "composable_cards": len(composable_cards),
            "composable_events": sum(int(row["events"]) for row in cards if row["exact_card_id"] in composable_cards),
            "fully_composable_statements": sum(all(event["card_no"] in composable_cards for event in rows) for rows in by_statement.values()),
            "usable_parameterized_rules": sum(needed <= vocabulary for needed in rule_needs.values()),
            "decision": "SELECT" if label == "RULE_33" else "REFERENCE",
        })
    write(
        "SEVEN_HUNDRED_SEVENTY_SECOND_6_VOCABULARY_OPTIONS.tsv",
        options,
        ["option", "components", "composable_cards", "composable_events", "fully_composable_statements", "usable_parameterized_rules", "decision"],
    )

    report = """# Pass 772 — Zwoelf Werte im Mund, einundzwanzig an der Wand

Die39 Komponenten teilen sich besser als bisher:

-12 schnelle Kernwerte werden frei gesprochen und geschrieben;
-21 weitere Werte stehen auf einer Werkstattleiste, weil mindestens eine der neun Packregeln sie braucht;
-6 seltene Werte (`LSH, CFH, DA, LD, OS, TALAM`) bleiben nur in ihren sieben Ganzkartenmodellen.

Die33 Regelwerte halten alle neun Handgriffe ausführbar. Sie komponieren166 der173 Karten und373 der381 sichtbaren Ereignisse;109 der116 Aussagen brauchen kein seltenes Modell. Die sechs Modellwerte betreffen nur sieben Karten, acht Ereignisse und sieben Aussagen. Keine deutsche Kartenlesung wird geändert.

Das ist besser als stumpf die häufigsten27 zu lernen: Top27 komponiert zwar361 Ereignisse, lässt aber vier der neun Handgriffe ohne alle benötigten Werte. Die33er-Auswahl ist nicht bloß Häufigkeitsrang, sondern das kleinste hier verwendete Regelvokabular.

Als naechstes wird der Stundenplan auf12 oral +21 Wandleiste +6 Modellwerte umgestellt. Dann werden die sieben modellabhängigen Aussagen als konkrete Meisterblattübungen ausgeschrieben.
"""
    (HERE / "SEVEN_HUNDRED_SEVENTY_SECOND_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "fast_components": len(fast),
        "wall_components": len(rule_union - fast),
        "model_only_components": len(model_only),
        "rules_usable": sum(row["usable_with_33_rule_vocabulary"] == "YES" for row in rule_rows),
        "fast_cards": sum(row["access_mode"] == "FAST_ORAL_COMPOSITION" for row in card_access),
        "wall_cards": sum(row["access_mode"] == "WALL_STRIP_COMPOSITION" for row in card_access),
        "model_cards": sum(row["access_mode"] == "REGISTERED_WHOLE_CARD_MODEL_LOOKUP" for row in card_access),
        "fast_events": sum(int(row["events"]) for row in card_access if row["access_mode"] == "FAST_ORAL_COMPOSITION"),
        "wall_events": sum(int(row["events"]) for row in card_access if row["access_mode"] == "WALL_STRIP_COMPOSITION"),
        "model_events": sum(int(row["events"]) for row in card_access if row["access_mode"] == "REGISTERED_WHOLE_CARD_MODEL_LOOKUP"),
        "decision": "FAST12_PLUS_WALL21_PLUS_MODEL6__ALL_NINE_RULES_PRESERVED",
    }
    (HERE / "SEVEN_HUNDRED_SEVENTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
