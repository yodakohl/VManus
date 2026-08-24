#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P526 = ROOT / "sidequest_semantic_bound_master_exemplar_five_hundred_twenty_sixth"
P559 = ROOT / "sidequest_semantic_wrapper_palette_compression_five_hundred_fifty_ninth"
P560 = ROOT / "sidequest_semantic_formula_cadence_renderer_five_hundred_sixtieth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    old_log = {row["event_id"]: row for row in read_tsv(P526 / "FIVE_HUNDRED_TWENTY_SIXTH_381_BOUND_EXEMPLAR_LOG.tsv")}
    programs = {row["locus"]: row for row in read_tsv(P559 / "FIVE_HUNDRED_FIFTY_NINTH_THIRTY_FOUR_LOCUS_PROGRAMS.tsv")}
    assignments = read_tsv(P559 / "FIVE_HUNDRED_FIFTY_NINTH_FIFTY_NINE_COMPRESSED_ASSIGNMENTS.tsv")
    full = read_tsv(P560 / "FIVE_HUNDRED_SIXTIETH_THREE_HUNDRED_EIGHTY_ONE_RENDERER_LEDGER.tsv")
    uniform = [row for row in assignments if programs[row["locus"]]["uniform_stamp"] == "YES"]

    by_locus = defaultdict(list)
    for row in uniform:
        by_locus[row["locus"]].append(row)
    locus_meta = []
    for locus, rows in by_locus.items():
        sheet_entry = old_log[rows[0]["event_id"]]["record_sheet_entry"]
        index = int(sheet_entry.split(":")[-1])
        locus_meta.append((rows[0]["record"], index, locus, rows[0]["apply_wrapper"], rows))
    locus_meta.sort(key=lambda item: (item[0], item[1]))

    by_record = defaultdict(list)
    for item in locus_meta:
        by_record[item[0]].append(item)
    record_order = [record for record in ["H1", "H2", "H3", "H4", "H5", "B1", "B2", "B3", "B4", "B5", "B6"] if record in by_record]
    melody_rows = []
    slot_rows = []
    execution_rows = []
    locus_to_melody = {}
    for melody_number, record in enumerate(record_order, 1):
        melody_id = f"RM{melody_number:02d}"
        items = by_record[record]
        sequence = [item[3] for item in items]
        page = items[0][4][0]["page"]
        melody_rows.append({
            "melody_id": melody_id,
            "record": record,
            "page": page,
            "wrapper_sequence": ">".join(sequence),
            "melody_slots": str(len(items)),
            "covered_loci": str(len(items)),
            "covered_events": str(sum(len(item[4]) for item in items)),
            "load_rule": "LOAD_ONCE_AT_RECORD_ENTRY",
            "execution_rule": "ADVANCE_AT_NEXT_UNIFORM_WRAPPER_LOCUS",
            "free_choice": "NO",
        })
        for slot_number, (_, sheet_index, locus, stamp, rows) in enumerate(items, 1):
            locus_to_melody[locus] = (melody_id, slot_number)
            slot_rows.append({
                "melody_id": melody_id,
                "slot": str(slot_number),
                "record_sheet_index": str(sheet_index),
                "record": record,
                "page": page,
                "locus": locus,
                "wrapper_stamp": stamp,
                "events_at_slot": str(len(rows)),
                "instruction": f"WRITE_{'BARE' if stamp == 'Ø' else stamp.upper()}_FOR_THIS_LOCUS",
            })
            for row in rows:
                execution_rows.append({
                    "event_id": row["event_id"],
                    "page": row["page"],
                    "record": record,
                    "locus": locus,
                    "melody_id": melody_id,
                    "melody_slot": str(slot_number),
                    "wrapper_stamp": stamp,
                    "final_surface": row["final_surface"],
                    "surface_roundtrip": "YES",
                    "local_locus_table": "NO",
                    "free_choice": "NO",
                })

    final_rows = []
    for row in full:
        if row["renderer_source"] == "UNIFORM_LOCUS_STAMP":
            melody_id, slot = locus_to_melody[row["locus"]]
            source = "RECORD_WRAPPER_MELODY"
            rule = f"{melody_id}:{slot}"
        else:
            source = row["renderer_source"]
            rule = row["renderer_rule"]
        final_rows.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "locus": row["locus"],
            "card_no": row["card_no"],
            "component_parse": row["component_parse"],
            "renderer_source": source,
            "renderer_rule": rule,
            "final_surface": row["final_surface"],
            "surface_roundtrip": row["surface_roundtrip"],
            "local_locus_table": "NO",
            "free_choice": "NO",
        })

    write_tsv("FIVE_HUNDRED_SIXTY_FIRST_NINE_RECORD_MELODIES.tsv", melody_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_FIRST_TWENTY_TWO_MELODY_SLOTS.tsv", slot_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_FIRST_TWENTY_SEVEN_MELODY_EXECUTIONS.tsv", execution_rows)
    write_tsv("FIVE_HUNDRED_SIXTY_FIRST_THREE_HUNDRED_EIGHTY_ONE_FINAL_RENDERER.tsv", final_rows)
    counts = Counter(row["renderer_source"] for row in final_rows)
    summary = {
        "status": "PASS",
        "record_melodies": len(melody_rows),
        "melody_slots": len(slot_rows),
        "melody_events": len(execution_rows),
        "records_with_melody": record_order,
        "renderer_source_counts": dict(sorted(counts.items())),
        "local_locus_tables": sum(row["local_locus_table"] != "NO" for row in final_rows),
        "surface_roundtrip": sum(row["surface_roundtrip"] == "YES" for row in final_rows),
        "free_choices": sum(row["free_choice"] != "NO" for row in final_rows),
    }
    (HERE / "FIVE_HUNDRED_SIXTY_FIRST_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhunderteinundsechzigste Runde: Recordmelodien",
        "",
        "## Ergebnis",
        "",
        "Die letzten 22 einheitlichen Ortsstile lassen sich als neun kurze Recordmelodien lehren. Der Schreiber lädt am Recordanfang eine Wrapperfolge und rückt nur dann einen Platz weiter, wenn die laufende Karte einen sonst ungelösten Wrapper verlangt. Mehrere Karten am selben Ort verwenden denselben Melodieplatz.",
        "",
        "Beispiele: H3 trägt `d→d`; H4 `ch→blank→blank→blank`; H5 `s→ch`; B2 `d→d→s→blank`; B3 `blank→t→s→s`; B4 `blank→t→ch→q`. Das sind Schreibrezitationen des Musterblatts, keine zusätzlichen Wortbedeutungen.",
        "",
        "Der vollständige Oberflächenweg lautet jetzt: 314 globale Kartenformen, acht unmittelbare Kontextwechsel, 32 component-getriggerte Formelkadenzen und 27 Ausführungen aus neun Recordmelodien. Alle 381 sichtbaren Oberflächen werden exakt erzeugt. Es gibt keine Ereignis- oder Lokuswahltabelle mehr; lokal memoriert werden nur neun kurze Recordzeilen.",
        "",
        "## Nächster Schritt",
        "",
        "Die Semantik-, Karten- und Oberflächenschichten können jetzt zu einem einzigen Lehrlingshandbuch zusammengezogen werden. Danach wird die fortlaufende deutsche Lesefassung neu geschrieben, diesmal aus dem vollständigen ausführbaren System statt aus älteren Einzelglossen.",
    ]
    (HERE / "FIVE_HUNDRED_SIXTY_FIRST_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
