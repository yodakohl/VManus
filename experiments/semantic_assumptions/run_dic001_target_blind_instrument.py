#!/usr/bin/env python3
"""Develop DIC001 reset-likeness instrument with all target pages excluded."""

from __future__ import annotations
import csv, hashlib, json, math, re
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

BASE=Path(__file__).resolve().parent; R=BASE/'results'
SRC=R/'source_native_structural_interlinear_v1.tsv'; CAP=R/'dic001_drawing_interruption_capacity.tsv'
SPEC=BASE/'DIC001_TARGET_BLIND_INSTRUMENT_SPEC.md'; SCRIPT=Path(__file__).resolve()
OUT=R/'dic001_target_blind_instrument.json'; REPORT=R/'dic001_target_blind_instrument_report.md'
SPACE='ZL3b:DEFINITE_SPACE;IT2a:DEFINITE_SPACE;RF1b:DEFINITE_SPACE'
SRC_SHA='95a15329c61a11c1c4dc671b4df2b3482af9d25a1108eadac2f69b066d3785af'
CAP_SHA='e4e1a507211230f362ac4fd34bc0c382442300600132b7deb4e971cab69cfa2c'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def folio(p): return re.match(r'f\d+',p).group()
def number(l): return int(l.rsplit('.',1)[1])
def shape(a,b):
    l=a['family_surface']; r=b['family_surface']
    return {'L1':l[-1], 'R1':r[0], 'X':l[-1]+'|'+r[0], 'L2':l[-2:] if len(l)>1 else '#'+l,
            'R2':r[:2] if len(r)>1 else r+'#', 'X22':(l[-2:] if len(l)>1 else '#'+l)+'|'+(r[:2] if len(r)>1 else r+'#')}
def length(a,b):
    x=min(len(a['family_surface']),8); y=min(len(b['family_surface']),8)
    return {'LL':str(x),'RL':str(y),'LEN':f'{x}|{y}'}
def fit(train, feature):
    counts={0:defaultdict(Counter),1:defaultdict(Counter)}; totals={0:Counter(),1:Counter()}; values=defaultdict(set)
    for e in train:
        for slot,val in feature(e[3],e[4]).items(): counts[e[2]][slot][val]+=1; totals[e[2]][slot]+=1; values[slot].add(val)
    def score(e):
        s=0.0
        for slot,val in feature(e[3],e[4]).items():
            k=len(values[slot])+1
            s += math.log((counts[1][slot][val]+1)/(totals[1][slot]+k))-math.log((counts[0][slot][val]+1)/(totals[0][slot]+k))
        return s
    return score
def summaries(scored, labels=None):
    page=defaultdict(lambda:{0:[],1:[]})
    for i,e,s in scored: page[e[0]][e[2] if labels is None else labels[i]].append(s)
    fol=defaultdict(list); cur=defaultdict(list)
    for p,v in page.items():
        if not v[0] or not v[1]: continue
        auc=np.mean([(a>b)+.5*(a==b) for a in v[1] for b in v[0]])
        f=next(e[1] for _,e,_ in scored if e[0]==p); c=next(e[5] for _,e,_ in scored if e[0]==p)
        fol[f].append(float(auc)); cur[c].append(float(auc))
    fa={f:float(np.mean(v)) for f,v in fol.items()}; ca={c:float(np.mean(v)) for c,v in cur.items()}
    return {'auc':float(np.mean(list(fa.values()))),'folio_auc':fa,'currier_auc':ca,'positive_folios':sum(v>.5 for v in fa.values()),'folios':len(fa),'pages':len(page)}
