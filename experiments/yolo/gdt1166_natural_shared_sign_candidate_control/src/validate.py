#!/usr/bin/env python3
"""Independent finite-channel checks; no runner/source-preparer imports."""
import argparse
import itertools
import collections
import gzip
import hashlib
import math
from functools import lru_cache
import json
from pathlib import Path


def residuals(carrier, word):
    """All distinct residual strings of ordered carrier embeddings (tiny oracle)."""
    if len(carrier) > len(word):
        return set()
    out = set()
    for kept in itertools.combinations(range(len(word)), len(carrier)):
        if ''.join(word[i] for i in kept) == carrier:
            indices = set(kept)
            out.add(''.join(c for i, c in enumerate(word) if i not in indices))
    return out


def compatible(carrier, word, marks, arm, constant=''):
    if arm == 'LITERAL' or marks == 0:
        return carrier == word
    d = len(word) - len(carrier)
    if len(carrier) < 2 or not 0 <= d <= 4:
        return False
    possible = residuals(carrier, word)
    if arm == 'VARIABLE':
        return bool(possible)
    if arm == 'CONSTANT':
        return constant * marks in possible
    raise ValueError(arm)


def fixture_checks():
    cases = [
        ('literal exact', compatible('ab', 'ab', 0, 'LITERAL')),
        ('literal no insertion', not compatible('ab', 'amb', 0, 'LITERAL')),
        ('variable middle', compatible('ab', 'amb', 1, 'VARIABLE')),
        ('variable ordered', not compatible('ab', 'ba', 1, 'VARIABLE')),
        ('variable zero', compatible('ab', 'ab', 1, 'VARIABLE')),
        ('variable four total', compatible('ab', 'axxxxb', 2, 'VARIABLE')),
        ('variable five rejected', not compatible('ab', 'axxxxxb', 2, 'VARIABLE')),
        ('minimum two carriers', not compatible('a', 'an', 1, 'VARIABLE')),
        ('no marker no insertion', not compatible('ab', 'amb', 0, 'VARIABLE')),
        ('constant repeated', compatible('ab', 'anbn', 2, 'CONSTANT', 'n')),
        ('constant once insufficient', not compatible('ab', 'anb', 2, 'CONSTANT', 'n')),
        ('constant sequence ordered', not compatible('ab', 'anmb', 1, 'CONSTANT', 'mn')),
        ('constant empty', compatible('ab', 'ab', 3, 'CONSTANT', '')),
        ('duplicate alignment dedup', residuals('aa', 'aaa') == {'a'}),
        ('distinct residuals retained', residuals('ab', 'abab') == {'ab', 'ba'}),
    ]
    toy = ReferenceIndex([{'word':w,'count':1} for n in range(1,7) for w in map(''.join,itertools.product('ab',repeat=n))])
    for n in range(1,4):
        for carrier in map(''.join,itertools.product('ab',repeat=n)):
            expected = tuple(i for i,w in enumerate(toy.words) if 0<=len(w)-len(carrier)<=4 and residuals(carrier,w))
            cases.append(('trie exhaustive '+carrier,toy.matches(carrier)==expected))
    return {name: bool(ok) for name, ok in cases}


class ReferenceIndex:
    """Independent trie traversal, with omission budget carried in search states."""
    def __init__(self, rows):
        self.rows = sorted(rows, key=lambda r:r['word'])
        self.words = [r['word'] for r in self.rows]
        self.counts = [r['count'] for r in self.rows]
        self.total = sum(self.counts)
        self.trie = [{}]
        self.ends = {}
        for i, word in enumerate(self.words):
            n = 0
            for c in word:
                if c not in self.trie[n]:
                    self.trie[n][c] = len(self.trie)
                    self.trie.append({})
                n = self.trie[n][c]
            self.ends[n] = i
        self.exact = {w:i for i,w in enumerate(self.words)}

    @lru_cache(maxsize=100000)
    def matches(self, carrier):
        stack = [(0,0,0)]
        seen = set()
        found = set()
        while stack:
            node, used, omitted = stack.pop()
            state = node,used,omitted
            if state in seen:
                continue
            seen.add(state)
            if used == len(carrier) and node in self.ends:
                found.add(self.ends[node])
            for c, nxt in self.trie[node].items():
                if used < len(carrier) and c == carrier[used]:
                    stack.append((nxt,used+1,omitted))
                if omitted < 4:
                    stack.append((nxt,used,omitted+1))
        return tuple(sorted(found))

    def weight(self, i, length):
        return self.counts[i] / self.total * 2.0 ** (length-len(self.words[i]))


