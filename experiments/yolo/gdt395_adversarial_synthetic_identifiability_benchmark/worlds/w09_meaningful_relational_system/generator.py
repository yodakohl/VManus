#!/usr/bin/env python3
"""Deterministic generator for W09, an organic route/resource notation."""

from __future__ import annotations

import hashlib
import random
from typing import Any


ALPHABET = list("kptmnsrlxvzo")
REGISTERS = ["RG_0", "RG_1", "RG_2", "RG_3"]
HANDS = ["HD_0", "HD_1", "HD_2"]

# Historical forms are phonological labels.  The script maps several sounds to
# the same sign, and context/hand rules then further disturb the mapping.
_SCRIPT_MAP = {
    "a": "k", "e": "p", "i": "t", "u": "m", "o": "n",
    "k": "s", "p": "r", "t": "l", "m": "x", "n": "v",
    "s": "z", "r": "o", "l": "k", "x": "p", "v": "t", "z": "m",
}

WORLD_META = {
    "world_id": "W09",
    "title": "The Wayhouse Tallies",
    "broad_family": "MEANINGFUL_RELATIONAL_SYSTEM",
    "practical_domain": "route planning and resource allocation",
    "semantics_light": False,
    "organic_evolution": True,
    "clean_engineered_control": False,
    "adversarial_pair_id": "PAIR_SEMANTIC",
    "carrier_profile": "CARRIER_ADVERSARIAL_MATCHED",
    "alphabet": ALPHABET,
    "registers": REGISTERS,
    "hands": HANDS,
    "evolution_processes": [
        "frequency_driven_shortening", "analogy", "merger", "split",
        "bleaching", "fossilization", "polyfunctionality",
        "suppletion_and_exceptions", "register_school_divergence",
    ],
    "generator_schema": "GDT395_WORLD_GENERATOR_V1",
}


def _lex(lexical_id: str, entity: str, category: str, function: str,
         stem: str, form: str, frequency: int = 1, flags: str = "NONE",
         fossils: str = "NONE") -> dict[str, Any]:
    return {
        "lexical_id": lexical_id, "semantic_entity_id": entity,
        "semantic_category": category, "function_class": function,
        "historical_stem_id": stem, "form": form,
        "frequency": frequency, "flags": flags, "fossils": fossils,
    }


