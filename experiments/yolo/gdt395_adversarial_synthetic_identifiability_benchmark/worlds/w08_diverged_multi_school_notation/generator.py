#!/usr/bin/env python3
"""Deterministic generator for GDT395 synthetic world W08."""

from __future__ import annotations

import hashlib
import random
from typing import Any


WORLD_ID = "W08"
GLYPHS = (
    "ƛ", "ȣ", "ʘ", "ʚ", "ϟ", "Ϟ", "Ͽ", "҂", "Ҙ", "Ӝ", "Ӿ", "Ө",
    "Ѧ", "Ѯ", "ⴲ", "ⴴ", "ⴷ", "ⵁ", "ⵔ", "ⵙ", "Ꙩ", "Ꙭ", "Ꚛ",
    "ꜛ", "ꜜ", "⊣", "⊢", "⋔", "⋉", "⌁", "⌇", "◇", "·",
)

WORLD_META = {
    "world_id": WORLD_ID,
    "title": "The Divided Casebook Hands",
    "broad_family": "DIVERGED_MULTI_SCHOOL_NOTATION",
    "practical_domain": "medical teaching and case procedure",
    "semantics_light": False,
    "organic_evolution": True,
    "clean_engineered_control": False,
    "adversarial_pair_id": "NONE",
    "carrier_profile": "CARRIER_SCHOOLS",
    "alphabet": list(GLYPHS),
    "registers": ["S0", "S1", "S2", "S3"],
    "hands": ["H0", "H1", "H2"],
    "evolution_processes": [
        "frequency_shortening", "analogy", "merger", "semantic_split",
        "bleaching", "fossilization", "homography", "polyfunctionality",
        "suppletion", "productive_innovation", "regional_variation",
        "positional_allography",
    ],
    "generator_schema": "GDT395_WORLD_GENERATOR_V1",
}


