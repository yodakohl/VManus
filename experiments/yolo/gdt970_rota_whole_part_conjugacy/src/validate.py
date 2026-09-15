#!/usr/bin/env python3
"""Independent source, intake and direct cyclic-conjugacy audit for GDT970."""
import argparse
from collections import Counter, defaultdict
import csv
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import re

E = Path(__file__).resolve().parents[1]
R = E.parents[2]
A = E / "artifacts"
D = R / "research_registry/work_batches/ten_hours_20260915"
P = R / "experiments/yolo/gdt915_terminal_lr_phrase_transfer"
EDS = ("ZL3b", "IT2a", "RF1b")
DECISIONS = ("TOO_SHORT", "UNEQUAL_LENGTH", "UNEQUAL_INVENTORY",
             "UNEQUAL_CYCLIC_ORDER", "NECESSARY_CONSEQUENCE_ONLY")


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_cycle(value):
    # Independent simple definition, deliberately not the primary fast algorithm.
    return min((value[i:]+value[:i] for i in range(len(value))), default="")


def direct_offsets(left, right):
    if not left or len(left) != len(right):
        return []
    doubled = left+left
    offsets, start = [], 0
    while True:
        found = doubled.find(right, start)
        if found < 0 or found >= len(left):
            return offsets
        offsets.append(found)
        start = found+1


def pair_consequence(left, right):
    if min(len(left), len(right)) < 9:
        return "TOO_SHORT", []
    if len(left) != len(right):
        return "UNEQUAL_LENGTH", []
    if Counter(left) != Counter(right):
        return "UNEQUAL_INVENTORY", []
    offsets = direct_offsets(left, right)
    return ("NECESSARY_CONSEQUENCE_ONLY", offsets) if offsets else ("UNEQUAL_CYCLIC_ORDER", [])


def literal_defects(words, indices, lefts, rights):
    defects = []
    if not words:
        defects.append("EMPTY_LINE")
    if not all(isinstance(w, str) and re.fullmatch("[a-z]+", w) for w in words):
        defects.append("NON_LITERAL")
    if any(v != u+1 for u, v in zip(indices, indices[1:])):
        defects.append("INDEX_GAP")
    if any(rights[i] != "DEFINITE_SPACE" or lefts[i+1] != "DEFINITE_SPACE"
           for i in range(len(words)-1)):
        defects.append("INDEFINITE_SEAM")
    return defects


def paragraph_blocks(lines):
    """Independent interval construction using the next explicit start as fence."""
    ordered = sorted(lines, key=lambda line: line["row"])
    starts = [i for i, line in enumerate(ordered) if line["start"]]
    blocks, diagnostics = [], Counter()
    for k, first in enumerate(starts):
        limit = starts[k+1] if k+1 < len(starts) else len(ordered)
        last = next((i for i in range(first, limit) if ordered[i]["end"]), None)
        if last is None:
            diagnostics["unclosed_start" if k+1 < len(starts) else "unclosed_end"] += 1
            continue
        block = ordered[first:last+1]
        numbers = [int(line["locus"].rsplit(".", 1)[1]) for line in block]
        if numbers != list(range(numbers[0], numbers[0]+len(numbers))):
            diagnostics["gapped_paragraphs"] += 1
        else:
            blocks.append(block)
    return blocks, diagnostics


