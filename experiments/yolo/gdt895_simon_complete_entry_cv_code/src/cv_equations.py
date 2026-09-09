"""Exact fixed-entry CV word equations; invented-data development before freeze."""
import hashlib
import importlib.util
from pathlib import Path
import time

CORE = Path(__file__).resolve().parents[2] / 'gdt892_joint_abugida_paradigm_reconstruction/src/core.py'
CORE_SHA256 = '832651909344428b41c63b817170f6bae1427ae55b78aaa1de138bf02b997abe'
if hashlib.sha256(CORE.read_bytes()).hexdigest() != CORE_SHA256:
    raise ValueError('frozen CV channel source changed')
_spec = importlib.util.spec_from_file_location('gdt892_cv', CORE)
_core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_core)


class BudgetExpired(Exception):
    pass


def extendable(mapping):
    values = list(mapping.values())
    if len(values) > 27 or len(values) != len(set(values)):
        return False
    if any(len(v) not in (1, 2) or any(c not in _core.LETTERS for c in v) for v in values):
        return False
    if any(a != b and b.startswith(a) for a in values for b in values):
        return False
    singles = sum(len(v) == 1 for v in values)
    # Complete unused components using unused two-character strings only.
    return 27 <= singles + 26 * (26 - singles)


def entry_extensions(source_words, cipher_words, inherent, initial=None, deadline=None, stats=None):
    """Yield all observed-component maps extending initial for one fixed entry.

    Unused components have existential completions, never claimed identified.
    A BudgetExpired exception means that the yielded list is only a subset.
    """
    if inherent not in _core.VOWELS:
        raise ValueError('invalid inherent vowel')
    if any(not _core.alphabetic(w) for w in (*source_words, *cipher_words)):
        raise ValueError('words must be complete normalized ASCII letter strings')
    if not source_words or len(source_words) != len(cipher_words):
        return
    mapping = dict(initial or {})
    if set(mapping) - set(_core.inventory(inherent)) or not extendable(mapping):
        return
    rows = [(_core.components(w, inherent), c) for w, c in zip(source_words, cipher_words)]
    if any(not len(parts) <= len(cipher) <= 2 * len(parts) for parts, cipher in rows):
        return
    rows.sort(key=lambda row: (len(row[1]), len(set(row[0])), row[1], row[0]))
    stats = {} if stats is None else stats
    stats.setdefault('nodes', 0)

    def checkpoint():
        stats['nodes'] += 1
        if deadline is not None and time.monotonic() >= deadline:
            raise BudgetExpired()

    def lengths_possible():
        for parts, cipher in rows:
            low = sum(len(mapping[p]) if p in mapping else 1 for p in parts)
            high = sum(len(mapping[p]) if p in mapping else 2 for p in parts)
            if not low <= len(cipher) <= high:
                return False
        return True

    def word(row_index):
        checkpoint()
        if row_index == len(rows):
            if extendable(mapping):
                yield dict(mapping)
            return
        parts, cipher = rows[row_index]

        def match(component_index, character_index):
            checkpoint()
            if component_index == len(parts):
                if character_index == len(cipher):
                    yield None
                return
            component = parts[component_index]
            if component in mapping:
                value = mapping[component]
                if cipher.startswith(value, character_index):
                    yield from match(component_index + 1, character_index + len(value))
                return
            for size in (1, 2):
                value = cipher[character_index:character_index + size]
                if len(value) != size or any(value.startswith(v) or v.startswith(value) for v in mapping.values()):
                    continue
                mapping[component] = value
                try:
                    if lengths_possible():
                        yield from match(component_index + 1, character_index + size)
                finally:
                    del mapping[component]

        for _ in match(0, 0):
            yield from word(row_index + 1)

    if lengths_possible():
        yield from word(0)


def fixed_entry_solutions(source_words, cipher_words, inherent, deadline=None):
    solutions, stats = [], {}
    try:
        for mapping in entry_extensions(source_words, cipher_words, inherent, deadline=deadline, stats=stats):
            solutions.append(mapping)
    except BudgetExpired:
        return {'status': 'UNKNOWN_BUDGET', 'solutions': solutions, 'stats': stats}
    return {'status': 'COMPLETE', 'solutions': solutions, 'stats': stats}
