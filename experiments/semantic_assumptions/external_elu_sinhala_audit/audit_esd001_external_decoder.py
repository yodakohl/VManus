#!/usr/bin/env python3
"""Audit the public kamb-code/Voynich decoder without importing its code."""

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
PUBLIC_REPOSITORY = "https://github.com/kamb-code/Voynich"
HERE = Path(__file__).resolve().parent
RESULT_JSON = HERE / "esd001_external_decoder_audit.json"
REPORT = HERE.parent / "results" / "esd001_external_decoder_audit.md"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_bytes(repo: Path, rel: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(repo), "show", f"HEAD:{rel}"]
    )


def parse_specificity(text: str) -> dict:
    m = re.search(
        r"^\s*Sinhala\s+([+-][\d,]+)\s+([+-][\d.]+)\s+"
        r"([\d.]+)\s+([+-][\d.]+)\s+(\d+)/(\d+)\s*$",
        text,
        re.MULTILINE,
    )
    if not m:
        raise ValueError("Sinhala specificity row not found")
    best = re.search(r"Most specifically boosted:\s+(\S+)", text)
    generic = "cannot be fully rejected" in text.lower()
    return {
        "h12_delta_tokens": int(m.group(1).replace(",", "")),
        "random_mean_delta_tokens": float(m.group(2)),
        "random_sd_delta_tokens": float(m.group(3)),
        "delta_z": float(m.group(4)),
        "random_decoders_meeting_or_beating_h12": int(m.group(5)),
        "random_decoder_count": int(m.group(6)),
        "most_specifically_boosted_language": best.group(1) if best else None,
        "generic_cv_not_rejected": generic,
    }