# lexical_id, entity, category, historical stem, inherited glyphs, weight
_LEX_ROWS = [
    ("LX_PAT", "patient", "ENTITY_PERSON", "HS_PERSON", "ʘѦ", 18),
    ("LX_TEACH", "teacher", "ENTITY_PERSON", "HS_ELDER", "Ѯƛ", 4),
    ("LX_WOUND", "wound", "ENTITY_CONDITION", "HS_CUT", "Ҙⴷ", 10),
    ("LX_FEVER", "fever", "ENTITY_CONDITION", "HS_FIRE", "Ӝϟ", 12),
    ("LX_COUGH", "cough", "ENTITY_CONDITION", "HS_BREATH_BREAK", "ȣ҂", 8),
    ("LX_PAIN", "pain", "ENTITY_CONDITION", "HS_STING", "ϞҘ", 14),
    ("LX_SWELL", "swelling", "ENTITY_CONDITION", "HS_RISE", "ӜꙨ", 7),
    ("LX_BLOOD", "blood", "ENTITY_SUBSTANCE", "HS_RED_FLUID", "Ꙭʚ", 7),
    ("LX_BREATH", "breath", "ENTITY_MEASURE", "HS_WIND", "ȣⵁ", 7),
    ("LX_URINE", "urine", "ENTITY_MEASURE", "HS_WATER_CAST", "ⴴꚚ", 5),
    ("LX_PULSE", "pulse", "ENTITY_MEASURE", "HS_BEAT", "⋔⋉", 11),
    ("LX_LIMB", "limb", "ENTITY_BODY", "HS_BRANCH", "ⵔѦ", 5),
    ("LX_EYE", "eye", "ENTITY_BODY", "HS_EYE", "Ꙩ", 4),
    ("LX_BROTH", "broth", "ENTITY_MATERIAL", "HS_WATER_FOOD", "ⴴⵙ", 5),
    ("LX_SALVE", "salve", "ENTITY_MATERIAL", "HS_SMOOTH", "ӨꚚ", 7),
    ("LX_HERB", "herb", "ENTITY_MATERIAL", "HS_LEAF", "ⵙƛ", 6),
    ("LX_BAND", "bandage", "ENTITY_MATERIAL", "HS_CLOTH", "⊣ⴲ", 7),
    ("LX_HEAT", "heated_stone", "ENTITY_MATERIAL", "HS_FIRE_STONE", "Ӝ◇", 4),
    ("LX_OBS", "observe", "ACTION_EXAMINATION", "HS_EYE_TAKE", "Ꙩ⌇", 15),
    ("LX_WASH", "wash", "ACTION_PROCEDURE", "HS_WATER_HAND", "ⴴ⌁", 9),
    ("LX_BIND", "bind", "ACTION_PROCEDURE", "HS_CLOTH_HAND", "⊣⌁", 10),
    ("LX_WARM", "warm", "ACTION_PROCEDURE", "HS_FIRE_NEAR", "Ӝⴲ", 5),
    ("LX_COOL", "cool", "ACTION_PROCEDURE", "HS_WATER_NEAR", "ⴴⴲ", 7),
    ("LX_BLEED", "draw_blood", "ACTION_PROCEDURE", "HS_RED_OPEN", "Ꙭⴷ", 3),
    ("LX_GIVE", "administer", "ACTION_PROCEDURE", "HS_HAND_PASS", "⌁⊢", 10),
    ("LX_REST", "rest", "ACTION_CARE", "HS_LIE", "Ѧ⋉", 8),
    ("LX_COMPARE", "compare", "ACTION_TEACHING", "HS_TWO_EYE", "ꙨꙨ", 5),
    ("LX_REPORT", "report", "ACTION_TEACHING", "HS_MOUTH_RETURN", "Ͽȣ", 6),
    ("LX_REPEAT", "repeat", "ACTION_TEACHING", "HS_TURN", "⌇⌇", 7),
    ("LX_AVOID", "avoid", "ACTION_WARNING", "HS_TURN_AWAY", "⌇ʚ", 5),
    ("LX_HOT", "hot", "STATE_QUALITY", "HS_FIRE_HIGH", "Ӝꜛ", 9),
    ("LX_COLD", "cold", "STATE_QUALITY", "HS_WATER_LOW", "ⴴꜜ", 6),
    ("LX_DRY", "dry", "STATE_QUALITY", "HS_EMPTY", "ϟ◇", 5),
    ("LX_WET", "wet", "STATE_QUALITY", "HS_WATER_FULL", "ⴴʘ", 5),
    ("LX_SEV", "severe", "STATE_DEGREE", "HS_HIGH", "ꜛҘ", 10),
    ("LX_MILD", "mild", "STATE_DEGREE", "HS_LOW", "ꜜӨ", 7),
    ("LX_BETTER", "improving", "STATE_CHANGE", "HS_RISE_GOOD", "Ꙩ⊢", 7),
    ("LX_WORSE", "worsening", "STATE_CHANGE", "HS_FALL_BAD", "Ꙭ⊣", 5),
    ("LX_HAS", "possesses_symptom", "RELATION_POSSESSION", "HS_HOLD", "⌁ʘ", 14),
    ("LX_LOC", "located_at", "RELATION_LOCATION", "HS_AT", "ⵁ", 12),
    ("LX_CAUSE", "caused_by", "RELATION_CAUSAL", "HS_FROM", "ʚⵁ", 5),
    ("LX_NEXT", "then_relation", "RELATION_SEQUENCE", "HS_FOLLOW", "⊢", 14),
    ("LX_FOR", "treatment_for", "RELATION_PURPOSE", "HS_TOWARD", "ⵔ", 9),
    ("LX_RPAT", "current_patient", "REFERENCE_PERSON", "HS_PERSON_SHORT", "ʘ", 16),
    ("LX_RPREV", "previous_finding", "REFERENCE_ANAPHOR", "HS_BACK", "ʚ", 12),
    ("LX_RITEM", "prepared_item", "REFERENCE_OBJECT", "HS_NEAR", "ⴲ", 8),
    ("LX_RAUTH", "teacher_authority", "REFERENCE_SOURCE", "HS_ELDER_SHORT", "Ѯ", 4),
    ("LX_IF", "conditional_scope", "SCOPE_CONDITION", "HS_TURN_IF", "⌇Ͽ", 9),
    ("LX_THEN", "consequent_scope", "SCOPE_CONSEQUENT", "HS_FOLLOW", "⊢", 9),
    ("LX_END", "scope_closure", "SCOPE_CLOSURE", "HS_CLOSE", "⊣", 9),
    ("LX_NOT", "negation", "FUNCTION_POLARITY", "HS_AWAY", "ʚ", 6),
    ("LX_ASSERT", "teaching_assertion", "FUNCTION_EVIDENTIAL", "HS_ELDER_SEE", "ѮꙨ", 7),
    ("LX_COUNT", "dosage_count", "FUNCTION_QUANTITY", "HS_BEAT_COUNT", "⋔⌇", 5),
    ("LX_TOPIC", "case_topic", "FUNCTION_DISCOURSE", "HS_LIFT", "ꜛ", 9),
]

LEXICON = {
    row[0]: {
        "lexical_id": row[0], "entity": row[1], "category": row[2],
        "stem": row[3], "form": row[4], "weight": row[5],
    }
    for row in _LEX_ROWS
}

ENTITIES = ["LX_WOUND", "LX_FEVER", "LX_COUGH", "LX_PAIN", "LX_SWELL"]
MEASURES = ["LX_BLOOD", "LX_BREATH", "LX_URINE", "LX_PULSE"]
BODIES = ["LX_LIMB", "LX_EYE"]
MATERIALS = ["LX_BROTH", "LX_SALVE", "LX_HERB", "LX_BAND", "LX_HEAT"]
PROCEDURES = ["LX_WASH", "LX_BIND", "LX_WARM", "LX_COOL", "LX_BLEED", "LX_GIVE", "LX_REST"]
QUALITIES = ["LX_HOT", "LX_COLD", "LX_DRY", "LX_WET"]
DEGREES = ["LX_SEV", "LX_MILD"]

