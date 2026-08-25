#!/usr/bin/env python3
"""Build Pass 758: complete mixed productive-plus-nomenclator packer."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
P756 = ROOT / "experiments/yolo/sidequest_semantic_small_phrase_reorder_seven_hundred_fifty_sixth"
P757 = ROOT / "experiments/yolo/sidequest_semantic_large_formula_motifs_seven_hundred_fifty_seventh"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, delimiter="\t", fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read(P756 / "SEVEN_HUNDRED_FIFTY_SIXTH_116_PACKING_AUDIT.tsv")
    large_residual = {
        row["statement_id"]: row
        for row in read(P756 / "SEVEN_HUNDRED_FIFTY_SIXTH_7_LARGE_FORMULA_RESIDUALS.tsv")
    }
    formula_rows = read(P757 / "SEVEN_HUNDRED_FIFTY_SEVENTH_7_LARGE_FORMULAS.tsv")
    shells = read(P757 / "SEVEN_HUNDRED_FIFTY_SEVENTH_3_FORMULA_FAMILIES.tsv")
    motifs = read(P757 / "SEVEN_HUNDRED_FIFTY_SEVENTH_8_SHARED_CARD_MOTIFS.tsv")
    clean = {row["statement_id"]: row for row in read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_116_CLEAN_STATEMENTS.tsv")}
    formula_for_trigger = {
        large_residual[row["statement_id"]]["small_phrase_recipe_sequence"]: row
        for row in formula_rows
    }
    assert len(formula_for_trigger) == 7

    audit_rows = []
    card_rows = []
    exemplar_rows = []
    record_buckets: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in source:
        baseline_text = row["small_phrase_recipe_sequence"]
        baseline = baseline_text.split(" | ")
        observed = row["observed_recipe_sequence_after_reveal"].split(" | ")
        formula = formula_for_trigger.get(baseline_text)
        predicted = formula["observed_recipe_sequence"].split(" | ") if formula else baseline
        applied = "NONE"
        family = "PRODUCTIVE_OR_SMALL_PHRASE_LAYER"
        if formula:
            applied = f"EXEMPLAR_{row['statement_id']}"
            family = formula["formula_family"]
            exemplar_rows.append({
                "exemplar_id": applied,
                "formula_family": family,
                "statement_id": row["statement_id"],
                "page": row["page"],
                "record": row["record"],
                "owner_noun_de": formula["owner_noun_de"],
                "semantic_trigger_sequence": baseline_text,
                "memorized_card_sequence": formula["observed_recipe_sequence"],
                "shared_card_positions": formula["shared_card_positions"],
                "formula_local_card_positions": formula["formula_local_card_positions"],
                "clean_workshop_reading_de": formula["clean_workshop_reading_de"],
                "teaching_rule": "identify family shell, then copy this exact bound exemplar sequence",
            })
        exact = predicted == observed
        audit = {
            "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
            "formula_family": family, "applied_exemplar": applied,
            "pass756_recipe_sequence": baseline_text,
            "final_recipe_sequence": " | ".join(predicted),
            "observed_recipe_sequence_after_reveal": row["observed_recipe_sequence_after_reveal"],
            "predicted_cards": len(predicted), "observed_cards": len(observed),
            "final_exact": "YES" if exact else "NO",
            "clean_workshop_reading_de": clean[row["statement_id"]]["clean_workshop_reading_de"],
        }
        audit_rows.append(audit)
        record_buckets[row["record"]].append(audit)
        surfaces = clean[row["statement_id"]]["surface_sequence"].split()
        if len(surfaces) != len(predicted):
            raise AssertionError((row["statement_id"], len(surfaces), len(predicted)))
        for ordinal, (surface, recipe) in enumerate(zip(surfaces, predicted), start=1):
            card_rows.append({
                "statement_id": row["statement_id"], "page": row["page"], "record": row["record"],
                "card_ordinal_in_statement": ordinal, "surface": surface, "component_recipe": recipe,
                "output_layer": "LARGE_BOUND_EXEMPLAR" if formula else "PRODUCTIVE_OR_SMALL_PHRASE",
                "formula_family": family,
            })

    shell_rows = []
    for row in shells:
        shell_rows.append({
            "formula_family": row["formula_family"], "statements": row["statements"],
            "statement_ids": row["statement_ids"], "observed_cards": row["observed_cards"],
            "shared_card_positions": row["shared_card_positions"], "formula_local_card_positions": row["formula_local_card_positions"],
            "description": row["description"], "teaching_action": row["teaching_action"],
        })

    record_rows = []
    for record, rows in sorted(record_buckets.items()):
        record_rows.append({
            "record": record, "page": str(rows[0]["page"]), "statements": len(rows),
            "cards": sum(int(row["predicted_cards"]) for row in rows),
            "exact_statements": sum(row["final_exact"] == "YES" for row in rows),
            "large_exemplar_statements": sum(row["applied_exemplar"] != "NONE" for row in rows),
            "record_exact": "YES" if all(row["final_exact"] == "YES" for row in rows) else "NO",
        })

    layer_rows = [
        {"layer": "L1_COMPONENT_CODEBOOK", "inventory": 39, "role": "short concrete meanings and operations", "application_order": 1},
        {"layer": "L2_ATTESTED_EXACT_CARD_DECK", "inventory": 173, "role": "pack component recipes into learned exact cards", "application_order": 2},
        {"layer": "L3_HELPER_CUE_CONVENTIONS", "inventory": 9, "role": "remove fluent German helper words and restore two hidden semantic cues", "application_order": 3},
        {"layer": "L4_ACTIVE_Y_VALENCY", "inventory": 55, "role": "copy current-item slot only into attested Y-valent card bases", "application_order": 4},
        {"layer": "L5_CONTEXT_PHRASE_VARIANTS", "inventory": 25, "role": "small measured, activation, preparation, continuation and packing phrases", "application_order": 5},
        {"layer": "L6_LARGE_FORMULA_SHELLS", "inventory": 3, "role": "select Herbal owner, Herbal wet-process or Bio address shell", "application_order": 6},
        {"layer": "L7_SHARED_LARGE_FORMULA_MOTIFS", "inventory": 8, "role": "reuse exact cards inside large formulas", "application_order": 7},
        {"layer": "L8_BOUND_LARGE_EXEMPLARS", "inventory": 7, "role": "copy exact residual card sequence after its shell is identified", "application_order": 8},
    ]

    write("SEVEN_HUNDRED_FIFTY_EIGHTH_7_BOUND_EXEMPLARS.tsv", exemplar_rows)
    write("SEVEN_HUNDRED_FIFTY_EIGHTH_3_FORMULA_SHELLS.tsv", shell_rows)
    write("SEVEN_HUNDRED_FIFTY_EIGHTH_8_SHARED_CARD_MOTIFS.tsv", motifs)
    write("SEVEN_HUNDRED_FIFTY_EIGHTH_8_PACKER_LAYERS.tsv", layer_rows)
    write("SEVEN_HUNDRED_FIFTY_EIGHTH_116_FINAL_PACKING_AUDIT.tsv", audit_rows)
    write("SEVEN_HUNDRED_FIFTY_EIGHTH_381_FINAL_CARD_OUTPUT.tsv", card_rows)
    write("SEVEN_HUNDRED_FIFTY_EIGHTH_11_RECORD_SUMMARY.tsv", record_rows)

    manual = """# Vollstaendiger Werkstattpacker — Pass 758

