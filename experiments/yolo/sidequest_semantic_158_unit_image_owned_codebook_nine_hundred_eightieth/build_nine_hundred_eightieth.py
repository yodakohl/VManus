#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P971 = ROOT / "experiments/yolo/sidequest_semantic_canonical_compact_workshop_edition_nine_hundred_seventy_first"
P972 = ROOT / "experiments/yolo/sidequest_semantic_visual_material_owner_revision_nine_hundred_seventy_second"
P975 = ROOT / "experiments/yolo/sidequest_semantic_specialist_whole_card_drawer_nine_hundred_seventy_fifth"
P976 = ROOT / "experiments/yolo/sidequest_semantic_three_layer_apprentice_lexicon_nine_hundred_seventy_sixth"
P979 = ROOT / "experiments/yolo/sidequest_semantic_f13r_root_crown_article_nine_hundred_seventy_ninth"


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base = read(P976 / "PASS976_137_TEACHING_UNIT_LEXICON.tsv")
    base_fields = list(base[0])
    local_source = [r for r in read(P979 / "PASS979_F13R_77_EVENT_ROOT_CROWN_EDITION.tsv") if r["local_visual_headword_de"] != "NONE"]
    label_source = read(P972 / "PASS972_F88R_SIXTEEN_LABEL_OWNER_MAP.tsv")

    local_rows = []
    for index, row in enumerate(local_source, 1):
        local_rows.append({
            "teaching_unit_id": f"L{index:03d}",
            "layer": "F_IMAGE_OWNED_SPECIALIST_CARD",
            "unit_type": "MEMORIZED_VISUAL_WHOLE_CARD",
            "recognition_forms": row["surface"],
            "spoken_value_de": row["local_visual_headword_de"],
            "concrete_context_values_de": row["image_owned_expansion_de"],
            "specialist_surface_forms": row["surface"],
            "observed_specialist_events": "1",
            "pages": "f13r",
            "teaching_rule_de": "Als Bildteilkarte dieses Pflanzenartikels lernen; gemeinsame Wurzeln bleiben Merkhilfe.",
        })
    label_rows = []
    for index, row in enumerate(label_source, 1):
        label_rows.append({
            "teaching_unit_id": f"D{index:03d}",
            "layer": "G_DRUG_LABEL_NOMENCLATOR",
            "unit_type": "MEMORIZED_DRUG_LABEL",
            "recognition_forms": row["surface"],
            "spoken_value_de": row["visual_object_id"],
            "concrete_context_values_de": row["visible_object_de"],
            "specialist_surface_forms": row["surface"],
            "observed_specialist_events": "1",
            "pages": "f88r",
            "teaching_rule_de": "Als Name/Klassencode des unmittelbar benachbarten sichtbaren Drogenpostens lernen; nicht zerlegen.",
        })
    lexicon = base + local_rows + label_rows
    write(HERE / "PASS980_158_TEACHING_UNIT_CODEBOOK.tsv", lexicon, base_fields)

    all_events = read(P975 / "PASS975_2511_EVENT_HYBRID_EDITION.tsv")
    unit_by_id = {r["teaching_unit_id"]: r for r in lexicon}
    common_units = [r for r in base if r["unit_type"] in {"ROOT_OR_LOCAL_SIGN", "FORMULA_CARD"}]
    root_by_form = {r["recognition_forms"]: r["teaching_unit_id"] for r in common_units if r["unit_type"] == "ROOT_OR_LOCAL_SIGN"}
    specialist_by_value = {r["spoken_value_de"].casefold(): r["teaching_unit_id"] for r in base if r["teaching_unit_id"].startswith("W")}
    specialist_by_value.update({"auffangen": "R-SOLK", "befestigen": "R-LD", "zusatz": "R-AN"})
    local_by_event = {r["event_id"]: f"L{index:03d}" for index, r in enumerate(local_source, 1)}
    label_by_event = {r["event_id"]: f"D{index:03d}" for index, r in enumerate(label_source, 1)}

    bindings = []
    counts = {}
    for event in all_events:
        if event["compact_layer"] == "LEARNED_FORMULA_CARD":
            mnemonic_ids = [event["formula_card_id"]]
        else:
            mnemonic_ids = [root_by_form[part] for part in event["component_recipe"].split("+")]
        if event["event_id"] in label_by_event:
            primary_layer = "DRUG_LABEL_NOMENCLATOR"
            primary_ids = [label_by_event[event["event_id"]]]
            mnemonic = []
            reading = unit_by_id[primary_ids[0]]["concrete_context_values_de"]
        elif event["event_id"] in local_by_event:
            primary_layer = "IMAGE_OWNED_SPECIALIST_CARD"
            primary_ids = [local_by_event[event["event_id"]]]
            mnemonic = mnemonic_ids
            reading = unit_by_id[primary_ids[0]]["concrete_context_values_de"]
        elif event["specialist_headword_de"]:
            primary_layer = "MEMORIZED_SPECIALIST_WHOLE_WORD"
            primary_ids = [specialist_by_value[event["specialist_headword_de"].casefold()]]
            mnemonic = mnemonic_ids
            reading = event["specialist_context_expansion_de"]
        elif event["compact_layer"] == "LOCAL_NOMENCLATOR_OR_ADDRESS":
            primary_layer = "LOCAL_ADDRESS_COMPOSITION"
            primary_ids = mnemonic_ids
            mnemonic = []
            reading = event["hybrid_working_reading_de"]
        elif event["compact_layer"] == "LEARNED_FORMULA_CARD":
            primary_layer = "COMMON_FORMULA_CARD"
            primary_ids = mnemonic_ids
            mnemonic = []
            reading = event["hybrid_working_reading_de"]
        else:
            primary_layer = "PRODUCTIVE_ROOT_COMPOSITION"
            primary_ids = mnemonic_ids
            mnemonic = []
            reading = event["hybrid_working_reading_de"]
        counts[primary_layer] = counts.get(primary_layer, 0) + 1
        bindings.append({
            "event_id": event["event_id"],
            "physical_page": event["physical_page"],
            "locus": event["locus"],
            "surface": event["surface"],
            "component_recipe": event["component_recipe"],
            "primary_layer": primary_layer,
            "primary_teaching_unit_ids": "|".join(primary_ids),
            "mnemonic_common_unit_ids": "|".join(mnemonic),
            "complete_working_reading_de": reading,
        })
    write(HERE / "PASS980_2511_EVENT_TEACHING_BINDING.tsv", bindings, list(bindings[0]))

    lines = [
        "# Pass 980 — das 158-Einheiten-Werkstattcodebuch",
        "",
        "## Was der Lehrling lernt",
        "",
        "- 86 gemeinsame Wurzeln, Formelkarten und lokale Zeichen;",
        "- 51 ältere Fachwort-Einheiten;",
        "- 5 Bildteilkarten für den neuen f13r-Artikel;",
        "- 16 Drogenetiketten für die drei f88r-Gefäßfächer.",
        "",
        "Gesamt: **158 gelernte Einheiten**. Jede der 2.511 sichtbaren Gruppen hat",
        "genau einen primären Lesekanal. Ein lokales Ganzwort darf sichtbare Wurzeln",
        "als Eselsbrücke behalten, wird aber nicht aus ihnen neu übersetzt.",
        "",
        "## Ereignisverteilung",
        "",
    ]
    for layer, count in sorted(counts.items()):
        lines.append(f"- {layer}: {count}")
    lines += [
        "",
        "## Schreibregel",
        "",
        "> Zuerst Bild oder Diagrammplatz bestimmen. Dann prüfen, ob die Karte ein",
        "> gelerntes Fachwort/Etikett ist. Nur wenn nicht, die gemeinsame Formel oder",
        "> ihre Wurzeln lesen. Positionshüllen verändern die Bedeutung nicht.",
        "",
        "Dieses Modell ist klein genug für eine Werkstatt mit mehreren Schreibern,",
        "aber groß genug, um WURZEL, TUCH, KLARLAUF, DÜSE und einzelne Drogenposten",
        "als echte Fachwörter statt als überdehnte Satzkompositionen zu behandeln.",
        "",
    ]
    (HERE / "PASS980_WORKSHOP_CODEBOOK_REPORT.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "status": "PASS",
        "teaching_units": len(lexicon),
        "events": len(bindings),
        "primary_layer_counts": counts,
    }
    (HERE / "PASS980_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
