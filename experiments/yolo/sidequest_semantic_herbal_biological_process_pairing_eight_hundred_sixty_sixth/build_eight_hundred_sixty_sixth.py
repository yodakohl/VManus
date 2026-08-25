#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HERBAL_DIR = ROOT / "sidequest_semantic_four_herbal_process_atlas_eight_hundred_sixty_fourth"
BIO_DIR = ROOT / "sidequest_semantic_three_biological_process_atlas_eight_hundred_sixty_fifth"
HERBAL_EVENTS = HERBAL_DIR / "EIGHT_HUNDRED_SIXTY_FOURTH_100_CARD_HERBAL_ATLAS.tsv"
HERBAL_PROFILES = HERBAL_DIR / "EIGHT_HUNDRED_SIXTY_FOURTH_4_PAGE_PROCESS_PROFILES.tsv"
BIO_EVENTS = BIO_DIR / "EIGHT_HUNDRED_SIXTY_FIFTH_281_CARD_BIOLOGICAL_ATLAS.tsv"
BIO_PROFILES = BIO_DIR / "EIGHT_HUNDRED_SIXTY_FIFTH_6_RECORD_PROCESS_PROFILES.tsv"
PREFIX = "EIGHT_HUNDRED_SIXTY_SIXTH"

PREPARATIONS = {
    "f10r": {
        "preparation_type": "WAESSRIGER_GRUNDANSATZ_MIT_OFFENEM_ABZWEIG",
        "workshop_name_de": "wässriger Grundansatz mit offenem Nebenansatz",
        "supplies_de": "Wasser; Quelle; Sollmaß; Hauptansatz; abgezweigter Posten",
    },
    "f11r": {
        "preparation_type": "AUSGEPRESSTER_UND_AUFGENOMMENER_AUSZUG",
        "workshop_name_de": "ausgepresster und aufgenommener Auszug",
        "supplies_de": "Pflanzenstoff; Auspressen; Empfänger; geschlossener Erstauszug; davon",
    },
    "f55v": {
        "preparation_type": "GEMESSENER_ERWAERMTER_ANSATZ",
        "workshop_name_de": "gemessener, erwärmter Ansatz",
        "supplies_de": "mehrere Maße; Zusatz; Ansatz; Wärme; Zielstelle",
    },
    "f56r": {
        "preparation_type": "ZUTATENREICHER_DURCHLASS_UND_ANWENDUNGSANSATZ",
        "workshop_name_de": "zutatenreicher Durchlass- und Anwendungsansatz",
        "supplies_de": "wiederholte Zutat; Portion; Durchlass; Zielstelle; Anwendungsgang",
    },
}

APPLICATIONS = {
    "B1": "gemeinsame Beckenanwendung mit Wasser, Quelle, Ziel und wiederholtem Weiterführen",
    "B2": "fünf gemessene Stationsanwendungen mit Durchlass und Haltezeit",
    "B3": "Gefäß- und Paarstationsfolge mit Entnahme, Bereitung und wiederholtem Ablassen",
    "B4": "Transfer-, Portions- und Haltefolge an gekoppelten Stellen",
    "B5": "kurzer Weiterleitungs- und Messnachtrag",
    "B6": "offene Einstellung eines Postens an einer Zielstelle",
}

