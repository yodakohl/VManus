"""Independent complete necessary-condition proof and synthetic primary oracle.

The manuscript scan never calls the primary compiler, gate or solver. Each
rejection follows from nonempty, injective, prefix-free unit images. The primary
solver is invoked only on explicitly invented toy equations in the optional
oracle review.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import random
import sys
import time

SOURCE_HASH = "7647eb754fd68d939d041d7a6a35e1711d1783f936f316a5f669b0f58f39846c"
PACKET_HASH = "1b536c8f46dca72522d9cd059869a963aad124ee5da44218b886c88d91ddf2ed"
TARGET_HASH = "dfb5f1981b609fadaf4c93c406ad86042d928f60296d8010a022fe303033df6a"
SCHEMES = ("LETTER", "PAIR_LEFT", "PAIR_RIGHT")
PAIRS = list(itertools.combinations(range(18), 2))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def require(condition, label):
    if not condition:
        raise ValueError(label)


def split_units(atoms, scheme):
    if scheme == "LETTER":
        return tuple((atom,) for atom in atoms)
    work = list(enumerate(atoms))
    if scheme == "PAIR_RIGHT":
        work.reverse()
    groups = {}
    for offset, (_, atom) in enumerate(work):
        groups.setdefault(offset // 2, []).append(atom)
    parts = list(groups.values())
    if scheme == "PAIR_RIGHT":
        parts = [part[::-1] for part in parts[::-1]]
    require(tuple(a for part in parts for a in part) == tuple(atoms), "pair_roundtrip")
    return tuple(tuple(part) for part in parts)


def family(source):
    variants = list(itertools.product(("LETTER_ABSENT", "LETTER_PRESENT"), repeat=2))
    variant_ids = ("IMPERFECT_1SG_C2", "IMPERFECT_3PL_C2")
    require(source["variants"] == [dict(zip(variant_ids, pair)) for pair in variants], "all_four_source_variants")
    traversals = [(columns, major) for columns in itertools.permutations(range(3)) for major in ("ROW", "COLUMN")]
    result = []
    for vi, pair in enumerate(variants):
        selected = dict(zip(variant_ids, pair))
        for scheme in SCHEMES:
            for ti, (columns, major) in enumerate(traversals):
                rank = {column: index for index, column in enumerate(columns)}
                positions = list(itertools.product(range(6), range(3)))
                positions.sort(key=lambda rc: (rc[0], rank[rc[1]]) if major == "ROW" else (rank[rc[1]], rc[0]))
                patterns = []
                for table in source["tables"]:
                    pattern = []
                    for row, column in positions:
                        cell = table["rows"][row][column]
                        atoms = cell["alternatives"][selected[cell["id"]]] if cell["id"] in selected else cell["graphemes"]
                        pattern.append(split_units(atoms, scheme))
                    require(len(pattern) == len(set(pattern)) == 18, "complete_distinct_table")
                    patterns.append(tuple(pattern))
                require(len(set(patterns[0] + patterns[1])) == 36, "complete_36_distinct_cells")
                result.append({"variant": vi, "scheme": scheme, "traversal": ti, "patterns": patterns})
    return result


def common_length(a, b):
    return next((index for index in range(min(len(a), len(b))) if a[index] != b[index]), min(len(a), len(b)))


def signature(words):
    relations = []
    prefixes, suffixes = [], []
    for i, j in PAIRS:
        a, b = words[i], words[j]
        relations.append((a == b[:len(a)], b == a[:len(b)]))
        prefixes.append(common_length(a, b))
        suffixes.append(common_length(a[::-1], b[::-1]))
    return {"lengths": tuple(map(len, words)), "prefix_order": tuple(relations), "prefixes": prefixes, "suffixes": suffixes}


def first_obstruction(source_signature, target_signature):
    for cell, (minimum, actual) in enumerate(zip(source_signature["lengths"], target_signature["lengths"])):
        if minimum > actual:
            return ("NONEMPTY_IMAGE_LENGTH", cell)
    # Test shared-end lower bounds before prefix-order reflection; this order
    # deliberately differs from the primary implementation.
    for index, (minimum, actual) in enumerate(zip(source_signature["suffixes"], target_signature["suffixes"])):
        if minimum > actual:
            return ("SHARED_SUFFIX_MINIMUM", index)
    for index, (minimum, actual) in enumerate(zip(source_signature["prefixes"], target_signature["prefixes"])):
        if minimum > actual:
            return ("SHARED_PREFIX_MINIMUM", index)
    for index, (source_relation, target_relation) in enumerate(zip(source_signature["prefix_order"], target_signature["prefix_order"])):
        if source_relation != target_relation:
            return ("PREFIX_ORDER_REFLECTION", index)
    return None


def toy_oracle(primary_path):
    sys.path.insert(0, str(Path(primary_path).resolve().parent))
    spec = importlib.util.spec_from_file_location("gdt900_primary_toy_subject", primary_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rng = random.Random(9002026)
    alphabet = ("a", "b")
    units = (("X",), ("Y",), ("Z",))
    fixtures = [[], [((units[0],), "a")], [((units[0],), "a"), ((units[0],), "b")], [((units[0],), "a"), ((units[1],), "ab")], [((units[0], units[0]), "abab"), ((units[1],), "ba")]]
    for index in range(80):
        chosen_units = units[:2 + (index % 5 == 0)]
        equations = []
        for _ in range(rng.randint(1, 3)):
            seq = tuple(rng.choice(chosen_units) for _ in range(rng.randint(1, 3)))
            word = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 3)))
            equations.append((seq, word))
        fixtures.append(equations)
    assignments_checked, positive_cases = 0, 0
    for equations in fixtures:
        used = sorted({unit for seq, _ in equations for unit in seq})
        domains = []
        for unit in used:
            maximum = min(len(word) // seq.count(unit) for seq, word in equations if unit in seq)
            domains.append(["".join(chars) for size in range(1, maximum + 1) for chars in itertools.product(alphabet, repeat=size)])
        expected = set()
        for values in itertools.product(*domains):
            assignments_checked += 1
            if any(a.startswith(b) or b.startswith(a) for a, b in itertools.combinations(values, 2)):
                continue
            key = dict(zip(used, values))
            if all("".join(key[unit] for unit in seq) == word for seq, word in equations):
                expected.add(tuple(sorted(key.items())))
        actual = {tuple(sorted(key.items())) for key in module.solve_words(equations, time.monotonic() + 20)}
        require(actual == expected, "synthetic_solver_bruteforce_parity")
        positive_cases += bool(expected)
    pattern = []
    for size in range(1, 5):
        pattern.extend(itertools.product(units[:2], repeat=size))
    pattern = pattern[:18]
    candidates = ["".join(chars) for size in range(1, 4) for chars in itertools.product(alphabet, repeat=size)]
    valid_codebooks = 0
    for left, right in itertools.product(candidates, repeat=2):
        if left.startswith(right) or right.startswith(left):
            continue
        key = dict(zip(units[:2], (left, right)))
        words = ["".join(key[unit] for unit in seq) for seq in pattern]
        require(module.reject(pattern, words, module.constraints(pattern)) is None, "no_false_rejection_of_complete_toy_table")
        valid_codebooks += 1
    return {"status": "PASS", "whole_equation_fixtures": len(fixtures), "positive_equation_fixtures": positive_cases, "bruteforce_assignments_checked": assignments_checked, "complete_18_cell_valid_codebooks_checked": valid_codebooks, "primary_sha256": digest(Path(primary_path).read_bytes()), "scope": "Synthetic finite oracle only; no primary manuscript fitting invoked."}


def validate(source_path, packet_path, target_path, result_path=None, primary_path=None):
    started = time.monotonic()
    source_blob, packet_blob, target_blob = (Path(path).read_bytes() for path in (source_path, packet_path, target_path))
    require(digest(source_blob) == SOURCE_HASH, "frozen_source")
    require(digest(packet_blob) == PACKET_HASH, "frozen_odd_packet")
    require(digest(target_blob) == TARGET_HASH, "frozen_target")
    source, packet, target = json.loads(source_blob), json.loads(gzip.decompress(packet_blob)), json.loads(target_blob)
    source_cases = family(source)
    patterns = {pattern for case in source_cases for pattern in case["patterns"]}
    require(len(source_cases) == 144 and len(patterns) == 180, "complete_source_family")
    source_signatures = {pattern: signature(pattern) for pattern in patterns}
    components, cases, cached = [], [], {}
    for panel in sorted(packet["panels"]):
        windows = []
        for paragraph in packet["panels"][panel]:
            require(not paragraph["page"].startswith("f84") and int(paragraph["physical_folio"][1:]) % 2 == 1, "odd_admission")
            for end in range(18, len(paragraph["words"]) + 1):
                start = end - 18
                windows.append({"id": paragraph["id"] + "@" + str(start), "paragraph_id": paragraph["id"], "page": paragraph["page"], "physical_folio": paragraph["physical_folio"], "start": start, "words": paragraph["words"][start:end], "source_group_ids": paragraph["source_group_ids"][start:end]})
        require(windows == target["panels"][panel], "independent_raw_window_reconstruction")
        inspected = [(window["id"], None if len(set(window["words"])) < 18 else signature(window["words"])) for window in windows]
        for pattern in sorted(patterns):
            counts, survivors, trace = Counter(), [], hashlib.sha256()
            for window_id, target_signature in inspected:
                reason = ("DISTINCT_WHOLE_WORD_COLLISION", -1) if target_signature is None else first_obstruction(source_signatures[pattern], target_signature)
                if reason is None:
                    survivors.append(window_id)
                    reason = ("SURVIVES_NECESSARY_CONDITIONS", -1)
                counts[reason[0]] += 1
                trace.update(canonical([window_id, reason]) + b"\n")
            component = {"panel": panel, "pattern_sha256": digest(canonical(pattern)), "windows": len(windows), "complete": True, "counts": dict(counts), "survivor_window_ids": survivors, "rejection_trace_sha256": trace.hexdigest()}
            components.append(component)
            cached[panel, pattern] = component
        for case in source_cases:
            component_pair = [cached[panel, pattern] for pattern in case["patterns"]]
            closed = any(not component["survivor_window_ids"] for component in component_pair)
            cases.append({"panel": panel, "variant": case["variant"], "scheme": case["scheme"], "traversal": case["traversal"], "components": [component["pattern_sha256"] for component in component_pair], "proved_unsat": closed})
    closed = all(case["proved_unsat"] for case in cases)
    require(len(cases) == 576 and len(components) == 720, "complete_global_case_component_counts")
    primary_comparison = None
    if result_path is not None:
        result_blob = Path(result_path).read_bytes()
        result = json.loads(result_blob)
        require(result["source_sha256"] == SOURCE_HASH and result["target_sha256"] == TARGET_HASH, "primary_result_inputs")
        expected_keys = {(c["panel"], c["variant"], c["scheme"], c["traversal"]) for c in cases}
        require(len(result["cases"]) == 576 and {(c["panel"], c["variant"], c["scheme"], c["traversal"]) for c in result["cases"]} == expected_keys, "primary_complete_case_union")
        require(closed and result["complete"] and result["status"] == "ALL_FOUR_PANELS_UNSAT", "primary_negative_verdict_parity")
        require(all(c["status"] == "UNSAT" and c["joint_solutions"] == 0 for c in result["cases"]) and not result["joint_solutions"], "primary_no_witnesses")
        primary_comparison = {"status": "PASS", "result_sha256": digest(result_blob), "all_576_case_verdicts_independently_proved": True}
    return {"schema": "GDT900_INDEPENDENT_NECESSARY_DOMAIN_PROOF_V1", "status": "ALL_FOUR_PANELS_UNSAT_PROVED" if closed else "NECESSARY_CONDITIONS_INCONCLUSIVE", "source_sha256": SOURCE_HASH, "parent_packet_sha256": PACKET_HASH, "target_sha256": TARGET_HASH, "validator_sha256": digest(Path(__file__).read_bytes()), "complete": True, "global_cases": cases, "components": components, "component_count": len(components), "surviving_component_windows": sum(len(c["survivor_window_ids"]) for c in components), "primary_result_comparison": primary_comparison, "synthetic_primary_oracle": toy_oracle(primary_path) if primary_path is not None else None, "elapsed_seconds": time.monotonic() - started, "proof": ["A nonempty code gives at least one target character per source unit.", "An injective prefix-free unit code is uniquely decodable, so distinct complete source-unit words have distinct images.", "Such a code preserves and reflects complete word-prefix relations: after decoding a shorter image, a prefix can end only at its final unit boundary.", "Each common source prefix or suffix unit contributes at least one identical target-end character, regardless of whether the code is suffix-free.", "Every excluded complete window violates at least one of those necessary conditions; no source-cell subset is used.", "The exhaustive union covers four independent deletion variants, three globally shared unit schemes, twelve globally shared traversals and every admitted 18-group window."], "code_review": "No unsound gate, missing local code assignment or incomplete shared-key join found by bounded inspection. The primary word solver's unknown-tail minimum can be loose for a repeated newly assigned unit, which increases enumeration without excluding models. Shared-unit values are indexed exactly; the join checks all cross-key prefixes and source-group nonoverlap. Timeouts remain incomplete. This proof independently closes the actual negative result without relying on key enumeration.", "claim_ceiling": "Fixed edited two-subtable/global-code/window conjunction only; no manuscript meaning, historical identity or general multilingual refutation."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-input", required=True)
    parser.add_argument("--target-packet", required=True)
    parser.add_argument("--target-input", required=True)
    parser.add_argument("--result")
    parser.add_argument("--primary")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = validate(args.source_input, args.target_packet, args.target_input, args.result, args.primary)
    output = Path(args.output)
    temporary = output.with_name(output.name + ".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=True, indent=2) + "\n")
    temporary.replace(output)
    print(json.dumps({"status": result["status"], "cases": len(result["global_cases"]), "components": result["component_count"], "survivors": result["surviving_component_windows"], "oracle": result["synthetic_primary_oracle"], "seconds": result["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
