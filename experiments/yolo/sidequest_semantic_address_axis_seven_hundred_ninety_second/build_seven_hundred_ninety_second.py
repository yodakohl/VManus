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
TOKENS = ("AL", "AR")
READING = {"AL": "ZIELSTELLE", "AR": "QUELLE"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def address_token(recipe: str) -> str | None:
    present = [token for token in recipe.split("+") if token in TOKENS]
    return present[0] if len(present) == 1 else None


def address_signature(recipe: str) -> str:
    return "+".join("ADDR" if token in TOKENS else token for token in recipe.split("+"))


def swap_recipe(recipe: str, source_token: str) -> str:
    target = "AR" if source_token == "AL" else "AL"
    return "+".join(target if token == source_token else token for token in recipe.split("+"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    rows = read(SOURCE)
    seen_surfaces = {row["surface"] for row in rows}
    target = [row for row in rows if address_token(row["component_recipe"])]

    event_rows = []
    for row in target:
        token = address_token(row["component_recipe"])
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "exact_card_id": row["card_no"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "address_token": token,
                "address_reading_de": READING[token],
                "working_reading_de": row["rebuilt_reading_de"],
                "surface_transparency": "TRANSPARENT" if token.lower() in row["surface"] else "OPAQUE",
            }
        )

    by_card: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_card[str(row["exact_card_id"])].append(row)
    card_rows = []
    for card, card_events in sorted(by_card.items()):
        card_rows.append(
            {
                "exact_card_id": card,
                "address_token": card_events[0]["address_token"],
                "component_recipe": card_events[0]["component_recipe"],
                "working_reading_de": card_events[0]["working_reading_de"],
                "surfaces": ",".join(sorted({str(row["surface"]) for row in card_events})),
                "events": len(card_events),
                "pages": ",".join(sorted({str(row["page"]) for row in card_events})),
            }
        )

    by_signature: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        by_signature[address_signature(str(row["component_recipe"]))].append(row)
    paired = {
        key: value
        for key, value in by_signature.items()
        if {str(row["address_token"]) for row in value} == set(TOKENS)
    }
    pair_rows = []
    rung_rows = []
    direct_pairs = []
    for sig, sig_events in sorted(paired.items()):
        al_surfaces = sorted({str(row["surface"]) for row in sig_events if row["address_token"] == "AL"})
        ar_surfaces = sorted({str(row["surface"]) for row in sig_events if row["address_token"] == "AR"})
        pair_rows.append(
            {
                "address_signature": sig,
                "al_events": sum(row["address_token"] == "AL" for row in sig_events),
                "ar_events": sum(row["address_token"] == "AR" for row in sig_events),
                "total_events": len(sig_events),
                "al_surfaces": ",".join(al_surfaces),
                "ar_surfaces": ",".join(ar_surfaces),
                "instruction_reversal": "TARGET_TO_SOURCE_WITH_OPERATION_FIXED",
            }
        )
        for token in TOKENS:
            token_events = [row for row in sig_events if row["address_token"] == token]
            rung_rows.append(
                {
                    "address_signature": sig,
                    "address_token": token,
                    "address_reading_de": READING[token],
                    "component_recipes": ",".join(sorted({str(row["component_recipe"]) for row in token_events})),
                    "surfaces": ",".join(sorted({str(row["surface"]) for row in token_events})),
                    "events": len(token_events),
                    "working_readings_de": " | ".join(sorted({str(row["working_reading_de"]) for row in token_events})),
                }
            )
        for al_surface in al_surfaces:
            predicted_ar = al_surface.replace("al", "ar")
            if predicted_ar in ar_surfaces:
                direct_pairs.append(
                    {
                        "address_signature": sig,
                        "al_surface": al_surface,
                        "al_reading_de": next(str(row["working_reading_de"]) for row in sig_events if row["surface"] == al_surface),
                        "ar_surface": predicted_ar,
                        "ar_reading_de": next(str(row["working_reading_de"]) for row in sig_events if row["surface"] == predicted_ar),
                        "surface_change": "al→ar",
                    }
                )

    recipe_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in event_rows:
        recipe_groups[str(row["component_recipe"])].append(row)
    unpaired = [recipe for recipe in recipe_groups if address_signature(recipe) not in paired]
    counterpart_rows = []
    prediction_rows = []
    for recipe in sorted(unpaired):
        recipe_events = recipe_groups[recipe]
        source_token = str(recipe_events[0]["address_token"])
        target_token = "AR" if source_token == "AL" else "AL"
        target_recipe = swap_recipe(recipe, source_token)
        source_reading = str(recipe_events[0]["working_reading_de"])
        target_reading = source_reading.replace(READING[source_token], READING[target_token])
        surfaces = sorted({str(row["surface"]) for row in recipe_events})
        predicted = [surface.replace(source_token.lower(), target_token.lower()) for surface in surfaces]
        counterpart_rows.append(
            {
                "source_recipe": recipe,
                "source_address": source_token,
                "source_surfaces": ",".join(surfaces),
                "source_events": len(recipe_events),
                "counterpart_recipe": target_recipe,
                "counterpart_address": target_token,
                "counterpart_reading_de": target_reading,
                "predicted_surfaces": ",".join(predicted),
                "status": "SURFACE_PREDICTABLE",
            }
        )
        for source_surface, predicted_surface in zip(surfaces, predicted):
            prediction_rows.append(
                {
                    "source_recipe": recipe,
                    "source_surface": source_surface,
                    "counterpart_recipe": target_recipe,
                    "predicted_surface": predicted_surface,
                    "counterpart_reading_de": target_reading,
                    "fixed_page_collision": "YES" if predicted_surface in seen_surfaces else "NO",
                    "status": "WORKSHOP_PREDICTION_ONLY__DO_NOT_INSERT",
                }
            )

    false_splits = [
        {
            "event_id": row["event_id"],
            "surface": row["surface"],
            "component_recipe": row["component_recipe"],
            "working_reading_de": row["rebuilt_reading_de"],
            "reason": "visible al belongs to learned TALAM whole card",
        }
        for row in rows
        if "al" in row["surface"] and "AL" not in row["component_recipe"].split("+")
    ]

    write(
        "SEVEN_HUNDRED_NINETY_SECOND_53_ADDRESS_EVENTS.tsv",
        event_rows,
        ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "address_token", "address_reading_de", "working_reading_de", "surface_transparency"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SECOND_32_ADDRESS_CARDS.tsv",
        card_rows,
        ["exact_card_id", "address_token", "component_recipe", "working_reading_de", "surfaces", "events", "pages"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SECOND_5_PAIRED_PARADIGMS.tsv",
        pair_rows,
        ["address_signature", "al_events", "ar_events", "total_events", "al_surfaces", "ar_surfaces", "instruction_reversal"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SECOND_10_ADDRESS_RUNGS.tsv",
        rung_rows,
        ["address_signature", "address_token", "address_reading_de", "component_recipes", "surfaces", "events", "working_readings_de"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SECOND_6_DIRECT_SURFACE_PAIRS.tsv",
        direct_pairs,
        ["address_signature", "al_surface", "al_reading_de", "ar_surface", "ar_reading_de", "surface_change"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SECOND_22_UNPAIRED_COUNTERPARTS.tsv",
        counterpart_rows,
        ["source_recipe", "source_address", "source_surfaces", "source_events", "counterpart_recipe", "counterpart_address", "counterpart_reading_de", "predicted_surfaces", "status"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SECOND_22_PREDICTED_SURFACES.tsv",
        prediction_rows,
        ["source_recipe", "source_surface", "counterpart_recipe", "predicted_surface", "counterpart_reading_de", "fixed_page_collision", "status"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SECOND_1_FALSE_AL_SPLIT.tsv",
        false_splits,
        ["event_id", "surface", "component_recipe", "working_reading_de", "reason"],
    )

    report = """# Pass 792 — AL zeigt zum Ziel, AR holt aus der Quelle

Die feste Prosa enthält 53 Adressereignisse: 39× AL und 14× AR, verteilt auf 32 Karten und 32 Rezepte. Alle 53 schreiben ihren Adresskern sichtbar. Das einzige verführerische fremde `al` ist `talam`; dort gehört es zur gelernten Ganzkarte TALAM=VERWAHREN und wird nicht abgespalten.

Fünf gemeinsame Hüllen bilden echte Ziel-/Quellpaare und decken 30 Ereignisse:

- `AL/AR`: Zielstelle gegen Quelle;
- `OK+AL/OK+AR`: an der Zielstelle ansetzen gegen aus der Quelle ansetzen;
- `K+AL/K+AR`: zur Zielstelle zugeben gegen aus der Quelle zugeben;
- `L+CHD+AL/L+CHD+AR`: zur Zielstelle leiten und umsetzen gegen aus der Quelle leiten und umsetzen;
- `OT+AL/OT+AR`: danach zur Zielstelle gegen danach aus der Quelle.

Sechs Oberflächenpaare zeigen den Wechsel besonders direkt: `dal/dar`, `sal/sar`, `chal/char`, `qokal/qokar`, `otal/otar`, `lchedal/lchedar`. Hier bleibt die Hülle stehen und nur `l→r` kehrt die Arbeitsadresse um.

Die 22 bislang einseitigen Rezepte liefern ebenso 22 Gegenoberflächen ohne Kollision, darunter `daldy→dardy`, `qokeedal→qokeedar`, `cheoar→cheoal`, `pchedal→pchedar` und `lar→lal`. Damit steht neben Grad und Menge nun eine dritte produktive Achse: Adresse AL/AR = Ziel/Quelle.

Als nächstes setzen wir diese 22 Gegenkarten in ihre vollständigen Aussagen ein. Dabei muss sich nur die Richtung der lokalen Handlung ändern; Stoff, Grad, Menge und Abschluss bleiben fest.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_SECOND_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "address_events": len(event_rows),
        "address_cards": len(card_rows),
        "address_recipes": len(recipe_groups),
        "al_events": sum(row["address_token"] == "AL" for row in event_rows),
        "ar_events": sum(row["address_token"] == "AR" for row in event_rows),
        "transparent_events": sum(row["surface_transparency"] == "TRANSPARENT" for row in event_rows),
        "paired_paradigms": len(pair_rows),
        "paired_events": sum(int(row["total_events"]) for row in pair_rows),
        "direct_surface_pairs": len(direct_pairs),
        "unpaired_recipes": len(counterpart_rows),
        "predicted_surfaces": len(prediction_rows),
        "prediction_collisions": sum(row["fixed_page_collision"] == "YES" for row in prediction_rows),
        "false_al_splits": len(false_splits),
        "decision": "AL_TARGET_AND_AR_SOURCE_FORM_PRODUCTIVE_ADDRESS_PAIRS",
    }
    (HERE / "SEVEN_HUNDRED_NINETY_SECOND_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
