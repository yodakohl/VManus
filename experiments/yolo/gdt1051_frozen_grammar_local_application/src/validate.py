#!/usr/bin/env python3
"""Verify full packet coverage, frozen transformations and local conclusions."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/yolo/gdt605_multisymbol_unit_alphabet/src"))
from run_gdt012_core_semantic_atlas import strip_layers
from run_gdt062_right_family_register_renderer import preparse
from separator_crossing import apply_bpe, collapse


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    r = json.loads((BASE / "artifacts/RESULT.json").read_text())
    assert r["status"] == "FORMAL_REPLAY_ONLY" and r["confirmed_words"] == 0
    assert r["sealed_data"] == {"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"}
    for name, expected in r["input_hashes"].items():
        p = (ROOT / name if "/" in name or name.startswith("run_") else
             ROOT / "research_registry/proposals/laufenberg_f85r2_20260926" / name)
        assert sha(p) == expected, name
    mergepath = ROOT / "experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_bpe_merges.tsv"
    with mergepath.open(newline="") as f:
        merges = [(x["left"], x["right"], x["merged"], int(x["train_occurrences"]))
                  for x in csv.DictReader(f, delimiter="\t")]
    assert len(merges) == 64
    children = {merged: (left, right) for left, right, merged, _ in merges}
    def tree(unit):
        if unit not in children:
            return unit
        left, right = children[unit]
        return [tree(left), tree(right)]
    dossier = ROOT / "research_registry/proposals/laufenberg_f85r2_20260926"
    ring = json.loads((dossier / "F68R_PAIRED_OPENINGS_SOURCE_20260927.json").read_text())
    prose = json.loads((dossier / "F89V1_OKOAIIN_CONTEXT_SOURCE_20260927.json").read_text())
    src_ring = next(q["rows"] for q in ring["queries"] if q["command"][-1] ==
                    "edition,locus,source_group_index,left_separator,right_separator,ivtff_group_raw")
    original = {(x["edition"], x["locus"], int(x["source_group_index"])): x
                for x in [*src_ring, *prose["query"]["rows"]]}
    groups = r["groups"]
    assert len(groups) == len(original) == r["raw_groups"] == 288
    keys = [(g["edition"], g["locus"], g["index"]) for g in groups]
    assert set(keys) == set(original) and len(set(keys)) == len(keys)
    assert all(not key[1].startswith("f84") for key in keys)
    for g, key in zip(groups, keys):
        source = original[key]
        assert g["raw"] == source["ivtff_group_raw"]
        assert (g["left_separator"], g["right_separator"]) == (source["left_separator"], source["right_separator"])
        if re.fullmatch("[a-z]+", g["raw"]):
            prefix, residual, dy = strip_layers(g["raw"])
            host, b3, right, inner = preparse({"residual_host": residual, "stripped_prefix": prefix})
            assert g["wrapper_host"] == dict(wrapper=prefix, residual_host=residual,
                                             dy_closure=dy, page_host_before_local_frame=host,
                                             b3=b3, right_family=right, inner_d=inner,
                                             local_frame="NOT_FROZEN_FOR_NEW_INPUT")
        else:
            assert g["wrapper_host"] is None
    assert sum(g["wrapper_host"] is not None for g in groups) == r["eligible_groups"] == 269
    byline = defaultdict(list)
    for g in groups:
        byline[g["edition"], g["locus"]].append(g)
    expected_chunks = []
    for (edition, locus), line in sorted(byline.items()):
        line.sort(key=lambda x: x["index"])
        pending = []
        for g in line:
            pending.append(g)
            if g["right_separator"] != "UNCERTAIN_SMALL_SPACE":
                raw = "".join(x["raw"] for x in pending)
                eligible = all(x["wrapper_host"] is not None for x in pending)
                expected_chunks.append((edition, locus, [x["index"] for x in pending],
                                        raw, list(apply_bpe(collapse(raw), merges)) if eligible else None))
                pending = []
        assert not pending
    assert len(expected_chunks) == len(r["chunks"]) == r["hard_chunks"] == 279
    for expected, got in zip(expected_chunks, r["chunks"]):
        ed, locus, indices, raw, units = expected
        assert (got["edition"], got["locus"], got["group_indices"], got["raw_joined"], got["units"]) == expected
        if units is not None:
            assert "".join(units) == collapse(raw) == got["collapsed"]
            assert got["unit_trees"] == [tree(u) for u in units]
        else:
            assert got["collapsed"] is None and got["unit_trees"] is None
    assert sum(x[4] is not None for x in expected_chunks) == r["eligible_chunks"] == 260
    focus = [g for g in groups if g["raw"] in ("okoaiin", "okaiin", "qokaiin", "chokaiin", "okar", "okor", "okol")]
    assert focus == r["focus_occurrences"]
    for form, host, wrapper in [("okoaiin", "oko", "NONE"), ("okaiin", "ok", "NONE"),
                                ("qokaiin", "ok", "q"), ("chokaiin", "ok", "ch")]:
        matches = [g for g in focus if g["raw"] == form and g["locus"].startswith("f89v1")]
        assert len(matches) == 3 and all(g["wrapper_host"]["page_host_before_local_frame"] == host
                                         and g["wrapper_host"]["wrapper"] == wrapper
                                         and g["wrapper_host"]["right_family"] == "aiin" for g in matches)
    result = {"status": "PASS_FORMAL_REPLAY_AND_FULL_PACKET_COVERAGE_ONLY", "raw_groups": 288,
              "hard_chunks": 279, "eligible_groups": 269, "eligible_chunks": 260,
              "semantic_validation": False, "confirmed_words": 0}
    (BASE / "artifacts/VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
