#!/usr/bin/env python3
"""Deterministic generator for W04, an evolved procedural recipe notation."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field


WORLD_META = {
    "world_id": "W04",
    "title": "Layered Workshop Recipe Notation",
    "broad_family": "PROCEDURAL_RECIPE_NOTATION",
    "practical_domain": "multi-step material transformation",
    "semantics_light": False,
    "organic_evolution": True,
    "clean_engineered_control": False,
    "adversarial_pair_id": "NONE",
    "carrier_profile": "CARRIER_PROCEDURAL",
    "alphabet": list("ʘƛɣŋʃʒɬɲɸβðþχʁɯəɨɔæɜʔ·"),
    "registers": ["R0", "R1", "R2", "R3"],
    "hands": ["H0", "H1", "H2"],
    "evolution_processes": [
        "frequency_shortening", "lexical_to_construction", "analogy",
        "conditioned_merger", "conditioned_split", "semantic_bleaching",
        "fossilization", "register_divergence", "suppletion", "exceptions",
        "position_allography", "construction_fusion",
    ],
    "generator_schema": "GDT395_WORLD_GENERATOR_V1",
}


MATERIALS = [
    ("MAT_CLAY", "ENT_CLAY", "ST_KALAM", "ɣæɬəβ"),
    ("MAT_RESIN", "ENT_RESIN", "ST_DURUK", "ðɯʁəχ"),
    ("MAT_FIBER", "ENT_FIBER", "ST_NESI", "ɲəʃɨ"),
    ("MAT_SALT", "ENT_SALT", "ST_TAL", "þæɬ"),
    ("MAT_PIGMENT", "ENT_PIGMENT", "ST_MARU", "βæʁɯ"),
    ("MAT_OIL", "ENT_OIL", "ST_SUK", "ʃɯχ"),
    ("MAT_ASH", "ENT_ASH", "ST_PANA", "ɸæɲə"),
    ("MAT_WATER", "ENT_WATER", "ST_WEL", "ɯəɬ"),
    ("MAT_WAX", "ENT_WAX", "ST_GEM", "ʒəβ"),
    ("MAT_LIME", "ENT_LIME", "ST_XARI", "χæʁɨ"),
]

OPS = [
    ("OP_ADD", "ACT_ADD", "ST_DA", "ðæ"),
    ("OP_GRIND", "ACT_GRIND", "ST_KER", "χəʁ"),
    ("OP_HEAT", "ACT_HEAT", "ST_MOX", "βɔχ"),
    ("OP_REST", "ACT_REST", "ST_SEN", "ʃəɲ"),
    ("OP_STIR", "ACT_STIR", "ST_LUP", "ɬɯɸ"),
    ("OP_STRAIN", "ACT_STRAIN", "ST_ZAR", "ʒæʁ"),
    ("OP_DIVIDE", "ACT_DIVIDE", "ST_PEK", "ɸəχ"),
    ("OP_SEAL", "ACT_SEAL", "ST_GOL", "ɣɔɬ"),
    ("OP_REPEAT", "ACT_REPEAT", "ST_RI", "ʁɨ"),
    ("OP_INSPECT", "ACT_INSPECT", "ST_NAW", "ɲæɯ"),
    ("OP_COOL", "ACT_COOL", "ST_XUN", "χɯɲ"),
]

QUALITIES = [
    ("QL_DRY", "STATE_DRY", "ST_TAKA", "þæχə"),
    ("QL_SMOOTH", "STATE_SMOOTH", "ST_LEME", "ɬəβə"),
    ("QL_THICK", "STATE_THICK", "ST_GURU", "ɣɯʁɯ"),
    ("QL_CLEAR", "STATE_CLEAR", "ST_SAI", "ʃæɨ"),
    ("QL_HOT", "STATE_HOT", "ST_MOXA", "βɔχə"),
    ("QL_COOL", "STATE_COOL", "ST_XUNA", "χɯɲə"),
    ("QL_UNEVEN", "STATE_UNEVEN", "ST_PEZI", "ɸəʒɨ"),
]

VESSELS = [
    ("VES_BOWL", "ENT_BOWL", "ST_KUM", "χɯβ"),
    ("VES_TRAY", "ENT_TRAY", "ST_LAS", "ɬæʃ"),
    ("VES_JAR", "ENT_JAR", "ST_DON", "ðɔɲ"),
    ("VES_CLOTH", "ENT_CLOTH", "ST_PER", "ɸəʁ"),
]

FUNCTIONS = [
    ("FN_BEGIN", "SEM_BEGIN", "ST_AKA", "æχə"),
    ("FN_END", "SEM_END", "ST_TUM", "þɯβ"),
    ("FN_WITH", "REL_WITH", "ST_WITI", "ɯɨþɨ"),
    ("FN_UNTIL", "REL_UNTIL", "ST_SADA", "ʃæðə"),
    ("FN_IF", "REL_IF", "ST_KANI", "χæɲɨ"),
    ("FN_ELSE", "REL_ELSE", "ST_BARA", "βæʁə"),
    ("FN_THEN", "REL_THEN", "ST_NU", "ɲɯ"),
    ("FN_OF", "REL_OF", "ST_I", "ɨ"),
    ("FN_BACKREF", "REL_BACK", "ST_RA", "ʁæ"),
    ("FN_ALT", "REL_ALT", "ST_DU", "ðɯ"),
    ("FN_GATE_END", "REL_CLOSE", "ST_HA", "ʔæ"),
    ("QTY_ONE", "QTY_ONE", "ST_MIN", "βɨɲ"),
    ("QTY_TWO", "QTY_TWO", "ST_MIMIN", "βɨβɨɲ"),
    ("QTY_SMALL", "QTY_SMALL", "ST_SIKI", "ʃɨχɨ"),
    ("QTY_LARGE", "QTY_LARGE", "ST_GARA", "ɣæʁə"),
    ("TIME_SHORT", "TIME_SHORT", "ST_NEM", "ɲəβ"),
    ("TIME_LONG", "TIME_LONG", "ST_NENEM", "ɲəɲəβ"),
]


@dataclass
class Token:
    lexical_id: str
    entity: str
    category: str
    function: str
    activity: str = "NONE"
    state_before: str = "NONE"
    state_after: str = "NONE"
    relation_type: str = "NONE"
    target_local: int | None = None
    construction: str = "CX_BARE"
    productive: str = "FALSE"
    morphemes: tuple[str, ...] = field(default_factory=tuple)
    fossils: tuple[str, ...] = field(default_factory=tuple)
    component_semantics: tuple[str, ...] = field(default_factory=tuple)
    scope_start_local: int | None = None
    scope_end_local: int | None = None
    layout_role: str = "L1"


LEXICON = {x[0]: x for x in MATERIALS + OPS + QUALITIES + VESSELS + FUNCTIONS}
MAT_IDS = [x[0] for x in MATERIALS]
OP_IDS = [x[0] for x in OPS]
QL_IDS = [x[0] for x in QUALITIES]
VES_IDS = [x[0] for x in VESSELS]


def _rng(seed: int) -> random.Random:
    raw = hashlib.sha256(f"GDT395:W04:{seed}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))


def _sid(prefix: str, *parts: object) -> str:
    raw = "\x1f".join(map(str, parts)).encode()
    return f"{prefix}_{hashlib.sha256(raw).hexdigest()[:12]}"


def _pipe(values: tuple[str, ...] | list[str]) -> str:
    vals = sorted({v for v in values if v and v != "NONE"})
    return "|".join(vals) if vals else "NONE"


def _tok(lex: str, category: str, function: str, **kw: object) -> Token:
    entity = LEXICON[lex][1]
    stem = LEXICON[lex][2]
    kw.setdefault("morphemes", (stem,))
    kw.setdefault("component_semantics", (entity,))
    return Token(lex, entity, category, function, **kw)


def _recipe(rng: random.Random, record_no: int) -> tuple[list[Token], str]:
    """Create one stateful record, including a guarded alternative or reference."""
    schema = rng.choices(
        ["SC_BASE", "SC_GUARDED", "SC_FORK", "SC_CORRECTIVE"],
        weights=[34, 29, 23, 14], k=1,
    )[0]
    material = rng.choice(MAT_IDS)
    additive = rng.choice([m for m in MAT_IDS if m != material])
    vessel = rng.choice(VES_IDS)
    desired = rng.choice(["QL_SMOOTH", "QL_THICK", "QL_CLEAR", "QL_DRY"])
    state = "RAW"
    t: list[Token] = []

    def add(token: Token) -> int:
        t.append(token)
        return len(t) - 1

    add(_tok("FN_BEGIN", "DISCOURSE", "RECORD_OPEN", construction="CX_FRAME", layout_role="L0"))
    add(_tok("QTY_ONE", "QUANTITY", "MEASURE", construction="CX_INITIAL_MEASURE", productive="TRUE"))
    mat_i = add(_tok(material, "MATERIAL", "PATIENT", state_before="STORED", state_after=state,
                     construction="CX_INITIAL_MEASURE", layout_role="L0"))
    add(_tok("FN_WITH", "RELATOR", "COMITATIVE", construction="CX_WITH_PHRASE",
             productive="TRUE", morphemes=("ST_WITI", "CL_LINK"),
             component_semantics=("COMITATIVE", "CONSTRUCTION_LINK")))
    add(_tok(vessel, "VESSEL", "LOCATION", construction="CX_WITH_PHRASE", layout_role="L0"))

    step_count = rng.randint(3, 5)
    last_op_i = mat_i
    for step in range(step_count):
        op = rng.choices(
            ["OP_GRIND", "OP_ADD", "OP_STIR", "OP_HEAT", "OP_REST", "OP_STRAIN", "OP_COOL"],
            weights=[12, 16, 18, 13, 12, 8, 7], k=1,
        )[0]
        before = state
        after = {
            "OP_GRIND": "GROUND", "OP_ADD": "COMBINED", "OP_STIR": "MIXED",
            "OP_HEAT": "HEATED", "OP_REST": "SETTLED", "OP_STRAIN": "FILTERED",
            "OP_COOL": "COOLED",
        }[op]
        construction = "CX_CHAINED_STEP" if step else "CX_FIRST_STEP"
        if step:
            add(_tok("FN_THEN", "RELATOR", "SEQUENCE", construction="CX_CHAINED_STEP",
                     productive="TRUE", morphemes=("ST_NU", "CL_CHAIN"),
                     component_semantics=("SEQUENCE", "CLAUSE_LINK")))
        last_op_i = add(_tok(op, "OPERATION", "PREDICATE", activity=LEXICON[op][1],
                             state_before=before, state_after=after, construction=construction,
                             productive="TRUE" if op in ("OP_ADD", "OP_STIR") else "FALSE"))
        state = after
        if op == "OP_ADD":
            add(_tok("QTY_SMALL" if rng.random() < .7 else "QTY_TWO", "QUANTITY", "MEASURE",
                     construction="CX_OBJECT", productive="TRUE"))
            add(_tok(additive, "MATERIAL", "PATIENT", state_before="STORED", state_after="INCORPORATED",
                     construction="CX_OBJECT"))
        elif op in ("OP_HEAT", "OP_REST", "OP_COOL"):
            add(_tok("TIME_SHORT" if rng.random() < .68 else "TIME_LONG", "DURATION", "EXTENT",
                     construction="CX_DURATION"))
        elif op == "OP_STRAIN":
            add(_tok("FN_WITH", "RELATOR", "INSTRUMENT", construction="CX_INSTRUMENT",
                     productive="TRUE", morphemes=("ST_WITI", "CL_INSTR", "FX_LOC"), fossils=("FX_LOC",),
                     component_semantics=("INSTRUMENT",)))
            add(_tok("VES_CLOTH", "VESSEL", "INSTRUMENT", construction="CX_INSTRUMENT"))

    if schema in ("SC_GUARDED", "SC_FORK"):
        gate_quality = rng.choice(["QL_THICK", "QL_UNEVEN", "QL_HOT"])
        gate_i = add(_tok("FN_IF", "GATE", "CONDITION_OPEN", construction="CX_GATE",
                          productive="TRUE", morphemes=("ST_KANI", "CL_SCOPE"),
                          component_semantics=("CONDITION", "SCOPE_OPEN")))
        add(_tok(gate_quality, "QUALITY", "CONDITION", state_before=state, state_after=state,
                 construction="CX_GATE_TEST"))
        remedy = "OP_STIR" if gate_quality != "QL_HOT" else "OP_COOL"
        remedy_i = add(_tok(remedy, "OPERATION", "PREDICATE", activity=LEXICON[remedy][1],
                            state_before=state, state_after="CORRECTED", construction="CX_GATE_BODY"))
        state = "CORRECTED"
        if schema == "SC_FORK":
            add(_tok("FN_ELSE", "GATE", "ALTERNATIVE", construction="CX_ALT_BRANCH",
                     morphemes=("ST_BARA", "CL_SCOPE"), component_semantics=("ALTERNATIVE", "SCOPE_SWITCH")))
            alt = rng.choice(["OP_REST", "OP_STRAIN", "OP_ADD"])
            add(_tok(alt, "OPERATION", "PREDICATE", activity=LEXICON[alt][1],
                     state_before=state, state_after="ALT_READY", construction="CX_ALT_BRANCH"))
            state = "ALT_READY"
        close_i = add(_tok("FN_GATE_END", "GATE", "SCOPE_CLOSE", construction="CX_GATE_CLOSE",
                           fossils=("FX_DEM",), morphemes=("ST_HA", "FX_DEM"),
                           component_semantics=("SCOPE_CLOSE",)))
        t[gate_i].scope_start_local = remedy_i
        t[gate_i].scope_end_local = close_i

    if schema == "SC_CORRECTIVE" or rng.random() < .28:
        add(_tok("OP_REPEAT", "OPERATION", "ITERATIVE", activity="ACT_REPEAT",
                 relation_type="REPEAT_EVENT", target_local=last_op_i,
                 state_before=state, state_after=state, construction="CX_BACKREF",
                 morphemes=("ST_RI", "FX_BACK"), component_semantics=("ITERATIVE", "BACK_REFERENCE")))
        add(_tok("FN_BACKREF", "REFERENCE", "ANAPHOR", relation_type="REF_EVENT",
                 target_local=last_op_i, construction="CX_BACKREF", fossils=("FX_BODY",),
                 morphemes=("ST_RA", "FX_BODY"), component_semantics=("ANAPHOR",)))

    add(_tok("FN_UNTIL", "RELATOR", "TERMINATIVE", construction="CX_RESULT_GATE",
             productive="TRUE", morphemes=("ST_SADA", "CL_RESULT"),
             component_semantics=("TERMINATIVE", "RESULT_LINK")))
    add(_tok(desired, "QUALITY", "RESULT", state_before=state,
             state_after=LEXICON[desired][1], construction="CX_RESULT_GATE"))
    state = LEXICON[desired][1]
    if record_no % 5 == 0:
        add(_tok("OP_INSPECT", "OPERATION", "PREDICATE", activity="ACT_INSPECT",
                 relation_type="CHECK_RESULT", target_local=len(t) - 1,
                 state_before=state, state_after=state, construction="CX_FOSSIL_AUDIT",
                 fossils=("FX_IMP",), morphemes=("ST_NAW", "FX_IMP"),
                 component_semantics=("INSPECT",)))
    add(_tok("OP_SEAL", "OPERATION", "PREDICATE", activity="ACT_SEAL",
             state_before=state, state_after="SEALED", construction="CX_CLOSING",
             productive="FALSE"))
    add(_tok("FN_END", "DISCOURSE", "RECORD_CLOSE", construction="CX_FRAME", layout_role="L2"))
    return t, schema


def _historical_form(lex: str, register: str, hand: str, line_pos: str,
                     construction: str, joined_left: bool, rng: random.Random) -> tuple[str, str, str]:
    """Apply layered changes; output surface, realization id, genealogy stage."""
    root = LEXICON[lex][3]
    stage = "S8"
    irregular: list[str] = []

    # S1 high-frequency reduction and S2 conditioned sound change.
    reductions = {
        "FN_WITH": "ɯþ", "FN_THEN": "ɲ", "FN_OF": "ɨ", "FN_IF": "χɲ",
        "FN_UNTIL": "ʃð", "OP_ADD": "ð", "OP_STIR": "ɬɸ",
        "QTY_ONE": "βɲ", "TIME_SHORT": "ɲβ",
    }
    root = reductions.get(lex, root)
    root = root.replace("əɲ", "ɨɲ").replace("æʁ", "æɣ")

    # S3 constructional cliticization and lexical fusion; not compositional affixation.
    if construction in ("CX_CHAINED_STEP", "CX_GATE_BODY") and lex.startswith("OP_"):
        root = ("ʘ" + root[1:]) if len(root) > 1 else "ʘ"
    if construction == "CX_INITIAL_MEASURE" and lex.startswith("MAT_"):
        root = root[:-1] + "ŋ" if len(root) > 2 else root + "ŋ"
    if construction == "CX_RESULT_GATE" and lex.startswith("QL_"):
        root = "ƛ" + root[1:]

    # S4 analogical remodeling with lexical exceptions.
    if lex in ("OP_GRIND", "OP_STRAIN", "OP_DIVIDE") and construction != "CX_BACKREF":
        root = root + "ɨ"
    if lex == "MAT_WATER":  # suppletive workshop form
        root = "ɔð" if register in ("R0", "R2") else "ɯəɬ"
        irregular.append("SUPPLETION")
    if lex == "OP_HEAT" and construction == "CX_CHAINED_STEP":
        root = "ʒɔ"  # fossilized inherited imperative
        irregular.append("FOSSIL_SUPPLETIVE")

    # S5 merger in rapid registers, split in formal ones.
    if register in ("R0", "R2"):
        root = root.replace("ð", "þ").replace("β", "ɸ")
    else:
        root = root.replace("χɯ", "χɨ").replace("ɣɯ", "ɣɔ")

    # S6 school/register divergence and S7 scribal/position allography.
    if register == "R0":
        root = root.replace("ɨ", "").replace("ə", "")
    elif register == "R1":
        root = root + ("·" if lex.startswith(("FN_", "QL_")) else "")
    elif register == "R2":
        root = root.replace("æ", "ə").replace("ɔ", "ɯ")
    else:
        root = "ʔ" + root if lex.startswith("OP_") else root.replace("ɯ", "ɔ")
    if hand == "H1":
        root = root.replace("ɬ", "ƛ").replace("ʃ", "ɣ")
    elif hand == "H2":
        root = root.replace("ɲ", "ŋ").replace("ʁ", "ɣ")
    if line_pos == "INITIAL" and root and root[0] in "ɣχʃʒ":
        root = "ʘ" + root[1:]
    elif line_pos == "FINAL" and root.endswith(("ə", "ɨ")):
        root = root[:-1] + "ʔ"
    if joined_left and len(root) > 1:
        root = root[1:] if root[0] in "əɨæɯ" else root
    if rng.random() < .035 and lex not in ("FN_BEGIN", "FN_END"):
        root = root.replace("ɨ", "ə", 1)
        irregular.append("TOKEN_VARIANT")
    realization = f"{register}_{hand}_{line_pos}_{'J' if joined_left else 'D'}"
    return root or "ʔ", realization, stage


def _genealogy() -> list[dict[str, str]]:
    rows = [
        ("S0", "R00", "inheritance", "PROTO_LEXICON", "WORKSHOP_LEXICON", "all lexemes", "NO", "material and action vocabulary enters recipe use"),
        ("S1", "R01", "frequency_shortening", "ST_WITI|ST_NU|ST_DA|ST_LUP", "CL_LINK|CL_CHAIN|RD_DA|RD_LUP", "high token frequency", "NO", "unequal erosion creates opaque short forms"),
        ("S2", "R02", "conditioned_merger", "PH_D|PH_T|PH_B|PH_P", "PH_T|PH_P", "rapid workshop speech", "YES", "register-conditioned obstruent merger"),
        ("S2", "R03", "conditioned_split", "PH_U", "PH_U_FRONT|PH_U_BACK", "adjacent dorsal or palatal", "YES", "formal schools preserve a new vowel contrast"),
        ("S3", "R04", "lexical_to_construction", "ST_NU|ST_KANI|ST_SADA", "CL_CHAIN|CL_SCOPE|CL_RESULT", "clause-initial procedural frames", "YES", "former words become construction markers"),
        ("S3", "R05", "construction_fusion", "CL_CHAIN|OPERATION", "CX_CHAINED_STEP", "frequent sequential actions", "YES", "initial segments mutate rather than concatenate cleanly"),
        ("S4", "R06", "analogy", "CUTTING_OPERATION_SET", "ANALOGICAL_I_CLASS", "instrumental operations", "YES", "grind strain divide remodel as a class"),
        ("S4", "R07", "suppletion", "MAT_WATER|OP_HEAT", "SUP_WATER|SUP_HEAT", "workshop register or chained imperative", "NO", "lexically restricted replacements"),
        ("S5", "R08", "semantic_bleaching", "OLD_DEMONSTRATIVE|OLD_BODY_PART", "FX_DEM|FX_BODY", "scope close and back reference", "NO", "referential nouns bleach into procedural signs"),
        ("S5", "R09", "fossilization", "OLD_IMPERATIVE|OLD_LOCATIVE", "FX_IMP|FX_LOC", "audit and instrument constructions", "NO", "components survive without productive meanings"),
        ("S6", "R10", "register_divergence", "COMMON_NOTATION", "R0|R1|R2|R3", "shop rapid, archive, field, ceremonial schools", "YES", "four norms differ in deletion, vowels, and marking"),
        ("S7", "R11", "position_allography", "DORSAL_INITIAL|FINAL_VOWEL", "ROUND_INITIAL|GLOTTAL_FINAL", "physical line edge", "YES", "line position predicts glyph replacement"),
        ("S8", "R12", "exception_diffusion", "TOKEN_VARIANTS", "LOCAL_VARIANTS", "low-frequency copying noise", "YES", "bounded variants coexist with school norms"),
    ]
    return [dict(zip(("stage", "rule_id", "process_type", "input_ids", "output_ids", "conditioning", "currently_productive", "notes"), r)) for r in rows]


def _codebook() -> list[dict[str, str]]:
    rows = []
    for lex, entity, stem, form in MATERIALS + OPS + QUALITIES + VESSELS + FUNCTIONS:
        flags = []
        if lex == "MAT_WATER":
            flags.append("REGISTER_SUPPLETION")
        if lex == "OP_HEAT":
            flags.append("CHAINED_SUPPLETION")
        if lex in ("FN_GATE_END", "FN_BACKREF", "OP_INSPECT"):
            flags.append("FOSSILIZED_CONSTRUCTION")
        if lex in ("FN_WITH", "FN_THEN", "FN_IF", "FN_UNTIL", "OP_ADD", "OP_STIR"):
            flags.append("FREQUENCY_REDUCTION")
        category = "MATERIAL" if lex.startswith("MAT_") else "OPERATION" if lex.startswith("OP_") else "QUALITY" if lex.startswith("QL_") else "VESSEL" if lex.startswith("VES_") else "FUNCTION"
        rows.append({
            "lexical_id": lex,
            "semantic_entity_id": entity,
            "semantic_category": category,
            "historical_stem_id": stem,
            "canonical_hidden_form": form,
            "final_realization_rules": "S1_REDUCTION>S2_SOUND_CHANGE>S3_CONSTRUCTION>S4_ANALOGY>S5_MERGER_SPLIT>S6_REGISTER>S7_POSITION",
            "irregularity_flags": "|".join(sorted(flags)) if flags else "NONE",
        })
    return rows


def generate(seed: int, target_events: int = 8448) -> dict[str, list[dict]]:
    if target_events < 1:
        raise ValueError("target_events must be positive")
    rng = _rng(seed)
    records: list[tuple[list[Token], str]] = []
    count = 0
    while count < target_events:
        rec = _recipe(rng, len(records))
        records.append(rec)
        count += len(rec[0])

    observations: list[dict] = []
    oracle: list[dict] = []
    global_index = 0
    for rec_no, (tokens, schema) in enumerate(records):
        page_no = rec_no // 8
        para_no = rec_no // 2
        register = rng.choices(["R0", "R1", "R2", "R3"], [45, 25, 21, 9], k=1)[0]
        hand = rng.choices(["H0", "H1", "H2"], [52, 31, 17], k=1)[0]
        record_id = _sid("R", seed, rec_no)
        page_id = _sid("P", seed, page_no)
        para_id = _sid("A", seed, para_no)
        event_ids = [_sid("E", seed, global_index + i) for i in range(len(tokens))]
        # Lines have 4--8 groups, with construction-sensitive joins.
        line_breaks = [0]
        cursor = 0
        while cursor < len(tokens):
            cursor = min(len(tokens), cursor + rng.randint(4, 8))
            line_breaks.append(cursor)
        join_before = [False] * len(tokens)
        for i in range(1, len(tokens)):
            same_line = not any(i == boundary for boundary in line_breaks[1:-1])
            joinable = tokens[i].construction in {
                "CX_CHAINED_STEP", "CX_INITIAL_MEASURE", "CX_RESULT_GATE",
                "CX_GATE_BODY", "CX_BACKREF",
            }
            if same_line and joinable:
                join_before[i] = rng.random() < {
                    "R0": .66, "R1": .28, "R2": .47, "R3": .18,
                }[register]
        for local_i, tok in enumerate(tokens):
            line_no = max(i for i, start in enumerate(line_breaks[:-1]) if start <= local_i)
            line_start, line_end = line_breaks[line_no], line_breaks[line_no + 1]
            if local_i == line_start:
                line_pos = "INITIAL"
            elif local_i == line_end - 1:
                line_pos = "FINAL"
            else:
                line_pos = "MEDIAL"
            rec_frac = local_i / max(1, len(tokens) - 1)
            rec_pos = "INITIAL" if rec_frac < .18 else "FINAL" if rec_frac > .82 else "MEDIAL"
            joinable = tok.construction in {"CX_CHAINED_STEP", "CX_INITIAL_MEASURE", "CX_RESULT_GATE", "CX_GATE_BODY", "CX_BACKREF"}
            joined_left = join_before[local_i]
            visible, realization, stage = _historical_form(tok.lexical_id, register, hand, line_pos,
                                                           tok.construction, joined_left, rng)
            is_first_record = rec_no == 0
            is_first_para = rec_no % 2 == 0
            is_first_page = rec_no % 8 == 0
            if local_i == 0:
                sep_before = "PAGE" if is_first_page else "PARAGRAPH" if is_first_para else "RECORD"
            elif local_i == line_start:
                sep_before = "LINE"
            elif joined_left:
                sep_before = "JOIN"
            elif tokens[local_i - 1].construction != tok.construction:
                sep_before = "FIELD"
            else:
                sep_before = "SPACE"
            if local_i == len(tokens) - 1:
                last_record = rec_no == len(records) - 1
                next_page = (rec_no + 1) % 8 == 0
                next_para = (rec_no + 1) % 2 == 0
                sep_after = "PAGE" if last_record or next_page else "PARAGRAPH" if next_para else "RECORD"
            elif local_i == line_end - 1:
                sep_after = "LINE"
            else:
                # Boundary ambiguity is produced by clitic-like adjacency and occasional detached copies.
                if join_before[local_i + 1]:
                    sep_after = "JOIN"
                elif tok.construction != tokens[local_i + 1].construction:
                    sep_after = "FIELD"
                else:
                    sep_after = "SPACE"
            ambiguous = "YES" if sep_before == "JOIN" or sep_after == "JOIN" or (joinable and rng.random() < .12) else "NO"
            event_id = event_ids[local_i]
            observations.append({
                "world_id": "W04", "corpus_seed": str(seed), "event_id": event_id,
                "page_id": page_id, "paragraph_id": para_id, "record_id": record_id,
                "line_id": _sid("L", seed, rec_no, line_no), "event_index": str(global_index),
                "group_index": str(local_i - line_start), "visible_group": visible,
                "separator_before": sep_before, "separator_after": sep_after,
                "register_id": register, "hand_id": hand, "layout_role": tok.layout_role,
                "line_position_bin": line_pos, "record_position_bin": rec_pos,
                "ambiguous_boundary": ambiguous,
            })
            stem = LEXICON[tok.lexical_id][2]
            target = event_ids[tok.target_local] if tok.target_local is not None else "NONE"
            scope_start = event_ids[tok.scope_start_local] if tok.scope_start_local is not None else "NONE"
            scope_end = event_ids[tok.scope_end_local] if tok.scope_end_local is not None else "NONE"
            oracle.append({
                "world_id": "W04", "corpus_seed": str(seed), "event_id": event_id,
                "domain_id": "DOM_MATERIAL_TRANSFORMATION", "activity_id": tok.activity,
                "lexical_id": tok.lexical_id, "semantic_entity_id": tok.entity,
                "semantic_category": tok.category, "function_class": tok.function,
                "relation_type": tok.relation_type, "relation_target_event_id": target,
                "state_before": tok.state_before, "state_after": tok.state_after,
                "historical_stem_id": stem, "current_morpheme_ids": _pipe(tok.morphemes),
                "fossilized_component_ids": _pipe(tok.fossils), "construction_id": tok.construction,
                "scope_start_event_id": scope_start, "scope_end_event_id": scope_end,
                "record_schema_id": schema, "register_realization_id": realization,
                "productive_morphology": tok.productive,
                "current_component_semantics": _pipe(tok.component_semantics),
                "genealogy_stage": stage,
            })
            global_index += 1

    return {"observations": observations, "oracle": oracle,
            "codebook": _codebook(), "genealogy": _genealogy()}
