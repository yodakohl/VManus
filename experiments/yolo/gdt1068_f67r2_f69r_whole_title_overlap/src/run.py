#!/usr/bin/env python3
"""GDT1068: literal complete-title transfer, with selector-first source intake."""
import csv
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
EDITIONS = ("ZL3b", "IT2a", "RF1b")
COL = {"ZL3b": "zl3b_clean", "IT2a": "it2a_clean", "RF1b": "rf1b_clean"}
TITLE = ROOT / "experiments/yolo/gdt958_wind_fixed_form_variation/artifacts/FROZEN_TITLE_VARIANTS.tsv"
LINES = "transcription/voynich_cross_transcription_lines.tsv"


def load_target():
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", LINES, "--selector", "page",
           "--allow", "f69r", "--columns", "locus,zl3b_clean,it2a_clean,rf1b_clean"]
    run = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    rows = list(csv.DictReader(io.StringIO(run.stdout), delimiter="\t"))
    assert len(rows) == 49
    assert [r["locus"] for r in rows] == [f"f69r.{i}" for i in range(1, 50)]
    return rows


def load_titles():
    with TITLE.open(newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    out = {}
    for ed in EDITIONS:
        block = [r for r in rows if r["edition"] == ed and r["model"] == "LM_ONLY"]
        vals = {int(r["sector"]): r["raw_title"] for r in block}
        assert sorted(vals) == list(range(1, 13))
        assert all(len({r["raw_title"] for r in block if int(r["sector"]) == n}) == 1 for n in vals)
        out[ed] = vals
    return out


def contains(title, item):
    a, b = title.split(), item.split()
    return any(b[i:i + len(a)] == a for i in range(len(b) - len(a) + 1))


def main():
    titles, target = load_titles(), load_target()
    result = {"experiment_id": "GDT1068", "source_loci": [r["locus"] for r in target], "readings": {}}
    for ed in EDITIONS:
        data = {}
        for register, lo, hi in (("outer", 5, 20), ("radial", 21, 42)):
            items = [(r["locus"], r[COL[ed]]) for r in target
                     if lo <= int(r["locus"].split(".")[1]) <= hi]
            matches, shared = [], []
            for sector, title in sorted(titles[ed].items()):
                for locus, phrase in items:
                    if contains(title, phrase):
                        matches.append({"sector": sector, "title": title, "locus": locus, "item": phrase})
                    for token in title.split():
                        if token in phrase.split():
                            shared.append({"sector": sector, "token": token, "locus": locus})
            data[register] = {"items": len(items), "title_item_cells": len(items) * 12,
                              "complete_matches": matches, "constituent_overlaps": shared}
        result["readings"][ed] = data
    (HERE / "artifacts/RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({ed: {reg: {"complete": len(result["readings"][ed][reg]["complete_matches"]),
                                  "overlaps": len(result["readings"][ed][reg]["constituent_overlaps"])}
                            for reg in ("outer", "radial")} for ed in EDITIONS}))


if __name__ == "__main__":
    main()
