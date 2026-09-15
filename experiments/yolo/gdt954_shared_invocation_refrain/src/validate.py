#!/usr/bin/env python3
"""Independent GDT954 contract audit; this never imports run.py."""
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import csv, hashlib, json, re

HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
ROOT = EXPERIMENT.parents[2]
BOUND = {"DEFINITE_SPACE", "LINE_START", "LINE_END"}
LITERAL = re.compile(r"^[a-z]+$")

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def locus_no(locus):
    return int(locus.rsplit(".", 1)[1])

def suffix(groups, width):
    if len(groups) < width:
        return {"status": "INSUFFICIENT_FIXED_GROUP_CAPACITY",
                "words": [g["ivtff_group_raw"] for g in groups],
                "source_ids": [g["source_group_id"] for g in groups],
                "reasons": ["TOO_FEW_GROUPS"]}
    chosen = groups[-width:]
    reasons = []
    if any(not LITERAL.fullmatch(g["ivtff_group_raw"]) for g in chosen):
        reasons.append("NONLITERAL_GROUP")
    if any(g["left_separator"] not in BOUND or
           g["right_separator"] not in BOUND for g in chosen):
        reasons.append("UNCERTAIN_BOUNDARY")
    for a, b in zip(chosen, chosen[1:]):
        expected = (("DEFINITE_SPACE", "DEFINITE_SPACE")
                    if a["locus"] == b["locus"]
                    else ("LINE_END", "LINE_START"))
        if (a["right_separator"], b["left_separator"]) != expected:
            reasons.append("INCOMPATIBLE_ADJACENCY")
    return {"status": "UNKNOWN" if reasons else "KNOWN",
            "words": [g["ivtff_group_raw"] for g in chosen],
            "source_ids": [g["source_group_id"] for g in chosen],
            "reasons": sorted(set(reasons))}

def classify(ss, width):
    known = [(i, s) for i, s in enumerate(ss) if s["status"] == "KNOWN"]
    conflicts = [[i + 1, j + 1] for (i, a), (j, b) in combinations(known, 2)
                 if a["words"] != b["words"]]
    noninjective = [i + 1 for i, s in known
                    if width == 5 and len(set(s["words"])) != 5]
    if any(s["status"] == "INSUFFICIENT_FIXED_GROUP_CAPACITY" for s in ss):
        status = "INSUFFICIENT_FIXED_GROUP_CAPACITY"
    elif conflicts or noninjective:
        status = "CONTRADICTED"
    elif any(s["status"] == "UNKNOWN" for s in ss):
        status = "UNRESOLVED_ONLY"
    else:
        status = "OBSERVED_RECURRENT_CLOSURE"
    return status, conflicts, noninjective

def synthetic_checks():
    def g(raw, locus="f1r.1", left="DEFINITE_SPACE", right="DEFINITE_SPACE"):
        return {"ivtff_group_raw": raw, "source_group_id": locus + "|G001",
                "locus": locus, "left_separator": left,
                "right_separator": right}
    a, b = g("alpha", right="LINE_END"), g("beta", "f1r.2", "LINE_START")
    checks = {
        "cross_line_seam": suffix([a, b], 2)["status"] == "KNOWN",
        "distinct_r1_conflict": classify([
            {"status":"KNOWN", "words":["a"]},
            {"status":"KNOWN", "words":["b"]}], 1)[0] == "CONTRADICTED",
        "uncertain_group": suffix([g("?alpha")], 1)["status"] == "UNKNOWN",
        "r5_noninjective": classify([
            {"status":"KNOWN", "words":["a","b","b","d","e"]}], 5)[0] == "CONTRADICTED",
        "short_capacity": suffix([g("a"), g("b")], 5)["status"] ==
            "INSUFFICIENT_FIXED_GROUP_CAPACITY",
    }
    checks["all_pass"] = all(checks.values())
    return checks

