#!/usr/bin/env python3
"""Replay unchanged formal transforms on saved local source packets."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
BASE = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "research_registry/proposals/laufenberg_f85r2_20260926"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/yolo/gdt605_multisymbol_unit_alphabet/src"))
from run_gdt012_core_semantic_atlas import strip_layers
from run_gdt062_right_family_register_renderer import preparse
from separator_crossing import apply_bpe, collapse

RING = "F68R_PAIRED_OPENINGS_SOURCE_20260927.json"
PROSE = "F89V1_OKOAIIN_CONTEXT_SOURCE_20260927.json"
MERGES = ROOT / "experiments/yolo/gdt605_multisymbol_unit_alphabet/artifacts/gdt605_bpe_merges.tsv"
TARGETS = ("okoaiin", "okaiin", "qokaiin", "chokaiin", "okar", "okor", "okol")
PURE = re.compile(r"[a-z]+\Z")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name: str):
    return json.loads((DOSSIER / name).read_text())


def load_merges():
    with MERGES.open(newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    assert len(rows) == 64 and [int(r["rank"]) for r in rows] == list(range(1, 65))
    return [(r["left"], r["right"], r["merged"], int(r["train_occurrences"])) for r in rows]


def merge_trees(merges):
    children = {merged: (left, right) for left, right, merged, _ in merges}
    assert len(children) == len(merges)
    def tree(unit):
        if unit not in children:
            return unit
        left, right = children[unit]
        return [tree(left), tree(right)]
    return tree


def group_rows():
    ring, prose = read(RING), read(PROSE)
    assert ring["scope"] == ["f68r2.6", "f68r2.31"]
    assert prose["registered_scope"] == [f"f89v1.{x}" for x in range(13, 21)]
    ring_query = next(q for q in ring["queries"] if q["command"][-1] ==
                      "edition,locus,source_group_index,left_separator,right_separator,ivtff_group_raw")
    output = [("ring", r) for r in ring_query["rows"]]
    output += [("paragraph", r) for r in prose["query"]["rows"]]
    assert len(output) == 288
    for r in ring["groups"]:
        got = [row["ivtff_group_raw"] for part, row in output
               if part == "ring" and row["edition"] == r["edition"] and row["locus"] == r["locus"]]
        assert got == r["groups"]
    for u in prose["units"]:
        got = [row["ivtff_group_raw"] for part, row in output
               if part == "paragraph" and row["edition"] == u["edition"] and row["locus"] == u["locus"]]
        assert got == u["groups"]
    return output


def parse_group(part, row):
    raw = row["ivtff_group_raw"]
    result = dict(part=part, edition=row["edition"], locus=row["locus"],
                  index=int(row["source_group_index"]), raw=raw,
                  left_separator=row["left_separator"], right_separator=row["right_separator"])
    if not PURE.fullmatch(raw):
        result["parse_status"] = "MARKED_OR_NONLOWERCASE_UNRESOLVED"
        result["wrapper_host"] = None
        return result
    prefix, residual, dy = strip_layers(raw)
    host, b3, right, inner = preparse({"residual_host": residual,
                                      "stripped_prefix": prefix})
    result["parse_status"] = "PURE_FUNCTION_REPLAY"
    result["wrapper_host"] = dict(wrapper=prefix, residual_host=residual,
                                  dy_closure=dy, page_host_before_local_frame=host,
                                  b3=b3, right_family=right, inner_d=inner,
                                  local_frame="NOT_FROZEN_FOR_NEW_INPUT")
    return result


def make_chunks(groups, merges):
    byline = defaultdict(list)
    tree = merge_trees(merges)
    for group in groups:
        byline[group["edition"], group["locus"]].append(group)
    out = []
    for (edition, locus), line in sorted(byline.items()):
        line.sort(key=lambda x: x["index"])
        assert [x["index"] for x in line] == list(range(1, len(line) + 1))
        pending = []
        def emit():
            raw = "".join(x["raw"] for x in pending)
            eligible = all(x["parse_status"] == "PURE_FUNCTION_REPLAY" for x in pending)
            units = list(apply_bpe(collapse(raw), merges)) if eligible else None
            if units is not None:
                assert "".join(units) == collapse(raw)
            out.append(dict(edition=edition, locus=locus,
                            group_indices=[x["index"] for x in pending],
                            raw_joined=raw, collapsed=collapse(raw) if eligible else None,
                            units=units, unit_trees=[tree(u) for u in units] if units is not None else None,
                            status="REPLAY" if eligible else "UNRESOLVED_MARKED_GROUP"))
        for group in line:
            pending.append(group)
            if group["right_separator"] != "UNCERTAIN_SMALL_SPACE":
                emit(); pending = []
        assert not pending
    return out


def main():
    merges = load_merges()
    groups = [parse_group(part, row) for part, row in group_rows()]
    chunks = make_chunks(groups, merges)
    focus = [g for g in groups if g["raw"] in TARGETS]
    output = dict(schema="gdt1051-local-frozen-grammar-v1", status="FORMAL_REPLAY_ONLY",
                  input_hashes={RING: sha(DOSSIER / RING), PROSE: sha(DOSSIER / PROSE),
                                str(MERGES.relative_to(ROOT)): sha(MERGES),
                                "run_gdt012_core_semantic_atlas.py": sha(ROOT / "run_gdt012_core_semantic_atlas.py"),
                                "run_gdt062_right_family_register_renderer.py": sha(ROOT / "run_gdt062_right_family_register_renderer.py"),
                                "experiments/yolo/gdt605_multisymbol_unit_alphabet/src/separator_crossing.py":
                                sha(ROOT / "experiments/yolo/gdt605_multisymbol_unit_alphabet/src/separator_crossing.py")},
                  raw_groups=len(groups), eligible_groups=sum(g["wrapper_host"] is not None for g in groups),
                  hard_chunks=len(chunks), eligible_chunks=sum(c["units"] is not None for c in chunks),
                  groups=groups, chunks=chunks, focus_occurrences=focus,
                  confirmed_words=0, semantic_validation=False,
                  sealed_data={"f84": "FORBIDDEN_AND_ABSENT", "f84r": "FORBIDDEN_AND_ABSENT"})
    path = BASE / "artifacts/RESULT.json"
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: output[k] for k in ("raw_groups", "eligible_groups", "hard_chunks", "eligible_chunks", "status")}, indent=2))


if __name__ == "__main__":
    main()
