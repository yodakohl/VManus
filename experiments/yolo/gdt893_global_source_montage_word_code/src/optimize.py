"""Exact weighted complete-paragraph compatibility optimization for GDT893.

Inputs contain opaque integer word IDs only.  No source text, transcription,
language model, or per-candidate semantic score enters this optimizer.
"""

from __future__ import annotations

from collections import defaultdict
import math
import time


class _BudgetExpired(Exception):
    pass


def _integer(value):
    return isinstance(value, int) and not isinstance(value, bool)


def solve(candidates, deadline):
    """Enumerate all maximum-weight candidate-index sets under one bijection.

    At most one candidate may be selected for each paragraph.  Selected maps
    must agree in both directions.  Omitted paragraphs receive zero weight.
    Candidate aliases are not collapsed: callers may merge them beforehand
    while preserving provenance, or quotient the complete result afterward.

    ``deadline`` is an absolute ``time.monotonic()`` value.  UNKNOWN_BUDGET
    returns the best *known* feasible sets, not a proof that they are optimal
    or unique.  The empty set is always an available feasible weight0 bound.
    """
    if not isinstance(deadline, (int, float)) or math.isnan(deadline):
        raise ValueError("deadline must be an absolute monotonic time")
    began = time.monotonic()
    best = 0
    optimal = {()}
    root_upper_bound = None
    stage = "preparation"
    operations = 0
    stats = {
        "candidates": 0,
        "paragraphs": 0,
        "negative_weight_candidates_removed": 0,
        "nodes": 0,
        "branches": 0,
        "candidate_compatibility_checks": 0,
        "candidates_filtered": 0,
        "upper_bound_prunes": 0,
        "leaves": 0,
        "best_improvements": 0,
        "maximum_stack_depth": 0,
    }

    def check(force=False):
        nonlocal operations
        operations += 1
        if (force or operations % 256 == 0) and time.monotonic() >= deadline:
            raise _BudgetExpired

    def finish(status):
        stats["elapsed_seconds"] = time.monotonic() - began
        stats["budget_stage"] = stage if status == "UNKNOWN_BUDGET" else None
        stats["best_weight_is_proven"] = status == "COMPLETE"
        stats["upper_bound"] = best if status == "COMPLETE" else root_upper_bound
        return {
            "status": status,
            "best_weight": best,
            "optimal_solutions": [list(indices) for indices in sorted(optimal)],
            "stats": stats,
        }

    try:
        check(True)
        weights = []
        mappings = []
        paragraph_candidates = defaultdict(list)
        all_paragraphs = set()
        for index, candidate in enumerate(candidates):
            check()
            try:
                paragraph = candidate["paragraph"]
                weight = candidate["weight"]
                mapping = candidate["mapping"]
            except (TypeError, KeyError) as error:
                raise ValueError("Each candidate requires paragraph, weight, mapping") from error
            if not isinstance(paragraph, str):
                raise ValueError("paragraph must be a string")
            if not _integer(weight):
                raise ValueError("weight must be an integer")
            if not isinstance(mapping, dict):
                raise ValueError("mapping must be a dictionary")
            pairs = []
            reverse = set()
            for left, right in mapping.items():
                check()
                if not _integer(left) or not _integer(right):
                    raise ValueError("mapping keys and values must be integer IDs")
                if right in reverse:
                    raise ValueError("Each candidate mapping must be injective")
                reverse.add(right)
                pairs.append((left, right))
            weights.append(weight)
            mappings.append(tuple(sorted(pairs)))
            all_paragraphs.add(paragraph)
            # A negative-weight member cannot occur in any optimum: deleting
            # it preserves every compatibility constraint and improves weight.
            # Zero-weight candidates are retained because all ties are required.
            if weight < 0:
                stats["negative_weight_candidates_removed"] += 1
            else:
                paragraph_candidates[paragraph].append(index)
        stats["candidates"] = len(weights)
        stats["paragraphs"] = len(all_paragraphs)
        check(True)

        def domain_weight(domain):
            return max((weights[index] for index in domain), default=0)

        domains = tuple((paragraph, tuple(indices))
                        for paragraph, indices in sorted(paragraph_candidates.items()))
        root_upper_bound = sum(domain_weight(domain) for _, domain in domains)
        missing = object()

        def compatible(index, forward, reverse):
            stats["candidate_compatibility_checks"] += 1
            for left, right in mappings[index]:
                check()
                assigned = forward.get(left, missing)
                if assigned is not missing and assigned != right:
                    return False
                assigned = reverse.get(right, missing)
                if assigned is not missing and assigned != left:
                    return False
            return True

        def frame(remaining, forward, reverse, selected, weight, upper):
            return {"domains": remaining, "forward": forward, "reverse": reverse,
                    "selected": selected, "weight": weight, "upper": upper}

        # Frames keep a branch cursor, so a paragraph with many source aliases
        # does not cause all child key/domain copies to be retained at once.
        stack = [frame(domains, {}, {}, (), 0, root_upper_bound)]
        stats["maximum_stack_depth"] = 1
        stage = "search"
        while stack:
            check(True)
            current = stack[-1]
            if current["upper"] < best:
                stats["upper_bound_prunes"] += 1
                stack.pop()
                continue
            if "choices" not in current:
                stats["nodes"] += 1
                remaining = current["domains"]
                if not remaining:
                    stats["leaves"] += 1
                    selected = tuple(sorted(current["selected"]))
                    weight = current["weight"]
                    if weight > best:
                        best = weight
                        optimal.clear()
                        stats["best_improvements"] += 1
                    if weight == best:
                        optimal.add(selected)
                    stack.pop()
                    continue
                chosen = min(range(len(remaining)), key=lambda position: (
                    len(remaining[position][1]),
                    -domain_weight(remaining[position][1]),
                    remaining[position][0]))
                domain = remaining[chosen][1]
                current["rest"] = remaining[:chosen] + remaining[chosen + 1:]
                current["choices"] = sorted(domain, key=lambda index: (
                    -weights[index], -len(mappings[index]), index)) + [None]
                current["next_choice"] = 0
            if current["next_choice"] == len(current["choices"]):
                stack.pop()
                continue
            choice = current["choices"][current["next_choice"]]
            current["next_choice"] += 1
            stats["branches"] += 1
            if choice is None:
                # Explicitly omitting a whole paragraph does not change any
                # word assignment.  Parent maps are read-only after creation.
                forward = current["forward"]
                reverse = current["reverse"]
                selected = current["selected"]
                weight = current["weight"]
                remaining = current["rest"]
            else:
                forward = dict(current["forward"])
                reverse = dict(current["reverse"])
                for left, right in mappings[choice]:
                    check()
                    forward[left] = right
                    reverse[right] = left
                selected = current["selected"] + (choice,)
                weight = current["weight"] + weights[choice]
                filtered = []
                for paragraph, domain in current["rest"]:
                    check()
                    allowed = []
                    for index in domain:
                        if compatible(index, forward, reverse):
                            allowed.append(index)
                        else:
                            stats["candidates_filtered"] += 1
                    if allowed:
                        filtered.append((paragraph, tuple(allowed)))
                    # An empty domain forces omission, not rejection of other
                    # compatible paragraphs in this maximum-coverage model.
                remaining = tuple(filtered)
            upper = weight + sum(domain_weight(domain) for _, domain in remaining)
            if upper < best:
                stats["upper_bound_prunes"] += 1
                continue
            stack.append(frame(remaining, forward, reverse, selected, weight, upper))
            stats["maximum_stack_depth"] = max(stats["maximum_stack_depth"], len(stack))
        check(True)
        return finish("COMPLETE")
    except _BudgetExpired:
        return finish("UNKNOWN_BUDGET")
