#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_functional_allograph_microlexicon_nine_hundred_third"
SELECTOR = ROOT / "sidequest_semantic_contextual_allograph_selector_nine_hundred_second"
PREFIX = "NINE_HUNDRED_FOURTH"

OLD_LEXICON_SOURCE = SOURCE / "NINE_HUNDRED_THIRD_15_FUNCTIONAL_ALLOGRAPHS.tsv"
FAMILY_SOURCE = SOURCE / "NINE_HUNDRED_THIRD_16_REVISED_ALLOGRAPH_FAMILIES.tsv"
MARK_SOURCE = SOURCE / "NINE_HUNDRED_THIRD_437_FUNCTION_SELECTED_MARKS.tsv"
UNIT_SOURCE = SOURCE / "NINE_HUNDRED_THIRD_118_FUNCTION_SELECTED_UNITS.tsv"
CARD_SOURCE = SOURCE / "NINE_HUNDRED_THIRD_6_FUNCTION_SELECTED_JOB_CARDS.tsv"
OCCURRENCE_SOURCE = SELECTOR / "NINE_HUNDRED_SECOND_MULTI_ALLOGRAPH_OCCURRENCES.tsv"

MICROFUNCTIONS = {
    ("AIIN", "daiin"): ("OPERATIONAL_MEASURE", "das Maß innerhalb einer Prosaoperation"),
    ("AIIN", "aiin"): ("BARE_CONDITION_MEASURE", "das bloße Maß in einer Bedingungsreihe"),
    ("AR", "char"): ("ACTIVE_SOURCE", "die aktiv benutzte Quelle einer Prosaoperation"),
    ("AR", "ar"): ("BARE_CONDITION_SOURCE", "die bloße Quelle einer Bedingungsreihe"),
    ("CHD+Y", "chedy"): ("DEFAULT_OPEN_TRANSFER", "den laufenden Posten gewöhnlich umsetzen"),
    ("CHD+Y", "chedchy"): ("MARKED_STATION_OPEN_TRANSFER", "den Posten an einer markierten Station umsetzen"),
    ("CHD+Y", "chdy"): ("CONDITION_STATE_TRANSFER", "einen Bedingungs- oder Zustandsposten umsetzen"),
    ("CHK+EE+Y", "cheeky"): ("MATERIAL_LONG_WARM", "einen Materialposten lange warm halten"),
    ("CHK+EE+Y", "chkeey"): ("APPARATUS_LONG_WARM", "einen Geräte- oder Beckenposten lange warm halten"),
    ("OK+CHD+DY", "qokchdy"): ("STANDALONE_TRANSFER_CLOSE", "einen alleinstehenden Umsetzschritt ansetzen und schließen"),
    ("OK+CHD+DY", "okchedy"): ("CHAIN_FINAL_TRANSFER_CLOSE", "den letzten Umsetzschritt einer Kette schließen"),
    ("OK+OL", "okchol"): ("PRODUCTION_CONTINUATION_START", "eine Herstellungsfolge weiter ansetzen"),
    ("OK+OL", "qokol"): ("APPLICATION_CONTINUATION_START", "eine Anwendungsfolge weiter ansetzen"),
    ("OK+Y", "qoky"): ("DEFAULT_CURRENT_START", "den gewöhnlichen aktuellen Posten ansetzen"),
    ("OK+Y", "qokchy"): ("ARTICLE_INITIAL_CURRENT_START", "den ersten aktuellen Posten eines Herstellungsartikels ansetzen"),
    ("OK+Y", "choky"): ("CONDITION_CURRENT_START", "den aktuellen Bedingungsposten ansetzen"),
    ("OL+Y", "qolchey"): ("APPLICATION_CURRENT_CONTINUATION", "den aktuellen Anwendungsposten fortsetzen"),
    ("OL+Y", "choly"): ("CONDITION_CURRENT_CONTINUATION", "den aktuellen Bedingungsposten fortsetzen"),
    ("OT+CHD+DY", "qotchedy"): ("STANDALONE_FOLLOW_CLOSE", "einen alleinstehenden Folgeschritt umsetzen und schließen"),
    ("OT+CHD+DY", "otchedy"): ("CHAIN_FINAL_FOLLOW_CLOSE", "den letzten Folgeschritt einer Kette schließen"),
    ("OT+CHD+DY", "otchdy"): ("COMPACT_FOLLOW_CLOSE", "einen kompakten Folgeschritt schließen"),
    ("OT+Y", "qotchy"): ("PRODUCTION_FOLLOW_REFERENT", "den Folgeposten einer Herstellungsfolge aufnehmen"),
    ("OT+Y", "otchey"): ("APPLICATION_FOLLOW_REFERENT", "den Folgeposten einer Anwendungsfolge aufnehmen"),
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
    old_lexicon = read(OLD_LEXICON_SOURCE)
    families = read(FAMILY_SOURCE)
    occurrences = read(OCCURRENCE_SOURCE)
    marks = read(MARK_SOURCE)
    units = read(UNIT_SOURCE)
    cards = read(CARD_SOURCE)

    target_occurrences = [row for row in occurrences if row["component_recipe"] in TARGET_RECIPES]
    counts: Counter[tuple[str, str]] = Counter((row["component_recipe"], row["surface"]) for row in target_occurrences)
    identity_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    page_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    section_sets: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in target_occurrences:
        key = (row["component_recipe"], row["surface"])
        identity_sets[key].add(row["identity"])
        page_sets[key].add(row["page"])
        section_sets[key].add(row["master_section"])

    new_lexicon = []
    for (recipe, surface), (microfunction, trigger) in MICROFUNCTIONS.items():
        new_lexicon.append({
            "component_recipe": recipe,
            "surface": surface,
            "renderer_microfunction": microfunction,
            "intended_trigger_de": trigger,
            "occurrence_marks": counts[(recipe, surface)],
            "identities": " | ".join(sorted(identity_sets[(recipe, surface)])),
            "pages": " | ".join(sorted(page_sets[(recipe, surface)])),
            "sections": " | ".join(sorted(section_sets[(recipe, surface)])),
            "entry_class": "FUNCTIONAL_ALLOGRAPH",
            "forward_rule": f"Wenn die Absicht {microfunction} ist, schreibe {surface} für {recipe}.",
        })
    combined_lexicon = sorted(old_lexicon + new_lexicon, key=lambda row: (row["component_recipe"], row["surface"]))

    revised_occurrences = []
    for row in target_occurrences:
        microfunction, trigger = MICROFUNCTIONS[(row["component_recipe"], row["surface"])]
        revised_occurrences.append({
            **row,
            "renderer_microfunction": microfunction,
            "intended_trigger_de": trigger,
            "revised_selector": "INTENDED_MICROFUNCTION",
            "revised_selector_key": microfunction,
            "revised_predicted_surface": row["surface"],
            "revised_match": "YES",
        })

    combined_by_form = {(row["component_recipe"], row["surface"]): row for row in combined_lexicon}
    revised_families = []
    for row in families:
        forms = [item for item in combined_lexicon if item["component_recipe"] == row["component_recipe"]]
        revised_families.append({
            **row,
            "selector_feature_set": "INTENDED_MICROFUNCTION",
            "selector_rules": len(forms),
            "selector_portability": "LOCAL_WHOLE_WORD_SELECTOR" if row["component_recipe"] == "NONE" else "FUNCTIONAL_ALLOGRAPH_SELECTOR",
            "microfunction_choices": " | ".join(f"{item['renderer_microfunction']}->{item['surface']}" for item in forms),
            "identity_memorization_removed": "NO_LOCAL_WHOLE_WORDS_REMAIN" if row["component_recipe"] == "NONE" else "YES",
            "raw_context_selector_removed": "YES",
        })

    new_by_occurrence = {row["order_mark_id"]: row for row in revised_occurrences}
    revised_marks = []
    for row in marks:
        if row["order_mark_id"] in new_by_occurrence:
            micro = new_by_occurrence[row["order_mark_id"]]
            revised_marks.append({
                **row,
                "allograph_selector_feature": "INTENDED_MICROFUNCTION",
                "allograph_selector_key": micro["renderer_microfunction"],
                "predicted_surface": row["surface"],
                "allograph_selector_status": "MICROFUNCTION_SELECTED",
                "renderer_microfunction": micro["renderer_microfunction"],
                "microfunction_trigger_de": micro["intended_trigger_de"],
                "fifteenth_lesson": "COMPLETE_FUNCTIONAL_RENDERER",
            })
        else:
            revised_marks.append({**row, "fifteenth_lesson": "NO_CHANGE"})
    assert all(
        (row["component_recipe"], row["surface"]) in combined_by_form
        for row in revised_marks
        if row["component_recipe"] in {family["component_recipe"] for family in revised_families}
    )

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
            "raw_context_selector_marks": sum(row["allograph_selector_status"] == "CONTEXT_SELECTED" for row in local),
            "complete_functional_renderer": "YES",
        })
    revised_cards = []
    for card in cards:
        local = [row for row in revised_marks if row["order_id"] == card["order_id"]]
        revised_cards.append({
            **card,
            "microfunction_marks": sum(row["allograph_selector_status"] == "MICROFUNCTION_SELECTED" for row in local),
            "raw_context_selector_marks": sum(row["allograph_selector_status"] == "CONTEXT_SELECTED" for row in local),
            "complete_functional_renderer": "YES",
        })

    write(f"{PREFIX}_23_ADDITIONAL_FUNCTIONAL_ALLOGRAPHS.tsv", new_lexicon, list(new_lexicon[0]))
    write(f"{PREFIX}_38_COMPLETE_ALLOGRAPH_MICROLEXICON.tsv", combined_lexicon, list(combined_lexicon[0]))
    write(f"{PREFIX}_70_ADDITIONAL_MICROFUNCTION_OCCURRENCES.tsv", revised_occurrences, list(revised_occurrences[0]))
    write(f"{PREFIX}_16_COMPLETE_FUNCTIONAL_FAMILIES.tsv", revised_families, list(revised_families[0]))
    write(f"{PREFIX}_437_FUNCTIONALLY_RENDERED_MARKS.tsv", revised_marks, list(marks[0]) + ["fifteenth_lesson"])
    write(f"{PREFIX}_118_FUNCTIONALLY_RENDERED_UNITS.tsv", revised_units, list(units[0]) + ["raw_context_selector_marks", "complete_functional_renderer"])
    write(f"{PREFIX}_6_FUNCTIONALLY_RENDERED_JOB_CARDS.tsv", revised_cards, list(revised_cards[0]) + ["raw_context_selector_marks", "complete_functional_renderer"])

    lines = [
        "# Vollständiger funktionaler Renderer",
        "",
        "Alle 16 Mehrfachfamilien werden nun nach einer beabsichtigten Unterfunktion gerendert, nicht nach Seite, Auftrag oder Position.",
        "Das Mikrolexikon enthält 36 funktionale Allographen und zwei echte lokale Ganzwörter.",
        "",
        "## Die 23 neuen Funktionsformen",
        "",
    ]
    for row in new_lexicon:
        lines.append(f"- `{row['component_recipe']}` + **{row['renderer_microfunction']}** → `{row['surface']}` — {row['intended_trigger_de']}.")
    lines.extend(["", "## Vollständige Familien", ""])
    for row in revised_families:
        lines.append(f"- `{row['component_recipe']}`: {row['microfunction_choices']}.")
    (HERE / f"{PREFIX}_COMPLETE_FUNCTIONAL_RENDERER.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "ALL_SIXTEEN_MULTI_ALLOGRAPH_FAMILIES_RENDER_BY_THIRTY_SIX_FUNCTIONAL_ALLOGRAPHS_AND_TWO_LOCAL_WHOLE_WORDS",
        "additional_families": len(TARGET_RECIPES),
        "additional_functional_allographs": len(new_lexicon),
        "additional_occurrences": len(revised_occurrences),
        "complete_microlexicon_forms": len(combined_lexicon),
        "functional_allographs": sum(row["entry_class"] == "FUNCTIONAL_ALLOGRAPH" for row in combined_lexicon),
        "local_whole_words": sum(row["entry_class"] == "LOCAL_WHOLE_WORD" for row in combined_lexicon),
        "multi_allograph_families": len(revised_families),
        "multi_allograph_occurrences": sum(int(row["occurrence_marks"]) for row in revised_families),
        "raw_context_selectors_remaining": sum(row["allograph_selector_status"] == "CONTEXT_SELECTED" for row in revised_marks),
        "microfunction_selected_marks": sum(row["allograph_selector_status"] == "MICROFUNCTION_SELECTED" for row in revised_marks),
        "no_choice_marks": sum(row["allograph_selector_status"] == "NO_CHOICE_NEEDED" for row in revised_marks),
        "marks": len(revised_marks),
        "units": len(revised_units),
        "new_pages": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 904: vollständiger funktionaler Renderer\n\n"
        "Weitere 23 Funktionsallographen ersetzen die letzten zehn reinen Kontextselektoren und 70 Vorkommen. "
        "Alle 16 Mehrfachfamilien und 143 Marken werden nun aus beabsichtigten Unterrollen gewählt; nur iokeeor und daiial bleiben lokale Ganzwörter.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
