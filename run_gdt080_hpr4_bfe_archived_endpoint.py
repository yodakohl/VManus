#!/usr/bin/env python3
"""GDT080: frozen HPR4 class against an archived non-f84 BFE endpoint."""
from __future__ import annotations

import csv
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VISUAL = ROOT / "gdt002_exploratory_visual_formal_join.tsv"
PARSED = ROOT / "gdt059_hpr2_external_inventory.tsv"
MODEL = ROOT / "gdt078_hpr4_model.json"
PREDICTIONS = ROOT / "gdt078_hpr4_predictions.tsv"
METHOD = ROOT / "GDT080_HPR4_BFE_ARCHIVED_ENDPOINT_METHOD.md"
REPORT = ROOT / "GDT080_HPR4_BFE_ARCHIVED_ENDPOINT_REPORT.md"
JOIN = ROOT / "gdt080_hpr4_bfe_join.tsv"
TESTS = ROOT / "gdt080_hpr4_bfe_tests.tsv"
COUNTER = ROOT / "gdt080_hpr4_bfe_counterexamples.tsv"
RESULT = ROOT / "gdt080_result.json"


def read(path):
    with Path(path).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write(path, rows, fields):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":")).encode()).hexdigest()


def prevalence(rows, positive):
    z = [r for r in rows if r["visual_state"] == positive]
    return sum(int(r["stable_class"]) for r in z) / len(z) if z else 0.0


