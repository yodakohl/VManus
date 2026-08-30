#!/usr/bin/env python3
"""Build the GDT675 f81r-card exact-occurrence transfer scan."""

from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt675_f81r_card_occurrence_conflict_scan"
ART = EXP / "artifacts"
CARDS_PATH = ROOT / "experiments/yolo/gdt674_v49_f81r_concrete_renderer/src/F81R_TRANSFER_CARDS.tsv"
REVIEW_PATH = ROOT / "experiments/yolo/gdt674_v49_f81r_concrete_renderer/artifacts/F81R_REVIEW_CARDS.tsv"
TRACES_PATH = ROOT / "experiments/yolo/gdt674_v49_f81r_concrete_renderer/artifacts/F81R_COMPONENT_TRACES.tsv"
PANEL_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/ALL_LINE_CONCRETE_COVERAGE_V48.tsv"
ALLOWLIST_PATH = ROOT / "experiments/yolo/gdt671_fifteen_residual_family_completion/artifacts/PAGE_ALLOWLIST.tsv"
GDT673_OCCURRENCES_PATH = ROOT / "experiments/yolo/gdt673_v48_transfer_occurrence_conflict_scan/artifacts/TRANSFERABLE_EXACT_OCCURRENCES.tsv"
GDT673_RUN_PATH = ROOT / "experiments/yolo/gdt673_v48_transfer_occurrence_conflict_scan/src/run.py"
DECISIONS_PATH = EXP / "src/CARD_TRANSFER_DECISIONS.tsv"


