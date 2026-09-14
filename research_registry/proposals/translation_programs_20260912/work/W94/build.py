"""Frozen P14 mass/ratio consequences on all exposed W89 paragraphs."""
import csv
import hashlib
import json
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path

D = Path(__file__).resolve().parent.relative_to(Path.cwd())
B = D.parent

def dump(name, obj):
    (D / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def table(name, rows):
    with (D / name).open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter='\t', lineterminator='\n')
        w.writeheader(); w.writerows(rows)

def rref(rows):
    a = [[Fraction(x) for x in row] for row in rows if any(row)]
    pos = 0
    for c in range(3):
        k = next((k for k in range(pos, len(a)) if a[k][c]), None)
        if k is None: continue
        a[pos], a[k] = a[k], a[pos]
        scale = a[pos][c]; a[pos] = [x / scale for x in a[pos]]
        for j in range(len(a)):
            if j != pos:
                scale = a[j][c]; a[j] = [x - scale*y for x, y in zip(a[j], a[pos])]
        pos += 1
    return [[str(x) for x in row] for row in a[:pos]]

def graph_constraints(edges):
    tree = defaultdict(list); chords = []
    for e in edges:
        src, dst = e['denominator'], e['numerator']
        queue = deque([(src, [0, 0, 0], [])]); visited = {src}; found = None
        while queue:
            node, value, path = queue.popleft()
            if node == dst:
                found = (value, path); break
            for target, vec, at, sign in tree[node]:
                if target not in visited:
                    visited.add(target)
                    queue.append((target, [a+b for a, b in zip(value, vec)], path+[[at, sign]]))
        unit = [int(x == e['value']) for x in 'ABC']
        if found is None:
            tree[src].append((dst, unit, e['at'], 1))
            tree[dst].append((src, [-x for x in unit], e['at'], -1))
        else:
            vec, path = found
            coeff = [a-b for a, b in zip(vec, unit)]
            chords.append({'closing_at': e['at'], 'coefficients': coeff,
                           'support': path+[[e['at'], -1]], 'nontrivial': any(coeff)})
    return chords

for name, digest in json.loads((D/'FROZEN_INPUTS.json').read_text()).items():
    assert hashlib.sha256(Path(name).read_bytes()).hexdigest() == digest, name
ps = json.loads((B/'W89/PARAGRAPHS.json').read_text())
model = json.loads((B/'P14/MODEL.json').read_text())
materials = set(model['materials']); values = model['values']
assert len(ps) == 140 and all(not p['page'].startswith('f84') for p in ps)
fields = []; alignment = []; coverage = []; systems = []
for p in ps:
    tokens = [dict(word=w, at=at, line=l['locus']) for l in p['lines']
              for w, at in zip(l['words'], l['source_ids'])]
    assert len(tokens) == p['groups']
    coverage.append(dict(edition=p['edition'], paragraph=p['id'], page=p['page'], leaf=p['leaf'],
                         lines=len(p['lines']), groups=len(tokens), values=sum(t['word'] in values for t in tokens)))
    for scope in ['RECORD', 'LINE']:
        current = previous = None; lastline = None; local = []
        for t in tokens:
            if scope == 'LINE' and t['line'] != lastline: current = previous = None
            lastline = t['line']; w = t['word']
            if w in materials:
                if current and current['word'] != w: previous = current
                current = t
            if w in values:
                f = dict(edition=p['edition'], paragraph=p['id'], page=p['page'], scope=scope,
                         at=t['at'], word=w, value=values[w],
                         numerator=current['word'] if current else '',
                         numerator_at=current['at'] if current else '',
                         denominator=previous['word'] if previous else '',
                         denominator_at=previous['at'] if previous else '',
                         M_status='BOUND' if current else 'MISSING_MATERIAL',
                         R_status='BOUND' if current and previous else 'MISSING_DENOMINATOR' if current else 'MISSING_BOTH')
                fields.append(f); local.append(f)
        for reading in ['R', 'M']:
            for identity in ['TYPE', 'MENTION']:
                edges = []
                for f in local:
                    if f[reading+'_status'] != 'BOUND': continue
                    suffix = '' if identity == 'TYPE' else '_at'
                    edges.append(dict(at=f['at'], value=f['value'], numerator=f['numerator'+suffix],
                                      denominator=f['denominator'+suffix] if reading == 'R' else 'UNIT'))
                chords = graph_constraints(edges)
                systems.append(dict(edition=p['edition'], paragraph=p['id'], page=p['page'], leaf=p['leaf'],
                                    scope=scope, reading=reading, identity=identity, edges=edges,
                                    chords=chords, basis=rref([x['coefficients'] for x in chords])))
    fby = {f['at']: f for f in fields if f['paragraph'] == p['id'] and f['edition'] == p['edition'] and f['scope'] == 'RECORD'}
    for t in tokens:
        w = t['word']; f = fby.get(t['at'])
        r = m = 'M('+w+') [Materialhypothese]' if w in materials else '⟦'+w+'⟧'
        if f:
            r = 'm('+ (f['numerator'] or '?') +')/m('+(f['denominator'] or '?')+')='+f['value']
            m = 'm('+(f['numerator'] or '?')+')='+f['value']+'·Uₚ'
        alignment.append(dict(edition=p['edition'], paragraph=p['id'], at=t['at'], word=w,
                              role='VALUE_ASSUMED' if f else 'MATERIAL_ASSUMED' if w in materials else 'UNREAD', R=r, M=m))

