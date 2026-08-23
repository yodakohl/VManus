#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_result_close_integration_two_hundred_twenty_first/TWO_HUNDRED_TWENTY_FIRST_116_STATEMENT_PROSE.tsv"

CONTEXTS = {
    "H2-S001": ("TARGET", "Auszugsansatz bereitstellen und Folgeansatz vorbereiten; diesen und den folgenden Posten führen, den folgenden auf Sollwert setzen und als aktuellen Posten halten."),
    "H2-S002": ("NEIGHBOR", "Folgeansatz und bisherigen Ansatz weiterführen; davon den Sollwert-Anteil nehmen und in der Folge behalten."),
    "H2-S003": ("NEIGHBOR", "Im Zubereitungsgefäß den Ansatz auf der Arbeitsstufe bearbeiten und die vorgeschriebene Zugabe einsetzen."),
    "B3-S001": ("NEIGHBOR", "An der oberen offenen Randstation länger sammeln; Schluss."),
    "B3-S002": ("NEIGHBOR", "Zur nächsten Stelle führen und dort länger wärmen; Schluss."),
    "B3-S003": ("TARGET", "Diesen Bestand auf Sollwert setzen, als denselben Bestand aktiv halten und abführen; Schluss."),
    "B3-S004": ("NEIGHBOR", "Davon abmessen und zur Folgestelle bringen."),
    "B3-S005": ("NEIGHBOR", "In die mittlere runde Station überführen; Schluss."),
}

PARSES = [
    {"parse_id": "P1", "parse_name": "VALUE_BRACKET_WITH_REFERENT_RETURN", "core_reading_de": "dieser Posten – Sollwert – derselbe Posten bleibt aktiv", "h2_fit_0_3": 3, "b3_fit_0_3": 3, "extra_meanings_required": 0, "decision": "SELECT"},
    {"parse_id": "P2", "parse_name": "TWO_POSTS_EQUAL_VALUE", "core_reading_de": "zwei Posten erhalten denselben Wert", "h2_fit_0_3": 3, "b3_fit_0_3": 2, "extra_meanings_required": 1, "decision": "KEEP_AS_LOCAL_EXPANSION"},
    {"parse_id": "P3", "parse_name": "PLAIN_REFERENT_REPETITION", "core_reading_de": "dies – Wert – dies ohne Rahmenfunktion", "h2_fit_0_3": 2, "b3_fit_0_3": 2, "extra_meanings_required": 0, "decision": "RIVAL"},
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = {row["statement_id"]: row for row in read(SOURCE)}
    rows: list[dict[str, object]] = []
    for statement_id, (role, translation) in CONTEXTS.items():
        row = source[statement_id]
        rows.append({
            "statement_id": statement_id,
            "record_unit_id": row["record_unit_id"],
            "context_role": role,
            "visible_owner": row["visible_owner"],
            "visible_sequence": row["visible_sequence"],
            "literal_card_reading": row["r221_literal_card_reading"],
            "selected_context_translation_de": translation,
            "contains_y_aiin_y": "YES" if statement_id in {"H2-S001", "B3-S003"} else "NO",
        })
    write(OUT / "TWO_HUNDRED_TWENTY_THIRD_EIGHT_CONTEXT_STATEMENTS.tsv", rows)
    write(OUT / "TWO_HUNDRED_TWENTY_THIRD_THREE_FRAME_PARSES.tsv", PARSES)

    lines = [
        "# Y–AIIN–Y in seinen beiden Arbeitskontexten",
        "",
        "Gewählte Grundregel: **aktueller Posten – vorgeschriebener Wert – derselbe Posten bleibt aktiv**.",
        "",
        "Die symmetrischen Y-Karten öffnen und schließen damit einen Referenzrahmen um AIIN. AIIN bleibt Sollwert; es muss nicht zusätzlich „gleich“ bedeuten.",
        "",
    ]
    for unit, title in (("H2", "Pflanzenartikel f10r"), ("B3", "Stationsfolge f83r")):
        lines.extend([f"## {title}", ""])
        for row in [row for row in rows if row["record_unit_id"] == unit]:
            marker = "ZIEL" if row["context_role"] == "TARGET" else "UMGEBUNG"
            lines.extend([
                f"- **{row['statement_id']} · {marker}** `{row['visible_sequence']}`",
                f"  - Karten: {row['literal_card_reading']}",
                f"  - Lesung: {row['selected_context_translation_de']}",
            ])
        lines.append("")
    lines.extend([
        "## Konkrete Folgerung",
        "",
        "In B3 ist der Rahmen fast wörtlich ausführbar: Bestand bemessen, als denselben aktiven Bestand behalten, dann abführen. In H2 steht unmittelbar vor dem Rahmen eine weitere Y-Karte. Dort kann die lokale Erweiterung zwei aufeinander bezogene Posten meinen: diesen und den folgenden führen; den folgenden bemessen und aktiv halten.",
    ])
    (OUT / "TWO_HUNDRED_TWENTY_THIRD_TWO_CONTEXT_READINGS.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "context_statements": len(rows),
        "target_statements": sum(row["context_role"] == "TARGET" for row in rows),
        "neighbor_statements": sum(row["context_role"] == "NEIGHBOR" for row in rows),
        "parses_compared": len(PARSES),
        "selected_parse": "VALUE_BRACKET_WITH_REFERENT_RETURN",
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
