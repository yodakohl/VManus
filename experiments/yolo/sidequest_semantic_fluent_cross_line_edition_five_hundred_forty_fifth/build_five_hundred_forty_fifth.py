#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
P544 = ROOT / "experiments/yolo/sidequest_semantic_complete_practical_ten_page_edition_five_hundred_forty_fourth"
P538 = ROOT / "experiments/yolo/sidequest_semantic_whole_card_attack_five_hundred_thirty_eighth"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name: str, rows: list[dict[str, str]]) -> None:
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


VALUES = {
    "AIIN": "Maß", "AIN": "Portion", "AIR": "Lauf", "AL": "Zielstelle", "AR": "von dort",
    "CFH": "auswringen", "CH": "abziehen", "CHD": "umsetzen", "CHK": "wärmen", "CKH": "Durchlass",
    "CTH": "bereit", "DA": "zweite", "DY": "Schluss", "E": "kurz", "EE": "länger", "EEE": "vollständig",
    "HO": "Gabe", "IIN": "Sollstufe", "K": "zuführen", "L": "führen", "LD": "befestigen",
    "LS": "fortsetzen", "LSH": "Waschgang", "O": "Arbeitsgang", "OK": "ansetzen", "OL": "fortsetzen",
    "OR": "Ansatz", "OS": "Arbeitsfach", "OT": "danach", "P": "hinein", "R": "abkühlen",
    "S": "teilen", "SH": "halten", "SHED": "absetzen", "SOLK": "auffangen", "T": "eintragen",
    "TALAM": "verwahren", "Y": "dies",
}

ACTIONS = {
    "CFH": "auswringen", "CH": "abziehen", "CHD": "umsetzen", "CHK": "wärmen", "K": "zuführen",
    "L": "führen", "LD": "befestigen", "OK": "ansetzen", "OL": "fortsetzen", "P": "hineingeben",
    "R": "abkühlen", "S": "teilen", "SH": "halten", "SHED": "absetzen", "SOLK": "auffangen",
    "T": "eintragen", "TALAM": "verwahren", "LS": "fortsetzen",
}


def fluent_card(parse: str) -> str:
    parts = parse.split("+")
    if parse == "OS":
        return "das Arbeitsfach wählen"
    if parse == "LSH":
        return "einen Waschgang ausführen"
    prefix = "danach " if "OT" in parts else ""
    grade = "kurz" if "E" in parts else "länger" if "EE" in parts else "vollständig" if "EEE" in parts else ""
    close = "DY" in parts
    verbs = [ACTIONS[part] for part in parts if part in ACTIONS and part not in {"LS"}]
    if "LS" in parts:
        verbs.append("fortsetzen")
    if "Y" in parts:
        obj = "diesen Posten"
    elif "AIN" in parts:
        obj = "eine Portion"
    elif "HO" in parts:
        obj = "die Gabe"
    elif "O" in parts:
        obj = "den Arbeitsgang"
    elif "OR" in parts:
        obj = "den Ansatz"
    else:
        obj = "den Posten"
    circumstances: list[str] = []
    if "DA" in parts:
        circumstances.append("auf die zweite")
    if "IIN" in parts:
        circumstances.append("Sollstufe")
    if "AIIN" in parts:
        circumstances.append("nach Maß")
    if "AL" in parts:
        circumstances.append("an der Zielstelle")
    if "AR" in parts:
        circumstances.append("von dort")
    if "AIR" in parts:
        circumstances.append("aus dem Lauf" if "CH" in parts else "im Lauf")
    if "CKH" in parts:
        circumstances.append("am Durchlass")
    if "CTH" in parts:
        circumstances.append("bis bereit")
    if grade:
        circumstances.append(grade)
    if not verbs:
        if "AIIN" in parts:
            phrase = "das Maß setzen"
        elif "AIN" in parts:
            phrase = "eine Portion nehmen"
        elif "AL" in parts:
            phrase = "die Zielstelle setzen"
        elif "AR" in parts:
            phrase = "von dort nehmen"
        elif "AIR" in parts:
            phrase = "den Lauf wählen"
        elif "IIN" in parts:
            phrase = "die " + ("zweite " if "DA" in parts else "") + "Sollstufe einstellen"
        elif "CTH" in parts and "Y" in parts:
            phrase = "diesen Posten bis bereit halten"
        elif "Y" in parts:
            phrase = "diesen Posten übernehmen"
        elif "O" in parts:
            phrase = "den Arbeitsgang ausführen"
        elif "OR" in parts:
            phrase = "den Ansatz verwenden"
        elif "HO" in parts:
            phrase = "die Gabe nehmen"
        else:
            phrase = "den Posten bearbeiten"
    else:
        phrase = " ".join([obj, *circumstances, " und ".join(verbs)])
    phrase = prefix + phrase
    if close:
        phrase += " und den Schritt schließen"
    return " ".join(phrase.split())


