#!/usr/bin/env python3
"""Independent arithmetic, source, fixed-parse and result audit for GDT969."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import re

E = Path(__file__).resolve().parents[1]
R = E.parents[2]
A = E / "artifacts"
OPS = "INPUT HIGH ROOT SQUARE SUB DOUBLE APPEND QUOTIENT CHOOSE MUL SUB APPEND SQUARE SUB APPEND MOD SQUARE MOD MOD ADD MOD MOD CHECK".split()
EDITION_ORDER = ("ZL3b", "IT2a", "RF1b")


def require(ok, message):
    if not ok:
        raise AssertionError(message)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_trace(n):
    """Compute root by an independent square interval; verify the ten-digit rule."""
    require(100 <= n <= 9999, "Input range")
    leading, last_pair = divmod(n, 100)
    tens, units = divmod(last_pair, 10)
    small = next(x for x in range(1, 10) if x*x <= leading < (x+1)*(x+1))
    root = next(x for x in range(10, 100) if x*x <= n < (x+1)*(x+1))
    chosen = root - 10*small
    first_square = small*small
    initial_remainder = leading-first_square
    doubled = small+small
    joined = initial_remainder*10+tens
    estimate = joined//doubled
    trials = {x: 10*(joined-doubled*x)+units-x*x for x in range(10)}
    require(chosen == max(x for x, rem in trials.items() if rem >= 0), "Maximal digit")
    product = doubled*chosen
    cross_remainder = joined-product
    brought = cross_remainder*10+units
    second_square = chosen*chosen
    remainder = brought-second_square
    root_residue, remainder_residue = root % 7, remainder % 7
    residue_square = root_residue*root_residue
    square_residue = residue_square % 7
    residue_sum = square_residue+remainder_residue
    require(n == root*root+remainder and 0 <= remainder <= 2*root, "Exact endpoint")
    require(cross_remainder >= 0 and residue_sum % 7 == n % 7, "Residual/proof")
    return [n, leading, small, first_square, initial_remainder, doubled, joined,
            estimate, chosen, product, cross_remainder, brought, second_square,
            remainder, root, root_residue, residue_square, square_residue,
            remainder_residue, residue_sum, residue_sum % 7, n % 7]


def independent_parse(words, values, width):
    """Constraint history reconstructs the unique suffix cut; no runner import."""
    if len(words) != 23 or len(values) != 22 or width < 1:
        return None, ("INVALID_PARSE_DOMAIN", 0)
    if not all(isinstance(w, str) and re.fullmatch("[a-z]+", w) for w in words):
        return None, ("INVALID_PARSE_DOMAIN", 0)
    operator_history = []
    digit_history = []
    for position in range(23):
        role, word = OPS[position], words[position]
        decimal = "" if position == 22 else str(values[position])
        start = len(word)-width*len(decimal)
        if start < 1:
            return None, ("NONEMPTY_PREFIX_LENGTH", position+1)
        operator = word[:start]
        earlier_same = [code for old_role, code in operator_history if old_role == role]
        if earlier_same and any(code != operator for code in earlier_same):
            return None, ("OPCODE_INCONSISTENT", position+1)
        if not earlier_same and any(code == operator for _, code in operator_history):
            return None, ("OPCODE_NOT_DISTINCT", position+1)
        operator_history.append((role, operator))
        for j, digit in enumerate(decimal):
            code = word[start+j*width:start+(j+1)*width]
            if any(old_digit == digit and old_code != code for old_digit, old_code in digit_history):
                return None, ("DIGIT_INCONSISTENT", position+1)
            if any(old_code == code and old_digit != digit for old_digit, old_code in digit_history):
                return None, ("DIGIT_NOT_DISTINCT", position+1)
            digit_history.append((digit, code))
    return {"width": width, "opcodes": dict(operator_history), "digits": dict(digit_history)}, None


def independent_combine(left, right):
    if left["width"] != right["width"] or left["opcodes"] != right["opcodes"]:
        return None
    pairs = list(left["digits"].items()) + list(right["digits"].items())
    by_digit, by_code = defaultdict(set), defaultdict(set)
    for digit, code in pairs:
        by_digit[digit].add(code)
        by_code[code].add(digit)
    if any(len(v) != 1 for v in by_digit.values()) or any(len(v) != 1 for v in by_code.values()):
        return None
    return {"width": left["width"], "opcodes": dict(left["opcodes"]),
            "digits": {digit: next(iter(values)) for digit, values in by_digit.items()}}


def completions(key):
    missing = [str(i) for i in range(10) if str(i) not in key["digits"]]
    choices = 26**key["width"]-len(key["digits"])
    count = 1
    for _ in missing:
        count *= choices
        choices -= 1
    return {"missing_digits": missing, "distinct_completion_count": count,
            "interpretation": "all injective unused literal[a-z] strings of the same width; no preferred completion"}


def encode(values, key):
    return [key["opcodes"][op] + ("" if i == 22 else "".join(key["digits"][d] for d in str(values[i])))
            for i, op in enumerate(OPS)]


def synthetics():
    # Loading the primary only cross-checks planted cases; independent cores above
    # do not call it, and importing run.py does not execute main or load targets.
    spec = importlib.util.spec_from_file_location("primary969_synthetic_only", E/"src/run.py")
    primary = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(primary)
    ordered = list(dict.fromkeys(OPS))
    operations = {op: "q"+chr(97+i) for i, op in enumerate(ordered)}
    operations["INPUT"] = "q"  # Deliberate prefix overlap with other opcodes.
    keys = []
    count = 0
    for width in (1, 2):
        key = {"width": width, "opcodes": operations,
               "digits": {str(i): chr(97+i)*width for i in range(10)}}
        for n in (100, 105, 864, 960, 1234, 6142, 9999):
            values = independent_trace(n)
            words = encode(values, key)
            ours, reason = independent_parse(words, values, width)
            theirs, primary_reason = primary.parse(words, values, width)
            require(reason is primary_reason is None and ours == theirs, "Synthetic positive parse")
            require(encode(values, ours) == words, "Synthetic exact reencoding")
            require(completions(ours) == primary.completion(theirs), "Synthetic completion count")
            keys.append((n, ours))
            count += 1
    base = {"width": 1, "opcodes": operations, "digits": {str(i): chr(97+i) for i in range(10)}}
    values = independent_trace(864)
    words = encode(values, base)
    mutants = []
    short = list(words); short[0] = "a"; mutants.append(short)
    same = list(words); same[1] = operations["INPUT"] + base["digits"]["8"]; mutants.append(same)
    opchange = list(words); opchange[12] = "zz" + opchange[12][len(operations["SQUARE"]):]; mutants.append(opchange)
    wrongvalues = list(values); wrongvalues[13] += 1; mutants.append(encode(wrongvalues, base))
    alias = {**base, "digits": {**base["digits"], "1": base["digits"]["0"]}}
    mutants.append(encode(values, alias))
    for mutant in mutants:
        own, reason = independent_parse(mutant, values, 1)
        other, why = primary.parse(mutant, values, 1)
        require(own is other is None and reason == why, "Synthetic first-contradiction parity")
        count += 1
    require(independent_parse(words[:-1], values, 1)[0] is None, "Truncation guard")
    require(independent_parse(words, values, 0)[0] is None, "Width guard")
    count += 2
    samewidth = [key for n, key in keys if key["width"] == 1 and n in (864, 960, 6142)]
    joint = independent_combine(independent_combine(samewidth[0], samewidth[1]), samewidth[2])
    require(joint is not None and len(joint["digits"]) == 10, "Three-program shared complete key")
    require(primary.combine(primary.combine(samewidth[0], samewidth[1]), samewidth[2]) == joint, "Joint parity")
    count += 1
    for bad in (dict(joint, width=2),
                dict(joint, opcodes={**joint["opcodes"], "HIGH": "zzz"}),
                dict(joint, digits={**joint["digits"], "0": "zz"})):
        require(independent_combine(joint, bad) is None and primary.combine(joint, bad) is None, "Incompatible keys")
        count += 1
    # Mutual injectivity can fail without a same-digit assignment conflict.
    left = dict(joint, digits={"0": "a"})
    right = dict(joint, digits={"1": "a"})
    require(independent_combine(left, right) is None and primary.combine(left, right) is None, "Cross-record digit alias")
    count += 1
    require((864-22*22-23) % 7 == 0 and 0 <= 23 <= 44 and 864 != 22*22+23, "Modulo countercase")
    require(independent_trace(960)[13] == 2*independent_trace(960)[14], "Non-strict bound case")
    require(independent_trace(105)[19:22] == [7, 0, 0], "Post-sum reduction")
    return count+3


def source_checks():
    with (A/"SOURCE_PROGRAMMES.tsv").open(newline="") as stream:
        reader = csv.reader(stream, delimiter="\t")
        require(next(reader) == [f"{i+1}_{op}" for i, op in enumerate(OPS)], "Source TSV header")
        total = 0
        for n, row in enumerate(reader, start=100):
            require(n <= 9999 and row == [str(v) for v in independent_trace(n)]+["CHECK"], "Source trace row")
            total += 1
    require(total == 9900, "Complete source domain")
    summary = read(A/"SOURCE_PROGRAMME_SUMMARY.json")
    require(summary["programmes"] == total and summary["range"] == [100, 9999], "Source summary domain")
    require(summary["opcode_sequence"] == OPS and summary["numeric_outputs"] == 22 and summary["whole_groups"] == 23, "Source shape")
    expected_examples = (100, 105, 153, 864, 960, 1234, 6142, 8171, 8172, 9999)
    require(summary["examples"] == {str(n): independent_trace(n) for n in expected_examples}, "Source examples")
    return total


def lock_checks():
    lock = read(E/"PREREG_LOCK.json")
    require(lock["stage"] == "AFTER_METADATA_PREFLIGHT_BEFORE_NUMERIC_TARGET_FIT", "Registration stage")
    bindings = lock["files"]
    for relative in ("METHOD.md", "PREREGISTRATION.md", "src/run.py", "artifacts/SOURCE_PROGRAMMES.tsv", "artifacts/SOURCE_PROGRAMME_SUMMARY.json"):
        require((E/relative).relative_to(R).as_posix() in bindings, "Missing scientific binding")
    for name, expected in bindings.items():
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "Bound path")
        require(sha(R/name) == expected, "Frozen source mismatch: "+name)
    return len(bindings)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration-only", action="store_true")
    args = parser.parse_args()
    receipt = {"status": "PASS_REGISTRATION_ONLY" if args.registration_only else "PASS",
               "registration_only": args.registration_only,
               "source_programmes_checked": source_checks(),
               "synthetic_cases": synthetics(),
               "bound_files_checked": lock_checks(),
               "validator_sha256": sha(Path(__file__)),
               "prereg_lock_sha256": sha(E/"PREREG_LOCK.json"),
               "claim_ceiling": "Conditional source, code and result fidelity; no meaning confirmation."}
    if not args.registration_only:
        raise NotImplementedError("Actual target reconciliation will be added after public registration.")
    (A/"VALIDATION.json").write_text(json.dumps(receipt, sort_keys=True, indent=2)+"\n")
    print(json.dumps({k: receipt[k] for k in ("status", "source_programmes_checked", "synthetic_cases")}, sort_keys=True))


if __name__ == "__main__":
    main()