def source_checks():
    source_path = D / "ROTA_SOURCE_EVENTS.json"
    source = read(source_path)
    require(sha(source_path) == "3923d12c26de3d309bef06cfbd1732985ae8d5ba133adc21f1633ff56fb8f34a",
            "Frozen public Rota source")
    require(source["events"] == read(D/"ROTA_SOURCE_EVENTS_PRECOMPARISON.json"),
            "Preserved precomparison event matrix")
    event_digest = hashlib.sha256(json.dumps(source["events"], sort_keys=True,
                                           separators=(",", ":")).encode()).hexdigest()
    require(event_digest == "2ff05f993c8ffcba901184bf811557ad604f4e497f785a5d80fedce3b37163fd",
            "Exact source event array")
    parts = {p: [e for e in source["events"] if e["part"] == p] for p in ("M", "P1", "P2")}
    require([len(parts[p]) for p in parts] == [79, 9, 9], "Complete written parts")
    own = read(D/"ROTA_PES_RULES_INDEPENDENT.json")
    for i, part in enumerate(("P1", "P2")):
        actual = parts[part]
        for left, right in zip(own["parts"][i]["events"], actual):
            require(left["kind"] == right["kind"], "Independent pes note/pause order")
            if left["kind"] == "note":
                require(left["diatonic_staff_steps_from_C"] ==
                        right["pitch_reading"]["diatonic_steps_above_c_reference"],
                        "Independent pes staff position")
    expected_changes = [{}, {"MN007": "3/2", "MN008": "1/2"},
                        {"P1N004": "1", "P2N007": "1"},
                        {"MN066": "2", "MN067": "1", "MN068": "3"}]
    summaries, source_variants = [], []
    require(len(source["documentary_duration_branches"]) == 4, "Duration branch scope")
    for branch, changes in zip(source["documentary_duration_branches"], expected_changes):
        require(branch["changes"] == changes, "Unchanged duration alternatives")
        ds = {i: Fraction(v) for i, v in source["baseline_conditional_duration_breves"].items()}
        ds.update({i: Fraction(v) for i, v in changes.items()})
        words = {p: [("R" if e["kind"] == "pause" else e["pitch_reading"]["conventional_pitch"],
                       ds[e["id"]]) for e in es] for p, es in parts.items()}
        require(words["P2"] == words["P1"][5:] + words["P1"][:5], "Full timed pes conjugacy")
        ab = [sum(ds[e["id"]] for e in parts["P1"][:5]),
              sum(ds[e["id"]] for e in parts["P1"][5:])]
        require(ab == ([Fraction(11), Fraction(12)] if changes == expected_changes[2]
                       else [Fraction(12), Fraction(12)]), "Block-duration qualification")
        summaries.append({"branch": branch["id"], "A": str(ab[0]), "B": str(ab[1])})
        declared_durations = dict(source["baseline_conditional_duration_breves"])
        declared_durations.update(changes)
        serial_parts = {p: [[None if e["kind"] == "pause" else e["pitch_reading"]["conventional_pitch"],
                             declared_durations[e["id"]]] for e in es] for p, es in parts.items()}
        source_variants.append({"branch": branch["id"], "parts": serial_parts,
                                "A": serial_parts["P1"][:5], "B": serial_parts["P1"][5:]})
    published_consequence = read(A/"SOURCE_CONSEQUENCES.json")
    require(published_consequence["source_path"] == source_path.relative_to(R).as_posix()
            and published_consequence["source_sha256"] == sha(source_path), "Source consequence provenance")
    require(published_consequence["variants"] == source_variants,
            "Every published source event/duration/block in all four branches")
    return {"source_events_checked": 97, "independent_pes_events_checked": 18,
            "source_event_array_sha256": event_digest, "duration_branches": summaries}


