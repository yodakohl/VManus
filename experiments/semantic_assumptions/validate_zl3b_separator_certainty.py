#!/usr/bin/env python3
"""Clean-room validation of the ZL3b manual separator-certainty audit.

This implementation imports no production experiment module.  It independently
reconstructs the raw-source/table bindings, the parser-free exact-y capacity
panel, manual separator classes, candidate summaries, residual-y inventory,
gates, claim ceiling, and rendered production report.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RESULTS = HERE / "results"

PRODUCER = HERE / "audit_zl3b_separator_certainty.py"
INTERLINEAR = RESULTS / "pre_grounding_interlinear.tsv"
RESIDUAL = RESULTS / "pre_grounding_surface_residual_atlas.tsv"
CAPACITY = RESULTS / "usr002_exact_y_capacity.tsv"
ZL_LINES = ROOT / "transcription" / "voynich_zl3b_lines.tsv"
ZL_SOURCE = ROOT / "transcription" / "sources" / "ZL3b-n.txt"
RESULT_JSON = RESULTS / "zl3b_separator_certainty.json"
RESULT_REPORT = RESULTS / "zl3b_separator_certainty_report.md"
VALIDATION_JSON = RESULTS / "zl3b_separator_certainty_validation.json"
VALIDATION_REPORT = RESULTS / "zl3b_separator_certainty_validation_report.md"

EXPECTED_SHA256 = {
    PRODUCER: "df63db83228827c63c0e57e2a92d8a1f60279083fc25e5f8393339e7728d32cc",
    INTERLINEAR: "8052a51fa37ad467e754be39648336ec4014442dab5e223daab2e77efaba4a43",
    RESIDUAL: "43f145ae81ffbcb78fdb8217c3a45575d427d3211c2252ac94400928ef4f47f3",
    CAPACITY: "280bd2d89c39a0d1466b6a79ae62a9cbfe3d92f2c63cd670f9abd842496d0407",
    ZL_LINES: "7520dd4c11f4d23c8492e4b2a52cc0fcbda6d9fc88a96ead8f1c31081a4d7ed2",
    ZL_SOURCE: "bf5b6d4ac1e3a51b1847a9c388318d609020441ccd56984c901c32b09beccafc",
    RESULT_JSON: "6399664f6709e472d32b5728cd491ff82115b812a55a04eee5943981635faa3a",
    RESULT_REPORT: "bf7128565354369ca28c343b301e7fc0ae37861f888ef6a5d1cf2092cd5c81bc",
}

READINGS = ("ZL3b", "IT2a", "RF1b")
SOURCE_LINE_RE = re.compile(r"^<(?P<locus>f[^,;>]+)[,;][^>]*>\s*(?P<raw>.*)$")
FOLIO_RE = re.compile(r"^(f\d+)")
SEP_NAME = {
    ".": "DEFINITE_SPACE",
    ",": "UNCERTAIN_SMALL_SPACE",
    "§": "DRAWING_INTERRUPTION",
    "¶": "DRAWING_INTERRUPTION_UNALIGNED",
}

STATUS = "PASS_ZL3B_MANUAL_SEPARATOR_CERTAINTY_AUDIT"
DECISION = "USR002_CONTEXT_ROUTE_STOPPED_EXPLICIT_SEPARATOR_UNCERTAINTY_EXPLAINS_ZL_DISAGREEMENTS"
CLAIM_CEILING = (
    "The ZL3b-side exact-y split/fused disagreements are fully contained in spaces the manual "
    "transcription already marks uncertain or interrupted by drawings. This explains the proposed "
    "USR002 target as transcription/layout uncertainty, not a newly discovered grammar. It does not "
    "prove which spacing is authorial or assign y a separator, suffix, sound, word, or meaning."
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def digest(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_sha256(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    return sha256_bytes(encoded)


def load_tsv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        return list(reader.fieldnames or ()), list(reader)


def raw_source_rows(path: Path) -> tuple[str, dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    out: dict[str, str] = {}
    for line in lines:
        match = SOURCE_LINE_RE.match(line)
        if not match:
            continue
        locus = match.group("locus")
        if locus in out:
            raise RuntimeError(f"duplicate raw ZL source locus: {locus}")
        out[locus] = match.group("raw")
    return lines[0] if lines else "", out


def separators(raw: str, token_count: int) -> list[str] | None:
    protected = raw.replace("<->", "§").replace("<~>", "¶")
    without_comments = re.sub(r"<[^>]*>", "", protected)
    values = [SEP_NAME[char] for char in without_comments if char in SEP_NAME]
    return values if len(values) == max(0, token_count - 1) else None


def token_spans(tokens: list[str]) -> list[tuple[int, int]]:
    out: list[tuple[int, int]] = []
    start = 0
    for token in tokens:
        end = start + len(token)
        out.append((start, end))
        start = end
    return out


def internal_boundaries(tokens: list[str]) -> set[int]:
    return {end for _start, end in token_spans(tokens)[:-1]}


def reconstruct_capacity(
    interlinear: list[dict[str, str]], interrupted: set[str]
) -> list[dict[str, str]]:
    by_locus: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for row in interlinear:
        edition = row["edition"]
        locus = row["locus"]
        if edition in by_locus[locus]:
            raise RuntimeError(f"duplicate interlinear edition/locus: {edition}/{locus}")
        by_locus[locus][edition] = row

    candidates: list[dict[str, str]] = []
    for locus, reading_rows in sorted(by_locus.items()):
        if set(reading_rows) != set(READINGS):
            continue
        tokens = {reading: reading_rows[reading]["surface"].split() for reading in READINGS}
        compact = {reading: "".join(tokens[reading]) for reading in READINGS}
        if len(set(compact.values())) != 1:
            continue
        boundaries = {reading: internal_boundaries(tokens[reading]) for reading in READINGS}
        offsets: set[tuple[int, int]] = set()
        for reading in READINGS:
            for span, token in zip(token_spans(tokens[reading]), tokens[reading]):
                if token == "y":
                    offsets.add(span)
        for start, end in sorted(offsets):
            if end - start != 1:
                raise RuntimeError("literal y span is not one character")
            if start == 0 or end == len(compact["ZL3b"]):
                continue
            isolated: dict[str, bool] = {}
            for reading in READINGS:
                all_boundaries = {0, len(compact[reading])} | boundaries[reading]
                isolated[reading] = start in all_boundaries and end in all_boundaries
            isolated_count = sum(isolated.values())
            if isolated_count not in (1, 2):
                continue
            zl_row = reading_rows["ZL3b"]
            all_confirmed_prose = all(
                reading_rows[reading]["grammar_scope"] == "CONFIRMED_PROSE"
                for reading in READINGS
            )
            folio_match = FOLIO_RE.match(zl_row["page"])
            if not folio_match:
                raise RuntimeError(f"unresolved physical folio: {locus}")
            candidates.append({
                "candidate_id": f"{locus}@{start + 1}",
                "locus": locus,
                "page": zl_row["page"],
                "physical_folio": folio_match.group(1),
                "section": zl_row["section"],
                "currier": zl_row["currier"],
                "character_offset_1based": str(start + 1),
                "isolated_reading_count": str(isolated_count),
                "ZL3b_isolated": str(int(isolated["ZL3b"])),
                "IT2a_isolated": str(int(isolated["IT2a"])),
                "RF1b_isolated": str(int(isolated["RF1b"])),
                "outcome_vector": "".join(str(int(isolated[reading])) for reading in READINGS),
                "manual_zl_line_has_interruption": str(int(locus in interrupted)),
                "eligible_after_manual_interruption_exclusion": str(int(locus not in interrupted)),
                "all_readings_confirmed_prose": str(int(all_confirmed_prose)),
                "eligible_for_context_power_preflight": str(
                    int(locus not in interrupted and all_confirmed_prose)
                ),
                "compact_character_length": str(len(compact["ZL3b"])),
            })
    return candidates


def render_production_report(
    source_rows: int,
    interlinear_rows: int,
    separator_rows: int,
    candidate_pairs: Counter[tuple[str, str]],
    context_isolated: int,
    residual_total: int,
    residual_resolved: int,
) -> str:
    return f"""# ZL3b manual separator-certainty audit

