#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
TRACE = ROOT / "experiments/yolo/sidequest_semantic_bio_renderer_three_hundred_twelfth/THREE_HUNDRED_TWELFTH_281_RENDERER_TRACE.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    trace = read_tsv(TRACE)
    wrappers = sorted({row["observed_wrapper"] for row in trace})
    stat_rows: list[dict[str, object]] = []
    for wrapper in wrappers:
        members = [row for row in trace if row["observed_wrapper"] == wrapper]
        first_or_only = sum(row["within_field_position"] in {"FIRST", "ONLY"} for row in members)
        stat_rows.append({
            "wrapper": wrapper,
            "events": len(members),
            "after_close": sum(row["prev_dy"] == "1" for row in members),
            "after_close_percent": f"{100 * sum(row['prev_dy'] == '1' for row in members) / len(members):.1f}",
            "line_first": sum(row["line_first"] == "1" for row in members),
            "line_first_percent": f"{100 * sum(row['line_first'] == '1' for row in members) / len(members):.1f}",
            "field_first_or_only": first_or_only,
            "field_first_or_only_percent": f"{100 * first_or_only / len(members):.1f}",
            "first": sum(row["within_field_position"] == "FIRST" for row in members),
            "middle": sum(row["within_field_position"] == "MIDDLE" for row in members),
            "last": sum(row["within_field_position"] == "LAST" for row in members),
            "only": sum(row["within_field_position"] == "ONLY" for row in members),
        })
    write_tsv(OUT / "PASS968_WRAPPER_POSITION_COUNTS.tsv", stat_rows)

    event_rows: list[dict[str, object]] = []
    exceptions: list[dict[str, object]] = []
    for row in trace:
        event = {
            "event_id": row["event_id"], "page": row["page"], "locus": row["locus"], "field_id": row["field_id"],
            "observed_surface": row["observed_surface"], "observed_wrapper": row["observed_wrapper"],
            "card_wrapper_palette": row["card_wrapper_palette"], "line_first": row["line_first"],
            "prev_dy": row["prev_dy"], "within_field_position": row["within_field_position"],
            "record_position_surface": row["record_position_surface"], "record_position_match": row["record_position_match"],
            "copy_instruction": row["copy_instruction"],
            "portable_renderer_reading_de": "gleiche Kartenbedeutung; nur Stellungs-/Handhülle",
        }
        event_rows.append(event)
        if row["record_position_match"] != "YES":
            exceptions.append(event)
    write_tsv(OUT / "PASS968_281_POSITION_RENDERER_TRACE.tsv", event_rows)
    write_tsv(OUT / "PASS968_12_COPY_EXCEPTIONS.tsv", exceptions)

    q = next(row for row in stat_rows if row["wrapper"] == "q")
    s = next(row for row in stat_rows if row["wrapper"] == "s")
    report = f"""# Pass 968 — q folgt der Zelle, s folgt eher der Zeile

Die feldsegmentierte 281-Ereignis-Bioausgabe zeigt die Stellungsregel deutlich:

- `q` kommt {q['events']}mal vor; {q['after_close']} davon direkt nach einer
  Schließkarte und {q['field_first_or_only']} als erstes oder einziges
  Feldereignis. Das sind {q['after_close_percent']} % nach Schluss und
  {q['field_first_or_only_percent']} % am Feldeintritt.
- `s` kommt {s['events']}mal vor; {s['line_first']} davon stehen wirklich am
  Zeilenanfang ({s['line_first_percent']} %).
- `q` ist dagegen nur {q['line_first']}mal zeileninitial
  ({q['line_first_percent']} %). Es ist daher kein gewöhnliches
  Zeilenanfangszeichen.

## Lehrregel

1. Zuerst die Karte und ihre kleine erlaubte Hüllenpalette wählen.
2. Nach einer Schließkarte oder am Beginn einer neuen Zelle innerhalb dieser
   Palette `q` bevorzugen.
3. Am physischen Zeilenanfang innerhalb der Palette `s` bevorzugen.
4. `d`, `ch`, `sh` und andere Hüllen bleiben karten- und handlokale Varianten.
5. Nur bei zwölf Ereignissen muss der Lehrling die konkrete Oberfläche aus dem
   Exemplar kopieren.

Die einfache Record-/Feldpositionsregel schreibt **269/281** sichtbare Formen
richtig. Das bestätigt die Werkstattidee: Die Hülle kodiert vor allem
Schreibstellung und Kartenpalette, nicht ein zusätzliches Wort.
"""
    (OUT / "PASS968_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS968_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {
        "events": len(event_rows), "wrappers": len(stat_rows), "position_matches": sum(row["record_position_match"] == "YES" for row in event_rows),
        "copy_exceptions": len(exceptions), "outputs": outputs,
    }
    (OUT / "PASS968_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