def synthetics():
    """Planted logical fixtures only; imports no primary runner."""
    checks = 0
    h = {"F": "aaaa", "G": " aaa", "g": " a a", "A": "aa a",
         "C": "a aa", "B": "aaa ", "R": "a a "}
    require(len(set(h.values())) == 7 and all(len(v) == 4 for v in h.values()),
            "Seven distinct prefix-free fixture event codes")
    upper, lower = "FGFgACBCR", "CBCRFGFgA"
    encoded = ["".join(h[c] for c in s) for s in (upper, lower)]
    x, y = [s.strip(" ") for s in encoded]
    require(len(x) == 35 and len(y) == 36 and x != y and "  " not in x+y,
            "Trimmed full strings differ in length")
    xp, yp = x.replace(" ", ""), y.replace(" ", "")
    require(xp == yp == "a"*27 and pair_consequence(xp, yp) ==
            ("NECESSARY_CONSEQUENCE_ONLY", list(range(27))),
            "Collapsed projections preserve identity and every offset")
    checks += 3
    varying = {symbol: chr(98+i)*(i+1) for i, symbol in enumerate(h)}
    u, v = ["".join(varying[c] for c in s) for s in (upper, lower)]
    require(" " not in u+v and pair_consequence(u, v)[0] == "NECESSARY_CONSEQUENCE_ONLY",
            "Variable widths and many events inside one group")
    checks += 1
    cases = [
        ("a", "bbbbbbbbbb", "TOO_SHORT", []),
        ("abcdefgh", "hgfedcba", "TOO_SHORT", []),
        ("abcdefghi", "abcdefghij", "UNEQUAL_LENGTH", []),
        ("abcabcabd", "abcabcabe", "UNEQUAL_INVENTORY", []),
        ("aaaabbbbcc", "aaababbbcc", "UNEQUAL_CYCLIC_ORDER", []),
        ("abcdefghi", "fghiabcde", "NECESSARY_CONSEQUENCE_ONLY", [5]),
        ("abcabcabc", "abcabcabc", "NECESSARY_CONSEQUENCE_ONLY", [0, 3, 6]),
    ]
    for a, b, decision, offsets in cases:
        require(pair_consequence(a, b) == (decision, offsets), "Synthetic pair certificate")
        require((canonical_cycle(a) == canonical_cycle(b)) == bool(direct_offsets(a, b)),
                "Canonical definition versus direct cyclic search")
        checks += 1
    require(len("abcdefghi") == len(upper) and "abcdefghi"[0] != "abcdefghi"[2],
            "Conjugacy alone does not fit repeated source F")
    checks += 1
    require(not direct_offsets("ab ", "ba ") and direct_offsets("ab", "ba") == [1],
            "Exterior padding is not generally harmless")
    checks += 1
    require(literal_defects(["abc"], [8], ["UNCERTAIN"], ["UNCERTAIN"]) == [],
            "One-group line and exterior seams")
    require(literal_defects([], [], [], []) == ["EMPTY_LINE"], "Empty line")
    require(literal_defects(["ab!"], [1], ["X"], ["X"]) == ["NON_LITERAL"], "Literal raw group")
    require(literal_defects(["a", "b"], [1, 3], ["X", "DEFINITE_SPACE"],
                            ["DEFINITE_SPACE", "X"]) == ["INDEX_GAP"], "Source index gap")
    require(literal_defects(["a", "b"], [1, 2], ["X", "X"],
                            ["DEFINITE_SPACE", "X"]) == ["INDEFINITE_SEAM"], "Both separator sides")
    checks += 5
    def line(number, start=False, end=False):
        return {"row": number, "locus": "f1r."+str(number), "start": start, "end": end}
    blocks, den = paragraph_blocks([line(1, True), line(2, end=True)])
    require(len(blocks) == 1 and len(blocks[0]) == 2 and not den, "Complete paragraph")
    blocks, den = paragraph_blocks([line(1, True), line(3, end=True)])
    require(not blocks and den == {"gapped_paragraphs": 1}, "Gapped paragraph")
    blocks, den = paragraph_blocks([line(1, True), line(2, True, True), line(3, True)])
    require(len(blocks) == 1 and den == {"unclosed_start": 1, "unclosed_end": 1},
            "Conflicting starts and trailing unclosed paragraph")
    checks += 3
    return checks


def lock_checks(registration_only):
    lock = read(E/"PREREG_LOCK.json")
    bindings = lock["files"]
    for relative in ("PREREGISTRATION.md", "METHOD.md", "src/run.py"):
        require((E/relative).relative_to(R).as_posix() in bindings, "Missing scientific binding")
    checked, deferred = {}, []
    parent = read(R/"experiments/yolo/gdt928_multi_anchor_complete_paragraphs/PREREG_LOCK.json")
    require(all(bindings.get(name) == expected for name, expected in parent["files"].items()),
            "Every original GDT928 binding is inherited unchanged")
    for name, expected in bindings.items():
        require(not Path(name).is_absolute() and ".." not in Path(name).parts, "Safe bound path")
        path = R/name
        # Registration-only mode deliberately avoids even reading cache bytes.
        if registration_only and path.parent == P/"artifacts" and path.name.startswith("SOURCE_"):
            require(path.is_file(), "Deferred original cache exists")
            deferred.append(name)
            continue
        actual = sha(path)
        require(actual == expected, "Frozen binding mismatch: "+name)
        checked[name] = actual
    return {"input_hashes": checked, "cache_hashes_deferred_until_public_target_validation": deferred,
            "prereg_lock_sha256": sha(E/"PREREG_LOCK.json")}