# Forms are outcomes of the genealogy below, not a compositional encoding.
_LEXEMES = [
    _lex("LX_001", "REC_DISPATCH", "record_kind", "schema_marker", "HS_001", "korsa", 34, "frequent_shortening"),
    _lex("LX_002", "REC_ALLOCATION", "record_kind", "schema_marker", "HS_002", "toran", 24, "analogical_ending"),
    _lex("LX_003", "REC_GATE_REPORT", "record_kind", "schema_marker", "HS_003", "moxel", 18),
    _lex("LX_004", "REC_CONTINGENCY", "record_kind", "schema_marker", "HS_004", "sarko", 16, "polyfunctional_marker"),
    _lex("LX_005", "REC_AMENDMENT", "record_kind", "schema_marker", "HS_005", "novar", 12, "suppletive_archive"),
    _lex("LX_006", "REC_RECEIPT", "record_kind", "schema_marker", "HS_006", "pelon", 14),
    _lex("LX_010", "OP_DEPART", "operation", "predicate", "HS_010", "kavel", 24, "suppletive_field"),
    _lex("LX_011", "OP_TRAVERSE", "operation", "predicate", "HS_011", "morak", 30, "stem_split_by_register"),
    _lex("LX_012", "OP_ARRIVE", "operation", "predicate", "HS_010", "xoran", 27, "suppletive_common|shared_historical_stem"),
    _lex("LX_013", "OP_LOAD", "operation", "predicate", "HS_013", "tamel", 22),
    _lex("LX_014", "OP_UNLOAD", "operation", "predicate", "HS_014", "sovan", 20),
    _lex("LX_015", "OP_RESERVE", "operation", "predicate", "HS_015", "narel", 17, "bleached_hold_stem"),
    _lex("LX_016", "OP_CONSUME", "operation", "predicate", "HS_016", "poxar", 13),
    _lex("LX_017", "OP_TRANSFER", "operation", "predicate", "HS_017", "velom", 16),
    _lex("LX_018", "OP_INSPECT", "operation", "predicate", "HS_018", "rikon", 20),
    _lex("LX_019", "OP_WAIT", "operation", "predicate", "HS_019", "nasor", 12),
    _lex("LX_020", "OP_REROUTE", "operation", "predicate", "HS_020", "zarek", 11, "fossil_path", "FC_PATH_OLD"),
    _lex("LX_021", "OP_RELEASE", "operation", "predicate", "HS_021", "lomar", 10),
    _lex("LX_022", "OP_REPORT", "operation", "predicate", "HS_022", "teson", 18),
    _lex("LX_030", "REL_FROM", "relation", "relator", "HS_030", "karo", 50, "frequent_shortening"),
    _lex("LX_031", "REL_TO", "relation", "relator", "HS_031", "saro", 70, "partial_merger_with_beneficiary"),
    _lex("LX_032", "REL_VIA", "relation", "relator", "HS_032", "melo", 35),
    _lex("LX_033", "REL_CARGO", "relation", "relator", "HS_033", "naro", 34, "bleached_association"),
    _lex("LX_034", "REL_BENEFICIARY", "relation", "relator", "HS_034", "saro", 31, "partial_merger_with_goal"),
    _lex("LX_035", "REL_QUANTITY", "relation", "relator", "HS_035", "pato", 32),
    _lex("LX_036", "REL_CONDITION", "relation", "relator", "HS_036", "zelo", 28, "polyfunctional_with_resume"),
    _lex("LX_037", "REL_ALTERNATIVE", "relation", "relator", "HS_037", "tora", 23),
    _lex("LX_038", "REL_REFERENCE", "relation", "relator", "HS_036", "zelo", 18, "polyfunctional_with_condition"),
    _lex("LX_039", "REL_SEGMENT", "relation", "relator", "HS_039", "lavo", 20, "fossil_locative"),
    _lex("LX_040", "REL_AGENT", "relation", "relator", "HS_040", "rano", 22),
    _lex("LX_050", "LOC_NORTH_HOUSE", "location", "argument", "HS_050", "kortem", 16),
    _lex("LX_051", "LOC_RIVER_HOUSE", "location", "argument", "HS_051", "palor", 19),
    _lex("LX_052", "LOC_HIGH_PASS", "location", "argument", "HS_052", "mavon", 17),
    _lex("LX_053", "LOC_FORK_DEPOT", "location", "argument", "HS_053", "senak", 23),
    _lex("LX_054", "LOC_WELL_CAMP", "location", "argument", "HS_054", "rovem", 18),
    _lex("LX_055", "LOC_STONE_BRIDGE", "location", "argument", "HS_055", "taxor", 14),
    _lex("LX_056", "LOC_SOUTH_YARD", "location", "argument", "HS_056", "nesol", 15),
    _lex("LX_057", "LOC_LAKE_STORE", "location", "argument", "HS_057", "varem", 13, "fossil_vessel", "FC_VESSEL_OLD"),
    _lex("LX_060", "SEG_NORTH_RIVER", "route_segment", "argument", "HS_060", "kolan", 14),
    _lex("LX_061", "SEG_RIVER_FORK", "route_segment", "argument", "HS_061", "perom", 16),
    _lex("LX_062", "SEG_FORK_PASS", "route_segment", "argument", "HS_062", "mesar", 15),
    _lex("LX_063", "SEG_FORK_WELL", "route_segment", "argument", "HS_063", "saxel", 13),
    _lex("LX_064", "SEG_WELL_SOUTH", "route_segment", "argument", "HS_064", "ravel", 12),
    _lex("LX_065", "SEG_PASS_LAKE", "route_segment", "argument", "HS_065", "notem", 11),
    _lex("LX_070", "UNIT_RED_TEAM", "mobile_unit", "argument", "HS_070", "keman", 16),
    _lex("LX_071", "UNIT_REED_TEAM", "mobile_unit", "argument", "HS_071", "poler", 14),
    _lex("LX_072", "UNIT_HILL_TEAM", "mobile_unit", "argument", "HS_072", "navox", 13),
    _lex("LX_073", "UNIT_PACK_TRAIN", "mobile_unit", "argument", "HS_073", "tavor", 18, "fossil_vessel", "FC_VESSEL_OLD"),
    _lex("LX_074", "UNIT_SCOUT_PAIR", "mobile_unit", "argument", "HS_074", "serom", 15),
    _lex("LX_080", "RES_WATER", "resource", "argument", "HS_080", "noxel", 24),
    _lex("LX_081", "RES_GRAIN", "resource", "argument", "HS_081", "maren", 22),
    _lex("LX_082", "RES_FODDER", "resource", "argument", "HS_082", "maren", 15, "lexical_merger_with_grain"),
    _lex("LX_083", "RES_LAMP_OIL", "resource", "argument", "HS_083", "pavor", 12),
    _lex("LX_084", "RES_MEDICINE", "resource", "argument", "HS_084", "toxen", 10),
    _lex("LX_085", "RES_ROPE", "resource", "argument", "HS_085", "lasem", 9),
    _lex("LX_090", "QTY_ONE", "quantity", "quantifier", "HS_090", "kor", 20, "frequent_shortening"),
    _lex("LX_091", "QTY_TWO", "quantity", "quantifier", "HS_091", "pem", 18),
    _lex("LX_092", "QTY_THREE", "quantity", "quantifier", "HS_092", "nav", 13),
    _lex("LX_093", "QTY_HALF", "quantity", "quantifier", "HS_093", "tor", 9, "irregular_measure"),
    _lex("LX_094", "QTY_MANY", "quantity", "quantifier", "HS_094", "sal", 11),
    _lex("LX_100", "STATE_OPEN", "gate_state", "state_value", "HS_100", "narel", 18, "homograph_with_reserve|bleached_hold_stem"),
    _lex("LX_101", "STATE_BLOCKED", "gate_state", "state_value", "HS_101", "zoman", 12),
    _lex("LX_102", "STATE_LOW", "stock_state", "state_value", "HS_102", "par", 14),
    _lex("LX_103", "STATE_READY", "stock_state", "state_value", "HS_103", "mel", 16),
    _lex("LX_104", "STATE_DELAYED", "movement_state", "state_value", "HS_104", "ras", 11),
    _lex("LX_105", "STATE_CLEARED", "gate_state", "state_value", "HS_105", "kov", 10),
]

