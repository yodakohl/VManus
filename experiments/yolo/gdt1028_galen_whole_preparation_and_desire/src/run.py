from collections import Counter,defaultdict
from common import *
from model import compile_reading,evaluate
from independent import observe

check_lock();assert read(A/'PUBLIC_REGISTRATION.json')['commit']
s=source();cfg=spec();fs=cases();lex={x['form']:x for x in s['lexicon']}
lines=s['target_choice']['whole_record']['lines']
graphs=[];outputs=[];rows=[];summary=[]
for c in cfg['candidates']:
    g=compile_reading(lines,lex,c);assert g['status']=='COMPLETE_GRAPH',g
    graphs.append(g);cr=[]
    for f in fs if c['syntax']=='QUOTED_FOOD_TRANSFER' else [dict(name='STATIC_WHOLE_GRAPH')]:
        out=evaluate(g,f);row=observe(c,f['name'],out);rows.append(row);cr.append(row)
        outputs.append(dict(candidate=c['id'],case=f['name'],output=out))
    summary.append(dict(candidate=c['id'],**{k:v for k,v in c.items() if k!='id'},checked_cases=len(cr),coherent=sum(r['status']=='COHERENT_CONDITIONAL_CONTENT' for r in cr),contradicted=sum(r['status'] in ['CONTRADICTED_FIXTURE','STATIC_CONTRADICTION'] for r in cr),source_complete_rows=sum(r['source_complete'] for r in cr),source_complete_and_coherent=sum(r['source_complete'] and r['status']=='COHERENT_CONDITIONAL_CONTENT' for r in cr),derived_intention_cases=sum(r['not_lose_all']=='DERIVED' for r in cr),rebound_denotations=len(g['rebound_denotations']),independent_meaning_capacity=0))
table(A/'CASES.tsv',rows);table(A/'CANDIDATES.tsv',summary)
write(A/'GRAPHS.json',graphs);write(A/'OUTPUTS.json',outputs)
positions=[];n=0
for line in lines:
    for w,sid in zip(line['words'],line['source_ids']):
        n+=1;e=lex[w]
        positions.append(dict(position=n,locus=line['locus'],source_id=sid,word=w,value=e['value'],denotation=e['denotation'],clause=s['token_receipt'][n-1]['clause'],anchor_eligible=line['anchor_eligible'],liquor_rebind=int(w in ['chody','oteedy','dy']),confirmed=0))
table(A/'ALL_POSITIONS.tsv',positions)
scope={}
for rd,rec in [('ZL3b',s['target_choice']['whole_record']),('IT2a',s['target_choice']['alternative_reader_records']['IT2a'])]:
    result=compile_reading(rec['lines'],lex,cfg['candidates'][0])
    scope[rd]=dict(groups=rec['groups'],status=result['status'],unknown=result.get('unknown',[]),ineligible_lines=[l['locus'] for l in rec['lines'] if not l['anchor_eligible']],record=rec)
scope['RF1b']=dict(records=s['target_choice']['alternative_reader_records']['RF1b'])
write(A/'DIPLOMATIC_SCOPE.json',scope)
groups=defaultdict(list);physical=defaultdict(list)
for c in cfg['candidates']:
    rr=[r for r in rows if r['candidate']==c['id']]
    signature=json.dumps([{k:v for k,v in r.items() if k!='candidate'} for r in rr],sort_keys=True)
    groups[signature].append(c['id'])
    if c['syntax']=='QUOTED_FOOD_TRANSFER':
        oo=[o['output']['dry'] for o in outputs if o['candidate']==c['id']]
        physical[json.dumps(oo,sort_keys=True)].append(c['id'])
write(A/'EQUIVALENCE.json',dict(whole_declared_fixture_projection=list(groups.values()),dry_physical_trace_only=list(physical.values()),scope='Equality of conditional model projections; no empirical discrimination or probability'))
counts=Counter(w for l in lines for w in l['words'])
result=dict(experiment='GDT1028',status='EXECUTED_PENDING_VALIDATION',utc=now(),whole_groups=n,types=len(counts),singleton_types=sum(v==1 for v in counts.values()),productions=5,baseline_bindings=15,optional_bridge='B16a-d with best existence and selection intention separate',new_values=36,liquor_rebound_values=3,ideal_reinterpreted_values=1,literally_shared_with_liquor=33,literally_shared_with_combined_liquor_ideal=32,candidates=summary,case_rows=len(rows),conditional_coherent_rows=sum(r['status']=='COHERENT_CONDITIONAL_CONTENT' for r in rows),contradicted_rows=sum(r['status'] in ['CONTRADICTED_FIXTURE','STATIC_CONTRADICTION'] for r in rows),source_complete_coherent_rows=sum(r['source_complete'] and r['status']=='COHERENT_CONDITIONAL_CONTENT' for r in rows),whole_projection_classes=len(groups),physical_projection_classes=len(physical),confirmed_words=0,independent_meaning_capacity=0,clinical_observations=0,decision='Retain only a conditional source-complete intrinsic/general/bridged account where all bridge premises and source laws hold; preserve coherent unbridged, ideal, scope and ownership rivals and their source-content gaps. No meaning ranking from these invented fixtures.')
write(A/'RESULT.json',result)
print(json.dumps({k:result[k] for k in ['status','case_rows','conditional_coherent_rows','contradicted_rows','source_complete_coherent_rows','confirmed_words']}))
