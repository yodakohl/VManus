#!/usr/bin/env python3
"""Deterministic generator for GDT395 W02, an organic apothecary codebook."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from src.world_api import pipe, seeded_rng, stable_id


ALPHABET = tuple("ɓɕɗɣɦƙɬɱŋƥʂƭʋʐ")
REGISTERS = ("R0", "R1", "R2")
HANDS = ("H0", "H1")

WORLD_META = {
    "world_id": "W02",
    "title": "Three-School Apothecary Codebook",
    "broad_family": "ORGANIC_CODEBOOK",
    "practical_domain": "apothecary inventory and preparation",
    "semantics_light": False,
    "organic_evolution": True,
    "clean_engineered_control": False,
    "adversarial_pair_id": "PAIR_CODEBOOK",
    "carrier_profile": "CARRIER_CODEBOOK_MATCHED",
    "alphabet": list(ALPHABET),
    "registers": list(REGISTERS),
    "hands": list(HANDS),
    "evolution_processes": [
        "frequency_driven_shortening", "analogy", "merger",
        "conditioned_split", "semantic_bleaching", "fossilization",
        "polyfunctionality", "suppletion", "register_divergence",
        "school_divergence", "hand_reshaping", "position_conditioning",
    ],
    "generator_schema": "GDT395_WORLD_GENERATOR_V1",
}


# id, entity, category, historical stem, proto mnemonic, modern code form,
# frequency band, irregularity flags.  Forms are whole codebook outcomes, not
# spellings of the English glosses.
_ENTRY_DATA = (
    # Ingredients and materials.
    ("L001", "ALOE", "INGREDIENT", "HS001", "PROTO_ALEK", "ɦɓɱƭʂ", "M", "NONE"),
    ("L002", "ANISE", "INGREDIENT", "HS002", "PROTO_NISU", "ŋɕɬƥɣ", "M", "COUNTER_MERGER"),
    ("L003", "MYRRH", "INGREDIENT", "HS003", "PROTO_MARU", "ɱɣƭʐɗ", "M", "NONE"),
    ("L004", "SAGE", "INGREDIENT", "HS004", "PROTO_SAG", "ʂɓƙɬɦ", "H", "NONE"),
    ("L005", "MINT", "INGREDIENT", "HS005", "PROTO_MINT", "ŋɕɬƥʋ", "H", "COUNTER_MERGER"),
    ("L006", "WAX", "INGREDIENT", "HS006", "PROTO_WAK", "ƥɦɗɱɬ", "H", "PARTIAL_MERGER"),
    ("L007", "HONEY", "INGREDIENT", "HS007", "PROTO_HANI", "ɦŋɓʂƭ", "H", "NONE"),
    ("L008", "SALT", "INGREDIENT", "HS008", "PROTO_SALT", "ʂɬɓɗƙ", "H", "NONE"),
    ("L009", "IRIS", "INGREDIENT", "HS009", "PROTO_IRID", "ɣƭɕʋŋ", "L", "NONE"),
    ("L010", "POPPY", "INGREDIENT", "HS010", "PROTO_PAP", "ƥɓƥɣɦ", "M", "NONE"),
    ("L011", "RESIN", "INGREDIENT", "HS011", "PROTO_RASIN", "ƥɦɗɱʐ", "M", "PARTIAL_MERGER"),
    ("L012", "VINEGAR", "INGREDIENT", "HS012", "PROTO_VINAK", "ʋɣŋɓƙɬ", "M", "NONE"),
    ("L013", "OIL", "INGREDIENT", "HS013L", "PROTO_LIQUID_Q", "ɬʋɦƭɗ", "H", "CONSTRUCTION_SPLIT"),
    ("L014", "BARK", "INGREDIENT", "HS014", "PROTO_BARAK", "ɗɓƭɓƙ", "M", "NONE"),
    ("L015", "WINE", "INGREDIENT", "HS015", "PROTO_WIN", "ʋɕŋɦʂ", "M", "NONE"),
    ("L016", "ASH", "INGREDIENT", "HS016", "PROTO_ASH", "ɓʂɦƙƭ", "L", "NONE"),
    # Prepared products; several are fossilized constructions.
    ("L017", "SALVE", "PREPARATION", "HS017", "PROTO_GRIND_WAX", "ɱƥɦɬƭ", "H", "FOSSILIZED_GRIND_WAX"),
    ("L018", "TONIC", "PREPARATION", "HS018", "PROTO_HEAT_WINE", "ƭʋɓŋɣ", "H", "FOSSILIZED_HEAT_WINE"),
    ("L019", "POWDER", "PREPARATION", "HS019", "PROTO_DRY_GRIND", "ɗƥʂɕƙ", "H", "FOSSILIZED_DRY_GRIND"),
    ("L020", "SYRUP", "PREPARATION", "HS013L", "PROTO_LIQUID_Q", "ɬʋɦɱʐ", "M", "CONSTRUCTION_SPLIT"),
    ("L021", "WASH", "PREPARATION", "HS021", "PROTO_WASH", "ʐɕɦɗƥ", "M", "NONE"),
    ("L022", "DRAUGHT", "PREPARATION", "HS022", "PROTO_DRINK_DOSE", "ɗƭɓʋɬ", "M", "FOSSILIZED_DOSE"),
    ("L023", "PLASTER", "PREPARATION", "HS023", "PROTO_BIND_WAX", "ƙɬɣƥƭ", "L", "FOSSILIZED_BIND_WAX"),
    ("L024", "TINCTURE", "PREPARATION", "HS024", "PROTO_STEEP", "ƭɕŋƙʋ", "L", "NONE"),
    # Operations.
    ("L025", "COUNT", "ACTION", "HS025", "PROTO_COUNT", "ƙɓɱƭ", "H", "LEDGER_SUPPLETION|FREQUENCY_CLIP"),
    ("L026", "RECEIVE", "ACTION", "HS026", "PROTO_RECEIVE", "ƥɣɓʐ", "H", "FREQUENCY_CLIP"),
    ("L027", "GRIND", "ACTION", "HS027", "PROTO_GRIND", "ɱƥɣɗƙ", "H", "BENCH_CLIP"),
    ("L028", "HEAT", "ACTION", "HS028", "PROTO_HEAT", "ɦƭɓƙɬ", "H", "NONE"),
    ("L029", "MIX", "ACTION", "HS029", "PROTO_MIX", "ɱɕƙʂƭ", "H", "NONE"),
    ("L030", "STRAIN", "ACTION", "HS030", "PROTO_STRAIN", "ʂƭƥɓŋ", "M", "NONE"),
    ("L031", "BOTTLE", "ACTION", "HS031", "PROTO_BOTTLE", "ɓƭɬɗʋ", "M", "NONE"),
    ("L032", "ISSUE", "ACTION", "HS032", "PROTO_GIVE", "ɣʂƭɬ", "H", "FREQUENCY_CLIP"),
    ("L033", "DISCARD", "ACTION", "HS033", "PROTO_CAST", "ƙɓʂƭŋ", "M", "NONE"),
    ("L034", "TRANSFER", "ACTION", "HS034", "PROTO_MOVE", "ʋɱɓɗƥ", "M", "NONE"),
    ("L035", "INSPECT", "ACTION", "HS035", "PROTO_SEE", "ɕŋʂƭɦ", "M", "NONE"),
    ("L036", "SEAL", "ACTION", "HS036", "PROTO_SEAL", "ʂɓɬɣƥ", "M", "NONE"),
    # Numerals and analogically remodeled units.
    ("L037", "ONE", "QUANTITY", "HS037", "PROTO_ONE", "ɓɣƭɬ", "H", "NUMERAL_SUPPLETION"),
    ("L038", "TWO", "QUANTITY", "HS038", "PROTO_TWO", "ɗʋɱƙ", "H", "NUMERAL_SUPPLETION"),
    ("L039", "THREE", "QUANTITY", "HS039", "PROTO_THREE", "ɬɣƥƭ", "H", "NONE"),
    ("L040", "FOUR", "QUANTITY", "HS040", "PROTO_FOUR", "ɦɗɓŋ", "M", "NONE"),
    ("L041", "SIX", "QUANTITY", "HS041", "PROTO_SIX", "ʂɣʋƥ", "M", "NONE"),
    ("L042", "TWELVE", "QUANTITY", "HS042", "PROTO_TWELVE", "ƭɱɕɦ", "M", "NONE"),
    ("L043", "DRAM", "UNIT", "HS043", "PROTO_WEIGHT_D", "ɗɣɱƭɬ", "H", "ANALOGICAL_UNIT_FINAL"),
    ("L044", "OUNCE", "UNIT", "HS044", "PROTO_WEIGHT_O", "ɓʋŋƭɬ", "H", "ANALOGICAL_UNIT_FINAL"),
    ("L045", "JARFUL", "UNIT", "HS045", "PROTO_JAR_AMOUNT", "ƙɓƥƭɬ", "M", "ANALOGICAL_UNIT_FINAL"),
    ("L046", "SCOOP", "UNIT", "HS046", "PROTO_SCOOP", "ʂƙɣƭɬ", "M", "ANALOGICAL_UNIT_FINAL"),
    ("L047", "DROP", "UNIT", "HS047", "PROTO_DROP", "ɗƥɓƭɬ", "M", "ANALOGICAL_UNIT_FINAL"),
    # Qualities and participants.
    ("L048", "DRY", "STATE", "HS048", "PROTO_DRY", "ɗƭɕƙɦ", "H", "NONE"),
    ("L049", "FRESH", "STATE", "HS049", "PROTO_FRESH", "ʋƥɕʂŋ", "H", "NONE"),
    ("L050", "FINE", "STATE", "HS050", "PROTO_FINE", "ɣŋƥɗʂ", "M", "NONE"),
    ("L051", "WARM", "STATE", "HS051", "PROTO_WARM", "ʐɓƭɱɦ", "M", "NONE"),
    ("L052", "SPOILED", "STATE", "HS052", "PROTO_BAD", "ʂƙɱɗʐ", "M", "NONE"),
    ("L053", "SEALED", "STATE", "HS053", "PROTO_CLOSED", "ƙɬʂɓʋ", "M", "NONE"),
    ("L054", "SUPPLIER_A", "PARTICIPANT", "HS054", "PROTO_HOUSE_A", "ɦɓɗɕŋ", "M", "NONE"),
    ("L055", "SUPPLIER_B", "PARTICIPANT", "HS055", "PROTO_HOUSE_B", "ɦɓɗʂƥ", "L", "NONE"),
    ("L056", "RECIPIENT", "PARTICIPANT", "HS056", "PROTO_PATIENT", "ƥɓʐɕɗ", "M", "NONE"),
    ("L057", "JAR", "CONTAINER", "HS057", "PROTO_JAR", "ƙɣɓƭŋ", "H", "NONE"),
    ("L058", "VIAL", "CONTAINER", "HS058", "PROTO_VIAL", "ʋɣɓɬƭ", "M", "NONE"),
    ("L059", "SHELF_A", "LOCATION", "HS059", "PROTO_SHELF_A", "ʂɦɓɬɗ", "H", "NONE"),
    ("L060", "SHELF_B", "LOCATION", "HS060", "PROTO_SHELF_B", "ʂɦɓɬʋ", "M", "NONE"),
    ("L061", "CELLAR", "LOCATION", "HS061", "PROTO_CELLAR", "ƙɬɓƭɱ", "M", "NONE"),
    ("L062", "BATCH", "REFERENCE", "HS062", "PROTO_BATCH", "ɓƭɕƭʂ", "H", "NONE"),
    # Function entries.  L063 is the bleached polyfunctional item.
    ("L063", "DEICTIC_DA", "FUNCTION", "HS063", "PROTO_AT", "ɗɓɦ", "H", "BLEACHED_POLYFUNCTIONAL"),
    ("L064", "MEASURE_LINK", "FUNCTION", "HS064", "PROTO_AS", "ɱɦƭ", "H", "CLITIC_OPTIONAL"),
    ("L065", "SOURCE_LINK", "FUNCTION", "HS065", "PROTO_FROM", "ʂƥɓɣ", "M", "CLITIC_OPTIONAL"),
    ("L066", "REFERENCE_LINK", "FUNCTION", "HS066", "PROTO_AGAIN", "ƭƥɕ", "M", "FREQUENCY_CLIP"),
    ("L067", "NEGATIVE", "FUNCTION", "HS067", "PROTO_NOT", "ŋɓʂ", "M", "NONE"),
    ("L068", "IMPERATIVE", "FUNCTION", "HS068", "PROTO_DO", "ƙƭɦ", "M", "CLITIC_OPTIONAL"),
    ("L069", "SEQUENCE_LINK", "FUNCTION", "HS069", "PROTO_THEN", "ɬɱɓ", "H", "CLITIC_OPTIONAL"),
    ("L070", "CAUSE_LINK", "FUNCTION", "HS070", "PROTO_BECAUSE", "ƙʂʋɕ", "L", "NONE"),
    ("L071", "DAILY", "FREQUENCY", "HS071", "PROTO_DAY", "ɗɓʋƭɣ", "M", "NONE"),
    ("L072", "TWICE_DAILY", "FREQUENCY", "HS072", "PROTO_TWO_DAY", "ɗʋɗɓɣ", "M", "FOSSILIZED_NUMERAL"),
)


def _entries() -> dict[str, dict[str, str]]:
    out = {}
    for row in _ENTRY_DATA:
        lex, entity, category, stem, proto, modern, freq, flags = row
        out[lex] = {
            "lexical_id": lex,
            "entity": entity,
            "category": category,
            "stem": stem,
            "proto": proto,
            "modern": modern,
            "frequency": freq,
            "flags": flags,
        }
    return out


ENTRIES = _entries()
BY_ENTITY = {v["entity"]: k for k, v in ENTRIES.items()}

MATERIALS = tuple(f"L{i:03d}" for i in range(1, 17))
PREPARATIONS = tuple(f"L{i:03d}" for i in range(17, 25))
QUANTITIES = tuple(f"L{i:03d}" for i in range(37, 43))
UNITS = tuple(f"L{i:03d}" for i in range(43, 48))
STATES = tuple(f"L{i:03d}" for i in range(48, 54))
SHELVES = ("L059", "L060", "L061")
CONTAINERS = ("L057", "L058")

FOSSILS = {
    "L017": ("FC_OLD_GRIND", "FC_OLD_WAX"),
    "L018": ("FC_OLD_HEAT", "FC_OLD_WINE"),
    "L019": ("FC_OLD_DRY", "FC_OLD_GRIND"),
    "L022": ("FC_OLD_DRINK", "FC_OLD_DOSE"),
    "L023": ("FC_OLD_BIND", "FC_OLD_WAX"),
    "L072": ("FC_OLD_TWO", "FC_OLD_DAY"),
}

# These are recorded historical allomorphs.  They intentionally cut across the
# general school rules and create merger, suppletion, and exception behavior.
SPECIAL_FORMS = {
    ("L002", "R1"): "ŋɕƥɣ",          # merger with mint in counter school
    ("L005", "R1"): "ŋɕƥɣ",
    ("L006", "R1"): "ƥɦɗɱ",          # partial merger with resin
    ("L011", "R1"): "ƥɦɗɱ",
    ("L013", "R2"): "ɬʋɗ",           # old liquid split by frame
    ("L020", "R2"): "ɬʋʐ",
    ("L025", "R2"): "ʐƥɗ",           # suppletive ledger count sign
    ("L027", "R2"): "ɱƥƙ",
    ("L032", "R2"): "ɣʂɬ",
    ("L037", "R2"): "ƥɓ",
    ("L038", "R2"): "ƥɗ",
    ("L063", "R2"): "ɗɦ",
    ("L066", "R1"): "ƭɕ",
}


GENEALOGY = (
    ("S00", "R00", "codebook_foundation", "WAREHOUSE_MNEMONICS", "HS001|HS002|HS003|HS004|HS005|HS006|HS007|HS008|HS009|HS010|HS011|HS012|HS013L|HS014|HS015|HS016|HS025|HS026|HS037|HS038|HS039|HS040|HS041|HS042", "first-generation stock and count entries", "NO", "Mnemonic labels are whole signs, not alphabetic encodings."),
    ("S01", "R01", "lexical_expansion", "WAREHOUSE_MNEMONICS|RECIPE_PHRASES", "HS017|HS018|HS019|HS021|HS022|HS023|HS024|HS027|HS028|HS029|HS030|HS031|HS032|HS033|HS034|HS035|HS036", "recipe copying becomes a second professional use", "NO", "New recipe labels freely borrow and reshape older stock signs."),
    ("S02", "R02", "frequency_driven_shortening", "L025|L026|L032|L063|L066", "CLIPPED_COUNT|CLIPPED_RECEIVE|CLIPPED_ISSUE|CLIPPED_DA|CLIPPED_REFERENCE", "high token frequency in running records", "NO", "Shortening affects different edges and is lexeme-specific."),
    ("S03", "R03", "merger", "L002|L005|L006|L011", "MERGER_ANISE_MINT_R1|MERGER_WAX_RESIN_R1", "counter-school R1 only; full copies retain contrasts", "NO", "Two independent register-limited mergers."),
    ("S04", "R04", "conditioned_split", "HS013L", "L013|L020", "ingredient frame yields oil; prepared-product frame yields syrup", "NO", "Later codebook copies lexicalize the two frame-conditioned readings."),
    ("S05", "R05", "semantic_bleaching", "L063:LOCATIVE", "L063:TOPIC|L063:COMPLETIVE|L063:DESTINATION", "record-initial, record-final, or transfer frame", "YES", "One surface family remains polyfunctional; the oracle records the active function."),
    ("S06", "R06", "fossilization", "OLD_GRIND+OLD_WAX|OLD_HEAT+OLD_WINE|OLD_DRY+OLD_GRIND|OLD_DRINK+OLD_DOSE|OLD_BIND+OLD_WAX|OLD_TWO+OLD_DAY", "L017|L018|L019|L022|L023|L072", "whole recipe labels become opaque lexical entries", "NO", "Historical components survive only in genealogy, not current compositional semantics."),
    ("S07", "R07", "analogy", "L043|L044|L045|L046|L047", "UNIT_CLASS_FINAL_ɬ", "membership in the measure-sign paradigm", "NO", "Unrelated measures acquire a common final by graphic analogy."),
    ("S08", "R08", "register_school_divergence", "FULL_COPY_TRADITION", "R0|R1|R2", "full copy, counter school, and bench ledger transmission", "NO", "R0 preserves longer forms; R1 clips frequent entries; R2 develops signs and suppletion."),
    ("S09", "R09", "suppletion_and_exceptions", "L025|L037|L038|L027|L032", "R2_SUPPLETIVES", "ledger register R2", "NO", "Count and two numerals use unrelated signs; two actions preserve local abbreviations."),
    ("S10", "R10", "hand_reshaping", "H0_FINALS", "H1_FINALS", "second hand after long or marked groups", "YES", "H1 changes selected final shapes but leaves protected analogical unit finals intact."),
    ("S11", "R11", "productive_attachment_and_clipping", "L063|L064|L065|L068|L069|HOST_GROUP", "JOINED_OR_DETACHED_REALIZATIONS", "construction, register, and physical line position", "YES", "Optional clitic fusion and final-position clipping create ambiguous group boundaries."),
)


def _weighted(rng, values, weights):
    return rng.choices(values, weights=weights, k=1)[0]


def _pick_material(rng):
    return _weighted(rng, MATERIALS, (15, 13, 9, 18, 20, 17, 18, 16, 5, 10, 12, 8, 21, 9, 7, 4))


def _pick_prep(rng):
    return _weighted(rng, PREPARATIONS, (20, 18, 22, 14, 10, 12, 7, 5))


def _pick_quantity(rng):
    return _weighted(rng, QUANTITIES, (28, 26, 17, 12, 10, 7))


def _pick_unit(rng):
    return _weighted(rng, UNITS, (30, 22, 17, 18, 13))


def _spec(lex: str, function: str = "CONTENT", relation: str = "NONE",
          target: Any = None, components: tuple[str, ...] = (),
          component_semantics: tuple[str, ...] = (), productive: str = "NO") -> dict[str, Any]:
    return {
        "lex": lex, "function": function, "relation": relation,
        "target": target, "components": components,
        "component_semantics": component_semantics,
        "productive": productive,
    }


def _inventory(rng):
    mat = _pick_material(rng)
    specs = [
        _spec("L063", "TOPIC", "SCOPE_HEAD", 1),
        _spec("L025", "PREDICATE"),
        _spec(mat, "ENTITY", "ARGUMENT_OF", 1),
        _spec(_pick_quantity(rng), "QUANTITY", "QUANTITY_OF", 2),
        _spec("L064", "MEASURE_LINK", "LINKS", 2),
        _spec(_pick_unit(rng), "UNIT", "UNIT_OF", 2),
        _spec(_weighted(rng, ("L048", "L049", "L053"), (5, 6, 2)), "STATE", "STATE_OF", 2),
        _spec(_weighted(rng, SHELVES, (6, 3, 2)), "LOCATION", "LOCATION_OF", 2),
    ]
    if rng.random() < .42:
        specs.append(_spec("L066", "REFERENCE", "PREVIOUS_MENTION", ("previous", mat)))
    if rng.random() < .55:
        specs.append(_spec("L062", "REFERENCE", "IDENTIFIES", 2))
    specs.append(_spec("L063", "COMPLETIVE", "SCOPE_TAIL", 1))
    return "SCHEMA_INVENTORY", mat, 0, specs


def _receipt(rng):
    mat = _pick_material(rng)
    supplier = _weighted(rng, ("L054", "L055"), (4, 1))
    specs = [
        _spec("L026", "PREDICATE"),
        _spec(mat, "ENTITY", "ARGUMENT_OF", 0),
        _spec(_pick_quantity(rng), "QUANTITY", "QUANTITY_OF", 1),
        _spec(_pick_unit(rng), "UNIT", "UNIT_OF", 1),
        _spec("L065", "SOURCE_LINK", "LINKS", 5),
        _spec(supplier, "SOURCE", "SOURCE_OF", 1),
        _spec("L035", "PREDICATE", "SEQUENCE_AFTER", 0),
        _spec(_weighted(rng, ("L048", "L049", "L053"), (3, 7, 2)), "STATE", "STATE_OF", 1),
        _spec("L062", "REFERENCE", "IDENTIFIES", 1),
    ]
    if rng.random() < .55:
        specs.insert(-1, _spec(_weighted(rng, CONTAINERS, (3, 1)), "CONTAINER", "CONTAINER_OF", 1))
    specs.append(_spec("L063", "COMPLETIVE", "SCOPE_TAIL", 0))
    return "SCHEMA_RECEIPT", mat, rng.choice((1, 2, 3, 4, 6, 12)), specs


def _preparation(rng):
    prep = _pick_prep(rng)
    mat1 = _pick_material(rng)
    mat2 = _pick_material(rng)
    while mat2 == mat1:
        mat2 = _pick_material(rng)
    operation = _weighted(rng, ("L027", "L028", "L029", "L030"), (5, 4, 7, 2))
    specs = [
        _spec("L068", "IMPERATIVE", "SCOPE_HEAD", 1),
        _spec(prep, "RESULT", "RESULT_OF", 6),
        _spec(mat1, "INGREDIENT", "INGREDIENT_OF", 1),
        _spec(_pick_quantity(rng), "QUANTITY", "QUANTITY_OF", 2),
        _spec(_pick_unit(rng), "UNIT", "UNIT_OF", 2),
        _spec("L069", "SEQUENCE_LINK", "LINKS", 6),
        _spec(operation, "PREDICATE", "PRODUCES", 1),
        _spec(mat2, "INGREDIENT", "INGREDIENT_OF", 1),
        _spec(_weighted(rng, ("L050", "L051"), (3, 2)), "STATE", "RESULT_STATE_OF", 1),
        _spec(_weighted(rng, CONTAINERS, (3, 2)), "CONTAINER", "CONTAINER_OF", 1),
        _spec("L031", "PREDICATE", "SEQUENCE_AFTER", 6),
        _spec("L062", "REFERENCE", "IDENTIFIES", 1),
        _spec("L063", "COMPLETIVE", "SCOPE_TAIL", 1),
    ]
    if rng.random() < .35:
        specs.insert(10, _spec("L036", "PREDICATE", "SEQUENCE_AFTER", 6))
    return "SCHEMA_PREPARATION", prep, rng.choice((1, 2, 3)), specs[:14]


def _dispense(rng):
    prep = _pick_prep(rng)
    specs = [
        _spec("L068", "IMPERATIVE", "SCOPE_HEAD", 1),
        _spec("L032", "PREDICATE"),
        _spec(prep, "ENTITY", "ARGUMENT_OF", 1),
        _spec(_pick_quantity(rng), "QUANTITY", "QUANTITY_OF", 2),
        _spec(_pick_unit(rng), "UNIT", "UNIT_OF", 2),
        _spec("L056", "RECIPIENT", "RECIPIENT_OF", 1),
        _spec(_weighted(rng, ("L071", "L072"), (3, 2)), "FREQUENCY", "INSTRUCTION_FOR", 2),
        _spec("L066", "REFERENCE", "PREVIOUS_MENTION", ("previous", prep)),
        _spec("L063", "COMPLETIVE", "SCOPE_TAIL", 1),
    ]
    return "SCHEMA_DISPENSE", prep, -rng.choice((1, 2)), specs


def _loss(rng):
    mat = _pick_material(rng)
    specs = [
        _spec(mat, "ENTITY", "ARGUMENT_OF", 2),
        _spec("L052", "STATE", "STATE_OF", 0),
        _spec("L033", "PREDICATE"),
        _spec(_pick_quantity(rng), "QUANTITY", "QUANTITY_OF", 0),
        _spec(_pick_unit(rng), "UNIT", "UNIT_OF", 0),
        _spec("L070", "CAUSE_LINK", "LINKS", 1),
        _spec(_weighted(rng, ("L051", "L067"), (2, 1)), "CAUSE", "CAUSE_OF", 2),
        _spec("L062", "REFERENCE", "IDENTIFIES", 0),
        _spec("L063", "COMPLETIVE", "SCOPE_TAIL", 2),
    ]
    return "SCHEMA_LOSS", mat, -rng.choice((1, 2, 3, 4)), specs


def _transfer(rng):
    mat = _pick_material(rng)
    origin = _weighted(rng, SHELVES, (6, 3, 2))
    dest = _weighted(rng, SHELVES, (4, 4, 2))
    while dest == origin:
        dest = _weighted(rng, SHELVES, (4, 4, 2))
    specs = [
        _spec("L034", "PREDICATE"),
        _spec(mat, "ENTITY", "ARGUMENT_OF", 0),
        _spec(_pick_quantity(rng), "QUANTITY", "QUANTITY_OF", 1),
        _spec(_pick_unit(rng), "UNIT", "UNIT_OF", 1),
        _spec("L065", "SOURCE_LINK", "LINKS", 5),
        _spec(origin, "SOURCE", "SOURCE_OF", 1),
        _spec("L063", "DESTINATION", "LINKS", 7),
        _spec(dest, "DESTINATION", "DESTINATION_OF", 1),
        _spec("L062", "REFERENCE", "IDENTIFIES", 1),
        _spec("L063", "COMPLETIVE", "SCOPE_TAIL", 0),
    ]
    return "SCHEMA_TRANSFER", mat, 0, specs


RECORD_BUILDERS = (_inventory, _receipt, _preparation, _dispense, _loss, _transfer)


def _surface(entry: dict[str, str], register: str, hand: str,
             position: str, construction: str, rng) -> tuple[str, tuple[str, ...], tuple[str, ...], str]:
    lex = entry["lexical_id"]
    form = SPECIAL_FORMS.get((lex, register), entry["modern"])
    morphemes = [lex]
    component_semantics = [entry["entity"]]
    productive = "NO"

    # School changes are probabilistic within historically licensed zones.
    if (lex, register) not in SPECIAL_FORMS:
        if register == "R0" and entry["frequency"] == "L" and rng.random() < .45:
            form = form + "ɣ"                 # conservative rubric flourish
        elif register == "R1" and entry["frequency"] == "H" and len(form) > 5:
            form = form[0:2] + form[3:]       # inherited medial clipping
        elif register == "R2":
            if entry["category"] in {"ACTION", "FUNCTION", "QUANTITY"}:
                form = form[:2] + form[-1]
            elif len(form) > 5:
                form = form[0] + form[2:5]

    # The bleached particle and four old clitics can fuse to an adjacent host.
    # Fusion does not erase lexical identity in the oracle.
    if entry["category"] not in {"FUNCTION"} and construction in {
        "SCHEMA_PREPARATION", "SCHEMA_DISPENSE", "SCHEMA_TRANSFER"
    } and rng.random() < (.22 if register != "R0" else .10):
        clitic = "CL_SEQ" if construction == "SCHEMA_PREPARATION" else "CL_DA"
        glyph = "ɬ" if clitic == "CL_SEQ" else "ɗ"
        if rng.random() < .5:
            form = glyph + form
        else:
            form = form + glyph
        morphemes.append(clitic)
        component_semantics.append("SEQUENCE" if clitic == "CL_SEQ" else "FRAME_LINK")
        productive = "YES"

    # Productive record/line-final clipping, blocked by analogical unit finals.
    if position == "FINAL" and register != "R0" and len(form) > 3 and entry["category"] != "UNIT":
        if rng.random() < .48:
            form = form[:-1]
            morphemes.append("MOR_FINAL_CLIP")
            productive = "YES"

    # H1 inherited a graphic final alternation.  It is not a full substitution.
    if hand == "H1" and entry["category"] != "UNIT" and len(form) > 3:
        hmap = {"ɦ": "ʂ", "ɗ": "ʋ", "ƭ": "ɬ", "ŋ": "ɱ"}
        if form[-1] in hmap and rng.random() < .72:
            form = form[:-1] + hmap[form[-1]]
            morphemes.append("HAND_H1_FINAL")

    return form, tuple(morphemes), tuple(component_semantics), productive


def _codebook_rows() -> list[dict[str, str]]:
    rows = []
    for lex in sorted(ENTRIES):
        e = ENTRIES[lex]
        special = [f"{reg}:{form}" for (lx, reg), form in sorted(SPECIAL_FORMS.items()) if lx == lex]
        rules = [
            f"current={e['modern']}",
            "R0=full_copy_with_optional_rare_flourish",
            "R1=licensed_high_frequency_medial_clip_on_long_forms",
            "R2=category_conditioned_ledger_reduction",
            "H1=conditioned_final_reshaping_except_units",
            "record_or_line_final=productive_clip_outside_R0_except_units",
        ]
        if special:
            rules.append("fixed_allomorphs=" + ",".join(special))
        if e["category"] != "FUNCTION":
            rules.append("recipe_dispense_transfer=optional_CL_SEQ_or_CL_DA_fusion")
        rows.append({
            "lexical_id": lex,
            "semantic_entity_id": "SEM_" + e["entity"],
            "semantic_category": e["category"],
            "historical_stem_id": e["stem"],
            "canonical_hidden_form": e["proto"],
            "final_realization_rules": ";".join(rules),
            "irregularity_flags": e["flags"],
        })
    return rows


def _genealogy_rows() -> list[dict[str, str]]:
    return [
        {
            "stage": stage, "rule_id": rule, "process_type": process,
            "input_ids": inputs, "output_ids": outputs,
            "conditioning": conditioning, "currently_productive": productive,
            "notes": notes,
        }
        for stage, rule, process, inputs, outputs, conditioning, productive, notes in GENEALOGY
    ]


def _line_sizes(n: int, rng) -> list[int]:
    """Partition a 6--14 group record into physical lines of 4--9 groups."""
    if n <= 9:
        return [n]
    low = max(4, n - 9)
    high = min(9, n - 4)
    first = rng.randint(low, high)
    return [first, n - first]


def generate(seed: int, target_events: int = 8448) -> dict[str, list[dict]]:
    if not isinstance(seed, int):
        raise TypeError("seed must be an int")
    if not isinstance(target_events, int) or target_events < 1:
        raise ValueError("target_events must be a positive int")
    rng = seeded_rng("W02", seed)
    observations: list[dict[str, str]] = []
    oracle: list[dict[str, str]] = []
    stock = defaultdict(lambda: 18)
    last_event_by_lex: dict[str, str] = {}
    record_no = 0
    event_no = 0

    while event_no < target_events:
        record_no += 1
        page_no = (record_no - 1) // 14 + 1
        record_on_page = (record_no - 1) % 14
        paragraph_no = (record_on_page // 5) + 1
        register = _weighted(rng, REGISTERS, (58, 28, 14))
        hand = _weighted(rng, HANDS, (73, 27))
        builder = _weighted(rng, RECORD_BUILDERS, (31, 17, 20, 15, 7, 10))
        schema, focus_lex, delta, specs = builder(rng)
        if not 6 <= len(specs) <= 14:
            raise AssertionError("record outside carrier bound")

        line_sizes = _line_sizes(len(specs), rng)
        line_for_index = {}
        line_pos_for_index = {}
        cursor = 0
        for line_offset, size in enumerate(line_sizes):
            for local in range(size):
                idx = cursor + local
                line_for_index[idx] = line_offset
                if local == 0:
                    line_pos_for_index[idx] = "INITIAL"
                elif local == size - 1:
                    line_pos_for_index[idx] = "FINAL"
                else:
                    line_pos_for_index[idx] = "MEDIAL"
            cursor += size

        # Materialize every within-record boundary exactly once.  Both adjacent
        # observation rows then receive the same value, including physical line
        # transitions and ambiguous JOIN/NONE boundaries.
        internal_boundaries = {}
        for boundary_index in range(1, len(specs)):
            if line_for_index[boundary_index - 1] != line_for_index[boundary_index]:
                boundary = "LINE"
            elif specs[boundary_index - 1]["lex"] in {"L063", "L064", "L065", "L068", "L069"} and rng.random() < .30:
                boundary = "JOIN"
            elif rng.random() < .08:
                boundary = "FIELD"
            elif rng.random() < .04:
                boundary = "NONE"
            else:
                boundary = "SPACE"
            internal_boundaries[boundary_index] = boundary

        record_boundary_before = (
            "PAGE" if record_on_page == 0
            else "PARAGRAPH" if record_on_page % 5 == 0
            else "RECORD"
        )
        record_boundary_after = (
            "PAGE" if record_on_page == 13
            else "PARAGRAPH" if record_on_page in {4, 9}
            else "RECORD"
        )

        event_ids = [stable_id("E", "W02", seed, event_no + i) for i in range(len(specs))]
        scope_start = event_ids[0]
        scope_end = event_ids[-1]
        state_before = stock[focus_lex]
        state_after = max(0, state_before + delta)
        stock[focus_lex] = state_after

        for i, spec in enumerate(specs):
            global_index = event_no + i
            event_id = event_ids[i]
            line_offset = line_for_index[i]
            line_position = line_pos_for_index[i]
            entry = ENTRIES[spec["lex"]]
            form, surface_morphs, surface_semantics, surfaced_productive = _surface(
                entry, register, hand, line_position, schema, rng
            )
            all_morphs = tuple(spec["components"]) + surface_morphs
            all_semantics = tuple(spec["component_semantics"]) + surface_semantics
            productive = "YES" if spec["productive"] == "YES" or surfaced_productive == "YES" else "NO"

            target = spec["target"]
            if isinstance(target, int):
                relation_target = event_ids[target]
            elif isinstance(target, tuple) and target[0] == "previous":
                relation_target = last_event_by_lex.get(target[1], "NONE")
            else:
                relation_target = "NONE"

            if i == 0:
                before = record_boundary_before
            else:
                before = internal_boundaries[i]
            if i == len(specs) - 1:
                after = record_boundary_after
            else:
                after = internal_boundaries[i + 1]
            ambiguous = "YES" if before in {"JOIN", "NONE"} or after in {"JOIN", "NONE"} or "CL_" in pipe(all_morphs) else "NO"

            observations.append({
                "world_id": "W02",
                "corpus_seed": str(seed),
                "event_id": event_id,
                "page_id": f"P{page_no:04d}",
                "paragraph_id": f"P{page_no:04d}A{paragraph_no:02d}",
                "record_id": f"R{record_no:06d}",
                "line_id": f"R{record_no:06d}L{line_offset + 1:02d}",
                "event_index": str(global_index),
                "group_index": str(i),
                "visible_group": form,
                "separator_before": before,
                "separator_after": after,
                "register_id": register,
                "hand_id": hand,
                "layout_role": "L0" if i == 0 else ("L2" if i == len(specs) - 1 else "L1"),
                "line_position_bin": {"INITIAL": "B0", "MEDIAL": "B1", "FINAL": "B2"}[line_position],
                "record_position_bin": "B0" if i < len(specs) / 3 else ("B2" if i >= 2 * len(specs) / 3 else "B1"),
                "ambiguous_boundary": ambiguous,
            })

            fossils = FOSSILS.get(spec["lex"], ())
            active_state_before = f"stock:{state_before}" if spec["lex"] == focus_lex or spec["relation"] in {"ARGUMENT_OF", "RESULT_OF"} else "NONE"
            active_state_after = f"stock:{state_after}" if spec["lex"] == focus_lex or spec["relation"] in {"ARGUMENT_OF", "RESULT_OF"} else "NONE"
            is_scoped = schema in {"SCHEMA_PREPARATION", "SCHEMA_DISPENSE"} or spec["function"] in {"TOPIC", "COMPLETIVE", "DESTINATION"}
            oracle.append({
                "world_id": "W02",
                "corpus_seed": str(seed),
                "event_id": event_id,
                "domain_id": "APOTHECARY",
                "activity_id": schema.removeprefix("SCHEMA_"),
                "lexical_id": spec["lex"],
                "semantic_entity_id": "SEM_" + entry["entity"],
                "semantic_category": entry["category"],
                "function_class": spec["function"],
                "relation_type": spec["relation"],
                "relation_target_event_id": relation_target,
                "state_before": active_state_before,
                "state_after": active_state_after,
                "historical_stem_id": entry["stem"],
                "current_morpheme_ids": pipe(all_morphs),
                "fossilized_component_ids": pipe(fossils),
                "construction_id": schema,
                "scope_start_event_id": scope_start if is_scoped else "NONE",
                "scope_end_event_id": scope_end if is_scoped else "NONE",
                "record_schema_id": schema,
                "register_realization_id": f"{register}_{hand}",
                "productive_morphology": "TRUE" if productive == "YES" else "FALSE",
                "current_component_semantics": pipe(all_semantics),
                "genealogy_stage": "S11",
            })
            last_event_by_lex[spec["lex"]] = event_id

        event_no += len(specs)

    return {
        "observations": observations,
        "oracle": oracle,
        "codebook": _codebook_rows(),
        "genealogy": _genealogy_rows(),
    }


__all__ = ["WORLD_META", "generate"]
