#!/usr/bin/env python3
"""Render two exact-whole counterfactual displays, without semantic scoring."""
import argparse
import csv
import hashlib
import io
import json
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parents[2]
ART = BASE / "artifacts"
SOURCE = "experiments/yolo/gdt812_additional_page_semantic_bridge/artifacts/ADMITTED_PAGE_LINES.tsv"
COLS = ["page", "locus", "line_number", "kind", "paragraph_start", "paragraph_end",
        "eva_clean", "it2a_clean", "rf1b_clean"]
READERS = {"ZL3b": "eva_clean", "IT2a": "it2a_clean", "RF1b": "rf1b_clean"}
OUTCOLS = COLS[:6] + ["reader_id", "source_text", "token_count", "daiin_count",
                       "unknown_count", "daiin_positions_1based", "model_III", "model_sehr"]
STATUS = "POST_RESULT_EXPLORATORY_DISPLAY_ONLY"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode_json(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare replay bytes; do not write.")
    args = parser.parse_args()
    spec_bytes = (BASE / "src/FOLLOWUP_RENDER_SPEC.json").read_bytes()
    spec = json.loads(spec_bytes)
    require(spec["status"] == STATUS and spec["source"] == SOURCE, "Wrong follow-up status/source")
    require(spec["selector"] == "page" and spec["allowed"] == ["f32v"], "Scope must remain f32v only")
    require(spec["sealed_data"] == ["f84", "f84r"], "Both seals must be explicit")
    require(spec["source_columns"] == COLS and spec["readers"] == READERS,
            "Source projection or reader identity changed")
    require(spec["reader_order"] == list(READERS) and spec["required_locus_count"] == 11,
            "All eleven loci and three readings are required")
    require(spec["target_whole"] == "daiin" and spec["models"] == {"model_III": "III?", "model_sehr": "sehr?"},
            "Only the two specified whole-daiin displays are permitted")
    require(spec["unknown_template"] == "[token]", "Unknown display policy changed")
    require(all(spec[k] == 0 for k in ("confirmed_words", "confirmed_plaintext_clauses", "new_admissions"))
            and spec["dictionary_changed"] is False, "The spec must not claim semantic results")

    command = ["./vmanus-exp", "query-tsv", SOURCE, "--selector", "page", "--allow", "f32v",
               "--columns", ",".join(COLS), "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    query = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=True)
    stats = [json.loads(s.removeprefix("GUARD_STATS ")) for s in query.stderr.splitlines()
             if s.startswith("GUARD_STATS ")]
    require(len(stats) == 1 and stats[0]["selected"] == 11, "Guard did not select exactly eleven loci")
    reader = csv.DictReader(io.StringIO(query.stdout), delimiter="\t")
    require(reader.fieldnames == COLS, "Guard returned unexpected columns")
    source = list(reader)
    require([r["locus"] for r in source] == [f"f32v.{n}" for n in range(1, 12)],
            "Source loci are incomplete, duplicated, or reordered")
    require(all(r["page"] == "f32v" and r["line_number"] == str(n)
                for n, r in enumerate(source, 1)), "Source page/line coordinates changed")
    require(all(r[c].strip() for r in source for c in READERS.values()), "A cached reading is missing")

    rows = []
    totals = {name: {"loci": 0, "tokens": 0, "daiin_wholes": 0, "unknown_wholes": 0}
              for name in READERS}
    for record in source:
        for name, column in READERS.items():
            tokens = record[column].split()
            positions = [i for i, token in enumerate(tokens, 1) if token == "daiin"]
            row = {key: record[key] for key in COLS[:6]}
            row.update(reader_id=name, source_text=record[column], token_count=len(tokens),
                       daiin_count=len(positions), unknown_count=len(tokens) - len(positions),
                       daiin_positions_1based=json.dumps(positions, separators=(",", ":")))
            for model, label in spec["models"].items():
                row[model] = " ".join(label if t == "daiin" else "[" + t + "]" for t in tokens)
            rows.append(row)
            tally = totals[name]
            tally["loci"] += 1
            tally["tokens"] += len(tokens)
            tally["daiin_wholes"] += len(positions)
            tally["unknown_wholes"] += len(tokens) - len(positions)
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=OUTCOLS, delimiter="\t", lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    output = stream.getvalue().encode()
    differences = {}
    names = list(READERS)
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            differences[left + "_vs_" + right] = [r["locus"] for r in source
                                                  if r[READERS[left]] != r[READERS[right]]]
    result = {
        "status": STATUS, "page": "f32v", "source_loci": 11, "reader_rows": len(rows),
        "readers_are_alternate_readings_not_independent_witnesses": True,
        "models": spec["models"], "per_reader": totals, "source_difference_loci": differences,
        "confirmed_words": 0, "confirmed_plaintext_clauses": 0, "new_admissions": 0,
        "dictionary_changed": False, "semantic_score": None, "meanings_validated": False,
        "claim_ceiling": "Model-display contrast and exact-whole substitution reproducibility only.",
        "guard": {"command": command, "stats": stats[0], "projection_sha256": digest(query.stdout.encode())},
        "spec_sha256": digest(spec_bytes), "runner_sha256": digest(Path(__file__).read_bytes()),
        "trial_tsv_sha256": digest(output),
    }
    products = {"FOLLOWUP_WHOLE_PAGE_TRIAL.tsv": output, "FOLLOWUP_TRIAL_RESULT.json": encode_json(result)}
    for name, data in products.items():
        path = ART / name
        if args.check:
            require(path.is_file() and path.read_bytes() == data, "Replay mismatch: " + name)
        else:
            path.write_bytes(data)
    print(json.dumps({"status": "REPLAY_PASS" if args.check else "DISPLAY_WRITTEN",
                      "reader_rows": len(rows), "per_reader": totals, "meanings_validated": False}, sort_keys=True))


if __name__ == "__main__":
    main()
