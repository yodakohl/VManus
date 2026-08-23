#!/usr/bin/env python3
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


OUT = Path(__file__).resolve().parent
EXP = OUT.parents[1]
R138 = EXP / "yolo" / "sidequest_semantic_bracket_formula_revision_hundred_thirty_eighth"
R139 = EXP / "yolo" / "sidequest_semantic_productive_composer_hundred_thirty_ninth"

REPAIRS = {
    "C01": ("H1-S001", "Material; davon Anteil; Gefäß/Fluss; einsetzen; Sollmaß."),
    "C02": ("H3-S001", "Auswringen; stehen lassen; nachseihen; Klarauszug; schließen."),
    "C03": ("H2-S002", "Folgeansatz; weiter; derselbe Ansatz; weiter; Sollmaß; davon."),
    "C04": ("B1-S014", "Überführen; weiter; zur Zielstelle abführen; vom Ausgang weiter."),
    "C05": ("B3-S003", "Zwei Posten unter demselben Sollmaß; abführen; schließen."),
    "C06": ("B4-S003", "Überführen; danach dorthin; das nächste; lange einwirken; einsetzen; weiter; absetzen; schließen."),
    "C07": ("B4-S004|B4-S005", "Festbinden; dann Tuch einlegen, überführen und lange einwirken lassen; schließen."),
    "C08": ("B3-S034", "Arbeitsstufe; bereit; Anteil; Folgemaß; Zielposten; absetzen; schließen."),
}


def read_tsv(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def lcs(a, b):
    grid = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, x in enumerate(a, 1):
        for j, y in enumerate(b, 1):
            grid[i][j] = grid[i - 1][j - 1] + 1 if x == y else max(grid[i - 1][j], grid[i][j - 1])
    return grid[-1][-1]


def main():
    cards = read_tsv(R138 / "HUNDRED_THIRTY_EIGHTH_173_FORMULA_REVISED_DICTIONARY.tsv")
    events = read_tsv(R138 / "HUNDRED_THIRTY_EIGHTH_381_FORMULA_REVISED_EVENTS.tsv")
    composed = read_tsv(R139 / "HUNDRED_THIRTY_NINTH_EIGHT_COMPOSED_INSTRUCTIONS.tsv")
    by_form = {r["master_form"]: r for r in cards}
    by_statement = defaultdict(list)
    for row in events:
        by_statement[row["statement_id"]].append(row)
    pair_counts = Counter((a["master_card_id"], b["master_card_id"]) for group in by_statement.values() for a, b in zip(group, group[1:]))

    audits = []
    repaired = []
    for row in composed:
        source_forms = row["master_card_sequence"].split()
        source_ids = [by_form[x]["master_card_id"] for x in source_forms]
        pair_support = [pair_counts[(a, b)] for a, b in zip(source_ids, source_ids[1:])]
        nearest = max(by_statement, key=lambda sid: (lcs(source_ids, [r["master_card_id"] for r in by_statement[sid]]) / max(len(source_ids), len(by_statement[sid])), lcs(source_ids, [r["master_card_id"] for r in by_statement[sid]])))
        nearest_ids = [r["master_card_id"] for r in by_statement[nearest]]
        support_count = sum(n > 0 for n in pair_support)
        audits.append({
            "exercise_id": row["exercise_id"], "original_master_sequence": row["master_card_sequence"],
            "adjacent_pairs": str(len(pair_support)), "attested_adjacent_pairs": str(support_count),
            "pair_support_counts": "|".join(map(str, pair_support)) if pair_support else "NONE",
            "nearest_attested_statement": nearest,
            "nearest_lcs_cards": str(lcs(source_ids, nearest_ids)),
            "apprentice_verdict": "KEEP_FORMULA" if support_count == len(pair_support) else "REORDER_FROM_ATTESTED_TEMPLATE",
        })
        source_sids, spoken = REPAIRS[row["exercise_id"]]
        groups = [by_statement[sid] for sid in source_sids.split("|")]
        repaired_cards = [r for group in groups for r in group]
        repaired.append({
            "exercise_id": row["exercise_id"], "register": row["register"],
            "primary_drawer": row["specialist_drawer"], "source_statement_ids": source_sids,
            "original_instruction_de": row["ordinary_source_instruction_de"],
            "repaired_instruction_de": spoken,
            "repaired_master_sequence": " || ".join(" ".join(r["visible_surface"] for r in group) for group in groups),
            "repaired_literal_values_de": " || ".join(" | ".join(r["current_spoken_default_de"] for r in group) for group in groups),
            "template_policy": "COPY_ATTESTED_ORDER_THEN_SUBSTITUTE_ONLY_OWNER_OR_LOCAL_WHOLE_CARD",
        })

    write_tsv("HUNDRED_FORTIETH_EIGHT_COMPOSER_ECOLOGY_AUDITS.tsv", audits)
    write_tsv("HUNDRED_FORTIETH_EIGHT_REPAIRED_TEMPLATE_INSTRUCTIONS.tsv", repaired)

    manual = ["# Lehrmeisterkorrektur des produktiven Komponisten", "",
              "The hand renderer was sound; the free card order was too permissive. Use these rules:", "",
              "1. Begin from one attested complete statement template.",
              "2. Preserve its shared-card order and endpoint position.",
              "3. Substitute only the picture owner or one learned local whole card in the same slot.",
              "4. A bracket may contain local payload, but its two boundary cards stay in place.",
              "5. A second cell is allowed; do not force application and closure into one card string.",
              "6. Apply hand rendering only after this order is complete.", ""]
    for row in repaired:
        manual += [f"## {row['exercise_id']} · Vorlage {row['source_statement_ids']}", "",
                   row["repaired_instruction_de"], "", f"Karten: `{row['repaired_master_sequence']}`", "",
                   f"Wörtlich: {row['repaired_literal_values_de']}", ""]
    (OUT / "HUNDRED_FORTIETH_ATTESTED_ORDER_COMPOSER_MANUAL.md").write_text("\n".join(manual).rstrip() + "\n", encoding="utf-8")

    report = [
        "# Hundertvierzigste Runde: der Lehrmeister korrigiert die Kartenreihenfolge", "",
        "The R139 renderer works, but free semantic composition was too generous. None of the eight novel strings",
        "preserves every internal adjacent pair from the manuscript ecology. C05 preserves its paired-measure core",
        "and C03 preserves its carry-frame core; their added final cards create the unsupported joins. The other",
        "instructions use sensible words in orders not actually taught by the ten-page sample.", "",
        "The composer is therefore revised from FREE ORDER to TEMPLATE-BOUND SUBSTITUTION. Each of the eight",
        "instructions now inherits a full attested statement order. C07 honestly uses two cells: fastening, then",
        "cloth transfer and long contact. C02 adopts the actual H3 wring/stand/re-strain/clear-result order. C08",
        "adopts the actual stage/ready/share/following-measure/target/settle order.", "",
        "This makes the 1420 workshop model more realistic. An apprentice did not generate arbitrary strings from",
        "a dictionary; the apprentice copied a known clause mould, changed the pictured owner or one local payload",
        "card, and only then rendered it in a personal hand. Next turn these eight repaired templates into a compact",
        "phrasebook with slots and show which of the 116 statements instantiate each mould.",
    ]
    (OUT / "HUNDRED_FORTIETH_ATTESTED_ORDER_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps({"audited_instructions": len(audits), "repaired_instructions": len(repaired), "fully_adjacent_supported": sum(r["apprentice_verdict"] == "KEEP_FORMULA" for r in audits), "source_statements_used": len({sid for r in repaired for sid in r["source_statement_ids"].split("|")})}, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
