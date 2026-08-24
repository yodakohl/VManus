#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREV = ROOT / "experiments/yolo/sidequest_semantic_biological_union_four_hundred_forty_seventh"

COMPOSITIONS = {
    "22fb87a5a83e5c3fb510": ("K+AIR", "Wasser zufuehren"),
    "1496a731803a9f48d2e1": ("R+OL", "weiter abkuehlen"),
    "0f18de177ed7c878bf95": ("L", "weiterfuehren"),
    "54e32e9c1414b20640e9": ("SH+K+CHD+DY", "gebuendelt umsetzen; Schluss"),
    "4da0f0f7b5fc7ac20067": ("R+AL", "an der Stelle abkuehlen"),
    "be0974b366c981dc1eef": ("LSH+O", "Waschgang"),
    "2e7e89e0bd12b999c280": ("LSH+E+DY", "Waschgang; Schluss"),
    "c205570c49d4d93c23d3": ("OLK+Y", "dies auffangen"),
    "a06244ef1f2b37ca44c1": ("E+OL", "kurz fortsetzen"),
    "d225b7a7b95da7aee437": ("CHD+DY", "umsetzen; Schluss"),
    "b38d70daefd663d74625": ("L+Y", "dies fuehren"),
    "2d2e37ccb2dacc53ee5a": ("SOLK+AIIN", "Auffangmass"),
    "cbb42a4fe68068325d6b": ("SH+E+DY", "kurz halten; Schluss"),
    "5eff216ba51fbfb21f22": ("L+S", "abfuehren"),
    "d4a31dbcf1ed6d9e5aa9": ("SH+E+Y", "dies kurz halten"),
    "78b3b3140714da19090d": ("AL+DY", "an der Stelle schliessen"),
    "7f68f60279efe6b28cd7": ("R+SHED+DY", "abkuehlen und absetzen; Schluss"),
    "0bdc8b6db811b4e67a63": ("AR+Y", "dies aus der Quelle nehmen"),
    "2b7fa918d1b2f5c656e3": ("L+O", "hinausfuehren"),
    "cb57b696b815fdef9cb7": ("SH+E+CTH+Y", "dies kurz bereit halten"),
    "342c3f0777337648f4b3": ("EE+D+AR", "laenger aus der Quelle fuehren"),
    "d72f71baff01cd0a0406": ("L+D+AIIN", "Abfuehrmass"),
    "d788d8d72d41b25a3c71": ("AL+R+OR", "Ansatz an der Stelle auffangen"),
    "883a6708116c342cb10b": ("K+AR", "aus dem Vorrat zufuehren"),
}

WHOLES = {
    "a7af89ab31ce5e247395": "fuellen",
    "a8f891de626fc00028e9": "gleich einstellen",
    "db729b598e89e11452e0": "teilen",
    "348e81ba084c5acdb32b": "aufstreichen",
    "80ebbbbf238eee9f0aef": "zerkleinern",
    "8c97dfde96fbc78e3355": "warm",
    "43eb9aa12959b4d5cdc9": "roh",
}

