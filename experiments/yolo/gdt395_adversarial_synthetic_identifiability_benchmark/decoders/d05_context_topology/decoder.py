"""D05: an oracle-blind context/topology decoder.

This deliberately uses only observable row structure.  Labels are stable,
anonymous identifiers (hashes) rather than semantic guesses.  The decoder is
kept dependency-free so it can also be used as a small audit reference.
"""
from __future__ import annotations

import hashlib
import math
import re
from collections import Counter, defaultdict

try:  # Works both as a package import and when a harness loads this file.
    from ...src.decoder_api import blank_claim
except ImportError:  # pragma: no cover - harness compatibility path
    _CLAIM_FIELDS = ("world_id", "corpus_seed", "event_id", "representation", "decoder_id",
        "entity_cluster", "lexical_cluster", "stem_cluster", "function_cluster",
        "operator_cluster", "construction_cluster", "register_variant_cluster",
        "semantic_category_cluster", "predicted_relation_target_event_id",
        "predicted_reference_target_event_id", "predicted_scope_start_event_id",
        "predicted_scope_end_event_id", "productive_component_prediction",
        "fossilized_component_prediction", "record_schema_cluster", "confidence")
    def blank_claim(obs, decoder_id, representation):
        row = {k: "UNRESOLVED" for k in _CLAIM_FIELDS}
        row.update({"world_id": obs["world_id"], "corpus_seed": obs["corpus_seed"],
                    "event_id": obs["event_id"], "representation": representation,
                    "decoder_id": decoder_id, "confidence": 0.0})
        return row

DECODER_META = {
    "decoder_id": "D05",
    "designer_model": "gpt-5.6-luna",
    "method_family": "cooccurrence_record_topology_graph",
    "oracle_blind": True,
    "supported_representations": ["FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE",
        "INFERRED_COMPONENTS", "CONSTRUCTION_SPAN", "RECORD_TOPOLOGY"],
}

_META = {"world_id", "corpus_seed", "event_id", "representation", "decoder_id"}
_WORD_KEYS = ("text", "token", "surface", "glyphs", "group", "host", "string",
              "symbol", "atom")
_REC_KEYS = ("record_id", "record", "line_id", "line", "row_id", "page", "folio")
_SEP = re.compile(r"[^\w]+", re.UNICODE)
_BLOCKED = re.compile(r"(?:oracle|truth|meaning|semantic|label)", re.IGNORECASE)

def _digest(tag, value):
    return tag + "_" + hashlib.sha1(str(value).encode("utf-8")).hexdigest()[:10]

def _scalar(value):
    # Lists/sets/dicts are not licensed as opaque surface strings.  This also
    # prevents representation-dependent Python stringification.
    if value is None or isinstance(value, (list, tuple, set, frozenset, dict)):
        return None
    text = str(value)
    return text if text else None

def _text(row):
    for k in _WORD_KEYS:
        if k in row and not _BLOCKED.search(k):
            value = _scalar(row[k])
            if value is not None:
                return value
    return None

def _record(row):
    for k in _REC_KEYS:
        if k in row and not _BLOCKED.search(k):
            value = _scalar(row[k])
            if value is not None:
                return value
    return None

def _parts(s):
    if s is None:
        return ()
    p = [x for x in _SEP.split(s.lower()) if x]
    return tuple(p)

