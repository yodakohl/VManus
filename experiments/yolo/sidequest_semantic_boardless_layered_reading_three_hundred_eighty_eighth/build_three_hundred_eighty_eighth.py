#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P382 = ROOT / "experiments/yolo/sidequest_semantic_fourth_copy_combination_three_hundred_eighty_second"

ANALYSES = {
    1: ("COMPONENT_DIRECT", "ENTRY_S+HO", "Zutat", "Zutat der abgebildeten H4-Pflanze"),
    2: ("COMPONENT_DIRECT", "BARE+OR", "Ansatz", "Ansatz zur abgebildeten H4-Pflanze"),
    3: ("WHOLE_CARD_MEMORY", "CHEOAR", "Auszugnahme", "Aus dem H4-Pflanzenansatz einen Auszug nehmen"),
    4: ("WHOLE_CARD_MEMORY", "CHEKY", "Kurzwärme", "Den H4-Ansatz kurz wärmen"),
    5: ("WHOLE_CARD_MEMORY", "LCHEEY", "Klarabzug", "Den klaren Anteil des H4-Ansatzes abziehen"),
    6: ("WHOLE_CARD_MEMORY", "CPHY", "Nachseihen", "Den H4-Auszug nachseihen"),
    7: ("COMPONENT_DIRECT", "ENTRY_CHE+CTHY", "Bereit", "Den H4-Auszug bereitstellen"),
    8: ("COMPONENT_DIRECT", "ENTRY_D+Y", "Diesposten", "Diesen Posten der B3-Station"),
    9: ("COMPONENT_DIRECT", "ENTRY_D+AIIN", "Sollmaß", "Im Sollmaß der B3-Station"),
    10: ("COMPONENT_DIRECT", "ENTRY_SH+CKH+Y", "durchleiten", "Durch die sichtbare B3-Verbindung leiten"),
    11: ("COMPONENT_DIRECT", "ENTRY_Q+OK+Y", "Einsetzen", "In der sichtbaren B3-Station einsetzen"),
    12: ("COMPONENT_DIRECT", "ENTRY_Q+OK+EE+Y", "Langkontakt", "An der B3-Station länger in Kontakt halten"),
    13: ("COMPONENT_DIRECT", "ENTRY_Q+OK+E+DY", "Kurzkontakt", "Kurz in Kontakt bringen und den B3-Schritt schließen"),
    14: ("WHOLE_CARD_MEMORY", "TALAM", "Verwahren", "Das Ergebnis der B3-Station verwahren"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    source = read(P382 / "THREE_HUNDRED_EIGHTY_SECOND_14_SOURCE_CARDS.tsv")
    layer_rows: list[dict[str, object]] = []
    for row in source:
        position = int(row["source_position"])
        route, composition, atomic, owner_expansion = ANALYSES[position]
        layer_rows.append({
            "source_position": position,
            "surface": row["fourth_copy_surface"],
            "joint_tuple_id": row["joint_tuple_id"],
            "owner_code": row["owner_code"],
            "microcycle": row["microcycle"],
            "read_route": route,
            "strict_composition_or_whole_card": composition,
            "atomic_reading_de": atomic,
            "picture_argument_required": "YES",
            "picture_supplied_argument": "H4_PICTURED_PLANT" if row["owner_code"] == "H4" else "B3_VISIBLE_BASIN_CONNECTION_STATION",
            "owner_expanded_reading_de": owner_expansion,
            "board_call_used": "NO",
            "fluent_domain_noun_from_card": "NO",
        })
    write("THREE_HUNDRED_EIGHTY_EIGHTH_14_LAYERED_READINGS.tsv", layer_rows)

    layers = [
        {"layer": 1, "name": "SURFACE", "input": "visible form and carry mark", "output": "fourteen source forms", "needs_picture": "NO"},
        {"layer": 2, "name": "CARD_OR_COMPONENT", "input": "compact component manual plus five learned cards", "output": "fourteen atomic readings", "needs_picture": "NO"},
        {"layer": 3, "name": "OWNER_ARGUMENT", "input": "H4 plant and B3 basin/connection image owners", "output": "what the action concerns", "needs_picture": "YES"},
        {"layer": 4, "name": "FLUENT_EXPANSION", "input": "atomic reading plus inherited owner", "output": "short workshop instruction", "needs_picture": "YES"},
    ]
    write("THREE_HUNDRED_EIGHTY_EIGHTH_FOUR_READING_LAYERS.tsv", layers)

    edition = """# Pass 388 — Rücklesung ohne Brettaufrufe

## Sichtbare Seite

```text
sho or cheoar cheky
cheky
lcheey cphy checthy
dy daiin shckhy qoky
qokeey qokedy talam
```

Die markierte zweite `cheky`-Form wird einmal gelesen.

## Atomare Rücklesung

```text
Zutat · Ansatz · Auszugnahme · Kurzwärme
Klarabzug · Nachseihen · Bereit
Diesposten · Sollmaß · durchleiten · Einsetzen
Langkontakt · Kurzkontakt/Schluss · Verwahren
```

Neun Karten kommen direkt aus dem Komponentenmanual; fünf — `cheoar`, `cheky`,
`lcheey`, `cphy`, `talam` — müssen als Ganzkarten gelernt sein.

## Bildgestützte Werkstattlektüre

**H4:** Von der abgebildeten Pflanze eine Zutat in den Ansatz nehmen; Auszug
nehmen und kurz wärmen; klar abziehen, nachseihen und bereitstellen.

**B3:** Diesen Posten im Sollmaß durch die sichtbare Verbindung leiten und
einsetzen; länger in Kontakt halten, kurz abschließen und verwahren.

Die Wörter „Pflanze“, „Verbindung“ und „Station“ kommen nicht aus den Karten.
Sie sind die stillen Argumente der beiden Bilder.
"""
    (HERE / "THREE_HUNDRED_EIGHTY_EIGHTH_BOARDLESS_EDITION.md").write_text(edition, encoding="utf-8")
    report = """# Pass 388 — neun Komponenten, fünf Ganzkarten, vierzehn Bildargumente

Nach Entfernung sämtlicher Brettaufrufe bleiben neun kompositionell lesbare
Karten und fünf gelernte Ganzkarten. Das reicht für eine vollständige atomare
Folge. Es reicht nicht für die konkreten Substantive: Jede der vierzehn Karten
benötigt den sichtbaren H4- oder B3-Besitzer, um zu sagen, wovon der Ansatz, das
Maß, der Kontakt oder das Verwahren handelt.

Die beste Arbeitsarchitektur lautet nun:

`sichtbare Form → Karte/Komponenten → atomarer Werkstattwert → Bildargument`.

Das ist einfacher als die früheren satzlangen Wortglossen und erklärt zugleich,
warum mehrere Schreiber denselben Text verschieden rendern können. Als nächstes
soll der fünfteilige Ganzkartenrest selbst angegriffen werden: Welche Karten
bilden eine Auszug–Wärme–Klär–Sieb–Speicher-Kette, und welche davon lassen sich
noch in wiederkehrende Kerne zerlegen?
"""
    (HERE / "THREE_HUNDRED_EIGHTY_EIGHTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "source_cards": len(layer_rows),
        "component_direct": sum(row["read_route"] == "COMPONENT_DIRECT" for row in layer_rows),
        "whole_card_memory": sum(row["read_route"] == "WHOLE_CARD_MEMORY" for row in layer_rows),
        "picture_arguments": sum(row["picture_argument_required"] == "YES" for row in layer_rows),
        "reading_layers": len(layers),
        "board_calls_used": 0,
    }
    (HERE / "THREE_HUNDRED_EIGHTY_EIGHTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
