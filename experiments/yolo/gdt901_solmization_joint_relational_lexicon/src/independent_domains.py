#!/usr/bin/env python3
"""Independent necessary histogram/head domains; never a positive full fit.

Under an injective one-word lexicon, a retained word's count in each selected
paragraph equals its atom count in that source record. Distinct paragraphs give
an injection from every source count bin into the corresponding target bin,
including count zero. An empty atom domain therefore excludes the full model.
Nonempty domains prove neither a simultaneous lexicon nor sequence order.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path

PITCHES = ['Gamma','A','B_square','C','D','E','F','G','a','b_flat','b_square',
           'c','d','e','f','g','aa','bb_flat','bb_square','cc','dd','ee']
TYPES = {'H':'hard', 'N':'natural', 'S':'soft'}
DIRECTIONS = {'ascendendo':'ascending','descendendo':'descending'}


def independent_compile(observer):
    rows = observer['records']
    if len(rows) != len(PITCHES):
        raise ValueError('Expected the complete 22-record B source')
    origin_ids = {f'P{i+1:02}': name for i,name in enumerate(PITCHES)}
    records = []
    for i,row in enumerate(rows):
        name = PITCHES[i]
        assert row['pitch_id'] == f'P{i+1:02}'
        def origin_atom(oid):
            resolved = origin_ids[oid]
            return 'SELF' if resolved == name else 'PITCH:' + resolved
        head = 'PITCH:' + name
        seq = [head]
        for m in row['voice_memberships_in_written_order']:
            seq.extend(['VOICE:'+m['voice'], 'CANTUS:'+TYPES[m['cantus_type']],
                        origin_atom(m['origin_pitch_id'])])
        mutations = row['directed_mutations']
        assert len(mutations) == row['mutation_count_explicit']
        for ordinal,e in enumerate(mutations,1):
            assert e['listed_ordinal'] == ordinal
            seq.extend(['VOICE:'+e['from_voice'], 'VOICE:'+e['to_voice'],
                        'DIRECTION:'+DIRECTIONS[e['direction']],
                        'CANTUS:'+TYPES[e['destination_cantus_type']],
                        origin_atom(e['destination_origin_pitch_id'])])
        if row['explicit_zero']:
            assert not mutations
            seq.append('ZERO')
        else:
            assert mutations
        records.append({'id':name, 'head_atom':head, 'sequence':seq})
    return records


def domains(records, paragraphs):
    if not records or not paragraphs:
        raise ValueError('Source and target lists must be nonempty')
    if len({r['id'] for r in records}) != len(records):
        raise ValueError('Duplicate source IDs')
    if len({p['id'] for p in paragraphs}) != len(paragraphs):
        raise ValueError('Duplicate target IDs')
    atoms = sorted({a for r in records for a in r['sequence']})
    for r in records:
        assert r['sequence'] and r['sequence'][0] == r['head_atom']
        assert all(isinstance(a,str) and a for a in r['sequence'])
    heads = {r['head_atom'] for r in records}
    scounts = [Counter(r['sequence']) for r in records]
    shist = {a: Counter(c[a] for c in scounts) for a in atoms}
    # Keep zero explicitly even when its required count is zero.
    for h in shist.values():
        h.setdefault(0,0)
    target_hist = defaultdict(Counter)
    first_words = set()
    for p in paragraphs:
        words = p['words']
        assert isinstance(words,list) and words
        assert all(isinstance(w,str) and w for w in words)
        first_words.add(words[0])
        for word,count in Counter(words).items():
            target_hist[word][count] += 1
    for h in target_hist.values():
        h[0] = len(paragraphs) - sum(h.values())
    result = {}
    rejection = {}
    for atom in atoms:
        accepted = []
        stats = Counter()
        for word in sorted(target_hist):
            missing = [n for n,required in shist[atom].items()
                       if target_hist[word][n] < required]
            if missing:
                stats['count_histogram_rejected'] += 1
                if 0 in missing:
                    stats['zero_bin_rejected'] += 1
                continue
            if atom in heads and word not in first_words:
                stats['first_word_rejected_after_histogram'] += 1
                continue
            accepted.append(word)
        result[atom] = accepted
        rejection[atom] = dict(stats)
    empty = [a for a in atoms if not result[a]]
    capacity = len(paragraphs) < len(records)
    return {'status': 'FULL_MODEL_UNSAT_NECESSARY_CONDITION' if empty or capacity
                     else 'NECESSARY_DOMAINS_NONEMPTY_FULL_MODEL_UNRESOLVED',
            'source_records':len(records), 'target_paragraphs':len(paragraphs),
            'atom_count':len(atoms), 'target_word_types':len(target_hist),
            'distinct_first_words':len(first_words), 'capacity_failure':capacity,
            'source_count_histograms':{a:dict(sorted(h.items())) for a,h in shist.items()},
            'head_atoms':sorted(heads), 'domains':result,
            'domain_sizes':{a:len(v) for a,v in result.items()},
            'empty_domains':empty, 'rejections':rejection,
            'criterion':'For each atom a and count m including0, target_hist(word,m) >= source_hist(a,m); head words additionally occur first in at least one raw paragraph.',
            'limitation':'Nonempty individual domains do not establish simultaneous assignments, all-different lexicon values, or full projected order.'}


def full_toy_witnesses(records, paragraphs):
    """Small finite enumeration used only in self-tests, never actual inference."""
    atoms = sorted({a for r in records for a in r['sequence']})
    vocabulary = sorted({w for p in paragraphs for w in p['words']})
    for values in itertools.permutations(vocabulary,len(atoms)):
        code = dict(zip(atoms,values))
        keep = set(values)
        for placement in itertools.permutations(range(len(paragraphs)),len(records)):
            if all(paragraphs[j]['words'][0] == code[r['head_atom']] and
                   [w for w in paragraphs[j]['words'] if w in keep] ==
                   [code[a] for a in r['sequence']]
                   for r,j in zip(records,placement)):
                yield code


def self_test():
    source = [{'id':'r0','head_atom':'A','sequence':['A','X']},
              {'id':'r1','head_atom':'B','sequence':['B','X','X']}]
    target = [{'id':'t0','words':['a','bg','x']},
              {'id':'t1','words':['b','x','bg','x']}, {'id':'t2','words':['bg']}]
    d = domains(source,target)
    assert d['rejections']['A']['first_word_rejected_after_histogram'] >= 1
    witnesses = list(full_toy_witnesses(source,target))
    assert witnesses and all(code[a] in d['domains'][a] for code in witnesses for a in code)
    zero_target = [{'id':'t0','words':['a','b','x']}, {'id':'t1','words':['b','a','x']}]
    zero = domains(source,zero_target)
    assert zero['empty_domains'] and zero['rejections']['A']['zero_bin_rejected'] == 3
    # Both X/Y histograms fit, but the two paragraphs force opposite orders.
    order_source = [{'id':'r0','head_atom':'A','sequence':['A','X','Y']},
                    {'id':'r1','head_atom':'B','sequence':['B','X','Y']}]
    order_target = [{'id':'t0','words':['a','x','y']}, {'id':'t1','words':['b','y','x']}]
    nd = domains(order_source,order_target)
    assert not nd['empty_domains'] and not list(full_toy_witnesses(order_source,order_target))
    assert nd['status'] == 'NECESSARY_DOMAINS_NONEMPTY_FULL_MODEL_UNRESOLVED'
    assert 'x' not in nd['domains']['A']
    assert domains(source,target[:1])['capacity_failure']
    print('PASS: feasible-map preservation, exact zero bin, head restriction, capacity, and nonempty-but-order-impossible example')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source',type=Path)
    p.add_argument('--observer',type=Path)
    p.add_argument('--target',type=Path)
    p.add_argument('--panel',default='IT2a')
    p.add_argument('--output',type=Path)
    p.add_argument('--self-test',action='store_true')
    a = p.parse_args()
    if a.self_test:
        self_test(); return
    if any(x is None for x in [a.source,a.observer,a.target,a.output]):
        p.error('source, observer, target, output required')
    sb,ob,tb = a.source.read_bytes(),a.observer.read_bytes(),a.target.read_bytes()
    source,observer,target = json.loads(sb),json.loads(ob),json.loads(tb)
    oh = hashlib.sha256(ob).hexdigest()
    assert oh in [r['sha256'] for r in source['source_receipts']]
    records = independent_compile(observer)
    assert records == source['records']
    assert sorted({x for r in records for x in r['sequence']}) == source['atoms']
    result = domains(records,target['panels'][a.panel])
    result.update(schema='GDT901_INDEPENDENT_COUNT_DOMAIN_V1',
                  source_sha256=hashlib.sha256(sb).hexdigest(),
                  target_sha256=hashlib.sha256(tb).hexdigest(),observer_sha256=oh,
                  panel=a.panel,independent_B_source_compilation='EXACT_MATCH',
                  full_sequence_fit_performed=False,
                  proof=['Global injective one-word lexicon makes the count of an encoded atom exactly equal to the count of its word in each selected raw paragraph.',
                         'An occurrence of a mapped word cannot be erased as background at another position; background membership is global by word type.',
                         'Distinct selected paragraphs inject each source count-bin into the corresponding target count-bin, including zero.',
                         'Each head atom must have a codeword appearing as a first raw word. If any atom has no word satisfying these necessary conditions, no complete model exists.'])
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(result['status'])


if __name__ == '__main__':
    main()
