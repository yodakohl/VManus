#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P739 = ROOT / "experiments/yolo/sidequest_semantic_clean_fluent_edition_seven_hundred_thirty_ninth"
LICENSED = {
    "OP1_CHED_CHD": {"CHD+DY", "OK+CHD+DY", "OT+CHD+DY"},
    "OP2_Y_CHY": {"OK+Y", "CHD+Y"},
}
PAGE_HAND = {"f10r": "HAND_1", "f11r": "HAND_1", "f56r": "HAND_1", "f55v": "HAND_2", "f81v": "HAND_2", "f82r": "HAND_2", "f83r": "HAND_2"}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        out = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    events = read(P739 / "SEVEN_HUNDRED_THIRTY_NINTH_381_EVENT_INTERLINEAR.tsv")
    by_recipe: dict[str, list[dict[str, str]]] = defaultdict(list)
    surface_recipes: dict[str, set[str]] = defaultdict(set)
    surface_events: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in events:
        by_recipe[row["component_recipe"]].append(row)
        surface_recipes[row["surface"]].add(row["component_recipe"])
        surface_events[row["surface"]].append(row)

    candidates = []
    seen_keys = set()
    for recipe, rows in by_recipe.items():
        components = recipe.split("+")
        for surface in sorted({row["surface"] for row in rows}):
            generated = []
            if "CHD" in components:
                if "ched" in surface:
                    generated.append(("OP1_CHED_CHD", surface.replace("ched", "chd", 1)))
                elif "chd" in surface:
                    generated.append(("OP1_CHED_CHD", surface.replace("chd", "ched", 1)))
            if "Y" in components and "DY" not in components and surface.endswith("y"):
                partner = surface[:-3] + "y" if surface.endswith("chy") else surface[:-1] + "chy"
                generated.append(("OP2_Y_CHY", partner))
            for operation, partner in generated:
                key = (operation, recipe, surface, partner)
                if partner == surface or key in seen_keys:
                    continue
                seen_keys.add(key)
                partner_recipes = surface_recipes.get(partner, set())
                if recipe in partner_recipes:
                    status = "ATTESTED_SAME_RECIPE"
                elif partner_recipes:
                    status = "ATTESTED_DIFFERENT_RECIPE_COLLISION"
                else:
                    status = "UNATTESTED_ON_FIXED_TEN_PAGES"
                licensed = recipe in LICENSED[operation]
                if status == "ATTESTED_SAME_RECIPE":
                    action = "KEEP_AS_OPERATION_SUPPORT"
                elif status == "ATTESTED_DIFFERENT_RECIPE_COLLISION":
                    action = "BLOCK_GLOBAL_SEMANTIC_COLLAPSE"
                elif licensed:
                    action = "STRONG_FUTURE_SURFACE_PREDICTION"
                else:
                    action = "LOW_PRIORITY_EXTRAPOLATION"
                source_rows = [row for row in rows if row["surface"] == surface]
                candidates.append(
                    {
                        "operation": operation,
                        "component_recipe": recipe,
                        "workshop_reading_de": source_rows[0]["rebuilt_reading_de"],
                        "source_surface": surface,
                        "source_events": ",".join(row["event_id"] for row in source_rows),
                        "source_pages": ",".join(sorted({row["page"] for row in source_rows})),
                        "source_hands": ",".join(sorted({PAGE_HAND[row["page"]] for row in source_rows})),
                        "predicted_partner_surface": partner,
                        "partner_attested_recipes": ",".join(sorted(partner_recipes)) or "NONE",
                        "status": status,
                        "already_licensed_recipe_family": "YES" if licensed else "NO",
                        "action": action,
                    }
                )
    write(
        "SEVEN_HUNDRED_EIGHTY_FOURTH_95_SURFACE_PREDICTIONS.tsv",
        candidates,
        ["operation", "component_recipe", "workshop_reading_de", "source_surface", "source_events", "source_pages", "source_hands", "predicted_partner_surface", "partner_attested_recipes", "status", "already_licensed_recipe_family", "action"],
    )

    same = [row for row in candidates if row["status"] == "ATTESTED_SAME_RECIPE"]
    collisions = [row for row in candidates if row["status"] == "ATTESTED_DIFFERENT_RECIPE_COLLISION"]
    strong = [row for row in candidates if row["action"] == "STRONG_FUTURE_SURFACE_PREDICTION"]
    write("SEVEN_HUNDRED_EIGHTY_FOURTH_18_SAME_RECIPE_HITS.tsv", same, list(candidates[0].keys()))
    write("SEVEN_HUNDRED_EIGHTY_FOURTH_2_CROSS_RECIPE_COLLISIONS.tsv", collisions, list(candidates[0].keys()))
    write("SEVEN_HUNDRED_EIGHTY_FOURTH_5_STRONG_UNSEEN_PARTNERS.tsv", strong, list(candidates[0].keys()))

    score_rows = []
    for operation in ("OP1_CHED_CHD", "OP2_Y_CHY"):
        rows = [row for row in candidates if row["operation"] == operation]
        counts = Counter(row["status"] for row in rows)
        score_rows.append(
            {
                "operation": operation,
                "predictions": len(rows),
                "same_recipe_hits": counts["ATTESTED_SAME_RECIPE"],
                "different_recipe_collisions": counts["ATTESTED_DIFFERENT_RECIPE_COLLISION"],
                "unattested": counts["UNATTESTED_ON_FIXED_TEN_PAGES"],
                "strong_unseen_in_licensed_families": sum(row["action"] == "STRONG_FUTURE_SURFACE_PREDICTION" for row in rows),
                "working_scope": "ALL_CHD_RECIPES" if operation == "OP1_CHED_CHD" else "ONLY_LICENSED_OK_OR_CHD_Y_CONTEXTS",
            }
        )
    write(
        "SEVEN_HUNDRED_EIGHTY_FOURTH_2_OPERATION_SCORECARD.tsv",
        score_rows,
        ["operation", "predictions", "same_recipe_hits", "different_recipe_collisions", "unattested", "strong_unseen_in_licensed_families", "working_scope"],
    )

    report = """# Pass 784 — Die Variantenregeln machen echte Vorhersagen, aber Y↔CHY braucht Grenzen

Auf alle163 Rezeptwerte angewandt erzeugen CHED↔CHD und Y↔CHY zusammen95 gerichtete Partnerprognosen. Achtzehn treffen eine bereits sichtbare Form desselben Rezepts;75 Partner fehlen auf den zehn Seiten; zwei treffen eine Form mit **anderem** Rezept.

CHED↔CHD ist die sauberere Regel:27 Prognosen,8 gleiche-Rezept-Treffer,19 bislang unsichtbare Partner und keine Bedeutungs-Kollision. Y↔CHY liefert68 Prognosen,10 Treffer,56 unsichtbare Partner und die entscheidende Kollision:

- `ly = L+Y = LEITEN · DIES`;
- `lchy = L+CH+Y = LEITEN · ENTNEHMEN · DIES`.

Damit ist CH vor Y nicht global bloße Schreiberhülle. In manchen Rezepten trägt CH weiterhin seinen eigenen Wert. Y↔CHY bleibt deshalb nur in den bereits belegten OK+Y- und CHD+Y-Familien produktiv.

Fünf bislang fehlende Formen sind starke, konkrete Vorhersagen innerhalb bereits lizenzierter Familien: `chdchy`, `schdy`, `tchdy`, `okchdy`, `qotchdy`. Sie werden auf den zehn Seiten nicht erfunden oder eingesetzt; sie sind nur unsere Erwartung, falls später weitere Seiten freigegeben werden.

Als nächstes konzentrieren wir uns auf die kollisionsfreie CHED↔CHD-Regel. Wir prüfen, ob lang/kurz mit Hand, offenem Posten, Schluss, Position oder Besitzer zusammenhängt. Daraus könnte erstmals nicht nur eine Partnerform, sondern die Wahl der richtigen Variante folgen.
"""
    (HERE / "SEVEN_HUNDRED_EIGHTY_FOURTH_REPORT.md").write_text(report, encoding="utf-8")
    summary = {
        "status": "PASS",
        "predictions": len(candidates),
        "same_recipe_hits": len(same),
        "cross_recipe_collisions": len(collisions),
        "unattested": sum(row["status"] == "UNATTESTED_ON_FIXED_TEN_PAGES" for row in candidates),
        "strong_unseen": len(strong),
        "decision": "CHED_CHD_PORTABLE_NO_COLLISION__Y_CHY_RESTRICT_TO_LICENSED_CONTEXTS",
    }
    (HERE / "SEVEN_HUNDRED_EIGHTY_FOURTH_BUILD_SUMMARY.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
