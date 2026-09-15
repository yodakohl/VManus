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
    summaries = []
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


def target_checks():
    raise NotImplementedError("Full target branch awaits public registration and final artifact schema")


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
