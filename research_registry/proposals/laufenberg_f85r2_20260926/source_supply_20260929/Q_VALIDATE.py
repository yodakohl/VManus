#!/usr/bin/env python3
"""Check Q documentary preservation only; no semantic execution or target search."""
import csv
import hashlib
import io
import json
from pathlib import Path
import subprocess
from collections import Counter


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    base = Path(__file__).parent
    receipt = json.loads((base / "Q_INPUT_RECEIPTS.json").read_text())
    for path, expected in receipt["primary_hashes"].items():
        assert sha(path) == expected, path
    for item in receipt["queries"]:
        assert sha(item["path"]) == item["sha256"], item["path"]

    with (base / "Q_COMPLETE_UNITS.tsv").open() as stream:
        units = list(csv.DictReader(stream, delimiter="\t"))
    actual = {}
    counts = Counter()
    for row in units:
        groups = json.loads(row["groups_json"])
        assert len(groups) == int(row["group_count"])
        key = (row["idea"], row["edition"], row["locus"])
        assert key not in actual
        actual[key] = groups
        counts[f'{row["idea"]}/{row["edition"]}'] += len(groups)
    assert dict(counts) == receipt["complete_group_counts"]

    expected = {}
    for item in receipt["queries"]:
        if "argv" not in item:
            continue
        run = subprocess.run(item["argv"], text=True, capture_output=True, check=True)
        rows = list(csv.DictReader(io.StringIO(run.stdout), delimiter="\t"))
        assert len(rows) == item["selected_rows"]
        for row in rows:
            if "eva_clean" in row:
                for edition, column in (("ZL3b", "eva_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean")):
                    expected[("IDEA000766", edition, row["locus"])] = row[column].split()
            else:
                idea = "IDEA000765" if "raw_group" in row else "IDEA000767"
                word = row["raw_group"] if "raw_group" in row else row["ivtff_group_raw"]
                expected.setdefault((idea, row["edition"], row["locus"]), []).append(word)
    assert actual == expected
    assert actual[("IDEA000766", "IT2a", "f29v.2")][:3] == ["qotcheaiin", "schol", "chol"]
    for edition in ("ZL3b", "RF1b"):
        assert actual[("IDEA000766", edition, "f29v.2")][:4] == ["qotcheaiin", "s", "chol", "chol"]
    for edition in ("ZL3b", "IT2a", "RF1b"):
        assert actual[("IDEA000766", edition, "f29v.3")][:2] == ["chol", "chol"]
        assert actual[("IDEA000767", edition, "f105v.5")][:5] == ["pchedal", "qopchdy", "daiin", "chedy", "daiin"]
    assert actual[("IDEA000765", "RF1b", "f89v1.14")][4:8] == ["okol", "cho@152;y", "okoaiin", "dal"]

    report = " ".join((base / "Q_COMPARE_AND_CONSTRUCTION.md").read_text().split())
    for claim in ("No candidate currently supplies a complete meaning account",
                  "does not imply transitivity", "The differing\nreader is IT",
                  "GDT1053 explicitly downgrades", "All eight upper-ring groups remain unread"):
        assert " ".join(claim.split()) in report, claim
    result = {
        "status": "PASS_DOCUMENTARY_PRESERVATION_ONLY",
        "whole_line_records": len(units),
        "reader_group_positions": sum(counts.values()),
        "counts": dict(counts),
        "exact_guarded_source_replay": True,
        "reader_correction": "IDEA766 first doublet differs in IT, not RF",
        "new_raw_cards": 0,
        "semantic_test": "none",
        "complete_reading_selected": False,
        "files": {path.name: {"sha256": sha(path), "bytes": path.stat().st_size}
                  for path in sorted(base.glob("Q_*"))
                  if path.is_file() and path.name != "Q_INTEGRITY_RECEIPT.json"},
    }
    (base / "Q_INTEGRITY_RECEIPT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "files"}, indent=2))


if __name__ == "__main__":
    main()
