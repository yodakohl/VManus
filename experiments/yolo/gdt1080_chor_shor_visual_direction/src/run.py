#!/usr/bin/env python3
"""Frozen exact-word visual contrast for GDT1080; no raw mixed TSV access."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
PANEL = ROOT / "experiments/yolo/gdt364_reproductive_structure_joint_atlas/artifacts/gdt364_panel.tsv"
CACHE = ROOT / "experiments/semantic_assumptions/cache/word_profiles.sqlite"
OUT = HERE / "artifacts"
PANEL_SHA = "76b51f8bf05459e8d86650e14810b7b6e5775e0c8906c091efcd2bb61db24235"
ALLOW_SHA = "f0def5a04bd91443cf4770c78f1b67e62cac2060627d8de38faba27899188483"
SOURCE_SHA = "4b649c8290d5afc7a5fbcc8e98db2bc123a1ceb5f3858d3befa781ce96b680f0"
READERS = ("ZL3b", "IT2a", "RF1b")
STATES = ("FLOWER_SIDE", "BERRY_NO_CIRCLES", "NO_FRUIT_OR_FLOWER")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair_or(f: Counter, b: Counter) -> float:
    return (f["chor"] + 0.5) * (b["shor"] + 0.5) / ((f["shor"] + 0.5) * (b["chor"] + 0.5))


def main() -> None:
    assert digest(PANEL) == PANEL_SHA
    with PANEL.open(newline="", encoding="utf-8") as fh:
        panel = list(csv.DictReader(fh, delimiter="\t"))
    assert len(panel) == 34 and len({r["page"] for r in panel}) == 34
    assert all(not r["page"].startswith("f84") for r in panel)
    cx = sqlite3.connect(CACHE)
    receipt = json.loads(cx.execute("select value from metadata where key='receipt'").fetchone()[0])
    assert receipt["inputs"]["allowlist_sha256"] == ALLOW_SHA
    assert receipt["inputs"]["source_sha256"] == SOURCE_SHA
    admitted = set(receipt["inputs"]["selectors"])
    assert len(admitted) == 179 and all(not p.startswith("f84") for p in admitted)
    excluded = [p["page"] for p in panel if p["page"] not in admitted]
    assert excluded == ["f54r", "f90v2"], excluded
    used = [p for p in panel if p["page"] in admitted]
    assert len(used) == 32
    page_map = {r["page"]: r for r in used}
    counts = defaultdict(Counter)
    sql = "select edition,page,ivtff_group_raw from groups where kind='P' and page in ({})".format(
        ",".join("?" for _ in used)
    )
    for edition, page, raw in cx.execute(sql, tuple(page_map)):
        assert not page.startswith("f84")
        if edition not in READERS:
            continue
        counts[(edition, page)]["groups"] += 1
        if raw in ("chor", "shor"):
            counts[(edition, page)][raw] += 1
    OUT.mkdir(exist_ok=True)
    rows = []
    for edition in READERS:
        for p in used:
            c = counts[(edition, p["page"])]
            rows.append({"reader": edition, "page": p["page"], "folio": p["physical_folio"],
                         "quire": p["quire"], "state": p["visual_state"],
                         "groups": c["groups"], "chor": c["chor"], "shor": c["shor"]})
    with (OUT / "PAGE_COUNTS.tsv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, delimiter="\t", lineterminator="\n", fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    aggregates = []
    pair_rows = []
    decision = {}
    for edition in READERS:
        sums = {}
        for state in STATES:
            rs = [r for r in rows if r["reader"] == edition and r["state"] == state]
            c = Counter()
            for r in rs:
                for k in ("groups", "chor", "shor"):
                    c[k] += r[k]
            sums[state] = c
            aggregates.append({"reader": edition, "state": state, "pages": len(rs),
                               "groups": c["groups"], "chor": c["chor"], "shor": c["shor"],
                               "chor_per_1000": 1000*c["chor"]/c["groups"],
                               "shor_per_1000": 1000*c["shor"]/c["groups"],
                               "chor_shor_ratio_corrected": (c["chor"]+0.5)/(c["shor"]+0.5)})
        overall = pair_or(sums["FLOWER_SIDE"], sums["BERRY_NO_CIRCLES"])
        pair_logsum = 0.0
        for folio, flower, berry in (("f4", "f4v", "f4r"), ("f17", "f17r", "f17v")):
            fc = counts[(edition, flower)]; bc = counts[(edition, berry)]
            odd = pair_or(fc, bc)
            pair_logsum += math.log(odd)
            pair_rows.append({"reader": edition, "folio": folio, "flower_page": flower,
                              "berry_page": berry, "flower_chor": fc["chor"],
                              "flower_shor": fc["shor"], "berry_chor": bc["chor"],
                              "berry_shor": bc["shor"], "cross_class_or": odd})
        decision[edition] = {"cross_class_or": overall, "pair_log_or_sum": pair_logsum,
                             "counts_F": dict(sums["FLOWER_SIDE"]),
                             "counts_B": dict(sums["BERRY_NO_CIRCLES"])}
    primary = decision["ZL3b"]
    cap = all(primary[k][w] >= 3 for k in ("counts_F", "counts_B") for w in ("chor", "shor"))
    direction = 1 if primary["cross_class_or"] >= 2 else (-1 if primary["cross_class_or"] <= 0.5 else 0)
    observed_positive = primary["cross_class_or"] > 1
    same_readers = all((decision[r]["cross_class_or"] > 1) == observed_positive
                       for r in READERS[1:])
    same_pairs = (primary["pair_log_or_sum"] > 0) == observed_positive
    preferred = "chor=flower" if cap and same_readers and same_pairs and direction == 1 else (
        "shor=flower" if cap and same_readers and same_pairs and direction == -1 else "TIED")
    payload = {"panel_sha256": PANEL_SHA, "cache_sha256": digest(CACHE),
               "excluded_panel_pages": excluded, "n_pages": len(used),
               "aggregates": aggregates, "pairs": pair_rows, "readers": decision,
               "gates": {"capacity": cap, "magnitude": direction != 0,
                         "other_readers_same_sign": same_readers,
                         "paired_folios_same_sign": same_pairs},
               "working_preference": preferred,
               "claim_ceiling": "postexposure C0 page association only; no lexical confirmation"}
    (OUT / "RESULT.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"pages": len(used), "excluded": excluded, "preference": preferred,
                      "gates": payload["gates"], "or": primary["cross_class_or"]}))


if __name__ == "__main__":
    main()
