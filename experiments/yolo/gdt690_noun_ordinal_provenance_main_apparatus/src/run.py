#!/usr/bin/env python3
"""Build V63: exact noun spans, compact main text, and a rival apparatus."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE = ROOT / "experiments/yolo/gdt690_noun_ordinal_provenance_main_apparatus"
ART = BASE / "artifacts"
SRC = BASE / "src"
V62_READER = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts/V62_51_LINE_READER.tsv"
V62_RESULT = ROOT / "experiments/yolo/gdt689_v62_bound_dy_sister_endpoint_dispatch/artifacts/RESULT.json"
G635_DICT = ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/WORKING_DICTIONARY_V12.tsv"
G636_DICT = ROOT / "experiments/yolo/gdt636_residual_four_head_semantics/artifacts/WORKING_DICTIONARY_V13.tsv"
G635_GRID = ROOT / "experiments/yolo/gdt635_initial_head_same_remainder_swaps/artifacts/CONCRETE_FOUR_HEAD_PARADIGMS.tsv"
G636_GRID = ROOT / "experiments/yolo/gdt636_residual_four_head_semantics/artifacts/RESIDUAL_76_FORM_GRID.tsv"
G685_STATE = ROOT / "experiments/yolo/gdt685_v58_ch_sh_t_ol_ansatz_dispatch/artifacts/SURFACE_STATE_DISPATCH_SUMMARY.tsv"
RENDER_RULES = SRC / "V63_NOUN_RENDER_RULES.tsv"
NOUN_LEXICON = SRC / "V63_NOUN_LEXICON.tsv"
NON_NOUN_ALLOWLIST = SRC / "V63_NON_NOUN_ALLOWLIST.tsv"
HISTORICAL_RIVALS = SRC / "HISTORICAL_NOUN_RIVALS.tsv"

WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")
PRODUCTIVE_HEAD_RE = re.compile(r"^(p|s|r|l).+")
FOCUS_SURFACES = {
    "GUMMI": {"shx"},
    "BLUETE": {"fchoky", "fdar", "shor", "shoral", "ofchedy", "dshor"},
    "WURZEL": {"r", "rr", "raiin", "ram"},
    "CTH_MATERIAL": {"checthy"},
    "RAHMEN": {"qotain", "otain", "otaiin", "okain", "okaiin"},
    "HOLZBINDUNG": {"olkar", "olam"},
}
CTH_FAMILY = {"cthoor", "cthororaiin", "ykecthey", "checthy", "checthedy", "chcthey"}
STATE_NULL_SURFACES = {"chol", "shol", "tol"}


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        if not rows:
            raise ValueError(f"Cannot infer fields for empty TSV {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_with_segments(glosses: list[str]) -> tuple[str, list[dict[str, object]]]:
    """Render one line while retaining exact character spans per token."""
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
        separator = "" if not text else (" " if text.endswith((";", ".", ":")) else "; ")
        text += separator
        start = len(text)
        text += gloss
        segments.append({"ordinal": ordinal, "start": start, "end": len(text), "gloss": gloss})
    if text and not text.endswith("."):
        text += "."
    if text:
        text = text[:1].upper() + text[1:]
    return text, segments


def productive_head(surface: str) -> str:
    if surface.startswith("sh") or not PRODUCTIVE_HEAD_RE.match(surface):
        return "NONE"
    return surface[0]


def focus_family(surface: str) -> str:
    hits = [name for name, surfaces in FOCUS_SURFACES.items() if surface in surfaces]
    assert len(hits) <= 1
    return hits[0] if hits else "NONE"


def load_word_classes() -> tuple[dict[str, dict[str, str]], dict[str, str]]:
    noun_by_form: dict[str, dict[str, str]] = {}
    for row in read_tsv(NOUN_LEXICON):
        for form in row["normalized_forms"].split("|"):
            assert form and form not in noun_by_form, form
            noun_by_form[form] = row
    non_noun_by_form: dict[str, str] = {}
    for row in read_tsv(NON_NOUN_ALLOWLIST):
        for form in row["normalized_forms"].split("|"):
            assert form and form not in non_noun_by_form, form
            non_noun_by_form[form] = row["class"]
    assert not (set(noun_by_form) & set(non_noun_by_form))
    return noun_by_form, non_noun_by_form


def source_index() -> dict[str, list[dict[str, str]]]:
    index: dict[str, list[dict[str, str]]] = defaultdict(list)
    specifications = [
        ("GDT635", G635_DICT, "entry", "working_meaning_de"),
        ("GDT636", G636_DICT, "entry", "working_meaning_de"),
        ("GDT635", G635_GRID, "form", "working_default_de"),
        ("GDT636", G636_GRID, "form", "working_default_de"),
        ("GDT685", G685_STATE, "surface", "default_de"),
    ]
    for experiment, path, key_field, gloss_field in specifications:
        rows = read_tsv(path)
        assert rows and key_field in rows[0] and gloss_field in rows[0]
        for row in rows:
            key = row[key_field]
            if not key or any(mark in key for mark in "/+()"):
                continue
            index[key].append({
                "source_experiment": experiment,
                "source_artifact": str(path.relative_to(ROOT)),
                "source_key": key,
                "source_gloss_de": row[gloss_field],
            })
    return index


def source_summary(surface: str, gloss: str, index: dict[str, list[dict[str, str]]]) -> dict[str, object]:
    records = index.get(surface, [])
    exact = [row for row in records if row["source_gloss_de"] == gloss]
    head = productive_head(surface)
    if exact:
        match = "EXACT_GLOSS"
    elif records:
        match = "EXACT_SURFACE_ONLY"
    elif head != "NONE":
        match = "HEAD_ONLY"
    else:
        match = "NONE"
    return {
        "upstream_source_match": match,
        "upstream_source_records": len(records),
        "upstream_source_experiments": "|".join(sorted({row["source_experiment"] for row in records})) or "NONE",
        "upstream_source_artifacts": "|".join(sorted({row["source_artifact"] for row in records})) or "NONE",
        "upstream_source_glosses_de": " || ".join(sorted({row["source_gloss_de"] for row in records})) or "NONE",
        "productive_initial_head": head,
        "upstream_card_status": "EXPORTED" if records else "UPSTREAM_CARD_NOT_EXPORTED_IN_GDT690_SCOPE",
    }


def word_rows(
    *, phase: str, page: str, locus: str, ordinal: int, surface: str, gloss: str,
    segment_start: int, line_text: str, noun_by_form: dict[str, dict[str, str]],
    token_meta: dict[str, object],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for match in WORD_RE.finditer(gloss):
        normalized = match.group(0).casefold()
        if normalized not in noun_by_form:
            continue
        lex = noun_by_form[normalized]
        line_start = segment_start + match.start()
        line_end = segment_start + match.end()
        actual = line_text[line_start:line_end]
        assert actual.casefold() == match.group(0).casefold(), (locus, ordinal, actual, match.group(0))
        rows.append({
            "phase": phase, "page": page, "locus": locus, "token_ordinal": ordinal,
            "surface": surface, "token_char_start": match.start(), "token_char_end": match.end(),
            "line_char_start": line_start, "line_char_end": line_end, "noun_surface_de": actual,
            "normalized_form": normalized, "canonical_noun_de": lex["canonical_noun_de"],
            "noun_class": lex["noun_class"], "content_status": lex["content_status"],
            "token_gloss_de": gloss, **token_meta,
        })
    return rows


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    reader_rows = read_tsv(V62_READER)
    v62_result = json.loads(V62_RESULT.read_text(encoding="utf-8"))
    render_rule_rows = read_tsv(RENDER_RULES)
    render_by_surface = {row["surface"]: row for row in render_rule_rows}
    assert len(render_by_surface) == len(render_rule_rows) == 72
    noun_by_form, non_noun_by_form = load_word_classes()
    sources = source_index()

    assert len(reader_rows) == 51
    assert sum(int(row["token_count"]) for row in reader_rows) == 479
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in reader_rows)

    used_rules: Counter[str] = Counter()
    word_type_counts: Counter[tuple[str, str, str]] = Counter()
    token_rows: list[dict[str, object]] = []
    source_nouns: list[dict[str, object]] = []
    main_nouns: list[dict[str, object]] = []
    line_rows: list[dict[str, object]] = []

    for source_line in reader_rows:
        tokens = source_line["zl3b_line"].split()
        source_glosses = source_line["v62_literal_token_glosses_de"].split(" | ")
        assert len(tokens) == len(source_glosses) == int(source_line["token_count"])
        main_glosses: list[str] = []
        rules_for_line: list[dict[str, str] | None] = []
        for surface, source_gloss in zip(tokens, source_glosses):
            rule = render_by_surface.get(surface)
            if rule:
                assert source_gloss == rule["expected_v62_gloss_de"], (source_line["locus"], surface, source_gloss)
                main_glosses.append(rule["main_gloss_de"])
                used_rules[rule["rule_id"]] += 1
            else:
                main_glosses.append(source_gloss)
            rules_for_line.append(rule)

        source_text, source_segments = render_with_segments(source_glosses)
        main_text, main_segments = render_with_segments(main_glosses)
        assert len(source_segments) == len(main_segments) == len(tokens)
        main_apparatus: list[str] = []
        line_changed = 0

        for ordinal, packed in enumerate(zip(tokens, source_glosses, main_glosses, rules_for_line, source_segments, main_segments), 1):
            surface, source_gloss, main_gloss, rule, source_segment, main_segment = packed
            src = source_summary(surface, source_gloss, sources)
            family = focus_family(surface)
            changed = int(source_gloss != main_gloss)
            line_changed += changed
            if rule:
                tier = rule["provenance_tier"]
            elif src["productive_initial_head"] != "NONE":
                tier = "PRODUCTIVE_INITIAL_HEAD"
            elif src["upstream_source_match"] == "EXACT_GLOSS":
                tier = "INHERITED_EXACT_UPSTREAM_GLOSS"
            elif src["upstream_source_match"] == "EXACT_SURFACE_ONLY":
                tier = "INHERITED_EXACT_SURFACE_ONLY"
            else:
                tier = "INHERITED_V62_GLOSS__UPSTREAM_CARD_UNEXPORTED"
            selected = rule["selected_noun_de"] if rule else "INHERITED"
            rivals = rule["live_rivals_de"] if rule else "NONE"
            note = rule["apparatus_note_de"] if rule else "NONE"
            token_meta: dict[str, object] = {
                "focus_family": family, "cth_family": int(surface in CTH_FAMILY),
                "renderer_rule_id": rule["rule_id"] if rule else "NONE", "renderer_changed": changed,
                "selected_head_de": selected, "live_rivals_de": rivals, "provenance_tier": tier,
                "apparatus_note_de": note, **src,
            }
            token_rows.append({
                "page": source_line["page"], "locus": source_line["locus"], "token_ordinal": ordinal,
                "surface": surface, "v62_token_gloss_de": source_gloss, "v63_main_token_gloss_de": main_gloss,
                **token_meta,
            })
            source_nouns.extend(word_rows(
                phase="V62_SOURCE", page=source_line["page"], locus=source_line["locus"], ordinal=ordinal,
                surface=surface, gloss=source_gloss, segment_start=int(source_segment["start"]), line_text=source_text,
                noun_by_form=noun_by_form, token_meta=token_meta,
            ))
            main_nouns.extend(word_rows(
                phase="V63_MAIN", page=source_line["page"], locus=source_line["locus"], ordinal=ordinal,
                surface=surface, gloss=main_gloss, segment_start=int(main_segment["start"]), line_text=main_text,
                noun_by_form=noun_by_form, token_meta=token_meta,
            ))
            if rule:
                main_apparatus.append(
                    f"#{ordinal} {surface}: {rule['selected_noun_de']}"
                    f" [Rivalen: {rule['live_rivals_de']}; {rule['provenance_tier']}]"
                )
            for phase, gloss in (("V62_SOURCE", source_gloss), ("V63_MAIN", main_gloss)):
                for word in WORD_RE.finditer(gloss):
                    normalized = word.group(0).casefold()
                    if normalized in noun_by_form:
                        word_class = "NOUN"
                    elif normalized in non_noun_by_form:
                        word_class = non_noun_by_form[normalized]
                    else:
                        raise AssertionError((phase, source_line["locus"], ordinal, surface, normalized))
                    word_type_counts[(phase, normalized, word_class)] += 1

        line_rows.append({
            "page": source_line["page"], "locus": source_line["locus"], "section": source_line["section"],
            "language": source_line["language"], "hand": source_line["hand"], "token_count": len(tokens),
            "zl3b_line": source_line["zl3b_line"], "v62_practical_translation_de": source_text,
            "v63_main_translation_de": main_text, "v63_changed_token_positions": line_changed,
            "v63_noun_occurrences": sum(1 for row in main_nouns if row["locus"] == source_line["locus"]),
            "v63_apparatus_entries": len(main_apparatus),
            "v63_compact_apparatus_de": " || ".join(main_apparatus) or "NONE",
            "v63_status": "EVERY_MAIN_NOUN_EXACT_WRITTEN_ORDINAL",
        })

    assert set(used_rules) == {row["rule_id"] for row in render_rule_rows}
    assert len(token_rows) == 479
    assert len({(row["locus"], row["token_ordinal"]) for row in token_rows}) == 479
    assert len({(row["locus"], row["token_ordinal"], row["line_char_start"], row["line_char_end"]) for row in main_nouns}) == len(main_nouns)
    assert not any(row["content_status"] == "APPARATUS_ONLY" for row in main_nouns)
    assert not any("/" in row["v63_main_token_gloss_de"] or " oder " in row["v63_main_token_gloss_de"] for row in token_rows)

    source_meta = [row for row in source_nouns if row["content_status"] == "APPARATUS_ONLY"]
    changed_tokens = [row for row in token_rows if row["renderer_changed"]]
    head_tokens = [row for row in token_rows if row["productive_initial_head"] != "NONE"]
    assert len(head_tokens) == 36
    assert Counter(row["productive_initial_head"] for row in head_tokens) == {"l": 19, "s": 9, "p": 5, "r": 3}
    state_null = [row for row in token_rows if row["surface"] in STATE_NULL_SURFACES]
    state_null_nouns = [row for row in main_nouns if row["surface"] in STATE_NULL_SURFACES]
    assert len(state_null) == 8 and not state_null_nouns

    focus_counts = Counter(row["focus_family"] for row in token_rows if row["focus_family"] != "NONE")
    assert focus_counts == {"HOLZBINDUNG": 20, "RAHMEN": 12, "BLUETE": 8, "WURZEL": 4, "GUMMI": 1, "CTH_MATERIAL": 1}
    assert sum(focus_counts.values()) == 46

    word_rows_out = [
        {"phase": phase, "normalized_form": form, "word_class": word_class, "occurrences": count}
        for (phase, form, word_class), count in sorted(word_type_counts.items())
    ]
    source_match_counts = Counter(row["upstream_source_match"] for row in token_rows)
    source_noun_match_counts = Counter(row["upstream_source_match"] for row in source_nouns)
    main_tier_counts = Counter(row["provenance_tier"] for row in main_nouns)
    main_class_counts = Counter(row["noun_class"] for row in main_nouns)

    focus_rows: list[dict[str, object]] = []
    for family in FOCUS_SURFACES:
        family_tokens = [row for row in token_rows if row["focus_family"] == family]
        family_nouns = [row for row in main_nouns if row["focus_family"] == family]
        focus_rows.append({
            "focus_family": family, "token_positions": len(family_tokens),
            "surfaces": len({row["surface"] for row in family_tokens}), "main_noun_spans": len(family_nouns),
            "changed_positions": sum(int(row["renderer_changed"]) for row in family_tokens),
            "exact_gloss_positions": sum(row["upstream_source_match"] == "EXACT_GLOSS" for row in family_tokens),
            "exact_surface_only_positions": sum(row["upstream_source_match"] == "EXACT_SURFACE_ONLY" for row in family_tokens),
            "head_only_positions": sum(row["upstream_source_match"] == "HEAD_ONLY" for row in family_tokens),
            "unexported_positions": sum(row["upstream_source_match"] == "NONE" for row in family_tokens),
            "main_selected_heads": "|".join(sorted({str(row["selected_head_de"]) for row in family_tokens})),
            "apparatus_rivals": "|".join(sorted({str(row["live_rivals_de"]) for row in family_tokens})),
        })

    write_tsv(output_dir / "V63_479_TOKEN_NOUN_BINDING.tsv", token_rows)
    write_tsv(output_dir / "V62_SOURCE_NOUN_OCCURRENCE_AUDIT.tsv", source_nouns)
    write_tsv(output_dir / "V63_MAIN_NOUN_OCCURRENCE_PROVENANCE.tsv", main_nouns)
    write_tsv(output_dir / "V63_51_LINE_MAIN_AND_APPARATUS.tsv", line_rows)
    write_tsv(output_dir / "V63_WORD_CLASS_CENSUS.tsv", word_rows_out)
    write_tsv(output_dir / "V63_SIX_FOCUS_FAMILY_SUMMARY.tsv", focus_rows)
    historical_rows = read_tsv(HISTORICAL_RIVALS)
    assert len(historical_rows) == 12
    write_tsv(output_dir / "HISTORICAL_NOUN_RIVALS.tsv", historical_rows)

    reader_doc = [
        "# GDT690 V63 — konkrete Hauptfassung mit Nomenapparat", "",
        "Jedes Haupttextnomen ist an genau eine sichtbare Tokenposition gebunden. Rivalen und strukturelle Hilfsbegriffe stehen im Apparat, nicht im Rezepttext.", "",
    ]
    for line in line_rows:
        reader_doc.extend([
            f"## {line['locus']}", "", f"`{line['zl3b_line']}`", "", str(line["v63_main_translation_de"]), "",
            f"Apparat: {line['v63_compact_apparatus_de']}", "",
        ])
    (output_dir / "GDT690_V63_CONCRETE_NOUN_READER.md").write_text("\n".join(reader_doc).rstrip() + "\n", encoding="utf-8")

    comparison_rows = [
        {"dimension": "spoken structural metanouns", "v62_before": len(source_meta), "v63_after": 0,
         "interpretation": "Holzbindung, Rahmen, CTH/Herbal, Eintrag and abstract alternatives moved to apparatus"},
        {"dimension": "slash-or alternative token positions",
         "v62_before": sum("/" in row["v62_token_gloss_de"] or " oder " in row["v62_token_gloss_de"] for row in token_rows),
         "v63_after": 0, "interpretation": "one main noun selected; rivals preserved separately"},
        {"dimension": "exact noun spans bound to a written ordinal", "v62_before": len(source_nouns), "v63_after": len(main_nouns),
         "interpretation": "both phases are span-addressable; V63 removes alternatives and meta spans"},
        {"dimension": "productive p/s/r/l head token positions", "v62_before": len(head_tokens), "v63_after": len(head_tokens),
         "interpretation": "same 36 positions; main heads normalized to Pulver/Samen/Wurzel/Holz"},
        {"dimension": "chol/shol/tol state cells emitting nouns", "v62_before": 0, "v63_after": 0,
         "interpretation": "GDT685 no-universal-Ansatz guard retained"},
    ]
    write_tsv(output_dir / "V62_TO_V63_NOUN_RENDER_COMPARISON.tsv", comparison_rows)

    generated = {
        "GDT690_V63_CONCRETE_NOUN_READER.md", "HISTORICAL_NOUN_RIVALS.tsv", "V62_SOURCE_NOUN_OCCURRENCE_AUDIT.tsv",
        "V62_TO_V63_NOUN_RENDER_COMPARISON.tsv", "V63_479_TOKEN_NOUN_BINDING.tsv",
        "V63_51_LINE_MAIN_AND_APPARATUS.tsv", "V63_MAIN_NOUN_OCCURRENCE_PROVENANCE.tsv",
        "V63_SIX_FOCUS_FAMILY_SUMMARY.tsv", "V63_WORD_CLASS_CENSUS.tsv",
    }
    input_paths = [
        V62_READER, V62_RESULT, G635_DICT, G636_DICT, G635_GRID, G636_GRID, G685_STATE,
        RENDER_RULES, NOUN_LEXICON, NON_NOUN_ALLOWLIST, HISTORICAL_RIVALS, Path(__file__).resolve(),
    ]
    result = {
        "status": "PASS_V63_ALL_MAIN_NOUNS_EXACT_ORDINAL__ONE_MAIN_HEAD_PLUS_RIVAL_APPARATUS",
        "basis": {"lines": 51, "token_positions": 479, "pages": len({row["page"] for row in token_rows}),
                  "new_pages": 0, "f84_access": 0, "f84r_access": 0, "render_rules": len(render_rule_rows),
                  "rule_touched_positions": sum(used_rules.values()), "changed_token_positions": len(changed_tokens)},
        "noun_inventory": {"v62_source_noun_occurrences": len(source_nouns), "v63_main_noun_occurrences": len(main_nouns),
                           "v63_noun_bearing_token_positions": len({(row["locus"], row["token_ordinal"]) for row in main_nouns}),
                           "v63_canonical_nouns": len({row["canonical_noun_de"] for row in main_nouns}),
                           "main_noun_classes": dict(sorted(main_class_counts.items())),
                           "main_provenance_tiers": dict(sorted(main_tier_counts.items()))},
        "upstream_provenance": {"token_position_source_matches": dict(sorted(source_match_counts.items())),
                                "v62_noun_occurrence_source_matches": dict(sorted(source_noun_match_counts.items())),
                                "explicit_unexported_status": True,
                                "interpretation": "written ordinal provenance is complete; upstream card provenance remains incomplete and is never fabricated"},
        "main_decisions": {"productive_heads": {"p": "Pulver", "s": "Samen", "r": "Wurzel", "l": "Holz"},
                           "shx": "Gummi", "shor": "Blüte", "checthy": "Kraut", "qotain": "kalter Ansatz, Grad II",
                           "olkar": "erste erhitzte Holzfraktion im Ansatz (provisional local scope head)",
                           "olam": "ein Maß Holz (provisional local scope head)"},
        "historical_comparator": {"rows": len(historical_rows), "role": "short-head and rival calibration only",
                                  "sources": len({row["primary_source_url"] for row in historical_rows})},
        "renderer_cleanup": {"source_apparatus_only_noun_occurrences": len(source_meta),
                             "main_apparatus_only_noun_occurrences": 0,
                             "source_slash_or_positions": comparison_rows[1]["v62_before"], "main_slash_or_positions": 0,
                             "focus_token_positions": dict(sorted(focus_counts.items())),
                             "state_null_positions": len(state_null), "state_null_nouns": 0},
        "inherited_debt": {"strict": int(v62_result["semantic_debt"]["strict"]),
                           "mechanical_union": int(v62_result["semantic_debt"]["mechanical_union"]),
                           "four_layer_union": int(v62_result["semantic_debt"]["four_layer_union"])},
        "claim_ceiling": "V63 is a concrete working renderer, not a decipherment. It proves that every selected German noun in the 51-line main text is copied inside one exact written token ordinal. Productive p/s/r/l heads retain their scoped GDT635/636 licenses; local Gummi/Blüte/Kraut and bounded olkar/olam Holz readings remain explicit working selections with rivals. Missing upstream cards are marked, never invented.",
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
        "files": {},
    }
    for name in sorted(generated):
        result["files"][name] = sha256(output_dir / name)
    write_json(output_dir / "RESULT.json", result)
    return result


def main() -> int:
    result = build(Path(os.environ.get("GDT690_OUTPUT_DIR", ART)))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
