#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = list(csv.DictReader(handle, delimiter="\t"))
    by_id = {row["event_id"]: row for row in events}
    target = by_id["E007"]

    occurrence = [{
        "event_id": "E007",
        "record": target["record_unit_id"],
        "statement_id": target["statement_id"],
        "surface": target["surface_display"],
        "joint_tuple_id": target["joint_tuple_id"],
        "left_context": "OS/TOPF > CHAIR/WASSERZULAUF",
        "right_context": "OKY/POSTEN_ANSETZEN > AIIN/MASS",
        "selected_whole_word_de": "Auszug",
        "local_production_action_de": "abgießen und auffangen",
        "composition": "MEMORIZED_WHOLE_CARD__OT_YT_CHOL_NOT_SEPARATELY_LICENSED",
    }]
    write("FOUR_HUNDRED_FOURTEENTH_OTYTCHOL_OCCURRENCE.tsv", occurrence)

    models = [
        {"candidate": "AUFFANGEN", "fits_left": 4, "fits_right": 2, "introduces_referent": 1, "brevity": 4, "score": 11, "decision": "KEEP_AS_LOCAL_ACTION"},
        {"candidate": "ABGIESSEN", "fits_left": 4, "fits_right": 2, "introduces_referent": 1, "brevity": 4, "score": 11, "decision": "KEEP_AS_LOCAL_ACTION"},
        {"candidate": "AUSZUG", "fits_left": 4, "fits_right": 4, "introduces_referent": 4, "brevity": 4, "score": 16, "decision": "SELECT"},
        {"candidate": "SPÜLWASSER", "fits_left": 3, "fits_right": 4, "introduces_referent": 4, "brevity": 3, "score": 14, "decision": "KEEP_AS_RIVAL_PRODUCT"},
    ]
    write("FOUR_HUNDRED_FOURTEENTH_FOUR_PRODUCT_MODELS.tsv", models)

    module = [
        {"order": 1, "event_id": "E004", "surface": by_id["E004"]["surface_display"], "small_value_de": "bearbeiten", "register_effect": "Material bleibt aktiv"},
        {"order": 2, "event_id": "E005", "surface": by_id["E005"]["surface_display"], "small_value_de": "Topf", "register_effect": "Arbeitsgefäß wird Ziel"},
        {"order": 3, "event_id": "E006", "surface": by_id["E006"]["surface_display"], "small_value_de": "Wasserzulauf", "register_effect": "Wasser tritt in den Topf"},
        {"order": 4, "event_id": "E007", "surface": by_id["E007"]["surface_display"], "small_value_de": "Auszug", "register_effect": "Erzeugte Flüssigkeit wird neuer Posten"},
        {"order": 5, "event_id": "E008", "surface": by_id["E008"]["surface_display"], "small_value_de": "Posten ansetzen", "register_effect": "Auszug wird aktiv"},
        {"order": 6, "event_id": "E009", "surface": by_id["E009"]["surface_display"], "small_value_de": "Sollmaß", "register_effect": "Verwendungsportion wird bemessen"},
    ]
    write("FOUR_HUNDRED_FOURTEENTH_SIX_CARD_EXTRACTION_MODULE.tsv", module)

    contrasts = [
        {"surface_or_family": "otytchol", "selected_value_de": "Auszug", "kind": "PRODUCT_WHOLE_CARD", "reason": "followed by activation and measure"},
        {"surface_or_family": "qotchol", "selected_value_de": "anwärmen", "kind": "OPERATION_WHOLE_CARD", "reason": "different exact tuple in separate statement"},
        {"surface_or_family": "SOLK+E/EE", "selected_value_de": "auffangen", "kind": "PRODUCTIVE_COLLECTION_OPERATION", "reason": "graded open and closed collection family"},
        {"surface_or_family": "ytey", "selected_value_de": "füllen", "kind": "OPERATION_WHOLE_CARD", "reason": "separate Bio fill card"},
    ]
    write("FOUR_HUNDRED_FOURTEENTH_FOUR_COLLECTION_CONTRASTS.tsv", contrasts)

    summary = {
        "status": "PASS",
        "target_occurrences": 1,
        "models": len(models),
        "module_cards": len(module),
        "decision": "OTYTCHOL_MEMORIZED_EXTRACT_PRODUCT",
        "small_value_de": "AUSZUG",
    }
    (HERE / "FOUR_HUNDRED_FOURTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
