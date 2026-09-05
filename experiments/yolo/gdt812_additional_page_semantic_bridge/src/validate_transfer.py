#!/usr/bin/env python3
"""Verify selected scalar-context source cards, not their proposed meanings."""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

EXP = Path(__file__).resolve().parent.parent
ROOT = EXP.parents[2]
SOURCE = "experiments/yolo/gdt812_additional_page_semantic_bridge/artifacts/ADMITTED_PAGE_LINES.tsv"
PAGES = ["f21r", "f100v", "f101r"]
LOCI = ["f21r.2", "f101r.2", "f101r.4", "f101r.5", "f101r.8", "f101r.9", "f100v.14", "f100v.21", "f100v.22"]
READERS = [("ZL3b", "eva_clean"), ("IT2a", "it2a_clean"), ("RF1b", "rf1b_clean")]
COLS = ["page", "locus", "line_number", "kind", "paragraph_start", "paragraph_end"] + [c for _, c in READERS]
FIELDS = ["card_id", "page", "locus", "reader_id", "paragraph_start", "paragraph_end", "source_text",
          "exact_daiin_positions_1based", "target_spans", "candidate_classes", "unknown_policy", "design_timing"]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--check", action="store_true", help="Compare validation bytes without writing.")
    args = cli.parse_args()
    command = ["./vmanus-exp", "query-tsv", SOURCE, "--selector", "page"]
    for page in PAGES:
        command += ["--allow", page]
    command += ["--columns", ",".join(COLS), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    fresh = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    stats = [json.loads(s[12:]) for s in fresh.stderr.splitlines() if s.startswith("GUARD_STATS ")]
    require(len(stats) == 1 and stats[0]["selected"] == 44, "Guard must select exactly 44 admitted loci")
    parsed = csv.DictReader(io.StringIO(fresh.stdout), delimiter="\t")
    require(parsed.fieldnames == COLS, "Unexpected guarded projection")
    source = list(parsed)
    require(len(source) == 44 and {r["page"] for r in source} == set(PAGES), "Source page/locus scope")
    by_locus = {r["locus"]: r for r in source}
    require(len(by_locus) == 44, "Duplicate source locus")
    boundary = [(r["locus"], r["paragraph_start"], r["paragraph_end"]) for r in source if r["page"] == "f101r"]
    require(boundary == [(f"f101r.{i}", str(int(i in (1, 3, 7))), str(int(i in (2, 6, 10))))
                         for i in range(1, 11)], "All f101r paragraph boundaries must remain source-exact")
    card_bytes = (EXP / "src/SCALAR_TRANSFER_CARDS.tsv").read_bytes()
    cards = csv.DictReader(io.StringIO(card_bytes.decode()), delimiter="\t")
    require(cards.fieldnames == FIELDS, "Card schema")
    actual = list(cards)
    expected, hits, crossline, zero_target = [], 0, 0, 0
    for locus in LOCI:
        rec = by_locus[locus]
        require(rec["kind"] == "P", "Card context must be source prose")
        for name, column in READERS:
            words = rec[column].split()
            require(bool(words), "Missing alternate reading")
            positions = [i + 1 for i, token in enumerate(words) if token == "daiin"]
            spans, candidates = [], []
            for position in positions:
                host = rec if position > 1 else by_locus[rec["page"] + "." + str(int(rec["line_number"]) - 1)]
                require(position > 1 or (rec["paragraph_start"] == "0" and host["paragraph_end"] == "0"
                        and host["locus"] in LOCI), "Cross-line host omitted or paragraph boundary crossed")
                host_words = host[column].split()
                host_position = position - 1 if position > 1 else len(host_words)
                spans.append(f"{host['locus']}@{host_position}..{locus}@{position}={host_words[host_position - 1]} daiin")
                candidates.append("HIGH_AMOUNT_HYPOTHESIS" if locus == "f21r.2" else
                                  "HIGH_INTENSITY_HYPOTHESIS" if locus == "f101r.2" else "OPEN")
                crossline += int(position == 1)
            hits += len(positions)
            zero_target += int(not positions)
            values = [f"ST{len(expected) + 1:02d}", rec["page"], locus, name, rec["paragraph_start"], rec["paragraph_end"],
                      rec[column], ",".join(map(str, positions)) or "NONE", "|".join(spans) or "NONE",
                      ",".join(candidates) or "NONE", "ALL_NON_TARGET_WHOLES_UNKNOWN", "POST_RESULT_EXPLORATION"]
            expected.append(dict(zip(FIELDS, values)))
    require(actual == expected and len(actual) == 27, "Source join: changed context, target omission, extra target, or altered hypothesis tag")
    report = {"status": "PASS_SELECTED_CONTEXT_SOURCE_REPRODUCIBILITY_ONLY", "design_timing": "POST_RESULT_EXPLORATION",
              "selected_context_loci": LOCI, "source_loci_guarded": len(source), "card_rows": len(actual),
              "target_occurrences_in_selected_contexts": hits, "cross_line_spans": crossline, "zero_target_reader_rows_retained": zero_target,
              "f101r_paragraphs": [[1, 2], [3, 6], [7, 10]], "all_selected_context_targets_retained": True,
              "coverage_limit": "Nine selected complete contexts, not all daiin on the three pages.",
              "readers_are_alternate_readings_not_independent_witnesses": True, "semantic_score": None,
              "meanings_validated": False, "confirmed_words": 0, "confirmed_plaintext_clauses": 0,
              "dictionary_changed": False, "new_admissions": 0, "sealed_data": ["f84", "f84r"],
              "guard": {"command": command, "stats": stats[0], "projection_sha256": sha(fresh.stdout.encode())},
              "cards_sha256": sha(card_bytes), "validator_sha256": sha(Path(__file__).read_bytes())}
    payload = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode()
    target = EXP / "artifacts/SCALAR_TRANSFER_VALIDATION.json"
    if args.check:
        require(target.is_file() and target.read_bytes() == payload, "Validation replay differs")
    else:
        target.write_bytes(payload)
    print(json.dumps({k: report[k] for k in ("status", "card_rows", "target_occurrences_in_selected_contexts", "meanings_validated")}, sort_keys=True))


if __name__ == "__main__":
    main()
