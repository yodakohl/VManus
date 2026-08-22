#!/usr/bin/env python3
"""V35 creative sidequest: encode new instructions with the frozen V25 card lexicon."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_theory_candidates_v25/V25_SELECTED_COMPLETE_TRANSLATION_LEDGER.tsv"


RECIPES = [
    {
        "id": "NEW01_SCABIOSA_RED_WINE",
        "owner": "pictured Scabiosa/Succisa candidate",
        "german": "Nimm die faserige untere Wurzel, wasche sie in fließendem Wasser, gib Rotwein zu, koche sanft und trinke den Auszug gegen Magenschmerz.",
        "template": "HERBAL_OPEN_CLAUSES_THEN_COMMITTED_USE",
        "fields": [
            ["take the fibrous lower root", "wash it in running water"],
            ["add red wine", "boil gently; close the rubric"],
            ["drink it for pain of the stomach"],
        ],
    },
    {
        "id": "NEW02_VIOLET_WARM_POULTICE",
        "owner": "pictured Viola candidate",
        "german": "Bereite aus den Blättern einen warmen Umschlag, mische ihn mit Honig und binde ihn warm auf die geschwollene Stelle.",
        "template": "HERBAL_PREPARATION_AND_APPLICATION",
        "fields": [
            ["make a warm poultice from its leaves", "mix it with honey"],
            ["apply it while warm", "bind it upon a swollen place"],
        ],
    },
    {
        "id": "NEW03_ALLIUM_WOUND_WASH",
        "owner": "pictured broad Allium/ramsons candidate",
        "german": "Beginne den nächsten abgemessenen Eintrag, setze die übliche Menge in Weißwein an und wasche die wunde Stelle einmal.",
        "template": "MEASURED_HERBAL_WASH",
        "fields": [
            ["begin the next measured entry", "in the stated or usual measure"],
            ["steep it in white wine", "wash the sore place once"],
        ],
    },
    {
        "id": "NEW04_SUNDEW_HONEY_APPLICATION",
        "owner": "pictured Drosera/sundew candidate",
        "german": "Setze die übliche Menge in Weißwein an, mische sie mit Honig und trage sie warm an der in der Zeichnung bezeichneten Stelle auf.",
        "template": "HERBAL_MEDIUM_MIX_APPLICATION",
        "fields": [
            ["in the stated or usual measure", "steep it in white wine"],
            ["mix it with honey", "apply it while warm", "apply it at the place indicated by the drawing"],
        ],
    },
    {
        "id": "NEW05_COMMON_WARM_BATH",
        "owner": "generic Biological bath station",
        "german": "Gib sauberes Wasser zu, temperiere die Arbeitsflüssigkeit lauwarm und bade darin; beende die Anweisung.",
        "template": "BIO_WATER_TEMPER_IMMERSE_COMMIT",
        "fields": [
            ["add clean water; close the rubric"],
            ["temper the working liquid and keep it lukewarm"],
            ["bathe or immerse in the tempered warm liquid; end this instruction"],
        ],
    },
    {
        "id": "NEW06_FILTER_REST_APPLICATION",
        "owner": "generic Biological preparation vessel",
        "german": "Rühre gleichmäßig, seihe durch ein Tuch klar, lasse die Flüssigkeit bis zur Bereitschaft stehen und trage sie an der bezeichneten Stelle auf.",
        "template": "BIO_MIX_FILTER_REST_APPLY",
        "fields": [
            ["stir until evenly mixed", "through a cloth", "strain it clear; close the rubric"],
            ["let it stand until ready; end this instruction"],
            ["apply it at the place indicated by the drawing"],
        ],
    },
    {
        "id": "NEW07_LOCAL_RINSE_DRAIN",
        "owner": "generic Biological local conduit/outlet",
        "german": "Spüle die bezeichnete Stelle einmal, bis die Flüssigkeit klar läuft, und lasse die verbrauchte Flüssigkeit in das untere Auffanggefäß ablaufen.",
        "template": "BIO_RINSE_UNTIL_CLEAR_DRAIN",
        "fields": [
            ["rinse the indicated place once; end this instruction"],
            ["until the liquid runs clear"],
            ["let the spent liquid drain into the lower receiving vessel; end this instruction"],
        ],
    },
    {
        "id": "NEW08_MEASURED_WHITE_WINE_BATCH",
        "owner": "generic pictured medicinal simple",
        "german": "Beginne einen abgemessenen Eintrag, gib in der üblichen Menge Weißwein zu, rühre gleichmäßig und lasse den Ansatz bis zur Bereitschaft stehen.",
        "template": "HERBAL_MEASURE_MIX_REST",
        "fields": [
            ["begin the next measured entry", "in the stated or usual measure", "add white wine"],
            ["stir until evenly mixed"],
            ["let it stand until ready; end this instruction"],
        ],
    },
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_tsv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, delimiter="\t", fieldnames=fields, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    HERE.mkdir(parents=True, exist_ok=True)
    with SOURCE.open(encoding="utf-8", newline="") as f:
        source = [r for r in csv.DictReader(f, delimiter="\t") if r["ledger_scope"] == "GDT327_PROSE"]

    by_meaning: dict[str, list[dict]] = defaultdict(list)
    by_surface_meanings: dict[str, set[str]] = defaultdict(set)
    for row in source:
        by_meaning[row["default_English"]].append(row)
        by_surface_meanings[row["surface"]].add(row["default_English"])

    chosen = {}
    for meaning in {m for recipe in RECIPES for field in recipe["fields"] for m in field}:
        rows = by_meaning.get(meaning, [])
        if not rows:
            raise SystemExit(f"missing frozen meaning: {meaning}")
        id_counts = Counter(r["exact_tuple_id"] for r in rows)
        tuple_id = sorted(id_counts, key=lambda x: (-id_counts[x], x))[0]
        surface_counts = Counter(r["surface"] for r in rows if r["exact_tuple_id"] == tuple_id)
        surface = sorted(surface_counts, key=lambda x: (-surface_counts[x], x))[0]
        chosen[meaning] = {
            "tuple_id": tuple_id,
            "surface": surface,
            "support_events": len(rows),
            "support_folios": len({r["page"] for r in rows}),
            "surface_meaning_count": len(by_surface_meanings[surface]),
        }

    enc_rows = []
    round_rows = []
    for recipe in RECIPES:
        flat = []
        for field_no, meanings in enumerate(recipe["fields"], 1):
            for card_no, meaning in enumerate(meanings, 1):
                item = chosen[meaning]
                flat.append(item)
                enc_rows.append({
                    "recipe_id": recipe["id"],
                    "pictured_owner": recipe["owner"],
                    "template": recipe["template"],
                    "field_no": field_no,
                    "card_no": card_no,
                    "exact_tuple_id": item["tuple_id"],
                    "selected_surface": item["surface"],
                    "intended_default_English": meaning,
                    "support_events": item["support_events"],
                    "support_folios": item["support_folios"],
                    "surface_meaning_count": item["surface_meaning_count"],
                })
        decoded_exact = [next(m for m, x in chosen.items() if x["tuple_id"] == item["tuple_id"]) for item in flat]
        intended = [m for field in recipe["fields"] for m in field]
        surface_ambiguous = sum(item["surface_meaning_count"] > 1 for item in flat)
        round_rows.append({
            "recipe_id": recipe["id"],
            "german_instruction": recipe["german"],
            "field_count": len(recipe["fields"]),
            "card_count": len(flat),
            "exact_card_roundtrip": str(decoded_exact == intended).upper(),
            "surface_ambiguous_cards": surface_ambiguous,
            "surface_sequence": " | ".join(" ".join(chosen[m]["surface"] for m in field) for field in recipe["fields"]),
            "interpretation_status": "CREATIVE_GENERATIVE_TEST_NOT_DECIPHERMENT",
        })

    enc = HERE / "V35_NEW_RECIPE_ENCODINGS.tsv"
    rnd = HERE / "V35_ROUNDTRIP_RESULTS.tsv"
    write_tsv(enc, enc_rows, list(enc_rows[0]))
    write_tsv(rnd, round_rows, list(round_rows[0]))

    summary = {
        "schema": "SIDEQUEST_V35_PRODUCTIVE_WRITING_TEST_V1",
        "status": "PASS_CREATIVE_GENERATIVE_TEST",
        "source": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha(SOURCE),
        "recipe_count": len(RECIPES),
        "encoded_card_count": len(enc_rows),
        "distinct_frozen_meanings_used": len(chosen),
        "exact_roundtrip_pass_count": sum(r["exact_card_roundtrip"] == "TRUE" for r in round_rows),
        "new_tuple_ids_created": 0,
        "new_surface_forms_created": 0,
        "f84_rows_accessed": 0,
        "f84r_rows_accessed": 0,
        "outputs": {enc.name: sha(enc), rnd.name: sha(rnd)},
    }
    (HERE / "V35_VALIDATION.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
