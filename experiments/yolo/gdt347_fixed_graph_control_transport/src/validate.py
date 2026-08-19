#!/usr/bin/env python3
"""Independent source and accounting validator for GDT347; no scorer import."""
from __future__ import annotations
import csv,hashlib,json,math
from collections import Counter,defaultdict
from pathlib import Path

def root(p):
    for q in (p,*p.parents):
        if (q/'AGENTS.md').is_file() and (q/'.git').exists():return q
    raise RuntimeError
ROOT=root(Path(__file__).resolve());EXP=ROOT/'experiments/yolo/gdt347_fixed_graph_control_transport';ART=EXP/'artifacts'
FROZEN=ART/'gdt347_frozen_graph.json';G345=ROOT/'experiments/yolo/gdt345_productive_operator_transfer/artifacts/gdt345_transition_inventory.tsv';NATIVE=ROOT/'gdt278_native_event_inventory.tsv';MATCHED=ROOT/'gdt278_matched_event_inventory.tsv'
PANELS=ART/'gdt347_panel_scores.tsv';FOLDS=ART/'gdt347_folio_scores.tsv';ENV=ART/'gdt347_environment_scores.tsv';EDGE=ART/'gdt347_edge_scores.tsv';NULL=ART/'gdt347_null.tsv';COUNTER=ART/'gdt347_counterexamples.tsv';RESULT=ART/'gdt347_result.json';VALID=ART/'gdt347_validation.json'

def read(p):
    with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1<<20),b''):h.update(b)
    return h.hexdigest()
