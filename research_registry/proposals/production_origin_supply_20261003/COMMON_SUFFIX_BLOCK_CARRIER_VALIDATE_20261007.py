"""Independent example/table/framing reader; does not import the carrier."""
import hashlib
import json
import re
from pathlib import Path

B = Path(__file__).parent
S = json.loads((B / 'COMMON_SUFFIX_BLOCK_CARRIER_CONTRACT_20261007.json').read_text())
R = json.loads((B / 'COMMON_SUFFIX_BLOCK_CARRIER_RESULT_20261007.json').read_text())
A = S['working_signs']
symbols = re.compile('|'.join(sorted(A, key=len, reverse=True)))
raw = json.loads((B / 'COMMON_SUFFIX_BLOCK_WRITER_RAW_20261007.json').read_text())
domain = list(raw['design']['source_contract']['lowercase_letters']) + raw['design']['source_contract']['additional_characters']
assert domain == S['source_characters'] and len(set(domain)) == 82
codes = {}
for i, char in enumerate(domain):
    if i < 21:
        codes[char] = [[s for s in A if s != 'q'][i]]
    else:
        codes[char] = ['q', A[(i - 21) // 22], A[(i - 21) % 22]]
assert codes == R['code_table']
reverse = {tuple(value): key for key, value in codes.items()}
assert len(reverse) == 82
assert all(tuple(v[:2]) != ('q', 'q') for v in codes.values())


def literal(u):
    chars = []
    while u:
        width = 3 if u[0] == 'q' else 1
        key = tuple(u[:width])
        if key not in reverse:
            raise ValueError('bad code')
        chars.append(reverse[key]); u = u[width:]
    return ''.join(chars)


def physical(text):
    paragraphs = []; allrows = []
    for para in text.split('\n\n'):
        rows = []
        for line in para.split('\n'):
            row = []
            for word in line.split(' '):
                parsed = symbols.findall(word)
                if not parsed or ''.join(parsed) != word:
                    raise ValueError('bad sign')
                row.append(parsed)
            if sum(len(x) for x in row) + len(row) - 1 > 24:
                raise ValueError('row overflow')
            rows.append(row)
        for previous, following in zip(rows, rows[1:]):
            used = sum(len(x) for x in previous) + len(previous) - 1
            if used + 1 + len(following[0]) <= 24:
                raise ValueError('non-greedy wrap')
        paragraphs.append([x for row in rows for x in row]); allrows.extend(rows)
    costs = dict(signs=sum(len(g) for row in allrows for g in row),
                 physical_groups=sum(len(row) for row in allrows), rows=len(allrows),
                 occupied_cells=sum(sum(map(len, row)) + len(row) - 1 for row in allrows),
                 paragraph_breaks=len(paragraphs) - 1)
    return paragraphs, costs


def read(text):
    paras, costs = physical(text)
    source = []; teaching = []
    for p in paras:
        logical = []; pending = []; inside_frame = False
        for g in p:
            if g[:4] == ['q'] * 4:
                if len(g) < 6 or g[4] not in ('a', 'o'):
                    raise ValueError('bad frame')
                fragment = g[5:]
                if g[4] == 'a':
                    if len(fragment) != 12:
                        raise ValueError('short intermediate fragment')
                    inside_frame = True; pending.extend(fragment)
                else:
                    if not inside_frame or len(fragment) > 12:
                        raise ValueError('last fragment without start')
                    pending.extend(fragment); logical.append(pending)
                    pending = []; inside_frame = False
            else:
                if inside_frame or len(g) > 12:
                    raise ValueError('unframed or interrupted long group')
                logical.append(g)
        if inside_frame:
            raise ValueError('unclosed frame')
        tail = None; n = 0; words = []; abstract = []
        for g in logical:
            if g == ['q']:
                if tail is None:
                    raise ValueError('empty outside block')
                abstract.append('@0'); words.append(tail); n += 1
            elif g == ['q', 'q']:
                if tail is None or n < 2:
                    raise ValueError('bad close')
                abstract.append('@}'); tail = None
            elif g[:2] == ['q', 'q']:
                if tail is not None:
                    raise ValueError('nested block')
                tail = literal(g[2:]); n = 0
                if re.fullmatch('[a-z]{2,}', tail) is None:
                    raise ValueError('bad suffix')
                abstract.append('@{' + tail + '}')
            else:
                word = literal(g)
                abstract.append(word)
                if tail is not None:
                    if re.fullmatch('[a-z]+', word) is None:
                        raise ValueError('bad member')
                    word += tail; n += 1
                words.append(word)
        if tail is not None:
            raise ValueError('unclosed block')
        source.append(' '.join(words)); teaching.append(' '.join(abstract))
    return source, teaching, costs


old = json.loads((B / 'COMMON_SUFFIX_BLOCK_MANUAL_RESULT_20261007.json').read_text())
expected = [[c['written']] for c in old['cases']]
expected += [['@{ation} st n @}', '@{aring} st d @}', 'station'],
             [''.join(domain)], ['a' * 13], ['a' * 24], ['a' * 25],
             ['@{abcdefghijklmnop} @0 @0 @}']]
assert len(expected) == len(R['cases'])
for row, teaching in zip(R['cases'], expected):
    src, expanded, cost = read(row['written'])
    assert src == row['source'] and expanded == teaching and cost == row['cost']
    src, expanded, cost = read(row['literal'])
    assert src == row['source'] and expanded == src and cost == row['literal_cost']
    assert row['signs_saved'] == cost['signs'] - row['cost']['signs']
    assert row['occupied_cells_saved'] == cost['occupied_cells'] - row['cost']['occupied_cells']

rejected = []
for name, text in [('empty_outside', 'q'), ('close_outside', 'qq'),
                   ('short_suffix', 'qqa q q qq'), ('bad_escape', 'qcfhcfh'),
                   ('last_without_first', 'qqqqoa'), ('unfinished_fragment', 'qqqqaaaaaaaaaaaaa'),
                   ('outside_alphabet', 'z')]:
    try:
        read(text)
    except ValueError:
        rejected.append(name)
    else:
        raise AssertionError(name)
assert R['contract_sha256'] == hashlib.sha256((B / 'COMMON_SUFFIX_BLOCK_CARRIER_CONTRACT_20261007.json').read_bytes()).hexdigest()
print(json.dumps(dict(status='PASS', scope='Same-author independently written table/reader/cost reconstruction of exposed teaching cases, not historical/native validation',
                      code_entries=82, working_signs=22, source_cases=len(expected),
                      rejected_malformed=rejected,
                      program_sha256=hashlib.sha256((B / 'COMMON_SUFFIX_BLOCK_CARRIER_20261007.py').read_bytes()).hexdigest(),
                      validator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()), indent=2))