FLUENT = {
    "B1-S002": "Bemessen, Wasser zufuehren und an die Stelle setzen; denselben Posten mit einer und einer weiteren Portion fortsetzen; weiter abkuehlen, weiterfuehren und einen weiteren Ansatz zugeben; kurz an der Durchlassstelle halten, auf Mass bringen, laenger an der Stelle halten, nochmals bemessen, durchfuehren, ueberfuehren und schliessen.",
    "B1-S003": "Fortsetzen, gebuendelt umsetzen und schliessen.",
    "B1-S006": "Eine Portion zugeben, durchfuehren, weiterfuehren und an der Stelle abkuehlen.",
    "B1-S012": "Den Waschgang kurz ansetzen und schliessen.",
    "B1-S013": "Den Waschgang schliessen.",
    "B1-S014": "Dies umsetzen, auffangen, zum Auslass fuehren, fortsetzen und danach von dort weitergehen.",
    "B1-S015": "Fuellen, den Ansatz umsetzen und schliessen.",
    "B1-S017": "An der Stelle kurz fortsetzen, umsetzen und schliessen.",
    "B1-S018": "Dies fuehren, kurz halten, auf Sollstand bringen, laenger auffangen und schliessen.",
    "B2-S005": "Dies an die Stelle setzen, das Auffangmass einstellen, durchfuehren, zweimal bemessen, gleich einstellen, dies laenger waermen, abfuehren und schliessen.",
    "B2-S007": "Kurz halten und schliessen.",
    "B2-S010": "Laenger ansetzen, dies verwenden, abfuehren und den Klarauszug nehmen.",
    "B2-S015": "Dies kurz halten, laenger ansetzen und schliessen.",
    "B2-S016": "Von der Stelle hinausfuehren, teilen, auf Mass bringen, den naechsten Posten laenger halten, bemessen, kurz ansetzen, hineinfuehren und schliessen.",
    "B2-S017": "Die Waschfluessigkeit an die Stelle bringen und dort schliessen.",
    "B2-S019": "Abkuehlen, absetzen und schliessen.",
    "B3-S011": "Aufstreichen, verwenden, umsetzen und dies aus der Quelle nehmen.",
    "B3-S016": "Hinausfuehren, den Ansatz umsetzen und schliessen.",
    "B3-S021": "Bemessen und bereitstellen; an der Stelle absetzen, dies kurz bereit halten und an der Stelle ueberfuehren und schliessen.",
    "B3-S026": "Laenger aus der Quelle fuehren, das Abfuehrmass setzen, dies umsetzen, eine Portion zugeben, bereitstellen, den Ansatz an der Stelle auffangen, laenger auffangen und schliessen.",
    "B3-S034": "Auf Sollstand bringen, bereitstellen, zerkleinern, das naechste Mass nehmen, dies an der Stelle fortsetzen, kurz absetzen und schliessen.",
    "B4-S016": "Eine weitere Portion an die Stelle bringen, aus dem Vorrat zufuehren, kurz absetzen und schliessen.",
    "B5-S003": "An der Absetzstelle weiterfuehren, warm halten, an dieser Stelle umsetzen, auf Mass bringen, fortsetzen, die zweite Stufe einstellen und den laufenden Posten umsetzen.",
    "B6-S001": "Den Rohansatz laenger auffangen, diesen abkuehlen und fortsetzen; auf Mass bringen, durch das Tuch fuehren und den Ansatz zur bezeichneten Stelle fuehren.",
}


