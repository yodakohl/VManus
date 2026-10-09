"""IDEA972's invented, paid source carrier. No native key or fit."""
import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).parent
CONTRACT = BASE / 'COMMON_SUFFIX_BLOCK_CARRIER_CONTRACT_20261007.json'
SPEC = json.loads(CONTRACT.read_text())
assert hashlib.sha256(Path(SPEC['parent_path']).read_bytes()).hexdigest() == SPEC['parent_sha256']
SIGNS = SPEC['working_signs']
CHARACTERS = SPEC['source_characters']
DIRECT = dict(zip(SPEC['literal_code']['direct_source'], SPEC['literal_code']['direct_signs']))
CODES = {c: (s,) for c, s in DIRECT.items()}
for i, c in enumerate(SPEC['literal_code']['escaped_source']):
    CODES[c] = ('q', SIGNS[i // 22], SIGNS[i % 22])
INVERSE = {v: k for k, v in CODES.items()}
assert len(CODES) == len(INVERSE) == 82
MORE = ('q', 'q', 'q', 'q', 'a')
LAST = ('q', 'q', 'q', 'q', 'o')


def letters(text):
    return tuple(u for c in text for u in CODES[c])


def unletters(units):
    result = []; i = 0
    while i < len(units):
        size = 3 if units[i] == 'q' else 1
        part = tuple(units[i:i + size])
        if part not in INVERSE:
            raise ValueError('invalid literal code')
        result.append(INVERSE[part]); i += size
    return ''.join(result)


def common_suffix(a, b):
    n = 0
    for x, y in zip(a[::-1], b[::-1]):
        if x != y:
            break
        n += 1
    return a[-n:] if n else ''


def eligible(word):
    return re.fullmatch('[a-z]+', word) is not None


def logical_groups(paragraph, compress=True):
    words = paragraph.split(' ')
    if not all(w and set(w) <= set(CHARACTERS) for w in words):
        raise ValueError('outside declared normalized source domain')
    out = []; i = 0
    while i < len(words):
        s = ''
        if compress and i + 1 < len(words) and eligible(words[i]) and eligible(words[i + 1]):
            s = common_suffix(words[i], words[i + 1])
        if len(s) < 2:
            out.append(letters(words[i])); i += 1
            continue
        out.append(('q', 'q') + letters(s))
        while i < len(words) and eligible(words[i]) and words[i].endswith(s):
            prefix = words[i][:-len(s)]
            out.append(letters(prefix) if prefix else ('q',))
            i += 1
        out.append(('q', 'q'))
    return out


def frame(groups):
    result = []
    for g in groups:
        if len(g) <= 12:
            result.append(g)
        else:
            chunks = [g[i:i + 12] for i in range(0, len(g), 12)]
            result.extend((LAST if i == len(chunks) - 1 else MORE) + chunk
                          for i, chunk in enumerate(chunks))
    return result


def unframe(groups):
    out = []; pending = None
    for group in groups:
        g = tuple(group)
        if g[:4] == ('q',) * 4:
            tag, payload = g[:5], g[5:]
            if tag == MORE and len(payload) == 12:
                pending = (pending or ()) + payload
            elif tag == LAST and pending is not None and 1 <= len(payload) <= 12:
                out.append(pending + payload); pending = None
            else:
                raise ValueError('invalid continuation')
        elif pending is not None or not (1 <= len(g) <= 12):
            raise ValueError('missing continuation or overwide group')
        else:
            out.append(g)
    if pending is not None:
        raise ValueError('unfinished continuation')
    return out


def expand(groups):
    words = []; s = None; count = 0
    for g in groups:
        g = tuple(g)
        if g == ('q',):
            if s is None:
                raise ValueError('empty member outside block')
            words.append(s); count += 1
        elif g == ('q', 'q'):
            if s is None or count < 2:
                raise ValueError('invalid block close')
            s = None
        elif g[:2] == ('q', 'q'):
            if s is not None:
                raise ValueError('nested block')
            s = unletters(g[2:]); count = 0
            if len(s) < 2 or not eligible(s):
                raise ValueError('invalid suffix')
        else:
            p = unletters(g)
            if s is not None:
                if not eligible(p):
                    raise ValueError('invalid member')
                words.append(p + s); count += 1
            else:
                words.append(p)
    if s is not None or not words:
        raise ValueError('unclosed or empty paragraph')
    return ' '.join(words)


def wrap(groups):
    lines = []; row = []; used = 0
    for g in groups:
        if not (1 <= len(g) <= 24):
            raise ValueError('physical width')
        if row and used + 1 + len(g) > 24:
            lines.append(' '.join(''.join(x) for x in row)); row = []; used = 0
        used += len(g) + bool(row); row.append(g)
    if row:
        lines.append(' '.join(''.join(x) for x in row))
    return '\n'.join(lines)


def encode(paragraphs, compress=True):
    if not paragraphs:
        raise ValueError('empty message')
    return '\n\n'.join(wrap(frame(logical_groups(p, compress))) for p in paragraphs)


def units(group):
    remaining = group; out = []
    ordered = sorted(SIGNS, key=len, reverse=True)
    while remaining:
        found = next((s for s in ordered if remaining.startswith(s)), None)
        if found is None:
            raise ValueError('outside working alphabet')
        out.append(found); remaining = remaining[len(found):]
    return tuple(out)


def decode(text, canonical=True):
    paragraphs = []
    for p in text.split('\n\n'):
        physical = []
        for line in p.split('\n'):
            gs = [units(g) for g in line.split(' ')]
            if any(not g for g in gs) or sum(map(len, gs)) + len(gs) - 1 > 24:
                raise ValueError('physical spacing or row width')
            physical.extend(gs)
        paragraphs.append(expand(unframe(physical)))
    if canonical and encode(paragraphs) != text:
        raise ValueError('noncanonical source or physical spelling')
    return paragraphs


def cost(text):
    lines = [line for line in text.split('\n') if line]
    groups = [g for line in lines for g in line.split(' ')]
    signs = sum(len(units(g)) for g in groups)
    return dict(signs=signs, physical_groups=len(groups), rows=len(lines),
                occupied_cells=signs + sum(line.count(' ') for line in lines),
                paragraph_breaks=text.count('\n\n'))


if __name__ == '__main__':
    old = json.loads((BASE / 'COMMON_SUFFIX_BLOCK_MANUAL_RESULT_20261007.json').read_text())
    cases = [[r['source']] for r in old['cases']]
    cases += [['station nation', 'staring daring', 'station'],
              [''.join(CHARACTERS)], ['a' * 13], ['a' * 24], ['a' * 25],
              ['abcdefghijklmnop abcdefghijklmnop']]
    rows = []
    for source in cases:
        written = encode(source); literal = encode(source, compress=False)
        assert decode(written) == source
        c, l = cost(written), cost(literal)
        rows.append(dict(source=source, written=written, literal=literal,
                         cost=c, literal_cost=l,
                         signs_saved=l['signs'] - c['signs'],
                         occupied_cells_saved=l['occupied_cells'] - c['occupied_cells']))
    result = dict(status='COMPLETE_PAID_TEACHING_CARRIER_ONLY', cases=rows,
                  contract_sha256=hashlib.sha256(CONTRACT.read_bytes()).hexdigest(),
                  code_table={k: list(v) for k, v in CODES.items()},
                  scope='Invented source teaching cases; no native key, meanings, statistical fit or human usability trial.')
    print(json.dumps(result, ensure_ascii=False, indent=2))
