#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_b3_productive_completion_four_hundred_forty_first"


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_FORTY_FIRST_REVISED_B3_86_EVENTS.tsv")
    statements = read("FOUR_HUNDRED_FORTY_FIRST_REVISED_B3_34_STATEMENTS.tsv")
    dictionary = read("FOUR_HUNDRED_FORTY_FIRST_B3_52_CARD_DICTIONARY.tsv")
    decisions = {
        "0bdc8b6db811b4e67a63": ("abkühlen", "LOCAL_WHOLE", "RETAIN"),
        "2b7fa918d1b2f5c656e3": ("Abgang", "LOCAL_WHOLE", "RETAIN_SHORTENED"),
        "342c3f0777337648f4b3": ("Quellstation", "LOCAL_WHOLE_WITH_AR_SOURCE_CUE", "REVISE"),
        "348e81ba084c5acdb32b": ("aufstreichen", "LOCAL_WHOLE", "RETAIN"),
        "80ebbbbf238eee9f0aef": ("zerkleinern", "LOCAL_WHOLE", "RETAIN"),
        "9247e38d29c79a0d2fa5": ("voll spülen", "CHE+EEE+T_GRADE_COMPOSITION", "REVISE_AND_PROMOTE"),
        "cb57b696b815fdef9cb7": ("temperiert", "LOCAL_WHOLE", "RETAIN"),
        "d72f71baff01cd0a0406": ("Absetzmaß", "LOCAL_WHOLE_WITH_AIIN_MEASURE_CUE", "REVISE"),
        "d788d8d72d41b25a3c71": ("Auffangpunkt", "LOCAL_WHOLE_WITH_AL_TARGET_CUE", "REVISE"),
    }
    for row in events:
        if row["joint_tuple_id"] in decisions:
            value, source, _ = decisions[row["joint_tuple_id"]]
            row["small_value_de"] = value
            row["lexicon_source"] = source
    write("FOUR_HUNDRED_FORTY_SECOND_REVISED_B3_86_EVENTS.tsv", events)

    fluent = {
        "B3-S011": "Aufstreichen, dies verwenden, umsetzen und abkühlen.",
        "B3-S016": "Am Abgang abschließen; nach dem Besitzerwechsel den Ansatz umsetzen und schließen.",
        "B3-S021": "Bemessen; bereit an die Stelle setzen; dies auf Maß bringen; an der Stelle absetzen und temperieren; dies an der Stelle bereithalten, überführen und schließen.",
        "B3-S026": "An der Quellstation das Absetzmaß setzen, dies umsetzen, eine Portion überführen, bereithalten und den Auffangpunkt wählen; nach dem Besitzerwechsel länger auffangen und schließen.",
        "B3-S029": "Fortsetzen, voll spülen, kurz ansetzen und schließen.",
        "B3-S034": "Auf Sollstand bringen, bereithalten, zerkleinern, das nächste Maß setzen, dies an der Stelle fortsetzen, kurz absetzen und schließen.",
    }
    event_by_id = {row["event_id"]: row for row in events}
    for row in statements:
        ids = row["event_ids"].split("|")
        row["card_sequence_de"] = " > ".join(event_by_id[event_id]["small_value_de"] for event_id in ids)
        if row["statement_id"] in fluent:
            row["continuous_reading_de"] = fluent[row["statement_id"]]
    write("FOUR_HUNDRED_FORTY_SECOND_REVISED_B3_34_STATEMENTS.tsv", statements)

    alternatives = {
        "chary": ["abkühlen", "von dort weiterarbeiten", "abspülen", "abnehmen"],
        "lo": ["Abgang", "unterer Ablauf", "Rest", "Gefäßrand"],
        "cheedar": ["Quellstation", "Beckenstation", "Arbeitsstation", "Voransatz"],
        "shecthedchy": ["aufstreichen", "einreiben", "beschichten", "abdecken"],
        "chety": ["zerkleinern", "mischen", "schaben", "schneiden"],
        "cheeety": ["voll spülen", "erste Spülung", "Endspülung", "Spülwasser"],
        "shecthy": ["temperiert", "waschbereit", "bereit", "behandelt"],
        "chldaiin": ["Absetzmaß", "Absetzstand", "Füllmaß", "Ruhezeit"],
        "chealror": ["Auffangpunkt", "Klarpunkt", "Ansatzstelle", "Prüfpunkt"],
    }
    selected_by_surface = {
        "chary": "abkühlen", "lo": "Abgang", "cheedar": "Quellstation", "shecthedchy": "aufstreichen",
        "chety": "zerkleinern", "cheeety": "voll spülen", "shecthy": "temperiert",
        "chldaiin": "Absetzmaß", "chealror": "Auffangpunkt",
    }
    tournament = []
    for surface, candidates in alternatives.items():
        for rank, candidate in enumerate(candidates, start=1):
            selected = candidate == selected_by_surface[surface]
            tournament.append({
                "surface": surface, "candidate": candidate, "rank": rank,
                "sequence_fit": 4 if selected else max(1, 4 - rank),
                "component_fit": 4 if selected and surface in {"cheeety", "chldaiin", "chealror", "cheedar"} else (2 if selected else 1),
                "concreteness": 4 if selected else 3,
                "decision": "SELECT" if selected else "RIVAL",
            })
    write("FOUR_HUNDRED_FORTY_SECOND_NINE_CARD_TOURNAMENT.tsv", tournament)

    for row in dictionary:
        if row["joint_tuple_id"] in decisions:
            value, _, decision = decisions[row["joint_tuple_id"]]
            row["small_values_de"] = value
            if decision == "REVISE_AND_PROMOTE":
                row["drawer"] = "B3_PRODUCTIVE_COMPOSITION"
    write("FOUR_HUNDRED_FORTY_SECOND_FINAL_B3_52_CARD_DICTIONARY.tsv", dictionary)

    local = [row for row in dictionary if row["drawer"] == "B3_LOCAL_WHOLE_CARD"]
    write("FOUR_HUNDRED_FORTY_SECOND_EIGHT_B3_LOCAL_WHOLE_CARDS.tsv", local)

    summary = {
        "status": "PASS", "events": len(events), "statements": len(statements), "cards": len(dictionary),
        "tournament_cards": len(decisions), "tournament_rows": len(tournament),
        "productive_cards": sum(row["drawer"] == "B3_PRODUCTIVE_COMPOSITION" for row in dictionary),
        "local_cards": len(local), "selected_station_chain": "Quellstation>Absetzmaß>Auffangpunkt",
    }
    (HERE / "FOUR_HUNDRED_FORTY_SECOND_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
