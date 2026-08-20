#!/usr/bin/env python3
"""Deterministic generator for W05, a mnemonic calendrical ritual legacy."""

from __future__ import annotations

import hashlib
import random
from typing import Any


WORLD_META = {
    "world_id": "W05",
    "title": "Mnemonic Ritual Legacy",
    "broad_family": "MNEMONIC_RITUAL_LEGACY",
    "practical_domain": "conservative calendrical ritual procedure",
    "semantics_light": False,
    "organic_evolution": True,
    "clean_engineered_control": False,
    "adversarial_pair_id": "NONE",
    "carrier_profile": "CARRIER_MNEMONIC",
    "alphabet": ["ϙ", "ƛ", "ȝ", "ʒ", "ŋ", "š", "ṭ", "ḷ", "ṛ", "ḳ", "ḿ", "·", "ː", "ʔ"],
    "registers": ["r0", "r1", "r2"],
    "hands": ["h0", "h1", "h2"],
    "evolution_processes": [
        "frequency_shortening", "analogy", "merger", "split", "semantic_bleaching",
        "fossilization", "suppletion", "polyfunctionality", "register_divergence",
        "hand_conditioned_ligation",
    ],
    "generator_schema": "GDT395_WORLD_GENERATOR_V1",
}


# key: lexical id, entity, category, historical stem, canonical form, base cue,
# irregularity flags.  Canonical forms are hidden reconstructions; base cues are
# final conservative written realizations.
_RAW_LEXICON = {
    "CAL_NEW": ("LX001", "new_cycle", "CALENDAR_PHASE", "HS01", "kawanu", "ϙḷš", "FOSSIL_CLASSIFIER|REGISTER_SPLIT"),
    "CAL_WAX": ("LX002", "waxing_phase", "CALENDAR_PHASE", "HS02", "miretu", "ḿṛṭ", "FREQUENCY_SHORTENING"),
    "CAL_FULL": ("LX003", "full_phase", "CALENDAR_PHASE", "HS03", "palaku", "ʒḳḷ", "SUPPLETIVE_FORMAL"),
    "CAL_WANE": ("LX004", "waning_phase", "CALENDAR_PHASE", "HS04", "sorenu", "šṛŋ", "ANALOGICAL_RESHAPING"),
    "SEASON_A": ("LX005", "season_one", "CALENDAR_UNIT", "HS05", "taluma", "ṭḷḿ", "FOSSIL_INITIAL"),
    "SEASON_B": ("LX006", "season_two", "CALENDAR_UNIT", "HS06", "kerima", "ḳṛḿ", "FOSSIL_INITIAL"),
    "SEASON_C": ("LX007", "season_three", "CALENDAR_UNIT", "HS07", "wonasa", "ŋšʒ", "FOSSIL_INITIAL"),
    "SEASON_D": ("LX008", "season_four", "CALENDAR_UNIT", "HS08", "lirata", "ḷṛṭ", "FOSSIL_INITIAL"),
    "SEASON_E": ("LX009", "season_five", "CALENDAR_UNIT", "HS09", "sumaka", "šḿḳ", "FOSSIL_INITIAL"),
    "SEASON_F": ("LX010", "season_six", "CALENDAR_UNIT", "HS10", "parina", "ʒṛŋ", "FOSSIL_INITIAL"),
    "NUM_ONE": ("LX011", "count_one", "NUMBER", "HS11", "ita", "ṭ", "CONTEXTUAL_SUPPLETION"),
    "NUM_TWO": ("LX012", "count_two", "NUMBER", "HS12", "naku", "ŋḳ", "ANALOGICAL_SERIES"),
    "NUM_THREE": ("LX013", "count_three", "NUMBER", "HS13", "sami", "šḿ", "ANALOGICAL_SERIES"),
    "NUM_SEVEN": ("LX014", "count_seven", "NUMBER", "HS14", "toripe", "ȝḷ", "SUPPLETION"),
    "NUM_NINE": ("LX015", "count_nine", "NUMBER", "HS15", "wakasu", "ϙš", "SUPPLETION"),
    "RITE_DAILY": ("LX016", "lamp_observance", "RITUAL_PROGRAM", "HS16", "melakaru", "ḿḷϙṛ", "MNEMONIC_TRUNCATION"),
    "RITE_FULL": ("LX017", "full_phase_offering", "RITUAL_PROGRAM", "HS17", "pasunari", "ʒšŋṛ", "REGISTER_SPLIT"),
    "RITE_RENEW": ("LX018", "season_renewal", "RITUAL_PROGRAM", "HS18", "ketaluma", "ḳṭḷḿ", "FOSSILIZED_COMPOUND"),
    "RITE_MEMORY": ("LX019", "lineage_memorial", "RITUAL_PROGRAM", "HS19", "norasati", "ŋṛšṭ", "ANALOGICAL_EXTENSION"),
    "RITE_REPAIR": ("LX020", "calendar_repair", "RITUAL_PROGRAM", "HS20", "uyekema", "ʔȝḳ", "SUPPLETIVE|SCHOOL_VARIANT"),
    "GATE_DAWN": ("LX021", "dawn_admission", "CONDITION", "HS21", "harime", "ȝṛḿ", "BLEACHED_GATE"),
    "GATE_DARK": ("LX022", "darkness_admission", "CONDITION", "HS22", "sumire", "šḿṛ", "BLEACHED_GATE"),
    "GATE_RAIN": ("LX023", "rain_exception", "CONDITION", "HS23", "waloke", "ϙḷḳ", "REGISTER_MERGER"),
    "SCOPE_CLOSE": ("LX024", "condition_end", "SCOPE_OPERATOR", "HS24", "kati", "ḳṭ", "BLEACHED|CLOSURE_MERGER"),
    "ACT_CLEAN": ("LX025", "cleanse", "RITUAL_ACTION", "HS25", "sirama", "šṛḿ", "FREQUENCY_SHORTENING"),
    "ACT_KINDLE": ("LX026", "kindle", "RITUAL_ACTION", "HS26", "pokare", "ʒḳṛ", "HAND_LIGATURE"),
    "ACT_POUR": ("LX027", "pour", "RITUAL_ACTION", "HS27", "nalume", "ŋḷḿ", "OBJECT_CONDITIONED_SPLIT"),
    "ACT_BIND": ("LX028", "bind", "RITUAL_ACTION", "HS28", "tikara", "ṭḳṛ", "FOSSIL_FINAL"),
    "ACT_RECITE": ("LX029", "recite", "RITUAL_ACTION", "HS29", "masore", "ḿšṛ", "REGISTER_SHORTENING"),
    "ACT_CARRY": ("LX030", "carry", "RITUAL_ACTION", "HS30", "winate", "ϙŋṭ", "ANALOGICAL_FRAME"),
    "ACT_MARK": ("LX031", "mark_calendar", "RITUAL_ACTION", "HS31", "keratu", "ḳṛṭ", "POLYFUNCTIONAL_MARK"),
    "ACT_FAST": ("LX032", "withhold_food", "RITUAL_ACTION", "HS32", "salume", "šḷḿ", "NEGATIVE_FRAME"),
    "ACT_RELEASE": ("LX033", "release", "RITUAL_ACTION", "HS33", "parike", "ʒṛḳ", "CLOSURE_ANALOGY"),
    "ACT_TURN": ("LX034", "turn_object", "RITUAL_ACTION", "HS34", "tiranu", "ṭṛŋ", "POLYFUNCTIONAL_WITH_REFERENCE"),
    "OBJ_WATER": ("LX035", "lustral_water", "RITUAL_MATERIAL", "HS35", "wanume", "ϙŋḿ", "POUR_FUSION"),
    "OBJ_OIL": ("LX036", "lamp_oil", "RITUAL_MATERIAL", "HS36", "molike", "ḿḷḳ", "POUR_FUSION"),
    "OBJ_GRAIN": ("LX037", "grain_portion", "RITUAL_MATERIAL", "HS37", "seraku", "šṛḳ", "CLASSIFIER_FOSSIL"),
    "OBJ_HERB": ("LX038", "bitter_herb", "RITUAL_MATERIAL", "HS38", "yamori", "ʔḿṛ", "SCHOOL_REANALYSIS"),
    "OBJ_THREAD": ("LX039", "votive_thread", "RITUAL_MATERIAL", "HS39", "tilane", "ṭḷŋ", "BINDING_FUSION"),
    "OBJ_LAMP": ("LX040", "ritual_lamp", "RITUAL_IMPLEMENT", "HS40", "peluma", "ʒḷḿ", "HIGH_FREQUENCY_SHORTENING"),
    "OBJ_BELL": ("LX041", "ritual_bell", "RITUAL_IMPLEMENT", "HS41", "konari", "ḳŋṛ", "HAND_VARIANT"),
    "OBJ_CUP": ("LX042", "offering_cup", "RITUAL_IMPLEMENT", "HS42", "sunake", "šŋḳ", "CLASSIFIER_FOSSIL"),
    "OBJ_SEAL": ("LX043", "calendar_seal", "RITUAL_IMPLEMENT", "HS43", "turame", "ṭṛḿ", "POLYFUNCTIONAL_MARK"),
    "OBJ_ASH": ("LX044", "hearth_ash", "RITUAL_MATERIAL", "HS44", "porisa", "ʒṛš", "FORMAL_ARCHAISM"),
    "AG_PRIEST": ("LX045", "senior_officiant", "RITUAL_AGENT", "HS45", "kalume", "ḳḷḿ", "TITLE_SHORTENING"),
    "AG_KEEPER": ("LX046", "calendar_keeper", "RITUAL_AGENT", "HS46", "warita", "ϙṛṭ", "TITLE_SHORTENING"),
    "AG_NOVICE": ("LX047", "junior_assistant", "RITUAL_AGENT", "HS47", "nasime", "ŋšḿ", "SCHOOL_EXPANSION"),
    "DIR_EAST": ("LX048", "east_station", "DIRECTION", "HS48", "haraku", "ȝṛḳ", "GATE_ASSOCIATION"),
    "DIR_WEST": ("LX049", "west_station", "DIRECTION", "HS49", "sumatu", "šḿṭ", "GATE_ASSOCIATION"),
    "OP_THEN": ("LX050", "ordered_next", "SEQUENCE_OPERATOR", "HS50", "lati", "ḷṭ", "MERGED_IN_COMPACT"),
    "OP_REPEAT": ("LX051", "repeat_instruction", "RECURRENCE_OPERATOR", "HS51", "tiran", "ṭṛŋ", "BLEACHED_TURN|MERGED_IN_COMPACT"),
    "OP_REF": ("LX052", "prior_record_reference", "REFERENCE_OPERATOR", "HS34", "tiranu", "ṭṛŋː", "LEXICAL_SPLIT|BLEACHED_TURN"),
    "OP_ALT": ("LX053", "licensed_alternative", "ALTERNATIVE_OPERATOR", "HS53", "uyati", "ʔȝṭ", "SCOPE_BLEACHING"),
    "OP_UNTIL": ("LX054", "termination_gate", "SCOPE_OPERATOR", "HS54", "monake", "ḿŋḳ", "BLEACHED_TEMPORAL"),
    "OP_NEG": ("LX055", "withhold_operator", "POLARITY_OPERATOR", "HS55", "asala", "ʔšḷ", "FUSED_WITH_FAST"),
    "CLOSE_DONE": ("LX056", "procedure_complete", "CLOSURE", "HS56", "katume", "ḳṭḿ", "SUPPLETIVE_COMPACT|CLOSURE_MERGER"),
    "MEM_LINE": ("LX057", "remembered_lineage", "RECITED_TEXT", "HS57", "norayame", "ŋṛʔḿ", "MNEMONIC_TRUNCATION"),
    "TEXT_HYMN": ("LX058", "phase_hymn", "RECITED_TEXT", "HS58", "masulore", "ḿšḷṛ", "RECITATION_FUSION"),
}

