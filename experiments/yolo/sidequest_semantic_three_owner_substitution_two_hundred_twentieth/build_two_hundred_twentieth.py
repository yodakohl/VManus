#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_portable_dictionary_entries_two_hundred_nineteenth/TWO_HUNDRED_NINETEENTH_ELEVEN_PORTABLE_DICTIONARY_ENTRIES.tsv"

TESTS = {
    "OK": {
        "PLANT": ("Wurzel am vorgesehenen Platz einsetzen.", 3, "ansetzen", "Wurzel am Platz ansetzen.", 2),
        "BIO": ("Posten am Becken einsetzen.", 3, "ansetzen", "Posten am Becken ansetzen.", 2),
        "ASTRO": ("Wert am Sektor einsetzen.", 3, "setzen", "Wert am Sektor setzen.", 3),
    },
    "OL": {
        "PLANT": ("Mit demselben Ansatz weiter.", 3, "fortsetzen", "Denselben Ansatz fortsetzen.", 3),
        "BIO": ("Im selben Lauf weiter.", 3, "fortsetzen", "Den selben Lauf fortsetzen.", 3),
        "ASTRO": ("Im selben Ring weiter.", 3, "fortsetzen", "Im Ring fortsetzen.", 3),
    },
    "OT": {
        "PLANT": ("Zum Folgeteil.", 3, "danach", "Danach den Teil nehmen.", 3),
        "BIO": ("Zur Folgestation.", 3, "danach", "Danach zur Station.", 3),
        "ASTRO": ("Zum Folgeplatz.", 3, "danach", "Danach zum Platz.", 3),
    },
    "AR": {
        "PLANT": ("Davon eine Portion nehmen.", 3, "Quelle", "Aus der Quelle eine Portion nehmen.", 2),
        "BIO": ("Von dort abführen.", 3, "Quelle", "Von der Quelle abführen.", 2),
        "ASTRO": ("Vom Ausgangssektor übernehmen.", 3, "Quelle", "Vom Quellsektor übernehmen.", 2),
    },
    "AL": {
        "PLANT": ("An die Zielstelle geben.", 3, "dorthin", "Dorthin geben.", 3),
        "BIO": ("Zum Zielbecken führen.", 3, "dorthin", "Dorthin führen.", 3),
        "ASTRO": ("Zum Zielfeld setzen.", 3, "dorthin", "Dorthin setzen.", 3),
    },
    "AIIN": {
        "PLANT": ("Auf Sollwert bringen.", 3, "Maß", "Auf Maß bringen.", 3),
        "BIO": ("Den Sollwert einstellen.", 3, "Maß", "Das Maß einstellen.", 2),
        "ASTRO": ("Sollwert am Platz ablesen.", 3, "Maß", "Maß am Platz ablesen.", 2),
    },
    "Y": {
        "PLANT": ("Dies als aktuellen Teil halten.", 3, "Posten", "Den Posten halten.", 2),
        "BIO": ("Dies weiterführen.", 3, "Posten", "Den Posten weiterführen.", 2),
        "ASTRO": ("Dies am Diagrammplatz setzen.", 3, "Posten", "Den Diagrammposten setzen.", 2),
    },
    "DY": {
        "PLANT": ("Ansatz fertig.", 2, "Schluss", "Ansatz; Schluss.", 3),
        "BIO": ("Gang fertig.", 1, "Schluss", "Gang; Schluss.", 3),
        "ASTRO": ("Eintrag fertig.", 2, "Schluss", "Eintrag; Schluss.", 3),
    },
    "OR": {
        "PLANT": ("Der laufende Ansatz.", 3, "Eintrag", "Der laufende Eintrag.", 1),
        "BIO": ("Den Ansatz weiterführen.", 3, "Eintrag", "Den Eintrag weiterführen.", 2),
        "ASTRO": ("Ansatz des Schemas.", 2, "Eintrag", "Eintrag des Schemas.", 3),
    },
    "CHED~CHD": {
        "PLANT": ("Die Portion überführen.", 3, "umsetzen", "Die Portion umsetzen.", 3),
        "BIO": ("Den Posten überführen.", 3, "umsetzen", "Den Posten umsetzen.", 3),
        "ASTRO": ("Den Wert überführen.", 3, "umsetzen", "Den Wert umsetzen.", 2),
    },
    "RESULT": {
        "PLANT": ("Freigabewert des Auszugs.", 1, "Ergebnis", "Ergebnis des Auszugs.", 3),
        "BIO": ("Freigabewert des Laufs.", 2, "Ergebnis", "Ergebnis des Laufs.", 3),
        "ASTRO": ("Freigabewert des Sektors.", 3, "Ergebnis", "Ergebnis des Sektors.", 3),
    },
}

REVISIONS = {"DY": "SCHLUSS", "RESULT": "ERGEBNIS"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    entries = read(SOURCE)
    tests: list[dict[str, object]] = []
    revised: list[dict[str, object]] = []
    for entry in entries:
        key = entry["entry_key"]
        rows = TESTS[key]
        current_total = 0
        alternate_total = 0
        for owner in ("PLANT", "BIO", "ASTRO"):
            current_phrase, current_score, alternate, alternate_phrase, alternate_score = rows[owner]
            current_total += current_score
            alternate_total += alternate_score
            tests.append({
                "entry_key": key,
                "current_headword_de": entry["headword_de"],
                "owner_register": owner,
                "current_phrase_de": current_phrase,
                "current_naturalness_0_3": current_score,
                "strongest_alternate_de": alternate,
                "alternate_phrase_de": alternate_phrase,
                "alternate_naturalness_0_3": alternate_score,
                "selected_headword_de": REVISIONS.get(key, entry["headword_de"]),
            })
        selected = REVISIONS.get(key, entry["headword_de"])
        revised.append({
            **entry,
            "previous_headword_de": entry["headword_de"],
            "selected_headword_de": selected,
            "decision": "REVISE" if key in REVISIONS else "KEEP",
            "current_three_owner_score": current_total,
            "alternate_three_owner_score": alternate_total,
            "decision_reason_de": "kürzer und in allen drei Besitzern natürlich" if key in REVISIONS else "beste oder gleich gute registerübergreifende Lesung",
        })
    write(OUT / "TWO_HUNDRED_TWENTIETH_33_SUBSTITUTION_TESTS.tsv", tests)
    write(OUT / "TWO_HUNDRED_TWENTIETH_ELEVEN_REVISED_ENTRIES.tsv", revised)

    lines = ["# Drei-Besitzer-Ersetzungsprobe", ""]
    for entry in revised:
        lines.extend([
            f"## {entry['entry_key']}: {entry['previous_headword_de']} → {entry['selected_headword_de']}",
            "",
            f"Entscheidung: **{entry['decision']}**; aktuelle Probe {entry['current_three_owner_score']}/9, Alternative {entry['alternate_three_owner_score']}/9.",
            "",
        ])
        for row in [row for row in tests if row["entry_key"] == entry["entry_key"]]:
            selected_phrase = row["alternate_phrase_de"] if entry["decision"] == "REVISE" else row["current_phrase_de"]
            lines.append(f"- {row['owner_register']}: {selected_phrase}")
        lines.append("")
    (OUT / "TWO_HUNDRED_TWENTIETH_THREE_OWNER_PHRASEBOOK.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    summary = {
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "entries": len(entries),
        "tests": len(tests),
        "owners_per_entry": 3,
        "revisions": len(REVISIONS),
        "kept": len(entries) - len(REVISIONS),
        "revised_entries": REVISIONS,
        "sealed_pages_accessed": False,
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
