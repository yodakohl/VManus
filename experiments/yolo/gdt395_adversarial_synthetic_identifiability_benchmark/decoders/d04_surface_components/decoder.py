"""D04: an oracle-blind surface-component decoder.

The implementation deliberately treats all observed strings as anonymous
forms.  It learns only recurrence, local affixes, and observable layout from
the training packets; no semantic dictionary or external labels are used.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import re
from typing import Any

from src.decoder_api import CLAIM_FIELDS, REPRESENTATIONS, blank_claim


DECODER_META = {
    "decoder_id": "D04_surface_components",
    "designer_model": "gpt-5.6-luna",
    "method_family": "surface recurrence, affix and layout induction",
    "oracle_blind": True,
    "supported_representations": ["FULL_GROUP", "HOST_LIKE", "COMPOSITE_STATE",
                                   "INFERRED_COMPONENTS", "CONSTRUCTION_SPAN",
                                   "RECORD_TOPOLOGY"],
}

_ID_KEYS = {"world_id", "corpus_seed", "event_id", "decoder_id"}
_SURFACE_KEYS = {
    "text", "token", "tokens", "group", "groups", "host", "record", "records",
    "line", "lines", "glyph", "glyphs", "symbol", "symbols", "form", "forms",
    "string", "strings", "surface", "raw", "sequence", "layout", "position",
    "separator", "separators",
}
_STRUCTURAL_KEYS = {
    "group", "groups", "record", "records", "line", "lines", "layout",
    "position", "separator", "separators", "sequence",
}
_FORBIDDEN_HINTS = ("oracle", "truth", "meaning", "semantic", "label", "target",
                   "relation", "reference", "scope", "translation", "gloss")
_PUNCT = re.compile(r"[^a-z0-9]+")
_TOKEN = re.compile(r"[A-Za-z0-9]+")


def _anon(kind: str, value: str) -> str:
    digest = hashlib.sha256((kind + "\0" + value).encode("utf-8")).hexdigest()[:12]
    return kind.upper() + "_" + digest


def _strings(value: Any, key: str = "") -> list[str]:
    """Collect visible string material, excluding provenance identifiers."""
    if isinstance(value, str):
        if key in _ID_KEYS or key.endswith("_id"):
            return []
        return [value] if value.strip() else []
    if isinstance(value, dict):
        out: list[str] = []
        for k, v in value.items():
            lk = str(k).lower()
            if lk in _ID_KEYS or lk.endswith("_id") or any(h in lk for h in _FORBIDDEN_HINTS):
                continue
            if lk in _SURFACE_KEYS:
                out.extend(_strings(v, lk))
        return out
    if isinstance(value, (list, tuple)):
        out = []
        for v in value:
            out.extend(_strings(v, key))
        return out
    return []


def _surface(row: dict) -> tuple[str, list[str]]:
    vals = _strings(row)
    text = " ".join(vals)
    toks = [t.lower() for t in _TOKEN.findall(text)]
    return text, toks


def _norm(s: str) -> str:
    return _PUNCT.sub("", s.lower())


def _model(rows: list[dict]) -> dict:
    forms = Counter(); token_forms = defaultdict(set); token_counts = Counter()
    prefixes = defaultdict(set); suffixes = defaultdict(set)
    substrings = defaultdict(set); contexts = defaultdict(Counter); positions = defaultdict(Counter)
    schemas = Counter(); lengths = Counter(); separators = Counter()
    for row in rows:
        text, toks = _surface(row)
        forms[_norm(text)] += 1
        lengths[len(toks)] += 1
        schemas[tuple(sorted(k for k in row if k in _STRUCTURAL_KEYS))] += 1
        separators.update(ch for ch in text if not ch.isalnum() and not ch.isspace())
        for i, tok in enumerate(toks):
            token_forms[tok].add(tok)
            token_counts[tok] += 1
            positions[ tok ]["first" if i == 0 else "last" if i == len(toks)-1 else "middle"] += 1
            if i:
                contexts[tok][toks[i - 1]] += 1
            for n in range(1, min(4, len(tok)) + 1):
                prefixes[tok[:n]].add(tok)
                suffixes[tok[-n:]].add(tok)
            for n in (2, 3, 4):
                for j in range(max(0, len(tok)-n+1)):
                    substrings[tok[j:j+n]].add(tok)
    # Component recurrence is measured over distinct complete token forms.
    recurring_prefixes = {x for x, fs in prefixes.items() if len(fs) >= 2}
    recurring_suffixes = {x for x, fs in suffixes.items() if len(fs) >= 2}
    recurring_substrings = {x for x, fs in substrings.items() if len(fs) >= 2}
    productive = {x for x in recurring_prefixes | recurring_suffixes | recurring_substrings
                  if len(prefixes.get(x, suffixes.get(x, substrings.get(x, set())))) >= 3}
    fossil = {x for x in (recurring_prefixes | recurring_suffixes | recurring_substrings)
              if x not in productive and len(prefixes.get(x, suffixes.get(x, substrings.get(x, set())))) == 2 and len(x) >= 3}
    return {"forms": forms, "tokens": token_forms, "prefixes": recurring_prefixes,
            "suffixes": recurring_suffixes, "substrings": recurring_substrings,
            "token_counts": token_counts,
            "productive": productive, "fossil": fossil,
            "contexts": contexts, "positions": positions, "schemas": schemas,
            "lengths": lengths, "separators": separators, "n": max(1, len(rows))}


def _components(tok: str, m: dict) -> tuple[list[str], list[str]]:
    # Candidate generation is bounded by the token itself (length <= 4 affix
    # candidates and <= 3 internal candidates), with set membership lookups.
    ps = sorted((tok[:n] for n in range(1, min(4, len(tok)) + 1)
                 if tok[:n] in m["prefixes"]), key=lambda x: (-len(x), x))
    ss = sorted((tok[-n:] for n in range(1, min(4, len(tok)) + 1)
                 if tok[-n:] in m["suffixes"]), key=lambda x: (-len(x), x))
    # Keep the maximal affix set, plus recurring internal material when there
    # is no defensible affix.  Labels remain opaque hashes.
    parts = [_anon("COMP", x) for x in (ps[:2] + ss[:2])]
    internal = sorted((tok[j:j+n] for n in (2, 3, 4) for j in range(max(0, len(tok)-n+1))
                       if tok[j:j+n] in m["substrings"] and tok[j:j+n] not in ps and tok[j:j+n] not in ss),
                      key=lambda x: (-len(x), x))
    if not parts and internal:
        parts.append(_anon("COMP", internal[0]))
    return parts, ps + ss + internal[:1]


def decode(train_rows: list[dict], held_rows: list[dict], representation: str) -> list[dict]:
    if representation not in REPRESENTATIONS:
        raise ValueError("unknown representation")
    m = _model(train_rows)
    out = []
    for row in held_rows:
        claim = blank_claim(row, DECODER_META["decoder_id"], representation)
        text, toks = _surface(row)
        norm = _norm(text)
        unique = list(dict.fromkeys(toks))
        known = [t for t in unique if t in m["tokens"]]
        comps = []
        raw_comps = []
        for tok in unique:
            cs, raw = _components(tok, m); comps.extend(cs); raw_comps.extend(raw)
        if norm and norm in m["forms"]:
            claim["entity_cluster"] = _anon("ENTITY", norm)
            claim["lexical_cluster"] = _anon("LEX", norm)
            claim["confidence"] = min(0.92, 0.55 + 0.08 * m["forms"][norm])
        elif known:
            claim["lexical_cluster"] = _anon("LEX", known[0])
            claim["confidence"] = 0.30
        if toks:
            host = toks[0]
            claim["stem_cluster"] = _anon("STEM", host)
            claim["function_cluster"] = _anon("FUNC", "|".join(sorted(set(raw_comps)))) if raw_comps else "UNRESOLVED"
            claim["record_schema_cluster"] = _anon("SCHEMA", str(tuple(sorted(k for k in row if k in _STRUCTURAL_KEYS))))
            claim["construction_cluster"] = _anon("CONSTR", str(len(toks)) + ":" + "|".join(raw_comps[:3]))
            claim["register_variant_cluster"] = _anon("POS", "first" if len(toks) == 1 else "multi")
        if comps:
            fossils = sorted(set(raw_comps) & m["fossil"])
            productive = sorted(set(raw_comps) & m["productive"])
            if productive:
                claim["productive_component_prediction"] = _anon("PRODUCTIVE", "|".join(productive))
            if fossils and not productive:
                claim["fossilized_component_prediction"] = _anon("FOSSIL", "|".join(fossils))
            claim["operator_cluster"] = _anon("OP", "|".join(sorted(set(comps))))
            claim["semantic_category_cluster"] = "UNRESOLVED"
        if representation == "HOST_LIKE" and toks:
            claim["entity_cluster"] = _anon("HOST", _norm(toks[0]))
        elif representation == "COMPOSITE_STATE" and toks:
            claim["entity_cluster"] = _anon("STATE", "|".join(toks))
        elif representation == "INFERRED_COMPONENTS" and comps:
            claim["entity_cluster"] = _anon("COMPSET", "|".join(sorted(set(comps))))
        elif representation == "CONSTRUCTION_SPAN" and toks:
            claim["entity_cluster"] = _anon("SPAN", str(len(toks)))
        elif representation == "RECORD_TOPOLOGY" and toks:
            claim["entity_cluster"] = _anon("TOPO", str(len(toks)))
        out.append({k: claim[k] for k in CLAIM_FIELDS})
    return out


def classify_world(train_rows: list[dict]) -> dict:
    m = _model(train_rows)
    # `tokens` stores sets for distinct-form membership; use occurrence counts
    # for the repetition ratio used by the structural classifier.
    repeated = sum(n for n in m["token_counts"].values() if n > 1)
    ratio = repeated / max(1, sum(m["token_counts"].values()))
    if ratio > 0.45 and m["prefixes"]:
        arch = "ARCH_RECURRENT_COMPONENTAL"
    elif m["separators"]:
        arch = "ARCH_SEGMENTED_SURFACE"
    else:
        arch = "ARCH_LOW_REPETITION"
    conf = min(0.8, 0.25 + abs(ratio - 0.25))
    return {"decoder_id": DECODER_META["decoder_id"], "architecture_cluster": arch,
            "language_like": "UNRESOLVED", "notation_like": "UNRESOLVED",
            "codebook_like": "UNRESOLVED", "semantics_light_like": "UNRESOLVED",
            "confidence": float(conf)}
