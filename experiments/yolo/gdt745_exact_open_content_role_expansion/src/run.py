#!/usr/bin/env python3
"""Expand GDT744's exact open content forms across the inherited safe cache.

The experiment keeps complete EVA surfaces opaque. It asks whether the same
unknown whole repeatedly occupies descriptive, prescriptive, quantity/part or
ambiguous materia contexts. A role is a working slot assignment, never a word
translation or a component value.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import subprocess
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
BASE_REL = Path("experiments/yolo/gdt745_exact_open_content_role_expansion")
EXP = ROOT / BASE_REL
SRC = EXP / "src"
DEFAULT_ARTIFACTS = EXP / "artifacts"

G739_RUN_REL = Path(
    "experiments/yolo/gdt739_twelve_whole_local_dimension_dispatch/src/run.py"
)
G734_DICTIONARY_REL = Path(
    "experiments/yolo/gdt734_v99r7_recurrent_unknown_family_dispatch/artifacts/"
    "V99R7_1606_COMPLETE_WORD_CONFIDENCE.tsv"
)
G743_PATCH_REL = Path(
    "experiments/yolo/gdt743_r2_run_intersection_adjudication/artifacts/"
    "TARGET_202_RENDERER_PATCH_V5.tsv"
)
G744_RUN_REL = Path(
    "experiments/yolo/gdt744_historical_microfield_channel_bridge/src/run.py"
)
G744_CANDIDATE_REL = Path(
    "experiments/yolo/gdt744_historical_microfield_channel_bridge/artifacts/"
    "UNRESOLVED_CONTENT_SLOT_CANDIDATES.tsv"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load dependency: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


g739 = load_module("gdt739_builder_for_gdt745", ROOT / G739_RUN_REL)
g744 = load_module("gdt744_builder_for_gdt745", ROOT / G744_RUN_REL)

ROLE_ORDER = (
    "DESCRIPTIVE_LEMMA_OR_ATTRIBUTE",
    "INGREDIENT_OR_PROCESS_COMPLEMENT",
    "QUANTITY_REFERENT_OR_PART_NAME",
    "MATERIA_OR_INGREDIENT",
    "OPEN",
)
SPECIFIC_ROLES = set(ROLE_ORDER[:3])
ROLE_BY_CHANNEL = {
    "DESCRIPTIVE_MATERIA": "DESCRIPTIVE_LEMMA_OR_ATTRIBUTE",
    "DESCRIPTIVE_QUALITY": "DESCRIPTIVE_LEMMA_OR_ATTRIBUTE",
    "PRESCRIPTIVE_RECIPE": "INGREDIENT_OR_PROCESS_COMPLEMENT",
    "PRESCRIPTIVE_PROCESS": "INGREDIENT_OR_PROCESS_COMPLEMENT",
    "QUANTITY_OR_PART": "QUANTITY_REFERENT_OR_PART_NAME",
    "MATERIA_OR_INGREDIENT": "MATERIA_OR_INGREDIENT",
    "OPEN": "OPEN",
}
TIER_ORDER = {
    "R3_PERSISTENT_CROSS_PAGE_ROLE": 4,
    "R2_DOMINANT_CROSS_PAGE_ROLE_WITH_RIVALS": 3,
    "R2_CROSS_PAGE_ROLE_LEAD": 3,
    "R1_EXTERNAL_CONTEXT_LEAD": 2,
    "R1_SEED_FIELD_ONLY": 1,
    "R1_MATERIA_INGREDIENT_AMBIGUITY": 1,
    "R0_OPEN": 0,
}
ANALOGY_TIER_ORDER = {
    "A3_DISTANCE1_MULTIWHOLE_CONSENSUS": 5,
    "A2_DISTANCE1_PLUS_RADIUS2_CONSENSUS": 4,
    "A2_DISTANCE2_MULTIWHOLE_CONSENSUS": 4,
    "A1_SINGLE_NEIGHBOR_LEAD": 2,
    "A1_MIXED_NEIGHBORHOOD": 1,
    "A0_NO_CLEAN_NEIGHBOR": 0,
}
ANALOGY_TAG_ORDER = (
    "HOT", "COLD", "DRY", "MOIST", "AMOUNT", "PART", "MATERIAL",
    "PREPARATION", "PROCESS", "CLOSE", "PASS", "BEGIN_STAGE",
    "MIDDLE_STAGE", "END_STAGE", "LEVEL_II", "LEVEL_III",
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
STATUS = (
    "PARTIAL__41_EXACT_OPEN_SURFACES__136_CACHE_OCCURRENCES__53_PAGES__"
    "22_CROSS_PAGE_WHOLES__136_OF_136_CENTERED_CONTEXTS_OPEN__"
    "34_MULTIWHOLE_AXIS_CONSENSUS__17_DISTANCE1_MULTIWHOLE__"
    "41_EXPLORATORY_WORKING_DEFAULTS__ZERO_LITERAL_IDENTITIES__"
    "ZERO_COMPONENT_EXPORT__NO_NEW_PAGE"
)
OUTPUT_NAMES = (
    "EXACT_136_OCCURRENCE_CONTEXTS.tsv",
    "GDT744_44_FIELD_MEMBERSHIPS.tsv",
    "WHOLE_NEIGHBOR_ANALOGY_DECK.tsv",
    "CONTENT_41_ROLE_CENSUS.tsv",
    "CROSS_PAGE_ROLE_CARDS.tsv",
    "FOCUS_20_CROSS_PAGE_ROLE_READER.tsv",
    "GDT745_EXACT_CONTENT_ROLE_READER.md",
    "GDT745_GDT388_CONTENT_ROLE_EDGE_PACKET.tsv",
    "GDT745_GDT388_EDGE_INTAKE.json",
)


def read_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def write_tsv(path: Path, rows: Iterable[dict[str, object]], fields: Iterable[str]) -> None:
    names = list(fields)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=names, delimiter="\t", lineterminator="\n",
            extrasaction="raise",
        )
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in names})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def joined(items: Iterable[str], order: Iterable[str] | None = None) -> str:
    members = set(items)
    selected = sorted(members) if order is None else [item for item in order if item in members]
    return "|".join(selected) or "NONE"


def count_string(counter: Counter[str], order: Iterable[str] | None = None) -> str:
    keys = sorted(counter) if order is None else [key for key in order if counter[key]]
    return "|".join(f"{key}:{counter[key]}" for key in keys) or "NONE"


def physical_folio(page: str) -> str:
    if page.startswith("fRos"):
        return "fRos"
    match = re.match(r"^(f\d+)", page)
    if not match:
        raise AssertionError(f"invalid page: {page}")
    return match.group(1)


def line_position(ordinal: int, length: int) -> str:
    if length == 1:
        return "SINGLE"
    if ordinal == 1:
        return "FIRST"
    if ordinal == length:
        return "LAST"
    return "MIDDLE"


def role_for(channel: str) -> str:
    return ROLE_BY_CHANNEL[channel]


def role_default_de(role: str, headword_like: bool = False) -> str:
    if role == "DESCRIPTIVE_LEMMA_OR_ATTRIBUTE":
        if headword_like:
            return "gelerntes Stoff-/Pflanzenlemma; konkrete Identität offen"
        return "gelerntes Beschreibungslemma oder Stoffname; konkrete Identität offen"
    if role == "INGREDIENT_OR_PROCESS_COMPLEMENT":
        return "Zutat oder Ergänzung eines Verarbeitungsvorgangs; konkrete Identität offen"
    if role == "QUANTITY_REFERENT_OR_PART_NAME":
        return "Bezugsstoff oder Teilname einer Menge; konkrete Identität offen"
    if role == "MATERIA_OR_INGREDIENT":
        return "Stoff- oder Zutatenname; Beschreibungs-/Rezeptkanal offen"
    if role == "MIXED_CONTEXT_CONTENT_WHOLE":
        return "wiederkehrende Inhaltsform mit wechselnder Feldrolle"
    return "Inhaltsform unbekannt"


def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for left_index, left_char in enumerate(left, start=1):
        current = [left_index]
        for right_index, right_char in enumerate(right, start=1):
            current.append(min(
                current[-1] + 1,
                previous[right_index] + 1,
                previous[right_index - 1] + int(left_char != right_char),
            ))
        previous = current
    return previous[-1]


def analogy_tags(text: str, patterns: dict[str, re.Pattern[str]]) -> set[str]:
    tags = set(g739.axes_for(text, patterns))
    # The inherited anchor vocabulary predates the explicit boil/heat synonym.
    if re.search(r"koch|ausgekoch", text, re.I):
        tags.add("HOT")
    tags.update(tag for tag, pattern in STAGE_PATTERNS.items() if pattern.search(text))
    return tags


def analogy_functional_class(tags: set[str]) -> str:
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


def automatic_analogy_default(tags: set[str], nearest_gloss: str, tier: str) -> str:
    if not tags:
        if nearest_gloss != "NONE":
            return f"Ganzwort-Analogie zu „{nearest_gloss}“; genaue Funktion offen"
        return "keine saubere Ganzwort-Analogie; Funktion offen"
    qualities = [
        label for tag, label in (
            ("DRY", "trocken"), ("HOT", "heiß/erhitzt"),
            ("COLD", "kalt/gekühlt"), ("MOIST", "feucht/eingeweicht"),
        ) if tag in tags
    ]
    stages = [
        label for tag, label in (
            ("BEGIN_STAGE", "Anfangs-/Grundstufe"),
            ("MIDDLE_STAGE", "Mittelstufe"),
            ("END_STAGE", "End-/Vollstufe"),
            ("LEVEL_II", "Stufe II"), ("LEVEL_III", "Stufe III"),
        ) if tag in tags
    ]
    nouns = [
        label for tag, label in (
            ("MATERIAL", "Stoff/Material"),
            ("PREPARATION", "Ansatz/Zubereitung"),
            ("AMOUNT", "Menge/Portion"), ("PART", "Teil/Fraktion"),
            ("PROCESS", "Vorgang"), ("CLOSE", "Abschluss/Resultat"),
            ("PASS", "Verarbeitungsgang"),
        ) if tag in tags
    ]
    if not nouns:
        nouns = ["Zustand/Feld"]
    phrase = ", ".join(qualities + stages + nouns)
    suffix = "Mehrfachanalogie" if tier.startswith(("A2", "A3")) else "Einzelanalogie"
    return f"{phrase}; konkrete Identität offen ({suffix})"


def build_analogy_deck(
    surfaces: set[str],
) -> tuple[list[dict[str, object]], dict[str, dict[str, object]], dict[str, object]]:
    _, patterns = g739.load_axis_specs()
    dictionary = read_tsv(ROOT / G734_DICTIONARY_REL)
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
    for surface, rows in grouped.items():
        reading_tags = [analogy_tags(row["working_meaning_de"], patterns) for row in rows]
        core_tags = set.intersection(*reading_tags)
        if not core_tags:
            continue
        ranked = sorted(rows, key=lambda row: (
            -int(row["working_model_level"].startswith("W3")),
            -int(row["working_model_score_0_100_not_probability"]),
            row["reading_id"],
        ))
        glosses = list(dict.fromkeys(row["working_meaning_de"] for row in ranked))
        pool[surface] = {
            "surface": surface,
            "rows": rows,
            "core_tags": core_tags,
            "union_tags": set.union(*reading_tags),
            "best_gloss": glosses[0],
            "glosses": " || ".join(glosses),
            "reading_ids": "|".join(row["reading_id"] for row in ranked),
            "levels": joined(row["working_model_level"] for row in rows),
            "max_score": max(int(row["working_model_score_0_100_not_probability"]) for row in rows),
            "page_count": max(int(row["page_count"]) for row in rows),
            "occurrence_count": max(int(row["occurrence_count"]) for row in rows),
        }

    deck_rows: list[dict[str, object]] = []
    summaries: dict[str, dict[str, object]] = {}
    for candidate in sorted(surfaces):
        neighbors = sorted(
            (
                levenshtein(candidate, known_surface), known_surface, spec
            )
            for known_surface, spec in pool.items()
            if known_surface != candidate and levenshtein(candidate, known_surface) <= 2
        )
        if not neighbors:
            summaries[candidate] = {
                "analogy_min_edit_distance": "NA",
                "analogy_radius": 0,
                "analogy_neighbor_wholes": 0,
                "analogy_closest_neighbor_wholes": 0,
                "analogy_neighbor_surfaces": "NONE",
                "analogy_nearest_glosses_de": "NONE",
                "analogy_consensus_axes": "NONE",
                "analogy_rival_axes": "NONE",
                "analogy_axis_support": "NONE",
                "analogy_functional_class": "MIXED_OR_OPEN_WHOLE",
                "analogy_confidence_level": "A0_NO_CLEAN_NEIGHBOR",
                "automatic_working_meaning_de": automatic_analogy_default(
                    set(), "NONE", "A0_NO_CLEAN_NEIGHBOR"
                ),
            }
            continue
        minimum = neighbors[0][0]
        closest = [row for row in neighbors if row[0] == minimum]
        radius = minimum if len(closest) >= 2 or minimum == 2 else 2
        selected = [row for row in neighbors if row[0] <= radius]
        counts: Counter[str] = Counter(
            tag for _, _, spec in selected for tag in spec["core_tags"]
        )
        consensus = {
            tag for tag, count in counts.items()
            if tag != "VALUE" and count >= 2 and count / len(selected) >= 0.60
        }
        rivals = {
            tag for tag, count in counts.items()
            if tag != "VALUE" and tag not in consensus and count >= 1
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
        nearest_glosses = " || ".join(
            f"{known_surface}={spec['best_gloss']}" for _, known_surface, spec in closest
        )
        summaries[candidate] = {
            "analogy_min_edit_distance": minimum,
            "analogy_radius": radius,
            "analogy_neighbor_wholes": len(selected),
            "analogy_closest_neighbor_wholes": len(closest),
            "analogy_neighbor_surfaces": "|".join(row[1] for row in selected),
            "analogy_nearest_glosses_de": nearest_glosses,
            "analogy_consensus_axes": joined(consensus, ANALOGY_TAG_ORDER),
            "analogy_rival_axes": joined(rivals, ANALOGY_TAG_ORDER),
            "analogy_axis_support": count_string(counts, ANALOGY_TAG_ORDER),
            "analogy_functional_class": analogy_functional_class(consensus),
            "analogy_confidence_level": tier,
            "automatic_working_meaning_de": automatic_analogy_default(
                consensus,
                str(closest[0][2]["best_gloss"]) if closest else "NONE",
                tier,
            ),
        }
        for distance, known_surface, spec in selected:
            deck_rows.append({
                "analogy_id": f"G745-A{len(deck_rows) + 1:04d}",
                "candidate_surface": candidate,
                "known_neighbor_surface": known_surface,
                "levenshtein_distance": distance,
                "within_closest_layer": int(distance == minimum),
                "selected_radius": radius,
                "known_neighbor_reading_ids": spec["reading_ids"],
                "known_neighbor_levels": spec["levels"],
                "known_neighbor_max_score_not_probability": spec["max_score"],
                "known_neighbor_occurrences": spec["occurrence_count"],
                "known_neighbor_pages": spec["page_count"],
                "known_neighbor_core_axes": joined(spec["core_tags"], ANALOGY_TAG_ORDER),
                "known_neighbor_union_axes": joined(spec["union_tags"], ANALOGY_TAG_ORDER),
                "known_neighbor_best_gloss_de": spec["best_gloss"],
                "known_neighbor_all_glosses_de": spec["glosses"],
                "candidate_consensus_axes": joined(consensus, ANALOGY_TAG_ORDER),
                "candidate_analogy_confidence_level": tier,
                "relation_scope": "EXACT_WHOLE_EDIT_ANALOGY_ONLY",
                "literal_identity_credit": 0,
                "component_export_credit": 0,
            })
    diagnostics = {
        "dictionary_rows": len(dictionary),
        "clean_axis_reading_rows": sum(len(rows) for rows in grouped.values()),
        "clean_axis_whole_pool": len(pool),
    }
    return deck_rows, summaries, diagnostics


def make_neighbor(
    locus: str,
    center_ordinal: int,
    delta: int,
    line: list[dict[str, str]],
    exact: dict[tuple[str, int], int],
    cells: dict[tuple[str, int], dict[str, str]],
    patterns: dict[str, re.Pattern[str]],
    target_coordinates: set[tuple[str, int]],
) -> dict[str, object] | None:
    ordinal = center_ordinal + delta
    if not 1 <= ordinal <= len(line):
        return None
    token = line[ordinal - 1]
    cell = cells[(locus, ordinal)]
    if token["eva"] != cell["surface"]:
        raise AssertionError(f"raw/cache mismatch at {locus}:{ordinal}")
    semantic = cell["v99r7_semantic_value_de"]
    tags = g739.axes_for(semantic, patterns)
    scalar_types = g739.host_scalar_types(tags, semantic)
    hits = g739.retired_hits(semantic)
    reader_exact = exact[(locus, int(token["token_index"]))]
    initial_head = int(g739.strict_initial_head(cell["surface"]))
    another_target = int((locus, ordinal) in target_coordinates)
    known = int(cell["unknown_v99r7"] == "0")
    w23 = int(cell["gdt734_confidence_level"].startswith(("W2", "W3")))
    zero_composition = int(cell["gdt734_composition_semantic_credit"] == "0")
    zero_component = int(cell["component_export_credit"] == "0")
    failures: list[str] = []
    if not reader_exact:
        failures.append("READER_VARIANT")
    if initial_head:
        failures.append("OPAQUE_INITIAL_HEAD")
    if another_target:
        failures.append("GDT738_TARGET_BOUNDARY")
    if not known:
        failures.append("UNKNOWN")
    if not w23:
        failures.append("BELOW_W2_OR_NA")
    if not zero_composition:
        failures.append("COMPOSITION_CREDIT")
    if not zero_component:
        failures.append("COMPONENT_EXPORT_CREDIT")
    if hits:
        failures.append("RETIRED_LITERAL_PATIENT")
    if not tags:
        failures.append("NO_SELECTING_AXIS")
    return {
        "window_id": "PENDING",
        "side": "L" if delta < 0 else "R",
        "signed_offset": delta,
        "distance": abs(delta),
        "neighbor_ordinal": ordinal,
        "neighbor_surface": cell["surface"],
        "neighbor_reader_exact": reader_exact,
        "neighbor_semantic_value_de": semantic,
        "neighbor_confidence_level": cell["gdt734_confidence_level"],
        "neighbor_unknown_v99r7": cell["unknown_v99r7"],
        "neighbor_composition_semantic_credit": cell["gdt734_composition_semantic_credit"],
        "strict_initial_head_neighbor": initial_head,
        "another_gdt738_target": another_target,
        "retired_patient_words": "|".join(hits) or "NONE",
        "axis_tags": "|".join(tags) or "NONE",
        "scalar_host_types": "|".join(scalar_types) or "NONE",
        "eligible_local_anchor": int(
            reader_exact and not initial_head and not another_target and known and w23
            and zero_composition and zero_component and not hits and bool(tags)
        ),
        "ineligibility_reasons": "|".join(failures) or "NONE",
        "head_or_body_lexeme_credit": 0,
        "component_export_credit": 0,
    }


def render_context(
    span: list[dict[str, object]], center_surface: str, center_ordinal: int,
) -> tuple[str, str]:
    ordered = sorted(span, key=lambda row: int(row["neighbor_ordinal"]))
    surfaces: list[str] = []
    rendered: list[str] = []
    inserted = False
    for neighbor in ordered:
        ordinal = int(neighbor["neighbor_ordinal"])
        if not inserted and center_ordinal < ordinal:
            surfaces.append(f"⟦{center_surface}⟧")
            rendered.append(f"⟦{center_surface}: offene Inhaltsform⟧")
            inserted = True
        surfaces.append(str(neighbor["neighbor_surface"]))
        if g744.strong_anchor(neighbor, g744.STRONG_W23):
            rendered.append(str(neighbor["neighbor_semantic_value_de"]))
        else:
            rendered.append(f"[{neighbor['neighbor_surface']}:?]")
    if not inserted:
        surfaces.append(f"⟦{center_surface}⟧")
        rendered.append(f"⟦{center_surface}: offene Inhaltsform⟧")
    return " ".join(surfaces), "; ".join(rendered)


def build_occurrences(
    candidate_rows: list[dict[str, str]],
    rules: list[dict[str, str]],
    supplements: dict[str, dict[str, str]],
) -> tuple[list[dict[str, object]], dict[str, object]]:
    surfaces = {row["candidate_surface"] for row in candidate_rows}
    seed_by_coordinate: dict[tuple[str, int, str], list[dict[str, str]]] = defaultdict(list)
    for row in candidate_rows:
        seed_by_coordinate[(
            row["locus"], int(row["candidate_ordinal"]), row["candidate_surface"]
        )].append(row)

    by_line, exact, guard = g739.g738.token_context()
    cells = g739.g738.compact_cells()
    _, patterns = g739.load_axis_specs()
    target_coordinates = {
        (row["locus"], int(row["token_ordinal"]))
        for row in read_tsv(ROOT / G743_PATCH_REL)
    }
    selected_cells = [row for row in cells.values() if row["surface"] in surfaces]
    selected_cells.sort(key=lambda row: row["cell_id"])
    if (
        len(candidate_rows) != 42 or len(surfaces) != 41 or len(selected_cells) != 136
        or len({row["page"] for row in selected_cells}) != 53
    ):
        raise AssertionError("GDT744 candidate or GDT734 recurrence boundary changed")

    output: list[dict[str, object]] = []
    for number, cell in enumerate(selected_cells, start=1):
        locus = cell["locus"]
        ordinal = int(cell["token_ordinal"])
        line = by_line[locus]
        token = line[ordinal - 1]
        if token["eva"] != cell["surface"]:
            raise AssertionError(f"candidate raw/cache mismatch at {locus}:{ordinal}")
        window: dict[tuple[str, int], dict[str, object]] = {}
        for delta in (*range(-5, 0), *range(1, 6)):
            neighbor = make_neighbor(
                locus, ordinal, delta, line, exact, cells, patterns, target_coordinates,
            )
            if neighbor is None:
                continue
            neighbor["window_id"] = f"G745-N{number:03d}-{delta:+d}"
            window[(str(neighbor["side"]), int(neighbor["distance"]))] = neighbor

        span, left_reason, right_reason = g744.clipped_span(window, 5)
        anchors, tags, signature, evidence = g744.anchor_bundle(
            span, g744.STRONG_W23, supplements
        )
        w3_anchors, w3_tags, w3_signature, _ = g744.anchor_bundle(
            span, g744.STRONG_W3, supplements
        )
        channel = g744.channel_for(tags, rules)
        w3_channel = g744.channel_for(w3_tags, rules)
        seed = seed_by_coordinate.get((locus, ordinal, cell["surface"]), [])
        eva_context, safe_render = render_context(span, cell["surface"], ordinal)
        left_extent = max(
            (int(row["distance"]) for row in span if row["side"] == "L"), default=0
        )
        right_extent = max(
            (int(row["distance"]) for row in span if row["side"] == "R"), default=0
        )
        output.append({
            "gdt745_occurrence_id": f"G745-O{number:03d}",
            "cell_id": cell["cell_id"],
            "page": cell["page"],
            "physical_folio": physical_folio(cell["page"]),
            "locus": locus,
            "candidate_ordinal": ordinal,
            "candidate_surface": cell["surface"],
            "candidate_reader_exact": exact[(locus, int(token["token_index"]))],
            "section": token["section"],
            "language": token["language"],
            "hand": token["hand"],
            "line_position": line_position(ordinal, len(line)),
            "line_token_count": len(line),
            "gdt744_seed_occurrence": int(bool(seed)),
            "gdt744_seed_field_ids": joined(row["gdt744_field_id"] for row in seed),
            "gdt744_seed_channels": joined(
                (row["field_channel"] for row in seed), g744.CHANNEL_ORDER
            ),
            "gdt744_seed_slot_classes": joined(row["candidate_slot_class"] for row in seed),
            "external_to_gdt744_seed": int(not seed),
            "left_extent": left_extent,
            "right_extent": right_extent,
            "bounded_span_tokens": len(span),
            "left_boundary_reason": left_reason,
            "right_boundary_reason": right_reason,
            "boundary_complete": int(g744.complete_boundary(left_reason, right_reason)),
            "strong_anchor_count": len(anchors),
            "strong_anchor_surfaces": joined(row["neighbor_surface"] for row in anchors),
            "strong_anchor_tags": joined(tags),
            "strong_anchor_signature": signature,
            "strong_anchor_evidence": evidence,
            "w3_anchor_count": len(w3_anchors),
            "w3_anchor_signature": w3_signature,
            "w3_context_channel": w3_channel,
            "context_channel": channel,
            "context_role_family": role_for(channel),
            "context_informative": int(channel != "OPEN"),
            "quality_conflict": int(
                {"HOT", "COLD"} <= tags or {"DRY", "MOIST"} <= tags
            ),
            "eva_context": eva_context,
            "safe_context_render_de": safe_render,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
            "unseen_form_export": 0,
            "_anchors": anchors,
        })

    if sum(int(row["gdt744_seed_occurrence"]) for row in output) != 42:
        raise AssertionError("not all 42 GDT744 seed cells returned")
    return output, guard


def build_field_memberships(
    candidate_rows: list[dict[str, str]],
    rules: list[dict[str, str]],
    supplements: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    surfaces = {row["candidate_surface"] for row in candidate_rows}
    seed_ids = {row["candidate_id"] for row in candidate_rows}
    seed_keys = {
        (
            row["gdt744_field_id"], row["locus"], int(row["candidate_ordinal"]),
            row["candidate_surface"],
        ): row["candidate_id"]
        for row in candidate_rows
    }
    windows = g744.read_tsv(ROOT / g744.G739_WINDOW_REL)
    patches = g744.read_tsv(ROOT / g744.G743_PATCH_REL)
    patches.sort(key=lambda row: row["gdt743_patch_id"])
    fields = g744.build_initial_fields(patches, windows, rules, supplements)
    fields, _, _, _ = g744.decorate_fields(fields, rules)
    output: list[dict[str, object]] = []
    for field in fields:
        for neighbor in field["_span"]:
            if neighbor["neighbor_surface"] not in surfaces:
                continue
            if not g744.unresolved_candidate(neighbor):
                continue
            key = (
                str(field["gdt744_field_id"]), str(field["locus"]),
                int(neighbor["neighbor_ordinal"]), str(neighbor["neighbor_surface"]),
            )
            seed_id = seed_keys.get(key, "NONE")
            output.append({
                "membership_id": f"G745-M{len(output) + 1:03d}",
                "candidate_surface": neighbor["neighbor_surface"],
                "page": field["page"],
                "locus": field["locus"],
                "candidate_ordinal": neighbor["neighbor_ordinal"],
                "gdt744_field_id": field["gdt744_field_id"],
                "gdt744_target_surface": field["surface"],
                "gdt744_target_ordinal": field["target_ordinal"],
                "field_channel": field["raw_field_channel"],
                "field_role_family": role_for(str(field["raw_field_channel"])),
                "field_confidence_tier": field["field_confidence_tier"],
                "template_backed_field_reading": field["template_backed_field_reading"],
                "strong_anchor_count": field["strong_anchor_count"],
                "strong_anchor_evidence": field["strong_anchor_evidence"],
                "gdt744_seed_membership": int(seed_id != "NONE"),
                "gdt744_seed_candidate_id": seed_id,
                "literal_identity": "OPEN",
                "component_export_credit": 0,
            })
    if len(output) != 44 or {row["candidate_surface"] for row in output} != surfaces:
        raise AssertionError("expanded GDT744 field membership boundary changed")
    if {row["gdt744_seed_candidate_id"] for row in output if row["gdt744_seed_membership"]} != seed_ids:
        raise AssertionError("GDT744 seed membership recovery incomplete")
    return output


def decorate_census_with_analogy(
    census: list[dict[str, object]],
    summaries: dict[str, dict[str, object]],
    memberships: list[dict[str, object]],
) -> list[dict[str, object]]:
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in memberships:
        by_surface[str(row["candidate_surface"])].append(row)
    overrides_path = SRC / "WORKING_DEFAULT_OVERRIDES.tsv"
    overrides = (
        {row["candidate_surface"]: row for row in read_tsv(overrides_path)}
        if overrides_path.is_file() else {}
    )
    if overrides and set(overrides) != {str(row["candidate_surface"]) for row in census}:
        raise AssertionError("working-default override surface deck must contain all 41 forms")
    for row in census:
        surface = str(row["candidate_surface"])
        fields = by_surface[surface]
        channels = Counter(str(field["field_channel"]) for field in fields)
        specific_field_roles = {
            str(field["field_role_family"])
            for field in fields if str(field["field_role_family"]) in SPECIFIC_ROLES
        }
        summary = summaries[surface]
        row.update({
            "gdt744_all_field_memberships": len(fields),
            "gdt744_all_field_pages": len({str(field["page"]) for field in fields}),
            "gdt744_all_field_channel_counts": count_string(channels, g744.CHANNEL_ORDER),
            "gdt744_cross_field_specific_role_conflict": int(len(specific_field_roles) > 1),
            **summary,
        })
        override = overrides.get(surface)
        if override is not None:
            if override["expected_analogy_confidence_level"] != summary["analogy_confidence_level"]:
                raise AssertionError(f"analogy tier drift for manual default: {surface}")
            if override["expected_consensus_axes"] != summary["analogy_consensus_axes"]:
                raise AssertionError(f"analogy axes drift for manual default: {surface}")
            row["next_working_meaning_de"] = override["next_working_meaning_de"]
            row["meaning_rationale_de"] = override["meaning_rationale_de"]
            row["manual_default_applied"] = 1
        else:
            row["next_working_meaning_de"] = summary["automatic_working_meaning_de"]
            row["meaning_rationale_de"] = (
                "automatic whole-neighbor axis synthesis; manual wording pending"
            )
            row["manual_default_applied"] = 0
        row["next_renderer_scope"] = "EXACT_WHOLE_EXPLORATORY_ANALOGY_ONLY"
        row["next_literal_identity"] = "OPEN"
        row["next_confirmed_lexeme"] = 0
        row["next_component_export_credit"] = 0
    return census


def choose_role(
    surface_rows: list[dict[str, object]], seed_rows: list[dict[str, str]],
) -> dict[str, object]:
    seed_specific = Counter(
        role_for(row["field_channel"])
        for row in seed_rows if role_for(row["field_channel"]) in SPECIFIC_ROLES
    )
    seed_ambiguous = sum(
        role_for(row["field_channel"]) == "MATERIA_OR_INGREDIENT" for row in seed_rows
    )
    external_exact = [
        row for row in surface_rows
        if int(row["external_to_gdt744_seed"]) and int(row["candidate_reader_exact"])
    ]
    external_info = [row for row in external_exact if int(row["context_informative"])]
    external_specific = Counter(
        str(row["context_role_family"])
        for row in external_info if str(row["context_role_family"]) in SPECIFIC_ROLES
    )
    external_ambiguous = sum(
        row["context_role_family"] == "MATERIA_OR_INGREDIENT" for row in external_info
    )
    combined = seed_specific + external_specific
    winner = "OPEN"
    dominance = 0.0
    tied = False
    if combined:
        highest = max(combined.values())
        winners = [role for role in ROLE_ORDER if combined[role] == highest]
        tied = len(winners) != 1
        winner = winners[0] if not tied else "MIXED_CONTEXT_CONTENT_WHOLE"
        dominance = highest / sum(combined.values())
    elif seed_ambiguous or external_ambiguous:
        winner = "MATERIA_OR_INGREDIENT"

    evidence_rows = [
        row for row in surface_rows
        if str(row["context_role_family"]) == winner
        and int(row["candidate_reader_exact"]) and int(row["context_informative"])
    ]
    seed_pages = {
        row["page"] for row in seed_rows if role_for(row["field_channel"]) == winner
    }
    support_pages = seed_pages | {str(row["page"]) for row in evidence_rows}
    competing_roles = {role for role in combined if role != winner and combined[role]}
    external_support_pages = {
        str(row["page"]) for row in external_info
        if str(row["context_role_family"]) == winner
    }
    external_support_signatures = {
        str(row["strong_anchor_signature"]) for row in external_info
        if str(row["context_role_family"]) == winner
    }

    if winner in SPECIFIC_ROLES and len(support_pages) >= 2 and not competing_roles:
        tier = "R3_PERSISTENT_CROSS_PAGE_ROLE"
    elif winner in SPECIFIC_ROLES and len(support_pages) >= 2 and dominance >= (2 / 3):
        tier = "R2_DOMINANT_CROSS_PAGE_ROLE_WITH_RIVALS"
    elif winner in SPECIFIC_ROLES and len(support_pages) >= 2:
        tier = "R2_CROSS_PAGE_ROLE_LEAD"
    elif winner in SPECIFIC_ROLES and external_info:
        tier = "R1_EXTERNAL_CONTEXT_LEAD"
    elif winner in SPECIFIC_ROLES:
        tier = "R1_SEED_FIELD_ONLY"
    elif winner == "MATERIA_OR_INGREDIENT":
        tier = "R1_MATERIA_INGREDIENT_AMBIGUITY"
    else:
        tier = "R0_OPEN"

    exact_rows = [row for row in surface_rows if int(row["candidate_reader_exact"])]
    first_count = sum(row["line_position"] in {"FIRST", "SINGLE"} for row in exact_rows)
    headword_like = bool(
        winner == "DESCRIPTIVE_LEMMA_OR_ATTRIBUTE" and len(exact_rows) >= 2
        and first_count / len(exact_rows) >= 0.5
    )
    if tied:
        winner = "MIXED_CONTEXT_CONTENT_WHOLE"
    return {
        "selected_working_role": winner,
        "working_role_confidence_level": tier,
        "role_dominance_fraction": f"{dominance:.3f}",
        "competing_specific_roles": joined(competing_roles, ROLE_ORDER),
        "seed_specific_role_counts": count_string(seed_specific, ROLE_ORDER),
        "external_specific_role_counts": count_string(external_specific, ROLE_ORDER),
        "seed_ambiguous_count": seed_ambiguous,
        "external_ambiguous_count": external_ambiguous,
        "external_informative_exact_occurrences": len(external_info),
        "external_support_pages": len(external_support_pages),
        "external_support_signatures": len(external_support_signatures),
        "combined_support_pages": len(support_pages),
        "headword_position_lead": int(headword_like),
        "working_default_de": role_default_de(winner, headword_like),
    }


def build_census(
    occurrences: list[dict[str, object]], candidates: list[dict[str, str]],
) -> list[dict[str, object]]:
    by_surface: dict[str, list[dict[str, object]]] = defaultdict(list)
    seed_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in occurrences:
        by_surface[str(row["candidate_surface"])].append(row)
    for row in candidates:
        seed_by_surface[row["candidate_surface"]].append(row)

    output: list[dict[str, object]] = []
    for number, surface in enumerate(sorted(by_surface), start=1):
        rows = by_surface[surface]
        exact_rows = [row for row in rows if int(row["candidate_reader_exact"])]
        external = [row for row in rows if int(row["external_to_gdt744_seed"])]
        channels = Counter(str(row["context_channel"]) for row in exact_rows)
        roles = Counter(str(row["context_role_family"]) for row in exact_rows)
        positions = Counter(str(row["line_position"]) for row in exact_rows)
        decision = choose_role(rows, seed_by_surface[surface])
        anchor_surfaces = sorted({
            anchor_surface for row in rows if int(row["candidate_reader_exact"])
            for anchor_surface in str(row["strong_anchor_surfaces"]).split("|")
            if anchor_surface != "NONE"
        })
        evidence = (
            f"GDT744 seed={joined((row['field_channel'] for row in seed_by_surface[surface]), g744.CHANNEL_ORDER)}; "
            f"external exact informative={decision['external_informative_exact_occurrences']}; "
            f"selected support pages={decision['combined_support_pages']}; "
            f"external signatures={decision['external_support_signatures']}; "
            f"anchor wholes={','.join(anchor_surfaces[:8]) or 'none'}"
        )
        open_external = sum(
            int(row["candidate_reader_exact"]) and row["context_role_family"] == "OPEN"
            for row in external
        )
        variants = len(rows) - len(exact_rows)
        counter = (
            f"reader-variant occurrences={variants}; external exact open contexts={open_external}; "
            f"competing specific roles={decision['competing_specific_roles']}; "
            "role is inferred from neighboring working cards, not from the surface itself"
        )
        output.append({
            "gdt745_role_id": f"G745-R{number:03d}",
            "candidate_surface": surface,
            "cache_occurrences": len(rows),
            "cache_pages": len({str(row["page"]) for row in rows}),
            "cache_loci": len({str(row["locus"]) for row in rows}),
            "reader_exact_occurrences": len(exact_rows),
            "reader_exact_pages": len({str(row["page"]) for row in exact_rows}),
            "gdt744_seed_cells": len(seed_by_surface[surface]),
            "gdt744_seed_pages": len({row["page"] for row in seed_by_surface[surface]}),
            "gdt744_seed_channels": joined(
                (row["field_channel"] for row in seed_by_surface[surface]), g744.CHANNEL_ORDER,
            ),
            "external_occurrences": len(external),
            "external_reader_exact_occurrences": sum(
                int(row["candidate_reader_exact"]) for row in external
            ),
            "boundary_complete_reader_exact_occurrences": sum(
                int(row["candidate_reader_exact"]) and int(row["boundary_complete"])
                for row in rows
            ),
            "exact_context_channel_counts": count_string(channels, g744.CHANNEL_ORDER),
            "exact_context_role_counts": count_string(roles, ROLE_ORDER),
            "exact_line_position_counts": count_string(
                positions, ("FIRST", "MIDDLE", "LAST", "SINGLE")
            ),
            **decision,
            "positive_evidence": evidence,
            "counterevidence": counter,
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "plaintext_credit": 0,
            "component_export_credit": 0,
            "unseen_form_export": 0,
        })
    return output


def role_cards(census: list[dict[str, object]]) -> list[dict[str, object]]:
    selected = [
        row for row in census if int(row["cache_pages"]) >= 2
        and row["analogy_confidence_level"] != "A0_NO_CLEAN_NEIGHBOR"
    ]
    selected.sort(key=lambda row: (
        -ANALOGY_TIER_ORDER[str(row["analogy_confidence_level"])],
        -int(row["reader_exact_pages"]), -int(row["cache_occurrences"]),
        str(row["candidate_surface"]),
    ))
    output: list[dict[str, object]] = []
    for number, row in enumerate(selected, start=1):
        output.append({
            "gdt745_card_id": f"G745-C{number:03d}",
            "candidate_surface": row["candidate_surface"],
            "gdt744_field_slot_role": row["selected_working_role"],
            "analogy_functional_class": row["analogy_functional_class"],
            "next_working_meaning_de": row["next_working_meaning_de"],
            "analogy_confidence_level": row["analogy_confidence_level"],
            "analogy_consensus_axes": row["analogy_consensus_axes"],
            "analogy_rival_axes": row["analogy_rival_axes"],
            "analogy_neighbor_surfaces": row["analogy_neighbor_surfaces"],
            "analogy_nearest_glosses_de": row["analogy_nearest_glosses_de"],
            "cache_occurrences": row["cache_occurrences"],
            "cache_pages": row["cache_pages"],
            "reader_exact_occurrences": row["reader_exact_occurrences"],
            "reader_exact_pages": row["reader_exact_pages"],
            "gdt744_seed_channels": row["gdt744_seed_channels"],
            "gdt744_all_field_channel_counts": row["gdt744_all_field_channel_counts"],
            "gdt744_cross_field_specific_role_conflict": row[
                "gdt744_cross_field_specific_role_conflict"
            ],
            "positive_evidence": row["positive_evidence"],
            "counterevidence": row["counterevidence"],
            "renderer_scope": "EXACT_WHOLE_ROLE_CARD_ONLY_NO_LITERAL_SUBSTANCE",
            "literal_identity": "OPEN",
            "confirmed_lexeme": 0,
            "component_export_credit": 0,
        })
    return output


def focus_rows(
    occurrences: list[dict[str, object]], census: list[dict[str, object]],
) -> list[dict[str, object]]:
    census_map = {str(row["candidate_surface"]): row for row in census}
    ranked_surfaces = sorted(census_map, key=lambda surface: (
        -ANALOGY_TIER_ORDER[str(census_map[surface]["analogy_confidence_level"])],
        -int(census_map[surface]["reader_exact_pages"]),
        -int(census_map[surface]["cache_occurrences"]), surface,
    ))
    output: list[dict[str, object]] = []
    for surface in ranked_surfaces:
        if len(output) >= 20:
            break
        candidates = [
            row for row in occurrences
            if row["candidate_surface"] == surface and int(row["candidate_reader_exact"])
        ]
        candidates.sort(key=lambda row: (
            -int(row["external_to_gdt744_seed"]), -int(row["context_informative"]),
            -int(row["boundary_complete"]), -int(row["strong_anchor_count"]),
            str(row["gdt745_occurrence_id"]),
        ))
        if not candidates:
            continue
        row = candidates[0]
        card = census_map[surface]
        output.append({
            "focus_id": f"G745-F{len(output) + 1:02d}",
            "selection_role": "BEST_EXTERNAL_EXACT_CONTEXT_PER_RANKED_SURFACE",
            "candidate_surface": surface,
            "gdt744_field_slot_role": card["selected_working_role"],
            "analogy_functional_class": card["analogy_functional_class"],
            "next_working_meaning_de": card["next_working_meaning_de"],
            "analogy_confidence_level": card["analogy_confidence_level"],
            "analogy_consensus_axes": card["analogy_consensus_axes"],
            "analogy_rival_axes": card["analogy_rival_axes"],
            "analogy_neighbor_surfaces": card["analogy_neighbor_surfaces"],
            "analogy_nearest_glosses_de": card["analogy_nearest_glosses_de"],
            "page": row["page"],
            "locus": row["locus"],
            "candidate_ordinal": row["candidate_ordinal"],
            "line_position": row["line_position"],
            "external_to_gdt744_seed": row["external_to_gdt744_seed"],
            "boundary_complete": row["boundary_complete"],
            "context_channel": row["context_channel"],
            "context_role_family": row["context_role_family"],
            "strong_anchor_count": row["strong_anchor_count"],
            "strong_anchor_evidence": row["strong_anchor_evidence"],
            "eva_context": row["eva_context"],
            "safe_context_render_de": row["safe_context_render_de"],
            "manual_assessment": "PENDING_MANUAL_REVIEW",
            "manual_note": "PENDING_MANUAL_REVIEW",
            "literal_identity": "OPEN",
        })
    return output


def attach_manual(focus: list[dict[str, object]]) -> list[dict[str, object]]:
    manual_path = SRC / "MANUAL_FOCUS_ASSESSMENTS.tsv"
    if not manual_path.is_file():
        return focus
    specs = {row["focus_id"]: row for row in read_tsv(manual_path)}
    if set(specs) != {str(row["focus_id"]) for row in focus}:
        raise AssertionError("manual focus assessment IDs do not match generated focus deck")
    for row in focus:
        spec = specs[str(row["focus_id"])]
        if spec["expected_surface"] != row["candidate_surface"] or spec["expected_locus"] != row["locus"]:
            raise AssertionError(f"manual focus input drift: {row['focus_id']}")
        row["manual_assessment"] = spec["manual_assessment"]
        row["manual_note"] = spec["manual_note"]
    return focus


def write_reader(
    path: Path,
    census: list[dict[str, object]],
    cards: list[dict[str, object]],
    focus: list[dict[str, object]],
) -> None:
    tiers = Counter(str(row["analogy_confidence_level"]) for row in census)
    roles = Counter(str(row["analogy_functional_class"]) for row in census)
    lines = [
        "# GDT745 exact open content role reader", "",
        "This is an exploratory whole-form role atlas, not a Voynich translation. It keeps",
        "all literal identities open and grants no substring or component value.", "",
        "## Overview", "",
        "- 41 GDT744 content surfaces expand to 136 cached occurrences on 53 pages.",
        f"- {len(cards)} recurrent cross-page role cards are emitted.",
        f"- Role tiers: {count_string(tiers)}.",
        f"- Selected roles: {count_string(roles)}.", "",
        "## Cross-page cards", "",
        "| EVA whole | functional class | working meaning | tier | exact pages |",
        "|---|---|---|---|---:|",
    ]
    for row in cards:
        lines.append(
            f"| `{row['candidate_surface']}` | {row['analogy_functional_class']} | "
            f"{row['next_working_meaning_de']} | {row['analogy_confidence_level']} | "
            f"{row['reader_exact_pages']} |"
        )
    lines.extend(["", "## Focus contexts", ""])
    for row in focus:
        lines.extend([
            f"### {row['focus_id']} — `{row['candidate_surface']}` at {row['locus']}", "",
            f"- GDT744 field-slot role: {row['gdt744_field_slot_role']}",
            f"- Whole-neighbor class: {row['analogy_functional_class']} ({row['analogy_confidence_level']})",
            f"- Working meaning: {row['next_working_meaning_de']}",
            f"- Consensus axes: {row['analogy_consensus_axes']}; rivals: {row['analogy_rival_axes']}",
            f"- Nearest known wholes: {row['analogy_nearest_glosses_de']}",
            f"- Candidate-centered context channel: {row['context_channel']}; anchors: {row['strong_anchor_evidence']}",
            f"- EVA: `{row['eva_context']}`",
            f"- Safe local rendering: {row['safe_context_render_de']}",
            f"- Manual assessment: {row['manual_assessment']} — {row['manual_note']}", "",
        ])
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def edge_packet(
    output_dir: Path,
    occurrences: list[dict[str, object]],
    census: list[dict[str, object]],
    analogy_deck: list[dict[str, object]],
) -> dict[str, object]:
    census_map = {str(row["candidate_surface"]): row for row in census}
    ranked_cards = sorted(
        (
            row for row in census
            if int(row["cache_pages"]) >= 2
            and row["analogy_confidence_level"] != "A0_NO_CLEAN_NEIGHBOR"
        ),
        key=lambda row: (
            -ANALOGY_TIER_ORDER[str(row["analogy_confidence_level"])],
            -int(row["reader_exact_pages"]), str(row["candidate_surface"]),
        ),
    )
    compact = g739.g738.compact_cells()
    cells_by_surface: dict[str, list[dict[str, str]]] = defaultdict(list)
    for cell in compact.values():
        if cell["unknown_v99r7"] == "0":
            cells_by_surface[cell["surface"]].append(cell)
    selected_relation = None
    for candidate_card in ranked_cards:
        source_rows = sorted(
            (
                row for row in occurrences
                if row["candidate_surface"] == candidate_card["candidate_surface"]
                and int(row["candidate_reader_exact"])
            ),
            key=lambda row: str(row["gdt745_occurrence_id"]),
        )
        analog_rows = sorted(
            (
                row for row in analogy_deck
                if row["candidate_surface"] == candidate_card["candidate_surface"]
            ),
            key=lambda row: (
                int(row["levenshtein_distance"]), str(row["known_neighbor_surface"])
            ),
        )
        for candidate_analog in analog_rows:
            known_rows = cells_by_surface[str(candidate_analog["known_neighbor_surface"])]
            for source_row in source_rows:
                same_page = sorted(
                    (row for row in known_rows if row["page"] == source_row["page"]),
                    key=lambda row: row["cell_id"],
                )
                if same_page:
                    selected_relation = (
                        candidate_card, source_row, candidate_analog, same_page[0]
                    )
                    break
            if selected_relation:
                break
        if selected_relation:
            break
    if selected_relation is None:
        raise AssertionError("no same-page whole-analogy relation available for edge intake")
    card, source, analog, known_cell = selected_relation
    packet = [{
        "edge_id": "G745E001",
        "batch_id": "GDT745_EXACT_CONTENT_ROLE_CONTEXT",
        "page": source["page"],
        "physical_folio": source["physical_folio"],
        "diagram_unit_id": "CACHED_TEXT_ROLE_CONTEXT",
        "pivot_visual_id": f"UNKNOWN_WHOLE_{source['candidate_surface']}",
        "pivot_locus": f"{source['locus']}@{source['candidate_ordinal']}",
        "target_visual_id": (
            f"KNOWN_WHOLE_{analog['known_neighbor_surface']}_{known_cell['page']}"
        ),
        "target_locus": f"{known_cell['locus']}@{known_cell['token_ordinal']}",
        "relation_type": "EXACT_WHOLE_EDIT_NEIGHBOR_ANALOGY",
        "direction_basis": f"LEVENSHTEIN_DISTANCE_{analog['levenshtein_distance']}",
        "ownership_basis": "CLEAN_W2_W3_WHOLE_AXIS_CONSENSUS",
        "geometry_only_selection": "FALSE",
        "source_manifest_id": "GDT745",
        "page_crop_sha256": "NONE",
        "pivot_crop_sha256": "NONE",
        "target_crop_sha256": "NONE",
        "source_aware_localizer": "GDT745_BUILDER",
        "relation_reviewer": "PENDING_EXTERNAL",
        "relation_confidence": card["analogy_confidence_level"],
        "ambiguity_state": "ANALOGY_ONLY_LITERAL_IDENTITY_OPEN",
        "formal_access_state": "FORMAL_ACCESSED",
        "fold_assignment": "NONE",
        "eligibility_status": "INELIGIBLE_FORMAL_CONTEXT_RELATION",
    }]
    packet_path = output_dir / "GDT745_GDT388_CONTENT_ROLE_EDGE_PACKET.tsv"
    write_tsv(packet_path, packet, list(packet[0]))
    completed = subprocess.run(
        [str(ROOT / "vmanus-exp"), "check-edge-packet", str(packet_path)],
        cwd=ROOT, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if completed.returncode not in {0, 1} or not completed.stdout:
        raise AssertionError(f"edge intake failed: {completed.stderr}")
    intake = json.loads(completed.stdout)
    if intake["status"] != "INVALID_PACKET" or intake["score_ready"]:
        raise AssertionError("role-context relation packet unexpectedly score-ready")
    (output_dir / "GDT745_GDT388_EDGE_INTAKE.json").write_text(
        json.dumps(intake, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return intake


def public_occurrence(row: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in row.items() if not key.startswith("_")}


def build(output_dir: Path) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates = read_tsv(ROOT / G744_CANDIDATE_REL)
    rules = g744.load_channel_rules()
    supplements = g744.load_whole_supplements()
    occurrences, guard = build_occurrences(candidates, rules, supplements)
    memberships = build_field_memberships(candidates, rules, supplements)
    census = build_census(occurrences, candidates)
    analogy_deck, analogy_summaries, analogy_diagnostics = build_analogy_deck(
        {row["candidate_surface"] for row in candidates}
    )
    census = decorate_census_with_analogy(
        census, analogy_summaries, memberships
    )
    cards = role_cards(census)
    focus = attach_manual(focus_rows(occurrences, census))

    public_occurrences = [public_occurrence(row) for row in occurrences]
    write_tsv(
        output_dir / "EXACT_136_OCCURRENCE_CONTEXTS.tsv",
        public_occurrences, list(public_occurrences[0]),
    )
    write_tsv(
        output_dir / "GDT744_44_FIELD_MEMBERSHIPS.tsv",
        memberships, list(memberships[0]),
    )
    write_tsv(
        output_dir / "WHOLE_NEIGHBOR_ANALOGY_DECK.tsv",
        analogy_deck, list(analogy_deck[0]),
    )
    write_tsv(output_dir / "CONTENT_41_ROLE_CENSUS.tsv", census, list(census[0]))
    write_tsv(
        output_dir / "CROSS_PAGE_ROLE_CARDS.tsv", cards,
        list(cards[0]) if cards else ["gdt745_card_id"],
    )
    write_tsv(
        output_dir / "FOCUS_20_CROSS_PAGE_ROLE_READER.tsv", focus, list(focus[0])
    )
    write_reader(output_dir / "GDT745_EXACT_CONTENT_ROLE_READER.md", census, cards, focus)
    intake = edge_packet(output_dir, occurrences, census, analogy_deck)

    channels = Counter(str(row["context_channel"]) for row in occurrences)
    roles = Counter(str(row["analogy_functional_class"]) for row in census)
    tiers = Counter(str(row["analogy_confidence_level"]) for row in census)
    exact_total = sum(int(row["candidate_reader_exact"]) for row in occurrences)
    result: dict[str, object] = {
        "schema": "GDT745_EXACT_OPEN_CONTENT_ROLE_EXPANSION_RESULT_V1",
        "status": STATUS,
        "scope": {
            "gdt744_seed_cells": len(candidates),
            "candidate_surfaces": len(census),
            "cache_occurrences": len(occurrences),
            "cache_pages": len({str(row["page"]) for row in occurrences}),
            "cache_loci": len({str(row["locus"]) for row in occurrences}),
            "cross_page_surfaces": sum(int(row["cache_pages"]) >= 2 for row in census),
            "reader_exact_occurrences": exact_total,
            "reader_exact_surfaces": sum(int(row["reader_exact_occurrences"]) > 0 for row in census),
            "inherited_allowed_pages": guard["allowed_pages"],
            "new_pages_used": 0,
            "new_images_used": 0,
            "new_transcriptions_used": 0,
            "f84_used": False,
            "f84r_used": False,
        },
        "contexts": {
            "channel_counts": dict(sorted(channels.items())),
            "boundary_complete_occurrences": sum(int(row["boundary_complete"]) for row in occurrences),
            "informative_occurrences": sum(int(row["context_informative"]) for row in occurrences),
            "external_occurrences": sum(int(row["external_to_gdt744_seed"]) for row in occurrences),
            "external_reader_exact_informative_occurrences": sum(
                int(row["external_to_gdt744_seed"]) and int(row["candidate_reader_exact"])
                and int(row["context_informative"]) for row in occurrences
            ),
        },
        "roles": {
            "analogy_functional_class_counts": dict(sorted(roles.items())),
            "analogy_confidence_tier_counts": dict(sorted(tiers.items())),
            "cross_page_role_cards": len(cards),
            "multiwhole_consensus_surfaces": sum(
                str(row["analogy_confidence_level"]).startswith(("A2", "A3"))
                for row in census
            ),
            "distance1_multiwhole_consensus_surfaces": sum(
                row["analogy_confidence_level"] == "A3_DISTANCE1_MULTIWHOLE_CONSENSUS"
                for row in census
            ),
            "no_clean_neighbor_surfaces": sum(
                row["analogy_confidence_level"] == "A0_NO_CLEAN_NEIGHBOR"
                for row in census
            ),
            "headword_position_leads": sum(int(row["headword_position_lead"]) for row in census),
        },
        "field_membership": {
            "all_memberships": len(memberships),
            "all_surfaces": len({str(row["candidate_surface"]) for row in memberships}),
            "cross_page_membership_surfaces": sum(
                int(row["gdt744_all_field_pages"]) >= 2 for row in census
            ),
            "specific_role_conflict_surfaces": sum(
                int(row["gdt744_cross_field_specific_role_conflict"]) for row in census
            ),
        },
        "whole_analogy": {
            **analogy_diagnostics,
            "analogy_relations": len(analogy_deck),
            "surfaces_with_consensus_axes": sum(
                row["analogy_consensus_axes"] != "NONE" for row in census
            ),
            "manual_defaults_applied": sum(int(row["manual_default_applied"]) for row in census),
        },
        "relation_edge_intake": intake,
        "claims": {
            "confirmed_lexemes": 0,
            "plaintext_translations": 0,
            "literal_substances_or_species": 0,
            "head_or_body_lexeme_credit": 0,
            "component_export_credit": 0,
            "unseen_form_predictions": 0,
        },
        "guarded_cache": guard,
        "artifact_rows": {
            "EXACT_136_OCCURRENCE_CONTEXTS.tsv": len(occurrences),
            "GDT744_44_FIELD_MEMBERSHIPS.tsv": len(memberships),
            "WHOLE_NEIGHBOR_ANALOGY_DECK.tsv": len(analogy_deck),
            "CONTENT_41_ROLE_CENSUS.tsv": len(census),
            "CROSS_PAGE_ROLE_CARDS.tsv": len(cards),
            "FOCUS_20_CROSS_PAGE_ROLE_READER.tsv": len(focus),
            "GDT745_GDT388_CONTENT_ROLE_EDGE_PACKET.tsv": 1,
            "GDT745_GDT388_EDGE_INTAKE.json": 1,
        },
        "artifact_hashes": {
            str(BASE_REL / "artifacts" / name): sha256(output_dir / name)
            for name in OUTPUT_NAMES
        },
    }
    (output_dir / "RESULT.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_ARTIFACTS)
    result = build(parser.parse_args().output_dir)
    print(json.dumps({
        "schema": result["schema"], "status": result["status"],
        "scope": result["scope"], "contexts": result["contexts"],
        "roles": result["roles"],
    }, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
