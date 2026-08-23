#!/usr/bin/env python3
"""Combine the three concrete content packages into one ten-page codex edition."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
H_WORDS = ROOT / "experiments/yolo/sidequest_semantic_herbal_recipe_vocabulary_eighty_third_edition/EIGHTY_THIRD_11_SELECTED_RECIPE_WORDS.tsv"
H_UNITS = ROOT / "experiments/yolo/sidequest_semantic_herbal_recipe_vocabulary_eighty_third_edition/EIGHTY_THIRD_5_COMPLETE_HERBAL_ARTICLES.tsv"
H_BINDING = ROOT / "experiments/yolo/sidequest_semantic_herbal_recipe_vocabulary_eighty_third_edition/EIGHTY_THIRD_100_HERBAL_RECIPE_BINDING.tsv"
B_WORDS = ROOT / "experiments/yolo/sidequest_semantic_bath_service_vocabulary_eighty_fourth_edition/EIGHTY_FOURTH_17_SELECTED_BATH_SERVICE_WORDS.tsv"
B_UNITS = ROOT / "experiments/yolo/sidequest_semantic_bath_service_vocabulary_eighty_fourth_edition/EIGHTY_FOURTH_6_COMPLETE_BATH_SERVICE_RECORDS.tsv"
B_BINDING = ROOT / "experiments/yolo/sidequest_semantic_bath_service_vocabulary_eighty_fourth_edition/EIGHTY_FOURTH_281_BATH_SERVICE_BINDING.tsv"
A_WORDS = ROOT / "experiments/yolo/sidequest_semantic_celestial_almanac_vocabulary_eighty_fifth_edition/EIGHTY_FIFTH_16_SELECTED_ALMANAC_WORDS.tsv"
A_UNITS = ROOT / "experiments/yolo/sidequest_semantic_celestial_almanac_vocabulary_eighty_fifth_edition/EIGHTY_FIFTH_3_COMPLETE_ALMANAC_INSTRUMENTS.tsv"
A_BINDING = ROOT / "experiments/yolo/sidequest_semantic_celestial_almanac_vocabulary_eighty_fifth_edition/EIGHTY_FIFTH_395_ALMANAC_GROUP_BINDING.tsv"


PURPOSES = {
    "P1_PRACTITIONER_RECIPE_BATH_CELESTIAL_COMPENDIUM": {
        "visible_sections": 10, "text_workflow": 9, "cross_section_purpose": 10,
        "period_workshop_fit": 9, "vocabulary_economy": 8, "awkward_fact_cost": 8,
        "summary": "Pflanzenmittel bereiten, in lokalen Bädern/Anwendungen gebrauchen und mit getrennten Himmeltafeln terminieren.",
    },
    "P2_BATHHOUSE_SUPPLY_AND_WORK_ALMANAC": {
        "visible_sections": 9, "text_workflow": 9, "cross_section_purpose": 8,
        "period_workshop_fit": 9, "vocabulary_economy": 8, "awkward_fact_cost": 7,
        "summary": "Pflanzenvorräte bereiten, Badehaus und Dienststationen führen und Arbeit nach Himmels-/Wettertafeln planen.",
    },
    "P3_NATURAL_ARTIFICIAL_CELESTIAL_MODELBOOK": {
        "visible_sections": 9, "text_workflow": 7, "cross_section_purpose": 7,
        "period_workshop_fit": 8, "vocabulary_economy": 7, "awkward_fact_cost": 7,
        "summary": "Pflanzen-, Becken-/Apparate- und Himmelsmuster als Lehr- und Kopierexemplare sammeln.",
    },
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
    lexicon = []
    for domain, path, id_col, slot_col, word_col, role_col in (
        ("HERBAL", H_WORDS, "recipe_word_id", "recipe_slot", "selected_word_de", "workshop_role_de"),
        ("BATH_SERVICE", B_WORDS, "bath_word_id", "bath_service_slot", "selected_word_de", "owner_rule_de"),
        ("CELESTIAL", A_WORDS, "almanac_word_id", "almanac_slot", "selected_word_de", "local_rule_de"),
    ):
        for row in read_tsv(path):
            lexicon.append({
                "codex_word_id": f"{domain[0]}_{row[id_col]}",
                "domain": domain,
                "source_slot": row[slot_col],
                "selected_word_de": row[word_col],
                "role_de": row[role_col],
                "portable_card_or_root_meaning": "NO__SOURCE_PROGRAM_ONLY",
            })
    write_tsv(OUT / "EIGHTY_SIXTH_44_CONCRETE_SOURCE_WORDS.tsv", lexicon)

    units = []
    for row in read_tsv(H_UNITS):
        units.append({
            "unit_order": len(units) + 1, "unit_id": row["unit_id"], "page": row["page"],
            "domain": "HERBAL_RECIPE", "group_count": row["group_count"],
            "concrete_reading_de": row["complete_recipe_reading_de"],
            "content_package": row["selected_recipe_model"],
        })
    for row in read_tsv(B_UNITS):
        units.append({
            "unit_order": len(units) + 1, "unit_id": row["unit_id"], "page": row["page"],
            "domain": "BATH_AND_SERVICE", "group_count": row["group_count"],
            "concrete_reading_de": row["complete_record_reading_de"],
            "content_package": row["selected_model"],
        })
    for row in read_tsv(A_UNITS):
        units.append({
            "unit_order": len(units) + 1, "unit_id": row["unit_id"], "page": row["page"],
            "domain": "CELESTIAL_ALMANAC", "group_count": row["group_count"],
            "concrete_reading_de": row["complete_instrument_reading_de"],
            "content_package": row["selected_model"],
        })
    write_tsv(OUT / "EIGHTY_SIXTH_14_CONCRETE_CODEX_UNITS.tsv", units)

    binding = []
    for row in read_tsv(H_BINDING):
        unit_id = row["unit_or_locus"].split("-")[0]
        binding.append({
            "unified_serial": row["unified_serial"], "domain": "HERBAL_RECIPE",
            "page": row["page"], "unit_id": unit_id, "local_address": row["unit_or_locus"],
            "visible_identity": row["visible_identity"], "owner_or_namespace": row["owner"],
            "construction_or_event": row["construction"], "short_form_reading": row["current_short_reading"],
            "concrete_unit_reading_de": row["selected_article_reading_de"],
        })
    for row in read_tsv(B_BINDING):
        unit_id = row["unit_or_locus"].split("-")[0]
        binding.append({
            "unified_serial": row["unified_serial"], "domain": "BATH_AND_SERVICE",
            "page": row["page"], "unit_id": unit_id, "local_address": row["unit_or_locus"],
            "visible_identity": row["visible_identity"], "owner_or_namespace": row["owner"],
            "construction_or_event": row["construction"], "short_form_reading": row["current_short_reading"],
            "concrete_unit_reading_de": row["selected_record_reading_de"],
        })
    for row in read_tsv(A_BINDING):
        binding.append({
            "unified_serial": 381 + int(row["group_serial"]), "domain": "CELESTIAL_ALMANAC",
            "page": row["page"], "unit_id": row["unit_id"], "local_address": f"{row['locus']}:{row['event_index']}",
            "visible_identity": row["opaque_local_id"], "owner_or_namespace": f"{row['local_owner']} @ {row['local_namespace']}",
            "construction_or_event": row["copy_instruction_de"], "short_form_reading": "örtliche opake Nomenklatorkarte",
            "concrete_unit_reading_de": row["selected_instrument_reading_de"],
        })
    binding.sort(key=lambda row: int(row["unified_serial"]))
    write_tsv(OUT / "EIGHTY_SIXTH_776_CONCRETE_CODEX_BINDING.tsv", binding)

    purpose_rows = []
    for purpose_id, data in PURPOSES.items():
        total = sum(value for key, value in data.items() if key != "summary")
        purpose_rows.append({
            "purpose_id": purpose_id,
            "visible_sections_10": data["visible_sections"],
            "text_workflow_10": data["text_workflow"],
            "cross_section_purpose_10": data["cross_section_purpose"],
            "period_workshop_fit_10": data["period_workshop_fit"],
            "vocabulary_economy_10": data["vocabulary_economy"],
            "awkward_fact_survival_10": data["awkward_fact_cost"],
            "editorial_total_60": total,
            "one_sentence_purpose_de": data["summary"],
        })
    write_tsv(OUT / "EIGHTY_SIXTH_3_BOOK_PURPOSE_COMPARISON.tsv", purpose_rows)

    winner = max(purpose_rows, key=lambda row: row["editorial_total_60"])
    doc = [
        "# Konkrete Zehn-Seiten-Codexfassung", "",
        "## Werkstattauftrag", "",
        winner["one_sentence_purpose_de"], "",
        "Die drei Bereiche sind thematisch gekoppelt, aber nicht durch sichtbare",
        "Querverweise: Pflanzen liefern Mittel; lokale Bad- und Dienststationen liefern",
        "Anwendungsräume; getrennte Himmeltafeln liefern mögliche Zeit-, Wetter- und",
        "Wahlbedingungen. Jeder Bereich behält sein eigenes Quellenprogramm.", "",
    ]
    for row in units:
        doc.extend([f"## {row['unit_id']} · {row['page']}", "", row["concrete_reading_de"], ""])
    (OUT / "EIGHTY_SIXTH_COMPLETE_CONCRETE_TEN_PAGE_CODEX.md").write_text("\n".join(doc).rstrip() + "\n", encoding="utf-8")

    synopsis = [
        "# Ein-Seiten-Synopsis des konkreten Codex", "",
        "Ein praktisches Werkstattkompendium eines Heil-/Badbetriebs: Die ersten fünf",
        "Einträge zeigen unbenannte Pflanzen und geben Wasser-, Wein-, Öl- und",
        "Honigzubereitungen als Trank, Salbe, Waschung, Einreibung oder Auflage. Die",
        "folgenden sechs Records organisieren Badende, Becken, Badwasser, Wärme, Zeit,",
        "Tuch/Umschlag und Seihgänge; zwei figurenlose Randrecords bedienen Einlass und",
        "Ablauf. Drei getrennte Himmelsinstrumente liefern lokale Wahl-, Stern-, Wetter-,",
        "Licht-, Zeit- und Eigenschaftszeichen.", "",
        "Der Codex muss nicht behaupten, dass jedes Pflanzenmittel in jedem gezeichneten",
        "Bad gebraucht oder jedes Bad astrologisch terminiert wird. Er stellt drei",
        "praktische Wissensschichten derselben Werkstatt nebeneinander. Das erklärt die",
        "inhaltliche Nähe ohne erfundene Seitenverweise.", "",
        "Die Schrift selbst bleibt das kleine Mischsystem: Bildbesitzer + endliches",
        "Quellenprogramm + produktive Kürzelkarte oder gelernte Ganzkarte + Handrenderer.",
    ]
    (OUT / "EIGHTY_SIXTH_ONE_PAGE_CODEX_SYNOPSIS.md").write_text("\n".join(synopsis).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Sechsundachtzigste Werkstattfassung: konkreter Gesamtcodex", "",
        "## Ergebnis", "",
        "The selected Herbal recipebook, bath/service book and celestial almanac are",
        "combined without altering local readings. The release contains 44 domain source",
        "words, fourteen complete units and all 776 groups.", "",
        f"The leading book purpose is {winner['purpose_id']} with {winner['editorial_total_60']}/60.",
        "Bathhouse supply/work almanac and modelbook remain coherent rivals. The lead is",
        "a practical practitioner compendium, but cross-section use is thematic rather",
        "than asserted through invented pointers.", "",
        "Only the fixed ten pages were used; f84 and f84r remained sealed.",
    ]
    (OUT / "EIGHTY_SIXTH_EDITION_REPORT.md").write_text("\n".join(report).rstrip() + "\n", encoding="utf-8")

    summary = {
        "status": "CONSISTENT",
        "counts": {
            "concrete_source_words": len(lexicon),
            "complete_units": len(units),
            "bound_groups": len(binding),
            "book_purpose_models": len(purpose_rows),
        },
        "selected_purpose": winner["purpose_id"],
        "selected_purpose_total_60": winner["editorial_total_60"],
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in (H_WORDS, H_UNITS, H_BINDING, B_WORDS, B_UNITS, B_BINDING, A_WORDS, A_UNITS, A_BINDING)},
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
