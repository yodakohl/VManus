#!/usr/bin/env python3
"""Build the V67 zero-Fraktion working reader from 22 exact migration cards."""

from __future__ import annotations

import csv
import hashlib
import json
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
BASE = ROOT / "experiments/yolo/gdt694_residual_fraction_share_migration"
SRC = BASE / "src"
ART = BASE / "artifacts"
G693 = ROOT / "experiments/yolo/gdt693_ar_head_semantic_tournament"

TOKENS = G693 / "artifacts/V66_479_TOKEN_SELECTED_SHARE_READER.tsv"
LINES = G693 / "artifacts/V66_51_LINE_SELECTED_SHARE_READER.tsv"
RESIDUALS = G693 / "artifacts/V66_22_RESIDUAL_FRACTION_BEARING_OCCURRENCES.tsv"
VERBS = G693 / "artifacts/V66_113_SELECTED_VERB_PRESERVATION.tsv"
OLD_SPANS = G693 / "artifacts/V66_2_SELECTED_BOUND_SPANS.tsv"
PRODUCT_RIVALS = G693 / "artifacts/V66_6_SELECTED_PRODUCT_RIVALS.tsv"
G693_RESULT = G693 / "artifacts/RESULT.json"
RULES = SRC / "V67_22_RESIDUAL_SHARE_RULES.tsv"
NEW_SPAN = SRC / "V67_ADDITIONAL_BOUND_SPAN.tsv"
PROVENANCE_REPORTS = tuple(
    ROOT / path for path in (
        "experiments/yolo/gdt639_strict_hole_component_repair/REPORT.md",
        "experiments/yolo/gdt648_strict_v24_hole_completion/REPORT.md",
        "experiments/yolo/gdt652_strict_v28_frontier_completion/REPORT.md",
        "experiments/yolo/gdt654_ar_or_surface_consolidation/REPORT.md",
        "experiments/yolo/gdt663_one_hundred_two_residual_family_completion/REPORT.md",
        "experiments/yolo/gdt666_one_hundred_fifty_one_residual_family_completion/REPORT.md",
        "experiments/yolo/gdt678_seventeen_two_hole_family_completion/REPORT.md",
        "experiments/yolo/gdt679_eight_three_hole_family_completion/REPORT.md",
        "experiments/yolo/gdt680_eight_four_hole_family_completion/REPORT.md",
        "experiments/yolo/gdt681_six_five_hole_family_completion/REPORT.md",
        "experiments/yolo/gdt682_final_seven_hole_line_completion/REPORT.md",
        "experiments/yolo/gdt690_noun_ordinal_provenance_main_apparatus/REPORT.md",
        "experiments/yolo/gdt691_preparation_head_role_dispatch/REPORT.md",
    )
)
WORD_RE = re.compile(r"[A-Za-zÄÖÜäöüß]+(?:-[A-Za-zÄÖÜäöüß]+)*")
STATUS = "PASS_V67_22_RESIDUAL_SHARE_MIGRATIONS__ZERO_FRAKTION_479_TOKEN_READER__3_BOUND_SPANS"


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


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def render(glosses: list[str]) -> str:
    text = ""
    for gloss in glosses:
        if gloss in {";", "."}:
            text = text.rstrip(" ,;.") + gloss
            continue
        separator = "" if not text else (" " if text.endswith((";", ".", ":")) else "; ")
        text += separator + gloss
    if text and not text.endswith("."):
        text += "."
    return text[:1].upper() + text[1:] if text else text


def count_term(texts: list[str], needle: str) -> int:
    return sum(needle.casefold() in word.casefold() for text in texts for word in words(text))


def make_census(channel: str, texts: list[str]) -> dict[str, object]:
    return {
        "channel": channel,
        "units": len(texts),
        "word_count": sum(len(words(text)) for text in texts),
        "character_count": sum(len(text) for text in texts),
        "fraktion_bearing_words": count_term(texts, "fraktion"),
        "anteil_bearing_words": count_term(texts, "anteil"),
        "portion_bearing_words": count_term(texts, "portion"),
        "auszug_bearing_words": count_term(texts, "auszug"),
        "ansatz_bearing_words": count_term(texts, "ansatz"),
        "mass_bearing_words": count_term(texts, "maß"),
        "droge_bearing_words": count_term(texts, "droge"),
    }


