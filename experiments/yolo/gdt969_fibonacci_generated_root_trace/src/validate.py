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


def reconstruct_targets():
    """Read the fixed original caches; independently form start/end intervals."""
    parent = R/"experiments/yolo/gdt915_terminal_lr_phrase_transfer"
    inherited = read(R/"experiments/yolo/gdt928_multi_anchor_complete_paragraphs/PREREG_LOCK.json")["files"]
    for name, digest in inherited.items():
        require(sha(R/name) == digest, "Inherited source hash")
    allowed = set(read(parent/"src/SPEC.json")["allowed_selectors"])
    require(len(allowed) == 179 and not any(p.startswith(("f84", "f116v")) for p in allowed), "Closed source scope")
    capacity = read(R/"research_registry/work_batches/ten_hours_20260915/ROOT_TRACE_CAPACITY.json")
    targets, denominators = {}, {}
    for ed in EDITION_ORDER:
        pages, seen, den = defaultdict(list), set(), Counter()
        for phase in ("DISCOVERY", "EVALUATION"):
            cache = read(parent/"artifacts"/f"SOURCE_{phase}_{ed}.json")
            ix = {name: i for i, name in enumerate(cache["group_columns"])}
            for raw in cache["lines"]:
                m = raw["metadata"]
                require(m["page"] in allowed, "Unadmitted selector")
                if m["kind"] != "P":
                    continue
                identity = (m["page"], m["locus"], m["source_row_index"])
                require(identity not in seen, "Duplicate source line")
                seen.add(identity)
                groups = raw["groups"]
                words = [g[ix["ivtff_group_raw"]] for g in groups]
                indices = [int(g[ix["source_group_index"]]) for g in groups]
                literal = all(re.fullmatch("[a-z]+", word) for word in words)
                consecutive = all(v == u+1 for u, v in zip(indices, indices[1:]))
                seams = all(u[ix["right_separator"]] == v[ix["left_separator"]] == "DEFINITE_SPACE"
                            for u, v in zip(groups, groups[1:]))
                pages[m["page"]].append({"row": int(m["source_row_index"]),
                    "locus": m["locus"], "number": int(m["locus"].rsplit(".", 1)[1]),
                    "start": m["paragraph_start"] == "1", "end": m["paragraph_end"] == "1",
                    "words": words, "ids": [g[ix["source_group_id"]] for g in groups],
                    "eligible": bool(len(words) >= 2 and literal and consecutive and seams)})
                den["P_lines"] += 1
        frames, eligible_targets = [], []
        for page, lines in sorted(pages.items()):
            lines.sort(key=lambda line: line["row"])
            starts = [i for i, line in enumerate(lines) if line["start"]]
            for j, first in enumerate(starts):
                limit = starts[j+1] if j+1 < len(starts) else len(lines)
                last = next((i for i in range(first, limit) if lines[i]["end"]), None)
                if last is None:
                    den["unclosed_start" if j+1 < len(starts) else "unclosed_end"] += 1
                    continue
                block = lines[first:last+1]
                numbers = [line["number"] for line in block]
                if numbers != list(range(numbers[0], numbers[0]+len(numbers))):
                    den["gapped_paragraphs"] += 1
                    continue
                den["complete_paragraphs"] += 1
                den["anchor_lines"] += sum(line["eligible"] for line in block)
                frame = {"id": page+"|"+block[0]["locus"]+"-"+block[-1]["locus"],
                         "page": page, "leaf": int(re.match(r"f(\d+)", page)[1]),
                         "groups": sum(len(line["words"]) for line in block),
                         "eligible": all(line["eligible"] for line in block),
                         "ineligible_lines": [line["locus"] for line in block if not line["eligible"]]}
                frames.append(frame)
                if frame["groups"] == 23 and frame["eligible"]:
                    target = {k: frame[k] for k in ("id", "page", "leaf", "groups")}
                    target["words"] = [w for line in block for w in line["words"]]
                    target["source_ids"] = [sid for line in block for sid in line["ids"]]
                    require(len(target["source_ids"]) == len(set(target["source_ids"])) == 23, "Group ownership")
                    eligible_targets.append(target)
        hist = {str(n): v for n, v in Counter(f["groups"] for f in frames).items()}
        literal_hist = {str(n): v for n, v in Counter(f["groups"] for f in frames if f["eligible"]).items()}
        candidate_rows = [f for f in frames if f["groups"] == 23]
        leaves = sorted({f["leaf"] for f in candidate_rows if f["eligible"]})
        own_capacity = {"complete": len(frames), "literal": sum(literal_hist.values()),
            "all_length_histogram": hist, "literal_length_histogram": literal_hist,
            "candidate_rows": candidate_rows, "eligible_physical_leaves": leaves,
            "three_leaf_capacity": len(leaves) >= 3}
        require(own_capacity == capacity["panels"][ed], "Independent capacity reconstruction: "+ed)
        require(dict(den) == capacity["denominators"][ed], "Independent source denominators")
        targets[ed], denominators[ed] = eligible_targets, dict(den)
    return targets, denominators


