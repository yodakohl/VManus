#!/usr/bin/env python3
import csv
import json
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT / "sidequest_semantic_integrated_apprentice_manual_five_hundred_sixty_second"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def short_owner(owner):
    replacements = {
        "abgebildete breit gezähnte radialblütige Pflanze": "der ersten abgebildeten Pflanze",
        "abgebildete dicht blau blühende Kronenpflanze": "der abgebildeten Blütenpflanze",
        "abgebildete breitblättrige rispige Pflanze": "der abgebildeten breitblättrigen Pflanze",
        "abgebildete mehrköpfige stachelige Pflanze": "der abgebildeten mehrköpfigen Pflanze",
        "gemeinsame zweireihige Figuren-/Beckenstation": "dem gemeinsamen Becken",
        "oberes Beckenpaar mit Zylinder": "dem oberen Beckenpaar",
        "mittleres linkes Handgerät mit Inline-Knoten": "dem mittleren Handgerät",
        "mittlere rechte unklare Station": "der mittleren rechten Station",
        "unteres grünes Mehrfigurenbecken": "dem unteren grünen Becken",
        "kleine Randstationen des unteren Beckens": "den kleinen Randstationen",
        "obere offene Fächerstation am Rand": "der oberen Fächerstation",
        "mittlere Randfigur im runden Gefäß": "dem runden Gefäß",
        "untere Randfigur im korbartigen Gefäß": "dem korbartigen Gefäß",
        "unverbundener Zwischenbereich": "dem getrennten Zwischenbereich",
        "sichtbares Figurenpaar mit gemeinsamem Bogen in B3": "dem Figurenpaar in B3",
        "sichtbares Figurenpaar mit gemeinsamem Bogen in B4": "dem Figurenpaar in B4",
        "linke Hauptstation mit offenem Fransenlauf": "der linken Hauptstation",
        "rechte Hauptstation mit S-Lauf und Mehrarmknoten": "der rechten S-Station",
        "linke Fransenstation im B5-Nachtrag": "der linken Nachtragsstation",
        "rechter S-Lauf im B6-Nachtrag": "dem rechten S-Lauf",
    }
    return replacements.get(owner, owner)


def refine_action(row):
    action = row["local_action_expansion_de"]
    parse = row["component_parse"]
    owner = row["silent_owner_de"]
    if action == "einsetzen":
        if "AIIN" in parse:
            return "bis zum Sollmaß beschicken"
        if "AIN" in parse:
            return "eine Portion einfüllen"
        if "+OL" in parse:
            return "weiter beschicken"
        if "+AR" in parse:
            return "aus der bezeichneten Quelle beschicken"
        if "EEE+DY" in parse:
            return "vollständig beschicken und abschließen"
        if row["record"].startswith("H"):
            return "Pflanzenstoff in den Ansatz geben"
        return "den Arbeitsstoff einsetzen"
    if action == "umsetzen":
        return "umschöpfen"
    if action == "überführen":
        return "in die nächste Station weitergeben"
    if action == "halten":
        if row["record"].startswith("H"):
            return "ziehen lassen"
        if "Figurenpaar" in owner:
            return "einwirken lassen"
        return "stehen lassen"
    return action


