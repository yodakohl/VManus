from collections import defaultdict
from common import *
from model import compile_reading,evaluate,projection
check_lock();assert read(A/'PUBLIC_REGISTRATION.json')['commit']
s=source();lex={e['form']:e for e in s['lexicon']};lines=s['selected_target']['full_record']['lines']
rows=[];outs=[];graphs=[];summ=[]
for c in spec()['candidates']:
 g=compile_reading(lines,lex,c);assert g['status']=='COMPLETE_GRAPH'
 g['source_argument_bindings']=[p['structure'] for p in s['whole_paragraph_productions']];graphs.append(g);cr=[]
 for f in cases():
  o=evaluate(g,f);r=projection(c,f['name'],o);cr.append(r);rows.append(r);outs.append(dict(candidate=c['id'],case=f['name'],output=o))
 summ.append(dict(candidate=c['id'],worlds=len(cr),unit_compatible=sum(r['status']=='COMPATIBLE_IN_HYPOTHETICAL_WORLD' for r in cr),unit_contradicted=sum(r['status']=='CONTRADICTED_IN_HYPOTHETICAL_WORLD' for r in cr),full_parent_compatible=sum(r['full_parent_compatible'] for r in cr),literal_values=33-len(c['rebound']),rebound_values=','.join(c['rebound']) or '[]',extra_actuation=c['actuator'],extra_duration=c['duration'],independent_meaning_capacity=0))
table(A/'CASES.tsv',rows);table(A/'CANDIDATES.tsv',summ);write(A/'GRAPHS.json',graphs);write(A/'OUTPUTS.json',outs)
positions=[];i=0
for l in lines:
 for w,sid in zip(l['words'],l['source_ids']):
  i+=1;e=lex[w];p=next(p for p in s['whole_paragraph_productions'] if i in p['positions'])
  positions.append(dict(position=i,locus=l['locus'],source_id=sid,form=w,value=e['value'],denotation=e['denotation'],clause=p['id'],anchor_eligible=l['anchor_eligible'],confirmed=0))
table(A/'ALL_POSITIONS.tsv',positions)
it=s['selected_target']['alternatives']['IT2a'][0]
write(A/'DIPLOMATIC_SCOPE.json',dict(IT2a=dict(record=it,whole_compilation=compile_reading(it['lines'],lex,spec()['candidates'][0])),RF1b=s['selected_target']['alternatives']['RF1b']))
full=defaultdict(list);water=defaultdict(list)
for c in spec()['candidates']:
 full[json.dumps([{k:v for k,v in r.items() if k not in ['candidate','literal_values']} for r in rows if r['candidate']==c['id']],sort_keys=True)].append(c['id'])
 water[json.dumps([o['output']['water_only_derived'] for o in outs if o['candidate']==c['id']],sort_keys=True)].append(c['id'])
write(A/'EQUIVALENCE.json',dict(full_world_projection=list(full.values()),water_motion_projection=list(water.values()),warning='Equality of conditional predictions, not independent confirmation'))
result=dict(experiment='GDT1030',status='EXECUTED_PENDING_VALIDATION',utc=now(),whole_groups=40,whole_types=33,singleton_types=27,productions=4,discontinuous_productions=3,source_assumptions=20,additional_temporal_witness_convention=1,candidates=summ,world_rows=len(rows),unit_compatible=sum(r['status']=='COMPATIBLE_IN_HYPOTHETICAL_WORLD' for r in rows),unit_contradicted=sum(r['status']=='CONTRADICTED_IN_HYPOTHETICAL_WORLD' for r in rows),full_parent_compatible=sum(r['full_parent_compatible'] for r in rows),full_projection_classes=len(full),water_projection_classes=len(water),confirmed_words=0,independent_meaning_capacity=0,decision='Retain complete qualitative clock hypothesis conditional on fitted meanings/references. Water motion does not alone entail index or month completion. Equal duration is not compatible with full retained parent source; alternate reader remains unbound. Seek fixed-value complete-content extension, not more unchanged hypothetical worlds.')
write(A/'RESULT.json',result);print(json.dumps({k:result[k] for k in ['status','world_rows','unit_compatible','unit_contradicted','full_parent_compatible','confirmed_words']}))