GENEALOGY = [
    {"stage": "1", "rule_id": "EV01", "process_type": "mnemonic_formation", "input_ids": "spoken case prompts|object sketches", "output_ids": "HS_PERSON|HS_CUT|HS_FIRE|HS_WATER_HAND|HS_EYE_TAKE", "conditioning": "infirmary teaching demonstrations", "currently_productive": "false", "notes": "Mixed word signs and rebus compounds establish the shared core."},
    {"stage": "2", "rule_id": "EV02", "process_type": "frequency_shortening", "input_ids": "HS_PERSON|HS_AT|HS_FOLLOW|HS_BACK", "output_ids": "AB_PERSON|AB_AT|AB_FOLLOW|AB_BACK", "conditioning": "high-frequency case slots", "currently_productive": "false", "notes": "Independent words shorten unevenly; some collide with inherited signs."},
    {"stage": "3", "rule_id": "EV03", "process_type": "lexicalization", "input_ids": "HS_WATER+HS_HAND|HS_EYE+HS_TAKE|HS_CLOTH+HS_HAND", "output_ids": "HS_WATER_HAND|HS_EYE_TAKE|HS_CLOTH_HAND", "conditioning": "recurring procedure demonstrations", "currently_productive": "false", "notes": "Compounds become indivisible lexical stems."},
    {"stage": "3", "rule_id": "EV04", "process_type": "fossilization", "input_ids": "HS_WATER_HAND|HS_EYE_TAKE", "output_ids": "FC_WATER|FC_EYE", "conditioning": "after lexicalization and phonetic erosion", "currently_productive": "false", "notes": "Old components survive graphically without current component meaning."},
    {"stage": "4", "rule_id": "EV05", "process_type": "analogy", "input_ids": "procedure commands", "output_ids": "PM_ACTION_CUE", "conditioning": "demonstration-frame actions", "currently_productive": "true", "notes": "A recurrent action cue spreads beyond compounds, with lexical omissions."},
    {"stage": "4", "rule_id": "EV06", "process_type": "bleaching", "input_ids": "HS_HAND", "output_ids": "PM_ACTION_CUE", "conditioning": "preposed in procedure frames", "currently_productive": "true", "notes": "HAND loses lexical content in one daughter school."},
    {"stage": "5", "rule_id": "EV07", "process_type": "school_divergence", "input_ids": "shared casebook hand", "output_ids": "S0|S1|S2|S3", "conditioning": "separate teaching lineages", "currently_productive": "false", "notes": "Archive, ward, littoral, and itinerant norms diverge."},
    {"stage": "6", "rule_id": "EV08", "process_type": "merger", "input_ids": "LX_FEVER|LX_SWELL|LX_WASH|LX_COOL", "output_ids": "MG_WARD_RISE|MG_WARD_WATER", "conditioning": "S1 rapid ward notation", "currently_productive": "true", "notes": "Two pairs merge, one across distinct procedures."},
    {"stage": "6", "rule_id": "EV09", "process_type": "semantic_split", "input_ids": "LX_PAIN", "output_ids": "SP_PAIN_MILD|SP_PAIN_SEVERE", "conditioning": "S2 following degree context", "currently_productive": "true", "notes": "One inherited sign splits by severity and later extends analogically."},
    {"stage": "6", "rule_id": "EV10", "process_type": "reanalysis", "input_ids": "LX_LOC", "output_ids": "PM_S2_EVIDENTIAL", "conditioning": "S2 clause-final teaching assertions", "currently_productive": "true", "notes": "The old locative is rebound as witnessed-evidence marking."},
    {"stage": "7", "rule_id": "EV11", "process_type": "suppletion", "input_ids": "LX_BIND|LX_GIVE|LX_REPORT", "output_ids": "SU_BIND|SU_GIVE|SU_REPORT", "conditioning": "S3 frequent oral commands", "currently_productive": "false", "notes": "Borrowed command signs replace inherited roots in the itinerant school."},
    {"stage": "7", "rule_id": "EV12", "process_type": "productive_reduplication", "input_ids": "initial glyph", "output_ids": "PM_REPEAT", "conditioning": "S3 iterative actions and worsening states", "currently_productive": "true", "notes": "Initial copying marks iteration but is blocked in suppletive commands."},
    {"stage": "8", "rule_id": "EV13", "process_type": "polyfunctionality", "input_ids": "AB_BACK|AB_FOLLOW|AB_AT", "output_ids": "reference|sequence|scope|evidential", "conditioning": "school-specific construction slots", "currently_productive": "true", "notes": "Short signs acquire multiple grammatical functions."},
    {"stage": "8", "rule_id": "EV14", "process_type": "exceptional_leveling", "input_ids": "LX_OBS|LX_REST|LX_AVOID", "output_ids": "EX_CUELESS_ACTIONS", "conditioning": "lexically listed commands", "currently_productive": "false", "notes": "Frequent actions resist the productive ward action cue."},
    {"stage": "9", "rule_id": "EV15", "process_type": "regional_allography", "input_ids": "shared glyph inventory", "output_ids": "H0|H1|H2", "conditioning": "copyist hand and line position", "currently_productive": "true", "notes": "Lead strokes, final tails, joins, and allographs obscure school correspondences."},
]