LEX = {x["lexical_id"]: x for x in _LEXEMES}
ENTITY_TO_LEX = {x["semantic_entity_id"]: x["lexical_id"] for x in _LEXEMES}

LOCATIONS = [f"LX_{n:03d}" for n in range(50, 58)]
SEGMENTS = [f"LX_{n:03d}" for n in range(60, 66)]
UNITS = [f"LX_{n:03d}" for n in range(70, 75)]
RESOURCES = [f"LX_{n:03d}" for n in range(80, 86)]
QUANTITIES = [f"LX_{n:03d}" for n in range(90, 95)]

SEGMENT_ENDPOINTS = {
    "LX_060": ("LX_050", "LX_051"), "LX_061": ("LX_051", "LX_053"),
    "LX_062": ("LX_053", "LX_052"), "LX_063": ("LX_053", "LX_054"),
    "LX_064": ("LX_054", "LX_056"), "LX_065": ("LX_052", "LX_057"),
}


GENEALOGY = [
    (1, "EV_01", "frequency_driven_shortening", "HS_001|HS_030|HS_031|HS_090", "MR_SHORT_A", "high token frequency and phrase-initial position", "YES", "record, goal, source, and unit-count forms reduce unevenly"),
    (2, "EV_02", "analogy", "MR_ROUTE_IMPV|HS_002", "MR_ORDER_FINAL", "productive route orders outside archival register", "YES", "allocation marker and several predicates acquire the order-school final"),
    (3, "EV_03", "merger", "HS_031|HS_034|HS_081|HS_082", "MR_GOAL_BEN|MR_DRY_STORE", "unaccented relation slots and inventory tallies", "NO", "goal/beneficiary and grain/fodder become partly homographic"),
    (3, "EV_04", "split", "HS_011", "MR_TRAVERSE_LEDGER|MR_TRAVERSE_FIELD", "register-conditioned before later lexicalization", "NO", "one inherited motion verb splits across schools"),
    (4, "EV_05", "bleaching", "HS_015", "MR_RESERVE|MR_GATE_HOLD", "before resource or route-state arguments", "YES", "hold verb becomes reservation predicate and gate-state operator"),
    (5, "EV_06", "fossilization", "FC_PATH_OLD|FC_VESSEL_OLD", "HS_020|HS_057|HS_073", "opaque lexical survivors", "NO", "obsolete path/vessel classifiers remain inside three stems"),
    (6, "EV_07", "polyfunctionality", "HS_036", "MR_CONDITION|MR_RESUME_REF", "clause edge versus amendment onset", "YES", "conditional particle extends to cross-record resumption"),
    (7, "EV_08", "suppletion_and_exceptions", "HS_010|HS_005", "MR_MOTION_SUPPL|MR_AMEND_ARCH", "field motion and archival amendment contexts", "NO", "common motion and amendment forms recruit unrelated stems"),
    (8, "EV_09", "register_school_divergence", "MR_SHARED_SYSTEM", "RG_0|RG_1|RG_2|RG_3", "dispatch, ledger, field, and archive schools", "YES", "schools differ in syncope, endings, joins, and retained forms"),
]