LEXICON = {
    key: {
        "lexical_id": row[0], "semantic_entity_id": row[1], "semantic_category": row[2],
        "historical_stem_id": row[3], "canonical_hidden_form": row[4], "base": row[5],
        "flags": row[6],
    }
    for key, row in _RAW_LEXICON.items()
}


GENEALOGY = [
    {"stage": "1", "rule_id": "EV01", "process_type": "lexical_cue_adoption", "input_ids": "HS01|HS58", "output_ids": "LX001|LX058", "conditioning": "spoken procedural items selected as written mnemonic cues", "currently_productive": "NO", "notes": "Full cues initially preserve most stem material."},
    {"stage": "2", "rule_id": "EV02", "process_type": "frequency_shortening", "input_ids": "HS01|HS16|HS24|HS25|HS40|HS50|HS56", "output_ids": "LX001|LX016|LX024|LX025|LX040|LX050|LX056", "conditioning": "high token frequency and predictable record position", "currently_productive": "LIMITED", "notes": "Different words lose different material; no uniform clipping edge."},
    {"stage": "3", "rule_id": "EV03", "process_type": "analogy", "input_ids": "LX012|LX013|LX028|LX030|LX033", "output_ids": "M_SERIES|M_ACTION_FRAME", "conditioning": "copyists extend common number and action frames", "currently_productive": "YES", "notes": "Rare numerals and common closures remain exceptions."},
    {"stage": "4", "rule_id": "EV04", "process_type": "merger", "input_ids": "LX050|LX051", "output_ids": "FORM_COMPACT_ƛ", "conditioning": "register r1 outside record onset", "currently_productive": "NO", "notes": "Sequence and recurrence remain distinct in r0."},
    {"stage": "4", "rule_id": "EV05", "process_type": "split", "input_ids": "LX027", "output_ids": "FORM_POUR_WATER|FORM_POUR_OIL|FORM_POUR_DRY", "conditioning": "following material class and construction", "currently_productive": "NO", "notes": "Inherited object-conditioned allomorphy masks one historical action."},
    {"stage": "5", "rule_id": "EV06", "process_type": "semantic_bleaching", "input_ids": "HS34|HS24|HS54", "output_ids": "LX051|LX052|LX024|LX054", "conditioning": "recurrence, reference, and gated procedural frames", "currently_productive": "LIMITED", "notes": "Motion and completion meanings survive in other constructions."},
    {"stage": "5", "rule_id": "EV07", "process_type": "polyfunctionality", "input_ids": "LX034|LX031|LX056", "output_ids": "FC_ACTION|FC_REFERENCE|FC_CALENDAR_MARK|FC_CLOSURE", "conditioning": "construction and record schema", "currently_productive": "YES", "notes": "Function is not recoverable from form alone."},
    {"stage": "6", "rule_id": "EV08", "process_type": "fossilization", "input_ids": "M_OLD_CYCLE|M_OLD_PORTION|M_OLD_BOUNDARY", "output_ids": "LX001|LX018|LX037|LX042", "conditioning": "lexicalized calendar and offering cues", "currently_productive": "NO", "notes": "Fossil pieces resemble later live class marks."},
    {"stage": "7", "rule_id": "EV09", "process_type": "suppletion", "input_ids": "LX011|LX014|LX015|LX020|LX056", "output_ids": "FORM_EXCEPTION_SET", "conditioning": "rare counts, repair schema, and compact closure", "currently_productive": "NO", "notes": "Multiple unrelated sources remain in the final paradigm."},
    {"stage": "8", "rule_id": "EV10", "process_type": "register_divergence", "input_ids": "LX001|LX058", "output_ids": "R0_FORMS|R1_FORMS|R2_FORMS", "conditioning": "house-book, officiant checklist, and teaching transmission", "currently_productive": "YES", "notes": "Registers differ by replacement, expansion, and boundary habits."},
    {"stage": "8", "rule_id": "EV11", "process_type": "scribal_ligation", "input_ids": "R0_FORMS|R1_FORMS|R2_FORMS", "output_ids": "H0_FORMS|H1_FORMS|H2_FORMS", "conditioning": "hand, line position, and neighboring cue", "currently_productive": "YES", "notes": "Ligature marks can coincide with but do not reliably encode syntactic dependency."},
]


