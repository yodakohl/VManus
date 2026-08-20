#!/usr/bin/env python3
"""Deterministic generator for W06, an organically evolved collection index."""

from __future__ import annotations

import hashlib
import random


WORLD_META = {
    "world_id": "W06",
    "title": "Namar Organic Catalogue Index",
    "broad_family": "ORGANIC_CATALOGUE_INDEX",
    "practical_domain": "taxonomic collection and cross-reference",
    "semantics_light": False,
    "organic_evolution": True,
    "clean_engineered_control": False,
    "adversarial_pair_id": "NONE",
    "carrier_profile": "CARRIER_INDEX",
    "alphabet": list("abdefghiklmnoprstuvxyz"),
    "registers": ["r0", "r1", "r2", "r3"],
    "hands": ["h0", "h1", "h2"],
    "evolution_processes": [
        "frequency_shortening", "analogy", "merger", "conditioned_split",
        "bleaching", "fossilization", "polyfunctionality",
        "suppletion_and_exceptions", "register_and_school_divergence",
    ],
    "generator_schema": "GDT395_WORLD_GENERATOR_V1",
}


ROOTS = [
    "badur", "gemin", "kofal", "murek", "naxis", "pedon", "ravil", "sotem",
    "tugar", "vames", "xorin", "zefad", "bromi", "dakun", "fegor", "gisam",
    "kivet", "lomar", "nerud", "paxis", "ruden", "sivak", "tomeg", "vural",
    "xamid", "zunek", "birel", "dovas", "furen", "gaxon", "kemir", "modak",
    "nufel", "poris", "rasek", "sugen", "tavid", "vexor", "xubal", "zomir",
    "banek", "dirus", "fomar", "gurev", "kesan", "munor", "nivet", "puzar",
    "revik", "sadon", "tirem", "vogar", "xenus", "zarek", "bovin", "dumek",
    "firas", "goran", "kuzel", "mavin", "nored", "pigem", "rusak", "sevor",
    "tunik", "vared", "xemur", "zigan", "borak", "dusin", "favel", "girem",
]

ENTITY_KINDS = (
    ("SP", "SPECIMEN", 64), ("TX", "TAXON", 28),
    ("LC", "LOCALITY", 16), ("HB", "HABITAT", 10),
    ("CL", "COLLECTOR", 12), ("SH", "SHELF_LOCUS", 14),
    ("SC", "CATALOGUE_SCHOOL", 4),
)

FUNCTIONS = {
    "M_ACC": ("ACCESSION_MARK", "RECORD_OPERATOR", "kares"),
    "M_DET": ("DETERMINATION_MARK", "RECORD_OPERATOR", "dorin"),
    "M_REV": ("REVISION_MARK", "RECORD_OPERATOR", "vorak"),
    "M_SYN": ("SYNONYM_MARK", "RELATION_OPERATOR", "rimen"),
    "M_XRF": ("CROSS_REFERENCE_MARK", "RELATION_OPERATOR", "rimet"),
    "M_ALT": ("ALTERNATIVE_MARK", "RELATION_OPERATOR", "rimel"),
    "M_SCP": ("SCOPE_OPEN", "SCOPE_OPERATOR", "pador"),
    "M_CNT": ("SCOPE_CONTINUE", "SCOPE_OPERATOR", "rimos"),
    "M_END": ("SCOPE_CLOSE", "SCOPE_OPERATOR", "pedar"),
    "M_LOC": ("LOCALITY_FIELD", "FIELD_OPERATOR", "lomes"),
    "M_HAB": ("HABITAT_FIELD", "FIELD_OPERATOR", "habet"),
    "M_COL": ("COLLECTOR_FIELD", "FIELD_OPERATOR", "suvan"),
    "M_DAT": ("DATE_FIELD", "FIELD_OPERATOR", "temir"),
    "M_LOAN": ("LOAN_MARK", "RECORD_OPERATOR", "gared"),
    "M_RET": ("RETURN_MARK", "RELATION_OPERATOR", "garin"),
    "M_AUTH": ("AUTHORITY_MARK", "FIELD_OPERATOR", "auvek"),
    "M_SEE": ("INDEX_POINTER", "RELATION_OPERATOR", "rivet"),
    "M_EQ": ("IDENTITY_OPERATOR", "RELATION_OPERATOR", "esam"),
    "M_UNC": ("UNCERTAINTY_OPERATOR", "STANCE_OPERATOR", "nokan"),
    "M_EXC": ("EXCEPTION_OPERATOR", "STANCE_OPERATOR", "xedar"),
    "M_NUM": ("COUNT_FIELD", "FIELD_OPERATOR", "duvin"),
    "M_KEY": ("INDEX_KEY", "FIELD_OPERATOR", "kesar"),
}

