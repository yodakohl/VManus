#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ROOTS = ROOT / "experiments/yolo/sidequest_semantic_cross_register_core_normalization_nine_hundred_sixty_second/PASS962_56_PORTABLE_ROOT_CORES.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_compact_30_card_deck_nine_hundred_sixty_fifth/PASS965_2511_COMPACT_DECK_EDITION.tsv"

SLOTS = {
    "FRAME": {"CARRIER_Q", "RESUME_CARD"},
    "ORDER": {"OT", "OL"},
    "ACTION": {"OK", "O", "CH", "SH", "K", "T", "CHD", "SHED", "CHK", "CTH", "CKH", "P", "L", "CHEO", "SOLK", "LSH", "CPH", "CFH", "LD", "R", "S"},
    "GRADE": {"E", "EE", "EEE", "IIN", "DA"},
    "ARGUMENT": {"AIIN", "AIN", "AL", "AR", "OR", "D_ADDR", "A_ADDR", "AM_ADDR", "S_ADDR", "Z_ADDR", "D_LABEL", "S_LABEL", "LOCAL_CHAR_F", "LOCAL_CHAR_G", "LOCAL_CHAR_I", "LOCAL_CHAR_B", "LOCAL_CHAR_J", "LOCAL_CHAR_Z", "M_LOCAL", "G_LABEL", "HO", "AN", "OS", "AIR"},
    "REFERENT": {"Y"},
    "CLOSE": {"DY"},
}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    roots = read_tsv(ROOTS)
    events = read_tsv(EVENTS)
    slot_by_component = {component: slot for slot, components in SLOTS.items() for component in components}

    root_rows: list[dict[str, object]] = []
    for row in roots:
        component = row["component"]
        root_rows.append({
            "component": component,
            "portable_core_de": row["portable_core_de"],
            "primary_slot": slot_by_component[component],
            "slot_function_de": {
                "FRAME": "Karte aufnehmen oder wiederaufnehmen",
                "ORDER": "Reihe oder Folge setzen",
                "ACTION": "Handlung, Auswahl oder Transfer ausführen",
                "GRADE": "Stufe, Dauer oder Vollständigkeit modifizieren",
                "ARGUMENT": "Quelle, Menge, Ziel, Stoff oder lokale Adresse einsetzen",
                "REFERENT": "aktuell sichtbaren Posten offen halten",
                "CLOSE": "Teilgang schließen",
            }[slot_by_component[component]],
        })
    write_tsv(OUT / "PASS969_56_COMPONENT_SLOTS.tsv", root_rows)

    event_rows: list[dict[str, object]] = []
    patterns: Counter[str] = Counter()
    recipes_by_pattern: dict[str, set[str]] = {}
    for row in events:
        components = row["component_recipe"].split("+")
        full_slots = [slot_by_component[component] for component in components]
        collapsed: list[str] = []
        for slot in full_slots:
            if not collapsed or collapsed[-1] != slot:
                collapsed.append(slot)
        pattern = ">".join(collapsed)
        patterns[pattern] += 1
        recipes_by_pattern.setdefault(pattern, set()).add(row["component_recipe"])
        event_rows.append({
            "event_id": row["event_id"], "physical_page": row["physical_page"], "locus": row["locus"],
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "component_slots": "+".join(full_slots), "collapsed_slot_pattern": pattern,
            "portable_atomic_reading_de": row["portable_atomic_reading_de"],
            "compact_layer": row["compact_layer"],
        })
    write_tsv(OUT / "PASS969_2511_SLOT_PARSES.tsv", event_rows)

    pattern_rows: list[dict[str, object]] = []
    cumulative = 0
    for rank, (pattern, count) in enumerate(patterns.most_common(), 1):
        cumulative += count
        pattern_rows.append({
            "rank": rank,
            "slot_pattern": pattern,
            "events": count,
            "distinct_component_recipes": len(recipes_by_pattern[pattern]),
            "event_percent": f"{100 * count / len(events):.2f}",
            "cumulative_percent": f"{100 * cumulative / len(events):.2f}",
            "teaching_status": "CORE_PATTERN" if rank <= 20 else "EXTENDED_PATTERN",
        })
    write_tsv(OUT / "PASS969_221_SLOT_PATTERNS.tsv", pattern_rows)

    top20 = sum(int(row["events"]) for row in pattern_rows[:20])
    report = f"""# Pass 969 — die Wortstellung innerhalb der Karte

Die 56 Zeichen fallen in sieben einfache Slots:

`[FRAME] [ORDER] [ACTION] [GRADE] [ARGUMENT] [REFERENT|CLOSE]`

Nicht jede Karte besetzt jeden Slot, und ACTION sowie ARGUMENT dürfen sich in
langen Mikrosequenzen wiederholen. Der Endunterschied ist aber stabil: `Y`
hält den aktuellen Posten offen, `DY` schließt den Teilgang.

## Häufigste Kartenformen

- `ACTION > ARGUMENT` — 332 Ereignisse,
- `ARGUMENT` — 265,
- `ACTION > REFERENT` — 214,
- `ACTION > GRADE > REFERENT` — 156,
- `ACTION > GRADE > CLOSE` — 148,
- `ACTION` — 120,
- `REFERENT` — 119,
- `ACTION > CLOSE` — 101.

Die zwanzig häufigsten Slotmuster decken **{top20}/2511 Ereignisse
({100 * top20 / len(events):.1f} %)**. Insgesamt gibt es 221 Muster, weil
Bildadressen und lange Mikrosequenzen mehrere Aktionen und Argumente koppeln.

## Schreibregel für den Meister

1. Optional Rahmen oder Fortsetzung setzen.
2. Handlung oder Auswahl schreiben.
3. Grad direkt an den betroffenen Arbeitskern binden.
4. Quelle, Menge, Ziel oder lokale Adresse ergänzen.
5. Mit `Y` den Posten offen weiterführen oder mit der lizenzierten `DY`-Karte
   schließen.

Damit wird die Komposition vorhersagbar, ohne natürliche Satzsyntax zu
erfinden: Eine Karte ist eine kleine typisierte Arbeitsanweisung, keine
buchstabenweise verschlüsselte Vokabel.
"""
    (OUT / "PASS969_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS969_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {
        "components": len(root_rows), "events": len(event_rows), "slot_patterns": len(pattern_rows),
        "top20_events": top20, "top20_percent": f"{100 * top20 / len(events):.2f}", "outputs": outputs,
    }
    (OUT / "PASS969_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
