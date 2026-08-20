#!/usr/bin/env python3
"""Deterministic W10 semantics-light structured-production generator."""

from __future__ import annotations

import hashlib
import random


WORLD_ID = "W10"
ALPHABET = tuple("BDFGHJKMPRTV")
REGISTERS = ("R0", "R1", "R2", "R3")
HANDS = ("H0", "H1", "H2")

WORLD_META = {
    "world_id": WORLD_ID,
    "title": "Semantics-light structured production",
    "broad_family": "SEMANTICS_LIGHT_GENERATOR",
    "practical_domain": "semantics-light structured production",
    "semantics_light": True,
    "organic_evolution": False,
    "clean_engineered_control": False,
    "adversarial_pair_id": "PAIR_SEMANTIC",
    "carrier_profile": "CARRIER_ADVERSARIAL_MATCHED",
    "alphabet": list(ALPHABET),
    "registers": list(REGISTERS),
    "hands": list(HANDS),
    "evolution_processes": [
        "inert_prototype_drift",
        "copy_variant_inheritance",
        "contextual_clipping",
        "graphic_fusion",
        "frequency_leveling",
        "hand_substitution",
        "register_divergence",
    ],
    "generator_schema": "GDT395_WORLD_GENERATOR_V1",
}


# These are arbitrary inherited graphic prototypes, not lexical forms.
BASE_FORMS = (
    "BDGRT", "MFKD", "TPRBJ", "GVMFD", "RJTB", "DKMPV",
    "FHBRD", "PTGKM", "VDRF", "KJMBT", "BRVGD", "TMDFK",
    "GPRB", "JVDMT", "FKTRG", "MPBJD", "RGTKV", "DBMFR",
    "HVTPD", "KBRMG", "PGDJ", "VMTFK", "DRBJV", "GTMPD",
    "JFKRV", "BMVGT", "TKDPB", "RFMJG", "VGKDR", "PJBMT",
    "DTVRK", "MGRFB",
)

# Each construction is a cyclic sequence of purely formal slot classes.
CONSTRUCTIONS = (
    ("A", "B", "C", "B", "D"),
    ("A", "A", "D", "C"),
    ("E", "B", "E", "D", "C", "B"),
    ("C", "F", "B", "C", "D"),
    ("D", "A", "B", "F", "B"),
    ("F", "E", "C", "E"),
    ("B", "D", "B", "A", "C", "F"),
    ("C", "A", "E", "B", "E"),
)

# Every profile is one completed record; every physical line has 4--8 groups.
RECORD_PROFILES = (
    (4, 4), (5, 5), (6, 5), (4, 4, 4),
    (5, 4, 5), (6, 5, 5), (7, 7), (8, 6),
)
PROFILE_WEIGHTS = (5, 8, 9, 10, 10, 5, 7, 5)
REGISTER_WEIGHTS = (42, 28, 18, 12)
HAND_WEIGHTS = (50, 30, 20)

SLOT_RESIDUES = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5}
STATE_TRANSITIONS = (
    (44, 19, 12, 8, 7, 6, 4),
    (16, 43, 15, 9, 7, 6, 4),
    (11, 18, 42, 12, 7, 6, 4),
    (8, 10, 17, 43, 11, 7, 4),
    (7, 8, 10, 18, 42, 10, 5),
    (6, 7, 8, 10, 18, 44, 7),
    (9, 7, 6, 7, 10, 17, 44),
)

FOSSILS = {
    0: "FC00", 4: "FC04", 7: "FC07", 11: "FC11", 14: "FC14",
    18: "FC18", 21: "FC21", 25: "FC25", 28: "FC28",
}

HAND_MAPS = (
    {},
    {"B": "D", "G": "J", "M": "P", "T": "V"},
    {"D": "F", "J": "K", "P": "R", "V": "B"},
)
REGISTER_INITIAL = ("B", "M", "T", "G")
REGISTER_FINAL = ("R", "D", "K", "V")