def _stable_id(prefix: str, *parts: object) -> str:
    raw = "\x1f".join(map(str, parts)).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(raw).hexdigest()[:12]}"


def _rng(seed: int) -> random.Random:
    raw = hashlib.sha256(f"GDT395:W05:{seed}".encode("utf-8")).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))


def _pipe(values: list[str]) -> str:
    vals = sorted({v for v in values if v and v != "NONE"})
    return "|".join(vals) if vals else "NONE"


def _state(calendar: dict[str, int], ritual: dict[str, str]) -> str:
    return ";".join([
        f"season={calendar['season']}", f"day={calendar['day']}",
        f"phase={calendar['phase']}", f"prepared={ritual['prepared']}",
        f"gate={ritual['gate']}", f"flame={ritual['flame']}",
        f"offering={ritual['offering']}", f"closed={ritual['closed']}",
    ])


def _make_plan(schema: str, calendar: dict[str, int], rng: random.Random,
               previous: dict[str, str]) -> list[dict[str, Any]]:
    ritual = {"prepared": "no", "gate": "shut", "flame": "out", "offering": "none", "closed": "no"}
    plan: list[dict[str, Any]] = []
    scope_stack: list[int] = []

    def add(key: str, function: str, activity: str, field: int,
            relation: str = "NONE", target: Any = None,
            effect: tuple[str, str] | None = None,
            construction: str = "C_FREE", morphemes: list[str] | None = None,
            fossils: list[str] | None = None, productive: str = "NO",
            component_semantics: list[str] | None = None) -> int:
        before = _state(calendar, ritual)
        if effect is not None:
            ritual[effect[0]] = effect[1]
        after = _state(calendar, ritual)
        plan.append({
            "key": key, "function": function, "activity": activity, "field": field,
            "relation": relation, "target": target, "state_before": before,
            "state_after": after, "construction": construction,
            "morphemes": morphemes or [f"M_{LEXICON[key]['historical_stem_id']}"],
            "fossils": fossils or [], "productive": productive,
            "components": component_semantics or [LEXICON[key]["semantic_entity_id"]],
            "scope_start": None, "scope_end": None,
        })
        return len(plan) - 1

    phase_keys = ["CAL_NEW", "CAL_WAX", "CAL_FULL", "CAL_WANE"]
    season_keys = ["SEASON_A", "SEASON_B", "SEASON_C", "SEASON_D", "SEASON_E", "SEASON_F"]
    phase = phase_keys[calendar["phase"]]
    add(phase, "CALENDAR_ANCHOR", "ANCHOR_CYCLE", 0, construction="C_CALENDAR_HEADER",
        morphemes=[f"M_{LEXICON[phase]['historical_stem_id']}", "M_PHASE_FRAME"],
        fossils=["M_OLD_CYCLE"] if phase == "CAL_NEW" else [], productive="LIMITED")
    add(season_keys[calendar["season"]], "CALENDAR_ANCHOR", "ANCHOR_SEASON", 0,
        relation="COANCHOR", target=0, construction="C_CALENDAR_HEADER",
        morphemes=[f"M_{LEXICON[season_keys[calendar['season']]]['historical_stem_id']}", "M_SEASON_FRAME"], productive="YES")

    rite_key = {
        "RS_DAILY": "RITE_DAILY", "RS_FULL": "RITE_FULL", "RS_RENEW": "RITE_RENEW",
        "RS_MEMORY": "RITE_MEMORY", "RS_REPAIR": "RITE_REPAIR",
    }[schema]
    rite_idx = add(rite_key, "PROGRAM_LABEL", "DECLARE_RITE", 0, relation="SPECIFIES", target=0,
                   construction="C_PROGRAM_HEADER", fossils=["M_OLD_BOUNDARY"] if rite_key == "RITE_RENEW" else [])

    if schema in {"RS_MEMORY", "RS_REPAIR"} and previous.get("rite"):
        add("OP_REF", "REFERENCE_OPERATOR", "RECALL_PRIOR_PROGRAM", 1,
            relation="REFERENCE", target=previous["rite"], construction="C_CROSS_RECORD_REFERENCE",
            morphemes=["M_HS34", "M_REF_BLEACHED"], productive="LIMITED",
            component_semantics=["prior_record_reference"])

    gate_key = "GATE_DAWN" if schema in {"RS_DAILY", "RS_RENEW"} else ("GATE_DARK" if schema in {"RS_FULL", "RS_MEMORY"} else "GATE_RAIN")
    gate_idx = add(gate_key, "SCOPE_GATE", "TEST_ADMISSION", 1, relation="OPENS_SCOPE",
                   construction="C_CONDITIONAL_BLOCK", effect=("gate", "open"),
                   morphemes=[f"M_{LEXICON[gate_key]['historical_stem_id']}", "M_GATE"], productive="YES")
    scope_stack.append(gate_idx)

    clean_idx = add("ACT_CLEAN", "ACTION", "PREPARE_SPACE", 2, relation="STEP_OF", target=rite_idx,
                    effect=("prepared", "yes"), construction="C_PREPARATION")
    material = "OBJ_WATER" if schema != "RS_MEMORY" else "OBJ_ASH"
    add(material, "PATIENT", "SUPPLY_PREPARATION_MATERIAL", 2, relation="ARGUMENT_OF", target=clean_idx,
        construction="C_PREPARATION", fossils=["M_OLD_PORTION"] if material == "OBJ_ASH" else [])
    agent = "AG_KEEPER" if schema in {"RS_RENEW", "RS_REPAIR"} else ("AG_NOVICE" if schema == "RS_MEMORY" else "AG_PRIEST")
    add(agent, "AGENT", "ASSIGN_OFFICIANT", 2, relation="ARGUMENT_OF", target=clean_idx, construction="C_AGENT_ACTION")

    add("OP_THEN", "SEQUENCE_OPERATOR", "ADVANCE_PHASE", 3, relation="SEQUENCE", target=clean_idx,
        construction="C_ORDERED_CHAIN", morphemes=["M_HS50", "M_CHAIN"], productive="YES")

    if schema in {"RS_DAILY", "RS_FULL", "RS_RENEW"}:
        kindle_idx = add("ACT_KINDLE", "ACTION", "KINDLE_LIGHT", 3, relation="STEP_OF", target=rite_idx,
                          effect=("flame", "lit"), construction="C_LIGHTING")
        add("OBJ_LAMP", "PATIENT", "LIGHT_IMPLEMENT", 3, relation="ARGUMENT_OF", target=kindle_idx,
            construction="C_LIGHTING")
    else:
        mark_idx = add("ACT_MARK", "ACTION", "MARK_RECKONING", 3, relation="STEP_OF", target=rite_idx,
                       construction="C_MARKING")
        add("OBJ_SEAL", "PATIENT", "MARK_IMPLEMENT", 3, relation="ARGUMENT_OF", target=mark_idx,
            construction="C_MARKING")

    add("OP_THEN", "SEQUENCE_OPERATOR", "ADVANCE_PHASE", 4, relation="SEQUENCE", target=len(plan) - 2,
        construction="C_ORDERED_CHAIN", morphemes=["M_HS50", "M_CHAIN"], productive="YES")

    if schema == "RS_DAILY":
        act_idx = add("ACT_POUR", "ACTION", "POUR_OIL", 4, relation="STEP_OF", target=rite_idx,
                      effect=("offering", "oil"), construction="C_POUR_OIL",
                      morphemes=["M_HS27", "M_OIL_ALLOMORPH"], productive="NO")
        add("OBJ_OIL", "PATIENT", "OIL_PORTION", 4, relation="ARGUMENT_OF", target=act_idx,
            construction="C_POUR_OIL")
    elif schema == "RS_FULL":
        act_idx = add("ACT_POUR", "ACTION", "POUR_GRAIN", 4, relation="STEP_OF", target=rite_idx,
                      effect=("offering", "grain"), construction="C_POUR_DRY",
                      morphemes=["M_HS27", "M_DRY_ALLOMORPH"], productive="NO")
        add("OBJ_GRAIN", "PATIENT", "GRAIN_PORTION", 4, relation="ARGUMENT_OF", target=act_idx,
            construction="C_POUR_DRY", fossils=["M_OLD_PORTION"])
    elif schema == "RS_RENEW":
        act_idx = add("ACT_BIND", "ACTION", "BIND_RENEWAL", 4, relation="STEP_OF", target=rite_idx,
                      effect=("offering", "thread"), construction="C_BINDING")
        add("OBJ_THREAD", "PATIENT", "VOTIVE_THREAD", 4, relation="ARGUMENT_OF", target=act_idx,
            construction="C_BINDING", fossils=["M_OLD_BOUNDARY"])
    elif schema == "RS_MEMORY":
        act_idx = add("ACT_RECITE", "ACTION", "RECITE_LINEAGE", 4, relation="STEP_OF", target=rite_idx,
                      effect=("offering", "recitation"), construction="C_MEMORIAL_RECITATION")
        add("MEM_LINE", "CONTENT", "LINEAGE_TEXT", 4, relation="ARGUMENT_OF", target=act_idx,
            construction="C_MEMORIAL_RECITATION")
    else:
        act_idx = add("ACT_TURN", "ACTION", "REVERSE_CALENDAR_MARK", 4, relation="STEP_OF", target=rite_idx,
                      effect=("offering", "repair"), construction="C_REPAIR_REVERSAL",
                      morphemes=["M_HS34", "M_ACTION_SURVIVAL"], productive="NO")
        add("OBJ_SEAL", "PATIENT", "CALENDAR_SEAL", 4, relation="ARGUMENT_OF", target=act_idx,
            construction="C_REPAIR_REVERSAL")

    # A licensed alternative is executable only inside the admission scope.
    alt_idx = add("OP_ALT", "ALTERNATIVE_OPERATOR", "LICENSE_SUBSTITUTE", 5,
                  relation="ALTERNATIVE_TO", target=act_idx, construction="C_ALTERNATIVE_BRANCH",
                  morphemes=["M_HS53", "M_ALT"], productive="YES")
    if schema in {"RS_DAILY", "RS_FULL"}:
        substitute = "OBJ_HERB" if schema == "RS_DAILY" else "OBJ_CUP"
        add(substitute, "ALTERNATIVE_PATIENT", "SUBSTITUTE_MATERIAL", 5,
            relation="GOVERNED_BY", target=alt_idx, construction="C_ALTERNATIVE_BRANCH")
    else:
        substitute_action = "ACT_CARRY" if schema == "RS_RENEW" else ("ACT_FAST" if schema == "RS_MEMORY" else "ACT_RELEASE")
        sub_idx = add(substitute_action, "ALTERNATIVE_ACTION", "SUBSTITUTE_PROCEDURE", 5,
                      relation="ALTERNATIVE_TO", target=act_idx, construction="C_ALTERNATIVE_BRANCH")
        if substitute_action == "ACT_FAST":
            add("OP_NEG", "POLARITY_OPERATOR", "WITHHOLD", 5, relation="GOVERNS", target=sub_idx,
                construction="C_NEGATIVE_FAST", morphemes=["M_HS55", "M_NEG_FRAME"], productive="YES")

    close_scope_idx = add("SCOPE_CLOSE", "SCOPE_CLOSER", "END_ADMISSION_BLOCK", 6,
                          relation="CLOSES_SCOPE", target=gate_idx, construction="C_CONDITIONAL_BLOCK",
                          effect=("gate", "shut"), morphemes=["M_HS24", "M_CLOSE_BLEACHED"], productive="LIMITED")
    opener = scope_stack.pop()
    plan[opener]["target"] = close_scope_idx
    for pos in range(opener, close_scope_idx + 1):
        plan[pos]["scope_start"] = opener
        plan[pos]["scope_end"] = close_scope_idx

    repeat_target: Any = previous.get("offering") or act_idx
    add("OP_REPEAT", "RECURRENCE_OPERATOR", "SCHEDULE_RECURRENCE", 7,
        relation="RECURRENCE", target=repeat_target, construction="C_COUNTED_RECURRENCE",
        morphemes=["M_HS34", "M_REPEAT_BLEACHED"], productive="LIMITED",
        component_semantics=["repeat_instruction"])
    count_key = "NUM_NINE" if schema == "RS_MEMORY" else ("NUM_SEVEN" if schema == "RS_RENEW" else rng.choice(["NUM_ONE", "NUM_TWO", "NUM_THREE"]))
    add(count_key, "RECURRENCE_COUNT", "SET_INTERVAL", 7, relation="QUANTIFIES", target=len(plan) - 1,
        construction="C_COUNTED_RECURRENCE", morphemes=[f"M_{LEXICON[count_key]['historical_stem_id']}", "M_COUNT_FRAME"],
        productive="LIMITED")

    if schema in {"RS_FULL", "RS_MEMORY"}:
        rec_idx = add("ACT_RECITE", "ACTION", "RECITE_PHASE_TEXT", 8, relation="STEP_OF", target=rite_idx,
                      construction="C_FINAL_RECITATION")
        add("TEXT_HYMN", "CONTENT", "PHASE_TEXT", 8, relation="ARGUMENT_OF", target=rec_idx,
            construction="C_FINAL_RECITATION")
    if schema == "RS_REPAIR":
        release_idx = add("ACT_RELEASE", "ACTION", "RELEASE_RECKONING", 8, relation="STEP_OF", target=rite_idx,
                          construction="C_REPAIR_RELEASE")
        add("AG_KEEPER", "AGENT", "VERIFY_REPAIR", 8, relation="ARGUMENT_OF", target=release_idx,
            construction="C_REPAIR_RELEASE")

    add("CLOSE_DONE", "CLOSURE", "COMPLETE_PROGRAM", 9, relation="CLOSES", target=rite_idx,
        effect=("closed", "yes"), construction="C_RECORD_CLOSURE",
        morphemes=["M_HS56", "M_COMPLETIVE"], productive="NO")
    return plan


