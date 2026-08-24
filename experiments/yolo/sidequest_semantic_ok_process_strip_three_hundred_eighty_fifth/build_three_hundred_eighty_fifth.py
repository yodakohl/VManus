#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

CARDS = {
    "dy": ("b921a237be883a820352", "D+Y", "ENTRY_D + DIESPOSTEN", "Diesposten"),
    "daiin": ("2f1c5e56e8f0ff459065", "D+AIIN", "ENTRY_D + SOLLMASS", "Sollmaß"),
    "okey": ("08bd5ca0c2ad137a056d", "OK+E+Y", "ANSETZEN + KURZ + OFFEN", "kurz ansetzen; offen"),
    "qokedy": ("7db18b2f0fb7ed0fcfd3", "OK+E+DY", "ANSETZEN + KURZ + SCHLUSS", "kurz ansetzen; Schluss"),
    "okeey": ("0275fbf14e07935b0a45", "OK+EE+Y", "ANSETZEN + LÄNGER + OFFEN", "länger halten; offen"),
    "qokeedy": ("7d25241b0e56c836372a", "OK+EE+DY", "ANSETZEN + LÄNGER + SCHLUSS", "länger halten; Schluss"),
    "qokeeedy": ("d25110e0d8488927278f", "OK+EEE+DY", "ANSETZEN + VOLLSTÄNDIG + SCHLUSS", "vollständig in Kontakt; Schluss"),
}

TRACKS = [
    ("KURZ", ["dy", "daiin", "okey", "qokedy"]),
    ("LÄNGER", ["dy", "daiin", "okeey", "qokeedy"]),
    ("VOLLSTÄNDIG", ["dy", "daiin", "qokeeedy"]),
]


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    token_rows: list[dict[str, object]] = []
    track_rows: list[dict[str, object]] = []
    for track_no, (track, surfaces) in enumerate(TRACKS, 1):
        for position, surface in enumerate(surfaces, 1):
            joint_id, composition, components, atomic = CARDS[surface]
            token_rows.append({
                "track_no": track_no,
                "track": track,
                "position": position,
                "surface": surface,
                "joint_tuple_id": joint_id,
                "strict_composition": composition,
                "strict_component_backread_de": components,
                "short_card_reading_de": atomic,
                "existing_registered_card": "YES",
                "new_surface_invented": "NO",
            })
        track_rows.append({
            "track_no": track_no,
            "track": track,
            "surface_strip": " ".join(surfaces),
            "component_strip": " | ".join(CARDS[surface][2] for surface in surfaces),
            "short_backread": " | ".join(CARDS[surface][3] for surface in surfaces),
            "open_to_closed_pair": "YES" if track != "VOLLSTÄNDIG" else "NO_OPEN_TOP_GRADE_CARD_REGISTERED",
            "owner_prompt": "CURRENT_VISIBLE_OWNER",
            "teaching_use": "PARALLEL_GRADE_TRACK_NOT_CONTINUOUS_RECIPE",
        })
    write("THREE_HUNDRED_EIGHTY_FIFTH_11_TOKEN_COMPONENT_BACKREAD.tsv", token_rows)
    write("THREE_HUNDRED_EIGHTY_FIFTH_THREE_GRADE_TRACKS.tsv", track_rows)

    component_rows = [
        {"component": "ENTRY_D", "compact_value_de": "Eintrittsschale", "content_word": "NO", "scope": "Y and AIIN registered forms"},
        {"component": "Y", "compact_value_de": "Diesposten", "content_word": "YES", "scope": "open current-item endpoint"},
        {"component": "AIIN", "compact_value_de": "Sollmaß", "content_word": "YES", "scope": "measure/setting card"},
        {"component": "OK", "compact_value_de": "ansetzen", "content_word": "YES", "scope": "OK ladder only"},
        {"component": "E", "compact_value_de": "kurz", "content_word": "YES", "scope": "licensed OK grade"},
        {"component": "EE", "compact_value_de": "länger", "content_word": "YES", "scope": "licensed OK grade"},
        {"component": "EEE", "compact_value_de": "vollständig", "content_word": "YES", "scope": "licensed OK top grade"},
        {"component": "DY", "compact_value_de": "Schluss", "content_word": "NO_CONSTRUCTION", "scope": "licensed OK terminal cards only"},
    ]
    write("THREE_HUNDRED_EIGHTY_FIFTH_EIGHT_COMPONENT_MANUAL.tsv", component_rows)

    lesson = """# Pass 385 — dreibahniger OK-Lehrstreifen

Das Blatt zeigt Alternativen, keinen fortlaufenden Rezepttext:

```text
KURZ:         dy daiin okey    qokedy
LÄNGER:       dy daiin okeey   qokeedy
VOLLSTÄNDIG:  dy daiin         qokeeedy
```

Strenge Rücklesung:

- `dy` = Eintritt D + Diesposten.
- `daiin` = Eintritt D + Sollmaß.
- `okey` / `qokedy` = ansetzen + kurz + offen / Schluss.
- `okeey` / `qokeedy` = ansetzen + länger + offen / Schluss.
- `qokeeedy` = ansetzen + vollständig + Schluss.

Die Lücke in der obersten offenen Zelle wird **nicht** mit einer erfundenen Form
gefüllt. Der Werkstattvorrat kennt hier nur den vollständig geschlossenen Gang.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_FIFTH_PROCESS_STRIP.md").write_text(lesson, encoding="utf-8")
    report = """# Pass 385 — vom langen Gloss zurück zu Komponenten

Der Lehrstreifen benutzt sieben bereits belegte Karten in elf Positionen. Zwei
Bahnen zeigen dasselbe offene/geschlossene Paar bei kurzem und längerem Grad;
die vollständige Bahn besitzt nur eine registrierte geschlossene Karte.

Der wichtige Gewinn ist sprachlich: `qokeedy` braucht nicht mehr als eigenes
langes Wort „länger in Kontakt halten und den Schritt abschließen“ gespeichert
zu werden. Es wird aus OK=ansetzen, EE=länger und dem lizenzierten DY-Schluss
gelesen. Ebenso bleiben `dy` und `daiin` trotz gleicher Eintrittsschale getrennt.

Als nächstes bekommt der Lehrling genau einen absichtlichen Grad- oder
Endpunktfehler in jeder Bahn. Die Korrektur darf nur eine bestehende Karte
austauschen und muss erklären, welcher Bestandteil falsch war.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_FIFTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "tracks": len(track_rows),
        "token_positions": len(token_rows),
        "unique_cards": len({row["joint_tuple_id"] for row in token_rows}),
        "components": len(component_rows),
        "invented_surfaces": 0,
        "open_closed_pairs": sum(row["open_to_closed_pair"] == "YES" for row in track_rows),
    }
    (HERE / "THREE_HUNDRED_EIGHTY_FIFTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
