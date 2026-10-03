#!/usr/bin/env python3
"""Independent GDT1156 reconstruction from frozen admitted event cache."""
import collections
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import random

E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def read(p):return json.loads(p.read_text())
def mean(xs):return sum(xs)/len(xs) if xs else None
def close(a,b):return a is b if a is None or b is None else math.isclose(a,b,rel_tol=1e-11,abs_tol=1e-13)
def ranks(xs):
    ordered=sorted(range(len(xs)),key=lambda i:xs[i]);out=[0.]*len(xs);i=0
    while i<len(xs):
        j=i+1
        while j<len(xs) and xs[ordered[j]]==xs[ordered[i]]:j+=1
        for k in range(i,j):out[ordered[k]]=(i+1+j)/2
        i=j
    return out
def spearman(xs,ys):
    if len(xs)<2:return None
    a,b=ranks(xs),ranks(ys);aa,bb=mean(a),mean(b)
    denom=math.sqrt(sum((x-aa)**2 for x in a)*sum((y-bb)**2 for y in b))
    return sum((x-aa)*(y-bb) for x,y in zip(a,b))/denom if denom else None

def reconstruct():
    for name,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
    geometry=read(E/'src/SOURCE.json');quires={int(q):v for q,v in geometry['nominal_quires'].items()}
    assert quires==dict([(q,list(range(8*(q-1)+1,8*q+1))) for q in range(1,8)]+[(20,list(range(103,117)))])
    allowed=set(read(ROOT/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json')['allowed_selectors'])
    inv={}
    with (ROOT/'experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_155_MATCHED_STEM_SUMMARY.tsv').open() as f:
        for row in csv.DictReader(f,delimiter='\t'):
            for y,c in enumerate(['l','m']):inv[row[c+'_surface']]=(row['stem'],y)
    assert len(inv)==310
    cache=read(ROOT/'experiments/yolo/gdt1155_terminal_drawing_edge_transport/artifacts/EVENTS.json');out={}
    for r,original in cache.items():
        assert len({e['source_id'] for e in original})==len(original)
        for e in original:
            assert e['page'] in allowed and not e['page'].startswith(('f84','f116v'))
            assert inv[e['word']]==(e['stem'],e['m'])
        events=[e for e in original if e['boundary'] in ['END','SPACE'] and e['leaf'] not in [104,115]]
        bypage=collections.defaultdict(list)
        for e in original:
            if e['boundary'] in ['END','SPACE']:bypage[e['page']].append(e)
        pages={};sheets=[];blocks=collections.defaultdict(list)
        for q,leaves in sorted(quires.items()):
            for leaf in leaves:
                for side in ['r','v']:
                    page=f'f{leaf}{side}';es=bypage[page];strata=sorted({tuple(e['stratum']) for e in es})
                    why=[]
                    if leaf in [103,116]:why.append('excluded_pair_page')
                    if page not in allowed:why.append('unadmitted')
                    if leaf in [104,115]:why.append('excluded_leaf')
                    if not es:why.append('unrepresented')
                    if len(es)<10:why.append('few_events')
                    if len(strata)!=1:why.append('non_single_stratum')
                    elif not (strata[0][0] and strata[0][1] in ['A','B'] and strata[0][2] in ['1','2','3','4','5']):why.append('unknown_stratum')
                    pages[page]={'quire':q,'leaf':leaf,'events':len(es),'strata':strata,'reasons':why,'m':sum(e['m'] for e in es),'boundaries':dict(collections.Counter(e['boundary'] for e in es))}
            for a,b in zip(leaves[:len(leaves)//2],reversed(leaves[len(leaves)//2:])):
                pp=[f'f{a}r',f'f{a}v',f'f{b}r',f'f{b}v'];why=[]
                if [a,b]==[103,116]:why.append('excluded_pair')
                if any(pages[p]['reasons'] for p in pp):why.append('page_ineligible')
                sts={s for p in pp for s in pages[p]['strata']}
                if len(sts)!=1:why.append('strata_differ')
                s={'quire':q,'a':a,'b':b,'pages':pp,'reasons':why,'stratum':next(iter(sts)) if len(sts)==1 else None}
                sheets.append(s)
                if not why:blocks[(q,s['stratum'])].append(s)
        for key,ss in blocks.items():
            if len(ss)<2:
                for s in ss:s['reasons'].append('singleton_block')
        blocks={key:sorted(ss,key=lambda s:s['a']) for key,ss in sorted(blocks.items()) if len(ss)>=2}
        retained=[s for ss in blocks.values() for s in ss]
        preds={};residuals={}
        for q in sorted(quires):
            counts={b:collections.defaultdict(lambda:[0,0]) for b in ['END','SPACE']}
            for e in events:
                if e['leaf'] in quires[q]:continue
                st=tuple(e['stratum'])
                for key in [(),st,(e['stem'],)+st]:
                    c=counts[e['boundary']][key];c[0]+=1;c[1]+=e['m']
            for page in sorted(p for p,record in pages.items() if record['quire']==q and record['leaf'] not in [103,104,115,116] and bypage[p]):
                residual=[]
                for e in bypage[page]:
                    st=tuple(e['stratum']);cc=counts[e['boundary']];ng,mg=cc[()];ns,ms=cc[st];nt,mt=cc[(e['stem'],)+st]
                    g=(mg+.5)/(ng+1);z=(ms+20*g)/(ns+20);p=(mt+10*z)/(nt+10);res=e['m']-p;residual.append(res)
                    preds[e['source_id']]={'event':e,'quire':q,'model':{'N_global':ng,'M_global':mg,'g':g,'N_stratum':ns,'M_stratum':ms,'s':z,'N_stem_stratum':nt,'M_stem_stratum':mt,'p':p},'residual':res}
                residuals[page]=mean(residual)
        for s in retained:
            s['delta_a']=residuals[f"f{s['a']}r"]-residuals[f"f{s['a']}v"]
            s['delta_b']=residuals[f"f{s['b']}r"]-residuals[f"f{s['b']}v"]
            s['score']=-.5*s['delta_a']*s['delta_b']
        qs=sorted({s['quire'] for s in retained});qobs={q:mean([s['score'] for s in retained if s['quire']==q]) for q in qs};qcenter={}
        for q in qs:
            numerator=0;n=0
            for (qq,st),ss in blocks.items():
                if qq==q:
                    numerator+=len(ss)*(-.5*mean([s['delta_a'] for s in ss])*mean([s['delta_b'] for s in ss]));n+=len(ss)
            qcenter[q]=numerator/n
        obs=mean(list(qobs.values()));center=mean(list(qcenter.values()));orbit=math.prod(math.factorial(len(ss)) for ss in blocks.values())
        def score(orders):
            contrib=collections.defaultdict(list)
            for ((q,st),ss),order in zip(blocks.items(),orders):
                upper={s['b']:s['delta_b'] for s in ss}
                for s,b in zip(ss,order):contrib[q].append(-.5*s['delta_a']*upper[b])
            qq={q:mean(contrib[q]) for q in qs};return {'score':mean(list(qq.values())),'quires':qq}
        if not blocks:null=[];method='NO_CAPACITY'
        elif orbit<=100000:
            orders=[list(itertools.permutations(sorted(s['b'] for s in ss))) for ss in blocks.values()]
            null=[score(o) for o in itertools.product(*orders)];method='EXACT'
        else:
            rng=random.Random(1156);null=[];method='MONTE_CARLO'
            for _ in range(9999):
                orders=[]
                for ss in blocks.values():
                    bs=sorted(s['b'] for s in ss);rng.shuffle(bs);orders.append(bs)
                null.append(score(orders))
        nmore=sum(x['score']>=obs-1e-15 for x in null) if null else None
        rank=(nmore/len(null) if method=='EXACT' else (1+nmore)/10000) if null else None
        cap=len(retained)>=8 and len(qs)>=3
        frac=sum(qobs[q]-qcenter[q]>0 for q in qs)/len(qs) if qs else None
        status='NO_CAPACITY' if not cap else 'SAME_FACE_RESIDUAL_CANDIDATE' if obs-center>0 and rank<=.05 and frac>=2/3 else 'NOT_SUPPORTED'
        def diag(ss):return {'lower':spearman([s['a'] for s in ss],[s['delta_a'] for s in ss]),'upper':spearman([s['b'] for s in ss],[s['delta_b'] for s in ss])}
        out[r]={'pages':pages,'sheets':sheets,'blocks':blocks,'retained':retained,'predictions':preds,'residuals':residuals,'qobs':qobs,'qcenter':qcenter,'observed':obs,'center':center,'orbit':orbit,'null':null,'method':method,'rank':rank,'capacity':cap,'positive_fraction':frac,'status':status,'diagnostics':{'pooled':diag(retained),'quires':{q:diag([s for s in retained if s['quire']==q]) for q in qs}}}
    return out
def main():
    independent=reconstruct(); art=E/'artifacts'
    eligibility=read(art/'ELIGIBILITY.json'); predictions=read(art/'PREDICTIONS.json'); residuals=read(art/'PAGE_RESIDUALS.json'); sheets=read(art/'SHEETS.json'); quires=read(art/'QUIRES.json'); null=read(art/'NULL_SCORES.json'); diag=read(art/'DIAGNOSTICS.json'); result=read(art/'RESULT.json')
    checks=['all7pins_verified','frozen_geometry155stems310forms_and_source_IDs','no_reserved_source_events','whole_quire_and_mixed_hand_training_exclusions']
    prmap={'excluded_pair_page':'INCOMPLETE_BIFOLIUM_EXPLICIT_EXCLUSION','excluded_leaf':'MIXED_HAND_EXPLICIT_EXCLUSION','unadmitted':'PAGE_NOT_ADMITTED','unrepresented':'NO_END_SPACE_EVENTS','few_events':'FEWER_THAN_10_EVENTS','non_single_stratum':'NOT_SINGLE_KNOWN_STRATUM','unknown_stratum':'NOT_SINGLE_KNOWN_STRATUM'}
    for r,x in independent.items():
        ep=eligibility[r]['pages']; assert set(ep)==set(x['pages'])
        for page,p in x['pages'].items():
            a=ep[page]
            for k in ['quire','leaf','events','m','boundaries']:assert a[k]==p[k],(r,page,k)
            assert a['strata']==[list(z) for z in p['strata']]
            assert set(a['reasons'])=={prmap[z] for z in p['reasons']},(r,page,'reasons')
            assert a['eligible']==(not p['reasons']) and a['admitted']==('unadmitted' not in p['reasons'])
        eb=eligibility[r]['bifolia'];assert len(eb)==len(x['sheets'])
        for a,p in zip(eb,x['sheets']):
            for k in ['quire','a','b','pages']:assert a[k]==p[k]
            assert a['stratum']==(list(p['stratum']) if p['stratum'] else None)
            reasons=[]
            if 'page_ineligible' in p['reasons']:reasons.append('PAGE_ELIGIBILITY_FAILED')
            if 'strata_differ' in p['reasons']:reasons.append('FOUR_PAGE_STRATUM_MISMATCH')
            base=not reasons
            if 'singleton_block' in p['reasons']:reasons.append('QUIRE_STRATUM_FEWER_THAN_TWO_BIFOLIA')
            assert a['reasons']==reasons and a['base_eligible']==base and a['eligible']==(not reasons)
        pred=predictions[r];assert len(pred)==len(x['predictions']) and len({p['source_id'] for p in pred})==len(pred)
        retainedpages={p for s in x['retained'] for p in s['pages']}
        for a in pred:
            p=x['predictions'][a['source_id']]
            assert all(a[k]==v for k,v in p['event'].items())
            assert a['quire']==p['quire'] and close(a['residual'],p['residual'])
            assert a['diagnostic_only']==(a['page'] not in retainedpages)
            assert set(a['model'])==set(p['model'])
            for k,v in p['model'].items():assert close(a['model'][k],v),(r,a['source_id'],k)
        assert set(residuals[r])==set(x['residuals'])
        for page,val in x['residuals'].items():
            a=residuals[r][page];p=[z for z in x['predictions'].values() if z['event']['page']==page]
            assert a['page']==page and a['quire']==x['pages'][page]['quire'] and a['events']==len(p)
            assert close(a['residual'],val) and close(a['observed_m_rate'],mean([z['event']['m'] for z in p])) and close(a['predicted_m_rate'],mean([z['model']['p'] for z in p]))
            assert set(a['source_ids'])=={z['event']['source_id'] for z in p} and len(a['source_ids'])==len(p)
            assert a['retained_sheet']==(page in retainedpages) and a['diagnostic_only']==(page not in retainedpages)
            assert a['page_eligible']==(not x['pages'][page]['reasons'])
        assert len(sheets[r])==len(x['retained'])
        for a,p in zip(sheets[r],x['retained']):
            assert all(a[k]==p[k] for k in ['quire','a','b','pages'])
            assert close(a['delta_a'],p['delta_a']) and close(a['delta_b'],p['delta_b']) and close(a['contribution'],p['score'])
        assert set(quires[r])=={str(q) for q in x['qobs']}
        for q,obs in x['qobs'].items():
            a=quires[r][str(q)];assert a['sheets']==sum(s['quire']==q for s in x['retained'])
            assert close(a['observed'],obs) and close(a['analytical_null_mean'],x['qcenter'][q]) and close(a['centered'],obs-x['qcenter'][q])
            assert close(a['empirical_null_mean'],mean([n['quires'][q] for n in x['null']]))
        a=null[r];assert a['method']==x['method'] and a['orbit_size']==x['orbit'] and a['seed']==1156
        blocklist=[{'quire':q,'stratum':list(st),'lower_leaves':sorted(s['a'] for s in ss),'upper_leaves':sorted(s['b'] for s in ss)} for (q,st),ss in x['blocks'].items()]
        assert a['blocks']==blocklist and len(a['scores'])==len(x['null'])
        for n,p in zip(a['scores'],x['null']):
            assert close(n['score'],p['score']) and set(n['quires'])=={str(q) for q in p['quires']}
            assert all(close(n['quires'][str(q)],v) for q,v in p['quires'].items())
        for group,ds in [('pooled',x['diagnostics']['pooled'])]+[(str(q),d) for q,d in x['diagnostics']['quires'].items()]:
            a=diag[r]['pooled'] if group=='pooled' else diag[r]['quires'][group]
            count=len(x['retained']) if group=='pooled' else sum(s['quire']==int(group) for s in x['retained'])
            for label,key in [('a','lower'),('b','upper')]:assert a[label]['n']==count and close(a[label]['rho'],ds[key])
        a=result['readers'][r]
        expected={'status':x['status'],'capacity':x['capacity'],'sheets':len(x['retained']),'quires':len(x['qobs']),'observed':x['observed'],'analytical_null_mean':x['center'],'centered':x['observed']-x['center'],'empirical_null_mean':mean([n['score'] for n in x['null']]),'positive_centered_quires':sum(x['qobs'][q]-x['qcenter'][q]>0 for q in x['qobs']),'null_method':x['method'],'orbit_size':x['orbit'],'draws':len(x['null']),'null_at_least_observed':sum(n['score']>=x['observed']-1e-15 for n in x['null']),'reference_rank':x['rank']}
        for k,v in expected.items():assert close(a[k],v) if isinstance(v,float) else a[k]==v,(r,k)
    checks+=['all140nominal_pages_perreader_counts_metadata_exclusions','all35nominal_bifolia_perreader_and_singleton_blocks','all_diagnostic_and_target_event_hierarchy_predictions','all_page_residuals_and_complete_source_ID_sets','all_same_face_sheet_and_equal_quire_scores','analytical_block_centers_and_empirical_orbit_means','all24exact_repairings_eachreader','all_average_rank_Spearman_diagnostics','capacity_ranks_and_primary_only_decision']
    assert result['primary_reader']=='IT2a' and result['status']==independent['IT2a']['status'] and result['meanings']==0
    assert all(result[k] is False for k in ['causal_production_vs_reading_order_claim','independent_confirmation','significance_claim'])
    assert spearman([1,2,2,4],[4,2,2,1])==-1 and spearman([1,1],[3,4]) is None and spearman([1],[2]) is None
    checks.append('no_causal_or_semantic_claim_and_rank_edge_cases')
    out={'status':'PASS','checks_passed':len(checks),'checks':checks,'scientific_decision':result['status'],'readers':{r:{'retained_sheets':len(x['retained']),'quires':len(x['qobs']),'prediction_events':len(x['predictions']),'reference_rank':x['rank'],'decision':x['status']} for r,x in independent.items()},'limitations':['Fixed collation geometry accepted as pinned input; physical conjugacy not newly inspected.','No independent manuscript confirmation; three readers are alternative transcriptions.','Serial trends, content arrangement, parchment properties and unmeasured hand differences can produce association.','The endpoint cannot distinguish production chronology from reading order.','Capacity failure is not evidence against manuscript-wide sheet-face effects.','Additional page predictions are diagnostic only and do not alter eligibility or the fixed statistic.']}
    (art/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n')
    text=['# GDT1156 independent validation','','PASS: '+str(len(checks))+' check groups.','','Independent extraction from pinned1155 events, whole-quire exclusion, fixed hierarchy, all geometry and eligibility, residuals, exact24-configuration orbit per reader and diagnostics. No runner functions imported.','','Primary decision: '+result['status']+'. Four retained sheets in one quire in every reader; required minimum is eight sheets in three quires.','','## Checks','']+['- '+c for c in checks]+['','## Limitations','']+['- '+c for c in out['limitations']]
    (art/'VALIDATION.md').write_text('\n'.join(text)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ['checks','limitations']}))
if __name__=='__main__':main()
