#!/usr/bin/env python3
"""Project the final 23 reader-exact cardless wholes after ``ol``.

The selector is deliberately small and occurrence-free: a GDT780 row must be
a fallback, its complete right token must be reader-exact, and that complete
surface must occur in the frozen 23-row specification.  Analogy, recurrence,
location and proposed German wording are evidence metadata, never selectors.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Sequence

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
EXP = ROOT / "experiments/yolo/gdt781_ol_remaining_23_exploratory_whole_projection"
SRC = EXP / "src"
ART = EXP / "artifacts"
REPORT = EXP / "REPORT.md"
SPECS_PATH = SRC / "WHOLE_23_SPECS.tsv"
LOCK_PATH = SRC / "SOURCE_LOCK.tsv"
PARENT_ART = ROOT / "experiments/yolo/gdt780_ol_two_cardless_whole_bridge/artifacts"
PARENT_RENDERER = PARENT_ART / "GDT780_376_RENDERER.tsv"
PARENT_RESULT = PARENT_ART / "RESULT.json"
PARENT_RESIDUAL = PARENT_ART / "GDT780_RESIDUAL_129_FALLBACK_CENSUS.tsv"
PARENT_INTAKE = PARENT_ART / "GDT780_25_EXACT_CARDLESS_INTAKE.tsv"
G779_DICTIONARY = ROOT / "experiments/yolo/gdt779_ol_residual_v99r7_exact_whole_recovery/artifacts/GDT779_WORKING_DICTIONARY.tsv"
G734_DICTIONARY = ROOT / "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
G739_AXIS_SPECS = ROOT / "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/ANCHOR_AXIS_SPECS.tsv"
G745_CARDS = ROOT / "experiments/yolo/gdt745_exact_open_content_role_expansion/artifacts/CROSS_PAGE_ROLE_CARDS.tsv"
G762_NEIGHBORS = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/CANDIDATE_DIRECT_NEIGHBOR_DECK.tsv"
G762_NULL = ROOT / "experiments/yolo/gdt762_moist_medium_candidate_discrimination/artifacts/DIRECTED_PATTERN_NULL_CENSUS.tsv"
G748_SERIAL = ROOT / "experiments/yolo/gdt748_complete_whole_serial_paradigm_census/artifacts/COLLAPSED_POSITION_EVIDENCE.tsv"
G775_SLOT = ROOT / "experiments/yolo/gdt775_ol_right_complement_slot_test/artifacts/RIGHT_COMPLEMENT_SURFACE_CENSUS.tsv"
G780_SUPPLEMENTS = PARENT_ART / "GDT780_2_WORKING_DICTIONARY_EVIDENCE.tsv"

SOURCE_LOCK_SHA256 = "fb4d3d35b8208a3f36cd922516293379d80909c162384e09ec93635a0383d0ab"
SPEC_SHA256 = "96f34e57f97e06c2386e37bc4e9de3561bde8dd0b99b9c944835d9016a6c912e"
REMOVED_PARENT_FORMS = frozenset({"eees", "sheeol"})
FROZEN_SURFACES = frozenset({
    "chockhar", "sheeoy", "ear", "cheedaiin", "keeor", "keeed", "otlaiin",
    "chlor", "lkan", "chesey", "okes", "kcheeky", "chedor", "chealor",
    "okalor", "eses", "sheckhal", "shdair", "sheoly", "chsky",
    "chorcholsal", "cheokchey", "okachey",
})
SELECTION_RULE = (
    "GDT780_RENDERER_CONTEXTUAL_0_AND_RIGHT_READER_EXACT_1_AND_COMPLETE_"
    "RIGHT_SURFACE_IN_FROZEN_WHOLE_23_SPECS"
)
STATUS = (
    "PASS__23_EXPLORATORY_EXACT_WHOLES__23_FORMS__23_LOCI__"
    "270_CONTEXTUAL__106_FALLBACKS__230_CONSUMED__12_A3__10_A2__1_A0__"
    "NO_COMPONENT_EXPORT"
)
ANALOGY_TAG_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "CLOSE", "PASS", "BEGIN_STAGE",
    "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III",
)
EXPECTED_AXIS_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "VALUE", "PART",
    "MATERIAL", "PREPARATION", "PROCESS", "CLOSE", "PASS",
)
STAGE_PATTERNS = {
    "BEGIN_STAGE": re.compile(
        r"anfangsstufe|gradanfang|anfang des grades|grundform|grundstufe", re.I
    ),
    "MIDDLE_STAGE": re.compile(
        r"mittelstufe|gradmitte|mitte des grades|mittlere|mittelstufig", re.I
    ),
    "END_STAGE": re.compile(
        r"endstufe|gradende|ende des grades|vollständig|fertig|abgeschlossen", re.I
    ),
    "LEVEL_II": re.compile(r"(?:stufe|grad|index|wert|klasse|charge) ii\b", re.I),
    "LEVEL_III": re.compile(r"(?:stufe|grad|index|wert|klasse|charge) iii\b", re.I),
}
RETIRED_LITERAL_PATIENTS = ("pulver", "samen", "saat", "wurzel", "holz")


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def serialise(value: object) -> object:
    return int(value) if isinstance(value, bool) else value


def write_tsv(path: Path, rows: Iterable[Mapping[str, object]], fields: Sequence[str]) -> None:
    material = list(rows)
    assert material, path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(fields), delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in material:
            writer.writerow({field: serialise(row.get(field, "")) for field in fields})


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def joined(values: Iterable[str], order: Sequence[str] | None = None) -> str:
    members = set(values)
    selected = sorted(members) if order is None else [value for value in order if value in members]
    return "|".join(selected) or "NONE"


def count_string(values: Counter[str], order: Sequence[str]) -> str:
    return "|".join(f"{axis}:{values[axis]}" for axis in order if values[axis]) or "NONE"


def one_by(rows: Sequence[Mapping[str, str]], key: str) -> dict[str, dict[str, str]]:
    output: dict[str, dict[str, str]] = {}
    for row in rows:
        value = row[key]
        assert value not in output, (key, value)
        output[value] = dict(row)
    return output


def verify_locks() -> int:
    assert sha256(LOCK_PATH) == SOURCE_LOCK_SHA256, "SOURCE_LOCK.tsv changed"
    assert sha256(SPECS_PATH) == SPEC_SHA256, "WHOLE_23_SPECS.tsv changed"
    rows = read_tsv(LOCK_PATH)
    assert len(rows) == 14
    seen: set[str] = set()
    for row in rows:
        relative = Path(row["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        assert str(relative) not in seen
        seen.add(str(relative))
        source = ROOT / relative
        assert source.is_file(), source
        assert sha256(source) == row["expected_sha256"], f"source changed: {relative}"
    required = {
        PARENT_RENDERER, PARENT_RESULT, PARENT_RESIDUAL, PARENT_INTAKE,
        G779_DICTIONARY, G734_DICTIONARY, G739_AXIS_SPECS, G745_CARDS,
        G762_NEIGHBORS, G762_NULL, G748_SERIAL, G775_SLOT, G780_SUPPLEMENTS,
        ROOT / "tools/relation_edge_intake.py",
    }
    assert {str(path.relative_to(ROOT)) for path in required} == seen
    return len(rows)


def validate_specs(rows: Sequence[Mapping[str, str]]) -> dict[str, dict[str, str]]:
    expected_fields = [
        "surface", "default_de", "alternate_1_de", "alternate_2_de", "confidence",
        "analogy_tier", "functional_axes", "cache_occurrences",
        "reader_exact_occurrences", "reader_exact_pages", "positive_evidence",
        "counterevidence", "source_evidence", "card_class", "renderer_scope",
        "selected_by_exploratory_policy", "literal_identity", "confirmed_lexeme",
        "component_export_credit", "numeric_identity_confirmed",
        "specific_substance_confirmed", "default_is_translation",
    ]
    assert len(rows) == 23 and list(rows[0]) == expected_fields
    specs = one_by(rows, "surface")
    assert len(specs) == 23
    assert set(specs) == FROZEN_SURFACES
    assert Counter(row["analogy_tier"][:2] for row in rows) == Counter({"A3": 12, "A2": 10, "A0": 1})
    assert [row["surface"] for row in rows if row["analogy_tier"].startswith("A0")] == ["chorcholsal"]
    for row in rows:
        assert row["surface"] and " " not in row["surface"]
        assert len({row["default_de"], row["alternate_1_de"], row["alternate_2_de"]}) == 3
        assert row["selected_by_exploratory_policy"] == "1"
        assert row["literal_identity"] == "OPEN"
        for field in (
            "confirmed_lexeme", "component_export_credit", "numeric_identity_confirmed",
            "specific_substance_confirmed", "default_is_translation",
        ):
            assert row[field] == "0"
        if row["surface"] == "chorcholsal":
            assert row["renderer_scope"] == "EXACT_ENUMERATED_OL_CHORCHOLSAL_SPAN_ONLY"
        else:
            assert row["renderer_scope"] == "EXACT_OL_PLUS_COMPLETE_WHOLE_ONLY"
    assert specs["eses"]["analogy_tier"] == "A2_DISTANCE2_MULTIWHOLE_CONSENSUS"
    assert specs["eses"]["functional_axes"] == "PREPARATION"
    assert specs["sheeoy"]["analogy_tier"] == "A3_DISTANCE1_MULTIWHOLE_CONSENSUS"
    assert specs["sheeoy"]["functional_axes"] == "MOIST|END_STAGE"
    assert specs["chorcholsal"]["functional_axes"] == "DRY|PART|MATERIAL|PREPARATION"
    return specs


def load_axis_patterns() -> dict[str, re.Pattern[str]]:
    rows = read_tsv(G739_AXIS_SPECS)
    assert tuple(row["axis_id"] for row in rows) == EXPECTED_AXIS_ORDER
    return {
        row["axis_id"]: re.compile(row["keyword_regex"].replace("\\\\", "\\"), re.I)
        for row in rows
    }


def analogy_tags(text: str, patterns: Mapping[str, re.Pattern[str]]) -> set[str]:
    tags = {axis for axis, pattern in patterns.items() if pattern.search(text)}
    if re.search(r"koch|ausgekoch", text, re.I):
        tags.add("HOT")
    tags.update(axis for axis, pattern in STAGE_PATTERNS.items() if pattern.search(text))
    return tags


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, 1):
        current = [left_index]
        for right_index, right_char in enumerate(right, 1):
            current.append(min(
                current[-1] + 1,
                previous[right_index] + 1,
                previous[right_index - 1] + int(left_char != right_char),
            ))
        previous = current
    return previous[-1]


def build_clean_pool() -> tuple[dict[str, dict[str, object]], dict[str, int]]:
    patterns = load_axis_patterns()
    dictionary = read_tsv(G734_DICTIONARY)
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in dictionary:
        meaning = row["working_meaning_de"]
        if not row["working_model_level"].startswith(("W2", "W3")):
            continue
        if row["gdt734_composition_semantic_credit"] != "0":
            continue
        if row["gdt734_component_export_allowed"] != "0":
            continue
        if row["gdt734_renderer_decision"] == "HOLD_UNCHANGED":
            continue
        if any(word in meaning.lower() for word in RETIRED_LITERAL_PATIENTS):
            continue
        if not analogy_tags(meaning, patterns):
            continue
        grouped[row["surface"]].append(row)

    pool: dict[str, dict[str, object]] = {}
    for surface, source_rows in grouped.items():
        reading_tags = [analogy_tags(row["working_meaning_de"], patterns) for row in source_rows]
        core_tags = set.intersection(*reading_tags)
        if not core_tags:
            continue
        ranked = sorted(source_rows, key=lambda row: (
            -int(row["working_model_level"].startswith("W3")),
            -int(row["working_model_score_0_100_not_probability"]),
            row["reading_id"],
        ))
        glosses = list(dict.fromkeys(row["working_meaning_de"] for row in ranked))
        pool[surface] = {
            "core_tags": core_tags,
            "union_tags": set.union(*reading_tags),
            "reading_ids": "|".join(row["reading_id"] for row in ranked),
            "levels": joined(row["working_model_level"] for row in source_rows),
            "max_score": max(int(row["working_model_score_0_100_not_probability"]) for row in source_rows),
            "occurrences": max(int(row["occurrence_count"]) for row in source_rows),
            "pages": max(int(row["page_count"]) for row in source_rows),
            "best_gloss": glosses[0],
            "all_glosses": " || ".join(glosses),
        }
    diagnostics = {
        "dictionary_rows": len(dictionary),
        "clean_axis_reading_rows": sum(len(rows) for rows in grouped.values()),
        "clean_axis_whole_pool": len(pool),
    }
    assert diagnostics["clean_axis_reading_rows"] == 770
    assert diagnostics["clean_axis_whole_pool"] == 769
    assert not (REMOVED_PARENT_FORMS & set(pool))
    return pool, diagnostics


def analogy_class(tags: set[str]) -> str:
    quality = tags & {"HOT", "COLD", "DRY", "MOIST"}
    carrier = tags & {"MATERIAL", "PREPARATION"}
    quantity = tags & {"AMOUNT", "PART"}
    process = tags & {"PROCESS", "CLOSE", "PASS"}
    stage = tags & {"BEGIN_STAGE", "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III"}
    if quality and carrier:
        return "QUALIFIED_MATERIAL_OR_PREPARATION_WHOLE"
    if quality and process:
        return "QUALITY_PROCESS_OR_RESULT_WHOLE"
    if quality:
        return "QUALITY_OR_STATE_WHOLE"
    if quantity and carrier:
        return "QUANTIFIED_MATERIAL_OR_PREPARATION_WHOLE"
    if quantity:
        return "QUANTITY_OR_PART_WHOLE"
    if carrier:
        return "MATERIAL_OR_PREPARATION_WHOLE"
    if process:
        return "PROCESS_OR_RESULT_WHOLE"
    if stage:
        return "STAGE_OR_RESULT_WHOLE"
    return "MIXED_OR_OPEN_WHOLE"


def build_raw_analogy(
    surfaces: set[str], pool: Mapping[str, Mapping[str, object]],
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    relations: list[dict[str, object]] = []
    summaries: dict[str, dict[str, object]] = {}
    for candidate in sorted(surfaces):
        neighbors = sorted(
            (levenshtein(candidate, known), known, record)
            for known, record in pool.items()
            if known != candidate and levenshtein(candidate, known) <= 2
        )
        if not neighbors:
            summaries[candidate] = {
                "raw_min_edit_distance": "NA", "raw_selected_radius": 0,
                "raw_neighbor_wholes": 0, "raw_closest_neighbor_wholes": 0,
                "raw_neighbor_surfaces": "NONE", "raw_nearest_glosses_de": "NONE",
                "raw_consensus_axes": "NONE", "raw_rival_axes": "NONE",
                "raw_axis_support": "NONE", "raw_functional_class": "MIXED_OR_OPEN_WHOLE",
                "raw_analogy_tier": "A0_NO_CLEAN_NEIGHBOR",
            }
            continue
        minimum = neighbors[0][0]
        closest = [item for item in neighbors if item[0] == minimum]
        radius = minimum if len(closest) >= 2 or minimum == 2 else 2
        selected = [item for item in neighbors if item[0] <= radius]
        counts: Counter[str] = Counter(
            axis for _, _, record in selected for axis in record["core_tags"]  # type: ignore[union-attr]
        )
        consensus = {
            axis for axis, count in counts.items()
            if axis != "VALUE" and count >= 2 and count / len(selected) >= 0.60
        }
        rivals = {
            axis for axis, count in counts.items()
            if axis != "VALUE" and axis not in consensus and count >= 1
        }
        if consensus and minimum == 1 and len(closest) >= 2:
            tier = "A3_DISTANCE1_MULTIWHOLE_CONSENSUS"
        elif consensus and minimum == 1:
            tier = "A2_DISTANCE1_PLUS_RADIUS2_CONSENSUS"
        elif consensus:
            tier = "A2_DISTANCE2_MULTIWHOLE_CONSENSUS"
        elif len(selected) == 1:
            tier = "A1_SINGLE_NEIGHBOR_LEAD"
        else:
            tier = "A1_MIXED_NEIGHBORHOOD"
        summaries[candidate] = {
            "raw_min_edit_distance": minimum, "raw_selected_radius": radius,
            "raw_neighbor_wholes": len(selected),
            "raw_closest_neighbor_wholes": len(closest),
            "raw_neighbor_surfaces": "|".join(item[1] for item in selected),
            "raw_nearest_glosses_de": " || ".join(
                f"{known}={record['best_gloss']}" for _, known, record in closest
            ),
            "raw_consensus_axes": joined(consensus, ANALOGY_TAG_ORDER),
            "raw_rival_axes": joined(rivals, ANALOGY_TAG_ORDER),
            "raw_axis_support": count_string(counts, ANALOGY_TAG_ORDER),
            "raw_functional_class": analogy_class(consensus),
            "raw_analogy_tier": tier,
        }
        for distance, known, record in selected:
            relations.append({
                "relation_id": f"G781-A{len(relations) + 1:04d}",
                "candidate_surface": candidate, "known_neighbor_surface": known,
                "whole_levenshtein_distance": distance,
                "within_raw_closest_layer": int(distance == minimum),
                "raw_selected_radius": radius,
                "known_neighbor_reading_ids": record["reading_ids"],
                "known_neighbor_levels": record["levels"],
                "known_neighbor_max_score_not_probability": record["max_score"],
                "known_neighbor_occurrences": record["occurrences"],
                "known_neighbor_pages": record["pages"],
                "known_neighbor_core_axes": joined(record["core_tags"], ANALOGY_TAG_ORDER),
                "known_neighbor_union_axes": joined(record["union_tags"], ANALOGY_TAG_ORDER),
                "known_neighbor_best_gloss_de": record["best_gloss"],
                "known_neighbor_all_glosses_de": record["all_glosses"],
                "candidate_raw_consensus_axes": joined(consensus, ANALOGY_TAG_ORDER),
                "candidate_raw_rival_axes": joined(rivals, ANALOGY_TAG_ORDER),
                "candidate_raw_analogy_tier": tier,
                "relation_scope": "COMPLETE_WHOLE_EDIT_ANALOGY_ONLY",
                "selector_credit": 0, "literal_identity_credit": 0,
                "component_export_credit": 0,
            })
    assert len(relations) == 135
    assert Counter(str(row["raw_analogy_tier"])[:2] for row in summaries.values()) == Counter({"A3": 12, "A2": 10, "A0": 1})
    return relations, summaries


def select_gdt781_row(
    parent_contextual: str, right_reader_exact: str, right_surface: str,
    frozen_surfaces: frozenset[str],
) -> bool:
    """Pure selector over exactly the three preregistered parent properties."""
    return parent_contextual == "0" and right_reader_exact == "1" and right_surface in frozen_surfaces


def reconstruct_cohort(
    parent_intake: Sequence[Mapping[str, str]], specs: Mapping[str, Mapping[str, str]],
) -> list[dict[str, object]]:
    assert len(parent_intake) == 25
    cohort_source = [row for row in parent_intake if row["right_surface"] not in REMOVED_PARENT_FORMS]
    assert len(cohort_source) == 23
    assert {row["right_surface"] for row in cohort_source} == set(specs)
    assert all(row["selected_by_pure_rule"] == "0" for row in cohort_source)
    output: list[dict[str, object]] = []
    for number, source in enumerate(cohort_source, 1):
        output.append({
            "cohort_id": f"G781-I{number:03d}",
            "parent_intake_id": source["intake_id"],
            "target_occurrence_id": source["target_occurrence_id"],
            "page": source["page"], "physical_folio": source["physical_folio"],
            "locus": source["locus"], "section": source["section"],
            "language": source["language"], "hand": source["hand"],
            "ol_ordinal": int(source["ol_ordinal"]),
            "right_ordinal": int(source["right_ordinal"]),
            "right_surface": source["right_surface"],
            "right_reader_exact": int(source["right_reader_exact"]),
            "parent_gdt780_selected": int(source["selected_by_pure_rule"]),
            "frozen_whole_23_member": 1,
            "selection_rule": SELECTION_RULE,
            "selection_uses_occurrence_id": 0, "selection_uses_page_or_locus": 0,
            "selection_uses_analogy_or_meaning": 0, "selection_uses_frequency": 0,
            "selection_uses_substring": 0, "default_is_translation": 0,
            "confirmed_lexeme": 0, "component_export_credit": 0,
        })
    assert len({row["target_occurrence_id"] for row in output}) == 23
    assert len({row["locus"] for row in output}) == 23
    assert len({row["page"] for row in output}) == 23
    assert len({row["physical_folio"] for row in output}) == 20
    return output


def inherited_owner_map(base: Sequence[Mapping[str, str]]) -> dict[str, str]:
    owners: dict[str, str] = {}
    for row in base:
        value = row["gdt780_consumed_token_ids"]
        count = int(row["gdt780_consumed_token_count"])
        tokens = [] if value == "NONE" else value.split("|")
        assert len(tokens) == count
        for token in tokens:
            assert token not in owners
            owners[token] = row["target_occurrence_id"]
    assert len(owners) == 207
    return owners


def verify_chorcholsal_frame(
    specs: Mapping[str, Mapping[str, str]],
) -> dict[str, str]:
    """Resolve the readable f88r.22 field list from locked whole-card values."""
    wanted = {"ychey", "okaiin", "chol", "cheor"}
    g734_rows = [row for row in read_tsv(G734_DICTIONARY) if row["surface"] in wanted]
    assert len(g734_rows) == 4
    g734 = one_by(g734_rows, "surface")
    assert g734["ychey"]["v99r7_spoken_default_de"] == "trockne hiervon bis zur Mittelstufe und schließe ab"
    assert g734["okaiin"]["v99r7_spoken_default_de"] == "heißer Ansatz, Grad III"
    assert g734["chol"]["v99r7_spoken_default_de"] == "trocken"
    assert g734["cheor"]["v99r7_spoken_default_de"] == "trockener Drogenteil"
    assert all(g734[surface]["gdt734_component_export_allowed"] == "0" for surface in wanted)
    g779 = one_by(read_tsv(G779_DICTIONARY), "entry")
    assert g779["cheor"]["preferred_gdt779_default_de"] == "trockener Teil"
    assert g779["cheor"]["component_export_credit"] == "0"
    assert specs["chorcholsal"]["default_de"] == "getrocknete Stoffzubereitung"
    source_values = {
        "ychey": g734["ychey"]["v99r7_spoken_default_de"],
        "okaiin": g734["okaiin"]["v99r7_spoken_default_de"],
        "chol": g734["chol"]["v99r7_spoken_default_de"],
        "cheor": g779["cheor"]["preferred_gdt779_default_de"],
        "chorcholsal": specs["chorcholsal"]["default_de"],
    }
    return {
        "working_display": (
            "Trocknung bis zur Mittelstufe, dann Abschluss | Heißansatz, Grad III | "
            "trocken | trockener Teil | getrocknete Stoffzubereitung"
        ),
        "source_values": " || ".join(f"{surface}={source_values[surface]}" for surface in (
            "ychey", "okaiin", "chol", "cheor", "chorcholsal"
        )),
    }


def build_spans(
    base: Sequence[Mapping[str, str]], specs: Mapping[str, Mapping[str, str]],
    summaries: Mapping[str, Mapping[str, object]],
) -> list[dict[str, object]]:
    assert frozenset(specs) == FROZEN_SURFACES
    matches = [
        row for row in base
        if select_gdt781_row(
            row["gdt780_renderer_contextual"], row["right_reader_exact"],
            row["right_surface"], FROZEN_SURFACES,
        )
    ]
    all_deck_matches = [row for row in base if row["right_surface"] in FROZEN_SURFACES]
    assert matches == all_deck_matches and len(matches) == 23
    assert all(row["gdt780_renderer_contextual"] == "0" for row in matches)
    assert all(row["right_reader_exact"] == "1" for row in matches)
    owners = inherited_owner_map(base)
    spans: list[dict[str, object]] = []
    for number, source in enumerate(matches, 1):
        surface, spec, raw = source["right_surface"], specs[source["right_surface"]], summaries[source["right_surface"]]
        ol_ordinal, right_ordinal = int(source["ordinal"]), int(source["right_ordinal"])
        tokens = source["written_line_eva"].split()
        assert right_ordinal == ol_ordinal + 1
        assert tokens[ol_ordinal - 1] == "ol" and tokens[right_ordinal - 1] == surface
        assert source["gdt780_consumed_token_count"] == "0"
        assert source["gdt780_consumed_token_ids"] == "NONE"
        assert spec["default_de"] != source["gdt780_default_de"]
        assert raw["raw_analogy_tier"] == spec["analogy_tier"], surface
        if surface != "chorcholsal":
            assert raw["raw_consensus_axes"] == spec["functional_axes"], surface
        else:
            assert raw["raw_consensus_axes"] == "NONE"
            assert source["target_occurrence_id"] == "G769-T0488"
            assert source["locus"] == "f88r.22" and ol_ordinal == 5 and right_ordinal == 6
        token_id = f"{source['locus']}@{right_ordinal}"
        assert token_id not in owners
        spans.append({
            "span_id": f"G781-S{number:03d}",
            "target_occurrence_id": source["target_occurrence_id"],
            "page": source["page"], "physical_folio": source["physical_folio"],
            "locus": source["locus"], "section": source["section"],
            "language": source["language"], "hand": source["hand"],
            "register_id": f"{source['section']}|{source['language']}|{source['hand']}",
            "ol_ordinal": ol_ordinal, "right_ordinal": right_ordinal,
            "line_token_count": len(tokens), "right_surface": surface,
            "written_span_eva": f"ol {surface}", "written_line_eva": source["written_line_eva"],
            "right_reader_exact": 1,
            "old_gdt780_branch": source["gdt780_branch"],
            "old_gdt780_default_de": source["gdt780_default_de"],
            "old_gdt780_contextual": 0,
            "selected_whole_default_de": spec["default_de"],
            "new_gdt781_default_de": spec["default_de"],
            "alternate_1_de": spec["alternate_1_de"],
            "alternate_2_de": spec["alternate_2_de"],
            "confidence": spec["confidence"], "analogy_tier": spec["analogy_tier"],
            "raw_analogy_consensus_axes": raw["raw_consensus_axes"],
            "working_functional_axes": spec["functional_axes"],
            "card_class": spec["card_class"], "source_evidence": spec["source_evidence"],
            "positive_evidence": spec["positive_evidence"],
            "counterevidence": spec["counterevidence"],
            "scope_status": spec["renderer_scope"],
            "semantic_change_class": "EXPLORATORY_FALLBACK_REPLACEMENT",
            "fallback_replacement": 1, "display_changed": 1,
            "inherited_consumed_token_ids": source["gdt780_consumed_token_ids"],
            "gdt781_consumed_token_id": token_id,
            "same_row_inherited_consumption_takeover": 0,
            "new_unique_consumption": 1, "cross_row_consumption_collision": 0,
            "selection_rule": SELECTION_RULE, "selection_uses_occurrence_id": 0,
            "selection_uses_page_or_locus": 0, "selection_uses_analogy_or_meaning": 0,
            "selection_uses_frequency": 0, "selection_uses_substring": 0,
            "exact_complete_whole_only": 1, "default_is_translation": 0,
            "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    assert len({row["right_surface"] for row in spans}) == 23
    assert len({row["locus"] for row in spans}) == 23
    assert len({row["page"] for row in spans}) == 23
    assert len({row["physical_folio"] for row in spans}) == 20
    return spans


def build_evidence(
    specs: Mapping[str, Mapping[str, str]], summaries: Mapping[str, Mapping[str, object]],
    spans: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    g762_rows = read_tsv(G762_NEIGHBORS)
    recurrence = {
        surface: [
            row for row in g762_rows
            if row["candidate_surface"] == "ol" and row["neighbor_surface"] == surface
        ]
        for surface in specs
    }
    assert all(len(rows) == 1 for rows in recurrence.values())
    null_by_surface = one_by(read_tsv(G762_NULL), "surface")
    slot_by_surface = one_by(read_tsv(G775_SLOT), "right_surface")
    serial_rows = read_tsv(G748_SERIAL)
    serial_by_surface = defaultdict(list)
    for row in serial_rows:
        if row["target_surface"] in specs:
            serial_by_surface[row["target_surface"]].append(row)
    assert set(serial_by_surface) == {"cheedaiin", "otlaiin"}
    supplements = one_by(read_tsv(G780_SUPPLEMENTS), "entry")
    assert set(supplements) == REMOVED_PARENT_FORMS
    supplement_by_surface: dict[str, list[tuple[str, int, dict[str, str]]]] = {}
    for surface in specs:
        supplement_by_surface[surface] = [
            (entry, levenshtein(surface, entry), record)
            for entry, record in sorted(supplements.items())
            if levenshtein(surface, entry) <= 2
        ]
    assert sum(len(rows) for rows in supplement_by_surface.values()) == 5
    assert {(surface, item[0]) for surface, rows in supplement_by_surface.items() for item in rows} == {
        ("sheeoy", "sheeol"), ("keeed", "eees"), ("okes", "eees"),
        ("eses", "eees"), ("sheoly", "sheeol"),
    }
    g745_rows = [row for row in read_tsv(G745_CARDS) if row["candidate_surface"] in specs]
    assert len(g745_rows) == 1 and g745_rows[0]["candidate_surface"] == "okalor"
    g745_okalor = g745_rows[0]
    assert g745_okalor["gdt745_card_id"] == "G745-C018"
    assert g745_okalor["analogy_confidence_level"] == summaries["okalor"]["raw_analogy_tier"]
    assert g745_okalor["analogy_consensus_axes"] == summaries["okalor"]["raw_consensus_axes"]
    assert g745_okalor["analogy_neighbor_surfaces"] == summaries["okalor"]["raw_neighbor_surfaces"]
    span_by_surface = {str(row["right_surface"]): row for row in spans}

    output: list[dict[str, object]] = []
    for number, spec in enumerate(specs.values(), 1):
        surface = spec["surface"]
        raw = summaries[surface]
        recurrent = recurrence[surface][0]
        assert recurrent["global_reader_exact_occurrences"] == spec["reader_exact_occurrences"]
        assert recurrent["global_reader_exact_pages"] == spec["reader_exact_pages"]
        assert slot_by_surface[surface]["fallback_target_tokens"] == "1"
        assert slot_by_surface[surface]["slot_evidence_tier"] == "UNINFORMATIVE"
        exact_occ = int(spec["reader_exact_occurrences"])
        null = null_by_surface.get(surface)
        if exact_occ > 1:
            assert null is not None
            assert null["reader_exact_occurrences"] == spec["reader_exact_occurrences"]
            assert null["reader_exact_pages"] == spec["reader_exact_pages"]
        else:
            assert null is None
        external_axes = "NONE"
        target_local_axes = spec["functional_axes"] if surface == "chorcholsal" else "NONE"
        serial_evidence_ids = "NONE"
        serial_bridge_tiers = "NONE"
        if surface in serial_by_surface:
            rows = serial_by_surface[surface]
            assert len(rows) == 1
            serial = rows[0]
            serial_evidence_ids = serial["evidence_id"]
            serial_bridge_tiers = serial["whole_form_bridge_tier"]
            assert serial["best_predicted_axes"] == "END_STAGE"
            assert serial["whole_form_bridge_tier"] == "B0_NO_WHOLE_FORM_BRIDGE"
            span = span_by_surface[surface]
            same_target = (
                serial["locus"] == span["locus"]
                and int(serial["target_ordinal"]) == int(span["right_ordinal"])
            )
            if surface == "cheedaiin":
                assert not same_target and serial["evidence_id"] == "G748-E0313"
                external_axes = "END_STAGE"
            else:
                assert same_target and serial["evidence_id"] == "G748-E0391"
                target_local_axes = "END_STAGE"
        later = supplement_by_surface[surface]
        output.append({
            "card_id": f"G781-C{number:03d}", "surface": surface,
            "preferred_gdt781_default_de": spec["default_de"],
            "alternate_1_de": spec["alternate_1_de"],
            "alternate_2_de": spec["alternate_2_de"],
            "confidence": spec["confidence"], "card_class": spec["card_class"],
            "renderer_scope": spec["renderer_scope"],
            "selected_exact_fallback_contexts": 1,
            "raw_pool_reading_rows": 770, "raw_pool_wholes": 769,
            "raw_analogy_tier": raw["raw_analogy_tier"],
            "raw_min_edit_distance": raw["raw_min_edit_distance"],
            "raw_selected_radius": raw["raw_selected_radius"],
            "raw_neighbor_wholes": raw["raw_neighbor_wholes"],
            "raw_closest_neighbor_wholes": raw["raw_closest_neighbor_wholes"],
            "raw_neighbor_surfaces": raw["raw_neighbor_surfaces"],
            "raw_nearest_glosses_de": raw["raw_nearest_glosses_de"],
            "raw_consensus_axes": raw["raw_consensus_axes"],
            "raw_rival_axes": raw["raw_rival_axes"],
            "raw_axis_support": raw["raw_axis_support"],
            "raw_functional_class": raw["raw_functional_class"],
            "later_supplement_surfaces": "|".join(item[0] for item in later) or "NONE",
            "later_supplement_edit_distances": "|".join(str(item[1]) for item in later) or "NONE",
            "later_supplement_defaults_de": " || ".join(
                f"{item[0]}={item[2]['preferred_gdt780_default_de']}" for item in later
            ) or "NONE",
            "later_supplement_functional_axes": " || ".join(
                f"{item[0]}={item[2]['functional_axis']}" for item in later
            ) or "NONE",
            "later_supplement_pool_vote_credit": 0,
            "external_serial_axes": external_axes,
            "target_local_axes": target_local_axes,
            "serial_evidence_ids": serial_evidence_ids,
            "serial_whole_bridge_tiers": serial_bridge_tiers,
            "working_functional_axes": spec["functional_axes"],
            "cache_occurrences": int(spec["cache_occurrences"]),
            "reader_exact_occurrences": exact_occ,
            "reader_exact_pages": int(spec["reader_exact_pages"]),
            "gdt762_direct_ol_contacts": int(recurrent["direct_contacts"]),
            "gdt762_direct_ol_contact_pages": int(recurrent["contact_pages"]),
            "gdt762_pattern_null_row_present": int(null is not None),
            "gdt775_fallback_target_tokens": int(slot_by_surface[surface]["fallback_target_tokens"]),
            "gdt775_slot_evidence_tier": slot_by_surface[surface]["slot_evidence_tier"],
            "existing_gdt745_card_id": g745_okalor["gdt745_card_id"] if surface == "okalor" else "NONE",
            "positive_evidence": spec["positive_evidence"],
            "counterevidence": spec["counterevidence"],
            "source_evidence": spec["source_evidence"],
            "replaceable": 1, "selected_by_exploratory_policy": 1,
            "literal_identity": spec["literal_identity"],
            "confirmed_lexeme": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0, "numeric_identity_confirmed": 0,
            "specific_substance_confirmed": 0, "default_is_translation": 0,
        })
    assert len(output) == 23
    assert sum(int(row["cache_occurrences"]) for row in output) == 40
    assert sum(int(row["reader_exact_occurrences"]) for row in output) == 32
    assert sum(int(row["reader_exact_occurrences"]) > 1 for row in output) == 7
    assert sum(int(row["reader_exact_occurrences"]) == 1 for row in output) == 16
    eses = next(row for row in output if row["surface"] == "eses")
    assert eses["raw_neighbor_surfaces"] == "oeees|oees|shes"
    assert eses["raw_consensus_axes"] == "PREPARATION"
    assert eses["later_supplement_surfaces"] == "eees"
    sheeoy = next(row for row in output if row["surface"] == "sheeoy")
    assert sheeoy["raw_neighbor_wholes"] == 6 and "sheeol" not in str(sheeoy["raw_neighbor_surfaces"])
    assert sheeoy["later_supplement_surfaces"] == "sheeol"
    chorcholsal = next(row for row in output if row["surface"] == "chorcholsal")
    assert chorcholsal["raw_analogy_tier"] == "A0_NO_CLEAN_NEIGHBOR"
    assert chorcholsal["raw_consensus_axes"] == "NONE"
    assert chorcholsal["target_local_axes"] == "DRY|PART|MATERIAL|PREPARATION"
    return output


def build_renderer(
    base: Sequence[Mapping[str, str]], spans: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], dict[str, str]]:
    by_target = {str(row["target_occurrence_id"]): row for row in spans}
    assert len(by_target) == 23
    output: list[dict[str, object]] = []
    for source in base:
        row: dict[str, object] = dict(source)
        row.update({
            "gdt781_branch": "INHERITED_GDT780",
            "gdt781_default_de": source["gdt780_default_de"],
            "gdt781_renderer_contextual": int(source["gdt780_renderer_contextual"]),
            "gdt781_span_id": source["gdt780_span_id"],
            "gdt781_exact_whole": source["gdt780_exact_whole"],
            "gdt781_confidence": source["gdt780_confidence"],
            "gdt781_analogy_tier": "INHERITED_GDT780",
            "gdt781_functional_axes": source["gdt780_functional_axis"],
            "gdt781_consumed_token_count": int(source["gdt780_consumed_token_count"]),
            "gdt781_consumed_token_ids": source["gdt780_consumed_token_ids"],
            "gdt781_fallback_replacement": 0, "gdt781_display_changed": 0,
            "gdt781_new_unique_consumption": 0,
            "gdt781_positive_evidence": "INHERITED_GDT780",
            "gdt781_counterevidence": "INHERITED_GDT780",
            "gdt781_dispatch_rule": "INHERITED_GDT780",
            "gdt781_scope_status": "INHERITED_GDT780",
            "gdt781_card_class": "INHERITED_GDT780",
            "gdt781_default_is_translation": 0, "gdt781_confirmed_lexeme": 0,
            "gdt781_confirmed_plaintext": 0, "gdt781_component_export_credit": 0,
        })
        span = by_target.get(source["target_occurrence_id"])
        if span is not None:
            row.update({
                "gdt781_branch": "GDT781_EXPLORATORY_EXACT_OL_PLUS_COMPLETE_WHOLE",
                "gdt781_default_de": span["new_gdt781_default_de"],
                "gdt781_renderer_contextual": 1, "gdt781_span_id": span["span_id"],
                "gdt781_exact_whole": span["right_surface"],
                "gdt781_confidence": span["confidence"],
                "gdt781_analogy_tier": span["analogy_tier"],
                "gdt781_functional_axes": span["working_functional_axes"],
                "gdt781_consumed_token_count": 1,
                "gdt781_consumed_token_ids": span["gdt781_consumed_token_id"],
                "gdt781_fallback_replacement": 1, "gdt781_display_changed": 1,
                "gdt781_new_unique_consumption": 1,
                "gdt781_positive_evidence": span["positive_evidence"],
                "gdt781_counterevidence": span["counterevidence"],
                "gdt781_dispatch_rule": SELECTION_RULE,
                "gdt781_scope_status": span["scope_status"],
                "gdt781_card_class": span["card_class"],
            })
        output.append(row)

    owners: dict[str, str] = {}
    for row in output:
        value = str(row["gdt781_consumed_token_ids"])
        count = int(row["gdt781_consumed_token_count"])
        token_ids = [] if value == "NONE" else value.split("|")
        assert len(token_ids) == count
        for token_id in token_ids:
            assert token_id not in owners, (token_id, row["target_occurrence_id"])
            owners[token_id] = str(row["target_occurrence_id"])
    assert len(output) == 376
    assert sum(int(row["gdt781_renderer_contextual"]) for row in output) == 270
    assert sum(1 - int(row["gdt781_renderer_contextual"]) for row in output) == 106
    assert sum(int(row["gdt781_fallback_replacement"]) for row in output) == 23
    assert sum(int(row["gdt781_display_changed"]) for row in output) == 23
    assert sum(int(row["gdt781_new_unique_consumption"]) for row in output) == 23
    assert len(owners) == 230
    for source, row in zip(base, output):
        assert all(str(row[field]) == source[field] for field in source)
        if source["target_occurrence_id"] not in by_target:
            assert row["gdt781_default_de"] == source["gdt780_default_de"]
            assert int(row["gdt781_renderer_contextual"]) == int(source["gdt780_renderer_contextual"])
            assert row["gdt781_consumed_token_ids"] == source["gdt780_consumed_token_ids"]
    return output, owners


def build_precedence(
    base: Sequence[Mapping[str, str]], renderer: Sequence[Mapping[str, object]],
    spans: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    old = one_by(base, "target_occurrence_id")
    new = {str(row["target_occurrence_id"]): row for row in renderer}
    output: list[dict[str, object]] = []
    for number, span in enumerate(spans, 1):
        target = str(span["target_occurrence_id"])
        before, after = old[target], new[target]
        output.append({
            "precedence_id": f"G781-H{number:03d}", "target_occurrence_id": target,
            "page": before["page"], "physical_folio": before["physical_folio"],
            "locus": before["locus"], "ol_ordinal": int(before["ordinal"]),
            "right_ordinal": int(before["right_ordinal"]),
            "right_surface": before["right_surface"],
            "right_reader_exact": int(before["right_reader_exact"]),
            "parent_gdt780_fallback": 1, "parent_gdt780_contextual": 0,
            "frozen_whole_23_member": 1,
            "precedence_disposition": "SELECTED_GDT781_EXPLORATORY_FALLBACK",
            "old_gdt780_branch": before["gdt780_branch"],
            "old_gdt780_default_de": before["gdt780_default_de"],
            "old_gdt780_consumed_token_count": int(before["gdt780_consumed_token_count"]),
            "old_gdt780_consumed_token_ids": before["gdt780_consumed_token_ids"],
            "new_gdt781_branch": after["gdt781_branch"],
            "new_gdt781_default_de": after["gdt781_default_de"],
            "new_gdt781_contextual": int(after["gdt781_renderer_contextual"]),
            "new_gdt781_consumed_token_count": int(after["gdt781_consumed_token_count"]),
            "new_gdt781_consumed_token_ids": after["gdt781_consumed_token_ids"],
            "fallback_replacement": 1,
            "same_row_inherited_consumption_takeover": 0,
            "cross_row_consumption_collision": 0, "selection_rule": SELECTION_RULE,
            "selection_uses_occurrence_id": 0, "selection_uses_page_or_locus": 0,
            "selection_uses_analogy_or_meaning": 0, "selection_uses_substring": 0,
            "component_export_credit": 0,
        })
    assert len(output) == 23
    return output


def render_line(
    locus: str, written: str,
    renderer_by_position: Mapping[tuple[str, int], Mapping[str, object]], generation: str,
) -> str:
    assert generation in {"gdt780", "gdt781"}
    rendered: list[str] = []
    consumed: set[int] = set()
    for ordinal, token in enumerate(written.split(), 1):
        if ordinal in consumed:
            continue
        dispatch = renderer_by_position.get((locus, ordinal))
        if dispatch is None:
            rendered.append(token)
        elif int(dispatch[f"{generation}_renderer_contextual"]):
            rendered.append(f"⟦{dispatch[f'{generation}_default_de']}⟧")
            count = int(dispatch[f"{generation}_consumed_token_count"])
            consumed.update(range(ordinal + 1, ordinal + count + 1))
        else:
            rendered.append(token)
    return " ".join(rendered)


def build_passages(
    base: Sequence[Mapping[str, str]], renderer: Sequence[Mapping[str, object]],
    spans: Sequence[Mapping[str, object]], frame_display: Mapping[str, str],
) -> list[dict[str, object]]:
    old_by_pos = {(row["locus"], int(row["ordinal"])): row for row in base}
    new_by_pos = {(str(row["locus"]), int(row["ordinal"])): row for row in renderer}
    output: list[dict[str, object]] = []
    for number, span in enumerate(sorted(spans, key=lambda row: str(row["locus"])), 1):
        locus, written = str(span["locus"]), str(span["written_line_eva"])
        before = render_line(locus, written, old_by_pos, "gdt780")
        after = render_line(locus, written, new_by_pos, "gdt781")
        assert before != after
        special = span["right_surface"] == "chorcholsal"
        if special:
            assert locus == "f88r.22"
            assert written == "ychey okaiin chol cheor ol chorcholsal"
        output.append({
            "passage_patch_id": f"G781-P{number:03d}", "span_id": span["span_id"],
            "target_occurrence_id": span["target_occurrence_id"],
            "page": span["page"], "physical_folio": span["physical_folio"],
            "locus": locus, "ol_ordinal": span["ol_ordinal"],
            "right_ordinal": span["right_ordinal"], "right_surface": span["right_surface"],
            "right_token_id": span["gdt781_consumed_token_id"],
            "selected_whole_default_de": span["selected_whole_default_de"],
            "written_line_eva": written, "inherited_gdt780_patch_de": before,
            "gdt781_practical_patch_de": after,
            "working_field_list_de": frame_display["working_display"] if special else "NA",
            "working_field_list_source_values_de": frame_display["source_values"] if special else "NA",
            "working_field_list_status": "WORKING_DISPLAY_NOT_PLAINTEXT" if special else "NA",
            "patch_legend": "double brackets are replaceable exact-span defaults; unbracketed EVA remains unresolved",
            "default_is_translation": 0, "confirmed_plaintext": 0,
            "component_export_credit": 0,
        })
    assert len(output) == 23
    assert sum(row["working_field_list_status"] == "WORKING_DISPLAY_NOT_PLAINTEXT" for row in output) == 1
    return output


def normalize_residual_reason(parent_reason: str) -> str:
    if parent_reason in {"V99_CARD_NONEXACT_FINAL44", "V99_CARD_NONEXACT_RAW_ONLY"}:
        return "V99_CARD_NONEXACT"
    return parent_reason


def build_residual(
    renderer: Sequence[Mapping[str, object]], parent_residual: Sequence[Mapping[str, str]],
    surfaces: set[str],
) -> list[dict[str, object]]:
    parent = one_by(parent_residual, "target_occurrence_id")
    remaining = [row for row in renderer if int(row["gdt781_renderer_contextual"]) == 0]
    output: list[dict[str, object]] = []
    for number, row in enumerate(remaining, 1):
        source = parent[str(row["target_occurrence_id"])]
        reason = normalize_residual_reason(source["residual_reason"])
        output.append({
            "residual_id": f"G781-R{number:03d}",
            "parent_gdt780_residual_id": source["residual_id"],
            "target_occurrence_id": row["target_occurrence_id"],
            "page": row["page"], "physical_folio": row["physical_folio"],
            "locus": row["locus"], "ol_ordinal": int(row["ordinal"]),
            "right_ordinal": int(row["right_ordinal"]), "right_surface": row["right_surface"],
            "right_reader_exact": int(row["right_reader_exact"]),
            "parent_residual_reason": source["residual_reason"],
            "residual_reason": reason, "gdt781_default_de": row["gdt781_default_de"],
            "frozen_whole_23_member": int(str(row["right_surface"]) in surfaces),
            "component_export_credit": 0,
        })
    assert len(output) == 106
    assert Counter(row["residual_reason"] for row in output) == Counter({
        "V99_CARD_NONEXACT": 49,
        "NO_V99R7_COMPLETE_WORD_CARD_READER_NONEXACT": 20,
        "LINE_FINAL_NO_RIGHT": 37,
    })
    assert not any(int(row["frozen_whole_23_member"]) for row in output)
    return output


def make_packet(
    spans: Sequence[Mapping[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    packet: list[dict[str, object]] = []
    crosswalk: list[dict[str, object]] = []
    for number, span in enumerate(spans, 1):
        edge_id = f"G781-E{number:03d}"
        packet.append({
            "edge_id": edge_id, "batch_id": "GDT781_REMAINING_23_EXPLORATORY_WHOLES",
            "page": span["page"], "physical_folio": span["physical_folio"],
            "diagram_unit_id": f"LINE:{span['locus']}",
            "pivot_visual_id": f"TOKEN:{span['locus']}:{span['ol_ordinal']}",
            "pivot_locus": f"{span['locus']}@{span['ol_ordinal']}",
            "target_visual_id": f"TOKEN:{span['locus']}:{span['right_ordinal']}",
            "target_locus": f"{span['locus']}@{span['right_ordinal']}",
            "relation_type": "NEXT_TOKEN", "direction_basis": "TRANSCRIPTION_ORDER_ONLY",
            "ownership_basis": "NONVISUAL_TEXT_ADJACENCY", "geometry_only_selection": "FALSE",
            "source_manifest_id": "GDT780", "page_crop_sha256": "NONE",
            "pivot_crop_sha256": "NONE", "target_crop_sha256": "NONE",
            "source_aware_localizer": "GDT781_RUNNER",
            "relation_reviewer": "GDT781_VALIDATOR", "relation_confidence": "EXPLORATORY",
            "ambiguity_state": "UNREVIEWED_TEXT_RELATION",
            "formal_access_state": "SEALED_NOT_ACCESSED", "fold_assignment": "NONE",
            "eligibility_status": "INELIGIBLE_EXPLORATORY_TEXT_RELATION",
        })
        crosswalk.append({
            "edge_id": edge_id, "batch_id": "GDT781_REMAINING_23_EXPLORATORY_WHOLES",
            "span_id": span["span_id"], "target_occurrence_id": span["target_occurrence_id"],
            "page": span["page"], "physical_folio": span["physical_folio"],
            "locus": span["locus"], "ol_ordinal": span["ol_ordinal"],
            "right_ordinal": span["right_ordinal"], "right_surface": span["right_surface"],
            "written_span_eva": span["written_span_eva"], "selection_rule": SELECTION_RULE,
            "score_eligible": 0, "component_export_credit": 0,
        })
    assert len(packet) == len(crosswalk) == 23
    return packet, crosswalk


def build_artifact_readme() -> str:
    return """# GDT781 artifacts

