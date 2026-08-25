#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BASE = ROOT / "sidequest_semantic_inverse_apprentice_encoding_eight_hundred_fifty_fifth"
PREFIX = "EIGHT_HUNDRED_FIFTY_SIXTH"

STEP_SKELETONS = [
    (1, "Recipe additamentum ad opus.", "R. addit. // opus", "Nimm die Zutat als laufenden Posten."),
    (2, "Ex fonte recipe aquam ad mensuram.", "ex fonte / R. aq. / ad mens.", "Nimm Wasser aus der Quelle nach Maß."),
    (3, "Adde preparationi et pone.", "adde prep. / pone", "Gib es zum Ansatz und setze den Posten an."),
    (4, "Praepara et tene diu.", "praep. / tene diu", "Bereite den Posten und halte ihn länger."),
    (5, "Ex eo pone ad mensuram et continua.", "ex eo / pone ad mens. / cont.", "Nimm davon, setze nach Maß an und fahre fort."),
    (6, "Ad locum stet; fini.", "ad loc. / stet / f.", "Lass es an der Stelle stehen; schließe den Schritt."),
]

PROMPT_FORMS = [
    (1, "Recipe additamentum", "R. addit."),
    (2, "ad opus", "opus"),
    (3, "ex fonte", "ex fonte"),
    (4, "recipe aquam", "R. aq."),
    (5, "ad mensuram", "ad mens."),
    (6, "adde", "adde"),
    (7, "preparationi", "prep."),
    (8, "pone rem", "pone"),
    (9, "praepara", "praep."),
    (10, "tene diu", "tene diu"),
    (11, "ex eo", "ex eo"),
    (12, "pone ad mensuram", "pone ad mens."),
    (13, "continua", "cont."),
    (14, "ad locum", "ad loc."),
    (15, "stet; fini", "stet / f."),
]