def _rng(seed: int) -> random.Random:
    digest = hashlib.sha256(f"GDT395:W09:{seed}".encode()).digest()
    return random.Random(int.from_bytes(digest[:8], "big"))


def _weighted(rng: random.Random, values: list[Any], weights: list[float]) -> Any:
    return rng.choices(values, weights=weights, k=1)[0]


def _token(lexical_id: str, *, relation: str = "NONE", target: int | str = "NONE",
           before: str = "NONE", after: str = "NONE", construction: str = "NONE",
           scope: tuple[int, int] | None = None, productive: str = "FALSE",
           components: str | None = None) -> dict[str, Any]:
    return {
        "lex": lexical_id, "relation": relation, "target": target,
        "before": before, "after": after, "construction": construction,
        "scope": scope, "productive": productive, "components": components,
    }


def _state(*parts: str) -> str:
    vals = sorted({p for p in parts if p and p != "NONE"})
    return "|".join(vals) if vals else "NONE"


def _record_dispatch(rng: random.Random, state: dict[str, Any]) -> tuple[list[dict], str, str]:
    unit = _weighted(rng, UNITS, [6, 5, 4, 7, 4])
    origin = state["unit_loc"][unit]
    candidates = [s for s, ep in SEGMENT_ENDPOINTS.items() if origin in ep]
    if not candidates:
        segment = rng.choice(SEGMENTS)
        origin = SEGMENT_ENDPOINTS[segment][0]
        state["unit_loc"][unit] = origin
    else:
        segment = rng.choice(candidates)
    a, b = SEGMENT_ENDPOINTS[segment]
    goal = b if origin == a else a
    resource = _weighted(rng, RESOURCES, [8, 7, 5, 3, 2, 2])
    qty = _weighted(rng, QUANTITIES, [8, 6, 4, 2, 3])
    pre = f"unit:{LEX[unit]['semantic_entity_id']}@{LEX[origin]['semantic_entity_id']}"
    post = f"unit:{LEX[unit]['semantic_entity_id']}@{LEX[goal]['semantic_entity_id']}"
    t = [_token("LX_001"), _token(unit), _token("LX_010", before=pre, after="unit:enroute", construction="CX_ROUTE_ORDER", productive="TRUE")]
    t += [_token("LX_030", relation="SOURCE", target=4), _token(origin),
          _token("LX_032", relation="VIA", target=6), _token(segment),
          _token("LX_033", relation="CARGO", target=8), _token(resource),
          _token("LX_035", relation="QUANTITY", target=10), _token(qty),
          _token("LX_012", before="unit:enroute", after=post, construction="CX_ROUTE_ORDER", productive="TRUE"),
          _token("LX_031", relation="GOAL", target=13), _token(goal)]
    if rng.random() < .48:
        gate = "LX_100" if state["gate"][segment] == "open" else "LX_101"
        t += [_token("LX_036", relation="CONDITION", target=15, construction="CX_GATE_SCOPE"), _token(gate)]
        t[14]["scope"] = (14, 15)
    state["unit_loc"][unit] = goal
    return t, "ACT_ROUTE_DISPATCH", "SCHEMA_DISPATCH"


def _record_allocation(rng: random.Random, state: dict[str, Any]) -> tuple[list[dict], str, str]:
    source, goal = rng.sample(LOCATIONS, 2)
    resource = _weighted(rng, RESOURCES, [9, 8, 5, 3, 2, 2])
    qty = _weighted(rng, QUANTITIES, [8, 6, 4, 2, 3])
    unit = _weighted(rng, UNITS, [6, 5, 4, 7, 4])
    key_s, key_g = (source, resource), (goal, resource)
    old_s, old_g = state["stock"][key_s], state["stock"][key_g]
    state["stock"][key_s] = max(0, old_s - 1)
    state["stock"][key_g] = min(4, old_g + 1)
    t = [_token("LX_002"), _token("LX_017", before=f"stock:{old_s}", after=f"stock:{state['stock'][key_s]}", construction="CX_ALLOCATION", productive="TRUE"),
         _token("LX_033", relation="CARGO", target=3), _token(resource),
         _token("LX_035", relation="QUANTITY", target=5), _token(qty),
         _token("LX_030", relation="SOURCE", target=7), _token(source),
         _token("LX_031", relation="GOAL", target=9), _token(goal),
         _token("LX_040", relation="AGENT", target=11), _token(unit)]
    if old_g <= 1:
        t += [_token("LX_034", relation="BENEFICIARY", target=13), _token(goal), _token("LX_103", before="stock:low", after="stock:ready")]
    return t, "ACT_RESOURCE_ALLOCATION", "SCHEMA_ALLOCATION"


