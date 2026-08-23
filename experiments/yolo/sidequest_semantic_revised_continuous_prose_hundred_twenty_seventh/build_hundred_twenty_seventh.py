#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R121 = ROOT / "experiments/yolo/sidequest_semantic_complete_working_edition_hundred_twenty_first"
R126 = ROOT / "experiments/yolo/sidequest_semantic_shared_card_meaning_revision_hundred_twenty_sixth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def rewrite_fluent(text, forms):
    revised = text
    replacements = []

    def replace(old, new):
        nonlocal revised
        if old in revised:
            revised = revised.replace(old, new)
            replacements.append(f"{old}->{new}")

    if "cheeky" in forms:
        replace("wärme länger", "bearbeite länger")
        replace("Wärme länger", "Bearbeite länger")
    if "okaiin" in forms:
        replace("Stelle das Sollmaß ein", "Stelle auf Sollmaß")
        replace("stelle das Sollmaß ein", "stelle auf Sollmaß")
        replace("Bemiss den Posten", "Stelle den Posten auf Sollmaß")
        replace("bemiss den Posten", "stelle den Posten auf Sollmaß")
    if "okal" in forms:
        replace("Setze dort an", "Setze dort ein")
        replace("setze dort an", "setze dort ein")
        replace("setze den Posten dort an", "setze den Posten dort ein")
        replace("setze ihn dort an", "setze ihn dort ein")
        replace("Setze dorthin um", "Übertrage dorthin")
        replace("setze dorthin um", "übertrage dorthin")
    if "choky" in forms:
        replace("Setze den Posten an", "Setze diesen Posten ein")
        replace("setze den Posten an", "setze diesen Posten ein")
        replace("setze ihn an", "setze ihn ein")
        replace("setze es mit Wasser kurz an", "setze es kurz in Wasser ein")
    if "chdy" in forms:
        replace("Setze um", "Übertrage")
        replace("setze um", "übertrage")
        replace("Setze den bereiten Posten um", "Übertrage den bereiten Posten")
        replace("Setze eine Portion um", "Übertrage eine Portion")
        replace("Setze die entnommene Sollmaßportion um", "Übertrage die entnommene Sollmaßportion")
    if "oldy" in forms and "schließ" not in revised.lower() and "abschließ" not in revised.lower():
        revised = revised.rstrip()
        if not revised.endswith("."):
            revised += "."
        revised += " Schließe den Arbeitsgang."
        replacements.append("ADD_EXPLICIT_CLOSE")
    return revised, replacements


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    events = read_tsv(R121 / "HUNDRED_TWENTY_FIRST_381_EVENT_INTERLINEAR.tsv")
    statements = read_tsv(R121 / "HUNDRED_TWENTY_FIRST_116_CURRENT_STATEMENTS.tsv")
    decisions = read_tsv(R126 / "HUNDRED_TWENTY_SIXTH_SEVENTEEN_REVISED_MEANINGS.tsv")
    revised_by_id = {row["master_card_id"]: row["revised_portable_default_de"] for row in decisions}
    form_by_id = {row["master_card_id"]: row["master_form"] for row in decisions}

    events_by_statement = defaultdict(list)
    event_rows = []
    for row in events:
        events_by_statement[row["statement_id"]].append(row)
        if row["master_card_id"] in revised_by_id:
            value = revised_by_id[row["master_card_id"]]
            layer = "REVISED_SHARED_17"
        else:
            value = row["short_default_de"]
            layer = "UNCHANGED_SECTION_OR_SPECIALIST_CARD"
        event_rows.append({
            "event_serial": row["event_serial"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "visible_surface": row["visible_surface"],
            "master_card_id": row["master_card_id"],
            "semantic_atoms": row["semantic_atoms"],
            "revised_short_reading_de": value,
            "reading_layer": layer,
        })
    write_tsv("HUNDRED_TWENTY_SEVENTH_381_REVISED_EVENT_INTERLINEAR.tsv", event_rows)

    statement_rows = []
    for row in statements:
        members = events_by_statement[row["statement_id"]]
        forms = [form_by_id[event["master_card_id"]] for event in members if event["master_card_id"] in form_by_id]
        shared_literal = " ".join(revised_by_id[event["master_card_id"]] for event in members if event["master_card_id"] in revised_by_id)
        revised, replacements = rewrite_fluent(row["current_reading_de"], set(forms))
        if not forms:
            status = "NO_SHARED_CARD__UNCHANGED"
        elif replacements:
            status = "FLUENT_TEXT_REVISED"
        else:
            status = "FLUENT_TEXT_ALREADY_COMPATIBLE"
        statement_rows.append({
            "statement_order": row["statement_order"],
            "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"],
            "page": row["page"],
            "visible_surface_sequence": row["visible_surface_sequence"],
            "shared_master_forms": " ".join(forms) or "NONE",
            "revised_shared_kernel_de": shared_literal or "NONE",
            "old_current_reading_de": row["current_reading_de"],
            "revised_continuous_reading_de": revised,
            "revision_actions": " | ".join(replacements) or "NONE",
            "revision_status": status,
        })
    write_tsv("HUNDRED_TWENTY_SEVENTH_116_REVISED_STATEMENTS.tsv", statement_rows)

    records = defaultdict(list)
    for row in statement_rows:
        records[row["record_unit_id"]].append(row)
    record_rows = []
    md = ["# Elf fortlaufende Records mit dem revidierten gemeinsamen Deck", ""]
    for record, members in records.items():
        page = members[0]["page"]
        changed = sum(row["revision_status"] == "FLUENT_TEXT_REVISED" for row in members)
        record_rows.append({
            "record_unit_id": record,
            "page": page,
            "statement_count": str(len(members)),
            "shared_card_statements": str(sum(row["shared_master_forms"] != "NONE" for row in members)),
            "fluent_revisions": str(changed),
            "continuous_record_de": " ".join(row["revised_continuous_reading_de"] for row in members),
        })
        md += [f"## {record} · {page}", ""]
        for row in members:
            md.append(f"{row['statement_id']}: {row['revised_continuous_reading_de']}")
        md.append("")
    write_tsv("HUNDRED_TWENTY_SEVENTH_ELEVEN_REVISED_RECORDS.tsv", record_rows)
    (OUT / "HUNDRED_TWENTY_SEVENTH_COMPLETE_REVISED_PROSE.md").write_text("\n".join(md).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertsiebenundzwanzigste Runde: die neue Kurzsprache in allen elf Records", "",
        "Die R126-Kartenwerte sind nun durch alle 381 Ereignisse und 116 Aussagen gezogen. Der untere",
        "Interlineartext zeigt jede sichtbare Karte mit genau einem kurzen Arbeitswert. Die flüssige Ebene",
        "ändert nur Stellen, an denen die alten engen Verben noch ausdrücklich standen; sonst bleibt die",
        "bereits konkrete Abschnittslesung erhalten.", "",
        "Das Ergebnis klingt eher wie ein Werkstattformular: Posten einsetzen oder übertragen, davon nehmen,",
        "dorthin führen, auf Sollmaß stellen, Klarlauf nehmen, damit weiter, Arbeitsgang schließen. Wärme,",
        "Wasser, Tuch, Pflanzenpart und Becken bleiben lokale Inhalte und werden nicht aus der gemeinsamen",
        "Karte allein abgeleitet.", "",
        "Der nächste Engpass liegt nun in den 156 nichtgemeinsamen Karten. Statt sie alle neu zu erfinden,",
        "sollen zuerst die häufigsten wiederkehrenden Section-Karten gegen dieselbe kurze Sprachdisziplin",
        "geprüft und zu kleinen Herbal- beziehungsweise Bio-Fachwortlisten verdichtet werden.",
    ]
    (OUT / "HUNDRED_TWENTY_SEVENTH_REVISED_PROSE_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE",
        "events": len(event_rows),
        "statements": len(statement_rows),
        "records": len(record_rows),
        "shared_event_overlays": sum(row["reading_layer"] == "REVISED_SHARED_17" for row in event_rows),
        "statements_with_shared_cards": sum(row["shared_master_forms"] != "NONE" for row in statement_rows),
        "fluent_statements_revised": sum(row["revision_status"] == "FLUENT_TEXT_REVISED" for row in statement_rows),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
