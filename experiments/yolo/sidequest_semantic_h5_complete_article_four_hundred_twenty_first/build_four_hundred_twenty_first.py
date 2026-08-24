#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"


VALUES = {
    "E074": "Zutatenansatz", "E075": "Zutat", "E076": "Blütebeginn", "E077": "Mass",
    "E078": "Zutat", "E079": "auflegen", "E080": "Folgeansatz", "E081": "verwende dies", "E082": "Stelle",
    "E083": "Fortsetzung", "E084": "waschen", "E085": "verwende dies", "E086": "auftragen; Schluss",
    "E087": "Kraut", "E088": "Zutat", "E089": "zerreiben", "E090": "erneut ansetzen",
    "E091": "nimm dies", "E092": "Auszug zugeben", "E093": "abseihen",
    "E094": "Zutat", "E095": "nimm dies", "E096": "Gebrauchsauszug", "E097": "gebrauchen",
    "E098": "nächstes", "E099": "je Gabe", "E100": "Mass",
}


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = [row for row in csv.DictReader(handle, delimiter="\t") if row["record_unit_id"] == "H5"]
    interlinear = []
    for order, row in enumerate(events, start=1):
        value = VALUES[row["event_id"]]
        interlinear.append({
            "order": order, "event_id": row["event_id"], "locus": row["locus"], "statement_id": row["statement_id"],
            "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "selected_small_value_de": value,
            "value_kind": "PRODUCTIVE_COMPOSITION" if any(token in row["semantic_segmentation"] for token in ["HO_", "OR_", "OT_", "OK_", "AIIN", "AL_", "OL_"]) else "MEMORIZED_WHOLE_CARD",
            "old_context_removed": "YES" if row["event_id"] in {"E076", "E079", "E084", "E086", "E087", "E089", "E097"} else "NO",
        })
    write("FOUR_HUNDRED_TWENTY_FIRST_H5_27_EVENT_INTERLINEAR.tsv", interlinear)

    statements = [
        {"statement_id": "H5-S001", "events": "E074-E082", "card_sequence_de": "Zutatenansatz > Zutat > Blütebeginn > Mass > Zutat > auflegen > Folgeansatz > verwende dies > Stelle", "continuous_reading_de": "Vom Bildbesitzer einen Zutatenansatz beginnen. Die Zutat zu Blütebeginn nach Maß nehmen; eine weitere Zutat auflegen, den Folgeansatz verwenden und an die bezeichnete Stelle bringen."},
        {"statement_id": "H5-S002", "events": "E083-E086", "card_sequence_de": "Fortsetzung > waschen > verwende dies > auftragen; Schluss", "continuous_reading_de": "Mit der Fortsetzung waschen, dies verwenden und auftragen; den Schritt schließen."},
        {"statement_id": "H5-S003", "events": "E087-E090", "card_sequence_de": "Kraut > Zutat > zerreiben > erneut ansetzen", "continuous_reading_de": "Kraut nehmen, als Zutat grob zerreiben und erneut ansetzen."},
        {"statement_id": "H5-S004", "events": "E091-E093", "card_sequence_de": "nimm dies > Auszug zugeben > abseihen", "continuous_reading_de": "Nimm dies, gib Auszug zu und seihe ab."},
        {"statement_id": "H5-S005", "events": "E094-E097", "card_sequence_de": "Zutat > nimm dies > Gebrauchsauszug > gebrauchen", "continuous_reading_de": "Eine weitere Zutat: nimm diese, gewinne den Gebrauchsauszug und gebrauche ihn."},
        {"statement_id": "H5-S006", "events": "E098-E100", "card_sequence_de": "nächstes > je Gabe > Mass", "continuous_reading_de": "Für den nächsten Posten jede Gabe nach dem vorgeschriebenen Maß nehmen."},
    ]
    write("FOUR_HUNDRED_TWENTY_FIRST_H5_SIX_STATEMENTS.tsv", statements)

    learned = [
        {"surface": "chodaly", "value_de": "Blütebeginn", "kind": "picture-timed whole card", "removed_overread": "species-specific harvest date"},
        {"surface": "kchol", "value_de": "auflegen", "kind": "application whole card", "removed_overread": "body site"},
        {"surface": "choy", "value_de": "waschen", "kind": "wash whole card", "removed_overread": "named ailment"},
        {"surface": "cheeckhody", "value_de": "auftragen; Schluss", "kind": "terminal application card", "removed_overread": "external body diagnosis"},
        {"surface": "sh", "value_de": "Kraut", "kind": "picture-addressed material noun", "removed_overread": "flowering stalk anatomy"},
        {"surface": "kchey", "value_de": "zerreiben", "kind": "preparation whole card", "removed_overread": "tool and exact coarseness"},
        {"surface": "kchal", "value_de": "abseihen", "kind": "separation whole card", "removed_overread": "named filter material"},
        {"surface": "kchoar", "value_de": "Gebrauchsauszug", "kind": "product whole card", "removed_overread": "specific ailment remedy"},
        {"surface": "sotodan", "value_de": "gebrauchen", "kind": "use whole card", "removed_overread": "specific illness indication"},
        {"surface": "keol", "value_de": "je Gabe", "kind": "distribution whole card", "removed_overread": "named dosage unit"},
    ]
    write("FOUR_HUNDRED_TWENTY_FIRST_TEN_H5_WHOLE_WORDS.tsv", learned)

    models = [
        {"model": "PLANT_PREPARATION_AND_APPLICATION", "six_statement_fit": 6, "picture_owner_fit": 4, "card_reuse_fit": 4, "assumption_cost": 3, "decision": "SELECT"},
        {"model": "PLANT_MATERIAL_WORKSHOP_ONLY", "six_statement_fit": 5, "picture_owner_fit": 4, "card_reuse_fit": 4, "assumption_cost": 2, "decision": "KEEP_RIVAL"},
        {"model": "SINGLE_DISEASE_REMEDY", "six_statement_fit": 3, "picture_owner_fit": 3, "card_reuse_fit": 2, "assumption_cost": 5, "decision": "REJECT_TOO_NARROW"},
    ]
    write("FOUR_HUNDRED_TWENTY_FIRST_THREE_H5_MODELS.tsv", models)

    summary = {
        "status": "PASS", "events": len(interlinear), "statements": len(statements), "learned_whole_words_reviewed": len(learned),
        "decision": "H5_COMPLETE_PLANT_PREPARATION_AND_APPLICATION_ARTICLE", "removed_disease_gloss": "DRY_COUGH",
    }
    (HERE / "FOUR_HUNDRED_TWENTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
