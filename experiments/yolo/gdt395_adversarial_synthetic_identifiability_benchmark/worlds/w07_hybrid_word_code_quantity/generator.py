#!/usr/bin/env python3
"""Deterministic generator for GDT395 world W07.

This module is intentionally self contained.  All semantic labels in the
returned oracle and codebook are hidden from the observation carrier.
"""

from __future__ import annotations

import hashlib
import random


WORLD_META = {
    "world_id": "W07",
    "title": "The Split-Bench Measure Ledgers",
    "broad_family": "HYBRID_WORD_CODE_QUANTITY",
    "practical_domain": "measurement and workshop accounting",
    "semantics_light": False,
    "organic_evolution": True,
    "clean_engineered_control": False,
    "adversarial_pair_id": "NONE",
    "carrier_profile": "CARRIER_HYBRID",
    "alphabet": ["ŋ", "ʃ", "ƛ", "ʒ", "ɣ", "χ", "ɬ", "ʘ", "ǂ", "ə", "ɐ", "ɔ", "ɯ", "ɨ", "·", "꞉"],
    "registers": ["R0", "R1", "R2"],
    "hands": ["H0", "H1", "H2"],
    "evolution_processes": [
        "compounding", "frequency_shortening", "analogy", "merger",
        "conditioned_split", "bleaching", "fossilization",
        "polyfunctionality", "suppletion", "register_divergence",
        "joined_detached_alternation",
    ],
    "generator_schema": "GDT395_WORLD_GENERATOR_V1",
}


GLYPHS = ("ŋ", "ʃ", "ƛ", "ʒ", "ɣ", "χ", "ɬ", "ʘ", "ǂ", "ə", "ɐ", "ɔ", "ɯ", "ɨ")


ITEMS = [
    ("copper_rod", "IT_COPPER", "ŋɐʃ", "ST_COPPER"),
    ("iron_blank", "IT_IRON", "χəŋ", "ST_IRON"),
    ("bronze_strip", "IT_BRONZE", "ʒɔɬ", "ST_BRONZE"),
    ("oak_stock", "IT_OAK", "ƛɨŋ", "ST_OAK"),
    ("linen_roll", "IT_LINEN", "ɣɐʒ", "ST_LINEN"),
    ("charcoal_sack", "IT_CHARCOAL", "ɬəχ", "ST_CHARCOAL"),
    ("tin_ingot", "IT_TIN", "ʘɔŋ", "ST_TIN"),
    ("resin_jar", "IT_RESIN", "ǂɨʃ", "ST_RESIN"),
]

UNITS = {
    "UN_MASS": ("mass_unit", "UNIT", "ŋə", "ST_MASS_UNIT"),
    "UN_LENGTH": ("length_unit", "UNIT", "ʃɐ", "ST_LENGTH_UNIT"),
    "UN_COUNT": ("count_unit", "UNIT", "ƛɔ", "ST_COUNT_UNIT"),
    "UN_VOLUME": ("volume_unit", "UNIT", "ʒɨ", "ST_VOLUME_UNIT"),
}

UNIT_FOR_ITEM = {
    "copper_rod": "UN_LENGTH", "iron_blank": "UN_COUNT",
    "bronze_strip": "UN_LENGTH", "oak_stock": "UN_LENGTH",
    "linen_roll": "UN_LENGTH", "charcoal_sack": "UN_MASS",
    "tin_ingot": "UN_MASS", "resin_jar": "UN_VOLUME",
}

OPERATORS = {
    "OP_ADD": ("receive_into_stock", "TRANSACTION_OPERATOR", "ʘŋɐ", "ST_RECEIVE"),
    "OP_SUB": ("issue_from_stock", "TRANSACTION_OPERATOR", "ʘʃə", "ST_ISSUE"),
    "OP_MEASURE": ("measure_object", "MEASURE_OPERATOR", "ʘƛɔ", "ST_MEASURE"),
    "OP_TRANSFORM": ("convert_material", "TRANSACTION_OPERATOR", "ʘʒɨ", "ST_TRANSFORM"),
    "OP_BALANCE": ("take_inventory", "TRANSACTION_OPERATOR", "ʘɣɐ", "ST_BALANCE"),
    "OP_CORRECT": ("correct_prior_entry", "REFERENCE_OPERATOR", "ʘχə", "ST_CORRECT"),
    "OP_MOVE": ("move_between_benches", "TRANSACTION_OPERATOR", "ʘɬɔ", "ST_MOVE"),
    "OP_CARRY": ("carry_forward", "SCOPE_OPERATOR", "ʘǂɨ", "ST_CARRY"),
}