- `GDT781_23_COHORT_INTAKE.tsv`: GDT780's 25-form intake minus only `eees` and `sheeol`.
- `GDT781_RAW_COMPLETE_WHOLE_ANALOGY_RELATIONS.tsv`: all 135 selected complete-whole relations reconstructed from the frozen 769-whole GDT745 pool.
- `GDT781_23_RECURRENCE_EVIDENCE_CARDS.tsv`: fixed defaults, rivals, raw analogy, separate later supplements, recurrence and zero-credit fields.
- `GDT781_23_SELECTED_ATLAS.tsv`: every pure-selector match and its complete-token consumption.
- `GDT781_23_PRECEDENCE_AUDIT.tsv`: parent/new state for every replacement.
- `GDT781_376_RENDERER.tsv`: the complete GDT780 parent plus compact GDT781 state.
- `GDT781_23_PASSAGE_PATCHES.tsv`: changed line displays; the `f88r.22` field list is explicitly `WORKING_DISPLAY_NOT_PLAINTEXT`.
- `GDT781_RESIDUAL_106_FALLBACK_CENSUS.tsv`: every remaining fallback and its normalized reason.
- `GDT781_GDT388_RELATION_PACKET.tsv`: executable acquisition-only adjacency packet.
- `GDT781_RELATION_EDGE_CROSSWALK.tsv`: relation-edge to selected-span crosswalk.
- `RELATION_PACKET_INTAKE.json`: executable GDT388 intake result.
- `RESULT.json`: compact machine-readable result.