def reconstruct_intake():
    """Read original guarded caches, then assemble intervals without GDT928 code."""
    specification = read(P/"src/SPEC.json")
    allowed = set(specification["allowed_selectors"])
    require(len(allowed) == 179 and not any(p.startswith("f84") or p == "f116v" for p in allowed),
            "Exact admitted selector fence")
    outputs, denominators, coverage = {}, {}, {}
    names = {"NON_LITERAL": "NONLITERAL_GROUP", "INDEX_GAP": "NONCONSECUTIVE_GROUP_INDICES",
             "INDEFINITE_SEAM": "UNRESOLVED_INTERIOR_BOUNDARY", "EMPTY_LINE": "EMPTY_LINE"}
    for edition in EDS:
        pages, errors, seen = defaultdict(list), {}, set()
        den = Counter()
        raw_count, raw_group_count = 0, 0
        for phase in ("DISCOVERY", "EVALUATION"):
            cache = read(P/"artifacts"/("SOURCE_"+phase+"_"+edition+".json"))
            columns = cache["group_columns"]
            require(len(columns) == len(set(columns)), "Unique original group columns")
            for raw in cache["lines"]:
                meta = raw["metadata"]
                # Raw selector metadata is checked before group contents are accessed.
                page = meta["page"]
                require(page in allowed and not page.startswith("f84") and page != "f116v",
                        "Original cache metadata outside admitted scope")
                raw_count += 1
                if meta["kind"] != "P":
                    continue
                row = int(meta["source_row_index"])
                require((page, row) not in seen, "Duplicated P-line source ownership")
                seen.add((page, row))
                require(all(len(g) == len(columns) for g in raw["groups"]), "Original group schema")
                gs = [dict(zip(columns, g)) for g in raw["groups"]]
                words = [g["ivtff_group_raw"] for g in gs]
                bad = literal_defects(words, [int(g["source_group_index"]) for g in gs],
                                      [g["left_separator"] for g in gs],
                                      [g["right_separator"] for g in gs])
                errors[(page, row)] = [names[b] for b in bad]
                pages[page].append({"locus": meta["locus"], "row": row,
                                   "start": meta["paragraph_start"] == "1",
                                   "end": meta["paragraph_end"] == "1", "words": words,
                                   "source_ids": [g["source_group_id"] for g in gs],
                                   "anchor_eligible": len(words) >= 2 and not bad})
                den["P_lines"] += 1
                raw_group_count += len(words)
        paragraphs = []
        for page in sorted(pages):
            blocks, diagnostics = paragraph_blocks(pages[page])
            den.update(diagnostics)
            for block in blocks:
                group_count = 0
                for line in block:
                    line["offset"] = group_count
                    group_count += len(line["words"])
                paragraph = {"id": page+"|"+block[0]["locus"]+"-"+block[-1]["locus"],
                             "page": page, "leaf": int(re.match(r"f(\d+)", page)[1]),
                             "lines": block, "groups": group_count}
                paragraph["defects"] = [{"locus": line["locus"], "reasons": errors[(page, line["row"])]}
                                         for line in block if errors[(page, line["row"])]]
                paragraph["literal_eligible"] = not paragraph["defects"]
                words = list(itertools.chain.from_iterable(line["words"] for line in block))
                paragraph["full_text"] = " ".join(words)
                projection = "".join(words) if paragraph["literal_eligible"] else None
                paragraph["projection"] = projection
                paragraph["canonical_cycle"] = canonical_cycle(projection) if projection is not None else None
                paragraph["min_pes_letters"] = len(projection) >= 9 if projection is not None else None
                paragraphs.append(paragraph)
                den["complete_paragraphs"] += 1
                den["anchor_lines"] += sum(line["anchor_eligible"] for line in block)
        require(len({p["id"] for p in paragraphs}) == len(paragraphs), "Distinct complete paragraph IDs")
        outputs[edition], denominators[edition] = paragraphs, dict(den)
        coverage[edition] = {"raw_metadata_rows_guarded": raw_count, "P_lines_reconstructed": den["P_lines"],
                             "P_groups_reconstructed": raw_group_count,
                             "complete_paragraphs": len(paragraphs),
                             "complete_paragraph_lines": sum(len(p["lines"]) for p in paragraphs),
                             "paragraphs_admitted_by_single_group_rule": sum(
                                  p["literal_eligible"] and any(not line["anchor_eligible"] for line in p["lines"])
                                  for p in paragraphs),
                             "eligible_single_group_lines": sum(len(line["words"]) == 1
                                  for p in paragraphs if p["literal_eligible"] for line in p["lines"])}
    return outputs, denominators, coverage


def read_table(name, expected_header):
    with (A/name).open(newline="") as handle:
        rows = list(csv.reader(handle, delimiter="\t"))
    require(bool(rows) and rows[0] == expected_header, "Exact table columns: "+name)
    require(all(len(row) == len(expected_header) for row in rows[1:]), "Rectangular table: "+name)
    return rows[1:]


