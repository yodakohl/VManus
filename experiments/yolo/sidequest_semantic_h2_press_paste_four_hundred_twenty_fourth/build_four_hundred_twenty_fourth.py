#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"

VALUES = {
    "E015": "Spitzen", "E016": "bereit", "E017": "Ansatz", "E018": "zerstoßen", "E019": "abpressen",
    "E020": "dies A", "E021": "dies B", "E022": "Mass", "E023": "dies bemessene",
    "E024": "Folgeansatz", "E025": "Ansatz", "E026": "danach fortsetzen", "E027": "fortsetzen", "E028": "Fortsetzungsansatz", "E029": "fortsetzen", "E030": "Mass", "E031": "dasselbe",
    "E032": "glasiertes Gefäß", "E033": "Ansatz A", "E034": "Ansatz B", "E035": "dies", "E036": "weicher Sollstand", "E037": "dies", "E038": "Paste",
}


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = [row for row in csv.DictReader(handle, delimiter="\t") if row["record_unit_id"] == "H2"]
    interlinear = []
    for order, row in enumerate(events, start=1):
        event_id = row["event_id"]
        if event_id == "E020":
            register = "PRODUCT_A__LOCAL_PRESS_LIQUID_RIVAL"
        elif event_id == "E021":
            register = "PRODUCT_B__LOCAL_PRESS_RESIDUE_RIVAL"
        elif event_id == "E023":
            register = "MEASURED_SELECTED_PRODUCT"
        elif event_id == "E033":
            register = "PREPARATION_A_REJOIN"
        elif event_id == "E034":
            register = "PREPARATION_B_REJOIN"
        elif event_id == "E038":
            register = "FINAL_PRODUCT"
        else:
            register = "CURRENT_PROCESS"
        interlinear.append({
            "order": order, "event_id": event_id, "locus": row["locus"], "statement_id": row["statement_id"],
            "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "selected_small_value_de": VALUES[event_id], "product_register": register,
        })
    write("FOUR_HUNDRED_TWENTY_FOURTH_H2_24_EVENT_INTERLINEAR.tsv", interlinear)

    statements = [
        {"statement_id": "H2-S001", "events": "E015-E023", "card_sequence_de": "Spitzen > bereit > Ansatz > zerstoßen > abpressen > dies A > dies B > Mass > dies bemessene", "continuous_reading_de": "Die Spitzen bereitstellen, als Ansatz zerstoßen und abpressen. Die beiden Pressprodukte A und B getrennt führen; eines nach Maß abteilen und aktiv halten."},
        {"statement_id": "H2-S002", "events": "E024-E031", "card_sequence_de": "Folgeansatz > Ansatz > danach fortsetzen > fortsetzen > Fortsetzungsansatz > fortsetzen > Mass > dasselbe", "continuous_reading_de": "Mit Folgeansatz und Ansatz beide Arbeitswege weiterführen, den Fortsetzungsansatz bemessen und denselben Bestand in den nächsten Schritt tragen."},
        {"statement_id": "H2-S003", "events": "E032-E038", "card_sequence_de": "glasiertes Gefäß > Ansatz A > Ansatz B > dies > weicher Sollstand > dies > Paste", "continuous_reading_de": "Beide Ansätze im glasierten Gefäß zusammenbringen, die Mischung auf weichen Sollstand bringen und als Paste abnehmen."},
    ]
    write("FOUR_HUNDRED_TWENTY_FOURTH_H2_THREE_STATEMENTS.tsv", statements)

    graph = [
        {"step": 1, "node_or_edge": "INPUT", "value": "Spitzen", "from": "picture owner", "to": "Ansatz"},
        {"step": 2, "node_or_edge": "OPERATION", "value": "zerstoßen", "from": "Ansatz", "to": "crushed material"},
        {"step": 3, "node_or_edge": "SPLIT", "value": "abpressen", "from": "crushed material", "to": "PRODUCT_A|PRODUCT_B"},
        {"step": 4, "node_or_edge": "BRANCH_A", "value": "dies A; Mass", "from": "PRODUCT_A", "to": "PREPARATION_A"},
        {"step": 5, "node_or_edge": "BRANCH_B", "value": "dies B; Fortsetzung", "from": "PRODUCT_B", "to": "PREPARATION_B"},
        {"step": 6, "node_or_edge": "REJOIN", "value": "Ansatz A + Ansatz B", "from": "PREPARATION_A|PREPARATION_B", "to": "glazed vessel mixture"},
        {"step": 7, "node_or_edge": "SETTING", "value": "weicher Sollstand", "from": "glazed vessel mixture", "to": "Paste"},
    ]
    write("FOUR_HUNDRED_TWENTY_FOURTH_H2_SPLIT_REJOIN_GRAPH.tsv", graph)

    product_models = [
        {"final_card": "CHODAIIN", "candidate": "GESCHWÜR", "process_fit": 1, "image_need": 4, "brevity": 4, "score": 9, "decision": "REJECT_OLD_INDICATION_OVERREAD"},
        {"final_card": "CHODAIIN", "candidate": "SALBE", "process_fit": 4, "image_need": 2, "brevity": 4, "score": 10, "decision": "KEEP_MEDICAL_RIVAL"},
        {"final_card": "CHODAIIN", "candidate": "PASTE", "process_fit": 4, "image_need": 1, "brevity": 4, "score": 11, "decision": "SELECT"},
        {"final_card": "CHODAIIN", "candidate": "PRESSKUCHEN", "process_fit": 2, "image_need": 1, "brevity": 3, "score": 6, "decision": "REJECT_REJOIN_CONFLICT"},
    ]
    write("FOUR_HUNDRED_TWENTY_FOURTH_FOUR_FINAL_PRODUCT_MODELS.tsv", product_models)

    comparison = [
        {"record": "H2", "branch_mechanism": "press split", "held_items": 2, "recall_mechanism": "parallel continuation", "rejoin": "two adjacent OR preparations", "final_product": "Paste"},
        {"record": "H3", "branch_mechanism": "reserve one portion", "held_items": 1, "recall_mechanism": "Reserve nehmen card", "rejoin": "none explicit; second product remains separate", "final_product": "Klarauszug and later Trank"},
    ]
    write("FOUR_HUNDRED_TWENTY_FOURTH_H2_H3_MULTIPRODUCT_COMPARISON.tsv", comparison)

    summary = {
        "status": "PASS", "events": len(interlinear), "statements": len(statements), "graph_steps": len(graph),
        "decision": "H2_PRESS_SPLIT_PARALLEL_CONTINUATION_REJOIN_TO_PASTE",
        "portable_commonality_with_H3": "MULTIPRODUCT_REGISTER_NOT_IDENTICAL_BRANCH_CARD",
    }
    (HERE / "FOUR_HUNDRED_TWENTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