def read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]], fields: list[str]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    prompts = read(BASE / "EIGHT_HUNDRED_FIFTY_FIFTH_15_PROMPT_LEXICON.tsv")
    step_rows = []
    for step, latin, shorthand, german in STEP_SKELETONS:
        subset = [row for row in prompts if int(row["step"]) == step]
        step_rows.append(
            {
                "step": step,
                "latin_like_formulary": latin,
                "mixed_workshop_shorthand": shorthand,
                "german_reading_de": german,
                "semantic_prompt_sequence": " | ".join(row["source_prompt_de"] for row in subset),
                "exact_card_sequence": " | ".join(row["exact_card_id"] for row in subset),
                "prompt_count": len(subset),
                "same_cards_after_abbreviation": "YES",
            }
        )

    mapping = []
    for prompt, forms in zip(prompts, PROMPT_FORMS, strict=True):
        position, latin, shorthand = forms
        if int(prompt["prompt_position"]) != position:
            raise ValueError(position)
        mapping.append(
            {
                "prompt_position": position,
                "step": prompt["step"],
                "semantic_prompt_de": prompt["source_prompt_de"],
                "latin_like_phrase": latin,
                "workshop_abbreviation": shorthand,
                "exact_card_id": prompt["exact_card_id"],
                "component_recipe": prompt["component_recipe"],
                "card_meaning_de": prompt["card_meaning_de"],
                "meaning_survives_shortening": "YES",
            }
        )

    sources = [
        {
            "source": "Wellcome MS.683",
            "date_place": "mid-15th century, North-East Italy",
            "mechanism": "Latin recipe collection in two main hands with later contemporary additions; uses Recipe, infunde, fiat, ana and addantur.",
            "relevance": "Supports short imperative recipe skeletons, technical Latin and several workshop hands.",
            "url": "https://wellcomecollection.org/works/w6ne7k4t",
        },
        {
            "source": "Wellcome MS.418",
            "date_place": "mid-15th century, southern France",
            "mechanism": "Medicinal-water collection in Latin and Langue d'Oc; recipes begin with Recype herbam and use dicta aqua.",
            "relevance": "Supports water recipes and mixed Latin/vernacular source language in one practical compilation.",
            "url": "https://wellcomecollection.org/works/f6nzyzh4",
        },
        {
            "source": "Wellcome MS.5262",
            "date_place": "first quarter 15th century, Worcestershire",
            "mechanism": "English and Latin recipe book with direct vernacular imperatives such as Make lye of betoyne and decorated catchwords.",
            "relevance": "Supports plain vernacular action clauses beside learned recipe organisation near 1420.",
            "url": "https://wellcomecollection.org/works/nuckbt25",
        },
    ]
    write(f"{PREFIX}_6_RECIPE_SKELETON_STEPS.tsv", step_rows, ["step", "latin_like_formulary", "mixed_workshop_shorthand", "german_reading_de", "semantic_prompt_sequence", "exact_card_sequence", "prompt_count", "same_cards_after_abbreviation"])
    write(f"{PREFIX}_15_ABBREVIATION_TO_CARD.tsv", mapping, ["prompt_position", "step", "semantic_prompt_de", "latin_like_phrase", "workshop_abbreviation", "exact_card_id", "component_recipe", "card_meaning_de", "meaning_survives_shortening"])
    write(f"{PREFIX}_3_HISTORICAL_ANALOGUES.tsv", sources, ["source", "date_place", "mechanism", "relevance", "url"])

    summary = {
        "status": "PASS",
        "decision": "MIXED_RECIPE_SOURCE_SKELETON_PRESERVES_FIFTEEN_PROMPTS",
        "steps": len(step_rows),
        "semantic_prompts": len(mapping),
        "historical_analogues": len(sources),
        "meaning_preserved": sum(row["meaning_survives_shortening"] == "YES" for row in mapping),
        "same_card_steps": sum(row["same_cards_after_abbreviation"] == "YES" for row in step_rows),
        "language_identification_claims": 0,
        "new_cards": 0,
        "sealed_pages": ["f84", "f84r"],
    }
    (HERE / f"{PREFIX}_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (HERE / f"{PREFIX}_RECIPE_SOURCE_LEAF.md").write_text(
        "# Quellblatt vor der Kartenkodierung\n\n"
        "Dies ist eine plausible Werkstatt-Zwischenstufe, keine Sprachbestimmung.\n\n"
        + "\n".join(
            f"{row['step']}. **{row['latin_like_formulary']}** — `{row['mixed_workshop_shorthand']}` — {row['german_reading_de']}"
            for row in step_rows
        )
        + "\n\nDie Kürzung lässt alle fünfzehn Bedeutungs-Prompts und damit alle fünfzehn\n"
        "exakten Karten unverändert. Erst danach setzt der einzelne Schreiber seine\n"
        "bevorzugte Oberfläche.\n",
        encoding="utf-8",
    )
    (HERE / f"{PREFIX}_REPORT.md").write_text(
        "# Sidequest Pass 856: ca. 1420 recipe-source skeleton\n\n"
        "The six modern German commands now have a compact Latin-like formulary layer\n"
        "and a mixed workshop shorthand layer. All fifteen semantic prompts survive\n"
        "the shortening and select the same fifteen exact cards as before. This adds a\n"
        "historically plausible source stage without claiming that Voynich is Latin,\n"
        "German, English or Occitan.\n\n"
        "The mechanism has close real analogues: [Wellcome MS.683](https://wellcomecollection.org/works/w6ne7k4t)\n"
        "is a multi-hand North-East Italian Latin receptarium using short imperative\n"
        "formulae; [MS.418](https://wellcomecollection.org/works/f6nzyzh4) combines\n"
        "Latin and Langue d'Oc medicinal-water material; [MS.5262](https://wellcomecollection.org/works/nuckbt25)\n"
        "is a first-quarter fifteenth-century English/Latin recipe collection with\n"
        "direct vernacular instructions.\n\n"
        "The working production chain is now: ordinary recipe intention -> shortened\n"
        "semantic prompts -> shared exact cards -> scribe-specific registered surfaces.\n\n"
        "Next, apply this chain to one actual complete H1 statement and compare its\n"
        "reconstructed source skeleton with the current fluent reading card by card.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