# Creative workshop fit: fixed before calculating shared-card overlap. It says
# how naturally a preparation type could feed an application record; it is not
# evidence for an exact page-to-page pointer.
PROCESS_FIT = {
    ("f10r", "B1"): (5, "Wasser und offener Grundansatz passen zur gemeinsamen Beckenfolge"),
    ("f11r", "B1"): (2, "ein fertiger Auszug wäre möglich, erklärt aber den Wasseraufbau schwächer"),
    ("f55v", "B1"): (3, "Maß und Wärme passen, der gemeinsame Grundansatz weniger"),
    ("f56r", "B1"): (4, "Durchlass und Zielanwendung passen, der Wassergrundstock bleibt indirekt"),
    ("f10r", "B2"): (2, "Grundansatz passt nur allgemein zu den fünf getrennten Stationen"),
    ("f11r", "B2"): (3, "Auszug und Halten passen, die wiederholten Durchlasszellen nur teilweise"),
    ("f55v", "B2"): (4, "Maß, Wärme und Halten passen gut"),
    ("f56r", "B2"): (5, "Portion, Durchlass, Zielstelle und wiederholte Anwendung passen direkt"),
    ("f10r", "B3"): (2, "offener Grundansatz ist zu allgemein für die Gefäßfolge"),
    ("f11r", "B3"): (5, "Auspressen, Empfangen, Davon-Nehmen und Ablassen passen zur Gefäßfolge"),
    ("f55v", "B3"): (3, "Maß und Ansatz passen, aber der Extraktionscharakter fehlt"),
    ("f56r", "B3"): (3, "Zutat und Anwendung passen, der Empfang des Auszugs weniger"),
    ("f10r", "B4"): (2, "ein offener Nebenansatz kann transferiert werden, bleibt aber unspezifisch"),
    ("f11r", "B4"): (4, "aufgenommener Auszug und Davon-Portion passen zu Transfer und Halten"),
    ("f55v", "B4"): (5, "gemessener warmer Ansatz passt zu Portion, Transfer und Haltegrad"),
    ("f56r", "B4"): (3, "Anwendungsgang passt, die starke Haltefolge ist weniger spezifisch"),
    ("f10r", "B5"): (2, "Quelle und Weiterführung sind vorhanden, aber ohne besonderen Leitungsabschluss"),
    ("f11r", "B5"): (2, "Auszug kann weitergeleitet werden, der Messnachtrag bleibt unspezifisch"),
    ("f55v", "B5"): (3, "Maß passt, die Weiterleitung nur mittelbar"),
    ("f56r", "B5"): (5, "Durchlass, Ziel und Portion passen zum kurzen Routennachtrag"),
    ("f10r", "B6"): (4, "offener abgezweigter Posten passt zur offenen Zieleinstellung"),
    ("f11r", "B6"): (2, "ein fertiger Auszug wäre möglich, aber nicht eigens angezeigt"),
    ("f55v", "B6"): (5, "gemessener Ansatz und Zielstelle passen zur offenen Einstellung"),
    ("f56r", "B6"): (3, "Zielanwendung passt, der erwartete Durchlass erscheint nicht"),
}


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    herbal = read(HERBAL_EVENTS)
    biological = read(BIO_EVENTS)
    herbal_profiles = {row["page"]: row for row in read(HERBAL_PROFILES)}
    bio_profiles = {row["record"]: row for row in read(BIO_PROFILES)}

    preparation_rows = []
    for page, description in PREPARATIONS.items():
        profile = herbal_profiles[page]
        preparation_rows.append(
            {
                "page": page,
                **description,
                "cards": profile["cards"],
                "statements": profile["statements"],
                "closes": profile["closes"],
                "quantity_cards": profile["quantity_cards"],
                "water_cards": profile["water_cards"],
                "press_cards": profile["press_cards"],
                "passage_cards": profile["passage_cards"],
                "heat_cards": profile["heat_cards"],
                "ingredient_cards": profile["ingredient_cards"],
                "target_cards": profile["target_cards"],
            }
        )

    matrix = []
    for record in APPLICATIONS:
        bio_subset = [row for row in biological if row["record"] == record]
        bio_ids = {row["exact_card_id"] for row in bio_subset}
        for page in PREPARATIONS:
            herb_subset = [row for row in herbal if row["page"] == page]
            herb_ids = {row["exact_card_id"] for row in herb_subset}
            common = herb_ids & bio_ids
            shared_bio_events = sum(row["exact_card_id"] in common for row in bio_subset)
            fit, reason = PROCESS_FIT[(page, record)]
            # A mnemonic ranking for the workshop exercise: process judgement is
            # primary, while observed shared cards break close choices.
            score = fit * 10 + len(common) * 2 + shared_bio_events
            matrix.append(
                {
                    "biological_record": record,
                    "biological_application_de": APPLICATIONS[record],
                    "herbal_page": page,
                    "herbal_preparation_type": PREPARATIONS[page]["preparation_type"],
                    "process_fit_0_5": fit,
                    "shared_exact_card_types": len(common),
                    "shared_biological_events": shared_bio_events,
                    "shared_exact_cards": "|".join(sorted(common)) or "NONE",
                    "workshop_pairing_score": score,
                    "reason_de": reason,
                    "direct_product_reference": "NO",
                }
            )

    selected = []
    for record in APPLICATIONS:
        candidates = [row for row in matrix if row["biological_record"] == record]
        candidates.sort(key=lambda row: (-int(row["workshop_pairing_score"]), str(row["herbal_page"])))
        best, second = candidates[:2]
        selected.append(
            {
                "biological_record": record,
                "page": bio_profiles[record]["page"],
                "application_de": APPLICATIONS[record],
                "primary_preparation_page": best["herbal_page"],
                "primary_preparation_de": PREPARATIONS[str(best["herbal_page"])]["workshop_name_de"],
                "primary_score": best["workshop_pairing_score"],
                "secondary_preparation_page": second["herbal_page"],
                "secondary_preparation_de": PREPARATIONS[str(second["herbal_page"])]["workshop_name_de"],
                "secondary_score": second["workshop_pairing_score"],
                "working_reading_de": (
                    f"Für {APPLICATIONS[record]} würde der Schreiber am ehesten den Typ „"
                    f"{PREPARATIONS[str(best['herbal_page'])]['workshop_name_de']}“ bereitstellen."
                ),
                "identity_ceiling": "ZUBEREITUNGSART_NICHT_EXAKTES_PRODUKT",
            }
        )

    usage = Counter(str(row["primary_preparation_page"]) for row in selected)
    write(
        f"{PREFIX}_4_HERBAL_PREPARATION_ARCHETYPES.tsv",
        preparation_rows,
        ["page", "preparation_type", "workshop_name_de", "supplies_de", "cards", "statements", "closes", "quantity_cards", "water_cards", "press_cards", "passage_cards", "heat_cards", "ingredient_cards", "target_cards"],
    )
    write(
        f"{PREFIX}_24_PAIR_COMPATIBILITY_MATRIX.tsv",
        matrix,
        ["biological_record", "biological_application_de", "herbal_page", "herbal_preparation_type", "process_fit_0_5", "shared_exact_card_types", "shared_biological_events", "shared_exact_cards", "workshop_pairing_score", "reason_de", "direct_product_reference"],
    )
    write(
        f"{PREFIX}_6_SELECTED_PROCESS_PAIRINGS.tsv",
        selected,
        ["biological_record", "page", "application_de", "primary_preparation_page", "primary_preparation_de", "primary_score", "secondary_preparation_page", "secondary_preparation_de", "secondary_score", "working_reading_de", "identity_ceiling"],
    )

    lines = ["# Herbal → Biological: Werkstatt-Zuordnung", ""]
    for row in selected:
        lines.extend(
            [
                f"## {row['biological_record']} / {row['page']}",
                "",
                str(row["working_reading_de"]),
                "",
                f"Zweite Möglichkeit: {row['secondary_preparation_de']} ({row['secondary_preparation_page']}).",
                "",
            ]
        )
    lines.extend(
        [
            "## Leseschlüssel",
            "",
            "Die Zuordnung benennt nur eine Zubereitungsart. Sie behauptet weder denselben",
            "Stoff noch einen direkten Seitenverweis. Ein Schreiber könnte denselben kurzen",
            "Anwendungszettel mit mehreren konkret benannten Produkten aus dem Masterexemplar",
            "füllen; genau diese Produktnamen fehlen der derzeit lesbaren gemeinsamen Schicht.",
        ]
    )
    (HERE / f"{PREFIX}_WORKSHOP_PAIRING_READING.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    summary = {
        "status": "PASS",
        "decision": "PROCESS_TYPES_PAIR_PLAUSIBLY_BUT_PRODUCTS_REMAIN_UNNAMED",
        "herbal_preparation_types": len(PREPARATIONS),
        "biological_application_records": len(APPLICATIONS),
        "pair_candidates": len(matrix),
        "selected_pairings": len(selected),
        "herbal_types_used_as_primary": len(usage),
        "primary_usage": dict(sorted(usage.items())),
        "direct_product_references": 0,
        "new_card_meanings": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 866: Herbal-to-Biological process pairing\n\n"
        "The four Herbal pages now supply four concrete preparation archetypes, and the\n"
        "six Biological records supply six application archetypes. A compact 4x6 workshop\n"
        "matrix combines process fit with already observed exact-card overlap. All four\n"
        "Herbal archetypes win at least one Biological record.\n\n"
        "The resulting chain is useful but deliberately one level above product identity:\n"
        "an application can request an aqueous base, expressed extract, measured warm batch\n"
        "or ingredient-rich passage preparation without telling us which plant product it is.\n"
        "The current ten pages therefore support preparation-type -> application-type pairing,\n"
        "not an exact Herbal-page -> Biological-station key.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