def reconstruct(spec):
    lines, inputs = {}, []
    for rel in spec["sources"]:
        path, src = ROOT / rel, load(ROOT / rel)
        inputs.append({"path": rel, "sha256": digest(path),
                       "line_count": len(src["lines"])})
        for row in src["lines"]:
            md = row["metadata"]
            key = (md["edition"], md["locus"])
            if key in lines:
                raise AssertionError("duplicate source line %s" % (key,))
            lines[key] = [dict(md, **dict(zip(src["group_columns"], g)))
                          for g in row["groups"]]
    ppath = ROOT / spec["paragraph_source"]
    paragraphs = load(ppath)
    inputs.append({"path": spec["paragraph_source"], "sha256": digest(ppath)})
    allowed = set(load(ROOT / spec["allow_source"])["allowed_selectors"])
    all_cases, suffix_rows, remaining, denom = [], [], {}, {}
    integrity = Counter()
    for edition in spec["editions"]:
        by_page, per_para = defaultdict(list), {}
        for p in paragraphs.get(edition, []):
            if p["page"] not in allowed or not p.get("lines"):
                raise AssertionError("paragraph outside scope or empty")
            groups = []
            for line in p["lines"]:
                key = (edition, line["locus"])
                if key not in lines:
                    raise AssertionError("missing paragraph line %s" % (key,))
                gs = lines[key]
                if [g["ivtff_group_raw"] for g in gs] != line["words"]:
                    raise AssertionError("word mismatch %s" % (key,))
                if [g["source_group_id"] for g in gs] != line["source_ids"]:
                    raise AssertionError("id mismatch %s" % (key,))
                groups.extend(gs); integrity["line_refs"] += 1
            if len(groups) != p["groups"]:
                raise AssertionError("group count mismatch %s" % p["id"])
            integrity["paragraphs"] += 1; integrity["groups"] += len(groups)
            by_page[p["page"]].append(p); per_para[p["id"]] = {}
            for model, width in spec["models"].items():
                got = suffix(groups, width)
                per_para[p["id"]][model] = got
                suffix_rows.append({"edition":edition, "page":p["page"],
                                    "paragraph":p["id"], "model":model, **got})
        windows, rejected = 0, 0
        outcomes = {m: Counter() for m in spec["models"]}
        for page, ps in sorted(by_page.items()):
            ps = sorted(ps, key=lambda p: p["lines"][0]["row"])
            n = spec["window_paragraphs"]
            for start in range(len(ps) - n + 1):
                chosen = ps[start:start+n]
                adjacent = all(locus_no(b["lines"][0]["locus"]) ==
                                locus_no(a["lines"][-1]["locus"]) + 1
                                for a, b in zip(chosen, chosen[1:]))
                if not adjacent:
                    rejected += 1; continue
                windows += 1
                for model, width in spec["models"].items():
                    ss = [per_para[p["id"]][model] for p in chosen]
                    status, conflicts, noninjective = classify(ss, width)
                    outcomes[model][status] += 1
                    all_cases.append({"edition":edition, "page":page,
                        "physical_leaf":chosen[0]["leaf"],
                        "window_start":chosen[0]["id"], "model":model,
                        "status":status, "paragraph_ids":[p["id"] for p in chosen],
                        "suffixes":ss,
                        "contradictory_paragraph_pairs_1based":conflicts,
                        "R5_noninjective_paragraphs_1based":noninjective,
                        "independent_confirmation_leaves":0})
                    if status in {"UNRESOLVED_ONLY", "OBSERVED_RECURRENT_CLOSURE"}:
                        for p in chosen:
                            remaining[edition + "|" + p["id"]] = {"edition":edition, **p}
        denom[edition] = {"complete_paragraphs":len(paragraphs.get(edition, [])),
            "source_pages":len(by_page), "seven_paragraph_windows":windows,
            "rejected_gapped_windows":rejected,
            "paragraph_capacity":"AVAILABLE" if by_page else "NO_PARAGRAPH_CAPACITY",
            "models":{m:dict(c) for m,c in outcomes.items()}}
    result = {"status":"COMPLETE_FIXED_REFRAIN_SCREEN", "source_prayers":7,
        "source_refrain_translation_hypothesis":"Come quickly with your spirits.",
        "editions":denom, "case_rows":len(all_cases), "suffix_rows":len(suffix_rows),
        "remaining_context_paragraphs":len(remaining), "confirmed_words":0,
        "claim_ceiling":"Necessary shared-closure condition only; preceding names and source identity not established; no significance or independent leaf confirmation."}
    return result, all_cases, suffix_rows, remaining, inputs, dict(integrity)

def compare(name, expected, actual, checks):
    ok = expected == actual
    checks[name] = {"status":"PASS" if ok else "FAIL"}
    if not ok:
        checks[name].update({"expected_count":len(expected) if hasattr(expected,"__len__") else None,
                             "actual_count":len(actual) if hasattr(actual,"__len__") else None})
    return ok