def target_checks():
    targets, denominators = reconstruct_targets()
    require(read(A/"TARGET.json") == targets, "All target groups/source IDs and boundaries")
    result, actual_joint = read(A/"RESULT.json"), read(A/"JOINT_CANDIDATES.json")
    require(result["denominators"] == denominators, "Result denominators")
    require(set(result["panels"]) == set(actual_joint) == set(EDITION_ORDER), "Edition scope")
    require(result["confirmed_words"] == result["independent_meaning_confirmation_capacity"] == 0
            and result["significance_claim"] is False, "Semantic claim ceiling")
    require(isinstance(result["elapsed_seconds"], (int, float)) and result["elapsed_seconds"] >= 0, "Elapsed time")
    values_by_input = {n: independent_trace(n) for n in range(100, 10000)}
    tested_total, complete_domain_total = 0, 0
    local_witnesses, joint_witnesses, any_unknown = 0, 0, False
    certificate_counts, position_counts, panel_counts = Counter(), Counter(), {}
    with (A/"CASE_CONSEQUENCES.tsv").open(newline="") as stream:
        rows = csv.DictReader(stream, delimiter="\t")
        require(rows.fieldnames == ["edition", "paragraph", "input", "width", "status", "first_failed_position"], "Case header")
        for ed in EDITION_ORDER:
            panel = result["panels"][ed]
            require(len(panel["records"]) == len(targets[ed]), "One complete case record per target")
            singles = {}
            local_unknown = False
            for target, record in zip(targets[ed], panel["records"]):
                require(record["paragraph"] == target["id"] and record["page"] == target["page"]
                        and record["leaf"] == target["leaf"], "Result ownership/order")
                width_bound = min(len(word)-1 for word in target["words"][:22])
                finite = 9900*max(0, width_bound)
                tested = record["tested_cases"]
                require(record["width_upper_bound"] == width_bound and record["finite_cases"] == finite, "Finite width scope")
                require(isinstance(tested, int) and 0 <= tested <= finite, "Tested case count")
                if width_bound > 0:
                    require(tested % width_bound == 0, "Registered deadline preserves complete input batches")
                if record["status"] == "COMPUTATION_UNKNOWN":
                    require(tested < finite, "Unknown must preserve untested finite cases")
                    local_unknown = True
                else:
                    require(tested == finite, "Exhaustive record missing cases")
                found, failures = [], Counter()
                for index in range(tested):
                    n, width = 100+index//width_bound, 1+index % width_bound
                    values = values_by_input[n]
                    key, reason = independent_parse(target["words"], values, width)
                    expected = {"edition": ed, "paragraph": target["id"],
                                "input": str(n), "width": str(width)}
                    if key is None:
                        expected.update(status=reason[0], first_failed_position=str(reason[1]))
                        failures[reason[0]] += 1
                        certificate_counts[reason[0]] += 1
                        position_counts[reason[1]] += 1
                    else:
                        require(encode(values, key) == target["words"], "Whole witness reencoding")
                        candidate = {**key, "input": n, "values": values,
                                     "paragraph": target["id"], "leaf": target["leaf"]}
                        candidate["completions"] = completions(key)
                        require(candidate["completions"]["distinct_completion_count"] > 0, "No complete digit key")
                        found.append(candidate)
                        expected.update(status="EXACT_SINGLE_FRAME", first_failed_position="0")
                    actual = next(rows, None)
                    require(actual == expected, "Every ordered first-contradiction or exact-case row")
                require(record["first_failure_counts"] == dict(failures), "First-failure histogram")
                require(record["candidates"] == found, "Complete single candidate set/order")
                expected_status = "COMPUTATION_UNKNOWN" if tested < finite else "SINGLE_FRAME_WITNESSES" if found else "CONTRADICTED"
                require(record["status"] == expected_status, "Single record conclusion")
                singles[target["id"]] = found
                tested_total += tested
                complete_domain_total += finite
                local_witnesses += len(found)
            leaves = sorted({t["leaf"] for t in targets[ed]})
            require(panel["eligible_physical_leaves"] == leaves, "Physical leaf capacity")
            # Reconstruct every visited triple in deterministic source/candidate order.
            def all_triples():
                for owners in itertools.combinations(targets[ed], 3):
                    if len({owner["leaf"] for owner in owners}) != 3:
                        continue
                    yield from itertools.product(*(singles[owner["id"]] for owner in owners))
            declared = panel["joint_combinations_tested"]
            require(isinstance(declared, int) and declared >= 0, "Joint tested count")
            iterator = iter(all_triples())
            joint = []
            for _ in range(declared):
                triple = next(iterator, None)
                require(triple is not None, "Overstated tested triple count")
                if len({candidate["input"] for candidate in triple}) != 3:
                    continue
                key = independent_combine(triple[0], triple[1])
                if key is not None:
                    key = independent_combine(key, triple[2])
                if key is None:
                    continue
                for candidate in triple:
                    target = next(t for t in targets[ed] if t["id"] == candidate["paragraph"])
                    require(encode(candidate["values"], key) == target["words"], "Unchanged joint key reencoding")
                joint.append({"key": key, "completions": completions(key),
                              "records": [{k: x[k] for k in ("paragraph", "leaf", "input", "values")} for x in triple]})
            join_incomplete = next(iterator, None) is not None
            require(actual_joint[ed] == joint and panel["joint_witnesses"] == len(joint), "Complete joint witnesses")
            expected_panel = ("INSUFFICIENT_LITERAL_THREE_LEAF_CAPACITY" if len(leaves) < 3 else
                              "COMPUTATION_UNKNOWN" if local_unknown or join_incomplete else
                              "JOINT_CONDITIONAL_WITNESSES" if joint else "FIXED_TRACE_MODEL_CONTRADICTED")
            require(panel["status"] == expected_panel, "Panel scope/conclusion")
            any_unknown |= local_unknown or join_incomplete
            joint_witnesses += len(joint)
            panel_counts[ed] = {"eligible_frames": len(targets[ed]), "eligible_physical_leaves": leaves,
                               "single_candidates": sum(len(v) for v in singles.values()),
                               "joint_candidates": len(joint), "status": expected_panel,
                               "unvisited_joint_triples_exist": join_incomplete}
        require(next(rows, None) is None, "Extra consequence-table rows")
    expected_overall = "FINITE_TRACE_EVALUATION_WITH_UNKNOWNS" if any_unknown else "FINITE_TRACE_EVALUATION_COMPLETE"
    require(result["status"] == expected_overall, "Global unknown propagation")
    return {"target_frames_checked": sum(len(t) for t in targets.values()),
            "source_ids_checked": sum(len(t["source_ids"]) for ts in targets.values() for t in ts),
            "finite_cases": complete_domain_total, "case_rows_replayed": tested_total,
            "first_failure_counts": dict(certificate_counts), "single_witnesses": local_witnesses,
            "first_failure_positions": {str(p): n for p, n in sorted(position_counts.items())},
            "actual_target_maximum_examined_position": 23 if local_witnesses else max(position_counts, default=0),
            "joint_witnesses": joint_witnesses, "panels": panel_counts,
            "result_status": expected_overall, "runtime_limit_exercised": any_unknown,
            "runtime_limit_claim": ("Partial receipts checked; unvisited search remains unknown." if any_unknown else
                                   "NOT_EXERCISED: no empirical validation of deadline execution paths is claimed."),
            "artifact_hashes": {name: sha(A/name) for name in
                               ("TARGET.json", "CASE_CONSEQUENCES.tsv", "JOINT_CANDIDATES.json", "RESULT.json")}}


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
        receipt.update(target_checks())
    (A/"VALIDATION.json").write_text(json.dumps(receipt, sort_keys=True, indent=2)+"\n")
    print(json.dumps({k: receipt[k] for k in ("status", "source_programmes_checked", "synthetic_cases")}, sort_keys=True))


if __name__ == "__main__":
    main()