def _record_gate(rng: random.Random, state: dict[str, Any]) -> tuple[list[dict], str, str]:
    segment = _weighted(rng, SEGMENTS, [7, 8, 7, 6, 5, 4])
    old = state["gate"][segment]
    new = "blocked" if (old == "open" and rng.random() < .38) else "open"
    state["gate"][segment] = new
    status = "LX_101" if new == "blocked" else "LX_100"
    scout = "LX_074"
    t = [_token("LX_003"), _token("LX_018", before=f"gate:{old}", after=f"gate:{new}", construction="CX_GATE_REPORT"),
         _token("LX_039", relation="SEGMENT", target=3), _token(segment),
         _token(status, before=f"gate:{old}", after=f"gate:{new}"),
         _token("LX_040", relation="AGENT", target=6), _token(scout),
         _token("LX_022", construction="CX_GATE_REPORT"),
         _token("LX_031", relation="GOAL", target=9), _token(SEGMENT_ENDPOINTS[segment][1])]
    if new == "blocked":
        t += [_token("LX_019", before="movement:ready", after="movement:delayed"), _token("LX_104")]
    return t, "ACT_ROUTE_INSPECTION", "SCHEMA_GATE_REPORT"


def _record_contingency(rng: random.Random, state: dict[str, Any]) -> tuple[list[dict], str, str]:
    blocked = [s for s in SEGMENTS if state["gate"][s] == "blocked"]
    segment = rng.choice(blocked or SEGMENTS)
    alternate = rng.choice([s for s in SEGMENTS if s != segment])
    unit = rng.choice(UNITS)
    gate_lex = "LX_101" if state["gate"][segment] == "blocked" else "LX_100"
    t = [_token("LX_004"), _token(unit),
         _token("LX_036", relation="CONDITION", target=3, construction="CX_IF_ALT", productive="TRUE"), _token(gate_lex),
         _token("LX_039", relation="SEGMENT", target=5), _token(segment),
         _token("LX_019", before="movement:ready", after="movement:delayed", construction="CX_IF_ALT"),
         _token("LX_037", relation="ALTERNATIVE", target=8, construction="CX_IF_ALT", productive="TRUE"), _token(alternate),
         _token("LX_020", before="movement:delayed", after="movement:rerouted", construction="CX_IF_ALT"),
         _token("LX_032", relation="VIA", target=11), _token(alternate),
         _token("LX_031", relation="GOAL", target=13), _token(SEGMENT_ENDPOINTS[alternate][1])]
    t[2]["scope"] = (2, 6)
    t[7]["scope"] = (7, 13)
    return t, "ACT_CONTINGENCY_PLANNING", "SCHEMA_CONTINGENCY"


def _record_amendment(rng: random.Random, state: dict[str, Any]) -> tuple[list[dict], str, str]:
    resource = rng.choice(RESOURCES)
    goal = rng.choice(LOCATIONS)
    unit = rng.choice(UNITS)
    old = state["stock"][(goal, resource)]
    op = "LX_015" if old <= 1 else "LX_021"
    after = min(4, old + 1) if op == "LX_015" else max(0, old - 1)
    state["stock"][(goal, resource)] = after
    t = [_token("LX_005"), _token("LX_038", relation="REFERENCE", target="PREVIOUS_RECORD", construction="CX_RESUMPTIVE_REF"),
         _token(op, before=f"stock:{old}", after=f"stock:{after}", construction="CX_AMENDMENT"),
         _token("LX_033", relation="CARGO", target=4), _token(resource),
         _token("LX_031", relation="GOAL", target=6), _token(goal),
         _token("LX_040", relation="AGENT", target=8), _token(unit),
         _token("LX_035", relation="QUANTITY", target=10), _token(rng.choice(QUANTITIES))]
    return t, "ACT_ALLOCATION_REVISION", "SCHEMA_AMENDMENT"