RELATIONS = {
    "REL_LINK": ("directed_link", "RELATION", "ǂɐ", "ST_LINK"),
    "REL_PRIOR": ("prior_record_reference", "RELATION", "ǂə", "ST_PRIOR"),
    "REL_SAME": ("same_as_reference", "RELATION", "ʘǂɨ", "ST_CARRY"),
    "REL_FOR": ("work_order_purpose", "RELATION", "ǂɔ", "ST_PURPOSE"),
    "REL_FROM": ("source_relation", "RELATION", "ǂɯ", "ST_SOURCE"),
    "REL_TO": ("destination_relation", "RELATION", "ǂɨ", "ST_DESTINATION"),
}

MISC = {
    "MARK_CLOSE": ("record_scope_close", "SCOPE_MARKER", "ɨʘ", "ST_CLOSE"),
    "MARK_EST": ("estimated_quantity", "QUALIFIER", "ɐɣ", "ST_ESTIMATE"),
    "MARK_LOSS": ("processing_loss", "QUALIFIER", "ɐχ", "ST_LOSS"),
    "MARK_CHECK": ("verified_entry", "QUALIFIER", "ɐɬ", "ST_CHECK"),
    "DIM_LONG": ("long_dimension", "DIMENSION", "ɔŋ", "ST_LONG"),
    "DIM_WIDE": ("wide_dimension", "DIMENSION", "ɔʃ", "ST_WIDE"),
    "DIM_THICK": ("thick_dimension", "DIMENSION", "ɔƛ", "ST_THICK"),
    "REASON_DAMAGE": ("damage_correction", "REASON", "ɯŋ", "ST_DAMAGE"),
    "REASON_COUNT": ("count_discrepancy", "REASON", "ɯʃ", "ST_DISCREPANCY"),
    "REASON_WASTE": ("waste_correction", "REASON", "ɯƛ", "ST_WASTE"),
}

LOCATIONS = {
    "LOC_A": ("receiving_bench", "LOCATION", "ɣŋ", "ST_LOC_A"),
    "LOC_B": ("cutting_bench", "LOCATION", "ɣʃ", "ST_LOC_B"),
    "LOC_C": ("finishing_bench", "LOCATION", "ɣƛ", "ST_LOC_C"),
    "LOC_D": ("locked_store", "LOCATION", "ɣʒ", "ST_LOC_D"),
}

PARTICIPANTS = {
    "PART_A": ("supplier_house_a", "PARTICIPANT", "χŋɐ", "ST_PART_A"),
    "PART_B": ("supplier_house_b", "PARTICIPANT", "χʃə", "ST_PART_B"),
    "PART_C": ("journeyman_group", "PARTICIPANT", "χƛɔ", "ST_PART_C"),
    "PART_D": ("master_account", "PARTICIPANT", "χʒɨ", "ST_PART_D"),
}


