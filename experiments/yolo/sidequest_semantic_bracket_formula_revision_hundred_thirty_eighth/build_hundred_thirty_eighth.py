#!/usr/bin/env python3
import csv
import json
from collections import defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
EXP = OUT.parents[1]
R136 = EXP / "yolo" / "sidequest_semantic_period_sized_current_edition_hundred_thirty_sixth"

SHARED = {"MC019", "MC026", "MC032", "MC039", "MC040", "MC055", "MC074", "MC080", "MC086", "MC119", "MC120", "MC123", "MC153", "MC154", "MC157", "MC161", "MC171"}
F1 = ("MC123", "MC039", "MC123")
F2 = ("MC153", "MC157", "MC153")


def read_tsv(name):
    with (R136 / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def find_pattern(ids, pattern):
    return [i for i in range(len(ids) - len(pattern) + 1) if tuple(ids[i:i + len(pattern)]) == pattern]


def main():
    cards = read_tsv("HUNDRED_THIRTY_SIXTH_173_CARD_DICTIONARY.tsv")
    events = read_tsv("HUNDRED_THIRTY_SIXTH_381_PROSE_EVENTS.tsv")
    statements = read_tsv("HUNDRED_THIRTY_SIXTH_116_TERSE_STATEMENTS.tsv")
    records = read_tsv("HUNDRED_THIRTY_SIXTH_11_TERSE_RECORDS.tsv")

    out_cards = []
    for row in cards:
        new = "derselbe Ansatz" if row["master_card_id"] == "MC157" else row["current_spoken_default_de"]
        out_cards.append({**row, "pre_formula_default_de": row["current_spoken_default_de"],
                          "current_spoken_default_de": new,
                          "formula_revision": "CARRIED_PREPARATION_NOUN" if row["master_card_id"] == "MC157" else "NONE"})
    value = {r["master_card_id"]: r["current_spoken_default_de"] for r in out_cards}

    out_events = []
    for row in events:
        out_events.append({**row, "current_spoken_default_de": value[row["master_card_id"]]})
    by_statement = defaultdict(list)
    for row in out_events:
        by_statement[row["statement_id"]].append(row)

    formula_occ = []
    out_statements = []
    old_by_id = {r["statement_id"]: r for r in statements}
    for sid, group in by_statement.items():
        shared_group = [r for r in group if r["master_card_id"] in SHARED]
        shared_ids = [r["master_card_id"] for r in shared_group]
        formula_labels = []
        for formula_id, pattern, spoken in (("F1_PAIRED_MEASURE", F1, "zwei Posten unter demselben Sollmaß"),
                                             ("F2_CARRIED_PREPARATION", F2, "Fortsetzung mit demselben Ansatz")):
            for start in find_pattern(shared_ids, pattern):
                chosen = shared_group[start:start + 3]
                first_serial, last_serial = int(chosen[0]["event_serial"]), int(chosen[-1]["event_serial"])
                full_span = [r for r in group if first_serial <= int(r["event_serial"]) <= last_serial]
                formula_occ.append({
                    "formula_id": formula_id, "statement_id": sid, "record_unit_id": group[0]["record_unit_id"],
                    "page": group[0]["page"], "shared_card_ids": "|".join(pattern),
                    "shared_surfaces": " ".join(r["visible_surface"] for r in chosen),
                    "full_visible_span": " ".join(r["visible_surface"] for r in full_span),
                    "full_value_span_de": " | ".join(value[r["master_card_id"]] for r in full_span),
                    "spoken_formula_de": spoken,
                })
                formula_labels.append(spoken)
        chain = " | ".join(value[r["master_card_id"]] for r in group)
        out_statements.append({
            "statement_id": sid, "record_unit_id": group[0]["record_unit_id"], "page": group[0]["page"],
            "visible_surface_sequence": " ".join(r["visible_surface"] for r in group),
            "revised_literal_chain_de": chain,
            "shared_skeleton_de": " | ".join(value[r["master_card_id"]] for r in shared_group) or "KEINE GEMEINSAME KARTE",
            "formula_expansion_de": " + ".join(formula_labels) if formula_labels else "KEINE KLAMMERFORMEL",
            "spoken_clause_de": "; ".join(value[r["master_card_id"]] for r in group).rstrip(".; ") + ".",
            "previous_clause_de": old_by_id[sid]["terse_workshop_clause_de"],
        })

    by_record = defaultdict(list)
    for row in out_statements:
        by_record[row["record_unit_id"]].append(row)
    out_records = []
    for row in records:
        group = by_record[row["record_unit_id"]]
        out_records.append({
            "record_unit_id": row["record_unit_id"], "page": row["page"],
            "statement_count": row["statement_count"], "event_count": row["event_count"],
            "formula_ids": "|".join(sorted({f["formula_id"] for f in formula_occ if f["record_unit_id"] == row["record_unit_id"]})) or "NONE",
            "continuous_revised_record_de": " ".join(r["spoken_clause_de"] for r in group),
        })

    write_tsv("HUNDRED_THIRTY_EIGHTH_173_FORMULA_REVISED_DICTIONARY.tsv", out_cards)
    write_tsv("HUNDRED_THIRTY_EIGHTH_381_FORMULA_REVISED_EVENTS.tsv", out_events)
    write_tsv("HUNDRED_THIRTY_EIGHTH_116_FORMULA_STATEMENTS.tsv", out_statements)
    write_tsv("HUNDRED_THIRTY_EIGHTH_FIVE_FORMULA_OCCURRENCES.tsv", formula_occ)
    write_tsv("HUNDRED_THIRTY_EIGHTH_11_REVISED_RECORDS.tsv", out_records)

    readable = ["# Zwei Klammerformeln in ihren vollständigen Records", ""]
    for formula in formula_occ:
        readable += [f"## {formula['formula_id']} · {formula['statement_id']} · {formula['page']}", "",
                     f"Sichtbar: `{formula['full_visible_span']}`", "",
                     f"Wörtlich: {formula['full_value_span_de']}", "",
                     f"Gesprochen: **{formula['spoken_formula_de']}**", ""]
    readable += ["## Vollständige betroffene Records", ""]
    affected = {f["record_unit_id"] for f in formula_occ}
    for row in out_records:
        if row["record_unit_id"] in affected:
            readable += [f"### {row['record_unit_id']} · {row['page']}", "", row["continuous_revised_record_de"], ""]
    (OUT / "HUNDRED_THIRTY_EIGHTH_BRACKET_FORMULAE_IN_CONTEXT.md").write_text("\n".join(readable).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertachtunddreißigste Runde: die zwei gesprochenen Klammern", "",
        "Both recurrent shared-deck frames are now expanded inside the complete event stream. F1 occurs in H2-S001,",
        "B3-S003 and, with local payload inside the span, B3-S021; it reads `zwei Posten unter demselben Sollmaß`.",
        "F2 occurs in H2-S002 and B1-S002 and reads",
        "`Fortsetzung mit demselben Ansatz`. In B1 the F2 shared skeleton legitimately brackets intervening",
        "specialist payload; it is not required to be an adjacent exact-card triple in the full stream.", "",
        "`CHOLOR` is revised globally from the redundant action phrase `damit weiter` to the carried object",
        "`derselbe Ansatz`. Only two events change. This is a useful model of the script: the common cards can form",
        "a sparse scaffold around locally memorized cards, like a technical formula with a nomenclator payload.", "",
        "Next use these bracketed statements to build a small source-to-card composer that predicts which shared",
        "cards surround a new workshop instruction while choosing specialist contents from a drawer.",
    ]
    (OUT / "HUNDRED_THIRTY_EIGHTH_BRACKET_FORMULA_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({"cards": len(out_cards), "events": len(out_events), "statements": len(out_statements), "records": len(out_records), "formula_occurrences": len(formula_occ), "paired_measure_occurrences": sum(r["formula_id"] == "F1_PAIRED_MEASURE" for r in formula_occ), "carried_preparation_occurrences": sum(r["formula_id"] == "F2_CARRIED_PREPARATION" for r in formula_occ), "changed_events": sum(r["master_card_id"] == "MC157" for r in out_events)}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