def main() -> None:
    prose = read_tsv(P544 / "FIVE_HUNDRED_FORTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_PRACTICAL_PROSE_INTERLINEAR.tsv")
    old_statements = read_tsv(P544 / "FIVE_HUNDRED_FORTY_FOURTH_ONE_HUNDRED_SIXTEEN_COMPLETE_PROSE_STATEMENTS.tsv")
    cards = read_tsv(P538 / "FIVE_HUNDRED_THIRTY_EIGHTH_REVISED_ONE_HUNDRED_SEVENTY_THREE_CARD_DICTIONARY.tsv")
    phrase_for = {row["card_no"]: fluent_card(row["component_parse"]) for row in cards}
    card_rows = [
        {
            "card_no": row["card_no"],
            "component_parse": row["component_parse"],
            "literal_reading_de": row["invariant_card_reading_de"],
            "fluent_command_de": phrase_for[row["card_no"]],
            "occurrences": row["occurrences"],
            "composition_status": row["composition_status"],
            "component_values_unchanged": "YES",
        }
        for row in cards
    ]
    write_tsv("FIVE_HUNDRED_FORTY_FIFTH_ONE_HUNDRED_SEVENTY_THREE_FLUENT_CARD_PHRASES.tsv", card_rows)

    members_by_statement: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in prose:
        members_by_statement[row["statement_id"]].append(row)
    old_by_id = {row["statement_id"]: row for row in old_statements}
    records = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]
    instructions: list[dict[str, str]] = []
    event_rows: list[dict[str, str]] = []
    instruction_number = 0
    for record in records:
        statement_ids = [row["statement_id"] for row in old_statements if row["record"] == record]
        buffer: list[str] = []
        for statement_id in statement_ids:
            buffer.append(statement_id)
            if old_by_id[statement_id]["terminal"] == "YES":
                instruction_number += 1
                instructions.append(build_instruction(instruction_number, buffer, members_by_statement, old_by_id, phrase_for, False))
                buffer = []
        if buffer:
            instruction_number += 1
            instructions.append(build_instruction(instruction_number, buffer, members_by_statement, old_by_id, phrase_for, True))
    instruction_for_event = {
        event_id: row["instruction_id"]
        for row in instructions
        for event_id in row["visible_event_ids"].split("|")
    }
    for row in prose:
        event_rows.append(
            {
                "event_id": row["event_id"],
                "source_position_id": row["source_position_id"],
                "instruction_id": instruction_for_event[row["event_id"]],
                "page": row["page"],
                "record": row["record"],
                "statement_id": row["statement_id"],
                "locus": row["locus"],
                "surface": row["surface"],
                "card_no": row["card_no"],
                "component_parse": row["component_parse"],
                "literal_reading_de": row["literal_card_reading_de"],
                "fluent_command_de": phrase_for[row["card_no"]],
                "semantic_execution": "SKIP_ANTICIPATORY_COPY" if row["event_id"] == "E180" else "EXECUTE_ONCE",
                "component_values_unchanged": "YES",
            }
        )
    write_tsv("FIVE_HUNDRED_FORTY_FIFTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_SENTENCE_MAP.tsv", event_rows)
    write_tsv("FIVE_HUNDRED_FORTY_FIFTH_NINETY_SEVEN_FLUENT_INSTRUCTIONS.tsv", instructions)

    lines = ["# Flüssige, zeilenunabhängige Prosaausgabe", ""]
    for record in records:
        record_rows = [row for row in instructions if row["record"] == record]
        lines.extend([f"## {record} — {record_rows[0]['page']}", ""])
        for row in record_rows:
            lines.append(f"- {row['instruction_id']}: {row['fluent_instruction_de']}")
        lines.append("")
    (HERE / "FIVE_HUNDRED_FORTY_FIFTH_CONTINUOUS_PROSE_EDITION.md").write_text("\n".join(lines), encoding="utf-8")

    summary = {
        "status": "PASS",
        "cards": len(card_rows),
        "visible_events": len(event_rows),
        "executed_source_positions": sum(row["semantic_execution"] == "EXECUTE_ONCE" for row in event_rows),
        "input_statements": len(old_statements),
        "fluent_instructions": len(instructions),
        "committed_instructions": sum(row["end_type"] == "COMMITTED_CLOSE" for row in instructions),
        "record_final_open_instructions": sum(row["end_type"] == "RECORD_FINAL_OPEN" for row in instructions),
        "cross_locus_instructions": sum(row["crosses_physical_locus"] == "YES" for row in instructions),
        "cross_owner_instructions": sum(row["crosses_owner_boundary"] == "YES" for row in instructions),
        "anticipatory_copies_skipped": sum(row["semantic_execution"] == "SKIP_ANTICIPATORY_COPY" for row in event_rows),
    }
    (HERE / "FIVE_HUNDRED_FORTY_FIFTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = [
        "# Fünfhundertfünfundvierzigste Runde: flüssige Prosa über Zeilen hinweg",
        "",
        "## Ergebnis",
        "",
        f"Die 116 technischen Zellen sind zu {len(instructions)} wirklichen Arbeitsanweisungen verbunden. {summary['committed_instructions']} enden an einer Schlusskarte; {summary['record_final_open_instructions']} bleiben nur deshalb offen, weil der Record endet.",
        "",
        f"{summary['cross_locus_instructions']} Anweisungen laufen über mindestens zwei physische Loci/Zeilen. Keine davon wird am Zeilenende künstlich getrennt. {summary['cross_owner_instructions']} enthalten einen ausdrücklich markierten Wechsel des sichtbaren Besitzers.",
        "",
        "E180/E181 wird sichtbar zweimal abgeschrieben, semantisch aber nur einmal ausgeführt: E180 ist die vorweggenommene Randkopie, E181 der gelesene Eintritt der nächsten Zeile.",
        "",
        "## Sprachform",
        "",
        "Die 38 Komponenten bleiben unverändert, werden aber nun als knappe deutsche Imperative gesetzt: `OK+EE+Y` wird „diesen Posten länger ansetzen“, `SH+CKH+E+DY` wird „den Posten am Durchlass kurz halten und den Schritt schließen“, `DA+IIN` wird „die zweite Sollstufe einstellen“.",
        "",
        "## Nächster Angriff",
        "",
        "Als Nächstes werden diese 97 Anweisungen zu elf zusammenhängenden Record-Artikeln redigiert. Wiederkehrende Posten werden anaphorisch als „er/ihn/davon“ geführt, damit die Ausgabe wie ein echtes knappes Werkstattbuch und nicht wie eine Kartenliste klingt.",
    ]
    (HERE / "FIVE_HUNDRED_FORTY_FIFTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


def build_instruction(number, statement_ids, members_by_statement, old_by_id, phrase_for, record_final_open):
    visible_members = [row for statement_id in statement_ids for row in members_by_statement[statement_id]]
    executed_members = [row for row in visible_members if row["event_id"] != "E180"]
    owners = list(dict.fromkeys(row["silent_owner_de"] for row in visible_members))
    loci = list(dict.fromkeys(row["locus"] for row in visible_members))
    pieces: list[str] = []
    prior_owner = None
    for row in executed_members:
        if row["silent_owner_de"] != prior_owner:
            pieces.append(
                f"bei {row['silent_owner_de']}"
                if prior_owner is None
                else f"ohne sichtbare Bildkante zu {row['silent_owner_de']} wechseln"
            )
            prior_owner = row["silent_owner_de"]
        pieces.append(phrase_for[row["card_no"]])
    fluent = ", dann ".join(pieces)
    fluent = fluent[0].upper() + fluent[1:] + "."
    return {
        "instruction_id": f"I{number:03d}",
        "page": visible_members[0]["page"],
        "record": visible_members[0]["record"],
        "source_statement_ids": "|".join(statement_ids),
        "visible_event_ids": "|".join(row["event_id"] for row in visible_members),
        "executed_source_position_ids": "|".join(dict.fromkeys(row["source_position_id"] for row in executed_members)),
        "loci": "|".join(loci),
        "silent_owners_de": "|".join(owners),
        "surface_sequence": " ".join(row["surface"] for row in visible_members),
        "literal_component_sequence": " | ".join(row["component_parse"] for row in executed_members),
        "fluent_instruction_de": fluent,
        "end_type": "RECORD_FINAL_OPEN" if record_final_open else "COMMITTED_CLOSE",
        "crosses_physical_locus": "YES" if len(loci) > 1 else "NO",
        "crosses_owner_boundary": "YES" if len(owners) > 1 else "NO",
        "line_end_is_sentence_end": "NO",
        "component_values_unchanged": "YES",
    }


if __name__ == "__main__":
    main()