def parse_translation(text: str) -> dict:
    rows = [
        (int(a), int(b), float(c), int(d))
        for a, b, c, d in re.findall(
            r"\*(\d+) words — (\d+) translated \(([\d.]+)%\) — (\d+) gaps\*",
            text,
        )
    ]
    if not rows:
        raise ValueError("translation folio summaries not found")
    words = sum(r[0] for r in rows)
    translated = sum(r[1] for r in rows)
    gaps = sum(r[3] for r in rows)
    if words != translated + gaps:
        raise ValueError("translation coverage does not partition words")
    return {
        "folios": len(rows),
        "words": words,
        "translated_gloss_slots": translated,
        "gap_slots": gaps,
        "translated_fraction": translated / words,
        "literal_gap_markers": text.count("[___]"),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--external-repo", type=Path, required=True)
    ap.add_argument(
        "--rerun-specificity",
        type=Path,
        required=True,
        help="Result produced once by the current public specificity script",
    )
    args = ap.parse_args()
    repo = args.external_repo.resolve()

    commit = subprocess.check_output(
        ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
    ).strip()
    if commit != EXPECTED_COMMIT:
        raise SystemExit(f"wrong external commit: {commit}")

    rels = [
        "README.md",
        "run_all.sh",
        "scripts/h12_decoder.py",
        "scripts/v14_decoder.py",
        "scripts/v15_decoder.py",
        "scripts/holdout_validation.py",
        "scripts/decoder_specificity_test.py",
        "scripts/pipeline/translate_manuscript.py",
        "results/decoder_specificity.txt",
        "results/holdout_validation.txt",
        "output/voynich_translation.md",
    ]
    committed = {rel: git_bytes(repo, rel) for rel in rels}
    texts = {rel: data.decode("utf-8", "replace") for rel, data in committed.items()}

    committed_spec = parse_specificity(texts["results/decoder_specificity.txt"])
    rerun_bytes = args.rerun_specificity.read_bytes()
    rerun_spec = parse_specificity(rerun_bytes.decode("utf-8", "replace"))
    translation = parse_translation(texts["output/voynich_translation.md"])

    run_all = texts["run_all.sh"]
    holdout = texts["scripts/holdout_validation.py"]
    h12 = texts["scripts/h12_decoder.py"]
    v14 = texts["scripts/v14_decoder.py"]
    v15 = texts["scripts/v15_decoder.py"]
    translator = texts["scripts/pipeline/translate_manuscript.py"]

    static = {
        "holdout_in_run_all": '"scripts/holdout_validation.py"' in run_all,
        "specificity_in_run_all": "decoder_specificity_test.py" in run_all,
        "h12_says_mapping_derived_against_sinhala_dictionary": (
            "cross-validation against the Sinhala dictionary" in h12
        ),
        "v14_accepts_global_meanings": "meanings=None" in v14,
        "v14_conditionally_selects_using_meanings": (
            "if meanings is not None" in v14 and "should_strip = False" in v14
        ),
        "v15_selects_strict_dictionary_or_gloss_tier_improvement": (
            "if v15_t < v14_t" in v15 and "dict_set" in v15
        ),
        "holdout_loads_global_curated_vocab_before_split": (
            holdout.index("load_decoded_vocab(VOCAB_TSV_PATH)")
            < holdout.index("train_lines = []")
        ),
        "english_renderer_uses_exact_eva_vocabulary_lookup": "if eva in vocab:" in translator,
        "english_renderer_uses_regex_reordering": "def restructure_line" in translator
        and "re.sub" in translator,
    }

    holdout_summary = {
        "claims_all_three_pass": "HOLDOUT TESTS PASSED: 3/3" in texts[
            "results/holdout_validation.txt"
        ],
        "claims_generalisation": (
            "H12 decoder claims generalise from TRAIN to unseen TEST data."
            in texts["results/holdout_validation.txt"]
        ),
    }

    db_path = repo / "translation" / "voynich_v20_corpus.db"
    db_sha = sha256(db_path.read_bytes())
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    try:
        evidence_tiers = dict(
            con.execute(
                "SELECT evidence_tier, COUNT(*) FROM tokens GROUP BY evidence_tier"
            ).fetchall()
        )
        tier_sources = Counter(
            dict(
                con.execute(
                    "SELECT tier_source, COUNT(*) FROM tokens GROUP BY tier_source"
                ).fetchall()
            )
        )
        token_count = con.execute("SELECT COUNT(*) FROM tokens").fetchone()[0]
    finally:
        con.close()

    provenance_counts = {
        "context_gloss_no_direct_external_attestation": tier_sources[
            "Context/gloss assigned, no direct external attestation"
        ],
        "rule_generated_q_compound": tier_sources[
            "Deictic q- compound (rule-generated)"
        ],
        "rule_generated_ch_compound": tier_sources[
            "Deictic ch- compound (rule-generated)"
        ],
    }
    weak_total = sum(provenance_counts.values())

    gates = {
        "committed_specificity_above_random_mean": committed_spec["delta_z"] > 0,
        "rerun_specificity_above_random_mean": rerun_spec["delta_z"] > 0,
        "specificity_in_advertised_gate": static["specificity_in_run_all"],
        "held_folio_glosses_train_only": not static[
            "holdout_loads_global_curated_vocab_before_split"
        ],
        "published_output_at_least_half_translated": translation[
            "translated_fraction"
        ] >= 0.5,
    }
    status = (
        "PASS_EXTERNAL_DECODER_AS_INDEPENDENT_EVIDENCE"
        if all(gates.values())
        else "REJECT_EXTERNAL_DECODER_AS_TRANSLATION_EVIDENCE"
    )

    result = {
        "experiment": "ESD001",
        "status": status,
        "public_repository": PUBLIC_REPOSITORY,
        "external_commit": commit,
        "committed_file_sha256": {rel: sha256(data) for rel, data in committed.items()},
        "v20_database_sha256": db_sha,
        "specificity_committed": committed_spec,
        "specificity_current_source_rerun": rerun_spec,
        "specificity_rerun_sha256": sha256(rerun_bytes),
        "specificity_result_is_stale_against_current_source": (
            sha256(rerun_bytes) != sha256(committed["results/decoder_specificity.txt"])
        ),
        "advertised_holdout": holdout_summary,
        "static_pipeline_audit": static,
        "published_english_output": translation,
        "v20_database": {
            "tokens": token_count,
            "evidence_tiers": evidence_tiers,
            "selected_nonindependent_provenance_counts": provenance_counts,
            "selected_nonindependent_provenance_total": weak_total,
            "selected_nonindependent_provenance_fraction": weak_total / token_count,
        },
        "decision_gates": gates,
        "claim_ceiling": (
            "This rejects the audited public decoder and English gloss layer as "
            "independent translation evidence. It does not disprove Elu-Sinhala "
            "or any other known-language hypothesis in the abstract."
        ),
    }

    RESULT_JSON.parent.mkdir(parents=True, exist_ok=True)
    RESULT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    report = f"""# ESD001 external Elu-Sinhala decoder audit

Status: **{status}**

The public decoder cannot be imported as a Voynich translation. Its own
committed specificity test puts Sinhala below its random-decoder mean
(Z={committed_spec['delta_z']:.2f};
{committed_spec['random_decoders_meeting_or_beating_h12']}/{committed_spec['random_decoder_count']}
random decoders meet or beat H12). Re-running the unchanged public test against
the current committed source still fails (Z={rerun_spec['delta_z']:.2f};
{rerun_spec['random_decoders_meeting_or_beating_h12']}/{rerun_spec['random_decoder_count']})
and changes the result bytes, so the release result is stale.

The advertised `run_all.sh` includes the odd/even holdout but omits the failed
decoder-specificity test. The holdout loads the full curated decoded vocabulary
before creating its train/test lists; later decoder layers also select variants
when they improve a full Sinhala dictionary or curated gloss tier. It is
therefore not a held-out discovery of the mapping or English lexicon.

The file titled “Complete English Translation” reports only
{translation['translated_gloss_slots']:,}/{translation['words']:,}
({100*translation['translated_fraction']:.2f}%) translated gloss slots and
{translation['gap_slots']:,} gaps. Its renderer performs exact EVA-type lookup,
small regex reorderings, capitalization, and punctuation; it does not derive
sentence meanings. The V20 database later fills all tokens, but
{weak_total:,}/{token_count:,} ({100*weak_total/token_count:.2f}%) tokens alone
come from the three explicit provenance classes “context/gloss assigned, no
direct external attestation” or rule-generated q-/ch- compounds.

This is a useful falsification, not a translation: the repository supplies a
deterministic romanization candidate, but it does not demonstrate that the
mapping is specifically Sinhala or that its English gloss stream is plaintext.
The result closes only this audited decoder version.
"""
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(report)

    print(json.dumps({
        "status": status,
        "result": str(RESULT_JSON.relative_to(HERE.parents[2])),
        "report": str(REPORT.relative_to(HERE.parents[2])),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
