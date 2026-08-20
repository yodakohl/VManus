"""D03: inexpensive oracle-blind frequency/position/recurrence baseline.

The implementation intentionally treats every supplied value as opaque.  It
uses equality, string shape, record/line position and recurrence only; no
semantic interpretation is attempted.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter

from src.decoder_api import CLAIM_FIELDS, REPRESENTATIONS


DECODER_META = {
    "decoder_id": "D03_frequency_position",
    "designer_model": "gpt-5.6-luna",
    "method_family": "frequency_position_recurrence_baseline",
    "oracle_blind": True,
    "supported_representations": [
        "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE", "INFERRED_COMPONENTS",
        "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY",
    ],
}

_META_KEYS = frozenset({"world_id", "corpus_seed", "event_id", "representation",
                        "decoder_id"})

# These are the only observation names that may supply an opaque surface
# identity.  Matching is exact (after case-folding); substring matching could
# accidentally admit an answer-bearing field such as ``oracle_token``.
_ID_NAMES = (
    "identity", "surface", "surface_form", "observable", "observable_surface",
    "symbol", "token", "group", "host", "glyph", "item", "value", "form",
    "text", "string",
)
_RECORD_NAMES = ("record", "line", "folio", "sequence", "stream")
_REGISTER_NAMES = ("register", "hand")
_POS_NAMES = ("position", "index", "offset", "line", "boundary", "column",
             "ordinal", "span")

# Defense in depth for future additions to the explicit allow-lists.  These
# names must never become observable inputs to an anonymous baseline.
_BLOCKED_KEY_PARTS = (
    "oracle", "truth", "meaning", "semantic", "label", "answer", "target",
    "reference", "scope", "category", "gloss", "translation", "english",
    "entity", "lexical", "stem", "function", "operator", "construction",
    "component", "productive", "fossilized", "schema", "cluster", "relation",
    "genealogy", "codebook", "family", "definition", "sense",
)


def _stable(value: object, n: int = 10) -> str:
    raw = repr(value).encode("utf-8", "backslashreplace")
    return "C_" + hashlib.sha256(raw).hexdigest()[:n]


def _canonical(value: object) -> object | None:
    """Return a deterministic opaque value, or None when unsupported.

    In particular, sets are sorted by their canonical representations rather
    than passed through process-randomized ``repr`` output.
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return ("bool", value)
    if isinstance(value, int):
        return ("int", value)
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return ("float", value)
    if isinstance(value, str):
        return ("str", value)
    if isinstance(value, bytes):
        return ("bytes", value.hex())
    if isinstance(value, (list, tuple)):
        items = tuple(_canonical(item) for item in value)
        if any(item is None for item in items):
            return None
        return ("sequence", items)
    if isinstance(value, (set, frozenset)):
        items = [_canonical(item) for item in value]
        if any(item is None for item in items):
            return None
        return ("set", tuple(sorted(items, key=repr)))
    if isinstance(value, dict):
        items = []
        for key, item in value.items():
            if _blocked_key(key):
                return None
            ckey, citem = _canonical(key), _canonical(item)
            if ckey is None or citem is None:
                return None
            items.append((ckey, citem))
        return ("mapping", tuple(sorted(items, key=repr)))
    return None


def _text(value: object) -> str | None:
    canonical = _canonical(value)
    return repr(canonical) if canonical is not None else None


def _normal_key(key: object) -> str:
    return str(key).strip().casefold()


def _blocked_key(key: object) -> bool:
    low = _normal_key(key)
    return any(part in low for part in _BLOCKED_KEY_PARTS)


def _field(row: dict, names: tuple[str, ...]) -> object | None:
    """Read only an explicitly licensed, non-answer-bearing field."""
    for name in names:
        for key, value in row.items():
            low = _normal_key(key)
            if (low == name and low not in _META_KEYS
                    and not _blocked_key(key)):
                canonical = _canonical(value)
                if canonical is not None:
                    return canonical
    return None


def _identity(row: dict) -> str | None:
    value = _field(row, _ID_NAMES)
    return repr(value) if value is not None else None


def _record(row: dict) -> str | None:
    value = _field(row, _RECORD_NAMES)
    return repr(value) if value is not None else None


def _register(row: dict) -> str | None:
    value = _field(row, _REGISTER_NAMES)
    return repr(value) if value is not None else None


def _position(row: dict) -> float | None:
    value = _field(row, _POS_NAMES)
    try:
        # _field returns a canonical scalar/container tuple.  Only scalar
        # values are meaningful positions; containers are unsupported here.
        if value is None or value[0] not in {"int", "float", "str"}:
            return None
        return float(value[1])
    except (TypeError, ValueError):
        return None


