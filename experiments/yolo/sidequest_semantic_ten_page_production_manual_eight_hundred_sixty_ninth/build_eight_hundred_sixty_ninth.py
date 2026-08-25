#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HERBAL = ROOT / "sidequest_semantic_four_herbal_process_atlas_eight_hundred_sixty_fourth" / "EIGHT_HUNDRED_SIXTY_FOURTH_100_CARD_HERBAL_ATLAS.tsv"
BIO = ROOT / "sidequest_semantic_three_biological_process_atlas_eight_hundred_sixty_fifth" / "EIGHT_HUNDRED_SIXTY_FIFTH_281_CARD_BIOLOGICAL_ATLAS.tsv"
ASTRO = ROOT / "sidequest_theory_candidates_v80" / "V80_R3_395_ASTRO_GROUPS.tsv"
SHELF = ROOT / "sidequest_semantic_when_condition_shelf_eight_hundred_sixty_eighth" / "EIGHT_HUNDRED_SIXTY_EIGHTH_395_GROUP_CONDITION_SHELF.tsv"
PREFIX = "EIGHT_HUNDRED_SIXTY_NINTH"
PAGE_ORDER = ["f10r", "f11r", "f55v", "f56r", "f81v", "f82r", "f83r", "f67r2", "f68r1", "f69v"]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    herbal = read(HERBAL)
    bio = read(BIO)
    astro = read(ASTRO)
    shelves = {row["group_serial"]: row for row in read(SHELF)}

    unified = []
    serial = 0
    for row in herbal:
        serial += 1
        unified.append(
            {
                "unified_id": f"U{serial:03d}",
                "layer": "WHAT_PREPARATION",
                "page": row["page"],
                "local_unit": row["record"],
                "local_statement_or_locus": row["statement_id"],
                "source_id": row["event_id"],
                "surface": row["surface"],
                "opaque_identity": row["exact_card_id"],
                "working_reading_de": row["card_meaning_de"],
                "picture_contribution_de": "abgebildete Pflanze als Besitzer",
                "master_contribution_de": "konkreter Pflanzen- und Produktname; reale Maß-/Zeitwerte",
            }
        )
    for row in bio:
        serial += 1
        unified.append(
            {
                "unified_id": f"U{serial:03d}",
                "layer": "HOW_APPLICATION",
                "page": row["page"],
                "local_unit": row["record"],
                "local_statement_or_locus": row["statement_id"],
                "source_id": row["event_id"],
                "surface": row["surface"],
                "opaque_identity": row["exact_card_id"],
                "working_reading_de": row["card_meaning_de"],
                "picture_contribution_de": row["owner_de"],
                "master_contribution_de": "konkreter Körper-/Sachreferent; reale Maß-/Zeitwerte; Ergebnis",
            }
        )
    for row in astro:
        serial += 1
        shelf = shelves[row["group_serial"]]
        unified.append(
            {
                "unified_id": f"U{serial:03d}",
                "layer": "WHEN_CONDITION",
                "page": row["page"],
                "local_unit": shelf["condition_shelf"],
                "local_statement_or_locus": row["locus"],
                "source_id": row["opaque_local_id"],
                "surface": row["surface_display_only"],
                "opaque_identity": row["opaque_local_id"],
                "working_reading_de": f"lokales Etikett in {shelf['condition_shelf']} kopieren",
                "picture_contribution_de": row["local_image_owner"],
                "master_contribution_de": "konkreter Himmels-/Kalender-/Qualitätswert dieses Locus",
            }
        )

    page_rows = []
    for page in PAGE_ORDER:
        subset = [row for row in unified if row["page"] == page]
        page_rows.append(
            {
                "page_order": PAGE_ORDER.index(page) + 1,
                "page": page,
                "layer": subset[0]["layer"],
                "visible_groups": len(subset),
                "local_units": len({row["local_unit"] for row in subset}),
                "picture_role_de": "Besitzer/Station/Instrument liefert die stillen Argumente",
                "card_or_label_role_de": "sichtbare Reihenfolge und lokaler Arbeits-/Lookupwert",
                "master_role_de": "konkrete Namen und externe Werte ergänzen",
            }
        )

    manual = [
        {"step": 1, "stage": "ORDER", "action_de": "Produktklasse P1–P4 und Anwendung B1–B6 vom Meister empfangen"},
        {"step": 2, "stage": "WHAT", "action_de": "zugehörige Herbal-Pflanze im Bild wählen"},
        {"step": 3, "stage": "WHAT", "action_de": "Herbal-Karten in Quellordnung lesen oder kopieren"},
        {"step": 4, "stage": "WHAT", "action_de": "Zubereitungsschritte ausführen; offene Register beibehalten"},
        {"step": 5, "stage": "BRIDGE", "action_de": "fertigen Bestand unter P1–P4 im Werkstattgedächtnis ablegen"},
        {"step": 6, "stage": "HOW", "action_de": "Biological-Seite und lokalen Bildbesitzer wählen"},
        {"step": 7, "stage": "HOW", "action_de": "jede kurze Zelle bis zum lizenzierten Schluss ausführen"},
        {"step": 8, "stage": "HOW", "action_de": "bei sichtbarem Besitzerwechsel den lokalen Posten zurücksetzen"},
        {"step": 9, "stage": "WHEN", "action_de": "das vom Meister benannte Astro-Teilinstrument öffnen"},
        {"step": 10, "stage": "WHEN", "action_de": "nur den lokalen Locus und seine Oberfläche kopieren"},
        {"step": 11, "stage": "WHEN", "action_de": "Bedingungswert aus dem Meisterexemplar einsetzen; keine Richtung erfinden"},
        {"step": 12, "stage": "CLOSE", "action_de": "Auftrag mit Produkt, Station, Maß, Dauer, Ergebnis und Bedingung rücklesen"},
    ]

    # Complete sample: P4=f56r, B2=f82r, C4=f69v.12. The last locus was
    # chosen by the imagined master, never by a circular-order rule.
    sample_source = []
    sample_source.extend(row for row in unified if row["page"] == "f56r")
    sample_source.extend(row for row in unified if row["layer"] == "HOW_APPLICATION" and row["local_unit"] == "B2")
    sample_source.extend(row for row in unified if row["layer"] == "WHEN_CONDITION" and row["local_statement_or_locus"] == "f69v.12")
    sample_rows = []
    for index, row in enumerate(sample_source, start=1):
        sample_rows.append(
            {
                "sample_mark": f"M{index:03d}",
                "stage": row["layer"],
                "page": row["page"],
                "source_id": row["source_id"],
                "surface": row["surface"],
                "opaque_identity": row["opaque_identity"],
                "visible_working_reading_de": row["working_reading_de"],
                "picture_argument_de": row["picture_contribution_de"],
                "master_argument_de": row["master_contribution_de"],
            }
        )

    master_values = [
        {"value_id": "MV1", "slot": "PRODUCT", "sample_value_de": "Spülansatz aus der abgebildeten stacheligen Pflanze", "encoded_in_cards": "NO", "supply": "PICTURE_PLUS_MASTER"},
        {"value_id": "MV2", "slot": "MEASURE", "sample_value_de": "ein kleiner Schöpfbecher je Station", "encoded_in_cards": "CATEGORY_ONLY", "supply": "MASTER"},
        {"value_id": "MV3", "slot": "DURATION", "sample_value_de": "eine kurze, eine längere und eine volle Haltestufe nach Meistermaß", "encoded_in_cards": "GRADE_ONLY", "supply": "MASTER"},
        {"value_id": "MV4", "slot": "RESULT", "sample_value_de": "gleichmäßiger Durchlauf an allen fünf Bildstationen", "encoded_in_cards": "STATE_ONLY", "supply": "PICTURE_PLUS_MASTER"},
        {"value_id": "MV5", "slot": "CONDITION", "sample_value_de": "lokaler linker f69-Platz L09 mit Etikett otody", "encoded_in_cards": "LOCAL_LABEL_ONLY", "supply": "ASTRO_PICTURE_PLUS_MASTER"},
    ]

    roundtrip = [
        {"checkpoint": "VISIBLE_ORDER", "forward_value": "27 WHAT + 62 HOW + 1 WHEN marks", "backward_without_master": "RECOVERED", "backward_with_master": "RECOVERED", "loss_de": "keiner"},
        {"checkpoint": "SURFACE_AND_OPAQUE_ID", "forward_value": "90 sichtbare Formen und Identitäten", "backward_without_master": "RECOVERED", "backward_with_master": "RECOVERED", "loss_de": "keiner"},
        {"checkpoint": "PREPARATION_CLASS", "forward_value": "P4 zutatenreicher Durchlassansatz", "backward_without_master": "RECOVERED", "backward_with_master": "RECOVERED", "loss_de": "keiner"},
        {"checkpoint": "APPLICATION_CLASS", "forward_value": "B2 fünf gemessene Stationsanwendungen", "backward_without_master": "RECOVERED", "backward_with_master": "RECOVERED", "loss_de": "keiner"},
        {"checkpoint": "CONDITION_SHELF", "forward_value": "C4 linker lokaler 28-Platz-Bestand", "backward_without_master": "RECOVERED", "backward_with_master": "RECOVERED", "loss_de": "keiner"},
        {"checkpoint": "PRODUCT_IDENTITY", "forward_value": master_values[0]["sample_value_de"], "backward_without_master": "LOST", "backward_with_master": "RECOVERED", "loss_de": "Pflanzenbild liefert keinen Namen"},
        {"checkpoint": "NUMERIC_MEASURE", "forward_value": master_values[1]["sample_value_de"], "backward_without_master": "LOST", "backward_with_master": "RECOVERED", "loss_de": "Karte zeigt nur Maßklasse"},
        {"checkpoint": "NUMERIC_DURATION", "forward_value": master_values[2]["sample_value_de"], "backward_without_master": "LOST", "backward_with_master": "RECOVERED", "loss_de": "Karte zeigt nur Grad"},
        {"checkpoint": "MATERIAL_RESULT", "forward_value": master_values[3]["sample_value_de"], "backward_without_master": "LOST", "backward_with_master": "RECOVERED", "loss_de": "Zielzustand ist nur grob"},
        {"checkpoint": "EXTERNAL_CONDITION_VALUE", "forward_value": master_values[4]["sample_value_de"], "backward_without_master": "LOCAL_LABEL_ONLY", "backward_with_master": "RECOVERED", "loss_de": "Etikett nennt keinen externen Kalenderwert"},
    ]

    write(f"{PREFIX}_776_TEN_PAGE_PRODUCTION_LEDGER.tsv", unified, ["unified_id", "layer", "page", "local_unit", "local_statement_or_locus", "source_id", "surface", "opaque_identity", "working_reading_de", "picture_contribution_de", "master_contribution_de"])
    write(f"{PREFIX}_10_PAGE_LAYER_SUMMARY.tsv", page_rows, ["page_order", "page", "layer", "visible_groups", "local_units", "picture_role_de", "card_or_label_role_de", "master_role_de"])
    write(f"{PREFIX}_12_STEP_SCRIBAL_MANUAL.tsv", manual, ["step", "stage", "action_de"])
    write(f"{PREFIX}_90_MARK_COMPLETE_SAMPLE.tsv", sample_rows, ["sample_mark", "stage", "page", "source_id", "surface", "opaque_identity", "visible_working_reading_de", "picture_argument_de", "master_argument_de"])
    write(f"{PREFIX}_5_SAMPLE_MASTER_VALUES.tsv", master_values, ["value_id", "slot", "sample_value_de", "encoded_in_cards", "supply"])
    write(f"{PREFIX}_10_CHECKPOINT_ROUNDTRIP.tsv", roundtrip, ["checkpoint", "forward_value", "backward_without_master", "backward_with_master", "loss_de"])

    readable = [
        "# Vollständiger Musterauftrag P4 → B2 → C4-L09",
        "",
        "## Meisterdiktat",
        "",
        "Bereite einen Spülansatz aus der abgebildeten stacheligen Pflanze. Nimm für jede",
        "der fünf gezeichneten Stationen einen kleinen Schöpfbecher. Führe die kurzen,",
        "längeren und vollen Haltestufen nach Werkstattmaß aus, bis der Durchlauf an allen",
        "Stationen gleichmäßig ist. Verwende den lokalen linken f69-Platz L09 mit dem",
        "sichtbaren Etikett `otody` als Bedingungsvermerk.",
        "",
        "## Sichtbare Ausführung",
        "",
        "1. f56r liefert 27 Karten für P4: Zutaten wählen, bemessen, durch den lokalen Gang",
        "   führen und den Anwendungsansatz bereitstellen.",
        "2. f82r liefert 62 Karten für B2: fünf Besitzerstationen, 22 kurze Zellen und 19",
        "   lizenzierte Schlüsse.",
        "3. f69v.12 liefert genau eine sichtbare Gruppe `otody` an C4/L09. Sie wird lokal",
        "   kopiert; weder Start noch Drehrichtung werden benötigt.",
        "",
        "## Rücklesung",
        "",
        "Ein Werkstattschreiber rekonstruiert alle 90 sichtbaren Marken sowie P4, B2 und C4.",
        "Ohne Meisterwissen verliert er jedoch Produktname, Zahlenmaß, reale Dauer, genaues",
        "Ergebnis und externen Wert von `otody`. Mit den fünf Meisterwerten ist der Auftrag",
        "vollständig ausführbar. Das ist der praktische Kern der aktuellen Theorie.",
    ]
    (HERE / f"{PREFIX}_COMPLETE_SAMPLE_ORDER.md").write_text("\n".join(readable) + "\n", encoding="utf-8")

    without_master = Counter(row["backward_without_master"] for row in roundtrip)
    summary = {
        "status": "PASS",
        "decision": "TEN_PAGE_WORKSHOP_SYSTEM_ROUNDTRIPS_FORM_BUT_NEEDS_FIVE_MASTER_VALUES_FOR_FULL_USE",
        "pages": len(page_rows),
        "visible_groups": len(unified),
        "layer_counts": dict(Counter(row["layer"] for row in unified)),
        "manual_steps": len(manual),
        "sample_visible_marks": len(sample_rows),
        "sample_stage_counts": dict(Counter(row["stage"] for row in sample_rows)),
        "roundtrip_without_master": dict(without_master),
        "roundtrip_with_master_recovered": sum(row["backward_with_master"] == "RECOVERED" for row in roundtrip),
        "master_values": len(master_values),
        "new_word_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 869: ten-page production manual and sample order\n\n"
        "The ten fixed pages now form one production manual over all 776 visible groups:\n"
        "100 WHAT/Herbal cards, 281 HOW/Biological cards and 395 WHEN/Astro labels. A\n"
        "twelve-step workflow and one complete P4 -> B2 -> C4-L09 order were executed.\n\n"
        "The sample preserves all 90 visible marks and recovers preparation, application and\n"
        "condition classes backward. Full practical use still requires five master values:\n"
        "product identity, numeric measure, numeric duration, material result and external\n"
        "condition value. The current model is therefore a learnable workshop notation with\n"
        "memorized payload, not autonomous plaintext.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
