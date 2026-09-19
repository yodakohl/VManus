"""Fixed endpoint-carry consequences; no trained decoder or semantic scoring."""
import collections
import csv
import functools
import hashlib
import json
from pathlib import Path

E = Path(__file__).resolve().parents[1]
R = E.parents[2]

def dump(name, obj):
    (E / 'artifacts' / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')

def table(name, rows, fields):
    with (E / 'artifacts' / name).open('w') as out:
        w = csv.DictWriter(out, fields, delimiter='\t', lineterminator='\n')
        w.writeheader()
        w.writerows({k: row[k] for k in fields} for row in rows)

def order_range(events, direction):
    """Exact extrema over permutations of whole event types; no p-value."""
    types = ('rr', 'rl', 'lr', 'll')
    counts = tuple(sum(e['ends'] == t for e in events) for t in types)
    ii, oi = (0, 1) if direction == 'F' else (1, 0)
    @functools.lru_cache(None)
    def walk(counts, previous):
        if not any(counts):
            return 0, 0
        possibilities = []
        for i, n in enumerate(counts):
            if not n:
                continue
            rest = list(counts)
            rest[i] -= 1
            lo, hi = walk(tuple(rest), types[i][oi])
            score = int(previous is not None and previous == types[i][ii])
            possibilities.append((lo + score, hi + score))
        return min(x[0] for x in possibilities), max(x[1] for x in possibilities)
    return walk(counts, None)

def main():
    lock = json.loads((E / 'PREREG_LOCK.json').read_text())
    for name, digest in lock['files'].items():
        assert hashlib.sha256((R / name).read_bytes()).hexdigest() == digest, name
    spec = json.loads((E / 'src/SPEC.json').read_text())
    families = json.loads((R / spec['families']).read_text())
    panels = json.loads((R / spec['paragraphs']).read_text())
    allowed = set(json.loads((R / spec['scope']).read_text())['allowed_selectors'])
    pair_map = {(a+x, b+y): (a+'/'+b, x+y) for a,b in families for x in 'rl' for y in 'rl'}
    events, chains, ranges, paragraphs = [], [], [], {}
    for edition, ps in panels.items():
        for p in ps:
            assert p['page'] in allowed and not p['page'].startswith('f84') and p['page'] != 'f116v'
            channels = collections.defaultdict(list)
            for li, line in enumerate(p['lines']):
                if not line['anchor_eligible']:
                    continue
                for wi, pair in enumerate(zip(line['words'], line['words'][1:])):
                    if pair not in pair_map:
                        continue
                    family, ends = pair_map[pair]
                    event = dict(edition=edition, paragraph=p['id'], page=p['page'],
                        leaf=p['leaf'], family=family, ends=ends, locus=line['locus'],
                        line_index=li, word_index=wi, source_ids=line['source_ids'][wi:wi+2],
                        words=list(pair), id=edition+'|'+line['locus']+'|'+str(wi+1))
                    events.append(event)
                    channels[family].append(event)
            for family, es in channels.items():
                if len(es) < 2:
                    continue
                paragraphs[edition+'|'+p['id']] = p
                for prev, nxt in zip(es, es[1:]):
                    clear = all(l['anchor_eligible'] for l in p['lines'][prev['line_index']:nxt['line_index']+1])
                    chain = dict(id='C%04d' % (len(chains)+1), edition=edition,
                        paragraph=p['id'], leaf=p['leaf'], family=family,
                        previous=prev['id'], next=nxt['id'],
                        previous_words=' '.join(prev['words']), next_words=' '.join(nxt['words']),
                        previous_ends=prev['ends'], next_ends=nxt['ends'], clear=clear,
                        F_expected=prev['ends'][1], F_observed=nxt['ends'][0],
                        R_expected=prev['ends'][0], R_observed=nxt['ends'][1])
                    for direction in 'FR':
                        chain[direction+'_result'] = ('UNRESOLVED' if not clear else
                            'MATCH' if chain[direction+'_expected'] == chain[direction+'_observed']
                            else 'CONTRADICTION')
                    chains.append(chain)
                if all(l['anchor_eligible'] for l in p['lines']):
                    for direction in 'FR':
                        low, high = order_range(es, direction)
                        ranges.append(dict(edition=edition, paragraph=p['id'], leaf=p['leaf'],
                            family=family, direction=direction, events=len(es),
                            minimum=low, maximum=high, mobile=low != high))
    candidates = []
    for edition in panels:
        for a, b in families:
            family = a+'/'+b
            es = [e for e in events if e['edition']==edition and e['family']==family]
            cs = [c for c in chains if c['edition']==edition and c['family']==family]
            for direction in 'FR':
                rs = [r for r in ranges if r['edition']==edition and r['family']==family and r['direction']==direction and r['mobile']]
                counts = collections.Counter(c[direction+'_result'] for c in cs)
                bad = [c['id'] for c in cs if c[direction+'_result']=='CONTRADICTION']
                candidates.append(dict(edition=edition, family=family, direction=direction,
                    events=len(es), chains=len(cs), tested=sum(c['clear'] for c in cs),
                    matches=counts['MATCH'], contradictions=len(bad), unresolved=counts['UNRESOLVED'],
                    contradiction_ids=','.join(bad),
                    prediction_vector=''.join(c[direction+'_expected'] for c in cs if c['clear']),
                    mobile_leaves=','.join(map(str, sorted({r['leaf'] for r in rs}))),
                    status='CONTRADICTED' if bad else 'UNTESTED' if not any(c['clear'] for c in cs)
                    else 'NOT_CONTRADICTED_UNCONFIRMED', independent_confirmation=0))
    summary = dict(status='FIXED_STATE_CARRY_TEST_COMPLETE', confirmed_words=0,
        significance_claim=False, reserve_access=False,
        exposure='All source paragraphs previously project-exposed; editions are not independent.',
        candidates=len(families), interpretations=['F','R'], panels={})
    for ed, ps in panels.items():
        cs = [c for c in chains if c['edition']==ed]
        summary['panels'][ed] = dict(paragraphs=len(ps), events=sum(e['edition']==ed for e in events),
            chains=len(cs), tested=sum(c['clear'] for c in cs), unresolved=sum(not c['clear'] for c in cs),
            physical_leaves=sorted({c['leaf'] for c in cs if c['clear']}),
            outcomes={d:dict(collections.Counter(c[d+'_result'] for c in cs)) for d in 'FR'},
            mobile_leaves={d:sorted({r['leaf'] for r in ranges if r['edition']==ed and r['direction']==d and r['mobile']}) for d in 'FR'})
    for name, value in [('EVENTS',events),('CHAINS',chains),('ORDER_CAPACITY',ranges),
                        ('COMPLETE_CHAIN_PARAGRAPHS',paragraphs),('CANDIDATES',candidates),('RESULT',summary)]:
        dump(name+'.json',value)
    table('CANDIDATE_TABLE.tsv', candidates, list(candidates[0]))
    table('CONSEQUENCES.tsv', chains, ['id','edition','paragraph','leaf','family','previous','next',
        'previous_words','next_words','clear','F_expected','F_observed','F_result','R_expected','R_observed','R_result'])
    print(json.dumps(summary))

if __name__ == '__main__':
    main()
