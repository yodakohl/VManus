#!/usr/bin/env python3
"""Independent reconstruction of compact FPR001 target-blind calibration."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
SPEC = BASE / "FPR001_ORDERED_ROOT_TARGET_BLIND_CALIBRATION_SPEC.md"
CAP = BASE / "results/fpr001_fifth_relation_ordered_root_capacity.json"
SOURCE = BASE / "results/pre_grounding_interlinear.tsv"
RESULT = BASE / "results/fpr001_ordered_root_target_blind_calibration.json"
REPORT = BASE / "results/fpr001_ordered_root_target_blind_calibration_report.md"
OUT = BASE / "results/fpr001_ordered_root_target_blind_calibration_validation.json"
OUT_MD = BASE / "results/fpr001_ordered_root_target_blind_calibration_validation_report.md"
E = ("ZL3b", "IT2a", "RF1b")
Q = ("ot", "od", "e", "od", "or")
F = (("NULL", 64), ("FULL_ORDERED", 8), ("REDUCED_ORDERED", 8), ("UNORDERED_BAG", 8),
     ("ONE_EDGE", 8), ("CROSS_WORD_SPLIT", 8), ("ONE_READING", 8), ("READING_DISAGREEMENT", 8))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def lcs(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, x in enumerate(a, 1):
        for j, y in enumerate(b, 1):
            d[i][j] = d[i - 1][j - 1] + 1 if x == y else max(d[i - 1][j], d[i][j - 1])
    return d[-1][-1]


def renamed(items: tuple[str, ...]) -> tuple[str, ...]:
    return tuple("R:" + item for item in items)


def fixtures(family: str, i: int, edition: str) -> tuple[tuple[str, ...], ...]:
    if family == "NULL": return ()
    if family == "FULL_ORDERED": return (Q,)
    if family == "REDUCED_ORDERED": return (Q[:3],)
    if family == "UNORDERED_BAG": return (("e", "or", "od", "od", "ot"),)
    if family == "ONE_EDGE": return (("x", "ot", "od", "x"),)
    if family == "CROSS_WORD_SPLIT": return (("ot", "od"), ("e", "x"), ("od", "or"))
    if family == "ONE_READING": return (Q[:3],) if edition == E[i % 3] else ()
    if family == "READING_DISAGREEMENT": return (Q[:3],) if edition in E[:2] else ()
    raise AssertionError(family)


def main() -> None:
    checks = []
    base = {e: defaultdict(int) for e in E}; skipped = 0; rename_ok = True
    with SOURCE.open(newline="", encoding="utf-8") as h:
        for r in csv.DictReader(h, delimiter="\t"):
            if r["page"] == "f37v": skipped += 1; continue
            if (r["section"], r["currier"], r["hand"], r["grammar_scope"]) != ("H", "A", "1", "CONFIRMED_PROSE"): continue
            for w in r["root_sequence"].split():
                atoms = tuple(w.split("+")); score = lcs(Q, atoms)
                rename_ok &= score == lcs(renamed(Q), renamed(atoms))
                base[r["edition"]][r["page"]] = max(base[r["edition"]][r["page"]], score)
    pages = sorted(set.intersection(*(set(base[e]) for e in E)))
    assert len(pages) == 94 and skipped == 69
    assert {e: Counter(base[e].values()) for e in E} == {"ZL3b": Counter({2: 55, 1: 39}), "IT2a": Counter({2: 56, 1: 38}), "RF1b": Counter({2: 53, 1: 41})}
    checks.append("background_reconstructed")

    def passes(family: str, i: int, order: list[str]) -> bool:
        target = order[i % len(order)]; x = {e: dict(base[e]) for e in E}
        for e in E:
            score = max((lcs(Q, word) for word in fixtures(family, i, e)), default=0)
            x[e][target] = max(x[e][target], score)
        rp = all(x[e][target] >= 3 and sum(v >= x[e][target] for v in x[e].values()) == 1 for e in E)
        pt = sum(x[e][target] for e in E)
        return rp and sum(sum(x[e][p] for e in E) >= pt for p in order) == 1

    outcomes = []
    counts = Counter()
    for family, n in F:
        for i in range(n):
            z = passes(family, i, pages); outcomes.append(z); counts[family] += z
            assert z == passes(family, i, list(reversed(pages)))
    assert counts == Counter({"FULL_ORDERED": 8, "REDUCED_ORDERED": 8, "NULL": 0, "UNORDERED_BAG": 0, "ONE_EDGE": 0, "CROSS_WORD_SPLIT": 0, "ONE_READING": 0, "READING_DISAGREEMENT": 0})
    checks.append("all_120_world_outcomes_and_reversal")
    assert rename_ok and all(
        lcs(Q, word) == lcs(renamed(Q), renamed(word))
        for family, n in F for i in range(n) for e in E for word in fixtures(family, i, e)
    )
    checks.append("root_renaming_invariant")

    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    assert stored["pass_counts"] == dict(counts)
    assert stored["world_count"] == 120 and stored["world_outcome_sha256"] == hashlib.sha256(bytes(outcomes)).hexdigest()
    checks.append("counts_and_digest")
    assert all(stored["gates"].values()) and stored["decision"] == "GO_FREEZE_ONE_SHOT_F37V_TARGET"
    checks.append("twelve_gates_and_decision")
    assert stored["target_access"] == {"f37v_formal_rows_accessed": False, "f37v_rank_computed": False, "f37v_score_computed": False}
    checks.append("target_isolation")
    assert stored["inputs"] == {str(p.relative_to(ROOT)): sha(p) for p in (SPEC, CAP, SOURCE)}
    checks.append("bindings")
    expected = (
        "# FPR001 ordered-root target-blind calibration\n\nDecision: **GO_FREEZE_ONE_SHOT_F37V_TARGET**.\n\n"
        "The compact 120-world suite yields 0/64 NULL, 8/8 FULL_ORDERED, 8/8 REDUCED_ORDERED, and 0/8 in each "
        "UNORDERED_BAG, ONE_EDGE, CROSS_WORD_SPLIT, ONE_READING, and READING_DISAGREEMENT family. Page reversal "
        "is invariant. All 69 f37v reading rows were skipped before formal-field access; no target score or rank was "
        "computed. Literal root fixtures and injective root renaming also pass their frozen controls.\n\nThis authorizes only a separately frozen one-shot f37v target. No plant name, word, plaintext, meaning, or "
        "translation follows.\n"
    )
    assert REPORT.read_text(encoding="utf-8") == expected
    checks.append("report_bytes")
    assert len(checks) == 8
    val = {"experiment": "FPR001_ORDERED_ROOT_TARGET_BLIND_CALIBRATION_VALIDATION", "schema": "FPR001_ORDERED_ROOT_TARGET_BLIND_CALIBRATION_VALIDATION_V1", "status": "PASS_8_CHECK_INDEPENDENT_120_WORLD_RECONSTRUCTION", "check_count": 8, "checks": checks, "validated_result_sha256": sha(RESULT), "validated_report_sha256": sha(REPORT), "claim_ceiling": "Validation authorizes only one frozen f37v target and supplies no translation."}
    OUT.write_bytes(canonical(val))
    OUT_MD.write_text("# FPR001 ordered-root calibration validation\n\nStatus: **PASS — 8 independent checks**.\n\nIndependent code reconstructs the background, literal fixtures, all 120 worlds, invariances, digests, gates, isolation, bindings, and report. It supplies no f37v score or translation.\n", encoding="utf-8")


if __name__ == "__main__":
    main()