def _schema_for(record_no: int, calendar: dict[str, int], rng: random.Random) -> str:
    if calendar["day"] == 0:
        return "RS_RENEW"
    if calendar["day"] in {14, 15}:
        return "RS_FULL"
    if record_no and record_no % 9 == 0:
        return "RS_MEMORY"
    if (record_no + calendar["season"]) % 23 == 17 or rng.random() < 0.035:
        return "RS_REPAIR"
    return "RS_DAILY"


def _register(record_no: int) -> str:
    if record_no % 12 == 11:
        return "r2"
    if record_no % 5 == 4 or record_no % 5 == 3:
        return "r1"
    return "r0"


def _hand(record_no: int) -> str:
    if record_no % 17 == 16:
        return "h2"
    if record_no % 7 == 6 or record_no % 7 == 5:
        return "h1"
    return "h0"


_R1_REPLACE = {
    "CAL_NEW": "ϙš", "CAL_FULL": "ʒḷ", "RITE_DAILY": "ḿϙ", "RITE_FULL": "ʒŋ",
    "RITE_RENEW": "ḳḿ", "RITE_MEMORY": "ŋṭ", "RITE_REPAIR": "ʔḳ", "GATE_DAWN": "ȝḿ",
    "GATE_DARK": "šṛ", "GATE_RAIN": "ϙḳ", "SCOPE_CLOSE": "ḳ", "ACT_CLEAN": "šḿ",
    "ACT_KINDLE": "ʒṛ", "ACT_RECITE": "ḿṛ", "OBJ_LAMP": "ʒḿ", "AG_PRIEST": "ḳḿ",
    "AG_KEEPER": "ϙṭ", "OP_THEN": "ƛ", "OP_REPEAT": "ƛ", "OP_REF": "ṭŋ",
    "OP_ALT": "ʔṭ", "CLOSE_DONE": "ȝ", "TEXT_HYMN": "ḿḷ",
}