Decision: **STOP USR002 BEFORE A CONTEXT SCORE**.

The manual ZL3b source explicitly distinguishes confident spaces (`.`),
uncertain small spaces (`,`), and drawing interruptions (`<->`/`<~>`).  The
definitions are in section 6.7 of the
[IVTFF format specification](https://www.voynich.nu/software/ivtt/IVTFF_format.pdf).
The
derived ZL table matches all {source_rows:,} raw source rows exactly, and
the pre-grounding surface matches all {interlinear_rows:,} shared clean
rows.  Separator order is directly recoverable on
{separator_rows:,}/{source_rows:,} rows and on every exact-y
candidate.

Of the 30 parser-free split/fused `y` spans, ZL3b isolates `y` in 28 and fuses
it in two.  All 28 isolated cases already carry at least one explicit uncertain
small-space or drawing-interruption boundary:

| ZL left boundary | ZL right boundary | spans |
|---|---|---:|
| definite | uncertain | {candidate_pairs[("DEFINITE_SPACE", "UNCERTAIN_SMALL_SPACE")]} |
| uncertain | definite | {candidate_pairs[("UNCERTAIN_SMALL_SPACE", "DEFINITE_SPACE")]} |
| uncertain | uncertain | {candidate_pairs[("UNCERTAIN_SMALL_SPACE", "UNCERTAIN_SMALL_SPACE")]} |
| drawing interruption | uncertain | {candidate_pairs[("DRAWING_INTERRUPTION", "UNCERTAIN_SMALL_SPACE")]} |
| definite | definite | {candidate_pairs[("DEFINITE_SPACE", "DEFINITE_SPACE")]} |

After the earlier drawing-line and confirmed-prose exclusions, all
{context_isolated} ZL-isolated cases remain explicitly uncertain.  A
context classifier would therefore model a confidence flag already supplied by
the human transcription, not discover an independent manuscript boundary.

This stop does not make literal `y` meaningless.  Across all {residual_total} ZL residual
`y` events, {residual_resolved} have recoverable
separator metadata and some are bounded by two confident spaces.  It closes
only the proposed exact-y disagreement route.  No authorial spacing, suffix,
separator, sound, plaintext, or English meaning follows.
"""


def main() -> None:
    passed: list[str] = []
    failures: list[str] = []

    def check(name: str, condition: bool, detail: str = "") -> None:
        if condition:
            passed.append(name)
        else:
            failures.append(f"{name}: {detail}" if detail else name)

    observed_sha256 = {path: digest(path) for path in EXPECTED_SHA256}
    for path, expected in EXPECTED_SHA256.items():
        check(
            f"sha256:{path.relative_to(ROOT)}",
            observed_sha256[path] == expected,
            f"expected {expected}, observed {observed_sha256[path]}",
        )
    if failures:
        raise RuntimeError("hash binding failure: " + "; ".join(failures))

    result = json.loads(RESULT_JSON.read_text(encoding="utf-8"))
    interlinear_fields, interlinear = load_tsv(INTERLINEAR)
    residual_fields, residuals = load_tsv(RESIDUAL)
    capacity_fields, capacity = load_tsv(CAPACITY)
    zl_line_fields, zl_lines = load_tsv(ZL_LINES)
    header, source = raw_source_rows(ZL_SOURCE)

    check("source:manual_header", header == "#=IVTFF Eva- 2.0 M 5", header)
    check("source:row_count", len(source) == 5_385, str(len(source)))
    check("table:row_count", len(zl_lines) == 5_385, str(len(zl_lines)))
    check("table:unique_loci", len({row["locus"] for row in zl_lines}) == 5_385)
    check(
        "table:required_fields",
        {"locus", "token_count", "eva_clean", "ivtff_raw"} <= set(zl_line_fields),
    )
    zl_index = {row["locus"]: row for row in zl_lines}
    raw_mismatches = [
        row["locus"] for row in zl_lines if source.get(row["locus"]) != row["ivtff_raw"]
    ]
    check("source_table:exact_raw_binding", not raw_mismatches, str(raw_mismatches[:3]))

    check(
        "interlinear:required_fields",
        {"edition", "locus", "page", "section", "currier", "grammar_scope", "surface"}
        <= set(interlinear_fields),
    )
    interlinear_keys = [(row["edition"], row["locus"]) for row in interlinear]
    check("interlinear:unique_edition_locus", len(interlinear_keys) == len(set(interlinear_keys)))
    zl_interlinear_rows = [row for row in interlinear if row["edition"] == "ZL3b"]
    check("interlinear:zl_row_count", len(zl_interlinear_rows) == 5_376, str(len(zl_interlinear_rows)))
    zl_interlinear = {row["locus"]: row for row in zl_interlinear_rows}
    clean_mismatches = [
        locus for locus, row in zl_interlinear.items()
        if locus not in zl_index or row["surface"] != zl_index[locus]["eva_clean"]
    ]
    check("table_interlinear:exact_clean_surface_binding", not clean_mismatches, str(clean_mismatches[:3]))

    separator_by_locus = {
        row["locus"]: separators(row["ivtff_raw"], len(row["eva_clean"].split()))
        for row in zl_lines
    }
    parsed_separator_rows = sum(value is not None for value in separator_by_locus.values())
    check("separators:resolved_rows", parsed_separator_rows == 5_323, str(parsed_separator_rows))
    check("separators:unresolved_rows", len(zl_lines) - parsed_separator_rows == 62)

    interrupted = {locus for locus, raw in source.items() if "<->" in raw}
    reconstructed_capacity = reconstruct_capacity(interlinear, interrupted)
    check("capacity:required_fields", set(capacity_fields) == set(reconstructed_capacity[0]))
    check("capacity:full_row_reconstruction", capacity == reconstructed_capacity)
    check("capacity:exact_y_spans", len(reconstructed_capacity) == 30, str(len(reconstructed_capacity)))

    candidate_pairs: Counter[tuple[str, str]] = Counter()
    candidate_details: list[dict[str, Any]] = []
    zl_isolated = 0
    zl_fused = 0
    candidate_separator_failures: list[str] = []
    for candidate in reconstructed_capacity:
        locus = candidate["locus"]
        row = zl_index[locus]
        tokens = row["eva_clean"].split()
        values = separator_by_locus[locus]
        if values is None:
            candidate_separator_failures.append(locus)
            continue
        target_start = int(candidate["character_offset_1based"]) - 1
        position = next(
            (
                index
                for index, ((start, _end), token) in enumerate(zip(token_spans(tokens), tokens))
                if start == target_start and token == "y"
            ),
            None,
        )
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
            raise RuntimeError(f"noninternal exact-y candidate: {candidate['candidate_id']}")
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

    check("candidates:all_separator_rows_reconstructed", not candidate_separator_failures)
    check("candidates:zl_isolated", zl_isolated == 28, str(zl_isolated))
    check("candidates:zl_fused", zl_fused == 2, str(zl_fused))
    expected_breakdown = {
        ("DEFINITE_SPACE", "UNCERTAIN_SMALL_SPACE"): 15,
        ("UNCERTAIN_SMALL_SPACE", "DEFINITE_SPACE"): 8,
        ("UNCERTAIN_SMALL_SPACE", "UNCERTAIN_SMALL_SPACE"): 3,
        ("DRAWING_INTERRUPTION", "UNCERTAIN_SMALL_SPACE"): 2,
        ("DEFINITE_SPACE", "DEFINITE_SPACE"): 0,
    }
    for pair, expected_count in expected_breakdown.items():
        check(f"candidates:pair:{pair[0]}|{pair[1]}", candidate_pairs[pair] == expected_count)
    check("candidates:details_exact", candidate_details == result["exact_y_candidates"]["details"])

    candidate_uncertain = sum(
        count for pair, count in candidate_pairs.items() if "UNCERTAIN_SMALL_SPACE" in pair
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
    context_explicit = sum(
        "UNCERTAIN_SMALL_SPACE" in (row["left_separator"], row["right_separator"])
        or str(row["left_separator"]).startswith("DRAWING_")
        or str(row["right_separator"]).startswith("DRAWING_")
        for row in context_isolated
    )
    check("context:isolated_count", len(context_isolated) == 19, str(len(context_isolated)))
    check("context:all_explicit_uncertainty", context_explicit == 19, str(context_explicit))

    check(
        "residual:required_fields",
        {"edition", "locus", "omitted_positions_1based", "omitted_tokens"} <= set(residual_fields),
    )
    residual_y_pairs: Counter[tuple[str, str]] = Counter()
    residual_y_total = 0
    residual_y_unresolved = 0
    for residual in residuals:
        if residual["edition"] != "ZL3b":
            continue
        locus = residual["locus"]
        tokens = zl_index[locus]["eva_clean"].split()
        values = separator_by_locus[locus]
        positions = [int(value) for value in residual["omitted_positions_1based"].split(";")]
        omitted = residual["omitted_tokens"].split()
        if len(positions) != len(omitted):
            raise RuntimeError(f"residual position/token mismatch: {locus}")
        for position, token in zip(positions, omitted):
            if token != "y":
                continue
            residual_y_total += 1
            if values is None:
                residual_y_unresolved += 1
                continue
            index = position - 1
            left = "LINE_START" if index == 0 else values[index - 1]
            right = "LINE_END" if index == len(tokens) - 1 else values[index]
            residual_y_pairs[(left, right)] += 1
    residual_resolved = residual_y_total - residual_y_unresolved
    check("residual_y:events", residual_y_total == 341, str(residual_y_total))
    check("residual_y:resolved", residual_resolved == 318, str(residual_resolved))
    check("residual_y:unresolved", residual_y_unresolved == 23, str(residual_y_unresolved))

    candidate_pair_payload = {
        f"{left}|{right}": count for (left, right), count in sorted(candidate_pairs.items())
    }
    residual_pair_payload = {
        f"{left}|{right}": count for (left, right), count in sorted(residual_y_pairs.items())
    }
    check(
        "residual_y:pair_inventory_exact",
        residual_pair_payload == result["all_zl3b_residual_y"]["separator_pairs"],
    )

    source_provenance = {
        "manual_header": "#=IVTFF Eva- 2.0 M 5",
        "separator_definition_source": (
            "IVTFF format specification section 6.7: "
            "https://www.voynich.nu/software/ivtt/IVTFF_format.pdf"
        ),
        "source_rows": len(source),
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
    }
    gates = {
        "all_candidate_separator_rows_reconstructed": not candidate_separator_failures
        and zl_isolated + zl_fused == len(reconstructed_capacity),
        "every_zl_isolated_disagreement_has_uncertain_or_drawing_boundary": (
            candidate_uncertain_or_drawing == zl_isolated
        ),
        "zero_zl_isolated_disagreements_have_two_definite_spaces": (
            candidate_pairs[("DEFINITE_SPACE", "DEFINITE_SPACE")] == 0
        ),
        "every_context_scope_zl_isolated_case_is_explicitly_uncertain": (
            len(context_isolated) > 0 and len(context_isolated) == context_explicit
        ),
    }
    exact_y_candidates = {
        "spans": len(reconstructed_capacity),
        "zl3b_isolated": zl_isolated,
        "zl3b_fused": zl_fused,
        "isolated_separator_pairs": candidate_pair_payload,
        "isolated_with_uncertain_small_space": candidate_uncertain,
        "isolated_with_drawing_interruption": candidate_drawing,
        "isolated_with_uncertain_or_drawing_boundary": candidate_uncertain_or_drawing,
        "isolated_with_two_definite_spaces": candidate_pairs[("DEFINITE_SPACE", "DEFINITE_SPACE")],
        "context_scope_zl3b_isolated": len(context_isolated),
        "context_scope_isolated_with_uncertain_or_drawing": context_explicit,
        "details": candidate_details,
    }
    all_residual_y = {
        "events": residual_y_total,
        "separator_resolved": residual_resolved,
        "separator_unresolved": residual_y_unresolved,
        "separator_pairs": residual_pair_payload,
    }
    input_sha256 = {
        str(path.relative_to(ROOT)): observed_sha256[path]
        for path in (INTERLINEAR, RESIDUAL, CAPACITY, ZL_LINES, ZL_SOURCE)
    }
    expected_payload = {
        "status": STATUS,
        "decision": DECISION,
        "input_sha256": input_sha256,
        "source_provenance": source_provenance,
        "exact_y_candidates": exact_y_candidates,
        "all_zl3b_residual_y": all_residual_y,
        "gates": gates,
        "claim_ceiling": CLAIM_CEILING,
        "english_lexical_glosses": 0,
    }
    check("result:status", result.get("status") == STATUS)
    check("result:decision", result.get("decision") == DECISION)
    check("result:input_hash_bindings", result.get("input_sha256") == input_sha256)
    check("result:source_provenance", result.get("source_provenance") == source_provenance)
    check("result:exact_y_candidates", result.get("exact_y_candidates") == exact_y_candidates)
    check("result:all_residual_y", result.get("all_zl3b_residual_y") == all_residual_y)
    check("result:gates_exact", result.get("gates") == gates)
    check("result:gates_all_pass", all(gates.values()))
    check("result:claim_ceiling_exact", result.get("claim_ceiling") == CLAIM_CEILING)
    check("result:english_gloss_count", result.get("english_lexical_glosses") == 0)
    check("result:full_payload_exact", result == expected_payload)
    reconstructed_result_bytes = (
        json.dumps(expected_payload, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")
    check(
        "result:canonical_bytes_exact",
        sha256_bytes(reconstructed_result_bytes) == observed_sha256[RESULT_JSON],
    )

    expected_report = render_production_report(
        len(source),
        len(zl_interlinear),
        parsed_separator_rows,
        candidate_pairs,
        len(context_isolated),
        residual_y_total,
        residual_resolved,
    )
    check("report:exact_text", RESULT_REPORT.read_text(encoding="utf-8") == expected_report)

    if failures:
        raise RuntimeError("validation failure: " + "; ".join(failures))

    validator_sha256 = digest(Path(__file__))
    gates_sha256 = canonical_sha256(gates)
    claim_sha256 = sha256_bytes(CLAIM_CEILING.encode("utf-8"))
    details_sha256 = canonical_sha256(candidate_details)
    report_text = f"""# Independent ZL3b separator-certainty validation

Decision: **PASS — EXACT CLEAN-ROOM RECONSTRUCTION**.

The standalone validator imports no production experiment module. It binds the
manual ZL3b source, derived line table, complete pre-grounding surface,
parser-free capacity panel, and residual atlas, then independently reconstructs
the complete production JSON and report.

The IVTFF separator definitions are provenance-bound to section 6.7 of the
official format specification, and the new JSON field and report citation both
reconstruct exactly.

- Raw source/table binding: **5,385/5,385** exact rows.
- Interlinear/table clean-surface binding: **5,376/5,376** exact rows.
- Separator extraction: **5,323 resolved / 62 unresolved** rows.
- Exact-y panel: **30 spans; 28 ZL-isolated / 2 ZL-fused**.
- Isolated boundary pairs: **15 / 8 / 3 / 2 / 0** in the frozen report order.
- Confirmed-prose clean scope: **19/19** ZL-isolated cases explicitly uncertain.
- Residual ZL `y`: **341 events; 318 resolved / 23 unresolved**.
- Independent checks passed: **{len(passed)}** with zero discrepancies.

Hashes:

- Validator: `{validator_sha256}`
- Producer: `{observed_sha256[PRODUCER]}`
- Production JSON: `{observed_sha256[RESULT_JSON]}`
- Production report: `{observed_sha256[RESULT_REPORT]}`
- Gate object: `{gates_sha256}`
- Claim ceiling: `{claim_sha256}`

The validated claim remains a route-specific transcription/layout-uncertainty
stop. It assigns no authorial spacing, separator, suffix, sound, word, plaintext,
or meaning.
"""
    VALIDATION_REPORT.write_text(report_text, encoding="utf-8")
    validation_report_sha256 = digest(VALIDATION_REPORT)

    validation_payload = {
        "status": "PASS_INDEPENDENT_ZL3B_SEPARATOR_CERTAINTY_VALIDATION",
        "decision": DECISION,
        "production_imported": False,
        "check_count": len(passed),
        "failure_count": 0,
        "check_names": passed,
        "artifact_sha256": {
            "validator": validator_sha256,
            "producer": observed_sha256[PRODUCER],
            "production_json": observed_sha256[RESULT_JSON],
            "production_report": observed_sha256[RESULT_REPORT],
            "validation_report": validation_report_sha256,
        },
        "input_sha256": input_sha256,
        "reconstruction": {
            "separator_definition_source": source_provenance["separator_definition_source"],
            "source_rows": len(source),
            "table_rows": len(zl_lines),
            "interlinear_zl_rows": len(zl_interlinear),
            "separator_rows_reconstructed": parsed_separator_rows,
            "separator_rows_unresolved": len(zl_lines) - parsed_separator_rows,
            "exact_y_spans": len(reconstructed_capacity),
            "zl3b_isolated": zl_isolated,
            "zl3b_fused": zl_fused,
            "pair_breakdown_report_order": [
                candidate_pairs[("DEFINITE_SPACE", "UNCERTAIN_SMALL_SPACE")],
                candidate_pairs[("UNCERTAIN_SMALL_SPACE", "DEFINITE_SPACE")],
                candidate_pairs[("UNCERTAIN_SMALL_SPACE", "UNCERTAIN_SMALL_SPACE")],
                candidate_pairs[("DRAWING_INTERRUPTION", "UNCERTAIN_SMALL_SPACE")],
                candidate_pairs[("DEFINITE_SPACE", "DEFINITE_SPACE")],
            ],
            "context_scope_zl3b_isolated": len(context_isolated),
            "context_scope_explicit_uncertainty": context_explicit,
            "residual_y_events": residual_y_total,
            "residual_y_separator_resolved": residual_resolved,
            "residual_y_separator_unresolved": residual_y_unresolved,
        },
        "exact_object_sha256": {
            "source_provenance": canonical_sha256(source_provenance),
            "gates": gates_sha256,
            "claim_ceiling": claim_sha256,
            "candidate_details": details_sha256,
            "reconstructed_production_payload": sha256_bytes(reconstructed_result_bytes),
        },
        "gates": gates,
        "claim_ceiling": CLAIM_CEILING,
        "english_lexical_glosses": 0,
    }
    VALIDATION_JSON.write_text(
        json.dumps(validation_payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": validation_payload["status"],
        "checks": len(passed),
        "failures": 0,
        "validation_json_sha256": digest(VALIDATION_JSON),
        "validation_report_sha256": validation_report_sha256,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
