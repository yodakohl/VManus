#!/usr/bin/env python3
"""Deterministic generator for W03, an engineered catalogue/stock code."""

from __future__ import annotations

import hashlib
import random
from typing import Any


ALPHABET = tuple("αβγδεζηθικλμνξ")

WORLD_META = {
    "world_id": "W03",
    "title": "Engineered Catalogue Code",
    "broad_family": "ENGINEERED_CATALOGUE_CODE",
    "practical_domain": "catalogue and stock indexing",
    "semantics_light": False,
    "organic_evolution": False,
    "clean_engineered_control": True,
    "adversarial_pair_id": "PAIR_CODEBOOK",
    "carrier_profile": "CARRIER_CODEBOOK_MATCHED",
    "alphabet": list(ALPHABET),
    "registers": ["R0", "R1", "R2"],
    "hands": ["H0", "H1"],
    "evolution_processes": [
        "inventory_class_allocation",
        "checksummed_serial_assignment",
        "operator_argument_composition",
        "register_formatting",
        "hand_glyph_bijection",
        "layout_conditioned_rendering",
    ],
    "generator_schema": "GDT395_WORLD_GENERATOR_V1",
}


CATEGORY_ORDER = (
    "FRAME", "ACTIVITY", "OPERATOR", "PRODUCT", "PRODUCT_CLASS",
    "LOCATION", "LOT", "SUPPLIER", "QUANTITY", "STATUS", "RELATION",
)
CATEGORY_TAG = {name: i for i, name in enumerate(CATEGORY_ORDER)}
IRREGULAR_SERIAL = {
    "PROD_00": 0,
    "PROD_01": 1,
    "QTY_00": 2,
    "STATUS_HOLD": 3,
}


def _seeded_rng(seed: int) -> random.Random:
    raw = hashlib.sha256(f"GDT395:W03:{seed}".encode()).digest()
    return random.Random(int.from_bytes(raw[:8], "big"))


def _pipe(values: list[str] | tuple[str, ...]) -> str:
    result = sorted({v for v in values if v and v != "NONE"})
    return "|".join(result) if result else "NONE"


def _checksum(indices: list[int]) -> int:
    return sum((i + 2) * value for i, value in enumerate(indices)) % 14


