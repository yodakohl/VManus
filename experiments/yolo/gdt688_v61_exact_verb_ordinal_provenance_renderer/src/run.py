#!/usr/bin/env python3
"""Build V61 with exact practical-verb to written-ordinal provenance."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt688_v61_exact_verb_ordinal_provenance_renderer"
ART = BASE / "artifacts"
V60_READER = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/V60_51_LINE_READER.tsv"
V60_RESULT = ROOT / "experiments/yolo/gdt687_v60_dchey_y_dy_action_result_boundary_dispatch/artifacts/RESULT.json"
V59_READER = ROOT / "experiments/yolo/gdt686_v59_dain_daiin_qodaiin_value_head_dispatch/artifacts/V59_51_LINE_READER.tsv"
V57_LINE_AUDIT = ROOT / "experiments/yolo/gdt684_v57_complete_semantic_debt_census/artifacts/V57_51_LINE_INFORMATION_SUMMARY.tsv"
LEGACY_RULES = ROOT / "experiments/yolo/gdt684_v57_complete_semantic_debt_census/artifacts/PRACTICAL_OPERATION_RULES.tsv"
V61_RULES = BASE / "src/V61_VERB_RULES.tsv"


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def int_set(value: str) -> set[int]:
    return {int(item) for item in value.split("|") if item and item != "NONE"}


def compile_rules(rows: list[dict[str, str]], lemma_field: str) -> list[tuple[str, re.Pattern[str]]]:
    compiled = [(row[lemma_field], re.compile(row["regex"], re.IGNORECASE)) for row in rows]
    assert len({lemma for lemma, _ in compiled}) == len(compiled)
    return compiled


def occurrences(text: str, rules: list[tuple[str, re.Pattern[str]]]) -> list[dict[str, object]]:
    found = [
        {"start": match.start(), "end": match.end(), "lemma": lemma, "matched_text": match.group(0)}
        for lemma, pattern in rules for match in pattern.finditer(text)
    ]
    found.sort(key=lambda row: (int(row["start"]), int(row["end"]), str(row["lemma"])))
    for left, right in zip(found, found[1:]):
        assert int(left["end"]) <= int(right["start"]), (text, left, right)
    return found


def lemma_set(text: str, rules: list[tuple[str, re.Pattern[str]]]) -> set[str]:
    # Legacy GDT684 deliberately permits overlapping labels (notably
    # ``kühle`` as both abkühlen and kühlen); set comparison must replay that
    # behavior rather than the non-overlap invariant of the V61 scanner.
    return {lemma for lemma, pattern in rules if pattern.search(text)}


def render_with_segments(glosses: list[str]) -> tuple[str, list[dict[str, object]]]:
    """Render source order while retaining exact character spans per token."""
    text = ""
    segments: list[dict[str, object]] = []
    for ordinal, gloss in enumerate(glosses, 1):
        if gloss in {";", "."}:
            stripped = text.rstrip(" ,;.")
            for segment in segments:
                if int(segment["end"]) > len(stripped):
                    segment["end"] = len(stripped)
            text = stripped
            start = len(text)
            text += gloss
            segments.append({"ordinal": ordinal, "start": start, "end": len(text), "gloss": gloss})
            continue
        if not text:
            separator = ""
        elif text.endswith((";", ".", ":")):
            separator = " "
        else:
            separator = "; "
        text += separator
        start = len(text)
        text += gloss
        segments.append({"ordinal": ordinal, "start": start, "end": len(text), "gloss": gloss})
    if text and not text.endswith("."):
        text += "."
    text = text[:1].upper() + text[1:]
    return text, segments


def reader_mode(line_mode: str) -> str:
    return {
        "ACTION_SEQUENCE": "ARBEITSGANG",
        "MIXED_RECORD": "HYBRID_ARBEIT_UND_ZUSTAND",
        "NOMINAL_REGISTER": "ZUSTANDSLISTE",
        "QUANTITY_LABEL": "MENGEN_UND_ZUSTANDSLISTE",
    }[line_mode]


def legacy_line_stats(rows: list[dict[str, str]], rules: list[tuple[str, re.Pattern[str]]]) -> tuple[int, int]:
    pairs = 0
    lines = 0
    for row in rows:
        glosses = row["literal_token_glosses_de"].split(" | ")
        actions = int_set(row["action_ordinals"])
        licensed = lemma_set(" ".join(glosses[ordinal - 1] for ordinal in sorted(actions)), rules)
        practical = lemma_set(row["practical_translation_de"], rules)
        extra = practical - licensed
        pairs += len(extra)
        lines += int(bool(extra))
    return pairs, lines


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    v60_rows = read_tsv(V60_READER)
    v59_rows = read_tsv(V59_READER)
    v57_lines = read_tsv(V57_LINE_AUDIT)
    legacy_rules = compile_rules(read_tsv(LEGACY_RULES), "operation_lemma")
    v61_rule_rows = read_tsv(V61_RULES)
    v61_rules = compile_rules(v61_rule_rows, "canonical_lemma")
    v60_result = json.loads(V60_RESULT.read_text(encoding="utf-8"))

    assert len(v60_rows) == len(v59_rows) == len(v57_lines) == 51
    assert sum(int(row["token_count"]) for row in v60_rows) == 479
    assert sum(int(row["action_positions"]) for row in v60_rows) == 85
    assert len(v61_rules) == 32

    v61_rows: list[dict[str, object]] = []
    changed_rows: list[dict[str, object]] = []
    before_provenance: list[dict[str, object]] = []
    verb_provenance: list[dict[str, object]] = []
    action_arity: list[dict[str, object]] = []
    line_audit: list[dict[str, object]] = []
    v61_row_by_locus: dict[str, dict[str, object]] = {}

    for line in v60_rows:
        tokens = line["zl3b_line"].split()
        glosses = line["literal_token_glosses_de"].split(" | ")
        actions = int_set(line["action_ordinals"])
        assert len(tokens) == len(glosses) == int(line["token_count"])
        assert len(actions) == int(line["action_positions"])
        assert "|".join(tokens[ordinal - 1] for ordinal in sorted(actions)) == line["action_surfaces"] or (
            not actions and line["action_surfaces"] == "NONE"
        )

        strict_text, segments = render_with_segments(glosses)
        segment_by_ordinal = {int(segment["ordinal"]): segment for segment in segments}
        assert len(segment_by_ordinal) == len(tokens)
        v61_occurrences = occurrences(strict_text, v61_rules)
        old_occurrences = occurrences(line["practical_translation_de"], v61_rules)
        strict_matches_old = strict_text == line["practical_translation_de"]

        action_lemma_by_ordinal: dict[int, set[str]] = {}
        for ordinal in sorted(actions):
            local = occurrences(glosses[ordinal - 1], v61_rules)
            assert local, (line["locus"], ordinal, glosses[ordinal - 1])
            action_lemma_by_ordinal[ordinal] = {str(row["lemma"]) for row in local}
            action_arity.append({
                "page": line["page"], "locus": line["locus"], "ordinal": ordinal,
                "surface": tokens[ordinal - 1], "literal_gloss_de": glosses[ordinal - 1],
                "verb_occurrences": len(local),
                "canonical_lemmas": "|".join(str(row["lemma"]) for row in local),
                "matched_forms": "|".join(str(row["matched_text"]) for row in local),
                "provenance_status": "ALL_VERBS_FROM_THIS_EXACT_ACTION_ORDINAL",
            })

        for occurrence_index, occurrence in enumerate(old_occurrences, 1):
            if strict_matches_old:
                containers = [
                    segment for segment in segments
                    if int(segment["start"]) <= int(occurrence["start"])
                    and int(occurrence["end"]) <= int(segment["end"])
                ]
                assert len(containers) == 1
                candidates = [int(containers[0]["ordinal"])]
                status = "EXACT_RENDERER_SPAN_TO_ACTION_ORDINAL"
                assert candidates[0] in actions
            else:
                candidates = [
                    ordinal for ordinal in sorted(actions)
                    if str(occurrence["lemma"]) in action_lemma_by_ordinal[ordinal]
                ]
                status = {
                    0: "ZERO_ACTION_ORDINAL_CANDIDATE",
                    1: "ONE_LEXICAL_CANDIDATE_NO_STORED_SPAN",
                }.get(len(candidates), "MULTIPLE_LEXICAL_CANDIDATES_NO_STORED_SPAN")
            before_provenance.append({
                "page": line["page"], "locus": line["locus"], "occurrence_index": occurrence_index,
                "char_start": occurrence["start"], "char_end": occurrence["end"],
                "matched_text": occurrence["matched_text"], "canonical_lemma": occurrence["lemma"],
                "candidate_action_ordinals": "|".join(str(value) for value in candidates) if candidates else "NONE",
                "candidate_action_surfaces": "|".join(tokens[value - 1] for value in candidates) if candidates else "NONE",
                "provenance_status": status,
            })

        for occurrence_index, occurrence in enumerate(v61_occurrences, 1):
            containers = [
                segment for segment in segments
                if int(segment["start"]) <= int(occurrence["start"])
                and int(occurrence["end"]) <= int(segment["end"])
            ]
            assert len(containers) == 1, (line["locus"], occurrence, containers)
            ordinal = int(containers[0]["ordinal"])
            assert ordinal in actions, (line["locus"], occurrence, ordinal, actions)
            assert str(occurrence["lemma"]) in action_lemma_by_ordinal[ordinal]
            verb_provenance.append({
                "page": line["page"], "locus": line["locus"], "line_mode": line["line_mode"],
                "v61_reader_mode": reader_mode(line["line_mode"]), "occurrence_index": occurrence_index,
                "char_start": occurrence["start"], "char_end": occurrence["end"],
                "matched_text": occurrence["matched_text"], "canonical_lemma": occurrence["lemma"],
                "source_ordinal": ordinal, "source_surface": tokens[ordinal - 1],
                "source_literal_gloss_de": glosses[ordinal - 1], "action_licensed": 1,
                "provenance_status": "EXACT_RENDERER_SPAN_TO_ACTION_ORDINAL",
            })

        action_lemmas = {lemma for values in action_lemma_by_ordinal.values() for lemma in values}
        before_lemmas = {str(row["lemma"]) for row in old_occurrences}
        after_lemmas = {str(row["lemma"]) for row in v61_occurrences}
        before_extra = sorted(before_lemmas - action_lemmas)
        after_extra = sorted(after_lemmas - action_lemmas)
        assert not after_extra

        output: dict[str, object] = dict(line)
        output["v60_practical_translation_de"] = line["practical_translation_de"]
        output["practical_translation_de"] = strict_text
        output["v61_reader_mode"] = reader_mode(line["line_mode"])
        output["v61_renderer_revision"] = int(not strict_matches_old)
        output["v61_verb_occurrences"] = len(v61_occurrences)
        output["v61_verb_ordinals"] = "|".join(
            str(row["source_ordinal"]) for row in verb_provenance if row["locus"] == line["locus"]
        ) or "NONE"
        output["v61_provenance_status"] = "ALL_PRACTICAL_VERBS_EXACT_ACTION_ORDINAL"
        v61_rows.append(output)
        v61_row_by_locus[line["locus"]] = output

        if not strict_matches_old:
            changed_rows.append({
                "page": line["page"], "locus": line["locus"], "line_mode": line["line_mode"],
                "v61_reader_mode": reader_mode(line["line_mode"]), "token_count": line["token_count"],
                "action_ordinals": line["action_ordinals"], "action_surfaces": line["action_surfaces"],
                "v60_practical_translation_de": line["practical_translation_de"],
                "v61_practical_translation_de": strict_text,
                "v60_verb_occurrences": len(old_occurrences), "v61_verb_occurrences": len(v61_occurrences),
                "v60_extra_lemmas": "|".join(before_extra) if before_extra else "NONE",
                "v61_extra_lemmas": "NONE",
                "revision_reason": "REMOVE_ZERO_SOURCE_VERBS" if before_extra else "NORMALIZE_RENDERER_SPAN_PROVENANCE",
            })

        status_counts = Counter(
            str(row["provenance_status"]) for row in before_provenance if row["locus"] == line["locus"]
        )
        line_audit.append({
            "page": line["page"], "locus": line["locus"], "line_mode": line["line_mode"],
            "v61_reader_mode": reader_mode(line["line_mode"]), "token_count": line["token_count"],
            "action_positions": line["action_positions"], "v60_verb_occurrences": len(old_occurrences),
            "v61_verb_occurrences": len(v61_occurrences),
            "v60_exact_span_verbs": status_counts["EXACT_RENDERER_SPAN_TO_ACTION_ORDINAL"],
            "v60_one_candidate_without_span": status_counts["ONE_LEXICAL_CANDIDATE_NO_STORED_SPAN"],
            "v60_multiple_candidates_without_span": status_counts["MULTIPLE_LEXICAL_CANDIDATES_NO_STORED_SPAN"],
            "v60_zero_candidate_verbs": status_counts["ZERO_ACTION_ORDINAL_CANDIDATE"],
            "v60_extra_lemmas": "|".join(before_extra) if before_extra else "NONE",
            "v61_extra_lemmas": "NONE", "v61_changed": int(not strict_matches_old),
            "v61_status": "ALL_VERBS_EXACT_ACTION_ORDINAL",
        })

    assert len(v61_rows) == 51
    assert len(changed_rows) == 10
    assert {row["locus"] for row in changed_rows if row["revision_reason"] == "REMOVE_ZERO_SOURCE_VERBS"} == {"f114v.36", "f75r.3"}
    assert len(before_provenance) == 116
    assert Counter(row["provenance_status"] for row in before_provenance) == {
        "EXACT_RENDERER_SPAN_TO_ACTION_ORDINAL": 95,
        "ONE_LEXICAL_CANDIDATE_NO_STORED_SPAN": 7,
        "MULTIPLE_LEXICAL_CANDIDATES_NO_STORED_SPAN": 10,
        "ZERO_ACTION_ORDINAL_CANDIDATE": 4,
    }
    assert len(verb_provenance) == 113
    assert len(action_arity) == 85
    assert Counter(int(row["verb_occurrences"]) for row in action_arity) == {1: 65, 2: 12, 3: 8}
    assert len({row["locus"] for row in verb_provenance}) == 39
    assert Counter(row["v61_reader_mode"] for row in v61_rows) == {
        "ARBEITSGANG": 16, "HYBRID_ARBEIT_UND_ZUSTAND": 23,
        "ZUSTANDSLISTE": 6, "MENGEN_UND_ZUSTANDSLISTE": 6,
    }

    v61_fields = list(v60_rows[0]) + [
        "v60_practical_translation_de", "v61_reader_mode", "v61_renderer_revision",
        "v61_verb_occurrences", "v61_verb_ordinals", "v61_provenance_status",
    ]
    write_tsv(output_dir / "V61_51_LINE_READER.tsv", v61_rows, v61_fields)
    write_tsv(output_dir / "V61_10_RERENDERED_LINES.tsv", changed_rows, list(changed_rows[0]))
    write_tsv(output_dir / "V60_BEFORE_116_VERB_PROVENANCE.tsv", before_provenance, list(before_provenance[0]))
    write_tsv(output_dir / "V61_113_VERB_OCCURRENCE_PROVENANCE.tsv", verb_provenance, list(verb_provenance[0]))
    write_tsv(output_dir / "V61_85_ACTION_POSITION_ARITY.tsv", action_arity, list(action_arity[0]))
    write_tsv(output_dir / "V61_51_LINE_VERB_AUDIT.tsv", line_audit, list(line_audit[0]))

    v57_pairs = sum(int(row["extra_practical_operation_count"]) for row in v57_lines)
    v57_extra_lines = sum(int(row["extra_practical_operation_count"]) > 0 for row in v57_lines)
    v59_pairs, v59_extra_lines = legacy_line_stats(v59_rows, legacy_rules)
    v60_pairs, v60_extra_lines = legacy_line_stats(v60_rows, legacy_rules)
    v61_pairs, v61_extra_lines = legacy_line_stats(
        [{**row, "practical_translation_de": str(row["practical_translation_de"])} for row in v61_rows], legacy_rules
    )
    assert (v57_pairs, v57_extra_lines, v59_pairs, v59_extra_lines, v60_pairs, v60_extra_lines, v61_pairs, v61_extra_lines) == (
        74, 29, 66, 28, 4, 2, 0, 0
    )
    comparison_rows = [
        {"phase": "GDT684_V57", "source_action_positions": 86, "extra_legacy_lemma_line_pairs": 74, "lines_with_extra": 29, "interpretation": "original fluent renderer debt"},
        {"phase": "GDT686_V59", "source_action_positions": 86, "extra_legacy_lemma_line_pairs": 66, "lines_with_extra": 28, "interpretation": "eight pairs already removed before V60"},
        {"phase": "GDT687_V60", "source_action_positions": 85, "extra_legacy_lemma_line_pairs": 4, "lines_with_extra": 2, "interpretation": "GDT687 strict rerender removed another 62; the published next-route 66 was stale V59 scope"},
        {"phase": "GDT688_V61", "source_action_positions": 85, "extra_legacy_lemma_line_pairs": 0, "lines_with_extra": 0, "interpretation": "all 51 lines use one exact token-span renderer"},
    ]
    write_tsv(output_dir / "LEGACY_ACTION_LEAKAGE_COMPARISON.tsv", comparison_rows, list(comparison_rows[0]))

    counter_rows = [
        {"case": "f114v.36", "v60_failure": "two written take actions collapsed to one; verbinden and abschließen had zero source", "v61_resolution": "both take verbs remain separate; zero-source verbs removed"},
        {"case": "f75r.3", "v60_failure": "trocknen and bringen were created from nominal state cards", "v61_resolution": "only nehmen plus einweichen/erhitzen/abschließen remain verbs"},
        {"case": "f80r.17", "v60_failure": "three identical sheky actions gave ten lexical multi-candidates without stored spans", "v61_resolution": "each occurrence is contained in its exact token-ordinal segment"},
        {"case": "ytol kühle ... ab", "v60_failure": "legacy deck counted one span as both abkühlen and kühlen", "v61_resolution": "separable form belongs only to canonical abkühlen"},
        {"case": "GDT687 next-route count", "v60_failure": "66 extra pairs described the V59 input, not the generated V60 reader", "v61_resolution": "executable comparison fixes the sequence at 74→66→4→0"},
        {"case": "multi-verb action cards", "v60_failure": "one action ordinal was implicitly treated as one possible verb", "v61_resolution": "65 cards carry one verb, 12 carry two and 8 carry three"},
    ]
    write_tsv(output_dir / "COUNTEREXAMPLE_AUDIT.tsv", counter_rows, list(counter_rows[0]))

    reader_doc = [
        "# GDT688 — V61 exact-verb workshop reader", "",
        "Every practical verb below is emitted inside one written token span whose exact ordinal is action-licensed. "
        "The mode label is metadata, not manuscript plaintext.", "",
        "```text", "ARBEITSGANG                 = inherited ACTION_SEQUENCE",
        "HYBRID_ARBEIT_UND_ZUSTAND = inherited MIXED_RECORD",
        "ZUSTANDSLISTE              = inherited NOMINAL_REGISTER",
        "MENGEN_UND_ZUSTANDSLISTE   = inherited QUANTITY_LABEL", "```", "",
    ]
    for mode in ("ARBEITSGANG", "HYBRID_ARBEIT_UND_ZUSTAND", "ZUSTANDSLISTE", "MENGEN_UND_ZUSTANDSLISTE"):
        reader_doc.extend([f"## {mode}", ""])
        for line in v61_rows:
            if line["v61_reader_mode"] != mode:
                continue
            reader_doc.extend([
                f"### {line['locus']}", "", f"`{line['zl3b_line']}`", "",
                str(line["practical_translation_de"]), "",
                f"Aktionsordinale: `{line['action_ordinals']}`; Verbordinale: `{line['v61_verb_ordinals']}`.", "",
            ])
    (output_dir / "GDT688_V61_WORKSHOP_READER.md").write_text("\n".join(reader_doc).rstrip() + "\n", encoding="utf-8")

    generated_files = {
        "COUNTEREXAMPLE_AUDIT.tsv",
        "GDT688_V61_WORKSHOP_READER.md",
        "LEGACY_ACTION_LEAKAGE_COMPARISON.tsv",
        "V60_BEFORE_116_VERB_PROVENANCE.tsv",
        "V61_10_RERENDERED_LINES.tsv",
        "V61_113_VERB_OCCURRENCE_PROVENANCE.tsv",
        "V61_51_LINE_READER.tsv",
        "V61_51_LINE_VERB_AUDIT.tsv",
        "V61_85_ACTION_POSITION_ARITY.tsv",
    }
    assert all((output_dir / name).is_file() for name in generated_files)
    result = {
        "status": "PASS_V61_113_OF_113_PRACTICAL_VERBS_EXACT_ACTION_ORDINAL__LEGACY_LEAKAGE_74_TO_66_TO_4_TO_0",
        "basis": {
            "lines": 51, "positions": 479, "source_action_positions": 85,
            "action_bearing_lines": 39, "non_action_lines": 12,
            "v60_practical_verb_occurrences": 116, "v61_practical_verb_occurrences": 113,
            "new_pages": 0, "f84_access": 0, "f84r_access": 0,
        },
        "v60_before": {
            "exact_span_to_action_ordinal": 95,
            "one_lexical_candidate_without_span": 7,
            "multiple_lexical_candidates_without_span": 10,
            "zero_action_ordinal_candidate": 4,
            "legacy_extra_lemma_line_pairs": 4, "lines_with_legacy_extra": 2,
        },
        "v61": {
            "exact_span_to_action_ordinal": 113, "unmapped_verbs": 0,
            "action_positions_with_at_least_one_verb": 85,
            "action_position_verb_arity": {"one": 65, "two": 12, "three": 8},
            "renderer_revised_lines": 10, "semantic_card_revisions": 0,
            "legacy_extra_lemma_line_pairs": 0, "lines_with_legacy_extra": 0,
            "reader_modes": {"work": 16, "hybrid": 23, "state_list": 6, "quantity_state_list": 6},
            "strict_debt_positions": int(v60_result["v60"]["strict_debt_positions_after"]),
            "mechanical_debt_union": int(v60_result["v60"]["mechanical_debt_union_after"]),
            "four_layer_union": int(v60_result["v60"]["four_layer_union_after"]),
        },
        "correction": "GDT687's prose named 66 as the next starting scope. Executable replay shows 66 was V59; GDT687's generated V60 already reduced it to four on two untouched lines.",
        "claim_ceiling": "V61 proves renderer provenance only: every detected practical German verb is copied from one exact written action ordinal. It changes no token meaning or action license and does not prove that any German verb is historical plaintext.",
        "files": {name: sha256(output_dir / name) for name in sorted(generated_files)},
    }
    write_json(output_dir / "RESULT.json", result)
    return result


def main() -> int:
    result = build(ART)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
