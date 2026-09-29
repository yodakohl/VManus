"""Acquire declared complete contexts after the idea freeze; no semantic parser."""
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


def main():
    boundary_path = HERE / "W_OKO_BOUNDARIES.json"
    boundary = json.loads(boundary_path.read_text())
    source_path = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == boundary["source_sha256"]
    freeze_path = HERE / "W_FIRST_FREEZE.json"
    freeze = json.loads(freeze_path.read_text())
    proposal = ROOT / freeze["proposal"]
    assert hashlib.sha256(proposal.read_bytes()).hexdigest() == freeze["sha256"]
    loci = sorted({x for b in boundary["units"] for x in b["loci"]})
    assert len(loci) == 27 and all(not x.startswith("f84") for x in loci)
    columns = ["source_group_id", "edition", "page", "locus", "source_group_index",
               "source_group_count", "paragraph_start", "paragraph_end", "left_separator",
               "right_separator", "ivtff_group_raw"]
    cmd = ["./vmanus-exp", "query-tsv", "experiments/semantic_assumptions/results/source_separator_transcription.tsv", "--selector", "locus"]
    for locus in loci:
        cmd.extend(["--allow", locus])
    cmd.extend(["--columns", ",".join(columns)])
    output = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=True)
    assert hashlib.sha256(source_path.read_bytes()).hexdigest() == boundary["source_sha256"]
    rows = list(csv.DictReader(io.StringIO(output.stdout), delimiter="\t"))
    assert set(rows[0]) == set(columns) and {r["locus"] for r in rows} == set(loci)
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r["edition"], r["locus"])].append(r)
    for values in grouped.values():
        values.sort(key=lambda r: int(r["source_group_index"]))
        assert [int(r["source_group_index"]) for r in values] == list(range(1, int(values[0]["source_group_count"]) + 1))
    expected_ids = {r["source_group_id"] for r in json.loads((HERE / "W_OKO_LOCATORS.json").read_text())["rows"]}
    assert {r["source_group_id"] for r in rows if r["ivtff_group_raw"] == "oko"} == expected_ids
    ring_path = HERE.parent / "F68R_PAIRED_OPENINGS_SOURCE_20260927.json"
    ring_packet = json.loads(ring_path.read_text())
    ring_rows = next(q["rows"] for q in ring_packet["queries"] if q["id"] == "groups")
    comparison_rows = defaultdict(list)
    for r in ring_rows:
        comparison_rows[("ring", r["edition"], r["locus"])].append(r)
    prose_path = HERE.parent / "F89V1_OKOAIIN_CONTEXT_SOURCE_20260927.json"
    prose = json.loads(prose_path.read_text())
    for r in prose["query"]["rows"]:
        comparison_rows[("f89", r["edition"], r["locus"])].append(r)
    for values in comparison_rows.values():
        values.sort(key=lambda r: int(r["source_group_index"]))
    matches = []
    # Every contiguous match containing exact bare oko, length >=2.
    # Cross-reading comparisons are displayed, never pooled as independent.
    for (ed, locus), target in grouped.items():
        literal = [r["ivtff_group_raw"] for r in target]
        for anchor in [i for i, s in enumerate(literal) if s == "oko"]:
            for (kind, old_ed, old_locus), old in comparison_rows.items():
                old_literal = [r["ivtff_group_raw"] for r in old]
                for left in range(anchor + 1):
                    for right in range(anchor + 1, len(target) + 1):
                        length = right - left
                        if length < 2:
                            continue
                        fragment = literal[left:right]
                        for old_left in range(len(old) - length + 1):
                            if old_literal[old_left:old_left + length] != fragment:
                                continue
                            segment = target[left:right]
                            old_segment = old[old_left:old_left + length]
                            def gaps(x):
                                return all(a["right_separator"] == b["left_separator"] == "DEFINITE_SPACE" for a, b in zip(x, x[1:]))
                            matches.append({"outside_reader": ed, "outside_locus": locus,
                                            "outside_start": left + 1, "outside_end": right,
                                            "comparison_kind": kind, "comparison_reader": old_ed,
                                            "comparison_locus": old_locus, "comparison_start": old_left + 1,
                                            "same_reader": ed == old_ed, "groups": fragment,
                                            "definite_both": gaps(segment) and gaps(old_segment)})
    units = []
    md = ["# All declared bare-oko outside contexts", "", "All groups and reader differences are retained. Pipe marks are editorial group separators; original boundary flags are in the TSV. RF windows borrow corresponding ZL/IT scope. No translation is asserted.", ""]
    for b in boundary["units"]:
        selected = [r for locus in b["loci"] for r in grouped[(b["edition"], locus)]]
        unit = dict(b, group_count=len(selected), exact_oko=sum(r["ivtff_group_raw"] == "oko" for r in selected))
        units.append(unit)
        md.append(f"## {b['edition']} {b['loci'][0]}–{b['loci'][-1]} ({b['scope']}; {len(selected)} groups)")
        md.append("")
        for locus in b["loci"]:
            md.append(locus + " `" + " | ".join(r["ivtff_group_raw"] for r in grouped[(b["edition"], locus)]) + "`")
            md.append("")
    report = {"status": "COMPLETE_SOURCE_PACKET_NOT_MEANING_TEST", "opened_utc": datetime.now(timezone.utc).isoformat(),
              "freeze": freeze, "command": cmd, "guard": output.stderr.strip(), "rows": len(rows),
              "units": units, "all_matches_containing_bare_oko_length_at_least_two": matches,
              "inputs": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (boundary_path, freeze_path, proposal, ring_path, prose_path)},
              "source_sha256": boundary["source_sha256"],
              "source_tsv_sha256": hashlib.sha256(output.stdout.encode()).hexdigest(),
              "confirmed_meanings": 0, "independent_confirmation_leaves": 0}
    (HERE / "W_OKO_CONTEXT.tsv").write_text(output.stdout)
    (HERE / "W_OKO_CONTEXT.md").write_text("\n".join(md) + "\n")
    (HERE / "W_OKO_CONTEXT.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "rows": len(rows), "guard": report["guard"],
                      "units": [{"reader": b["edition"], "first": b["loci"][0], "last": b["loci"][-1], "groups": b["group_count"], "oko": b["exact_oko"]} for b in units],
                      "matches": matches}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
