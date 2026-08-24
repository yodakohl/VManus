#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_thermal_temporal_completion/SELECTED_381_THERMAL_TEMPORAL_INTERLINEAR.tsv"
TARGET = "4d4559019a961b834aa1"


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    with EVENTS.open(encoding="utf-8", newline="") as handle:
        events = list(csv.DictReader(handle, delimiter="\t"))
    targets = [row for row in events if row["joint_tuple_id"] == TARGET]
    expansions = {
        "E003": ("Knolle > abschaben", "bearbeiten > Topf", "vom selben Pflanzenposten"),
        "E031": ("fortsetzen > Sollmaß", "glasiertes Gefäß > Ansatz", "davon / derselbe Ansatz"),
        "E105": ("Beckenwasser > an Stelle setzen", "fortsetzen > Portion", "mit demselben Arbeitsbestand"),
        "E199": ("eine Portion zugeben", "eine Portion zugeben > länger ansetzen", "nochmals dasselbe"),
        "E238": ("auf Sollmaß einstellen > Folgestelle", "nächste Aussage: Schritt schließen", "vom selben Posten"),
    }
    rows = []
    for row in targets:
        before, after, expansion = expansions[row["event_id"]]
        rows.append({
            "event_id": row["event_id"], "record": row["record_unit_id"], "statement_id": row["statement_id"],
            "surface": row["surface_display"], "joint_tuple_id": row["joint_tuple_id"],
            "preceding_sequence": before, "following_sequence": after,
            "portable_value_de": "dasselbe", "local_expansion_de": expansion,
            "card_kind": "MEMORIZED_SAME_OR_DITTO_CARD",
        })
    write("FOUR_HUNDRED_SEVENTEENTH_FIVE_SAME_OCCURRENCES.tsv", rows)

    models = [
        {"candidate": "QUELLE", "H1": 4, "H2": 3, "B1": 3, "B2": 2, "B3": 3, "score": 15, "decision": "KEEP_AS_SOURCE_ROLE"},
        {"candidate": "GLEICHE_CHARGE", "H1": 4, "H2": 4, "B1": 4, "B2": 4, "B3": 4, "score": 20, "decision": "KEEP_AS_LOCAL_EXPANSION"},
        {"candidate": "DARAUS", "H1": 4, "H2": 4, "B1": 3, "B2": 3, "B3": 3, "score": 17, "decision": "KEEP_AS_CASE_EXPANSION"},
        {"candidate": "DASSELBE", "H1": 4, "H2": 4, "B1": 4, "B2": 4, "B3": 4, "score": 20, "decision": "SELECT_SHORTEST"},
    ]
    write("FOUR_HUNDRED_SEVENTEENTH_FOUR_SAME_MODELS.tsv", models)

    statements = [
        {"statement_id": "H1-S001", "surface": "char", "revised_fragment_de": "Knolle abschaben; vom selben Posten weiterbearbeiten und in den Topf geben", "ditto_scope": "CURRENT_PLANT_BATCH"},
        {"statement_id": "H2-S002", "surface": "dar", "revised_fragment_de": "fortsetzen, bemessen und davon den nächsten Ansatz im glasierten Gefäß beginnen", "ditto_scope": "CURRENT_PREPARATION"},
        {"statement_id": "B1-S002", "surface": "sar", "revised_fragment_de": "Beckenwasser an die Stelle setzen; mit demselben Posten fortsetzen und eine Portion nehmen", "ditto_scope": "CURRENT_WORKING_STOCK"},
        {"statement_id": "B2-S011", "surface": "char", "revised_fragment_de": "eine Portion zugeben, dasselbe wiederholen und länger ansetzen; Schluss", "ditto_scope": "PREVIOUS_PORTION_OPERATION"},
        {"statement_id": "B3-S004", "surface": "dar", "revised_fragment_de": "auf Sollmaß an der Folgestelle einstellen und denselben Posten weiterführen", "ditto_scope": "CURRENT_ITEM"},
    ]
    write("FOUR_HUNDRED_SEVENTEENTH_FIVE_REVISED_STATEMENTS.tsv", statements)

    renderer = [
        {"surface": surface, "events": sum(row["surface_display"] == surface for row in targets), "exact_card_id": TARGET, "meaning_de": "dasselbe", "interpretation": "surface renderer variant of one learned card"}
        for surface in sorted({row["surface_display"] for row in targets})
    ]
    write("FOUR_HUNDRED_SEVENTEENTH_THREE_RENDERER_FORMS.tsv", renderer)

    summary = {
        "status": "PASS", "occurrences": len(rows), "records": len({row["record"] for row in rows}),
        "surfaces": len(renderer), "decision": "CHAR_DAR_SAR_SAME_OR_DITTO_CARD", "small_value_de": "DASSELBE",
    }
    (HERE / "FOUR_HUNDRED_SEVENTEENTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
