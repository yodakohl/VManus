#!/usr/bin/env python3
"""Independent, literal-only GDT894 reconstruction and guarded replay.

Importing this module opens no data. Tests supply invented rows. The executable
requeries the one admitted page; invoke it only after preregistration admission.
It never imports the primary runner or grants values to previously unknown codes.
"""
import argparse
from collections import defaultdict
import csv
from hashlib import sha256
import io
import json
from pathlib import Path
import re
import subprocess

E = Path(__file__).resolve().parents[1]
ROOT = E.parents[2]
RAW = "experiments/semantic_assumptions/results/source_separator_transcription.tsv"
RAWCOLS = ("source_group_id,edition,locus,page,kind,source_group_index,source_group_count,"
           "left_separator,right_separator,ivtff_group_raw")
PAGE, EDITION = "f103v", "RF1b"
CONTRADICTED = "CONTRADICTED"
COMPATIBLE = "COMPATIBLE_NECESSARY_CONDITIONS"
UNKNOWN = "UNKNOWN_MEASUREMENT"


class InvalidPacket(ValueError):
    """Invalid input/run, never a scientific contradiction."""


def require(condition, message):
    if not condition:
        raise InvalidPacket(message)


def numeric_locus(row):
    match = re.fullmatch(re.escape(PAGE) + r"\.([0-9]+)", row["locus"])
    require(match is not None, "INVALID_TARGET_SCHEMA: nonnumeric or foreign locus")
    return int(match.group(1))


def ordered_rows(rows):
    require(isinstance(rows, list), "INVALID_TARGET_SCHEMA: rows must be a list")
    seen = set()
    for row in rows:
        require(isinstance(row, dict) and all(key in row for key in RAWCOLS.split(",")),
                "INVALID_TARGET_SCHEMA: missing row fields")
        require(row["page"] == PAGE and row["edition"] == EDITION,
                "INVALID_TARGET_SCHEMA: target scope")
        identifier = row["source_group_id"]
        require(isinstance(identifier, str) and identifier and identifier not in seen,
                "INVALID_TARGET_SCHEMA: duplicate or invalid group ID")
        seen.add(identifier)
        numeric_locus(row)
        try:
            int(row["source_group_index"])
        except (ValueError, TypeError):
            raise InvalidPacket("INVALID_TARGET_SCHEMA: nonnumeric group index") from None
    return sorted(rows, key=lambda row: (numeric_locus(row), int(row["source_group_index"])))


def line_integrity(line):
    try:
        indices = [int(row["source_group_index"]) for row in line]
        counts = [int(row["source_group_count"]) for row in line]
    except (ValueError, TypeError):
        return False
    return (indices == list(range(1, len(line) + 1))
            and all(count == len(line) for count in counts)
            and len({row["source_group_id"] for row in line}) == len(line))


def edge_barrier(left, right):
    """Rows are in physical reading order, also during a backward traversal."""
    a, b = numeric_locus(left), numeric_locus(right)
    if a == b:
        if left["right_separator"] != "DEFINITE_SPACE" or right["left_separator"] != "DEFINITE_SPACE":
            return "NONDEFINITE_SEPARATOR"
    else:
        if b != a + 1:
            return "MISSING_NUMERIC_LINE"
        if left["right_separator"] != "LINE_END" or right["left_separator"] != "LINE_START":
            return "NONDEFINITE_SEPARATOR"
    return None


def row_barrier(row, good_lines):
    if not good_lines[row["locus"]]:
        return "INVALID_LINE_COUNTS"
    if row["kind"] != "P":
        return "NON_P_KIND"
    if not isinstance(row["ivtff_group_raw"], str) or not re.fullmatch(r"[a-z]+", row["ivtff_group_raw"]):
        return "NONLITERAL_GROUP"
    return None


def comparison(offset, source_word, row, mapping, known_values):
    code = row["ivtff_group_raw"]
    if source_word in known_values:
        condition = "KNOWN_MATCH" if mapping.get(code) == source_word else "KNOWN_MISMATCH"
    elif code in mapping:
        condition = "FORBIDDEN_KNOWN_CODE"
    else:
        condition = "UNMAPPED_COMPATIBLE"
    return dict(offset=offset, source_word=source_word, source_group_id=row["source_group_id"],
                cipher_word=code, condition=condition,
                compatible=condition in {"KNOWN_MATCH", "UNMAPPED_COMPATIBLE"})


