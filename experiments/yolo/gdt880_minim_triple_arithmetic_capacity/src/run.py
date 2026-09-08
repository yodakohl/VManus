#!/usr/bin/env python3
"""Build the guarded, arithmetic-free GDT880 adjacent-triple inventory."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXP = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "AGENTS.md").is_file() and (p / ".git").exists())
ART = EXP / "artifacts"
SPEC_PATH = HERE / "SPEC.json"
PREREG = EXP / "PREREGISTRATION.md"
PREREG_SHA256 = "39a29a975d6944d8a0a5fd6f3c855dd38bae6415792ec03770d621c9fb75e0e5"
SPEC_SHA256 = "51fe285cc6b83b154be386b09018e10ce377993fa03fb41773a5d0803ae99842"
READINGS = ("ZL3b", "IT2a", "RF1b")
FIELDS = ("source_group_id", "edition", "locus", "page", "kind", "source_group_index",
          "source_group_count", "ivtff_group_raw", "clean_ascii_fragments",
          "clean_ascii_fragment_count", "left_separator", "right_separator")
WHOLE = re.compile(r"^([a-z]+)a(i{0,3})n$")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def query(spec: dict, selectors: list[str]) -> tuple[list[dict[str, str]], dict, bytes]:
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", spec["source"], "--selector", "page"]
    for page in selectors:
        cmd += ["--allow", page]
    cmd += ["--columns", ",".join(FIELDS), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, check=False,
                          env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    if proc.returncode:
        raise RuntimeError(proc.stderr.decode(errors="replace"))
    guard = [line for line in proc.stderr.decode().splitlines() if line.startswith("GUARD_STATS ")]
    if len(guard) != 1:
        raise RuntimeError("missing unique GUARD_STATS receipt")
    stats = json.loads(guard[0][12:])
    reader = csv.DictReader(io.StringIO(proc.stdout.decode()), delimiter="\t")
    if reader.fieldnames != list(FIELDS):
        raise RuntimeError("guarded projection columns differ from SPEC")
    rows = list(reader)
    if len(rows) != stats["selected"] or any(row.get("page", "").startswith("f84") for row in rows):
        raise RuntimeError("guard row count/sealed scope mismatch")
    return rows, {"command": cmd, "projection_sha256": digest(proc.stdout), "stats": stats}, proc.stdout


def numeric(row: dict[str, str], field: str) -> int:
    value = row.get(field, "")
    if not value.isdigit():
        raise ValueError(f"non-numeric {field}: {value!r}")
    return int(value)


def physical_leaf(page: str) -> str:
    match = re.match(r"f\d+", page)
    if not match:
        raise ValueError(f"bad selector: {page}")
    return match.group(0)


def eligible(row: dict[str, str]) -> tuple[str, int] | None:
    if row.get("kind") != "P":
        return None
    raw = row.get("ivtff_group_raw", "")
    if raw != row.get("clean_ascii_fragments", "") or row.get("clean_ascii_fragment_count") != "1":
        return None
    match = WHOLE.fullmatch(raw)
    if match is None:
        return None
    return match.group(1), len(match.group(2))


def grouped(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], list[dict[str, str]]]:
    out: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        out[(row["page"], row["locus"], row["edition"])].append(row)
    for values in out.values():
        values.sort(key=lambda row: (numeric(row, "source_group_index"),
                                     numeric(row, "source_row_index") if row.get("source_row_index", "").isdigit() else 0))
    return out


def windows(rows: list[dict[str, str]]) -> list[dict]:
    """Find windows without filtering invalid/interstitial rows first."""
    found = []
    for start in range(max(0, len(rows) - 2)):
        triple = rows[start:start + 3]
        parsed = [eligible(row) for row in triple]
        if len(triple) != 3 or any(item is None for item in parsed):
            continue
        heads = [item[0] for item in parsed]
        indices = [numeric(row, "source_group_index") for row in triple]
        counts = [numeric(row, "source_group_count") for row in triple]
        if (len(set(heads)) != 1 or indices != list(range(indices[0], indices[0] + 3)) or
                len(set(counts)) != 1 or any(index < 0 or index >= count for index, count in zip(indices, counts)) or
                triple[0].get("right_separator") != "DEFINITE_SPACE" or triple[1].get("left_separator") != "DEFINITE_SPACE" or
                triple[1].get("right_separator") != "DEFINITE_SPACE" or triple[2].get("left_separator") != "DEFINITE_SPACE"):
            continue
        found.append({
            "raw_groups": [row["ivtff_group_raw"] for row in triple],
            "minim_runs": [item[1] for item in parsed],
            "head": heads[0],
            "zl_indices": indices,
        })
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="query and validate without writing artifacts")
    args = parser.parse_args()
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    if spec["experiment_id"] != "GDT880" or spec["editions"] != list(READINGS) or spec["kind"] != "P":
        raise RuntimeError("SPEC identity differs")
    if spec["sealed_data"] != {"f84": "FORBIDDEN", "f84r": "FORBIDDEN"}:
        raise RuntimeError("sealed scope differs")
    if digest(PREREG.read_bytes()) != PREREG_SHA256:
        raise RuntimeError("frozen preregistration hash mismatch")
    if digest(SPEC_PATH.read_bytes()) != SPEC_SHA256:
        raise RuntimeError("frozen SPEC hash mismatch")
    selectors = list(spec["selectors"])
    if len(selectors) != 163 or len(selectors) != len(set(selectors)):
        raise RuntimeError("expected 163 unique selectors")
    excluded = set(spec["excluded_physical_leaves"])
    selectors = [page for page in selectors if physical_leaf(page) not in excluded]
    if len(selectors) != 163 or any(page.startswith("f84") for page in selectors):
        raise RuntimeError("selector exclusion/seal mismatch")

    rows, receipt, projection_bytes = query(spec, sorted(selectors))
    by_group = grouped(rows)
    windows_by_key = {key: windows(values) for key, values in by_group.items()}
    zl_windows = []
    loci = sorted({(page, locus) for page, locus, edition in windows_by_key if edition == "ZL3b"})
    for page, locus in loci:
        zls = windows_by_key[(page, locus, "ZL3b")]
        for window in zls:
            joins = {}
            for edition in READINGS:
                matches = [candidate for candidate in windows_by_key.get((page, locus, edition), [])
                           if candidate["raw_groups"] == window["raw_groups"]]
                joins[edition] = {"match_count": len(matches), "indices": [item["zl_indices"] for item in matches]}
            zl_windows.append({"page": page, "locus": locus, **window, "joins": joins,
                               "consensus": all(joins[edition]["match_count"] == 1 for edition in READINGS)})

    candidate_loci = {(row["page"], row["locus"]) for row in zl_windows}
    source_rows = [row for row in rows if (row["page"], row["locus"]) in candidate_loci]
    consensus = [row for row in zl_windows if row["consensus"]]
    lines = len({(x["page"], x["locus"]) for x in consensus})
    leaves = len({physical_leaf(x["page"]) for x in consensus})
    heads = len({x["head"] for x in consensus})
    result = {
        "experiment_id": "GDT880",
        "status": "DESIGN_REVIEW_CAPACITY_ONLY" if lines >= 20 and leaves >= 5 and heads >= 2 else "STOP_INSUFFICIENT_IMMEDIATE_TRIPLE_CAPACITY",
        "zl_candidate_windows": len(zl_windows), "consensus_windows": len(consensus),
        "consensus_lines": lines, "physical_leaves": leaves, "heads": heads,
        "triage_thresholds": {"lines": 20, "physical_leaves": 5, "heads": 2},
        "claim_ceiling": spec["claim_ceiling"],
    }
    if args.check:
        print(json.dumps({"status": "CHECK_ONLY", "rows": len(rows), "source_rows": len(source_rows), "result": result}, ensure_ascii=False))
        return 0
    ART.mkdir(parents=True, exist_ok=True)
    runtime = EXP / "runtime"
    runtime.mkdir(parents=True, exist_ok=True)
    (runtime / "SOURCE_PROJECTION.tsv").write_bytes(projection_bytes)
    (ART / "SOURCE_ROWS.json").write_text(json.dumps(source_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ART / "SOURCE_RECEIPT.json").write_text(json.dumps({
        "source": spec["source"], "projection_sha256": receipt["projection_sha256"],
        "guard_stats": receipt["stats"], "retained_rows": len(source_rows),
        "preregistration_sha256": PREREG_SHA256, "spec_sha256": SPEC_SHA256
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ART / "CANDIDATES.json").write_text(json.dumps(zl_windows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ART / "RESULT.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "zl_candidates": len(zl_windows), "consensus": len(consensus), "source_rows": len(source_rows)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
