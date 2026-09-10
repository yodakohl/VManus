"""Source-only independent collation and exhaustive compiler parity audit.

Expected cells come from the independently sealed M observation and its explicit
after-seal adjudication. The primary compiler runs in a separate subprocess only
as the test subject; none of its functions supplies expected results.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

SOURCE_HASH = "7647eb754fd68d939d041d7a6a35e1711d1783f936f316a5f669b0f58f39846c"
RECEIPTS = {
    "OBSERVER_A.json": "d786abd6b446762dfb5e90b274c25a29f0890507ce3967604aad16d9b27c301d",
    "OBSERVER_M.json": "ed5b2e7f0ca7fc30cacace927b92b584e733454fc3e9dd1a14efb6fd26f6bc28",
    "ADJUDICATION.json": "53b11dd7c2a3ea74f0c3d0a7891eb14bd210acaa993920a751897878e90aa367",
}
SOURCE_BYTES = {
    "kuun1880.pdf": "78be07bc3ebd06f683a6b06501fe38a2fb7f660fb77c9f25845a1035a62e09f9",
    "page-149.png": "34099878ae7ac823896232da391c483aef0575f4c8848e4b93e1c247c10561bd",
    "page-153.png": "1112a0e1d26ca987866b3ffd0cd6487731e1d6a982f5119114a223f120ea6301",
    "detail-149.png": "4eac18c0bb17b19bccc123bb4f3af6a92195cc056aa24b16a71f7c23cfc6d0c3",
}
TABLES = ("PRESENT", "IMPERFECT")
ROWS = ("1SG", "2SG", "3SG", "1PL", "2PL", "3PL")
SCHEMES = ("LETTER", "PAIR_LEFT", "PAIR_RIGHT")
ALTERED = ("IMPERFECT_1SG_C2", "IMPERFECT_3PL_C2")
OPTIONS = {
    ALTERED[0]: {"LETTER_ABSENT": list("mesindem"), "LETTER_PRESENT": list("mesinidem")},
    ALTERED[1]: {"LETTER_ABSENT": list("mesnident"), "LETTER_PRESENT": list("mesinident")},
}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def independently_unitize(atoms, scheme):
    if scheme == "LETTER":
        return [[atom] for atom in atoms]
    # Build groups from the chosen edge; right-pairing is reversed twice.
    work = list(atoms if scheme == "PAIR_LEFT" else reversed(atoms))
    groups = []
    while work:
        group = [work.pop(0)]
        if work:
            group.append(work.pop(0))
        groups.append(group)
    if scheme == "PAIR_RIGHT":
        groups = [list(reversed(group)) for group in reversed(groups)]
    require([a for group in groups for a in group] == atoms, "unit_roundtrip")
    return groups


def validate(source_path, compiler_path, source_cache=None):
    source_path, compiler_path = Path(source_path), Path(compiler_path)
    source_blob = source_path.read_bytes()
    require(sha(source_blob) == SOURCE_HASH, "frozen_source_hash")
    source = json.loads(source_blob)
    require(source["schema"] == "GDT900_FROZEN_SOURCE_V1", "source_schema")
    receipts = {}
    for name, expected_hash in RECEIPTS.items():
        blob = (source_path.parent / name).read_bytes()
        require(sha(blob) == expected_hash, "receipt_hash:" + name)
        receipts[name] = json.loads(blob)
    expected_observer_bindings = {name: value for name, value in RECEIPTS.items() if name != "ADJUDICATION.json"}
    require({r["artifact"]: r["sha256"] for r in source["observers"]} == expected_observer_bindings, "observer_binding")
    require(source["adjudication"]["artifact"] == "ADJUDICATION.json", "adjudication_name")
    require(source["adjudication"]["sha256"] == RECEIPTS["ADJUDICATION.json"], "adjudication_binding")
    adjudication = receipts["ADJUDICATION.json"]
    require(adjudication["original_receipt_sha256"] == RECEIPTS["OBSERVER_M.json"], "original_seal_binding")
    require(adjudication["cell"] == "IMPERFECT_3SG_C3" and adjudication["adjudicated_reading"] == "esituredi", "adjudication_scope")
    source_meta = source["source"]
    require(source_meta["pdf_sha256"] == SOURCE_BYTES["kuun1880.pdf"], "source_pdf_binding")
    require(source_meta["image_sha256"] == SOURCE_BYTES["detail-149.png"], "source_detail_binding")
    require(source_meta["second_rendering"]["sha256"] == SOURCE_BYTES["page-149.png"], "source_first_render_binding")
    native_bytes_verified = []
    if source_cache is not None:
        for name, expected_hash in SOURCE_BYTES.items():
            require(sha((Path(source_cache) / name).read_bytes()) == expected_hash, "native_source_bytes:" + name)
            native_bytes_verified.append(name)

    observation = receipts["OBSERVER_M.json"]
    require(len(observation["cells"]) == 36, "observer_36_cells")
    expected_cells = {}
    for cell in observation["cells"]:
        cell_id, printed = cell["id"], cell["printed"]
        require(cell_id not in expected_cells, "observer_duplicate_cell")
        if cell_id == "PRESENT_3PL_C1":
            require(printed == "audiūt", "observed_abbreviation")
            atoms = ["a", "u", "d", "i", "U_ABBR", "t"]
        elif cell_id == ALTERED[0]:
            require(printed == "mesin(.)dem¹", "observed_erasure_1")
            atoms = list("mesindem")
        elif cell_id == ALTERED[1]:
            require(printed == "mesinident²", "observed_erasure_2")
            atoms = list("mesinident")
        elif cell_id == adjudication["cell"]:
            require(printed == adjudication["original_reading"], "original_adjudication_letter")
            atoms = list(adjudication["adjudicated_reading"])
        else:
            require(printed.isascii() and printed.isalpha() and printed.islower(), "unexpected_unregistered_source_mark")
            atoms = list(printed)
        expected_cells[cell_id] = atoms
    require([t["id"] for t in source["tables"]] == list(TABLES), "table_order")
    seen = set()
    for table_index, table in enumerate(source["tables"]):
        require(len(table["rows"]) == 6, "complete_six_person_table")
        for row_index, row in enumerate(table["rows"]):
            require(len(row) == 3, "complete_three_language_row")
            for column, cell in enumerate(row, 1):
                expected_id = f"{TABLES[table_index]}_{ROWS[row_index]}_C{column}"
                require(cell["id"] == expected_id, "exact_row_column_binding")
                require(cell["graphemes"] == expected_cells[expected_id], "grapheme_parity:" + expected_id)
                require(cell["notes"] == (["1"] if expected_id == ALTERED[0] else ["2"] if expected_id == ALTERED[1] else []), "apparatus_scope")
                if expected_id in OPTIONS:
                    require(cell["alternatives"] == OPTIONS[expected_id], "explicit_letter_options")
                else:
                    require("alternatives" not in cell, "unregistered_cell_variant")
                seen.add(expected_id)
    require(seen == set(expected_cells) and len(seen) == 36, "complete_cell_set")
    variants = [dict(zip(ALTERED, pair)) for pair in itertools.product(("LETTER_ABSENT", "LETTER_PRESENT"), repeat=2)]
    require(source["variant_cells"] == list(ALTERED), "variant_cell_scope")
    require(source["variants"] == variants, "complete_four_variant_cartesian_union")
    require(source["unit_schemes"] == list(SCHEMES), "all_three_unit_schemes")
    traversals = [{"columns": list(columns), "major": major} for columns in itertools.permutations((0, 1, 2)) for major in ("ROW", "COLUMN")]
    expected = []
    inventories = {scheme: set() for scheme in SCHEMES}
    for variant in variants:
        for scheme in SCHEMES:
            for traversal in traversals:
                compiled = []
                column_rank = {column: rank for rank, column in enumerate(traversal["columns"])}
                grid = list(itertools.product(range(6), range(3)))
                grid.sort(key=lambda rc: (rc[0], column_rank[rc[1]]) if traversal["major"] == "ROW" else (column_rank[rc[1]], rc[0]))
                all_sequences = []
                for table in TABLES:
                    records = []
                    for row, column in grid:
                        cell_id = f"{table}_{ROWS[row]}_C{column + 1}"
                        atoms = OPTIONS[cell_id][variant[cell_id]] if cell_id in OPTIONS else expected_cells[cell_id]
                        units = independently_unitize(atoms, scheme)
                        records.append({"id": cell_id, "units": units})
                        inventories[scheme].update(tuple(unit) for unit in units)
                        all_sequences.append(tuple(tuple(unit) for unit in units))
                    require(len(records) == 18, "full_compiled_table")
                    compiled.append({"id": table, "cells": records})
                require(len(set(all_sequences)) == 36, "all_36_complete_source_words_distinct")
                expected.append({"variant": variant, "scheme": scheme, "traversal": traversal, "tables": compiled})

    # Black-box invocation of the frozen primary, after independently constructing
    # every expected cell and ordering. No target file is passed or opened.
    probe = """import importlib.util,json,sys
