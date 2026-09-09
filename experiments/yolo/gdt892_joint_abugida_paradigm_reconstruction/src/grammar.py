"""Source-derived feature CFG and exact Earley recognition for GDT892.

Only the supplied sentence records enter induction.  No sentence is repaired,
no lemma is lexicalized, and terminal symbols denote complete projected tags,
not written words.  A recognized paragraph is one or more source-rooted parses.
The returned grammar is JSON serializable and may be round-tripped unchanged.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from typing import Iterable, Mapping


FEATURE_PROJECTION = ("UPOS", "Case", "Number", "Person", "VerbForm", "Mood")
SCHEMA = "GDT892_FEATURE_DEPENDENCY_CFG_V1"
Tag = tuple[str, ...]


def tag_of(word: Mapping) -> Tag:
    """Project exactly the registered six fields, with '_' for absent values."""
    upos = word.get("upos")
    feats = word.get("feats", {})
    if not isinstance(upos, str) or not upos:
        raise ValueError("A nonempty UPOS string is required")
    if not isinstance(feats, Mapping):
        raise ValueError("feats must be a mapping")
    values = [upos]
    for name in FEATURE_PROJECTION[1:]:
        value = feats.get(name, "_")
        if value is None or value == "":
            value = "_"
        if not isinstance(value, str):
            raise ValueError("Feature values must be strings")
        values.append(value)
    return tuple(values)


def _checked_tree(sentence: Mapping):
    """Return intact projective-tree data, or a specific exclusion reason."""
    words = sentence.get("words")
    if not isinstance(words, list) or not words:
        return None, "empty_or_invalid_words"
    ids = []
    for word in words:
        if not isinstance(word, Mapping):
            return None, "invalid_word_record"
        value = word.get("id")
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            return None, "invalid_word_id"
        ids.append(value)
    if len(set(ids)) != len(ids):
        return None, "duplicate_word_id"
    if ids != sorted(ids):
        return None, "non_source_order"
    id_set = set(ids)
    heads = {}
    tags = {}
    for word in words:
        word_id, head = word["id"], word.get("head")
        if isinstance(head, bool) or not isinstance(head, int) or head < 0:
            return None, "invalid_head"
        if head != 0 and head not in id_set:
            return None, "missing_head"
        if head == word_id:
            return None, "self_head"
        if word.get("upos") == "PUNCT":
            return None, "punctuation_not_removed"
        try:
            tags[word_id] = tag_of(word)
        except ValueError:
            return None, "invalid_feature_projection"
        heads[word_id] = head
    roots = [word_id for word_id in ids if heads[word_id] == 0]
    if len(roots) != 1:
        return None, "root_count"

    # Following unchanged parent pointers detects disconnected cycles as well
    # as cycles in the component of an otherwise legitimate root.
    finished = {0}
    for word_id in ids:
        path = set()
        current = word_id
        while current not in finished:
            if current in path:
                return None, "cycle"
            path.add(current)
            current = heads[current]
        finished.update(path)

    children = {word_id: [] for word_id in ids}
    for word_id in ids:
        if heads[word_id]:
            children[heads[word_id]].append(word_id)
    root = roots[0]
    traversal = []
    stack = [root]
    while stack:
        current = stack.pop()
        traversal.append(current)
        stack.extend(children[current])
    if len(traversal) != len(ids):
        return None, "disconnected"

    positions = {word_id: position for position, word_id in enumerate(ids)}
    spans = {}
    for word_id in reversed(traversal):
        left = right = positions[word_id]
        size = 1
        for child in children[word_id]:
            child_left, child_right, child_size = spans[child]
            left = min(left, child_left)
            right = max(right, child_right)
            size += child_size
        # A dependency tree is projective iff every rooted subtree occupies
        # a contiguous interval of the retained source word order.
        if right - left + 1 != size:
            return None, "nonprojective"
        spans[word_id] = (left, right, size)
    return {
        "ids": ids,
        "root": root,
        "tags": tags,
        "children": children,
        "positions": positions,
        "spans": spans,
    }, None


def build_grammar(sentences: Iterable[Mapping]) -> dict:
    """Induce a fixed CFG from complete, intact, projective sentence trees.

    Each dependency rule contains the head's one lexical terminal and its
    immediate dependents' nonterminals in source surface order.  Root and
    paragraph-concatenation rules are separately marked.  Every production
    records all source sentence IDs licensing that production.
    """
    retained = []
    excluded = []
    seen_sentence_ids = set()
    tags = set()
    for sentence in sentences:
        if not isinstance(sentence, Mapping):
            excluded.append({"id": None, "reason": "invalid_sentence_record"})
            continue
        sentence_id = sentence.get("id")
        if not isinstance(sentence_id, str) or not sentence_id:
            excluded.append({"id": sentence_id, "reason": "missing_sentence_id"})
            continue
        if sentence_id in seen_sentence_ids:
            raise ValueError("Duplicate source sentence id: " + sentence_id)
        seen_sentence_ids.add(sentence_id)
        tree, reason = _checked_tree(sentence)
        if reason is not None:
            excluded.append({"id": sentence_id, "reason": reason})
            continue
        retained.append((sentence_id, tree))
        tags.update(tree["tags"].values())

    tag_list = sorted(tags)
    tag_ids = {tag: index for index, tag in enumerate(tag_list)}
    start = len(tag_list)
    # Keys contain only immutable identifiers; source order does not affect
    # production numbering, while source_sentence_ids retain the intake order.
    sources = defaultdict(set)
    for sentence_id, tree in retained:
        for word_id in tree["ids"]:
            lhs = tag_ids[tree["tags"][word_id]]
            pieces = [(tree["positions"][word_id], ("T", lhs))]
            for child in tree["children"][word_id]:
                pieces.append((tree["spans"][child][0],
                               ("N", tag_ids[tree["tags"][child]])))
            rhs = tuple(symbol for _, symbol in sorted(pieces))
            sources[(lhs, rhs, "dependency")].add(sentence_id)
        root_tag = tag_ids[tree["tags"][tree["root"]]]
        sources[(start, (("N", root_tag),), "sentence_root")].add(sentence_id)
        sources[(start, (("N", root_tag), ("N", start)),
                 "paragraph_concatenation")].add(sentence_id)

    productions = []
    by_lhs = [[] for _ in range(start + 1)]
    for (lhs, rhs, kind), sentence_ids in sorted(sources.items()):
        rule_id = len(productions)
        productions.append({
            "lhs": lhs,
            "rhs": [[symbol_kind, tag_id] for symbol_kind, tag_id in rhs],
            "kind": kind,
            "source_sentence_ids": sorted(sentence_ids),
        })
        by_lhs[lhs].append(rule_id)
    return {
        "schema": SCHEMA,
        "feature_projection": list(FEATURE_PROJECTION),
        "tags": [list(tag) for tag in tag_list],
        "start": start,
        "productions": productions,
        "by_lhs": by_lhs,
        "source_sentence_ids": [sentence_id for sentence_id, _ in retained],
        "excluded_sentences": excluded,
        "counts": {
            "included_sentences": len(retained),
            "excluded_sentences": len(excluded),
            "included_words": sum(len(tree["ids"]) for _, tree in retained),
            "tags": len(tag_list),
            "productions": len(productions),
            "exclusion_reasons": dict(sorted(Counter(
                row["reason"] for row in excluded).items())),
        },
    }


def accepts(grammar: Mapping, analyses: Iterable[Iterable[Tag]]) -> bool:
    """Recognize an ambiguous word-tag lattice by exact, epsilon-free Earley.

    Each word position may have several complete analyses.  Feature fields
    from different analyses are never independently mixed.  Unknown complete
    tags cannot scan terminals.  No word, including an unrecognized word, is
    skipped, and acceptance requires consuming the complete input.
    """
    if grammar.get("schema") != SCHEMA:
        raise ValueError("Unsupported grammar schema")
    if tuple(grammar.get("feature_projection", ())) != FEATURE_PROJECTION:
        raise ValueError("Unexpected feature projection")
    tag_ids = {tuple(tag): index for index, tag in enumerate(grammar["tags"])}
    lattice = []
    for alternatives in analyses:
        projected = set()
        for alternative in alternatives:
            tag = tuple(alternative)
            if len(tag) != len(FEATURE_PROJECTION) or not all(
                    isinstance(value, str) for value in tag):
                raise ValueError("Each analysis must be a complete six-string tag")
            if tag in tag_ids:
                projected.add(tag_ids[tag])
        if not projected:
            return False
        lattice.append(projected)
    if not lattice:
        return False

    # Source productions are read directly, avoiding a mutable object-identity
    # cache and preserving the same behavior after a JSON round trip.
    productions = grammar["productions"]
    by_lhs = grammar["by_lhs"]
    start = grammar["start"]
    augmented_id = len(productions)
    augmented = {"lhs": len(by_lhs), "rhs": [["N", start]]}
    n = len(lattice)
    chart = [set() for _ in range(n + 1)]
    queues = [deque() for _ in range(n + 1)]
    waiting = [defaultdict(list) for _ in range(n + 1)]
    predicted = [set() for _ in range(n + 1)]

    def add(position, state):
        if state not in chart[position]:
            chart[position].add(state)
            queues[position].append(state)

    add(0, (augmented_id, 0, 0))
    for position in range(n + 1):
        while queues[position]:
            rule_id, dot, origin = queues[position].popleft()
            production = augmented if rule_id == augmented_id else productions[rule_id]
            rhs = production["rhs"]
            if dot == len(rhs):
                if rule_id == augmented_id:
                    if origin == 0 and position == n:
                        return True
                    continue
                lhs = production["lhs"]
                for parent_rule, parent_dot, parent_origin in waiting[origin].get(lhs, ()):
                    add(position, (parent_rule, parent_dot + 1, parent_origin))
                continue
            kind, symbol = rhs[dot]
            if kind == "T":
                if position < n and symbol in lattice[position]:
                    add(position + 1, (rule_id, dot + 1, origin))
            elif kind == "N":
                waiting[position][symbol].append((rule_id, dot, origin))
                if symbol not in predicted[position]:
                    predicted[position].add(symbol)
                    for next_rule in by_lhs[symbol]:
                        add(position, (next_rule, 0, position))
            else:
                raise ValueError("Invalid grammar symbol kind")
    return False
