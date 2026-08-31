#!/usr/bin/env python3
"""Build the GDT676 51-line context-aware V50 reader."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt676_v50_external_line_renderer"
ART = EXP / "artifacts"
TOUCHED_PATH = ROOT / "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan/artifacts/TOUCHED_LINE_OVERLAY.tsv"
OCCURRENCES_PATH = ROOT / "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan/artifacts/EXTERNAL_TRANSFERABLE_OCCURRENCES.tsv"
GDT675_RESULT_PATH = ROOT / "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan/artifacts/RESULT.json"
LINE_MODE_PATH = EXP / "src/LINE_MODE_SPECS.tsv"
LINE_READER_PATH = EXP / "src/LINE_READER_SPECS.tsv"
VALUE_PATH = EXP / "src/VALUE_ATTACHMENT_SPECS.tsv"
TEMPLATES_PATH = EXP / "src/SYNTAX_TEMPLATES.tsv"
SELECTIONS_PATH = EXP / "src/PASSAGE_SELECTIONS.tsv"

BROAD_CARRIER = re.compile(
    r"\b(?:\w*Ansatz\w*|\w*Kompositum\w*|\w*Species\w*|Drogenstoff|"
    r"Trockengut|Feuchtmaterial|Materialmaß|Grundauszug)\b",
    re.IGNORECASE,
)
GENERIC_FILLER = re.compile(
    r"\b(?:Arbeitsgut|Arbeitsmaterial|Arbeitsstoff|Arbeitsmittel|Arbeitsprodukt|"
    r"Arbeitsstelle|Arbeitsort|Arbeitsgang|Arbeitszyklus|Arbeitsvorgang|"
    r"Arbeitsschritt|Stationsansatz|Stationsposten|Stationswert|Stationsanteil|"
    r"Stationseinheit|Aktiver Posten|laufender Eintrag|work item|working material|"
    r"worksite|work cycle|source vessel|destination place|destination vessel)\b",
    re.IGNORECASE,
)
EXTENDED_CLASS_CARRIER = re.compile(
    r"(?:gut|stoff|droge|material|ansatz|kompositum|species|klasse|grad|maß|menge|"
    r"posten|charge|zubereitung|teil|eintrag|feld|form|einheit|portion|fraktion|"
    r"qualität|rahmen)",
    re.IGNORECASE,
)
UNKNOWN_MARKER = re.compile(r"⟦([^:⟧]+):\?⟧")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: list[dict[str, object]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_ordinals(raw: str) -> list[int]:
    return [] if raw == "NONE" else [int(value) for value in raw.split("|")]


def parse_action_specs(raw: str) -> list[tuple[int, str]]:
    if raw == "NONE":
        return []
    result = []
    for item in raw.split("|"):
        ordinal, label = item.split(":", 1)
        result.append((int(ordinal), label))
    return result


def parse_surface_ordinals(raw: str) -> set[int]:
    return {int(value) for value in raw.split("|") if value and value != "NONE"}


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    touched = read_tsv(TOUCHED_PATH)
    occurrences = read_tsv(OCCURRENCES_PATH)
    mode_specs = {row["locus"]: row for row in read_tsv(LINE_MODE_PATH)}
    reader_specs = {row["locus"]: row for row in read_tsv(LINE_READER_PATH)}
    value_specs = read_tsv(VALUE_PATH)
    templates = read_tsv(TEMPLATES_PATH)
    selections = read_tsv(SELECTIONS_PATH)
    gdt675_result = json.loads(GDT675_RESULT_PATH.read_text(encoding="utf-8"))

    assert len(touched) == 51 and len(occurrences) == 51
    assert len(mode_specs) == len(reader_specs) == 51
    assert set(mode_specs) == set(reader_specs) == {row["locus"] for row in touched}
    assert len(value_specs) == 17 and len(templates) == 8 and len(selections) == 4
    occurrence_by_key = {(row["locus"], int(row["ordinal"])): row for row in occurrences}
    assert len(occurrence_by_key) == 51

    token_rows: list[dict[str, object]] = []
    line_rows: list[dict[str, object]] = []
    line_by_locus: dict[str, dict[str, object]] = {}
    totals = Counter()
    distribution = Counter()
    literal_narrow_carrier_positions = 0
    literal_narrow_carrier_matches = 0
    working_narrow_carrier_positions = 0
    working_narrow_carrier_matches = 0
    assigned_extended_class_positions = 0
    literal_generic_matches = 0
    working_generic_matches = 0

    for line in touched:
        locus = line["locus"]
        tokens = line["zl3b_line"].split()
        before = line["before_overlay_glosses_de"].split(" | ")
        after = line["gdt675_overlay_glosses_de"].split(" | ")
        applied = parse_surface_ordinals(line["applied_ordinals"])
        remaining = parse_surface_ordinals(line["remaining_unknown_ordinals"])
        assert len(tokens) == len(before) == len(after)
        assert sum(gloss == f"[{surface}:?]" for surface, gloss in zip(tokens, before)) == int(
            line["unknown_after_gdt673"]
        )
        assert sum(gloss == f"[{surface}:?]" for surface, gloss in zip(tokens, after)) == int(
            line["unknown_after_gdt675"]
        )
        assert len(applied) == 1 and len(remaining) == int(line["unknown_after_gdt675"])
        changed = {index for index, (old, new) in enumerate(zip(before, after), start=1) if old != new}
        assert changed == applied
        for index in applied:
            assert before[index - 1] == f"[{tokens[index - 1]}:?]"
            occurrence = occurrence_by_key[(locus, index)]
            assert occurrence["surface"] == tokens[index - 1]
            assert occurrence["applied_meaning_de"] == after[index - 1]

        mode = mode_specs[locus]
        reader = reader_specs[locus]
        working_chunks = reader["working_line_de"].rstrip(".").split(" · ")
        assert len(working_chunks) == len(tokens)
        action_specs = parse_action_specs(mode["action_ordinals"])
        action_ordinals = {ordinal for ordinal, _ in action_specs}
        final_action_ordinals = set(parse_ordinals(reader["action_ordinals"]))
        assert action_ordinals == final_action_ordinals
        for ordinal, label in action_specs:
            assert 1 <= ordinal <= len(tokens)
            if "<" in label:
                subspan, owner = label[:-1].split("<", 1)
                assert owner == tokens[ordinal - 1] and owner.startswith(subspan)
            else:
                assert label == tokens[ordinal - 1]

        unknown_markers = Counter(UNKNOWN_MARKER.findall(reader["working_line_de"]))
        expected_markers = Counter(tokens[index - 1] for index in remaining)
        assert unknown_markers == expected_markers
        line_working_broad_positions = sum(bool(BROAD_CARRIER.search(chunk)) for chunk in working_chunks)
        line_working_broad_matches = sum(len(BROAD_CARRIER.findall(chunk)) for chunk in working_chunks)
        line_working_generic_matches = sum(len(GENERIC_FILLER.findall(chunk)) for chunk in working_chunks)
        working_narrow_carrier_positions += line_working_broad_positions
        working_narrow_carrier_matches += line_working_broad_matches
        working_generic_matches += line_working_generic_matches
        assert line_working_generic_matches == 0

        categories = Counter()
        line_literal_broad_matches = 0
        line_literal_broad_positions = 0
        for index, (surface, old_gloss, new_gloss, working_chunk) in enumerate(
            zip(tokens, before, after, working_chunks), start=1
        ):
            if index in applied:
                category = "NEW_V50"
            elif index in remaining:
                category = "RESIDUAL_UNKNOWN"
            elif BROAD_CARRIER.search(new_gloss):
                category = "INHERITED_NARROW_CARRIER"
            else:
                category = "INHERITED_OTHER_ASSIGNED"
            broad_hits = len(BROAD_CARRIER.findall(new_gloss))
            working_broad_hits = len(BROAD_CARRIER.findall(working_chunk))
            extended_hit = index not in remaining and bool(EXTENDED_CLASS_CARRIER.search(new_gloss))
            hard_hits = len(GENERIC_FILLER.findall(new_gloss))
            working_hard_hits = len(GENERIC_FILLER.findall(working_chunk))
            categories[category] += 1
            totals[category] += 1
            if broad_hits:
                line_literal_broad_positions += 1
                literal_narrow_carrier_positions += 1
            line_literal_broad_matches += broad_hits
            literal_narrow_carrier_matches += broad_hits
            assigned_extended_class_positions += int(extended_hit)
            literal_generic_matches += hard_hits
            occurrence = occurrence_by_key.get((locus, index))
            token_rows.append({
                "page": line["page"], "locus": locus, "section": line["section"],
                "language": line["language"], "hand": line["hand"], "ordinal": index,
                "surface": surface, "before_v50_gloss_de": old_gloss, "v50_gloss_de": new_gloss,
                "information_category": category, "licensed_action": "1" if index in action_ordinals else "0",
                "literal_narrow_carrier": "1" if broad_hits else "0",
                "literal_narrow_match_count": broad_hits,
                "assigned_extended_class_carrier": "1" if extended_hit else "0",
                "working_chunk_de": working_chunk,
                "working_narrow_carrier": "1" if working_broad_hits else "0",
                "working_narrow_match_count": working_broad_hits,
                "literal_hard_generic_hits": hard_hits,
                "working_hard_generic_hits": working_hard_hits,
                "new_card_surface": occurrence["surface"] if occurrence else "NONE",
                "new_card_render_mode": occurrence["render_mode"] if occurrence else "NONE",
                "new_card_reader_support": occurrence["reader_support"] if occurrence else "NONE",
            })

        token_count = len(tokens)
        residual = categories["RESIDUAL_UNKNOWN"]
        assigned = token_count - residual
        distribution[residual] += 1
        row = {
            "page": line["page"], "locus": locus, "section": line["section"],
            "language": line["language"], "hand": line["hand"], "token_count": token_count,
            "new_v50_positions": categories["NEW_V50"],
            "residual_unknown_positions": residual,
            "inherited_narrow_carrier_positions": categories["INHERITED_NARROW_CARRIER"],
            "inherited_other_assigned_positions": categories["INHERITED_OTHER_ASSIGNED"],
            "literal_narrow_carrier_positions": line_literal_broad_positions,
            "literal_narrow_carrier_matches": line_literal_broad_matches,
            "working_narrow_carrier_positions": line_working_broad_positions,
            "working_narrow_carrier_matches": line_working_broad_matches,
            "assigned_fraction": f"{assigned / token_count:.6f}",
            "complete": "1" if residual == 0 else "0",
            "action_positions": len(action_ordinals),
            "action_ordinals": "|".join(map(str, sorted(action_ordinals))) or "NONE",
            "action_surfaces": "|".join(tokens[index - 1] for index in sorted(action_ordinals)) or "NONE",
            "line_mode": reader["line_mode"],
            "source_action_mode": mode["line_mode"],
            "gdt675_render_correction": mode["gdt675_render_correction"],
            "new_surface": tokens[next(iter(applied)) - 1],
            "new_reader_support": occurrence_by_key[(locus, next(iter(applied)))]["reader_support"],
            "remaining_unknown_surfaces": line["remaining_unknown_surfaces"],
            "zl3b_line": line["zl3b_line"],
            "literal_token_glosses_de": line["gdt675_overlay_glosses_de"],
            "working_line_de": reader["working_line_de"],
            "review_note": reader["review_note"],
        }
        line_rows.append(row)
        line_by_locus[locus] = row

    assert totals == {
        "NEW_V50": 51, "RESIDUAL_UNKNOWN": 136,
        "INHERITED_NARROW_CARRIER": 77, "INHERITED_OTHER_ASSIGNED": 215,
    }
    assert sum(totals.values()) == 479
    assert distribution == {0: 2, 1: 9, 2: 17, 3: 8, 4: 8, 5: 6, 7: 1}
    assert literal_narrow_carrier_positions == 105 and literal_narrow_carrier_matches == 106
    assert working_narrow_carrier_positions == 113 and working_narrow_carrier_matches == 114
    assert assigned_extended_class_positions == 311
    assert literal_generic_matches == working_generic_matches == 0
    assert Counter(row["line_mode"] for row in line_rows) == {
        "ACTION_SEQUENCE": 11, "NOMINAL_REGISTER": 14,
        "MIXED_RECORD": 18, "QUANTITY_LABEL": 8,
    }
    assert sum(int(row["action_positions"]) for row in line_rows) == 48
    assert sum(row["complete"] == "1" for row in line_rows) == 2
    line_scale_override_loci = sorted(
        locus for locus, spec in mode_specs.items()
        if spec["gdt675_render_correction"].startswith("OVERRIDE_")
    )
    assert line_scale_override_loci == ["f26r.2"]
    line_scale_holds = len(line_rows) - len(line_scale_override_loci)

    value_rows: list[dict[str, object]] = []
    for number, spec in enumerate(value_specs, start=1):
        line = next(row for row in touched if row["locus"] == spec["locus"])
        tokens = line["zl3b_line"].split()
        heads = parse_ordinals(spec["head_ordinals"])
        values = parse_ordinals(spec["value_ordinals"])
        close = [] if spec["close_ordinal"] == "NONE" else [int(spec["close_ordinal"])]
        assert all(1 <= value <= len(tokens) for value in [*heads, *values, *close])
        value_rows.append({
            "attachment_id": f"GDT676-V{number:02d}", "locus": spec["locus"],
            "head_ordinals": spec["head_ordinals"],
            "head_surfaces": "|".join(tokens[value - 1] for value in heads),
            "value_ordinals": spec["value_ordinals"],
            "value_surfaces": "|".join(tokens[value - 1] for value in values),
            "close_ordinal": spec["close_ordinal"],
            "close_surface": "|".join(tokens[value - 1] for value in close) or "NONE",
            "decision": spec["decision"], "contextual_reading_de": spec["contextual_reading_de"],
            "note": spec["note"],
        })
    assert Counter(row["decision"] for row in value_rows) == {
        "BIND": 9, "BIND_NOMINAL": 1, "PROVISIONAL": 3, "REJECT_JUMP": 4,
    }

    ranked = sorted(
        line_rows,
        key=lambda row: (
            int(row["residual_unknown_positions"]), -int(row["inherited_other_assigned_positions"]),
            int(row["inherited_narrow_carrier_positions"]), -int(row["token_count"]), str(row["locus"]),
        ),
    )
    ranking_rows = [
        {"rank": rank, **row} for rank, row in enumerate(ranked, start=1)
    ]
    low_residual_rows = [row for row in ranking_rows if int(row["residual_unknown_positions"]) <= 2]
    assert len(low_residual_rows) == 28

    page_groups: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in line_rows:
        page_groups[str(row["page"])].append(row)
    page_rows = []
    for page, rows in page_groups.items():
        if len(rows) < 2:
            continue
        tokens = sum(int(row["token_count"]) for row in rows)
        residual = sum(int(row["residual_unknown_positions"]) for row in rows)
        page_rows.append({
            "page": page, "touched_lines": len(rows), "tokens": tokens, "residual_unknown": residual,
            "assigned_fraction": f"{(tokens - residual) / tokens:.6f}",
            "inherited_other_assigned": sum(int(row["inherited_other_assigned_positions"]) for row in rows),
            "inherited_narrow_carrier": sum(int(row["inherited_narrow_carrier_positions"]) for row in rows),
            "distinct_v50_surfaces": len({str(row["new_surface"]) for row in rows}),
            "v50_surfaces": "|".join(sorted({str(row["new_surface"]) for row in rows})),
            "loci": "|".join(str(row["locus"]) for row in rows),
        })
    page_rows.sort(key=lambda row: (
        -float(row["assigned_fraction"]), -int(row["distinct_v50_surfaces"]), -int(row["touched_lines"]),
        -int(row["inherited_other_assigned"]), int(row["inherited_narrow_carrier"]), str(row["page"]),
    ))
    page_rows = [{"rank": rank, **row} for rank, row in enumerate(page_rows, start=1)]

    passage_rows = []
    for selection in selections:
        loci = selection["loci"].split("|")
        rows = [line_by_locus[locus] for locus in loci]
        token_count = sum(int(row["token_count"]) for row in rows)
        residual = sum(int(row["residual_unknown_positions"]) for row in rows)
        passage_rows.append({
            "selection_id": selection["selection_id"], "loci": selection["loci"],
            "selection_class": selection["selection_class"], "purpose": selection["purpose"],
            "lines": len(rows), "tokens": token_count, "residual_unknown": residual,
            "assigned_fraction": f"{(token_count - residual) / token_count:.6f}",
            "inherited_other_assigned": sum(int(row["inherited_other_assigned_positions"]) for row in rows),
            "inherited_narrow_carrier": sum(int(row["inherited_narrow_carrier_positions"]) for row in rows),
            "new_v50_positions": sum(int(row["new_v50_positions"]) for row in rows),
            "working_passage_de": " || ".join(str(row["working_line_de"]) for row in rows),
        })

    profile_rows = []
    for axis, field in (("register", "section"), ("language", "language"), ("hand", "hand")):
        groups: dict[str, list[dict[str, object]]] = defaultdict(list)
        for row in line_rows:
            groups[str(row[field])].append(row)
        for value, rows in sorted(groups.items()):
            token_count = sum(int(row["token_count"]) for row in rows)
            residual = sum(int(row["residual_unknown_positions"]) for row in rows)
            profile_rows.append({
                "axis": axis, "value": value, "lines": len(rows), "tokens": token_count,
                "new_v50": sum(int(row["new_v50_positions"]) for row in rows),
                "residual_unknown": residual,
                "inherited_narrow_carrier": sum(int(row["inherited_narrow_carrier_positions"]) for row in rows),
                "inherited_other_assigned": sum(int(row["inherited_other_assigned_positions"]) for row in rows),
                "complete_lines": sum(row["complete"] == "1" for row in rows),
                "assigned_fraction": f"{(token_count - residual) / token_count:.6f}",
            })

    rule_rows = [
        {"priority": 0, "rule_id": "HARD_GENERIC_PREFLIGHT_VETO", "predicate": GENERIC_FILLER.pattern, "output": "REJECT_RENDER"},
        {"priority": 1, "rule_id": "NEW_V50", "predicate": "ordinal in applied_ordinals", "output": "NEW_V50"},
        {"priority": 2, "rule_id": "RESIDUAL_UNKNOWN", "predicate": "ordinal in remaining_unknown_ordinals", "output": "RESIDUAL_UNKNOWN"},
        {"priority": 3, "rule_id": "INHERITED_NARROW_CARRIER", "predicate": BROAD_CARRIER.pattern, "output": "INHERITED_NARROW_CARRIER"},
        {"priority": 4, "rule_id": "INHERITED_OTHER_ASSIGNED", "predicate": "otherwise", "output": "INHERITED_OTHER_ASSIGNED"},
    ]
    category_rows = [{
        "category": category, "positions": totals[category],
        "denominator": 479, "share": f"{totals[category] / 479:.6f}",
    } for category in (
        "NEW_V50", "RESIDUAL_UNKNOWN", "INHERITED_NARROW_CARRIER", "INHERITED_OTHER_ASSIGNED",
    )]
    category_rows.extend([
        {"category": "LITERAL_NARROW_CARRIER_POSITIONS", "positions": literal_narrow_carrier_positions, "denominator": 479, "share": f"{literal_narrow_carrier_positions / 479:.6f}"},
        {"category": "LITERAL_NARROW_CARRIER_MATCHES", "positions": literal_narrow_carrier_matches, "denominator": 479, "share": f"{literal_narrow_carrier_matches / 479:.6f}"},
        {"category": "WORKING_NARROW_CARRIER_POSITIONS", "positions": working_narrow_carrier_positions, "denominator": 479, "share": f"{working_narrow_carrier_positions / 479:.6f}"},
        {"category": "WORKING_NARROW_CARRIER_MATCHES", "positions": working_narrow_carrier_matches, "denominator": 479, "share": f"{working_narrow_carrier_matches / 479:.6f}"},
        {"category": "ASSIGNED_EXTENDED_CLASS_CARRIER_POSITIONS", "positions": assigned_extended_class_positions, "denominator": 343, "share": f"{assigned_extended_class_positions / 343:.6f}"},
        {"category": "LITERAL_HARD_GENERIC_MATCHES", "positions": literal_generic_matches, "denominator": 479, "share": "0.000000"},
        {"category": "WORKING_HARD_GENERIC_MATCHES", "positions": working_generic_matches, "denominator": 479, "share": "0.000000"},
    ])

    token_fields = [
        "page", "locus", "section", "language", "hand", "ordinal", "surface",
        "before_v50_gloss_de", "v50_gloss_de", "information_category", "licensed_action",
        "literal_narrow_carrier", "literal_narrow_match_count", "assigned_extended_class_carrier",
        "working_chunk_de", "working_narrow_carrier", "working_narrow_match_count",
        "literal_hard_generic_hits", "working_hard_generic_hits", "new_card_surface",
        "new_card_render_mode", "new_card_reader_support",
    ]
    line_fields = [
        "page", "locus", "section", "language", "hand", "token_count", "new_v50_positions",
        "residual_unknown_positions", "inherited_narrow_carrier_positions", "inherited_other_assigned_positions",
        "literal_narrow_carrier_positions", "literal_narrow_carrier_matches",
        "working_narrow_carrier_positions", "working_narrow_carrier_matches", "assigned_fraction",
        "complete", "action_positions",
        "action_ordinals", "action_surfaces", "line_mode", "source_action_mode", "gdt675_render_correction",
        "new_surface", "new_reader_support", "remaining_unknown_surfaces", "zl3b_line",
        "literal_token_glosses_de", "working_line_de", "review_note",
    ]
    write_tsv(ART / "V50_EXTERNAL_TOKEN_READER.tsv", token_rows, token_fields)
    write_tsv(ART / "V50_EXTERNAL_LINE_READER.tsv", line_rows, line_fields)
    write_tsv(ART / "LINE_INFORMATION_RANKING.tsv", ranking_rows, ["rank", *line_fields])
    write_tsv(ART / "LOW_RESIDUAL_FRONTIER.tsv", low_residual_rows, ["rank", *line_fields])
    write_tsv(
        ART / "PAGE_TRANSFER_RANKING.tsv", page_rows,
        ["rank", "page", "touched_lines", "tokens", "residual_unknown", "assigned_fraction",
         "inherited_other_assigned", "inherited_narrow_carrier", "distinct_v50_surfaces", "v50_surfaces", "loci"],
    )
    write_tsv(
        ART / "PASSAGE_TEST_DECK.tsv", passage_rows,
        ["selection_id", "loci", "selection_class", "purpose", "lines", "tokens", "residual_unknown",
         "assigned_fraction", "inherited_other_assigned", "inherited_narrow_carrier", "new_v50_positions", "working_passage_de"],
    )
    write_tsv(
        ART / "REGISTER_HAND_PROFILE.tsv", profile_rows,
        ["axis", "value", "lines", "tokens", "new_v50", "residual_unknown", "inherited_narrow_carrier",
         "inherited_other_assigned", "complete_lines", "assigned_fraction"],
    )
    write_tsv(
        ART / "VALUE_ATTACHMENT_AUDIT.tsv", value_rows,
        ["attachment_id", "locus", "head_ordinals", "head_surfaces", "value_ordinals", "value_surfaces",
         "close_ordinal", "close_surface", "decision", "contextual_reading_de", "note"],
    )
    write_tsv(
        ART / "ACTION_SCOPE_AUDIT.tsv",
        [{"locus": locus, **mode_specs[locus]} for locus in mode_specs],
        ["locus", "action_ordinals", "line_mode", "gdt675_render_correction"],
    )
    write_tsv(ART / "SYNTAX_TEMPLATE_CARDS.tsv", templates, ["template_id", "visible_pattern", "renderer_rule"])
    write_tsv(ART / "RENDERER_RULE_CARDS.tsv", rule_rows, ["priority", "rule_id", "predicate", "output"])
    write_tsv(ART / "INFORMATION_CATEGORY_COUNTS.tsv", category_rows, ["category", "positions", "denominator", "share"])

    reader_doc = [
        "# GDT676 — V50 external 51-line working reader", "",
        "Every source token remains visible. `⟦surface:?⟧` is an unresolved position; broad carriers remain named rather than silently concretized.", "",
    ]
    for row in line_rows:
        reader_doc.extend([
            f"## {row['locus']} · {row['line_mode']}", "",
            f"**ZL3b:** `{row['zl3b_line']}`", "",
            f"**Tokenwerte:** {row['literal_token_glosses_de']}", "",
            f"**Arbeitslesung:** {row['working_line_de']}", "",
            f"**Aktionen:** {row['action_ordinals']} ({row['action_surfaces']})", "",
            f"**Rest:** {row['residual_unknown_positions']} offen; {row['remaining_unknown_surfaces']}", "",
            f"**Audit:** {row['review_note']}", "",
        ])
    (ART / "GDT676_V50_EXTERNAL_WORKING_READER.md").write_text("\n".join(reader_doc).rstrip() + "\n", encoding="utf-8")

    status = "PASS_51_LINE_READER__479_TOKENS__136_OPEN__1_DCHEY_OVERRIDE__ZERO_HARD_GENERIC"
    result = {
        "status": status,
        "basis": {
            "touched_lines": 51, "tokens": 479, "pages": len({row["page"] for row in line_rows}),
            "new_pages_opened": 0, "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
            "gdt675_status": gdt675_result["status"],
        },
        "information": {
            "unknown_before_v50": totals["RESIDUAL_UNKNOWN"] + totals["NEW_V50"],
            "unknown_after_v50": totals["RESIDUAL_UNKNOWN"],
            "assigned_before_v50": 479 - totals["RESIDUAL_UNKNOWN"] - totals["NEW_V50"],
            "assigned_after_v50": 479 - totals["RESIDUAL_UNKNOWN"],
            "assigned_fraction_before": f"{(479 - 187) / 479:.6f}",
            "assigned_fraction_after": f"{(479 - 136) / 479:.6f}",
            "new_v50_positions": totals["NEW_V50"],
            "inherited_narrow_carrier_positions": totals["INHERITED_NARROW_CARRIER"],
            "inherited_other_assigned_positions": totals["INHERITED_OTHER_ASSIGNED"],
            "literal_narrow_carrier_positions": literal_narrow_carrier_positions,
            "literal_narrow_carrier_matches": literal_narrow_carrier_matches,
            "working_narrow_carrier_positions": working_narrow_carrier_positions,
            "working_narrow_carrier_matches": working_narrow_carrier_matches,
            "assigned_extended_class_carrier_positions": assigned_extended_class_positions,
            "assigned_extended_class_carrier_fraction": f"{assigned_extended_class_positions / 343:.6f}",
            "literal_hard_generic_matches": literal_generic_matches,
            "working_hard_generic_matches": working_generic_matches,
        },
        "lines": {
            "complete": 2, "with_residual_unknown": 49,
            "at_most_one_unknown": sum(int(row["residual_unknown_positions"]) <= 1 for row in line_rows),
            "at_most_two_unknown": len(low_residual_rows),
            "unknown_distribution": {str(key): distribution[key] for key in sorted(distribution)},
            "modes": dict(sorted(Counter(str(row["line_mode"]) for row in line_rows).items())),
            "licensed_action_positions": sum(int(row["action_positions"]) for row in line_rows),
            "lines_with_licensed_action": sum(int(row["action_positions"]) > 0 for row in line_rows),
        },
        "renderer": {
            "gdt675_applications_hold_at_line_scale": line_scale_holds,
            "named_line_scale_overrides": len(line_scale_override_loci),
            "override_locus": line_scale_override_loci[0],
            "override": "initial dchey becomes a nominal measured dry result before adjacent quantity III",
            "value_bindings": sum(row["decision"] in {"BIND", "BIND_NOMINAL"} for row in value_rows),
            "provisional_value_bindings": sum(row["decision"] == "PROVISIONAL" for row in value_rows),
            "rejected_value_jumps": sum(row["decision"] == "REJECT_JUMP" for row in value_rows),
            "syntax_templates": len(templates),
        },
        "next_frontier": {
            "low_residual_lines": len(low_residual_rows),
            "best_complete_multitoken": "f112v.10",
            "best_consecutive_passage": "f86v6.4|f86v6.5",
            "best_action_contrast_passage": "f86v3.18|f86v3.19",
        },
        "files": {},
        "claim_ceiling": (
            "A token-preserving practical reader for 51 already touched V50 lines. It renders all 479 positions, "
            "but 136 remain explicitly unknown, 113 working-reader positions match the narrow carrier screen, and "
            "311 of 343 assigned literal values match an explicitly broad extended class sensitivity screen. Only "
            "two lines are complete. This is not plaintext, a historical codebook, or proof of manuscript-wide language, lexemes, "
            "substances, procedures, plants, diseases, patients or cures."
        ),
    }
    for path in sorted(ART.glob("*.tsv")):
        result["files"][path.name] = sha256(path)
    result["files"]["GDT676_V50_EXTERNAL_WORKING_READER.md"] = sha256(
        ART / "GDT676_V50_EXTERNAL_WORKING_READER.md"
    )
    (ART / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": status, "information": result["information"], "lines": result["lines"],
        "renderer": result["renderer"], "next_frontier": result["next_frontier"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
