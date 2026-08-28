#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path


LITERAL = "literal_carrier"
SYLLABIC = "syllabic_carrier"
PREFIX = "prefix_operator"
SUFFIX = "suffix_operator"
CONNECTOR = "connector"
CONTEXT = "context_abbreviation_mark"
WHOLE = "wholeform_logogram"
NULL = "null_layout"
CORE_ROLES = {LITERAL, SYLLABIC}


def read_tsv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


@dataclass(frozen=True)
class Piece:
    role: str
    output: str
    source_id: int
    source_level: str


@dataclass(frozen=True)
class ParseResult:
    legal: bool
    output: str
    roles: tuple[str, ...]
    edge_connectors: int
    connector_only: bool
    null_interior: int
    reason: str


EXPECTED_EBNF = [
    "CHUNK := NULL* (CONNECTOR? BODY CONNECTOR? | CONNECTOR | BOUNDARY_COMPOUND) NULL*",
    "BODY := WHOLE | PREFIX{0,2} CORE (CONNECTOR CORE){0,3} SUFFIX{0,2}",
    "CORE := LITERAL | SYLLABIC | CONTEXT_MARK LITERAL | LITERAL CONTEXT_MARK",
    "BOUNDARY_COMPOUND := CONNECTOR SUFFIX",
]


class UnitTree:
    def __init__(self, units_path: Path, compiled_model_path: Path | None = None):
        self.units = {int(row["unit_id"]): row for row in read_tsv(units_path)}
        self.unit_id = {row["unit"]: uid for uid, row in self.units.items()}
        self.primitive_unit = {
            int(row["primitive_id"]): uid
            for uid, row in self.units.items()
            if row["is_primitive"] == "1"
        }
        if len(self.units) != 98 or len(self.primitive_unit) != 34:
            raise ValueError("unexpected GDT613 unit tree")
        self.short_override_role = SYLLABIC
        if compiled_model_path is not None:
            model = json.loads(compiled_model_path.read_text(encoding="utf-8"))
            if model["source_model_id"] != "HISTORICAL_MIXED_ABBREVIATION_FST_34_V1":
                raise ValueError("unexpected compiled model")
            if model["grammar"]["chunk_grammar_ebnf"] != EXPECTED_EBNF:
                raise ValueError("compiled grammar drift")
            if len(model["primitive_cards"]) != 34 or len(model["override_cards"]) != 8:
                raise ValueError("compiled capacity drift")
            if len(model["merges"]) != 64:
                raise ValueError("compiled merge drift")
            for merge in model["merges"]:
                row = self.units[merge["unit_id"]]
                if (
                    row["unit"] != merge["unit"]
                    or int(row["left_unit_id"]) != merge["left_unit_id"]
                    or int(row["right_unit_id"]) != merge["right_unit_id"]
                ):
                    raise ValueError(f"compiled merge mismatch {merge['unit']}")
            self.short_override_role = model["override_transitions"]["short"]
            if self.short_override_role != SYLLABIC:
                raise ValueError("unsupported nonwhole override transition")

    def pieces(self, uid, primitive_mapping, overrides, memo=None):
        memo = {} if memo is None else memo
        if uid in memo:
            return memo[uid]
        row = self.units[uid]
        if uid in overrides:
            kind, output = overrides[uid]
            result = (
                Piece(
                    WHOLE if kind == "wholeform" else self.short_override_role,
                    output,
                    uid,
                    "override",
                ),
            )
        elif row["is_primitive"] == "1":
            pid = int(row["primitive_id"])
            role, output = primitive_mapping[pid]
            result = (Piece(role, output, pid, "primitive"),)
        else:
            result = self.pieces(
                int(row["left_unit_id"]), primitive_mapping, overrides, memo
            ) + self.pieces(
                int(row["right_unit_id"]), primitive_mapping, overrides, memo
            )
        memo[uid] = result
        return result

    def decode(self, sequence, primitive_mapping, overrides):
        memo = {}
        pieces = tuple(
            piece
            for uid in sequence
            for piece in self.pieces(uid, primitive_mapping, overrides, memo)
        )
        return parse_pieces(pieces)


def _parse_core(roles, position):
    if position >= len(roles):
        return None
    if (
        roles[position] == CONTEXT
        and position + 1 < len(roles)
        and roles[position + 1] == LITERAL
    ):
        return position + 2
    if (
        roles[position] == LITERAL
        and position + 1 < len(roles)
        and roles[position + 1] == CONTEXT
    ):
        return position + 2
    if roles[position] in CORE_ROLES:
        return position + 1
    return None


