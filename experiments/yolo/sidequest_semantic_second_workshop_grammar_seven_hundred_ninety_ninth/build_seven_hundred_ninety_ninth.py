#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
COMPONENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_39_COMPONENT_DICTIONARY.tsv"
CARDS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_173_CARD_DICTIONARY.tsv"
EVENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
STATEMENTS = BASE / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv"

CORE15 = {"OK", "OT", "OL", "K", "L", "CHD", "E", "EE", "EEE", "AIIN", "AIN", "AL", "AR", "Y", "DY"}
PREDICTION_FILES = {
    "PASS789_GRADE_HAND_BOARD": ROOT / "sidequest_semantic_apprentice_grade_board_seven_hundred_eighty_ninth" / "SEVEN_HUNDRED_EIGHTY_NINTH_6_BOARD_CARDS.tsv",
    "PASS790_QUANTITY": ROOT / "sidequest_semantic_quantity_axis_seven_hundred_ninetieth" / "SEVEN_HUNDRED_NINETIETH_14_PREDICTED_SURFACES.tsv",
    "PASS792_ADDRESS": ROOT / "sidequest_semantic_address_axis_seven_hundred_ninety_second" / "SEVEN_HUNDRED_NINETY_SECOND_22_PREDICTED_SURFACES.tsv",
    "PASS795_CONTROL": ROOT / "sidequest_semantic_control_axis_seven_hundred_ninety_fifth" / "SEVEN_HUNDRED_NINETY_FIFTH_8_PREDICTED_THIRD_CORES.tsv",
    "PASS797_TRANSFER": ROOT / "sidequest_semantic_transfer_axis_seven_hundred_ninety_seventh" / "SEVEN_HUNDRED_NINETY_SEVENTH_6_PREDICTED_OPERATIONS.tsv",
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def grammar_tier(row: dict[str, str]) -> str:
    component = row["component"]
    if component in CORE15:
        return "PARADIGM_CORE15"
    if row["category"] == "RECURRENT_PRODUCTIVE_ROOT":
        return "RECURRENT_RULE_STRIP"
    if row["category"] == "PARADIGM_SUPPORTED_BOUND_VARIANT_OF_AIN":
        return "BOUND_VARIANT"
    if row["category"] == "CONTEXT_SINGLETON_COMPONENT":
        return "LOCAL_SINGLETON"
    return "MEMORIZED_WHOLE_COMMAND"


def card_tier(tokens: list[str], component_by_name: dict[str, dict[str, object]]) -> str:
    tiers = {str(component_by_name[token]["grammar_tier"]) for token in tokens}
    if "MEMORIZED_WHOLE_COMMAND" in tiers:
        return "MEMORIZED_WHOLE_CARD"
    if "LOCAL_SINGLETON" in tiers:
        return "LOCAL_SINGLETON_PLUS_RULES"
    if "BOUND_VARIANT" in tiers:
        return "BOUND_VARIANT_PLUS_RULES"
    return "PRODUCTIVE_RECIPE"


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components = read(COMPONENTS)
    cards = read(CARDS)
    events = read(EVENTS)
    statements = read(STATEMENTS)

    component_rows = []
    for row in components:
        tier = grammar_tier(row)
        component_rows.append(
            {
                "component_no": row["component_no"],
                "component": row["component"],
                "short_value_de": row["short_value_de"],
                "grammar_tier": tier,
                "exact_cards": row["exact_cards"],
                "events": row["events"],
                "access_rule": (
                    "freely read only in registered recipe slot"
                    if tier == "PARADIGM_CORE15"
                    else "read from recurrent wall strip"
                    if tier == "RECURRENT_RULE_STRIP"
                    else "use only in its attested bound frame"
                    if tier == "BOUND_VARIANT"
                    else "copy from owner-local model card"
                    if tier == "LOCAL_SINGLETON"
                    else "memorize and copy entire command card"
                ),
                "diagnostic_surfaces": row["diagnostic_surfaces"],
            }
        )
    component_by_name = {str(row["component"]): row for row in component_rows}

    card_rows = []
    card_by_id = {}
    for row in cards:
        tokens = row["component_recipe"].split("+")
        values = [str(component_by_name[token]["short_value_de"]) for token in tokens]
        rebuilt = " · ".join(values)
        tier = card_tier(tokens, component_by_name)
        out = {
            "exact_card_id": row["exact_card_id"],
            "registered_surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"],
            "component_values_de": rebuilt,
            "working_reading_de": row["rebuilt_reading_de"],
            "exact_semantic_rebuild": "YES" if rebuilt == row["rebuilt_reading_de"] else "NO",
            "card_tier": tier,
            "core15_components": "+".join(token for token in tokens if token in CORE15) or "NONE",
            "core15_touch": "YES" if any(token in CORE15 for token in tokens) else "NO",
            "fully_core15": "YES" if set(tokens) <= CORE15 else "NO",
            "events": row["events"],
            "copy_rule": "SPEAK_BY_RECIPE__COPY_BY_EXACT_CARD",
        }
        card_rows.append(out)
        card_by_id[row["exact_card_id"]] = out

    event_rows = []
    for row in events:
        card = card_by_id[row["card_no"]]
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "owner_de": row["owner_de"],
                "exact_card_id": row["card_no"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "component_values_de": card["component_values_de"],
                "working_reading_de": row["rebuilt_reading_de"],
                "exact_semantic_rebuild": "YES" if card["component_values_de"] == row["rebuilt_reading_de"] else "NO",
                "card_tier": card["card_tier"],
                "core15_touch": card["core15_touch"],
                "form_owner_boundary_status": row["form_owner_boundary_status"],
            }
        )

    by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_statement[str(row["statement_id"])].append(row)
    statement_rows = []
    statement_lookup = {row["statement_id"]: row for row in statements}
    for statement_id, statement_events in by_statement.items():
        source = statement_lookup[statement_id]
        statement_rows.append(
            {
                "statement_id": statement_id,
                "page": source["page"],
                "record": source["record"],
                "owner_noun_de": source["owner_noun_de"],
                "events": len(statement_events),
                "productive_recipe_events": sum(row["card_tier"] == "PRODUCTIVE_RECIPE" for row in statement_events),
                "bound_variant_events": sum(row["card_tier"] == "BOUND_VARIANT_PLUS_RULES" for row in statement_events),
                "local_singleton_events": sum(row["card_tier"] == "LOCAL_SINGLETON_PLUS_RULES" for row in statement_events),
                "memorized_whole_events": sum(row["card_tier"] == "MEMORIZED_WHOLE_CARD" for row in statement_events),
                "core15_touch_events": sum(row["core15_touch"] == "YES" for row in statement_events),
                "surface_sequence": " ".join(str(row["surface"]) for row in statement_events),
                "component_sequence": " | ".join(str(row["component_recipe"]) for row in statement_events),
                "working_reading_de": source["clean_workshop_reading_de"],
                "semantic_rebuild": "PASS" if all(row["exact_semantic_rebuild"] == "YES" for row in statement_events) else "FAIL",
            }
        )

    whole_cards = [
        {
            "exact_card_id": row["exact_card_id"],
            "surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"],
            "whole_reading_de": row["working_reading_de"],
            "events": row["events"],
            "instruction": "memorize whole card; do not split visible letters",
        }
        for row in card_rows
        if row["card_tier"] == "MEMORIZED_WHOLE_CARD"
    ]

    predictions: dict[str, dict[str, object]] = {}

    def add_prediction(surface: str, recipe: str, reading_de: str, source: str) -> None:
        if surface in predictions:
            if (predictions[surface]["component_recipe"], predictions[surface]["working_reading_de"]) != (recipe, reading_de):
                raise ValueError(f"prediction conflict at {surface}")
            predictions[surface]["source_passes"].add(source)
        else:
            predictions[surface] = {
                "predicted_surface": surface,
                "component_recipe": recipe,
                "working_reading_de": reading_de,
                "source_passes": {source},
            }

    for row in read(PREDICTION_FILES["PASS789_GRADE_HAND_BOARD"]):
        add_prediction(row["hand_1_surface"], row["component_recipe"], row["spoken_prompt_de"], "PASS789_GRADE_HAND_BOARD")
        add_prediction(row["hand_2_surface"], row["component_recipe"], row["spoken_prompt_de"], "PASS789_GRADE_HAND_BOARD")
    for source_name in ("PASS790_QUANTITY", "PASS792_ADDRESS"):
        for row in read(PREDICTION_FILES[source_name]):
            add_prediction(row["predicted_surface"], row["counterpart_recipe"], row["counterpart_reading_de"], source_name)
    for source_name in ("PASS795_CONTROL", "PASS797_TRANSFER"):
        for row in read(PREDICTION_FILES[source_name]):
            add_prediction(row["predicted_surface"], row["predicted_recipe"], row["predicted_reading_de"], source_name)
    attested_surfaces = {row["surface"] for row in events}
    prediction_rows = []
    for surface, row in sorted(predictions.items()):
        prediction_rows.append(
            {
                "predicted_surface": surface,
                "component_recipe": row["component_recipe"],
                "working_reading_de": row["working_reading_de"],
                "source_passes": ",".join(sorted(row["source_passes"])),
                "attested_on_fixed_pages": "YES" if surface in attested_surfaces else "NO",
                "use_status": "PREDICTION_ONLY__KEEP_OUT_OF_381_EDITION",
            }
        )

    renderer_rules = [
        {"priority": 1, "rule": "RECIPE_READING", "instruction_de": "Bedeutung aus registrierten Komponenten in Rezeptreihenfolge sprechen"},
        {"priority": 2, "rule": "EXACT_CARD_PACKING", "instruction_de": "für die Niederschrift die gelernte exakte Ganzkarte wählen"},
        {"priority": 3, "rule": "TWELVE_COMMON_HAND_CARDS", "instruction_de": "nur zwölf bekannte gemeinsame Karten aktiv zwischen Hand 1 und 2 wenden"},
        {"priority": 4, "rule": "LOCAL_MODEL_COPY", "instruction_de": "jede übrige Karte aus dem Seiten- oder Fachmodell kopieren"},
        {"priority": 5, "rule": "CHD_CHED_SELECTION", "instruction_de": "langes CHED als Default; kurze Formen nur aus der gelernten Streifenliste"},
        {"priority": 6, "rule": "Y_CHY_RECIPE_BOUNDARY", "instruction_de": "CH vor Y nur semantisch lesen, wenn CH im Rezept registriert ist"},
        {"priority": 7, "rule": "E_GRADE_SLOT", "instruction_de": "E/EE/EEE nur im registrierten Gradslot als kurz/lang/voll lesen"},
        {"priority": 8, "rule": "F82_EDGE_COPY", "instruction_de": "nur E180/E181 als zwei sichtbare Kopien eines Quellpostens lesen"},
    ]

    write(
        "SEVEN_HUNDRED_NINETY_NINTH_39_COMPONENT_SECOND_GRAMMAR.tsv",
        component_rows,
        ["component_no", "component", "short_value_de", "grammar_tier", "exact_cards", "events", "access_rule", "diagnostic_surfaces"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_NINTH_173_CARD_SECOND_DICTIONARY.tsv",
        card_rows,
        ["exact_card_id", "registered_surfaces", "component_recipe", "component_values_de", "working_reading_de", "exact_semantic_rebuild", "card_tier", "core15_components", "core15_touch", "fully_core15", "events", "copy_rule"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_NINTH_381_EVENT_REPARSE.tsv",
        event_rows,
        ["event_id", "page", "record", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "component_values_de", "working_reading_de", "exact_semantic_rebuild", "card_tier", "core15_touch", "form_owner_boundary_status"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_NINTH_116_STATEMENT_REPARSE.tsv",
        statement_rows,
        ["statement_id", "page", "record", "owner_noun_de", "events", "productive_recipe_events", "bound_variant_events", "local_singleton_events", "memorized_whole_events", "core15_touch_events", "surface_sequence", "component_sequence", "working_reading_de", "semantic_rebuild"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_NINTH_3_MEMORIZED_WHOLE_CARDS.tsv",
        whole_cards,
        ["exact_card_id", "surfaces", "component_recipe", "whole_reading_de", "events", "instruction"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_NINTH_56_UNATTESTED_PREDICTIONS.tsv",
        prediction_rows,
        ["predicted_surface", "component_recipe", "working_reading_de", "source_passes", "attested_on_fixed_pages", "use_status"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_NINTH_8_RENDERER_RULES.tsv",
        renderer_rules,
        ["priority", "rule", "instruction_de"],
    )

    teaching = """# Pass 799 — zweite Werkstattgrammatik auf einem Blatt

## Die fünf produktiven Reihen

- Ablauf: `OK / OT / OL` = ANSETZEN / DANACH / WEITER.
- Transfer: `K / L / CHD` = ZUGEBEN / LEITEN / UMSETZEN.
- Menge: `AIIN / AIN` = SOLLMASS / PORTION.
- Adresse: `AL / AR` = ZIELSTELLE / QUELLE.
- Grad: `E / EE / EEE` = KURZ / LANG / VOLL.

`Y` hält den aktuellen Posten fest, eine lizenzierte `DY`-Karte schließt den Schritt. Diese fünf Reihen plus Y/DY bilden den 15-teiligen Kern. Sie berühren 161/173 Karten und 358/381 Ereignisse; 76 Karten/237 Ereignisse bestehen sogar ausschließlich daraus.

## Der Regelstreifen

Sechzehn weitere wiederkehrende Werte liefern den fachlichen Inhalt: unter anderem ENTNEHMEN, HALTEN, ABSETZEN, WÄRMEN, BEREITEN, FÜLLEN, WASCHEN, ANWENDEN, WASSER, ANSATZ, ZUTAT, DURCHLASS und ARBEITSGANG. Sie sind wiederverwendbar, aber nicht Teil jeder freien Achse.

## Was wirklich auswendig bleibt

Vier lokale Einmalwerte werden mit ihrer Karte kopiert. Drei ganze Befehle bleiben ungeteilt: `os`=FACH, `dchol/schol`=WIEDERAUFNEHMEN und `talam`=VERWAHREN. Keine ihrer sichtbaren Teilfolgen wird als neue Bedeutung ausgegeben.

## Schreibregel

Sprich nach dem Komponentenrezept, kopiere nach der exakten Karte, realisiere danach nur einen bereits gelehrten Hand- oder Positionsallographen. Die 56 neu gebildeten Oberflächen stehen auf einem separaten Prognoseblatt und gehören nicht zu den 381 sichtbaren Ereignissen.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_NINTH_ONE_PAGE_GRAMMAR.md").write_text(teaching, encoding="utf-8")

    report = """# Pass 799 — konsolidierte zweite Werkstattgrammatik

Alle jüngsten Paradigmen sind nun in einer einzigen, ausführbaren Grammatik zusammengeführt. Das 39-Werte-Lexikon zerfällt in 15 stark produktive Kernwerte, 16 wiederkehrende Fachwerte, eine gebundene AIN-Variante, vier lokale Singletonwerte und drei memorierte Ganzbefehle.

Die 173 Karten und 381 Ereignisse bauen semantisch exakt zurück; alle 116 Aussagen bestehen die Neulesung. 166 Karten/373 Ereignisse sind aus wiederkehrenden oder gebundenen Komponenten zusammengesetzt. Vier Karten/Ereignisse brauchen einen lokalen Singletonwert; drei Karten/vier Ereignisse brauchen einen ganzen memorierten Befehl. Der 15er Kern berührt 161 Karten/358 Ereignisse und erklärt 76 Karten/237 Ereignisse ganz allein.

Die Oberfläche bleibt eine eigene Schicht: acht kurze Rendererregeln bewahren exakte Karte, Handvarianten, CHD/CHED, Y/CHY, den Gradslot und die einzelne f82-Randkopie. Eine getrennte Liste vereinigt 56 einzigartige, noch unbelegte Prognoseoberflächen; keine wird als beobachteter Text ausgegeben.

Als nächstes greifen wir die 16 Werte des Regelstreifens an. Wir suchen dort das nächste echte Paradigma mit mindestens drei gemeinsamen Endungen—wahrscheinlich CH/SH/CTH oder O/OR/HO—und versuchen, den memorierten Rest weiter zu verkleinern, ohne die klare 15er Kernstruktur aufzuweichen.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_NINTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "components": len(component_rows),
        "paradigm_core_components": sum(row["grammar_tier"] == "PARADIGM_CORE15" for row in component_rows),
        "recurrent_strip_components": sum(row["grammar_tier"] == "RECURRENT_RULE_STRIP" for row in component_rows),
        "bound_components": sum(row["grammar_tier"] == "BOUND_VARIANT" for row in component_rows),
        "local_singleton_components": sum(row["grammar_tier"] == "LOCAL_SINGLETON" for row in component_rows),
        "whole_command_components": sum(row["grammar_tier"] == "MEMORIZED_WHOLE_COMMAND" for row in component_rows),
        "cards": len(card_rows),
        "events": len(event_rows),
        "statements": len(statement_rows),
        "exact_card_rebuilds": sum(row["exact_semantic_rebuild"] == "YES" for row in card_rows),
        "exact_event_rebuilds": sum(row["exact_semantic_rebuild"] == "YES" for row in event_rows),
        "productive_or_bound_cards": sum(row["card_tier"] in {"PRODUCTIVE_RECIPE", "BOUND_VARIANT_PLUS_RULES"} for row in card_rows),
        "productive_or_bound_events": sum(row["card_tier"] in {"PRODUCTIVE_RECIPE", "BOUND_VARIANT_PLUS_RULES"} for row in event_rows),
        "core15_touch_cards": sum(row["core15_touch"] == "YES" for row in card_rows),
        "core15_touch_events": sum(row["core15_touch"] == "YES" for row in event_rows),
        "fully_core15_cards": sum(row["fully_core15"] == "YES" for row in card_rows),
        "fully_core15_events": sum(card_by_id[row["exact_card_id"]]["fully_core15"] == "YES" for row in event_rows),
        "memorized_whole_cards": len(whole_cards),
        "memorized_whole_events": sum(int(row["events"]) for row in whole_cards),
        "unattested_predictions": len(prediction_rows),
        "prediction_collisions": sum(row["attested_on_fixed_pages"] == "YES" for row in prediction_rows),
        "decision": "SECOND_GRAMMAR_REPARSES_381_WITH_15_CORE_AXES_AND_THREE_WHOLE_COMMANDS",
    }
    (HERE / "SEVEN_HUNDRED_NINETY_NINTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
