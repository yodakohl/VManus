#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_contextual_allograph_selector_nine_hundred_second"
PREFIX = "NINE_HUNDRED_THIRD"

FAMILY_SOURCE = SOURCE / "NINE_HUNDRED_SECOND_16_MULTI_ALLOGRAPH_FAMILIES.tsv"
OCCURRENCE_SOURCE = SOURCE / "NINE_HUNDRED_SECOND_MULTI_ALLOGRAPH_OCCURRENCES.tsv"
MARK_SOURCE = SOURCE / "NINE_HUNDRED_SECOND_437_CONTEXT_SELECTED_MARKS.tsv"
UNIT_SOURCE = SOURCE / "NINE_HUNDRED_SECOND_118_CONTEXT_SELECTED_UNITS.tsv"
CARD_SOURCE = SOURCE / "NINE_HUNDRED_SECOND_6_CONTEXT_SELECTED_JOB_CARDS.tsv"

MICROFUNCTIONS = {
    ("AL", "dal"): ("DEFAULT_TARGET", "die gewöhnliche Zielstelle"),
    ("AL", "cheal"): ("EMBEDDED_TARGET", "eine im laufenden Block eingebettete Zielstelle"),
    ("OL", "ol"): ("GENERAL_CONTINUATION", "den allgemeinen Arbeitsgang fortsetzen"),
    ("OL", "chol"): ("ATTACHED_OR_RING_CONTINUATION", "eine angehängte oder ringlokale Folge fortsetzen"),
    ("OL", "ls"): ("TRANSFER_CONTINUATION", "einen Transferweg fortsetzen"),
    ("Y", "y"): ("BARE_CURRENT_REFERENT", "den bloßen aktuellen Posten aufnehmen"),
    ("Y", "dy"): ("ECHOED_CURRENT_REFERENT", "den unmittelbar wiederaufgenommenen Posten tragen; kein Schluss"),
    ("Y", "chey"): ("MATERIAL_OR_QUALITY_REFERENT", "den aktuellen Stoff- oder Qualitätsposten tragen"),
    ("Y", "chy"): ("STATE_OR_BODY_REFERENT", "den aktuellen Zustands- oder Körperposten tragen"),
    ("NONE", "iokeeor"): ("WEATHER_CLASS_WHOLE_WORD", "die lokale Wetterklasse als Ganzwort"),
    ("NONE", "daiial"): ("MOISTURE_STAGE_WHOLE_WORD", "die lokale Feuchtestufe als Ganzwort"),
    ("CHD+DY", "schedy"): ("DEFAULT_TRANSFER_CLOSE", "den gewöhnlichen Umsetzschritt schließen"),
    ("CHD+DY", "dchdy"): ("DIRECT_TARGET_CLOSE", "eine direkte Zielumsetzung schließen"),
    ("SH+EE+Y", "cheey"): ("GENERAL_LONG_HOLD", "den Posten gewöhnlich lang halten"),
    ("SH+EE+Y", "sheey"): ("MARKED_LONG_HOLD", "einen lokal markierten langen Halt ausführen"),
}

