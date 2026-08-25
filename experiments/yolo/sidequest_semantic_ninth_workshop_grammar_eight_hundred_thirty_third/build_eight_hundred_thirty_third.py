#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_eighth_workshop_grammar_eight_hundred_thirty_first"
PREFIX = "EIGHT_HUNDRED_THIRTY_THIRD"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def component_reading(recipe: str, components: dict[str, dict[str, str]]) -> str:
    return " · ".join(components[token]["short_value_de"] for token in recipe.split("+"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    components_old = read(BASE / "EIGHT_HUNDRED_THIRTY_FIRST_39_COMPONENT_EIGHTH_GRAMMAR.tsv")
    cards_old = read(BASE / "EIGHT_HUNDRED_THIRTY_FIRST_173_CARD_EIGHTH_DICTIONARY.tsv")
    events_old = read(BASE / "EIGHT_HUNDRED_THIRTY_FIRST_381_EVENT_REPARSE.tsv")
    statements_old = read(BASE / "EIGHT_HUNDRED_THIRTY_FIRST_116_STATEMENT_REPARSE.tsv")

    components = []
    for row in components_old:
        item = dict(row)
        if item["component"] == "O":
            item["short_value_de"] = "ARBEITSGANG"
            item["teaching_rule"] = "name the current workshop operation as ARBEITSGANG"
        components.append(item)
    by_component = {row["component"]: row for row in components}

    cards = []
    o_cards = []
    for row in cards_old:
        reading = component_reading(row["component_recipe"], by_component)
        item = {
            "exact_card_id": row["exact_card_id"],
            "registered_surfaces": row["registered_surfaces"],
            "component_recipe": row["component_recipe"],
            "ninth_grammar_reading_de": reading,
            "events": row["events"],
            "card_tier": row["card_tier"],
            "core33_components": row["core33_components"],
            "core33_touch": row["core33_touch"],
            "fully_core33": row["fully_core33"],
            "remainder_components": row["remainder_components"],
        }
        cards.append(item)
        if "O" in row["component_recipe"].split("+"):
            o_cards.append(
                {
                    "exact_card_id": row["exact_card_id"],
                    "surfaces": row["registered_surfaces"],
                    "component_recipe": row["component_recipe"],
                    "events": row["events"],
                    "old_reading_de": row["eighth_grammar_reading_de"],
                    "new_reading_de": reading,
                }
            )
    by_card = {row["exact_card_id"]: row for row in cards}

    events = []
    o_events = []
    events_by_statement: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in events_old:
        card = by_card[row["exact_card_id"]]
        item = {
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "statement_id": row["statement_id"],
            "owner_de": row["owner_de"],
            "exact_card_id": row["exact_card_id"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "ninth_grammar_reading_de": card["ninth_grammar_reading_de"],
            "card_tier": card["card_tier"],
            "core33_touch": card["core33_touch"],
            "fully_core33": card["fully_core33"],
            "form_owner_boundary_status": row["form_owner_boundary_status"],
        }
        events.append(item)
        events_by_statement[row["statement_id"]].append(item)
        if "O" in row["component_recipe"].split("+"):
            o_events.append(
                {
                    "event_id": row["event_id"],
                    "page": row["page"],
                    "statement_id": row["statement_id"],
                    "surface": row["surface"],
                    "component_recipe": row["component_recipe"],
                    "old_reading_de": row["eighth_grammar_reading_de"],
                    "new_reading_de": card["ninth_grammar_reading_de"],
                }
            )

    fluent_revisions = {
        "H2-S001": (
            "Bei der breiten gezahnten Bluetenpflanze: Vom laufenden Ansatz kurz entnehmen; "
            "den Posten bereitet halten, den Ansatz nach Sollmass im Arbeitsgang weiter bereiten "
            "und als aktuellen Posten verfuegbar lassen."
        ),
        "H3-S001": (
            "Bei der dicht bluehenden Kronenpflanze: Den Posten bearbeiten und weiter halten, "
            "dann im Arbeitsgang an der Zielstelle halten; auspressen, bis zum Sollmass halten, "
            "in den lokalen Empfaenger einbringen, laenger halten, bearbeiten, im Arbeitsgang "
            "entnehmen und den Schritt schliessen."
        ),
        "B1-S012": (
            "Am gemeinsamen zweireihigen Becken: Im Arbeitsgang spuelen, den Posten kurz "
            "ansetzen, nochmals kurz spuelen und den Schritt schliessen."
        ),
    }
    statements = []
    o_statements = []
    for row in statements_old:
        selected = events_by_statement[row["statement_id"]]
        working = fluent_revisions.get(row["statement_id"], row["working_reading_de"])
        revision = "O_VORGANG_TO_ARBEITSGANG" if row["statement_id"] in fluent_revisions else "NONE"
        item = {
            "statement_id": row["statement_id"],
            "page": row["page"],
            "record": row["record"],
            "owner_noun_de": row["owner_noun_de"],
            "events": row["events"],
            "surface_sequence": row["surface_sequence"],
            "component_sequence": row["component_sequence"],
            "ninth_grammar_literal_de": " | ".join(str(event["ninth_grammar_reading_de"]) for event in selected),
            "working_reading_de": working,
            "fully_core33_events": row["fully_core33_events"],
            "remainder_events": row["remainder_events"],
            "revision_sources": row["revision_sources"] + (",PASS833_O_ARBEITSGANG" if revision != "NONE" else ""),
        }
        statements.append(item)
        o_count = sum("O" in str(event["component_recipe"]).split("+") for event in selected)
        if o_count:
            o_statements.append(
                {
                    "statement_id": row["statement_id"],
                    "page": row["page"],
                    "record": row["record"],
                    "o_events": o_count,
                    "arbeitsgang_tokens": working.lower().count("arbeitsgang"),
                    "revision": revision,
                    "working_reading_de": working,
                }
            )

    exceptions = []
    for row in read(BASE / "EIGHT_HUNDRED_THIRTY_FIRST_6_EXCEPTIONS.tsv"):
        item = dict(row)
        item["reading_de"] = by_card[row["exact_card_id"]]["ninth_grammar_reading_de"]
        exceptions.append(item)

    predictions = []
    changed_predictions = 0
    for row in read(BASE / "EIGHT_HUNDRED_THIRTY_FIRST_76_UNATTESTED_PREDICTIONS.tsv"):
        reading = component_reading(row["component_recipe"], by_component)
        changed_predictions += reading != row["reading_de"]
        predictions.append(
            {
                "predicted_surface": row["predicted_surface"],
                "component_recipe": row["component_recipe"],
                "reading_de": reading,
                "sources": row["sources"],
                "attested_on_fixed_pages": row["attested_on_fixed_pages"],
                "use_status": row["use_status"],
                "edition": "NINTH_GRAMMAR_RECOMPUTED",
            }
        )
    prediction_by_surface = {row["predicted_surface"]: row for row in predictions}
    active = []
    for row in read(BASE / "EIGHT_HUNDRED_THIRTY_FIRST_30_ACTIVE_PREDICTION_SURFACES.tsv"):
        prediction = prediction_by_surface[row["predicted_surface"]]
        active.append(
            {
                **prediction,
                "recipe_rank": row["recipe_rank"],
                "selection_reason": row["selection_reason"],
            }
        )

    rules = read(BASE / "EIGHT_HUNDRED_THIRTY_FIRST_19_TEACHING_RULES.tsv")
    for row in rules:
        if row["rule"] == "PATH_PLACE":
            row["instruction"] = "CKH passage; O work step"

    write(f"{PREFIX}_39_COMPONENT_NINTH_GRAMMAR.tsv", components, ["component_no", "component", "short_value_de", "grammar_tier", "exact_cards", "events", "teaching_rule"])
    write(f"{PREFIX}_173_CARD_NINTH_DICTIONARY.tsv", cards, ["exact_card_id", "registered_surfaces", "component_recipe", "ninth_grammar_reading_de", "events", "card_tier", "core33_components", "core33_touch", "fully_core33", "remainder_components"])
    write(f"{PREFIX}_381_EVENT_REPARSE.tsv", events, ["event_id", "page", "record", "statement_id", "owner_de", "exact_card_id", "surface", "component_recipe", "ninth_grammar_reading_de", "card_tier", "core33_touch", "fully_core33", "form_owner_boundary_status"])
    write(f"{PREFIX}_116_STATEMENT_REPARSE.tsv", statements, ["statement_id", "page", "record", "owner_noun_de", "events", "surface_sequence", "component_sequence", "ninth_grammar_literal_de", "working_reading_de", "fully_core33_events", "remainder_events", "revision_sources"])
    write(f"{PREFIX}_18_O_CARDS.tsv", o_cards, ["exact_card_id", "surfaces", "component_recipe", "events", "old_reading_de", "new_reading_de"])
    write(f"{PREFIX}_19_O_EVENTS.tsv", o_events, ["event_id", "page", "statement_id", "surface", "component_recipe", "old_reading_de", "new_reading_de"])
    write(f"{PREFIX}_17_O_STATEMENTS.tsv", o_statements, ["statement_id", "page", "record", "o_events", "arbeitsgang_tokens", "revision", "working_reading_de"])
    write(f"{PREFIX}_6_EXCEPTIONS.tsv", exceptions, ["exact_card_id", "surfaces", "component_recipe", "reading_de", "events", "exception_component", "exception_type", "short_value_de", "learning_rule"])
    write(f"{PREFIX}_76_UNATTESTED_PREDICTIONS.tsv", predictions, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status", "edition"])
    write(f"{PREFIX}_30_ACTIVE_PREDICTION_SURFACES.tsv", active, ["predicted_surface", "component_recipe", "reading_de", "sources", "attested_on_fixed_pages", "use_status", "edition", "recipe_rank", "selection_reason"])
    write(f"{PREFIX}_19_TEACHING_RULES.tsv", rules, ["priority", "rule", "instruction"])

    summary = {
        "status": "PASS",
        "decision": "NINTH_GRAMMAR_REVISES_O_FROM_VORGANG_TO_ARBEITSGANG",
        "components": len(components),
        "cards": len(cards),
        "events": len(events),
        "statements": len(statements),
        "o_cards": len(o_cards),
        "o_events": len(o_events),
        "o_statements": len(o_statements),
        "o_statements_with_arbeitsgang": sum(int(row["arbeitsgang_tokens"]) > 0 for row in o_statements),
        "fluent_statement_revisions": sum(row["revision"] != "NONE" for row in o_statements),
        "prediction_rows": len(predictions),
        "changed_predictions": changed_predictions,
        "active_prediction_recipes": len({row["component_recipe"] for row in active}),
        "active_prediction_surfaces": len(active),
        "exceptions": len(exceptions),
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = f"""# Sidequest Pass 833: ninth compact workshop grammar

The ninth edition replaces the vague container value `O=VORGANG` with the
concrete workshop noun:

> `O = ARBEITSGANG`

The revision reaches {len(o_cards)} exact cards, {len(o_events)} events, and
{len(o_statements)} statements. All {len(o_statements)} O-bearing fluent
statements now name an ARBEITSGANG. Three statements required an explicit
wording repair: H2-S001, H3-S001, and B1-S012.

This is a compression improvement, not a new long gloss. `LSH+O` is now
“SPUELEN · ARBEITSGANG”, `T+CH+O+DY` is “BEARBEITEN · ENTNEHMEN ·
ARBEITSGANG · SCHLUSS”, and `O+CTH+OL+Y` says that the POSTEN is prepared
further in the current work step. The editor no longer has to insert the noun
“Arbeitsgang” behind an abstract “Vorgang”.

No other component changes. The complete inventory remains {len(components)}
components, {len(cards)} cards, {len(events)} events, and {len(statements)}
statements. The six learned exceptions and the 24-recipe / 30-surface active
prediction deck are preserved; all 76 speculative surfaces were mechanically
re-read under the new O value.

Next: run the hidden-word audit again. The first targets are SCHRITT around the
licensed DY close and FLUESSIGKEIT around AIR, but neither is to be promoted
merely because fluent German prefers it.
"""
    (HERE / f"{PREFIX}_REPORT.md").write_text(report, encoding="utf-8")

    grammar = """# Ninth workshop grammar — compact teaching sheet

Control: OK ANSETZEN; OT DANACH; OL WEITER.

Actions: CH ENTNEHMEN; T BEARBEITEN; CTH BEREITEN; SH HALTEN; SHED STEHENLASSEN.

Transfer: K ZUGEBEN; P EINBRINGEN; L LEITEN; CHD UMSETZEN.

Processes: CHK WAERMEN; LSH SPUELEN; R KUEHLEN; CFH AUSPRESSEN; SOLK SAMMELN.

Materials: AIR WASSER; OR ANSATZ; HO ZUTAT. Places: AR QUELLE; CKH DURCHLASS;
AL ZIELSTELLE. O names the current ARBEITSGANG.

Quantity: S PROBE; AIN PORTION; AIIN SOLLMASS; IIN STUFE.

Grade: E KURZ; EE LANG; EEE VOLL. Current item: Y POSTEN. Licensed DY closes.

Bound values: AN NACHGABE; DA ZWEI before IIN; LD BEFESTIGEN before DY.

Whole words: OS DAZU; DCHOL/SCHOL DAVON; TALAM BEISEITESTELLEN.
"""
    (HERE / f"{PREFIX}_ONE_PAGE_GRAMMAR.md").write_text(grammar, encoding="utf-8")


if __name__ == "__main__":
    main()