def load_gdt673_utilities():
    spec = importlib.util.spec_from_file_location("gdt673_run", GDT673_RUN_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load GDT673 guarded-reader utilities")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


UTIL = load_gdt673_utilities()
read_tsv = UTIL.read_tsv
write_tsv = UTIL.write_tsv
sha256 = UTIL.sha256
split_parallel = UTIL.split_parallel
unknown_ordinals = UTIL.unknown_ordinals
position_class = UTIL.position_class
reader_operations = UTIL.reader_operations
guarded_cross_query = UTIL.guarded_cross_query


def joined_counter(values: list[str]) -> str:
    counts = Counter(values)
    return "|".join(f"{key}:{counts[key]}" for key in sorted(counts)) or "NONE"


def external_render(card: dict[str, str], manual: dict[str, str], line_position: str) -> str:
    if manual["render_mode"] == "INITIAL_ACTION_ELSE_NOMINAL" and line_position == "INITIAL":
        return card["working_meaning_de"]
    return manual["external_working_meaning_de"]


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    cards = read_tsv(CARDS_PATH)
    reviews = read_tsv(REVIEW_PATH)
    traces = read_tsv(TRACES_PATH)
    panel = read_tsv(PANEL_PATH)
    allow_rows = read_tsv(ALLOWLIST_PATH)
    old_occurrences = read_tsv(GDT673_OCCURRENCES_PATH)
    decision_rows = read_tsv(DECISIONS_PATH)

    assert len(cards) == 23 and Counter(row["class"] for row in cards) == {"P": 20, "W": 3}
    assert len({row["surface"] for row in cards}) == 23
    card_by_surface = {row["surface"]: row for row in cards}
    assert {row["surface"] for row in reviews if row["surface"] in card_by_surface} == set(card_by_surface)
    decisions = {row["surface"]: row for row in decision_rows}
    assert set(decisions) == set(card_by_surface)
    assert all(
        row["decision"] in {
            "HOLD_SAME_CARD", "HOLD_WITH_ACTION_RESULT_SPLIT",
            "HOLD_WITH_SCOPE_SPLIT", "HOLD_LEARNED_WHOLE", "SOURCE_PAGE_ONLY_UNTESTED",
        }
        for row in decision_rows
    )
    assert len(panel) == 4128
    allowlist = [row["page"] for row in allow_rows]
    assert len(allowlist) == len(set(allowlist)) == 179
    assert "f81r" in allowlist and all(not page.lower().startswith("f84") for page in allowlist)
    assert set(row["page"] for row in panel) == set(allowlist)

    cross_rows, cross_guard = guarded_cross_query(allowlist)
    assert cross_guard["selected"] == len(cross_rows) == 4137
    assert cross_guard["skipped_forbidden"] > 0
    assert all(row["page"] in allowlist and not row["page"].lower().startswith("f84") for row in cross_rows)
    cross_by_locus = {row["locus"]: row for row in cross_rows}
    assert all(row["locus"] in cross_by_locus for row in panel)

    old_overlay_by_key = {
        (row["locus"], int(row["ordinal"])): row
        for row in old_occurrences
        if row["promotable"] == "1" and row["was_v48_unknown"] == "1"
    }
    assert len(old_overlay_by_key) == 162

    occurrences: list[dict[str, object]] = []
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    source_card_keys: set[tuple[str, int]] = set()
    for line in panel:
        tokens = line["zl3b_line"].split()
        base_glosses = split_parallel(line["token_glosses_de"])
        sources = split_parallel(line["gloss_sources"])
        states = split_parallel(line["scope_states"])
        assert len(tokens) == int(line["token_count"])
        assert len(tokens) == len(base_glosses) == len(sources) == len(states)
        v48_unknown = unknown_ordinals(line)
        v49_glosses = list(base_glosses)
        v49_sources = list(sources)
        v49_states = list(states)
        for index in range(1, len(tokens) + 1):
            previous = old_overlay_by_key.get((line["locus"], index))
            if previous:
                v49_glosses[index - 1] = previous["working_meaning_de"]
                v49_sources[index - 1] = "GDT673:EXACT_TRANSFER"
                v49_states[index - 1] = "ROLE_OR_WHOLE_EXACT_TRANSFER"

        hits = [(index, surface) for index, surface in enumerate(tokens, start=1) if surface in card_by_surface]
        if not hits:
            continue
        cross = cross_by_locus[line["locus"]]
        assert cross["zl3b_clean"].split() == tokens and cross["it2a_clean"] and cross["rf1b_clean"]
        it2a_ops = reader_operations(tokens, cross["it2a_clean"].split())
        rf1b_ops = reader_operations(tokens, cross["rf1b_clean"].split())
        for index, surface in hits:
            key = (line["locus"], index)
            card = card_by_surface[surface]
            manual = decisions[surface]
            was_v48_unknown = index in v48_unknown
            was_v49_unknown = was_v48_unknown and key not in old_overlay_by_key
            source_page = line["page"] == "f81r"
            if source_page:
                source_card_keys.add(key)
                occurrence_decision = "SOURCE_PAGE_CARD"
                promote_external = "0"
            else:
                assert manual["decision"] in {
                    "HOLD_SAME_CARD", "HOLD_WITH_ACTION_RESULT_SPLIT",
                    "HOLD_WITH_SCOPE_SPLIT", "HOLD_LEARNED_WHOLE",
                }
                occurrence_decision = "EXTERNAL_TRANSFER_HOLD"
                promote_external = "1"
            it2a_operation, it2a_render = it2a_ops[index - 1]
            rf1b_operation, rf1b_render = rf1b_ops[index - 1]
            reader_support = (
                "BOTH_EXACT" if it2a_operation == rf1b_operation == "EXACT"
                else "ONE_EXACT" if "EXACT" in {it2a_operation, rf1b_operation}
                else "NEITHER_EXACT"
            )
            item = {
                "surface": surface,
                "card_class": card["class"],
                "composition": card["composition"],
                "working_meaning_de": card["working_meaning_de"],
                "external_working_meaning_de": manual["external_working_meaning_de"],
                "applied_meaning_de": (
                    card["working_meaning_de"] if source_page
                    else external_render(card, manual, position_class(index, len(tokens)))
                ),
                "render_mode": manual["render_mode"],
                "strongest_rival_de": card["strongest_rival_de"],
                "confidence": card["confidence"],
                "page": line["page"], "locus": line["locus"], "section": line["section"],
                "language": line["language"], "hand": line["hand"], "ordinal": index,
                "line_token_count": len(tokens), "line_position": position_class(index, len(tokens)),
                "source_f81r": "1" if source_page else "0",
                "was_v48_unknown": "1" if was_v48_unknown else "0",
                "was_v49_unknown": "1" if was_v49_unknown else "0",
                "was_gdt674_unknown": "1" if was_v49_unknown and not source_page else "0",
                "target_v49_gloss_de": v49_glosses[index - 1],
                "target_v49_source": v49_sources[index - 1],
                "target_v49_scope_state": v49_states[index - 1],
                "left_surface": tokens[index - 2] if index > 1 else "BOUNDARY",
                "left_v49_gloss_de": v49_glosses[index - 2] if index > 1 else "BOUNDARY",
                "right_surface": tokens[index] if index < len(tokens) else "BOUNDARY",
                "right_v49_gloss_de": v49_glosses[index] if index < len(tokens) else "BOUNDARY",
                "it2a_operation": it2a_operation, "it2a_render": it2a_render,
                "rf1b_operation": rf1b_operation, "rf1b_render": rf1b_render,
                "reader_support": reader_support, "zl3b_line": line["zl3b_line"],
                "decision": occurrence_decision, "promote_external": promote_external,
                "review_note": manual["review_note"],
            }
            occurrences.append(item)
            by_surface[surface].append(item)

    assert len(occurrences) == 75 and len(source_card_keys) == 24
    assert all(row["was_v49_unknown"] == "1" for row in occurrences)
    external = [row for row in occurrences if row["source_f81r"] == "0"]
    source_occurrences = [row for row in occurrences if row["source_f81r"] == "1"]
    assert len(external) == 51 and len(source_occurrences) == 24
    assert all(row["was_gdt674_unknown"] == "1" for row in external)
    external_surfaces = {str(row["surface"]) for row in external}
    assert len(external_surfaces) == 12
    assert all(
        decisions[surface]["decision"] == "SOURCE_PAGE_ONLY_UNTESTED"
        for surface in set(card_by_surface) - external_surfaces
    )
    promoted_surfaces = {
        surface for surface in external_surfaces
        if decisions[surface]["decision"] in {
            "HOLD_SAME_CARD", "HOLD_WITH_ACTION_RESULT_SPLIT",
            "HOLD_WITH_SCOPE_SPLIT", "HOLD_LEARNED_WHOLE",
        }
    }
    assert promoted_surfaces == external_surfaces

    profile_rows: list[dict[str, object]] = []
    for card in cards:
        surface = card["surface"]
        hits = by_surface[surface]
        outside = [row for row in hits if row["source_f81r"] == "0"]
        manual = decisions[surface]
        profile_rows.append({
            "surface": surface, "card_class": card["class"], "composition": card["composition"],
            "working_meaning_de": card["working_meaning_de"], "confidence": card["confidence"],
            "external_working_meaning_de": manual["external_working_meaning_de"],
            "render_mode": manual["render_mode"],
            "source_positions": len(hits) - len(outside), "external_positions": len(outside),
            "external_lines": len({str(row["locus"]) for row in outside}),
            "external_pages": len({str(row["page"]) for row in outside}),
            "sections": joined_counter([str(row["section"]) for row in outside]),
            "languages": joined_counter([str(row["language"]) for row in outside]),
            "hands": joined_counter([str(row["hand"]) for row in outside]),
            "position_profile": joined_counter([str(row["line_position"]) for row in outside]),
            "reader_exact_both": sum(row["reader_support"] == "BOTH_EXACT" for row in outside),
            "reader_exact_one": sum(row["reader_support"] == "ONE_EXACT" for row in outside),
            "reader_exact_neither": sum(row["reader_support"] == "NEITHER_EXACT" for row in outside),
            "first_external_loci": "|".join(str(row["locus"]) for row in outside[:8]) or "NONE",
            "decision": manual["decision"], "promote_to_v50": "1" if surface in promoted_surfaces else "0",
            "review_note": manual["review_note"],
        })

    composition_rows: list[dict[str, object]] = []
    for card in cards:
        if card["class"] != "P":
            continue
        matching = [row for row in traces if row["eva"] == card["surface"] and row["route"] == "ROLE_COMPOSED_REVIEW"]
        assert matching
        first = min(int(row["global_ordinal"]) for row in matching)
        selected = sorted(
            (row for row in matching if int(row["global_ordinal"]) == first),
            key=lambda row: int(row["component_ordinal"]),
        )
        segments = [row["surface_segment"] for row in selected]
        roles = [row["component_role"] for row in selected]
        assert "".join(segments) == card["surface"] and "+".join(roles) == card["composition"]
        composition_rows.append({
            "surface": card["surface"], "composition": card["composition"],
            "segment_trace": "+".join(segments), "role_trace": "+".join(roles),
            "components": len(selected), "byte_complete": "1", "source_global_ordinal": first,
            "external_positions": sum(row["source_f81r"] == "0" for row in by_surface[card["surface"]]),
            "decision": decisions[card["surface"]]["decision"],
        })
    assert len(composition_rows) == 20

    touched_rows: list[dict[str, object]] = []
    newly_closed_rows: list[dict[str, object]] = []
    metrics: dict[str, Counter[str]] = {name: Counter() for name in ("V48", "GDT673", "GDT674", "GDT675")}
    for line in panel:
        tokens = line["zl3b_line"].split()
        base_glosses = split_parallel(line["token_glosses_de"])
        v48_unknown = unknown_ordinals(line)
        v49_unknown = {index for index in v48_unknown if (line["locus"], index) not in old_overlay_by_key}
        gdt674_unknown = {
            index for index in v49_unknown
            if not (line["page"] == "f81r" and tokens[index - 1] in card_by_surface)
        }
        applied = [
            index for index in sorted(gdt674_unknown)
            if line["page"] != "f81r" and tokens[index - 1] in promoted_surfaces
        ]
        gdt675_unknown = {index for index in gdt674_unknown if index not in applied}
        for name, unknown in {
            "V48": v48_unknown, "GDT673": v49_unknown,
            "GDT674": gdt674_unknown, "GDT675": gdt675_unknown,
        }.items():
            meter = metrics[name]
            meter["unknown"] += len(unknown)
            meter["complete"] += not unknown
            meter["one_unknown"] += len(unknown) == 1
            if len(tokens) > 1:
                meter["multi_complete"] += not unknown
                meter["multi_one_unknown"] += len(unknown) == 1
        if not applied:
            continue
        rendered = list(base_glosses)
        for index in range(1, len(tokens) + 1):
            previous = old_overlay_by_key.get((line["locus"], index))
            if previous:
                rendered[index - 1] = previous["working_meaning_de"]
            if line["page"] == "f81r" and index in v49_unknown and tokens[index - 1] in card_by_surface:
                rendered[index - 1] = card_by_surface[tokens[index - 1]]["working_meaning_de"]
        before_render = list(rendered)
        for index in applied:
            surface = tokens[index - 1]
            rendered[index - 1] = external_render(
                card_by_surface[surface], decisions[surface], position_class(index, len(tokens))
            )
        touched = {
            "page": line["page"], "locus": line["locus"], "section": line["section"],
            "language": line["language"], "hand": line["hand"], "zl3b_line": line["zl3b_line"],
            "unknown_after_gdt673": len(v49_unknown), "unknown_after_gdt674": len(gdt674_unknown),
            "applied_ordinals": "|".join(map(str, applied)),
            "applied_surfaces": "|".join(tokens[index - 1] for index in applied),
            "unknown_after_gdt675": len(gdt675_unknown),
            "remaining_unknown_ordinals": "|".join(map(str, sorted(gdt675_unknown))) or "NONE",
            "remaining_unknown_surfaces": "|".join(tokens[index - 1] for index in sorted(gdt675_unknown)) or "NONE",
            "before_overlay_glosses_de": " | ".join(before_render),
            "gdt675_overlay_glosses_de": " | ".join(rendered),
        }
        touched_rows.append(touched)
        if gdt674_unknown and not gdt675_unknown:
            newly_closed_rows.append(touched)

    assert len(touched_rows) == 51 and len(newly_closed_rows) == 2
    assert metrics["GDT673"]["unknown"] == 8018
    assert metrics["GDT674"]["unknown"] == 7994
    assert metrics["GDT675"]["unknown"] == 7943

    register_groups: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for row in external:
        register_groups[(str(row["section"]), str(row["language"]), str(row["hand"]))].append(row)
    register_rows = []
    for (section, language, hand), rows in sorted(register_groups.items()):
        register_rows.append({
            "section": section, "language": language, "hand": hand,
            "positions": len(rows), "surfaces": len({str(row["surface"]) for row in rows}),
            "lines": len({str(row["locus"]) for row in rows}), "pages": len({str(row["page"]) for row in rows}),
            "reader_exact_both": sum(row["reader_support"] == "BOTH_EXACT" for row in rows),
            "reader_exact_one": sum(row["reader_support"] == "ONE_EXACT" for row in rows),
            "reader_exact_neither": sum(row["reader_support"] == "NEITHER_EXACT" for row in rows),
        })

    occurrence_fields = [
        "surface", "card_class", "composition", "working_meaning_de", "external_working_meaning_de",
        "applied_meaning_de", "render_mode", "strongest_rival_de", "confidence",
        "page", "locus", "section", "language", "hand", "ordinal", "line_token_count", "line_position",
        "source_f81r", "was_v48_unknown", "was_v49_unknown", "was_gdt674_unknown", "target_v49_gloss_de",
        "target_v49_source", "target_v49_scope_state", "left_surface", "left_v49_gloss_de", "right_surface",
        "right_v49_gloss_de", "it2a_operation", "it2a_render", "rf1b_operation", "rf1b_render",
        "reader_support", "zl3b_line", "decision", "promote_external", "review_note",
    ]
    profile_fields = [
        "surface", "card_class", "composition", "working_meaning_de", "external_working_meaning_de",
        "render_mode", "confidence", "source_positions",
        "external_positions", "external_lines", "external_pages", "sections", "languages", "hands",
        "position_profile", "reader_exact_both", "reader_exact_one", "reader_exact_neither",
        "first_external_loci", "decision", "promote_to_v50", "review_note",
    ]
    touched_fields = [
        "page", "locus", "section", "language", "hand", "zl3b_line", "unknown_after_gdt673",
        "unknown_after_gdt674", "applied_ordinals", "applied_surfaces", "unknown_after_gdt675",
        "remaining_unknown_ordinals", "remaining_unknown_surfaces", "before_overlay_glosses_de",
        "gdt675_overlay_glosses_de",
    ]
    write_tsv(ART / "EXACT_OCCURRENCE_CONTEXTS.tsv", occurrences, occurrence_fields)
    write_tsv(ART / "EXTERNAL_TRANSFERABLE_OCCURRENCES.tsv", external, occurrence_fields)
    write_tsv(ART / "SOURCE_PAGE_CARD_OCCURRENCES.tsv", source_occurrences, occurrence_fields)
    write_tsv(ART / "CARD_PANEL_TRANSFER_PROFILE.tsv", profile_rows, profile_fields)
    write_tsv(
        ART / "COMPOSITION_BYTE_AUDIT.tsv", composition_rows,
        ["surface", "composition", "segment_trace", "role_trace", "components", "byte_complete",
         "source_global_ordinal", "external_positions", "decision"],
    )
    write_tsv(ART / "TOUCHED_LINE_OVERLAY.tsv", touched_rows, touched_fields)
    write_tsv(ART / "NEWLY_CLOSED_LINES.tsv", newly_closed_rows, touched_fields)
    write_tsv(
        ART / "TRANSFER_REGISTER_PROFILE.tsv", register_rows,
        ["section", "language", "hand", "positions", "surfaces", "lines", "pages",
         "reader_exact_both", "reader_exact_one", "reader_exact_neither"],
    )
    write_tsv(
        ART / "READER_RIVAL_OCCURRENCES.tsv",
        [row for row in occurrences if row["reader_support"] == "NEITHER_EXACT"], occurrence_fields,
    )
    promoted_rows = [{
        "surface": card["surface"], "card_class": card["class"], "composition": card["composition"],
        "source_working_meaning_de": card["working_meaning_de"],
        "working_meaning_de": decisions[card["surface"]]["external_working_meaning_de"],
        "render_mode": decisions[card["surface"]]["render_mode"],
        "source": "GDT675:GDT674_EXACT_EXTERNAL_TRANSFER",
        "scope_state": "ROLE_COMPOSED_EXACT_TRANSFER" if card["class"] == "P" else "LEARNED_EXACT_WHOLE_TRANSFER",
        "external_positions": sum(row["source_f81r"] == "0" for row in by_surface[card["surface"]]),
        "external_pages": len({str(row["page"]) for row in by_surface[card["surface"]] if row["source_f81r"] == "0"}),
    } for card in cards if card["surface"] in promoted_surfaces]
    write_tsv(
        ART / "V50_PANEL_TRANSFER_OVERLAY.tsv", promoted_rows,
        ["surface", "card_class", "composition", "source_working_meaning_de", "working_meaning_de",
         "render_mode", "source", "scope_state", "external_positions", "external_pages"],
    )
    write_tsv(
        ART / "SOURCE_ONLY_CARDS.tsv",
        [row for row in profile_rows if row["decision"] == "SOURCE_PAGE_ONLY_UNTESTED"], profile_fields,
    )

    reader_counts = Counter(str(row["reader_support"]) for row in occurrences)
    external_reader_counts = Counter(str(row["reader_support"]) for row in external)
    class_external = Counter(str(row["card_class"]) for row in external)
    card_status = Counter(str(row["decision"]) for row in profile_rows)
    assert reader_counts == {"BOTH_EXACT": 52, "ONE_EXACT": 18, "NEITHER_EXACT": 5}
    assert external_reader_counts == {"BOTH_EXACT": 42, "ONE_EXACT": 7, "NEITHER_EXACT": 2}
    assert class_external == {"P": 50, "W": 1}
    assert card_status == {
        "HOLD_SAME_CARD": 2, "HOLD_WITH_ACTION_RESULT_SPLIT": 4, "HOLD_WITH_SCOPE_SPLIT": 5,
        "SOURCE_PAGE_ONLY_UNTESTED": 11, "HOLD_LEARNED_WHOLE": 1,
    }
    status = "PASS_51_EXTERNAL_POSITIONS__12_CARDS_HOLD__9_RENDER_SPLITS__11_SOURCE_ONLY"
    result = {
        "status": status,
        "basis": {
            "panel_pages": len(allowlist), "panel_lines": len(panel),
            "panel_tokens": sum(int(row["token_count"]) for row in panel), "source_page": "f81r",
            "cross_transcription_lines_selected": len(cross_rows), "cross_guard": cross_guard,
            "new_pages_opened": 0, "f84": "FORBIDDEN", "f84r": "FORBIDDEN",
        },
        "cards": {
            "gdt674_candidate_cards": len(cards), "role_composed_cards": 20, "learned_whole_cards": 3,
            "externally_present_surfaces": len(external_surfaces),
            "externally_absent_source_only_surfaces": len(cards) - len(external_surfaces),
            "promoted_role_composed_surfaces": sum(card_by_surface[s]["class"] == "P" for s in promoted_surfaces),
            "retained_learned_whole_surfaces": sum(card_by_surface[s]["class"] == "W" for s in promoted_surfaces),
            "action_result_split_surfaces": card_status["HOLD_WITH_ACTION_RESULT_SPLIT"],
            "scope_or_boundary_split_surfaces": card_status["HOLD_WITH_SCOPE_SPLIT"],
            "full_byte_composition_audits": len(composition_rows), "named_context_conflict_surfaces": 0,
        },
        "occurrences": {
            "all_exact_positions": len(occurrences), "source_f81r_positions": len(source_occurrences),
            "external_positions": len(external), "external_lines": len({row["locus"] for row in external}),
            "external_pages": len({row["page"] for row in external}),
            "external_role_composed_positions": class_external["P"],
            "external_learned_whole_positions": class_external["W"],
            "reader_exact_both_all": reader_counts["BOTH_EXACT"],
            "reader_exact_one_all": reader_counts["ONE_EXACT"],
            "reader_exact_neither_all": reader_counts["NEITHER_EXACT"],
            "reader_exact_both_external": external_reader_counts["BOTH_EXACT"],
            "reader_exact_one_external": external_reader_counts["ONE_EXACT"],
            "reader_exact_neither_external": external_reader_counts["NEITHER_EXACT"],
            "external_sections": dict(sorted(Counter(str(row["section"]) for row in external).items())),
            "external_languages": dict(sorted(Counter(str(row["language"]) for row in external).items())),
            "external_hands": dict(sorted(Counter(str(row["hand"]) for row in external).items())),
        },
        "coverage_overlay": {
            "unknown_positions_before": metrics["GDT674"]["unknown"],
            "unknown_positions_after": metrics["GDT675"]["unknown"],
            "complete_lines_before": metrics["GDT674"]["complete"],
            "complete_lines_after": metrics["GDT675"]["complete"],
            "multi_token_complete_before": metrics["GDT674"]["multi_complete"],
            "multi_token_complete_after": metrics["GDT675"]["multi_complete"],
            "multi_token_one_unknown_before": metrics["GDT674"]["multi_one_unknown"],
            "multi_token_one_unknown_after": metrics["GDT675"]["multi_one_unknown"],
            "newly_closed_lines": len(newly_closed_rows),
        },
        "reader_rivals": {
            "all_neither_exact_positions": sum(row["reader_support"] == "NEITHER_EXACT" for row in occurrences),
            "external_neither_exact_positions": sum(
                row["reader_support"] == "NEITHER_EXACT" and row["source_f81r"] == "0" for row in occurrences
            ),
            "external_neither_exact_surface": "olkar",
        },
        "files": {},
        "claim_ceiling": (
            "An exploratory exact-spelling transfer test of GDT674's twenty composed cards and three learned "
            "wholes on the already admitted f84-free panel. Twelve surfaces retain their replaceable f81r meanings "
            "at 51 external positions; eleven remain source-page-only. This is not plaintext, a historical codebook, "
            "or proof of manuscript-wide lexemes, substances, procedures, language or phonetics."
        ),
    }
    for path in sorted(ART.glob("*.tsv")):
        result["files"][path.name] = sha256(path)
    (ART / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "status": status, "cards": result["cards"], "occurrences": result["occurrences"],
        "coverage_overlay": result["coverage_overlay"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