def _rng(seed: int) -> random.Random:
    raw = hashlib.sha256(f"GDT395:{WORLD_ID}:{seed}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))


def _sid(prefix: str, *parts: object) -> str:
    raw = "\x1f".join(map(str, parts)).encode()
    return f"{prefix}_{hashlib.sha256(raw).hexdigest()[:12]}"


def _pipe(*values: str) -> str:
    vals = sorted({v for v in values if v and v != "NONE"})
    return "|".join(vals) if vals else "NONE"


def _choice(rng: random.Random, values: list[str]) -> str:
    weights = [LEXICON[v]["weight"] for v in values]
    return rng.choices(values, weights=weights, k=1)[0]


def _event(lex: str, function: str | None = None, **kwargs: Any) -> dict[str, Any]:
    item = LEXICON[lex]
    row: dict[str, Any] = {
        "lex": lex,
        "function": function or item["category"].split("_", 1)[0],
        "relation": "NONE",
        "target": None,
        "before": "NONE",
        "after": "NONE",
        "productive": "NONE",
        "components": item["entity"],
        "fossils": "NONE",
        "scope_start": None,
        "scope_end": None,
        "role": "L1",
    }
    row.update(kwargs)
    return row


def _case_record(rng: random.Random) -> tuple[list[dict[str, Any]], str, str]:
    symptom = _choice(rng, ENTITIES)
    measure = _choice(rng, MEASURES)
    body = _choice(rng, BODIES)
    degree = _choice(rng, DEGREES)
    quality = _choice(rng, QUALITIES)
    action = _choice(rng, PROCEDURES)
    material = _choice(rng, MATERIALS)
    result = rng.choices(["LX_BETTER", "LX_WORSE"], weights=[4, 1], k=1)[0]
    ev = [
        _event("LX_TOPIC", "DISCOURSE", role="L0"),
        _event("LX_PAT", "ENTITY", role="L0"),
        _event(symptom, "ENTITY", relation="POSSESSED_BY", target=1),
        _event("LX_HAS", "RELATION", relation="LINKS", target=2),
        _event(degree, "STATE", relation="MODIFIES", target=2),
        _event(measure, "ENTITY", relation="OBSERVED_IN", target=1),
        _event(quality, "STATE", relation="MODIFIES", target=5),
        _event("LX_LOC", "RELATION", relation="LOCATES", target=2),
        _event(body, "ENTITY", relation="LOCATION_OF", target=2),
        _event("LX_IF", "SCOPE", relation="CONDITION_ON", target=2),
        _event(action, "ACTION", relation="ACTS_ON", target=2),
        _event("LX_NEXT", "RELATION", relation="SEQUENCES", target=10),
        _event("LX_GIVE" if action != "LX_GIVE" else "LX_BIND", "ACTION", relation="USES", target=13),
        _event(material, "ENTITY", relation="INSTRUMENT_OF", target=12),
        _event("LX_END", "SCOPE", relation="CLOSES", target=9),
        _event("LX_OBS", "ACTION", relation="ACTS_ON", target=1),
        _event(result, "STATE", relation="RESULT_OF", target=10),
        _event("LX_ASSERT", "EVIDENTIAL", relation="SOURCE_FOR", target=16),
    ]
    ev[9]["scope_start"], ev[9]["scope_end"] = 10, 13
    ev[14]["scope_start"], ev[14]["scope_end"] = 10, 13
    before, after = _transition(action, symptom)
    ev[10]["before"], ev[10]["after"] = before, after
    ev[12]["before"], ev[12]["after"] = "unprepared", "administered"
    return ev, "case_demonstration", "RS_CASE"


def _procedure_record(rng: random.Random) -> tuple[list[dict[str, Any]], str, str]:
    symptom = _choice(rng, ENTITIES)
    action1 = _choice(rng, PROCEDURES)
    action2 = _choice(rng, [x for x in PROCEDURES if x != action1])
    material = _choice(rng, MATERIALS)
    degree = _choice(rng, DEGREES)
    ev = [
        _event("LX_TOPIC", "DISCOURSE", role="L0"),
        _event("LX_TEACH", "ENTITY", role="L0"),
        _event("LX_RAUTH", "REFERENCE", relation="REFERS_TO", target=1),
        _event("LX_ASSERT", "EVIDENTIAL", relation="SOURCE_FOR", target=4),
        _event(symptom, "ENTITY"),
        _event(degree, "STATE", relation="MODIFIES", target=4),
        _event("LX_FOR", "RELATION", relation="PURPOSE", target=4),
        _event(action1, "ACTION", relation="ACTS_ON", target=4),
        _event(material, "ENTITY", relation="INSTRUMENT_OF", target=7),
        _event("LX_COUNT", "QUANTITY", relation="QUANTIFIES", target=7),
        _event("LX_NEXT", "RELATION", relation="SEQUENCES", target=7),
        _event(action2, "ACTION", relation="ACTS_ON", target=4),
        _event("LX_REPEAT", "ACTION", relation="ITERATES", target=11, productive="PM_ITER"),
        _event("LX_RPREV", "REFERENCE", relation="REFERS_TO", target=4),
        _event("LX_OBS", "ACTION", relation="ACTS_ON", target=13),
        _event("LX_END", "SCOPE", relation="CLOSES", target=6),
    ]
    ev[6]["scope_start"], ev[6]["scope_end"] = 7, 14
    ev[15]["scope_start"], ev[15]["scope_end"] = 7, 14
    ev[7]["before"], ev[7]["after"] = _transition(action1, symptom)
    ev[11]["before"], ev[11]["after"] = _transition(action2, symptom)
    return ev, "procedure_drill", "RS_PROCEDURE"


def _comparison_record(rng: random.Random) -> tuple[list[dict[str, Any]], str, str]:
    first, second = rng.sample(ENTITIES + MEASURES, 2)
    state1, state2 = rng.sample(QUALITIES + DEGREES, 2)
    ev = [
        _event("LX_TOPIC", "DISCOURSE", role="L0"),
        _event("LX_COMPARE", "ACTION", role="L0"),
        _event(first, "ENTITY", relation="ARGUMENT_OF", target=1),
        _event(state1, "STATE", relation="MODIFIES", target=2),
        _event("LX_NEXT", "RELATION", relation="SEQUENCES", target=2),
        _event(second, "ENTITY", relation="ARGUMENT_OF", target=1),
        _event(state2, "STATE", relation="MODIFIES", target=5),
        _event("LX_RPREV", "REFERENCE", relation="REFERS_TO", target=2),
        _event("LX_REPORT", "ACTION", relation="REPORTS", target=7),
        _event("LX_ASSERT", "EVIDENTIAL", relation="SOURCE_FOR", target=8),
        _event("LX_REPEAT", "ACTION", relation="ITERATES", target=1, productive="PM_ITER"),
        _event("LX_END", "SCOPE", relation="CLOSES", target=1),
    ]
    ev[11]["scope_start"], ev[11]["scope_end"] = 2, 10
    return ev, "comparative_review", "RS_COMPARE"


def _warning_record(rng: random.Random) -> tuple[list[dict[str, Any]], str, str]:
    symptom = _choice(rng, ENTITIES)
    bad_action = _choice(rng, ["LX_WARM", "LX_COOL", "LX_BLEED", "LX_GIVE"])
    alternative = _choice(rng, ["LX_WASH", "LX_BIND", "LX_REST", "LX_OBS"])
    ev = [
        _event("LX_TOPIC", "DISCOURSE", role="L0"),
        _event("LX_IF", "SCOPE", relation="CONDITION_ON", target=2, role="L0"),
        _event(symptom, "ENTITY"),
        _event("LX_SEV", "STATE", relation="MODIFIES", target=2),
        _event("LX_THEN", "SCOPE", relation="OPENS_RESULT", target=1),
        _event("LX_NOT", "POLARITY", relation="NEGATES", target=6),
        _event(bad_action, "ACTION", relation="ACTS_ON", target=2, before="at_risk", after="worsening"),
        _event("LX_AVOID", "ACTION", relation="GOVERNS", target=6),
        _event("LX_NEXT", "RELATION", relation="ALTERNATIVE_TO", target=6),
        _event(alternative, "ACTION", relation="ACTS_ON", target=2),
        _event("LX_RPAT", "REFERENCE", relation="REFERS_TO", target=2),
        _event("LX_OBS", "ACTION", relation="ACTS_ON", target=10),
        _event("LX_END", "SCOPE", relation="CLOSES", target=1),
        _event("LX_ASSERT", "EVIDENTIAL", relation="SOURCE_FOR", target=7),
    ]
    ev[1]["scope_start"], ev[1]["scope_end"] = 2, 11
    ev[4]["scope_start"], ev[4]["scope_end"] = 5, 11
    ev[12]["scope_start"], ev[12]["scope_end"] = 2, 11
    ev[9]["before"], ev[9]["after"] = _transition(alternative, symptom)
    return ev, "contraindication_lesson", "RS_WARNING"


def _followup_record(rng: random.Random) -> tuple[list[dict[str, Any]], str, str]:
    symptom = _choice(rng, ENTITIES)
    measure = _choice(rng, MEASURES)
    result = rng.choices(["LX_BETTER", "LX_WORSE"], weights=[3, 2], k=1)[0]
    action = _choice(rng, PROCEDURES)
    ev = [
        _event("LX_TOPIC", "DISCOURSE", role="L0"),
        _event("LX_RPAT", "REFERENCE", role="L0", relation="REFERS_TO", target=2),
        _event("LX_PAT", "ENTITY"),
        _event(symptom, "ENTITY", relation="POSSESSED_BY", target=2),
        _event("LX_RPREV", "REFERENCE", relation="REFERS_TO", target=3),
        _event(measure, "ENTITY", relation="OBSERVED_IN", target=2),
        _event("LX_OBS", "ACTION", relation="ACTS_ON", target=5),
        _event(result, "STATE", relation="RESULT_OF", target=6),
        _event("LX_IF", "SCOPE", relation="CONDITION_ON", target=7),
        _event(action, "ACTION", relation="ACTS_ON", target=3),
        _event("LX_REPEAT", "ACTION", relation="ITERATES", target=9, productive="PM_ITER"),
        _event("LX_END", "SCOPE", relation="CLOSES", target=8),
        _event("LX_REPORT", "ACTION", relation="REPORTS", target=7),
    ]
    ev[8]["scope_start"], ev[8]["scope_end"] = 9, 10
    ev[11]["scope_start"], ev[11]["scope_end"] = 9, 10
    ev[9]["before"], ev[9]["after"] = _transition(action, symptom)
    return ev, "followup_round", "RS_FOLLOWUP"


def _transition(action: str, symptom: str) -> tuple[str, str]:
    if action == "LX_WASH":
        return "soiled", "cleaned"
    if action == "LX_BIND":
        return "open_or_unstable", "contained"
    if action == "LX_WARM":
        return "cold_or_stiff", "warmed"
    if action == "LX_COOL":
        return "hot_or_swollen", "eased"
    if action == "LX_BLEED":
        return "congested", "reduced"
    if action == "LX_GIVE":
        return "untreated", "dosed"
    if action == "LX_REST":
        return "strained", "resting"
    return f"{LEXICON[symptom]['entity']}_present", "reassessed"


def _record(rng: random.Random, index: int) -> tuple[list[dict[str, Any]], str, str]:
    makers = [_case_record, _procedure_record, _comparison_record, _warning_record, _followup_record]
    if index < len(makers):
        return makers[index](rng)
    return rng.choices(makers, weights=[34, 25, 14, 11, 16], k=1)[0](rng)


_S1_MERGERS = {
    "LX_FEVER": "Ӝϟ", "LX_SWELL": "Ӝϟ", "LX_WASH": "ⴴ", "LX_COOL": "ⴴ",
    "LX_RPREV": "ʚ", "LX_NOT": "ʚ", "LX_NEXT": "⊢", "LX_THEN": "⊢",
}
_S3_SUPPLETION = {"LX_BIND": "Ѯ⋔", "LX_GIVE": "҂Ө", "LX_REPORT": "ꚚϞ"}
_FREQUENT_ABBR = {
    "LX_PAT": "ʘ", "LX_OBS": "Ꙩ", "LX_HAS": "⌁", "LX_LOC": "ⵁ",
    "LX_NEXT": "⊢", "LX_RPREV": "ʚ", "LX_IF": "Ͽ", "LX_END": "⊣",
}


def _realize(
    lex_id: str,
    register: str,
    hand: str,
    line_pos: str,
    construction: str,
    degree_context: str,
    rng: random.Random,
) -> tuple[str, str, str, str, str]:
    item = LEXICON[lex_id]
    form = item["form"]
    realization = f"{register}:INHERITED"
    productive = "NONE"
    fossils = "NONE"
    morphemes = [item["stem"]]

    if lex_id in {"LX_WASH", "LX_OBS"}:
        fossils = "FC_WATER" if lex_id == "LX_WASH" else "FC_EYE"
    if register == "S0":
        if lex_id in _FREQUENT_ABBR and rng.random() < 0.78:
            form = _FREQUENT_ABBR[lex_id]
            realization = "S0:OLD_ABBREVIATION"
            morphemes = ["AB_" + item["stem"]]
        elif lex_id in {"LX_WASH", "LX_OBS", "LX_BIND"}:
            realization = "S0:FOSSIL_COMPOUND"
    elif register == "S1":
        if lex_id in _S1_MERGERS:
            form = _S1_MERGERS[lex_id]
            realization = "S1:WARD_MERGER"
            morphemes = ["MG_WARD"]
        elif item["category"].startswith("ACTION") and lex_id not in {"LX_OBS", "LX_REST", "LX_AVOID"}:
            form = "⌁" + form[:-1] if len(form) > 1 else "⌁" + form
            realization = "S1:BLEACHED_ACTION_CUE"
            productive = "PM_ACTION_CUE"
            morphemes.append("PM_ACTION_CUE")
        elif lex_id in _FREQUENT_ABBR:
            form = _FREQUENT_ABBR[lex_id]
            realization = "S1:WARD_ABBREVIATION"
    elif register == "S2":
        if lex_id == "LX_PAIN":
            if degree_context == "LX_SEV":
                form = "ϞҘҘ"
                realization = "S2:PAIN_SEVERE_SPLIT"
                morphemes.append("SP_SEVERE")
            else:
                form = "ϞӨ"
                realization = "S2:PAIN_MILD_SPLIT"
                morphemes.append("SP_MILD")
            productive = "PM_DEGREE_SPLIT"
        elif lex_id == "LX_ASSERT":
            form = "ⵁ"
            realization = "S2:REBOUND_EVIDENTIAL"
            morphemes = ["PM_S2_EVIDENTIAL"]
            productive = "PM_S2_EVIDENTIAL"
        else:
            det = {
                "ENTITY": "◇", "ACTION": "⌇", "STATE": "҂",
                "RELATION": "ⵁ", "REFERENCE": "ʚ", "SCOPE": "Ͽ", "FUNCTION": "⋔",
            }.get(item["category"].split("_", 1)[0], "◇")
            # Old high-frequency forms resist the local determinative analogy.
            if lex_id in {"LX_PAT", "LX_NEXT", "LX_RPREV", "LX_END"}:
                form = _FREQUENT_ABBR.get(lex_id, form)
                realization = "S2:LEXICAL_EXCEPTION"
            else:
                form = form + det
                realization = "S2:REGIONAL_DETERMINATIVE"
                productive = "PM_S2_DETERMINATIVE"
                morphemes.append("PM_S2_" + item["category"].split("_", 1)[0])
    else:  # S3
        if lex_id in _S3_SUPPLETION:
            form = _S3_SUPPLETION[lex_id]
            realization = "S3:SUPPLETIVE_COMMAND"
            morphemes = ["SU_" + lex_id[3:]]
        elif lex_id == "LX_REPEAT" or lex_id == "LX_WORSE":
            form = form[0] + form
            realization = "S3:PRODUCTIVE_REDUPLICATION"
            productive = "PM_REPEAT"
            morphemes.append("PM_REPEAT")
        elif item["category"].startswith("STATE"):
            form = form + "·"
            realization = "S3:BLEACHED_STATE_TAIL"
            productive = "PM_STATE_TAIL"
            morphemes.append("PM_STATE_TAIL")
        elif lex_id in _FREQUENT_ABBR and rng.random() < 0.7:
            form = _FREQUENT_ABBR[lex_id]
            realization = "S3:ITINERANT_ABBREVIATION"

    # Copyist allography is intentionally incomplete, lexical, and non-bijective.
    if hand == "H1":
        table = str.maketrans({"ⴴ": "ȣ", "Ꙩ": "ʘ", "Ҙ": "ⴷ", "⊢": "ⵔ", "Ϟ": "ϟ"})
        form = form.translate(table)
        realization += "+H1"
    elif hand == "H2":
        table = str.maketrans({"Ѧ": "Ө", "⌁": "⌇", "ⵁ": "ⴲ", "Ӝ": "Ꚛ", "ʚ": "Ͽ"})
        form = form.translate(table)
        if len(form) > 2 and construction in {"RS_CASE", "RS_PROCEDURE"}:
            form = form[0] + "·" + form[1:]
        realization += "+H2"

    if line_pos == "B0" and lex_id in {"LX_TOPIC", "LX_PAT", "LX_TEACH", "LX_IF", "LX_COMPARE"}:
        form = "ꜛ" + form
        realization += "+INITIAL_LEAD"
    elif line_pos == "B2" and lex_id not in {"LX_END", "LX_NEXT", "LX_THEN"} and rng.random() < 0.55:
        form = form + "ꜜ"
        realization += "+FINAL_TAIL"

    return form, realization, _pipe(*morphemes), fossils, productive


def _codebook() -> list[dict[str, str]]:
    rows = []
    for lex_id in sorted(LEXICON):
        item = LEXICON[lex_id]
        flags = []
        if lex_id in _FREQUENT_ABBR:
            flags.append("frequency_abbreviation")
        if lex_id in _S1_MERGERS:
            flags.append("S1_homographic_merger")
        if lex_id == "LX_PAIN":
            flags.append("S2_context_split")
        if lex_id == "LX_ASSERT":
            flags.append("S2_rebinding")
        if lex_id in _S3_SUPPLETION:
            flags.append("S3_suppletion")
        if lex_id in {"LX_WASH", "LX_OBS"}:
            flags.append("fossilized_component")
        if lex_id in {"LX_OBS", "LX_REST", "LX_AVOID"}:
            flags.append("action_cue_exception")
        rows.append({
            "lexical_id": lex_id,
            "semantic_entity_id": item["entity"],
            "semantic_category": item["category"],
            "historical_stem_id": item["stem"],
            "canonical_hidden_form": item["form"],
            "final_realization_rules": (
                "S0 full/old-frequency abbreviation; S1 ward merger or bleached action cue; "
                "S2 determinative with listed exceptions and PAIN split/evidential rebinding; "
                "S3 suppletion/reduplication/state-tail; then hand and line-position allography"
            ),
            "irregularity_flags": _pipe(*flags),
        })
    return rows


def generate(seed: int, target_events: int = 8448) -> dict[str, list[dict[str, Any]]]:
    """Generate one completed-record corpus reaching at least target_events."""
    if not isinstance(seed, int):
        raise TypeError("seed must be an int")
    if not isinstance(target_events, int) or target_events < 1:
        raise ValueError("target_events must be a positive int")

    rng = _rng(seed)
    observations: list[dict[str, Any]] = []
    oracle: list[dict[str, Any]] = []
    page_no = 0
    paragraph_no = 0
    record_no = 0
    records_on_page = 0
    records_in_paragraph = 0
    page_capacity = rng.randint(6, 9)
    paragraph_capacity = rng.randint(2, 4)

    while len(observations) < target_events:
        new_page = record_no == 0 or records_on_page >= page_capacity
        if new_page:
            page_no += 1
            paragraph_no = 1
            records_on_page = 0
            records_in_paragraph = 0
            page_capacity = rng.randint(6, 9)
            paragraph_capacity = rng.randint(2, 4)
        new_paragraph = not new_page and records_in_paragraph >= paragraph_capacity
        if new_paragraph:
            paragraph_no += 1
            records_in_paragraph = 0
            paragraph_capacity = rng.randint(2, 4)

        record_boundary = "PAGE" if new_page else ("PARAGRAPH" if new_paragraph else "RECORD")
        if observations:
            # The following record decides the strongest intervening physical
            # reset, so finish the preceding record with that same boundary.
            observations[-1]["separator_after"] = record_boundary

        local, activity, schema = _record(rng, record_no)
        # Guarantee every register and hand early, then preserve skewed school use.
        register = ["S0", "S1", "S2", "S3"][record_no] if record_no < 4 else rng.choices(
            ["S0", "S1", "S2", "S3"], weights=[38, 31, 21, 10], k=1
        )[0]
        hand = ["H0", "H1", "H2"][record_no] if record_no < 3 else rng.choices(
            ["H0", "H1", "H2"], weights=[56, 29, 15], k=1
        )[0]
        page_id = f"P{page_no:04d}"
        paragraph_id = f"P{page_no:04d}G{paragraph_no:02d}"
        record_id = f"R{record_no:06d}"
        line_lengths: list[int] = []
        remain = len(local)
        while remain:
            amount = min(remain, rng.randint(4, 7))
            line_lengths.append(amount)
            remain -= amount
        line_for: list[int] = []
        pos_for: list[str] = []
        for line_i, amount in enumerate(line_lengths):
            line_for.extend([line_i] * amount)
            if amount == 1:
                pos_for.append("B0")
            else:
                pos_for.extend(["B0"] + ["B1"] * (amount - 2) + ["B2"])

        base_index = len(observations)
        event_ids = [_sid("E", WORLD_ID, seed, base_index + i) for i in range(len(local))]
        degree_context = next((e["lex"] for e in local if e["lex"] in DEGREES), "LX_MILD")
        rendered: list[dict[str, Any]] = []
        for i, desc in enumerate(local):
            form, realization, morphemes, fossils, productive = _realize(
                desc["lex"], register, hand, pos_for[i], schema, degree_context, rng
            )
            inherently_ambiguous = (
                desc["lex"] in _FREQUENT_ABBR
                or (register == "S1" and desc["lex"] in _S1_MERGERS)
                or "·" in form
            )
            rendered.append({
                "form": form,
                "realization": realization,
                "morphemes": _pipe(*morphemes.split("|"), productive, desc["productive"]),
                "fossils": fossils if fossils != "NONE" else desc["fossils"],
                "productive": "TRUE" if productive != "NONE" or desc["productive"] != "NONE" else "FALSE",
                "ambiguous": inherently_ambiguous or rng.random() < 0.07,
            })

        boundaries: list[str] = []
        for i in range(len(local) - 1):
            if line_for[i] != line_for[i + 1]:
                boundary = "LINE"
            elif local[i]["role"] != local[i + 1]["role"]:
                boundary = "FIELD"
            elif (rendered[i]["ambiguous"] or rendered[i + 1]["ambiguous"]) and rng.random() < 0.48:
                boundary = "JOIN"
            else:
                boundary = rng.choices(["SPACE", "JOIN", "NONE"], weights=[74, 17, 9], k=1)[0]
            boundaries.append(boundary)

        for i, (desc, vis) in enumerate(zip(local, rendered)):
            line_i = line_for[i]
            if i == 0:
                sep_before = record_boundary
            else:
                sep_before = boundaries[i - 1]
            if i == len(local) - 1:
                sep_after = "RECORD"
            else:
                sep_after = boundaries[i]

            event_id = event_ids[i]
            record_bin = "Q0" if i * 3 < len(local) else ("Q1" if i * 3 < 2 * len(local) else "Q2")
            observations.append({
                "world_id": WORLD_ID,
                "corpus_seed": seed,
                "event_id": event_id,
                "page_id": page_id,
                "paragraph_id": paragraph_id,
                "record_id": record_id,
                "line_id": f"{record_id}L{line_i:02d}",
                "event_index": base_index + i,
                "group_index": i,
                "visible_group": vis["form"],
                "separator_before": sep_before,
                "separator_after": sep_after,
                "register_id": register,
                "hand_id": hand,
                "layout_role": desc["role"],
                "line_position_bin": pos_for[i],
                "record_position_bin": record_bin,
                "ambiguous_boundary": bool(vis["ambiguous"] or sep_before in {"JOIN", "NONE"} or sep_after in {"JOIN", "NONE"}),
            })
            item = LEXICON[desc["lex"]]
            target = event_ids[desc["target"]] if desc["target"] is not None else "NONE"
            scope_start = event_ids[desc["scope_start"]] if desc["scope_start"] is not None else "NONE"
            scope_end = event_ids[desc["scope_end"]] if desc["scope_end"] is not None else "NONE"
            oracle.append({
                "world_id": WORLD_ID,
                "corpus_seed": seed,
                "event_id": event_id,
                "domain_id": "medical_pedagogy",
                "activity_id": activity,
                "lexical_id": desc["lex"],
                "semantic_entity_id": item["entity"],
                "semantic_category": item["category"],
                "function_class": desc["function"],
                "relation_type": desc["relation"],
                "relation_target_event_id": target,
                "state_before": desc["before"],
                "state_after": desc["after"],
                "historical_stem_id": item["stem"],
                "current_morpheme_ids": vis["morphemes"],
                "fossilized_component_ids": vis["fossils"],
                "construction_id": f"CX_{schema[3:]}",
                "scope_start_event_id": scope_start,
                "scope_end_event_id": scope_end,
                "record_schema_id": schema,
                "register_realization_id": vis["realization"],
                "productive_morphology": vis["productive"],
                "current_component_semantics": desc["components"],
                "genealogy_stage": "9",
            })

        record_no += 1
        records_on_page += 1
        records_in_paragraph += 1

    return {
        "observations": observations,
        "oracle": oracle,
        "codebook": _codebook(),
        "genealogy": [dict(row) for row in GENEALOGY],
    }


__all__ = ["WORLD_META", "generate"]
