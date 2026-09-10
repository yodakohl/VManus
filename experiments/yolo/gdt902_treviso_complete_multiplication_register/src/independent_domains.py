#!/usr/bin/env python3
"""Independent necessary counts and complete ordered operator-pair gate.

No primary compiler/checker imports. B's sealed numeric cells are the source.
Empty domains or no complete operator pair prove full-model impossibility;
survival does not establish numeral composition, injectivity, or complete order.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import time


def digest(b):
    return hashlib.sha256(b).hexdigest()


def compile_b(observer):
    records=[]
    for i,block in enumerate(observer['blocks']):
        assert block['block_order']==i+1 and block['multiplier_decimal']==str(i+2)
        seq=[]
        for j,row in enumerate(block['rows']):
            assert row['row_order_in_block']==j+1
            a,f,b,e,c=row['cells']
            assert f=='fia' and e=='fa' and int(a)*int(b)==int(c)
            assert a==str(i+2) and b==str(i+2+j if j<8-i else 0)
            seq += ['NUM:'+a,'OP:'+f,'NUM:'+b,'OP:'+e,'NUM:'+c]
        assert len(block['rows'])==9-i
        records.append({'id':block['id'],'row_count':len(block['rows']),'sequence':seq})
    assert len(records)==8 and sum(len(r['sequence']) for r in records)==220
    return records


def count_domains(records,paragraphs):
    atoms=sorted({a for r in records for a in r['sequence']})
    sc=[Counter(r['sequence']) for r in records]
    tc=[Counter(p['words']) for p in paragraphs]
    words=sorted({w for c in tc for w in c})
    sh={a:Counter(c[a] for c in sc) for a in atoms}
    th={w:Counter(c[w] for c in tc) for w in words}
    ds={a:[w for w in words if all(th[w][n]>=required for n,required in sh[a].items())]
        for a in atoms}
    return {'domains':ds,'source_histograms':sh,'domain_sizes':{a:len(v) for a,v in ds.items()},
            'empty_domains':[a for a in atoms if not ds[a]],
            'capacity_failure':len(paragraphs)<len(records),
            'source_record_count':len(records),'target_paragraph_count':len(paragraphs),
            'target_word_type_count':len(words),'head_filter_applied':False}


def operator_pairs(records,paragraphs,domains):
    ns=[r['row_count'] for r in records]
    assert len(set(ns))==len(ns)
    tc=[Counter(p['words']) for p in paragraphs]
    survivors=[]; coverage_hist=Counter(); tested=0
    for f in domains['OP:fia']:
        for e in domains['OP:fa']:
            if f==e:continue
            tested+=1
            by_n={n:[] for n in ns}
            for j,p in enumerate(paragraphs):
                n=tc[j][f]
                if n not in by_n or tc[j][e]!=n:continue
                projection=[w for w in p['words'] if w==f or w==e]
                if projection==[f,e]*n:
                    by_n[n].append(p['id'])
            covered=[n for n in ns if by_n[n]]
            coverage_hist[len(covered)]+=1
            if len(covered)==len(ns):
                # Exact n differs between blocks: paragraph choices are disjoint.
                assert len(set(j for ids in by_n.values() for j in ids))==sum(map(len,by_n.values()))
                survivors.append({'fia':f,'fa':e,'paragraph_domains':{
                    r['id']:by_n[r['row_count']] for r in records}})
    return {'ordered_distinct_pairs_tested':tested,'coverage_size_histogram':dict(coverage_hist),
            'surviving_pairs':survivors,'surviving_pair_count':len(survivors)}


def check_panel(records,paragraphs):
    assert len({p['id'] for p in paragraphs})==len(paragraphs)
    d=count_domains(records,paragraphs)
    if d['capacity_failure'] or d['empty_domains']:
        d.update(status='FULL_MODEL_UNSAT_NECESSARY_COUNTS',operator_gate_run=False)
    else:
        d.update(operator_pairs(records,paragraphs,d['domains']),operator_gate_run=True)
        d['status']=('FULL_MODEL_UNSAT_COMPLETE_OPERATOR_PAIRS' if not d['surviving_pair_count']
                     else 'NECESSARY_GATES_SURVIVE_FULL_MODEL_UNRESOLVED')
    return d


def self_test():
    records=[{'id':str(n),'row_count':n,'sequence':['N','OP:fia','N','OP:fa','N']*n}
             for n in [3,2]]
    ps=[{'id':r['id'],'words':['background']+
         [{'N':'x','OP:fia':'f','OP:fa':'e'}[a] for a in r['sequence']]+['background']}
        for r in records]
    d=count_domains(records,ps)
    assert all(w in d['domains'][a] for a,w in [('N','x'),('OP:fia','f'),('OP:fa','e')])
    pairs=operator_pairs(records,ps,d['domains'])
    assert [(x['fia'],x['fa']) for x in pairs['surviving_pairs']]==[('f','e')]
    bad=[dict(p,words=list(p['words'])) for p in ps]
    j,k=[i for i,w in enumerate(bad[0]['words']) if w in ['f','e']][:2]
    bad[0]['words'][j],bad[0]['words'][k]=bad[0]['words'][k],bad[0]['words'][j]
    assert count_domains(records,bad)['domains']==d['domains']
    assert not operator_pairs(records,bad,d['domains'])['surviving_pairs']
    zero_records=[{'sequence':['A']},{'sequence':['B']}]
    assert not count_domains(zero_records,[{'words':['x']},{'words':['x']}])['domains']['A']
    assert check_panel(records,ps[:1])['capacity_failure']
    # Count/alternation can survive a numerically invalid sequence; never claim SAT.
    assert check_panel(records,ps)['status']=='NECESSARY_GATES_SURVIVE_FULL_MODEL_UNRESOLVED'
    print('PASS synthetic feasible, no-head, ordered/reversed, zero-bin, capacity, and scope checks')


def main():
    started=time.monotonic()
    ap=argparse.ArgumentParser()
    for k in ['source','observer','target','output']:ap.add_argument('--'+k,type=Path)
    ap.add_argument('--panel',default=None)
    ap.add_argument('--source-only',action='store_true')
    ap.add_argument('--self-test',action='store_true')
    args=ap.parse_args()
    if args.self_test:self_test();return
    sb,bb=args.source.read_bytes(),args.observer.read_bytes()
    source,observer=json.loads(sb),json.loads(bb)
    assert digest(bb)==source['source_receipts']['B']
    records=compile_b(observer)
    assert records==source['records']
    assert sorted({a for r in records for a in r['sequence']})==source['atoms']
    assert len(source['atoms'])==38 and 'NUM:1' not in source['atoms']
    if args.source_only:
        print('PASS exact eight B-derived records,220fields,38atoms; no fabricated standalone1');return
    tb=args.target.read_bytes();target=json.loads(tb)
    names=[args.panel] if args.panel else list(target['panels'])
    out={'schema':'GDT902_INDEPENDENT_NECESSARY_DOMAINS_V1','source_sha256':digest(sb),
         'observer_sha256':digest(bb),'target_sha256':digest(tb),
         'code_sha256':digest(Path(__file__).read_bytes()),'source_compile':'EXACT_B_PARITY',
         'panels':{name:check_panel(records,target['panels'][name]) for name in names},
         'proof':['Global distinct realized numeral/operator words force exact per-block word counts, including zero.',
                  'Eight distinct target paragraphs require histogram capacity at every source count; there is no head constraint.',
                  'Projecting any complete valid block onto the two distinct operator words yields exactly(fia,fa)^n.',
                  'All ordered distinct pairs from the necessary operator domains are enumerated. Distinct n values make block paragraph domains disjoint.',
                  'No pair or an empty necessary domain excludes the complete model. Surviving pairs do not prove numeral code composition or complete foreground order.'],
         'numeral_composition_fitted':False,'full_model_fit_performed':False,
         'elapsed_seconds':time.monotonic()-started}
    args.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v['status'] for k,v in out['panels'].items()}))


if __name__=='__main__':main()