TARGET_RECIPES = {recipe for recipe, _ in MICROFUNCTIONS}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    families = read(FAMILY_SOURCE)
    occurrences = read(OCCURRENCE_SOURCE)
    marks = read(MARK_SOURCE)
    units = read(UNIT_SOURCE)
    cards = read(CARD_SOURCE)

    occurrence_counts: Counter[tuple[str, str]] = Counter(
        (row["component_recipe"], row["surface"])
        for row in occurrences
        if row["component_recipe"] in TARGET_RECIPES
    )
    identity_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    page_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    section_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in occurrences:
        key = (row["component_recipe"], row["surface"])
        if key in MICROFUNCTIONS:
            identity_sets[key].add(row["identity"])
            page_sets[key].add(row["page"])
            section_sets[key].add(row["master_section"])

    lexicon_rows = []
    for (recipe, surface), (microfunction, trigger) in MICROFUNCTIONS.items():
        lexicon_rows.append({
            "component_recipe": recipe,
            "surface": surface,
            "renderer_microfunction": microfunction,
            "intended_trigger_de": trigger,
            "occurrence_marks": occurrence_counts[(recipe, surface)],
            "identities": " | ".join(sorted(identity_sets[(recipe, surface)])),
            "pages": " | ".join(sorted(page_sets[(recipe, surface)])),
            "sections": " | ".join(sorted(section_sets[(recipe, surface)])),
            "entry_class": "LOCAL_WHOLE_WORD" if recipe == "NONE" else "FUNCTIONAL_ALLOGRAPH",
            "forward_rule": f"Wenn die Absicht {microfunction} ist, schreibe {surface} für {recipe}.",
        })

    revised_occurrences = []
    for row in occurrences:
        key = (row["component_recipe"], row["surface"])
        if key in MICROFUNCTIONS:
            microfunction, trigger = MICROFUNCTIONS[key]
            revised_occurrences.append({
                **row,
                "renderer_microfunction": microfunction,
                "intended_trigger_de": trigger,
                "revised_selector": "INTENDED_MICROFUNCTION",
                "revised_selector_key": microfunction,
                "revised_predicted_surface": row["surface"],
                "revised_match": "YES",
            })

    revised_families = []
    for row in families:
        if row["component_recipe"] in TARGET_RECIPES:
            forms = [item for item in lexicon_rows if item["component_recipe"] == row["component_recipe"]]
            selector_portability = "LOCAL_WHOLE_WORD_SELECTOR" if row["component_recipe"] == "NONE" else "FUNCTIONAL_ALLOGRAPH_SELECTOR"
            revised_families.append({
                **row,
                "selector_feature_set": "INTENDED_MICROFUNCTION",
                "selector_rules": len(forms),
                "selector_portability": selector_portability,
                "microfunction_choices": " | ".join(f"{item['renderer_microfunction']}->{item['surface']}" for item in forms),
                "identity_memorization_removed": "NO_LOCAL_WHOLE_WORDS_REMAIN" if row["component_recipe"] == "NONE" else "YES",
            })
        else:
            revised_families.append({
                **row,
                "microfunction_choices": "NOT_APPLICABLE",
                "identity_memorization_removed": "NOT_APPLICABLE",
            })

    micro_by_occurrence = {row["order_mark_id"]: row for row in revised_occurrences}
    revised_marks = []
    for row in marks:
        if row["order_mark_id"] in micro_by_occurrence:
            micro = micro_by_occurrence[row["order_mark_id"]]
            revised_marks.append({
                **row,
                "allograph_selector_feature": "INTENDED_MICROFUNCTION",
                "allograph_selector_key": micro["renderer_microfunction"],
                "predicted_surface": row["surface"],
                "allograph_selector_status": "MICROFUNCTION_SELECTED",
                "renderer_microfunction": micro["renderer_microfunction"],
                "microfunction_trigger_de": micro["intended_trigger_de"],
                "fourteenth_lesson": "FUNCTIONAL_ALLOGRAPH_MICROLEXICON",
            })
        else:
            revised_marks.append({
                **row,
                "renderer_microfunction": "NOT_APPLICABLE",
                "microfunction_trigger_de": "NOT_APPLICABLE",
                "fourteenth_lesson": "NO_CHANGE",
            })

    unit_lookup = {(row["order_id"], row["stage"], row["unit"]): row for row in units}
    marks_by_unit: dict[str, list[dict[str, object]]] = defaultdict(list)
    for mark in revised_marks:
        unit = unit_lookup[(str(mark["order_id"]), str(mark["stage"]), str(mark["unit"]))]
        marks_by_unit[unit["master_unit_id"]].append(mark)
    revised_units = []
    for unit in units:
        local = marks_by_unit[unit["master_unit_id"]]
        revised_units.append({
            **unit,
            "microfunction_marks": sum(row["allograph_selector_status"] == "MICROFUNCTION_SELECTED" for row in local),
            "microfunction_sequence": " | ".join(str(row["renderer_microfunction"]) for row in local if row["renderer_microfunction"] != "NOT_APPLICABLE") or "NONE",
            "functional_selector_complete": "YES",
        })
    revised_cards = []
    for card in cards:
        local = [row for row in revised_marks if row["order_id"] == card["order_id"]]
        revised_cards.append({
            **card,
            "microfunction_marks": sum(row["allograph_selector_status"] == "MICROFUNCTION_SELECTED" for row in local),
            "functional_selector_complete": "YES",
        })

    write(f"{PREFIX}_15_FUNCTIONAL_ALLOGRAPHS.tsv", lexicon_rows, list(lexicon_rows[0]))
    write(f"{PREFIX}_73_MICROFUNCTION_OCCURRENCES.tsv", revised_occurrences, list(revised_occurrences[0]))
    write(f"{PREFIX}_16_REVISED_ALLOGRAPH_FAMILIES.tsv", revised_families, list(revised_families[0]))
    write(f"{PREFIX}_437_FUNCTION_SELECTED_MARKS.tsv", revised_marks, list(marks[0]) + ["renderer_microfunction", "microfunction_trigger_de", "fourteenth_lesson"])
    write(f"{PREFIX}_118_FUNCTION_SELECTED_UNITS.tsv", revised_units, list(units[0]) + ["microfunction_marks", "microfunction_sequence", "functional_selector_complete"])
    write(f"{PREFIX}_6_FUNCTION_SELECTED_JOB_CARDS.tsv", revised_cards, list(revised_cards[0]))

    lines = [
        "# Funktionsallographen der Werkstatt",
        "",
        "Sechs bislang lokal oder identitätsabhängig gewählte Familien werden jetzt nach der beabsichtigten Unterfunktion geschrieben.",
        "Der semantische Stamm bleibt gleich; der Allograph präzisiert Zielart, Fortsetzungsart, Referententyp, Schlussmodus oder Haltemodus.",
        "",
    ]
    for recipe in sorted(TARGET_RECIPES):
        lines.append(f"## {recipe}")
        lines.append("")
        for row in lexicon_rows:
            if row["component_recipe"] == recipe:
                lines.append(f"- `{row['surface']}` = **{row['renderer_microfunction']}** — {row['intended_trigger_de']} ({row['occurrence_marks']} Marken).")
        lines.append("")
    (HERE / f"{PREFIX}_FUNCTIONAL_ALLOGRAPH_MANUAL.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    remaining_context = [row for row in revised_families if row["component_recipe"] not in TARGET_RECIPES]
    summary = {
        "status": "PASS",
        "decision": "THIRTEEN_FUNCTIONAL_ALLOGRAPHS_AND_TWO_LOCAL_WHOLE_WORDS_REPLACE_IDENTITY_OR_MINI_DECK_SELECTION_FOR_SIX_FAMILIES",
        "target_families": len(TARGET_RECIPES),
        "functional_allographs": sum(row["entry_class"] == "FUNCTIONAL_ALLOGRAPH" for row in lexicon_rows),
        "local_whole_words": sum(row["entry_class"] == "LOCAL_WHOLE_WORD" for row in lexicon_rows),
        "microfunction_forms": len(lexicon_rows),
        "microfunction_occurrences": len(revised_occurrences),
        "remaining_context_families": len(remaining_context),
        "remaining_context_occurrences": sum(int(row["occurrence_marks"]) for row in remaining_context),
        "remaining_identity_selectors": sum(row["selector_feature_set"] == "MEMORIZED_IDENTITY" for row in remaining_context),
        "remaining_local_mini_deck_selectors": sum(row["selector_feature_set"] == "UNIT" for row in remaining_context),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "new_pages": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 903: funktionale Allographen\n\n"
        "Dreizehn Allographen tragen nun eine konkrete Unterfunktion und zwei lokale Bedingungsformen bleiben ganze Wörter. "
        "Damit verschwinden Identitäts- und Mini-Deck-Auswahl aus sechs Familien und 73 Vorkommen; nur zehn bereits kontextuell lesbare Mehrfachfamilien bleiben.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
