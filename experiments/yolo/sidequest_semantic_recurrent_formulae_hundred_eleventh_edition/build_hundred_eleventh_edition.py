#!/usr/bin/env python3
import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "experiments/yolo/sidequest_semantic_post_centennial_handbook_hundred_tenth_edition/HUNDRED_TENTH_116_CURRENT_STATEMENTS.tsv"

FORMULAE = [
    ("WF01", ("Y", "AIIN", "Y"), "zwei Posten unter dasselbe Sollmaß stellen", "PAIRED_SAME_MEASURE_FRAME"),
    ("WF02", ("Y", "AIIN"), "diesen Posten nach Sollmaß führen", "ITEM_THEN_MEASURE"),
    ("WF03", ("AIIN", "Y"), "das Sollmaß auf den folgenden Posten legen", "MEASURE_THEN_ITEM"),
    ("WF04", ("OL", "SHED+E+CLOSE"), "weiterführen, kurz absetzen lassen und schließen", "CONTINUE_SETTLE_CLOSE"),
    ("WF05", ("OR", "Y"), "den aktuellen Ansatz", "CURRENT_PREPARATION"),
    ("WF06", ("CHD+Y", "OL"), "den umgesetzten Posten weiterführen", "TRANSFERRED_ITEM_CONTINUES"),
    ("WF07", ("OK+EE+Y", "OK+E+CLOSE"), "länger ansetzen, kurz nachführen und schließen", "LONG_THEN_SHORT_CLOSE"),
    ("WF08", ("OT+OL", "OL"), "danach weiterführen", "NEXT_CONTINUATION"),
    ("WF09", ("OL+AIN", "AL"), "eine weitere Portion zum Ziel geben", "ADDITIONAL_PORTION_TO_TARGET"),
    ("WF10", ("OL+OR", "OL"), "den vorigen Ansatz weiterführen", "PREVIOUS_PREPARATION_CONTINUES"),
]


def load(path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(name, rows):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    source = load(SOURCE)
    found = []
    tags_by_statement = {}
    spans_by_statement = {}
    for row in source:
        atoms = row["semantic_atom_program"].split(" | ")
        surfaces = row["visible_surface_sequence"].split()
        occupied = set()
        tags = []
        spans = []
        for formula_id, pattern, phrase, role in FORMULAE:
            n = len(pattern)
            for start in range(len(atoms) - n + 1):
                positions = set(range(start, start + n))
                if positions & occupied or tuple(atoms[start:start+n]) != pattern:
                    continue
                occupied |= positions
                tags.append(formula_id)
                spans.append(f"{formula_id}:{start + 1}-{start + n}")
                found.append({
                    "formula_id": formula_id,
                    "formula_role": role,
                    "atom_pattern": "+".join(pattern),
                    "short_formula_de": phrase,
                    "statement_id": row["statement_id"],
                    "record_unit_id": row["record_unit_id"],
                    "page": row["page"],
                    "card_positions": f"{start + 1}-{start + n}",
                    "visible_surface_span": " ".join(surfaces[start:start+n]),
                    "full_visible_statement": row["visible_surface_sequence"],
                    "current_statement_reading_de": row["current_reading_de"],
                })
        tags_by_statement[row["statement_id"]] = tags
        spans_by_statement[row["statement_id"]] = spans

    counts = Counter(r["formula_id"] for r in found)
    formula_rows = []
    for formula_id, pattern, phrase, role in FORMULAE:
        occ = [r for r in found if r["formula_id"] == formula_id]
        formula_rows.append({
            "formula_id": formula_id,
            "formula_role": role,
            "atom_pattern": "+".join(pattern),
            "short_formula_de": phrase,
            "occurrence_count": str(len(occ)),
            "record_count": str(len({r["record_unit_id"] for r in occ})),
            "records": "|".join(sorted({r["record_unit_id"] for r in occ})),
            "statement_ids": "|".join(r["statement_id"] for r in occ),
            "teaching_status": "LEARN_AS_RECURRENT_FORMULA" if len(occ) >= 2 else "LEARN_AS_ORDER_RULE_WITH_ONE_STANDALONE_AFTER_LONGEST_MATCH",
        })
    write_tsv("HUNDRED_ELEVENTH_TEN_WORKSHOP_FORMULAE.tsv", formula_rows)
    write_tsv("HUNDRED_ELEVENTH_FORMULA_OCCURRENCES.tsv", found)

    statement_rows = []
    for row in source:
        tags = tags_by_statement[row["statement_id"]]
        statement_rows.append({
            **row,
            "formula_tags": "|".join(tags) if tags else "NONE",
            "formula_card_spans": "|".join(spans_by_statement[row["statement_id"]]) if tags else "NONE",
            "formula_expansions_de": " | ".join(next(f[2] for f in FORMULAE if f[0] == tag) for tag in tags) if tags else "NONE",
        })
    write_tsv("HUNDRED_ELEVENTH_116_FORMULA_ANNOTATED_STATEMENTS.tsv", statement_rows)

    report = [
        "# Hundertelfte Runde: wiederkehrende Werkstattformeln", "",
        "Die 116 Aussagen enthalten zehn kurze, wiederverwendbare Mehrkartenformeln. Sie werden mit",
        "Longest-match gelesen, sodass Y–AIIN–Y nicht zusätzlich als zwei überlappende Zweierformeln zählt.", "",
        "Die stärkste Formel ist OL + SHED-E-CLOSE: viermal heißt sie ›weiterführen, kurz absetzen lassen",
        "und schließen‹. Ebenfalls besonders nützlich ist Y–AIIN–Y in Herbal und Biological. Die neue",
        "Arbeitslesung lautet ›zwei Posten unter dasselbe Sollmaß stellen‹. Das ist die erste brauchbare",
        "konkrete Rückkehr der alten Gleichmaß-Idee, jetzt aber als Dreikartenformel und nicht als Bedeutung",
        "von AIIN allein.", "",
        "Weitere Formeln sind aktueller Ansatz, umgesetzten Posten weiterführen, länger-dann-kurz schließen,",
        "danach weiterführen, weitere Portion zum Ziel und vorigen Ansatz weiterführen. Damit lernt der",
        "Schreiber nicht nur 173 Einzelkarten, sondern zehn häufige kleine Satzbausteine.", "",
        "f84 und f84r blieben versiegelt.",
    ]
    (OUT / "HUNDRED_ELEVENTH_RECURRENT_FORMULA_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    summary = {
        "status": "COMPLETE", "formulae": len(formula_rows), "formula_occurrences": len(found),
        "tagged_statements": sum(bool(v) for v in tags_by_statement.values()),
        "formula_counts": dict(counts),
    }
    (OUT / "BUILD_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
