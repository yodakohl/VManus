#!/usr/bin/env python3
import collections,concurrent.futures,csv,datetime,time
from common import *
import grammar

def family_job(family):
    started=time.monotonic();s=read(E/'src/SPEC.json');g=read(R/s['grammar']);pred=read(A/'PREDICTIONS.json');panel=read(A/'PANEL.json');raw=next(p['words'] for p in panel if p['edition']=='ZL3b')
    b=grammar.build(raw,g,family,timeout=s['primary_query_ms']);attempts=[];positive=[];failed=0;queries=[];exhaustive=False;next_unexamined=None
    while True:
        left=s['seconds_per_family']-(time.monotonic()-started)
        if left<=0:stop='WALL_BUDGET';break
        b['solver'].set(timeout=max(1,min(s['primary_query_ms'],int(left*1000))))
        answer=str(b['solver'].check());queries.append(answer)
        if answer=='unsat':exhaustive=True;stop='RESIDUAL_SYNTAX_EXHAUSTED';break
        if answer!='sat':stop='SOLVER_UNKNOWN';break
        if len(attempts)>=s['max_syntactic_maps'] or len(positive)>=s['max_positive_tuples']:
            next_unexamined=grammar.extract(b);stop='CANDIDATE_CAP';break
        w=grammar.extract(b);grammar.ground(w,raw,g,family);ev=evaluate(w['parse'],g,s,keep_full=True)
        row=dict(attempt=len(attempts),**w,coherent_variants=ev['coherent_variants'],replays=ev['replays'])
        if ev['coherent_variants']:
            projection={word:w['code'][word] for word in pred['projection_words']}
            for vi in ev['coherent_variants']:
                if any(x['values']==projection and x['variant_index']==vi for x in positive):continue
                positive.append(dict(tuple=len(positive),attempt=row['attempt'],values=projection,variant_index=vi));grammar.block_projection(b,projection,vi)
            row['full_replays']=ev['full']
        else:failed+=1
        grammar.block_exact(b,w)
        attempts.append(row)
        if len(attempts)%8==0:print(json.dumps(dict(family=family,attempts=len(attempts),coherent_tuples=len(positive),seconds=round(time.monotonic()-started,2))),flush=True)
    out=dict(family=family,exhaustive_projection=exhaustive,stop_reason=stop,queries=queries,attempts=attempts,positive_tuples=positive,failed_maps=failed,next_syntactic_witness_unexamined=next_unexamined,wall_seconds=time.monotonic()-started,confirmed_words=0,independent_meaning_capacity=0)
    put('FAMILY_'+family+'.json',out);return {k:v for k,v in out.items() if k not in ('attempts','next_syntactic_witness_unexamined')}

def main():
    checklock();assert read(A/'PUBLIC_REGISTRATION.json')['commit'];started=datetime.datetime.now(datetime.timezone.utc).isoformat();t=time.monotonic();s=read(E/'src/SPEC.json');panel=read(A/'PANEL.json');pred=read(A/'PREDICTIONS.json')
    with concurrent.futures.ProcessPoolExecutor(max_workers=s['workers']) as pool:summary=list(pool.map(family_job,s['families']))
    domains=[];raw=next(p['words'] for p in panel if p['edition']=='ZL3b');freq=collections.Counter(raw)
    for brief in summary:
        r=read(A/('FAMILY_'+brief['family']+'.json'));witnesses=[a for a in r['attempts'] if a['coherent_variants']]
        for word in sorted(set(raw)):
            projected=word in pred['projection_words'];values=sorted({w['code'][word] for w in witnesses})
            domains.append(dict(family=r['family'],word=word,occurrences=freq[word],values=values,projected=projected,domain_exhaustive=projected and r['exhaustive_projection'],meaning_status='CONDITIONAL_ROLE_DOMAIN' if projected and r['exhaustive_projection'] else 'WITNESSED_VALUES_ONLY',independent_meaning_capacity=0))
    result=dict(experiment='GDT1006',status='CONDITIONAL_UNFIXED_LEXICON_PROJECTIONS',readers=[{k:p[k] for k in ('edition','groups','whole_paragraph_contract','strict_anchor_eligible','status')} for p in panel],projection_words=pred['projection_words'],families=summary,confirmed_words=0,independent_meaning_capacity=0,significance=False)
    put('DOMAINS.json',domains);put('RESULT.json',result);put('EXECUTION_RECEIPT.json',dict(started_utc=started,finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),wall_seconds=time.monotonic()-t,prior_exposure=True,old_lexicon_bound_in_search=False,new_admissions=0,reserves_opened=False))
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['family','attempt','status','coherent_variants','code','clauses','independent_meaning_capacity'])
        for family in s['families']:
            for row in read(A/('FAMILY_'+family+'.json'))['attempts']:w.writerow([family,row['attempt'],'COHERENT' if row['coherent_variants'] else 'ALL_32_VARIANTS_REJECTED',','.join(map(str,row['coherent_variants'])),json.dumps(row['code'],sort_keys=True,separators=(',',':')),';'.join(f"{p['start']+1}-{p['end']}:{p['kind']}" for p in row['parse']),0])
    with (A/'PROJECTED_CANDIDATES.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['family','tuple','attempt',*pred['projection_words'],'variant_index',*read(R/s['grammar'])['variants'],'independent_meaning_capacity'])
        for family in s['families']:
            for p in read(A/('FAMILY_'+family+'.json'))['positive_tuples']:
                v=pred['all_variants'][p['variant_index']];w.writerow([family,p['tuple'],p['attempt'],*[p['values'][x] for x in pred['projection_words']],p['variant_index'],*v.values(),0])
    with (A/'WORD_DOMAINS.tsv').open('w',newline='') as f:
        w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(['family','word','occurrences','values','domain_exhaustive','meaning_status','independent_meaning_capacity'])
        for d in domains:w.writerow([d['family'],d['word'],d['occurrences'],','.join(d['values']),d['domain_exhaustive'],d['meaning_status'],0])
    print(json.dumps({**result,'families':[{k:v for k,v in r.items() if k not in ('queries','positive_tuples')} for r in summary]},indent=2))
if __name__=='__main__':main()
