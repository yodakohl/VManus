#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first"
EVENTS = SOURCE / "TWO_HUNDRED_TWENTY_FIRST_381_EVENT_PROSE.tsv"
LAYERED = SOURCE / "TWO_HUNDRED_TWENTY_FIRST_776_LAYERED_LEDGER.tsv"
COMMON = {"OK", "OL", "OT", "AR", "AL", "AIIN", "Y", "DY", "OR", "CHED~CHD"}

READINGS = {
    "Y > AIIN > Y": ("P01", "dies – Sollwert – dies", "zwei aktuelle Posten unter demselben vorgeschriebenen Wert", "STRONGEST_CONCRETE_HYPOTHESIS"),
    "OK+Y > OL > DY": ("P02", "einsetzen/bearbeiten – weiter – Schluss", "einen aktiven Gang fortsetzen und schließen", "STABLE_PROCESS_FRAME"),
    "AL > OL > OL": ("P03", "Ziel – weiter – Fortsetzung", "am Ziel in demselben Weg weitergehen", "STABLE_ROUTE_FRAME"),
    "AIIN > Y > CHED~CHD": ("P04", "Sollwert – Posten – übertragen", "einen bemessenen Posten in den nächsten Ort überführen", "STABLE_TRANSFER_FRAME"),
    "AIIN > Y > Y": ("P05", "Sollwert – Posten I – Posten II", "zwei Phasen oder Portionen unter einem Sollwert", "TWO_SLOT_FRAME"),
    "Y > Y > AIIN": ("P06", "Posten – dies – Sollwert", "aktiven Posten wiederaufnehmen und bemessen", "REFERENT_VALUE_FRAME"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read(EVENTS)
    layer = {row["source_id"]: row for row in read(LAYERED) if row["source_kind"] == "PROSE_EVENT"}
    by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)

    occurrences: dict[str, list[dict[str, object]]] = defaultdict(list)
    all_repeated: dict[tuple[str, ...], set[str]] = defaultdict(set)
    all_windows: dict[tuple[str, ...], list[tuple[str, int]]] = defaultdict(list)
    for statement_id, rows in by_statement.items():
        signatures: list[str] = []
        for row in rows:
            axes = [axis for axis in layer[row["event_id"]]["component_axes"].split("+") if axis in COMMON]
            signatures.append("+".join(axes) if axes else "LOCAL")
        for size in (3, 4, 5):
            for start in range(len(rows) - size + 1):
                window = tuple(signatures[start:start + size])
                if "LOCAL" in window:
                    continue
                all_repeated[window].add(statement_id)
                all_windows[window].append((statement_id, start))

    repeated = {window: places for window, places in all_windows.items() if len(all_repeated[window]) >= 2}
    three = {" > ".join(window): places for window, places in repeated.items() if len(window) == 3}
    if set(three) != set(READINGS):
        raise ValueError(f"unexpected recurrent windows: {sorted(three)}")

    phrase_rows: list[dict[str, object]] = []
    occurrence_rows: list[dict[str, object]] = []
    for signature, (phrase_id, literal, hypothesis, status) in READINGS.items():
        places = three[signature]
        phrase_rows.append({
            "phrase_id": phrase_id,
            "axis_signature": signature,
            "literal_core_de": literal,
            "working_phrase_de": hypothesis,
            "status": status,
            "occurrences": len(places),
            "distinct_statements": len({statement_id for statement_id, _ in places}),
            "distinct_records": len({by_statement[statement_id][0]["record_unit_id"] for statement_id, _ in places}),
        })
        for statement_id, start in places:
            rows = by_statement[statement_id][start:start + 3]
            occurrence_rows.append({
                "phrase_id": phrase_id,
                "statement_id": statement_id,
                "record_unit_id": rows[0]["record_unit_id"],
                "page": rows[0]["page"],
                "visible_owner": rows[0]["visible_owner"],
                "window_start_event": rows[0]["event_id"],
                "visible_window": " ".join(row["visible_surface"] for row in rows),
                "card_value_window": " > ".join(row["portable_value_de"] for row in rows),
                "axis_signature": signature,
                "working_phrase_de": hypothesis,
            })
    write(OUT / "TWO_HUNDRED_TWENTY_SECOND_SIX_RECURRENT_PHRASES.tsv", sorted(phrase_rows, key=lambda row: str(row["phrase_id"])))
    write(OUT / "TWO_HUNDRED_TWENTY_SECOND_TWELVE_REAL_OCCURRENCES.tsv", sorted(occurrence_rows, key=lambda row: (str(row["phrase_id"]), str(row["statement_id"]))))

    lines = ["# Reale Dreikarten-Miniaturen", ""]
    for phrase in sorted(phrase_rows, key=lambda row: str(row["phrase_id"])):
        lines.extend([
            f"## {phrase['phrase_id']}: `{phrase['axis_signature']}`",
            "",
            f"Kern: **{phrase['literal_core_de']}**.",
            "",
            f"Arbeitslesung: **{phrase['working_phrase_de']}**.",
            "",
        ])
        for row in sorted([row for row in occurrence_rows if row["phrase_id"] == phrase["phrase_id"]], key=lambda row: str(row["statement_id"])):
            lines.append(f"- {row['statement_id']} `{row['visible_window']}` → {row['card_value_window']}")
        lines.append("")
    lines.extend([
        "## Der konkrete Lead",
        "",
        "`Y–AIIN–Y` ist die einzige Miniatur, deren drei ganze Kartenwerte in beiden Vorkommen unverändert `dies – Sollwert – dies` lauten. Die beste Werkstattlektüre ist daher vorläufig: zwei bezeichnete Posten werden unter denselben vorgeschriebenen Wert gestellt. Das kann gleiche Menge, gleicher Grad oder gleiche Einstellung bedeuten; `AIIN` selbst bleibt nur Sollwert.",
    ])
    (OUT / "TWO_HUNDRED_TWENTY_SECOND_REAL_PHRASEBOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "event_source_sha256": hashlib.sha256(EVENTS.read_bytes()).hexdigest(),
        "layered_source_sha256": hashlib.sha256(LAYERED.read_bytes()).hexdigest(),
        "statements_scanned": len(by_statement),
        "windows_length_3_to_5": sum(len(places) for places in all_windows.values()),
        "cross_statement_recurrent_patterns": len(repeated),
        "recurrent_length_3": sum(len(window) == 3 for window in repeated),
        "recurrent_length_4": sum(len(window) == 4 for window in repeated),
        "recurrent_length_5": sum(len(window) == 5 for window in repeated),
        "selected_phrases": len(phrase_rows),
        "selected_occurrences": len(occurrence_rows),
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