def _lexicon() -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}

    def add(key: str, category: str, entity: str, function: str) -> None:
        serial = sum(1 for row in entries.values() if row["category"] == category)
        if key in IRREGULAR_SERIAL:
            digits = [13, 0, IRREGULAR_SERIAL[key], 12]
            irregular = "RESERVED_LEGACY_ALIAS"
        else:
            tag = CATEGORY_TAG[category]
            digits = [tag, serial // 14, serial % 14, (tag * 3 + serial) % 14]
            irregular = "NONE"
        code = "".join(ALPHABET[i] for i in digits + [_checksum(digits)])
        entries[key] = {
            "lexical_id": f"LX_{key}",
            "entity": entity,
            "category": category,
            "function": function,
            "stem": f"HS_{len(entries):04d}",
            "code": code,
            "irregular": irregular,
        }

    for key in ("FRAME_OPEN", "FRAME_CLOSE", "CHECK"):
        add(key, "FRAME", f"ENT_{key}", "SCOPE_OPERATOR" if "FRAME" in key else "VALIDATOR")
    for name in ("CATALOG", "RECEIVE", "ISSUE", "TRANSFER", "RECOUNT", "RESERVE", "RETURN", "CROSSREF"):
        add(f"ACT_{name}", "ACTIVITY", f"ENT_ACT_{name}", "STATE_OPERATOR")
    for name in ("AT", "FROM", "TO", "BY", "LOT", "AMOUNT", "STATUS", "BALANCE", "APPLY", "REF", "CLASS", "REASON"):
        add(f"OP_{name}", "OPERATOR", f"ENT_OP_{name}", "RELATION_OPERATOR")
    for i in range(48):
        add(f"PROD_{i:02d}", "PRODUCT", f"ENT_PROD_{i:02d}", "CONTENT")
    for i in range(6):
        add(f"CLASS_{i:02d}", "PRODUCT_CLASS", f"ENT_CLASS_{i:02d}", "CONTENT")
    for i in range(12):
        add(f"LOC_{i:02d}", "LOCATION", f"ENT_LOC_{i:02d}", "CONTENT")
    for i in range(24):
        add(f"LOT_{i:02d}", "LOT", f"ENT_LOT_{i:02d}", "CONTENT")
    for i in range(10):
        add(f"SUP_{i:02d}", "SUPPLIER", f"ENT_SUP_{i:02d}", "CONTENT")
    for i in range(32):
        add(f"QTY_{i:02d}", "QUANTITY", f"ENT_QTY_{i:02d}", "VALUE")
    for name in ("ACTIVE", "LOW", "EMPTY", "HOLD", "REORDER"):
        add(f"STATUS_{name}", "STATUS", f"ENT_STATUS_{name}", "STATE_LABEL")
    for name in ("SUBSTITUTE", "BUNDLE", "SUPERSEDE"):
        add(f"REL_{name}", "RELATION", f"ENT_REL_{name}", "RELATION_OPERATOR")
    return entries


LEXICON = _lexicon()


def _status(quantity: int, reserved: int) -> str:
    free = quantity - reserved
    if free <= 0:
        return "EMPTY"
    if free <= 3:
        return "REORDER"
    if free <= 8:
        return "LOW"
    return "ACTIVE"


def _state_text(state: dict[str, int | str]) -> str:
    return f"ON={state['on']};RS={state['reserved']};LC={state['loc']};ST={_status(int(state['on']), int(state['reserved']))}"


def _weighted_product(rng: random.Random) -> int:
    return rng.choices(range(48), weights=[1.0 / ((i + 2) ** 0.78) for i in range(48)], k=1)[0]


def _token(
    *components: str,
    function: str | None = None,
    relation: str = "NONE",
    target: str = "NONE",
    mutation: bool = False,
    compact: bool = False,
    role: str = "ROLE_1",
) -> dict[str, Any]:
    rows = [LEXICON[key] for key in components]
    return {
        "components": list(components),
        "function": function or rows[0]["function"],
        "relation": relation,
        "target": target,
        "mutation": mutation,
        "compact": compact,
        "role": role,
    }


def _record_tokens(
    schema: str,
    product: int,
    target_product: int,
    qty: int,
    lot: int,
    supplier: int,
    old_loc: int,
    new_loc: int,
    relation: str,
    result_status: str,
    balance_delta: int,
) -> list[dict[str, Any]]:
    p = f"PROD_{product:02d}"
    target_p = f"PROD_{target_product:02d}"
    q = f"QTY_{min(31, qty):02d}"
    lot_key = f"LOT_{lot:02d}"
    supplier_key = f"SUP_{supplier:02d}"
    old_l = f"LOC_{old_loc:02d}"
    new_l = f"LOC_{new_loc:02d}"
    status_key = f"STATUS_{result_status}"
    open_t = _token("FRAME_OPEN", relation="OPENS_SCOPE", target="scope_end", role="ROLE_0")
    close_t = _token("FRAME_CLOSE", relation="CLOSES_SCOPE", target="scope_start", role="ROLE_0")
    act_t = _token(f"ACT_{schema}", mutation=schema not in {"CATALOG", "CROSSREF"}, role="ROLE_2")
    item_t = _token(p, relation="DECLARES_ITEM", target="previous_product", compact=True, role="ROLE_3")
    check_t = _token("CHECK", function="VALIDATOR", relation="VALIDATES", target="scope_start", role="ROLE_6")

    if schema == "CATALOG":
        return [open_t, act_t, item_t,
                _token("OP_CLASS", f"CLASS_{product % 6:02d}", relation="CLASSIFIES", target="item_current", role="ROLE_4"),
                _token("OP_AT", new_l, relation="LOCATES", target="item_current", role="ROLE_4"),
                _token("OP_STATUS", status_key, relation="LABELS_STATE", target="item_current", role="ROLE_5"),
                check_t, close_t]
    if schema in {"RECEIVE", "RETURN"}:
        return [open_t, act_t, item_t,
                _token("OP_BY", supplier_key, relation="SOURCE", target="item_current", role="ROLE_4"),
                _token("OP_LOT", lot_key, relation="LOT_OF", target="item_current", role="ROLE_4"),
                _token("OP_AMOUNT", q, relation="INCREASES_BY", target="item_current", role="ROLE_5"),
                _token("OP_TO", new_l, relation="DESTINATION", target="item_current", role="ROLE_4"),
                _token("OP_STATUS", status_key, relation="RESULT_STATE", target="item_current", role="ROLE_5"),
                check_t, close_t]
    if schema == "ISSUE":
        return [open_t, act_t, item_t,
                _token("OP_REF", p, relation="REFERS_BACK", target="previous_product", compact=True, role="ROLE_4"),
                _token("OP_LOT", lot_key, relation="LOT_OF", target="item_current", role="ROLE_4"),
                _token("OP_AMOUNT", q, relation="DECREASES_BY", target="item_current", role="ROLE_5"),
                _token("OP_FROM", old_l, relation="SOURCE_LOCATION", target="item_current", role="ROLE_4"),
                _token("OP_STATUS", status_key, relation="RESULT_STATE", target="item_current", role="ROLE_5"),
                check_t, close_t]
    if schema == "TRANSFER":
        return [open_t, act_t, item_t,
                _token("OP_REF", p, relation="REFERS_BACK", target="previous_product", compact=True, role="ROLE_4"),
                _token("OP_LOT", lot_key, relation="LOT_OF", target="item_current", role="ROLE_4"),
                _token("OP_FROM", old_l, relation="SOURCE_LOCATION", target="item_current", role="ROLE_4"),
                _token("OP_TO", new_l, relation="DESTINATION", target="item_current", role="ROLE_4"),
                _token("OP_AMOUNT", q, relation="TRANSFER_AMOUNT", target="item_current", role="ROLE_5"),
                _token("OP_STATUS", status_key, relation="RESULT_STATE", target="item_current", role="ROLE_5"),
                _token("OP_APPLY", function="STATE_OPERATOR", relation="APPLIES_CHANGE", target="item_current", role="ROLE_2"),
                check_t, close_t]
    if schema == "RECOUNT":
        return [open_t, act_t,
                _token("OP_AT", old_l, relation="COUNT_LOCATION", target="scope_start", role="ROLE_4"),
                item_t,
                _token("OP_AMOUNT", q, relation="OBSERVED_COUNT", target="item_current", role="ROLE_5"),
                _token("OP_BALANCE", f"QTY_{min(31, balance_delta):02d}", relation="RECONCILES", target="item_current", role="ROLE_5"),
                _token("OP_STATUS", status_key, relation="RESULT_STATE", target="item_current", role="ROLE_5"),
                check_t, close_t]
    if schema == "RESERVE":
        return [open_t, act_t, item_t,
                _token("OP_REF", p, relation="REFERS_BACK", target="previous_product", compact=True, role="ROLE_4"),
                _token("OP_AMOUNT", q, relation="RESERVES_AMOUNT", target="item_current", role="ROLE_5"),
                _token("OP_AT", old_l, relation="LOCATES", target="item_current", role="ROLE_4"),
                _token("OP_STATUS", "STATUS_HOLD", relation="LABELS_STATE", target="item_current", role="ROLE_5"),
                _token("OP_APPLY", function="STATE_OPERATOR", relation="APPLIES_CHANGE", target="item_current", role="ROLE_2"),
                check_t, close_t]
    # CROSSREF is the only non-state schema with an explicit product-to-product edge.
    return [open_t, act_t, item_t,
            _token(f"REL_{relation}", "OP_REF", target_p, function="RELATION_OPERATOR",
                   relation=relation, target="target_previous", compact=True, role="ROLE_4"),
            _token("OP_CLASS", f"CLASS_{target_product % 6:02d}", relation="TARGET_CLASS", target="target_current", role="ROLE_4"),
            _token("OP_REASON", f"REL_{relation}", relation="EXPLAINS_LINK", target="item_current", role="ROLE_5"),
            check_t, close_t]


def _render(components: list[str], register: str, hand: str, compact: bool,
            guarded: bool, line_final: bool) -> str:
    codes = [LEXICON[key]["code"] for key in components]
    if len(codes) == 1:
        raw = codes[0]
    else:
        payload = codes[0][:2] + codes[-1][1:3]
        indices = [ALPHABET.index(ch) for ch in payload]
        raw = payload + ALPHABET[_checksum(indices)]
    chars = list(raw)
    if register == "R1":
        chars = chars[1:] + chars[:1]
        if compact:
            chars = chars[:-1]
    elif register == "R2":
        chars = list(reversed(chars[:-1])) + chars[-1:]
        if guarded:
            guard = (sum(ALPHABET.index(ch) for ch in chars) + 7) % 14
            chars.append(ALPHABET[guard])
    if line_final and len(chars) >= 2:
        chars[0], chars[1] = chars[1], chars[0]
    if hand == "H1":
        chars = [ALPHABET[(ALPHABET.index(ch) + 5) % 14] for ch in chars]
    return "".join(chars)


def _split_lines(length: int, rng: random.Random) -> list[int]:
    if length <= 9:
        return [length]
    possible = [left for left in range(4, 10) if 4 <= length - left <= 9]
    left = rng.choice(possible)
    return [left, length - left]


def _codebook() -> list[dict[str, str]]:
    rows = []
    for key, entry in sorted(LEXICON.items(), key=lambda pair: pair[1]["lexical_id"]):
        rows.append({
            "lexical_id": entry["lexical_id"],
            "semantic_entity_id": entry["entity"],
            "semantic_category": entry["category"],
            "historical_stem_id": entry["stem"],
            "canonical_hidden_form": entry["code"],
            "final_realization_rules": (
                "ATOM=class+serial_hi+serial_lo+parity+checksum;"
                "COMPOSITE=op[0:2]+arg[1:3]+recomputed_checksum;"
                "R0=identity;R1=rotate_left_and_optional_reference_checksum_drop;"
                "R2=reverse_payload_and_optional_state_guard;"
                "LINE_FINAL=swap_first_two;H1=alphabet_shift_5"
            ),
            "irregularity_flags": entry["irregular"],
        })
    return rows


def _genealogy() -> list[dict[str, str]]:
    specifications = [
        (0, "ENG00", "inventory_class_allocation", "SEMANTIC_INVENTORY", "TYPED_SERIALS", "global design", "FALSE", "Entity classes and bounded serial spaces are declared."),
        (1, "ENG01", "checksummed_code_assignment", "TYPED_SERIALS", "FIVE_SYMBOL_ATOMS", "class and within-class serial", "FALSE", "Parity and checksum digits are deterministic."),
        (2, "ENG02", "legacy_reservation", "FOUR_FREQUENT_ATOMS", "RESERVED_BANK_CODES", "declared exception list", "FALSE", "Intentional aliases occupy tag 13; this is engineering, not sound change."),
        (3, "ENG03", "operator_argument_composition", "OPERATOR|ARGUMENT", "PACKED_FIELD", "multi-component field", "TRUE", "Payload slices compose and receive a fresh checksum."),
        (4, "ENG04", "register_formatting", "CANONICAL_OR_PACKED_FIELD", "R0|R1|R2_REALIZATION", "record register and repeated-reference status", "TRUE", "Registers preserve, rotate/compact, or reverse/guard."),
        (5, "ENG05", "hand_bijection", "REGISTER_REALIZATION", "HAND_REALIZATION", "H0 identity; H1 alphabet shift 5", "TRUE", "Both hands retain the same fourteen-symbol inventory."),
        (6, "ENG06", "layout_rendering", "HAND_REALIZATION", "VISIBLE_GROUP", "line-final position", "TRUE", "Line-final groups swap their first two symbols."),
    ]
    return [{
        "stage": str(stage), "rule_id": rule_id, "process_type": process,
        "input_ids": inputs, "output_ids": outputs, "conditioning": conditioning,
        "currently_productive": productive, "notes": notes,
    } for stage, rule_id, process, inputs, outputs, conditioning, productive, notes in specifications]


def generate(seed: int, target_events: int = 8448) -> dict[str, list[dict]]:
    """Generate a completed-record corpus reaching or slightly exceeding target_events."""
    if not isinstance(seed, int):
        raise TypeError("seed must be an int")
    if not isinstance(target_events, int) or target_events < 1:
        raise ValueError("target_events must be a positive int")
    rng = _seeded_rng(seed)
    observations: list[dict] = []
    oracle: list[dict] = []
    stock = {
        i: {"on": rng.randint(4, 26), "reserved": rng.randint(0, 3), "loc": i % 12}
        for i in range(48)
    }
    last_product_event: dict[int, str] = {}
    schemas = ["CATALOG", "RECEIVE", "ISSUE", "TRANSFER", "RECOUNT", "RESERVE", "RETURN", "CROSSREF"]
    schema_weights = [8, 19, 18, 13, 10, 11, 8, 13]
    registers = ["R0", "R1", "R2"]
    register_weights = [58, 27, 15]
    relations = ["SUBSTITUTE", "BUNDLE", "SUPERSEDE"]
    record_number = 0
    event_number = 0

    while len(observations) < target_events:
        schema = rng.choices(schemas, weights=schema_weights, k=1)[0]
        product = _weighted_product(rng)
        target_product = _weighted_product(rng)
        while target_product == product:
            target_product = _weighted_product(rng)
        qty = rng.randint(1, 16)
        lot = rng.randrange(24)
        supplier = rng.randrange(10)
        old_loc = int(stock[product]["loc"])
        new_loc = rng.randrange(12)
        if new_loc == old_loc:
            new_loc = (new_loc + 1 + rng.randrange(11)) % 12
        relation = rng.choice(relations)
        before_on = int(stock[product]["on"])
        state_before = _state_text(stock[product])

        if schema in {"RECEIVE", "RETURN"}:
            stock[product]["on"] = int(stock[product]["on"]) + qty
            stock[product]["loc"] = new_loc
        elif schema == "ISSUE":
            stock[product]["on"] = max(0, int(stock[product]["on"]) - qty)
            stock[product]["reserved"] = min(int(stock[product]["reserved"]), int(stock[product]["on"]))
        elif schema == "TRANSFER":
            stock[product]["loc"] = new_loc
        elif schema == "RECOUNT":
            stock[product]["on"] = qty
            stock[product]["reserved"] = min(int(stock[product]["reserved"]), qty)
        elif schema == "RESERVE":
            available = max(0, int(stock[product]["on"]) - int(stock[product]["reserved"]))
            stock[product]["reserved"] = int(stock[product]["reserved"]) + min(qty, available)
        state_after = _state_text(stock[product])
        result_status = _status(int(stock[product]["on"]), int(stock[product]["reserved"]))

        tokens = _record_tokens(schema, product, target_product, qty, lot, supplier,
                                old_loc, new_loc, relation, result_status,
                                abs(qty - before_on))
        lengths = _split_lines(len(tokens), rng)
        register = rng.choices(registers, weights=register_weights, k=1)[0]
        page_number = record_number // 8
        paragraph_number = record_number // 2
        hand = "H0" if page_number % 3 != 2 else "H1"
        if rng.random() < 0.13:
            hand = "H1" if hand == "H0" else "H0"
        page_id = f"P{page_number:04d}"
        paragraph_id = f"G{paragraph_number:05d}"
        record_id = f"R{record_number:06d}"
        start_event_number = event_number
        event_ids = [f"W03E{event_number + i:08d}" for i in range(len(tokens))]
        scope_start, scope_end = event_ids[0], event_ids[-1]
        item_current = event_ids[2] if schema != "RECOUNT" else event_ids[3]
        # Back-references are resolved against a snapshot taken before this
        # record.  CROSSREF's target_current, by contrast, is the packed field
        # in this record that actually carries the target product entity.
        previous_product = last_product_event.get(product, "NONE")
        target_previous = last_product_event.get(target_product, "NONE")
        target_current = event_ids[3] if schema == "CROSSREF" else target_previous

        line_for_position: list[tuple[int, int, int]] = []
        cursor = 0
        for line_offset, line_length in enumerate(lengths):
            for group_index in range(line_length):
                line_for_position.append((line_offset, group_index, line_length))
            cursor += line_length

        boundaries = ["NONE"] * (len(tokens) + 1)
        if record_number % 8 == 0:
            boundaries[0] = "PAGE"
        elif record_number % 2 == 0:
            boundaries[0] = "PARAGRAPH"
        else:
            boundaries[0] = "RECORD"
        for i in range(1, len(tokens)):
            prev_line, _, _ = line_for_position[i - 1]
            this_line, _, _ = line_for_position[i]
            if prev_line != this_line:
                boundaries[i] = "LINE"
            elif len(tokens[i - 1]["components"]) > 1 or len(tokens[i]["components"]) > 1:
                boundaries[i] = "JOIN" if rng.random() < 0.58 else "SPACE"
            else:
                boundaries[i] = "FIELD" if rng.random() < 0.22 else "SPACE"
        if (record_number + 1) % 8 == 0:
            boundaries[-1] = "PAGE"
        elif (record_number + 1) % 2 == 0:
            boundaries[-1] = "PARAGRAPH"
        else:
            boundaries[-1] = "RECORD"

        for i, token in enumerate(tokens):
            line_offset, group_index, line_length = line_for_position[i]
            event_id = event_ids[i]
            if token["target"] == "scope_end":
                relation_target = scope_end
            elif token["target"] == "scope_start":
                relation_target = scope_start
            elif token["target"] == "item_current":
                relation_target = item_current
            elif token["target"] == "previous_product":
                relation_target = previous_product
            elif token["target"] in {"target_previous", "target_current"}:
                relation_target = target_previous if token["target"] == "target_previous" else target_current
            else:
                relation_target = "NONE"
            compact = bool(token["compact"] and relation_target != "NONE")
            guarded = bool(token["mutation"] or token["function"] == "STATE_OPERATOR")
            visible = _render(token["components"], register, hand, compact,
                              guarded, group_index == line_length - 1)
            if group_index == 0:
                line_bin = "LP0"
            elif group_index == line_length - 1:
                line_bin = "LP2"
            else:
                line_bin = "LP1"
            if i < 2:
                record_bin = "RP0"
            elif i >= len(tokens) - 2:
                record_bin = "RP2"
            else:
                record_bin = "RP1"
            ambiguous = boundaries[i] == "JOIN" or boundaries[i + 1] == "JOIN" or compact
            observations.append({
                "world_id": "W03", "corpus_seed": seed, "event_id": event_id,
                "page_id": page_id, "paragraph_id": paragraph_id, "record_id": record_id,
                "line_id": f"L{record_number:06d}_{line_offset}",
                "event_index": event_number, "group_index": group_index,
                "visible_group": visible, "separator_before": boundaries[i],
                "separator_after": boundaries[i + 1], "register_id": register,
                "hand_id": hand, "layout_role": token["role"],
                "line_position_bin": line_bin, "record_position_bin": record_bin,
                "ambiguous_boundary": ambiguous,
            })
            component_rows = [LEXICON[key] for key in token["components"]]
            oracle.append({
                "world_id": "W03", "corpus_seed": seed, "event_id": event_id,
                "domain_id": "CATALOGUE_STOCK", "activity_id": f"ACTIVITY_{schema}",
                "lexical_id": _pipe([row["lexical_id"] for row in component_rows]),
                "semantic_entity_id": _pipe([row["entity"] for row in component_rows]),
                "semantic_category": _pipe([row["category"] for row in component_rows]),
                "function_class": token["function"], "relation_type": token["relation"],
                "relation_target_event_id": relation_target,
                "state_before": state_before if token["mutation"] else "NONE",
                "state_after": state_after if token["mutation"] else "NONE",
                "historical_stem_id": _pipe([row["stem"] for row in component_rows]),
                "current_morpheme_ids": _pipe([f"M_{key}" for key in token["components"]]),
                "fossilized_component_ids": "NONE", "construction_id": f"CON_{schema}",
                "scope_start_event_id": scope_start, "scope_end_event_id": scope_end,
                "record_schema_id": f"SCH_{schema}",
                "register_realization_id": f"{register}_{hand}",
                "productive_morphology": "TRUE" if len(token["components"]) > 1 else "FALSE",
                "current_component_semantics": _pipe([row["entity"] for row in component_rows]),
                "genealogy_stage": "6",
            })
            event_number += 1
        # Track the most recent event that visibly encodes each product, not
        # merely the record's primary item.  This prevents a previously unseen
        # CROSSREF target from being aliased to the source item's event.
        for token, event_id in zip(tokens, event_ids):
            for component in token["components"]:
                if component.startswith("PROD_"):
                    last_product_event[int(component.removeprefix("PROD_"))] = event_id
        record_number += 1
        assert event_number == start_event_number + len(tokens)

    return {
        "observations": observations,
        "oracle": oracle,
        "codebook": _codebook(),
        "genealogy": _genealogy(),
    }