_R2_REPLACE = {
    "CAL_NEW": "ϙ·ḷš", "RITE_REPAIR": "ʔȝ·ḳ", "AG_NOVICE": "ŋš·ḿ",
    "OP_THEN": "ḷ·ṭ", "OP_REPEAT": "ṭ·ṛŋ", "OP_REF": "ṭ·ṛŋː",
    "SCOPE_CLOSE": "ḳ·ṭ", "CLOSE_DONE": "ḳ·ṭḿ", "OBJ_HERB": "ʔ·ḿṛ",
}


def _render(key: str, register: str, hand: str, construction: str,
            line_pos: str, next_key: str | None, rng: random.Random) -> str:
    form = LEXICON[key]["base"]
    if register == "r1":
        form = _R1_REPLACE.get(key, form[:-1] if len(form) >= 3 and key in {"ACT_BIND", "ACT_CARRY", "ACT_RELEASE", "OBJ_WATER", "OBJ_GRAIN", "OBJ_THREAD"} else form)
    elif register == "r2":
        form = _R2_REPLACE.get(key, form + "·" if key in {"RITE_RENEW", "RITE_MEMORY", "GATE_DAWN", "GATE_DARK"} else form)

    # The pour descendant is suppletive by construction, not transparently compositional.
    if key == "ACT_POUR":
        form = {"C_POUR_OIL": "ḿȝ", "C_POUR_DRY": "šʔḳ", "C_POUR_WATER": "ŋḷḿ"}.get(construction, "ŋḷḿ")
        if register == "r2":
            form += "·"
    if key == "NUM_ONE" and construction == "C_COUNTED_RECURRENCE":
        form = "ʔ" if register == "r0" else "ṭ"
    if key == "CLOSE_DONE" and register == "r1":
        form = "ȝ"  # unrelated checklist suppletion
    if key == "ACT_TURN" and construction == "C_REPAIR_REVERSAL":
        form = "ṭṛʔ"

    if hand == "h1":
        form = form.replace("ṛŋ", "ȝ").replace("ḷḿ", "ƛ")
        if line_pos == "END" and not form.endswith("ː"):
            form += "ː"
    elif hand == "h2":
        form = form.replace("šḿ", "ʒḿ").replace("ḳṭ", "ϙṭ")
        if line_pos == "START" and len(form) > 1 and rng.random() < 0.55:
            form = "·" + form

    # A final boundary mark is partly graphic and partly inherited.
    if line_pos == "END" and key not in {"CLOSE_DONE", "SCOPE_CLOSE"} and rng.random() < 0.22:
        form += "·"
    if next_key == "CLOSE_DONE" and register == "r0" and key == "OP_REPEAT":
        form = "ṭṛ"  # fossilized pre-closure truncation
    return form