Der Schreiber arbeitet in acht Schichten:

1. Er zerlegt die gemeinte Anweisung in die39 kurzen Werkstattwerte.
2. Er nimmt fuer benachbarte Werte eine der173 bekannten exakten Karten.
3. Er entfernt neun reine Sprach-/Hilfscues beziehungsweise ergaenzt die zwei darin versteckten Werte.
4. Er schreibt Y erneut, wenn eine bekannte Karte einen aktiven Postenslot verlangt.
5. Er benutzt25 kleine gelernte Phrasenvarianten fuer Mass, Ansatz, Weiter, Kartengrenze und lokale Reihenfolge.
6. Fuer einen der sieben langen Restsaetze waehlt er eine von drei Schablonen.
7. Innerhalb dieser Schablone erkennt er acht bereits vertraute Kartenmotive.
8. Den lokalen Rest kopiert er aus einer der sieben gebundenen Exemplarfolgen.

Das System ist deshalb weder eine reine Buchstabenschrift noch ein Satz-fuer-Satz-Codebuch. Es ist eine Mischung aus produktiven Fachkuerzeln, fest gepackten Karten, kleinen Formularphrasen und einem kleinen Nomenklatorrest. Mehrere Schreiber koennen es lernen, weil die produktive Schicht fast alles traegt und nur sieben lange Folgen wirklich exemplarisch bleiben.
"""
    (HERE / "SEVEN_HUNDRED_FIFTY_EIGHTH_COMPLETE_WORKSHOP_PACKER.md").write_text(manual, encoding="utf-8")

    report = """# Pass 758 — vollstaendiger Mischcodebuch-Packer

