#!/usr/bin/env python3
"""Attach complete Latin-formulary analogues to the 17 bridge cards."""

from __future__ import annotations

import csv
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
V20 = HERE.parent / "sidequest_theory_candidates_v20"

PHRASES = {
    "1b1ffdd869fb1429ad03": ("bulliat leniter; hic finiatur", "sanft sieden lassen; diesen Schritt beenden", "PROCESS_FORMULA"),
    "276a7c2d74d1143446f4": ("applica sive utere hac portione", "diese Portion auflegen oder verwenden", "APPLICATION_FORMULA"),
    "2c1a5fd92b9e3c762242": ("dum adhuc tepidum est", "solange es noch lauwarm ist", "TEMPERATURE_FORMULA"),
    "2f1c5e56e8f0ff459065": ("secundum mensuram consuetam", "nach dem üblichen Maß", "MEASURE_FORMULA"),
    "308e8ea2d5d190c498e8": ("misce duas portiones", "zwei Portionen miteinander mischen", "COMBINATION_FORMULA"),
    "4d4559019a961b834aa1": ("de eadem confectione praeparata", "aus demselben bereiteten Ansatz", "SAME_BATCH_FORMULA"),
    "6f7ff8287eddf4da9fdb": ("misce donec aequaliter incorporentur", "mischen, bis alles gleichmäßig verbunden ist", "MIXING_FORMULA"),
    "7a4bb8136330ee4e6e56": ("decoctum sive liquor praeparatus", "der bereitete Sud oder die Arbeitsflüssigkeit", "PREPARED_LIQUID_FORMULA"),
    "80ebbbbf238eee9f0aef": ("operare donec aequaliter incorporatum sit", "bearbeiten, bis es gleichmäßig homogen ist", "PROCESS_ENDPOINT_FORMULA"),
    "b5df9126607030b95175": ("donec liquor clarus currat", "bis die Flüssigkeit klar abläuft", "CLARITY_GATE_FORMULA"),
    "b5fcea1eaed06b2f2291": ("recipe et incipe sequentem introitum mensuratum", "nimm und beginne den nächsten abgemessenen Eintrag", "ENTRY_FORMULA"),
    "b921a237be883a820352": ("haec portio praesens", "diese gegenwärtige Portion", "CURRENT_PORTION_FORMULA"),
    "dcda95c81a5460feb191": ("cum praeparatione praedicta", "mit der vorgenannten Zubereitung", "FOREGOING_PREPARATION_FORMULA"),
    "dd0ecaf5e27d81befffc": ("applica loco in figura signato", "an der in der Abbildung bezeichneten Stelle anwenden", "PICTURED_LOCATION_FORMULA"),
    "dec401773c1f0347793d": ("de confectione praedicta", "aus dem vorgenannten Ansatz", "FOREGOING_BATCH_FORMULA"),
    "e0b630cb1b5df5e7105b": ("cum praeparatum fuerit", "wenn die Zubereitung fertig ist", "READINESS_FORMULA"),
    "faf321940aed922846a9": ("recipe ultimam partem signatam", "den letzten bezeichneten Anteil nehmen", "FINAL_SHARE_FORMULA"),
}


def main() -> None:
    with (V20 / "V20_CROSS_REGISTER_CARD_AUDIT.tsv").open(
            encoding="utf-8", newline="") as handle:
        cards = list(csv.DictReader(handle, delimiter="\t"))
    assert {row["exact_tuple_id"] for row in cards} == set(PHRASES)
    rows = []
    for card in cards:
        latin, german, family = PHRASES[card["exact_tuple_id"]]
        rows.append({
            "exact_tuple_id": card["exact_tuple_id"],
            "surface_realizations": card["surface_realizations"],
            "selected_English_source_function": card["selected_cross_register_default"],
            "Latin_formulary_analogue": latin,
            "German_source_paraphrase": german,
            "formula_family": family,
            "phonetic_or_language_identification": "NO",
            "working_interpretation": "WHOLE_CARD_COMPRESSES_SOURCE_PHRASE",
        })
    with (HERE / "V29_SEVENTEEN_CARD_SOURCE_PHRASEBOOK.tsv").open(
            "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "schema": "SIDEQUEST_V29_SOURCE_PHRASEBOOK_V1", "status": "PASS",
        "bridge_cards": 17, "complete_latin_analogues": 17,
        "complete_german_paraphrases": 17, "phonetic_claims": 0,
        "language_identification_claims": 0,
        "f84": {"opened": False, "queried": False, "retained": False},
        "f84r": {"opened": False, "queried": False, "retained": False},
    }
    (HERE / "V29_VALIDATION.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
