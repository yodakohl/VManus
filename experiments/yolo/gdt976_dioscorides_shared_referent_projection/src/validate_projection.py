#!/usr/bin/env python3
"""Independent validator for the GDT976 shared-referent projection."""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
REPO = EXP.parents[2]
SRC963 = REPO / "experiments/yolo/gdt963_dioscorides_complete_content_code/src/SOURCE.json"
ART963 = REPO / "experiments/yolo/gdt963_dioscorides_complete_content_code/artifacts"
PREREG = EXP / "PREREGISTRATION.md"
METHOD = EXP / "METHOD.md"
SPEC = EXP / "src/SPEC.json"
LOCK = EXP / "PREREG_LOCK.json"
ART = EXP / "artifacts"
FRAMES = ART963 / "TARGET_FRAMES.json.gz"
OLD_TABLE = ART963 / "CANDIDATE_TABLE.tsv"
KNOWN = ("IRIS", "XIPHION")
RECORD_ORDER = ("I.1", "I.2", "I.3", "IV.20")
LOCAL_KEEP = {"UNKNOWN_SOLVER", "UNKNOWN_WALL_CEILING", "SAT"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_gzip_json(path: Path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def prefix_incomparable(a: str, b: str) -> bool:
    return a != b and not a.startswith(b) and not b.startswith(a)


def all_starts(text: str, needle: str) -> list[int]:
    if not needle:
        return []
    return [m.start() for m in re.finditer("(?=" + re.escape(needle) + ")", text)]


def find_starts(text: str, needle: str, start: int = 0) -> list[int]:
    """Overlapping occurrence starts using the same literal semantics as regex."""
    out, pos = [], max(0, start)
    while needle:
        pos = text.find(needle, pos)
        if pos < 0:
            break
        out.append(pos)
        pos += 1
    return out


def source_atoms(record: dict) -> list[str]:
    return [atom for token in record.get("tokens", []) for atom in token.get("atoms", [])]


def derive_projection(source: dict, spec: dict) -> tuple[dict, list[dict]]:
    records = {record["id"]: record for record in source.get("records", [])}
    projections = {item["record"]: item for item in spec.get("projections", [])}
    derived, errors = {}, []
    for rid in RECORD_ORDER:
        record, contract = records.get(rid), projections.get(rid)
        if not isinstance(record, dict) or not isinstance(contract, dict):
            errors.append({"record": rid, "kind": "missing_record_or_projection"})
            continue
        atoms = source_atoms(record)
        if record.get("atoms") is not None and list(record["atoms"]) != atoms:
            errors.append({"record": rid, "kind": "registered_atom_stream_differs_from_tokens"})
        positions = [i for i, atom in enumerate(atoms) if atom in KNOWN]
        names = [atoms[i] for i in positions]
        gaps, previous = [], -1
        for pos in positions:
            gaps.append(pos - previous - 1)
            previous = pos
        tail = len(atoms) - positions[-1] - 1 if positions else len(atoms)
        if names != contract.get("events", []):
            errors.append({"record": rid, "kind": "event_order", "actual": names,
                           "expected": contract.get("events", [])})
        if len(atoms) != contract.get("source_atoms"):
            errors.append({"record": rid, "kind": "source_atom_count", "actual": len(atoms),
                           "expected": contract.get("source_atoms")})
        if gaps != contract.get("gaps_before", []) or tail != contract.get("tail"):
            errors.append({"record": rid, "kind": "gap_or_tail", "actual": [gaps, tail],
                           "expected": [contract.get("gaps_before", []), contract.get("tail")]})
        derived[rid] = {"source_atoms": len(atoms), "events": names,
                        "event_positions": positions, "gaps_before": gaps, "tail": tail}
    if source.get("known_atoms") is not None and list(source.get("known_atoms", [])) != list(spec.get("known_atoms", [])):
        errors.append({"kind": "known_atom_set", "actual": source.get("known_atoms"),
                       "expected": spec.get("known_atoms")})
    return derived, errors


def lock_checks() -> dict:
    checks = {"prereg_exists": PREREG.exists(), "method_exists": METHOD.exists(),
              "spec_exists": SPEC.exists(), "lock_exists": LOCK.exists(),
              "target_cache_opened": False}
    errors = []
    lock = load_json(LOCK) if LOCK.exists() else {}
    files = lock.get("files", {}) if isinstance(lock, dict) else {}
    if not isinstance(files, dict) or not files:
        errors.append("missing_or_empty_files_map")
    for relative, expected in files.items() if isinstance(files, dict) else ():
        if Path(relative).is_absolute() or ".." in Path(relative).parts:
            errors.append({"path": relative, "error": "lock_path_not_repository_relative"})
            continue
        path = REPO / relative
        actual = digest(path) if path.is_file() else None
        if actual != expected:
            errors.append({"path": relative, "expected": expected, "actual": actual})
    checks.update({"lock_file_count": len(files) if isinstance(files, dict) else 0,
                   "lock_hashes": not errors, "errors": errors,
                   "prereg_sha256": digest(PREREG) if PREREG.exists() else None,
                   "method_sha256": digest(METHOD) if METHOD.exists() else None,
                   "spec_sha256": digest(SPEC) if SPEC.exists() else None})
    required = ("prereg_exists", "method_exists", "spec_exists", "lock_exists", "lock_hashes")
    checks["status"] = "PASS_REGISTRATION_ONLY" if all(checks[k] for k in required) else "FAIL_REGISTRATION_ONLY"
    return checks


def source_checks() -> tuple[dict, dict]:
    source, spec = load_json(SRC963), load_json(SPEC)
    projection, errors = derive_projection(source, spec)
    ids = [r.get("id") for r in source.get("records", [])]
    checks = {"source_exists": SRC963.exists(),
              "source_schema": source.get("schema") == "GDT963_COMPLETE_PRINTED_CONTENT_STREAM_V1",
              "source_record_order": ids == list(RECORD_ORDER),
              "source_projection": not errors, "source_errors": errors,
              "source_sha256": digest(SRC963) if SRC963.exists() else None,
              "spec_sha256": digest(SPEC) if SPEC.exists() else None,
              "regex_fixture": regex_fixture_check()}
    checks["status"] = "PASS_SOURCE_PROJECTION" if all(checks[k] for k in
        ("source_exists", "source_schema", "source_record_order", "source_projection", "regex_fixture")) else "FAIL_SOURCE_PROJECTION"
    counts = {rid: {"source_atoms": value["source_atoms"], "events": value["events"],
                    "gaps_before": value["gaps_before"], "tail": value["tail"]}
              for rid, value in projection.items()}
    return checks, {"source": source, "spec": spec, "projection": projection, "counts": counts}


def load_domains(source: dict, spec: dict) -> tuple[dict, list[dict], list[dict]]:
    frames = load_gzip_json(FRAMES)
    with OLD_TABLE.open(encoding="utf-8", newline="") as handle:
        table = list(csv.DictReader(handle, delimiter="\t"))
    frame_by_id = {(f.get("edition"), f.get("page")): f for f in frames}
    domains = {edition: {rid: [] for rid in RECORD_ORDER} for edition in spec.get("editions", [])}
    for row in table:
        frame = frame_by_id.get((row.get("edition"), row.get("page")))
        if (frame is not None and frame.get("eligible") is True and row.get("status") in LOCAL_KEEP
                and row.get("record") in RECORD_ORDER):
            domains.setdefault(row["edition"], {}).setdefault(row["record"], []).append({
                "page": row["page"], "physical_leaf": frame.get("physical_leaf"), "text": frame.get("text")})
    for edition in domains:
        for rid in domains[edition]:
            domains[edition][rid].sort(key=lambda x: (str(x["page"]), str(x["physical_leaf"])))
    return domains, frames, table


def prefix_domain(text: str, atom_count: int, occurrences: int = 1) -> list[str]:
    """Prefixes bounded by one character for every other source atom."""
    upper = (len(text) - atom_count + occurrences) // occurrences
    return [text[:n] for n in range(1, max(0, upper) + 1)]


def i1_matches(text: str, v: str, w: str) -> list[tuple[int, int]]:
    if not text.startswith(v):
        return []
    return [(0, q) for q in all_starts(text, w)
            if q >= len(v) + 4 and len(text) - q - len(w) >= 259]


def iv20_matches(text: str, w: str, v: str) -> list[tuple[int, int]]:
    if not text.startswith(w):
        return []
    return [(0, q) for q in all_starts(text, v)
            if q >= len(w) + 14 and len(text) - q - len(v) >= 110]


def i2_matches(text: str, v: str) -> list[tuple[int, int]]:
    starts = find_starts(text, v, 6)
    return [(p, q) for p in starts for q in starts
            if p >= 6 and q >= p + len(v) + 92 and len(text) - q - len(v) >= 20]


def prefix_lcp(text: str, other: str, start: int) -> int:
    n = 0
    limit = min(len(other), len(text) - start)
    while n < limit and text[start + n] == other[n]:
        n += 1
    return n


def prefix_match_caps(text: str, prefix_source: str) -> list[tuple[int, int]]:
    if not prefix_source:
        return []
    return [(q, prefix_lcp(text, prefix_source, q))
            for q, char in enumerate(text) if char == prefix_source[0]]


def pruned_pair_matches(a: str, x: str, max_v: int, max_w: int) -> list[dict]:
    """Use occurrence caps to prune; verify retained pairs with both regexes."""
    # v is a prefix of the I.1 string a; measure its occurrences in IV.20 x.
    x_caps = prefix_match_caps(x, a)
    a_caps = prefix_match_caps(a, x)
    out = []
    for lv in range(1, max_v + 1):
        v = a[:lv]
        q4 = [q for q, cap in x_caps if cap >= lv and len(x) - q - lv >= 110]
        if not q4:
            continue
        max_w4 = max(q - 14 for q in q4)
        max_w1 = max((min(cap, len(a) - q - 259) for q, cap in a_caps
                      if q >= lv + 4 and len(a) - q - 259 >= 1), default=0)
        for lw in range(1, min(max_w1, max_w4, max_w) + 1):
            w = x[:lw]
            if prefix_incomparable(v, w):
                m1, m4 = i1_matches(a, v, w), iv20_matches(x, w, v)
                if m1 and m4:
                    out.append({"v": v, "w": w, "m1": list(m1[0]), "m4": list(m4[0])})
    return out


def regex_fixture_check() -> bool:
    """Small exact partition check for the three anchored event patterns."""
    v, w = "ab", "cde"
    for gap in (4, 5, 6):
        for tail in (259, 260):
            text = v + "x" * gap + w + "y" * tail
            if not i1_matches(text, v, w):
                return False
    if i1_matches(v + "x" * 3 + w + "y" * 259, v, w):
        return False
    for gap in (14, 15):
        for tail in (110, 111):
            text = w + "x" * gap + v + "y" * tail
            if not iv20_matches(text, w, v):
                return False
    text = w + "x" * 14 + v + "y" * 109
    if iv20_matches(text, w, v):
        return False
    for initial in (6, 7):
        for gap in (92, 93):
            for tail in (20, 21):
                text = "z" * initial + v + "x" * gap + v + "y" * tail
                if not i2_matches(text, v):
                    return False
    return True


def candidate_rows(edition: str, domains: dict, projection: dict):
    i1, i2, i3 = (domains.get(edition, {}).get(r, []) for r in ("I.1", "I.2", "I.3"))
    iv = domains.get(edition, {}).get("IV.20", [])
    support = defaultdict(list)
    v_values = sorted({v for a in i1 for v in prefix_domain(a["text"], projection["I.1"]["source_atoms"])})
    for ac in i2:
        for v in v_values:
            starts = all_starts(ac["text"], v)
            if starts:
                matches = i2_matches(ac["text"], v)
                support[v].append({"page": ac["page"], "physical_leaf": ac["physical_leaf"],
                                   "positions": list(matches[0]) if matches else []})
    rows, local_pairs = [], []
    for a in i1:
        for x in iv:
            matches = pruned_pair_matches(a["text"], x["text"],
                                           len(prefix_domain(a["text"], projection["I.1"]["source_atoms"])),
                                           len(prefix_domain(x["text"], projection["IV.20"]["source_atoms"])))
            for match in matches:
                v, w, m1, m4 = match["v"], match["w"], match["m1"], match["m4"]
                local_pairs.append((a["page"], x["page"], v, w))
                usable_ac = [z for z in support.get(v, []) if z["positions"]
                             if z["physical_leaf"] not in {a["physical_leaf"], x["physical_leaf"]}
                             and any(len({a["physical_leaf"], x["physical_leaf"], z["physical_leaf"], m["physical_leaf"]}) == 4 for m in i3)]
                assignments = sum(1 for z in usable_ac for m in i3
                                  if len({a["physical_leaf"], x["physical_leaf"], z["physical_leaf"], m["physical_leaf"]}) == 4)
                if assignments == 0:
                    continue
                rows.append({"edition": edition, "iris_page": a["page"], "xiphion_page": x["page"],
                             "iris_code": v, "xiphion_code": w, "iris_positions": m1,
                             "xiphion_positions": m4,
                             "acorus_pages": sorted({z["page"] for z in usable_ac}),
                             "four_page_assignments": assignments})
    rows.sort(key=lambda r: (r["iris_page"], r["xiphion_page"], len(r["iris_code"]), len(r["xiphion_code"]), r["iris_code"], r["xiphion_code"]))
    return rows, {k: sorted(v, key=lambda z: (z["page"], z["physical_leaf"], z["positions"])) for k, v in support.items()}, local_pairs


def derive_outputs(source: dict, projection: dict, domains: dict, frames: list[dict]):
    candidates, supports, pairs = [], {}, []
    classes = defaultdict(lambda: {"page_pairs": 0, "acorus_triples": 0, "four_page_assignments": 0})
    for edition in domains:
        rows, support, _ = candidate_rows(edition, domains, projection)
        candidates.extend(rows); supports[edition] = support
        by_pair = defaultdict(list)
        for row in rows:
            by_pair[(row["iris_page"], row["xiphion_page"])].append(row)
            key = (edition, row["iris_code"], row["xiphion_code"])
            classes[key]["page_pairs"] += 1
            classes[key]["acorus_triples"] += len(row["acorus_pages"])
            classes[key]["four_page_assignments"] += row["four_page_assignments"]
        d = domains[edition]
        capacity = all(d.values()) and len({z["physical_leaf"] for v in d.values() for z in v}) >= 4
        for a in d["I.1"]:
            for x in d["IV.20"]:
                selected = by_pair.get((a["page"], x["page"]), [])
                if a["physical_leaf"] == x["physical_leaf"]:
                    pair_status = "SAME_PHYSICAL_LEAF"
                elif not capacity:
                    pair_status = "NO_FOUR_LEAF_CAPACITY"
                else:
                    pair_status = "PARTIAL_SHARED_REFERENT_ONLY" if selected else "NO_SHARED_REFERENT_PROJECTION"
                pairs.append({"edition": edition, "iris_page": a["page"], "xiphion_page": x["page"],
                              "iris_leaf": a["physical_leaf"], "xiphion_leaf": x["physical_leaf"],
                              "status": pair_status, "candidate_code_pairs": len(selected),
                              "four_page_assignments": sum(r["four_page_assignments"] for r in selected)})
    pairs.sort(key=lambda r: (r["edition"], r["iris_page"], r["xiphion_page"]))
    class_rows = [{"edition": key[0], "iris_code": key[1], "xiphion_code": key[2], **value} for key, value in sorted(classes.items())]
    return candidates, supports, pairs, class_rows


def result_checks(source, domains, frames, candidates):
    actual = load_json(ART / "RESULT.json")
    editions = {}
    for ed,d in domains.items():
        rows = [x for x in candidates if x["edition"] == ed]
        leaves = {x["physical_leaf"] for xs in d.values() for x in xs}
        capacity = all(d.values()) and len(leaves) >= 4
        editions[ed] = dict(domains={k:len(v) for k,v in d.items()}, physical_leaves=len(leaves),
            status="NO_CAPACITY" if not capacity else "PARTIAL_SHARED_REFERENT_ONLY" if rows else "SHARED_REFERENT_PROJECTION_CONTRADICTED",
            candidate_code_pairs=len(rows), acorus_triples=sum(len(x["acorus_pages"]) for x in rows),
            four_page_assignments=sum(x["four_page_assignments"] for x in rows))
    expected = dict(status="PARTIAL_SHARED_REFERENT_BINDINGS_REMAIN" if candidates else "NO_LITERAL_SHARED_REFERENT_BINDING",
        frames=len(frames),eligible_frames=sum(x["eligible"] for x in frames),source_unknown_frames=sum(not x["eligible"] for x in frames),
        page_pairs=sum(len(d["I.1"])*len(d["IV.20"]) for d in domains.values()),candidate_code_pairs=len(candidates),
        code_classes=len({(x["edition"],x["iris_code"],x["xiphion_code"]) for x in candidates}),editions=editions,
        confirmed_words=0,independent_confirmation_leaves=0,full_code_tested=False,reserve_access=False,prior_exposure=True,complete_enumeration=True)
    errors=[dict(field=k,actual=actual.get(k),expected=v) for k,v in expected.items() if actual.get(k)!=v]
    return dict(status="PASS" if not errors else "FAIL",errors=errors)


def compare_artifacts(source, projection, domains, frames, table):
    candidates, supports, pairs, classes = derive_outputs(source, projection, domains, frames)
    errors = []
    checks = {"frames_complete": len(frames) == 357 and len({(f.get("edition"), f.get("page")) for f in frames}) == len(frames),
              "candidate_table_complete": len(table) == len(frames) * 4 and len({(r.get("edition"), r.get("page"), r.get("record")) for r in table}) == len(table)}
    errors.extend(name for name, ok in checks.items() if not ok)
    expected = {"DOMAINS.json": domains, "CANDIDATES.json.gz": candidates}
    for name, value in expected.items():
        path = ART / name
        checks[name] = path.exists() and (load_gzip_json(path) if name.endswith(".gz") else load_json(path)) == value
        if not checks[name]: errors.append(name)
    cache = load_gzip_json(ART / "ACORUS_SUPPORT.json.gz")
    cache_ok = set(cache) == set(domains)
    for ed,d in domains.items():
        values = cache.get(ed,{})
        required = {x["iris_code"] for x in candidates if x["edition"]==ed}
        cache_ok &= required <= set(values)
        for v,rows in values.items():
            legal_prefix = any(z["text"].startswith(v) and 0<len(v)<=len(z["text"])-projection["I.1"]["source_atoms"]+1 for z in d["I.1"])
            cache_ok &= legal_prefix and rows == [z for z in supports.get(ed,{}).get(v,[]) if z["positions"]]
    checks["ACORUS_SUPPORT.json.gz"] = bool(cache_ok)
    if not cache_ok: errors.append("ACORUS_SUPPORT.json.gz")
    pred_header=['edition','iris_page','xiphion_page','iris_code','xiphion_code','iris_positions','xiphion_positions','acorus_pages','four_page_assignments']
    pred_expected=[pred_header]+[[str(z) for z in [c['edition'],c['iris_page'],c['xiphion_page'],c['iris_code'],c['xiphion_code'],','.join(map(str,c['iris_positions'])),','.join(map(str,c['xiphion_positions'])),','.join(c['acorus_pages']),c['four_page_assignments']]] for c in candidates]
    with (ART/'CANDIDATE_PREDICTIONS.tsv').open() as f:checks['CANDIDATE_PREDICTIONS.tsv']=list(csv.reader(f,delimiter='\t'))==pred_expected
    if not checks['CANDIDATE_PREDICTIONS.tsv']:errors.append('CANDIDATE_PREDICTIONS.tsv')
    pair_path = ART / "PAGE_PAIRS.tsv"
    header = ["edition", "iris_page", "xiphion_page", "iris_leaf", "xiphion_leaf", "status", "candidate_code_pairs", "four_page_assignments"]
    if pair_path.exists():
        with pair_path.open(encoding="utf-8", newline="") as f: actual = list(csv.DictReader(f, delimiter="\t"))
        expected_rows = [{k: str(row[k]) for k in header} for row in pairs]
        checks["PAGE_PAIRS.tsv"] = actual == expected_rows and (not actual or list(actual[0]) == header)
    else: checks["PAGE_PAIRS.tsv"] = False
    if not checks["PAGE_PAIRS.tsv"]: errors.append("PAGE_PAIRS.tsv")
    class_path = ART / "CODE_CLASSES.tsv"
    chead = ["edition", "iris_code", "xiphion_code", "page_pairs", "acorus_triples", "four_page_assignments"]
    if class_path.exists():
        with class_path.open(encoding="utf-8", newline="") as f: actual = list(csv.DictReader(f, delimiter="\t"))
        expected_rows = [{k: str(row[k]) for k in chead} for row in classes]
        checks["CODE_CLASSES.tsv"] = actual == expected_rows and (not actual or list(actual[0]) == chead)
    else: checks["CODE_CLASSES.tsv"] = False
    if not checks["CODE_CLASSES.tsv"]: errors.append("CODE_CLASSES.tsv")
    result = result_checks(source, domains, frames, candidates)
    checks["RESULT.json"] = result["status"] == "PASS"
    if result["status"] != "PASS":
        errors.append("RESULT.json")
    return {"status": "PASS" if not errors else "FAIL", "checks": checks, "errors": errors,
            "derived_counts": {"frames": len(frames), "candidates": len(candidates), "page_pairs": len(pairs), "code_classes": len(classes)}}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--registration-only", action="store_true")
    args = ap.parse_args()
    registration, = (lock_checks(),)
    source_status, data = source_checks()
    if args.registration_only or not args.full:
        out = {"registration": registration, "source": source_status, "source_counts": data["counts"],
               "status": "PASS_REGISTRATION_ONLY" if registration["status"] == "PASS_REGISTRATION_ONLY" and source_status["status"] == "PASS_SOURCE_PROJECTION" else "FAIL_REGISTRATION_ONLY"}
        print(json.dumps(out, ensure_ascii=False, indent=2)); return 0 if out["status"] == "PASS_REGISTRATION_ONLY" else 1
    if registration["status"] != "PASS_REGISTRATION_ONLY":
        print(json.dumps({"registration": registration, "source": source_status, "status": "FAIL", "reason": "registration_lock_failed"}, ensure_ascii=False, indent=2)); return 1
    if not FRAMES.exists() or not OLD_TABLE.exists():
        print(json.dumps({"registration": registration, "source": source_status, "status": "FAIL", "reason": "bound_963_artifact_missing"}, ensure_ascii=False, indent=2)); return 1
    domains, frames, table = load_domains(data["source"], data["spec"])
    comparison = compare_artifacts(data["source"], data["projection"], domains, frames, table)
    out = {"registration": registration, "source": source_status, "source_counts": data["counts"], "target_frames": len(frames), "comparison": comparison, "status": comparison["status"], "claim_ceiling": "source/projection and artifact validation only; no word meaning"}
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "VALIDATION.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=2)); return 0 if out["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