def read(name: str) -> list[dict[str, str]]:
    with (PREV / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(name: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(name)
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = read("FOUR_HUNDRED_FORTY_SEVENTH_281_EVENT_EDITION.tsv")
    for row in events:
        joint_id = row["joint_tuple_id"]
        if joint_id in COMPOSITIONS:
            row["small_value_de"] = COMPOSITIONS[joint_id][1]
            row["union_drawer"] = "PRODUCTIVE_COMPOSITION"
        elif joint_id in WHOLES:
            row["small_value_de"] = WHOLES[joint_id]
            row["union_drawer"] = "RECORD_LOCAL_LEARNED_WHOLE_CARD"
    write("FOUR_HUNDRED_FORTY_EIGHTH_281_EVENT_EDITION.tsv", events)

    values_by_joint: dict[str, set[str]] = {}
    for row in events:
        values_by_joint.setdefault(row["joint_tuple_id"], set()).add(row["small_value_de"])
    dictionary = read("FOUR_HUNDRED_FORTY_SEVENTH_124_CARD_DICTIONARY.tsv")
    for row in dictionary:
        joint_id = row["joint_tuple_id"]
        row["small_value_de"] = next(iter(values_by_joint[joint_id]))
        if joint_id in COMPOSITIONS:
            row["union_drawer"] = "PRODUCTIVE_COMPOSITION"
            row["origin_drawer"] = "PASS448_PRODUCTIVE_REANALYSIS"
        elif joint_id in WHOLES:
            row["union_drawer"] = "RECORD_LOCAL_LEARNED_WHOLE_CARD"
            row["origin_drawer"] = "PASS448_COMPACT_WHOLE_CARD"
    write("FOUR_HUNDRED_FORTY_EIGHTH_124_CARD_DICTIONARY.tsv", dictionary)

    event_by_id = {row["event_id"]: row for row in events}
    statements = read("FOUR_HUNDRED_FORTY_SEVENTH_97_STATEMENT_EDITION.tsv")
    for row in statements:
        rows = [event_by_id[event_id] for event_id in row["event_ids"].split("|")]
        row["card_sequence_de"] = " > ".join(event["small_value_de"] for event in rows)
        if row["statement_id"] in FLUENT:
            row["continuous_reading_de"] = FLUENT[row["statement_id"]]
    write("FOUR_HUNDRED_FORTY_EIGHTH_97_STATEMENT_EDITION.tsv", statements)

    composition_rows = []
    for joint_id, (composition, value) in COMPOSITIONS.items():
        matching = [row for row in events if row["joint_tuple_id"] == joint_id]
        old = next(row for row in read("FOUR_HUNDRED_FORTY_SEVENTH_31_LOCAL_WHOLE_CARDS.tsv") if row["joint_tuple_id"] == joint_id)
        composition_rows.append({
            "joint_tuple_id": joint_id, "surfaces": old["surfaces"], "events": len(matching),
            "event_ids": "|".join(row["event_id"] for row in matching), "composition": composition,
            "old_local_value_de": old["small_value_de"], "new_value_de": value,
        })
    write("FOUR_HUNDRED_FORTY_EIGHTH_24_PROMOTED_COMPOSITIONS.tsv", composition_rows)

    whole_rows = []
    for joint_id, value in WHOLES.items():
        old = next(row for row in read("FOUR_HUNDRED_FORTY_SEVENTH_31_LOCAL_WHOLE_CARDS.tsv") if row["joint_tuple_id"] == joint_id)
        whole_rows.append({
            "joint_tuple_id": joint_id, "surfaces": old["surfaces"], "events": old["events"],
            "event_ids": old["event_ids"], "old_value_de": old["small_value_de"], "compact_whole_value_de": value,
        })
    write("FOUR_HUNDRED_FORTY_EIGHTH_SEVEN_LOCAL_WHOLE_CARDS.tsv", whole_rows)

    roots = [
        {"root": "AIR", "value_de": "Wasser", "workshop_use": "K+AIR Wasser zufuehren"},
        {"root": "AR", "value_de": "Quelle oder Vorrat", "workshop_use": "K+AR zufuehren; AR+Y aus Quelle nehmen"},
        {"root": "AL", "value_de": "Stelle", "workshop_use": "R+AL abkuehlen; AL+DY dort schliessen"},
        {"root": "K", "value_de": "zufuehren", "workshop_use": "nimmt AIR AIN oder AR als Inhalt"},
        {"root": "L", "value_de": "fuehren", "workshop_use": "L+Y dies fuehren; L+O hinausfuehren"},
        {"root": "OL", "value_de": "fortsetzen", "workshop_use": "E+OL kurz fortsetzen; R+OL weiter abkuehlen"},
        {"root": "R", "value_de": "abkuehlen", "workshop_use": "R+OL R+AL R+SHED und RALY"},
        {"root": "LSH", "value_de": "Waschgang", "workshop_use": "offen oder mit DY geschlossen"},
        {"root": "SOLK", "value_de": "auffangen", "workshop_use": "SOLK+AIIN Auffangmass"},
        {"root": "SH", "value_de": "halten", "workshop_use": "SH+E+Y offen; SH+E+DY geschlossen"},
    ]
    write("FOUR_HUNDRED_FORTY_EIGHTH_LOCAL_ROOT_CARD.tsv", roots)

    summary = {
        "status": "PASS", "cards": len(dictionary), "events": len(events), "statements": len(statements),
        "promoted_compositions": len(COMPOSITIONS), "remaining_local_wholes": len(WHOLES),
        "productive_cards": sum(row["union_drawer"] == "PRODUCTIVE_COMPOSITION" for row in dictionary),
        "portable_whole_cards": sum(row["union_drawer"] == "PORTABLE_LEARNED_WHOLE_CARD" for row in dictionary),
        "local_whole_cards": sum(row["union_drawer"] == "RECORD_LOCAL_LEARNED_WHOLE_CARD" for row in dictionary),
        "productive_events": sum(row["union_drawer"] == "PRODUCTIVE_COMPOSITION" for row in events),
        "portable_whole_events": sum(row["union_drawer"] == "PORTABLE_LEARNED_WHOLE_CARD" for row in events),
        "local_whole_events": sum(row["union_drawer"] == "RECORD_LOCAL_LEARNED_WHOLE_CARD" for row in events),
    }
    (HERE / "FOUR_HUNDRED_FORTY_EIGHTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