def _rng(seed: int) -> random.Random:
    raw = hashlib.sha256(f"GDT395:{WORLD_ID}:{seed}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))


def _weighted_index(rng: random.Random, weights: tuple[float, ...] | list[float]) -> int:
    total = float(sum(weights))
    point = rng.random() * total
    running = 0.0
    for index, weight in enumerate(weights):
        running += weight
        if point < running:
            return index
    return len(weights) - 1


def _choose_lineage(rng: random.Random, slot: str, state: int) -> int:
    """Zipf recurrence modulated by overlapping formal slot/state preferences."""
    residue = SLOT_RESIDUES[slot]
    weights = []
    for rank in range(len(BASE_FORMS)):
        weight = 1.0 / ((rank + 1) ** 1.08)
        if rank % 6 == residue:
            weight *= 4.6
        if rank % 7 == state:
            weight *= 2.2
        if (rank + state + residue) % 11 == 0:
            weight *= 1.7
        weights.append(weight)
    return _weighted_index(rng, weights)


def _advance_state(
    rng: random.Random, state: int, slot: str, register_index: int
) -> int:
    weights = list(STATE_TRANSITIONS[state])
    slot_pull = (SLOT_RESIDUES[slot] + register_index) % 7
    weights[slot_pull] += 13
    return _weighted_index(rng, weights)


def _render(
    lineage: int,
    register_index: int,
    hand_index: int,
    state: int,
    group_index: int,
    previous_final: str,
) -> str:
    """Apply semantically inert historical, register, hand, and context rules."""
    chars = list(BASE_FORMS[lineage])

    # Fixed graphic residues inherited by a minority of lineages.
    if lineage in FOSSILS:
        residue = ALPHABET[(lineage + 3) % len(ALPHABET)]
        chars.insert(1, residue)

    # Register realizations are deliberately overlapping and non-concatenative.
    if register_index == 0:
        if state in (2, 5) and len(chars) > 4:
            chars.pop(-2)
    elif register_index == 1:
        chars[0] = REGISTER_INITIAL[register_index]
        if lineage % 5 == 0:
            chars.append(REGISTER_FINAL[register_index])
    elif register_index == 2:
        if len(chars) > 4:
            chars.pop(1)
        chars.append(REGISTER_FINAL[register_index])
    else:
        chars = chars[1:] + chars[:1]
        chars[-1] = REGISTER_FINAL[register_index]

    # Repeated neighbouring strokes undergo clipping or echoing.
    if previous_final != "NONE" and chars[0] == previous_final and len(chars) > 4:
        chars.pop(0)
    elif previous_final != "NONE" and (state + lineage) % 9 == 0:
        chars.insert(0, previous_final)

    # A line-initial copy convention is physical, not functional.
    if group_index == 0 and state in (1, 4):
        chars[0] = REGISTER_INITIAL[register_index]

    chars = [HAND_MAPS[hand_index].get(char, char) for char in chars]

    # Bound visual length while retaining deterministic context sensitivity.
    if len(chars) < 4:
        chars.append(ALPHABET[(lineage + state) % len(ALPHABET)])
    if len(chars) > 7:
        chars = chars[:7]
    return "".join(chars)


def _position_bin(index: int, length: int) -> str:
    if index == 0:
        return "P0"
    if index == length - 1:
        return "P2"
    return "P1"


def _layout_role(line_index: int, group_index: int, line_length: int) -> str:
    if group_index == 0:
        return "LR0" if line_index == 0 else "LR1"
    if group_index == line_length - 1:
        return "LR3"
    return "LR2"


def _codebook() -> list[dict]:
    rows = []
    for index, form in enumerate(BASE_FORMS):
        fossil = FOSSILS.get(index, "NONE")
        rows.append({
            "lexical_id": "NONE",
            "semantic_entity_id": "NONE",
            "semantic_category": "NONE",
            "historical_stem_id": f"HS{index:02d}",
            "canonical_hidden_form": form,
            "final_realization_rules": (
                "INERT_FOSSIL_INSERTION|REGISTER_CONTEXT_RENDERING|"
                "HAND_SUBSTITUTION|NEIGHBOR_CLIPPING|LINE_INITIAL_COPY"
            ),
            "irregularity_flags": fossil,
        })
    return rows


def _genealogy() -> list[dict]:
    stages = (
        ("0", "G00", "inert_prototype_creation", "NONE", "HS00-HS31", "random graphic inventory", "FALSE", "Arbitrary forms; no denotation ever assigned."),
        ("1", "G01", "copy_variant_inheritance", "HS00-HS31", "V1_SET", "lineage-specific copying noise", "FALSE", "Variant families are historical graphics only."),
        ("2", "G02", "contextual_clipping", "V1_SET", "V2_SET", "dense adjacent strokes", "FALSE", "Clipping left inert traces in frequent forms."),
        ("3", "G03", "graphic_fusion", "V2_SET", "V3_SET|FC00-FC28", "selected inherited lineages", "FALSE", "Nine residues became fossilized components without meaning."),
        ("4", "G04", "frequency_leveling", "V3_SET", "V4_SET", "high recurrence during copying", "FALSE", "High-frequency shapes converged partially."),
        ("5", "G05", "hand_substitution", "V4_SET", "H0_SET|H1_SET|H2_SET", "copying hand", "TRUE", "Three live graphic substitution tables."),
        ("6", "G06", "register_divergence", "H0_SET|H1_SET|H2_SET", "R0_SET|R1_SET|R2_SET|R3_SET", "register and local context", "TRUE", "Four live rendering conventions; still no lexical meaning."),
    )
    return [
        {
            "stage": stage,
            "rule_id": rule_id,
            "process_type": process_type,
            "input_ids": inputs,
            "output_ids": outputs,
            "conditioning": conditioning,
            "currently_productive": productive,
            "notes": notes,
        }
        for stage, rule_id, process_type, inputs, outputs, conditioning, productive, notes in stages
    ]


def generate(seed: int, target_events: int = 8448) -> dict[str, list[dict]]:
    """Generate at least ``target_events``, stopping after a bounded record."""
    if not isinstance(seed, int):
        raise TypeError("seed must be an int")
    if not isinstance(target_events, int) or target_events < 1:
        raise ValueError("target_events must be a positive int")

    rng = _rng(seed)
    observations: list[dict] = []
    oracle: list[dict] = []

    page_index = 1
    paragraph_in_page = 1
    paragraph_global = 1
    records_in_paragraph = 0
    paragraphs_in_page = 1
    paragraph_record_target = rng.randint(3, 6)
    page_paragraph_target = rng.randint(2, 4)
    record_index = 0
    state = rng.randrange(7)
    previous_final = "NONE"

    while len(observations) < target_events:
        if record_index == 0:
            boundary_before = "PAGE"
        elif records_in_paragraph >= paragraph_record_target:
            records_in_paragraph = 0
            paragraph_record_target = rng.randint(3, 6)
            if paragraphs_in_page >= page_paragraph_target:
                page_index += 1
                paragraph_in_page = 1
                paragraphs_in_page = 1
                page_paragraph_target = rng.randint(2, 4)
                boundary_before = "PAGE"
            else:
                paragraph_in_page += 1
                paragraphs_in_page += 1
                boundary_before = "PARAGRAPH"
            paragraph_global += 1
        else:
            boundary_before = "RECORD"

        if observations:
            observations[-1]["separator_after"] = boundary_before

        record_index += 1
        records_in_paragraph += 1
        profile_index = _weighted_index(rng, PROFILE_WEIGHTS)
        profile = RECORD_PROFILES[profile_index]
        register_index = _weighted_index(rng, REGISTER_WEIGHTS)
        hand_index = _weighted_index(rng, HAND_WEIGHTS)
        construction_index = _weighted_index(rng, (17, 14, 12, 11, 10, 9, 8, 7))
        construction = CONSTRUCTIONS[construction_index]

        page_id = f"P{page_index:04d}"
        paragraph_id = f"Q{paragraph_global:05d}"
        record_id = f"R{record_index:06d}"
        record_length = sum(profile)
        record_start = len(observations)
        record_event_ids = [
            f"{WORLD_ID}-{seed}-E{record_start + offset:07d}"
            for offset in range(record_length)
        ]

        offset_in_record = 0
        previous_separator = boundary_before
        for line_index, line_length in enumerate(profile):
            line_id = f"L{record_index:06d}_{line_index + 1:02d}"
            for group_index in range(line_length):
                global_index = len(observations)
                event_id = record_event_ids[offset_in_record]
                slot = construction[offset_in_record % len(construction)]
                state_before = state
                lineage = _choose_lineage(rng, slot, state_before)
                state_after = _advance_state(rng, state_before, slot, register_index)
                visible = _render(
                    lineage,
                    register_index,
                    hand_index,
                    state_before,
                    group_index,
                    previous_final,
                )
                previous_final = visible[-1]

                is_record_last = offset_in_record == record_length - 1
                is_line_last = group_index == line_length - 1
                if is_record_last:
                    separator_after = "RECORD"
                    ambiguous = False
                elif is_line_last:
                    separator_after = "LINE"
                    ambiguous = rng.random() < 0.10
                else:
                    boundary_roll = rng.random()
                    if boundary_roll < 0.14:
                        separator_after = "JOIN"
                    elif boundary_roll < 0.22:
                        separator_after = "FIELD"
                    else:
                        separator_after = "SPACE"
                    ambiguous = rng.random() < 0.12

                observations.append({
                    "world_id": WORLD_ID,
                    "corpus_seed": seed,
                    "event_id": event_id,
                    "page_id": page_id,
                    "paragraph_id": paragraph_id,
                    "record_id": record_id,
                    "line_id": line_id,
                    "event_index": global_index,
                    "group_index": group_index,
                    "visible_group": visible,
                    "separator_before": previous_separator,
                    "separator_after": separator_after,
                    "register_id": REGISTERS[register_index],
                    "hand_id": HANDS[hand_index],
                    "layout_role": _layout_role(line_index, group_index, line_length),
                    "line_position_bin": _position_bin(group_index, line_length),
                    "record_position_bin": _position_bin(offset_in_record, record_length),
                    "ambiguous_boundary": ambiguous,
                })
                oracle.append({
                    "world_id": WORLD_ID,
                    "corpus_seed": seed,
                    "event_id": event_id,
                    "domain_id": "NONE",
                    "activity_id": "NONE",
                    "lexical_id": "NONE",
                    "semantic_entity_id": "NONE",
                    "semantic_category": "NONE",
                    "function_class": "NONE",
                    "relation_type": "NONE",
                    "relation_target_event_id": "NONE",
                    "state_before": f"PS{state_before}",
                    "state_after": f"PS{state_after}",
                    "historical_stem_id": f"HS{lineage:02d}",
                    "current_morpheme_ids": "NONE",
                    "fossilized_component_ids": FOSSILS.get(lineage, "NONE"),
                    "construction_id": f"C{construction_index}",
                    "scope_start_event_id": record_event_ids[0],
                    "scope_end_event_id": record_event_ids[-1],
                    "record_schema_id": f"RS{profile_index}",
                    "register_realization_id": f"RR{register_index}H{hand_index}",
                    "productive_morphology": "FALSE",
                    "current_component_semantics": "NONE",
                    "genealogy_stage": "G06",
                })

                state = state_after
                previous_separator = separator_after
                offset_in_record += 1

            # Physical line reset disrupts only renderer context.
            previous_final = "NONE"

    return {
        "observations": observations,
        "oracle": oracle,
        "codebook": _codebook(),
        "genealogy": _genealogy(),
    }
