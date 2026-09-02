#!/usr/bin/env python3
"""Build GDT738's two-deck occurrence-gated body adjudication.

FORMAL705 carries reader-exact surface/register evidence. SEM570 is a
permissive discovery deck. Only W23-AXIS195 may issue complete-form renderer
licences. Nothing here exports an H1--H4 or body lexeme.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

sys.dont_write_bytecode = True


def find_repo_root(start: Path) -> Path:
    for candidate in (start, *start.parents):
        if (candidate / "AGENTS.md").is_file() and (candidate / ".git").exists():
            return candidate
    raise RuntimeError("VManus repository root not found")


ROOT = find_repo_root(Path(__file__).resolve())
BASE_REL = Path("experiments/yolo/gdt738_held_body_occurrence_semantic_adjudication")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"
G734 = Path("experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch")
COMPACT_REL = G734 / "artifacts/V99R7_32339_COMPACT_CELL_REGISTER.tsv"
G735 = Path("experiments/yolo/gdt735_historical_semantic_bridge_atlas")
HISTORICAL_REGISTRY_REL = G735 / "src/HISTORICAL_SOURCE_REGISTRY.tsv"
G736 = Path("experiments/yolo/gdt736_opaque_head_record_role_bridge")
TRAIN_OCC_REL = G736 / "artifacts/OPAQUE_1166_OCCURRENCE_CONTEXTS.tsv"
TRAIN_BODY_REL = G736 / "artifacts/BODY_ROLE_DICTIONARY_V2.tsv"
G737 = Path("experiments/yolo/gdt737_held_body_record_role_transfer")
G737_RUN_REL = G737 / "src/run.py"
HELD_OCC_REL = G737 / "artifacts/HELD_811_OCCURRENCE_CONTEXTS.tsv"
HELD_BODY_REL = G737 / "artifacts/HELD_BODY_WORKING_CANDIDATES.tsv"
HELD_FORM_REL = G737 / "artifacts/HELD_273_FORM_ROLE_BRIDGE.tsv"
QUARANTINE_REL = G737 / "artifacts/V99R7_HELD_WHOLE_QUARANTINE.tsv"

module_spec = importlib.util.spec_from_file_location("gdt737_builder", ROOT / G737_RUN_REL)
if module_spec is None or module_spec.loader is None:
    raise RuntimeError("cannot load GDT737 guarded helpers")
g737 = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(g737)

HEADS = ("H1", "H2", "H3", "H4")
RETIRED_PATIENT_WORDS = ("pulver", "samen", "saat", "wurzel", "holz")
SUPPORTED = {"SUPPORTED_CROSS_HEAD", "SUPPORTED_FAMILY_ONLY"}
DISCOVERY_DECK = "SEM570"
LICENSE_DECK = "W23_AXIS195"

# Analogy sets only: these are not word segmentations or lexeme families.
FAMILY_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("VALUE_A", ("ain", "aiin", "aiiin")),
    ("HEAT_VALUE_KA", ("kain", "kaiin")),
    ("HEAT_STATE_KY", ("ky", "key", "keey")),
    ("DRY_RESULT_CHDY", ("chdy", "chedy", "cheedy")),
    ("MOIST_RESULT_SHDY", ("shdy", "shedy", "sheedy")),
    ("PREP_O", ("o", "oiin", "oaiin", "odaiin")),
    ("PART_AR", ("ar", "kar", "okar", "char", "chear")),
    ("DRY_PART_OR", ("or", "chor", "cheor")),
    ("MATERIAL_OL", ("ol", "cheol", "chal", "olchey")),
    ("PREP_RESULT_ODY", ("ody", "chody", "cheody", "sheody")),
)
FAMILY_BY_BODY = {body: name for name, members in FAMILY_GROUPS for body in members}
MEMBERS_BY_BODY = {body: members for _, members in FAMILY_GROUPS for body in members}

EXPECTED_DISCOVERY_BODIES = {
    "ain", "cheedy", "cheol", "cheor", "kaiin", "kain", "kar", "keey", "key", "ky", "sheedy",
}
EXPECTED_LICENSE_BODIES = {"ain", "cheedy", "cheol", "kaiin", "kain", "kar", "sheedy"}
EXPECTED_DISCOVERY_FORMS = {
    "lain", "lcheedy", "lcheol", "lcheor", "lkaiin", "lkain", "lkar", "lkeey", "lkey", "lky",
    "lsheedy", "pcheol", "pcheor", "rain", "rsheedy", "sain", "skaiin",
}
EXPECTED_LICENSE_FORMS = {
    "lain", "lcheedy", "lcheol", "lkaiin", "lkain", "lkar", "lsheedy", "pcheol", "rain",
    "rsheedy", "sain", "skaiin",
}
EXPECTED_DISCOVERY_ONLY_FORMS = {"lcheor", "lkeey", "lkey", "lky", "pcheor"}
OUTPUT_NAMES = (
    "ADJACENT_1266_SLOT_AUDIT.tsv", "NONHEAD_NEIGHBOR_AXIS_ANCHORS.tsv",
    "BODY_120_SEMANTIC_BRIDGE.tsv", "BODY_TRANSFER_METRICS.tsv", "FORM_273_ADJUDICATION.tsv",
    "AXIS_NEIGHBOR_ENRICHMENT.tsv", "MATRIX_WORKING_MODEL.tsv", "REPAIRED_SCOPED_WHOLE_CARDS.tsv",
    "ADJUDICATED_17_WHOLE_CARDS.tsv", "OCCURRENCE_RENDERER_PATCH.tsv", "MANUAL_HOLD_AUDIT.tsv",
    "HISTORICAL_MICROENTRY_MODELS.tsv",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=names, delimiter="\t", lineterminator="\n", extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fmt(value: float) -> str:
    return f"{value:.6f}"


def cosine(left: Counter[object], right: Counter[object]) -> float:
    keys = set(left) | set(right)
    numerator = sum(left[key] * right[key] for key in keys)
    denominator = math.sqrt(
        sum(value * value for value in left.values()) * sum(value * value for value in right.values())
    )
    return numerator / denominator if denominator else 0.0


def odds_ratio_haldene(a: int, b: int, c: int, d: int) -> float:
    return ((a + .5) * (d + .5)) / ((b + .5) * (c + .5))


def retired_hits(text: str) -> tuple[str, ...]:
    lowered = text.lower()
    return tuple(word for word in RETIRED_PATIENT_WORDS if word in lowered)


def strict_initial_head(surface: str) -> bool:
    return len(surface) > 1 and surface[0] in "psrl" and not surface.startswith("sh")


def position_exception(head: str, line_position: str) -> bool:
    return (head in ("H1", "H2") and line_position != "FIRST") or (
        head in ("H3", "H4") and line_position == "FIRST"
    )


def load_axis_rules() -> tuple[list[tuple[str, re.Pattern[str]]], list[dict[str, str]]]:
    rows = read_tsv(SRC / "SEMANTIC_AXIS_SPECS.tsv")
    expected = ["HEAT", "COLD", "DRY", "MOIST", "VALUE", "PART", "MATERIAL", "PREPARATION", "CLOSE", "PROCESS"]
    if [row["axis_id"] for row in rows] != expected:
        raise AssertionError("semantic-axis order or membership changed")
    compiled: list[tuple[str, re.Pattern[str]]] = []
    for row in rows:
        # Normalize the TSV's one escaped layer: \\bteil becomes regex \bteil.
        compiled.append((row["axis_id"], re.compile(row["keyword_regex"].replace("\\\\", "\\"), re.IGNORECASE)))
    rules = read_tsv(SRC / "FAMILY_AXIS_RULES.tsv")
    if len(rules) != 9 or any(row["expected_axis"] == "RESULT" for row in rules):
        raise AssertionError("family-axis rules changed or revived RESULT instead of CLOSE")
    return compiled, rules


def text_axes(text: str, axes: list[tuple[str, re.Pattern[str]]]) -> tuple[str, ...]:
    selected = tuple(axis for axis, pattern in axes if pattern.search(text))
    return selected or ("OTHER",)


def expected_axes(family: str, rules: list[dict[str, str]]) -> tuple[str, ...]:
    selected = [row["expected_axis"] for row in rules if re.search(row["family_regex"], family)]
    return tuple(dict.fromkeys(selected)) or ("OTHER",)


def token_context() -> tuple[dict[str, list[dict[str, str]]], dict[tuple[str, int], int], dict[str, object]]:
    pages = g737.allowed_pages()
    if len(pages) != 179 or any(page.startswith("f84") for page in pages):
        raise AssertionError("inherited page boundary changed")
    tokens, token_guard = g737.g631.guarded_query(
        g737.TOKENS_REL, pages, "page,locus,token_index,eva,section,language,hand"
    )
    cross, cross_guard = g737.g631.guarded_query(
        g737.CROSS_REL, pages, "page,locus,all_three_present,all_present_exact,zl3b_clean,it2a_clean,rf1b_clean"
    )
    by_line, _ = g737.g631.line_maps(tokens)
    exact, _ = g737.g634.stable_maps(tokens, {row["locus"]: row for row in cross})
    return by_line, exact, {"allowed_pages": len(pages), "tokens": token_guard, "cross": cross_guard}


def compact_cells() -> dict[tuple[str, int], dict[str, str]]:
    rows = read_tsv(ROOT / COMPACT_REL)
    if len(rows) != 32339 or len({row["page"] for row in rows}) != 179:
        raise AssertionError("GDT734 compact cache shape changed")
    if any(row["page"].startswith("f84") for row in rows):
        raise AssertionError("sealed page present in compact cache")
    cells = {(row["locus"], int(row["token_ordinal"])): row for row in rows}
    if len(cells) != len(rows):
        raise AssertionError("compact cells are not unique by locus and ordinal")
    return cells


def adjacent_slots(
    occurrences: list[dict[str, str]], by_line: dict[str, list[dict[str, str]]],
    exact: dict[tuple[str, int], int], cells: dict[tuple[str, int], dict[str, str]],
    axes: list[tuple[str, re.Pattern[str]]], panel: str,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for occurrence in occurrences:
        line = by_line[occurrence["locus"]]
        target_ordinal = int(occurrence["token_ordinal"])
        if line[target_ordinal - 1]["eva"] != occurrence["form"]:
            raise AssertionError(f"target/raw surface mismatch: {occurrence['occurrence_id']}")
        target_key = (occurrence["locus"], int(occurrence["token_index"]))
        if int(occurrence["all_readers_exact"]) != exact[target_key]:
            raise AssertionError(f"target exactness drift: {occurrence['occurrence_id']}")
        for side, neighbor_index in (("L", target_ordinal - 2), ("R", target_ordinal)):
            if not 0 <= neighbor_index < len(line):
                continue
            neighbor = line[neighbor_index]
            neighbor_ordinal = neighbor_index + 1
            cell = cells[(occurrence["locus"], neighbor_ordinal)]
            if cell["surface"] != neighbor["eva"]:
                raise AssertionError(f"compact/raw neighbour mismatch: {occurrence['occurrence_id']} {side}")
            target_exact = int(occurrence["all_readers_exact"])
            neighbor_exact = exact[(occurrence["locus"], int(neighbor["token_index"]))]
            both_exact = target_exact * neighbor_exact
            initial_head = int(strict_initial_head(neighbor["eva"]))
            formal = int(both_exact and not initial_head)
            semantic_text = cell["v99r7_semantic_value_de"]
            hits = retired_hits(semantic_text)
            sem570 = int(formal and cell["unknown_v99r7"] == "0" and not hits)
            selected_axes = text_axes(semantic_text, axes) if sem570 else ()
            level = cell["gdt734_confidence_level"]
            w23_pre = int(sem570 and level.startswith(("W2", "W3")))
            w23 = int(
                w23_pre
                and selected_axes != ("OTHER",)
                and cell["gdt734_composition_semantic_credit"] == "0"
            )
            rows.append({
                "slot_id": f"G738-{panel}S{len(rows) + 1:05d}", "target_panel": panel,
                "source_occurrence_id": occurrence["occurrence_id"], "body": occurrence["body"],
                "form": occurrence["form"], "opaque_head_id": occurrence["opaque_head_id"],
                "head_occupancy": occurrence.get("head_occupancy", "4"), "page": occurrence["page"],
                "locus": occurrence["locus"], "section": occurrence["section"],
                "language": occurrence["language"], "line_position": occurrence["line_position"],
                "position_exception": int(position_exception(occurrence["opaque_head_id"], occurrence["line_position"])),
                "side": side, "neighbor_token_ordinal": neighbor_ordinal, "neighbor_surface": neighbor["eva"],
                "target_reader_exact": target_exact, "neighbor_reader_exact": neighbor_exact,
                "both_reader_exact": both_exact, "strict_initial_head_neighbor": initial_head,
                "formal705_slot": formal, "sem570_slot": sem570,
                "w23_axis197_precomposition_slot": w23_pre, "w23_axis195_slot": w23,
                "neighbor_cell_id": cell["cell_id"],
                "neighbor_semantic_value_de": semantic_text if sem570 else "NONE",
                "neighbor_confidence_level": level if sem570 else "NONE",
                "neighbor_semantic_scope": cell["gdt734_semantic_scope"] if sem570 else "NONE",
                "neighbor_composition_semantic_credit": cell["gdt734_composition_semantic_credit"] if sem570 else 0,
                "retired_patient_words": "|".join(hits) or "NONE",
                "axis_tags": "|".join(selected_axes) if sem570 else "NONE",
                "semantic_fingerprint": "|".join(selected_axes) if sem570 else "NONE",
                "literal_head_lexeme_credit": 0, "literal_body_lexeme_credit": 0, "component_export_credit": 0,
            })
    return rows


def semantic_flag(deck: str) -> str:
    if deck == DISCOVERY_DECK:
        return "sem570_slot"
    if deck == LICENSE_DECK:
        return "w23_axis195_slot"
    raise ValueError(deck)


def profile(slots: list[dict[str, object]], deck: str) -> dict[str, Counter[object]]:
    formal = [row for row in slots if int(row["formal705_slot"])]
    semantic = [row for row in formal if int(row[semantic_flag(deck)])]
    labels: Counter[object] = Counter()
    for row in semantic:
        labels.update(str(row["axis_tags"]).split("|"))
    return {
        "surface": Counter(str(row["neighbor_surface"]) for row in formal),
        "axis": labels,
        "register": Counter((str(row["section"]), str(row["language"])) for row in formal),
    }


def repeated_values(
    rows: list[dict[str, object]], value_field: str, registered: bool,
) -> tuple[list[str], set[str]]:
    grouped: dict[tuple[str, ...], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        key = (str(row[value_field]),)
        if registered:
            key += (str(row["side"]), str(row["section"]), str(row["language"]))
        grouped[key].append(row)
    labels: list[str] = []
    evidence_heads: set[str] = set()
    for key, selected in grouped.items():
        heads = {str(row["opaque_head_id"]) for row in selected}
        if key[0] != "NONE" and len(heads) >= 2:
            labels.append("@".join(key))
            evidence_heads.update(heads)
    return sorted(labels), evidence_heads


def direct_metrics(
    slots: list[dict[str, object]], occurrences: list[dict[str, str]], deck: str,
) -> dict[str, object]:
    formal = [row for row in slots if int(row["formal705_slot"])]
    semantic = [row for row in formal if int(row[semantic_flag(deck)])]
    surface_repeat, surface_heads = repeated_values(formal, "neighbor_surface", False)
    registered_surface, _ = repeated_values(formal, "neighbor_surface", True)
    fingerprint_repeat, fingerprint_heads = repeated_values(semantic, "semantic_fingerprint", False)
    registered_fingerprint, _ = repeated_values(semantic, "semantic_fingerprint", True)
    by_register: dict[tuple[str, str], set[str]] = defaultdict(set)
    for row in formal:
        by_register[(str(row["section"]), str(row["language"]))].add(str(row["opaque_head_id"]))
    register_overlap = sorted(
        f"{section}|{language}" for (section, language), heads in by_register.items() if len(heads) >= 2
    )
    exact_by_head = Counter(row["opaque_head_id"] for row in occurrences if row["all_readers_exact"] == "1")
    evidence_heads = surface_heads | fingerprint_heads
    balanced = bool(evidence_heads) and all(exact_by_head[head] >= 2 for head in evidence_heads)
    score = (
        2 * int(bool(surface_repeat)) + int(bool(registered_surface))
        + int(bool(fingerprint_repeat)) + int(bool(registered_fingerprint)) + int(bool(register_overlap))
    )
    return {
        "direct_score": score,
        "shared_surface_count": len(surface_repeat), "shared_surfaces": "|".join(surface_repeat) or "NONE",
        "registered_surface_count": len(registered_surface),
        "registered_surfaces": "|".join(registered_surface) or "NONE",
        "shared_fingerprint_count": len(fingerprint_repeat),
        "shared_fingerprints": " || ".join(fingerprint_repeat) or "NONE",
        "registered_fingerprint_count": len(registered_fingerprint),
        "registered_fingerprints": " || ".join(registered_fingerprint) or "NONE",
        "register_overlap_count": len(register_overlap), "register_overlaps": "|".join(register_overlap) or "NONE",
        "recurrence_evidence_heads": "|".join(sorted(evidence_heads)) or "NONE",
        "recurrence_heads_balanced_ge2_exact": int(balanced),
        "exact_occurrences_by_head": "|".join(f"{head}:{exact_by_head[head]}" for head in HEADS),
    }


def best_family(
    body: str, slots_by_body: dict[str, list[dict[str, object]]], deck: str,
) -> dict[str, object]:
    if body not in MEMBERS_BY_BODY:
        return {
            "comparator": "NONE", "surface_cosine": 0.0, "axis_cosine": 0.0, "register_cosine": 0.0,
            "family_points": 0, "strong_family": 0,
        }
    left = profile(slots_by_body[body], deck)
    best: tuple[tuple[float, ...], str, float, float, float] | None = None
    for comparator in MEMBERS_BY_BODY[body]:
        if comparator == body:
            continue
        comparator_slots = slots_by_body[comparator]
        comparator_formal = sum(int(row["formal705_slot"]) for row in comparator_slots)
        comparator_semantic = sum(int(row[semantic_flag(deck)]) for row in comparator_slots)
        if comparator_formal < 5 or comparator_semantic < 3:
            continue
        right = profile(comparator_slots, deck)
        surface = cosine(left["surface"], right["surface"])
        axis = cosine(left["axis"], right["axis"])
        register = cosine(left["register"], right["register"])
        passed = int(surface >= .15) + int(axis >= .80) + int(register >= .70)
        quality = (float(passed), surface + axis + register, surface, axis, register)
        if best is None or quality > best[0]:
            best = (quality, comparator, surface, axis, register)
    if best is None:
        return {
            "comparator": "NONE", "surface_cosine": 0.0, "axis_cosine": 0.0, "register_cosine": 0.0,
            "family_points": 0, "strong_family": 0,
        }
    _, comparator, surface, axis, register = best
    points = 2 * int(surface >= .15) + int(axis >= .80) + int(register >= .70)
    return {
        "comparator": comparator, "surface_cosine": surface, "axis_cosine": axis,
        "register_cosine": register, "family_points": points,
        "strong_family": int(surface >= .15 and axis >= .80 and register >= .70),
    }


def decide_body(
    body: str, exact_count: int, formal_count: int, direct: dict[str, object], family: dict[str, object],
    capacity: int, penalty: int,
) -> tuple[int, str]:
    score = capacity + int(direct["direct_score"]) + int(family["family_points"]) + penalty
    if (
        int(direct["direct_score"]) >= 4 and exact_count >= 4
        and int(direct["recurrence_heads_balanced_ge2_exact"])
    ):
        return score, "SUPPORTED_CROSS_HEAD"
    if int(family["strong_family"]) and exact_count >= 4 and formal_count >= 4:
        return score, "SUPPORTED_FAMILY_ONLY"
    if (
        body in FAMILY_BY_BODY and family["comparator"] != "NONE" and exact_count >= 5 and formal_count >= 8
        and int(family["family_points"]) <= 1 and int(direct["direct_score"]) <= 1
    ):
        return score, "CONTRADICTED_FAMILY_TRANSFER"
    return score, "UNDECIDABLE"


def body_metrics(
    held_candidates: list[dict[str, str]], held_occ: list[dict[str, str]], held_slots: list[dict[str, object]],
    train_occ: list[dict[str, str]], train_slots: list[dict[str, object]],
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]]]:
    slots_by_body: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in held_slots + train_slots:
        slots_by_body[str(row["body"])].append(row)
    held_occ_by_body: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in held_occ:
        held_occ_by_body[row["body"]].append(row)
    rows: list[dict[str, object]] = []
    for source in sorted(held_candidates, key=lambda row: row["body"]):
        body = source["body"]
        occurrences = held_occ_by_body[body]
        slots = slots_by_body[body]
        exact_count = sum(row["all_readers_exact"] == "1" for row in occurrences)
        formal_count = sum(int(row["formal705_slot"]) for row in slots)
        sem_count = sum(int(row["sem570_slot"]) for row in slots)
        w23_count = sum(int(row["w23_axis195_slot"]) for row in slots)
        capacity = int(exact_count >= 4) + int(formal_count >= 4)
        formal_heads = {str(row["opaque_head_id"]) for row in slots if int(row["formal705_slot"])}
        exceptions = sum(position_exception(row["opaque_head_id"], row["line_position"]) for row in occurrences)
        penalty_single = -2 if formal_count >= 8 and len(formal_heads) == 1 else 0
        penalty_position = -1 if occurrences and exceptions / len(occurrences) >= 1 / 3 else 0
        penalty_prior = -1 if source["confidence"] in ("LOW", "UNKNOWN") else 0
        penalty = penalty_single + penalty_position + penalty_prior
        discovery_direct = direct_metrics(slots, occurrences, DISCOVERY_DECK)
        strict_direct = direct_metrics(slots, occurrences, LICENSE_DECK)
        discovery_family = best_family(body, slots_by_body, DISCOVERY_DECK)
        strict_family = best_family(body, slots_by_body, LICENSE_DECK)
        discovery_score, discovery_decision = decide_body(
            body, exact_count, formal_count, discovery_direct, discovery_family, capacity, penalty
        )
        strict_score, strict_decision = decide_body(
            body, exact_count, formal_count, strict_direct, strict_family, capacity, penalty
        )
        row: dict[str, object] = {
            "body": body, "head_occupancy": source["head_occupancy"], "opaque_heads": source["opaque_heads"],
            "candidate_family": source["family"], "analogy_family": FAMILY_BY_BODY.get(body, "NONE"),
            "prior_candidate_de": source["concrete_body_role_de"], "prior_confidence": source["confidence"],
            "headed_occurrences": len(occurrences), "reader_exact_occurrences": exact_count,
            "formal705_slots": formal_count, "sem570_slots": sem_count, "w23_axis195_slots": w23_count,
            "formal_head_count": len(formal_heads), "formal_heads": "|".join(sorted(formal_heads)) or "NONE",
            "position_exceptions": exceptions, "position_exception_rate": fmt(exceptions / len(occurrences)),
            "capacity_points": capacity, "penalty_single_formal_head": penalty_single,
            "penalty_position": penalty_position, "penalty_prior": penalty_prior, "total_penalty": penalty,
        }
        for prefix, direct, family, score, decision in (
            ("discovery", discovery_direct, discovery_family, discovery_score, discovery_decision),
            ("w23", strict_direct, strict_family, strict_score, strict_decision),
        ):
            for key, value in direct.items():
                row[f"{prefix}_{key}"] = value
            row[f"{prefix}_family_comparator"] = family["comparator"]
            row[f"{prefix}_family_surface_cosine"] = fmt(float(family["surface_cosine"]))
            row[f"{prefix}_family_axis_cosine"] = fmt(float(family["axis_cosine"]))
            row[f"{prefix}_family_register_cosine"] = fmt(float(family["register_cosine"]))
            row[f"{prefix}_family_points"] = family["family_points"]
            row[f"{prefix}_strong_family"] = family["strong_family"]
            row[f"{prefix}_working_score_not_probability"] = score
            row[f"{prefix}_decision"] = decision
        row.update({"body_renderer_license": 0, "literal_head_lexeme_credit": 0,
                    "literal_body_lexeme_credit": 0, "component_export_credit": 0})
        rows.append(row)
    if len(rows) != 120:
        raise AssertionError("body metrics must cover 120 bodies")
    mapping = {str(row["body"]): row for row in rows}
    discovery_counts = Counter(str(row["discovery_decision"]) for row in rows)
    strict_counts = Counter(str(row["w23_decision"]) for row in rows)
    if discovery_counts != Counter({"UNDECIDABLE": 107, "SUPPORTED_FAMILY_ONLY": 9,
                                    "SUPPORTED_CROSS_HEAD": 2, "CONTRADICTED_FAMILY_TRANSFER": 2}):
        raise AssertionError(f"SEM570 body decisions changed: {discovery_counts}")
    if strict_counts != Counter({"UNDECIDABLE": 108, "SUPPORTED_FAMILY_ONLY": 5,
                                 "CONTRADICTED_FAMILY_TRANSFER": 5, "SUPPORTED_CROSS_HEAD": 2}):
        raise AssertionError(f"W23 body decisions changed: {strict_counts}")
    if {row["body"] for row in rows if row["discovery_decision"] in SUPPORTED} != EXPECTED_DISCOVERY_BODIES:
        raise AssertionError("SEM570 supported body set changed")
    if {row["body"] for row in rows if row["w23_decision"] in SUPPORTED} != EXPECTED_LICENSE_BODIES:
        raise AssertionError("W23 supported body set changed")
    if {row["body"] for row in rows if row["discovery_decision"] == "SUPPORTED_CROSS_HEAD"} != {"ain", "sheedy"}:
        raise AssertionError("direct cross-head core changed")
    if {row["body"] for row in rows if row["discovery_decision"] == "CONTRADICTED_FAMILY_TRANSFER"} != {"char", "cheody"}:
        raise AssertionError("SEM570 contradicted family set changed")
    return rows, mapping


def form_adjudication(
    forms: list[dict[str, str]], occurrences: list[dict[str, str]], slots: list[dict[str, object]],
    bodies: dict[str, dict[str, object]], manual_specs: dict[str, dict[str, str]],
) -> tuple[list[dict[str, object]], set[str], set[str]]:
    occ_by_form: dict[str, list[dict[str, str]]] = defaultdict(list)
    slots_by_form: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in occurrences:
        occ_by_form[row["form"]].append(row)
    for row in slots:
        slots_by_form[str(row["form"])].append(row)
    rows: list[dict[str, object]] = []
    for source in forms:
        form, body = source["form"], source["body"]
        occurrence_deck, slot_deck = occ_by_form[form], slots_by_form[form]
        exact_count = sum(row["all_readers_exact"] == "1" for row in occurrence_deck)
        formal_count = sum(int(row["formal705_slot"]) for row in slot_deck)
        sem_count = sum(int(row["sem570_slot"]) for row in slot_deck)
        w23_count = sum(int(row["w23_axis195_slot"]) for row in slot_deck)
        exceptions = sum(position_exception(row["opaque_head_id"], row["line_position"]) for row in occurrence_deck)
        exception_rate = exceptions / len(occurrence_deck)
        body_metric = bodies[body]
        discovery_gate = body_metric["discovery_decision"] in SUPPORTED and exact_count >= 2 and formal_count >= 2
        strict_gate = body_metric["w23_decision"] in SUPPORTED and exact_count >= 2 and formal_count >= 2
        discovery_decision = (
            "SUPPORTED_EXACT_WHOLE_EXCEPTION" if discovery_gate and exception_rate >= .5
            else "SUPPORTED_SCOPED_WHOLE" if discovery_gate else "UNDECIDABLE"
        )
        strict_decision = (
            "SUPPORTED_EXACT_WHOLE_EXCEPTION" if strict_gate and exception_rate >= .5
            else "SUPPORTED_SCOPED_WHOLE" if strict_gate else "UNDECIDABLE"
        )
        spec = manual_specs.get(form)
        positions = Counter(row["line_position"] for row in occurrence_deck)
        exact_positions = Counter(row["line_position"] for row in occurrence_deck if row["all_readers_exact"] == "1")
        rows.append({
            "held_form_id": source["held_form_id"], "form": form, "opaque_head_id": source["opaque_head_id"],
            "body": body, "head_occupancy": source["head_occupancy"], "occurrences": len(occurrence_deck),
            "reader_exact_occurrences": exact_count, "formal705_slots": formal_count,
            "sem570_slots": sem_count, "w23_axis195_slots": w23_count,
            "line_first": positions["FIRST"], "line_middle": positions["MIDDLE"], "line_last": positions["LAST"],
            "exact_line_first": exact_positions["FIRST"], "exact_line_middle": exact_positions["MIDDLE"],
            "exact_line_last": exact_positions["LAST"], "position_exceptions": exceptions,
            "position_exception_rate": fmt(exception_rate),
            "discovery_body_decision": body_metric["discovery_decision"],
            "discovery_body_score_not_probability": body_metric["discovery_working_score_not_probability"],
            "discovery_form_gate": int(discovery_gate), "discovery_form_decision": discovery_decision,
            "w23_body_decision": body_metric["w23_decision"],
            "w23_body_score_not_probability": body_metric["w23_working_score_not_probability"],
            "w23_form_gate": int(strict_gate), "w23_form_decision": strict_decision,
            "discovery_working_whole_de": spec["selected_whole_de"] if discovery_gate and spec else "NONE",
            "licensed_working_whole_de": spec["selected_whole_de"] if strict_gate and spec else "NONE",
            "renderer_license": int(strict_gate),
            "renderer_scope": "EXACT_COMPLETE_SURFACE_AT_ENUMERATED_OCCURRENCES" if strict_gate else "NONE",
            "unconditional_global_export": 0, "literal_head_lexeme_credit": 0,
            "literal_body_lexeme_credit": 0, "component_export_credit": 0,
        })
    if len(rows) != 273:
        raise AssertionError("form adjudication must cover 273 forms")
    discovery = {str(row["form"]) for row in rows if int(row["discovery_form_gate"])}
    strict = {str(row["form"]) for row in rows if int(row["renderer_license"])}
    if discovery != EXPECTED_DISCOVERY_FORMS or strict != EXPECTED_LICENSE_FORMS:
        raise AssertionError(f"form sets changed: discovery={sorted(discovery)}, strict={sorted(strict)}")
    if discovery - strict != EXPECTED_DISCOVERY_ONLY_FORMS:
        raise AssertionError("discovery-only form set changed")
    if Counter(str(row["discovery_form_decision"]) for row in rows) != Counter(
        {"UNDECIDABLE": 256, "SUPPORTED_SCOPED_WHOLE": 16, "SUPPORTED_EXACT_WHOLE_EXCEPTION": 1}
    ):
        raise AssertionError("discovery form decision counts changed")
    if Counter(str(row["w23_form_decision"]) for row in rows) != Counter(
        {"UNDECIDABLE": 261, "SUPPORTED_SCOPED_WHOLE": 11, "SUPPORTED_EXACT_WHOLE_EXCEPTION": 1}
    ):
        raise AssertionError("W23 form decision counts changed")
    return rows, discovery, strict


def body_bridge_rows(
    candidates: list[dict[str, str]], metrics: dict[str, dict[str, object]], forms: list[dict[str, object]],
    rules: list[dict[str, str]],
) -> list[dict[str, object]]:
    discovery_forms = Counter(str(row["body"]) for row in forms if int(row["discovery_form_gate"]))
    licensed_forms = Counter(str(row["body"]) for row in forms if int(row["renderer_license"]))
    rows: list[dict[str, object]] = []
    for source in sorted(candidates, key=lambda row: row["body"]):
        body, metric = source["body"], metrics[source["body"]]
        axes = expected_axes(source["family"], rules)
        rows.append({
            "body": body, "family": source["family"], "working_axis_tags": "|".join(axes),
            "prior_candidate_de_unlicensed": source["concrete_body_role_de"],
            "prior_confidence": source["confidence"], "headed_occurrences": metric["headed_occurrences"],
            "reader_exact_occurrences": metric["reader_exact_occurrences"],
            "formal705_slots": metric["formal705_slots"], "sem570_slots": metric["sem570_slots"],
            "w23_axis195_slots": metric["w23_axis195_slots"],
            "discovery_score_not_probability": metric["discovery_working_score_not_probability"],
            "discovery_decision": metric["discovery_decision"],
            "w23_score_not_probability": metric["w23_working_score_not_probability"],
            "w23_decision": metric["w23_decision"], "discovery_complete_forms": discovery_forms[body],
            "renderer_licensed_complete_forms": licensed_forms[body],
            "state_patient_status": "OPEN" if any(axis in axes for axis in ("HEAT", "COLD", "DRY", "MOIST")) else "NOT_IDENTIFIED",
            "scalar_dimension_status": "OPEN" if "VALUE" in axes else "NOT_APPLICABLE",
            "body_renderer_license": 0, "literal_head_lexeme_credit": 0,
            "literal_body_lexeme_credit": 0, "component_export_credit": 0,
        })
    if len(rows) != 120:
        raise AssertionError("body bridge must cover 120 bodies")
    return rows


def adjudicated_discovery_cards(
    form_rows: list[dict[str, object]], specs: list[dict[str, str]],
) -> list[dict[str, object]]:
    forms = {str(row["form"]): row for row in form_rows}
    rows: list[dict[str, object]] = []
    for index, spec in enumerate(specs, 1):
        surface = spec["surface"]
        form = forms[surface]
        if not int(form["discovery_form_gate"]):
            raise AssertionError(f"renderer spec is not an algorithmic discovery survivor: {surface}")
        expected_license = int(form["renderer_license"])
        if spec["discovery_card_visible"] != "1" or int(spec["w23_renderer_license"]) != expected_license:
            raise AssertionError(f"manual display/licence flags disagree with algorithm: {surface}")
        rows.append({
            "discovery_card_id": f"G738-D{index:02d}",
            "surface": surface,
            "opaque_head_id": form["opaque_head_id"],
            "body": form["body"],
            "selected_whole_de": spec["selected_whole_de"],
            "first_realization_de": spec["first_realization_de"],
            "middle_realization_de": spec["middle_realization_de"],
            "last_realization_de": spec["last_realization_de"],
            "observed_positions": spec["observed_positions"],
            "reader_exact_positions": spec["reader_exact_positions"],
            "discovery_card_visible": 1,
            "w23_renderer_license": expected_license,
            "w23_allowed_positions": spec["w23_allowed_positions"] if expected_license else "NONE",
            "w23_license_note": spec["w23_license_note"],
            "occurrences": form["occurrences"],
            "reader_exact_occurrences": form["reader_exact_occurrences"],
            "formal705_slots": form["formal705_slots"],
            "sem570_slots": form["sem570_slots"],
            "w23_axis195_slots": form["w23_axis195_slots"],
            "discovery_body_score_not_probability": form["discovery_body_score_not_probability"],
            "w23_body_score_not_probability": form["w23_body_score_not_probability"],
            "discovery_form_decision": form["discovery_form_decision"],
            "w23_form_decision": form["w23_form_decision"],
            "confidence": spec["confidence"],
            "dimension_status": spec["dimension_status"],
            "patient_status": spec["patient_status"],
            "positive_evidence": spec["positive_evidence"],
            "counterevidence": spec["counterevidence"],
            "unconditional_global_export": 0,
            "literal_plaintext_claimed": 0,
            "component_export_credit": 0,
        })
    if len(rows) != 17 or sum(int(row["w23_renderer_license"]) for row in rows) != 12:
        raise AssertionError("discovery-card 17/12 split changed")
    return rows


def repaired_cards_and_patches(
    form_rows: list[dict[str, object]], manual_specs: dict[str, dict[str, str]],
    occurrences: list[dict[str, str]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    occ_by_form: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in occurrences:
        occ_by_form[row["form"]].append(row)
    licensed = sorted((row for row in form_rows if int(row["renderer_license"])), key=lambda row: str(row["form"]))
    cards: list[dict[str, object]] = []
    patches: list[dict[str, object]] = []
    for index, form_row in enumerate(licensed, 1):
        form = str(form_row["form"])
        spec = manual_specs.get(form)
        if spec is None:
            raise AssertionError(f"licensed form lacks renderer specification: {form}")
        if spec["w23_renderer_license"] != "1":
            raise AssertionError(f"licensed form disabled by renderer spec: {form}")
        cards.append({
            "card_id": f"G738-W{index:02d}", "surface": form,
            "opaque_head_id": form_row["opaque_head_id"], "body": form_row["body"],
            "selected_whole_de": spec["selected_whole_de"], "first_realization_de": spec["first_realization_de"],
            "middle_realization_de": spec["middle_realization_de"], "last_realization_de": spec["last_realization_de"],
            "w23_allowed_positions": spec["w23_allowed_positions"],
            "w23_license_note": spec["w23_license_note"],
            "dimension_status": spec["dimension_status"], "patient_status": spec["patient_status"],
            "occurrences": form_row["occurrences"], "reader_exact_occurrences": form_row["reader_exact_occurrences"],
            "formal705_slots": form_row["formal705_slots"], "sem570_slots": form_row["sem570_slots"],
            "w23_axis195_slots": form_row["w23_axis195_slots"],
            "position_exceptions": form_row["position_exceptions"],
            "w23_body_score_not_probability": form_row["w23_body_score_not_probability"],
            "form_decision": form_row["w23_form_decision"],
            "selection_basis": "ALGORITHMIC_W23_AXIS195_BODY_AND_FORM_GATE",
            "positive_evidence": spec["positive_evidence"], "counterevidence": spec["counterevidence"],
            "renderer_license": 1, "renderer_scope": "EXACT_COMPLETE_SURFACE_AT_ENUMERATED_OCCURRENCES",
            "unconditional_global_export": 0, "literal_plaintext_claimed": 0, "component_export_credit": 0,
        })
        card_id = f"G738-W{index:02d}"
        allowed_positions = set(spec["w23_allowed_positions"].split("|"))
        for occurrence in occ_by_form[form]:
            if occurrence["all_readers_exact"] != "1" or occurrence["line_position"] not in allowed_positions:
                continue
            field = {"FIRST": "first_realization_de", "MIDDLE": "middle_realization_de", "LAST": "last_realization_de"}[
                occurrence["line_position"]
            ]
            realization = spec[field]
            if realization == "HOLD":
                raise AssertionError(f"W23 allowed position has HOLD renderer: {form} {occurrence['line_position']}")
            patches.append({
                "patch_id": f"G738-P{len(patches) + 1:04d}", "card_id": card_id,
                "occurrence_id": occurrence["occurrence_id"], "page": occurrence["page"],
                "locus": occurrence["locus"], "token_index": occurrence["token_index"], "surface": form,
                "body": occurrence["body"], "opaque_head_id": occurrence["opaque_head_id"],
                "line_position": occurrence["line_position"],
                "position_exception": int(position_exception(occurrence["opaque_head_id"], occurrence["line_position"])),
                "exact_whole_fallback_used": 0, "section": occurrence["section"],
                "language": occurrence["language"], "previous_surface": occurrence["previous_surface"],
                "next_surface": occurrence["next_surface"], "surface_line": occurrence["surface_line"],
                "gdt738_scoped_whole_render_de": realization,
                "scope": "EXACT_COMPLETE_SURFACE_AT_ENUMERATED_OCCURRENCE",
                "unconditional_global_export": 0, "literal_plaintext_claimed": 0, "component_export_credit": 0,
            })
    if len(cards) != 12 or {row["surface"] for row in cards} != EXPECTED_LICENSE_FORMS:
        raise AssertionError("renderer card set changed")
    if len(patches) != 202:
        raise AssertionError(f"licensed exact occurrence count changed: {len(patches)}")
    licensed_exact = {
        row["occurrence_id"]: row
        for form in EXPECTED_LICENSE_FORMS for row in occ_by_form[form]
        if row["all_readers_exact"] == "1"
    }
    patched_ids = {str(row["occurrence_id"]) for row in patches}
    omitted = [row for occurrence_id, row in licensed_exact.items() if occurrence_id not in patched_ids]
    if len(licensed_exact) != 203 or len(omitted) != 1 or not (
        omitted[0]["form"] == "lkaiin"
        and omitted[0]["opaque_head_id"] == "H4"
        and omitted[0]["line_position"] == "FIRST"
    ):
        raise AssertionError("the single unpatched exact lkaiin H4 position exception changed")
    return cards, patches


def axis_enrichment(
    occurrences: list[dict[str, str]], slots: list[dict[str, object]], candidates: dict[str, dict[str, str]],
    rules: list[dict[str, str]],
) -> list[dict[str, object]]:
    occurrence_axes: dict[str, set[str]] = defaultdict(set)
    for row in slots:
        if int(row["w23_axis195_slot"]):
            occurrence_axes[str(row["source_occurrence_id"])].update(str(row["axis_tags"]).split("|"))
    exact = [row for row in occurrences if row["all_readers_exact"] == "1"]
    rows: list[dict[str, object]] = []
    for axis in ("HEAT", "COLD", "DRY", "MOIST", "VALUE", "PART"):
        target = [row for row in exact if axis in expected_axes(candidates[row["body"]]["family"], rules)]
        other = [row for row in exact if row not in target]
        if not target:
            continue
        a = sum(axis in occurrence_axes[row["occurrence_id"]] for row in target)
        b = len(target) - a
        c = sum(axis in occurrence_axes[row["occurrence_id"]] for row in other)
        d = len(other) - c
        rows.append({
            "axis": axis, "semantic_deck": LICENSE_DECK,
            "candidate_axis_exact_occurrences": len(target), "candidate_axis_neighbor_hits": a,
            "candidate_axis_hit_rate": fmt(a / len(target)), "other_exact_occurrences": len(other),
            "other_axis_neighbor_hits": c, "other_axis_hit_rate": fmt(c / len(other)),
            "haldane_odds_ratio": fmt(odds_ratio_haldene(a, b, c, d)),
            "interpretation": "CONTEXT_RANK_ONLY__NEIGHBOUR_AXIS_DOES_NOT_IDENTIFY_TARGET_LEXEME",
            "component_export_credit": 0,
        })
    if len(rows) != 6:
        raise AssertionError("axis enrichment must retain six core axes")
    return rows


def matrix_rows(
    body_map: dict[str, dict[str, object]], held_bodies: set[str], train_bodies: set[str],
) -> list[dict[str, object]]:
    orientation = {
        "VALUE_A": "host-selected scalar; dimension and absolute start open",
        "HEAT_VALUE_KA": "heat or processing intensity crossed with a scalar",
        "HEAT_STATE_KY": "heat or processing-intensity state",
        "DRY_RESULT_CHDY": "dry or firm result; patient open",
        "MOIST_RESULT_SHDY": "moist, soft or soaked result; patient open",
        "PREP_O": "preparation remains an unlicensed rival",
        "PART_AR": "part, fraction or share field; carrier open",
        "DRY_PART_OR": "dry crossed with part/share; patient open",
        "MATERIAL_OL": "state carrier with patient identity open",
        "PREP_RESULT_ODY": "preparation/result or process pass remains open",
    }
    rows: list[dict[str, object]] = []
    for family, members in FAMILY_GROUPS:
        for order, body in enumerate(members, 1):
            panel = "HELD_120" if body in held_bodies else "TRAINING_24" if body in train_bodies else "OUTSIDE_PANEL"
            metric = body_map.get(body)
            rows.append({
                "analogy_family": family, "member_order": order, "body_label": body, "panel": panel,
                "discovery_decision": metric["discovery_decision"] if metric else "COMPARATOR_ONLY",
                "w23_decision": metric["w23_decision"] if metric else "COMPARATOR_ONLY",
                "working_orientation": orientation[family], "literal_body_lexeme_credit": 0,
                "component_export_credit": 0,
            })
    if len(rows) != 34:
        raise AssertionError("analogy matrix membership changed")
    return rows


def hold_rows(
    specs: list[dict[str, str]], form_map: dict[str, dict[str, object]], body_map: dict[str, dict[str, object]],
    quarantine: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for source in specs:
        label = source["surface"]
        if label in form_map:
            row = form_map[label]
            values = (
                "HEADED_WHOLE", row["w23_form_decision"], row["occurrences"],
                row["reader_exact_occurrences"], row["formal705_slots"], row["sem570_slots"],
                row["w23_axis195_slots"], row["position_exceptions"],
            )
        elif label in body_map:
            row = body_map[label]
            values = (
                "BODY_TRANSFER", row["w23_decision"], row["headed_occurrences"],
                row["reader_exact_occurrences"], row["formal705_slots"], row["sem570_slots"],
                row["w23_axis195_slots"], row["position_exceptions"],
            )
        else:
            raise AssertionError(f"hold object not found: {label}")
        object_type, decision, occurrences, exact, formal, sem570, w23, exceptions = values
        rows.append({
            **source, "object_type": object_type, "algorithmic_w23_decision": decision,
            "occurrences": occurrences, "reader_exact_occurrences": exact, "formal705_slots": formal,
            "sem570_slots": sem570, "w23_axis195_slots": w23, "position_exceptions": exceptions,
            "gdt737_inherited_decision": quarantine.get(label, {}).get("gdt737_decision", "NO_GDT737_WHOLE_CARD"),
            "manual_text_is_audit_only": 1, "renderer_license_from_this_table": 0,
            "component_export_credit": 0,
        })
    if len(rows) != 14:
        raise AssertionError("manual hold audit row count changed")
    if not {"sary", "so", "lchor", "lsheody"} <= {row["surface"] for row in rows}:
        raise AssertionError("required held-out stress form missing")
    return rows


def historical_rows() -> list[dict[str, object]]:
    registered = {row["source_id"] for row in read_tsv(ROOT / HISTORICAL_REGISTRY_REL)}
    rows: list[dict[str, object]] = []
    for source in read_tsv(SRC / "HISTORICAL_MODEL_SPECS.tsv"):
        local_ids = [value for value in source["source_ids"].split("|") if value.startswith("HSR")]
        if any(value not in registered for value in local_ids) or source["voynich_relation_credit"] != "0":
            raise AssertionError(f"historical comparator gate failed: {source['model_id']}")
        rows.append({**source, "all_voynich_relation_credit_zero": 1})
    if len(rows) != 8:
        raise AssertionError("historical comparator count changed")
    return rows


def assert_decks(slots: list[dict[str, object]]) -> dict[str, object]:
    counts = {
        "adjacent_slots": len(slots),
        "neighbor_reader_exact": sum(int(row["neighbor_reader_exact"]) for row in slots),
        "both_reader_exact": sum(int(row["both_reader_exact"]) for row in slots),
        "formal705": sum(int(row["formal705_slot"]) for row in slots),
        "sem570": sum(int(row["sem570_slot"]) for row in slots),
        "w23_axis197_precomposition": sum(int(row["w23_axis197_precomposition_slot"]) for row in slots),
        "w23_axis195": sum(int(row["w23_axis195_slot"]) for row in slots),
    }
    expected = {
        "adjacent_slots": 1266, "neighbor_reader_exact": 972, "both_reader_exact": 783,
        "formal705": 705, "sem570": 570, "w23_axis197_precomposition": 197, "w23_axis195": 195,
    }
    if counts != expected:
        raise AssertionError(f"held deck counts changed: {counts}")
    for flag, footprint in (
        ("formal705_slot", (520, 109, 182)), ("sem570_slot", (444, 105, 162)),
        ("w23_axis197_precomposition_slot", (180, 71, 90)), ("w23_axis195_slot", (178, 71, 89)),
    ):
        selected = [row for row in slots if int(row[flag])]
        observed = (
            len({row["source_occurrence_id"] for row in selected}), len({row["body"] for row in selected}),
            len({row["form"] for row in selected}),
        )
        if observed != footprint:
            raise AssertionError(f"{flag} footprint changed: {observed}")
    sem = [row for row in slots if int(row["sem570_slot"])]
    levels = Counter(str(row["neighbor_confidence_level"]) for row in sem)
    expected_levels = Counter({
        "NA": 356, "W3_SOLID_WORKING_THEORY": 160, "W2_PROVISIONAL_WORKING": 37,
        "W1_WEAK_WORKING": 15, "W0_PLACEHOLDER_OR_SEMANTICALLY_EMPTY": 2,
    })
    if levels != expected_levels:
        raise AssertionError(f"SEM570 confidence distribution changed: {levels}")
    strict_levels = Counter(
        str(row["neighbor_confidence_level"]) for row in slots if int(row["w23_axis195_slot"])
    )
    if strict_levels != Counter({"W3_SOLID_WORKING_THEORY": 160, "W2_PROVISIONAL_WORKING": 35}):
        raise AssertionError(f"W23 confidence distribution changed: {strict_levels}")
    if sum(row["axis_tags"] == "OTHER" for row in sem) != 3:
        raise AssertionError("SEM570 OTHER-axis count changed")
    return counts


def assert_key_body_values(metrics: dict[str, dict[str, object]]) -> None:
    expected = {
        "ain": (12, 86, 71, 89, 76, 25), "sheedy": (12, 11, 6, 8, 7, 0),
        "kar": (10, 33, 31, 45, 38, 7), "keey": (8, 39, 35, 46, 39, 17),
        "cheol": (7, 18, 18, 22, 18, 5), "cheor": (7, 6, 6, 8, 6, 2),
        "kaiin": (7, 51, 46, 61, 45, 16), "kain": (7, 34, 28, 42, 40, 13),
        "ky": (7, 21, 18, 23, 16, 3), "key": (6, 8, 8, 12, 8, 1),
        "cheedy": (4, 10, 7, 9, 7, 3),
    }
    for body, wanted in expected.items():
        row = metrics[body]
        observed = (
            int(row["discovery_working_score_not_probability"]), int(row["headed_occurrences"]),
            int(row["reader_exact_occurrences"]), int(row["formal705_slots"]), int(row["sem570_slots"]),
            int(row["w23_axis195_slots"]),
        )
        if observed != wanted:
            raise AssertionError(f"key body metrics changed for {body}: {observed}")
    expected_cosines = {
        "ain": ("aiin", .421221, .969004, .974738),
        "sheedy": ("shedy", .164677, .928610, .748115),
        "kar": ("ar", .433101, .985497, .946835),
        "keey": ("ky", .156386, .949324, .994013),
        "cheol": ("ol", .221880, .884909, .830354),
        "cheor": ("or", .232119, .822463, .793725),
        "kaiin": ("kain", .389058, .980144, .986789),
        "kain": ("kaiin", .389058, .980144, .986789),
        "ky": ("keey", .156386, .949324, .994013),
        "key": ("ky", .180579, .918751, .815284),
        "cheedy": ("chedy", .436141, .926971, .875689),
        "char": ("ar", .000000, .731552, .296423),
        "cheody": ("chody", .000000, .776736, .780399),
    }
    for body, (comparator, surface, axis, register) in expected_cosines.items():
        row = metrics[body]
        observed = (
            row["discovery_family_comparator"], float(row["discovery_family_surface_cosine"]),
            float(row["discovery_family_axis_cosine"]), float(row["discovery_family_register_cosine"]),
        )
        if observed[0] != comparator or any(
            abs(value - wanted) > .000001 for value, wanted in zip(observed[1:], (surface, axis, register))
        ):
            raise AssertionError(f"key family cosine changed for {body}: {observed}")


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    axes, family_rules = load_axis_rules()
    held_occ = read_tsv(ROOT / HELD_OCC_REL)
    held_candidates = read_tsv(ROOT / HELD_BODY_REL)
    held_forms = read_tsv(ROOT / HELD_FORM_REL)
    train_occ = read_tsv(ROOT / TRAIN_OCC_REL)
    train_bodies = read_tsv(ROOT / TRAIN_BODY_REL)
    if (
        len(held_candidates) != 120 or len(held_forms) != 273 or len(held_occ) != 811
        or sum(row["all_readers_exact"] == "1" for row in held_occ) != 619
        or len({row["page"] for row in held_occ}) != 134 or len({row["locus"] for row in held_occ}) != 697
        or Counter(int(row["head_occupancy"]) for row in held_candidates) != Counter({2: 87, 3: 33})
        or len(train_bodies) != 24 or len(train_occ) != 1166
    ):
        raise AssertionError("GDT736/GDT737 source shape changed")
    if any(row["page"].startswith("f84") for row in held_occ + train_occ):
        raise AssertionError("sealed page entered occurrence inputs")

    manual_specs = read_tsv(SRC / "MANUAL_WHOLE_SPECS.tsv")
    manual_map = {row["surface"]: row for row in manual_specs}
    if len(manual_specs) != 17 or set(manual_map) != EXPECTED_DISCOVERY_FORMS:
        raise AssertionError("renderer-spec set must equal the 17 algorithmic discovery forms")

    by_line, exact, guards = token_context()
    cells = compact_cells()
    held_slots = adjacent_slots(held_occ, by_line, exact, cells, axes, "H")
    train_slots = adjacent_slots(train_occ, by_line, exact, cells, axes, "T")
    deck_counts = assert_decks(held_slots)
    metric_rows, metric_map = body_metrics(held_candidates, held_occ, held_slots, train_occ, train_slots)
    assert_key_body_values(metric_map)
    form_rows, discovery_forms, licensed_forms = form_adjudication(
        held_forms, held_occ, held_slots, metric_map, manual_map
    )
    form_map = {str(row["form"]): row for row in form_rows}
    if (
        sum(int(form_map[form]["occurrences"]) for form in discovery_forms) != 308
        or sum(int(form_map[form]["reader_exact_occurrences"]) for form in discovery_forms) != 266
        or sum(int(form_map[form]["formal705_slots"]) for form in discovery_forms) != 354
        or sum(int(form_map[form]["sem570_slots"]) for form in discovery_forms) != 291
        or sum(int(form_map[form]["w23_axis195_slots"]) for form in discovery_forms) != 91
    ):
        raise AssertionError("17-form discovery footprint changed")
    if (
        sum(int(form_map[form]["occurrences"]) for form in licensed_forms) != 238
        or sum(int(form_map[form]["reader_exact_occurrences"]) for form in licensed_forms) != 203
        or sum(int(form_map[form]["formal705_slots"]) for form in licensed_forms) != 273
        or sum(int(form_map[form]["w23_axis195_slots"]) for form in licensed_forms) != 68
    ):
        raise AssertionError("12-form renderer footprint changed")

    candidate_map = {row["body"]: row for row in held_candidates}
    body_bridge = body_bridge_rows(held_candidates, metric_map, form_rows, family_rules)
    semantic_anchors = [row for row in held_slots if int(row["sem570_slot"])]
    enrichment = axis_enrichment(held_occ, held_slots, candidate_map, family_rules)
    matrices = matrix_rows(metric_map, set(candidate_map), {row["body"] for row in train_bodies})
    discovery_cards = adjudicated_discovery_cards(form_rows, manual_specs)
    cards, patches = repaired_cards_and_patches(form_rows, manual_map, held_occ)
    quarantine = {row["surface"]: row for row in read_tsv(ROOT / QUARANTINE_REL)}
    holds = hold_rows(read_tsv(SRC / "MANUAL_HOLD_SPECS.tsv"), form_map, metric_map, quarantine)
    historical = historical_rows()

    artifacts: dict[str, list[dict[str, object]]] = {
        "ADJACENT_1266_SLOT_AUDIT.tsv": held_slots,
        "NONHEAD_NEIGHBOR_AXIS_ANCHORS.tsv": semantic_anchors,
        "BODY_120_SEMANTIC_BRIDGE.tsv": body_bridge,
        "BODY_TRANSFER_METRICS.tsv": metric_rows,
        "FORM_273_ADJUDICATION.tsv": form_rows,
        "AXIS_NEIGHBOR_ENRICHMENT.tsv": enrichment,
        "MATRIX_WORKING_MODEL.tsv": matrices,
        "REPAIRED_SCOPED_WHOLE_CARDS.tsv": cards,
        "ADJUDICATED_17_WHOLE_CARDS.tsv": discovery_cards,
        "OCCURRENCE_RENDERER_PATCH.tsv": patches,
        "MANUAL_HOLD_AUDIT.tsv": holds,
        "HISTORICAL_MICROENTRY_MODELS.tsv": historical,
    }
    for name, rows in artifacts.items():
        if not rows:
            raise AssertionError(f"empty artifact: {name}")
        write_tsv(output_dir / name, rows, list(rows[0]))

    discovery_counts = Counter(str(row["discovery_decision"]) for row in metric_rows)
    w23_counts = Counter(str(row["w23_decision"]) for row in metric_rows)
    result: dict[str, object] = {
        "schema": "GDT738_TWO_DECK_OCCURRENCE_ADJUDICATION_RESULT_V2",
        "status": (
            "PARTIAL__TWO_DIRECT_CROSS_HEAD_SURVIVORS__FIVE_ADDITIONAL_W23_FAMILY_SURVIVORS__"
            "FOUR_DISCOVERY_ONLY_FAMILY_PASSES__TWELVE_SCOPED_COMPLETE_WHOLE_CARDS__"
            "LITERAL_SALT_DOWNGRADED__ZERO_LEXEME_EXPORT__NO_NEW_PAGE"
        ),
        "scope": {
            "inherited_allowlist_pages": guards["allowed_pages"], "held_pages": 134, "held_loci": 697,
            "new_pages_used": 0, "f84_used": False, "f84r_used": False,
            "guard_stats": {"tokens": guards["tokens"], "cross": guards["cross"]},
        },
        "target": {
            "held_bodies": 120, "occupancy_2_bodies": 87, "occupancy_3_bodies": 33,
            "held_forms": 273, "held_occurrences": 811, "reader_exact_occurrences": 619,
            "adjacent_fields": 1266,
        },
        "decks": {
            **deck_counts,
            "sem570_confidence": {"NA": 356, "W3": 160, "W2": 37, "W1": 15, "W0": 2},
            "w23_axis195_confidence": {"W3": 160, "W2": 35},
            "formal705_footprint": {"target_occurrences": 520, "bodies": 109, "forms": 182},
            "sem570_footprint": {"target_occurrences": 444, "bodies": 105, "forms": 162},
            "w23_axis195_footprint": {"target_occurrences": 178, "bodies": 71, "forms": 89},
        },
        "discovery_adjudication": {
            "semantic_deck": DISCOVERY_DECK, "body_decisions": dict(sorted(discovery_counts.items())),
            "supported_bodies": sorted(EXPECTED_DISCOVERY_BODIES),
            "contradicted_family_transfers": ["char", "cheody"],
            "surviving_forms": sorted(discovery_forms), "surviving_form_count": 17,
            "discovery_cards": len(discovery_cards), "renderer_licences": 0,
        },
        "renderer_adjudication": {
            "semantic_deck": LICENSE_DECK, "body_decisions": dict(sorted(w23_counts.items())),
            "supported_bodies": sorted(EXPECTED_LICENSE_BODIES), "licensed_forms": sorted(licensed_forms),
            "licensed_form_count": 12, "patched_reader_exact_in_scope_occurrences": len(patches),
            "unpatched_exact_position_exceptions": 1,
            "discovery_only_forms": sorted(EXPECTED_DISCOVERY_ONLY_FORMS),
        },
        "scoring": {
            "capacity": "+1 exact-target>=4; +1 FORMAL705>=4",
            "direct": "+2 shared exact surface; +1 registered surface; +1 shared axis fingerprint; +1 registered fingerprint; +1 register overlap",
            "family": "+2 surface cosine>=.15; +1 axis cosine>=.80; +1 register cosine>=.70",
            "penalties": "-2 single formal head at >=8 slots; -1 position-exception rate>=1/3; -1 LOW/UNKNOWN prior",
            "score_is_probability": False,
        },
        "claims": {
            "literal_head_lexemes": 0, "literal_body_lexemes": 0, "component_export_credit": 0,
            "unseen_forms_predicted": 0, "plaintext_translations_claimed": 0,
            "state_patient": "OPEN", "scalar_dimension": "OPEN",
        },
        "artifact_rows": {name: len(rows) for name, rows in artifacts.items()},
        "artifact_hashes": {str(BASE_REL / "artifacts" / name): sha256(output_dir / name) for name in OUTPUT_NAMES},
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    result = build(parser.parse_args().output_dir)
    print(json.dumps({
        "schema": result["schema"], "status": result["status"], "decks": result["decks"],
        "discovery_adjudication": result["discovery_adjudication"],
        "renderer_adjudication": result["renderer_adjudication"], "artifact_rows": result["artifact_rows"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
