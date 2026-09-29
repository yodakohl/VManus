"""Acquire only metadata; retain whole native ZL/IT units and RF spatial unions."""
import csv
import hashlib
import io
import json
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = "experiments/semantic_assumptions/results/source_separator_transcription.tsv"


def main():
    locators = json.loads((HERE / "W_OKO_LOCATORS.json").read_text())
    pages = sorted({r["page"] for r in locators["rows"]})
    columns = ["edition", "page", "locus", "kind", "source_row_index", "source_group_index",
               "source_group_count", "paragraph_start", "paragraph_end"]
    cmd = ["./vmanus-exp", "query-tsv", SOURCE, "--selector", "page"]
    for page in pages:
        assert not page.startswith("f84")
        cmd.extend(["--allow", page])
    cmd.extend(["--columns", ",".join(columns)])
    run = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    rows = list(csv.DictReader(io.StringIO(run.stdout), delimiter="\t"))
    assert set(rows[0]) == set(columns)
    assert {r["page"] for r in rows} <= set(pages)
    lines = {}
    for row in rows:
        if row["kind"] == "P" and row["source_group_index"] == "1":
            key = (row["edition"], row["page"], row["locus"])
            assert key not in lines
            lines[key] = row
    blocks = []
    for reader in ("ZL3b", "IT2a"):
        for page in pages:
            ordered = sorted((r for (ed, pg, _), r in lines.items() if ed == reader and pg == page),
                             key=lambda r: int(r["source_row_index"]))
            active = []
            for row in ordered:
                if row["paragraph_start"] == "1" and active:
                    blocks.append({"edition": reader, "page": page, "lines": active,
                                   "start_marked": active[0]["paragraph_start"] == "1", "end_marked": False})
                    active = []
                active.append(row)
                if row["paragraph_end"] == "1":
                    blocks.append({"edition": reader, "page": page, "lines": active,
                                   "start_marked": active[0]["paragraph_start"] == "1", "end_marked": True})
                    active = []
            if active:
                blocks.append({"edition": reader, "page": page, "lines": active,
                               "start_marked": active[0]["paragraph_start"] == "1", "end_marked": False})
    anchor_loci = {(r["page"], r["locus"]) for r in locators["rows"]}
    selected = []
    for block in blocks:
        anchors = sorted(locus for page, locus in anchor_loci
                         if page == block["page"] and locus in {r["locus"] for r in block["lines"]})
        if anchors:
            selected.append({"edition": block["edition"], "page": block["page"],
                             "anchor_loci": anchors, "loci": [r["locus"] for r in block["lines"]],
                             "start_marked": block["start_marked"], "end_marked": block["end_marked"],
                             "scope": "own marked paragraph" if block["start_marked"] and block["end_marked"] else "metadata-bounded fragment"})
    for reader in ("ZL3b", "IT2a"):
        assert {x for b in selected if b["edition"] == reader for x in b["anchor_loci"]} == {x[1] for x in anchor_loci}
    # No paragraph claims for RF. Same named physical-line union, never inferred
    # from its lack of markers; missing corresponding lines are disclosed.
    for page in pages:
        loci = {x for b in selected if b["page"] == page for x in b["loci"]}
        rf = sorted((r for (ed, pg, _), r in lines.items() if ed == "RF1b" and pg == page and r["locus"] in loci),
                    key=lambda r: int(r["source_row_index"]))
        assert all(r["paragraph_start"] == r["paragraph_end"] == "0" for r in rf)
        selected.append({"edition": "RF1b", "page": page,
                         "anchor_loci": sorted(locus for pg, locus in anchor_loci if pg == page),
                         "loci": [r["locus"] for r in rf], "start_marked": False, "end_marked": False,
                         "scope": "union of corresponding ZL/IT named lines; not an RF paragraph",
                         "missing_corresponding_loci": sorted(loci - {r["locus"] for r in rf})})
    result = {"status": "METADATA_ONLY_CONTENT_UNOPENED", "queried_utc": datetime.now(timezone.utc).isoformat(),
              "command": cmd, "guard": run.stderr.strip(), "metadata_rows": len(rows),
              "source_sha256": hashlib.sha256((ROOT / SOURCE).read_bytes()).hexdigest(),
              "metadata_sha256": hashlib.sha256(run.stdout.encode()).hexdigest(), "units": selected}
    (HERE / "W_OKO_BOUNDARY_METADATA.tsv").write_text(run.stdout)
    (HERE / "W_OKO_BOUNDARIES.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": result["status"], "guard": result["guard"],
                      "units": [{k: v for k, v in b.items() if k != "loci"} | {"first": b["loci"][0], "last": b["loci"][-1], "line_count": len(b["loci"])}
                                for b in selected]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
