#!/usr/bin/env python3
"""Independent source-only replay of two sealed native Treviso readings.

No primary compiler, fit module, or target reader is imported. Native bytes
are checked when --native-dir is supplied; otherwise the published binding
between the two observations is checked without claiming reacquisition.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


BASE = Path(__file__).resolve().parents[1]
PINS = {
    "source_input": "aec96b65f3bc4248fd6979a3e69556720ad841523eca5c85d52ef6ce1c3e87cf",
    "observer_b": "b6317637ad52a4fdc846f65d0864d37aa4581129594920a85f29e4ea02e30beb",
    "observer_m": "7954fac9987cfb05fd9b973b2df587252d4c616a8a67de7876ad31fec3685f0e",
    "register_image": "8af134240a88ed8cdaafa40975fd09a347461c11b3a6cb7721e2f0f9404fbbb3",
}
ROLES = ["MULTIPLIER", "MULTIPLICATION_WORD", "MULTIPLICAND", "RESULT_WORD", "PRODUCT"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate(observer_b, observer_m, native_dir=None, source_input=None):
    source_input = source_input or BASE / "artifacts/SOURCE_INPUT.json"
    bindings = {"observer_b": digest(observer_b), "observer_m": digest(observer_m), "source_input": digest(source_input)}
    for name, got in bindings.items():
        require(got == PINS[name], "CHANGED_SEALED_" + name.upper())
    b = json.loads(Path(observer_b).read_text())
    m = json.loads(Path(observer_m).read_text())
    source = json.loads(Path(source_input).read_text())
    require(source["schema"] == "GDT902_FROZEN_ARITHMETIC_SOURCE_V1", "SOURCE_SCHEMA")
    require(source["source_receipts"] == {"B": bindings["observer_b"], "M": bindings["observer_m"]}, "SOURCE_RECEIPT_BINDING")
    require(source["source_image_sha256"] == PINS["register_image"], "SOURCE_IMAGE_BINDING")
    require(source["source_pdf_sha256"] == b["source"]["pdf_sha256"], "SOURCE_PDF_BINDING")
    require(len(b["blocks"]) == len(m["blocks"]) == 8, "BLOCK_COUNT")
    require(m["image"]["sha256"] == PINS["register_image"], "M_IMAGE_BINDING")
    require(not m["independence"]["read_other_observer_before_seal"], "M_NOT_INDEPENDENT")
    require(not m["independence"]["read_target_data"], "M_TARGET_EXPOSURE")
    require(not m["uncertain_rows"], "M_UNRESOLVED_ROWS")
    image_receipts = {r["filename"]: r for r in b["render_receipts"]}
    require(image_receipts["treviso-16.jpg"]["sha256"] == PINS["register_image"], "B_IMAGE_BINDING")
    require(image_receipts["treviso-16.jpg"]["pdf_page_one_based"] == 16, "B_PAGE_BINDING")
    require(m["field_order"] == ["first_factor", "fia", "second_factor", "fa", "product"], "M_FIELD_ORDER")

    all_rows, per_block, seen_ids = [], [], set()
    for k, (bb, mm) in enumerate(zip(b["blocks"], m["blocks"]), 2):
        require(bb["id"] == "T" + str(k) and mm["id"] == "B" + str(k), "BLOCK_ORDER")
        require(bb["block_order"] == k - 1 and bb["multiplier_decimal"] == str(k), "BLOCK_METADATA")
        require(bb["pdf_page_one_based"] == 16, "BLOCK_PAGE")
        require(bb["half"] == ("left" if k < 4 else "right"), "BLOCK_HALF")
        rows_b = [r["cells"] for r in bb["rows"]]
        rows_m = mm["rows"]
        require(rows_b == rows_m, "OBSERVER_CELL_DISAGREEMENT_" + str(k))
        require(len(rows_m) == bb["row_count"] == 11 - k, "COMPLETE_BLOCK_LENGTH")
        flat = [cell for row in rows_m for cell in row]
        require(flat == bb["sequence"], "B_COMPILED_SEQUENCE")
        require(bool(bb["block_boundary"]), "MISSING_BOUNDARY_RECORD")
        require([r[2] for r in rows_m] == [str(x) for x in range(k, 10)] + ["0"], "NATIVE_SECOND_FACTOR_ORDER")
        for j, (rb, row) in enumerate(zip(bb["rows"], rows_m), 1):
            require(len(row) == 5, "FIVE_FIELD_ROW")
            require(rb["id"] not in seen_ids, "DUPLICATE_ROW_ID")
            seen_ids.add(rb["id"])
            require(rb["id"] == "T%d_%02d" % (k, j), "ROW_ID")
            require(rb["row_order_in_block"] == j and rb["cell_roles"] == ROLES, "ROW_ORDER_OR_ROLE")
            require(row[0] == str(k) and row[1] == "fia" and row[3] == "fa", "ROW_FIELD_BINDING")
            require(all(x.isascii() and x.isdecimal() and str(int(x)) == x for x in (row[0], row[2], row[4])), "NONCANONICAL_NUMERAL")
            require(rb["numeric_values"] == [int(row[z]) for z in (0, 2, 4)], "B_NUMERIC_METADATA")
        require(rows_m[-1] == [str(k), "fia", "0", "fa", "0"], "ZERO_ROW_OR_END_BOUNDARY")
        all_rows.extend(rows_m)
        per_block.append({"id": bb["id"], "equations": len(rows_m), "fields": len(flat), "cell_parity": True})

    numerals = sorted({r[z] for r in all_rows for z in (0, 2, 4)}, key=int)
    fields = [x for r in all_rows for x in r]
    counts = Counter(fields)
    require(len(all_rows) == 44 and len(fields) == 220 and len(numerals) == 36, "REGISTER_TOTALS")
    require(counts["fia"] == counts["fa"] == 44 and counts["0"] == 16, "OPERATOR_ZERO_COUNTS")
    require(sum(r[4] == "0" for r in all_rows) == 8, "ZERO_PRODUCTS")
    require(set("".join(numerals)) == set("0123456789") and "1" not in numerals, "DIGIT_INVENTORY")
    require(all(int(r[0]) * int(r[2]) == int(r[4]) for r in all_rows), "INDEPENDENT_ARITHMETIC_PARITY")
    require(b["counts"]["distinct_realized_numeral_strings"] == len(numerals), "B_NUMERAL_COUNT")
    # Independently serialize M's actual cells by position, without importing
    # or using the primary compiler, or replacing rows by computed products.
    expected_records = []
    for k, block in enumerate(m["blocks"], 2):
        sequence = [("OP:" if column in (1, 3) else "NUM:") + cell
                    for row in block["rows"] for column, cell in enumerate(row)]
        expected_records.append({"id": "T" + str(k), "row_count": len(block["rows"]), "sequence": sequence})
    require(source["records"] == expected_records, "SOURCE_COMPLETE_COMPILATION")
    expected_atoms = sorted({cell for record in expected_records for cell in record["sequence"]})
    require(source["atoms"] == expected_atoms and len(expected_atoms) == 38, "SOURCE_ATOM_INVENTORY")
    require(source["digit_alphabet"] == list("0123456789"), "SOURCE_DIGIT_ALPHABET")
    require(source["operators"] == ["OP:fia", "OP:fa"], "SOURCE_OPERATOR_ALPHABET")
    require("NUM:1" not in source["atoms"], "FABRICATED_STANDALONE_ONE")

    native_checks = []
    if native_dir is not None:
        nd = Path(native_dir)
        for name, receipt in sorted(image_receipts.items()):
            require(Path(name).name == name, "NONLOCAL_RECEIPT_NAME")
            got = digest(nd / name)
            require(got == receipt["sha256"], "NATIVE_IMAGE_CHANGED_" + name)
            native_checks.append({"file": name, "sha256": got})
        got_pdf = digest(nd / "treviso1478.pdf")
        require(got_pdf == b["source"]["pdf_sha256"], "SOURCE_PDF_CHANGED")
        require((nd / "treviso1478.pdf").stat().st_size == b["source"]["pdf_bytes"], "SOURCE_PDF_SIZE")
        native_checks.append({"file": "treviso1478.pdf", "sha256": got_pdf})

    return {
        "schema": "GDT902_INDEPENDENT_SOURCE_VALIDATION_V1",
        "status": "PASS",
        "bindings": dict(bindings, register_image=PINS["register_image"]),
        "counts": {"blocks": 8, "equations": 44, "cells": 220, "numeric_cells": 132, "realized_numerals": 36, "operators": 2, "positive_products": 36, "zero_products": 8},
        "blocks": per_block,
        "numerals": numerals,
        "all_native_observer_cells_equal": True,
        "all_native_boundaries_equal": True,
        "source_complete_compilation_exact": True,
        "source_compiled_positions_checked": 220,
        "independent_integer_multiplication_parity": True,
        "native_bytes_rechecked": native_dir is not None,
        "native_bindings": native_checks,
        "source_compiler_imported": False,
        "target_read": False,
        "conditional_identifiability": [
            "Complete source block lengths45,40,35,30,25,20,15,10 are distinct. A position-preserving automorphism of this whole block family fixes every block and therefore every realized field value.",
            "After a fixed successful complete target projection, codes0,2..9 are realized as whole numeral fields. The field10 satisfies W10=K1 K0, so right cancellation gives the unique possible nonempty K1; this does not presume a standalone source field1.",
            "Source rigidity does not prove a unique target paragraph assignment, a unique foreground subset, existence of a key, or historical copying from this book. All alternative complete target models remain relevant."
        ],
        "claim_ceiling": "Two sealed native readings agree on the full fixed arithmetic register. Date, digit-primer interpretation and external end boundary additionally rely on B's separately bound observations; no target numeral or translation is established."
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--observer-b", type=Path, default=BASE / "artifacts/SOURCE_ARITHMETIC_B.json")
    ap.add_argument("--observer-m", type=Path, default=BASE / "artifacts/SOURCE_ARITHMETIC_M.json")
    ap.add_argument("--source-input", type=Path, default=BASE / "artifacts/SOURCE_INPUT.json")
    ap.add_argument("--native-dir", type=Path)
    ap.add_argument("--output", type=Path, default=BASE / "artifacts/SOURCE_VALIDATION.json")
    args = ap.parse_args()
    result = validate(args.observer_b, args.observer_m, args.native_dir, args.source_input)
    result["validator_sha256"] = digest(__file__)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": result["status"], "counts": result["counts"], "native_bytes_rechecked": result["native_bytes_rechecked"]}))


if __name__ == "__main__":
    main()