def _parse_body(roles):
    if roles == [WHOLE]:
        return True
    position = 0
    prefixes = 0
    while position < len(roles) and roles[position] == PREFIX and prefixes < 2:
        position += 1
        prefixes += 1
    position = _parse_core(roles, position)
    if position is None:
        return False
    connectors = 0
    while position < len(roles) and roles[position] == CONNECTOR and connectors < 3:
        following = _parse_core(roles, position + 1)
        if following is None:
            break
        position = following
        connectors += 1
    suffixes = 0
    while position < len(roles) and roles[position] == SUFFIX and suffixes < 2:
        position += 1
        suffixes += 1
    return position == len(roles)


def parse_pieces(pieces):
    nonempty = [piece for piece in pieces if piece.output or piece.role == NULL]
    roles = [piece.role for piece in nonempty]
    left = 0
    while left < len(roles) and roles[left] == NULL:
        left += 1
    right = len(roles)
    while right > left and roles[right - 1] == NULL:
        right -= 1
    interior = roles[left:right]
    null_interior = interior.count(NULL)
    output = "".join(piece.output for piece in nonempty if piece.role != NULL)
    if null_interior:
        return ParseResult(
            False,
            output,
            tuple(roles),
            0,
            False,
            null_interior,
            "interior_null",
        )
    if not interior:
        return ParseResult(False, output, tuple(roles), 0, False, 0, "empty")
    if interior == [CONNECTOR]:
        return ParseResult(True, output, tuple(roles), 1, True, 0, "connector_only")
    if interior == [CONNECTOR, SUFFIX]:
        return ParseResult(True, output, tuple(roles), 1, False, 0, "boundary_compound")

    edge_connectors = 0
    body = list(interior)
    if body and body[0] == CONNECTOR:
        edge_connectors += 1
        body = body[1:]
    if body and body[-1] == CONNECTOR:
        edge_connectors += 1
        body = body[:-1]
    legal = _parse_body(body)
    return ParseResult(
        legal,
        output,
        tuple(roles),
        edge_connectors,
        False,
        0,
        "body" if legal else "illegal_body",
    )


class CharacterModel:
    """Interpolated fourth-order 27-symbol model used without a lexicon term."""

    def __init__(self, words):
        size = 27
        ids = []
        for word in words:
            ids.extend((26, 26, 26))
            ids.extend(ord(char) - 97 for char in word)
            ids.append(26)
        unigram = [0.0] * size
        for value in ids:
            unigram[value] += 1
        total = sum(unigram)
        conditional = [(value + 1) / (total + size) for value in unigram]
        for order in range(1, 4):
            context_size = size**order
            counts = [0.0] * (context_size * size)
            if len(ids) > order:
                context = 0
                for value in ids[:order]:
                    context = context * size + value
                for value in ids[order:]:
                    counts[context * size + value] += 1
                    context = (context * size + value) % context_size
            lower_rows = len(conditional) // size
            following = [0.0] * (context_size * size)
            strength = 0.25 * size
            for context in range(context_size):
                row_total = sum(counts[context * size:(context + 1) * size])
                lower = context % lower_rows
                for symbol in range(size):
                    following[context * size + symbol] = (
                        counts[context * size + symbol]
                        + strength * conditional[lower * size + symbol]
                    ) / (row_total + strength)
            conditional = following
        self.log_probability = [math.log2(value) for value in conditional]

    def score_word(self, word):
        if not word:
            return -25.0, 0, 0
        context = 26 * 27 * 27 + 26 * 27 + 26
        modulus = 27**3
        total = 0.0
        for char in word:
            symbol = ord(char) - 97
            total += self.log_probability[context * 27 + symbol]
            context = (context * 27 + symbol) % modulus
        boundary = self.log_probability[context * 27 + 26]
        return total + boundary, len(word), 1

    def cross_entropy(self, weighted_words):
        log_probability = 0.0
        letters = 0.0
        boundaries = 0.0
        for weight, word in weighted_words:
            score, count, boundary = self.score_word(word)
            log_probability += weight * score
            letters += weight * count
            boundaries += weight * boundary
        return {
            "cross_entropy_bits_per_letter": -log_probability / max(1.0, letters),
            "negative_log2_probability": -log_probability,
            "weighted_letters": letters,
            "weighted_boundaries": boundaries,
        }
