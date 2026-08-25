#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_three_layer_codebook_nine_hundred_forty_sixth/PASS946_2511_THREE_LAYER_EVENT_EDITION.tsv"
LOCI = [f"f75r.{number}" for number in range(47, 54)]
LINE_READINGS = {
    "f75r.47": "Zielklasse wählen; am zweiten Grad eintragen und schließen.",
    "f75r.48": "Diesen Zielplatz mit dem wiederholten Gegenplatz verbinden.",
    "f75r.49": "Dieselbe Klasse an der unteren Quelladresse fortführen.",
    "f75r.50": "Diesen Platz auswählen, markieren und wieder als laufenden Platz setzen.",
    "f75r.51": "Eine Einheit auswählen und ihren örtlichen Gang aufrufen.",
    "f75r.52": "Den gewählten Zielplatz schließen.",
    "f75r.53": "Eine Einheit gehört zu diesem Platz.",
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
    source = [row for row in read_tsv(SOURCE) if row["locus"] in LOCI]
    events: list[dict[str, object]] = []
    for row in source:
        events.append({
            **row,
            "corrected_owner_id": "F75R_UPPER_LEFT_TRIANGULAR_INSET",
            "corrected_owner_de": "dreieckige Insel zwischen Rinnsal und breitem Ablauf",
            "corrected_text_role": "EMBEDDED_SEVEN_LINE_MICRO_REGISTER",
            "local_reading_de": LINE_READINGS[row["locus"]],
        })
    write_tsv(OUT / "PASS948_10_TRIANGULAR_INSET_EVENTS.tsv", events)

    line_rows: list[dict[str, object]] = []
    for locus in LOCI:
        rows = [row for row in events if row["locus"] == locus]
        line_rows.append({
            "line_order": len(line_rows) + 1,
            "locus": locus,
            "surfaces": " ".join(str(row["surface"]) for row in rows),
            "component_recipes": " | ".join(str(row["component_recipe"]) for row in rows),
            "line_reading_de": LINE_READINGS[locus],
            "owner_id": "F75R_UPPER_LEFT_TRIANGULAR_INSET",
        })
    write_tsv(OUT / "PASS948_7_INSET_LINES.tsv", line_rows)

    readable = [
        "# Das dreieckige f75r-Einsatzregister",
        "",
        "Die sieben kurzen Zeilen gehören gemeinsam zur dreieckigen Insel zwischen dem schmalen Rinnsal und dem breiten Ablauf. Sie werden daher als ein einziges kleines Register gelesen, nicht als sieben Namen für sieben Figuren.",
        "",
    ]
    for row in line_rows:
        readable.append(f"{row['line_order']}. `{row['surfaces']}` — {row['line_reading_de']}")
    readable.extend([
        "",
        "Flüssig gelesen: **Wähle die Zielklasse und trage sie am zweiten Grad ein. Verbinde den bezeichneten Platz mit seinem Gegenplatz; führe dieselbe Klasse an der unteren Quelladresse fort und markiere den laufenden Platz. Wähle eine Einheit für den örtlichen Gang, schließe den Zielplatz und ordne ihm eine Einheit zu.**",
        "",
        "Das ist eher eine kompakte Legende oder Einstellanweisung für den sichtbaren Teil der Anlage als eine Liste von Personennamen.",
    ])
    (OUT / "PASS948_COMPLETE_INSET_READING.md").write_text("\n".join(readable) + "\n", encoding="utf-8")

    report = """# Pass 948 — f75r hat ein eingebettetes Mini-Register

Die Loci f75r.47–53 wurden zuvor zu sieben einzelnen Stationen auseinandergezogen.
Das Bild und die vorhandene Objektannotation setzen alle sieben jedoch in dieselbe
dreieckige Insel zwischen Rinnsal und breitem Ablauf. Die zehn Gruppen bilden daher
einen zusammenhängenden Siebenzeiler mit Auswahl, Ziel, Grad, Fortsetzung,
Quelladresse, Einheit und Schluss.

Die Korrektur stärkt die Kartenlesung, weil sie keine sieben erfundenen lokalen
Namen mehr benötigt. Sie schwächt zugleich jede Behauptung, die zehn Gruppen seien
unmittelbare Figurenetiketten.
"""
    (OUT / "PASS948_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {}
    for path in sorted(OUT.glob("PASS948_*")):
        if "BUILD_SUMMARY" in path.name or "VALIDATION" in path.name:
            continue
        outputs[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    summary = {"events": len(events), "lines": len(line_rows), "owners": 1, "outputs": outputs}
    (OUT / "PASS948_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
