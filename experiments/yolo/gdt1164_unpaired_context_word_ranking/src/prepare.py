#!/usr/bin/env python3
"""GDT1164 source capacity and anonymous context geometry. Never reads site truth.
Run observed capacity first; null generation requires independent capacity PASS.
"""
import argparse,csv,gzip,hashlib,json,re
from datetime import datetime,timezone
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
EXP=Path(__file__).resolve().parents[1]
ROOT=EXP.parents[2]
MARKER='¤'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def load(p):return json.loads(p.read_text())
def stable_hash(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()

def check_inputs(spec):
    source=load(EXP/'src/SOURCE.json');assert source['input_sha256']==spec['inputs']
    for name,pin in spec['inputs'].items():assert digest(ROOT/name)==pin, 'INVALID_SOURCE_BINDING '+name

def blind_records(spec):
    """Unexpanded writing only; keep first record appearance and original line order."""
    records={}; bybook={b:[] for b in spec['books']}; line_ids=set();record_book={}
    with (ROOT/'gdt155_blinded_diplomatic.tsv').open(newline='') as f:
        for row in csv.DictReader(f,delimiter='\t'):
            if row['corpus']!=spec['corpus'] or row['book_or_ms'] not in bybook:continue
            key=row['record_id'];book=row['book_or_ms']
            assert row['line_id'] not in line_ids,'INVALID_SOURCE_BINDING repeated line'
            line_ids.add(row['line_id'])
            if key not in records:
                records[key]={'book':book,'record_id':key,'tokens':[],'lines':[],'markers':[]};bybook[book].append(key);record_book[key]=book
            r=records[key];assert r['book']==book,'INVALID_SOURCE_BINDING record reused across books'
            tokens=row['diplomatic_marked'].split();assert len(row['diplomatic_bare'].split())==int(row['surface_group_count'])
            assert sum(t.count(MARKER) for t in tokens)==int(row['abbreviation_site_count'])
            for token in tokens:
                location={'line_id':row['line_id'],'record_group_index':len(r['tokens']),'raw_group':token}
                r['tokens'].append(token)
                r['markers'].extend([location.copy() for _ in range(token.count(MARKER))])
            r['lines'].append({'line_id':row['line_id'],'expected_record_lines':int(row['record_line_count'])})
    for r in records.values():assert all(x['expected_record_lines']==len(r['lines']) for x in r['lines'])
    sites=[];ordinal=Counter();siteids=set()
    with (ROOT/'gdt155_blinded_abbreviation_sites.tsv').open(newline='') as f:
        for row in csv.DictReader(f,delimiter='\t'):
            if row['corpus']!=spec['corpus']:continue
            key=row['record_id'];assert key in records,'INVALID_SOURCE_BINDING unknown blind record'
            ordinal[key]+=1;assert ordinal[key]==int(row['site_index_in_record'])
            assert row['site_id'] not in siteids;siteids.add(row['site_id'])
            assert ordinal[key]<=len(records[key]['markers'])
            loc=records[key]['markers'][ordinal[key]-1]
            assert loc['line_id']==row['line_id'],'INVALID_SOURCE_BINDING site line differs'
            reasons=[]
            if row['surface_span_marked']!=loc['raw_group']:reasons.append('marked_span_not_complete_whitespace_group')
            if loc['raw_group'].count(MARKER)!=1:reasons.append('containing_group_marker_count_not_one')
            sites.append({'site_id':row['site_id'],'record_id':key,'book':record_book[key],
                'line_id':row['line_id'],'site_index_in_record':ordinal[key],
                'raw_group':loc['raw_group'],'marked_span':row['surface_span_marked'],
                'eligible':not reasons,'exclusion_reasons':reasons})
    assert all(ordinal[key]==len(r['markers']) for key,r in records.items()),'INVALID_SOURCE_BINDING unmatched markers'
    return records,bybook,sites

def reference_records(spec,held,blind):
    """Check corpus/book in raw selector prefix BEFORE parsing expanded payload.
    This line table is one physical TSV line per source line; malformed framing
    fails rather than admitting hidden multiline payloads or repairing boundaries.
    """
    records={}; bybook={b:[] for b in spec['books'] if b!=held}
    with (ROOT/'gdt155_unblinded_lines.tsv').open(newline='') as f:
        header=next(csv.reader([next(f)],delimiter='\t'))
        assert header==['corpus','book_or_ms','record_id','line_id','expanded_diplomatic']
        for raw in f:
            prefix=raw.split('\t',4)
            assert len(prefix)==5,'INVALID_SOURCE_BINDING expanded TSV framing'
            corpus,book,key,lineid=prefix[:4]
            if corpus!=spec['corpus'] or book not in bybook:continue
            # No held-book expanded payload is parsed or retained by this fold.
            parsed=list(csv.reader([raw],delimiter='\t',strict=True));assert len(parsed)==1 and len(parsed[0])==5
            row=dict(zip(header,parsed[0]));assert row['book_or_ms']==book and row['record_id']==key and row['line_id']==lineid
            assert key in blind and blind[key]['book']==book
            if key not in records:records[key]={'book':book,'record_id':key,'tokens':[],'line_ids':[]};bybook[book].append(key)
            records[key]['tokens'].extend(row['expanded_diplomatic'].split());records[key]['line_ids'].append(lineid)
    for key,r in records.items():assert r['line_ids']==[x['line_id'] for x in blind[key]['lines']]
    return records,bybook

def take_panel(records,ordered,budget):
    selected=[];count=0;overflow=None
    for key in ordered:
        n=len(records[key]['tokens'])
        if count+n>budget:overflow=key;break
        selected.append(key);count+=n
    return selected,{'groups':count,'records':len(selected),'first_overflow_record':overflow,'record_ids':selected,
        'record_lengths':[len(records[k]['tokens']) for k in selected]}

def round_robin(bybook,books):
    index={b:0 for b in books}
    while True:
        emitted=False
        for b in books:
            if index[b]<len(bybook[b]):yield bybook[b][index[b]];index[b]+=1;emitted=True
        if not emitted:return

def vocabulary(token_records,spec,fold,side):
    counts=Counter(t for rec in token_records for t in rec)
    ranked=sorted((t for t,n in counts.items() if n>=spec['panel']['minimum_fit_type_support']),key=lambda t:(-counts[t],t))
    maximum=spec['panel']['written_types'] if side==0 else spec['panel']['reference_types_max']
    chosen=ranked[:maximum]
    order=np.random.default_rng(spec['panel']['opaque_seed_base']+2*fold+side).permutation(len(chosen))
    nodes=[chosen[int(i)] for i in order]
    return nodes,counts,{'supported_types':len(ranked),'selected_types':len(nodes),'opaque_seed':spec['panel']['opaque_seed_base']+2*fold+side}

def geometry(records,nodes,counts,spec):
    top=sorted(counts,key=lambda t:(-counts[t],t))[:spec['panel']['contexts_top_types']]
    context={t:i for i,t in enumerate(top)};width=len(top)+1;offsets=spec['panel']['offsets']
    node={t:i for i,t in enumerate(nodes)}
    C=np.zeros((len(nodes),width*len(offsets)),dtype=np.float64)
    cols=np.zeros(width*len(offsets),dtype=np.float64);rows=np.zeros(len(nodes),dtype=np.float64);total=0
    for rec in records:
        n=len(rec);ci=np.array([context.get(t,len(top)) for t in rec],dtype=np.int64);ni=np.array([node.get(t,-1) for t in rec],dtype=np.int64)
        for oi,offset in enumerate(offsets):
            lo=max(0,-offset);hi=min(n,n-offset)
            if lo>=hi:continue
            center=ni[lo:hi];column=ci[lo+offset:hi+offset]+oi*width
            np.add.at(cols,column,1);total+=len(column)
            keep=center>=0
            np.add.at(C,(center[keep],column[keep]),1);np.add.at(rows,center[keep],1)
    assert int(cols.sum())==total
    pos=C>0;ppmi=np.zeros_like(C)
    rr,cc=np.nonzero(pos)
    ppmi[rr,cc]=np.maximum(0,np.log(C[rr,cc]*total/(rows[rr]*cols[cc])))
    norms=np.linalg.norm(ppmi,axis=1);nonzero=bool(len(nodes)>0 and np.all(norms>0))
    if not nonzero:return None,{'all_profiles_nonzero':False,'zero_profile_indices':np.where(norms==0)[0].tolist(),'mean_offdiagonal_positive':False,'context_events':total}
    normalized=ppmi/norms[:,None];D=np.clip(1-normalized@normalized.T,0,2);np.fill_diagonal(D,0)
    mean=float(D.sum()/(len(nodes)*(len(nodes)-1))) if len(nodes)>1 else 0.
    if mean>0:D/=mean
    return D,{'all_profiles_nonzero':True,'zero_profile_indices':[],'mean_offdiagonal_positive':mean>0,'raw_mean_offdiagonal':mean,'context_events':total,'context_columns':width*len(offsets),'all_center_marginal':True}

def shuffled(records,seed):
    lengths=[len(r) for r in records];flat=[t for r in records for t in r];permutation=np.random.default_rng(seed).permutation(len(flat));mixed=[flat[int(i)] for i in permutation]
    result=[];offset=0
    for n in lengths:result.append(mixed[offset:offset+n]);offset+=n
    return result,stable_hash(permutation.tolist())

def build(spec,runtime,nulls=False,registered_commit=None):
    started=datetime.now(timezone.utc).isoformat()
    check_inputs(spec);records,bybook,sites=blind_records(spec);folds=[];public=[]
    for fold,book in enumerate(spec['books']):
        refs,refbooks=reference_records(spec,book,records)
        wid,wpanel=take_panel(records,bybook[book],spec['panel']['group_budget_each_side'])
        rid,rpanel=take_panel(refs,round_robin(refbooks,[b for b in spec['books'] if b!=book]),spec['panel']['group_budget_each_side'])
        wr=[records[k]['tokens'] for k in wid];er=[refs[k]['tokens'] for k in rid]
        wn,wc,wv=vocabulary(wr,spec,fold,0);en,ec,ev=vocabulary(er,spec,fold,1)
        Dw,wg=geometry(wr,wn,wc,spec);De,eg=geometry(er,en,ec,spec)
        eligible=[dict(s,written_node=wn.index(s['raw_group']),inside_fit_record=s['record_id'] in set(wid)) for s in sites if s['book']==book and s['eligible'] and s['raw_group'] in wn]
        checks={'written_nodes_128':len(wn)==spec['panel']['written_types'],'reference_nodes_at_least128':len(en)>=spec['panel']['reference_types_min'],
            'selected_marked_types_at_least10':len({s['raw_group'] for s in eligible})>=spec['capacity']['minimum_selected_marked_types_each_book'],
            'selected_marked_sites_at_least200':len(eligible)>=spec['capacity']['minimum_selected_marked_wholebook_sites_each_book'],
            'written_profiles_nonzero':wg['all_profiles_nonzero'],'reference_profiles_nonzero':eg['all_profiles_nonzero'],
            'written_mean_distance_positive':wg['mean_offdiagonal_positive'],'reference_mean_distance_positive':eg['mean_offdiagonal_positive']}
        row={'fold':fold,'held_book':book,'checks':checks,'capacity_pass':all(checks.values()),'written_panel':wpanel,'reference_panel':rpanel,'written_vocabulary':wv,'reference_vocabulary':ev,
            'written_geometry':wg,'reference_geometry':eg,'selected_eligible_marked_types':len({s['raw_group'] for s in eligible}),'selected_eligible_wholebook_sites':len(eligible),
            'wholebook_site_coverage':{'all_blinded_sites':sum(s['book']==book for s in sites),'eligible_sites_including_unsupported':sum(s['book']==book and s['eligible'] for s in sites),'excluded_sites':sum(s['book']==book and not s['eligible'] for s in sites)},'world_payloads':[]}
        folds.append({'fold':fold,'book':book,'written_nodes':wn,'reference_nodes':en,'eligible_sites':eligible,
            'excluded_and_unsupported_sites':[dict(s,unsupported_type=s['eligible'] and s['raw_group'] not in wn) for s in sites if s['book']==book and not (s['eligible'] and s['raw_group'] in wn)]})
        for world in (range(20) if nulls else [0]):
            if not row['capacity_pass']:break
            ws,es=wr,er;permutation_hashes=None
            if world:
                ws,wh=shuffled(wr,spec['nulls']['seed_base']+100*fold+2*world)
                es,eh=shuffled(er,spec['nulls']['seed_base']+100*fold+2*world+1)
                Dw,wg=geometry(ws,wn,wc,spec);De,eg=geometry(es,en,ec,spec);permutation_hashes=[wh,eh]
                if not (wg['all_profiles_nonzero'] and eg['all_profiles_nonzero'] and wg['mean_offdiagonal_positive'] and eg['mean_offdiagonal_positive']):
                    raise RuntimeError('INVALID_CONTROL_CAPACITY '+str((fold,world,wg,eg)))
            a=np.array([wc[t] for t in wn],dtype=np.float64);b=np.array([ec[t] for t in en],dtype=np.float64)
            path=runtime/f'fold_{fold}'/f'world_{world:02d}.npz';path.parent.mkdir(parents=True,exist_ok=True)
            np.savez(path,Dw=Dw,De=De,p=a/a.sum(),q=b/b.sum(),written_rates=a/wpanel['groups'],reference_rates=b/rpanel['groups'])
            row['world_payloads'].append({'world':world,'path':f'fold_{fold}/world_{world:02d}.npz','sha256':digest(path),'permutation_sha256':permutation_hashes})
        public.append(row)
    status='CAPACITY_PASS' if all(f['capacity_pass'] for f in public) else 'NO_CAPACITY'
    dump(runtime/'BUILDER_AUDIT.json',{'schema':'GDT1164_BUILDER_AUDIT_V1','gold_read':False,'folds':folds})
    audit_public=EXP/'artifacts/BUILDER_AUDIT.json.gz'
    audit_public.write_bytes(gzip.compress((runtime/'BUILDER_AUDIT.json').read_bytes(),mtime=0))
    result={'experiment':'GDT1164','registered_commit':registered_commit,'extraction_started_utc':started,'extraction_finished_utc':datetime.now(timezone.utc).isoformat(),'status':status,'source_binding_valid':True,'site_truth_read':False,'folds':public,'all_four_required':True,'spec_sha256':digest(EXP/'SPEC.json'),
        'prepare_sha256':digest(Path(__file__)),'source_hashes':spec['inputs'],'audit_sha256':digest(runtime/'BUILDER_AUDIT.json'),'audit_public_gzip_sha256':digest(audit_public),'nulls_built':nulls}
    dump(EXP/'artifacts'/('GEOMETRY.json' if nulls else 'CAPACITY.json'),result)
    print(json.dumps({'status':status,'folds':[{'book':r['held_book'],'written':r['written_vocabulary']['selected_types'],'reference':r['reference_vocabulary']['selected_types'],'marked_types':r['selected_eligible_marked_types'],'marked_sites':r['selected_eligible_wholebook_sites'],'checks':r['checks']} for r in public]}))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--registered-commit',required=True);ap.add_argument('--nulls',action='store_true');ap.add_argument('--capacity-validation',type=Path);a=ap.parse_args()
    assert re.fullmatch('[0-9a-f]{7,40}',a.registered_commit)
    if a.nulls:
        assert a.capacity_validation is not None,'Independent capacity validation required before null construction'
        validation=load(a.capacity_validation);assert validation['status']=='PASS'
        assert load(EXP/'artifacts/CAPACITY.json')['status']=='CAPACITY_PASS'
    build(load(EXP/'SPEC.json'),a.runtime,a.nulls,a.registered_commit)
if __name__=='__main__':main()
