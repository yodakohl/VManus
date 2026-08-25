#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_extended_formula_deck_nine_hundred_forty_ninth/PASS949_2511_EXTENDED_THREE_LAYER_EDITION.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def drawer(component_count: int, events: int, pages: int) -> str:
    if component_count == 1:
        return "BASIC_ABBREVIATION"
    if events >= 3 and pages >= 2:
        return "NEXT_FORMULA_CANDIDATE"
    if events >= 2:
        return "RECURRENT_TRANSPARENT_COMPOSITION"
    return "ONE_OFF_PRODUCTIVE_COMPOSITION"


def main() -> None:
    events = [row for row in read_tsv(SOURCE) if row["codebook_layer"] == "PRODUCTIVE_ABBREVIATION_COMPOSITION"]
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_recipe[row["component_recipe"]].append(row)

    recipe_rows: list[dict[str, object]] = []
    for recipe, members in by_recipe.items():
        pages = sorted({row["physical_page"] for row in members})
        surfaces = Counter(row["surface"] for row in members)
        component_count = len(recipe.split("+"))
        selected_drawer = drawer(component_count, len(members), len(pages))
        example = Counter(row["current_value_de"] for row in members).most_common(1)[0][0]
        recipe_rows.append({
            "component_recipe": recipe,
            "component_count": component_count,
            "events": len(members),
            "surface_types": len(surfaces),
            "surfaces": "|".join(surface for surface, _ in surfaces.most_common()),
            "page_count": len(pages),
            "physical_pages": "|".join(pages),
            "residual_drawer": selected_drawer,
            "current_short_reading_de": example,
            "teaching_instruction_de": {
                "BASIC_ABBREVIATION": "Als einzelnes Kürzel lesen, nicht als Ganzkarte memorieren.",
                "NEXT_FORMULA_CANDIDATE": "Als mögliche fertige Formel prüfen; mehrere Seiten verwenden dieselbe Folge.",
                "RECURRENT_TRANSPARENT_COMPOSITION": "Aus den bekannten Kürzeln zusammensetzen; Wiederkehr allein erzwingt keine Ganzkarte.",
                "ONE_OFF_PRODUCTIVE_COMPOSITION": "Einmalig aus den bekannten Kürzeln zusammensetzen.",
            }[selected_drawer],
        })
    recipe_rows.sort(key=lambda row: (str(row["residual_drawer"]), -int(row["events"]), str(row["component_recipe"])))
    write_tsv(OUT / "PASS951_RESIDUAL_RECIPE_DRAWERS.tsv", recipe_rows)

    event_rows: list[dict[str, object]] = []
    drawer_by_recipe = {str(row["component_recipe"]): str(row["residual_drawer"]) for row in recipe_rows}
    for row in events:
        event_rows.append({**row, "residual_drawer": drawer_by_recipe[row["component_recipe"]]})
    write_tsv(OUT / "PASS951_903_RESIDUAL_EVENTS.tsv", event_rows)

    counts = Counter(row["residual_drawer"] for row in event_rows)
    recipe_counts = Counter(str(row["residual_drawer"]) for row in recipe_rows)
    candidates = [row for row in recipe_rows if row["residual_drawer"] == "NEXT_FORMULA_CANDIDATE"]
    md = [
        "# Die verbleibenden Kürzelschubladen",
        "",
        f"Nach dem 63-Karten-Deck bleiben {len(events)} produktiv gelesene Ereignisse in {len(recipe_rows)} Komponentenfolgen.",
        "",
        "## Nächste Formelkandidaten",
        "",
    ]
    for row in sorted(candidates, key=lambda item: (-int(item["events"]), -int(item["page_count"]), str(item["component_recipe"]))):
        md.append(f"- `{row['component_recipe']}` — {row['events']} Belege/{row['page_count']} Seiten — {row['current_short_reading_de']}")
    md.extend([
        "",
        "## Lehrmeisterentscheidung",
        "",
        "Einzelne Grundkürzel bleiben produktiv. Nur wiederkehrende Mehrteilfolgen auf mehreren Seiten kommen für eine weitere Formelschublade infrage. Einmalformen werden nicht zu künstlichen Wörterbucheinträgen aufgebläht.",
    ])
    (OUT / "PASS951_RESIDUAL_DRAWER_MANUAL.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    report = f"""# Pass 951 — was nach dem 63-Karten-Deck übrig bleibt

Die {len(events)} produktiven Ereignisse verteilen sich auf {len(recipe_rows)}
Komponentenfolgen. Ereignisschubladen: {dict(counts)}. Rezeptschubladen:
{dict(recipe_counts)}.

Die Trennung verhindert zwei Fehler zugleich: ein nacktes Kürzel wie `L` wird
nicht zur Ganzkarte erklärt, und eine seltene lange Form wird nicht automatisch
zum unanalysierbaren Wort. Der nächste Ausbau darf nur die echte mittlere
Schublade `NEXT_FORMULA_CANDIDATE` betreffen.
"""
    (OUT / "PASS951_REPORT.md").write_text(report, encoding="utf-8")
    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("PASS951_*")) if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name}
    summary = {"events": len(events), "recipes": len(recipe_rows), "event_drawers": counts, "recipe_drawers": recipe_counts, "outputs": outputs}
    (OUT / "PASS951_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
