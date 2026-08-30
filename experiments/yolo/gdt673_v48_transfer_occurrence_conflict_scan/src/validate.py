#!/usr/bin/env python3
"""Independent validation for GDT673."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt673_v48_transfer_occurrence_conflict_scan"
ART = EXP / "artifacts"
CARDS = ROOT / "experiments/yolo/gdt672_v48_concrete_page_renderer/src/F1R_TRANSFER_CARDS.tsv"
PANEL = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
ALLOWLIST = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/PAGE_ALLOWLIST.tsv"
DECISIONS = EXP / "src/CARD_CONTEXT_DECISIONS.tsv"
CROSS = "transcription/voynich_cross_transcription_lines.tsv"
STATUS = "PASS_162_PW_TRANSFER_POSITIONS__39_CARDS_HOLD__3_O_CARDS_SPLIT__2_F1R_CORRECTIONS"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unknowns(row: dict[str, str]) -> set[int]:
    return {int(value) for value in row["unknown_ordinals"].split("|") if value and value != "NONE"}


def guarded_cross(allowlist: list[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    command = [str(ROOT / "vmanus-exp"), "query-tsv", CROSS, "--selector", "page"]
    for page in allowlist:
        command.extend(("--allow", page))
    command.extend(
        (
            "--columns", "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean",
            "--forbid-prefix", "f84",
        )
    )
    completed = subprocess.run(command, cwd=ROOT, check=True, text=True, capture_output=True)
    match = re.search(r"GUARD_STATS\s+(\{[^\n]+\})", completed.stderr)
    if not match:
        raise RuntimeError("no GUARD_STATS from guarded cross query")
    return (
        list(csv.DictReader(io.StringIO(completed.stdout), delimiter="\t")),
        {str(key): int(value) for key, value in json.loads(match.group(1)).items()},
    )


def align(source: list[str], alternate: list[str]) -> list[tuple[str, tuple[int, ...], str]]:
    n, m = len(source), len(alternate)
    cells: list[list[tuple[int, int, list[tuple[str, tuple[int, ...], str]]] | None]] = [
        [None] * (m + 1) for _ in range(n + 1)
    ]
    cells[0][0] = (0, 0, [])

    def offer(i: int, j: int, cost: int, steps: int, path: list[tuple[str, tuple[int, ...], str]], op: tuple[str, tuple[int, ...], str]) -> None:
        candidate = (cost, steps, [*path, op])
        old = cells[i][j]
        if old is None or candidate[:2] < old[:2]:
            cells[i][j] = candidate

    for i in range(n + 1):
        for j in range(m + 1):
            cell = cells[i][j]
            if cell is None:
                continue
            cost, steps, path = cell
            if i < n and j < m:
                offer(i + 1, j + 1, cost + (0 if source[i] == alternate[j] else 10), steps + 1, path, ("ONE", (i,), alternate[j]))
            if i + 1 < n and j < m and source[i] + source[i + 1] == alternate[j]:
                offer(i + 2, j + 1, cost + 1, steps + 1, path, ("MERGE_2", (i, i + 1), alternate[j]))
            if i + 2 < n and j < m and source[i] + source[i + 1] + source[i + 2] == alternate[j]:
                offer(i + 3, j + 1, cost + 1, steps + 1, path, ("MERGE_3", (i, i + 1, i + 2), alternate[j]))
            if i < n and j + 1 < m and source[i] == alternate[j] + alternate[j + 1]:
                offer(i + 1, j + 2, cost + 1, steps + 1, path, ("SPLIT_2", (i,), source[i]))
            if i < n:
                offer(i + 1, j, cost + 10, steps + 1, path, ("DELETE", (i,), ""))
            if j < m:
                offer(i, j + 1, cost + 10, steps + 1, path, ("INSERT", (), alternate[j]))
    if cells[n][m] is None:
        raise RuntimeError("alignment failed")
    return cells[n][m][2]  # type: ignore[index]


def operations(source: list[str], alternate: list[str]) -> dict[int, tuple[str, str]]:
    result: dict[int, tuple[str, str]] = {}
    for operation, indices, value in align(source, alternate):
        for index in indices:
            result[index] = ("EXACT" if operation == "ONE" and value == source[index] else operation, value or "EMPTY")
    return result


def line_position(index: int, total: int) -> str:
    if total == 1:
        return "SINGLETON"
    if index == 1:
        return "INITIAL"
    if index == total:
        return "FINAL"
    return "MEDIAL"


def classify_o(surface: str, gloss: str, right_surface: str, right_gloss: str) -> tuple[str, str]:
    if surface == "y":
        if gloss in {"hierzu:", "; hierzu:", "Eintrag abgeschlossen", "Eintragsteil abgeschlossen", "Labelschluss"}:
            return "O_HOLD_COMPATIBLE", "Y_ALLOWED_REFERENCE_OR_LEFT_CLOSE"
        return "O_NAMED_CONTEXT_CONFLICT", "Y_ENTRY_OR_LABEL_OUTSIDE_CARD"
    if surface == "s":
        if gloss == "[Beschriftungszeichen]":
            return "O_HOLD_COMPATIBLE", "S_SIGLUM_COMPATIBLE"
        return "O_NAMED_CONTEXT_CONFLICT", "S_SEED_MATERIAL_NOT_SIGLUM"
    if surface == "d":
        if right_surface == "or":
            return "O_HOLD_COMPATIBLE", "D_RIGHT_OR_READER_BINDING_VISIBLE"
        if gloss == "Dosis":
            return "O_NAMED_CONTEXT_CONFLICT", "D_FREE_DOSE_NOT_SUFFIX_CLOSE"
        return "O_UNTESTABLE_LOCAL_BINDING", "D_FREE_QUANTITY_SIGN_NOT_ACTION"
    if surface == "r":
        if right_gloss in {"Trockenfraktion I", "trockene Fraktion I"}:
            return "O_HOLD_COMPATIBLE", "R_FOLLOWING_DRY_FRACTION_VISIBLE"
        return "O_UNTESTABLE_LOCAL_BINDING", "R_LOCAL_BINDING_CONDITION_ABSENT"
    if surface == "ok":
        if right_surface == "chey":
            return "O_HOLD_COMPATIBLE", "OK_CHEY_CONDITION_VISIBLE"
        return "O_UNTESTABLE_LOCAL_BINDING", "OK_LOCAL_LEFT_OF_CHEY_CONDITION_ABSENT"
    raise RuntimeError(surface)


def main() -> int:
    passed = 0
    failures: list[dict[str, object]] = []

    def check(condition: bool, name: str, observed: object = None, expected: object = None) -> None:
        nonlocal passed
        if condition:
            passed += 1
        else:
            failures.append({"check": name, "observed": observed, "expected": expected})

    stable_names = sorted(path.name for path in ART.iterdir() if path.is_file() and path.name != "VALIDATION.json")
    before = {name: (ART / name).read_bytes() for name in stable_names}
    rebuilt = subprocess.run(
        ["python3", str(EXP / "src/run.py")], cwd=ROOT, text=True, capture_output=True,
    )
    check(rebuilt.returncode == 0, "builder exits zero", rebuilt.stderr, "")
    after = {name: (ART / name).read_bytes() for name in stable_names}
    check(before == after, "builder byte-identical replay", sorted(after), sorted(before))

    cards = read_tsv(CARDS)
    panel = read_tsv(PANEL)
    allowlist = [row["page"] for row in read_tsv(ALLOWLIST)]
    decisions = {row["surface"]: row for row in read_tsv(DECISIONS)}
    cross_rows, guard = guarded_cross(allowlist)
    cross = {row["locus"]: row for row in cross_rows}
    card_map = {row["surface"]: row for row in cards}

    check(len(cards) == 80, "80 source cards", len(cards), 80)
    check(Counter(row["class"] for row in cards) == {"P": 53, "W": 22, "O": 5}, "source class inventory")
    check(len(panel) == 4128, "4128 panel token lines", len(panel), 4128)
    check(sum(int(row["token_count"]) for row in panel) == 32339, "32339 panel tokens")
    check(len(allowlist) == len(set(allowlist)) == 179, "179 unique allowed pages")
    check(all(not page.lower().startswith("f84") for page in allowlist), "allowlist excludes f84 prefix")
    check("f1r" not in allowlist, "f1r outside panel")
    check(guard["selected"] == len(cross_rows) == 4137, "guarded line census", len(cross_rows), 4137)
    check(guard["skipped_forbidden"] > 0, "guard rejected forbidden selectors")

    actual_occ = read_tsv(ART / "EXACT_OCCURRENCE_CONTEXTS.tsv")
    expected: list[dict[str, object]] = []
    for row in panel:
        tokens = row["zl3b_line"].split()
        glosses = row["token_glosses_de"].split(" | ")
        sources = row["gloss_sources"].split(" | ")
        states = row["scope_states"].split(" | ")
        if not any(surface in card_map for surface in tokens):
            continue
        cross_row = cross[row["locus"]]
        check(cross_row["zl3b_clean"].split() == tokens, f"ZL3b cross replay {row['locus']}")
        i_ops = operations(tokens, cross_row["it2a_clean"].split())
        r_ops = operations(tokens, cross_row["rf1b_clean"].split())
        line_unknown = unknowns(row)
        for index, surface in enumerate(tokens, start=1):
            if surface not in card_map:
                continue
            card = card_map[surface]
            right_surface = tokens[index] if index < len(tokens) else "BOUNDARY"
            right_gloss = glosses[index] if index < len(tokens) else "BOUNDARY"
            if card["class"] == "O":
                decision, reason = classify_o(surface, glosses[index - 1], right_surface, right_gloss)
                promotable = "0"
            else:
                decision, reason, promotable = decisions[surface]["decision"], "P_OR_W_MANUAL_CONTEXT_AUDIT", "1"
            i_op, i_value = i_ops[index - 1]
            r_op, r_value = r_ops[index - 1]
            support = "BOTH_EXACT" if i_op == r_op == "EXACT" else "ONE_EXACT" if "EXACT" in {i_op, r_op} else "NEITHER_EXACT"
            expected.append(
                {
                    "surface": surface, "card_class": card["class"], "page": row["page"], "locus": row["locus"],
                    "ordinal": str(index), "line_position": line_position(index, len(tokens)),
                    "was_v48_unknown": "1" if index in line_unknown else "0",
                    "target_v48_gloss_de": glosses[index - 1], "target_v48_source": sources[index - 1],
                    "target_v48_scope_state": states[index - 1], "right_surface": right_surface,
                    "right_gloss_de": right_gloss, "it2a_operation": i_op, "it2a_render": i_value,
                    "rf1b_operation": r_op, "rf1b_render": r_value, "reader_support": support,
                    "decision": decision, "reason_code": reason, "promotable": promotable,
                }
            )

    check(len(expected) == len(actual_occ) == 894, "894 exact occurrence rows")
    compared_fields = [
        "surface", "card_class", "page", "locus", "ordinal", "line_position", "was_v48_unknown",
        "target_v48_gloss_de", "target_v48_source", "target_v48_scope_state", "right_surface", "right_gloss_de",
        "it2a_operation", "it2a_render", "rf1b_operation", "rf1b_render", "reader_support", "decision",
        "reason_code", "promotable",
    ]
    for number, (want, got) in enumerate(zip(expected, actual_occ), start=1):
        for field in compared_fields:
            check(str(want[field]) == got[field], f"occurrence {number} field {field}", got[field], want[field])

    class_counts = Counter(row["card_class"] for row in actual_occ)
    decision_counts = Counter(row["decision"] for row in actual_occ)
    reader_counts = Counter(row["reader_support"] for row in actual_occ)
    check(class_counts == {"P": 155, "W": 7, "O": 732}, "occurrence class counts", class_counts)
    check(reader_counts == {"BOTH_EXACT": 432, "ONE_EXACT": 261, "NEITHER_EXACT": 201}, "reader support counts", reader_counts)
    check(decision_counts["HOLD_SAME_CARD"] + decision_counts["O_HOLD_COMPATIBLE"] == 373, "373 hold positions")
    check(decision_counts["O_NAMED_CONTEXT_CONFLICT"] == 381, "381 conflict positions")
    check(decision_counts["O_UNTESTABLE_LOCAL_BINDING"] == 140, "140 untestable positions")

    transferable = read_tsv(ART / "TRANSFERABLE_EXACT_OCCURRENCES.tsv")
    blocked = read_tsv(ART / "OCCURRENCE_SCOPED_BLOCKS.tsv")
    conflicts = read_tsv(ART / "CONTEXT_CONFLICTS.tsv")
    profile = read_tsv(ART / "CARD_PANEL_TRANSFER_PROFILE.tsv")
    overlay = read_tsv(ART / "V49_PANEL_TRANSFER_OVERLAY.tsv")
    touched = read_tsv(ART / "TOUCHED_LINE_OVERLAY.tsv")
    closed = read_tsv(ART / "NEWLY_CLOSED_LINES.tsv")
    corrections = read_tsv(ART / "F1R_OCCURRENCE_CARD_CORRECTIONS.tsv")
    refs = read_tsv(ART / "REFERENCE_SCOPE_WARNINGS.tsv")
    o_rules = read_tsv(ART / "O_CONTEXT_RULES.tsv")
    rivals = read_tsv(ART / "SEMANTIC_RIVAL_AUDIT.tsv")
    reader_rivals = read_tsv(ART / "READER_CONDITIONED_RIVALS.tsv")
    value_attachments = read_tsv(ART / "PANEL_VALUE_ATTACHMENT_AUDIT.tsv")
    check(len(transferable) == 162, "162 P/W transferable occurrences")
    check(len(blocked) == 732, "732 O occurrences isolated")
    check(len(conflicts) == 381, "381 conflict rows")
    check(len(profile) == 80, "80 card profiles")
    check(len(overlay) == 39, "39 V49 overlay cards")
    check(Counter(row["scope_state"] for row in overlay) == {"ROLE_COMPOSED_EXACT_TRANSFER": 35, "LEARNED_EXACT_WHOLE_TRANSFER": 4}, "overlay scope split")
    check(len(touched) == 156 and len({row["page"] for row in touched}) == 94, "156 touched lines on 94 pages")
    check(len(closed) == 6, "six newly closed lines")
    check(len(corrections) == 3 and sum(row["decision"] == "REVISE_F1R_OCCURRENCE" for row in corrections) == 2, "two f1r revisions plus retained join")
    check({row["locus"] for row in refs} == {"f114r.34", "f37v.23"}, "two cross-line reference bindings")
    check(len(o_rules) == 11 and sum(int(row["occurrences"]) for row in o_rules) == 732, "O rules partition 732 occurrences")
    check(len(rivals) == 3 and {row["surface"] for row in rivals} == {"shoaiin", "ytain", "yto"}, "semantic rival audit")
    check(len(reader_rivals) == 3 and {row["surface"] for row in reader_rivals} == {"sory", "kod", "daraiin"}, "reader-conditioned rival audit")
    check(len(value_attachments) == 20, "twenty value attachment decisions")
    check(Counter(row["decision"] for row in value_attachments) == {"BIND": 16, "DIRECTION_OPEN": 4}, "value attachment decision split")
    for number, attachment in enumerate(value_attachments, start=1):
        line = next(row for row in panel if row["locus"] == attachment["locus"])
        tokens = line["zl3b_line"].split()
        head = int(attachment["head_ordinal"])
        value = int(attachment["value_ordinal"])
        check(abs(head - value) == 1, f"attachment {number} adjacency")
        check(tokens[head - 1] == attachment["head_surface"], f"attachment {number} head")
        check(tokens[value - 1] == attachment["value_surface"], f"attachment {number} value")
    correction_map = {(row["locus"], row["surface"]): row for row in corrections}
    check(correction_map[("f1r.7", "s")]["v49_contextual_meaning_de"] == "Samen-/Saatgutposten", "f1r s correction")
    check(correction_map[("f1r.13", "d")]["v49_contextual_meaning_de"] == "Dosis-/Maßzeichen?", "f1r d correction")
    check(all(row["contextual_requirement"] == "CROSS_LINE_ANTECEDENT_VISIBLE" for row in refs), "cross-line references explicit")

    result = json.loads((ART / "RESULT.json").read_text(encoding="utf-8"))
    check(result["status"] == STATUS, "result status", result["status"], STATUS)
    check(result["coverage_overlay"]["unknown_positions_before"] == 8180, "unknown before")
    check(result["coverage_overlay"]["unknown_positions_after"] == 8018, "unknown after")
    check(result["coverage_overlay"]["multi_token_complete_before"] == 1242, "multi complete before")
    check(result["coverage_overlay"]["multi_token_complete_after"] == 1246, "multi complete after")
    for name, digest in result["files"].items():
        check(sha256(ART / name) == digest, f"result hash {name}", sha256(ART / name), digest)

    for rows, label in ((actual_occ, "occurrence"), (touched, "touched")):
        for number, row in enumerate(rows, start=1):
            check(not row["page"].lower().startswith("f84"), f"{label} row {number} excludes f84")

    validation = {
        "status": "PASS" if not failures else "FAIL",
        "checks_passed": passed,
        "checks_failed": len(failures),
        "failures": failures,
        "independent_reconstruction": True,
        "builder_byte_identical": before == after,
    }
    (ART / "VALIDATION.json").write_text(json.dumps(validation, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": validation["status"], "checks_passed": passed, "checks_failed": len(failures)}, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