spec=importlib.util.spec_from_file_location('primary_source_under_test',sys.argv[1])
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
source=module.load(sys.argv[2])
records=[]
for variant in source['variants']:
 for scheme in module.SCHEMES:
  for traversal in module.TRAVERSALS:
   records.append({'variant':variant,'scheme':scheme,'traversal':traversal,'tables':module.tables(source,variant,scheme,traversal)})
print(json.dumps(records))
"""
    process = subprocess.run([sys.executable, "-c", probe, str(compiler_path.resolve()), str(source_path.resolve())], capture_output=True, text=True, check=True)
    actual = json.loads(process.stdout)
    require(actual == expected, "primary_compiler_all_144_variants_exact_parity")
    compiled_hash = sha(json.dumps(expected, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode())
    return {
        "schema": "GDT900_INDEPENDENT_SOURCE_VALIDATION_V1", "status": "PASS",
        "source_input_sha256": SOURCE_HASH, "compiler_sha256": sha(compiler_path.read_bytes()),
        "validator_sha256": sha(Path(__file__).read_bytes()), "observer_receipt_sha256": RECEIPTS,
        "native_source_sha256": SOURCE_BYTES, "native_source_bytes_verified": native_bytes_verified,
        "tables": 2, "cells": 36, "source_variants": 4, "unit_schemes": 3,
        "traversals": 12, "joint_compilations": len(expected), "compiled_cells_checked": 36 * len(expected),
        "compiled_family_sha256": compiled_hash,
        "unit_inventory_sizes_over_complete_variant_union": {key: len(value) for key, value in inventories.items()},
        "source_variant_union": variants,
        "checks": ["All 36 base cells agree with sealed M observation plus the explicit after-seal final-i correction", "Marked u remains one U_ABBR atom and the initial ordinary u is retained", "Only the two apparatus-specified i positions vary, with all four independent combinations", "All 144 source variant/unitization/traversal compilations match an independent implementation", "Both complete 18-cell tables and all 36 distinct whole-cell unit sequences survive every compilation", "Original A/M receipts and the separate adjudication are hash-bound and unchanged"],
        "scope": "Source and compiler audit only. No target, fit, manuscript translation or model witness. The finite erasure union is a conservative envelope, not four certified historical revision layers. Exact heading typography is excluded from the lexical-cell model and remains recorded as uncertain in the original M observation.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-input", required=True)
    parser.add_argument("--compiler", required=True)
    parser.add_argument("--source-cache")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = validate(args.source_input, args.compiler, args.source_cache)
    output = Path(args.output)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, ensure_ascii=True) + "\n")
    temporary.replace(output)
    print(json.dumps({key: result[key] for key in ("status", "cells", "source_variants", "joint_compilations", "compiled_cells_checked", "compiled_family_sha256")}))


if __name__ == "__main__":
    main()