def target_checks():
    paragraphs, assembly, intake_coverage = reconstruct_intake()
    actual_paragraphs = read(A/"PARAGRAPHS.json")
    require(actual_paragraphs == paragraphs, "Every intake record, raw group, fence, defect and projection")
    actual_pairs, result = read(A/"PAIR_CONSEQUENCES.json"), read(A/"RESULT.json")
    require(set(actual_pairs) == set(EDS), "Pair edition coverage")
    require(set(result["panels"]) == set(EDS), "Result edition coverage")
    require(result["assembly_denominators"] == assembly, "Original paragraph assembly denominators")
    summary, candidate_rows, length_rows, pair_coverage = {}, [], [], {}
    counterexample_rows = []
    for edition in EDS:
        paras = paragraphs[edition]
        eligible = [p for p in paras if p["literal_eligible"]]
        partners, equal_pairs = defaultdict(list), []
        counts = Counter({name: 0 for name in DECISIONS})
        same_leaf = direct_calls = positive_nonzero = positive_identity = 0
        for left, right in itertools.combinations(eligible, 2):
            x, y = left["projection"], right["projection"]
            # This direct doubled-string search is independent of both cached
            # canonical values and the primary decision procedure.
            direct = direct_offsets(x, y)
            direct_calls += 1
            status, offsets = pair_consequence(x, y)
            counts[status] += 1
            same_leaf += left["leaf"] == right["leaf"]
            require((left["canonical_cycle"] == right["canonical_cycle"]) == bool(direct),
                    "Every-pair canonical claim versus direct search")
            if status == "NECESSARY_CONSEQUENCE_ONLY":
                require(offsets == direct and bool(offsets), "All actual cyclic offsets")
                positive_identity += 0 in offsets
                positive_nonzero += any(offset > 0 for offset in offsets)
                partners[left["id"]].append(right["id"])
                partners[right["id"]].append(left["id"])
            elif status != "TOO_SHORT":
                require(not direct, "Contradiction must lack any cyclic offset")
            if len(x) == len(y):
                equal_pairs.append({"a": left["id"], "b": right["id"],
                                    "decision": status, "offsets": offsets})
                differences = {letter: [x.count(letter), y.count(letter)]
                               for letter in sorted(set(x+y)) if x.count(letter) != y.count(letter)}
                counterexample_rows.append([edition, left["id"], right["id"], str(len(x)),
                    json.dumps(differences, separators=(",", ":")), status,
                    json.dumps(offsets, separators=(",", ":"))])
        require(actual_pairs[edition] == equal_pairs, "Every ordered artifact record for unordered equal-length pairs")
        n = len(eligible)
        total = n*(n-1)//2
        require(total == direct_calls == sum(counts.values()), "Complete unordered-pair census")
        groups = defaultdict(list)
        for p in eligible:
            groups[len(p["projection"])].append(p["id"])
        equal_count = sum(len(ids)*(len(ids)-1)//2 for ids in groups.values())
        require(equal_count == len(equal_pairs), "Independent length-partition pair denominator")
        short_count = sum(len(p["projection"]) < 9 for p in eligible)
        require(counts["TOO_SHORT"] == total-(n-short_count)*(n-short_count-1)//2,
                "Every short/nonshort pair receives priority TOO_SHORT")
        status = ("NO_COMPLETE_PARAGRAPH_CAPACITY" if len(paras) == 0 else
                  "NO_LITERAL_PAIR_CAPACITY" if n < 2 else
                  "NECESSARY_CONSEQUENCE_CAPACITY" if counts["NECESSARY_CONSEQUENCE_ONLY"] else
                  "FIXED_LITERAL_WHOLE_PART_CODE_CONTRADICTED")
        summary[edition] = {
            "complete_paragraphs": len(paras), "literal_paragraphs": n,
            "literal_physical_leaves": len({p["leaf"] for p in eligible}),
            "ineligible_paragraphs": len(paras)-n, "literal_below9letters": short_count,
            "all_literal_pairs": total, "same_leaf_pairs": same_leaf,
            "different_leaf_pairs": total-same_leaf, "equal_projection_length_pairs": equal_count,
            "pair_decisions": dict(counts), "status": status}
        require(result["panels"][edition] == summary[edition], "Exact edition counters and scope status")
        for p in paras:
            literal = p["literal_eligible"]
            mate = partners[p["id"]]
            status = ("UNKNOWN_LITERAL_CONTENT" if not literal else
                      "TOO_SHORT" if not p["min_pes_letters"] else
                      "NECESSARY_CONSEQUENCE_ONLY" if mate else "NO_COMPATIBLE_WHOLE_PARTNER")
            candidate_rows.append([edition, p["id"], p["page"], str(p["leaf"]),
                "LITERAL" if literal else json.dumps(p["defects"], separators=(",", ":")),
                str(len(p["projection"])) if literal else "",
                str(p["min_pes_letters"]) if literal else "", p["canonical_cycle"] or "",
                json.dumps(mate, separators=(",", ":")), status, "0"])
        for length, ids in sorted(groups.items()):
            length_rows.append([edition, str(length), str(len(ids)), str(len(ids)*(len(ids)-1)//2),
                                json.dumps(ids, separators=(",", ":"))])
        pair_coverage[edition] = {"all_pairs_directly_checked": direct_calls,
                                  "equal_length_certificate_records": len(equal_pairs),
                                  "real_positive_pairs": counts["NECESSARY_CONSEQUENCE_ONLY"],
                                  "real_identity_offset_pairs": positive_identity,
                                  "real_nonzero_offset_pairs": positive_nonzero,
                                  "decision_paths_exercised": [k for k in DECISIONS if counts[k]],
                                  "decision_paths_not_exercised": [k for k in DECISIONS if not counts[k]]}
    require(read_table("CANDIDATE_PREDICTIONS.tsv",
            ["edition", "paragraph", "page", "physical_leaf", "literal_status", "projected_length",
             "source_minimum_met", "required_cyclic_string", "observed_partners", "decision",
             "independent_confirmation_capacity"]) == candidate_rows, "Every complete-paragraph prediction row")
    require(read_table("LENGTH_PARTITION.tsv",
            ["edition", "projected_length", "paragraph_count", "all_same_length_pairs", "paragraph_ids"])
            == length_rows, "Every literal length group, count and paragraph ownership")
    require(read_table("EQUAL_LENGTH_COUNTEREXAMPLES.tsv",
            ["edition", "paragraph_a", "paragraph_b", "projected_length",
             "different_letter_counts_a_b", "decision", "rotation_offsets"]) == counterexample_rows,
            "Every equal-length pair and every differing letter count")
    fixed = {"status": "COMPLETE_NECESSARY_CONSEQUENCE_CENSUS", "translated_words": 0,
             "independent_confirmation_capacity": 0, "significance_claim": False,
             "reserve_access": False, "full_code_tested": False, "main_melody_tested": False}
    for key, value in fixed.items():
        require(result[key] == value and type(result[key]) is type(value), "Result claim ceiling: "+key)
    require(set(result) == set(fixed) | {"started_utc", "elapsed_seconds", "assembly_denominators", "panels"},
            "Result field coverage")
    from datetime import datetime
    require(datetime.fromisoformat(result["started_utc"]).utcoffset() is not None, "Recorded UTC run time")
    require(isinstance(result["elapsed_seconds"], (int, float)) and 0 <= result["elapsed_seconds"] < 3600,
            "Recorded finite run duration")
    output_names = ("PARAGRAPHS.json", "PAIR_CONSEQUENCES.json", "RESULT.json",
                    "CANDIDATE_PREDICTIONS.tsv", "LENGTH_PARTITION.tsv", "EQUAL_LENGTH_COUNTEREXAMPLES.tsv")
    return {"target_validation": "COMPLETE", "intake_coverage": intake_coverage,
            "panels": summary, "pair_validation": pair_coverage,
            "candidate_prediction_rows_checked": len(candidate_rows),
            "length_partition_rows_checked": len(length_rows),
            "equal_length_counterexample_rows_checked": len(counterexample_rows),
            "output_hashes": {name: sha(A/name) for name in output_names},
            "actual_full_code_paths_tested": False, "actual_main_melody_paths_tested": False,
            "runtime_limit_paths": "NOT_APPLICABLE: finite census has no capped search or unknown solver branch"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--registration-only", action="store_true")
    args = parser.parse_args()
    receipt = {"status": "PASS_REGISTRATION_ONLY" if args.registration_only else "PASS",
               "registration_only": args.registration_only,
               "validator_sha256": sha(Path(__file__)),
               **source_checks(), "synthetic_checks": synthetics(),
               **lock_checks(args.registration_only)}
    if not args.registration_only:
        receipt.update(target_checks())
    else:
        receipt["target_validation"] = "NOT_RUN"
    receipt["claim_ceiling"] = "Source and necessary-consequence fidelity; no full code or musical meaning confirmation."
    (A/"VALIDATION.json").write_text(json.dumps(receipt, indent=2, sort_keys=True)+"\n")
    print(json.dumps({"status": receipt["status"], "synthetic_checks": receipt["synthetic_checks"],
                      "source_events": receipt["source_events_checked"],
                      "target_validation": receipt.get("target_validation", "COMPLETE")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
