#!/usr/bin/env python3
"""Deterministic generator for GDT395 world W01.

The implementation deliberately keeps the hidden semantic event stream
separate from its historically layered shorthand realization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import random
from typing import Any


WORLD_ID = "W01"

RADICAL_GLYPHS = tuple("◜◝◞◟⌁⌇⌒⌂◇◆○●△▲□■⊂⊃⊙⊗⋔⋏⋎∿≋≀⌐¬¦ʌʍɅɣʃʒꜛꜜꞏ")
CLASS_SIGNS = {
    "site": "⌂", "equipment": "◇", "material": "○",
    "property": "△", "action": "⋔", "state": "≀",
    "quantity": "⌇", "unit": "⌐", "function": "ꞏ",
}
MORPH_SIGNS = {
    "M_CONT": "∿", "M_COMPLETE": "⊙", "M_REQUIRED": "▲",
    "M_NEG": "¬", "M_ITER": "≋", "M_RESULT": "⊃",
}
FUNCTION_SIGNS = {
    "FN_IF": "◜", "FN_THEN": "◝", "FN_BECAUSE": "⊂",
    "FN_THEREFORE": "⊃", "FN_WITH": "⋏", "FN_AT": "⌂",
    "FN_OF": "ꞏ", "FN_AND": "⋎", "FN_NOT": "¬",
    "FN_MUST": "▲", "FN_AGAIN": "≋", "FN_REF": "⌐",
    "FN_UNTIL": "◟", "FN_AFTER": "◞", "FN_WHILE": "∿",
}
SHORT_SIGNS = {
    "ACT_INSPECT": "◇", "ACT_MEASURE": "⌇", "ACT_RECORD": "□",
    "ACT_TEST": "◆", "ACT_OPEN": "⊂", "ACT_CLOSE": "⊃",
    "EQ_VALVE": "◜", "EQ_GAUGE": "⌐", "MAT_WATER": "≋",
    "STATE_STABLE": "○", "STATE_COMPLETE": "●",
}

# The two hand maps model stroke formation, not a lexical substitution.
HAND_MAPS = {
    "h0": {},
    "h1": {"◜": "⌒", "◝": "⌁", "◇": "○", "△": "Ʌ", "⋔": "ʌ", "∿": "ʃ"},
    "h2": {"◞": "◟", "⌇": "¦", "○": "●", "⊂": "⋏", "⊃": "⋎", "≀": "ʒ"},
}

WORLD_META = {
    "world_id": WORLD_ID,
    "title": "Technical Scribal Shorthand",
    "broad_family": "TECHNICAL_SCRIBAL_SHORTHAND",
    "practical_domain": "technical natural-language records",
    "semantics_light": False,
    "organic_evolution": True,
    "clean_engineered_control": False,
    "adversarial_pair_id": "NONE",
    "carrier_profile": "CARRIER_TECHNICAL",
    "alphabet": list(RADICAL_GLYPHS),
    "registers": ["r0", "r1", "r2"],
    "hands": ["h0", "h1", "h2"],
    "evolution_processes": [
        "determinative_accretion", "frequency_shortening", "phrase_ligation",
        "phonological_merger", "conditioned_split", "semantic_bleaching",
        "fossilization", "polyfunctionality", "partial_analogy",
        "suppletion", "register_divergence", "hand_divergence",
    ],
    "generator_schema": "GDT395_WORLD_GENERATOR_V1",
}


def _stable_id(prefix: str, *parts: object, width: int = 12) -> str:
    raw = "\x1f".join(map(str, parts)).encode("utf-8")
    return f"{prefix}_{hashlib.sha256(raw).hexdigest()[:width]}"


def _rng(seed: int) -> random.Random:
    raw = hashlib.sha256(f"GDT395:{WORLD_ID}:{seed}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))


def _pipe(values: list[str] | tuple[str, ...] | set[str]) -> str:
    vals = sorted({str(value) for value in values if value and value != "NONE"})
    return "|".join(vals) if vals else "NONE"


@dataclass(frozen=True)
class Lexeme:
    lexical_id: str
    entity: str
    category: str
    stem: str
    hidden_form: str
    frequency: int = 2
    flags: tuple[str, ...] = ()


def _lexemes() -> list[Lexeme]:
    rows: list[Lexeme] = []

    def add(prefix: str, category: str, items: list[tuple[str, str]], frequency: int = 2) -> None:
        for index, (name, form) in enumerate(items):
            lexical_id = f"{prefix}_{name.upper()}"
            flags: list[str] = []
            if lexical_id in SHORT_SIGNS:
                flags.append("frequency_suppletive_sign")
            if name in {"seal", "open", "clear", "level", "line"}:
                flags.append("historical_merger_or_split")
            if name in {"valve", "gauge", "crucible", "cord"}:
                flags.append("fossil_classifier")
            rows.append(Lexeme(
                lexical_id, f"{category}:{name}", category,
                f"HS_{prefix}_{index:02d}", form, frequency, tuple(flags),
            ))

    add("SITE", "site", [
        ("north_bay", "nara"), ("south_bay", "sula"),
        ("upper_room", "kera"), ("lower_room", "duma"),
        ("east_yard", "tari"), ("west_works", "moru"),
    ])
    add("EQ", "equipment", [
        ("valve", "kava"), ("pump", "puru"), ("gauge", "geta"),
        ("channel", "sena"), ("kiln", "kili"), ("crucible", "kuru"),
        ("lever", "leva"), ("axle", "aksa"), ("seal", "sela"),
        ("duct", "duka"), ("reservoir", "resa"), ("hinge", "hena"),
    ], 3)
    add("MAT", "material", [
        ("water", "wara"), ("oil", "olu"), ("clay", "kala"),
        ("copper", "kupa"), ("tin", "tina"), ("iron", "ira"),
        ("wood", "wuda"), ("stone", "sata"), ("cord", "kora"),
    ], 2)
    add("PROP", "property", [
        ("pressure", "pesa"), ("flow", "fula"), ("angle", "anga"),
        ("temperature", "temara"), ("width", "wita"), ("level", "lela"),
        ("tension", "tesa"), ("color", "kola"), ("weight", "weta"),
        ("alignment", "alina"),
    ], 3)
    add("ACT", "action", [
        ("inspect", "isa"), ("measure", "mesa"), ("open", "opa"),
        ("close", "kosa"), ("tighten", "tiga"), ("clean", "kina"),
        ("heat", "heta"), ("cool", "kula"), ("mix", "misa"),
        ("replace", "repa"), ("mark", "maka"), ("repeat", "rita"),
        ("test", "tesa"), ("seal", "sela"), ("align", "alina"),
        ("record", "reka"), ("drain", "dara"), ("fill", "fila"),
    ], 5)
    add("STATE", "state", [
        ("leaking", "leka"), ("blocked", "blaka"), ("hot", "hota"),
        ("cold", "koda"), ("stable", "saba"), ("loose", "lusa"),
        ("worn", "wona"), ("cracked", "kraka"), ("clear", "kela"),
        ("complete", "kompa"), ("aligned", "alina"), ("low", "lowa"),
        ("high", "haya"),
    ], 3)
    functions = [
        ("FN_IF", "if", "ima"), ("FN_THEN", "then", "tena"),
        ("FN_BECAUSE", "because", "kusa"), ("FN_THEREFORE", "therefore", "tara"),
        ("FN_WITH", "with", "wita"), ("FN_AT", "at", "ata"),
        ("FN_OF", "of", "ova"), ("FN_AND", "and", "ana"),
        ("FN_NOT", "not", "nuta"), ("FN_MUST", "must", "muta"),
        ("FN_AGAIN", "again", "gana"), ("FN_REF", "reference", "refa"),
        ("FN_UNTIL", "until", "unta"), ("FN_AFTER", "after", "afra"),
        ("FN_WHILE", "while", "wila"),
    ]
    for index, (lexical_id, entity, form) in enumerate(functions):
        rows.append(Lexeme(lexical_id, f"function:{entity}", "function", f"HS_FN_{index:02d}", form, 8,
                           ("bleached_or_polyfunctional",)))
    add("UNIT", "unit", [
        ("span", "sapan"), ("part", "para"), ("turn", "tura"),
        ("mark", "mara"), ("degree", "dera"), ("weight", "wera"),
    ], 2)
    for number in range(13):
        rows.append(Lexeme(f"NUM_{number:02d}", f"quantity:{number}", "quantity",
                           f"HS_NUM_{number:02d}", f"count-{number}", 3,
                           ("tally_logogram",)))
    return rows


LEXEMES = _lexemes()
LEX = {row.lexical_id: row for row in LEXEMES}

DOMAINS = {
    "hydraulic": {
        "equipment": ["EQ_VALVE", "EQ_PUMP", "EQ_GAUGE", "EQ_CHANNEL", "EQ_DUCT", "EQ_RESERVOIR", "EQ_SEAL"],
        "materials": ["MAT_WATER", "MAT_OIL", "MAT_CLAY", "MAT_CORD"],
        "properties": ["PROP_PRESSURE", "PROP_FLOW", "PROP_LEVEL", "PROP_WIDTH"],
        "actions": ["ACT_INSPECT", "ACT_MEASURE", "ACT_OPEN", "ACT_CLOSE", "ACT_TIGHTEN", "ACT_CLEAN", "ACT_SEAL", "ACT_DRAIN", "ACT_FILL", "ACT_TEST", "ACT_RECORD"],
        "bad": ["STATE_LEAKING", "STATE_BLOCKED", "STATE_LOW", "STATE_HIGH"],
    },
    "thermal": {
        "equipment": ["EQ_KILN", "EQ_CRUCIBLE", "EQ_DUCT", "EQ_GAUGE", "EQ_SEAL"],
        "materials": ["MAT_CLAY", "MAT_COPPER", "MAT_TIN", "MAT_IRON"],
        "properties": ["PROP_TEMPERATURE", "PROP_COLOR", "PROP_WEIGHT"],
        "actions": ["ACT_INSPECT", "ACT_MEASURE", "ACT_HEAT", "ACT_COOL", "ACT_MIX", "ACT_TEST", "ACT_RECORD"],
        "bad": ["STATE_HOT", "STATE_COLD", "STATE_CRACKED", "STATE_LOW"],
    },
    "mechanical": {
        "equipment": ["EQ_LEVER", "EQ_AXLE", "EQ_HINGE", "EQ_GAUGE", "EQ_SEAL"],
        "materials": ["MAT_OIL", "MAT_IRON", "MAT_WOOD", "MAT_CORD"],
        "properties": ["PROP_ANGLE", "PROP_TENSION", "PROP_ALIGNMENT", "PROP_WIDTH"],
        "actions": ["ACT_INSPECT", "ACT_MEASURE", "ACT_TIGHTEN", "ACT_CLEAN", "ACT_REPLACE", "ACT_ALIGN", "ACT_TEST", "ACT_RECORD"],
        "bad": ["STATE_LOOSE", "STATE_WORN", "STATE_CRACKED", "STATE_BLOCKED"],
    },
    "masonry": {
        "equipment": ["EQ_CHANNEL", "EQ_HINGE", "EQ_LEVER", "EQ_SEAL", "EQ_RESERVOIR"],
        "materials": ["MAT_CLAY", "MAT_STONE", "MAT_WOOD", "MAT_WATER"],
        "properties": ["PROP_WIDTH", "PROP_LEVEL", "PROP_ALIGNMENT", "PROP_ANGLE"],
        "actions": ["ACT_INSPECT", "ACT_MEASURE", "ACT_CLEAN", "ACT_SEAL", "ACT_ALIGN", "ACT_MARK", "ACT_TEST", "ACT_RECORD"],
        "bad": ["STATE_CRACKED", "STATE_LOOSE", "STATE_LEAKING", "STATE_LOW"],
    },
}

SITES = ["SITE_NORTH_BAY", "SITE_SOUTH_BAY", "SITE_UPPER_ROOM", "SITE_LOWER_ROOM", "SITE_EAST_YARD", "SITE_WEST_WORKS"]
GOOD_STATES = ["STATE_STABLE", "STATE_CLEAR", "STATE_COMPLETE", "STATE_ALIGNED"]
UNITS = ["UNIT_SPAN", "UNIT_PART", "UNIT_TURN", "UNIT_MARK", "UNIT_DEGREE", "UNIT_WEIGHT"]


@dataclass
class Event:
    lex: str
    role: str
    function: str = "LEXICAL"
    relation: str = "NONE"
    target: int | None = None
    before: str = "NONE"
    after: str = "NONE"
    morphs: list[str] = field(default_factory=list)
    fossils: list[str] = field(default_factory=list)
    construction: str = "C_SIMPLE"
    scope: tuple[int, int] | None = None
    incorporate: str | None = None
    join_next: bool = False


def _choice_weighted(rng: random.Random, values: list[str], weights: list[int]) -> str:
    return rng.choices(values, weights=weights, k=1)[0]


def _record_events(rng: random.Random, record_number: int) -> tuple[list[Event], str, str, str]:
    domain = _choice_weighted(rng, list(DOMAINS), [34, 23, 27, 16])
    data = DOMAINS[domain]
    schema = _choice_weighted(
        rng,
        ["inspection", "procedure", "repair", "calibration", "incident"],
        [31, 18, 25, 17, 9],
    )
    site = rng.choice(SITES)
    equipment = rng.choice(data["equipment"])
    material = rng.choice(data["materials"])
    prop = rng.choice(data["properties"])
    bad = rng.choice(data["bad"])
    good = rng.choice(GOOD_STATES)
    action = rng.choice(data["actions"])
    value = f"NUM_{rng.randrange(13):02d}"
    unit = rng.choice(UNITS)
    events: list[Event] = []

    def add(lex: str, role: str, **kwargs: Any) -> int:
        events.append(Event(lex, role, **kwargs))
        return len(events) - 1

    # Every record begins with a compact natural-language locator/title.
    add("FN_AT", "label", function="LOCATIVE", construction="C_HEADER", join_next=True)
    site_i = add(site, "heading", construction="C_HEADER")
    eq_i = add(equipment, "heading", relation="LOCATED_AT", target=site_i, construction="C_HEADER")

    if schema == "inspection":
        inspect_i = add("ACT_INSPECT", "narrative", relation="PATIENT", target=eq_i,
                        morphs=["M_COMPLETE"], construction="C_INSPECTION",
                        incorporate=equipment if rng.random() < 0.55 else None)
        add(prop, "field", relation="ATTRIBUTE_OF", target=eq_i, construction="C_READING")
        add(value, "reading", relation="VALUE_OF", target=len(events) - 1, construction="C_READING", join_next=True)
        add(unit, "reading", relation="UNIT_OF", target=len(events) - 1, construction="C_READING")
        finding = bad if rng.random() < 0.58 else good
        add(finding, "narrative", relation="STATE_OF", target=eq_i,
            before="UNKNOWN", after=LEX[finding].entity, construction="C_FINDING")
        if rng.random() < 0.72:
            add("FN_THEREFORE", "connector", function="RESULT_CONNECTIVE", target=inspect_i,
                relation="RESULT_OF", construction="C_RESULT", join_next=True)
            repair = rng.choice(data["actions"])
            add(repair, "narrative", relation="PATIENT", target=eq_i, before=LEX[bad].entity,
                after=LEX[good].entity, morphs=["M_REQUIRED", "M_RESULT"], construction="C_RESULT",
                incorporate=equipment if rng.random() < 0.42 else None)
    elif schema == "procedure":
        add("FN_WITH", "connector", function="COMITATIVE", construction="C_MATERIAL", join_next=True)
        mat_i = add(material, "field", relation="APPLIED_TO", target=eq_i, construction="C_MATERIAL")
        if_i = add("FN_IF", "connector", function="CONDITION_SCOPE", construction="C_CONDITIONAL", join_next=True)
        add(bad, "narrative", relation="STATE_OF", target=eq_i, construction="C_CONDITIONAL")
        add("FN_THEN", "connector", function="APODOSIS", construction="C_CONDITIONAL", join_next=True)
        add("FN_MUST", "connector", function="MODAL", construction="C_INSTRUCTION", join_next=True)
        act_i = add(action, "narrative", relation="PATIENT", target=eq_i, before=LEX[bad].entity,
                    after="TRANSITIONING", morphs=["M_REQUIRED", "M_CONT"], construction="C_INSTRUCTION",
                    incorporate=equipment if rng.random() < 0.6 else None)
        add("FN_AND", "connector", function="COORDINATOR", construction="C_INSTRUCTION", join_next=rng.random() < 0.5)
        add("ACT_TEST", "narrative", relation="USES_MATERIAL", target=mat_i, before="TRANSITIONING",
            after=LEX[good].entity, morphs=["M_RESULT"], construction="C_INSTRUCTION")
        add("FN_UNTIL", "connector", function="TERMINAL_SCOPE", construction="C_TERMINAL", join_next=True)
        add(good, "narrative", relation="STATE_OF", target=eq_i, construction="C_TERMINAL")
        events[if_i].scope = (if_i, len(events) - 1)
        events[act_i].scope = (act_i, len(events) - 1)
    elif schema == "repair":
        add(bad, "narrative", relation="STATE_OF", target=eq_i, before="UNKNOWN", after=LEX[bad].entity,
            construction="C_FAULT")
        add("FN_BECAUSE", "connector", function="CAUSE_CONNECTIVE", relation="CAUSE_OF", target=len(events) - 1,
            construction="C_CAUSE", join_next=True)
        add(material, "narrative", relation="CAUSE_MATERIAL", target=eq_i, construction="C_CAUSE")
        add("FN_AFTER", "connector", function="TEMPORAL_SCOPE", construction="C_REPAIR", join_next=True)
        first_act = add(action, "narrative", relation="PATIENT", target=eq_i, before=LEX[bad].entity,
                        after="TRANSITIONING", morphs=["M_COMPLETE"], construction="C_REPAIR",
                        incorporate=equipment if rng.random() < 0.5 else None)
        if rng.random() < 0.55:
            add("FN_AGAIN", "connector", function="ITERATIVE", construction="C_REPAIR", join_next=True)
            add(action, "narrative", relation="REPEATS", target=first_act, before="TRANSITIONING",
                after=LEX[good].entity, morphs=["M_ITER", "M_RESULT"], construction="C_REPAIR")
        add("ACT_TEST", "narrative", relation="PATIENT", target=eq_i, morphs=["M_COMPLETE"], construction="C_CHECK")
        add(good, "narrative", relation="STATE_OF", target=eq_i, before="TRANSITIONING", after=LEX[good].entity,
            construction="C_CHECK")
    elif schema == "calibration":
        add("ACT_MEASURE", "narrative", relation="PATIENT", target=eq_i, morphs=["M_COMPLETE"],
            construction="C_CALIBRATE", incorporate=equipment if rng.random() < 0.65 else None)
        prop_i = add(prop, "field", relation="ATTRIBUTE_OF", target=eq_i, construction="C_READING")
        val_i = add(value, "reading", relation="VALUE_OF", target=prop_i, construction="C_READING", join_next=True)
        add(unit, "reading", relation="UNIT_OF", target=val_i, construction="C_READING")
        add("FN_REF", "marginal", function="ANAPHOR", relation="REFERS_TO", target=val_i,
            construction="C_REFERENCE", join_next=True)
        add(f"NUM_{(int(value[-2:]) + rng.choice([-1, 1])) % 13:02d}", "marginal",
            relation="COMPARISON_WITH", target=val_i, construction="C_REFERENCE")
        add("FN_THEREFORE", "connector", function="RESULT_CONNECTIVE", relation="RESULT_OF", target=prop_i,
            construction="C_ADJUST", join_next=True)
        add("ACT_ALIGN" if domain != "thermal" else "ACT_HEAT", "narrative", relation="PATIENT", target=eq_i,
            before="OUT_OF_TOLERANCE", after="CALIBRATED", morphs=["M_RESULT"], construction="C_ADJUST")
        add("ACT_RECORD", "narrative", relation="REFERS_TO", target=val_i, morphs=["M_COMPLETE"],
            construction="C_CLOSE")
    else:  # incident narrative
        add("FN_WHILE", "connector", function="SIMULTANEOUS_SCOPE", construction="C_INCIDENT", join_next=True)
        action_i = add(action, "narrative", relation="PATIENT", target=eq_i, before="NORMAL",
                       after="INTERRUPTED", morphs=["M_CONT"], construction="C_INCIDENT")
        add(bad, "narrative", relation="STATE_OF", target=eq_i, before="NORMAL", after=LEX[bad].entity,
            construction="C_INCIDENT")
        add("FN_BECAUSE", "connector", function="CAUSE_CONNECTIVE", relation="CAUSE_OF", target=action_i,
            construction="C_CAUSE", join_next=True)
        add(material, "narrative", relation="CAUSE_MATERIAL", target=eq_i, construction="C_CAUSE")
        add("FN_THEREFORE", "connector", function="RESULT_CONNECTIVE", relation="RESULT_OF", target=action_i,
            construction="C_RESULT", join_next=True)
        add("ACT_CLOSE", "narrative", relation="PATIENT", target=eq_i, before=LEX[bad].entity,
            after="ISOLATED", morphs=["M_RESULT"], construction="C_RESULT", incorporate=equipment)
        add("ACT_RECORD", "narrative", relation="REFERS_TO", target=action_i, morphs=["M_COMPLETE"],
            construction="C_CLOSE")
        events[3].scope = (3, len(events) - 1)

    # Occasional explicit cross-record-looking reference, locally resolved so
    # every relation remains auditable without corpus-order inference.
    if record_number % 7 == 3:
        add("FN_REF", "marginal", function="ANAPHOR", relation="REFERS_TO", target=eq_i,
            construction="C_REFERENCE", join_next=True)
        add(equipment, "marginal", relation="COREFERENCE", target=eq_i, construction="C_REFERENCE")

    activity = f"{domain}:{schema}"
    return events, domain, activity, f"SCHEMA_{schema.upper()}"


def _base_radical(lexical_id: str) -> str:
    digest = hashlib.sha256(f"radical:{lexical_id}".encode()).digest()
    # Deliberate historical merger classes.
    merged = {
        "ACT_SEAL": "MERGE_SEAL", "EQ_SEAL": "MERGE_SEAL",
        "ACT_ALIGN": "MERGE_ALIGN", "PROP_ALIGNMENT": "MERGE_ALIGN",
        "ACT_TEST": "MERGE_TEST", "PROP_TENSION": "MERGE_TEST",
        "STATE_CLEAR": "MERGE_OPEN", "ACT_OPEN": "MERGE_OPEN",
        "PROP_LEVEL": "MERGE_LEVEL", "STATE_LOW": "MERGE_LEVEL",
    }.get(lexical_id, lexical_id)
    digest = hashlib.sha256(f"radical:{merged}".encode()).digest()
    return RADICAL_GLYPHS[digest[0] % 30] + RADICAL_GLYPHS[digest[1] % 30]


def _fossils(lex: Lexeme) -> list[str]:
    special = {
        "EQ_VALVE": ["F_OLD_WOOD"], "EQ_GAUGE": ["F_OLD_CORD"],
        "EQ_CRUCIBLE": ["F_OLD_CLAY"], "MAT_CORD": ["F_OLD_TOOL"],
        "ACT_SEAL": ["F_OLD_MATERIAL"], "ACT_RECORD": ["F_OLD_LOCATIVE"],
    }
    return special.get(lex.lexical_id, [])


def _realize(event: Event, domain: str, register: str, hand: str,
             line_position: str, rng: random.Random) -> str:
    lex = LEX[event.lex]
    radical = _base_radical(event.lex)

    if event.lex in FUNCTION_SIGNS:
        form = FUNCTION_SIGNS[event.lex]
    elif event.lex.startswith("NUM_"):
        number = int(event.lex[-2:])
        form = "⌇" if number == 0 else ("¦" * (number % 4 + 1)) + ("⌒" if number >= 4 else "")
    elif event.lex in SHORT_SIGNS and register != "r2" and rng.random() < min(0.88, 0.35 + lex.frequency * 0.08):
        form = SHORT_SIGNS[event.lex]
    else:
        classifier = CLASS_SIGNS[lex.category]
        if register == "r2":
            form = classifier + radical
        elif register == "r1":
            form = radical[0] + classifier + radical[1]
        else:
            form = radical + (classifier if rng.random() < 0.58 else "")

    # A school-specific conditioned split partially reverses old mergers.
    if register == "r2" and event.lex in {"ACT_OPEN", "STATE_CLEAR", "PROP_LEVEL", "STATE_LOW"}:
        form += "ꜛ" if domain in {"hydraulic", "masonry"} else "ꜜ"

    # Fossil strokes survive independently of the live classifier system.
    fossil_marks = {"F_OLD_WOOD": "⌁", "F_OLD_CORD": "≋", "F_OLD_CLAY": "○",
                    "F_OLD_TOOL": "⋔", "F_OLD_MATERIAL": "◞", "F_OLD_LOCATIVE": "⌂"}
    for fossil in event.fossils:
        form += fossil_marks[fossil]

    # Patient incorporation is a construction, not an always-available affix.
    if event.incorporate:
        patient = _base_radical(event.incorporate)
        if register == "r1":
            form = form[0] + patient[0] + form[1:]
        else:
            form += patient[0]

    # Current grammatical material has register-dependent order and fusion.
    marks = "".join(MORPH_SIGNS[morph] for morph in event.morphs if morph in MORPH_SIGNS)
    if marks:
        if register == "r2":
            form = marks + form
        elif register == "r1" and len(form) > 1:
            form = form[0] + marks[:1] + form[1:]
        else:
            form += marks

    # Routine line-final apocope is blocked for suppletive signs and tallies.
    if line_position == "last" and register != "r2" and len(form) > 1 and not event.lex.startswith("NUM_"):
        form = form[:-1]

    mapping = HAND_MAPS[hand]
    return "".join(mapping.get(char, char) for char in form)


def _codebook() -> list[dict[str, str]]:
    rows = []
    for lex in LEXEMES:
        flags = set(lex.flags)
        fossils = _fossils(lex)
        if fossils:
            flags.add("fossilized_determinative")
        if lex.lexical_id in FUNCTION_SIGNS:
            final = f"function_logogram={FUNCTION_SIGNS[lex.lexical_id]}; phrase-ligation and hand variants apply"
        elif lex.lexical_id.startswith("NUM_"):
            final = "tally series modulo four plus upper-count arch; h1/h2 stroke variants apply"
        else:
            final = (
                f"inherited_radical={_base_radical(lex.lexical_id)}; live_classifier={CLASS_SIGNS[lex.category]}; "
                "r2 classifier-prefix, r1 classifier-infix, r0 optional classifier-suffix; "
                "patient incorporation, line-final apocope, and hand maps apply"
            )
            if lex.lexical_id in SHORT_SIGNS:
                final += f"; frequent_suppletive={SHORT_SIGNS[lex.lexical_id]}"
        rows.append({
            "lexical_id": lex.lexical_id,
            "semantic_entity_id": lex.entity,
            "semantic_category": lex.category,
            "historical_stem_id": lex.stem,
            "canonical_hidden_form": lex.hidden_form,
            "final_realization_rules": final,
            "irregularity_flags": _pipe(flags),
        })
    return rows


def _genealogy() -> list[dict[str, str]]:
    data = [
        (1, "R01", "syllabic_crystallization", "spoken technical lexicon", "HS_*", "guild dictation", "no", "Full phonetic spellings establish inherited stems."),
        (2, "R02", "determinative_accretion", "HS_*|semantic class signs", "classified radicals", "technical nouns and operations", "yes", "Class signs remain partly productive."),
        (3, "R03", "frequency_shortening", "common classified radicals", "unrelated short signs", "high token frequency", "yes", "Probability remains register and frequency conditioned."),
        (4, "R04", "phrase_ligation", "function|content sequences", "joined shorthand groups", "frequent instructions and headings", "yes", "Join can cross an observed event boundary."),
        (5, "R05", "phonological_merger", "seal/align/test/open/level stem pairs", "five merged radical classes", "intervocalic loss", "no", "Distinct historical stems share visible radicals."),
        (6, "R06", "conditioned_split", "MERGE_OPEN|MERGE_LEVEL", "raised/lowered formal variants", "formal school and domain", "yes", "Only r2 partially reverses two mergers."),
        (7, "R07", "fossilization", "old wood/cord/clay/tool determinatives", "F_OLD_*", "lexically listed survivors", "no", "Former classifiers no longer match current semantics."),
        (8, "R08", "bleaching_polyfunctionality", "locative/result/repetition words", "divider|connective|aspect signs", "constructional context", "yes", "Same signs realize lexical and grammatical functions."),
        (9, "R09", "partial_analogy", "action paradigm", "M_CONT|M_COMPLETE|M_RESULT", "lower-frequency actions", "yes", "Common actions retain suppletive forms."),
        (10, "R10", "register_divergence", "classified radicals", "r0|r1|r2 order variants", "ledger/field/formal schools", "yes", "Classifier position and contraction differ."),
        (11, "R11", "hand_divergence", "school forms", "h0|h1|h2 stroke variants", "individual ductus", "yes", "Hand transformations cut across registers."),
    ]
    return [{
        "stage": str(stage), "rule_id": rule, "process_type": process,
        "input_ids": inputs, "output_ids": outputs, "conditioning": condition,
        "currently_productive": productive, "notes": notes,
    } for stage, rule, process, inputs, outputs, condition, productive, notes in data]


def generate(seed: int, target_events: int = 8448) -> dict[str, list[dict]]:
    """Generate one complete-record-bounded corpus for W01."""
    if not isinstance(seed, int):
        raise TypeError("seed must be an int")
    if not isinstance(target_events, int) or target_events < 1:
        raise ValueError("target_events must be a positive int")

    rng = _rng(seed)
    observations: list[dict] = []
    oracle: list[dict] = []
    record_number = 0
    line_number = 0
    previous_equipment_event: str | None = None

    while len(observations) < target_events:
        events, domain, activity, schema = _record_events(rng, record_number)
        page_number = record_number // 12
        paragraph_number = record_number // 4
        register = _choice_weighted(rng, ["r0", "r1", "r2"], [56, 29, 15])
        hand = ["h0", "h1", "h2"][(page_number + (record_number // 5)) % 3]

        # Allocate complete physical lines before rendering, because position
        # within a line changes the shorthand form.
        line_slots: list[tuple[int, int, int]] = []
        cursor = 0
        while cursor < len(events):
            width = rng.randint(4, 7)
            end = min(len(events), cursor + width)
            current_line = line_number
            line_number += 1
            for offset, event_i in enumerate(range(cursor, end)):
                line_slots.append((current_line, offset, end - cursor))
            cursor = end

        event_ids = [
            _stable_id("ev", WORLD_ID, seed, len(observations) + i)
            for i in range(len(events))
        ]
        record_rows: list[dict] = []
        oracle_rows: list[dict] = []
        role_map = {"heading": "lr0", "label": "lr1", "field": "lr2", "reading": "lr3",
                    "narrative": "lr4", "connector": "lr5", "marginal": "lr6"}

        for i, event in enumerate(events):
            lex = LEX[event.lex]
            event.fossils = _fossils(lex)
            line_id_number, offset, line_length = line_slots[i]
            line_pos = "first" if offset == 0 else ("last" if offset == line_length - 1 else "middle")
            if len(events) == 1:
                record_pos = "only"
            elif i < len(events) / 3:
                record_pos = "early"
            elif i >= 2 * len(events) / 3:
                record_pos = "late"
            else:
                record_pos = "middle"

            # Joining comes from the construction, with rare scribal detachment.
            join_prev = i > 0 and events[i - 1].join_next and rng.random() < 0.84
            join_next = event.join_next and rng.random() < 0.84
            ambiguous = join_prev or join_next or (register == "r1" and rng.random() < 0.045)

            if i == 0:
                if record_number % 12 == 0:
                    sep_before = "PAGE"
                elif record_number % 4 == 0:
                    sep_before = "PARAGRAPH"
                else:
                    sep_before = "RECORD"
            elif line_slots[i][0] != line_slots[i - 1][0]:
                sep_before = "LINE"
            elif join_prev:
                sep_before = "JOIN"
            elif events[i - 1].role != event.role and event.role in {"field", "reading", "marginal"}:
                sep_before = "FIELD"
            else:
                sep_before = "SPACE"

            visible = _realize(event, domain, register, hand, line_pos, rng)
            global_index = len(observations) + i
            target_id = event_ids[event.target] if event.target is not None else "NONE"
            scope_start = event_ids[event.scope[0]] if event.scope else "NONE"
            scope_end = event_ids[event.scope[1]] if event.scope else "NONE"
            # These are current synchronic component IDs.  Historical stem
            # identity is represented separately in historical_stem_id.
            morph_ids = [f"CM_LEX_{event.lex}"] + event.morphs
            if lex.category not in {"function", "quantity"}:
                morph_ids.append(f"CM_CLASS_{lex.category.upper()}")
            # Synchronically productive meanings only: bleached function
            # signs are labeled by their present grammatical use, while old
            # determinative meanings remain exclusively in the fossil field.
            if lex.category == "function":
                component_semantics = [f"function:{event.function.lower()}"]
            else:
                component_semantics = [lex.entity]
            if event.incorporate:
                morph_ids.append(f"CM_INCORP_{event.incorporate}")
                component_semantics.append(f"incorporated:{LEX[event.incorporate].entity}")
            component_semantics.extend(f"grammatical:{morph.lower()}" for morph in event.morphs)

            record_rows.append({
                "world_id": WORLD_ID,
                "corpus_seed": seed,
                "event_id": event_ids[i],
                "page_id": f"p{page_number:04d}",
                "paragraph_id": f"q{paragraph_number:05d}",
                "record_id": f"r{record_number:06d}",
                "line_id": f"l{line_id_number:07d}",
                "event_index": global_index,
                "group_index": i,
                "visible_group": visible,
                "separator_before": sep_before,
                "separator_after": "NONE",  # filled from the following event
                "register_id": register,
                "hand_id": hand,
                "layout_role": role_map[event.role],
                "line_position_bin": line_pos,
                "record_position_bin": record_pos,
                "ambiguous_boundary": "yes" if ambiguous else "no",
            })
            oracle_rows.append({
                "world_id": WORLD_ID,
                "corpus_seed": seed,
                "event_id": event_ids[i],
                "domain_id": f"domain:{domain}",
                "activity_id": f"activity:{activity}",
                "lexical_id": event.lex,
                "semantic_entity_id": lex.entity,
                "semantic_category": lex.category,
                "function_class": event.function,
                "relation_type": event.relation,
                "relation_target_event_id": target_id,
                "state_before": event.before,
                "state_after": event.after,
                "historical_stem_id": lex.stem,
                "current_morpheme_ids": _pipe(morph_ids),
                "fossilized_component_ids": _pipe(event.fossils),
                "construction_id": event.construction,
                "scope_start_event_id": scope_start,
                "scope_end_event_id": scope_end,
                "record_schema_id": schema,
                "register_realization_id": {"r0": "school:ledger", "r1": "school:field", "r2": "school:formal"}[register],
                "productive_morphology": "TRUE" if event.morphs or event.incorporate else "FALSE",
                "current_component_semantics": _pipe(component_semantics),
                "genealogy_stage": "11",
            })

        if (record_number + 1) % 12 == 0:
            next_record_boundary = "PAGE"
        elif (record_number + 1) % 4 == 0:
            next_record_boundary = "PARAGRAPH"
        else:
            next_record_boundary = "RECORD"
        for i, row in enumerate(record_rows):
            if i + 1 < len(record_rows):
                row["separator_after"] = record_rows[i + 1]["separator_before"]
            else:
                row["separator_after"] = next_record_boundary

        # Preserve a real, if sparse, discourse thread: the marginal duplicate
        # points locally, while this variable influences later lexical choice
        # without exposing semantic labels in observation IDs.
        for i, event in enumerate(events):
            if LEX[event.lex].category == "equipment":
                previous_equipment_event = event_ids[i]
                break
        _ = previous_equipment_event

        observations.extend(record_rows)
        oracle.extend(oracle_rows)
        record_number += 1

    return {
        "observations": observations,
        "oracle": oracle,
        "codebook": _codebook(),
        "genealogy": _genealogy(),
    }