summary = []
for edition in sorted({p['edition'] for p in ps}):
    for scope in ['RECORD', 'LINE']:
        for reading in ['R', 'M']:
            for identity in ['TYPE', 'MENTION']:
                ss = [s for s in systems if (s['edition'], s['scope'], s['reading'], s['identity']) == (edition, scope, reading, identity)]
                coeff = [c['coefficients'] for s in ss for c in s['chords']]
                basis = rref(coeff)
                forced_one = [v for i, v in enumerate('ABC') if rref(coeff+[[int(i == k) for k in range(3)]]) == basis]
                forced_equal = [a+'='+b for i, a in enumerate('ABC') for j, b in enumerate('ABC') if i < j
                                and rref(coeff+[[int(i == k)-int(j == k) for k in range(3)]]) == basis]
                summary.append(dict(edition=edition, scope=scope, reading=reading, identity=identity,
                                    edges=sum(len(s['edges']) for s in ss), chords=len(coeff),
                                    nontrivial_chords=sum(any(c) for c in coeff), rank=len(basis), basis=basis,
                                    forced_one=forced_one, forced_equal=forced_equal,
                                    contributing_paragraphs=sum(bool(s['basis']) for s in ss),
                                    contributing_leaves=sorted({s['leaf'] for s in ss if s['basis']})))
table('FIELDS.tsv', fields); table('ALIGNMENT.tsv', alignment); table('COVERAGE.tsv', coverage)
dump('SYSTEMS.json', systems); dump('CONSEQUENCES.json', summary)
vr = []
for edition in sorted({p['edition'] for p in ps}):
    cs = {(s['scope'], s['reading'], s['identity']): s for s in summary if s['edition'] == edition}
    counts = Counter(a['word'] for a in alignment if a['edition'] == edition)
    for word, value in values.items():
        vr.append(dict(edition=edition, word=word, symbol=value, all_occurrences=counts[word],
                       R_record_type_forced_one=value in cs['RECORD', 'R', 'TYPE']['forced_one'],
                       R_record_type_equalities=';'.join(cs['RECORD', 'R', 'TYPE']['forced_equal']),
                       M_record_type_forced_one=value in cs['RECORD', 'M', 'TYPE']['forced_one'],
                       M_record_type_equalities=';'.join(cs['RECORD', 'M', 'TYPE']['forced_equal']),
                       R_record_mention_forced_one=value in cs['RECORD', 'R', 'MENTION']['forced_one'],
                       R_record_mention_equalities=';'.join(cs['RECORD', 'R', 'MENTION']['forced_equal']),
                       R_line_rank=cs['LINE', 'R', 'TYPE']['rank'],
                       confirmed_translation=False, independent_confirmation_capacity=0))
table('VALUE_TABLE.tsv', vr)
wr = []
for s in systems:
    if s['scope'] != 'RECORD' or s['reading'] != 'R' or s['identity'] != 'TYPE': continue
    emap = {e['at']: e for e in s['edges']}
    for c in s['chords']:
        equations = [str(sign)+'*['+at+': m('+emap[at]['numerator']+')/m('+emap[at]['denominator']+')='+emap[at]['value']+']' for at, sign in c['support']]
        wr.append(dict(edition=s['edition'], paragraph=s['paragraph'], closing_at=c['closing_at'],
                       logA=c['coefficients'][0], logB=c['coefficients'][1], logC=c['coefficients'][2],
                       status='NONTRIVIAL' if c['nontrivial'] else 'DUPLICATE_NO_RESTRICTION',
                       signed_equations='; '.join(equations)))
table('ALL_PRIMARY_CYCLES.tsv', wr)
md = ['# W94 — vollständige Absätze, feste Mengenrivalen', '',
      'M(w) ist nur P14s Materialhypothese; A/B/C sind freie positive Werte. ⟦w⟧ bleibt ungelesen. Jede Rohgruppe bleibt erhalten. R/M gelten getrennt, nicht gleichzeitig.', '']
by = {(a['edition'], a['paragraph'], a['at']): a for a in alignment}
for p in ps:
    md += ['## '+p['edition']+' '+p['id'], '']
    for l in p['lines']:
        aa = [by[p['edition'], p['id'], at] for at in l['source_ids']]
        md += [l['locus']+' `'+ ' '.join(l['words'])+'`', '',
               'R: '+' · '.join(a['R'] for a in aa), '', 'M: '+' · '.join(a['M'] for a in aa), '']
(D/'READINGS.md').write_text('\n'.join(md)+'\n')
primary = [s for s in summary if s['scope'] == 'RECORD' and s['reading'] == 'R' and s['identity'] == 'TYPE']
dump('RESULT.json', dict(paragraph_transcriptions=len(ps), groups=len(alignment),
                         editions=dict(Counter(p['edition'] for p in ps)),
                         physical_leaves=len({p['leaf'] for p in ps}),
                         value_counts={e:dict(Counter(f['word'] for f in fields if f['edition'] == e and f['scope'] == 'RECORD')) for e in sorted({p['edition'] for p in ps})},
                         decision='STOP_DISTINCT_VALUE_EXTENSION' if all(s['forced_equal'] for s in primary) else 'ASSESS_CONDITIONAL_CONSTRAINTS',
                         primary=primary, confirmed_meanings=0, independent_confirmation_capacity=0,
                         reserved_access=False, old_experiments_changed=False,
                         claim_ceiling='Conditional algebra under assumed fixed masses and positional ratios; not word meaning or a selected interpretation'))
print((D/'RESULT.json').read_text())
print(json.dumps(summary, ensure_ascii=False))