Raw GDT745-pool fields never include the later GDT780 `eees`/`sheeol` cards or target-local axes. Every German value is a replaceable complete-whole working display, never plaintext or a component export.
"""


def build_report(result: Mapping[str, object], passages: Sequence[Mapping[str, object]]) -> str:
    special = next(row for row in passages if row["right_surface"] == "chorcholsal")
    return f"""# GDT781 — die verbleibenden 23 vollständigen Rechtsformen nach `ol`

Status: `{result['status']}`.

## Ergebnis

Der eingefrorene reine Selektor trifft alle **23** verbleibenden reader-exakten,
kartenlosen GDT780-Rechtsformen: 23 vollständige Formen an 23 loci, 23
Seitenlabels und 20 physischen Folios. Die Abdeckung steigt **247→270**, die
Restmenge fällt **129→106** und der kollisionsfreie Verbrauch rechter Tokens
steigt **207→230**. Alle anderen **353** Rendererzeilen bleiben unverändert;
es gibt null Takeovers, Kollisionen, geschützte Umschreibungen oder
nicht-exakte Treffer.

## Was die Projektion tatsächlich trägt

Der alte GDT745-Pool wird aus GDT734 und den GDT739-Achsen vollständig neu
aufgebaut: 770 zulässige Lesungszeilen ergeben 769 vollständige Ganzwörter.
Der unveränderte Whole-Levenshtein-Algorithmus erzeugt 135 ausgewählte
Nachbarrelationen und exakt **12 A3, 10 A2 und 1 A0**. Die späteren Karten
`eees` und `sheeol` bleiben ein getrenntes Supplement: `eses` behält roh seine
drei alten Distanz-2-Nachbarn und `PREPARATION`; `sheeoy` behält roh sechs
Nachbarn und A3. `chorcholsal` bleibt roh A0/NONE.