def main():
    if sha(SRC)!=SRC_SHA or sha(CAP)!=CAP_SHA: raise SystemExit('frozen DIC001 instrument input drift')
    target_pages=set()
    with CAP.open() as h:
        for r in csv.DictReader(h,delimiter='\t'):
            if r['boundary_class']=='DRAWING_INTERRUPTION': target_pages.add(r['page'])
    with SRC.open() as h: raw=list(csv.DictReader(h,delimiter='\t'))
    by=defaultdict(list)
    for r in raw:
        if r['page'] not in target_pages and r['grammar_scope']=='CONFIRMED_PROSE': by[r['locus']].append(r)
    for v in by.values(): v.sort(key=lambda r:int(r['group_index']))
    events=[]
    for v in by.values():
        for a,b in zip(v,v[1:]):
            if a['right_boundary_profile']==SPACE: events.append((a['page'],folio(a['page']),0,a,b,a['currier']))
    pages=defaultdict(list)
    for v in by.values(): pages[v[0]['page']].append(v)
    for p,lines in pages.items():
        lines.sort(key=lambda v:number(v[0]['locus']))
        for a,b in zip(lines,lines[1:]):
            if number(b[0]['locus'])==number(a[0]['locus'])+1 and b[0]['code'].startswith('+P'):
                events.append((p,folio(p),1,a[-1],b[0],b[0]['currier']))
    scored={'SHAPE':[],'LENGTH':[]}
    for f in sorted({e[1] for e in events}):
        train=[e for e in events if e[1]!=f]; test=[e for e in events if e[1]==f]
        for name,fn in (('SHAPE',shape),('LENGTH',length)):
            scorer=fit(train,fn)
            scored[name] += [(len(scored[name])+i,e,scorer(e)) for i,e in enumerate(test)]
    # replace unstable running indices with canonical event-order indices
    for name in scored: scored[name]=[(i,e,s) for i,(_,e,s) in enumerate(scored[name])]
    summary={name:summaries(vals) for name,vals in scored.items()}
    rng=np.random.default_rng(4100101); real=summary['SHAPE']['auc']; null=[]
    page_indices=defaultdict(list)
    for i,e,s in scored['SHAPE']: page_indices[e[0]].append(i)
    base=[e[2] for _,e,_ in scored['SHAPE']]
    for _ in range(64):
        lab=base.copy()
        for ids in page_indices.values():
            vals=[lab[i] for i in ids]; rng.shuffle(vals)
            for i,v in zip(ids,vals): lab[i]=v
        null.append(summaries(scored['SHAPE'],lab)['auc'])
    p=(1+sum(x>=real for x in null))/65
    counts=Counter(e[2] for e in events)
    gates={'resets_at_least_1000':counts[1]>=1000,'folios_at_least_60':summary['SHAPE']['folios']>=60,
           'shape_auc_at_least_075':real>=.75,'shape_minus_length_at_least_015':real-summary['LENGTH']['auc']>=.15,
           'positive_folios_at_least_90pct':summary['SHAPE']['positive_folios']>=math.ceil(.9*summary['SHAPE']['folios']),
           'currier_A_B_auc_at_least_070':all(summary['SHAPE']['currier_auc'].get(c,0)>=.70 for c in 'AB'),
           'permutation_p_at_most_1_over_65':p<=1/65,'target_pages_excluded':not ({e[0] for e in events}&target_pages)}
    result={'experiment':'DIC001_TARGET_BLIND_INSTRUMENT','status':'PASS_TARGET_BLIND_REFERENCE_INSTRUMENT' if all(gates.values()) else 'STOP_INSTRUMENT_GATES',
      'inputs':{x.name:sha(x) for x in (SRC,CAP,SPEC,SCRIPT)},'counts':{'events':len(events),'spaces':counts[0],'resets':counts[1],'target_pages_excluded':len(target_pages)},
      'summary':summary,'permutation':{'worlds':64,'p':p,'null_min':min(null),'null_max':max(null)},'gates':gates,
      'drawing_target_family_scores_computed':False,'decision':'AUTHORIZE_INDEPENDENT_RECONSTRUCTION_ONLY' if all(gates.values()) else 'STOP',
      'claim_ceiling':'Reference reset-likeness instrument only; no drawing result, word, sound, POS, meaning, plaintext, language, cipher, or translation.'}
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    REPORT.write_text(f"# DIC001 target-blind continuity instrument\n\nStatus: **{result['status']}**.\n\nAll **{len(target_pages)}** drawing-target pages were excluded. Held-folio shape AUC is **{real:.6f}** across **{summary['SHAPE']['folios']}** folios versus length-only **{summary['LENGTH']['auc']:.6f}**; **{summary['SHAPE']['positive_folios']}/{summary['SHAPE']['folios']}** folios are positive and the 64-world within-page permutation p is **{p:.6f}**. The reference has **{counts[1]:,}** continuation resets and **{counts[0]:,}** ordinary spaces.\n\nThis authorizes independent reconstruction only. No drawing-interruption family score or semantic value was computed.\n")
    print(json.dumps(result,indent=2,sort_keys=True))
if __name__=='__main__': main()
