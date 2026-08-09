#!/usr/bin/env python3
"""Recover ZL3b's manual separator certainty for exact-y disagreements."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
RESIDUAL = RESULTS / "pre_grounding_surface_residual_atlas.tsv"
CAPACITY = RESULTS / "usr002_exact_y_capacity.tsv"
ZL_LINES = HERE.parents[1] / "transcription" / "voynich_zl3b_lines.tsv"
ZL_SOURCE = HERE.parents[1] / "transcription" / "sources" / "ZL3b-n.txt"
OUTPUT_JSON = RESULTS / "zl3b_separator_certainty.json"
OUTPUT_REPORT = RESULTS / "zl3b_separator_certainty_report.md"
EXPECTED = {
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    RESIDUAL: "43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3",
    CAPACITY: "280bd2d89c39a0d1466b6a79ae62a9cbfe3d92f2c63cd670f9abd842496d0407",
    ZL_LINES: "7520dd4c11f4d23c8492e4b2a52cc0fcbda6d9fc88a96ead8f1c31081a4d7ed2",
    ZL_SOURCE: "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
}
SOURCE_LINE_RE = re.compile(r"^<(?P<locus>f[^,;>]+)[,;][^>]*>\s*(?P<raw>.*)$")
SEP_NAME = {
    ".": "DEFINITE_SPACE",
    ",": "UNCERTAIN_SMALL_SPACE",
    "§": "DRAWING_INTERRUPTION",
    "¶": "DRAWING_INTERRUPTION_UNALIGNED",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def source_rows(path: Path) -> dict[str, str]:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = SOURCE_LINE_RE.match(line)
        if match:
            locus = match.group("locus")
            if locus in out:
                raise RuntimeError(f"duplicate ZL source locus {locus}")
            out[locus] = match.group("raw")
    return out


def separators(raw: str, token_count: int) -> list[str] | None:
    protected = raw.replace("<->", "§").replace("<~>", "¶")
    without_comments = re.sub(r"<[^>]*>", "", protected)
    values = [SEP_NAME[char] for char in without_comments if char in SEP_NAME]
    return values if len(values) == max(0, token_count - 1) else None


def token_spans(tokens: list[str]) -> list[tuple[int, int]]:
    out = []
    start = 0
    for token in tokens:
        end = start + len(token)
        out.append((start, end))
        start = end
    return out


def main() -> None:
    observed = {path: digest(path) for path in EXPECTED}
    if observed != EXPECTED:
        raise RuntimeError("separator-certainty input drift")
    interlinear = load(INTERLINEAR)
    residuals = load(RESIDUAL)
    capacity = load(CAPACITY)
    zl_lines = load(ZL_LINES)
    raw_source = source_rows(ZL_SOURCE)
    if not (len(zl_lines) == len(raw_source) > 0):
        raise RuntimeError("ZL source/table count drift")
    if len(zl_lines) != 5_385 or len({row["locus"] for row in zl_lines}) != 5_385:
        raise RuntimeError("ZL row identity drift")
    for row in zl_lines:
        if raw_source.get(row["locus"]) != row["ivtff_raw"]:
            raise RuntimeError(f"ZL raw provenance mismatch at {row['locus']}")

    zl_interlinear = {row["locus"]: row for row in interlinear if row["edition"] == "ZL3b"}
    zl_index = {row["locus"]: row for row in zl_lines}
    if len(zl_interlinear) != 5_376:
        raise RuntimeError("ZL interlinear count drift")
    for locus, row in zl_interlinear.items():
        if row["surface"] != zl_index[locus]["eva_clean"]:
            raise RuntimeError(f"ZL clean surface mismatch at {locus}")

    separator_by_locus = {
        row["locus"]: separators(row["ivtff_raw"], len(row["eva_clean"].split()))
        for row in zl_lines
    }
    parsed_separator_rows = sum(value is not None for value in separator_by_locus.values())

    candidate_pairs = Counter()
    candidate_details = []
    zl_isolated = 0
    zl_fused = 0
    for candidate in capacity:
        locus = candidate["locus"]
        row = zl_index[locus]
        tokens = row["eva_clean"].split()
        values = separator_by_locus[locus]
        if values is None:
            raise RuntimeError(f"candidate separator parse failure at {locus}")
        target_start = int(candidate["character_offset_1based"]) - 1
        position = None
        for index, ((start, _), token) in enumerate(zip(token_spans(tokens), tokens)):
            if start == target_start and token == "y":
                position = index
                break
        if position is None:
            zl_fused += 1
            candidate_details.append({
                "candidate_id": candidate["candidate_id"],
                "outcome_vector": candidate["outcome_vector"],
                "zl3b_state": "FUSED",
                "left_separator": "NOT_APPLICABLE",
                "right_separator": "NOT_APPLICABLE",
                "manual_interruption_excluded": candidate["manual_zl_line_has_interruption"] == "1",
                "context_power_scope": candidate["eligible_for_context_power_preflight"] == "1",
            })
            continue
        if position == 0 or position == len(tokens) - 1:
            raise RuntimeError("capacity y is not internal")
        zl_isolated += 1
        left = values[position - 1]
        right = values[position]
        candidate_pairs[(left, right)] += 1
        candidate_details.append({
            "candidate_id": candidate["candidate_id"],
            "outcome_vector": candidate["outcome_vector"],
            "zl3b_state": "ISOLATED",
            "left_separator": left,
            "right_separator": right,
            "manual_interruption_excluded": candidate["manual_zl_line_has_interruption"] == "1",
            "context_power_scope": candidate["eligible_for_context_power_preflight"] == "1",
        })

    residual_y_pairs = Counter()
    residual_y_total = 0
    residual_y_unresolved_rows = 0
    for residual in residuals:
        if residual["edition"] != "ZL3b":
            continue
        locus = residual["locus"]
        tokens = zl_index[locus]["eva_clean"].split()
        values = separator_by_locus[locus]
        positions = [int(value) for value in residual["omitted_positions_1based"].split(";")]
        omitted = residual["omitted_tokens"].split()
        for position, token in zip(positions, omitted):
            if token != "y":
                continue
            residual_y_total += 1
            if values is None:
                residual_y_unresolved_rows += 1
                continue
            index = position - 1
            left = "LINE_START" if index == 0 else values[index - 1]
            right = "LINE_END" if index == len(tokens) - 1 else values[index]
            residual_y_pairs[(left, right)] += 1

    candidate_pair_payload = {
        f"{left}|{right}": count
        for (left, right), count in sorted(candidate_pairs.items())
    }
    residual_pair_payload = {
        f"{left}|{right}": count
        for (left, right), count in sorted(residual_y_pairs.items())
    }
    candidate_uncertain = sum(
        count for (left, right), count in candidate_pairs.items()
        if "UNCERTAIN_SMALL_SPACE" in (left, right)
    )
    candidate_drawing = sum(
        count for (left, right), count in candidate_pairs.items()
        if left.startswith("DRAWING_") or right.startswith("DRAWING_")
    )
    candidate_uncertain_or_drawing = sum(
        count for (left, right), count in candidate_pairs.items()
        if "UNCERTAIN_SMALL_SPACE" in (left, right)
        or left.startswith("DRAWING_") or right.startswith("DRAWING_")
    )
    context_isolated = [
        row for row in candidate_details
        if row["context_power_scope"] and row["zl3b_state"] == "ISOLATED"
    ]
    payload = {
        "status": "PASS_ZL3B_MANUAL_SEPARATOR_CERTAINTY_AUDIT",
        "decision": "USR002_CONTEXT_ROUTE_STOPPED_EXPLICIT_SEPARATOR_UNCERTAINTY_EXPLAINS_ZL_DISAGREEMENTS",
        "input_sha256": {
            str(path.relative_to(HERE.parents[1])): value for path, value in observed.items()
        },
        "source_provenance": {
            "manual_header": "#=IVTFF Eva- 2.0 M 5",
            "separator_definition_source": (
                "IVTFF format specification section 6.7: "
                "https://www.voynich.nu/software/ivtt/IVTFF_format.pdf"
            ),
            "source_rows": len(raw_source),
            "derived_rows_exact_raw_match": len(zl_lines),
            "interlinear_rows_exact_clean_surface_match": len(zl_interlinear),
            "separator_rows_reconstructed": parsed_separator_rows,
            "separator_rows_unresolved": len(zl_lines) - parsed_separator_rows,
            "separator_semantics": {
                ".": "confident apparent word space",
                ",": "uncertain small apparent word space",
                "<->": "drawing interruption implying a space",
                "<~>": "unaligned drawing interruption implying a space",
            },
        },
        "exact_y_candidates": {
            "spans": len(capacity),
            "zl3b_isolated": zl_isolated,
            "zl3b_fused": zl_fused,
            "isolated_separator_pairs": candidate_pair_payload,
            "isolated_with_uncertain_small_space": candidate_uncertain,
            "isolated_with_drawing_interruption": candidate_drawing,
            "isolated_with_uncertain_or_drawing_boundary": candidate_uncertain_or_drawing,
            "isolated_with_two_definite_spaces": candidate_pairs[("DEFINITE_SPACE", "DEFINITE_SPACE")],
            "context_scope_zl3b_isolated": len(context_isolated),
            "context_scope_isolated_with_uncertain_or_drawing": sum(
                "UNCERTAIN_SMALL_SPACE" in (row["left_separator"], row["right_separator"])
                or str(row["left_separator"]).startswith("DRAWING_")
                or str(row["right_separator"]).startswith("DRAWING_")
                for row in context_isolated
            ),
            "details": candidate_details,
        },
        "all_zl3b_residual_y": {
            "events": residual_y_total,
            "separator_resolved": residual_y_total - residual_y_unresolved_rows,
            "separator_unresolved": residual_y_unresolved_rows,
            "separator_pairs": residual_pair_payload,
        },
        "gates": {
            "all_candidate_separator_rows_reconstructed": zl_isolated + zl_fused == len(capacity),
            "every_zl_isolated_disagreement_has_uncertain_or_drawing_boundary": (
                candidate_uncertain_or_drawing == zl_isolated
            ),
            "zero_zl_isolated_disagreements_have_two_definite_spaces": (
                candidate_pairs[("DEFINITE_SPACE", "DEFINITE_SPACE")] == 0
            ),
            "every_context_scope_zl_isolated_case_is_explicitly_uncertain": (
                len(context_isolated) > 0
                and len(context_isolated) == sum(
                    "UNCERTAIN_SMALL_SPACE" in (row["left_separator"], row["right_separator"])
                    or str(row["left_separator"]).startswith("DRAWING_")
                    or str(row["right_separator"]).startswith("DRAWING_")
                    for row in context_isolated
                )
            ),
        },
        "claim_ceiling": (
            "The ZL3b-side exact-y split/fused disagreements are fully contained in spaces the manual "
            "transcription already marks uncertain or interrupted by drawings. This explains the proposed "
            "USR002 target as transcription/layout uncertainty, not a newly discovered grammar. It does not "
            "prove which spacing is authorial or assign y a separator, suffix, sound, word, or meaning."
        ),
        "english_lexical_glosses": 0,
    }
    if not all(payload["gates"].values()):
        raise RuntimeError(f"separator-certainty gate failure: {payload['gates']}")
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report = f"""# ZL3b manual separator-certainty audit

