#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
FAMILIES = ROOT / "experiments/yolo/sidequest_semantic_long_formula_deck_nine_hundred_fifty_second/PASS952_79_LEARNED_CARD_FAMILIES.tsv"
VARIANTS = ROOT / "experiments/yolo/sidequest_semantic_long_formula_deck_nine_hundred_fifty_second/PASS952_155_SURFACE_VARIANTS.tsv"
FORWARD = ROOT / "experiments/yolo/sidequest_semantic_ca1420_hybrid_teaching_book_nine_hundred_forty_third/PASS943_27_FORWARD_COMPOSITIONS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_long_formula_deck_nine_hundred_fifty_second/PASS952_2511_LONG_FORMULA_EDITION.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    families = read_tsv(FAMILIES)
    variants = read_tsv(VARIANTS)
    forward = read_tsv(FORWARD)
    events = read_tsv(EVENTS)
    family_by_id = {row["learned_card_id"]: row for row in families}
    by_family: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in variants:
        by_family[row["learned_card_id"]].append(row)

    variant_predictions: list[dict[str, object]] = []
    for family_id, members in by_family.items():
        primary = next(row for row in members if row["surface_role"] == "PRIMARY_FORM")
        family = family_by_id[family_id]
        for row in members:
            if row is primary:
                continue
            variant_predictions.append({
                "prediction_id": f"P954-V{len(variant_predictions) + 1:03d}",
                "learned_card_id": family_id,
                "component_recipe": family["component_recipe"],
                "known_primary_surface": primary["surface"],
                "predicted_equivalent_surface": row["surface"],
                "predicted_workshop_value_de": family["workshop_learned_value_de"],
                "predicted_image_value_de": family["image_register_value_de"],
                "observed_events": row["events"],
                "prediction_rule_de": "Gleiche Komponentenfolge, daher gleicher Kartenwert trotz anderer Eintritts-/Positionsform.",
            })
    write_tsv(OUT / "PASS954_76_RENDERER_VARIANT_PREDICTIONS.tsv", variant_predictions)

    observed_by_surface: dict[str, set[str]] = defaultdict(set)
    for row in events:
        observed_by_surface[row["surface"]].add(row["component_recipe"])
    formula_by_recipe = {row["component_recipe"]: row for row in families}
    forward_rows: list[dict[str, object]] = []
    for index, row in enumerate(forward, 1):
        recipe = row["component_recipe"]
        formula = formula_by_recipe.get(recipe)
        route = "LEARNED_FORMULA_CARD" if formula else "PRODUCTIVE_ABBREVIATION_COMPOSITION"
        workshop = formula["workshop_learned_value_de"] if formula else row["workshop_reading_de"]
        image = formula["image_register_value_de"] if formula else row["image_reading_de"]
        bare_seen = row["candidate_bare_surface"] in observed_by_surface
        entry_seen = row["candidate_entry_surface"] in observed_by_surface
        observed_recipes = observed_by_surface[row["candidate_bare_surface"]] | observed_by_surface[row["candidate_entry_surface"]]
        recipe_match = recipe in observed_recipes
        surface_status = "OBSERVED_RECIPE_MATCH" if recipe_match else "HOMOGRAPH_DIFFERENT_PARSE" if observed_recipes else "UNSEEN_FORWARD_FORM"
        forward_rows.append({
            "prediction_id": f"P954-F{index:03d}",
            "component_recipe": recipe,
            "candidate_bare_surface": row["candidate_bare_surface"],
            "candidate_entry_surface": row["candidate_entry_surface"],
            "prediction_route": route,
            "predicted_workshop_value_de": workshop,
            "predicted_image_value_de": image,
            "bare_surface_observed": "YES" if bare_seen else "NO",
            "entry_surface_observed": "YES" if entry_seen else "NO",
            "observed_component_recipes": "|".join(sorted(observed_recipes)) if observed_recipes else "NONE",
            "surface_prediction_status": surface_status,
            "use_if_written_de": "Als Kartenwert lesen, ohne eine neue Wurzel oder ein neues Ganzwort anzusetzen.",
        })
    write_tsv(OUT / "PASS954_27_FORWARD_COMPOSITION_PREDICTIONS.tsv", forward_rows)

    manual = [
        "# Vorhersagegrammatik des 135-Einträge-Systems",
        "",
        "## Regel 1 — bekannte Ganzkarte",
        "",
        "Wenn die Komponentenfolge einer der 79 Formelkarten entspricht, hat jede zulässige q/s/ch/d-Schreibvariante denselben Kartenwert.",
        "",
        "## Regel 2 — neue Komposition",
        "",
        "Wenn keine Formelkartenfolge passt, werden die 56 Kürzel in sichtbarer Reihenfolge gelesen. Besitzer und Sachgebiet füllen erst danach die konkrete Sache ein.",
        "",
        "## Regel 3 — lokale Namen",
        "",
        "Ein Wert, der nur an einem Bildbesitzer vorkommt, wird als lokale Nomenklatorkarte kopiert. Seine sichtbaren Teilformen liefern höchstens Klasse, Adresse oder Grad; sie erzwingen keinen Pflanzennamen.",
        "",
        f"Damit sagt das System {len(variant_predictions)} nichtprimäre beobachtete Schreibformen aus ihrer Kartenfamilie und {len(forward_rows)} noch nicht benötigte Kompositionsformen voraus.",
    ]
    (OUT / "PASS954_COMPOSITION_PREDICTION_MANUAL.md").write_text("\n".join(manual) + "\n", encoding="utf-8")

    unseen = sum(row["surface_prediction_status"] == "UNSEEN_FORWARD_FORM" for row in forward_rows)
    homographs = sum(row["surface_prediction_status"] == "HOMOGRAPH_DIFFERENT_PARSE" for row in forward_rows)
    matches = sum(row["surface_prediction_status"] == "OBSERVED_RECIPE_MATCH" for row in forward_rows)
    report = f"""# Pass 954 — das Wörterbuch sagt Kompositionen voraus

Die 79 Kartenfamilien erzeugen **{len(variant_predictions)}** beobachtete
Nichtprimärformen ohne Bedeutungswechsel. Daneben liefert die produktive
Kürzelgrammatik **{len(forward_rows)}** vorab formulierte Kartenpaare; {unseen}
davon sind auf den 14 Seiten in keiner der beiden vorgeschlagenen Oberflächen
belegt und bleiben echte Schreibervorhersagen. {homographs} Oberfläche ist als
Homograph mit anderer Zerlegung belegt; {matches} stimmen bereits in Form und
Komponentenfolge überein.

Die Vorhersage betrifft den internen Werkstattwert, nicht ein lateinisches oder
deutsches Lautwort. So kann `SOLK+EEE+DY` schon jetzt „vollständig auffangen;
Ende“ bedeuten, selbst wenn die konkrete Oberfläche erst auf einer anderen Seite
geschrieben würde.
"""
    (OUT / "PASS954_REPORT.md").write_text(report, encoding="utf-8")
    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("PASS954_*")) if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name}
    summary = {"variant_predictions": len(variant_predictions), "forward_predictions": len(forward_rows), "fully_unseen_forward_predictions": unseen, "homographs_with_different_parse": homographs, "observed_recipe_matches": matches, "outputs": outputs}
    (OUT / "PASS954_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
