#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
P971 = ROOT / "experiments/yolo/sidequest_semantic_canonical_compact_workshop_edition_nine_hundred_seventy_first"
P980 = ROOT / "experiments/yolo/sidequest_semantic_158_unit_image_owned_codebook_nine_hundred_eightieth"


TEMPLATES = [
    "Y", "AIIN", "AIN", "AL", "AR", "AIR",
    "OK+Y", "OK+AIN", "OK+AIIN", "OK+AL", "OK+AR", "OK+AIR",
    "OK+E+Y", "OK+EE+Y", "OK+E+DY", "OK+EE+DY",
    "OT+AL", "OT+AR", "OT+AIIN", "S+AIIN", "S+AL",
    "CHEO+L", "CKH+Y", "L+CHD+DY", "P+CHD+DY", "OL+DY",
    "SH+E+Y", "SH+EE+Y", "CTH+Y", "D_ADDR+AR",
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    encoder = {r["component_recipe"]: r for r in read(P971 / "PASS971_948_RECIPE_ENCODER.tsv")}
    events = read(P980 / "PASS980_2511_EVENT_TEACHING_BINDING.tsv")
    rows = []
    for index, recipe in enumerate(TEMPLATES, 1):
        source = encoder[recipe]
        observed = [r for r in events if r["component_recipe"] == recipe]
        rows.append({
            "template_id": f"T{index:02d}",
            "component_recipe": recipe,
            "portable_composed_value_de": source["portable_core_de"],
            "default_surface": source["default_surface"],
            "allowed_observed_surfaces": source["allowed_observed_surfaces"],
            "observed_events": str(len(observed)),
            "observed_pages": "|".join(sorted({r["physical_page"] for r in observed})),
            "scribe_prediction_rule_de": source["encode_instruction_de"],
        })
    write(HERE / "PASS982_THIRTY_FORWARD_COMPOSITION_TEMPLATES.tsv", rows, list(rows[0]))

    examples = [
        ("f13r", "qopchy", "O+P+Y", "Arbeitsgang ausführen; den aktuellen Pflanzenteil einsetzen."),
        ("f13r", "okchor", "OK+CH+OR", "Einen Teil entnehmen und als Ansatz setzen."),
        ("f13r", "cfholdy", "CFH+OL+DY", "Weiter auspressen und den Teilgang schließen."),
        ("f75r", "qokain", "OK+AIN", "Eine Teilmenge an der Station ansetzen."),
        ("f75r", "qokeedy", "OK+EE+DY", "Länger ansetzen/halten und die Stationszelle schließen."),
        ("f75r", "lchedy", "L+CHD+DY", "Zur nächsten Station leiten, umsetzen und schließen."),
        ("f70v", "otal", "OT+AL", "Zum nächsten Zielplatz gehen."),
        ("f70v", "otaiin", "OT+AIIN", "Den nächsten Tafelwert aufrufen."),
        ("f70v", "okair", "OK+AIR", "Den Ringlauf an dieser Stelle aktivieren."),
        ("f88r", "qokol", "OK+OL", "Den Gefäßansatz setzen und fortführen."),
        ("f88r", "cheol", "CHEO+L", "Den Auszug weiterleiten."),
        ("f88r", "saiin", "S+AIIN", "Den Sollwert für den Drogenposten auswählen."),
    ]
    example_rows = [
        {
            "example_id": f"X{index:02d}",
            "physical_page": page,
            "surface": surface,
            "component_recipe": recipe,
            "predicted_context_reading_de": reading,
        }
        for index, (page, surface, recipe, reading) in enumerate(examples, 1)
    ]
    write(HERE / "PASS982_TWELVE_NEW_PAGE_COMPOSITION_EXAMPLES.tsv", example_rows, list(example_rows[0]))

    lines = [
        "# Pass 982 — vorwärts schreibbares Kompositionshandbuch",
        "",
        "## Die fünf Regeln",
        "",
        "1. Steht die ganze Karte im Fachkasten, gilt der gelernte Ganzwert.",
        "2. Sonst werden die sichtbaren Wurzeln von links nach rechts gelesen.",
        "3. `E`, `EE`, `EEE` verändern den Grad: kurz, länger, vollständig.",
        "4. `Y` hält den aktuell gemeinten Posten offen; nur eine gelernte",
        "   `...DY`-Schlusskarte schließt.",
        "5. Im Diagramm werden QUELLE/ZIEL/LAUF zu Bezugsplatz, Zielplatz und",
        "   Ring- oder Stationslauf; die Relation bleibt dieselbe.",
        "",
        "## Warum das um 1420 lernbar ist",
        "",
        "Die gemischte Kanzleichiffre liefert das Architekturprinzip: längere",
        "Nomenklatorwerte haben Vorrang vor kleineren Zeichen. Mensuralnotation",
        "liefert das Modifierprinzip: ein kleiner Formzusatz verändert Grad oder",
        "Dauer, ohne den Grundwert neu zu erfinden. Rezept- und Apothekerkürzel",
        "liefern Maß-, Gefäß- und Handlungszeichen. Unser System übernimmt nicht",
        "deren Wörter, sondern genau diese drei Schreibgewohnheiten.",
        "",
        "## Die stärksten produktiven Reihen",
        "",
    ]
    for row in rows:
        lines.append(
            f"- `{row['component_recipe']}` → **{row['portable_composed_value_de']}** "
            f"(Default `{row['default_surface']}`, {row['observed_events']} Vorkommen)"
        )
    lines += [
        "",
        "## Neue-Seiten-Probe in Klartext",
        "",
    ]
    for row in example_rows:
        lines.append(f"- {row['physical_page']} `{row['surface']}`: {row['predicted_context_reading_de']}")
    lines += [
        "",
        "Damit kann ein Lehrling neue Karten schreiben, ohne jedes sichtbare Wort",
        "auswendig zu lernen. Bildgebundene Drogen- und Pflanzennamen bleiben im",
        "Fachkasten; Handlung, Menge, Grad, Quelle, Ziel und Schluss sind produktiv.",
        "",
    ]
    (HERE / "PASS982_FORWARD_COMPOSITION_HANDBOOK.md").write_text("\n".join(lines), encoding="utf-8")
    summary = {
        "status": "PASS",
        "templates": len(rows),
        "examples": len(example_rows),
        "template_events": sum(int(r["observed_events"]) for r in rows),
    }
    (HERE / "PASS982_BUILD_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
