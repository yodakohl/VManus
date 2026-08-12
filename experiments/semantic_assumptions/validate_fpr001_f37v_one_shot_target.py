#!/usr/bin/env python3
"""Independent reconstruction of the registered FPR001 f37v target."""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
SPEC = BASE / "FPR001_F37V_ONE_SHOT_TARGET_SPEC.md"
CAL = BASE / "results/fpr001_ordered_root_target_blind_calibration.json"
CALV = BASE / "results/fpr001_ordered_root_target_blind_calibration_validation.json"
SOURCE = BASE / "results/pre_grounding_interlinear.tsv"
RUNNER = BASE / "run_fpr001_f37v_one_shot_target.py"
FREEZE = BASE / "FPR001_F37V_ONE_SHOT_TARGET_FREEZE.json"
RESULT = BASE / "results/fpr001_f37v_one_shot_target.json"
REPORT = BASE / "results/fpr001_f37v_one_shot_target_report.md"
OUT = BASE / "results/fpr001_f37v_one_shot_target_validation.json"
OUT_MD = BASE / "results/fpr001_f37v_one_shot_target_validation_report.md"
Q = ("ot", "od", "e", "od", "or")
E = ("ZL3b", "IT2a", "RF1b")


def sha(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(x: object) -> bytes: return (json.dumps(x, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def strict(path: Path) -> dict[str, object]:
    raw = path.read_bytes()
    def hook(items):
        d = {}
        for k, v in items:
            if k in d: raise AssertionError(k)
            d[k] = v
        return d
    x = json.loads(raw, object_pairs_hook=hook, parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))
    assert canonical(x) == raw
    return x


def lcs(a: tuple[str, ...], b: tuple[str, ...]) -> int:
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, x in enumerate(a, 1):
        for j, y in enumerate(b, 1): d[i][j] = d[i-1][j-1] + 1 if x == y else max(d[i-1][j], d[i][j-1])
    return d[-1][-1]


def wit(word: tuple[str, ...]) -> dict[str, object]:
    found = []
    for n in range(1, 6):
        for qi in itertools.combinations(range(5), n):
            roots = tuple(Q[i] for i in qi)
            for ti in itertools.combinations(range(len(word)), n):
                if tuple(word[i] for i in ti) == roots:
                    found.append((n, qi, ti)); break
    if not found: return {"length": 0, "query_indices": [], "target_indices": [], "roots": []}
    n = max(x[0] for x in found); _, qi, ti = min(x for x in found if x[0] == n)
    return {"length": n, "query_indices": list(qi), "target_indices": list(ti), "roots": [Q[i] for i in qi]}


def reconstruct() -> tuple[dict[str, object], str, list[str]]:
    checks = []
    freeze = strict(FREEZE)
    inputs = {str(p.relative_to(ROOT)): sha(p) for p in (SPEC, CAL, CALV, SOURCE, RUNNER, Path(__file__).resolve())}
    assert freeze["inputs"] == inputs and freeze["query"] == list(Q) and freeze["target_page"] == "f37v"
    checks.append("freeze_and_inputs")
    bg = {e: defaultdict(int) for e in E}; tw = {e: [] for e in E}; rows = 0
    with SOURCE.open(newline="", encoding="utf-8") as h:
        for r in csv.DictReader(h, delimiter="\t"):
            target = r["page"] == "f37v"
            if target: rows += 1
            if (r["section"], r["currier"], r["hand"], r["grammar_scope"]) != ("H", "A", "1", "CONFIRMED_PROSE"): continue
            roots, surfaces = r["root_sequence"].split(), r["surface"].split(); assert len(roots) == len(surfaces)
            for i, (rw, sw) in enumerate(zip(roots, surfaces)):
                atoms = tuple(rw.split("+")); score = lcs(Q, atoms)
                if target: tw[r["edition"]].append({"locus": r["locus"], "word_index": i, "surface_word": sw, "root_word": rw, "score": score, "witness": wit(atoms)})
                else: bg[r["edition"]][r["page"]] = max(bg[r["edition"]][r["page"]], score)
    pages = sorted(set.intersection(*(set(bg[e]) for e in E))); assert len(pages) == 94 and rows == 69
    checks.append("registered_geometry")
    scores = {e: max(x["score"] for x in tw[e]) for e in E}
    ranks = {e: 1 + sum(v >= scores[e] for v in bg[e].values()) for e in E}
    pooled_score = sum(scores.values()); pooled_rank = 1 + sum(sum(bg[e][p] for e in E) >= pooled_score for p in pages)
    best = {e: [x for x in tw[e] if x["score"] == scores[e]] for e in E}
    gates = {"score_at_least_3_all_readings": all(scores[e] >= 3 for e in E),
             "inclusive_rank_1_of_95_all_readings": all(ranks[e] == 1 for e in E),
             "pooled_inclusive_rank_1_of_95": pooled_rank == 1,
             "all_readings_positive_agreement": all(scores[e] >= 3 and ranks[e] == 1 for e in E),
             "all_rank_fractions_at_most_0_02": all(ranks[e] / 95 <= .02 for e in E) and pooled_rank / 95 <= .02}
    passed = all(gates.values()); decision = "PASS_ANONYMOUS_SAME_PLANT_ORDERED_ROOT_RECURRENCE" if passed else "FINAL_NONCONFIRMATION_FIFTH_RELATION_ORDERED_ROOT"
    expected = {"experiment":"FPR001_F37V_ONE_SHOT_TARGET","schema":"FPR001_F37V_ONE_SHOT_TARGET_RESULT_V1",
                "status":"PASS_ONE_SHOT_TARGET" if passed else "FINAL_ONE_SHOT_NONCONFIRMATION","decision":decision,
                "query":list(Q),"target_page":"f37v","target_rows":rows,"background_pages_per_reading":94,
                "target_page_scores":scores,"inclusive_ranks":{e:{"rank":ranks[e],"denominator":95,"fraction":ranks[e]/95} for e in E},
                "pooled":{"score_sum":pooled_score,"rank":pooled_rank,"denominator":95,"fraction":pooled_rank/95},
                "best_target_words":best,"gates":gates,"freeze_sha256":sha(FREEZE),"registration_commit":freeze["registration_commit"],
                "inputs":freeze["inputs"],"claim_ceiling":"A pass establishes only anonymous ordered-root recurrence in one externally fixed same-plant relation. It does not establish a plant name, word, morpheme, sound, language, cipher, plaintext, meaning, or translation."}
    checks.append("scores_ranks_words_and_gates")
    text = ", ".join(f"{e}={scores[e]} (rank {ranks[e]}/95)" for e in E)
    expected_report = ("# FPR001 f37v one-shot ordered-root target\n\n"+f"Decision: **{decision}**.\n\n"+
        f"The frozen f37v page scores are {text}; pooled rank is {pooled_rank}/95. All five preregistered gates {'pass' if passed else 'do not all pass'}. The result file records every maximum-scoring target word and deterministic LCS witness.\n\n"+
        "This is an anonymous manuscript-internal formal recurrence test. It supplies no plant name, word, sound, language, cipher, plaintext, meaning, or translation.\n")
    assert RESULT.read_bytes() == canonical(expected); checks.append("canonical_result_bytes")
    assert REPORT.read_text(encoding="utf-8") == expected_report; checks.append("report_bytes")
    return expected, expected_report, checks


def install(data: bytes, text: str) -> None:
    tmp = Path(tempfile.mkdtemp(prefix="fpr001_validation_")); a=tmp/"a"; b=tmp/"b"; linked=[]
    try:
        a.write_bytes(data); b.write_text(text, encoding="utf-8")
        for s,d in ((a,OUT),(b,OUT_MD)): os.link(s,d); linked.append(d)
    except Exception:
        for p in linked:
            if p.exists(): p.unlink()
        raise
    finally:
        for p in (a,b):
            if p.exists(): p.unlink()
        tmp.rmdir()


def main() -> None:
    _, _, checks = reconstruct(); assert len(checks) == 5
    val = {"experiment":"FPR001_F37V_ONE_SHOT_TARGET_VALIDATION","schema":"FPR001_F37V_ONE_SHOT_TARGET_VALIDATION_V1",
           "status":"PASS_5_CHECK_INDEPENDENT_RECONSTRUCTION","check_count":5,"checks":checks,
           "validated_result_sha256":sha(RESULT),"validated_report_sha256":sha(REPORT),"freeze_sha256":sha(FREEZE),
           "claim_ceiling":"Validation confirms only the registered anonymous recurrence result and supplies no translation."}
    md = "# FPR001 f37v one-shot target validation\n\nStatus: **PASS — 5 independent checks**.\n\nIndependent code reconstructs the freeze bindings, geometry, target scores, ranks, maximum words, witnesses, gates, result, and report. It supplies no plant name, plaintext, meaning, or translation.\n"
    install(canonical(val), md)


if __name__ == "__main__": main()
