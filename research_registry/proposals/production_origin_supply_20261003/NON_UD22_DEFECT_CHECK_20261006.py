"""Post-result defect-lemma illustration and binding check; no native data query.

Run from repository root. The finite synthetic enumeration does not prove the
arbitrary-length theorem. The accompanying human proof supplies that argument.
"""
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from itertools import product
from pathlib import Path
import hashlib
import json

P = Path("research_registry/proposals/production_origin_supply_20261003")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=None)
def ud(code):
    """Sardinas-Patterson residual-set decision, including epsilon collision."""
    c = set(code)
    residuals = {v[len(u):] for u in c for v in c
                 if u != v and v.startswith(u)}
    visited = set()
    while residuals:
        r = residuals.pop()
        if not r or r in c:
            return False
        visited.add(r)
        for w in c:
            for longer, shorter in ((r, w), (w, r)):
                if longer.startswith(shorter):
                    tail = longer[len(shorter):]
                    if tail not in visited:
                        residuals.add(tail)
    return True


def covers(word, code):
    reachable = {0}
    for pos in range(len(word)):
        if pos in reachable:
            for c in code:
                if word.startswith(c, pos):
                    reachable.add(pos + len(c))
    return len(word) in reachable


def reduce_code(original):
    current = tuple(sorted(original))
    trace = []
    while not ud(current):
        pairs = sorted((u, v) for u in current for v in current
                       if u != v and v.startswith(u))
        assert pairs, "non-UD implies a proper prefix pair"
        u, v = pairs[0]
        r = v[len(u):]
        changed = tuple(sorted((set(current) - {v}) | {r}))
        assert r and sum(map(len, changed)) < sum(map(len, current))
        assert len(changed) <= len(current)
        assert all(covers(w, changed) for w in current)
        if len(changed) == len(current):
            assert not ud(changed), "same-size step cannot cure non-UD"
            assert r not in current and u != r
            # The abstract composition code has all atoms except R and UR.
            atoms = set(changed)
            abstract = {(x,) for x in atoms - {r}} | {(u, r)}
            assert not any(x != y and len(x) <= len(y)
                           and y[-len(x):] == x
                           for x in abstract for y in abstract)
        trace.append({"u": u, "v": v, "r": r,
                      "before": list(current), "after": list(changed)})
        current = changed
        assert all(covers(w, current) for w in original)
    if not ud(tuple(sorted(original))):
        assert len(current) < len(original)
    return current, trace


def main():
    result_path = P / "UD22_POSTRESULT_CAPACITY_CLOSURE_20261006.json"
    validation_path = P / "UD22_POSTRESULT_CAPACITY_VALIDATION_20261006.json"
    old = json.loads(result_path.read_text())
    validation = json.loads(validation_path.read_text())
    assert old["status"] == "ALL_NONTRIVIAL_UD_CODES_AT_MOST22_EXCLUDED_ALL_READINGS"
    assert validation["status"] == "PASS_POST_RESULT_HAND_CONSEQUENCE"
    assert validation["result_sha256"] == digest(result_path)
    for path, expected in old["sources"].items():
        assert digest(path) == expected, path
    check_path = Path("experiments/yolo/gdt1235_ud_short_word_capacity/src/validate.py")
    lock_path = Path("experiments/yolo/gdt1235_ud_short_word_capacity/artifacts/REGISTRATION_LOCK.json")
    lock = json.loads(lock_path.read_text())
    for path, expected in lock["files"].items():
        assert digest(path) == expected, path
    assert str(check_path) in lock["files"]
    # This inherited validator, already recorded PASS, verifies exact alphabet
    # occurrence equality. We do not decompress or rescore native groups here.
    assert "assert {g for w in words for g in w}==alphabet" in check_path.read_text()
    original_validation = json.loads(Path(
        "experiments/yolo/gdt1235_ud_short_word_capacity/artifacts/VALIDATION.json"
    ).read_text())
    assert original_validation["status"] == "PASS"
    spec = json.loads(Path(
        "experiments/yolo/gdt1235_ud_short_word_capacity/src/SPEC.json"
    ).read_text())
    assert len(set(spec["signs"])) == 22
    assert set(old["readers"]) == set(spec["readers"]) == {"IT2a", "RF1b", "ZL3b"}
    assert all(r["decision"] == "EXCLUDED_NONTRIVIAL_AT_MOST22"
               for r in old["readers"].values())

    words = ["".join(w) for n in range(1, 4) for w in product("ab", repeat=n)]
    counts = Counter()
    max_steps = 0
    for mask in range(1, 1 << len(words)):
        code = tuple(sorted(w for i, w in enumerate(words) if mask & (1 << i)))
        endpoint, trace = reduce_code(code)
        counts["tables"] += 1
        counts["initial_ud" if ud(code) else "initial_non_ud"] += 1
        counts["reduction_steps"] += len(trace)
        counts["strict_cardinality_steps"] += sum(
            len(t["after"]) < len(t["before"]) for t in trace)
        max_steps = max(max_steps, len(trace))
        assert ud(endpoint) and all(covers(w, endpoint) for w in code)
    assert counts["tables"] == 16383
    assert ud(("a", "ab"))  # Non-prefix-free alone does not imply a defect.
    assert not ud(("ab", "aba", "ba"))
    endpoint, trace = reduce_code(("ab", "aba", "ba"))
    assert endpoint == ("a", "b")
    bound_paths = [result_path, validation_path, check_path, lock_path,
                   P / "HUMAN_NON_UD_DEFECT_BOUND_REVIEW_20261006.json",
                   P / "NON_UD22_DEFECT_CHECK_20261006.py"]
    output = {
        "status": "PASS_SYNTHETIC_DEFECT_AND_INHERITED_PREMISE_BINDINGS",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "synthetic": dict(counts),
        "maximum_reduction_steps": max_steps,
        "hand_example": trace,
        "inherited_all_22_units_occur": {
            "status": "BOUND_TO_PREVIOUS_VALIDATOR_PASS_NOT_NEW_DATA_REPLAY",
            "readers": spec["readers"],
            "units": spec["signs"]},
        "bindings": {str(p): digest(p) for p in bound_paths},
        "scientific_limit": "Finite examples are not the general proof. The human proof applies to arbitrary finite nonempty codewords. This run verifies old evidence hashes, not its independent scientific correctness or the manuscript ink.",
        "native_data_query": False,
        "new_meaning": False,
    }
    target = P / "NON_UD22_DEFECT_VALIDATION_20261006.json"
    target.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({k: output[k] for k in ("status", "synthetic", "maximum_reduction_steps")}))


if __name__ == "__main__":
    main()
