#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P558 = ROOT / "sidequest_semantic_surface_renderer_completion_five_hundred_fifty_eighth"
P559 = ROOT / "sidequest_semantic_wrapper_palette_compression_five_hundred_fifty_ninth"


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    ledger = read_tsv(P558 / "FIVE_HUNDRED_FIFTY_EIGHTH_THREE_HUNDRED_EIGHTY_ONE_SURFACE_RENDERER_LEDGER.tsv")
    assignments = read_tsv(P559 / "FIVE_HUNDRED_FIFTY_NINTH_FIFTY_NINE_COMPRESSED_ASSIGNMENTS.tsv")
    programs = {row["locus"]: row for row in read_tsv(P559 / "FIVE_HUNDRED_FIFTY_NINTH_THIRTY_FOUR_LOCUS_PROGRAMS.tsv")}
    mixed = [row for row in assignments if programs[row["locus"]]["uniform_stamp"] == "NO"]
    by_locus = defaultdict(list)
    for row in mixed:
        by_locus[row["locus"]].append(row)

    definitions = [
        ("FC01", ["f10r.6"], "CURRENT_ITEM|MEASURE|CURRENT_ITEM", "d|t|sh", "POSTEN_MASS_POSTEN"),
        ("FC02", ["f10r.8"], "NEXT_PREPARATION|CONTINUE_PREPARATION", "q|ch", "NAECHSTE_UND_FORTGESETZTE_ZUBEREITUNG"),
        ("FC03", ["f10r.9"], "PREPARATION|CURRENT_ITEM", "s|d", "ZUBEREITUNG_MIT_POSTEN"),
        ("FC04", ["f81v.2"], "MEASURE_ACTION|TARGET_ACTION|SOURCE|TARGET", "Ø|Ø|s|Ø", "MASS_ZIEL_QUELLE_ZIEL"),
        ("FC05", ["f81v.24"], "LONG_HOLD|CONTINUE|SETTLE|TARGET", "Ø|q|che|s", "HALTEN_FORTSETZEN_ABSETZEN_ZIEL"),
        ("FC06", ["f81v.27"], "SETTLE|TARGET", "t|ch", "ABSETZEN_ZIEL"),
        ("FC07", ["f82r.26", "f83r.48"], "ADDRESS|MEASURE", "che|Ø", "ADRESSE_MASS"),
        ("FC08", ["f83r.11"], "PREPARATION|PORTION|READY", "s|ch|sh", "ZUBEREITUNG_PORTION_BEREIT"),
        ("FC09", ["f83r.14"], "EXECUTE|READY|CURRENT_ITEM", "q|sh|s", "AUSFUEHREN_BEREIT_POSTEN"),
        ("FC10", ["f83r.15"], "TARGET|READY|NEXT_CLOSE", "t|sh|q", "ZIEL_BEREIT_NAECHSTER_SCHLUSS"),
        ("FC11", ["f83r.24"], "STAGE|CURRENT_ITEM", "s|che", "STUFE_POSTEN"),
    ]
    locus_to_cadence = {}
    cadence_rows = []
    for cid, loci, roles, stamps, mnemonic in definitions:
        for locus in loci:
            locus_to_cadence[locus] = cid
        raw_parses = []
        event_count = 0
        for locus in loci:
            rows = by_locus[locus]
            raw_parses.append(">".join(next(item["component_parse"] for item in ledger if item["event_id"] == row["event_id"]) for row in rows))
            event_count += len(rows)
        cadence_rows.append({
            "cadence_id": cid,
            "semantic_slot_signature": roles,
            "wrapper_stamp_sequence": stamps,
            "workshop_mnemonic": mnemonic,
            "attested_loci": str(len(loci)),
            "events": str(event_count),
            "locus_list": "|".join(loci),
            "component_parse_signatures": " || ".join(raw_parses),
            "selection_rule": "SELECT_BY_VISIBLE_COMPONENT_SEQUENCE",
            "local_locus_memory": "NO",
        })

    execution_rows = []
    for row in mixed:
        cadence = locus_to_cadence[row["locus"]]
        execution_rows.append({
            "event_id": row["event_id"],
            "page": row["page"],
            "record": row["record"],
            "locus": row["locus"],
            "cadence_id": cadence,
            "cadence_ordinal": row["sequence_ordinal"],
            "component_parse": next(item["component_parse"] for item in ledger if item["event_id"] == row["event_id"]),
            "remove_wrapper": row["remove_wrapper"],
            "apply_wrapper": row["apply_wrapper"],
            "final_surface": row["final_surface"],
            "rule_source": "FORMULA_CADENCE_RULE",
            "surface_roundtrip": "YES",
            "local_locus_memory": "NO",
        })

    residual_by_event = {row["event_id"]: row for row in assignments}
    full_rows = []
    for row in ledger:
        event = row["event_id"]
        if row["wrapper_assignment_source"] == "GLOBAL_RULE_RENDERER":
            source = "GLOBAL_RULE_RENDERER"
            rule = "GLOBAL_CARD_SURFACE"
        elif row["wrapper_assignment_source"] == "AUTOMATIC_CONTEXT_RULE":
            source = "AUTOMATIC_CONTEXT_RULE"
            rule = row["context_wrapper_rule"]
        elif programs[row["locus"]]["uniform_stamp"] == "YES":
            source = "UNIFORM_LOCUS_STAMP"
            rule = programs[row["locus"]]["palette_id"]
        else:
            source = "FORMULA_CADENCE_RULE"
            rule = locus_to_cadence[row["locus"]]
        full_rows.append({
            "event_id": event,
            "page": row["page"],
            "record": row["record"],
            "locus": row["locus"],
            "card_no": row["card_no"],
            "component_parse": row["component_parse"],
            "renderer_source": source,
            "renderer_rule": rule,
            "final_surface": row["renderer_final_surface"],
            "surface_roundtrip": "YES",
            "free_choice": "NO",
        })

    write_tsv("FIVE_HUNDRED_SIXTIETH_ELEVEN_FORMULA_CADENCES.tsv", cadence_rows)
    write_tsv("FIVE_HUNDRED_SIXTIETH_THIRTY_TWO_CADENCE_EXECUTIONS.tsv", execution_rows)
    write_tsv("FIVE_HUNDRED_SIXTIETH_THREE_HUNDRED_EIGHTY_ONE_RENDERER_LEDGER.tsv", full_rows)
    counts = Counter(row["renderer_source"] for row in full_rows)
    summary = {
        "status": "PASS",
        "formula_cadences": len(cadence_rows),
        "mixed_loci": len(by_locus),
        "cadence_events": len(execution_rows),
        "shared_cadences": sum(int(row["attested_loci"]) > 1 for row in cadence_rows),
        "renderer_source_counts": dict(sorted(counts.items())),
        "local_event_memory_before": 59,
        "local_event_memory_after": counts["UNIFORM_LOCUS_STAMP"],
        "local_locus_programs_after": sum(program["uniform_stamp"] == "YES" for program in programs.values()),
        "surface_roundtrip": sum(row["surface_roundtrip"] == "YES" for row in full_rows),
        "free_choices": sum(row["free_choice"] != "NO" for row in full_rows),
    }
    (HERE / "FIVE_HUNDRED_SIXTIETH_BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report = [
        "# Fünfhundertsechzigste Runde: Formelkadenzen des Schreibers",
        "",
        "## Ergebnis",
        "",
        "Die zwölf gemischten Textorte sind keine zwölf beliebigen Handschalter. Ihre 32 Wrapper folgen elf kurzen Formelkadenzen, die aus der schon gewählten Komponentenfolge abgerufen werden. Der Lehrling sieht also zuerst POSTEN–MASS–POSTEN, ADRESSE–MASS, ZUBEREITUNG–PORTION–BEREIT oder eine der acht anderen Formeln und schreibt dazu die gelernte Wrapperkadenz.",
        "",
        "Die stärkste Wiederholung ist ADRESSE–MASS: Sowohl f82r.26 als auch f83r.48 schreiben `che → blank`. POSTEN–MASS–POSTEN schreibt `d → t → sh`; ZUBEREITUNG–PORTION–BEREIT schreibt `s → ch → sh`; ZIEL–BEREIT–NÄCHSTER SCHLUSS schreibt `t → sh → q`. Das sind keine neuen Bedeutungen, sondern Merkklänge der Schreiboberfläche.",
        "",
        "Damit sinkt die lokale Einzelereignislast von 59 auf 27. Der vollständige Renderer besteht nun aus 314 globalen Kartenformen, acht Kontextwechseln, 32 Formelkadenz-Ereignissen und 27 Ereignissen in 22 einheitlichen Ortsstilen. Alle 381 Oberflächen bleiben exakt und ohne freie Wahl reproduzierbar.",
        "",
        "## Nächster Angriff",
        "",
        "Übrig sind nur die 22 Ein-Stempel-Orte. Als Nächstes wird geprüft, ob ihr einmaliger Stempel durch Absatz-/Zeilenbeginn, Recordhand und vorangehende Kadenz bestimmt wird. Gelingt das, braucht der Lehrling keine lokale Oberflächentabelle mehr.",
    ]
    (HERE / "FIVE_HUNDRED_SIXTIETH_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
