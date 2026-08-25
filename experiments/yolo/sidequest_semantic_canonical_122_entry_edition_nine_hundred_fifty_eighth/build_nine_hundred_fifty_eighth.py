#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
ROOTS = ROOT / "experiments/yolo/sidequest_semantic_concrete_root_lemmas_nine_hundred_fifty_fifth/PASS955_56_CONCRETE_ROOT_LEMMAS.tsv"
FORMULAS = ROOT / "experiments/yolo/sidequest_semantic_deduplicated_root_formula_codebook_nine_hundred_fifty_seventh/PASS957_66_TRUE_MULTICOMPONENT_FORMULAS.tsv"
EVENTS = ROOT / "experiments/yolo/sidequest_semantic_deduplicated_root_formula_codebook_nine_hundred_fifty_seventh/PASS957_2511_DEDUPLICATED_THREE_LAYER_EDITION.tsv"
OLD_PROSE = ROOT / "experiments/yolo/sidequest_semantic_hybrid_card_retranslation_nine_hundred_forty_fourth/PASS944_2010_PROSE_CARD_INTERLINEAR.tsv"
CLAUSES = ROOT / "experiments/yolo/sidequest_semantic_hybrid_card_retranslation_nine_hundred_forty_fourth/PASS944_354_HYBRID_CARD_CLAUSES.tsv"
PAGES = ROOT / "experiments/yolo/sidequest_semantic_book_function_synthesis_nine_hundred_forty_seventh/PASS947_14_UNIT_BOOK_MAP.tsv"
F75_INSET = {f"f75r.{number}" for number in range(47, 54)}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    roots = {row["component"]: row["concrete_root_lemma_de"] for row in read_tsv(ROOTS)}
    formulas = {row["formula_card_id"]: row for row in read_tsv(FORMULAS)}
    source_events = read_tsv(EVENTS)
    old_prose = read_tsv(OLD_PROSE)
    clauses = read_tsv(CLAUSES)
    old_pages = read_tsv(PAGES)

    canonical: list[dict[str, object]] = []
    for row in source_events:
        layer = row["codebook_layer"]
        if layer == "PRODUCTIVE_ABBREVIATION_COMPOSITION":
            value = " · ".join(roots[component] for component in row["component_recipe"].split("+"))
            route = "COMPOSE_56_ROOTS"
        elif layer == "LEARNED_FORMULA_CARD":
            formula = formulas[row["formula_card_id"]]
            value = formula["workshop_formula_de"] if row["channel"] == "WORKSHOP_PROSE" else formula["image_formula_de"]
            route = "READ_66_FORMULAS"
        else:
            value = row["current_value_de"]
            route = "READ_LOCAL_OWNER_VALUE"
        owner_correction = "F75R_TRIANGULAR_INSET_SINGLE_OWNER" if row["locus"] in F75_INSET else "NONE"
        canonical.append({
            "event_id": row["event_id"], "physical_page": row["physical_page"], "locus": row["locus"], "channel": row["channel"],
            "surface": row["surface"], "component_recipe": row["component_recipe"], "codebook_layer": layer,
            "root_or_formula_id": row["formula_card_id"] if layer == "LEARNED_FORMULA_CARD" else row["component_recipe"],
            "canonical_card_reading_de": value, "canonical_reading_route": route, "owner_correction": owner_correction,
        })
    write_tsv(OUT / "PASS958_2511_CANONICAL_EVENT_DICTIONARY.tsv", canonical)
    canonical_by_id = {row["event_id"]: row for row in canonical}

    prose: list[dict[str, object]] = []
    by_clause: dict[str, list[dict[str, object]]] = defaultdict(list)
    for old in old_prose:
        current = canonical_by_id[old["event_id"]]
        row = {
            "event_id": old["event_id"], "clause_id": old["clause_id"], "physical_page": old["physical_page"], "locus": old["locus"],
            "surface": old["surface"], "component_recipe": old["component_recipe"], "codebook_layer": current["codebook_layer"],
            "root_or_formula_id": current["root_or_formula_id"], "canonical_card_reading_de": current["canonical_card_reading_de"],
        }
        prose.append(row)
        by_clause[old["clause_id"]].append(row)
    write_tsv(OUT / "PASS958_2010_CANONICAL_PROSE_INTERLINEAR.tsv", prose)

    clause_rows: list[dict[str, object]] = []
    for clause in clauses:
        members = by_clause[clause["clause_id"]]
        counts = Counter(str(row["codebook_layer"]) for row in members)
        chain = " ; ".join(str(row["canonical_card_reading_de"]) for row in members)
        ending = "TEILGANG GESCHLOSSEN" if clause["end_reason"] == "LICENSED_DY_CLOSE" else "FORTSETZUNG OFFEN" if clause["end_reason"] == "PAGE_END_OPEN" else "LOKALER ABSCHNITT"
        clause_rows.append({
            "clause_id": clause["clause_id"], "physical_page": clause["physical_page"], "register": clause["register"],
            "start_event": clause["start_event"], "end_event": clause["end_event"], "events": len(members),
            "formula_events": counts["LEARNED_FORMULA_CARD"], "root_composition_events": counts["PRODUCTIVE_ABBREVIATION_COMPOSITION"],
            "end_reason": clause["end_reason"], "canonical_clause_reading_de": f"{chain}. {ending}.",
            "event_ids": "|".join(str(row["event_id"]) for row in members),
        })
    write_tsv(OUT / "PASS958_354_CANONICAL_CLAUSE_TRANSLATIONS.tsv", clause_rows)

    layer_by_page: dict[str, Counter[str]] = defaultdict(Counter)
    for row in canonical:
        layer_by_page[str(row["physical_page"])][str(row["codebook_layer"])] += 1
    page_rows: list[dict[str, object]] = []
    for page in old_pages:
        physical = page["physical_page"]
        counts = layer_by_page[physical]
        page_rows.append({
            "physical_page": physical, "book_stage": page["book_stage"], "unit_role_de": page["unit_role_de"],
            "events": sum(counts.values()), "root_compositions": counts["PRODUCTIVE_ABBREVIATION_COMPOSITION"],
            "formula_cards": counts["LEARNED_FORMULA_CARD"], "local_owner_values": counts["LOCAL_NOMENCLATOR_OR_ADDRESS"],
            "canonical_page_reading_de": page["page_reading_de"],
            "page_specific_correction_de": "Sieben Zeilen bilden ein gemeinsames dreieckiges Einsatzregister." if physical == "f75r" else "NONE",
        })
    write_tsv(OUT / "PASS958_14_CANONICAL_PAGE_READINGS.tsv", page_rows)

    theory = [
        "# Kanonische kreative 122-Einträge-Fassung",
        "",
        "## Schreibsystem",
        "",
        "- 56 kurze produktive Stämme; jeder trägt genau ein Lemma.",
        "- 66 echte mehrteilige Formelkarten; jede besitzt eine oder mehrere Schreibvarianten.",
        "- lokale Bild- und Adresskarten, deren konkreter Besitzer aus der Zeichnung kommt.",
        "- Zeilen dienen dem verfügbaren Raum; der Teilgang endet nur an einer lizenzierten Endkarte.",
        "",
        "## Buchfunktion",
        "",
        "**Arbeitsbuch der einfachen Stoffe, Zubereitungen, Bäder und Himmelszeiten**: fünf Pflanzenartikel führen zu einem Gefäß-/Zutatenregister, vier Bade- und Stationsblättern und vier getrennten Himmels-Nachschlagetafeln.",
        "",
        "## Seiten",
        "",
    ]
    for row in page_rows:
        correction = " " + str(row["page_specific_correction_de"]) if row["page_specific_correction_de"] != "NONE" else ""
        theory.append(f"- **{row['physical_page']} — {row['unit_role_de']}**: {row['canonical_page_reading_de']}{correction}")
    theory.extend([
        "",
        "## Kürzeste Gesamtlesung",
        "",
        "Der Schreiber wählt am Bild den Stoff oder Platz, setzt eine Zubereitung an, fügt Portionen nach Sollmaß zu, hält oder bearbeitet sie für eine notierte Stufe, leitet sie zwischen Quelle, Durchlass und Ziel weiter und schließt den Teilgang. Bei den Himmelsbildern werden dieselben Adress- und Gradkarten als Ring-, Stern- und Stellenwerte gelesen.",
    ])
    (OUT / "PASS958_CANONICAL_WORKING_THEORY.md").write_text("\n".join(theory) + "\n", encoding="utf-8")

    counts = Counter(row["codebook_layer"] for row in canonical)
    report = f"""# Pass 958 — kanonische 122-Einträge-Ausgabe

Die bereinigte Grammatik ist vollständig auf 2.511 Ereignisse, 2.010
Prosagruppen, 354 Prosaklauseln und 14 Seiten angewandt. Das Inventar enthält 56
Stämme und 66 echte mehrteilige Formeln; Layerbilanz: {dict(counts)}.

Die f75r-Loci 47–53 besitzen nun durchgehend einen gemeinsamen dreieckigen
Bildbesitzer. Keine der zehn Gruppen wird mehr als unabhängiger Personenname
behandelt.
"""
    (OUT / "PASS958_REPORT.md").write_text(report, encoding="utf-8")
    outputs = {path.name: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(OUT.glob("PASS958_*")) if "BUILD_SUMMARY" not in path.name and "VALIDATION" not in path.name}
    summary = {"roots": 56, "formulas": 66, "events": len(canonical), "prose_events": len(prose), "clauses": len(clause_rows), "pages": len(page_rows), "layer_counts": counts, "outputs": outputs}
    (OUT / "PASS958_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