Die 23 Karten summieren sich zu 40 Cache- und 32 reader-exakten Vorkommen.
Sieben Formen sind reader-exakt wiederkehrend, sechzehn sind exakte
Singletons; bei `chsky` bleiben drei Cacheformen ausdrücklich nur ein exaktes
Vorkommen. GDT775 liefert für jede Zieloberfläche nur `UNINFORMATIVE`, also
keinen Selektionsbeitrag aus der `ol`-Position.

## Konkretes Feldlistenbeispiel

`{special['locus']}`: `{special['written_line_eva']}`

Arbeitsanzeige: **{special['working_field_list_de']}**

Kennzeichnung: `{special['working_field_list_status']}`. Diese lesbare
Feldliste ist ein Zielrahmen-gestütztes Arbeitsdisplay, kein entschlüsselter
Klartext. Für `chorcholsal` existiert kein sauberer Ganzwortnachbar innerhalb
Editdistanz zwei; der Default gilt ausschließlich für die exakt enumerierte
Spanne `ol chorcholsal` an G769-T0488 und zerlegt die Oberfläche nicht.

## Rest und Grenze

Die 106 Fallbacks zerfallen exakt in 49 nicht-exakte Rechte mit V99R7-Karte,
20 nicht-exakte Rechte ohne Karte und 37 Zeilenenden ohne rechtes Token; es
bleibt kein reader-exaktes kartenloses Rechtsganzwort übrig. Kein Buchstabe,
Präfix, Suffix oder Teilstring erhält Bedeutung. Kein Lexem, Klartext, Wert,
Stoff oder historische Identität wird bestätigt. Es wurden keine neuen Seiten,
Bilder, OCR oder Transkriptionen geöffnet; `f84` und `f84r` blieben versiegelt.
Das GDT388-Paket bleibt `{result['relation_packet']['status']}`.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts-dir", type=Path, default=ART)
    parser.add_argument("--report-path", type=Path, default=REPORT)
    args = parser.parse_args()
    artifacts = args.artifacts_dir.resolve()
    report_path = args.report_path.resolve()

    lock_count = verify_locks()
    spec_rows = read_tsv(SPECS_PATH)
    specs = validate_specs(spec_rows)
    base = read_tsv(PARENT_RENDERER)
    parent_result = json.loads(PARENT_RESULT.read_text(encoding="utf-8"))
    parent_residual = read_tsv(PARENT_RESIDUAL)
    parent_intake = read_tsv(PARENT_INTAKE)
    assert len(base) == 376 and len(parent_residual) == 129
    assert sum(int(row["gdt780_renderer_contextual"]) for row in base) == 247
    assert sum(1 - int(row["gdt780_renderer_contextual"]) for row in base) == 129
    assert parent_result["renderer"]["gdt780_contextual"] == 247
    assert parent_result["renderer"]["gdt780_fallbacks"] == 129
    assert parent_result["consumption"]["total_unique_right_tokens"] == 207

    cohort = reconstruct_cohort(parent_intake, specs)
    pool, pool_diagnostics = build_clean_pool()
    relations, summaries = build_raw_analogy(set(specs), pool)
    frame_display = verify_chorcholsal_frame(specs)
    for surface, spec in specs.items():
        assert summaries[surface]["raw_analogy_tier"] == spec["analogy_tier"], surface
        if surface != "chorcholsal":
            assert summaries[surface]["raw_consensus_axes"] == spec["functional_axes"], surface
    spans = build_spans(base, specs, summaries)
    evidence = build_evidence(specs, summaries, spans)
    renderer, owners = build_renderer(base, spans)
    precedence = build_precedence(base, renderer, spans)
    passages = build_passages(base, renderer, spans, frame_display)
    residual = build_residual(renderer, parent_residual, set(specs))
    packet, crosswalk = make_packet(spans)

    outputs = [
        ("GDT781_23_COHORT_INTAKE.tsv", cohort),
        ("GDT781_RAW_COMPLETE_WHOLE_ANALOGY_RELATIONS.tsv", relations),
        ("GDT781_23_RECURRENCE_EVIDENCE_CARDS.tsv", evidence),
        ("GDT781_23_SELECTED_ATLAS.tsv", spans),
        ("GDT781_23_PRECEDENCE_AUDIT.tsv", precedence),
        ("GDT781_376_RENDERER.tsv", renderer),
        ("GDT781_23_PASSAGE_PATCHES.tsv", passages),
        ("GDT781_RESIDUAL_106_FALLBACK_CENSUS.tsv", residual),
        ("GDT781_GDT388_RELATION_PACKET.tsv", packet),
        ("GDT781_RELATION_EDGE_CROSSWALK.tsv", crosswalk),
    ]
    for name, rows in outputs:
        write_tsv(artifacts / name, rows, list(rows[0]))

    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from tools.relation_edge_intake import validate_relation_edge_packet

    packet_intake = validate_relation_edge_packet(artifacts / "GDT781_GDT388_RELATION_PACKET.tsv")
    assert packet_intake == {
        "status": "VALID_ACQUISITION_NOT_SCORE_READY", "packet_rows": 23,
        "eligible_edges": 0, "eligible_folios": 0, "discovery_edges": 0,
        "holdout_edges": 0, "mobile_edges": 0,
        "capacity_gate_50_edges_5_folios": False, "holdout_gate": False,
        "mobile_null_gate": False, "score_ready": False, "errors": [],
    }
    write_json(artifacts / "RELATION_PACKET_INTAKE.json", packet_intake)

    result: dict[str, object] = {
        "experiment_id": "GDT781", "status": STATUS,
        "source_locks": lock_count, "source_lock_sha256": SOURCE_LOCK_SHA256,
        "whole_23_specs_sha256": SPEC_SHA256,
        "inherited_guard": parent_result["inherited_guard"],
        "cohort": {
            "parent_cardless_intake": 25, "removed_parent_selected_forms": 2,
            "renderer_rows": 376, "selected_spans": 23, "selected_forms": 23,
            "loci": 23, "page_labels": 23, "physical_folios": 20,
        },
        "precedence": {
            "full_parent_deck_matches": 23, "reader_exact_parent_deck_matches": 23,
            "nonexact_parent_deck_matches": 0, "parent_fallback_deck_matches": 23,
            "protected_contextual_deck_matches": 0, "selected_fallback_matches": 23,
            "nonselected_parent_rows_unchanged": 353,
        },
        "changes": {
            "fallback_replacements": 23, "actual_display_changes": 23,
            "contextual_sharpenings": 0, "contextual_confirmations": 0,
            "passage_patches": 23,
        },
        "renderer": {
            "gdt780_contextual": 247, "gdt781_contextual": 270,
            "gdt780_fallbacks": 129, "gdt781_fallbacks": 106,
        },
        "consumption": {
            "gdt780_unique_right_tokens": 207, "gdt781_selected_right_tokens": 23,
            "same_row_inherited_takeovers": 0, "new_unique_right_tokens": 23,
            "total_unique_right_tokens": len(owners), "cross_row_collisions": 0,
        },
        "whole_analogy": {
            **pool_diagnostics, "raw_relation_rows": len(relations),
            "a3_cards": 12, "a2_cards": 10, "a0_cards": 1,
            "a0_surface": "chorcholsal",
            "a0_raw_consensus_axes": "NONE",
            "a0_scope": "EXACT_ENUMERATED_OL_CHORCHOLSAL_SPAN_ONLY",
            "later_supplement_relations": 5,
            "later_supplements_in_raw_pool": 0,
            "target_local_axes_in_raw_consensus": 0,
            "eses_raw_neighbor_wholes": 3,
            "eses_raw_consensus_axes": "PREPARATION",
            "sheeoy_raw_neighbor_wholes": 6,
            "sheeoy_raw_analogy_tier": "A3_DISTANCE1_MULTIWHOLE_CONSENSUS",
        },
        "recurrence": {
            "cache_occurrences": 40, "reader_exact_occurrences": 32,
            "reader_exact_recurrent_forms": 7, "reader_exact_singleton_forms": 16,
            "chsky_cache_occurrences": 3, "chsky_reader_exact_occurrences": 1,
        },
        "serial_evidence": {
            "cheedaiin_external_axes": "END_STAGE",
            "cheedaiin_external_bridge_tier": "B0_NO_WHOLE_FORM_BRIDGE",
            "otlaiin_target_local_axes": "END_STAGE",
            "otlaiin_target_local_bridge_tier": "B0_NO_WHOLE_FORM_BRIDGE",
        },
        "chorcholsal_field_list": {
            "locus": "f88r.22", "target_occurrence_id": "G769-T0488",
            "status": "WORKING_DISPLAY_NOT_PLAINTEXT",
        },
        "residual_fallback_rows": 106,
        "residual_partition": {
            "no_card_reader_exact": 0, "v99_card_nonexact": 49,
            "no_card_reader_nonexact": 20, "line_final_no_right": 37,
        },
        "relation_packet": packet_intake,
        "confirmed_lexemes": 0, "confirmed_plaintext_clauses": 0,
        "numeric_identities": 0, "specific_substances": 0, "component_exports": 0,
        "new_pages": 0, "new_images": 0, "new_ocr": 0,
        "new_transcriptions": 0, "sealed_pages_accessed": 0,
        "claim_ceiling": (
            "Twenty-three replaceable exact ol plus complete-whole working displays only; "
            "no EVA component, lexeme, number, unit, substance, language or plaintext claim."
        ),
    }
    write_json(artifacts / "RESULT.json", result)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(result, passages), encoding="utf-8")
    (artifacts / "README.md").write_text(build_artifact_readme(), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
