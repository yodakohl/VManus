#!/usr/bin/env python3
"""D01: oracle-blind, train-fitted multiview context/graph decoder.

The implementation deliberately knows no world vocabulary.  It learns a small
set of field roles, token statistics, morphology, and contextual signatures
from the training observations, then uses equality and packet topology only.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import math
import re
from typing import Any


DECODER_META = {
    "decoder_id": "D01_MULTIVIEW_GRAPH",
    "designer_model": "gpt-5.6-sol",
    "method_family": "multiview_equality_context_graph",
    "oracle_blind": True,
    "supported_representations": [
        "FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE",
        "INFERRED_COMPONENTS", "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY",
    ],
}

CLAIM_FIELDS = (
    "world_id", "corpus_seed", "event_id", "representation", "decoder_id",
    "entity_cluster", "lexical_cluster", "stem_cluster", "function_cluster",
    "operator_cluster", "construction_cluster", "register_variant_cluster",
    "semantic_category_cluster", "predicted_relation_target_event_id",
    "predicted_reference_target_event_id", "predicted_scope_start_event_id",
    "predicted_scope_end_event_id", "productive_component_prediction",
    "fossilized_component_prediction", "record_schema_cluster", "confidence",
)

REPRESENTATIONS = set(DECODER_META["supported_representations"])
UNRESOLVED = "UNRESOLVED"

# Fields with these names are provenance or could accidentally disclose an
# answer.  Observation values are otherwise treated only as anonymous symbols.
_BLOCKED_PARTS = {
    "oracle", "truth", "gold", "answer", "meaning", "translation",
    "semantic", "codebook", "genealogy", "family", "architecture",
    "decoder", "label", "target", "relation", "reference", "scope",
}
_IDENTITY = {"world_id", "corpus_seed", "event_id", "representation"}
_REGISTER_HINTS = ("register", "hand", "scribe", "style", "dialect")
_RECORD_HINTS = ("record", "entry", "paragraph", "block", "section", "folio")
_LINE_HINTS = ("line", "row")
_POSITION_HINTS = ("position", "offset", "index", "order", "ordinal", "column")
_TEXT_HINTS = (
    "token", "text", "form", "glyph", "group", "host", "composite",
    "component", "span", "surface", "reading", "value", "symbol",
)
_REP_HINTS = {
    "FULL_GROUP": ("full_group", "fullgroup", "group"),
    "HOST_LIKE": ("host_like", "hostlike", "host"),
    "COMPOSITE_STATE": ("composite_state", "composite", "state"),
    "INFERRED_COMPONENTS": ("inferred_components", "components", "component"),
    "CONSTRUCTION_SPAN": ("construction_span", "construction", "span"),
    "RECORD_TOPOLOGY": ("record_topology", "topology", "record"),
}
_SEPARATOR_CHARS = "|,;:/+=[](){}<>"


def _anon(prefix: str, value: Any) -> str:
    raw = repr(value).encode("utf-8", "backslashreplace")
    return prefix + "_" + hashlib.blake2s(raw, digest_size=7).hexdigest().upper()


def _safe_key(key: Any) -> bool:
    name = str(key).lower()
    if name in _IDENTITY:
        return False
    return not any(part in name for part in _BLOCKED_PARTS)


def _scalar(value: Any) -> bool:
    return value is None or isinstance(value, (str, int, float, bool))


def _value_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, (list, tuple)):
        return " ".join(_value_text(v) for v in value if _scalar(v))
    return str(value).strip()


def _atoms(value: Any) -> tuple[str, ...]:
    """Visible equality atoms; no linguistic inventory is assumed."""
    if isinstance(value, (list, tuple)):
        out = []
        for item in value:
            if _scalar(item):
                out.extend(_atoms(item))
        return tuple(out)
    text = _value_text(value)
    if not text:
        return ()
    pieces = re.split(r"(\s+|[" + re.escape(_SEPARATOR_CHARS) + r"])", text)
    return tuple(p for p in pieces if p and not p.isspace())


def _as_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return float(value)
    if isinstance(value, str) and re.fullmatch(r"[-+]?\d+(?:\.\d+)?", value.strip()):
        return float(value)
    return None


def _quantile(values: list[float], q: float, default: float) -> float:
    if not values:
        return default
    ordered = sorted(values)
    return ordered[int(round((len(ordered) - 1) * max(0.0, min(1.0, q))))]


def _field_score(name: str, hint_words: tuple[str, ...]) -> int:
    low = name.lower()
    return max((len(h) for h in hint_words if h in low), default=0)


def _choose_hint_field(fields: list[str], hints: tuple[str, ...]) -> str | None:
    ranked = sorted(((-_field_score(f, hints), f) for f in fields))
    return ranked[0][1] if ranked and ranked[0][0] < 0 else None


def _common_affixes(words: Counter) -> tuple[set[str], set[str], dict[str, int]]:
    """Find short productive edge strings using train vocabulary alone."""
    prefix_hosts: dict[str, set[str]] = defaultdict(set)
    suffix_hosts: dict[str, set[str]] = defaultdict(set)
    affix_mass = Counter()
    for word, count in words.items():
        if len(word) < 4 or word.isspace():
            continue
        limit = min(4, len(word) - 2)
        for n in range(1, limit + 1):
            pre, suf = word[:n], word[-n:]
            prefix_hosts[pre].add(word[n:])
            suffix_hosts[suf].add(word[:-n])
            affix_mass["P:" + pre] += count
            affix_mass["S:" + suf] += count
    min_hosts = max(3, int(math.sqrt(max(1, len(words))) / 2))
    prefixes = {a for a, hosts in prefix_hosts.items() if len(hosts) >= min_hosts}
    suffixes = {a for a, hosts in suffix_hosts.items() if len(hosts) >= min_hosts}
    # Retain the longest defensible match at an edge, reducing one-character
    # oversegmentation when a longer productive component exists.
    prefixes = {a for a in prefixes if not any(b.startswith(a) and len(b) > len(a)
                                               for b in prefixes)}
    suffixes = {a for a in suffixes if not any(b.endswith(a) and len(b) > len(a)
                                               for b in suffixes)}
    productivity = {}
    for a in prefixes:
        productivity["P:" + a] = len(prefix_hosts[a])
    for a in suffixes:
        productivity["S:" + a] = len(suffix_hosts[a])
    return prefixes, suffixes, productivity


def _fit(train_rows: list[dict], representation: str | None = None) -> dict:
    if not train_rows:
        return {
            "fields": [], "text_fields": [], "primary_text_fields": [], "record_field": None,
            "line_field": None, "position_field": None, "register_field": None,
            "token_freq": Counter(), "token_docs": Counter(), "surface_freq": Counter(),
            "left": defaultdict(Counter), "right": defaultdict(Counter),
            "contexts": defaultdict(Counter), "function": set(), "operator": set(),
            "prefixes": set(), "suffixes": set(), "productivity": {},
            "stems": defaultdict(Counter), "field_cards": {}, "separator_atoms": set(),
            "rare_max": 1, "repeat_min": 2, "train_n": 0,
        }

    field_presence = Counter()
    field_values: dict[str, list[Any]] = defaultdict(list)
    for row in train_rows:
        for key, value in row.items():
            key = str(key)
            if _safe_key(key) and (_scalar(value) or isinstance(value, (list, tuple))):
                field_presence[key] += 1
                field_values[key].append(value)
    min_presence = max(2, int(0.60 * len(train_rows)))
    fields = sorted(k for k, n in field_presence.items() if n >= min_presence)
    field_cards = {k: len({_value_text(v) for v in field_values[k]}) for k in fields}

    register_field = _choose_hint_field(fields, _REGISTER_HINTS)
    record_field = _choose_hint_field(fields, _RECORD_HINTS)
    line_field = _choose_hint_field(fields, _LINE_HINTS)
    position_field = _choose_hint_field(fields, _POSITION_HINTS)

    structural = {x for x in (register_field, record_field, line_field, position_field) if x}
    text_fields = []
    for field in fields:
        if field in structural:
            continue
        values = field_values[field]
        atomized = sum(bool(_atoms(v)) for v in values)
        hinted = _field_score(field, _TEXT_HINTS) > 0
        # A content field must be nonconstant and principally text-like.
        if atomized >= max(2, int(0.60 * len(values))) and field_cards[field] > 1:
            if hinted or any(isinstance(v, (str, list, tuple)) for v in values):
                text_fields.append(field)
    if not text_fields:
        candidates = [f for f in fields if f not in structural and field_cards[f] > 1]
        if candidates:
            text_fields = [max(candidates, key=lambda f: (_field_score(f, _TEXT_HINTS),
                                                          field_cards[f], f))]
    rep_hints = _REP_HINTS.get(representation or "", ())
    primary_text_fields = [f for f in text_fields if _field_score(f, rep_hints) > 0]
    if not primary_text_fields:
        primary_text_fields = list(text_fields)

    token_freq = Counter()
    token_docs = Counter()
    surface_freq = Counter()
    left: dict[str, Counter] = defaultdict(Counter)
    right: dict[str, Counter] = defaultdict(Counter)
    contexts: dict[str, Counter] = defaultdict(Counter)
    separator_atoms = set()
    row_sequences = []
    for row in train_rows:
        seq = []
        surface = []
        for field in text_fields:
            atoms = _atoms(row.get(field))
            if atoms:
                seq.extend(atoms)
                surface.append((field, atoms))
        row_sequences.append(seq)
        surface_freq[tuple(surface)] += 1
        token_freq.update(seq)
        token_docs.update(set(seq))
        for i, token in enumerate(seq):
            lval = seq[i - 1] if i else "^"
            rval = seq[i + 1] if i + 1 < len(seq) else "$"
            left[token][lval] += 1
            right[token][rval] += 1
            contexts[token]["L:" + lval] += 1
            contexts[token]["R:" + rval] += 1
            if len(token) == 1 and token in _SEPARATOR_CHARS:
                separator_atoms.add(token)

    vocab_n = max(1, len(token_freq))
    diversity = {}
    asymmetry = {}
    function_score = {}
    for token, freq in token_freq.items():
        ld, rd = len(left[token]), len(right[token])
        diversity[token] = ld + rd
        asymmetry[token] = abs(ld - rd) / max(1, ld + rd)
        shortness = 1.0 / math.sqrt(max(1, len(token)))
        function_score[token] = math.log1p(freq) * math.log1p(ld + rd) * shortness
    ranked = sorted(token_freq, key=lambda t: (-function_score[t], t))
    function_limit = min(len(ranked), max(2, int(math.sqrt(vocab_n))))
    function = set(ranked[:function_limit])
    operator_ranked = sorted(
        function,
        key=lambda t: (-(asymmetry[t] + (1.0 if t in separator_atoms else 0.0)),
                       -function_score[t], t),
    )
    operator = set(operator_ranked[:max(1, function_limit // 3)])

    lexical_words = Counter({t: n for t, n in token_freq.items()
                             if t not in separator_atoms and len(t) >= 2})
    prefixes, suffixes, productivity = _common_affixes(lexical_words)
    stems: dict[str, Counter] = defaultdict(Counter)
    for word, count in lexical_words.items():
        stem, _, _ = _segment(word, prefixes, suffixes)
        stems[stem][word] += count

    freqs = [float(n) for n in token_freq.values()]
    return {
        "fields": fields, "text_fields": text_fields,
        "primary_text_fields": primary_text_fields, "record_field": record_field,
        "line_field": line_field, "position_field": position_field,
        "register_field": register_field, "token_freq": token_freq,
        "token_docs": token_docs, "surface_freq": surface_freq, "left": left,
        "right": right, "contexts": contexts, "function": function,
        "operator": operator, "prefixes": prefixes, "suffixes": suffixes,
        "productivity": productivity, "stems": stems, "field_cards": field_cards,
        "separator_atoms": separator_atoms,
        "rare_max": max(1, int(_quantile(freqs, 0.45, 1))),
        "repeat_min": max(2, int(_quantile(freqs, 0.60, 2))),
        "train_n": len(train_rows),
    }


def _segment(word: str, prefixes: set[str], suffixes: set[str]) -> tuple[str, str | None, str | None]:
    prefix = max((a for a in prefixes if word.startswith(a) and len(word) - len(a) >= 2),
                 key=len, default=None)
    base = word[len(prefix):] if prefix else word
    suffix = max((a for a in suffixes if base.endswith(a) and len(base) - len(a) >= 2),
                 key=len, default=None)
    stem = base[:-len(suffix)] if suffix else base
    return stem or word, prefix, suffix


def _row_view(row: dict, model: dict) -> dict:
    values = []
    seq = []
    for field in model["text_fields"]:
        atoms = _atoms(row.get(field))
        if atoms:
            seq.extend(atoms)
            if field in model["primary_text_fields"]:
                values.append((field, atoms))
    stems = []
    components = []
    for token in seq:
        if token in model["separator_atoms"] or token in model["function"]:
            continue
        stem, pre, suf = _segment(token, model["prefixes"], model["suffixes"])
        stems.append(stem)
        if pre:
            components.append("P:" + pre)
        if suf:
            components.append("S:" + suf)
    return {"surface": tuple(values), "seq": tuple(seq), "stems": tuple(stems),
            "components": tuple(components)}


def _record_key(row: dict, model: dict) -> tuple:
    fields = [model.get("record_field"), model.get("line_field")]
    vals = tuple(_value_text(row.get(f)) for f in fields if f)
    return vals or ("__packet__",)


def _order_key(index: int, row: dict, model: dict) -> tuple:
    values = []
    for field in (model.get("record_field"), model.get("line_field"),
                  model.get("position_field")):
        if not field:
            continue
        raw = row.get(field)
        num = _as_number(raw)
        values.append((0, num) if num is not None else (1, _value_text(raw)))
    values.append((0, float(index)))
    return tuple(values)


def _cosine(a: Counter, b: Counter) -> float:
    if not a or not b:
        return 0.0
    dot = sum(value * b.get(key, 0) for key, value in a.items())
    na = math.sqrt(sum(value * value for value in a.values()))
    nb = math.sqrt(sum(value * value for value in b.values()))
    return dot / (na * nb) if na and nb else 0.0


def _semantic_signature(tokens: tuple[str, ...], model: dict) -> tuple | None:
    aggregate = Counter()
    for token in tokens:
        aggregate.update(model["contexts"].get(token, {}))
    if not aggregate:
        return None
    # SimHash gives a coarse train-defined distributional bucket without
    # inventing readable categories or fitting a clustering hyperparameter.
    bits = [0.0] * 12
    for feature, weight in aggregate.items():
        digest = hashlib.blake2s(feature.encode("utf-8", "backslashreplace"),
                                digest_size=2).digest()
        number = int.from_bytes(digest, "big")
        for bit in range(12):
            bits[bit] += weight if number & (1 << bit) else -weight
    return tuple(1 if value >= 0 else 0 for value in bits)


def _roles(tokens: tuple[str, ...], model: dict) -> tuple[str, ...]:
    roles = []
    for token in tokens:
        if token in model["operator"]:
            roles.append("O")
        elif token in model["function"]:
            roles.append("F")
        elif token in model["separator_atoms"]:
            roles.append("B")
        elif model["token_freq"].get(token, 0) == 0:
            roles.append("N")
        else:
            roles.append("C")
    return tuple(roles)


def _blank(row: dict, representation: str) -> dict:
    claim = {field: UNRESOLVED for field in CLAIM_FIELDS}
    claim.update({
        "world_id": row["world_id"], "corpus_seed": row["corpus_seed"],
        "event_id": row["event_id"], "representation": representation,
        "decoder_id": DECODER_META["decoder_id"], "confidence": 0.0,
    })
    return claim


def decode(train_rows: list[dict], held_rows: list[dict], representation: str) -> list[dict]:
    """Return one anonymous claim per held event, preserving input order."""
    if representation not in REPRESENTATIONS:
        raise ValueError("unknown representation")
    model = _fit(train_rows, representation)
    if not held_rows:
        return []
    views = [_row_view(row, model) for row in held_rows]

    # Context graph over held packet: equality edges, stem edges, and ordered
    # adjacency within observed record/line topology.  No held statistic alters
    # learned vocabulary or thresholds.
    order = sorted(range(len(held_rows)), key=lambda i: _order_key(i, held_rows[i], model))
    order_rank = {index: rank for rank, index in enumerate(order)}
    previous_equal: dict[tuple, int] = {}
    previous_stem: dict[str, int] = {}
    record_members: dict[tuple, list[int]] = defaultdict(list)
    for index in order:
        record_members[_record_key(held_rows[index], model)].append(index)

    relation_target: dict[int, int] = {}
    reference_target: dict[int, int] = {}
    for index in order:
        view = views[index]
        rkey = _record_key(held_rows[index], model)
        surface = view["surface"]
        if surface and (rkey, surface) in previous_equal:
            reference_target[index] = previous_equal[(rkey, surface)]
        best = None
        for stem in view["stems"]:
            candidate = previous_stem.get((rkey, stem))
            if candidate is not None:
                # Prefer the most recent prior stem-sharing event.
                if best is None or order_rank[candidate] > order_rank[best]:
                    best = candidate
        if best is not None:
            relation_target[index] = best
        if surface:
            previous_equal[(rkey, surface)] = index
        for stem in set(view["stems"]):
            previous_stem[(rkey, stem)] = index

    claims = []
    for index, (row, view) in enumerate(zip(held_rows, views)):
        claim = _blank(row, representation)
        seq, stems = view["seq"], view["stems"]
        known = [t for t in seq if model["token_freq"].get(t, 0) > 0]
        evidence = len(known) / max(1, len(seq))
        recurrence = max((model["token_freq"].get(t, 0) for t in seq), default=0)

        if view["surface"]:
            claim["lexical_cluster"] = _anon("LEX", view["surface"])
        if stems:
            claim["stem_cluster"] = _anon("STM", stems)

        content = [t for t in seq if t not in model["function"]
                   and t not in model["separator_atoms"]]
        entity_tokens = [t for t in content if model["repeat_min"] <= model["token_freq"].get(t, 0)]
        if entity_tokens:
            chosen = min(entity_tokens, key=lambda t: (model["token_freq"][t], t))
            claim["entity_cluster"] = _anon("ENT", chosen)

        funcs = tuple(t for t in seq if t in model["function"])
        ops = tuple(t for t in seq if t in model["operator"])
        if funcs:
            claim["function_cluster"] = _anon("FUN", funcs)
        if ops:
            claim["operator_cluster"] = _anon("OPR", ops)

        role_signature = _roles(seq, model)
        if role_signature:
            claim["construction_cluster"] = _anon(
                "CNS", (len(role_signature), role_signature,
                        tuple(f for f in model["text_fields"] if row.get(f) is not None)))

        register_field = model.get("register_field")
        if register_field and row.get(register_field) not in (None, ""):
            claim["register_variant_cluster"] = _anon("REG", row.get(register_field))

        semantic = _semantic_signature(seq, model)
        if semantic is not None and known:
            claim["semantic_category_cluster"] = _anon("CTX", semantic)

        productive = [c for c in view["components"] if model["productivity"].get(c, 0) >= 3]
        fossilized = [c for c in view["components"] if 0 < model["productivity"].get(c, 0) < 3]
        if productive:
            claim["productive_component_prediction"] = _anon("PRD", tuple(productive))
        if fossilized:
            claim["fossilized_component_prediction"] = _anon("FSL", tuple(fossilized))

        rkey = _record_key(row, model)
        members = record_members[rkey]
        schema = (
            len(members),
            tuple(sorted(f for f in model["fields"] if row.get(f) not in (None, ""))),
            tuple(_roles(views[j]["seq"], model)[:3] for j in members[:4]),
        )
        if model.get("record_field") or model.get("line_field"):
            claim["record_schema_cluster"] = _anon("RSC", schema)

        if index in relation_target:
            claim["predicted_relation_target_event_id"] = held_rows[relation_target[index]]["event_id"]
        if index in reference_target:
            claim["predicted_reference_target_event_id"] = held_rows[reference_target[index]]["event_id"]

        # Scope is asserted only for an operator-bearing event inside explicit
        # record/line structure; bounds are the observed enclosing unit.
        if ops and (model.get("record_field") or model.get("line_field")) and len(members) > 1:
            claim["predicted_scope_start_event_id"] = held_rows[members[0]]["event_id"]
            claim["predicted_scope_end_event_id"] = held_rows[members[-1]]["event_id"]

        support = sum(claim[f] != UNRESOLVED for f in CLAIM_FIELDS[5:-1])
        structural_bonus = 0.08 if (model.get("record_field") or model.get("line_field")) else 0.0
        repeat_bonus = min(0.14, math.log1p(recurrence) / 25.0)
        claim["confidence"] = round(min(0.88, 0.18 + 0.42 * evidence +
                                              0.02 * min(7, support) +
                                              structural_bonus + repeat_bonus), 6)
        claims.append(claim)
    return claims


def classify_world(train_rows: list[dict]) -> dict:
    """Blind structural architecture hypothesis, fitted on train observations."""
    model = _fit(train_rows)
    total = sum(model["token_freq"].values())
    vocab = len(model["token_freq"])
    repeated_mass = sum(n for n in model["token_freq"].values() if n >= 2)
    repeat_ratio = repeated_mass / max(1, total)
    morph_ratio = len(model["productivity"]) / max(1, vocab)
    function_ratio = len(model["function"]) / max(1, vocab)
    structured = bool(model.get("record_field") or model.get("line_field") or
                      model.get("position_field"))
    separator_ratio = sum(model["token_freq"].get(t, 0) for t in model["separator_atoms"]) / max(1, total)

    language_like = bool(total >= 20 and repeat_ratio >= 0.35 and morph_ratio >= 0.01)
    notation_like = bool(structured and (separator_ratio >= 0.02 or function_ratio >= 0.05))
    codebook_like = bool(total >= 20 and repeat_ratio < 0.55 and morph_ratio < 0.02)
    semantics_light_like = bool(repeat_ratio >= 0.65 and vocab <= max(8, int(math.sqrt(max(1, total)) * 3)))
    signature = (
        min(4, int(5 * repeat_ratio)), min(4, int(20 * morph_ratio)),
        min(4, int(10 * function_ratio)), int(structured),
        min(4, int(20 * separator_ratio)),
    )
    features = sum((language_like, notation_like, codebook_like, semantics_light_like))
    confidence = min(0.86, 0.34 + 0.07 * features + 0.05 * int(structured) +
                     0.08 * min(1.0, total / 100.0))
    return {
        "decoder_id": DECODER_META["decoder_id"],
        "architecture_cluster": _anon("ARC", signature),
        "language_like": language_like,
        "notation_like": notation_like,
        "codebook_like": codebook_like,
        "semantics_light_like": semantics_light_like,
        "confidence": round(confidence, 6),
    }
