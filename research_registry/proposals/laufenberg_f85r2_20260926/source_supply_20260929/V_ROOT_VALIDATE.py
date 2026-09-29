"""Reproduce the owned-row account and an algebraic countermodel, not meaning."""
import argparse
import csv
import hashlib
import io
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    source = HERE / "L_F105V_COMPLETE_PARAGRAPH.tsv"
    card_path = HERE / "V_01_LOCAL_CORE_DIVISION.json"
    units_path = HERE / "V_COMPLETE_UNITS.json"
    card = json.loads(card_path.read_text())["design"]
    units = json.loads(units_path.read_text())
    rows = list(csv.DictReader(io.StringIO(source.read_text()), delimiter="\t"))
    assert len(rows) == 90 and len({r["source_group_id"] for r in rows}) == 90
    assert {r["page"] for r in rows} == {"f105v"}
    assert {r["locus"] for r in rows} == {"f105v.5", "f105v.6", "f105v.7"}
    assert units["source_sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert units["source_rows"] == rows
    index = {(r["edition"], r["locus"], int(r["source_group_index"])): r for r in rows}
    assert set(r["edition"] for r in rows) == {"ZL3b", "IT2a", "RF1b"}
    for unit in units["units"]:
        reader = unit["edition"]
        assert unit["positions"] == 30
        for line in unit["lines"]:
            selected = [r for r in rows if r["edition"] == reader and r["locus"] == line["locus"]]
            assert line["groups"] == [r["ivtff_group_raw"] for r in selected]
            assert line["group_ids"] == [r["source_group_id"] for r in selected]

    # Explicit countermodel: same cuts, arguments, identities and types;
    # only operand orientation changes. These are not manuscript quantities.
    witness = {"a": Fraction(2), "u": Fraction(3), "x": Fraction(4), "z": Fraction(6)}
    fixed = [
        ("E1", "f105v.5", 3, "daiin", "chedy", "x", "a"),
        ("E2", "f105v.5", 5, "daiin", "okaildy", "z", "a"),
        ("E3", "f105v.6", 4, "dar", "aiin", "a", "u"),
        ("E4", "f105v.6", 7, "dar", "ar", "u", "u"),
    ]
    expressions = []
    roles = {}
    for source_span, (eid, locus, pos, op, operand, numerator, denominator) in zip(card["exact_authored_spans"], fixed, strict=True):
        assert source_span["locus"] == locus
        assert source_span["groups"] == [pos, pos + 1]
        assert source_span["raw"] == op + " " + operand
        forward = witness[numerator] / witness[denominator]
        inverse = witness[denominator] / witness[numerator]
        expressions.append({"id": eid, "locus": locus, "positions": [pos, pos + 1],
                            "raw": op + " " + operand,
                            "forward": numerator + "/" + denominator,
                            "inverse": denominator + "/" + numerator,
                            "illustrative_forward": str(forward),
                            "illustrative_inverse": str(inverse),
                            "observed_value": None})
        for reader in ("ZL3b", "IT2a", "RF1b"):
            left = index[(reader, locus, pos)]
            right = index[(reader, locus, pos + 1)]
            assert left["ivtff_group_raw"] == op and right["ivtff_group_raw"] == operand
            assert left["right_separator"] == right["left_separator"] == "DEFINITE_SPACE"
            roles[left["source_group_id"]] = (eid, "PROPOSED_COMPOUND_OPERATOR")
            roles[right["source_group_id"]] = (eid, "PROPOSED_QUANTITY_ARGUMENT")
    assert expressions[-1]["illustrative_forward"] == expressions[-1]["illustrative_inverse"] == "1"
    assert all(e["illustrative_forward"] != e["illustrative_inverse"] for e in expressions[:3])
    assert card["assignment_account"]["remaining_positions"] == 22
    output_rows = [dict(r, expression=roles.get(r["source_group_id"], ("", "UNKNOWN"))[0],
                        proposed_role=roles.get(r["source_group_id"], ("", "UNKNOWN"))[1]) for r in rows]
    counts = {ed: dict(Counter(r["proposed_role"] for r in output_rows if r["edition"] == ed))
              for ed in ("ZL3b", "IT2a", "RF1b")}
    assert all(v == {"UNKNOWN": 22, "PROPOSED_COMPOUND_OPERATOR": 4, "PROPOSED_QUANTITY_ARGUMENT": 4}
               for v in counts.values())
    text = io.StringIO()
    writer = csv.DictWriter(text, fieldnames=list(output_rows[0]), delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(output_rows)
    receipt = {
        "status": "PASS_ROW_ACCOUNTING_AND_ALGEBRA_ONLY",
        "inputs": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in (source, card_path, units_path)},
        "rows": len(rows), "counts_by_reader": counts, "expressions": expressions,
        "illustrative_positive_quantities_not_target_values": {k: str(v) for k, v in witness.items()},
        "observed_numeric_results": 0, "independent_meaning_confirmation_capacity": 0,
        "confirmed_words": 0,
        "limit": "No parser, output semantics, rival subject binding, or manuscript arithmetic validated.",
    }
    outputs = {"V_ROOT_ACCOUNT.tsv": text.getvalue(),
               "V_ROOT_VALIDATION.json": json.dumps(receipt, ensure_ascii=False, indent=2) + "\n"}
    for name, content in outputs.items():
        path = HERE / name
        if args.check:
            assert path.read_text() == content, name
        else:
            path.write_text(content)
    print(receipt["status"], "90 rows; 4 shared pairs; opposite orientations retain self-ratio 1")


if __name__ == "__main__":
    main()