def evaluate(prediction, supplied_rows):
    """Reconstruct every safe comparison; no primary-runner result is consulted."""
    rows = ordered_rows(supplied_rows)
    require(isinstance(prediction, dict), "INVALID_PREDICTION")
    anchor = prediction["anchor"]
    require(anchor["page"] == PAGE and anchor["edition"] == EDITION, "INVALID_ANCHOR_SCOPE")
    ids, codes, source = (anchor[key] for key in ("source_group_ids", "cipher_words", "source_words"))
    require(isinstance(ids, list) and ids and len(ids) == len(codes) == len(source)
            and len(set(ids)) == len(ids), "INVALID_ANCHOR_ARRAYS")
    mapping = prediction["conditional_map"]
    require(isinstance(mapping, dict) and all(isinstance(k, str) and re.fullmatch(r"[a-z]+", k)
                                            and isinstance(v, str) and v for k, v in mapping.items()),
            "INVALID_CONDITIONAL_MAP")
    require(len(set(mapping.values())) == len(mapping), "NONINJECTIVE_CONDITIONAL_MAP")
    by_id = {row["source_group_id"]: i for i, row in enumerate(rows)}
    require(all(identifier in by_id for identifier in ids), "MISSING_ANCHOR_GROUP")
    start = by_id[ids[0]]
    stop = start + len(ids)
    anchored = rows[start:stop]
    require([row["source_group_id"] for row in anchored] == ids, "NONCONTIGUOUS_ANCHOR")
    require([row["ivtff_group_raw"] for row in anchored] == codes, "ANCHOR_CODE_MISMATCH")
    require(all(mapping.get(code) == word for code, word in zip(codes, source)), "ANCHOR_SOURCE_MISMATCH")
    lines = defaultdict(list)
    for row in rows:
        lines[row["locus"]].append(row)
    good_lines = {locus: line_integrity(line) for locus, line in lines.items()}
    for row in anchored:
        require(row_barrier(row, good_lines) is None, "INVALID_ANCHOR_ROW")
    for left, right in zip(anchored, anchored[1:]):
        require(edge_barrier(left, right) is None, "INVALID_ANCHOR_EDGE")
    directions = {}
    known_values = set(mapping.values())
    for name, step, edge_index in (("preceding", -1, start), ("following", 1, stop - 1)):
        horizon = prediction["horizons"][name]
        offsets, words = horizon["offsets"], horizon["source_words"]
        require(len(offsets) == len(words), "INVALID_HORIZON_LENGTH")
        expected = list(range(-len(words), 0)) if step < 0 else list(range(1, len(words) + 1))
        require(offsets == expected, "NONCONTIGUOUS_SOURCE_HORIZON")
        require(all(isinstance(word, str) and word for word in words), "INVALID_SOURCE_WORD")
        plan = list(zip(offsets, words))
        if step < 0:
            plan.reverse()
        comparisons, barrier = [], None
        current = edge_index
        for offset, word in plan:
            index = current + step
            if not 0 <= index < len(rows):
                barrier = dict(offset=offset, reason="FOLIO_EDGE")
                break
            left, right = (rows[index], rows[current]) if step < 0 else (rows[current], rows[index])
            reason = edge_barrier(left, right) or row_barrier(rows[index], good_lines)
            if reason:
                barrier = dict(offset=offset, reason=reason)
                break
            comparisons.append(comparison(offset, word, rows[index], mapping, known_values))
            current = index
        contradictions = [item for item in comparisons if not item["compatible"]]
        status = CONTRADICTED if contradictions else UNKNOWN if barrier else COMPATIBLE
        directions[name] = dict(requested_positions=len(words), checked_positions=len(comparisons),
                                barrier=barrier, comparisons=comparisons,
                                contradictions=contradictions, status=status)
    statuses = [direction["status"] for direction in directions.values()]
    status = CONTRADICTED if CONTRADICTED in statuses else UNKNOWN if UNKNOWN in statuses else COMPATIBLE
    return dict(status=status, directions=directions)


def guarded_target_query():
    """Only the fixed, explicitly projected, f84-excluding page query is allowed."""
    argv = ["./vmanus-exp", "query-tsv", RAW, "--selector", "page", "--allow", PAGE,
            "--columns", RAWCOLS, "--forbid-prefix", "f84", "--forbid-prefix", "f84r"]
    output = subprocess.run(argv, cwd=ROOT, check=True, capture_output=True, text=True).stdout
    admitted_rows = list(csv.DictReader(io.StringIO(output), delimiter="\t"))
    require(all(row["page"] == PAGE for row in admitted_rows), "GUARD_SCOPE_FAILURE")
    rows = ordered_rows([row for row in admitted_rows if row["edition"] == EDITION])
    guard = dict(argv=argv, source_sha256=sha256((ROOT / RAW).read_bytes()).hexdigest(),
                 projection_sha256=sha256(output.encode()).hexdigest())
    return dict(guard=guard, rows=rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true", help="Accepted verification-mode alias")
    args = parser.parse_args()
    paths = {name: E / "artifacts" / (name + ".json") for name in ("PREDICTION", "TARGET", "RESULT")}
    packets = {name: json.loads(path.read_text()) for name, path in paths.items()}
    independent_target = guarded_target_query()
    require(packets["TARGET"] == independent_target, "INDEPENDENT_GUARDED_TARGET_MISMATCH")
    result = evaluate(packets["PREDICTION"], independent_target["rows"])
    reported = packets["RESULT"]
    require(reported["prediction_sha256"] == sha256(paths["PREDICTION"].read_bytes()).hexdigest(),
            "PREDICTION_HASH_MISMATCH")
    require(reported["target_sha256"] == sha256(paths["TARGET"].read_bytes()).hexdigest(),
            "TARGET_HASH_MISMATCH")
    require(reported["status"] == result["status"], "INDEPENDENT_STATUS_MISMATCH")
    require(reported["directions"] == result["directions"], "INDEPENDENT_COMPARISON_MISMATCH")
    output = dict(status="PASS", independent_result=result,
                  input_sha256={name: sha256(path.read_bytes()).hexdigest() for name, path in paths.items()},
                  validator_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  guard=independent_target["guard"],
                  claim_ceiling="Literal RF conditional-copy contradiction only; no native certainty or held claim.")
    encoded = json.dumps(output, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded)
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