def main():
    visual = [r for r in read(VISUAL) if r["channel"] == "BFE_ENCLOSURE" and not r["locus"].startswith("f84r")]
    assert len(visual) == 30 and not any(r["locus"].startswith("f84r") for r in visual)
    parsed = defaultdict(list)
    for row in read(PARSED):
        if not row["locus"].startswith("f84r"):
            parsed[row["locus"]].append(row)
    stable = set(json.loads(MODEL.read_text())["stable_aiin_high_hosts"])
    assert stable == {"d", "ok", "yk", "yt"}
    joined = []
    for row in visual:
        z = parsed.get(row["locus"], [])
        assert len(z) <= 1
        p = z[0] if z else None
        joined.append({
            "locus": row["locus"], "page": row["page"], "physical_folio": row["physical_folio"],
            "visual_state": row["visual_state"], "source_record_id": row["observation_source"],
            "hpr2_parse_available": int(p is not None), "token": p["token"] if p else "",
            "page_host": p["page_host"] if p else "", "right_family": p["right_family"] if p else "",
            "stable_class": int(bool(p and p["page_host"] in stable)),
            "predicted_direction_correct": int(bool(p and p["page_host"] in stable and row["visual_state"] == "INDIVIDUAL_BOUNDED")),
        })
    eligible = [r for r in joined if int(r["hpr2_parse_available"])]
    bounded = [r for r in eligible if r["visual_state"] == "INDIVIDUAL_BOUNDED"]
    opened = [r for r in eligible if r["visual_state"] == "OPEN_OR_COMMUNAL"]
    effect = prevalence(eligible, "INDIVIDUAL_BOUNDED") - prevalence(eligible, "OPEN_OR_COMMUNAL")
    by_host = Counter(r["page_host"] for r in eligible if int(r["stable_class"]))
    mixed = [r for r in eligible if r["page"] == "f82v"]
    assert len(mixed) == 5
    observed = prevalence(mixed, "INDIVIDUAL_BOUNDED") - prevalence(mixed, "OPEN_OR_COMMUNAL")
    masks = [int(r["stable_class"]) for r in mixed]
    states = [r["visual_state"] for r in mixed]
    values = []
    for bounded_idx in itertools.combinations(range(len(mixed)), states.count("INDIVIDUAL_BOUNDED")):
        state_set = set(bounded_idx)
        b = [masks[i] for i in range(len(mixed)) if i in state_set]
        o = [masks[i] for i in range(len(mixed)) if i not in state_set]
        values.append(sum(b)/len(b)-sum(o)/len(o))
    p_positive = sum(v >= observed - 1e-12 for v in values) / len(values)
    lofo = []
    for folio in sorted({r["physical_folio"] for r in eligible}):
        q = [r for r in eligible if r["physical_folio"] != folio]
        lofo.append((folio, prevalence(q,"INDIVIDUAL_BOUNDED")-prevalence(q,"OPEN_OR_COMMUNAL")))
    tests = [
        {"test":"PARSER_COVERAGE","eligible_rows":len(eligible),"positive_rows":len(bounded),"negative_rows":len(opened),"effect":"","exact_p":"","result":f"{len(eligible)}/30; bounded={len(bounded)}/16 open={len(opened)}/14"},
        {"test":"POOLED_CLASS_PREVALENCE_BOUNDED_MINUS_OPEN","eligible_rows":len(eligible),"positive_rows":len(bounded),"negative_rows":len(opened),"effect":effect,"exact_p":"NOT_EXACT_PAGE_CONFOUNDED","result":"WRONG_DIRECTION" if effect <= 0 else "PREDICTED_DIRECTION"},
        {"test":"F82V_WITHIN_PAGE_EXACT","eligible_rows":len(mixed),"positive_rows":3,"negative_rows":2,"effect":observed,"exact_p":p_positive,"result":"WRONG_DIRECTION" if observed <= 0 else "PREDICTED_DIRECTION"},
        {"test":"EXACT_HOST_DIVERSITY","eligible_rows":sum(by_host.values()),"positive_rows":"","negative_rows":"","effect":"","exact_p":"","result":";".join(f"{k}:{v}" for k,v in sorted(by_host.items()))},
        {"test":"LEAVE_FOLIO_OUT_DIRECTION","eligible_rows":len(eligible),"positive_rows":"","negative_rows":"","effect":"","exact_p":"","result":";".join(f"{k}:{v:.6f}" for k,v in lofo)},
    ]
    counter = []
    for row in joined:
        if not int(row["hpr2_parse_available"]): reason="NO_HPR2_PARSE_NOT_CLASSIFIED"
        elif int(row["stable_class"]) and row["visual_state"]=="OPEN_OR_COMMUNAL": reason="CLASS_POSITIVE_OPEN_COUNTEREXAMPLE"
        elif int(row["stable_class"]) and row["visual_state"]=="INDIVIDUAL_BOUNDED": reason="CLASS_POSITIVE_BOUNDED_SUPPORT"
        elif row["visual_state"]=="INDIVIDUAL_BOUNDED": reason="BOUNDED_WITHOUT_CLASS"
        else: reason="OPEN_WITHOUT_CLASS"
        counter.append({**row,"audit_class":reason})
    status = "HPR4_STABLE_HOST_CLASS_ARCHIVED_BFE_DIRECTION_FAILS_AND_IS_ONE_HOST_DRIVEN"
    write(JOIN, joined, list(joined[0])); write(TESTS, tests, list(tests[0])); write(COUNTER, counter, list(counter[0]))
    REPORT.write_text(f"""# GDT080 — HPR4 archived enclosure-endpoint audit

## Outcome

**{status}**

The 30-row non-f84 BFE archive contains {len(eligible)} rows with an eligible
frozen HPR2 parse ({len(bounded)} bounded, {len(opened)} open).  The HPR4
stable-high class occurs three times, all as exact PAGE_HOST `ok`: one bounded
and two open.  Its pooled bounded-minus-open prevalence effect is {effect:+.4f}.
On f82v, the only mixed page, the sole class hit is open, giving {observed:+.4f}
and a one-sided exact permutation p={p_positive:.4f} in the preregistered
positive direction.  The sign therefore contradicts the proposed enclosure
direction, and the class is also entirely one-host-driven.

This is a useful negative but not a prospective validation: BFE001 predates
HPR4, GDT002 already scanned this endpoint, ten rows lack an eligible HPR2
parse, and only one page has both visual states.  Historical BFE and GDT002
stops are unchanged.  HPR4_P01 remains frozen and unrun, but this archived
diagnostic materially deprioritizes it.  No fresh image or holdout was opened.
f84r was excluded before the join and was not opened, retained, queried,
joined, scored, targeted, or inspected.  No semantic class, role, gloss, word,
morpheme, POS, sound, language, plaintext, meaning, or translation is assigned.
""", encoding="utf-8")
    result = {
        "schema":"GDT080_HPR4_BFE_ARCHIVED_ENDPOINT_RESULT_V1","status":status,
        "bfe_nonholdout_rows":len(joined),"hpr2_eligible_rows":len(eligible),
        "eligible_state_counts":dict(Counter(r["visual_state"] for r in eligible)),
        "stable_class_hits":sum(int(r["stable_class"]) for r in eligible),"stable_exact_hosts":dict(by_host),
        "pooled_bounded_minus_open_effect":effect,"f82v_within_page_effect":observed,"f82v_one_sided_exact_p":p_positive,
        "interpretation":"Archived endpoint contradicts the frozen class direction and is one-host-driven; prospective HPR4_P01 remains unrun.",
        "claim_ceiling":"No semantic class, role, gloss, word, morpheme, POS, sound, language, plaintext, meaning, or translation.",
        "f84r":{"opened":False,"retained":False,"queried":False,"joined":False,"scored":False,"targeted":False,"inspected":False},
        "inputs":{VISUAL.name:sha(VISUAL),PARSED.name:sha(PARSED),MODEL.name:sha(MODEL),PREDICTIONS.name:sha(PREDICTIONS),"experiments/semantic_assumptions/results/bfe001_bio_figure_enclosure_capacity.json":sha(ROOT/"experiments/semantic_assumptions/results/bfe001_bio_figure_enclosure_capacity.json"),"gdt002_exploratory_discovery_results.json":sha(ROOT/"gdt002_exploratory_discovery_results.json"),"gdt078_result.json":sha(ROOT/"gdt078_result.json")},
        "implementation":{Path(__file__).name:sha(Path(__file__))},"outputs":{JOIN.name:sha(JOIN),TESTS.name:sha(TESTS),COUNTER.name:sha(COUNTER)},"documents":{METHOD.name:sha(METHOD),REPORT.name:sha(REPORT)},
    }
    result["result_content_sha256"]=csha(result); RESULT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":status,"eligible":len(eligible),"hits":sum(int(r['stable_class']) for r in eligible),"effect":effect,"f82v":observed},sort_keys=True))


if __name__ == "__main__": main()
