#!/usr/bin/env python3
"""GDT1072: selector-guarded census of one exact whole on admitted text."""
import csv
import hashlib
import io
import json
import subprocess
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1] / "artifacts"
SOURCE = ROOT / "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
ALLOW = ROOT / "experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv"
COLS = "edition,locus,page,section,currier,hand,kind,source_group_index,ivtff_group_raw"
FIELDS = COLS.split(",")


def guarded(selector, values):
    cmd = [str(ROOT / "vmanus-exp"), "query-tsv", str(SOURCE),
           "--selector", selector, "--forbid-prefix", "f84", "--columns", COLS]
    for value in values:
        cmd.extend(["--allow", value])
    got = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    rows = list(csv.DictReader(io.StringIO(got.stdout), delimiter="\t"))
    if any(r["page"].startswith("f84") for r in rows):
        raise ValueError("forbidden page materialized")
    return rows, got.stderr.strip()


def main():
    with ALLOW.open(newline="") as file:
        pages = [r["page"] for r in csv.DictReader(file, delimiter="\t")]
    assert len(pages) == 179 and not any(p.startswith("f84") for p in pages)
    corpus, corpus_guard = guarded("page", pages)
    special, special_guard = guarded("locus", ["f68r1.1", "f68r1.26"])
    exact = [dict(r, cohort="179_SELECTOR_CORPUS") for r in corpus
             if r["ivtff_group_raw"] == "otor"]
    exact.extend(dict(r, cohort="F68R1_TWO_LOCI") for r in special
                 if r["ivtff_group_raw"] == "otor")
    exact.sort(key=lambda r: (r["edition"], r["page"], r["locus"],
                              int(r["source_group_index"])))
    OUT.mkdir(exist_ok=True)
    cols = ["cohort"] + FIELDS
    with (OUT / "EXACT_OCCURRENCES.tsv").open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=cols, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(exact)
    summary = {
        "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in [SOURCE, ALLOW]},
        "corpus_selector_count": len(pages),
        "corpus_materialized_rows": len(corpus),
        "special_materialized_rows": len(special),
        "guard": {"corpus": corpus_guard, "special": special_guard},
        "exact_counts": {edition: {
            "all": sum(r["edition"] == edition for r in exact),
            "corpus": sum(r["edition"] == edition and r["cohort"] == "179_SELECTOR_CORPUS" for r in exact),
            "special": sum(r["edition"] == edition and r["cohort"] == "F68R1_TWO_LOCI" for r in exact),
            "corpus_by_section": dict(sorted(Counter(r["section"] for r in exact
                if r["edition"] == edition and r["cohort"] == "179_SELECTOR_CORPUS").items())),
            "corpus_by_kind": dict(sorted(Counter(r["kind"] for r in exact
                if r["edition"] == edition and r["cohort"] == "179_SELECTOR_CORPUS").items())),
            "corpus_pages": len({r["page"] for r in exact if r["edition"] == edition
                                 and r["cohort"] == "179_SELECTOR_CORPUS"}),
        } for edition in ["ZL3b", "IT2a", "RF1b"]},
        "claim_ceiling": "Whole-form distribution and alternate boundaries only; no referent or meaning.",
    }
    (OUT / "RESULT.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(summary["exact_counts"], indent=2))


if __name__ == "__main__":
    main()
