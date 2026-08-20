#!/usr/bin/env python3
"""D02: oracle-blind MDL component and record-topology decoder.

All names emitted by this module are hashes of observable structural features.
The model is fitted afresh from ``train_rows`` on every call; held rows are used
only for equality, ordering, and applying the fitted model.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import blake2s
from math import exp, log2
import re
from statistics import mean
from typing import Any, Iterable


DECODER_META = {
    "decoder_id": "D02_MDL_COMPONENTS",
    "designer_model": "OpenAI Codex (Sol)",
    "method_family": "minimum-description-length components and record topology",
    "oracle_blind": True,
    "supported_representations": [
        "FULL_GROUP",
        "HOST_LIKE",
        "COMPOSITE_STATE",
        "INFERRED_COMPONENTS",
        "CONSTRUCTION_SPAN",
        "RECORD_TOPOLOGY",
    ],
}

_REPRESENTATIONS = frozenset(DECODER_META["supported_representations"])
_CLAIM_FIELDS = (
    "world_id", "corpus_seed", "event_id", "representation", "decoder_id",
    "entity_cluster", "lexical_cluster", "stem_cluster", "function_cluster",
    "operator_cluster", "construction_cluster", "register_variant_cluster",
    "semantic_category_cluster", "predicted_relation_target_event_id",
    "predicted_reference_target_event_id", "predicted_scope_start_event_id",
    "predicted_scope_end_event_id", "productive_component_prediction",
    "fossilized_component_prediction", "record_schema_cluster", "confidence",
)

_IDENTITY = {"world_id", "corpus_seed", "event_id"}
_FORBIDDEN_HINTS = (
    "oracle", "gold", "truth", "answer", "meaning", "semantic", "family",
    "codebook", "genealogy", "target", "claim", "decoder", "architecture",
)
_TOPOLOGY_HINTS = (
    "record", "line", "row", "paragraph", "section", "folio", "page",
    "block", "position", "index", "offset", "order", "register", "hand",
    "layout", "column",
)
_SURFACE_HINTS = (
    "surface", "observ", "transcript", "text", "token", "group", "glyph",
    "string", "form", "content", "sequence", "value",
)
_WORD_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def _sid(prefix: str, value: Any) -> str:
    """Stable opaque identifier: output never reveals an observed string."""
    raw = repr(value).encode("utf-8", "surrogatepass")
    return "%s-%s" % (prefix, blake2s(raw, digest_size=6).hexdigest().upper())


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _entropy(counts: Iterable[int]) -> float:
    values = [x for x in counts if x > 0]
    total = sum(values)
    if not total or len(values) < 2:
        return 0.0
    return -sum((x / total) * log2(x / total) for x in values)


def _blank(obs: dict, representation: str) -> dict:
    row = {key: "UNRESOLVED" for key in _CLAIM_FIELDS}
    row.update({
        "world_id": obs["world_id"],
        "corpus_seed": obs["corpus_seed"],
        "event_id": obs["event_id"],
        "representation": representation,
        "decoder_id": DECODER_META["decoder_id"],
        "confidence": 0.0,
    })
    return row


def _is_safe_observation_key(key: str) -> bool:
    lowered = key.lower()
    return not any(hint in lowered for hint in _FORBIDDEN_HINTS)


def _surface_keys(rows: list[dict]) -> tuple[str, ...]:
    """Choose visible surface columns without consulting any row semantics."""
    if not rows:
        return ()
    common = set(rows[0])
    for row in rows[1:]:
        common.intersection_update(row)
    candidates = []
    for key in sorted(common):
        low = key.lower()
        if key in _IDENTITY or not _is_safe_observation_key(key):
            continue
        if any(h in low for h in _TOPOLOGY_HINTS):
            continue
        values = [row.get(key) for row in rows]
        string_fraction = sum(isinstance(v, str) and bool(v) for v in values) / len(values)
        if string_fraction < 0.75:
            continue
        priority = 0 if any(h in low for h in _SURFACE_HINTS) else 1
        candidates.append((priority, key))
    if not candidates:
        return ()
    best_priority = min(p for p, _ in candidates)
    # Prefer named surface fields. With generic packet schemas, retain at most
    # three string columns so recurrence is not swamped by ancillary metadata.
    return tuple(k for p, k in candidates if p == best_priority)[:3]


def _atoms(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, (list, tuple)):
        answer = []
        for item in value:
            answer.extend(_atoms(item))
        return tuple(answer)
    if not isinstance(value, str):
        return ()
    return tuple(_WORD_RE.findall(value))


def _surface(row: dict, keys: tuple[str, ...]) -> tuple[str, ...]:
    answer = []
    for key in keys:
        part = _atoms(row.get(key))
        if part:
            if answer:
                answer.append("\x00")  # observable field boundary
            answer.extend(part)
    return tuple(answer)


def _lexemes(sequence: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(x for x in sequence if x != "\x00" and any(ch.isalnum() for ch in x))


def _separators(sequence: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(x for x in sequence if x == "\x00" or not any(ch.isalnum() for ch in x))


def _topology_keys(rows: list[dict]) -> tuple[str, ...]:
    keys = set().union(*(row.keys() for row in rows)) if rows else set()
    return tuple(sorted(
        k for k in keys
        if k not in _IDENTITY and _is_safe_observation_key(k)
        and any(h in k.lower() for h in _TOPOLOGY_HINTS)
    ))


def _record_key(row: dict, topology_keys: tuple[str, ...]) -> tuple[Any, ...]:
    recordish = [
        k for k in topology_keys
        if any(h in k.lower() for h in ("record", "line", "paragraph", "folio", "page", "block"))
        and "position" not in k.lower() and "index" not in k.lower()
    ]
    if recordish:
        return (row.get("corpus_seed"),) + tuple(row.get(k) for k in recordish)
    return (row.get("corpus_seed"),)


def _order_value(row: dict, topology_keys: tuple[str, ...], fallback: int) -> tuple:
    orderish = [
        k for k in topology_keys
        if any(h in k.lower() for h in ("position", "index", "offset", "order", "column"))
    ]
    values = []
    for key in orderish:
        value = row.get(key)
        if isinstance(value, (int, float, str)):
            values.append((type(value).__name__, value))
    return tuple(values) + (("fallback", fallback),)


class _Model:
    def __init__(self, rows: list[dict]):
        self.rows = list(rows)
        self.surface_keys = _surface_keys(self.rows)
        self.topology_keys = _topology_keys(self.rows)
        self.sequences = [_surface(row, self.surface_keys) for row in self.rows]
        self.words = [_lexemes(seq) for seq in self.sequences]
        self.token_counts = Counter(word for words in self.words for word in words)
        self.group_counts = Counter(self.sequences)
        self.token_seed_sets: dict[str, set] = defaultdict(set)
        for row, words in zip(self.rows, self.words):
            for word in set(words):
                self.token_seed_sets[word].add(row.get("corpus_seed"))
        self.components, self.fossils = self._learn_components()
        self.function_tokens, self.operator_tokens = self._learn_roles()
        self.records = self._make_records(self.rows, self.sequences)
        self.start_shapes, self.end_shapes = self._learn_boundaries()
        self.schema_counts = self._learn_schemas()
        self.register_keys = tuple(
            k for k in self.topology_keys if any(h in k.lower() for h in ("register", "hand"))
        )

    def _learn_components(self) -> tuple[dict[tuple[str, str], float], dict[str, float]]:
        edge_occ = Counter()
        edge_hosts: dict[tuple[str, str], set] = defaultdict(set)
        edge_seeds: dict[tuple[str, str], set] = defaultdict(set)
        internal_occ = Counter()
        internal_hosts: dict[str, set] = defaultdict(set)
        for word, count in self.token_counts.items():
            if len(word) < 3:
                continue
            max_width = min(5, len(word) - 1)
            for width in range(1, max_width + 1):
                for side, component, host in (
                    ("P", word[:width], word[width:]),
                    ("S", word[-width:], word[:-width]),
                ):
                    key = (side, component)
                    edge_occ[key] += count
                    edge_hosts[key].add(host)
                    edge_seeds[key].update(self.token_seed_sets[word])
            for width in range(2, min(5, len(word)) + 1):
                for start in range(1, len(word) - width):
                    component = word[start:start + width]
                    internal_occ[component] += count
                    internal_hosts[component].add(word[:start] + "|" + word[start + width:])

        scored = []
        for key, occurrences in edge_occ.items():
            side, component = key
            hosts = len(edge_hosts[key])
            seeds = len(edge_seeds[key])
            # Encoding gain: saved characters minus lexicon and attachment costs.
            gain = occurrences * max(0.25, len(component) - 0.55) - (2.5 * len(component) + hosts)
            if occurrences >= 4 and hosts >= 3 and seeds >= 2 and gain > 1.0:
                score = gain * log2(1.0 + hosts) * (1.0 + min(seeds, 5) / 10.0)
                scored.append((score, side, component, occurrences, hosts))
        scored.sort(reverse=True)
        components = {}
        for score, side, component, occurrences, hosts in scored[:96]:
            support = min(1.0, 0.30 + 0.08 * log2(occurrences + 1) + 0.07 * log2(hosts + 1))
            components[(side, component)] = support

        fossils = {}
        productive_strings = {component for _, component in components}
        for component, occurrences in internal_occ.items():
            hosts = len(internal_hosts[component])
            gain = occurrences * max(0.2, len(component) - 0.8) - (3.0 * len(component) + hosts)
            if component not in productive_strings and occurrences >= 5 and hosts >= 2 and gain > 1.0:
                fossils[component] = min(0.88, 0.25 + 0.08 * log2(occurrences + hosts))
        fossils = dict(sorted(fossils.items(), key=lambda kv: (-kv[1], -len(kv[0]), kv[0]))[:64])
        return components, fossils

    def split(self, word: str) -> tuple[str, tuple[tuple[str, str], ...], tuple[str, ...], float]:
        options = []
        for (side, component), support in self.components.items():
            if side == "P" and word.startswith(component) and len(component) < len(word):
                options.append((support * len(component), side, component))
            elif side == "S" and word.endswith(component) and len(component) < len(word):
                options.append((support * len(component), side, component))
        prefixes = sorted((x for x in options if x[1] == "P"), reverse=True)
        suffixes = sorted((x for x in options if x[1] == "S"), reverse=True)
        chosen = []
        left = right = 0
        if prefixes:
            _, side, component = prefixes[0]
            chosen.append((side, component)); left = len(component)
        if suffixes:
            _, side, component = suffixes[0]
            if left + len(component) < len(word):
                chosen.append((side, component)); right = len(component)
        host = word[left:len(word) - right if right else None]
        fossil = tuple(
            component for component in self.fossils
            if component in host and component != host
        )
        fossil = tuple(sorted(fossil, key=lambda x: (-len(x), x))[:2])
        supports = [self.components[x] for x in chosen] + [self.fossils[x] for x in fossil]
        confidence = mean(supports) if supports else 0.0
        return host or word, tuple(chosen), fossil, confidence

    def _learn_roles(self) -> tuple[set[str], set[str]]:
        positions: dict[str, Counter] = defaultdict(Counter)
        contexts: dict[str, set] = defaultdict(set)
        for words in self.words:
            for index, word in enumerate(words):
                bucket = "only" if len(words) == 1 else "start" if index == 0 else "end" if index == len(words) - 1 else "middle"
                positions[word][bucket] += 1
                left = words[index - 1] if index else "<"
                right = words[index + 1] if index + 1 < len(words) else ">"
                contexts[word].add((_sid("L", left), _sid("R", right)))
        total_events = max(1, len(self.rows))
        functions = set()
        operators = set()
        for word, count in self.token_counts.items():
            forms = max(1, len(contexts[word]))
            positional = positions[word]
            dominant = max(positional.values(), default=0) / max(1, sum(positional.values()))
            if count >= max(4, total_events // 20) and len(self.token_seed_sets[word]) >= 2 and forms >= 3:
                functions.add(word)
                if dominant >= 0.62 or (positional["middle"] / max(1, count)) >= 0.55:
                    operators.add(word)
        return functions, operators

    def _make_records(self, rows: list[dict], sequences: list[tuple[str, ...]]) -> list[list[tuple[dict, tuple[str, ...], int]]]:
        grouped: dict[tuple, list] = defaultdict(list)
        for index, (row, seq) in enumerate(zip(rows, sequences)):
            grouped[_record_key(row, self.topology_keys)].append((row, seq, index))
        answer = []
        for values in grouped.values():
            values.sort(key=lambda item: _order_value(item[0], self.topology_keys, item[2]))
            answer.append(values)
        return answer

    def shape(self, sequence: tuple[str, ...]) -> tuple:
        shaped = []
        for atom in sequence:
            if atom == "\x00" or not any(ch.isalnum() for ch in atom):
                shaped.append(("SEP", _sid("S", atom)))
                continue
            host, components, fossils, _ = self.split(atom)
            role = "O" if atom in self.operator_tokens else "F" if atom in self.function_tokens else "H"
            shaped.append((role, len(host), tuple(side for side, _ in components), len(fossils)))
        return tuple(shaped)

    def _learn_boundaries(self) -> tuple[set[tuple], set[tuple]]:
        starts = Counter(); ends = Counter(); interior = Counter()
        for record in self.records:
            if not record:
                continue
            shapes = [self.shape(seq) for _, seq, _ in record]
            starts[shapes[0]] += 1; ends[shapes[-1]] += 1
            interior.update(shapes[1:-1])
        start_set = {
            shape for shape, count in starts.items()
            if count >= 2 and count >= 2 * interior[shape] / max(1, len(self.records))
        }
        end_set = {
            shape for shape, count in ends.items()
            if count >= 2 and count >= 2 * interior[shape] / max(1, len(self.records))
        }
        return start_set, end_set

    def _schema(self, record: list[tuple[dict, tuple[str, ...], int]]) -> tuple:
        shapes = [self.shape(seq) for _, seq, _ in record]
        length_bucket = min(8, len(record))
        if not shapes:
            return (0, ())
        roles = tuple(
            "B" if i == 0 else "E" if i == len(shapes) - 1 else "I"
            for i in range(len(shapes))
        )
        compact = tuple((len(s), tuple(x[0] for x in s)) for s in shapes)
        return (length_bucket, roles, compact)

    def _learn_schemas(self) -> Counter:
        return Counter(self._schema(record) for record in self.records if record)

    def group_confidence(self, seq: tuple[str, ...]) -> float:
        count = self.group_counts[seq]
        return _clamp(0.42 + 0.12 * log2(count + 1)) if count else 0.34

    def host_signature(self, seq: tuple[str, ...]) -> tuple:
        signature = []
        for word in _lexemes(seq):
            host, _, _, _ = self.split(word)
            signature.append(host)
        return tuple(signature)

    def component_signature(self, seq: tuple[str, ...]) -> tuple[tuple, tuple, float]:
        productive = []; fossilized = []; supports = []
        for word in _lexemes(seq):
            _, components, fossils, support = self.split(word)
            productive.extend(components); fossilized.extend(fossils)
            if support:
                supports.append(support)
        return tuple(productive), tuple(fossilized), mean(supports) if supports else 0.0

    def role_signature(self, seq: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(
            "O" if word in self.operator_tokens else "F" if word in self.function_tokens else "H"
            for word in _lexemes(seq)
        )

    def architecture(self) -> dict:
        token_total = sum(self.token_counts.values())
        type_total = len(self.token_counts)
        recurrence = 1.0 - type_total / max(1, token_total)
        component_coverage = mean([
            1.0 if any(self.split(word)[1:3]) else 0.0
            for word in self.token_counts
        ]) if self.token_counts else 0.0
        separator_rate = sum(len(_separators(seq)) for seq in self.sequences) / max(1, sum(len(seq) for seq in self.sequences))
        schema_repeat = 1.0 - len(self.schema_counts) / max(1, sum(self.schema_counts.values()))
        role_fraction = len(self.function_tokens) / max(1, type_total)
        seed_spread = mean([
            min(1.0, len(seeds) / 5.0) for seeds in self.token_seed_sets.values()
        ]) if self.token_seed_sets else 0.0

        # Independent, non-exclusive structural hypotheses.
        language = _clamp(0.16 + 0.46 * component_coverage + 0.22 * seed_spread + 0.18 * role_fraction - 0.18 * schema_repeat)
        notation = _clamp(0.12 + 0.34 * separator_rate + 0.42 * schema_repeat + 0.15 * recurrence)
        codebook = _clamp(0.12 + 0.52 * recurrence + 0.20 * seed_spread - 0.38 * component_coverage)
        semantics_light = _clamp(0.10 + 0.48 * schema_repeat + 0.24 * role_fraction - 0.22 * component_coverage)
        features = tuple(round(x * 4) for x in (component_coverage, recurrence, separator_rate, schema_repeat, role_fraction))
        values = [language, notation, codebook, semantics_light]
        evidence = min(1.0, len(self.rows) / 80.0)
        separation = max(values) - sorted(values)[-2] if len(values) > 1 else 0.0
        return {
            "decoder_id": DECODER_META["decoder_id"],
            "architecture_cluster": _sid("ARCH", features),
            "language_like": round(language, 6),
            "notation_like": round(notation, 6),
            "codebook_like": round(codebook, 6),
            "semantics_light_like": round(semantics_light, 6),
            "confidence": round(_clamp(0.22 + 0.48 * evidence + 0.30 * separation), 6),
        }


def _held_relations(model: _Model, held_rows: list[dict], held_sequences: list[tuple[str, ...]]) -> dict:
    """Anonymous, conservative candidates based on recurrence inside held records."""
    records = model._make_records(held_rows, held_sequences)
    result = {row["event_id"]: {} for row in held_rows}
    for record in records:
        if not record:
            continue
        schema = model._schema(record)
        schema_support = model.schema_counts[schema]
        first_id = record[0][0]["event_id"]
        last_id = record[-1][0]["event_id"]
        first_shape = model.shape(record[0][1]); last_shape = model.shape(record[-1][1])
        boundary_ok = schema_support >= 2 and first_shape in model.start_shapes and last_shape in model.end_shapes
        for position, (row, seq, _) in enumerate(record):
            event_id = row["event_id"]
            words = set(_lexemes(seq))
            hosts = set(model.host_signature(seq))
            candidates = []
            for previous_position in range(position):
                previous_row, previous_seq, _ = record[previous_position]
                previous_words = set(_lexemes(previous_seq))
                previous_hosts = set(model.host_signature(previous_seq))
                exact = words & previous_words
                shared_hosts = {h for h in hosts & previous_hosts if h}
                rarity = sum(1.0 / max(1, model.token_counts[w]) for w in exact)
                score = 2.0 * len(exact) + 0.8 * len(shared_hosts) + rarity - 0.06 * (position - previous_position)
                candidates.append((score, previous_row["event_id"], exact, shared_hosts))
            candidates.sort(reverse=True, key=lambda item: item[0])
            if candidates:
                best = candidates[0]
                second_score = candidates[1][0] if len(candidates) > 1 else 0.0
                if best[0] >= 1.2 and best[0] - second_score >= 0.35:
                    result[event_id]["reference"] = best[1]
                has_operator = any(word in model.operator_tokens for word in words)
                if has_operator and best[0] >= 0.7 and best[0] - second_score >= 0.25:
                    result[event_id]["relation"] = best[1]
            if boundary_ok:
                result[event_id]["scope"] = (first_id, last_id)
                result[event_id]["schema"] = schema
                result[event_id]["schema_conf"] = _clamp(0.48 + 0.10 * log2(schema_support + 1))
    return result


def classify_world(train_rows: list[dict]) -> dict:
    """Return four blind architecture probabilities and an anonymous class."""
    return _Model(train_rows).architecture()


def decode(train_rows: list[dict], held_rows: list[dict], representation: str) -> list[dict]:
    """Fit on training observations and emit exactly one claim per held event."""
    if representation not in _REPRESENTATIONS:
        raise ValueError("unsupported representation")
    model = _Model(train_rows)
    held_sequences = [_surface(row, model.surface_keys) for row in held_rows]
    relations = _held_relations(model, held_rows, held_sequences)
    claims = []

    for obs, seq in zip(held_rows, held_sequences):
        claim = _blank(obs, representation)
        words = _lexemes(seq)
        hosts = model.host_signature(seq)
        productive, fossils, component_conf = model.component_signature(seq)
        roles = model.role_signature(seq)
        topology = relations.get(obs["event_id"], {})
        confidences = []

        if representation == "FULL_GROUP":
            if seq:
                claim["lexical_cluster"] = _sid("LEX", seq)
                confidences.append(model.group_confidence(seq))
            if model.register_keys:
                visible = tuple(obs.get(k) for k in model.register_keys)
                if any(x is not None for x in visible):
                    claim["register_variant_cluster"] = _sid("REG", (hosts, visible))
                    confidences.append(0.58)

        elif representation == "HOST_LIKE":
            if hosts and (productive or any(model.token_counts[w] >= 2 for w in words)):
                claim["stem_cluster"] = _sid("HOST", hosts)
                claim["entity_cluster"] = _sid("ENT", (hosts, len(words)))
                confidences.append(max(0.42, component_conf))
            if roles:
                claim["semantic_category_cluster"] = _sid("CAT", (roles, len(seq)))
                confidences.append(0.40 + 0.08 * bool(set(words) & model.function_tokens))

        elif representation == "COMPOSITE_STATE":
            if hosts and productive:
                claim["entity_cluster"] = _sid("ENT", (hosts, len(words)))
                claim["stem_cluster"] = _sid("HOST", hosts)
                confidences.append(max(0.48, component_conf))
            functions = tuple(word for word in words if word in model.function_tokens)
            operators = tuple(word for word in words if word in model.operator_tokens)
            if functions:
                claim["function_cluster"] = _sid("FUNC", tuple(_sid("F", x) for x in functions))
                confidences.append(0.58)
            if operators:
                claim["operator_cluster"] = _sid("OPER", tuple(_sid("O", x) for x in operators))
                confidences.append(0.62)
            if roles and (productive or functions):
                claim["construction_cluster"] = _sid("STATE", (roles, tuple(s for s, _ in productive)))
                confidences.append(0.52)

        elif representation == "INFERRED_COMPONENTS":
            if hosts and productive:
                claim["stem_cluster"] = _sid("HOST", hosts)
                claim["productive_component_prediction"] = "+".join(
                    _sid("CMP" + side, component) for side, component in productive
                )
                confidences.append(max(0.50, component_conf))
            if fossils:
                claim["fossilized_component_prediction"] = "+".join(
                    _sid("FOS", component) for component in fossils
                )
                confidences.append(max(0.42, component_conf * 0.9))
            if productive or fossils:
                claim["construction_cluster"] = _sid(
                    "MORPH", (tuple(side for side, _ in productive), len(fossils), roles)
                )

        elif representation == "CONSTRUCTION_SPAN":
            if roles and (set(words) & (model.function_tokens | model.operator_tokens) or productive):
                claim["construction_cluster"] = _sid(
                    "CONS", (roles, tuple(side for side, _ in productive), model.shape(seq))
                )
                confidences.append(max(0.44, component_conf))
            if "relation" in topology:
                claim["predicted_relation_target_event_id"] = topology["relation"]
                confidences.append(0.61)
            if "reference" in topology:
                claim["predicted_reference_target_event_id"] = topology["reference"]
                confidences.append(0.59)
            if "scope" in topology:
                claim["predicted_scope_start_event_id"], claim["predicted_scope_end_event_id"] = topology["scope"]
                confidences.append(topology["schema_conf"])

        elif representation == "RECORD_TOPOLOGY":
            if "schema" in topology:
                claim["record_schema_cluster"] = _sid("SCHEMA", topology["schema"])
                claim["predicted_scope_start_event_id"], claim["predicted_scope_end_event_id"] = topology["scope"]
                confidences.append(topology["schema_conf"])
            if "relation" in topology:
                claim["predicted_relation_target_event_id"] = topology["relation"]
                confidences.append(0.58)
            if "reference" in topology:
                claim["predicted_reference_target_event_id"] = topology["reference"]
                confidences.append(0.56)
            if model.shape(seq):
                claim["construction_cluster"] = _sid("ROLE", model.shape(seq))
                confidences.append(0.38)

        claim["confidence"] = round(_clamp(mean(confidences) if confidences else 0.0), 6)
        claims.append(claim)
    return claims

