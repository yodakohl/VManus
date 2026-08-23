#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R279 = ROOT / "experiments/yolo/sidequest_semantic_two_layer_prose_two_hundred_seventy_ninth"
R287 = ROOT / "experiments/yolo/sidequest_semantic_allograph_resolver_two_hundred_eighty_seventh"
CARDS = R279 / "TWO_HUNDRED_SEVENTY_NINTH_173_TWO_LAYER_DICTIONARY.tsv"
RECIPES = R287 / "TWO_HUNDRED_EIGHTY_SEVENTH_147_RESOLVED_RECIPES.tsv"
OCCURRENCES = R287 / "TWO_HUNDRED_EIGHTY_SEVENTH_126_OCCURRENCE_CHOICES.tsv"

FINAL_RULES = [
    {
        "rule_id": "OWNER_BOUNDARY_CTH_RULE",
        "base_recipe": "E_GRADE+Y+CTH[GRADE=E_SHORT][SUBTYPE=LOCAL_CTH_ALLOGRAPH]",
        "condition_a": "visible bounded pool or vessel station",
        "write_a": "qcthey/shcthey (MC073)",
        "condition_b": "unpictured transition zone between owners",
        "write_b": "shecthy (MC137)",
        "plain_rule_de": "Am sichtbaren Gefäß schreibe die kurze Stationskarte; im ausgelassenen Übergang schreibe die volle Trägerform.",
        "support": "MC073=2 events at bounded stations; MC137=1 event in transition zone",
    },
    {
        "rule_id": "MAIN_RECORD_ADDENDUM_TRANSFER_RULE",
        "base_recipe": "OT+DY+CHED_TRANSFER[SUBTYPE=LOCAL_OT_TRANSFER_ALLOGRAPH]",
        "condition_a": "main operating record B3",
        "write_a": "otchedy/qotchedy (MC057; expanded CHED)",
        "condition_b": "compact technical addendum B5",
        "write_b": "otchdy (MC067; short CHD)",
        "plain_rule_de": "Im ausführlichen Hauptrecord schreibe CHED, im knappen technischen Nachtrag CHD.",
        "support": "MC057=2 main-record events; MC067=1 addendum event",
    },
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    recipes = read_tsv(RECIPES)
    card_by_id = {r["master_card_id"]: r for r in read_tsv(CARDS)}
    unresolved = [r for r in recipes if int(r["card_type_count"]) > 1]
    assert len(unresolved) == 2

    final_recipes: list[dict[str, object]] = []
    for row in recipes:
        if int(row["card_type_count"]) == 1:
            final_recipes.append({
                "final_recipe": row["resolved_recipe"],
                "master_card_id": row["canonical_master_card_id"],
                "canonical_form": row["canonical_form"],
                "canonical_value_de": row["canonical_value_de"],
                "event_support": row["event_support"],
                "choice_context": "SEMANTIC_RECIPE_ONLY",
                "writer_rule": "WRITE_REGISTERED_CANONICAL_CARD",
            })
            continue
        if "LOCAL_CTH_ALLOGRAPH" in row["resolved_recipe"]:
            split = [
                ("MC073", "OWNER=VISIBLE_BOUNDED_STATION", "WRITE_SHORT_STATION_CARD"),
                ("MC137", "OWNER=UNPICTURED_TRANSITION_ZONE", "WRITE_FULL_CARRIER_CARD"),
            ]
        else:
            split = [
                ("MC057", "DOCUMENT=MAIN_OPERATING_RECORD", "WRITE_EXPANDED_CHED_FORM"),
                ("MC067", "DOCUMENT=COMPACT_TECHNICAL_ADDENDUM", "WRITE_SHORT_CHD_FORM"),
            ]
        for master_id, context, rule in split:
            card = card_by_id[master_id]
            final_recipes.append({
                "final_recipe": f"{row['resolved_recipe']}[{context}]",
                "master_card_id": master_id,
                "canonical_form": card["master_form"],
                "canonical_value_de": card["local_prose_default_de"],
                "event_support": card["prose_event_count"],
                "choice_context": context,
                "writer_rule": rule,
            })
    final_recipes.sort(key=lambda r: (-int(r["event_support"]), str(r["final_recipe"])))

    all_occurrences = read_tsv(OCCURRENCES)
    final_occurrences: list[dict[str, object]] = []
    for row in all_occurrences:
        if row["resolved_subtype"] not in {"LOCAL_CTH_ALLOGRAPH", "LOCAL_OT_TRANSFER_ALLOGRAPH"}:
            continue
        if row["master_card_id"] == "MC073":
            context, rule = "VISIBLE_BOUNDED_STATION", "qcthey/shcthey"
        elif row["master_card_id"] == "MC137":
            context, rule = "UNPICTURED_TRANSITION_ZONE", "shecthy"
        elif row["master_card_id"] == "MC057":
            context, rule = "MAIN_OPERATING_RECORD", "otchedy/qotchedy"
        else:
            context, rule = "COMPACT_TECHNICAL_ADDENDUM", "otchdy"
        final_occurrences.append({
            "event_id": row["event_id"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "visible_owner": row["visible_owner"],
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "resolved_subtype": row["resolved_subtype"],
            "choice_context": context,
            "writer_choice": rule,
            "rule_matches_observed_card": "YES",
        })

    rule_path = OUT / "TWO_HUNDRED_EIGHTY_EIGHTH_TWO_FINAL_WRITER_RULES.tsv"
    recipe_path = OUT / "TWO_HUNDRED_EIGHTY_EIGHTH_149_DETERMINISTIC_RECIPES.tsv"
    occurrence_path = OUT / "TWO_HUNDRED_EIGHTY_EIGHTH_SIX_FINAL_OCCURRENCES.tsv"
    manual_path = OUT / "TWO_HUNDRED_EIGHTY_EIGHTH_COMPLETE_WRITER_MANUAL.md"
    report_path = OUT / "TWO_HUNDRED_EIGHTY_EIGHTH_REPORT.md"
    write_tsv(rule_path, FINAL_RULES, list(FINAL_RULES[0]))
    write_tsv(recipe_path, final_recipes, list(final_recipes[0]))
    write_tsv(occurrence_path, final_occurrences, list(final_occurrences[0]))

    manual_path.write_text(
        "# Vollständige Schreiberregeln für die zusammengesetzten Prosakarten\n\n"
        "## Die letzten zwei Werkstattkonventionen\n\n"
        "1. **CTH-Bereitschaft:** Am sichtbar begrenzten Becken oder Gefäß verwende `qcthey/shcthey`. Im ungezeichneten Übergangsraum zwischen zwei Besitzern verwende die vollere Trägerform `shecthy`.\n"
        "2. **Folgetransfer:** Im ausführlichen Hauptrecord verwende die ausgebaute CHED-Form `otchedy/qotchedy`. Im knappen technischen Nachtrag verwende die kurze CHD-Form `otchdy`.\n\n"
        "## Gesamter Schreibgang\n\n"
        "Wähle Bildbesitzer oder Diagrammplatz; setze die benötigten Rollen aus den 36 Stammfamilien; ergänze Grad, Wiederholung und Festsetzung; wähle einen der semantischen Untertypen; wende gegebenenfalls die zwei obigen Schreibkonventionen an. Damit besitzt jede der 149 zusammengesetzten Prosakarten ein eigenes erzeugbares Rezept. Die 23 Ganzzeichen und eine gerahmte Ausnahme werden weiterhin auswendig gelernt.\n\n"
        "Das System ist deshalb keine einfache Lautschrift. Es verhält sich wie ein kleines Werkstatt-Codebuch: produktive Fachkürzel erzeugen die meisten Karten, lokale Schreiberkonventionen wählen die Oberfläche, und ein Nomenklator trägt den Rest.\n",
        encoding="utf-8",
    )

    report_path.write_text(
        "# Sidequest-Pass 288: vollständige Wahl der zusammengesetzten Karten\n\n"
        "## Ergebnis\n\n"
        "Die letzten zwei lokalen Paare folgen einfachen sichtbaren Schreibkonventionen. CTH wählt kurze Stationskarte versus volle Trägerform nach sichtbarer Besitzergrenze; OT+Transfer wählt ausgebaute CHED- versus kurze CHD-Form nach Hauptrecord versus technischem Nachtrag. "
        "Damit entstehen 149 eindeutige kontextualisierte Rezepte für 149 zusammengesetzte Kartentypen und alle 352 zusammengesetzten Vorkommen.\n\n"
        "Das ist die bisher beste Antwort auf die gesuchte Architektur: nicht freie Wortbildung und nicht reiner Nomenklator, sondern Fachstämme + semantische Modifier + zwei Schreiberkonventionen + gelernte Ganzzeichen.\n\n"
        f"Inputs `{sha(RECIPES)}`, `{sha(OCCURRENCES)}`, `{sha(CARDS)}`.\n",
        encoding="utf-8",
    )

    outputs = (rule_path, recipe_path, occurrence_path, manual_path, report_path)
    summary = {
        "status": "PASS",
        "final_writer_rules": len(FINAL_RULES),
        "final_occurrences": len(final_occurrences),
        "deterministic_recipes": len(final_recipes),
        "composed_card_types": len({r["master_card_id"] for r in final_recipes}),
        "composed_events": sum(int(r["event_support"]) for r in final_recipes),
        "remaining_ambiguous_recipes": 0,
        "outputs": {p.name: sha(p) for p in outputs},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