def canon(x):return (json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode()
def content(x):y=dict(x);y.pop('content_sha256',None);return hashlib.sha256(canon(y)).hexdigest()
def wrapper(r,prev):
    w=r['wrapper']
    if w=='s' and int(r['group_index'])==1:w='NONE'
    if w=='q' and prev is not None and prev['locus']==r['locus'] and prev['dy_closure']=='1':w='NONE'
    return w

def main():
    checks=[]
    def ck(name,ok,detail=''):
        checks.append({'check':name,'pass':bool(ok),'detail':str(detail)})
        if not ok:raise AssertionError(f'{name}: {detail}')
    result=json.loads(RESULT.read_text());frozen=json.loads(FROZEN.read_text());panels=read(PANELS);folds=read(FOLDS);edges=read(EDGE);null=read(NULL);env=read(ENV);counter=read(COUNTER)
    ck('status_vocab',result['status'] in {'GENERIC_WRITING_MECHANICS','COMPILER_STYLE_FORMAL_GRAMMAR','MANUSCRIPT_SPECIFIC_FORMAL_CONVENTION','GDT346_LOCAL_OVERFITTING','INCONCLUSIVE_CONTROL_TRANSPORT'})
    ck('topology_exact',[r['pair_id'] for r in result['frozen_topology']]==['1-5','3-5','2-3']);ck('selector_once',math.isclose(result['selector_bits_once'],math.log2(math.comb(15,3)),abs_tol=1e-15))
    src=read(G345);native=read(NATIVE);matched=read(MATCHED);ck('g345_census',len(src)==8268);ck('all_inputs_f84_free',not any(r['page'].startswith('f84') or r.get('locus','').startswith('f84') for r in src+native+matched))
    voy=[r for r in native if r['control_id']=='VOYNICH_REFERENCE'];by=defaultdict(list)
    for r in voy:by[r['page']].append(r)
    states={}
    for page,rs in by.items():
        prev=None
        for r in rs:states[(page,r['locus'],r['group_index'])]=(r['local_frame'],r['inner_d'],r['right_family'],r['dy_closure'],r['b3'],wrapper(r,prev));prev=r
    mismatch=0
    for r in src:
        for side in ('source','target'):
            key=(r['page'],r[f'{side}_locus'],r[f'{side}_group_index']);mismatch+=int(states[key]!=tuple(json.loads(r[f'{side}_state_json'])))
    ck('voynich_state_reconstruction',mismatch==0,mismatch);ck('voynich_group_census',len(voy)==8448)
    ck('panel_rows',len(panels)==26,len(panels));ck('native_panels',sum(r['view']=='NATIVE' for r in panels)==16);ck('matched_panels',sum(r['view']=='MATCHED' for r in panels)==10)
    keys={(r['view'],r['control_id']) for r in panels};ck('panel_unique',len(keys)==len(panels));ck('fold_panel_keys',{(r['view'],r['control_id']) for r in folds}==keys);ck('edge_panel_keys',{(r['view'],r['control_id']) for r in edges}==keys)
    for p in panels:
        key=(p['view'],p['control_id']);fs=[r for r in folds if (r['view'],r['control_id'])==key];es=[r for r in edges if (r['view'],r['control_id'])==key]
        ck('edge3:'+':'.join(key),len(es)==3);ck('n:'+':'.join(key),sum(int(r['events']) for r in fs)==int(p['scored_transitions']));ib=sum(float(r['independent_bits']) for r in fs);gb=sum(float(r['graph_bits']) for r in fs)
        ck('bits:'+':'.join(key),math.isclose(ib,float(p['independent_bits']),abs_tol=5e-6) and math.isclose(gb,float(p['frozen_graph_bits']),abs_tol=5e-6));ck('gain:'+':'.join(key),math.isclose(ib-gb,float(p['raw_gain']),abs_tol=5e-6));ck('hits:'+':'.join(key),sum(int(r['independent_exact']) for r in fs)==int(p['independent_exact']) and sum(int(r['graph_exact']) for r in fs)==int(p['graph_exact']));ck('positive:'+':'.join(key),sum(float(r['raw_gain'])>0 for r in fs)==int(p['positive_folios']))
        for e in es:
            tag=e['pair_id'].replace('-','_');ck('edge_gain:'+':'.join(key)+':'+tag,math.isclose(sum(float(r[f'pair_{tag}_gain']) for r in fs),float(e['gain']),abs_tol=5e-6));ck('edge_postscore:'+':'.join(key)+':'+tag,e['evidence_status']=='POSTSCORE_DIAGNOSTIC')
    grouped=defaultdict(list)
    for r in null:grouped[(r['view'],r['control_id'])].append(r)
    ck('null_panel_keys',set(grouped)==keys);ck('null_world_count',all(len(rs)==4096 and {int(r['world']) for r in rs}==set(range(4096)) for rs in grouped.values()))
    for p in panels:
        key=(p['view'],p['control_id']);rs=grouped[key];obs=float(p['raw_gain']);pv=(1+sum(float(r['combined_gain'])>=obs-1e-8 for r in rs))/4097
        ck('null_p:'+':'.join(key),math.isclose(pv,float(p['inclusive_p']),abs_tol=5e-10),(pv,p['inclusive_p']))
        es=[r for r in edges if (r['view'],r['control_id'])==key];obsmax=max([obs,*[float(e['gain']) for e in es]]);pm=(1+sum(float(r['max_four_gain'])>=obsmax-1e-8 for r in rs))/4097;ck('max4:'+':'.join(key),math.isclose(pm,float(p['max_four_p']),abs_tol=5e-10))
        for e in es:
            col='gain_'+e['pair_id'].replace('-','_');pe=(1+sum(float(r[col])>=float(e['gain'])-1e-8 for r in rs))/4097;ck('edge_p:'+':'.join(key)+':'+col,math.isclose(pe,float(e['inclusive_p']),abs_tol=5e-10))
    ck('environment_nonempty',len(env)>0);ck('counter_f84',any(r['code']=='F84' for r in counter));ck('semantics_zero',result['semantics']=='UNASSIGNED' and result['page_host_factorizations']==0 and result['tuple_merges']==0);ck('f84_flags',all(v is False for v in result['f84'].values()))
    primary=[r for r in panels if r['view']=='NATIVE'];voyrow=next(r for r in primary if r['control_id']=='VOYNICH_FIXED_HOLDOUT');trans=[r for r in primary if r['control_id']!='VOYNICH_FIXED_HOLDOUT' and int(r['transfers'])];ordinary=[r for r in trans if r['architecture_group']=='ORDINARY_OR_STRUCTURED_NATURAL_LANGUAGE'];dip=[r for r in trans if r['architecture_group']=='REAL_DIPLOMATIC'];comp=[r for r in trans if r['architecture_group'] in {'LEARNED_ABBREVIATION','COMPILER_LIKE_SYNTHETIC'}]
    if not int(voyrow['transfers']):expected='GDT346_LOCAL_OVERFITTING'
    elif ordinary and dip:expected='GENERIC_WRITING_MECHANICS'
    elif len({r['control_id'] for r in comp})>=2 and not ordinary:expected='COMPILER_STYLE_FORMAL_GRAMMAR'
    elif not trans:expected='MANUSCRIPT_SPECIFIC_FORMAL_CONVENTION'
    else:expected='INCONCLUSIVE_CONTROL_TRANSPORT'
    ck('decision',result['status']==expected,(result['status'],expected));ck('transport_list',result['native_transport_controls']==[r['control_id'] for r in trans])
    for p,d in result['inputs'].items():ck('input_hash:'+p,sha(ROOT/p)==d)
    for p,d in result['outputs'].items():ck('output_hash:'+p,sha(ROOT/p)==d)
    for p,d in result['implementation'].items():ck('implementation_hash:'+p,sha(ROOT/p)==d)
    ck('result_content_hash',content(result)==result['content_sha256'])
    validation={'schema':'GDT347_VALIDATION_V1','status':'PASS','checks_passed':len(checks),'checks_failed':0,'result_sha256':sha(RESULT),'source_reconstruction':{'g345_edges':len(src),'voynich_groups':len(voy),'state_mismatches':mismatch,'panels':len(panels),'null_rows':len(null)},'scope':'Independent source-state reconstruction and topology, fold/panel/edge/null/decision/accounting/hash/f84 validation. Control marginal fits and graph normalizers are not independently refit.','checks':checks};validation['content_sha256']=content(validation);VALID.write_bytes(canon(validation));print(f"PASS {len(checks)}/{len(checks)} {result['status']}");return 0
if __name__=='__main__':raise SystemExit(main())
