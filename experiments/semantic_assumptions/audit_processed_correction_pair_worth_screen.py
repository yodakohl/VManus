#!/usr/bin/env python3
"""Build the compact processed correction-pair worth-screen result."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "experiments/semantic_assumptions"
METHOD = BASE / "PROCESSED_CORRECTION_PAIR_WORTH_SCREEN_METHOD.md"
OBS = BASE / "processed_correction_pair_worth_screen_observations.tsv"
EVT = ROOT / "transcription/sources/Stolfi_text25e1-52.evt"
RESULT = BASE / "results/processed_correction_pair_worth_screen.json"
REPORT = BASE / "results/processed_correction_pair_worth_screen_report.md"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def load_rows() -> list[dict[str, str]]:
    with OBS.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if [(row["folio"], row["locus"], row["proposed_transition"]) for row in rows] != [
        ("f16r", "f16r.2", "e_TO_l"),
        ("f24v", "f24v.6", "a_TO_s"),
        ("f26r", "f26r.1", "ch_TO_sh"),
    ]:
        raise SystemExit("unexpected candidate order")
    if [int(row["candidate_instances"]) for row in rows] != [1, 1, 2]:
        raise SystemExit("unexpected instance counts")
    for row in rows:
        if row["stable_after_form"] != "YES":
            raise SystemExit("current form must be visible")
        if any(row[field] != "NO" for field in ("stable_before_form", "physical_order_resolved", "distinct_from_variant_or_damage", "recoverable_pair")):
            raise SystemExit("recoverable pair requires a different result")
        if row["decision"] != "NO_PAIR":
            raise SystemExit("unexpected decision")
        if any(len(row[field]) != 64 for field in ("official_sha256", "processed_sha256")):
            raise SystemExit("invalid sha256")
    source = EVT.read_bytes()
    phrases = {
        b"<f16r.2;U>": b"corrected to @l",
        b"<f24v.6;U>": b"final @s is over the preceding @a",
        b"<f26r.1;U>": b"corrected to @'sh'",
    }
    for locus, phrase in phrases.items():
        locus_at = source.find(locus)
        phrase_at = source.find(phrase)
        if phrase_at < 0 or locus_at < 0 or not 0 < locus_at - phrase_at < 1000:
            raise SystemExit("human correction annotation mismatch")
    return rows


def build() -> tuple[dict[str, object], str]:
    rows = load_rows()
    result: dict[str, object] = {
        "experiment": "PROCESSED_CORRECTION_PAIR_WORTH_SCREEN",
        "schema": "PROCESSED_CORRECTION_PAIR_WORTH_SCREEN_V1",
        "status": "STOP_NO_RECOVERABLE_BEFORE_AFTER_CORRECTION_PAIR",
        "decision": "STOP_BOUNDED_THREE_LOCUS_PROCESSED_SCREEN_NO_PAIR",
        "counts": {
            "loci_inspected": 3,
            "candidate_instances": 4,
            "official_images": 3,
            "processed_images": 3,
            "visible_current_forms": 4,
            "stable_before_forms": 0,
            "resolved_physical_orders": 0,
            "recoverable_correction_pairs": 0,
            "translation_anchors": 0,
        },
        "candidates": [
            {
                "folio": row["folio"],
                "locus": row["locus"],
                "candidate_instances": int(row["candidate_instances"]),
                "proposed_transition": row["proposed_transition"],
                "observation": row["observation"],
                "decision": row["decision"],
            }
            for row in rows
        ],
        "inputs": {
            str(METHOD.relative_to(ROOT)): sha(METHOD),
            str(OBS.relative_to(ROOT)): sha(OBS),
            str(EVT.relative_to(ROOT)): sha(EVT),
        },
        "claim_ceiling": (
            "The current and processed images show unusual current glyph forms at the three strongest explicitly proposed "
            "main-text corrections but do not recover independently bounded earlier states or physical before/after order. "
            "They establish no character substitution, sound, word, language, cipher, plaintext, meaning, or translation."
        ),
    }
    report = (
        "# Processed manuscript-correction pair worth screen\n\n"
        "Decision: **STOP — NO RECOVERABLE BEFORE/AFTER PAIR**.\n\n"
        "The official and paint-removal witnesses show the current unusual forms at f16r.2, f24v.6, and the two f26r.1 "
        "instances. None preserves an independently bounded earlier form plus a visible later intervention. The f26r "
        "plumes therefore remain sh-like variants rather than demonstrated `ch→sh` edits; the proposed f16r `e→l` and "
        "f24v `a→s` transitions likewise remain unresolved.\n\n"
        "This source-bound native AI assessment is machine-authored, not human annotation. Paint removal is an algorithmic "
        "display transform rather than physical-layer imaging. No OCR, automated transcription, glyph classifier, CLIP, "
        "embedding, similarity score, decoder, proposed reading, or language fit was used. The result establishes no "
        "character substitution, sound, word, language, cipher, plaintext, meaning, or translation.\n"
    )
    return result, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    result, report = build()
    if args.write:
        RESULT.write_bytes(canonical(result))
        REPORT.write_text(report, encoding="utf-8")
    else:
        print(canonical(result).decode(), end="")


if __name__ == "__main__":
    main()