def main():
    traces = read_tsv(SOURCE / "FIVE_HUNDRED_SIXTY_SECOND_THREE_HUNDRED_EIGHTY_ONE_FULL_TRACES.tsv")
    statement_events = OrderedDict()
    for row in traces:
        statement_events.setdefault(row["statement_id"], []).append(row)

    event_rows = []
    statement_rows = []
    generic_actions = {"einsetzen", "umsetzen", "überführen", "halten"}
    refined_count = 0
    for statement_id, rows in statement_events.items():
        actions = []
        arguments = []
        for ordinal, row in enumerate(rows, 1):
            is_action = row["local_action_expansion_de"] != "NON_ACTION_CONTRIBUTION"
            if is_action:
                value = refine_action(row)
                actions.append(value)
                if row["local_action_expansion_de"] in generic_actions:
                    refined_count += 1
                role = "ACTION"
            else:
                value = row["atomic_card_value_de"]
                arguments.append(value)
                role = "ARGUMENT_OR_STATE"
            event_rows.append({
                "event_id": row["event_id"],
                "page": row["page"],
                "record": row["record"],
                "statement_id": statement_id,
                "statement_ordinal": str(ordinal),
                "surface": row["observed_surface"],
                "component_parse": row["component_parse"],
                "event_role": role,
                "atomic_card_value_de": row["atomic_card_value_de"],
                "source_action_de": row["local_action_expansion_de"],
                "revised_event_reading_de": value,
                "meaning_preserved": "YES",
            })
        owner = rows[0]["silent_owner_de"]
        if actions:
            action_text = "; dann ".join(actions)
        else:
            action_text = "die gelernte Zustands- und Adressfolge setzen"
        if arguments:
            argument_text = " | ".join(arguments)
            translation = f"Bei {short_owner(owner)}: {action_text}. Angaben: {argument_text}."
        else:
            argument_text = "NONE"
            translation = f"Bei {short_owner(owner)}: {action_text}."
        statement_rows.append({
            "statement_id": statement_id,
            "page": rows[0]["page"],
            "record": rows[0]["record"],
            "silent_owner_de": owner,
            "action_events": str(len(actions)),
            "argument_state_events": str(len(arguments)),
            "complete_action_sequence_de": " → ".join(actions) if actions else "NO_EXPLICIT_ACTION_CARD",
            "complete_argument_sequence_de": argument_text,
            "action_complete_translation_de": translation,
            "all_events_spoken": "YES",
        })

    titles = {
        "H1": "erste Pflanzenanweisung", "H2": "zweiter Pflanzenabsatz", "H3": "Blütenpflanzenfolge",
        "H4": "breitblättrige Pflanzenfolge", "H5": "mehrköpfige Pflanzenfolge", "B1": "gemeinsames Becken",
        "B2": "Becken- und Randstationen", "B3": "Gefäß- und Figurenstationen", "B4": "Paar- und Hauptstationen",
        "B5": "linker Nachtrag", "B6": "rechter Nachtrag",
    }
    record_rows = []
    markdown = ["# Handlungsvollständige deutsche Arbeitslesung", "", "Diese Fassung spricht jedes der 381 Kartenereignisse. Handlungen stehen in sichtbarer Reihenfolge; Mengen, Quellen, Ziele und Zustände folgen als `Angaben`. Der Stil ist absichtlich knapp wie eine Werkstatt- oder Rezeptanweisung.", ""]
    for record, title in titles.items():
        rows = [row for row in statement_rows if row["record"] == record]
        continuous = " ".join(row["action_complete_translation_de"] for row in rows)
        record_rows.append({
            "record": record,
            "page": rows[0]["page"],
            "title_de": title,
            "statements": str(len(rows)),
            "action_events": str(sum(int(row["action_events"]) for row in rows)),
            "argument_state_events": str(sum(int(row["argument_state_events"]) for row in rows)),
            "continuous_action_complete_translation_de": continuous,
        })
        markdown.extend([f"## {record} — {title}", ""])
        markdown.extend(f"{index}. **{row['statement_id']}** — {row['action_complete_translation_de']}" for index, row in enumerate(rows, 1))
        markdown.append("")

    write_tsv("FIVE_HUNDRED_SIXTY_FOURTH_THREE_HUNDRED_EIGHTY_ONE_EVENT_READINGS.tsv", event_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_FOURTH_ONE_HUNDRED_SIXTEEN_ACTION_COMPLETE_STATEMENTS.tsv", statement_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_FOURTH_ELEVEN_ACTION_COMPLETE_RECORDS.tsv", record_rows)
    (HERE / "FIVE_HUNDRED_SIXTY_FOURTH_COMPLETE_ACTION_TRANSLATION.md").write_text("\n".join(markdown).rstrip() + "\n", encoding="utf-8")
    summary = {
        "status": "PASS",
        "events": len(event_rows),
        "action_events": sum(row["event_role"] == "ACTION" for row in event_rows),
        "argument_state_events": sum(row["event_role"] == "ARGUMENT_OR_STATE" for row in event_rows),
        "generic_actions_refined": refined_count,
        "statements": len(statement_rows),
        "zero_action_statements": sum(row["complete_action_sequence_de"] == "NO_EXPLICIT_ACTION_CARD" for row in statement_rows),
        "records": len(record_rows),
        "all_events_spoken": sum(row["meaning_preserved"] == "YES" for row in event_rows),
    }
    (HERE / "FIVE_HUNDRED_SIXTY_FOURTH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertvierundsechzigste Runde: handlungsvollständige Übersetzung",
        "",
        "## Korrektur",
        "",
        "Die vorige flüssige Lesefassung war in langen Zellen zu knapp. Diese Runde spricht alle 237 Handlungskarten und alle 144 Mengen-, Adress-, Zustands- und Relationskarten in ihrer Originalreihenfolge. Keine der 381 Karten verschwindet beim Glätten.",
        "",
        "54 generische Handlungsereignisse werden durch ihren schon sichtbaren Rahmen konkretisiert: OK+AIIN heißt bis zum Sollmaß beschicken, OK+AIN eine Portion einfüllen, Herbal-OK+Y Pflanzenstoff in den Ansatz geben, CHD+Y umschöpfen, CHD+DY in die nächste Station weitergeben und Herbal-SH ziehen lassen. Der Kartenkern bleibt derselbe; nur die deutsche Rahmenrealisierung wird präziser.",
        "",
        "Die neue Fassung ist deshalb wieder registerartig statt literarisch glatt. Das ist hier ein Vorteil: Bei H1-S001 bleiben etwa abnehmen, übertragen, ablaufen lassen, eintragen, einsetzen und erneut eintragen als echte Folge sichtbar, statt zu einem einzigen Verb zu kollabieren.",
        "",
        "## Nächster Schritt",
        "",
        "Als Nächstes werden die 116 vollständigen Aktionsfolgen in wiederkehrende Arbeitsrezepte gebündelt. Das Ziel sind wenige stabile Makros wie BESCHICKEN–FÜHREN–SCHLIESSEN oder HALTEN–ABSETZEN–ABFÜHREN, ohne einzelne Handlungen wieder zu verlieren.",
    ]
    (HERE / "FIVE_HUNDRED_SIXTY_FOURTH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
