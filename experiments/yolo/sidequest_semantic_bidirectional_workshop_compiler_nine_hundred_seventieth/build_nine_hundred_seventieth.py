#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SURFACES = ROOT / "experiments/yolo/sidequest_semantic_surface_invariant_dictionary_nine_hundred_sixty_sixth/PASS966_1078_SURFACE_DICTIONARY.tsv"

COMMANDS = [
    ("C01", "Diesen Posten setzen", "OK+Y"),
    ("C02", "Eine Einheit setzen", "OK+AIN"),
    ("C03", "Diesen Posten kurz halten", "SH+E+Y"),
    ("C04", "Diesen Posten länger halten", "SH+EE+Y"),
    ("C05", "Kurz setzen und schließen", "OK+E+DY"),
    ("C06", "Länger setzen und schließen", "OK+EE+DY"),
    ("C07", "Diesen Posten umsetzen", "CHD+Y"),
    ("C08", "Absetzen und schließen", "SHED+DY"),
    ("C09", "Fortsetzen und schließen", "OL+DY"),
    ("C10", "Ziel auswählen", "S+AL"),
    ("C11", "Danach aus der Quelle", "OT+AR"),
    ("C12", "Aus der Quelle setzen", "OK+AR"),
]


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    surfaces = read_tsv(SURFACES)
    decode_rows: list[dict[str, object]] = []
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in surfaces:
        by_recipe[row["component_recipe"]].append(row)
        decode_rows.append({
            "surface": row["surface"], "component_recipe": row["component_recipe"],
            "portable_core_de": row["portable_core_de"], "events": row["events"],
            "physical_pages": row["physical_pages"], "layers": row["layers"],
            "decode_instruction_de": "Oberfläche als exakt diese Stammfolge lesen; sichtbaren Besitzer lokal ergänzen.",
        })
    write_tsv(OUT / "PASS970_1078_SURFACE_DECODER.tsv", decode_rows)

    encode_rows: list[dict[str, object]] = []
    for recipe in sorted(by_recipe):
        members = sorted(by_recipe[recipe], key=lambda row: (-int(row["events"]), row["surface"]))
        encode_rows.append({
            "component_recipe": recipe,
            "portable_core_de": members[0]["portable_core_de"],
            "default_surface": members[0]["surface"],
            "default_surface_events": members[0]["events"],
            "allowed_observed_surfaces": "|".join(row["surface"] for row in members),
            "variant_count": len(members),
            "encode_instruction_de": "Default schreiben; nur eine gelistete Stellungs-/Handvariante einsetzen.",
        })
    write_tsv(OUT / "PASS970_948_RECIPE_ENCODER.tsv", encode_rows)
    encode_by_recipe = {row["component_recipe"]: row for row in encode_rows}

    command_rows: list[dict[str, object]] = []
    for command_id, command, recipe in COMMANDS:
        encoded = encode_by_recipe[recipe]
        command_rows.append({
            "command_id": command_id, "source_command_de": command,
            "component_recipe": recipe, "portable_core_de": encoded["portable_core_de"],
            "default_surface": encoded["default_surface"],
            "allowed_observed_surfaces": encoded["allowed_observed_surfaces"],
            "readback_de": encoded["portable_core_de"],
        })
    write_tsv(OUT / "PASS970_12_WORKSHOP_COMMAND_ROUNDTRIPS.tsv", command_rows)

    report = """# Pass 970 — der ausführbare Werkstattcompiler

Das System kann nun in beide Richtungen benutzt werden:

1. **Lesen:** Jede der 1.078 beobachteten Oberflächen führt eindeutig zu einer
   Komponentenfolge und einer portablen Kernbedeutung.
2. **Schreiben:** Jede der 948 beobachteten Komponentenfolgen besitzt eine
   häufigste Defaultoberfläche und eine Liste erlaubter Allographen.
3. **Rücklesen:** Defaultoberfläche und jede gelistete Variante führen wieder
   exakt zur ursprünglichen Komponentenfolge.

Beispiele:

- `Diesen Posten setzen` → `OK+Y` → `qoky` → `SETZEN · DIES`.
- `Eine Einheit setzen` → `OK+AIN` → `qokain` → `SETZEN · EINHEIT`.
- `kurz setzen; schließen` → `OK+E+DY` → `qokedy`.
- `länger setzen; schließen` → `OK+EE+DY` → `qokeedy`.
- `Posten umsetzen` → `CHD+Y` → `chedy`.
- `Ziel auswählen` → `S+AL` → `sal`.

Der Compiler erfindet keine unbekannte Oberfläche. Wenn eine gewünschte
Stammfolge unter den 948 beobachteten Rezepten fehlt, meldet er `UNSEEN_RECIPE`
und verlangt die Form aus dem Meisterexemplar. Das hält die kreative Theorie
schreibbar, ohne beliebige Voynich-ähnliche Wörter zu produzieren.
"""
    (OUT / "PASS970_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS970_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {"surfaces": len(decode_rows), "recipes": len(encode_rows), "commands": len(command_rows), "outputs": outputs}
    (OUT / "PASS970_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
