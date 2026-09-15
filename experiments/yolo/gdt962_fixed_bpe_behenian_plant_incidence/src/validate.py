#!/usr/bin/env python3
"""Independent replay/checker for GDT962's fixed parser incidence screen."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve()
EXP = HERE.parents[1]
ROOT = EXP.parents[2]
ART = EXP / "artifacts"


def load_json(path: Path):
    return json.loads(path.read_text())


def load_gzip_json(path: Path):
    return json.loads(gzip.open(path, "rt", encoding="utf-8").read())


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lock_check() -> dict:
    lock = load_json(EXP / "PREREG_LOCK.json")
    failures = []
    for rel, expected in lock.items():
        p = ROOT / rel
        got = sha256(p) if p.exists() else None
        if got != expected:
            failures.append({"path": rel, "expected": expected, "actual": got})
    return {"checked": len(lock), "failures": failures}


def collapse(raw: str, spec: dict) -> str:
    value = raw
    for old, new in spec["collapse"]:
        value = value.replace(old, new)
    return value


def bpe(raw: str, spec: dict, merges: list[dict]) -> tuple[list[str], list[str]]:
    """Return final units and every leaf/internal node instantiated."""
    tokens = [{"text": ch, "children": ()} for ch in collapse(raw, spec)]
    nodes = {t["text"] for t in tokens}
    for rule in merges:
        out = []
        i = 0
        while i < len(tokens):
            if (i + 1 < len(tokens)
                    and tokens[i]["text"] == rule["left"]
                    and tokens[i + 1]["text"] == rule["right"]):
                out.append({"text": rule["merged"], "children": (tokens[i], tokens[i + 1])})
                nodes.add(rule["merged"])
                i += 2
            else:
                out.append(tokens[i])
                i += 1
        tokens = out
    return [t["text"] for t in tokens], sorted(nodes)


def hard_chunks(paragraph: dict, spec: dict):
    """Partition at every non-UNCERTAIN_SMALL_SPACE seam."""
    chunks = []
    current = []
    join = spec["join_boundary"]
    for group in paragraph["groups"]:
        if current:
            # Paragraph exports concatenate source lines.  A line transition
            # is always a hard boundary, even though its LINE_END/LINE_START
            # classes do not describe one inter-group seam.
            if group["locus"] != current[-1]["locus"]:
                chunks.append(current)
                current = []
                current.append(group)
                continue
            left = current[-1]["right_separator"]
            right = group["left_separator"]
            if left != right:
                raise AssertionError(f"separator mismatch {current[-1]['source_group_id']} -> {group['source_group_id']}")
            if left != join:
                chunks.append(current)
                current = []
        current.append(group)
    if current:
        chunks.append(current)
    return chunks


def replay(windows: list[dict], spec: dict, inventory: list[str], merges: list[dict]):
    chunk_rows, changed, unit_masks, unknown_by_window, classes = [], [], {}, {}, []
    inventory_set = set(inventory)
    for window in windows:
        masks = {rep: {u: 0 for u in inventory} for rep in spec["representations"]}
        unknown = [0] * 15
        for pi, paragraph in enumerate(window["paragraphs"]):
            for ci, groups in enumerate(hard_chunks(paragraph, spec)):
                reasons = []
                if any(not re.fullmatch(r"[a-z]+", g["ivtff_group_raw"]) for g in groups):
                    reasons.append("NONLITERAL")
                if (groups[0]["left_separator"] not in spec["allowed_outer_boundaries"]
                        or groups[-1]["right_separator"] not in spec["allowed_outer_boundaries"]):
                    reasons.append("UNRESOLVED_OUTER_BOUNDARY")
                raw_joined = "".join(g["ivtff_group_raw"] for g in groups)
                final, nodes = ([], []) if reasons else bpe(raw_joined, spec, merges)
                known = not reasons
                if not known:
                    unknown[pi] += 1
                for rep, values in (("FINAL_UNITS", final), ("ALL_TREE_NODES", nodes)):
                    for unit in set(values) & inventory_set:
                        masks[rep][unit] |= 1 << pi
                chunk_rows.append({
                    "window_id": window["window_id"], "edition": window["edition"],
                    "page": window["page"], "paragraph_id": paragraph["id"],
                    "relative_paragraph": pi + 1, "chunk_index": ci, "locus": groups[0]["locus"],
                    "groups": [{"source_group_id": g["source_group_id"], "raw": g["ivtff_group_raw"],
                                "left_separator": g["left_separator"], "right_separator": g["right_separator"],
                                "known_in_gdt960": g["known"]} for g in groups],
                    "raw_joined": raw_joined, "known": known, "unknown_reasons": reasons,
                    "final_units": final, "tree_nodes": nodes,
                    "parsed_units_outside_inventory": sorted((set(final) | set(nodes)) - inventory_set),
                })
                for g in groups:
                    if bool(g["known"]) != known:
                        changed.append({"window_id": window["window_id"], "relative_paragraph": pi + 1,
                                        "locus": g["locus"], "source_group_id": g["source_group_id"],
                                        "raw": g["ivtff_group_raw"], "known_gdt960": g["known"],
                                        "known_gdt962": known, "chunk_raw": raw_joined,
                                        "left_separator": g["left_separator"], "right_separator": g["right_separator"]})
        unknown_by_window[window["window_id"]] = unknown
        for rep, ms in masks.items():
            unit_masks[window["window_id"], rep] = ms
            grouped = defaultdict(list)
            for unit, mask in ms.items():
                grouped[mask].append(unit)
            for mask, units in sorted(grouped.items()):
                classes.append({"window_id": window["window_id"], "representation": rep,
                                "mask": mask, "units": sorted(units)})
    return chunk_rows, changed, unit_masks, unknown_by_window, classes


def mask_from_rows(rows: list[int], direction: str) -> int:
    out = 0
    for row in rows:
        position = 16 - row if direction == "REVERSED" else row
        out |= 1 << (position - 1)
    return out


def hopcroft_karp(domains: dict[str, list[str]]) -> dict:
    """Independent maximum bipartite matcher with a Hall certificate."""
    left = sorted(domains)
    right = sorted({u for values in domains.values() for u in values})
    pair_left = {p: None for p in left}
    pair_right = {u: None for u in right}
    distance = {}

    def bfs() -> bool:
        queue, found = [], False
        for p in left:
            distance[p] = 0 if pair_left[p] is None else None
            if pair_left[p] is None:
                queue.append(p)
        while queue:
            p = queue.pop(0)
            for unit in sorted(domains[p]):
                owner = pair_right[unit]
                if owner is None:
                    found = True
                elif distance[owner] is None:
                    distance[owner] = distance[p] + 1
                    queue.append(owner)
        return found

    def dfs(p: str) -> bool:
        for unit in sorted(domains[p]):
            owner = pair_right[unit]
            if owner is None or (distance.get(owner) == distance[p] + 1 and dfs(owner)):
                pair_left[p], pair_right[unit] = unit, p
                return True
        distance[p] = None
        return False

    while bfs():
        for p in left:
            if pair_left[p] is None:
                dfs(p)
    witness = {p: pair_left[p] for p in left if pair_left[p] is not None}
    unmatched = [p for p in left if pair_left[p] is None]
    hall_p, hall_u, queue = set(unmatched), set(), list(unmatched)
    while queue:
        p = queue.pop()
        for unit in domains[p]:
            if unit in hall_u:
                continue
            hall_u.add(unit)
            owner = pair_right[unit]
            if owner is not None and owner not in hall_p:
                hall_p.add(owner)
                queue.append(owner)
    return {"size": len(witness), "witness": witness, "unmatched_plants": unmatched,
            "hall_plants": sorted(hall_p), "hall_units": sorted(hall_u),
            "deficiency": len(left) - len(witness)}


def expected_domains(window, model, direction, representation, unit_masks, unknown):
    required = {plant: mask_from_rows([int(x) for x in rows], direction)
                for plant, rows in model["incidence"].items()}
    unknown_mask = sum(1 << i for i, count in enumerate(unknown) if count)
    masks = unit_masks[window["window_id"], representation]
    result = {}
    for plant, req in required.items():
        lower = sorted(u for u, mask in masks.items() if mask == req)
        upper = []
        for unit, mask in masks.items():
            missing = req & ~mask
            if mask & ~req or missing & ~unknown_mask:
                continue
            upper.append({"unit": unit, "known_mask": mask, "missing_mask": missing})
        result[plant] = (lower, upper)
    return result, unknown_mask


def rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def gzip_rows(path: Path) -> list[dict]:
    with gzip.open(path, "rt", encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))


def validate() -> dict:
    lock = lock_check()
    spec = load_json(EXP / "src/SPEC.json")
    source = load_json(ROOT / spec["source"])
    windows = load_gzip_json(ROOT / spec["windows"])
    inventory_rows = rows(ROOT / spec["inventory"])
    # The runner freezes the closed inventory in lexical order after loading;
    # retain that order so exact TSV comparisons are meaningful.
    inventory = sorted(r["unit"] for r in inventory_rows)
    merge_rows = rows(ROOT / spec["merges"])
    merges = [{"rank": int(r["rank"]), "left": r["left"], "right": r["right"], "merged": r["merged"]}
              for r in merge_rows]
    pred = rows(ART / "PREDICTIONS.tsv")
    prior = rows(ROOT / spec["prior_predictions"])
    checks = [{"name": "lock", **lock, "ok": not lock["failures"]},
              {"name": "windows", "ok": len(windows) == 22, "actual": len(windows), "expected": 22},
              {"name": "inventory", "ok": len(inventory) == 98 and len(set(inventory)) == 98, "actual": len(inventory)},
              {"name": "merges", "ok": len(merges) == 64 and [r["rank"] for r in merges] == list(range(1, 65)),
               "actual": len(merges)},
              {"name": "prediction_count", "ok": len(pred) == 5808, "actual": len(pred), "expected": 5808}]

    source_row_errors = []
    for model_name, model in source["models"].items():
        reconstructed = defaultdict(list)
        for row in model["rows"]:
            for plant in row["plant_terms"]:
                reconstructed[plant].append(int(row["row"]))
        reconstructed = {plant: sorted(values) for plant, values in reconstructed.items()}
        registered = {plant: sorted(values) for plant, values in model["incidence"].items()}
        if reconstructed != registered:
            source_row_errors.append(model_name)
    checks.append({"name": "source_rows_to_incidence", "ok": not source_row_errors,
                   "errors": source_row_errors, "models": len(source["models"])})

    expected_pred = []
    prior_prediction_errors = 0
    for base in prior:
        source_rows = source["models"][base["model"]]["incidence"][base["plant"]]
        expected_rows = sorted(16 - r if base["direction"] == "REVERSED" else r for r in source_rows)
        req = mask_from_rows(expected_rows, "ORIGINAL")
        if base["required_rows"] != ",".join(str(x) for x in expected_rows) or int(base["required_mask"]) != req:
            prior_prediction_errors += 1
        for rep in spec["representations"]:
            expected_pred.append(dict(base, case_id=base["case_id"] + "|" + rep,
                                      required_mask=str(req), representation=rep))
    checks.append({"name": "prior_prediction_source_mask", "ok": prior_prediction_errors == 0,
                   "errors": prior_prediction_errors, "expected": 0})
    key = lambda r: (r["case_id"], r["plant"], r["representation"])
    checks.append({"name": "frozen_predictions", "ok": sorted(pred, key=key) == sorted(expected_pred, key=key),
                   "actual_count": len(pred), "expected_count": len(expected_pred)})

    chunk_rows, changed, unit_masks, unknown_by_window, classes = replay(windows, spec, inventory, merges)
    actual_chunks = load_gzip_json(ART / "PARSED_CHUNKS.json.gz")
    checks.append({"name": "parsed_chunks", "ok": actual_chunks == chunk_rows,
                   "actual_count": len(actual_chunks), "expected_count": len(chunk_rows)})
    actual_classes = load_gzip_json(ART / "IDENTICAL_UNIT_PREDICTIONS.json.gz")
    checks.append({"name": "identical_unit_predictions", "ok": actual_classes == classes,
                   "actual_count": len(actual_classes), "expected_count": len(classes)})
    actual_changed = gzip_rows(ART / "CHANGED_KNOWNNESS.tsv.gz")
    expected_changed = [{k: str(v) if isinstance(v, bool) else str(v) for k, v in x.items()} for x in changed]
    checks.append({"name": "changed_knownness", "ok": actual_changed == expected_changed,
                   "actual_count": len(actual_changed), "expected_count": len(expected_changed)})

    expected_masks = []
    for window in windows:
        for rep in spec["representations"]:
            for unit in inventory:
                mask = unit_masks[window["window_id"], rep][unit]
                expected_masks.append({"window_id": window["window_id"], "representation": rep, "unit": unit,
                                       "mask": str(mask),
                                       "observed_rows": ",".join(str(i + 1) for i in range(15) if mask & (1 << i))})
    actual_masks = gzip_rows(ART / "UNIT_MASKS.tsv.gz")
    checks.append({"name": "unit_masks", "ok": actual_masks == expected_masks,
                   "actual_count": len(actual_masks), "expected_count": len(expected_masks)})

    actual_domains = load_gzip_json(ART / "PLANT_DOMAINS.json.gz")
    expected_domains = []
    by_case = defaultdict(list)
    for p in pred:
        window = next(w for w in windows if w["window_id"] == p["window_id"])
        model = source["models"][p["model"]]
        dom, unknown_mask = expected_domains_for(window, model, p["direction"], p["representation"], unit_masks, unknown_by_window[window["window_id"]])
        lower, upper = dom[p["plant"]]
        status = "KNOWN_MASK_MATCH" if lower else "UNKNOWN_ONLY" if upper else "CONTRADICTED"
        value = dict(p, known_mask_units=lower, upper_units=upper, unknown_mask=unknown_mask, status=status)
        expected_domains.append(value)
        by_case[p["case_id"]].append(value)
    checks.append({"name": "plant_domains", "ok": actual_domains == expected_domains,
                   "actual_count": len(actual_domains), "expected_count": len(expected_domains)})

    expected_cases, case_errors = [], []
    for case_id, ds in by_case.items():
        first = ds[0]
        lo_dom = {d["plant"]: d["known_mask_units"] for d in ds}
        hi_dom = {d["plant"]: [x["unit"] for x in d["upper_units"]] for d in ds}
        lo, hi = hopcroft_karp(lo_dom), hopcroft_karp(hi_dom)
        status = "KNOWN_NECESSARY_MATCHING" if not lo["deficiency"] else "UPPER_NECESSARY_MATCHING" if not hi["deficiency"] else "CONTRADICTED"
        expected_cases.append({"case_id": case_id, "window_id": first["window_id"], "edition": first["edition"],
                               "page": first["page"], "physical_leaf": first["physical_leaf"], "model": first["model"],
                               "direction": first["direction"], "representation": first["representation"],
                               "source_names": len(ds), "known_matching": lo, "upper_matching": hi,
                               "plants_without_known_units": [d["plant"] for d in ds if not d["known_mask_units"]],
                               "plants_without_upper_units": [d["plant"] for d in ds if not d["upper_units"]],
                               "unknown_chunks": unknown_by_window[first["window_id"]], "status": status,
                               "complete_unknown_realization_assessed": False, "independent_confirmation_leaves": 0})
    actual_cases = load_gzip_json(ART / "ALL_CASES.json.gz")
    actual_by_case = {c["case_id"]: c for c in actual_cases}
    for e in expected_cases:
        a = actual_by_case.get(e["case_id"])
        if a is None:
            case_errors.append({"case_id": e["case_id"], "kind": "missing_case"})
            continue
        for side in ("known_matching", "upper_matching"):
            if a[side]["size"] != e[side]["size"] or a[side]["deficiency"] != e[side]["deficiency"]:
                case_errors.append({"case_id": e["case_id"], "kind": side + "_cardinality"})
            dom = {d["plant"]: d["known_mask_units"] if side == "known_matching" else [x["unit"] for x in d["upper_units"]]
                   for d in by_case[e["case_id"]]}
            wit = a[side]["witness"]
            if len(set(wit.values())) != len(wit) or any(p not in dom or u not in dom[p] for p, u in wit.items()):
                case_errors.append({"case_id": e["case_id"], "kind": side + "_invalid_witness"})
            if a[side]["deficiency"]:
                hp, hu = set(a[side]["hall_plants"]), set(a[side]["hall_units"])
                if len(hp) <= len(hu) or not hp.issubset(dom) or any(set(dom[p]) - hu for p in hp):
                    case_errors.append({"case_id": e["case_id"], "kind": side + "_invalid_hall"})
        if a["status"] != e["status"]:
            case_errors.append({"case_id": e["case_id"], "kind": "status"})
    checks.append({"name": "all_case_matchings", "ok": len(actual_cases) == 176 and not case_errors,
                   "actual_count": len(actual_cases), "expected_count": 176,
                   "errors": case_errors[:20], "error_count": len(case_errors)})

    result = load_json(ART / "RESULT.json")
    expected_outcomes = dict(Counter(c["status"] for c in expected_cases))
    expected_by_rep = {rep: dict(Counter(c["status"] for c in expected_cases if c["representation"] == rep))
                       for rep in spec["representations"]}
    result_fields = {
        "experiment_id": result.get("experiment_id") == "GDT962",
        "case_count": result.get("cases") == 176,
        "plant_predictions": result.get("plant_predictions") == 5808,
        "chunk_window_rows": result.get("chunk_window_rows") == len(chunk_rows),
        "known_chunk_window_rows": result.get("known_chunk_window_rows") == sum(bool(c["known"]) for c in chunk_rows),
        "changed_knownness_rows": result.get("changed_knownness_rows") == len(changed),
        "unit_masks": result.get("unit_window_representation_masks") == len(expected_masks),
        "case_outcomes": result.get("case_outcomes") == expected_outcomes,
        "by_representation": result.get("by_representation") == expected_by_rep,
        "plant_outcomes": result.get("plant_outcomes") == dict(Counter(d["status"] for d in expected_domains)),
        "mugwort_outcomes": result.get("mugwort_outcomes") == dict(Counter(d["status"] for d in expected_domains if d["plant"] == "Mugwort")),
        "mugwort_known_units": result.get("mugwort_known_units") == [],
        "confirmed_words_zero": result.get("confirmed_words") == 0,
        "independent_confirmation_zero": result.get("independent_confirmation_leaves") == 0,
    }
    checks.append({"name": "result", "ok": all(result_fields.values()), "fields": result_fields})
    ok = all(c.get("ok", False) for c in checks)
    return {"experiment_id": "GDT962", "status": "VALIDATION_PASS" if ok else "VALIDATION_FAIL",
            "independent_algorithm": "explicit parser replay + Hopcroft-Karp matching",
            "checks": checks,
            "actual_counts": {"windows": len(windows), "parsed_chunks": len(chunk_rows),
                              "known_chunks": sum(bool(c["known"]) for c in chunk_rows),
                              "changed_knownness": len(changed), "unit_masks": len(expected_masks),
                              "plant_predictions": len(pred), "cases": len(actual_cases),
                              "case_outcomes": dict(Counter(c["status"] for c in actual_cases))},
            "claim_ceiling": "engineering/source-contract validation only; no semantic confirmation"}


def expected_domains_for(window, model, direction, representation, unit_masks, unknown):
    required = {plant: mask_from_rows([int(x) for x in source_rows], direction)
                for plant, source_rows in model["incidence"].items()}
    unknown_mask = sum(1 << i for i, count in enumerate(unknown) if count)
    masks = unit_masks[window["window_id"], representation]
    result = {}
    for plant, req in required.items():
        lower = sorted(u for u, mask in masks.items() if mask == req)
        upper = []
        for unit, mask in masks.items():
            missing = req & ~mask
            if mask & ~req or missing & ~unknown_mask:
                continue
            upper.append({"unit": unit, "known_mask": mask, "missing_mask": missing})
        result[plant] = (lower, upper)
    return result, unknown_mask


def main() -> int:
    output = validate()
    (ART / "VALIDATION.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(output, indent=2, ensure_ascii=False))
    return 0 if output["status"] == "VALIDATION_PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