def _codebook() -> list[dict[str, str]]:
    rows = []
    for key in sorted(LEXICON, key=lambda k: LEXICON[k]["lexical_id"]):
        item = LEXICON[key]
        rules = ["r0 conservative whole cue", "r1 lexical replacement or irregular shortening", "r2 pedagogical expansion"]
        if key == "ACT_POUR":
            rules.append("object-conditioned whole-form split")
        if key in {"OP_THEN", "OP_REPEAT"}:
            rules.append("r1 merger as ƛ")
        if key in {"OP_REPEAT", "OP_REF", "ACT_TURN"}:
            rules.append("polyfunctional descendants of HS34")
        rows.append({
            "lexical_id": item["lexical_id"],
            "semantic_entity_id": item["semantic_entity_id"],
            "semantic_category": item["semantic_category"],
            "historical_stem_id": item["historical_stem_id"],
            "canonical_hidden_form": item["canonical_hidden_form"],
            "final_realization_rules": "; ".join(rules),
            "irregularity_flags": item["flags"],
        })
    return rows


def generate(seed: int, target_events: int = 8448) -> dict[str, list[dict]]:
    """Generate a complete-record corpus reaching at least ``target_events``."""
    if not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    if not isinstance(target_events, int) or target_events < 1:
        raise ValueError("target_events must be a positive integer")

    rng = _rng(seed)
    observations: list[dict] = []
    oracle: list[dict] = []
    previous: dict[str, str] = {}
    calendar = {"season": rng.randrange(6), "day": rng.randrange(30), "phase": 0}
    record_no = 0

    while len(observations) < target_events:
        calendar["phase"] = 0 if calendar["day"] < 3 else (1 if calendar["day"] < 14 else (2 if calendar["day"] < 18 else 3))
        schema = _schema_for(record_no, calendar, rng)
        plan = _make_plan(schema, calendar, rng, previous)
        register = _register(record_no)
        hand = _hand(record_no)
        page_no = record_no // 6
        paragraph_no = record_no // 2
        page_id = _stable_id("p", seed, page_no)
        paragraph_id = _stable_id("q", seed, paragraph_no)
        record_id = _stable_id("r", seed, record_no)
        event_ids = [_stable_id("e", "W05", seed, len(observations) + i) for i in range(len(plan))]

        # Short physical lines, with deterministic but seed-sensitive resets.
        line_starts = [0]
        cursor = rng.randint(4, 6)
        while cursor < len(plan):
            line_starts.append(cursor)
            cursor += rng.randint(4, 7)
        line_starts_set = set(line_starts)
        line_for: list[int] = []
        line_number = -1
        for i in range(len(plan)):
            if i in line_starts_set:
                line_number += 1
            line_for.append(line_number)

        boundaries: list[str] = []
        for i in range(1, len(plan)):
            if i in line_starts_set:
                boundaries.append("LINE")
            elif plan[i]["field"] != plan[i - 1]["field"]:
                boundaries.append("FIELD")
            elif register == "r1" and rng.random() < 0.31:
                boundaries.append("JOIN")
            elif hand == "h1" and rng.random() < 0.16:
                boundaries.append("JOIN")
            elif register == "r2" and rng.random() < 0.19:
                boundaries.append("NONE")
            else:
                boundaries.append("SPACE")

        for i, item in enumerate(plan):
            global_index = len(observations)
            line_members = [j for j, ln in enumerate(line_for) if ln == line_for[i]]
            group_index = line_members.index(i)
            if len(line_members) == 1:
                line_pos = "ONLY"
            elif i == line_members[0]:
                line_pos = "START"
            elif i == line_members[-1]:
                line_pos = "END"
            else:
                line_pos = "MIDDLE"
            if i == 0:
                record_pos = "START"
            elif i == len(plan) - 1:
                record_pos = "END"
            else:
                record_pos = "MIDDLE"

            if i == 0:
                if record_no % 6 == 0:
                    sep_before = "PAGE"
                elif record_no % 2 == 0:
                    sep_before = "PARAGRAPH"
                else:
                    sep_before = "RECORD"
            else:
                sep_before = boundaries[i - 1]
            if i == len(plan) - 1:
                sep_after = "PAGE" if record_no % 6 == 5 else ("PARAGRAPH" if record_no % 2 == 1 else "RECORD")
            else:
                sep_after = boundaries[i]

            event_register = "r2" if register != "r2" and hand == "h2" and i == len(plan) - 2 else register
            event_hand = "h2" if hand != "h2" and register == "r2" and i == 1 else hand
            next_key = plan[i + 1]["key"] if i + 1 < len(plan) else None
            visible = _render(item["key"], event_register, event_hand, item["construction"], line_pos, next_key, rng)
            ambiguous = "YES" if sep_before in {"JOIN", "NONE"} or sep_after in {"JOIN", "NONE"} or (len(visible) <= 2 and rng.random() < 0.24) else "NO"
            layout_role = "lr0" if item["field"] == 0 else ("lr2" if item["field"] >= 7 else "lr1")
            event_id = event_ids[i]
            line_id = _stable_id("l", seed, record_no, line_for[i])
            observations.append({
                "world_id": "W05", "corpus_seed": seed, "event_id": event_id,
                "page_id": page_id, "paragraph_id": paragraph_id, "record_id": record_id,
                "line_id": line_id, "event_index": global_index, "group_index": group_index,
                "visible_group": visible, "separator_before": sep_before, "separator_after": sep_after,
                "register_id": event_register, "hand_id": event_hand, "layout_role": layout_role,
                "line_position_bin": line_pos, "record_position_bin": record_pos,
                "ambiguous_boundary": ambiguous,
            })

            target = item["target"]
            if isinstance(target, int):
                target_id = event_ids[target]
            elif isinstance(target, str) and target:
                target_id = target
            else:
                target_id = "NONE"
            scope_start = event_ids[item["scope_start"]] if isinstance(item["scope_start"], int) else "NONE"
            scope_end = event_ids[item["scope_end"]] if isinstance(item["scope_end"], int) else "NONE"
            lex = LEXICON[item["key"]]
            register_realization = {
                "r0": "RR_CONSERVATIVE", "r1": "RR_CHECKLIST", "r2": "RR_PEDAGOGICAL",
            }[event_register] + "_" + event_hand.upper()
            oracle.append({
                "world_id": "W05", "corpus_seed": seed, "event_id": event_id,
                "domain_id": "DOM_CALENDRICAL_RITUAL", "activity_id": item["activity"],
                "lexical_id": lex["lexical_id"], "semantic_entity_id": lex["semantic_entity_id"],
                "semantic_category": lex["semantic_category"], "function_class": item["function"],
                "relation_type": item["relation"], "relation_target_event_id": target_id,
                "state_before": item["state_before"], "state_after": item["state_after"],
                "historical_stem_id": lex["historical_stem_id"],
                "current_morpheme_ids": _pipe(item["morphemes"]),
                "fossilized_component_ids": _pipe(item["fossils"]),
                "construction_id": item["construction"], "scope_start_event_id": scope_start,
                "scope_end_event_id": scope_end, "record_schema_id": schema,
                "register_realization_id": register_realization,
                "productive_morphology": item["productive"],
                "current_component_semantics": _pipe(item["components"]),
                "genealogy_stage": "8",
            })

        # Cross-record targets retain actual event identity.
        rite_positions = [i for i, p in enumerate(plan) if p["function"] == "PROGRAM_LABEL"]
        offering_positions = [i for i, p in enumerate(plan) if p["function"] in {"ACTION", "ALTERNATIVE_ACTION"} and p["field"] == 4]
        if rite_positions:
            previous["rite"] = event_ids[rite_positions[0]]
        if offering_positions:
            previous["offering"] = event_ids[offering_positions[0]]

        record_no += 1
        calendar["day"] += 1
        if calendar["day"] >= 30:
            calendar["day"] = 0
            calendar["season"] = (calendar["season"] + 1) % 6

    return {
        "observations": observations,
        "oracle": oracle,
        "codebook": _codebook(),
        "genealogy": [dict(row) for row in GENEALOGY],
    }
