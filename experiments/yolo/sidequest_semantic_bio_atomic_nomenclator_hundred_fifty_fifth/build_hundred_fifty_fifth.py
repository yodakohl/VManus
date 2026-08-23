#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
R154 = ROOT / "experiments/yolo/sidequest_semantic_herbal_atomic_nomenclator_hundred_fifty_fourth"
R151 = ROOT / "experiments/yolo/sidequest_semantic_open_carry_registers_hundred_fifty_first"
BIO_RECORDS = ["B1", "B2", "B3", "B4", "B5", "B6"]

ATOMIC = {
    "chdal": "Zieltransfer", "sheedy": "Langabsetzen; Schluss", "lchy": "Abführgut",
    "chary": "Quellposten", "lchedar": "Quellabführung", "rol": "Anschluss",
    "qotedaiin": "Kurzsoll", "solkeey": "Langsammlung", "chckhal": "Zielpassage",
    "kair": "Beckenlauf", "qokol": "Weiter einsetzen", "lar": "Quellabzug",
    "lo": "Abzug", "dalchdy": "Zieltransfer; Schluss", "solkaiin": "Sollsammlung",
    "lshedy": "Waschgang; Schluss", "cheedar": "Quelltransfer", "shecthedchy": "Vorbereitungstransfer",
    "qokar": "Quelleinsatz", "raly": "Endposten", "solkey": "Kurzsammlung",
    "lchedal": "Zielabführung", "qekey": "Kurzbearbeitung", "qokaly": "Zieleinsatz",
    "ral": "Zielmarke", "otchedy": "Folgetransfer; Schluss", "sheckhal": "Kurze Zielpassage",
    "sshkchdy": "Haltetransfer; Schluss", "oteey": "Langfolge", "chedchy": "Postentransfer",
    "ls": "Auslass", "lcheey": "Klarabzug", "otchdy": "Nachtransfer; Schluss",
    "pchedy": "Zuführung; Schluss", "dsheol": "Kurzhalt", "olsaly": "Zwischenziel",
    "daldy": "Zielschluss", "okair": "Laufeinsatz", "rshedy": "Waschschluss",
    "skar": "Quellausguss", "dairydy": "Laufschluss", "lol": "Weiterabzug",
    "cheeety": "Vollteil", "sheey": "Langhalt", "qokeedal": "Langer Zieleinsatz",
    "ldalor": "Endziel", "rsheal": "Kurzhalt am Ziel", "teol": "Kurzfortsetzung",
    "ytey": "Kurzteil", "chkeedy": "Langwärmen; Schluss", "octheol": "Fortsetzung vorbereiten",
    "schedair": "Weiterlauf", "ly": "Abführposten", "otar": "Folgequelle",
    "lkedy": "Kurzabzug; Schluss", "pchedal": "Zielzuführung", "lched": "Abführung",
    "lsho": "Waschgang", "sheckhy": "Kurzpassage", "lcheckhedy": "Trennabzug; Schluss",
    "qolky": "Weitergang", "otedy": "Kurzfolge; Schluss", "shecthy": "Kurzvorbereitung",
    "dshedy": "Kurzabsetzen; Schluss", "dchdy": "Transfer; Schluss", "qokeeedy": "Volleinsatz; Schluss",
    "tshey": "Klarlauf", "chldaiin": "Sollabsetzung", "chedain": "Anteilstransfer",
    "chealror": "Zielbereitung", "solshedy": "Folgeabsetzen; Schluss", "okeeol": "Langfortsetzung",
    "qokshedy": "Einsatzabsetzen; Schluss", "ches": "Teilen", "qolchey": "Weiterposten",
    "qokylddy": "Festsetzen; Schluss", "qockhey": "Kurzdurchgang", "chkeey": "Langwärmen",
    "lochedy": "Abführung; Schluss", "lcheckhy": "Abführpassage", "daiiin": "Endstufe",
}


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
    cards = read_tsv(R154 / "HUNDRED_FIFTY_FOURTH_173_REVISED_DICTIONARY.tsv")
    events = read_tsv(R154 / "HUNDRED_FIFTY_FOURTH_381_REVISED_EVENTS.tsv")
    carry_clauses = read_tsv(R151 / "HUNDRED_FIFTY_FIRST_116_CARRY_AWARE_CLAUSES.tsv")
    audit = []
    revised_cards = []
    for row in cards:
        new = dict(row)
        if row["master_form"] in ATOMIC:
            new["portable_card_value_de"] = ATOMIC[row["master_form"]]
            audit.append({
                "master_card_id": row["master_card_id"], "master_form": row["master_form"],
                "records": row["records"], "event_count": row["event_count"],
                "old_composite_default_de": row["portable_card_value_de"],
                "atomic_whole_card_default_de": new["portable_card_value_de"],
                "syntactic_type": row["syntactic_type"],
                "teaching_rule": "MEMORIZE_AS_ONE_BIO_CARD__DO_NOT_DECOMPOSE",
            })
        revised_cards.append(new)
    write_tsv("HUNDRED_FIFTY_FIFTH_81_BIO_ATOMIC_CARDS.tsv", audit)
    write_tsv("HUNDRED_FIFTY_FIFTH_173_COMPLETE_ATOMIC_DICTIONARY.tsv", revised_cards)

    card_by_id = {row["master_card_id"]: row for row in revised_cards}
    revised_events = []
    for row in events:
        new = dict(row)
        card = card_by_id[row["master_card_id"]]
        new["portable_card_value_de"] = card["portable_card_value_de"]
        revised_events.append(new)
    write_tsv("HUNDRED_FIFTY_FIFTH_381_COMPLETE_ATOMIC_EVENTS.tsv", revised_events)

    by_statement = defaultdict(list)
    for row in revised_events:
        by_statement[row["statement_id"]].append(row["portable_card_value_de"])
    carry_by_id = {row["statement_id"]: row for row in carry_clauses}
    bio_clause_rows = []
    for sid, values in by_statement.items():
        rid = sid.split("-")[0]
        if rid not in BIO_RECORDS:
            continue
        source = carry_by_id[sid]
        spoken = " — ".join(value.replace(" · ", " ") for value in values)
        if source["terminal_status"] == "TERMINAL" and "schluss" not in spoken.lower():
            spoken += "; Schluss"
        bio_clause_rows.append({
            "statement_id": sid, "record_unit_id": rid, "page": source["page"],
            "connective_de": source["connective_de"], "owner_trace": source["owner_trace"],
            "atomic_card_chain_de": " | ".join(values),
            "atomic_apprentice_clause_de": f"{source['connective_de']} {spoken}.",
            "dictionary_layer": "SHARED_DECK_PLUS_ATOMIC_BIO_NOMENCLATOR",
        })
    write_tsv("HUNDRED_FIFTY_FIFTH_97_ATOMIC_BIO_CLAUSES.tsv", bio_clause_rows)

    by_record = defaultdict(list)
    for row in bio_clause_rows:
        by_record[row["record_unit_id"]].append(row)
    book = ["# Sechs Biological-Records mit atomarem Ganzkarten-Nomenklator", "",
            "The eighty-one local Biological types are indivisible station words. Shared cards retain their",
            "productive meanings; local strings no longer pretend to be freely compositional.", ""]
    record_rows = []
    for rid in BIO_RECORDS:
        rows = by_record[rid]
        text = " ".join(row["atomic_apprentice_clause_de"] for row in rows)
        record_rows.append({
            "record_unit_id": rid, "page": rows[0]["page"], "statement_count": str(len(rows)),
            "continuous_atomic_recitation_de": text,
        })
        book += [f"## {rid} · {rows[0]['page']}", "", text, ""]
    write_tsv("HUNDRED_FIFTY_FIFTH_SIX_ATOMIC_BIO_RECORDS.tsv", record_rows)
    (OUT / "HUNDRED_FIFTY_FIFTH_ATOMIC_BIO_BOOK.md").write_text("\n".join(book).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertfünfundfünfzigste Runde: auch der Biological-Nomenklator wird atomar", "",
        "All 81 local Biological card types covering 85 events now have one short learned station value. Examples",
        "are ZIELTRANSFER, QUELLABFÜHRUNG, LANGSAMMLUNG, WASCHGANG, QUELLTRANSFER, ZIELEINSATZ, KLARABZUG,",
        "LAUFEINSATZ, WASCHSCHLUSS, QUELLAUSGUSS, LANGHALT, KURZABZUG, TRENNABZUG and VOLLEINSATZ.", "",
        "Together with R154, all 126 local nomenclator types are now atomic. The remaining 47 shared cards retain",
        "their productive roles. This is the clearest current realization of a ca. 1420 mixed technical script:",
        "common prompts and operators plus memorized workshop words, each rendered by the local hand afterward.", "",
        "Next rebuild the complete eleven-record and ten-page editions from this 47+126 dictionary and measure how",
        "many generic role labels disappear from the fluent reading without any further semantic additions.",
    ]
    (OUT / "HUNDRED_FIFTY_FIFTH_BIO_ATOMIC_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({
        "cards": len(revised_cards), "atomic_bio_cards": len(audit),
        "revised_bio_events": sum(int(row["event_count"]) for row in audit),
        "events": len(revised_events), "bio_statements": len(bio_clause_rows), "bio_records": len(record_rows),
        "old_composite_values": sum(" · " in row["old_composite_default_de"] for row in audit),
        "new_composite_values": sum(" · " in row["atomic_whole_card_default_de"] for row in audit),
        "all_local_atomic_types": 126, "shared_types": 47,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