def span_map(
    span_rows: list[dict[str, object]],
    tokens_by_locus: dict[str, list[dict[str, str]]],
) -> dict[str, dict[int, dict[str, object]]]:
    result: dict[str, dict[int, dict[str, object]]] = defaultdict(dict)
    covered: set[tuple[str, int]] = set()
    for span in span_rows:
        locus = str(span["locus"])
        start = int(span["start_ordinal"])
        end = int(span["end_ordinal"])
        assert locus in tokens_by_locus and 1 <= start <= end <= len(tokens_by_locus[locus])
        actual = "|".join(row["surface"] for row in tokens_by_locus[locus][start - 1:end])
        assert actual == span["surfaces"], (span["span_id"], actual, span["surfaces"])
        assert start not in result[locus]
        for ordinal in range(start, end + 1):
            key = (locus, ordinal)
            assert key not in covered
            covered.add(key)
        result[locus][start] = span
    return result


def render_locus(
    locus: str,
    token_values: dict[tuple[str, int], str],
    tokens_by_locus: dict[str, list[dict[str, str]]],
    spans: dict[str, dict[int, dict[str, object]]],
) -> str:
    units: list[str] = []
    ordinal = 1
    locus_tokens = tokens_by_locus[locus]
    while ordinal <= len(locus_tokens):
        span = spans.get(locus, {}).get(ordinal)
        if span:
            units.append(str(span["v67_selected_gloss_de"]))
            ordinal = int(span["end_ordinal"]) + 1
        else:
            units.append(token_values[(locus, ordinal)])
            ordinal += 1
    return render(units)


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    token_rows = read_tsv(TOKENS)
    line_rows = read_tsv(LINES)
    residual_rows = read_tsv(RESIDUALS)
    verb_rows = read_tsv(VERBS)
    old_span_rows = read_tsv(OLD_SPANS)
    product_rival_rows = read_tsv(PRODUCT_RIVALS)
    rule_rows = read_tsv(RULES)
    new_span_rows = read_tsv(NEW_SPAN)
    g693_result = json.loads(G693_RESULT.read_text(encoding="utf-8"))

    assert g693_result["status"].startswith("PASS_V66_")
    assert g693_result["basis"]["new_pages"] == 0
    assert g693_result["basis"]["f84_access"] == 0 and g693_result["basis"]["f84r_access"] == 0
    assert len(token_rows) == 479 and len(line_rows) == 51 and len(residual_rows) == 22
    assert len(verb_rows) == 113 and len(old_span_rows) == 2 and len(new_span_rows) == 1
    assert len(product_rival_rows) == 6 and len(rule_rows) == 22
    assert len({row["rule_id"] for row in rule_rows}) == 22
    assert all(not row["page"].startswith("f84") and not row["locus"].startswith("f84") for row in token_rows)

    tokens_by_locus: dict[str, list[dict[str, str]]] = defaultdict(list)
    token_by_key: dict[tuple[str, int], dict[str, str]] = {}
    for row in token_rows:
        key = (row["locus"], int(row["token_ordinal"]))
        assert key not in token_by_key
        token_by_key[key] = row
        tokens_by_locus[row["locus"]].append(row)
    for locus_rows in tokens_by_locus.values():
        locus_rows.sort(key=lambda row: int(row["token_ordinal"]))
        assert [int(row["token_ordinal"]) for row in locus_rows] == list(range(1, len(locus_rows) + 1))

    line_by_locus = {row["locus"]: row for row in line_rows}
    assert len(line_by_locus) == 51 and set(line_by_locus) == set(tokens_by_locus)

    residual_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in residual_rows}
    rule_by_key = {(row["locus"], int(row["token_ordinal"])): row for row in rule_rows}
    assert len(residual_by_key) == len(rule_by_key) == 22
    assert set(residual_by_key) == set(rule_by_key)

    for key, rule in rule_by_key.items():
        residual = residual_by_key[key]
        token = token_by_key[key]
        assert rule["surface"] == residual["surface"] == token["surface"]
        assert rule["expected_v66_gloss_de"] == residual["v66_selected_gloss_de"] == token["v66_selected_gloss_de"]
        assert "fraktion" in rule["expected_v66_gloss_de"].casefold()
        assert "fraktion" not in rule["v67_share_gloss_de"].casefold()
        assert rule["v67_share_gloss_de"] != rule["expected_v66_gloss_de"]

    v66_values: dict[tuple[str, int], str] = {}
    v67_values: dict[tuple[str, int], str] = {}
    token_out: list[dict[str, object]] = []
    migration_out: list[dict[str, object]] = []
    for source in token_rows:
        key = (source["locus"], int(source["token_ordinal"]))
        old = source["v66_selected_gloss_de"]
        rule = rule_by_key.get(key)
        new = rule["v67_share_gloss_de"] if rule else old
        v66_values[key] = old
        v67_values[key] = new
        out: dict[str, object] = dict(source)
        out.update({
            "v67_role": "EXACT_RESIDUAL_MIGRATION" if rule else "INHERITED_V66",
            "v67_rule_id": rule["rule_id"] if rule else "NONE",
            "v67_token_gloss_de": new,
            "v67_changed": int(new != old),
            "v67_migration_class": rule["migration_class"] if rule else "INHERITED",
            "v67_visible_parse": rule["visible_parse"] if rule else "NONE",
            "v67_share_index": rule["share_index"] if rule else "NONE",
            "v67_preserved_heads": rule["preserved_heads"] if rule else "NONE",
            "v67_local_rival_de": rule["local_rival_de"] if rule else "NONE",
            "v67_basis": rule["basis"] if rule else "INHERITED_V66",
        })
        token_out.append(out)
        if rule:
            migration_out.append({
                "page": source["page"], "locus": source["locus"],
                "token_ordinal": source["token_ordinal"], "surface": source["surface"],
                "rule_id": rule["rule_id"], "v66_gloss_de": old, "v67_gloss_de": new,
                "migration_class": rule["migration_class"], "visible_parse": rule["visible_parse"],
                "share_index": rule["share_index"], "preserved_heads": rule["preserved_heads"],
                "local_rival_de": rule["local_rival_de"], "primary_history": rule["primary_history"],
                "basis": rule["basis"],
                "exact_card_only": 1,
                "learned_whole_renderer": int(rule["migration_class"] == "LEARNED_WHOLE_WITH_SHARE_RENDERER"),
            })

    assert len(migration_out) == 22 and sum(int(row["v67_changed"]) for row in token_out) == 22

    combined_spans: list[dict[str, object]] = []
    inherited_spans: list[dict[str, object]] = []
    for row in old_span_rows:
        span = {
            "span_id": row["span_id"], "locus": row["locus"],
            "start_ordinal": row["start_ordinal"], "end_ordinal": row["end_ordinal"],
            "surfaces": row["surfaces"], "v67_selected_gloss_de": row["selected_gloss_de"],
            "span_origin": "INHERITED_GDT693", "basis": row["selected_semantics"],
        }
        inherited_spans.append(span)
        combined_spans.append(span)
    for row in new_span_rows:
        combined_spans.append({
            "span_id": row["span_id"], "locus": row["locus"],
            "start_ordinal": row["start_ordinal"], "end_ordinal": row["end_ordinal"],
            "surfaces": row["surfaces"], "v67_selected_gloss_de": row["selected_gloss_de"],
            "span_origin": "NEW_GDT694_EXACT_READER_SPAN", "basis": row["basis"],
        })
    assert len({row["span_id"] for row in combined_spans}) == 3
    v66_spans = span_map(inherited_spans, tokens_by_locus)
    v67_spans = span_map(combined_spans, tokens_by_locus)

    for source_line in line_rows:
        replay = render_locus(source_line["locus"], v66_values, tokens_by_locus, v66_spans)
        assert replay == source_line["v66_selected_translation_de"], source_line["locus"]

    line_out: list[dict[str, object]] = []
    changed_line_audit: list[dict[str, object]] = []
    for source_line in line_rows:
        locus = source_line["locus"]
        locus_rules = [
            rule_by_key[(locus, ordinal)]
            for ordinal in range(1, len(tokens_by_locus[locus]) + 1)
            if (locus, ordinal) in rule_by_key
        ]
        changed_ordinals = [
            ordinal for ordinal in range(1, len(tokens_by_locus[locus]) + 1)
            if v66_values[(locus, ordinal)] != v67_values[(locus, ordinal)]
        ]
        translation = render_locus(locus, v67_values, tokens_by_locus, v67_spans)
        apparatus = " || ".join(
            f"#{rule['token_ordinal']} {rule['surface']}: {rule['expected_v66_gloss_de']} → {rule['v67_share_gloss_de']} [{rule['rule_id']}; {rule['migration_class']}]"
            for rule in locus_rules
        ) or "NONE"
        local_rivals = " || ".join(
            f"#{rule['token_ordinal']} {rule['surface']}: {rule['local_rival_de']}" for rule in locus_rules
        ) or "NONE"
        span_notes = " || ".join(
            f"{span['span_id']} {span['surfaces']}: {span['v67_selected_gloss_de']}"
            for span in combined_spans if span["locus"] == locus
        ) or "NONE"
        out: dict[str, object] = dict(source_line)
        out.update({
            "v67_translation_de": translation,
            "v67_changed_token_positions": len(changed_ordinals),
            "v67_changed_ordinals": "|".join(map(str, changed_ordinals)) if changed_ordinals else "NONE",
            "v67_compact_apparatus_de": apparatus,
            "v67_local_rivals_de": local_rivals,
            "v67_bound_span_notes_de": span_notes,
            "v67_word_count": len(words(translation)),
            "v67_character_count": len(translation),
            "v67_status": "ZERO_FRAKTION_EXACT_CARD_READER__NO_FREE_SUBSTRING_EXPORT",
        })
        line_out.append(out)
        if changed_ordinals:
            changed_line_audit.append({
                "page": source_line["page"], "locus": locus,
                "line_mode": source_line["v66_line_mode"], "zl3b_line": source_line["zl3b_line"],
                "changed_token_positions": len(changed_ordinals),
                "changed_ordinals": "|".join(map(str, changed_ordinals)),
                "v66_translation_de": source_line["v66_selected_translation_de"],
                "v67_translation_de": translation, "apparatus_de": apparatus,
                "local_rivals_de": local_rivals, "bound_span_notes_de": span_notes,
            })

    assert len(changed_line_audit) == 17
    assert sum(int(row["v67_changed_token_positions"]) for row in line_out) == 22
    assert all("fraktion" not in str(row["v67_token_gloss_de"]).casefold() for row in token_out)
    assert all("fraktion" not in str(row["v67_translation_de"]).casefold() for row in line_out)

    verb_out: list[dict[str, object]] = []
    for source in verb_rows:
        key = (source["locus"], int(source["token_ordinal"]))
        assert key in v67_values
        expected_present = int(source["v66_selected_exact_form_present"])
        present = int(source["verb_de"].casefold() in v67_values[key].casefold())
        out: dict[str, object] = dict(source)
        out.update({
            "v67_token_gloss_de": v67_values[key], "v67_exact_form_present": present,
            "v67_preserved_exact_ordinal": int(present == expected_present),
            "v67_rule_id": rule_by_key[key]["rule_id"] if key in rule_by_key else "NONE",
        })
        verb_out.append(out)
    assert len(verb_out) == 113
    assert all(int(row["v67_preserved_exact_ordinal"]) == 1 for row in verb_out)
    assert sum(int(row["v67_exact_form_present"]) for row in verb_out) == 110

    rival_out: list[dict[str, object]] = []
    for source in product_rival_rows:
        locus = source["locus"]
        changed_inside = [
            ordinal for ordinal in range(int(source["start_ordinal"]), int(source["end_ordinal"]) + 1)
            if (locus, ordinal) in rule_by_key
        ]
        assert not changed_inside
        out: dict[str, object] = dict(source)
        out.update({"v67_main_span_preserved": 1, "v67_semantic_scope": source["semantic_scope"]})
        rival_out.append(out)
    assert len(rival_out) == 6

    census = [
        make_census("V66_TOKEN", [row["v66_selected_gloss_de"] for row in token_rows]),
        make_census("V67_TOKEN", [str(row["v67_token_gloss_de"]) for row in token_out]),
        make_census("V66_LINE", [row["v66_selected_translation_de"] for row in line_rows]),
        make_census("V67_LINE", [str(row["v67_translation_de"]) for row in line_out]),
    ]
    census_by_channel = {row["channel"]: row for row in census}
    assert census_by_channel["V66_TOKEN"]["fraktion_bearing_words"] == 22
    assert census_by_channel["V67_TOKEN"]["fraktion_bearing_words"] == 0
    assert census_by_channel["V66_LINE"]["fraktion_bearing_words"] == 22
    assert census_by_channel["V67_LINE"]["fraktion_bearing_words"] == 0

    class_counts = Counter(row["migration_class"] for row in rule_rows)
    class_census = [
        {
            "migration_class": migration_class, "exact_cards": count,
            "surfaces": "|".join(row["surface"] for row in rule_rows if row["migration_class"] == migration_class),
            "export_scope": (
                "EXACT_WHOLE_ONLY" if migration_class == "LEARNED_WHOLE_WITH_SHARE_RENDERER"
                else "EXACT_CARD_COMPOSITION_ONLY__NO_GLOBAL_SUBSTRING_EXPORT"
            ),
        }
        for migration_class, count in sorted(class_counts.items())
    ]
    assert class_counts["LEARNED_WHOLE_WITH_SHARE_RENDERER"] == 3

    write_tsv(output_dir / "V67_22_RESIDUAL_SHARE_MIGRATIONS.tsv", migration_out)
    write_tsv(output_dir / "V67_479_TOKEN_ZERO_FRACTION_READER.tsv", token_out)
    write_tsv(output_dir / "V67_51_LINE_ZERO_FRACTION_READER.tsv", line_out)
    write_tsv(output_dir / "V67_17_CHANGED_LINE_AUDIT.tsv", changed_line_audit)
    write_tsv(output_dir / "V67_3_BOUND_SPANS.tsv", combined_spans)
    write_tsv(output_dir / "V67_113_VERB_PRESERVATION.tsv", verb_out)
    write_tsv(output_dir / "V67_TERM_CENSUS.tsv", census)
    write_tsv(output_dir / "V67_COMPOSITION_CLASS_CENSUS.tsv", class_census)
    write_tsv(output_dir / "V67_6_PRODUCT_RIVALS.tsv", rival_out)

    report_lines = [
        "# GDT694 — V67 zero-*Fraktion* working reader", "", f"Status: `{STATUS}`", "",
        "## Result", "",
        "All 22 inherited fraction-bearing exact cards were migrated. The same 479-token,",
        "51-line, 36-page deck now contains zero German words bearing *Fraktion*. This is",
        "a terminology-normalized working renderer, not recovered plaintext.", "",
        "The migration deliberately mixes exact composition with learned whole forms.",
        "`arl`, `lldar`, and `chear` receive new whole-card German glosses but are not",
        "promoted to freely productive segmentations. Every other rule is also limited",
        "to its named exact card; no substring replacement is performed.", "",
        "Three ambiguity repairs matter more than the raw zero count:", "",
        "- `okeeodar` no longer spends its one written `d` on both *Auszug* and",
        "  *abgemessen*: the main keeps `KEEOD+AR`; the measured-Ansatz parse is a rival.",
        "- RF1b's `ar|aram` is rendered appositionally as *Drogenanteil I; davon ein Maß*;",
        "  the nested two-share reading remains visible rather than silently doubled.",
        "- `l|karchees` is one exact reader span, consuming the wood head once.", "",
        "`chdar` no longer counts the same I as both share I and preparation stage I;",
        "`chear` keeps CH+E as one bound dry shell, without inventing an E-stage.",
        "All 113 inherited exact verb profiles and all six local Holzauszug rivals survive.", "",
        "## The 22 exact migrations", "",
        "| locus | form | V67 main | mode | strongest local rival |",
        "|---|---|---|---|---|",
    ]
    for row in migration_out:
        report_lines.append(
            f"| {row['locus']}#{row['token_ordinal']} | `{row['surface']}` | {row['v67_gloss_de']} | "
            f"`{row['migration_class']}` | {row['local_rival_de']} |"
        )
    report_lines.extend(["", "## Complete 51-line working edition", ""])
    for row in line_out:
        report_lines.extend([
            f"### {row['locus']}", "", f"`{row['zl3b_line']}`", "", str(row["v67_translation_de"]), "",
        ])
    report_lines.extend([
        "## Claim ceiling", "",
        "V67 is the most internally explicit German working edition of this fixed deck.",
        "It assigns a default practical reading to every written token and preserves",
        "named rivals, but it does not establish Voynich plaintext, language, phonetics,",
        "or a manuscript-wide free morpheme dictionary. No new page was opened.", "",
    ])
    (output_dir / "GDT694_V67_ZERO_FRACTION_READER.md").write_text("\n".join(report_lines), encoding="utf-8")

    artifact_readme = """# GDT694 artifacts

`GDT694_V67_ZERO_FRACTION_READER.md` is the human-readable 51-line edition.
The TSVs preserve all 479 token decisions, the 22 changed exact cards, the 17
changed lines, three bound spans, 113 verb checks, six product rivals, and the
term/class censuses. `RESULT.json` binds inputs, output hashes, status and claim
ceiling; `VALIDATION.json` is produced independently by `src/validate.py`.
"""
    (output_dir / "README.md").write_text(artifact_readme, encoding="utf-8")

    generated = [
        "GDT694_V67_ZERO_FRACTION_READER.md", "README.md",
        "V67_113_VERB_PRESERVATION.tsv", "V67_17_CHANGED_LINE_AUDIT.tsv",
        "V67_22_RESIDUAL_SHARE_MIGRATIONS.tsv", "V67_3_BOUND_SPANS.tsv",
        "V67_479_TOKEN_ZERO_FRACTION_READER.tsv", "V67_51_LINE_ZERO_FRACTION_READER.tsv",
        "V67_6_PRODUCT_RIVALS.tsv", "V67_COMPOSITION_CLASS_CENSUS.tsv", "V67_TERM_CENSUS.tsv",
    ]
    input_paths = [
        TOKENS, LINES, RESIDUALS, VERBS, OLD_SPANS, PRODUCT_RIVALS,
        G693_RESULT, RULES, NEW_SPAN, SRC / "run.py", *PROVENANCE_REPORTS,
    ]
    result: dict[str, object] = {
        "status": STATUS,
        "question": "Can all 22 inherited fraction-bearing exact cards be migrated to the selected indexed-share renderer without erasing learned wholes, reader boundaries, verbs, product rivals, or material heads?",
        "basis": {
            "token_positions": 479, "lines": 51, "pages": len({row["page"] for row in token_rows}),
            "residual_exact_cards": 22, "changed_token_positions": 22, "changed_lines": 17,
            "bound_spans": 3, "verb_ordinals": 113, "product_rivals": 6,
            "new_pages": 0, "f84_access": 0, "f84r_access": 0,
        },
        "migration": {
            "zero_fraktion_token_reader": 1, "zero_fraktion_line_reader": 1,
            "learned_whole_share_renderers": class_counts["LEARNED_WHOLE_WITH_SHARE_RENDERER"],
            "exact_card_only_for_all_rules": 1, "free_substring_exports": 0,
            "composition_classes": dict(sorted(class_counts.items())),
        },
        "ambiguity_repairs": {
            "okeeodar_single_d_not_double_spent": 1, "araram_reader_boundary_apposition": 1,
            "l_karchees_bound_span": 1, "chdar_index_not_reused_as_stage": 1,
            "chear_bound_dry_shell_without_e_stage": 1,
        },
        "term_census": {row["channel"]: row for row in census},
        "verbs": {"ordinals": 113, "exact_forms_present": 110, "all_exact_profiles_preserved": 1},
        "inputs": {str(path.relative_to(ROOT)): sha256(path) for path in input_paths},
        "files": {name: sha256(output_dir / name) for name in sorted(generated)},
        "next_gap": "Polish nominal lists versus executable procedure clauses on the same 51 lines while freezing all 479 V67 token glosses and the three exact bound spans; no new page is needed.",
        "claim_ceiling": "V67 is an exploratory, exact-card German working renderer over the fixed 479-token deck. It removes a generic inherited renderer noun and makes 22 default readings concrete, but it is not recovered plaintext and exports no manuscript-wide substring meaning.",
    }
    return result


def main() -> int:
    if len(sys.argv) > 2:
        raise SystemExit("usage: run.py [OUTPUT_DIR]")
    output_dir = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else ART
    result = build(output_dir)
    write_json(output_dir / "RESULT.json", result)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
