#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R151 = ROOT / "experiments/yolo/sidequest_semantic_open_carry_registers_hundred_fifty_first"
R155 = ROOT / "experiments/yolo/sidequest_semantic_bio_atomic_nomenclator_hundred_fifty_fifth"
R145 = ROOT / "experiments/yolo/sidequest_semantic_complete_layered_ten_page_hundred_forty_fifth"
RECORD_ORDER = ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"]


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    rows = list(rows)
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(R155 / "HUNDRED_FIFTY_FIFTH_173_COMPLETE_ATOMIC_DICTIONARY.tsv")
    events = read_tsv(R155 / "HUNDRED_FIFTY_FIFTH_381_COMPLETE_ATOMIC_EVENTS.tsv")
    source_events = read_tsv(ROOT / "experiments/yolo/sidequest_semantic_eleven_record_source_book_hundred_fiftieth/HUNDRED_FIFTIETH_381_SOURCE_EVENTS.tsv")
    carry_clauses = read_tsv(R151 / "HUNDRED_FIFTY_FIRST_116_CARRY_AWARE_CLAUSES.tsv")
    astro = read_tsv(R145 / "HUNDRED_FORTY_FIFTH_395_OWNER_LOCAL_ASTRO.tsv")
    old_unified = read_tsv(R145 / "HUNDRED_FORTY_FIFTH_776_LAYERED_LEDGER.tsv")
    jobs = read_tsv(R145 / "HUNDRED_FORTY_FIFTH_FOUR_LAYERED_JOBS.tsv")

    write_tsv("HUNDRED_FIFTY_SIXTH_173_ATOMIC_DICTIONARY.tsv", cards)
    source_by_serial = {row["event_serial"]: row for row in source_events}
    atomic_events = []
    for row in events:
        source = source_by_serial[row["event_serial"]]
        atomic_events.append({
            "event_serial": row["event_serial"], "statement_id": row["statement_id"],
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "visible_surface": row["visible_surface"], "master_card_id": row["master_card_id"],
            "visible_owner": source["visible_owner"], "card_value_de": row["portable_card_value_de"],
            "teaching_layer": "SHARED_DECK" if row["portable_scope"].startswith("ACTIVE") else "ATOMIC_LOCAL_NOMENCLATOR",
            "terminal_status": source["terminal_status"],
        })
    write_tsv("HUNDRED_FIFTY_SIXTH_381_ATOMIC_EVENTS.tsv", atomic_events)

    surface_rows = []
    for card in cards:
        for surface in card["registered_surfaces"].split("|"):
            surface_rows.append({
                "visible_surface": surface, "master_card_id": card["master_card_id"],
                "master_form": card["master_form"], "card_value_de": card["portable_card_value_de"],
                "teaching_layer": "SHARED_DECK" if card["portable_scope"].startswith("ACTIVE") else "ATOMIC_LOCAL_NOMENCLATOR",
                "syntactic_type": card["syntactic_type"],
            })
    write_tsv("HUNDRED_FIFTY_SIXTH_230_SURFACE_READER.tsv", surface_rows)

    by_statement = defaultdict(list)
    for row in atomic_events:
        by_statement[row["statement_id"]].append(row)
    clauses = []
    for source in carry_clauses:
        ev = by_statement[source["statement_id"]]
        values = [row["card_value_de"] for row in ev]
        spoken = " — ".join(value.replace(" · ", " ") for value in values)
        if source["terminal_status"] == "TERMINAL" and "schluss" not in spoken.lower():
            spoken += "; Schluss"
        clauses.append({
            "statement_id": source["statement_id"], "record_unit_id": source["record_unit_id"],
            "page": source["page"], "boundary_from_previous": source["boundary_from_previous"],
            "owner_trace": source["owner_trace"], "terminal_status": source["terminal_status"],
            "shared_event_count": str(sum(row["teaching_layer"] == "SHARED_DECK" for row in ev)),
            "local_event_count": str(sum(row["teaching_layer"] == "ATOMIC_LOCAL_NOMENCLATOR" for row in ev)),
            "atomic_card_chain_de": " | ".join(values),
            "continuous_atomic_clause_de": f"{source['connective_de']} {spoken}.",
        })
    write_tsv("HUNDRED_FIFTY_SIXTH_116_ATOMIC_CLAUSES.tsv", clauses)

    by_record = defaultdict(list)
    for row in clauses:
        by_record[row["record_unit_id"]].append(row)
    records = []
    prose_book = ["# Aktuelle atomare Elf-Record-Ausgabe", "",
                  "Forty-seven shared cards remain productive. One hundred twenty-six local cards are recited as",
                  "indivisible technical whole words. Owner, carry and close rules remain separate.", ""]
    for rid in RECORD_ORDER:
        rows = by_record[rid]
        text = " ".join(row["continuous_atomic_clause_de"] for row in rows)
        records.append({
            "record_unit_id": rid, "page": rows[0]["page"], "statement_count": str(len(rows)),
            "event_count": str(sum(int(row["shared_event_count"]) + int(row["local_event_count"]) for row in rows)),
            "shared_events": str(sum(int(row["shared_event_count"]) for row in rows)),
            "local_events": str(sum(int(row["local_event_count"]) for row in rows)),
            "continuous_atomic_record_de": text,
        })
        prose_book += [f"## {rid} · {rows[0]['page']}", "", text, ""]
    write_tsv("HUNDRED_FIFTY_SIXTH_ELEVEN_ATOMIC_RECORDS.tsv", records)
    (OUT / "HUNDRED_FIFTY_SIXTH_COMPLETE_ATOMIC_PROSE.md").write_text("\n".join(prose_book).rstrip() + "\n", encoding="utf-8")

    atomic_by_group = {f"E{int(row['event_serial']):03d}": row for row in atomic_events}
    unified = []
    for old in old_unified:
        group = old["source_group_id"]
        if group.startswith("E"):
            event = atomic_by_group[group]
            unified.append({
                "unified_serial": old["unified_serial"], "job_id": old["job_id"], "phase": old["phase"],
                "page": old["page"], "local_unit": old["local_unit"], "source_group_id": group,
                "visible_owner": event["visible_owner"], "visible_surface": event["visible_surface"],
                "current_value_de": event["card_value_de"], "reading_layer": event["teaching_layer"],
                "orientation": "PROSE_ORDER", "crosspage_key": "NONE",
            })
        else:
            unified.append({
                "unified_serial": old["unified_serial"], "job_id": old["job_id"], "phase": old["phase"],
                "page": old["page"], "local_unit": old["local_unit"], "source_group_id": group,
                "visible_owner": old["visible_owner"], "visible_surface": old["visible_surface"],
                "current_value_de": old["controlled_local_expansion_de"], "reading_layer": "ASTRO_OWNER_LOCAL_MENU",
                "orientation": old["orientation"], "crosspage_key": old["crosspage_key"],
            })
    write_tsv("HUNDRED_FIFTY_SIXTH_776_ATOMIC_LEDGER.tsv", unified)
    write_tsv("HUNDRED_FIFTY_SIXTH_395_ASTRO_OWNER_MENU.tsv", astro)
    write_tsv("HUNDRED_FIFTY_SIXTH_FOUR_OPTIONAL_JOBS.tsv", jobs)

    manual = ["# Taschenbuch der atomaren Mischschrift", "", "## Schreiben und lesen", "",
              "1. Point to the visible owner.",
              "2. Choose one of 47 shared prompts/operators or one of 126 memorized whole cards.",
              "3. Preserve the attested clause mould and carry register.",
              "4. Close only with the exact learned terminal construction.",
              "5. Render the chosen master card in the local hand.",
              "6. On Astro pages read owner-local menu labels; import no prose word or cross-page key.", "",
              "## Shared deck", ""]
    for card in cards:
        if card["portable_scope"].startswith("ACTIVE"):
            manual.append(f"- `{card['master_form']}` = {card['portable_card_value_de']} ({card['syntactic_type']})")
    manual += ["", "## Local nomenclator", "",
               "The remaining 126 entries are copied as whole words. Never infer a new card by freely combining",
               "their visible substrings; their complete list is the 173-card dictionary after removing this shared deck."]
    (OUT / "HUNDRED_FIFTY_SIXTH_ATOMIC_POCKET_MANUAL.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    complete = ["# Aktuelle atomare Zehn-Seiten-Ausgabe", "", "## Elf Prosa-Records", ""]
    for row in records:
        complete += [f"### {row['record_unit_id']} · {row['page']}", "", row["continuous_atomic_record_de"], ""]
    complete += ["## Drei Astro-Instrumente", "",
                 "f67r2 remains two separate owner-local wheels; f68r1 a multipanel star menu; f69v three separate",
                 "wheels with the 28-place inventory only on the left. All 395 groups retain their local menu values.",
                 "No direction, rotation, common start, prose-word import or f68-to-f69 key is introduced."]
    (OUT / "HUNDRED_FIFTY_SIXTH_COMPLETE_TEN_PAGE_EDITION.md").write_text("\n".join(complete).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertsechsundfünfzigste Runde: neue aktuelle atomare Gesamtausgabe", "",
        "The current base now binds 230 visible prose forms to 173 master cards, 381 prose events, 116 clauses,",
        "eleven records, 395 Astro groups and all 776 visible groups. The prose economy is exactly 47 productive",
        "shared cards covering 251 events plus 126 atomic local cards covering 130 events.", "",
        "The old dotted singleton compositions have disappeared. The local cards are learned technical words; the",
        "shared deck carries reference, quantity, order, state, operation and closure. Visible owner and fluent",
        "expansion remain separate, and the Astro menu is unchanged and locally addressed.", "",
        "This becomes the new sidequest base. Next compare the 47 shared cards against the 230 observed surface",
        "forms and simplify the apprentice's renderer rules without changing any of the 173 meanings.",
    ]
    (OUT / "HUNDRED_FIFTY_SIXTH_ATOMIC_CURRENT_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "surfaces": len(surface_rows), "cards": len(cards), "shared_cards": sum(row["portable_scope"].startswith("ACTIVE") for row in cards),
        "local_atomic_cards": sum(row["portable_scope"] == "LOCAL_LEARNED_WHOLE_CARD" for row in cards),
        "prose_events": len(atomic_events), "shared_events": sum(row["teaching_layer"] == "SHARED_DECK" for row in atomic_events),
        "local_events": sum(row["teaching_layer"] == "ATOMIC_LOCAL_NOMENCLATOR" for row in atomic_events),
        "statements": len(clauses), "records": len(records), "astro_groups": len(astro), "unified_groups": len(unified), "jobs": len(jobs),
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