def _shape(token: str) -> str:
    if not token:
        return "EMPTY"
    return re.sub(r"[A-Za-z]", "A", re.sub(r"[0-9]", "N", token))


def _cluster(prefix: str, value: object) -> str:
    return prefix + _stable(value)


def _model(train_rows: list[dict]) -> dict:
    identities = [_identity(r) for r in train_rows]
    records_seen = [_record(r) for r in train_rows]
    freq = Counter(value for value in identities if value is not None)
    shape_freq = Counter(_shape(value) for value in identities if value is not None)
    records = Counter(value for value in records_seen if value is not None)
    return {"freq": freq, "shape_freq": shape_freq, "records": records,
            "n": len(train_rows)}


def decode(train_rows: list[dict], held_rows: list[dict], representation: str) -> list[dict]:
    """Fit solely on train_rows and emit one anonymous claim for each held row."""
    if representation not in REPRESENTATIONS:
        raise ValueError("unknown representation")
    if representation not in DECODER_META["supported_representations"]:
        raise ValueError("decoder does not support representation")
    model = _model(train_rows)
    prior: dict[tuple[str, str], str] = {}
    claims = []
    for row in held_rows:
        claim = {k: "UNRESOLVED" for k in CLAIM_FIELDS}
        ident = _identity(row)
        shape = _shape(ident) if ident is not None else None
        rec = _record(row)
        register = _register(row)
        pos = _position(row)
        event_id = row["event_id"]
        claim.update({
            "world_id": row["world_id"], "corpus_seed": row["corpus_seed"],
            "event_id": event_id, "representation": representation,
            "decoder_id": DECODER_META["decoder_id"],
        })
        # Entity, lexical, and stem clusters require a licensed surface
        # identity.  A missing identity must not turn into a hash of a
        # sentinel or of arbitrary row content.
        if ident is not None:
            claim.update({
                "entity_cluster": _cluster("E_", ident),
                "lexical_cluster": _cluster("L_", shape),
                "stem_cluster": _cluster("S_", ident[: max(1, len(ident) // 2)]),
            })
        # Likewise, schema/register claims require an actual record field;
        # there is no ``UNRESOLVED`` sentinel to hash.
        if rec is not None:
            claim["record_schema_cluster"] = _cluster("R_", rec)
            if register is not None:
                claim["register_variant_cluster"] = _cluster("V_", (rec, register))
            elif pos is not None:
                claim["register_variant_cluster"] = _cluster("V_", (rec, round(pos, 3)))
        # Function/operator guesses are intentionally limited to repeated,
        # position-stable opaque forms and never receive semantic names.
        if ident is not None and shape is not None and model["freq"][ident] >= 2:
            claim["function_cluster"] = _cluster("F_", (shape, "recurrent"))
        if pos is not None:
            claim["construction_cluster"] = _cluster("K_", (shape, round(pos, 3)))
        key = (rec, ident)
        if rec is not None and ident is not None and key in prior:
            claim["predicted_relation_target_event_id"] = prior[key]
            claim["confidence"] = min(0.55, 0.25 + 0.05 * model["freq"][ident])
        elif ident is not None and (model["freq"][ident] or model["shape_freq"][shape]):
            claim["confidence"] = 0.20 if model["freq"][ident] else 0.10
        if rec is not None and ident is not None:
            prior[key] = event_id
        claims.append(claim)
    return claims


def classify_world(train_rows: list[dict]) -> dict:
    """Return structural, explicitly non-semantic architecture hypotheses."""
    n = len(train_rows)
    ids = [value for r in train_rows if (value := _identity(r)) is not None]
    unique = len(set(ids))
    repeats = (len(ids) - unique) / len(ids) if ids else 0.0
    records = [value for r in train_rows if (value := _record(r)) is not None]
    record_count = len(set(records))
    # Scores are observational heuristics, not calibrated truth probabilities.
    language_like = min(1.0, 0.20 + 0.65 * repeats)
    notation_like = min(1.0, 0.15 + 0.45 * (record_count / len(records) if records else 0.0))
    codebook_like = min(1.0, 0.10 + 0.75 * (1.0 - unique / len(ids) if ids else 0.0))
    semantics_light_like = min(1.0, 0.35 + 0.35 * repeats)
    arch = "ARCH_RECURRENT" if repeats >= 0.30 else "ARCH_POSITIONAL"
    confidence = min(0.70, 0.20 + abs(repeats - 0.30))
    return {"decoder_id": DECODER_META["decoder_id"],
            "architecture_cluster": arch, "language_like": language_like,
            "notation_like": notation_like, "codebook_like": codebook_like,
            "semantics_light_like": semantics_light_like,
            "confidence": confidence}
