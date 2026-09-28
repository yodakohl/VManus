#!/usr/bin/env python3
"""Independent direct scan of the fixed GDT1068 source and output."""
import csv
import io
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parents[1]
NAMES = (("ZL3b", "zl3b_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean"))


def main():
    saved = json.loads((HERE / "artifacts/RESULT.json").read_text())
    with (ROOT / "experiments/yolo/gdt958_wind_fixed_form_variation/artifacts/FROZEN_TITLE_VARIANTS.tsv").open(newline="") as f:
        source = list(csv.DictReader(f, delimiter="\t"))
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", "transcription/voynich_cross_transcription_lines.tsv",
           "--selector", "page", "--allow", "f69r", "--columns", "locus,zl3b_clean,it2a_clean,rf1b_clean"]
    rows = list(csv.DictReader(io.StringIO(subprocess.run(cmd, cwd=ROOT, capture_output=True,
                                                          text=True, check=True).stdout), delimiter="\t"))
    assert len(rows) == 49
    checks = 0
    for edition, col in NAMES:
        title = {int(r["sector"]): r["raw_title"].split() for r in source
                 if r["edition"] == edition and r["model"] == "LM_ONLY"}
        assert len(title) == 12
        for reg, slc in (("outer", rows[4:20]), ("radial", rows[20:42])):
            got = saved["readings"][edition][reg]
            assert got["items"] == len(slc)
            assert got["title_item_cells"] == 12 * len(slc)
            expected_full, expected_parts = [], []
            for sector in range(1, 13):
                for row in slc:
                    phrase = row[col].split()
                    if any(phrase[j:j + len(title[sector])] == title[sector]
                           for j in range(max(0, len(phrase) - len(title[sector]) + 1))):
                        expected_full.append((sector, row["locus"]))
                    expected_parts.extend((sector, word, row["locus"]) for word in title[sector]
                                          if word in phrase)
                    checks += 1
            assert expected_full == [(m["sector"], m["locus"]) for m in got["complete_matches"]]
            assert expected_parts == [(m["sector"], m["token"], m["locus"])
                                      for m in got["constituent_overlaps"]]
    report = {"experiment_id": "GDT1068", "status": "PASS", "checked_title_item_cells": checks,
              "source_loci": len(rows)}
    (HERE / "artifacts/VALIDATION.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