SCHEMAS = {
    "ACCESSION": ["M_ACC", "SP", "SH", "M_LOC", "LC", "M_COL", "CL", "M_DAT", "TX", "M_KEY"],
    "DETERMINATION": ["M_DET", "SP", "M_EQ", "TX", "M_AUTH", "CL", "M_XRF", "SP"],
    "REVISION": ["M_REV", "SP", "TX", "M_ALT", "TX", "M_AUTH", "CL", "M_SEE", "SP"],
    "SYNONYMY": ["M_SYN", "TX", "M_EQ", "TX", "M_ALT", "TX", "M_AUTH", "SC"],
    "HABITAT_SCOPE": ["M_HAB", "HB", "M_SCP", "TX", "M_CNT", "TX", "M_CNT", "TX", "M_END"],
    "LOCALITY_INDEX": ["M_LOC", "LC", "M_SCP", "SP", "TX", "M_CNT", "SP", "TX", "M_END"],
    "LOAN": ["M_LOAN", "SP", "SH", "M_COL", "CL", "M_DAT", "M_RET", "M_SEE", "SP"],
    "TAXON_INDEX": ["M_KEY", "TX", "M_SCP", "SP", "M_SEE", "SP", "M_CNT", "SP", "M_END"],
}

SCHEMA_WEIGHTS = [
    ("ACCESSION", 25), ("DETERMINATION", 18), ("REVISION", 13),
    ("SYNONYMY", 9), ("HABITAT_SCOPE", 10), ("LOCALITY_INDEX", 9),
    ("LOAN", 6), ("TAXON_INDEX", 10),
]


def _stable_id(prefix: str, *parts: object, width: int = 12) -> str:
    raw = "\x1f".join(map(str, parts)).encode()
    return f"{prefix}_{hashlib.sha256(raw).hexdigest()[:width]}"