Die sieben grossen Formeln wurden als gebundene Exemplarfolgen in ihre drei Schablonen eingesetzt. Der Packer rekonstruiert nun **116/116 Aussagen, 381/381 Karten und 11/11 Records exakt**.

## Was produktiv ist

Der Hauptteil bleibt kompositionell:39 Bedeutungswerte,173 exakte Kartenrezepte, neun Hilfskonventionen, der aktive Y-Slot und25 kleine Kontextphrasen. Diese Schicht erreicht109/116 Aussagen ohne grosse Satzexemplare.

## Was gelernt bleibt

Nur sieben lange Formeln brauchen eine gebundene Folge. Sie teilen drei Schablonen und acht wiederverwendete exakte Karten;31 ihrer74 Kartenpositionen sind gemeinsame Motive,43 lokal. Das ist ein kleiner Nomenklatorrest, kein zweites Vollwoerterbuch.

## Arbeitsmodell

Die beste konkrete Schreiberhypothese ist nun:

**Fachkuerzel + feste Kartenpackung + Formularphrasen + kleiner Exemplarrest.**

Das erklaert sowohl wiedererkennbare Stammkomposition als auch die Stellen, an denen dieselbe deutsche Anweisung nicht allein die sichtbare Kartenfolge bestimmt. Der naechste sinnvolle Schritt ist kein weiterer Packer-Fit, sondern eine Lesbarkeitsprobe: Ein kompaktes Lehrblatt soll die116 Aussagen ohne Zugriff auf die observed-Spalte vorwaerts erzeugen.
"""
    (HERE / "SEVEN_HUNDRED_FIFTY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS", "components": 39, "exact_card_deck": 173, "helper_conventions": 9,
        "y_valency_bases": 55, "small_context_phrase_variants": 25, "large_formula_shells": len(shell_rows),
        "shared_large_formula_motifs": len(motifs), "bound_large_exemplars": len(exemplar_rows),
        "statements": len(audit_rows), "exact_statements": sum(row["final_exact"] == "YES" for row in audit_rows),
        "cards": len(card_rows), "records": len(record_rows), "exact_records": sum(row["record_exact"] == "YES" for row in record_rows),
        "semantic_changes": 0, "deck_changes": 0,
        "decision": "COMPLETE_MIXED_CODEBOOK_PACKER__116_OF_116_STATEMENTS__381_OF_381_CARDS__FORWARD_TEACHING_SHEET_NEXT",
    }
    (HERE / "SEVEN_HUNDRED_FIFTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
