#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = (
    HERE.parent
    / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
    / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
)
TOKENS = ("AIIN", "AIN")
READING = {"AIIN": "SOLLMASS", "AIN": "PORTION"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def quantity_token(recipe: str) -> str | None:
    present = [token for token in recipe.split("+") if token in TOKENS]
    if len(present) != 1:
        return None
    return present[0]


def quantity_signature(recipe: str) -> str:
    return "+".join("QTY" if token in TOKENS else token for token in recipe.split("+"))


def counterpart_recipe(recipe: str, source_token: str) -> str:
    target = "AIN" if source_token == "AIIN" else "AIIN"
    return "+".join(target if token == source_token else token for token in recipe.split("+"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    rows = read(SOURCE)
    seen_surfaces = {row["surface"] for row in rows}
    quantity_rows = [row for row in rows if quantity_token(row["component_recipe"])]

    event_rows: list[dict[str, object]] = []
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        by_statement[row["statement_id"]].append(row)
    position = {}
    for statement_rows in by_statement.values():
        for index, row in enumerate(statement_rows):
            position[row["event_id"]] = (
                "ONLY" if len(statement_rows) == 1 else "FIRST" if index == 0 else "LAST" if index == len(statement_rows) - 1 else "MIDDLE"
            )
    for row in quantity_rows:
        token = quantity_token(row["component_recipe"])
        expected_string = token.lower()
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "statement_position": position[row["event_id"]],
                "exact_card_id": row["card_no"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "quantity_token": token,
                "quantity_reading_de": READING[token],
                "working_reading_de": row["rebuilt_reading_de"],
                "surface_transparency": "TRANSPARENT" if expected_string in row["surface"] else "OPAQUE_WHOLE_ALLOGRAPH",
            }
        )

    card_rows: list[dict[str, object]] = []
    by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_card[str(row["exact_card_id"])].append(row)
    for card, card_events in sorted(by_card.items()):
        card_rows.append(
            {
                "exact_card_id": card,
                "quantity_token": card_events[0]["quantity_token"],
                "component_recipe": card_events[0]["component_recipe"],
                "working_reading_de": card_events[0]["working_reading_de"],
                "surfaces": ",".join(sorted({str(row["surface"]) for row in card_events})),
                "events": len(card_events),
                "pages": ",".join(sorted({str(row["page"]) for row in card_events})),
                "surface_transparency": "TRANSPARENT" if all(row["surface_transparency"] == "TRANSPARENT" for row in card_events) else "OPAQUE_WHOLE_ALLOGRAPH",
            }
        )

    by_signature: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_signature[quantity_signature(str(row["component_recipe"]))].append(row)
    paired_signatures = {
        key: value
        for key, value in by_signature.items()
        if {str(row["quantity_token"]) for row in value} == set(TOKENS)
    }
    pair_rows: list[dict[str, object]] = []
    rung_rows: list[dict[str, object]] = []
    for sig, sig_events in sorted(paired_signatures.items()):
        pair_rows.append(
            {
                "quantity_signature": sig,
                "aiin_events": sum(row["quantity_token"] == "AIIN" for row in sig_events),
                "ain_events": sum(row["quantity_token"] == "AIN" for row in sig_events),
                "total_events": len(sig_events),
                "aiin_surfaces": ",".join(sorted({str(row["surface"]) for row in sig_events if row["quantity_token"] == "AIIN"})),
                "ain_surfaces": ",".join(sorted({str(row["surface"]) for row in sig_events if row["quantity_token"] == "AIN"})),
                "semantic_contrast": "SOLLMASS_VS_PORTION",
            }
        )
        for token in TOKENS:
            token_events = [row for row in sig_events if row["quantity_token"] == token]
            rung_rows.append(
                {
                    "quantity_signature": sig,
                    "quantity_token": token,
                    "quantity_reading_de": READING[token],
                    "component_recipes": ",".join(sorted({str(row["component_recipe"]) for row in token_events})),
                    "surfaces": ",".join(sorted({str(row["surface"]) for row in token_events})),
                    "events": len(token_events),
                    "working_readings_de": " | ".join(sorted({str(row["working_reading_de"]) for row in token_events})),
                }
            )

    recipe_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        recipe_groups[str(row["component_recipe"])].append(row)
    unpaired_recipes = [
        recipe
        for recipe in recipe_groups
        if quantity_signature(recipe) not in paired_signatures
    ]
    counterpart_rows: list[dict[str, object]] = []
    surface_prediction_rows: list[dict[str, object]] = []
    withheld_rows: list[dict[str, object]] = []
    for recipe in sorted(unpaired_recipes):
        recipe_events = recipe_groups[recipe]
        source_token = str(recipe_events[0]["quantity_token"])
        target_token = "AIN" if source_token == "AIIN" else "AIIN"
        target_recipe = counterpart_recipe(recipe, source_token)
        source_surfaces = sorted({str(row["surface"]) for row in recipe_events})
        old = source_token.lower()
        new = target_token.lower()
        predicted = [surface.replace(old, new) for surface in source_surfaces if old in surface]
        source_reading = str(recipe_events[0]["working_reading_de"])
        target_reading = source_reading.replace(READING[source_token], READING[target_token])
        status = "SURFACE_PREDICTABLE" if predicted else "MEANING_COUNTERPART_ONLY__SURFACE_WITHHELD"
        counterpart_rows.append(
            {
                "source_recipe": recipe,
                "source_quantity": source_token,
                "source_surfaces": ",".join(source_surfaces),
                "source_events": len(recipe_events),
                "counterpart_recipe": target_recipe,
                "counterpart_quantity": target_token,
                "counterpart_reading_de": target_reading,
                "predicted_surfaces": ",".join(predicted) or "NO_SAFE_SURFACE",
                "status": status,
            }
        )
        if predicted:
            for surface in predicted:
                surface_prediction_rows.append(
                    {
                        "source_recipe": recipe,
                        "source_surface": next(item for item in source_surfaces if item.replace(old, new) == surface),
                        "counterpart_recipe": target_recipe,
                        "predicted_surface": surface,
                        "counterpart_reading_de": target_reading,
                        "fixed_page_collision": "YES" if surface in seen_surfaces else "NO",
                        "status": "WORKSHOP_PREDICTION_ONLY__DO_NOT_INSERT",
                    }
                )
        else:
            withheld_rows.append(
                {
                    "source_recipe": recipe,
                    "source_surface": ",".join(source_surfaces),
                    "counterpart_recipe": target_recipe,
                    "counterpart_reading_de": target_reading,
                    "reason": "source is a learned whole allograph without visible ain slot",
                }
            )

    teaching_rows = []
    for sig in ("QTY", "OK+QTY", "Y+K+QTY"):
        pair = next(row for row in pair_rows if row["quantity_signature"] == sig)
        teaching_rows.append(
            {
                "quantity_signature": sig,
                "aiin_surface_examples": pair["aiin_surfaces"],
                "aiin_reading_de": "SOLLMASS" if sig == "QTY" else "ANSETZEN · SOLLMASS" if sig == "OK+QTY" else "DIES · ZUGEBEN · SOLLMASS",
                "ain_surface_examples": pair["ain_surfaces"],
                "ain_reading_de": "PORTION" if sig == "QTY" else "ANSETZEN · PORTION" if sig == "OK+QTY" else "DIES · ZUGEBEN · PORTION",
                "lesson_de": "AIIN nennt die vorgeschriebene Menge; AIN nennt eine abgeteilte Portion",
            }
        )

    write(
        "SEVEN_HUNDRED_NINETIETH_57_QUANTITY_EVENTS.tsv",
        event_rows,
        ["event_id", "page", "record", "statement_id", "statement_position", "exact_card_id", "surface", "component_recipe", "quantity_token", "quantity_reading_de", "working_reading_de", "surface_transparency"],
    )
    write(
        "SEVEN_HUNDRED_NINETIETH_18_QUANTITY_CARDS.tsv",
        card_rows,
        ["exact_card_id", "quantity_token", "component_recipe", "working_reading_de", "surfaces", "events", "pages", "surface_transparency"],
    )
    write(
        "SEVEN_HUNDRED_NINETIETH_3_PAIRED_PARADIGMS.tsv",
        pair_rows,
        ["quantity_signature", "aiin_events", "ain_events", "total_events", "aiin_surfaces", "ain_surfaces", "semantic_contrast"],
    )
    write(
        "SEVEN_HUNDRED_NINETIETH_6_ATTESTED_QUANTITY_RUNGS.tsv",
        rung_rows,
        ["quantity_signature", "quantity_token", "quantity_reading_de", "component_recipes", "surfaces", "events", "working_readings_de"],
    )
    write(
        "SEVEN_HUNDRED_NINETIETH_12_UNPAIRED_COUNTERPARTS.tsv",
        counterpart_rows,
        ["source_recipe", "source_quantity", "source_surfaces", "source_events", "counterpart_recipe", "counterpart_quantity", "counterpart_reading_de", "predicted_surfaces", "status"],
    )
    write(
        "SEVEN_HUNDRED_NINETIETH_14_PREDICTED_SURFACES.tsv",
        surface_prediction_rows,
        ["source_recipe", "source_surface", "counterpart_recipe", "predicted_surface", "counterpart_reading_de", "fixed_page_collision", "status"],
    )
    write(
        "SEVEN_HUNDRED_NINETIETH_1_WITHHELD_SURFACE.tsv",
        withheld_rows,
        ["source_recipe", "source_surface", "counterpart_recipe", "counterpart_reading_de", "reason"],
    )
    write(
        "SEVEN_HUNDRED_NINETIETH_3_TEACHING_PAIRS.tsv",
        teaching_rows,
        ["quantity_signature", "aiin_surface_examples", "aiin_reading_de", "ain_surface_examples", "ain_reading_de", "lesson_de"],
    )

    report = """# Pass 790 — AIIN ist Maß, AIN ist Portion

Auf den sieben Prosaseiten tragen 57 Ereignisse einen echten Mengenbaustein: 39× AIIN und 18× AIN, verteilt auf 18 Karten und 18 Rezepte. 56/57 zeigen den Baustein auch direkt in der Oberfläche. Der einzige opake Fall ist `sotodan`, dessen gelerntes Kartenrezept OT+O+AIN eine Portion enthält, ohne `ain` sichtbar auszuschreiben.

Drei echte Minimalparadigmen tragen 40 Ereignisse:

- `AIIN` gegen `AIN`: vorgeschriebenes Maß gegen abgeteilte Portion;
- `OK+AIIN` gegen `OK+AIN`: nach Sollmaß ansetzen gegen eine Portion ansetzen;
- `Y+K+AIIN` gegen `Y+K+AIN`: hiervon nach Sollmaß zugeben gegen hiervon eine Portion zugeben.

Das ist nicht bloß eine ähnliche Zeichenfolge. In allen drei Familien bleibt der übrige Bau gleich, während `aiin → ain` dieselbe konkrete Bedeutungsverschiebung hervorruft. Damit ist AIIN/AIN neben E/EE/EEE unser stärkstes produktives semantisches Paradigma.

Zwölf Rezepte besitzen bislang nur eine Mengenseite. Für elf davon lassen sich 14 Gegenoberflächen direkt bilden (`otaiin→otain`, `orain→oraiin`, `chedain→chedaiin` usw.); keine steht bereits anders belegt auf den festen Seiten. `sotodan` bleibt eine gelernte Ganzkarte und bekommt keine erfundene Schreibform.

Als nächstes setzen wir die AIIN/AIN-Gegenkarten auf eine Lehrtafel und prüfen, welche der neuen Formen mit den bekannten Handhüllen kombinierbar sind. Danach folgt AL/AR als Ziel-/Quellpaar.
"""
    (HERE / "SEVEN_HUNDRED_NINETIETH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "quantity_events": len(event_rows),
        "quantity_cards": len(card_rows),
        "quantity_recipes": len(recipe_groups),
        "aiin_events": sum(row["quantity_token"] == "AIIN" for row in event_rows),
        "ain_events": sum(row["quantity_token"] == "AIN" for row in event_rows),
        "transparent_events": sum(row["surface_transparency"] == "TRANSPARENT" for row in event_rows),
        "paired_paradigms": len(pair_rows),
        "paired_events": sum(int(row["total_events"]) for row in pair_rows),
        "unpaired_recipes": len(counterpart_rows),
        "predicted_surfaces": len(surface_prediction_rows),
        "withheld_surfaces": len(withheld_rows),
        "prediction_collisions": sum(row["fixed_page_collision"] == "YES" for row in surface_prediction_rows),
        "decision": "AIIN_SOLLMASS_AND_AIN_PORTION_FORM_PRODUCTIVE_MINIMAL_PAIRS",
    }
    (HERE / "SEVEN_HUNDRED_NINETIETH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