def _seeded_rng(seed: int) -> random.Random:
    raw = hashlib.sha256(f"GDT395:W07:{seed}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))


def _pipe(values) -> str:
    vals = sorted({str(v) for v in values if str(v) and str(v) != "NONE"})
    return "|".join(vals) if vals else "NONE"


def _weighted(rng: random.Random, pairs):
    total = sum(weight for _, weight in pairs)
    point = rng.random() * total
    for value, weight in pairs:
        point -= weight
        if point <= 0:
            return value
    return pairs[-1][0]


def _hash_form(label: str, length: int = 3) -> str:
    digest = hashlib.sha256(("W07/form/" + label).encode()).digest()
    return "".join(GLYPHS[digest[i] % len(GLYPHS)] for i in range(length))


def _code_definitions():
    codes = []
    for index in range(28):
        item = ITEMS[index % len(ITEMS)]
        # Old classifier fragments remain visible only intermittently.  Rank
        # marks and inherited contractions make the labels opaque in practice.
        fragment = item[2][0] if index % 4 != 3 else _hash_form(f"opaque-{index}", 1)
        rank = GLYPHS[(index * 5 + 3) % len(GLYPHS)]
        tail = GLYPHS[(index * 7 + 1) % len(GLYPHS)]
        surface = fragment + rank + tail
        if index in (0, 1, 4, 8):
            surface = {0: "ŋʘ", 1: "χƛ", 4: "ɣǂ", 8: "ʒɬ"}[index]
        codes.append({
            "lex": f"CODE_{index:02d}",
            "entity": f"stock_lot_{index:02d}",
            "item": item[0],
            "item_lex": item[1],
            "surface": surface,
            "stem": f"ST_CATALOG_{index:02d}",
            "fossil": item[3] if index % 4 != 3 else "NONE",
        })
    return codes


CODES = _code_definitions()
CODE_BY_LEX = {row["lex"]: row for row in CODES}


def _quantity_form(number: int) -> str:
    if number == 1:
        return "ɬ"                 # suppletive high-frequency one
    if number == 2:
        return "ʒ"                 # suppletive high-frequency two
    if number == 6:
        return "ʘɐ"               # fossilized old dozen-half term
    digit = ("ɨ", "ŋ", "ʃ", "ƛ", "ʒ", "ɣ")
    places = []
    remainder = number
    while remainder:
        remainder, low = divmod(remainder, 6)
        places.append(digit[low])
    places.reverse()
    if len(places) == 1:
        return places[0] + "ə"
    return "ɐ".join(places)


def _build_lexicon():
    lexicon = {}

    def add(lex, entity, category, form, stem, rules, flags="NONE"):
        lexicon[lex] = {
            "lexical_id": lex,
            "semantic_entity_id": entity,
            "semantic_category": category,
            "historical_stem_id": stem,
            "canonical_hidden_form": form,
            "final_realization_rules": rules,
            "irregularity_flags": flags,
        }

    for lex, (entity, category, form, stem) in OPERATORS.items():
        flags = "polyfunctional_with_REL_SAME" if lex == "OP_CARRY" else "NONE"
        if lex == "OP_ADD":
            flags = "R0_merger_with_REL_TO"
        add(lex, entity, category, form, stem,
            "R0 frequency clipping; R1 school prefix retention; R2 guild vowel shift; position and hand allographs",
            flags)
    for lex, (entity, category, form, stem) in RELATIONS.items():
        flags = "polyfunctional_with_OP_CARRY" if lex == "REL_SAME" else "NONE"
        if lex == "REL_TO":
            flags = "R0_merger_with_OP_ADD"
        add(lex, entity, category, form, stem,
            "detached in R1; variably joined rightward in R0/R2; line-final clipping",
            flags)
    for lex, (entity, category, form, stem) in {**UNITS, **MISC, **LOCATIONS, **PARTICIPANTS}.items():
        flags = "analogical_unit_ending" if lex.startswith("UN_") else "NONE"
        add(lex, entity, category, form, stem,
            "register, hand, line-initial and line-final allomorphy", flags)
    for item, lex, form, stem in ITEMS:
        add(lex, item, "ARTIFACT_FAMILY", form, stem,
            "free lexical fragment; reduced after a matching inventory code; omitted in compact records",
            "bound_free_split")
    for code in CODES:
        fossil = code["fossil"]
        flags = ["opaque_inventory_code"]
        if fossil != "NONE":
            flags.append("fossilized_old_classifier")
        if code["lex"] in ("CODE_00", "CODE_01", "CODE_04", "CODE_08"):
            flags.append("suppletive_frequent_code")
        add(code["lex"], code["entity"], "INVENTORY_CODE", code["surface"], code["stem"],
            "catalog form; school register inserts divider; compact register may lose final rank; hand allographs",
            _pipe(flags))
    for number in range(1, 49):
        flags = "suppletive" if number in (1, 2, 6) else "NONE"
        add(f"Q_{number:02d}", f"quantity_{number}", "QUANTITY", _quantity_form(number),
            f"ST_QUANTITY_{number:02d}",
            "base-six productive composition above six; compact register contracts medial radix; positional clipping",
            flags)
    for number in range(1, 17):
        add(f"JOB_{number:02d}", f"work_order_{number:02d}", "WORK_ORDER",
            _hash_form(f"job-{number}", 3), f"ST_JOB_{number:02d}",
            "opaque work-order label; R1 divider after school prefix; hand allographs",
            "opaque_reference_code")
    return lexicon


LEXICON = _build_lexicon()


GENEALOGY = [
    {"stage": "S0", "rule_id": "W07-R00", "process_type": "lexical_inheritance",
     "input_ids": "ST_ITEM_ROOTS|ST_ACTION_ROOTS|ST_MEASURE_ROOTS", "output_ids": "PROTO_WORKSHOP_LEXICON",
     "conditioning": "early oral workshop vocabulary", "currently_productive": "false",
     "notes": "Independent item, action, unit and participant words."},
    {"stage": "S1", "rule_id": "W07-R01", "process_type": "compounding",
     "input_ids": "PROTO_WORKSHOP_LEXICON|RANK_MARKS", "output_ids": "ST_CATALOG_00..27",
     "conditioning": "lot labels written on bins", "currently_productive": "false",
     "notes": "Item classifiers compounded with rank marks to create inventory labels."},
    {"stage": "S2", "rule_id": "W07-R02", "process_type": "frequency_shortening",
     "input_ids": "OP_ADD|OP_SUB|Q_01|Q_02|CODE_00|CODE_01|CODE_04|CODE_08", "output_ids": "SHORT_HIGH_FREQUENCY_ALLOMORPHS",
     "conditioning": "frequent ledger tokens, strongest in R0", "currently_productive": "true",
     "notes": "Repeated entries lost weak material; four catalog codes became suppletive contractions."},
    {"stage": "S3", "rule_id": "W07-R03", "process_type": "analogy",
     "input_ids": "ST_MASS_UNIT|ST_LENGTH_UNIT|ST_COUNT_UNIT|ST_VOLUME_UNIT", "output_ids": "UNIT_ANALOGY_CLASS",
     "conditioning": "unit follows a numeral", "currently_productive": "true",
     "notes": "Four unrelated measure words acquired parallel final shapes."},
    {"stage": "S4", "rule_id": "W07-R04", "process_type": "merger",
     "input_ids": "OP_ADD|REL_TO", "output_ids": "R0_SHARED_ŋɐ",
     "conditioning": "compact counter register R0", "currently_productive": "true",
     "notes": "Receipt and goal markers became homographs in one register."},
    {"stage": "S5", "rule_id": "W07-R05", "process_type": "conditioned_split",
     "input_ids": "ITEM_STEMS", "output_ids": "FREE_ITEM|POSTCODE_REDUCED_ITEM",
     "conditioning": "after a semantically matching catalog code", "currently_productive": "true",
     "notes": "A free lexical noun and a shortened bound diagnostic alternate."},
    {"stage": "S6", "rule_id": "W07-R06", "process_type": "bleaching_and_fossilization",
     "input_ids": "OLD_ITEM_CLASSIFIERS", "output_ids": "FOSSIL_COMPONENTS_IN_CODES|REL_LINK",
     "conditioning": "catalog reanalysis and serial transactions", "currently_productive": "false",
     "notes": "Some class fragments survive inside opaque codes while a serial verb bleached to a link."},
    {"stage": "S7", "rule_id": "W07-R07", "process_type": "polyfunctionality",
     "input_ids": "ST_CARRY", "output_ids": "OP_CARRY|REL_SAME",
     "conditioning": "record initial versus reference field", "currently_productive": "true",
     "notes": "One inherited carry form marks both scope continuation and same-as reference."},
    {"stage": "S8", "rule_id": "W07-R08", "process_type": "suppletion_and_exceptions",
     "input_ids": "QUANTITY_PARADIGM|CATALOG_PARADIGM", "output_ids": "Q_01|Q_02|Q_06|FREQUENT_CODE_EXCEPTIONS",
     "conditioning": "lexically listed high-frequency members", "currently_productive": "false",
     "notes": "Three quantities and four codes resist productive composition."},
    {"stage": "S9", "rule_id": "W07-R09", "process_type": "register_school_divergence",
     "input_ids": "COMMON_LEDGER_SYSTEM", "output_ids": "R0|R1|R2",
     "conditioning": "counter, measurement school, and guild audit practice", "currently_productive": "true",
     "notes": "Schools differ in retained prefixes, dividers, vowel shifts and optional lexical glosses."},
    {"stage": "S10", "rule_id": "W07-R10", "process_type": "joined_detached_alternation",
     "input_ids": "REL_LINK|REL_PRIOR|REL_FROM|REL_TO", "output_ids": "BOUND_RELATION|FREE_RELATION",
     "conditioning": "joined in R0/R2 except at line end; detached in R1", "currently_productive": "true",
     "notes": "Spacing alternation and scribal fusion create ambiguous visible boundaries."},
]


HAND_MAP = {
    "H0": {},
    "H1": {"ŋ": "ɬ", "ʃ": "ʒ", "ə": "ɨ"},
    "H2": {"ƛ": "ǂ", "ɣ": "χ", "ɔ": "ɯ"},
}


def _entry(lex: str, function: str, relation="NONE", target="NONE",
           morphs=None, fossils=None, productive=False, components=None,
           stage="S10", field=0, join=False):
    book = LEXICON[lex]
    return {
        "lex": lex,
        "entity": book["semantic_entity_id"],
        "category": book["semantic_category"],
        "function": function,
        "relation": relation,
        "target": target,
        "stem": book["historical_stem_id"],
        "morphs": list(morphs or [lex]),
        "fossils": list(fossils or []),
        "productive": productive,
        "components": list(components or [book["semantic_entity_id"]]),
        "stage": stage,
        "field": field,
        "join": join,
        "state_before": "NONE",
        "state_after": "NONE",
    }


def _choose_code(rng: random.Random):
    # Zipf-like reuse is essential to the ledger ecology.
    weights = [(row, 1.0 / ((i + 1) ** 0.82)) for i, row in enumerate(CODES)]
    return _weighted(rng, weights)


def _choose_quantity(rng: random.Random, upper=48):
    common = [(1, 17), (2, 13), (3, 10), (4, 8), (5, 6), (6, 9),
              (8, 5), (10, 4), (12, 8), (18, 3), (24, 3), (30, 2), (36, 3), (48, 1)]
    candidates = [(n, w) for n, w in common if n <= upper]
    if rng.random() < 0.18:
        return rng.randint(1, upper)
    return _weighted(rng, candidates)


def _state_snapshot(inventory, keys):
    if not keys:
        return "NONE"
    return _pipe(f"{code}@{loc}={inventory.get((code, loc), 0)}" for code, loc in sorted(set(keys)))


def _mutate(inventory, changes):
    keys = [(code, loc) for code, loc, _, _ in changes]
    before = _state_snapshot(inventory, keys)
    for code, loc, mode, value in changes:
        old = inventory.get((code, loc), 0)
        if mode == "add":
            inventory[(code, loc)] = old + value
        elif mode == "sub":
            inventory[(code, loc)] = old - value
        elif mode == "set":
            inventory[(code, loc)] = value
    return before, _state_snapshot(inventory, keys)


def _code_event(code, field, target="PREVIOUS_CODE"):
    fossils = [] if code["fossil"] == "NONE" else [code["fossil"]]
    return _entry(code["lex"], "ENTITY_CODE", "code_recurrence", target,
                  morphs=[code["stem"], "M_RANK"], fossils=fossils,
                  productive=False,
                  components=[f"lot:{code['entity']}", f"material:{code['item']}"],
                  stage="S8" if "suppletive" in LEXICON[code["lex"]]["irregularity_flags"] else "S6",
                  field=field)


def _quantity_event(number, field, target):
    morphs = [f"M_DIGIT_{number}"] if number in (1, 2, 6) else [f"M_SIXES_{number // 6}", f"M_ONES_{number % 6}"]
    return _entry(f"Q_{number:02d}", "QUANTITY", "quantifies", target,
                  morphs=morphs, productive=number not in (1, 2, 6),
                  components=[f"cardinality:{number}"], stage="S8" if number in (1, 2, 6) else "S3", field=field)


def _unit_event(unit, field, target):
    return _entry(unit, "UNIT", "measures", target,
                  morphs=[LEXICON[unit]["historical_stem_id"], "M_UNIT_ANALOGY"],
                  productive=True, components=[LEXICON[unit]["semantic_entity_id"]], stage="S3", field=field)


def _relation_event(lex, field, target, register, relation):
    return _entry(lex, "RELATION", relation, target,
                  productive=True, components=[LEXICON[lex]["semantic_entity_id"]],
                  stage="S7" if lex == "REL_SAME" else "S10", field=field,
                  join=register != "R1")


def _item_event(code, field, target):
    entry = _entry(code["item_lex"], "LEXICAL_FRAGMENT", "classifies", target,
                   morphs=[code["item_lex"], "M_POSTCODE_REDUCTION"], productive=True,
                   components=[f"material:{code['item']}"], stage="S5", field=field,
                   join=True)
    return entry


def _record_plan(rng, register, inventory, previous_record_exists):
    schema = _weighted(rng, [
        ("RECEIPT", 23), ("ISSUE", 22), ("MEASURE", 16),
        ("TRANSFORM", 12), ("INVENTORY", 11), ("TRANSFER", 10),
        ("CORRECTION", 6 if previous_record_exists else 0),
    ])
    op_for = {
        "RECEIPT": "OP_ADD", "ISSUE": "OP_SUB", "MEASURE": "OP_MEASURE",
        "TRANSFORM": "OP_TRANSFORM", "INVENTORY": "OP_BALANCE",
        "TRANSFER": "OP_MOVE", "CORRECTION": "OP_CORRECT",
    }
    # A carry-forward is a genuine alternate construction, not a mere allograph.
    op = "OP_CARRY" if previous_record_exists and rng.random() < 0.055 else op_for[schema]
    events = [_entry(op, "RECORD_OPERATOR", field=0,
                     components=[OPERATORS[op][0]], stage="S7" if op == "OP_CARRY" else "S10")]
    changes = []
    locs = list(LOCATIONS)

    def add_gloss(code, field, local_target):
        rate = {"R0": 0.18, "R1": 0.72, "R2": 0.38}[register]
        if rng.random() < rate:
            events.append(_item_event(code, field, local_target))

    if schema == "RECEIPT":
        party = rng.choice(list(PARTICIPANTS))
        events.append(_entry(party, "PARTICIPANT", "source_of_record", "LOCAL:0", field=1))
        code = _choose_code(rng)
        qty = _choose_quantity(rng)
        loc = "LOC_A" if rng.random() < 0.7 else rng.choice(locs)
        ci = len(events); events.append(_code_event(code, 2))
        add_gloss(code, 2, f"LOCAL:{ci}")
        qi = len(events); events.append(_quantity_event(qty, 3, f"LOCAL:{ci}"))
        events.append(_unit_event(UNIT_FOR_ITEM[code["item"]], 3, f"LOCAL:{qi}"))
        if rng.random() < 0.22:
            events.append(_entry("MARK_CHECK", "QUALIFIER", "qualifies", f"LOCAL:{ci}", field=4))
        changes.append((code["lex"], loc, "add", qty))

    elif schema == "ISSUE":
        code = _choose_code(rng); qty = _choose_quantity(rng); loc = rng.choice(locs)
        station = rng.choice(list(LOCATIONS))
        events.append(_entry(station, "LOCATION", "destination_of_record", "LOCAL:0", field=1))
        ci = len(events); events.append(_code_event(code, 2))
        add_gloss(code, 2, f"LOCAL:{ci}")
        qi = len(events); events.append(_quantity_event(qty, 3, f"LOCAL:{ci}"))
        events.append(_unit_event(UNIT_FOR_ITEM[code["item"]], 3, f"LOCAL:{qi}"))
        if rng.random() < 0.58:
            events.append(_relation_event("REL_FOR", 4, f"LOCAL:{ci}", register, "purpose"))
            job = rng.randint(1, 16)
            events.append(_entry(f"JOB_{job:02d}", "WORK_ORDER", "purpose_of", f"LOCAL:{ci}", field=4))
        changes.append((code["lex"], loc, "sub", qty))

    elif schema == "MEASURE":
        code = _choose_code(rng); ci = len(events); events.append(_code_event(code, 1))
        add_gloss(code, 1, f"LOCAL:{ci}")
        dimension = rng.choice(["DIM_LONG", "DIM_WIDE", "DIM_THICK"])
        events.append(_entry(dimension, "DIMENSION", "property_of", f"LOCAL:{ci}", field=2))
        qty = _choose_quantity(rng)
        qi = len(events); events.append(_quantity_event(qty, 3, f"LOCAL:{ci}"))
        unit = "UN_LENGTH" if rng.random() < 0.88 else UNIT_FOR_ITEM[code["item"]]
        events.append(_unit_event(unit, 3, f"LOCAL:{qi}"))
        if rng.random() < 0.3:
            events.append(_entry("MARK_EST", "QUALIFIER", "qualifies", f"LOCAL:{qi}", field=3))

    elif schema == "TRANSFORM":
        source = _choose_code(rng)
        dest_candidates = [c for c in CODES if c["item"] == source["item"] and c["lex"] != source["lex"]]
        dest = rng.choice(dest_candidates or [c for c in CODES if c["lex"] != source["lex"]])
        qty = _choose_quantity(rng, 36); loc = rng.choice(locs)
        si = len(events); events.append(_code_event(source, 1))
        events.append(_relation_event("REL_LINK", 2, f"LOCAL:{si}", register, "transforms_from"))
        di = len(events); events.append(_code_event(dest, 2, target=f"LOCAL:{si}"))
        qi = len(events); events.append(_quantity_event(qty, 3, f"LOCAL:{di}"))
        events.append(_unit_event(UNIT_FOR_ITEM[dest["item"]], 3, f"LOCAL:{qi}"))
        loss = 1 if qty > 3 and rng.random() < 0.35 else 0
        if loss:
            events.append(_entry("MARK_LOSS", "QUALIFIER", "qualifies", f"LOCAL:{qi}", field=4))
        changes.extend([(source["lex"], loc, "sub", qty), (dest["lex"], loc, "add", qty - loss)])

    elif schema == "INVENTORY":
        loc = rng.choice(locs)
        events.append(_entry(loc, "LOCATION", "inventory_location", "LOCAL:0", field=1))
        for repetition in range(rng.randint(1, 3)):
            code = _choose_code(rng); qty = _choose_quantity(rng)
            ci = len(events); events.append(_code_event(code, 2 + repetition * 2))
            add_gloss(code, 2 + repetition * 2, f"LOCAL:{ci}")
            qi = len(events); events.append(_quantity_event(qty, 3 + repetition * 2, f"LOCAL:{ci}"))
            events.append(_unit_event(UNIT_FOR_ITEM[code["item"]], 3 + repetition * 2, f"LOCAL:{qi}"))
            changes.append((code["lex"], loc, "set", qty))
        if rng.random() < 0.7:
            events.append(_entry("MARK_CHECK", "QUALIFIER", "qualifies_scope", "LOCAL:0", field=9))

    elif schema == "TRANSFER":
        source_loc, dest_loc = rng.sample(locs, 2)
        code = _choose_code(rng); qty = _choose_quantity(rng)
        events.append(_relation_event("REL_FROM", 1, "LOCAL:0", register, "source"))
        events.append(_entry(source_loc, "LOCATION", "source_location", "LOCAL:0", field=1))
        ci = len(events); events.append(_code_event(code, 2))
        qi = len(events); events.append(_quantity_event(qty, 3, f"LOCAL:{ci}"))
        events.append(_unit_event(UNIT_FOR_ITEM[code["item"]], 3, f"LOCAL:{qi}"))
        events.append(_relation_event("REL_TO", 4, f"LOCAL:{ci}", register, "destination"))
        events.append(_entry(dest_loc, "LOCATION", "destination_location", f"LOCAL:{ci}", field=4))
        changes.extend([(code["lex"], source_loc, "sub", qty), (code["lex"], dest_loc, "add", qty)])

    else:  # CORRECTION
        events.append(_relation_event("REL_PRIOR", 1, "PREVIOUS_RECORD", register, "corrects"))
        code = _choose_code(rng); qty = _choose_quantity(rng, 24); loc = rng.choice(locs)
        ci = len(events); events.append(_code_event(code, 2))
        qi = len(events); events.append(_quantity_event(qty, 3, f"LOCAL:{ci}"))
        events.append(_unit_event(UNIT_FOR_ITEM[code["item"]], 3, f"LOCAL:{qi}"))
        reason = rng.choice(["REASON_DAMAGE", "REASON_COUNT", "REASON_WASTE"])
        events.append(_entry(reason, "REASON", "reason_for", "LOCAL:0", field=4))
        changes.append((code["lex"], loc, "add" if rng.random() < 0.45 else "sub", qty))

    # Same-as has the same canonical carrier as carry-forward but a different
    # relation and scope behavior.
    if previous_record_exists and rng.random() < 0.13:
        events.append(_relation_event("REL_SAME", 8, "PREVIOUS_RECORD", register, "continues_reference"))
    events.append(_entry("MARK_CLOSE", "SCOPE_CLOSE", "closes", "LOCAL:0", field=10,
                         components=["record_scope:end"], stage="S6"))
    before, after = _mutate(inventory, changes)
    events[0]["state_before"] = before
    events[0]["state_after"] = after
    events[-1]["state_before"] = "record:open"
    events[-1]["state_after"] = "record:posted"
    return schema, events


def _render(lex, register, hand, line_pos, record_pos, joined, rng):
    form = LEXICON[lex]["canonical_hidden_form"]
    ambiguous = False
    realization = []
    if register == "R0":
        realization.append("compact")
        if lex == "OP_ADD" or lex == "REL_TO":
            form = "ŋɐ"
            ambiguous = True
            realization.append("merger")
        elif lex.startswith("OP_") and len(form) > 2:
            form = form[1:]
            realization.append("frequency_clip")
        elif lex.startswith("UN_"):
            form = form[-1]
            realization.append("unit_clip")
        elif lex.startswith("CODE_") and rng.random() < 0.34 and len(form) > 1:
            form = form[:-1]
            ambiguous = True
            realization.append("code_clip")
        if lex.startswith("Q_") and len(form) > 2:
            form = form.replace("ɐ", "", 1)
            ambiguous = True
            realization.append("radix_contraction")
    elif register == "R1":
        realization.append("school")
        if lex.startswith(("CODE_", "JOB_")) and len(form) > 1:
            form = form[0] + "·" + form[1:]
            realization.append("school_divider")
        if lex.startswith("OP_") and not form.startswith("ʘ"):
            form = "ʘ" + form
            realization.append("restored_prefix")
    else:
        realization.append("guild")
        form = form.replace("ɐ", "ɔ").replace("ə", "ɨ")
        if lex in ("REL_LINK", "REL_PRIOR", "REL_FROM", "REL_TO"):
            form += "꞉"
            realization.append("guild_relation_tail")

    if joined:
        form = "ƛ" + form
        ambiguous = True
        realization.append("joined")
    else:
        realization.append("detached")

    if line_pos == "B0" and form:
        initial = {"ŋ": "ʘ", "ʃ": "ɬ", "ƛ": "ǂ"}.get(form[0])
        if initial:
            form = initial + form[1:]
            realization.append("line_initial_allograph")
    if line_pos == "B3" and len(form) > 1 and register != "R1":
        form = form[:-1]
        ambiguous = True
        realization.append("line_final_apocope")
    if record_pos == "B3" and lex == "MARK_CLOSE":
        form = "ɨ" if register == "R0" else form
        realization.append("record_final_close")
    mapping = HAND_MAP[hand]
    form = "".join(mapping.get(char, char) for char in form)
    realization.append(f"hand_{hand}")
    return form, ambiguous, _pipe(realization)


def _position_bin(index, size):
    if index == 0:
        return "B0"
    if index == size - 1:
        return "B3"
    if index * 2 < size:
        return "B1"
    return "B2"


def generate(seed: int, target_events: int = 8448) -> dict[str, list[dict]]:
    if not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    if not isinstance(target_events, int) or target_events < 1:
        raise ValueError("target_events must be a positive integer")
    rng = _seeded_rng(seed)
    observations = []
    oracle = []
    inventory = {}
    last_code_event = {}
    previous_record_operator = "NONE"
    record_number = 0
    page_number = -1
    paragraph_number = -1
    line_number = 0
    records_on_page = 0
    records_in_paragraph = 0
    page_capacity = 0
    paragraph_capacity = 0

    while len(observations) < target_events:
        new_page = page_number < 0 or records_on_page >= page_capacity
        if new_page:
            page_number += 1
            records_on_page = 0
            page_capacity = rng.randint(8, 13)
            paragraph_number += 1
            records_in_paragraph = 0
            paragraph_capacity = rng.randint(2, 4)
        new_paragraph = (not new_page) and records_in_paragraph >= paragraph_capacity
        if new_paragraph:
            paragraph_number += 1
            records_in_paragraph = 0
            paragraph_capacity = rng.randint(2, 4)

        register = _weighted(rng, [("R0", 52), ("R1", 29), ("R2", 19)])
        hand = _weighted(rng, [("H0", 58), ("H1", 27), ("H2", 15)])
        # School records favor H1, guild records mildly favor H2, without a
        # deterministic register/hand equivalence.
        if register == "R1" and rng.random() < 0.38:
            hand = "H1"
        elif register == "R2" and rng.random() < 0.32:
            hand = "H2"
        schema, specs = _record_plan(rng, register, inventory, previous_record_operator != "NONE")
        record_start = len(observations)
        event_ids = [f"W07E{record_start + i:07d}" for i in range(len(specs))]
        scope_start, scope_end = event_ids[0], event_ids[-1]

        # Physical lines have variable capacity and never cross a record.
        chunks = []
        cursor = 0
        while cursor < len(specs):
            capacity = rng.randint(4, 7)
            chunks.append((cursor, min(len(specs), cursor + capacity)))
            cursor += capacity

        local_line = {}
        for start, end in chunks:
            current_line = f"L{line_number:06d}"
            line_number += 1
            for i in range(start, end):
                local_line[i] = (current_line, i - start, end - start)

        page_id = f"P{page_number:04d}"
        paragraph_id = f"X{paragraph_number:05d}"
        record_id = f"R{record_number:06d}"
        for i, spec in enumerate(specs):
            line_id, in_line, line_size = local_line[i]
            line_pos = _position_bin(in_line, line_size)
            record_pos = _position_bin(i, len(specs))
            visible, render_ambiguous, realization = _render(
                spec["lex"], register, hand, line_pos, record_pos, spec["join"], rng)
            if i == 0:
                sep_before = "PAGE" if new_page else ("PARAGRAPH" if new_paragraph else "RECORD")
            elif local_line[i][0] != local_line[i - 1][0]:
                sep_before = "LINE"
            elif spec["join"]:
                sep_before = "JOIN"
            elif spec["field"] != specs[i - 1]["field"]:
                sep_before = "FIELD"
            else:
                sep_before = "SPACE"
            event_id = event_ids[i]
            observations.append({
                "world_id": "W07", "corpus_seed": seed, "event_id": event_id,
                "page_id": page_id, "paragraph_id": paragraph_id,
                "record_id": record_id, "line_id": line_id,
                "event_index": record_start + i, "group_index": in_line,
                "visible_group": visible, "separator_before": sep_before,
                "separator_after": "NONE", "register_id": register,
                "hand_id": hand,
                "layout_role": "LR0" if i == 0 else ("LR2" if i == len(specs) - 1 else "LR1"),
                "line_position_bin": line_pos, "record_position_bin": record_pos,
                "ambiguous_boundary": bool(render_ambiguous or sep_before == "JOIN"),
            })

            target = spec["target"]
            if target.startswith("LOCAL:"):
                relation_target = event_ids[int(target.split(":", 1)[1])]
            elif target == "PREVIOUS_RECORD":
                relation_target = previous_record_operator
            elif target == "PREVIOUS_CODE":
                relation_target = last_code_event.get(spec["lex"], "NONE")
            else:
                relation_target = "NONE"
            if spec["category"] == "INVENTORY_CODE":
                last_code_event[spec["lex"]] = event_id

            oracle.append({
                "world_id": "W07", "corpus_seed": seed, "event_id": event_id,
                "domain_id": "D_WORKSHOP_ACCOUNTING", "activity_id": f"ACT_{schema}",
                "lexical_id": spec["lex"], "semantic_entity_id": spec["entity"],
                "semantic_category": spec["category"], "function_class": spec["function"],
                "relation_type": spec["relation"], "relation_target_event_id": relation_target,
                "state_before": spec["state_before"], "state_after": spec["state_after"],
                "historical_stem_id": spec["stem"],
                "current_morpheme_ids": _pipe(spec["morphs"]),
                "fossilized_component_ids": _pipe(spec["fossils"]),
                "construction_id": f"CX_{schema}_{'CARRY' if specs[0]['lex'] == 'OP_CARRY' else 'BASE'}",
                "scope_start_event_id": scope_start, "scope_end_event_id": scope_end,
                "record_schema_id": f"RS_{schema}", "register_realization_id": realization,
                "productive_morphology": bool(spec["productive"]),
                "current_component_semantics": _pipe(spec["components"]),
                "genealogy_stage": spec["stage"],
            })

        previous_record_operator = event_ids[0]
        record_number += 1
        records_on_page += 1
        records_in_paragraph += 1

    # The right separator is the actual next visible hierarchical boundary.
    for index in range(len(observations) - 1):
        observations[index]["separator_after"] = observations[index + 1]["separator_before"]
    observations[-1]["separator_after"] = "NONE"
    codebook = [LEXICON[key].copy() for key in sorted(LEXICON)]
    genealogy = [row.copy() for row in GENEALOGY]
    return {
        "observations": observations,
        "oracle": oracle,
        "codebook": codebook,
        "genealogy": genealogy,
    }


if __name__ == "__main__":
    bundle = generate(7, 300)
    print(len(bundle["observations"]), len(bundle["codebook"]), len(bundle["genealogy"]))
