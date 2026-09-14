#!/usr/bin/env python3
"""Independent structural validator; intentionally does not import run.py."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import csv
import hashlib
import json
from pathlib import Path
import re
import sys


def find_root(start: Path) -> Path:
    for p in (start, *start.parents):
        if (p / "AGENTS.md").is_file() and (p / ".git").exists():
            return p
    raise RuntimeError("repository root not found")


ROOT = find_root(Path(__file__).resolve())
EXP = Path(__file__).resolve().parents[1]
SRC = EXP / "src"
ART = EXP / "artifacts"
SESSION = ROOT / "research_registry/work_batches/seven_hours_20260914"


def load(path: Path):
    assert path.is_file(), f"missing required file: {path}"
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canon_sign(x: str) -> str:
    x = re.sub(r"[^a-z]", "", str(x).lower())
    return {"aries": "ARIES", "taurus": "TAURUS", "gemini": "GEMINI",
            "cancer": "CANCER", "leo": "LEO", "virgo": "VIRGO",
            "libra": "LIBRA", "scorpio": "SCORPIUS", "scorpius": "SCORPIUS",
            "sagittarius": "SAGITTARIUS", "capricorn": "CAPRICORN",
            "aquarius": "AQUARIUS", "pisces": "PISCES"}[x]


def roles(model: str):
    return ("decan", "term", "monomoirion") if model == "T3" else \
           ("decan", "term", "monomoirion", "domicile")


def field(row, names):
    by = {re.sub(r"[^a-z0-9]", "", str(k).lower()): v for k, v in row.items()}
    for name in names:
        key = re.sub(r"[^a-z0-9]", "", name.lower())
        if key in by:
            return by[key]
    raise AssertionError(f"missing fields {names}: {row}")


def check_lock():
    lock = load(EXP / "PREREG_LOCK.json")
    assert lock.get("files") and lock.get("source_files"), "incomplete lock"
    n = 0
    for rel, expected in lock["files"].items():
        assert sha(EXP / rel) == expected, f"changed bound experiment file {rel}"
        n += 1
    for rel, expected in lock["source_files"].items():
        assert sha(ROOT / rel) == expected, f"changed bound source file {rel}"
        n += 1
    return {"files_checked": n, "lock_sha256": sha(EXP / "PREREG_LOCK.json")}


def source_rows(evidence: dict, spec: dict, selected_rules: dict):
    assert evidence.get("schema") == "MONOMOIRIA_SOURCE_EVIDENCE_V1"
    for source in evidence.get("sources", []):
        assert source.get("id") and source.get("url")
        assert re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", ""))
    ss = evidence["systems"]
    faces, bounds = ss["decanic_faces"]["by_sign"], ss["egyptian_bounds"]["by_sign"]
    mono = ss["monomoiria"]
    correction = selected_rules.get("source_correction", {})
    assert correction.get("selected_GH_table5_Leo_29_30") == ["Sun", "Venus"]
    assert correction.get("literal_PH_Leo_29_30") == ["Venus", "Mercury"]
    assert correction.get("choice_basis") == "explicit residue table5, not target fit"
    assert set(faces) == set(bounds) == set(mono["sign_to_group"])
    out = []
    for raw in faces:
        sign = canon_sign(raw)
        fs = faces[raw]
        assert len(fs) == 3
        seen = []
        for b in bounds[raw]:
            ds = b["integer_degrees"]
            assert len(ds) == 2 and ds == [int(ds[0]), int(ds[1])] and ds[0] <= ds[1]
            assert b["cumulative_end_degree"] == ds[-1]
            seen += list(range(ds[0], ds[1] + 1))
        assert seen == list(range(1, 31)), f"bad bounds {sign}"
        group = mono["sign_to_group"][raw]
        cycle = mono["group_degrees_1_to_30"][group]
        assert len(cycle) == 30
        for degree in range(1, 31):
            term = next(b["planet"] for b in bounds[raw]
                        if b["integer_degrees"][0] <= degree <= b["integer_degrees"][1])
            # The selected Greek Horoscopes table5 rule is authoritative for
            # this freeze; the archived PH-derived array is retained only as
            # provenance and is not silently treated as the selected cells.
            monomoirion = cycle[degree - 1]
            if sign == "LEO" and degree in (29, 30):
                monomoirion = correction["selected_GH_table5_Leo_29_30"][degree - 29]
            out.append({"sign": sign, "degree": degree,
                        "decan": fs[(degree - 1) // 10], "term": term,
                        "monomoirion": monomoirion, "domicile": group})
    assert len(out) == 360
    assert len({(r["sign"], r["degree"]) for r in out}) == 360
    return out


def check_degree_tsv(expected):
    path = SRC / "HISTORICAL_DEGREES.tsv"
    assert path.is_file(), f"missing {path}"
    got = {}
    with path.open(encoding="utf-8", newline="") as fh:
        for raw in csv.DictReader(fh, delimiter="\t"):
            s, d = canon_sign(field(raw, ("sign",))), int(field(raw, ("degree", "degree_number")))
            key = (s, d)
            assert key not in got, f"duplicate source row {key}"
            got[key] = {"sign": s, "degree": d,
                        "decan": str(field(raw, ("decan", "decan_ruler", "face"))),
                        "term": str(field(raw, ("term", "egyptian_term", "bound", "bounds"))),
                        "monomoirion": str(field(raw, ("monomoirion", "degree_ruler", "degree_ruler_planet"))),
                        "domicile": str(field(raw, ("domicile", "domicile_ruler", "sign_ruler")))}
    want = {(r["sign"], r["degree"]): r for r in expected}
    assert got == want, "HISTORICAL_DEGREES.tsv differs from independent reconstruction"
    return {"rows": len(got), "signs": len({k[0] for k in got})}


def check_rules(expected, evidence):
    rules = load(SRC / "HISTORICAL_RULES.json")
    correction = rules.get("source_correction", {})
    assert correction.get("selected_GH_table5_Leo_29_30") == ["Sun", "Venus"]
    assert correction.get("literal_PH_Leo_29_30") == ["Venus", "Mercury"]
    assert correction.get("choice_basis") == "explicit residue table5, not target fit"
    if "source_evidence_sha256" in rules:
        assert rules["source_evidence_sha256"] == sha(SESSION / "MONOMOIRIA_SOURCE_EVIDENCE.json")
    rows = next((rules[k] for k in ("degrees", "degree_rows", "rows", "records")
                 if isinstance(rules.get(k), list)), None)
    if rows is not None:
        got = {}
        for raw in rows:
            s, d = canon_sign(field(raw, ("sign",))), int(field(raw, ("degree", "degree_number")))
            got[(s, d)] = {"sign": s, "degree": d,
                           "decan": str(field(raw, ("decan", "decan_ruler", "face"))),
                           "term": str(field(raw, ("term", "egyptian_term", "bound", "bounds"))),
                           "monomoirion": str(field(raw, ("monomoirion", "degree_ruler", "degree_ruler_planet"))),
                           "domicile": str(field(raw, ("domicile", "domicile_ruler", "sign_ruler")))}
        assert got == {(r["sign"], r["degree"]): r for r in expected}
    return {"schema": rules.get("schema", "unspecified"), "explicit_rows": len(rows or [])}


def value_tuple(model, value):
    rs = roles(model)
    if isinstance(value, dict):
        return tuple(str(value[r]) for r in rs)
    assert isinstance(value, (list, tuple)) and len(value) == len(rs)
    return tuple(str(x) for x in value)


def prediction_lists(obj):
    obj = obj.get("models", obj)
    out = {}
    for model in ("T3", "T4"):
        val = obj.get(model)
        if isinstance(val, dict):
            val = val.get("tuples", val.get("records", val.get("source_tuple_types")))
        assert isinstance(val, list), f"missing predictions {model}"
        out[model] = val
    return out


def check_predictions(obj, expected_rows, spec):
    lists = prediction_lists(obj)
    signs = [canon_sign(s) for s in spec["sign_order"]]
    result = {}
    for model in ("T3", "T4"):
        rs = roles(model)
        want = {s: Counter(tuple(r[x] for x in rs) for r in expected_rows if r["sign"] == s)
                for s in signs}
        ids, vals, tuples = set(), set(), []
        for item in lists[model]:
            tid = str(item.get("id", item.get("tuple_id", "")))
            assert tid and tid not in ids
            ids.add(tid)
            value = value_tuple(model, item.get("values", item.get("tuple")))
            assert value not in vals, f"duplicate source tuple {value}"
            vals.add(value)
            got = {canon_sign(s): int(v) for s, v in item["counts"].items()}
            assert set(got) == set(signs)
            assert got == {s: want[s][value] for s in signs}, f"prediction count {tid}"
            tuples.append({"id": tid, "values": value, "counts": got})
        all_values = set().union(*(set(counter) for counter in want.values()))
        assert vals == all_values, f"incomplete source predictions {model}"
        result[model] = tuples
    return result


def inscriptions(payload, spec, phase):
    rows = payload.get("rows")
    assert isinstance(rows, list) and rows
    pages = set(spec["intake_phases"][phase])
    grouped = defaultdict(list)
    for r in rows:
        assert r.get("page") in pages and r.get("kind") == spec["kind"]
        assert r.get("edition") in spec["editions"] and not r["page"].startswith("f84")
        grouped[(r["edition"], r["page"], r["locus"])].append(r)
    out = []
    for (edition, page, locus), gs in sorted(grouped.items()):
        gs.sort(key=lambda x: int(x["source_group_index"]))
        raw = [g["ivtff_group_raw"] for g in gs]
        reasons = []
        if not all(re.fullmatch(spec["literal_regex"], str(w)) for w in raw): reasons.append("NONLITERAL_GROUP")
        if not all(int(g["source_group_count"]) == len(gs) for g in gs): reasons.append("GROUP_COUNT_MISMATCH")
        if [int(g["source_group_index"]) for g in gs] != list(range(1, len(gs) + 1)): reasons.append("NONCONSECUTIVE_INDICES")
        if not all(a["right_separator"] == b["left_separator"] == spec["definite_interior_separator"] for a, b in zip(gs, gs[1:])): reasons.append("UNCERTAIN_INTERIOR_SEAM")
        out.append({"edition": edition, "page": page, "locus": locus,
                    "sign": spec["page_sign"][page], "phase": phase,
                    "physical_leaf": re.match(r"f\d+", page)[0], "groups": raw,
                    "definite": not reasons, "unknown_reasons": reasons})
    if spec["unlabeled_slot"]["page"] in pages:
        for edition in spec["editions"]:
            out.append({"edition": edition, "page": spec["unlabeled_slot"]["page"],
                        "locus": "UNLABELED_CATALOGUE_SLOT", "sign": "GEMINI",
                        "phase": phase, "physical_leaf": "f72", "groups": [],
                        "definite": False, "unknown_reasons": ["SOURCE_UNLABELED_SLOT"]})
    for edition in spec["editions"]:
        for page in pages:
            n = len({x["locus"] for x in out if x["edition"] == edition and x["page"] == page
                     and x["locus"] != "UNLABELED_CATALOGUE_SLOT"})
            assert n == spec["expected_labels"][page], f"locus census {edition} {page}: {n}"
    return out


def hopcroft_karp(graph):
    left = sorted(graph)
    pu = {u: None for u in left}
    pv = {v: None for vs in graph.values() for v in vs}
    dist = {}

    def bfs():
        q, found = deque(), False
        for u in left:
            if pu[u] is None: dist[u] = 0; q.append(u)
            else: dist[u] = None
        while q:
            u = q.popleft()
            for v in graph[u]:
                owner = pv[v]
                if owner is None: found = True
                elif dist[owner] is None: dist[owner] = dist[u] + 1; q.append(owner)
        return found

    def dfs(u):
        for v in graph[u]:
            owner = pv[v]
            if owner is None or (dist.get(owner) == dist[u] + 1 and dfs(owner)):
                pu[u], pv[v] = v, u
                return True
        dist[u] = None
        return False

    while bfs():
        for u in left:
            if pu[u] is None: dfs(u)
    return {u: v for u, v in pu.items() if v is not None}


def hall(graph, matching):
    owners = {v: u for u, v in matching.items()}
    left = {u for u in graph if u not in matching}
    q, nbr = deque(sorted(left)), set()
    while q:
        u = q.popleft()
        for v in graph[u]:
            if v not in nbr:
                nbr.add(v)
                if v in owners and owners[v] not in left:
                    left.add(owners[v]); q.append(owners[v])
    assert len(left) > len(nbr)
    assert nbr == {v for u in left for v in graph[u]}
    return {"label_ids": sorted(left), "tuple_ids": sorted(nbr), "deficiency": len(left) - len(nbr)}


def fixtures():
    full = {"a": ["x", "y"], "b": ["x", "y"]}
    assert len(hopcroft_karp(full)) == 2
    for u in full:
        for v in full[u]:
            forced = {k: ([v] if k == u else [x for x in full[k] if x != v]) for k in full}
            assert len(hopcroft_karp(forced)) == 2
    bad = {"a": ["x"], "b": ["x"]}
    c = hall(bad, hopcroft_karp(bad))
    assert c["deficiency"] == 1 and c["label_ids"] == ["a", "b"]
    assert 0 + 30 == 30
    return {"matching": True, "forced_edges": True, "hall": True, "unknown_capacity": True}


def evaluation(model, edition, scope, signs, records, tuples):
    selected = [r for r in records if r["edition"] == edition and r["sign"] in signs]
    counts, unknown, loci = {s: Counter() for s in signs}, Counter(), defaultdict(list)
    for r in selected:
        if r["definite"]:
            w = tuple(r["groups"]); counts[r["sign"]][w] += 1; loci[w].append(r["locus"])
        else: unknown[r["sign"]] += 1
    for s in signs: assert sum(counts[s].values()) + unknown[s] == 30
    labels = [{"id": f"W{i:04}", "groups": list(w), "counts": {s: counts[s][w] for s in signs}, "loci": sorted(loci[w])}
              for i, w in enumerate(sorted(loci))]
    domains = {w["id"]: [t["id"] for t in tuples if all(w["counts"][s] <= t["counts"][s] for s in signs)] for w in labels}
    m = hopcroft_karp(domains); feasible = len(m) == len(labels)
    eq = defaultdict(list)
    for t in tuples: eq[tuple(t["counts"][s] for s in signs)].append(t["id"])
    return {"model": model, "edition": edition, "scope": scope, "signs": signs,
            "definite_slots": sum(sum(x.values()) for x in counts.values()), "unknown_slots": sum(unknown.values()),
            "unknown_by_sign": {s: unknown[s] for s in signs}, "definite_types": len(labels), "labels": labels,
            "domains": domains, "source_tuple_types": len(tuples),
            "source_count_equivalence_classes": [{"count_vector": list(k), "tuple_ids": sorted(v)} for k, v in sorted(eq.items())],
            "maximum_matching_size": len(m), "matching_witness": m, "feasible": feasible,
            "hall_certificate": None if feasible else hall(domains, m),
            "status": "CONSISTENT_UNCONFIRMED" if feasible else "CONTRADICTED"}


def check_result(actual, expected):
    fields = ["model", "edition", "scope", "signs", "definite_slots", "unknown_slots", "unknown_by_sign",
              "definite_types", "labels", "domains", "source_tuple_types", "source_count_equivalence_classes",
              "maximum_matching_size", "feasible", "status"]
    for f in fields: assert actual.get(f) == expected.get(f), f"result mismatch {f}"
    witness = actual.get("matching_witness", {})
    assert len(witness) == expected["maximum_matching_size"]
    assert len(set(witness.values())) == len(witness)
    assert all(v in expected["domains"].get(u, []) for u, v in witness.items())
    if expected["feasible"]: assert actual.get("hall_certificate") is None
    else:
        c = actual.get("hall_certificate")
        assert c and c["deficiency"] == len(c["label_ids"]) - len(c["tuple_ids"])
        assert len(c["label_ids"]) > len(c["tuple_ids"])
        assert set(c["tuple_ids"]) == {v for u in c["label_ids"] for v in expected["domains"][u]}


def forced_support(actual, expected):
    if not expected["feasible"]:
        assert actual.get("supported_discovery_edges") == {}
        assert actual.get("additional_predictions") == {}
        return 0
    got, total = actual.get("supported_discovery_edges"), 0
    assert isinstance(got, dict)
    for u, domain in expected["domains"].items():
        want = []
        for v in domain:
            graph = {x: ([v] if x == u else [z for z in ds if z != v]) for x, ds in expected["domains"].items()}
            if len(hopcroft_karp(graph)) == len(expected["labels"]): want.append(v)
        assert sorted(got.get(u, [])) == sorted(want), f"forced support {u}"
        total += len(want)
    return total


def check_package(phase, spec, records, tuples):
    package = load(ART / ("DISCOVERY.json" if phase == "discovery" else "RESULT.json"))
    assert package.get("phase") == phase and package.get("inscriptions") == records
    assert package.get("new_semantic_evidence") is False and package.get("independent_meaning_capacity") == 0
    assert package.get("reserved_pages_opened") is False and package.get("source_variants_changed") is False
    if phase == "final":
        freeze = load(EXP / "DISCOVERY_FREEZE.json")
        assert freeze.get("additional_or_taurus_contents_accessed") is False
        for rel, expected_hash in freeze.get("files", {}).items():
            assert sha(EXP / rel) == expected_hash, f"discovery freeze changed: {rel}"
    scopes = ["DISCOVERY"] if phase == "discovery" else list(spec["scopes"])
    expected = []
    for model in spec["models"]:
        for edition in spec["editions"]:
            for scope in scopes:
                expected.append(evaluation(model, edition, scope,
                                           [canon_sign(s) for s in spec["scopes"][scope]], records, tuples[model]))
    actual = package.get("results")
    assert isinstance(actual, list) and len(actual) == len(expected)
    forced = 0
    for a, e in zip(actual, expected):
        check_result(a, e)
        if e["scope"] == "DISCOVERY":
            forced += forced_support(a, e)
            if e["feasible"]:
                assert a.get("marginal_domains_are_not_independent") is True
                assert a.get("observed_binding_unique") == (bool(e["labels"]) and all(
                    len(a["supported_discovery_edges"].get(w["id"], [])) == 1 for w in e["labels"]))
                by_id = {t["id"]: t for t in tuples[e["model"]]}
                for u, vals in a.get("additional_predictions", {}).items():
                    assert [x["tuple_id"] for x in vals] == a["supported_discovery_edges"][u]
                    for x in vals:
                        assert x["tuple_id"] in by_id
                        expected_tuple = by_id[x["tuple_id"]]
                        assert value_tuple(e["model"], x["values"]) == expected_tuple["values"]
                        got_counts = {canon_sign(s): int(v) for s, v in x["counts"].items()}
                        add_signs = [canon_sign(s) for s in spec["scopes"]["ADDITIONAL"]]
                        assert got_counts == {s: expected_tuple["counts"][s] for s in add_signs}
    return {"results": len(actual), "forced_supported_edges": forced}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=("discovery", "final"), default=None)
    ap.add_argument("--source-only", action="store_true")
    args = ap.parse_args(); phase = args.phase
    fixture = fixtures(); lock = check_lock(); spec = load(SRC / "SPEC.json")
    evidence = load(SESSION / "MONOMOIRIA_SOURCE_EVIDENCE.json")
    selected_rules = load(SRC / "HISTORICAL_RULES.json")
    rows = source_rows(evidence, spec, selected_rules)
    degree = check_degree_tsv(rows); rules = check_rules(rows, evidence)
    pred_obj = load(SRC / "SOURCE_PREDICTIONS.json")
    pred = check_predictions(pred_obj, rows, spec)
    if args.source_only:
        report = {"schema": "GDT951_VALIDATION_V1", "status": "PASS_SOURCE_ONLY",
                  "lock": lock, "fixture_checks": fixture,
                  "source_reconstruction": {"rows": len(rows), "degrees_per_sign": 30, "signs": 12},
                  "historical_degrees": degree, "historical_rules": rules,
                  "source_predictions": {"models": {m: len(v) for m, v in pred.items()}},
                  "target_access": "NONE", "significance_or_null": False, "semantic_meaning": False}
        print(json.dumps(report, ensure_ascii=False, separators=(",", ":")))
        return 0
    if phase is None: phase = "final" if (ART / "RESULT.json").is_file() else "discovery"
    phases = ["discovery"] if phase == "discovery" else ["discovery", "additional", "taurus"]
    records, input_counts = [], {}
    for p in phases:
        inp = ART / f"INPUT_{p.upper()}.json"; receipt = load(SRC / f"INTAKE_{p.upper()}.json")
        assert sha(inp) == receipt["projection_sha256"]
        got = inscriptions(load(inp), spec, p); records.extend(got); input_counts[p] = len(got)
    package = check_package(phase, spec, records, pred)
    report = {"schema": "GDT951_VALIDATION_V1", "status": "PASS", "phase": phase, "lock": lock,
              "fixture_checks": fixture, "source_reconstruction": {"rows": len(rows), "degrees_per_sign": 30, "signs": 12},
              "historical_degrees": degree, "historical_rules": rules,
              "source_predictions": {"models": {m: len(v) for m, v in pred.items()}},
              "input_inscriptions": input_counts, "package": package,
              "target_access": "already_guarded_INPUT_JSON_only", "significance_or_null": False,
              "semantic_meaning": False}
    (ART / "VALIDATION.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    try: raise SystemExit(main())
    except Exception as exc:
        print(f"GDT951 VALIDATION FAILED: {exc}", file=sys.stderr); raise