Decision: **STOP USR002 BEFORE A CONTEXT SCORE**.

The manual ZL3b source explicitly distinguishes confident spaces (`.`),
uncertain small spaces (`,`), and drawing interruptions (`<->`/`<~>`).  The
definitions are in section 6.7 of the
[IVTFF format specification](https://www.voynich.nu/software/ivtt/IVTFF_format.pdf).
The
derived ZL table matches all {len(raw_source):,} raw source rows exactly, and
the pre-grounding surface matches all {len(zl_interlinear):,} shared clean
rows.  Separator order is directly recoverable on
{parsed_separator_rows:,}/{len(zl_lines):,} rows and on every exact-y
candidate.

Of the 30 parser-free split/fused `y` spans, ZL3b isolates `y` in 28 and fuses
it in two.  All 28 isolated cases already carry at least one explicit uncertain
small-space or drawing-interruption boundary:

| ZL left boundary | ZL right boundary | spans |
|---|---|---:|
| definite | uncertain | {candidate_pairs[('DEFINITE_SPACE', 'UNCERTAIN_SMALL_SPACE')]} |
| uncertain | definite | {candidate_pairs[('UNCERTAIN_SMALL_SPACE', 'DEFINITE_SPACE')]} |
| uncertain | uncertain | {candidate_pairs[('UNCERTAIN_SMALL_SPACE', 'UNCERTAIN_SMALL_SPACE')]} |
| drawing interruption | uncertain | {candidate_pairs[('DRAWING_INTERRUPTION', 'UNCERTAIN_SMALL_SPACE')]} |
| definite | definite | {candidate_pairs[('DEFINITE_SPACE', 'DEFINITE_SPACE')]} |

After the earlier drawing-line and confirmed-prose exclusions, all
{len(context_isolated)} ZL-isolated cases remain explicitly uncertain.  A
context classifier would therefore model a confidence flag already supplied by
the human transcription, not discover an independent manuscript boundary.

This stop does not make literal `y` meaningless.  Across all 341 ZL residual
`y` events, {residual_y_total - residual_y_unresolved_rows} have recoverable
separator metadata and some are bounded by two confident spaces.  It closes
only the proposed exact-y disagreement route.  No authorial spacing, suffix,
separator, sound, plaintext, or English meaning follows.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "candidate_spans": len(capacity),
        "zl_isolated": zl_isolated,
        "explicitly_uncertain_or_drawing": candidate_uncertain_or_drawing,
        "definite_definite": candidate_pairs[("DEFINITE_SPACE", "DEFINITE_SPACE")],
        "context_isolated": len(context_isolated),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