def _record_receipt(rng: random.Random, state: dict[str, Any]) -> tuple[list[dict], str, str]:
    unit = rng.choice(UNITS)
    location = state["unit_loc"][unit]
    resource = _weighted(rng, RESOURCES, [9, 8, 5, 3, 2, 2])
    old = state["stock"][(location, resource)]
    after = min(4, old + 1)
    state["stock"][(location, resource)] = after
    state_lex = "LX_102" if after <= 1 else "LX_103"
    t = [_token("LX_006"), _token(unit), _token("LX_014", before=f"stock:{old}", after=f"stock:{after}", construction="CX_RECEIPT"),
         _token("LX_033", relation="CARGO", target=4), _token(resource),
         _token("LX_035", relation="QUANTITY", target=6), _token(rng.choice(QUANTITIES)),
         _token("LX_031", relation="GOAL", target=8), _token(location),
         _token(state_lex, before=f"stock:{old}", after=f"stock:{after}"),
         _token("LX_022", construction="CX_RECEIPT")]
    if rng.random() < .35:
        t += [_token("LX_038", relation="REFERENCE", target="PREVIOUS_RECORD", construction="CX_RESUMPTIVE_REF")]
    return t, "ACT_DELIVERY_RECEIPT", "SCHEMA_RECEIPT"


BUILDERS = [_record_dispatch, _record_allocation, _record_gate,
            _record_contingency, _record_amendment, _record_receipt]


def _line_sizes(n: int, rng: random.Random) -> list[int]:
    choices: list[list[int]] = []
    for first in range(4, 9):
        for second in range(4, 9):
            if first + second == n:
                choices.append([first, second])
            for third in range(4, 9):
                if first + second + third == n:
                    choices.append([first, second, third])
    return rng.choice(choices)


def _rotate_char(ch: str, amount: int) -> str:
    i = ALPHABET.index(ch)
    return ALPHABET[(i + amount) % len(ALPHABET)]


def _surface(lex: dict[str, Any], register: int, hand: int, position: int,
             line_len: int, rng: random.Random) -> tuple[str, str, str, str]:
    form = lex["form"]
    realization = [f"BASE_{lex['lexical_id']}"]
    morphemes = [f"CM_{lex['lexical_id'][3:]}"]
    components = [lex["semantic_category"]]

    # Suppletion and lexical exceptions precede productive school rules.
    if lex["lexical_id"] == "LX_010" and register == 2:
        form = "sorem"
        realization.append("SUPPL_FIELD")
    elif lex["lexical_id"] == "LX_005" and register == 3:
        form = "velax"
        realization.append("SUPPL_ARCHIVE")
    elif lex["lexical_id"] == "LX_011" and register in (1, 3):
        form = "molak"
        realization.append("LEXICAL_SPLIT_LEDGER")

    if register == 0 and lex["function_class"] == "predicate" and len(form) < 7:
        form += "k"
        morphemes.append("CM_ORDER_FINAL")
        components.append("directive")
        realization.append("DISPATCH_FINAL")
    elif register == 1 and len(form) >= 5 and form[2] in "aeiou":
        form = form[:2] + form[3:]
        realization.append("LEDGER_SYNCOPE")
    elif register == 2 and lex["frequency"] >= 20 and len(form) > 4:
        form = form[:-1]
        realization.append("FIELD_SHORTENING")
    elif register == 3 and lex["semantic_category"] in ("record_kind", "relation"):
        form += "o"
        morphemes.append("CM_ARCHIVE_RETENTION")
        components.append("archival")
        realization.append("ARCHIVE_ENDING")

    if position == 0 and lex["semantic_category"] == "record_kind":
        form = "x" + form
        morphemes.append("CM_RECORD_EDGE")
        components.append("record_onset")
        realization.append("EDGE_FUSION")
    if position == line_len - 1 and len(form) <= 6 and rng.random() < .42:
        form += "n"
        morphemes.append("CM_LINE_CLOSURE")
        components.append("line_closure")
        realization.append("LINE_CLOSURE")

    # The many-to-one sound/sign mapping is older than the hand allographs.
    chars = [_SCRIPT_MAP[c] for c in form]
    for i in range(1, len(chars)):
        if chars[i] == chars[i - 1] and i % 2:
            chars[i] = _rotate_char(chars[i], 3)
    # Hands alter allographs contextually; this is deliberately non-bijective.
    if hand == 1:
        chars = [_rotate_char(c, 1) if c in "kvz" and i % 2 == 0 else c for i, c in enumerate(chars)]
        realization.append("HAND1_ALLOGRAPH")
    elif hand == 2:
        chars = [_rotate_char(c, 2) if c in "ptx" and i > 0 else c for i, c in enumerate(chars)]
        realization.append("HAND2_ALLOGRAPH")
    form = "".join(chars)
    if len(form) > 7:
        form = form[:7]
    return form, "|".join(sorted(set(morphemes))), "|".join(sorted(set(components))), ";".join(realization)


