"""Small conditional word-grammar proof; no source corpus or native query."""
from pathlib import Path
import datetime
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREFIX = "HAND_WRITER_1193_MEDIAL_CAPACITY_"

# Independent hand segmentation from the already reviewed nine exact forms.
HAND = {
    "daldy": "d a l d y",
    "daiin": "d a i i n",
    "chedy": "ch e d y",
    "ol": "o l",
    "aiin": "a i i n",
    "cheoltchedaiin": "ch e o l t ch e d a i i n",
    "cfham": "cfh a m",
    "ckholsy": "ckh o l s y",
    "kydainy": "k y d a i n y",
}


def main():
    contract_path = HERE / (PREFIX + "CONTRACT_20261006.json")
    contract = json.loads(contract_path.read_text())
    for path, digest in contract["inputs_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    table = json.loads((ROOT / "experiments/yolo/gdt1193_three_source_code_cycle/artifacts/PUBLIC_TABLE.json").read_text())
    alph = table["alphabets"]
    initial, medial, final = alph["initial"][:21], alph["medial"][:3], alph["final"][:6]
    assert len(set(medial)) == 3
    pattern = re.compile("|".join(re.escape(g) for g in sorted(contract["working_alphabet"], key=lambda g: (-len(g), g))))
    rows = []
    for word in contract["words"]:
        glyphs = pattern.findall(word)
        assert "".join(glyphs) == word
        assert glyphs == HAND[word].split()
        inner = glyphs[1:-1]
        violations = []
        if len(glyphs) < 2:
            violations.append("shorter_than_two")
        if glyphs[0] not in initial:
            violations.append("initial")
        if set(inner) - set(medial):
            violations.append("interior")
        if glyphs[-1] not in final:
            violations.append("final")
        rows.append({"word": word, "glyphs": glyphs, "interior_types": sorted(set(inner)),
                     "interior_type_count": len(set(inner)), "literal_grammar_violations": violations,
                     "necessary_literal_grammar_pass": not violations,
                     "all_global_bijections_excluded_by_interior_capacity": len(set(inner)) > len(set(medial))})
    # Hand-cardinality checks do not derive expected answers from the parser.
    by_word = {row["word"]: row for row in rows}
    assert by_word["cheoltchedaiin"]["interior_type_count"] == 8
    assert by_word["kydainy"]["interior_type_count"] == 5
    assert [r["word"] for r in rows if r["necessary_literal_grammar_pass"]] == ["ol"]
    assert [r["word"] for r in rows if r["all_global_bijections_excluded_by_interior_capacity"]] == ["cheoltchedaiin", "kydainy"]
    result = {"status": "FIXED_THREE_MEDIAL_GLYPH_ARCHITECTURE_CONTRADICTED_CONDITIONALLY",
              "completed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
              "program_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "actual_active_banks": {"initial": initial, "medial": medial, "final": final},
              "rows": rows,
              "proof": "A bijection preserves distinctness. The model offers three interior glyph types; one fixed observed whole needs eight and another needs five. Dictionary entries, initial-state counters, initial styles and length reassignment cannot change that bound.",
              "validation": "All bound input hashes verified; regex working-unit parser agrees with nine manually written vectors; independent hand cardinalities 8 and5 and explicit literal-bank checks agree. Same-author inspection, not blinded native evidence.",
              "scope": "Conditional on one observed whole per output group and the fixed22working units. No glyph meaning, general codebook rejection, new image, native corpus count, historical claim or statistical test.1193basicPASS and1195different-ruleFAIL remain unchanged."}
    output = HERE / (PREFIX + "RESULT_20261006.json")
    assert not output.exists(), "Preserve the first result; use an explicit temporary output for replay."
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"status": result["status"], "literal_necessary_pass": ["ol"],
                      "relabeling_counterexamples": {"cheoltchedaiin": 8, "kydainy": 5}}))


if __name__ == "__main__":
    main()