def main():
    checks = {"synthetic": synthetic_checks()}; ok = checks["synthetic"]["all_pass"]
    spec = load(EXPERIMENT / "src/SPEC.json"); source = load(EXPERIMENT / "src/SOURCE.json")
    checks["model_contract"] = {"status":"PASS" if spec.get("models")=={"R1":1,"R5":5} else "FAIL"}
    # SOURCE stores the catalogue refrain as a token array but each prayer's
    # copied field is a rendered string; compare the same representation.
    refrain = " ".join(source.get("refrain_latin", []))
    checks["source_refrain"] = {"status":"PASS" if len(source.get("prayers",[]))==7 and
        all(p.get("refrain_latin")==refrain for p in source.get("prayers",[])) else "FAIL"}
    ok &= checks["model_contract"]["status"] == "PASS" and checks["source_refrain"]["status"] == "PASS"
    try:
        expected = reconstruct(spec)
        checks["source_reconstruction"] = {"status":"PASS", "inputs":expected[4], "integrity":expected[5]}
    except Exception as exc:
        checks["source_reconstruction"] = {"status":"FAIL", "error":repr(exc)}; expected = None
    if expected:
        result, cases, suffixes, remaining = expected[:4]
        for name, value in [("RESULT.json",result), ("ALL_CANDIDATES.json",cases),
                            ("ALL_PARAGRAPH_SUFFIXES.json",suffixes),
                            ("REMAINING_CONTEXTS.json",remaining)]:
            path = EXPERIMENT / "artifacts" / name
            present = path.exists(); actual = load(path) if present else None
            ok &= compare(name, value, actual, checks) if present else False
            if not present: checks[name] = {"status":"MISSING"}
        path = EXPERIMENT / "artifacts/CANDIDATE_TABLE.tsv"
        if path.exists():
            rows = list(csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"))
            def table_row(c):
                return {"edition": c["edition"], "page": c["page"],
                    "physical_leaf": str(c["physical_leaf"]),
                    "window_start": c["window_start"], "model": c["model"],
                    "status": c["status"],
                    "paragraph_ids": ";".join(c["paragraph_ids"]),
                    "observed_suffixes": ";".join(" ".join(s["words"])
                                                   for s in c["suffixes"]),
                    "unknown_suffixes": str(sum(s["status"] == "UNKNOWN"
                                                for s in c["suffixes"])),
                    "pair_conflicts": json.dumps(
                        c["contradictory_paragraph_pairs_1based"],
                        separators=(",", ":")),
                    "R5_noninjective": ",".join(map(str,
                        c["R5_noninjective_paragraphs_1based"])),
                    "independent_confirmation_leaves": str(
                        c["independent_confirmation_leaves"])}
            fields = ["edition", "page", "physical_leaf", "window_start",
                      "model", "status", "paragraph_ids", "observed_suffixes",
                      "unknown_suffixes", "pair_conflicts", "R5_noninjective",
                      "independent_confirmation_leaves"]
            expected_rows = [{k: table_row(c)[k] for k in fields} for c in cases]
            got = [{k: row.get(k, "") for k in fields} for row in rows]
            good = got == expected_rows
            checks["CANDIDATE_TABLE.tsv"] = {"status":"PASS" if good else "FAIL", "rows":len(rows), "expected":len(cases)}
            ok &= good
        else:
            checks["CANDIDATE_TABLE.tsv"] = {"status":"MISSING"}; ok = False
    lock = EXPERIMENT / "PREREG_LOCK.json"
    if lock.exists():
        data = load(lock); good = all((ROOT/r).exists() and digest(ROOT/r)==v for r,v in data.get("files",{}).items())
        checks["prereg_lock"] = {"status":"PASS" if good else "FAIL", "sha256":digest(lock)}; ok &= good
    else:
        checks["prereg_lock"] = {"status":"NOT_PRESENT_PRE_INTAKE"}
    out = {"status":"PASS" if ok else "FAIL", "independent":True, "checks":checks,
           "claim_ceiling":"Necessary-condition audit only; no translation or source identity is confirmed."}
    (EXPERIMENT / "artifacts/VALIDATION.json").write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(out,ensure_ascii=False,indent=2)); return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
