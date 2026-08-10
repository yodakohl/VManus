#!/usr/bin/env python3
"""Independent result validator for ESD001; imports no producer module."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
from collections import Counter
from pathlib import Path


EXPECTED_COMMIT = "e608818b754ac79fc86e7f3bdbe3194db2260c51"
HERE = Path(__file__).resolve().parent
RESULT = HERE / "esd001_external_decoder_audit.json"
OUT = HERE / "esd001_external_decoder_audit_validation.json"
REPORT = HERE.parent / "results" / "esd001_external_decoder_audit_validation.md"


def digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def show(repo: Path, rel: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(repo), "show", f"HEAD:{rel}"])


def specificity(text: str) -> tuple[float, int, int]:
    m = re.search(
        r"^\s*Sinhala\s+[+-][\d,]+\s+[+-][\d.]+\s+[\d.]+\s+"
        r"([+-][\d.]+)\s+(\d+)/(\d+)\s*$",
        text,
        re.MULTILINE,
    )
    if not m:
        raise AssertionError("missing Sinhala specificity row")
    return float(m.group(1)), int(m.group(2)), int(m.group(3))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--external-repo", type=Path, required=True)
    ap.add_argument("--rerun-specificity", type=Path, required=True)
    args = ap.parse_args()
    repo = args.external_repo.resolve()
    obj = json.loads(RESULT.read_text())
    checks = []

    def check(name: str, condition: bool) -> None:
        checks.append({"name": name, "pass": bool(condition)})
        if not condition:
            raise AssertionError(name)

    commit = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    check("commit", commit == EXPECTED_COMMIT == obj["external_commit"])

    for rel, expected in obj["committed_file_sha256"].items():
        check(f"hash:{rel}", digest(show(repo, rel)) == expected)

    cz, cb, cn = specificity(show(repo, "results/decoder_specificity.txt").decode())
    rz, rb, rn = specificity(args.rerun_specificity.read_text())
    check("committed_specificity_values", (cz, cb, cn) == (-0.82, 154, 200))
    check("rerun_specificity_values", (rz, rb, rn) == (-0.76, 146, 200))
    check("both_specificity_results_fail", cz < 0 and rz < 0)
    check("rerun_digest", digest(args.rerun_specificity.read_bytes()) == obj["specificity_rerun_sha256"])

    run_all = show(repo, "run_all.sh").decode()
    holdout = show(repo, "scripts/holdout_validation.py").decode()
    translator = show(repo, "scripts/pipeline/translate_manuscript.py").decode()
    check("holdout_in_run_all", '"scripts/holdout_validation.py"' in run_all)
    check("specificity_omitted_from_run_all", "decoder_specificity_test.py" not in run_all)
    check(
        "global_vocab_loaded_before_split",
        holdout.index("load_decoded_vocab(VOCAB_TSV_PATH)") < holdout.index("train_lines = []"),
    )
    check("renderer_exact_eva_lookup", "if eva in vocab:" in translator)
    check(
        "renderer_regex_reordering",
        "def restructure_line" in translator and "re.sub" in translator,
    )

    translation = show(repo, "output/voynich_translation.md").decode()
    rows = [tuple(map(int, x)) for x in re.findall(
        r"\*(\d+) words — (\d+) translated \([\d.]+%\) — (\d+) gaps\*", translation
    )]
    words, translated, gaps = (sum(r[i] for r in rows) for i in range(3))
    check("translation_folios", len(rows) == 225)
    check("translation_partition", (words, translated, gaps) == (36231, 13472, 22759))
    check("translation_under_half", translated / words < 0.5)

    dbp = repo / "translation" / "voynich_v20_corpus.db"
    check("database_hash", digest(dbp.read_bytes()) == obj["v20_database_sha256"])
    con = sqlite3.connect(f"file:{dbp}?mode=ro", uri=True)
    try:
        tiers = dict(con.execute("SELECT evidence_tier,COUNT(*) FROM tokens GROUP BY evidence_tier"))
        sources = Counter(dict(con.execute("SELECT tier_source,COUNT(*) FROM tokens GROUP BY tier_source")))
        n = con.execute("SELECT COUNT(*) FROM tokens").fetchone()[0]
    finally:
        con.close()
    weak = (
        sources["Context/gloss assigned, no direct external attestation"]
        + sources["Deictic q- compound (rule-generated)"]
        + sources["Deictic ch- compound (rule-generated)"]
    )
    check("database_counts", (n, tiers, weak) == (36633, {"A": 8707, "B": 23780, "C": 4146}, 20571))
    check("decision", obj["status"] == "REJECT_EXTERNAL_DECODER_AS_TRANSLATION_EVIDENCE")
    check("all_decision_gates_false", not any(obj["decision_gates"].values()))

    out = {
        "experiment": "ESD001",
        "status": "PASS",
        "checks": len(checks),
        "failures": [c["name"] for c in checks if not c["pass"]],
        "producer_result_sha256": digest(RESULT.read_bytes()),
        "external_commit": commit,
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    REPORT.write_text(
        "# ESD001 validation\n\n"
        f"PASS: {len(checks)} independent checks reproduce the frozen public-file "
        "hashes, both failed specificity results, validation-gate omission, "
        "global-vocabulary ordering, translation coverage, database provenance "
        "counts, and rejection decision. No external production module was imported.\n"
    )
    print(json.dumps(out, sort_keys=True))


if __name__ == "__main__":
    main()
