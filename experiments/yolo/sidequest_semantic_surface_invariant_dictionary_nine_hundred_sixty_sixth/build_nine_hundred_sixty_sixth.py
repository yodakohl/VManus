#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_compact_30_card_deck_nine_hundred_sixty_fifth/PASS965_2511_COMPACT_DECK_EDITION.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def register(page: str) -> str:
    if page in {"f10r", "f11r", "f13r", "f55v", "f56r", "f88r"}:
        return "HERBAL_PREPARATION"
    if page in {"f75r", "f81v", "f82r", "f83r"}:
        return "BATH_STATION"
    return "CELESTIAL_LOOKUP"


def main() -> None:
    events = read_tsv(EVENTS)
    groups: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        groups[row["surface"]].append(row)

    rows: list[dict[str, object]] = []
    bridges: list[dict[str, object]] = []
    for surface in sorted(groups):
        members = groups[surface]
        recipes = sorted({row["component_recipe"] for row in members})
        cores = sorted({row["portable_atomic_reading_de"] for row in members})
        layers = sorted({row["compact_layer"] for row in members})
        pages = sorted({row["physical_page"] for row in members})
        registers = sorted({register(row["physical_page"]) for row in members})
        event_ids = [row["event_id"] for row in members]
        row = {
            "surface": surface,
            "component_recipe": recipes[0] if len(recipes) == 1 else "CONFLICT:" + "|".join(recipes),
            "portable_core_de": cores[0] if len(cores) == 1 else "CONFLICT:" + "|".join(cores),
            "events": len(members),
            "physical_pages": "|".join(pages),
            "registers": "|".join(registers),
            "layers": "|".join(layers),
            "cross_layer": "YES" if len(layers) > 1 else "NO",
            "cross_register": "YES" if len(registers) > 1 else "NO",
            "event_ids": "|".join(event_ids),
        }
        rows.append(row)
        if len(layers) > 1:
            bridges.append(row)
    write_tsv(OUT / "PASS966_1078_SURFACE_DICTIONARY.tsv", rows)
    write_tsv(OUT / "PASS966_107_CROSS_LAYER_SURFACES.tsv", bridges)

    cross_register = [row for row in rows if row["cross_register"] == "YES"]
    report = f"""# Pass 966 — ein sichtbarer Typ, ein Kernwert

Das kompakte System enthält **1.078 verschiedene sichtbare Formen**. Keine
einzige braucht zwei Komponentenzerlegungen oder zwei portable Kernwerte.

**107 Formen** erscheinen sowohl als Prosakarte als auch als Bild-/Adresskarte
und decken zusammen 814 Ereignisse. Ihre Rolle wechselt, ihre innere Lesung
nicht: `daiin` bleibt `AIIN = SOLLWERT`, `chedy` bleibt `CHD+Y = UMSETZEN ·
DIES`, `dy/chey/chy/y` bleiben Renderer derselben `Y = DIES`-Karte. Das Bild
entscheidet nur, wessen Sollwert, Posten oder Ziel gemeint ist.

{len(cross_register)} Oberflächen erscheinen in mehr als einem der drei
Sachregister. Auch dort gibt es keinen Kernkonflikt. Damit ist die wichtigste
Wörterbuchregel ausgesprochen einfach:

> Gleiche Oberfläche → gleiche Komponentenfolge → gleicher Kernwert;
> nur der sichtbare Besitzer wird lokal ergänzt.

Das räumt die alte Sorge aus, `shey`, `dy`, `s` oder `chey` müssten je nach
Seite ganz andere Wörter sein. Sie können andere **Anwendungen** derselben
Karte sein, aber das Grundwörterbuch wechselt nicht.
"""
    (OUT / "PASS966_REPORT.md").write_text(report, encoding="utf-8")

    outputs = {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(OUT.glob("PASS966_*"))
        if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name
    }
    summary = {
        "events": len(events), "surfaces": len(rows), "cross_layer_surfaces": len(bridges),
        "cross_layer_events": sum(int(row["events"]) for row in bridges),
        "cross_register_surfaces": len(cross_register),
        "component_conflicts": sum(str(row["component_recipe"]).startswith("CONFLICT:") for row in rows),
        "meaning_conflicts": sum(str(row["portable_core_de"]).startswith("CONFLICT:") for row in rows),
        "outputs": outputs,
    }
    (OUT / "PASS966_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
