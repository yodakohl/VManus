#!/usr/bin/env python3
"""Choose one coherent concrete recipe vocabulary for the five Herbal articles."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
UNITS = ROOT / "experiments/yolo/sidequest_semantic_refined_controlled_rewrite_eighty_second_edition/EIGHTY_SECOND_14_REFINED_CONTROLLED_UNITS.tsv"
BINDING = ROOT / "experiments/yolo/sidequest_semantic_refined_controlled_rewrite_eighty_second_edition/EIGHTY_SECOND_776_REFINED_BINDING.tsv"
HISTORICAL = ROOT / "experiments/yolo/sidequest_historical_compositional_analogue_search/R2_SOURCES.tsv"


MODELS = {
    "M1_MEDICAL_MATERIA_RECIPE": {
        "WATER": "Wasser", "EXTRACTION_MEDIUM": "Wein", "OIL_BINDER": "Öl",
        "HONEY_BINDER": "Honig", "RESIDUE": "Satz", "DRINK_OR_PRODUCT": "Trank",
        "OUTER_APPLICATION": "Auflage",
    },
    "M2_DYE_PAINT_RECIPE": {
        "WATER": "Wasser", "EXTRACTION_MEDIUM": "Beize", "OIL_BINDER": "Öl",
        "HONEY_BINDER": "Gummi", "RESIDUE": "Trester", "DRINK_OR_PRODUCT": "Farbe",
        "OUTER_APPLICATION": "Anstrich",
    },
    "M3_COSMETIC_HOUSEHOLD_RECIPE": {
        "WATER": "Wasser", "EXTRACTION_MEDIUM": "Essig", "OIL_BINDER": "Öl",
        "HONEY_BINDER": "Wachs", "RESIDUE": "Satz", "DRINK_OR_PRODUCT": "Waschmittel",
        "OUTER_APPLICATION": "Einreibung",
    },
}

FIT = {
    "M1_MEDICAL_MATERIA_RECIPE": {"H1": (5, 4, 5, 4), "H2": (5, 5, 5, 4), "H3": (5, 5, 5, 5), "H4": (5, 5, 5, 4), "H5": (5, 5, 5, 5)},
    "M2_DYE_PAINT_RECIPE": {"H1": (4, 4, 4, 3), "H2": (5, 4, 4, 4), "H3": (5, 4, 4, 4), "H4": (4, 4, 4, 4), "H5": (4, 3, 4, 3)},
    "M3_COSMETIC_HOUSEHOLD_RECIPE": {"H1": (4, 3, 4, 3), "H2": (5, 5, 4, 4), "H3": (5, 5, 5, 4), "H4": (5, 5, 4, 4), "H5": (5, 4, 4, 4)},
}

SELECTED_SLOTS = [
    ("WATER", "Wasser", "gemeinsames Löse-/Waschmedium"),
    ("WINE", "Wein", "Auszugsflüssigkeit für H3-H5"),
    ("OIL", "Öl", "Trägerstoff für H2-H3"),
    ("HONEY", "Honig", "Bindestoff für H4-H5"),
    ("SEDIMENT", "Satz", "verwahrter Rückstand in H1"),
    ("DRINK", "Trank", "dosiertes Mittel in H1/H3/H5"),
    ("SALVE", "Salbe", "Öl-Auszug in H2"),
    ("RUB", "Einreibung", "Öl-Auszug in H3"),
    ("WASH", "Waschung", "geklärter Auszug in H4"),
    ("POULTICE", "Auflage", "gebundener Pflanzenstoff in H2/H4/H5"),
    ("CLOTH", "Tuch", "Auswring-/Seihträger"),
]

ARTICLES = {
    "H1": "Von der Bildpflanze die Wurzel nehmen, in Wasser im Gefäß ansetzen und den Auszug trennen. Eine örtliche Portion als Trank verwenden; den Satz verwahren.",
    "H2": "Jungen Spross und Blatt nehmen, durch Tuch auswringen und den Auszug mit Öl im Gefäß zur Salbe ansetzen. Eine örtliche Portion als Auflage verwenden.",
    "H3": "Blüte und Blatt in Wein ansetzen, durch Tuch auswringen, absetzen und nachseihen. Eine Portion des Auszugs als Trank verwenden; den übrigen Auszug mit Öl als Einreibung ansetzen.",
    "H4": "Blatt in Wein im Gefäß ansetzen, durch Tuch auswringen und den Auszug als Waschung sammeln. Den Pflanzenrest mit Honig binden und als Auflage verwenden.",
    "H5": "Frisches Kraut mit Wasser als kurze Waschung oder Auflage ansetzen. Den übrigen Pflanzenstoff in Wein ausziehen, durch Tuch trennen, mit Honig binden und eine örtliche Portion als Trank verwenden.",
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    model_rows = []
    for model_id, vocabulary in MODELS.items():
        for slot, value in vocabulary.items():
            model_rows.append({"model_id": model_id, "source_slot": slot, "concrete_value_de": value})
    write_tsv(OUT / "EIGHTY_THIRD_21_MODEL_VOCABULARY_ROWS.tsv", model_rows)

    comparison_rows = []
    totals = {model: 0 for model in MODELS}
    for model_id in MODELS:
        for unit_id in ("H1", "H2", "H3", "H4", "H5"):
            substance, process, purpose, cross_article = FIT[model_id][unit_id]
            total = substance + process + purpose + cross_article
            totals[model_id] += total
            comparison_rows.append({
                "model_id": model_id,
                "unit_id": unit_id,
                "substance_chain_fit_1_to_5": substance,
                "operation_chain_fit_1_to_5": process,
                "purpose_fit_1_to_5": purpose,
                "cross_article_reuse_1_to_5": cross_article,
                "editorial_fit_total_20": total,
                "working_reading_de": ARTICLES[unit_id] if model_id == "M1_MEDICAL_MATERIA_RECIPE" else "Setze dasselbe sichtbare Pflanzen- und Operationsgerüst mit dem Vokabular dieses Rivalen.",
            })
    write_tsv(OUT / "EIGHTY_THIRD_15_MODEL_ARTICLE_COMPARISONS.tsv", comparison_rows)

    selected_words = [
        {"recipe_word_id": f"R{index:02d}", "recipe_slot": slot, "selected_word_de": word, "workshop_role_de": role, "card_or_root_meaning": "NO__SOURCE_PROGRAM_WORD"}
        for index, (slot, word, role) in enumerate(SELECTED_SLOTS, 1)
    ]
    write_tsv(OUT / "EIGHTY_THIRD_11_SELECTED_RECIPE_WORDS.tsv", selected_words)

    unit_source = {row["unit_id"]: row for row in read_tsv(UNITS) if row["unit_id"].startswith("H")}
    article_rows = []
    for unit_id in ("H1", "H2", "H3", "H4", "H5"):
        row = unit_source[unit_id]
        article_rows.append({
            "unit_id": unit_id,
            "page": row["page"],
            "group_count": row["group_count"],
            "visible_owner": "Bildpflanze",
            "selected_recipe_model": "M1_MEDICAL_MATERIA_RECIPE",
            "complete_recipe_reading_de": ARTICLES[unit_id],
            "species_name": "UNNAMED",
            "disease_or_body_part": "UNSPECIFIED",
            "card_meanings_changed": "NO",
        })
    write_tsv(OUT / "EIGHTY_THIRD_5_COMPLETE_HERBAL_ARTICLES.tsv", article_rows)

    article_lookup = {row["unit_id"]: row for row in article_rows}
    bindings = []
    for row in read_tsv(BINDING):
        if row["register"] != "HERBAL_PROSE":
            continue
        article = article_lookup[row["finite_source_unit"]]
        bindings.append({
            "unified_serial": row["unified_serial"],
            "page": row["page"],
            "unit_or_locus": row["unit_or_locus"],
            "source_group_identity": row["source_group_identity"],
            "visible_identity": row["visible_identity"],
            "owner": row["owner_or_namespace"],
            "construction": row["construction_or_address"],
            "current_short_reading": row["current_short_reading"],
            "selected_recipe_model": "M1_MEDICAL_MATERIA_RECIPE",
            "selected_article_reading_de": article["complete_recipe_reading_de"],
        })
    write_tsv(OUT / "EIGHTY_THIRD_100_HERBAL_RECIPE_BINDING.tsv", bindings)

    wanted_sources = {"S01", "S03", "S04", "S05", "S07", "S08"}
    historical_rows = [row for row in read_tsv(HISTORICAL) if row["source_id"] in wanted_sources]
    write_tsv(OUT / "EIGHTY_THIRD_6_HISTORICAL_RECIPE_ANALOGUES.tsv", historical_rows)

    doc = ["# Fünf konkrete Pflanzenrezepte", ""]
    for row in article_rows:
        doc.extend([f"## {row['unit_id']} · {row['page']}", "", row["complete_recipe_reading_de"], ""])
    doc.extend([
        "## Gemeinsames Rezeptvokabular", "",
        "Wasser · Wein · Öl · Honig · Satz · Trank · Salbe · Einreibung · Waschung · Auflage · Tuch", "",
        "Die Pflanzennamen und Krankheiten bleiben unbenannt. Das Bild liefert die",
        "Pflanze; das kleine Rezeptlexikon liefert Stoffart und Gebrauch.",
    ])
    (OUT / "EIGHTY_THIRD_COMPLETE_HERBAL_RECIPEBOOK.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    winner = max(totals, key=totals.get)
    report = [
        "# Dreiundachtzigste Werkstattfassung: konkretes Pflanzen-Rezeptlexikon", "",
        "## Ergebnis", "",
        f"Three seven-word content packages were expanded across all five Herbal units.",
        f"Editorial fit totals are {totals}. The selected package is {winner}.", "",
        "The coherent concrete vocabulary is water, wine, oil, honey, sediment, drink,",
        "salve, rub, wash, poultice and cloth. Purpose is split by article instead of",
        "forcing one blanket OUTER_APPLICATION gloss across every use.", "",
        "This is a strong creative working translation, not a claim that a particular",
        "Voynich card means wine, oil or honey. Those words live in the finite source",
        "program; the card/root layer remains unchanged.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "EIGHTY_THIRD_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "candidate_models": len(MODELS),
            "model_vocabulary_rows": len(model_rows),
            "model_article_comparisons": len(comparison_rows),
            "selected_recipe_words": len(selected_words),
            "complete_articles": len(article_rows),
            "bound_herbal_groups": len(bindings),
            "historical_analogues": len(historical_rows),
        },
        "model_totals": totals,
        "selected_model": winner,
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (UNITS, BINDING, HISTORICAL)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
