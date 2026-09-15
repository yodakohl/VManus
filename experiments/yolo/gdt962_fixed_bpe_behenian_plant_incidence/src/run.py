#!/usr/bin/env python3
"""Fixed-parser necessary plant-incidence test; no key/merge training."""
from pathlib import Path
from collections import Counter,defaultdict
import csv,gzip,hashlib,io,json,re
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def zipped(name,x): (A/name).write_bytes(gzip.compress((json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
def table(name,rows,fields=None):
 s=io.StringIO();w=csv.DictWriter(s,fields or list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
 data=s.getvalue().encode();(A/name).write_bytes(gzip.compress(data,mtime=0) if name.endswith('.gz') else data)
def rows(mask):return ','.join(str(i+1) for i in range(15) if mask>>i&1)
def parse(raw,spec,rules):
 for a,b in spec['collapse']:raw=raw.replace(a,b)
 units=list(raw);nodes=set(units)
 for rule in rules:
  out=[];i=0
  while i<len(units):
   if i+1<len(units) and units[i]==rule['left'] and units[i+1]==rule['right']:
    out.append(rule['merged']);nodes.add(rule['merged']);i+=2
   else:out.append(units[i]);i+=1
  units=out
 return units,sorted(nodes)
def chunks(paragraph,spec):
 current=[]
 for g in paragraph['groups']:
  if current and (g['locus']!=current[-1]['locus'] or g['left_separator']!=spec['join_boundary']):
   yield current;current=[]
  if current:assert current[-1]['right_separator']==g['left_separator']
  current.append(g)
 if current:yield current

def matching(domains):
 owner={}
 def visit(p,seen):
  for u in domains[p]:
   if u in seen:continue
   seen.add(u)
   if u not in owner or visit(owner[u],seen):owner[u]=p;return True
  return False
 for p in sorted(domains):visit(p,set())
 assigned={p:u for u,p in owner.items()};unmatched=sorted(set(domains)-set(assigned))
 S=set(unmatched);T=set();queue=list(unmatched)
 while queue:
  p=queue.pop()
  for u in domains[p]:
   if u in T:continue
   T.add(u)
   if u in owner and owner[u] not in S:S.add(owner[u]);queue.append(owner[u])
 assert not unmatched or len(S)>len(T)
 return {'size':len(assigned),'witness':dict(sorted(assigned.items())),'unmatched_plants':unmatched,'hall_plants':sorted(S),'hall_units':sorted(T),'deficiency':len(domains)-len(assigned)}

def main():
 for path,h in read(E/'PREREG_LOCK.json').items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h,path
 spec=read(E/'src/SPEC.json');wins=json.load(gzip.open(R/spec['windows'],'rt'));assert len(wins)==22
 inventory=sorted(r['unit'] for r in csv.DictReader((R/spec['inventory']).open(),delimiter='\t'));assert len(inventory)==len(set(inventory))==98
 rules=list(csv.DictReader((R/spec['merges']).open(),delimiter='\t'));assert len(rules)==64 and [int(r['rank']) for r in rules]==list(range(1,65))
 pred=list(csv.DictReader((A/'PREDICTIONS.tsv').open(),delimiter='\t'));assert len(pred)==5808
 inventories={};unknown={};chunk_rows=[];changed=[];mask_rows=[];classes=[]
 for w in wins:
  assert w['page']!='f116v' and not w['page'].startswith('f84')
  masks={rep:{u:0 for u in inventory} for rep in spec['representations']};unk=[0]*15
  for pi,p in enumerate(w['paragraphs']):
   for ci,gs in enumerate(chunks(p,spec)):
    reasons=[]
    if any(not re.fullmatch('[a-z]+',g['ivtff_group_raw']) for g in gs):reasons.append('NONLITERAL')
    if gs[0]['left_separator'] not in spec['allowed_outer_boundaries'] or gs[-1]['right_separator'] not in spec['allowed_outer_boundaries']:reasons.append('UNRESOLVED_OUTER_BOUNDARY')
    raw=''.join(g['ivtff_group_raw'] for g in gs);final=[];nodes=[]
    if not reasons:
     final,nodes=parse(raw,spec,rules)
     # The fixed inventory is a closed hypothesis, not a newly learned alphabet.
     for rep,us in [('FINAL_UNITS',final),('ALL_TREE_NODES',nodes)]:
      for u in set(us)&set(inventory):masks[rep][u]|=1<<pi
    else:unk[pi]+=1
    entry={'window_id':w['window_id'],'edition':w['edition'],'page':w['page'],'paragraph_id':p['id'],'relative_paragraph':pi+1,'chunk_index':ci,'locus':gs[0]['locus'],'groups':[{'source_group_id':g['source_group_id'],'raw':g['ivtff_group_raw'],'left_separator':g['left_separator'],'right_separator':g['right_separator'],'known_in_gdt960':g['known']} for g in gs],'raw_joined':raw,'known':not reasons,'unknown_reasons':reasons,'final_units':final,'tree_nodes':nodes,'parsed_units_outside_inventory':sorted((set(final)|set(nodes))-set(inventory))}
    chunk_rows.append(entry)
    for g in gs:
     if bool(g['known'])!=(not reasons):changed.append({'window_id':w['window_id'],'relative_paragraph':pi+1,'locus':g['locus'],'source_group_id':g['source_group_id'],'raw':g['ivtff_group_raw'],'known_gdt960':g['known'],'known_gdt962':not reasons,'chunk_raw':raw,'left_separator':g['left_separator'],'right_separator':g['right_separator']})
  unknown[w['window_id']]=unk
  for rep,ms in masks.items():
   inventories[w['window_id'],rep]=ms;eq=defaultdict(list)
   for u,m in ms.items():
    mask_rows.append({'window_id':w['window_id'],'representation':rep,'unit':u,'mask':m,'observed_rows':rows(m)});eq[m].append(u)
   for mask,us in sorted(eq.items()):classes.append({'window_id':w['window_id'],'representation':rep,'mask':mask,'units':us})
 domains=[];by=defaultdict(list)
 for p in pred:
  ms=inventories[p['window_id'],p['representation']];req=int(p['required_mask']);unknown_mask=sum(1<<i for i,n in enumerate(unknown[p['window_id']]) if n)
  lower=[u for u,m in ms.items() if m==req]
  upper=[{'unit':u,'known_mask':m,'missing_mask':req&~m} for u,m in ms.items() if not(m&~req) and not((req&~m)&~unknown_mask)]
  d=dict(p,known_mask_units=lower,upper_units=upper,unknown_mask=unknown_mask,status='KNOWN_MASK_MATCH' if lower else 'UNKNOWN_ONLY' if upper else 'CONTRADICTED');domains.append(d);by[p['case_id']].append(d)
 cases=[]
 for cid,ds in by.items():
  lo=matching({d['plant']:d['known_mask_units'] for d in ds});hi=matching({d['plant']:[x['unit'] for x in d['upper_units']] for d in ds})
  status='KNOWN_NECESSARY_MATCHING' if not lo['deficiency'] else 'UPPER_NECESSARY_MATCHING' if not hi['deficiency'] else 'CONTRADICTED'
  cases.append({k:ds[0][k] for k in ['case_id','window_id','edition','page','physical_leaf','model','direction','representation']}|{'source_names':len(ds),'known_matching':lo,'upper_matching':hi,'plants_without_known_units':[d['plant'] for d in ds if not d['known_mask_units']],'plants_without_upper_units':[d['plant'] for d in ds if not d['upper_units']],'unknown_chunks':unknown[ds[0]['window_id']],'status':status,'complete_unknown_realization_assessed':False,'independent_confirmation_leaves':0})
 flat=[]
 for c in cases:
  flat.append({k:c[k] for k in ['case_id','edition','page','model','direction','representation','source_names','status']}|{'known_matching_size':c['known_matching']['size'],'upper_matching_size':c['upper_matching']['size'],'known_deficiency':c['known_matching']['deficiency'],'upper_deficiency':c['upper_matching']['deficiency'],'plants_without_known_units':' | '.join(c['plants_without_known_units']),'plants_without_upper_units':' | '.join(c['plants_without_upper_units']),'independent_confirmation_leaves':0})
 mugs=[d for d in domains if d['plant']=='Mugwort'];mugrows=[]
 for d in mugs:
  best=max([x['known_mask'].bit_count() for x in d['upper_units']] or [0])
  mugrows.append({k:d[k] for k in ['case_id','edition','page','direction','representation','required_rows','status']}|{'known_mask_units':' | '.join(d['known_mask_units']),'upper_units':' | '.join(x['unit'] for x in d['upper_units']),'maximum_known_required_rows':best,'unknown_rows_required_at_least':int(d['required_mask']).bit_count()-best if d['upper_units'] else 'NO_COMPLETION'})
 table('UNIT_MASKS.tsv.gz',mask_rows);zipped('PARSED_CHUNKS.json.gz',chunk_rows);zipped('IDENTICAL_UNIT_PREDICTIONS.json.gz',classes);zipped('PLANT_DOMAINS.json.gz',domains);zipped('ALL_CASES.json.gz',cases);table('CANDIDATE_TABLE.tsv',flat);table('MUGWORT_ALL_CASES.tsv',mugrows)
 table('CHANGED_KNOWNNESS.tsv.gz',changed,fields=['window_id','relative_paragraph','locus','source_group_id','raw','known_gdt960','known_gdt962','chunk_raw','left_separator','right_separator'])
 result={'experiment_id':'GDT962','status':'COMPLETE_FIXED_BPE_NECESSARY_INCIDENCE_TEST','windows':len(wins),'representations':spec['representations'],'fixed_units':len(inventory),'chunk_window_rows':len(chunk_rows),'known_chunk_window_rows':sum(c['known'] for c in chunk_rows),'changed_knownness_rows':len(changed),'unit_window_representation_masks':len(mask_rows),'identical_prediction_classes':len(classes),'plant_predictions':len(domains),'cases':len(cases),'case_outcomes':dict(Counter(c['status'] for c in cases)),'by_representation':{rep:dict(Counter(c['status'] for c in cases if c['representation']==rep)) for rep in spec['representations']},'plant_outcomes':dict(Counter(d['status'] for d in domains)),'mugwort_outcomes':dict(Counter(d['status'] for d in mugs)),'mugwort_known_units':sorted({u for d in mugs for u in d['known_mask_units']}),'confirmed_words':0,'independent_confirmation_leaves':0,'complete_unknown_realization_assessed':False,'significance':'NOT_ASSESSED_POST_EXPOSURE_EXPLORATION'}
 (A/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