def _codebook() -> list[dict[str, str]]:
    rows = []
    rules = ("many-to-one historical sound/sign map; LX_010 field, LX_005 archive, "
             "and LX_011 ledger/archive lexical exceptions; RG_0 predicate final; "
             "RG_1 conditioned syncope; RG_2 frequency shortening; RG_3 retained "
             "ending; record-onset and seeded line-edge fusion; HD_1/HD_2 "
             "contextual allography")
    for x in _LEXEMES:
        rows.append({
            "lexical_id": x["lexical_id"],
            "semantic_entity_id": x["semantic_entity_id"],
            "semantic_category": x["semantic_category"],
            "historical_stem_id": x["historical_stem_id"],
            "canonical_hidden_form": x["form"],
            "final_realization_rules": rules,
            "irregularity_flags": x["flags"],
        })
    return rows


def _genealogy() -> list[dict[str, Any]]:
    return [{
        "stage": stage, "rule_id": rid, "process_type": process,
        "input_ids": inputs, "output_ids": outputs,
        "conditioning": condition, "currently_productive": productive,
        "notes": notes,
    } for stage, rid, process, inputs, outputs, condition, productive, notes in GENEALOGY]


def generate(seed: int, target_events: int = 8448) -> dict[str, list[dict]]:
    """Generate a stateful corpus, finishing the last record after target_events."""
    if not isinstance(seed, int):
        raise TypeError("seed must be int")
    if not isinstance(target_events, int) or target_events < 1:
        raise ValueError("target_events must be a positive int")
    rng = _rng(seed)
    observations: list[dict] = []
    oracle: list[dict] = []
    state = {
        "unit_loc": {u: LOCATIONS[i % len(LOCATIONS)] for i, u in enumerate(UNITS)},
        "gate": {s: "open" for s in SEGMENTS},
        "stock": {(loc, res): rng.randrange(1, 4) for loc in LOCATIONS for res in RESOURCES},
    }
    record_no = 0
    previous_record_anchor = "NONE"

    while len(observations) < target_events:
        # Zipf-like schema recurrence: common dispatch/allocation, rare amendments.
        builder = _weighted(rng, BUILDERS, [34, 25, 17, 12, 7, 14])
        tokens, activity_id, schema_id = builder(rng, state)
        if not 8 <= len(tokens) <= 16:
            raise AssertionError("record outside carrier envelope")
        record_no += 1
        page_no = (record_no - 1) // 10 + 1
        within_page = (record_no - 1) % 10
        paragraph_on_page = within_page // 3 + 1
        register = _weighted(rng, list(range(4)), [35, 29, 24, 12])
        hand = (page_no + register + rng.randrange(3)) % 3
        sizes = _line_sizes(len(tokens), rng)
        record_start_global = len(observations)
        local_event_ids = [f"W09_{seed:08x}_E{record_start_global+i:07d}" for i in range(len(tokens))]
        line_assign: list[tuple[int, int, int]] = []
        cursor = 0
        for line_offset, size in enumerate(sizes):
            for pos in range(size):
                line_assign.append((line_offset, pos, size))
            cursor += size

        for local_i, spec in enumerate(tokens):
            global_i = record_start_global + local_i
            line_offset, line_pos, line_len = line_assign[local_i]
            event_id = local_event_ids[local_i]
            lex = LEX[spec["lex"]]
            visible, morphs, components, realization = _surface(
                lex, register, hand, line_pos, line_len, rng)
            if spec["productive"] == "TRUE":
                construction_component = "CM_" + spec["construction"].removeprefix("CX_")
                morphs = "|".join(sorted(set(morphs.split("|") + [construction_component])))

            if local_i == 0:
                if within_page == 0:
                    sep_before = "PAGE"
                elif within_page % 3 == 0:
                    sep_before = "PARAGRAPH"
                else:
                    sep_before = "RECORD"
            elif line_pos == 0:
                sep_before = "LINE"
            elif rng.random() < .17:
                sep_before = "JOIN"
            elif spec["relation"] != "NONE" or tokens[local_i - 1]["relation"] != "NONE":
                sep_before = "FIELD" if rng.random() < .46 else "SPACE"
            else:
                sep_before = "NONE" if rng.random() < .07 else "SPACE"

            ambiguous = "NO"
            page_id = f"W09_P{page_no:04d}"
            paragraph_id = f"W09_P{page_no:04d}_A{paragraph_on_page:02d}"
            record_id = f"W09_R{record_no:06d}"
            line_id = f"W09_L{page_no:04d}_{line_offset + within_page * 3:03d}"
            record_bin = "INITIAL" if local_i < len(tokens) / 3 else ("FINAL" if local_i >= 2 * len(tokens) / 3 else "MEDIAL")
            line_bin = "INITIAL" if line_pos == 0 else ("FINAL" if line_pos == line_len - 1 else "MEDIAL")
            observations.append({
                "world_id": "W09", "corpus_seed": seed, "event_id": event_id,
                "page_id": page_id, "paragraph_id": paragraph_id,
                "record_id": record_id, "line_id": line_id,
                "event_index": global_i, "group_index": local_i,
                "visible_group": visible, "separator_before": sep_before,
                "separator_after": "NONE", "register_id": REGISTERS[register],
                "hand_id": HANDS[hand],
                "layout_role": "L0" if local_i == 0 else ("L1" if line_pos == 0 else "L2"),
                "line_position_bin": line_bin, "record_position_bin": record_bin,
                "ambiguous_boundary": ambiguous,
            })

            target = spec["target"]
            if isinstance(target, int):
                relation_target = local_event_ids[target]
            elif target == "PREVIOUS_RECORD":
                relation_target = previous_record_anchor
            else:
                relation_target = "NONE"
            scope = spec["scope"]
            scope_start = local_event_ids[scope[0]] if scope else "NONE"
            scope_end = local_event_ids[scope[1]] if scope else "NONE"
            fossils = lex["fossils"]
            oracle.append({
                "world_id": "W09", "corpus_seed": seed, "event_id": event_id,
                "domain_id": "DOMAIN_ROUTE_RESOURCE",
                "activity_id": activity_id, "lexical_id": lex["lexical_id"],
                "semantic_entity_id": lex["semantic_entity_id"],
                "semantic_category": lex["semantic_category"],
                "function_class": lex["function_class"],
                "relation_type": spec["relation"],
                "relation_target_event_id": relation_target,
                "state_before": spec["before"], "state_after": spec["after"],
                "historical_stem_id": lex["historical_stem_id"],
                "current_morpheme_ids": morphs,
                "fossilized_component_ids": fossils,
                "construction_id": spec["construction"],
                "scope_start_event_id": scope_start, "scope_end_event_id": scope_end,
                "record_schema_id": schema_id,
                "register_realization_id": f"{REGISTERS[register]}:{realization}",
                "productive_morphology": spec["productive"],
                "current_component_semantics": spec["components"] or components,
                "genealogy_stage": 8,
            })

        previous_record_anchor = local_event_ids[0]

    # Make after-boundaries agree with the next physical boundary.
    for i, row in enumerate(observations[:-1]):
        row["separator_after"] = observations[i + 1]["separator_before"]
    observations[-1]["separator_after"] = "NONE"

    # Exactly eleven percent of non-hierarchical boundaries are ambiguous.
    # Hash ranking makes this independent of list/dict iteration accidents.
    eligible = [r for r in observations if r["separator_before"] not in
                {"PAGE", "PARAGRAPH", "RECORD", "LINE"}]
    desired = min(len(eligible), round(len(observations) * .11))
    eligible.sort(key=lambda r: hashlib.sha256(
        f"W09:AMB:{seed}:{r['event_id']}".encode()).digest())
    for row in eligible[:desired]:
        row["ambiguous_boundary"] = "YES"

    return {
        "observations": observations,
        "oracle": oracle,
        "codebook": _codebook(),
        "genealogy": _genealogy(),
    }


if __name__ == "__main__":
    result = generate(9, 300)
    print(len(result["observations"]), len(result["oracle"]),
          len(result["codebook"]), len(result["genealogy"]))