def _rng(seed: int) -> random.Random:
    raw = hashlib.sha256(f"GDT395:W06:{seed}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))


def _weighted(rng: random.Random, pairs):
    total = sum(weight for _, weight in pairs)
    point = rng.randrange(total)
    for item, weight in pairs:
        if point < weight:
            return item
        point -= weight
    return pairs[-1][0]


def _entity_table():
    table = {}
    root_i = 0
    for prefix, category, count in ENTITY_KINDS:
        rows = []
        for i in range(count):
            root = ROOTS[root_i % len(ROOTS)]
            cycle = root_i // len(ROOTS)
            if cycle:
                root = root[:-1] + "aeiou"[(root_i + cycle) % 5] + "n"
            entity = f"{prefix}{i:03d}"
            rows.append((entity, f"L_{entity}", category, f"HS_{prefix}{i:03d}", root))
            root_i += 1
        table[prefix] = rows
    return table


ENTITIES = _entity_table()


def _genealogy():
    specs = [
        (1, "R01", "lexical_inheritance", "PROTO_CLASS_WORDS|PROTO_ENTITY_STEMS", "EARLY_CATALOGUE_LEXICON", "independent words in all positions", "FALSE", "Inherited entity and class vocabulary."),
        (2, "R02", "frequency_shortening", "M_XRF|M_CNT|COMMON_SP|COMMON_TX", "SHORT_RELATIONS|CLIPPED_COMMON_STEMS", "high token frequency", "FALSE", "Shortened forms are lexically stored."),
        (3, "R03", "analogy", "ACCESSION_FRAME_A|DETERMINATION_FRAME_A", "FRAME_KA|FRAME_DI", "productive records excluding inherited exceptions", "TRUE", "Frame analogy remains locally productive."),
        (4, "R04", "merger", "FINAL_ET|FINAL_ES|FINAL_EN", "FINAL_E", "nonformal medial position", "TRUE", "Several stem classes merge outside formal register."),
        (4, "R05", "conditioned_split", "PROTO_RIM", "M_XRF|M_ALT|M_CNT", "relation role, position, and school", "TRUE", "One index particle split without fully disambiguating."),
        (5, "R06", "bleaching", "CLASS_LOCALITY|CLASS_HABITAT|CLASS_KEY", "M_LOC|M_HAB|M_KEY", "record-initial or field-initial", "TRUE", "Class nouns became catalogue operators."),
        (6, "R07", "fossilization", "OLD_KA|OLD_NA", "FOSSIL_K|FOSSIL_N", "stored subset of specimens and localities", "FALSE", "Opaque residue survives on selected lexical items."),
        (7, "R08", "polyfunctionality", "M_XRF|M_ALT|M_CNT", "REL_RI", "joined construction or line edge", "TRUE", "Cross-reference, alternative, and continuation can coincide."),
        (8, "R09", "suppletion_and_exceptions", "COMMON_TX|M_ACC|M_SEE", "SUPPLETIVE_SCHOOL_FORMS", "high frequency taxa and inherited operator frames", "FALSE", "Lexical exceptions block regular realization."),
        (9, "R10", "register_divergence", "LATE_COMMON_INDEX", "FORMAL|FIELD|SCHOOL_A|SCHOOL_B", "register, school, hand, and line position", "TRUE", "Register and scribal traditions diverged."),
    ]
    return [dict(zip(("stage", "rule_id", "process_type", "input_ids", "output_ids", "conditioning", "currently_productive", "notes"), row)) for row in specs]


def _codebook():
    rows = []
    for members in ENTITIES.values():
        for entity, lex, category, hist, root in members:
            flags = []
            number = int(entity[2:])
            if category in {"SPECIMEN", "TAXON"} and number < 8:
                flags.append("FREQUENCY_SHORTENED")
            if category in {"SPECIMEN", "LOCALITY"} and number % 7 == 0:
                flags.append("FOSSILIZED_CLASS_RESIDUE")
            if category == "TAXON" and number < 4:
                flags.append("REGISTER_SUPPLETION")
            rows.append({
                "lexical_id": lex, "semantic_entity_id": entity,
                "semantic_category": category, "historical_stem_id": hist,
                "canonical_hidden_form": root,
                "final_realization_rules": "R02|R04|R07|R09|R10",
                "irregularity_flags": "|".join(flags) if flags else "NONE",
            })
    for lex, (entity, category, root) in FUNCTIONS.items():
        flags = []
        if lex in {"M_XRF", "M_ALT", "M_CNT"}:
            flags.extend(["HISTORICAL_SPLIT", "POLYFUNCTIONAL_MERGER"])
        if lex in {"M_ACC", "M_SEE"}:
            flags.append("SUPPLETIVE_OPERATOR")
        rows.append({
            "lexical_id": lex, "semantic_entity_id": entity,
            "semantic_category": category, "historical_stem_id": f"HS_{lex}",
            "canonical_hidden_form": root,
            "final_realization_rules": "R02|R03|R04|R05|R06|R08|R09|R10",
            "irregularity_flags": "|".join(flags) if flags else "NONE",
        })
    return rows


CODEBOOK = _codebook()
CODE_BY_LEX = {row["lexical_id"]: row for row in CODEBOOK}


def _choose_entity(rng, prefix, anchors):
    members = ENTITIES[prefix]
    # Zipf-like reuse with corpus-local anchors, plus a long tail.
    if anchors[prefix] and rng.random() < 0.58:
        return rng.choice(anchors[prefix][: min(8, len(anchors[prefix]))])
    rank = min(len(members) - 1, int(rng.expovariate(0.16)))
    row = members[rank]
    if row not in anchors[prefix]:
        anchors[prefix].insert(0, row)
        del anchors[prefix][12:]
    return row


def _specs_for_record(rng, schema, anchors):
    base = list(SCHEMAS[schema])
    # Real records omit, repeat, parenthesize, and move fields.
    if schema in {"ACCESSION", "DETERMINATION", "REVISION"} and rng.random() < 0.28:
        base.insert(-1, "M_UNC")
    if schema in {"REVISION", "SYNONYMY"} and rng.random() < 0.32:
        base.extend(["M_EXC", "TX"])
    if schema in {"ACCESSION", "LOAN"} and rng.random() < 0.22:
        base.extend(["M_NUM", "SP"])
    if rng.random() < 0.18 and len(base) > 7:
        del base[rng.randrange(4, len(base) - 2)]
    specs = []
    occurrence = {}
    for symbol in base:
        if symbol in ENTITIES:
            row = _choose_entity(rng, symbol, anchors)
            # Within-record repeated types usually contrast, but pointers reuse.
            if symbol == "SP" and symbol in occurrence and rng.random() < 0.45:
                row = occurrence[symbol]
            elif symbol == "TX" and symbol in occurrence and rng.random() < 0.15:
                row = occurrence[symbol]
            occurrence[symbol] = row
            specs.append((row[1], row[0], row[2], row[3]))
        else:
            entity, category, _ = FUNCTIONS[symbol]
            specs.append((symbol, entity, category, f"HS_{symbol}"))
    return specs


def _surface(lex, register, hand, position, joined, rng):
    row = CODE_BY_LEX[lex]
    form = row["canonical_hidden_form"]
    entity = row["semantic_entity_id"]
    category = row["semantic_category"]
    flags = row["irregularity_flags"]

    # Stage 2 stored shortening.
    if "FREQUENCY_SHORTENED" in flags:
        form = form[: max(2, len(form) - 2)]
    if lex in {"M_XRF", "M_ALT", "M_CNT"}:
        form = "ri" if joined or position in {"LEND", "RFEND"} else {"M_XRF": "rive", "M_ALT": "rila", "M_CNT": "riso"}[lex]
    # Stage 4 merger and stage 6 fossil residue.
    if register != "r0" and form.endswith(("et", "es", "en")):
        form = form[:-2] + "e"
    if "FOSSILIZED_CLASS_RESIDUE" in flags:
        form = ("k" if category == "SPECIMEN" else "n") + form
    # Stage 8 suppletion.
    if "REGISTER_SUPPLETION" in flags and register in {"r2", "r3"}:
        form = ["zu", "bai", "oxe", "dum"][int(entity[2:]) % 4]
    if lex == "M_ACC" and register == "r1":
        form = "ek"
    if lex == "M_SEE" and register in {"r2", "r3"}:
        form = "uzo"
    # Stage 9 register divergence.
    if register == "r0":
        form = form + ("a" if not form.endswith("a") else "n")
    elif register == "r1" and len(form) > 4:
        form = form[0] + form[2:]
    elif register == "r2":
        form = form.replace("a", "e", 1)
    elif register == "r3":
        form = ("s" + form[1:]) if len(form) > 2 else form + "s"
    # Position and hand are graphic, not clean morphemes.
    if position == "LSTART" and form[0] in "bdgkpt":
        form = "i" + form
    if position in {"LEND", "RFEND"} and len(form) > 3:
        form = form[:-1]
    if hand == "h1":
        form = form.translate(str.maketrans("bdgk", "ptxg"))
    elif hand == "h2":
        form = form.translate(str.maketrans("aeiou", "eioua"))
    if joined and len(form) > 3 and rng.random() < 0.65:
        form = form[:-1]
    return form


def _relation_type(lex):
    return {
        "M_XRF": "CROSS_REFERENCE", "M_SEE": "INDEX_REFERENCE",
        "M_ALT": "ALTERNATIVE", "M_EQ": "EQUIVALENCE",
        "M_SYN": "SYNONYMY", "M_CNT": "SCOPE_CONTINUATION",
        "M_SCP": "SCOPE_OPEN", "M_END": "SCOPE_CLOSE",
        "M_REV": "REVISION", "M_RET": "RETURN_RELATION",
    }.get(lex, "NONE")


def _function_class(lex, category):
    if lex.startswith("M_"):
        return FUNCTIONS[lex][1]
    return "ENTITY_REFERENCE" if category not in {"CATALOGUE_SCHOOL"} else "AUTHORITY_REFERENCE"


def _components(lex, category):
    if lex in {"M_XRF", "M_ALT", "M_CNT"}:
        return ("CM_REL_RI", "RELATIONAL_CONTINUITY", "NONE", "TRUE")
    if lex.startswith("M_"):
        return (f"CM_{lex[2:]}", FUNCTIONS[lex][0], "NONE", "TRUE" if lex in {"M_LOC", "M_HAB", "M_KEY", "M_SCP"} else "FALSE")
    row = CODE_BY_LEX[lex]
    fossil = "FC_OLD_CLASS" if "FOSSILIZED_CLASS_RESIDUE" in row["irregularity_flags"] else "NONE"
    morphemes = f"CM_STEM_{category}"
    return (morphemes, category, fossil, "FALSE")


def generate(seed: int, target_events: int = 8448) -> dict[str, list[dict]]:
    if not isinstance(seed, int):
        raise TypeError("seed must be int")
    if not isinstance(target_events, int) or target_events < 1:
        raise ValueError("target_events must be a positive int")
    rng = _rng(seed)
    observations = []
    oracle = []
    anchors = {prefix: [] for prefix in ENTITIES}
    last_event_for_entity = {}
    last_record_event = "NONE"
    states = {}
    record_no = 0
    page_no = 0
    paragraph_no = 0
    line_no = 0
    records_on_page = 0
    records_in_para = 0

    while len(observations) < target_events:
        record_no += 1
        new_page = record_no == 1 or records_on_page >= rng.randint(9, 15)
        if new_page:
            page_no += 1
            paragraph_no += 1
            records_on_page = 0
            records_in_para = 0
        new_para = new_page or records_in_para >= rng.randint(2, 5)
        if new_para and not new_page:
            paragraph_no += 1
            records_in_para = 0
        records_on_page += 1
        records_in_para += 1
        schema = _weighted(rng, SCHEMA_WEIGHTS)
        specs = _specs_for_record(rng, schema, anchors)
        register = _weighted(rng, [("r0", 22), ("r1", 43), ("r2", 23), ("r3", 12)])
        hand = _weighted(rng, [("h0", 48), ("h1", 31), ("h2", 21)])
        record_id = f"r{record_no:05d}"
        page_id = f"p{page_no:04d}"
        paragraph_id = f"q{paragraph_no:05d}"
        max_per_line = rng.choice([4, 5, 5, 6, 7])
        line_breaks = {0}
        cursor = max_per_line
        while cursor < len(specs):
            line_breaks.add(cursor)
            cursor += rng.choice([4, 5, 6, 7])
        event_ids = [_stable_id("e", "W06", seed, len(observations) + i) for i in range(len(specs))]
        scope_indices = [i for i, spec in enumerate(specs) if spec[0] in {"M_SCP", "M_END"}]
        scope_start = event_ids[scope_indices[0]] if scope_indices else "NONE"
        scope_end = event_ids[scope_indices[-1]] if len(scope_indices) > 1 else "NONE"
        record_first = event_ids[0]
        record_last = event_ids[-1]

        current_line_id = None
        group_in_line = 0
        for i, (lex, entity, category, hist) in enumerate(specs):
            global_i = len(observations)
            starts_line = i in line_breaks
            if starts_line:
                line_no += 1
                current_line_id = f"l{line_no:06d}"
                group_in_line = 0
            else:
                group_in_line += 1
            next_starts_line = (i + 1) in line_breaks
            is_last = i == len(specs) - 1
            is_scope = scope_start != "NONE" and scope_indices[0] <= i <= scope_indices[-1]
            joined = (lex in {"M_XRF", "M_ALT", "M_CNT", "M_EQ", "M_AUTH"} or (i and specs[i - 1][0] in {"M_XRF", "M_ALT", "M_CNT"})) and rng.random() < 0.57
            ambiguous = joined or (rng.random() < 0.075) or (next_starts_line and rng.random() < 0.25)
            if starts_line:
                pos = "LSTART"
            elif is_last:
                pos = "RFEND"
            elif next_starts_line:
                pos = "LEND"
            else:
                pos = "LMID"
            if i == 0:
                sep_before = "PAGE" if new_page else ("PARAGRAPH" if new_para else "RECORD")
            elif starts_line:
                sep_before = "LINE"
            elif joined:
                sep_before = "JOIN"
            elif lex in {"M_LOC", "M_HAB", "M_COL", "M_DAT", "M_AUTH", "M_KEY", "M_NUM"}:
                sep_before = "FIELD"
            else:
                sep_before = "SPACE"
            if is_last:
                sep_after = "RECORD"
            elif next_starts_line:
                sep_after = "LINE"
            elif joined or (i + 1 < len(specs) and specs[i + 1][0] in {"M_XRF", "M_ALT", "M_CNT", "M_EQ"} and rng.random() < 0.45):
                sep_after = "JOIN"
            elif i + 1 < len(specs) and specs[i + 1][0] in {"M_LOC", "M_HAB", "M_COL", "M_DAT", "M_AUTH", "M_KEY", "M_NUM"}:
                sep_after = "FIELD"
            else:
                sep_after = "SPACE"
            event_id = event_ids[i]
            visible = _surface(lex, register, hand, pos, joined, rng)
            layout = "L0" if i == 0 else ("L2" if is_scope else ("L3" if lex in {"M_XRF", "M_SEE", "M_ALT"} else "L1"))
            record_pos = "RSTART" if i == 0 else ("REND" if is_last else ("REARLY" if i < len(specs) / 2 else "RLATE"))
            observations.append({
                "world_id": "W06", "corpus_seed": seed, "event_id": event_id,
                "page_id": page_id, "paragraph_id": paragraph_id,
                "record_id": record_id, "line_id": current_line_id,
                "event_index": global_i, "group_index": group_in_line,
                "visible_group": visible, "separator_before": sep_before,
                "separator_after": sep_after, "register_id": register,
                "hand_id": hand, "layout_role": layout,
                "line_position_bin": pos, "record_position_bin": record_pos,
                "ambiguous_boundary": ambiguous,
            })

            relation = _relation_type(lex)
            target = "NONE"
            if relation in {"CROSS_REFERENCE", "INDEX_REFERENCE", "RETURN_RELATION"}:
                # Prefer an earlier occurrence of the next/previous entity.
                candidate_entities = [s[1] for s in specs[i + 1:] + specs[:i] if not s[0].startswith("M_")]
                for candidate in candidate_entities:
                    if candidate in last_event_for_entity:
                        target = last_event_for_entity[candidate]
                        break
                if target == "NONE":
                    target = last_record_event
            elif relation in {"ALTERNATIVE", "EQUIVALENCE", "SYNONYMY", "REVISION"}:
                candidates = [j for j in range(max(0, i - 2), min(len(specs), i + 3)) if j != i and not specs[j][0].startswith("M_")]
                if candidates:
                    target = event_ids[candidates[0]]
            elif relation == "SCOPE_OPEN":
                target = scope_end
            elif relation == "SCOPE_CLOSE":
                target = scope_start
            elif relation == "SCOPE_CONTINUATION":
                target = scope_start

            state_before = states.get(entity, "UNRECORDED") if not lex.startswith("M_") else "NONE"
            if category == "SPECIMEN":
                state_after = {"ACCESSION": "ACCESSIONED", "DETERMINATION": "DETERMINED", "REVISION": "REVISED", "LOAN": "ON_LOAN"}.get(schema, state_before)
            elif category == "TAXON":
                state_after = "INDEXED" if schema.endswith("INDEX") or "SCOPE" in schema else ("CURRENT_NAME" if schema == "REVISION" else "CITED")
            else:
                state_after = "CATALOGUED" if not lex.startswith("M_") else "NONE"
            if not lex.startswith("M_"):
                states[entity] = state_after
                last_event_for_entity[entity] = event_id
            morphemes, component_semantics, fossil, productive = _components(lex, category)
            in_scope_start = scope_start if is_scope else "NONE"
            in_scope_end = scope_end if is_scope else "NONE"
            oracle.append({
                "world_id": "W06", "corpus_seed": seed, "event_id": event_id,
                "domain_id": "TAXONOMIC_COLLECTION", "activity_id": schema,
                "lexical_id": lex, "semantic_entity_id": entity,
                "semantic_category": category,
                "function_class": _function_class(lex, category),
                "relation_type": relation, "relation_target_event_id": target,
                "state_before": state_before, "state_after": state_after,
                "historical_stem_id": hist, "current_morpheme_ids": morphemes,
                "fossilized_component_ids": fossil,
                "construction_id": f"C_{schema}_{'SCOPE' if is_scope else 'FRAME'}",
                "scope_start_event_id": in_scope_start,
                "scope_end_event_id": in_scope_end,
                "record_schema_id": f"RS_{schema}",
                "register_realization_id": f"RR_{register}_{hand}_{pos}",
                "productive_morphology": productive,
                "current_component_semantics": component_semantics,
                "genealogy_stage": "9",
            })
        last_record_event = record_last

    # Reconcile every physical adjacency from the realized hierarchy.  This
    # makes the two views of a boundary identical even where a record ending
    # also opens a paragraph or page.
    observations[0]["separator_before"] = "PAGE"
    for previous, current in zip(observations, observations[1:]):
        if previous["page_id"] != current["page_id"]:
            boundary = "PAGE"
        elif previous["paragraph_id"] != current["paragraph_id"]:
            boundary = "PARAGRAPH"
        elif previous["record_id"] != current["record_id"]:
            boundary = "RECORD"
        elif previous["line_id"] != current["line_id"]:
            boundary = "LINE"
        else:
            boundary = current["separator_before"]
        previous["separator_after"] = boundary
        current["separator_before"] = boundary

    return {
        "observations": observations,
        "oracle": oracle,
        "codebook": [dict(row) for row in CODEBOOK],
        "genealogy": _genealogy(),
    }
