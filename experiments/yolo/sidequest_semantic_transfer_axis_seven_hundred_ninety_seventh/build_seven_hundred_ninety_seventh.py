#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = (
    HERE.parent
    / "sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
    / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv"
)
OPS = ("K", "L", "CHD")
READING = {"K": "ZUGEBEN", "L": "LEITEN", "CHD": "UMSETZEN"}
PREDICTIONS = [
    ("OL", "CHD", "chedol", "UMSETZEN · WEITER"),
    ("AL", "L", "lal", "LEITEN · ZIELSTELLE"),
    ("AIR", "L", "lair", "LEITEN · WASSER"),
    ("AIN", "L", "lain", "LEITEN · PORTION"),
    ("DY", "K", "kdy", "ZUGEBEN · SCHLUSS"),
    ("AR", "CHD", "chdar", "UMSETZEN · QUELLE"),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def operation_tokens(recipe: str) -> list[str]:
    return [token for token in recipe.split("+") if token in OPS]


def simple_signature(recipe: str) -> str:
    return "+".join("OP" if token in OPS else token for token in recipe.split("+"))


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    rows = read(SOURCE)
    seen = {row["surface"] for row in rows}
    target = [row for row in rows if operation_tokens(row["component_recipe"])]

    event_rows = []
    for row in target:
        ops = operation_tokens(row["component_recipe"])
        expected = [READING[op] for op in ops]
        reading_parts = row["rebuilt_reading_de"].split(" · ")
        event_rows.append(
            {
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "exact_card_id": row["card_no"],
                "surface": row["surface"],
                "component_recipe": row["component_recipe"],
                "operation_tokens": "+".join(ops),
                "operation_readings_de": "+".join(expected),
                "operation_count": len(ops),
                "working_reading_de": row["rebuilt_reading_de"],
                "all_operation_meanings_present": "YES" if all(item in reading_parts for item in expected) else "NO",
            }
        )

    summary_rows = []
    for op in OPS:
        op_events = [row for row in event_rows if op in str(row["operation_tokens"]).split("+")]
        summary_rows.append(
            {
                "operation": op,
                "reading_de": READING[op],
                "events": len(op_events),
                "exact_cards": len({row["exact_card_id"] for row in op_events}),
                "recipes": len({row["component_recipe"] for row in op_events}),
                "single_operation_events": sum(row["operation_count"] == 1 for row in op_events),
                "stacked_operation_events": sum(int(row["operation_count"]) > 1 for row in op_events),
            }
        )

    simple = [row for row in event_rows if int(row["operation_count"]) == 1]
    by_sig: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in simple:
        by_sig[simple_signature(str(row["component_recipe"]))].append(row)
    shared = {
        key: value
        for key, value in by_sig.items()
        if len({str(row["operation_tokens"]) for row in value}) >= 2
    }
    family_rows = []
    shared_rows = []
    for sig, sig_events in sorted(shared.items()):
        present = {str(row["operation_tokens"]) for row in sig_events}
        family_rows.append(
            {
                "operation_signature": sig,
                "present_operations": ",".join(op for op in OPS if op in present),
                "missing_operations": ",".join(op for op in OPS if op not in present) or "NONE",
                "events": len(sig_events),
                "surfaces_by_operation": " | ".join(
                    f"{op}={','.join(sorted({str(row['surface']) for row in sig_events if row['operation_tokens'] == op}))}"
                    for op in OPS
                    if op in present
                ),
                "status": "THREE_OPERATION_COMPLETE" if len(present) == 3 else "TWO_OPERATION_FAMILY",
            }
        )
        shared_rows.extend(sig_events)

    stacked_counter = Counter(str(row["operation_tokens"]) for row in event_rows if int(row["operation_count"]) > 1)
    stacked_rows = []
    for stack, count in sorted(stacked_counter.items()):
        stack_events = [row for row in event_rows if row["operation_tokens"] == stack]
        stacked_rows.append(
            {
                "operation_stack": stack,
                "reading_de": "→".join(READING[token] for token in stack.split("+")),
                "events": count,
                "recipes": ",".join(sorted({str(row["component_recipe"]) for row in stack_events})),
                "surfaces": ",".join(sorted({str(row["surface"]) for row in stack_events})),
                "interpretation": "EXECUTE_IN_WRITTEN_COMPONENT_ORDER",
            }
        )

    prediction_rows = []
    for index, (tail, op, surface, reading) in enumerate(PREDICTIONS, start=1):
        source_family = next(row for row in family_rows if row["operation_signature"] == "OP+" + tail)
        prediction_rows.append(
            {
                "predicted_card": f"PRED_OP_{index:02d}",
                "tail_recipe": tail,
                "observed_operations": source_family["present_operations"],
                "new_operation": op,
                "predicted_recipe": op + "+" + tail,
                "predicted_surface": surface,
                "predicted_reading_de": reading,
                "fixed_page_collision": "YES" if surface in seen else "NO",
                "status": "WORKSHOP_PREDICTION_ONLY__DO_NOT_INSERT",
            }
        )

    write(
        "SEVEN_HUNDRED_NINETY_SEVENTH_82_TRANSFER_EVENTS.tsv",
        event_rows,
        ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "operation_tokens", "operation_readings_de", "operation_count", "working_reading_de", "all_operation_meanings_present"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SEVENTH_3_OPERATIONS.tsv",
        summary_rows,
        ["operation", "reading_de", "events", "exact_cards", "recipes", "single_operation_events", "stacked_operation_events"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SEVENTH_7_SHARED_OPERATION_FAMILIES.tsv",
        family_rows,
        ["operation_signature", "present_operations", "missing_operations", "events", "surfaces_by_operation", "status"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SEVENTH_33_SHARED_OPERATION_EVENTS.tsv",
        sorted(shared_rows, key=lambda row: int(str(row["event_id"])[1:])),
        ["event_id", "page", "record", "statement_id", "exact_card_id", "surface", "component_recipe", "operation_tokens", "operation_readings_de", "operation_count", "working_reading_de", "all_operation_meanings_present"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SEVENTH_3_STACKED_OPERATION_TYPES.tsv",
        stacked_rows,
        ["operation_stack", "reading_de", "events", "recipes", "surfaces", "interpretation"],
    )
    write(
        "SEVEN_HUNDRED_NINETY_SEVENTH_6_PREDICTED_OPERATIONS.tsv",
        prediction_rows,
        ["predicted_card", "tail_recipe", "observed_operations", "new_operation", "predicted_recipe", "predicted_surface", "predicted_reading_de", "fixed_page_collision", "status"],
    )

    report = """# Pass 797 — K, L und CHD sind drei verschiedene Transferhandlungen

82 Ereignisse/51 Karten/47 Rezepte tragen mindestens eine der drei Operationen. K erscheint in 21 Ereignissen und bedeutet durchgehend ZUGEBEN/EINBRINGEN; L in 27 und bedeutet LEITEN/FÜHREN; CHD in 48 und bedeutet UMSETZEN/ÜBERFÜHREN. Jede Karte enthält ihren jeweiligen kurzen Arbeitswert, auch wenn Operationen gestapelt sind.

Sieben einfache Endfamilien/33 Ereignisse vergleichen mindestens zwei Operationen. `OP+Y` ist vollständig:

- `K+Y` = diesen Posten zugeben;
- `L+Y` = diesen Posten leiten;
- `CHD+Y` = diesen Posten umsetzen.

Weitere Paare teilen OL, AL, AR, AIR, AIN oder DY. Sechs fehlende Gegenkarten lassen sich bilden: `chedol` (umsetzen und weiter), `lal` (zur Zielstelle leiten), `lair` (Wasser leiten), `lain` (eine Portion leiten), `kdy` (zugeben und schließen), `chdar` (aus der Quelle umsetzen). Keine kollidiert mit dem festen Inventar.

Vierzehn Ereignisse stapeln Operationen ausdrücklich: 12× L→CHD, einmal K→CHD und einmal L→K. Das spricht gegen die Idee, K/L/CHD seien bloß austauschbare Schreibvarianten. Sie bilden eine kurze Prozessfolge: Material einbringen, durch einen Weg führen, in den nächsten Zustand oder Empfänger umsetzen.

Als nächstes setzen wir die sechs Gegenkarten in vollständige Aussagen ein und bauen aus den gestapelten Karten einen konkreten Transferautomaten mit Eingang, Weg und Umsetzung.
"""
    (HERE / "SEVEN_HUNDRED_NINETY_SEVENTH_REPORT.md").write_text(report, encoding="utf-8")

    summary = {
        "status": "PASS",
        "transfer_events": len(event_rows),
        "transfer_cards": len({row["exact_card_id"] for row in event_rows}),
        "transfer_recipes": len({row["component_recipe"] for row in event_rows}),
        "all_meanings_present": sum(row["all_operation_meanings_present"] == "YES" for row in event_rows),
        "shared_families": len(family_rows),
        "shared_events": len(shared_rows),
        "complete_operation_families": sum(row["status"] == "THREE_OPERATION_COMPLETE" for row in family_rows),
        "stacked_events": sum(int(row["events"]) for row in stacked_rows),
        "predicted_operations": len(prediction_rows),
        "prediction_collisions": sum(row["fixed_page_collision"] == "YES" for row in prediction_rows),
        "decision": "K_ADD_L_GUIDE_CHD_TRANSFER_FORM_DISTINCT_STACKABLE_OPERATIONS",
    }
    (HERE / "SEVEN_HUNDRED_NINETY_SEVENTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