class _Model:
    def __init__(self, rows):
        self.rows = list(rows)
        self.count = Counter()
        self.neigh = defaultdict(Counter)
        self.rec_shapes = Counter()
        self.rec_pos = defaultdict(Counter)
        self.parts = Counter()
        self.events_by_rec = defaultdict(list)
        self.token_cluster = {}
        self.schema_cluster = {}
        self.record_sizes = Counter()
        self._fit()

    def _fit(self):
        last = None
        for i, row in enumerate(self.rows):
            t = _text(row); r = _record(row)
            if t is not None:
                self.count[t] += 1
                self.parts.update(_parts(t))
                if last is not None: self.neigh[last][t] += 1; self.neigh[t][last] += 1
                last = t
            if r is not None:
                self.events_by_rec[r].append(row.get("event_id"))
                self.rec_pos[r][len(self.events_by_rec[r]) - 1] += 1
        # Connected-component-like anonymous communities: deterministic
        # majority label propagation on the training cooccurrence graph.
        labels = {t: t for t in self.count}
        for _ in range(4):
            for t in sorted(labels):
                candidates = self.neigh[t]
                if candidates:
                    best = max(candidates, key=lambda x: (candidates[x], -len(x), x))
                    labels[t] = min(labels[t], labels.get(best, best))
        for t in labels: self.token_cluster[t] = _digest("ctx", labels[t])
        for r, es in self.events_by_rec.items():
            self.record_sizes[r] = len(es)
            shape = (len(es), tuple(sorted(self.rec_pos[r])))
            self.rec_shapes[shape] += 1
        for shape in self.rec_shapes: self.schema_cluster[shape] = _digest("schema", shape)

    def token(self, t):
        return self.token_cluster.get(t, "UNRESOLVED") if t is not None else "UNRESOLVED"

    def schema(self, row):
        r = _record(row)
        if r is None:
            return "UNRESOLVED"
        # Held records are assigned the nearest observed arity/position shape.
        n = self.record_sizes.get(r, 1)
        if not n: n = 1
        shape = min(self.rec_shapes, key=lambda s: abs(s[0] - n)) if self.rec_shapes else None
        return self.schema_cluster.get(shape, "UNRESOLVED")

def _confidence(model, t):
    if t is None:
        return 0.0
    if t in model.count:
        return min(0.92, 0.42 + 0.10 * math.log1p(model.count[t]) +
                   0.04 * min(4, sum(model.neigh[t].values())))
    return 0.16

def decode(train_rows: list[dict], held_rows: list[dict], representation: str) -> list[dict]:
    """Fit exclusively on train_rows and emit one complete claim per held row."""
    if representation not in DECODER_META["supported_representations"]:
        raise ValueError("unsupported representation")
    model = _Model(train_rows)
    out = []
    for i, obs in enumerate(held_rows):
        row = blank_claim(obs, DECODER_META["decoder_id"], representation)
        t = _text(obs); parts = _parts(t); c = _confidence(model, t)
        ctx = model.token(t)
        if t is not None:
            row["lexical_cluster"] = ctx
            row["stem_cluster"] = _digest("stem", parts[0]) if parts else "UNRESOLVED"
            row["entity_cluster"] = _digest("entity", ctx)
            row["function_cluster"] = _digest("function", (len(parts), ctx))
            row["operator_cluster"] = _digest("operator", tuple(sorted(set(parts))))
            row["construction_cluster"] = _digest("construction", (len(t), len(parts)))
        rec = _record(obs)
        if rec is not None:
            row["register_variant_cluster"] = _digest("register", rec)
            row["record_schema_cluster"] = model.schema(obs)
        row["confidence"] = round(c, 6)
        if representation in ("INFERRED_COMPONENTS", "COMPOSITE_STATE"):
            row["productive_component_prediction"] = (_digest("productive", parts[0])
                                                        if parts else "UNRESOLVED")
            row["fossilized_component_prediction"] = (_digest("fossil", parts[-1])
                                                        if len(parts) > 1 else "UNRESOLVED")
        # No visible alignment is sufficient for directional claims; remain
        # conservative about relations, references, and scope.
        out.append(row)
    return out

def classify_world(train_rows: list[dict]) -> dict:
    model = _Model(train_rows)
    n = len(train_rows); uniq = len(model.count)
    repeat = 1.0 - (uniq / n if n else 1.0)
    links = sum(sum(v.values()) for v in model.neigh.values()) / max(1, n)
    if not model.count and not model.events_by_rec:
        return {"decoder_id": "D05", "architecture_cluster": "UNRESOLVED",
                "language_like": "UNRESOLVED", "notation_like": "UNRESOLVED",
                "codebook_like": "UNRESOLVED", "semantics_light_like": "UNRESOLVED",
                "confidence": 0.0}
    if repeat > .55 and links < 1.5: arch = "architecture_codebook_like"
    elif links > 3.0: arch = "architecture_contextual_language_like"
    else: arch = "architecture_mixed_structural"
    conf = min(.86, .30 + .35 * min(1, abs(repeat-.3)*2) + .08 * min(4, links))
    return {"decoder_id": "D05", "architecture_cluster": _digest("arch", arch),
            "language_like": "HIGH" if links > 3 else "LOW",
            "notation_like": "HIGH" if links <= 3 else "MEDIUM",
            "codebook_like": "HIGH" if repeat > .55 else "LOW",
            "semantics_light_like": "UNRESOLVED", "confidence": round(conf, 6)}
