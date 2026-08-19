#!/usr/bin/env python3
"""Independent, nonimporting validation of the GDT347 public graph freeze."""

from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

def root(p):
    for q in (p,*p.parents):
        if (q/'AGENTS.md').is_file() and (q/'.git').exists():return q
    raise RuntimeError
ROOT=root(Path(__file__).resolve());EXP=ROOT/'experiments/yolo/gdt347_fixed_graph_control_transport';ART=EXP/'artifacts'
DESIGN=ART/'gdt347_design.json';FROZEN=ART/'gdt347_frozen_graph.json';CAP=ART/'gdt347_control_capacity.tsv';OUT=ART/'gdt347_freeze_validation.json'
G345=ROOT/'experiments/yolo/gdt345_productive_operator_transfer/artifacts/gdt345_transition_inventory.tsv';G346=ROOT/'experiments/yolo/gdt346_compositional_operator_manifold/artifacts/gdt346_graph_edges.tsv';MAN=ROOT/'gdt278_control_manifest.tsv';NATIVE=ROOT/'gdt278_native_event_inventory.tsv';MATCHED=ROOT/'gdt278_matched_event_inventory.tsv'

def read(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def canon(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def content(x):y=dict(x);y.pop('content_sha256',None);return hashlib.sha256(canon(y)).hexdigest()

def main():
    checks=[]
    def ck(n,v,d=''):
        checks.append({'check':n,'pass':bool(v),'detail':str(d)})
        if not v:raise AssertionError(f'{n}: {d}')
    design=json.loads(DESIGN.read_text());frozen=json.loads(FROZEN.read_text());src=read(G345);graph=read(G346)
    ck('source_census',len(src)==8268 and len({r['physical_folio'] for r in src})==91,len(src));ck('source_no_f84',not any(r['page'].startswith('f84') for r in src))
    primary=[r for r in graph if r['fold_tag'].startswith('PHYSICAL_FOLIO:')];folds=len({r['fold_tag'] for r in primary});counts=Counter(r['pair_id'] for r in primary if r['selected']=='1')
    topology=[r['pair_id'] for r in frozen['topology']];ck('topology_exact',topology==['1-5','3-5','2-3'],topology);ck('topology_frequency',[counts[p] for p in topology]==[91,91,82]);ck('folds',folds==91)
    fr={r['physical_folio']:r['register'] for r in src};held=[]
    for reg in sorted(set(fr.values())):
        fs=sorted([f for f,v in fr.items() if v==reg],key=lambda f:hashlib.sha256((design['voynich_split']['salt']+'\0'+reg+'\0'+f).encode()).hexdigest());held+=fs[:max(1,round(.2*len(fs)))]
    held=sorted(held);train=[r for r in src if r['physical_folio'] not in held]
    ck('held_exact',held==frozen['voynich_partition']['held_folios']);ck('partition_counts',len(train)==7037 and len(src)-len(train)==1231)
    edges=[]
    for r in train:edges.append({'source':tuple(json.loads(r['source_state_json'])),'target':tuple(json.loads(r['target_state_json'])),'delta':tuple(json.loads(r['delta_json'])),'layout':tuple(json.loads(r['layout_context_json'])),'scope':r['boundary_scope']})
    globals_=[Counter() for _ in range(6)];layouts=[defaultdict(Counter) for _ in range(6)];contexts=[defaultdict(Counter) for _ in range(6)]
    for e in edges:
        for i,y in enumerate(e['target']):globals_[i][y]+=1;layouts[i][e['layout']][y]+=1;contexts[i][(*e['layout'],f'C{i}',e['source'][i])][y]+=1
    def tprob(e,i):
        g=globals_[i];labels=sorted(g);pg={y:(g[y]+.5)/(sum(g.values())+.5*len(labels)) for y in labels};lc=layouts[i][e['layout']];pl={y:(lc[y]+64*pg[y])/(sum(lc.values())+64) for y in labels};cc=contexts[i][(*e['layout'],f'C{i}',e['source'][i])];return {y:(cc[y]+32*pl[y])/(sum(cc.values())+32) for y in labels}
    def dprob(e,i):
        o={}
        for y,p in tprob(e,i).items():
            d='KEEP' if y==e['source'][i] else 'SET:'+y;o[d]=o.get(d,0)+p
        return o
    expected={};observed={};scope_n=Counter(e['scope'] for e in edges)
    for pair in [(1,5),(3,5),(2,3)]:
        ex=defaultdict(float);ob=Counter()
        for e in edges:
            ob[(e['scope'],e['delta'][pair[0]],e['delta'][pair[1]])]+=1;pa,pb=dprob(e,pair[0]),dprob(e,pair[1])
            for a,va in pa.items():
                for b,vb in pb.items():ex[(e['scope'],a,b)]+=va*vb
        expected[pair]=ex;observed[pair]=ob
    recomputed={}
    for pair,ex in expected.items():
        for key,v in ex.items():
            q=v/max(1,scope_n[key[0]]);prior=16*q;recomputed[(f'{pair[0]}-{pair[1]}',*key)]=(observed[pair][key]+prior)/(v+prior)
    frozen_weights={(r['pair_id'],r['scope'],r['delta_a'],r['delta_b']):float(r['factor']) for r in frozen['potential_weights']}
    ck('weight_keys',set(recomputed)==set(frozen_weights),len(recomputed));ck('weight_values',all(math.isclose(v,frozen_weights[k],rel_tol=2e-15,abs_tol=2e-15) for k,v in recomputed.items()))
    ck('selector_once',math.isclose(frozen['selector_bits_once'],math.log2(math.comb(15,3)),abs_tol=1e-15));ck('f84_flags',all(v is False for v in frozen['f84'].values()));ck('content_hash',content(frozen)==frozen['content_sha256'])
    for p,d in frozen['inputs'].items():ck('hash:'+p,sha(ROOT/p)==d)
    caps=read(CAP);ck('capacity_rows',len(caps)==25,len(caps));ck('capacity_no_voynich',not any(r['control_id'].startswith('VOYNICH') for r in caps));ck('capacity_dy_zero',all(int(r['dy_positive'])==0 for r in caps))
    validation={'schema':'GDT347_FREEZE_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_failed':0,'frozen_graph_sha256':sha(FROZEN),'scope':'Independent GDT345/GDT346 topology, partition, marginal/potential, selector, capacity, hash, semantic-zero and f84-freeze reconstruction.','checks':checks};validation['content_sha256']=content(validation);OUT.write_bytes(canon(validation));print(f'PASS {len(checks)}/{len(checks)}')
    return 0
if __name__=='__main__':raise SystemExit(main())