def load(path):
    data = path.read_bytes()
    if path.suffix == '.gz':
        data = gzip.decompress(data)
    return json.loads(data)


def bindings(root, receipt):
    for rel, expected in receipt['bindings'].items():
        actual = hashlib.sha256((root/rel).read_bytes()).hexdigest()
        assert actual == expected, ('binding',rel)


def finite_audit(root):
    """Read fit outputs only after release; no held inputs or gold are opened."""
    release = load(root/'artifacts/FIT_RELEASE.json')
    assert release['status'] == 'FIT_RELEASED' and release['registered_commit']
    lock = load(root/'artifacts/KEY_SELECTION_LOCK.json')
    bindings(root,release)
    bindings(root,lock)
    train = load(root/'artifacts/TRAIN_INPUT.json')
    ref = ReferenceIndex(load(root/'artifacts/REFERENCE_INPUT.json')['words'])
    panel_data = load(root/'artifacts/KEY_PANEL.json.gz')
    scores_data = load(root/'artifacts/SEARCH_SCORES.json.gz')
    selected = load(root/'artifacts/KEY_SELECTION.json')
    rows = sorted((r for r in train['words'] if -1 not in r['atoms']),key=lambda r:(-r['count'],r['atoms']))[:512]
    active = sorted({a for r in rows for a in r['atoms']})
    alphabet = sorted(set(''.join(ref.words)))
    assert active == panel_data['fit_atoms'] == selected['fit_atoms']
    assert alphabet == panel_data['alphabet'] == selected['alphabet']
    assert len(panel_data['panel']) == 32
    assert [(p['start'],p['step']) for p in panel_data['panel']] == [(s,t) for s in range(8) for t in (5000,10000,15000,20000)]
    actual = {}
    for r in scores_data['scores']:
        identity = r['model'],r['panel'],r['marker'],tuple(r['residual_ids'])
        assert identity not in actual
        actual[identity] = r['score']
    reconstructed = {}
    histories=collections.Counter(); transitions=collections.Counter()
    start='<START>'; terminal='<TERMINAL>'
    for word,count in zip(ref.words,ref.counts):
        padded=[start,start,start]+list(word)+[terminal]
        for i in range(3,len(padded)):
            h=tuple(padded[i-3:i]); histories[h]+=count; transitions[h,padded[i]]+=count
    def surrogate(key,marker):
        weighted=[]
        for row in rows:
            word=[alphabet[key[a]] for a in row['atoms'] if a!=marker]
            padded=[start,start,start]+word+[terminal]; terms=[]
            for i in range(3,len(padded)):
                h=tuple(padded[i-3:i])
                terms.append(math.log((transitions[h,padded[i]]+.1)/(histories[h]+.1*(len(alphabet)+1))))
            weighted.append(row['count']*math.fsum(terms)/(len(word)+1))
        return math.fsum(weighted)/sum(r['count'] for r in rows)
    epsilon = 1e-8
    def objective(masses):
        return math.fsum(r['count']*math.log(epsilon+(1-epsilon)*m) for r,m in zip(rows,masses))
    for pi,p in enumerate(panel_data['panel']):
        key = p['key']
        assert len(key) == train['n_atoms'] and all(0 <= v < len(alphabet) for v in key)
        if p['start'] < 4:
            assert p['surrogate_marker'] == -1
        assert abs(surrogate(key,p['surrogate_marker'])-p['surrogate_score'])<1e-10
        lit_words = [''.join(alphabet[key[a]] for a in r['atoms']) for r in rows]
        literal = [ref.counts[ref.exact[w]]/ref.total if w in ref.exact else 0.0 for w in lit_words]
        for arm in ['L','C','V']:
            reconstructed[arm,pi,-1,()] = objective(literal)
        for marker in active:
            variable = list(literal)
            base = list(literal)
            constant = collections.defaultdict(dict)
            constant['']
            for wi,r in enumerate(rows):
                k = r['atoms'].count(marker)
                if not k:
                    continue
                carrier = ''.join(alphabet[key[a]] for a in r['atoms'] if a != marker)
                variable[wi] = base[wi] = 0.0
                if len(carrier) < 2:
                    continue
                candidates = ref.matches(carrier)
                variable[wi] = math.fsum(ref.weight(i,len(carrier)) for i in candidates)
                for i in candidates:
                    possible = residuals(carrier,ref.words[i])
                    units = set()
                    for rest in possible:
                        if len(rest)%k == 0:
                            unit = rest[:len(rest)//k]
                            if unit*k == rest:
                                units.add(unit)
                    for unit in units:
                        constant[unit][wi] = constant[unit].get(wi,0.0)+ref.weight(i,len(carrier))
            reconstructed['V',pi,marker,()] = objective(variable)
            for unit,values in constant.items():
                masses = list(base)
                for wi,mass in values.items():
                    masses[wi] = mass
                residual_ids = tuple(alphabet.index(c) for c in unit)
                reconstructed['C',pi,marker,residual_ids] = objective(masses)
        print(json.dumps({'validated_panel':pi+1,'of':32}),flush=True)
    assert actual.keys() == reconstructed.keys(), ('missing_or_extra_contracts',len(actual),len(reconstructed))
    max_error = max(abs(actual[k]-v) for k,v in reconstructed.items())
    assert max_error < 1e-7, ('objective_error',max_error)
    # Selection exactly follows recorded floating values; independent values
    # verify objectives but are not silently substituted at a 1e-12 tie boundary.
    for arm in ['L','C','V']:
        pool = [r for r in scores_data['scores'] if r['model']==arm]
        maximum = max(r['score'] for r in pool)
        tied = sorted((r for r in pool if r['score']>=maximum-1e-12),key=lambda r:(panel_data['panel'][r['panel']]['key'],r['marker'],r['residual_ids'],r['panel']))
        assert tied == scores_data['ties'][arm]
        for k,v in tied[0].items():
            assert selected['selected'][arm][k] == v
    return {'status':'PASS','scope':'all finite final-arm contracts, not optimizer trajectory replay',
            'objectives':len(actual),'max_absolute_objective_error':max_error,'panel_states':32,
            'limitations':['Floating objective replay tolerance 1e-7; deterministic ties checked against saved scores.',
                           'No source reconstruction, held prediction or gold scoring is claimed by this stage.']}


def score_audit(root):
    from fractions import Fraction
    import csv
    permission = load(root/'artifacts/SCORE_RELEASE.json')
    assert permission['status']=='SCORE_RELEASED'
    prediction_lock = load(root/'artifacts/PREDICTION_LOCK.json')
    assert hashlib.sha256((root/'artifacts/PREDICTION_LOCK.json').read_bytes()).hexdigest()==permission['prediction_lock_sha256']
    for name in ['PREREG_LOCK','FIT_RELEASE','KEY_SELECTION_LOCK','PREDICTION_LOCK']:
        bindings(root,load(root/f'artifacts/{name}.json'))
    assert hashlib.sha256((root/'artifacts/KEY_SELECTION_LOCK.json').read_bytes()).hexdigest()==prediction_lock['key_selection_lock_sha256']
    selection = load(root/'artifacts/KEY_SELECTION.json')
    output = load(root/'artifacts/PREDICTIONS.json.gz')
    reference = ReferenceIndex(load(root/'artifacts/REFERENCE_INPUT.json')['words'])
    train = load(root/'artifacts/TRAIN_INPUT.json')
    held = load(root/'artifacts/HOLDOUT_INPUT.json')
    truth = load(root/'artifacts/SOURCE_GOLD_LEDGER.json')
    result = load(root/'artifacts/RESULT.json')
    occurrences = load(root/'artifacts/OCCURRENCE_RESULTS.json.gz')
    assert output['held_records']==held['records']
    assert output['reference_words']==reference.words
    train_types={tuple(w) for r in train['records'] for w in r['words']}
    held_types={tuple(w) for r in held['records'] for w in r['words']}
    published={tuple(r['atoms']):r for r in output['types']}
    assert len(published)==len(output['types']) and set(published)==held_types
    alphabet=selection['alphabet']; active=set(selection['fit_atoms'])
    checked=0
    for atoms,p in published.items():
        assert p['novel_vs_all_training']==(atoms not in train_types)
        unsupported=bool(set(atoms)-active)
        assert p['contains_unsupported_fit_atom']==unsupported
        for arm,contract in selection['selected'].items():
            key=contract['key']; marker=contract['marker'] if arm!='L' else -1
            k=atoms.count(marker) if marker>=0 else 0
            carrier=''.join(alphabet[key[a]] for a in atoms if a!=marker) if not unsupported else ''
            ids=[]
            if not unsupported:
                if not k:
                    ids=[reference.exact[carrier]] if carrier in reference.exact else []
                elif len(carrier)>=2:
                    ids=list(reference.matches(carrier))
                    if arm=='C':
                        ids=[i for i in ids if contract['residual']*k in residuals(carrier,reference.words[i])]
            ids.sort(key=lambda i:(-reference.weight(i,len(carrier)),reference.words[i]))
            model=p['models'][arm]
            assert model['top5']==[reference.words[i] for i in ids[:5]],(atoms,arm,'top5')
            assert len(model['ranking'])==len(ids)
            for saved,i in zip(model['ranking'],ids):
                assert saved['word']==reference.words[i] and saved['reference_index']==i
                assert saved['omitted_characters']==len(reference.words[i])-len(carrier)
                assert saved['weight']==reference.weight(i,len(carrier))
            cut=reference.weight(ids[4],len(carrier)) if len(ids)>=5 else None
            assert model['cutoff_ties']==[reference.words[i] for i in ids if reference.weight(i,len(carrier))==cut]
            checked+=1
    tests=[r for r in truth['records'] if r['split']=='TEST']
    assert len(tests)==138 and len(train['records'])==130
    assert [{ 'record_id':r['record_id'],'words':[w['atoms'] for w in r['words']]} for r in tests]==held['records']
    groups=collections.defaultdict(list); unknown=[]; expected_occ=[]
    for r in tests:
        for w in r['words']:
            atoms=tuple(w['atoms']); ambiguous=w['input_unknown'] or w['expansion_unknown']
            assert w['input_unknown']==(-1 in atoms)
            bucket='OTHER_HELD'
            if w['abbreviated']:
                if ambiguous:
                    unknown.append(w); bucket='U_UNKNOWN_ZERO'
                elif atoms not in train_types:
                    groups[atoms].append(w); bucket='K_KNOWN_NOVEL_TYPE'
            row={k:w[k] for k in ['occurrence_id','atoms','reference','abbreviated','input_unknown','expansion_unknown']}
            row.update(record_id=r['record_id'],bucket=bucket,reference_OOV=w['reference'] not in reference.exact,models={})
            for arm in ['L','C','V']:
                top=published[atoms]['models'][arm]['top5']
                row['models'][arm]={'top5':top,'top1_hit':not ambiguous and w['reference'] in top[:1],'top5_hit':not ambiguous and w['reference'] in top}
            expected_occ.append(row)
    assert expected_occ==occurrences
    k,u=len(groups),len(unknown); denominator=k+u; scores={}
    for arm in ['L','C','V']:
        saved=result['metrics'][arm]; totals={}
        for topn in [1,5]:
            credit=sum((Fraction(sum(w['reference'] in published[a]['models'][arm]['top5'][:topn] for w in ws),len(ws)) for a,ws in groups.items()),Fraction())
            assert Fraction(saved[f'top{topn}_credit'])==credit
            value=float(credit/denominator) if denominator else None
            assert saved[f'primary_top{topn}']==value
            totals[topn]=credit
        assert saved['denominator']==denominator
        assert saved['known_type_top5_diagnostic']==(float(totals[5]/k) if k else None)
        scores[arm]=totals[5]/denominator if denominator else Fraction()
        primary=[r for r in expected_occ if r['bucket']!='OTHER_HELD']
        assert result['occurrence_weighted_diagnostic'][arm]=={'count':len(primary),'top1':sum(r['models'][arm]['top1_hit'] for r in primary)/len(primary) if primary else None,'top5':sum(r['models'][arm]['top5_hit'] for r in primary)/len(primary) if primary else None}
        assert result['empty_candidate_primary_types'][arm]==sum(not published[a]['models'][arm]['top5'] for a in groups)
    assert result['K_known_novel_abbreviated_types']==k and result['U_unknown_abbreviated_occurrences']==u
    assert result['primary_denominator']==denominator
    assert result['known_primary_reference_OOV_occurrences']==sum(w['reference'] not in reference.exact for ws in groups.values() for w in ws)
    assert result['unsupported_fit_primary_types']==sum(bool(set(a)-active) for a in groups)
    assert result['unsupported_fit_held_occurrences']==sum(bool(set(r['atoms'])-active) for r in expected_occ)
    assert result['selected_contracts']==selection['selected']
    assert result['held_records']==len(tests) and result['held_types']==len(published) and result['held_occurrences']==len(expected_occ)
    passed=k>=20 and scores['V']>=Fraction(1,2) and scores['V']-scores['L']>=Fraction(1,10) and scores['V']-scores['C']>=Fraction(1,10)
    assert result['status']==('PASS_SOURCE_CANDIDATE_CONTROL' if passed else 'FAIL_SOURCE_CANDIDATE_CONTROL' if k>=20 else 'NO_CAPACITY')
    assert result['capacity_met']==(k>=20)
    for arm in ['L','C']:
        assert result['V_minus_'+arm]==float(scores['V']-scores[arm])
    with (root/'artifacts/CANDIDATE_TABLE.tsv').open() as f:
        table=list(csv.DictReader(f,delimiter='\t'))
    expected_ids={('K',json.dumps(a)) for a in groups}|{('U',w['occurrence_id']) for w in unknown}
    assert len(table)==k+u and {(r['unit'],r['id']) for r in table}==expected_ids
    for row in table:
        if row['unit']=='K':
            a=tuple(json.loads(row['id'])); ws=groups[a]
            assert int(row['occurrences'])==len(ws)
            assert json.loads(row['gold_references'])==dict(collections.Counter(w['reference'] for w in ws))
            for arm in ['L','C','V']:
                assert json.loads(row[arm+'_top5'])==published[a]['models'][arm]['top5']
                assert Fraction(row[arm+'_top5_credit'])==Fraction(sum(w['reference'] in published[a]['models'][arm]['top5'] for w in ws),len(ws))
        else:
            assert all(Fraction(row[m+'_top5_credit'])==0 for m in ['L','C','V'])
    return {'status':'PASS','prediction_model_rows':checked,'held_occurrences':len(expected_occ),'K':k,'U':u,'registered_decision':result['status'],'limitations':['Source ledger treated as supplied transcription; independent source reconstruction is a separate stage.','No optimizer trajectory replay.']}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--fixtures', action='store_true')
    ap.add_argument('--finite', action='store_true')
    ap.add_argument('--score', action='store_true')
    args = ap.parse_args()
    if args.score:
        root=Path(__file__).resolve().parents[1]
        result=score_audit(root)
        (root/'artifacts/SCORE_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
        return 0
    if args.finite:
        root = Path(__file__).resolve().parents[1]
        result = finite_audit(root)
        (root/'artifacts/FINITE_VALIDATION.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
        return 0
    if not args.fixtures:
        ap.error('Choose --fixtures, --finite after key lock, or --score after score release.')
    checks = fixture_checks()
    print(json.dumps({'scope': 'synthetic fixtures only; not source validation', 'checks': checks,
                      'status': 'PASS' if all(checks.values()) else 'FAIL'}, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == '__main__':
    raise SystemExit(main())
