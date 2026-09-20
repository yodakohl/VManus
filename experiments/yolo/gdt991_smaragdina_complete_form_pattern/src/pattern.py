"""Complete non-erasing role-form patterns; no semantic-source changes."""
import collections
import itertools
import time
import regex


def key(e):
    return (e['root'], e['role'])


def compile_pattern(events):
    names = {}
    parts = []
    for i, e in enumerate(events):
        symbol = key(e)
        remaining = len(events) - i
        guard = r'(?=(?:[^|]*\|){0,' + str(remaining - 1) + r'}[^|]*\Z)'
        guard += r'(?=(?:[^|]\|*){' + str(remaining) + r'})'
        if symbol in names:
            parts.append(guard + '(?P=' + names[symbol] + ')')
        else:
            names[symbol] = 'v' + str(len(names))
            parts.append(guard + '(?P<' + names[symbol] + '>[^|]+?)')
    return regex.compile(r'\|?'.join(parts), regex.VERSION1), names


def replay(events, words, values):
    assert set(values) == {key(e) for e in events}
    parts = [values[key(e)] for e in events]
    assert all(type(p) is str and p and '|' not in p for p in parts)
    assert ''.join(parts) == ''.join(words)
    ends = set(itertools.accumulate(map(len, parts)))
    assert set(itertools.accumulate(map(len, words))).issubset(ends)
    return parts


def factor(events, words, values, seconds=2, nodes=100000):
    """Factor this one complete witness; not all other pattern witnesses."""
    began = time.monotonic()
    roots = {name: value for (name, role), value in values.items() if role == 0}
    if len(set(roots.values())) != len(roots):
        return dict(status='NO_FACTOR_FOR_THIS_WITNESS', nodes=0, reason='bare_root_collision')
    roles = sorted({role for _, role in values if role})
    choices = {}
    for role in roles:
        present = {name: value for (name, r), value in values.items() if r == role}
        shortest = min(present.values(), key=lambda v: (len(v), v))
        options = []
        for p in range(len(shortest)):
            prefix = shortest[:p]
            for s in range(len(shortest) - p):
                suffix = shortest[len(shortest) - s:] if s else ''
                if all(v.startswith(prefix) and v.endswith(suffix) and len(v) > p + s for v in present.values()):
                    cores = {n: v[p:len(v) - s] if s else v[p:] for n, v in present.items()}
                    if len(set(cores.values())) == len(cores):
                        options.append((prefix, suffix, cores))
        choices[role] = options
    count = 0
    limit = False

    def visit(i, assigned, frames):
        nonlocal count, limit
        count += 1
        if count > nodes or time.monotonic() - began > seconds:
            limit = True
            return None
        if i == len(roles):
            return assigned, frames
        role = roles[i]
        for prefix, suffix, cores in choices[role]:
            if any(n in assigned and assigned[n] != v for n, v in cores.items()):
                continue
            merged = dict(assigned, **cores)
            if len(set(merged.values())) != len(merged):
                continue
            f = dict(frames, **{f'P{role}': prefix, f'S{role}': suffix})
            found = visit(i + 1, merged, f)
            if found:
                return found
            if limit:
                return None
        return None

    answer = visit(0, roots, {})
    if answer:
        roots, frames = answer
        assert set(roots) == {e['root'] for e in events}
        assert all(roots.values()) and len(set(roots.values())) == len(roots)
        assert all(values[key(e)] == frames.get('P' + str(e['role']), '') + roots[e['root']] + frames.get('S' + str(e['role']), '') for e in events)
        replay(events, words, values)
        return dict(status='FULL_ORIGINAL_CODE_WITNESS', roots=roots, frames=frames, nodes=count,
                    code_uniqueness='UNASSESSED', other_pattern_witnesses='NOT_ENUMERATED')
    return dict(status='UNKNOWN_FACTOR_LIMIT' if limit else 'NO_FACTOR_FOR_THIS_WITNESS', nodes=count)


def solve(events, words, seconds=5, factor_seconds=2, factor_nodes=100000):
    began = time.monotonic()
    assert all(w and '|' not in w for w in words)
    pattern, names = compile_pattern(events)
    try:
        matched = pattern.fullmatch('|'.join(words), timeout=seconds)
    except TimeoutError:
        return dict(status='UNKNOWN_PATTERN_LIMIT', elapsed_seconds=time.monotonic() - began)
    if matched is None:
        return dict(status='NO_COMPLETE_ROLE_FORM_PATTERN', elapsed_seconds=time.monotonic() - began)
    values = {symbol: matched.group(name) for symbol, name in names.items()}
    replay(events, words, values)
    result = dict(status='COMPLETE_ROLE_FORM_PATTERN_WITNESS',
                  forms=[dict(root=r, role=s, value=v) for (r, s), v in values.items()])
    result['factorization'] = factor(events, words, values, seconds=factor_seconds, nodes=factor_nodes)
    result['elapsed_seconds'] = time.monotonic() - began
    return result
