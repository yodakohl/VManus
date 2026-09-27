#!/usr/bin/env python3
"""Literal/hash/inventory audit only; no semantic executor or meaning validation."""
import csv, hashlib, json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
B=Path(__file__).resolve().parent
R=B.parents[2]
F=B/'PLANET_MOTION_AUTHOR_FIRST_FREEZE_RECEIPT.json'
receipt=json.loads(F.read_text()); d=json.loads((B/'PLANET_MOTION_AUTHOR_FIRST.json').read_text())
checks=[]
def check(name,ok,detail=None):
 checks.append({'check':name,'pass':bool(ok),**({'detail':detail} if not ok else {})})
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
inputs={str(F.relative_to(R)):sha(F)}
for f in receipt['files']:
 p=R/f['path']; inputs[f['path']]=sha(p)
 check('freeze hash '+f['path'],sha(p)==f['sha256']);check('freeze size '+f['path'],p.stat().st_size==f['bytes'])
p=R/d['scope']['file'];inputs[d['scope']['file']]=sha(p);check('native hash',sha(p)==d['scope']['sha256'])
native=list(csv.DictReader(p.open(),delimiter='\t')); out=list(csv.DictReader((B/'PLANET_MOTION_AUTHOR_FIRST_473_CONSEQUENCES.tsv').open(),delimiter='\t'))
fields=d['scope']['original_fields'];check('473 original rows',len(native)==len(out)==473)
for i,(a,b) in enumerate(zip(native,out)):
 check('original twelve tuple '+str(i),[a[k] for k in fields]==[b[k] for k in fields])
lex=d['lexicon']; pieces=[x['literal'] for x in d['components']]; prefixes={x['literal']:x['value'] for x in d['components'] if x['type']=='NumberPrefix'};suffixes={x['literal']:x['value'] for x in d['components'] if x['type']=='UnitSuffix'}
product={a+b:{'cut':[a,b],'value':{'quantity':[av,bv]}} for a,av in prefixes.items() for b,bv in suffixes.items()}
check('Cartesian exact four forms',product==d['derived_wholes'])
occ=defaultdict(list);byid={a['source_group_id']:a for a in native};lines=defaultdict(list)
for a in native:occ[a['ivtff_group_raw']].append(a['source_group_id']);lines[(a['edition'],a['locus'])].append(a)
for line in lines.values():line.sort(key=lambda a:int(a['source_group_index']))
for a,b in zip(native,out):
 raw=a['ivtff_group_raw']; e=lex.get(raw);id=a['source_group_id']
 check('assignment '+id,b['first_status']==(e['status'] if e else 'unknown') and b['fixed_type']==(e['type'] if e else 'UNKNOWN'))
 check('value '+id,(json.loads(b['fixed_value']) if b['fixed_value'] else None)==(e['value'] if e else None))
 check('cut '+id,b['exact_cut']==('+'.join(product[raw]['cut']) if raw in product else ''))
 check('substring inventory '+id,b['candidate_piece_substrings']==','.join(x for x in pieces if x in raw))
 line=lines[(a['edition'],a['locus'])];pos=next(i for i,x in enumerate(line) if x['source_group_id']==id)
 for side,j,bound in [('left',pos-1,'LINE_START'),('right',pos+1,'LINE_END')]:
  neighbor=line[j]['ivtff_group_raw'] if 0<=j<len(line) else bound;typ=lex.get(neighbor,{}).get('type','UNKNOWN') if 0<=j<len(line) else 'BOUNDARY'
  check(side+' neighbor '+id,b[side+'_raw']==neighbor and b[side+'_type']==typ)
check('all assigned literal occurrence lists',dict(d['all_assigned_occurrences'])=={k:occ[k] for k in lex})
residual={raw:{'raw':raw,'status':lex.get(raw,{}).get('status','unknown'),'source_group_ids':ids,'not_claimed_morphological_segmentation':True} for raw,ids in occ.items() if raw not in product and any(x in raw for x in pieces)}
check('all non-G01 substring residuals',{x['raw']:x for x in d['non_G01_forms_with_literal_piece_substrings']}==residual)
readers={ed:{'rows':sum(a['edition']==ed for a in native),'assigned':sum(a['edition']==ed and a['ivtff_group_raw'] in lex for a in native),'G01_occurrences':sum(a['edition']==ed and a['ivtff_group_raw'] in product for a in native)} for ed in ['ZL3b','IT2a','RF1b']}
counts={'derived_types':len(product),'derived_occurrences':sum(len(occ[k]) for k in product),'derived_per_reader':{k:v['G01_occurrences'] for k,v in readers.items()},'assigned_whole_types':len(lex),'assigned_rows':sum(v['assigned'] for v in readers.values()),'assigned_by_reader':{k:v['assigned'] for k,v in readers.items()},'unknown_rows':sum(a['ivtff_group_raw'] not in lex for a in native)}
for k,v in counts.items():check('recomputed count '+k,v==d['counts'][k])
clauses=[];consumed=set()
for c in d['clauses']:
 check('ZL literal span '+c['id'],[byid[i]['ivtff_group_raw'] for i in c['zl_source_ids']]==c['raw'])
 for ed in readers:
  ids=[ed+'|'+i.split('|',1)[1] for i in c['zl_source_ids']];actual=[byid.get(i,{}).get('ivtff_group_raw') for i in ids];matches=actual==c['raw']
  missing=[{'id':i,'actual':raw,'expected':expected,'actual_fixed_type':lex.get(raw,{}).get('type','UNKNOWN')} for i,raw,expected in zip(ids,actual,c['raw']) if raw!=expected]
  clauses.append({'clause':c['id'],'edition':ed,'ids':ids,'raw':actual,'exact_template_eligible':matches,'differences':missing})
  check('clause declared literal eligibility '+c['id']+' '+ed,matches==c['variants'][ed].startswith('computed'))
  if matches:consumed.update(i for i,raw in zip(ids,actual) if raw in product)
# Independently enumerate finite type-pattern opportunities, without constructing semantic values.
patterns=[]
for (ed,locus),line in lines.items():
 types=[lex.get(a['ivtff_group_raw'],{}).get('type','UNKNOWN') for a in line]
 q=[(i,i+1,'G01') for i,a in enumerate(line) if a['ivtff_group_raw'] in product]
 q += [(i,i+2,'G03') for i in range(len(line)-1) if types[i:i+2]==['Number','Unit']]
 base=q[:]
 for a,b,ra in base:
  for c,e,rb in base:
   if c==b+1 and b<len(line) and line[b]['ivtff_group_raw']=='qotaiin':q.append((a,e,'G04'))
 for a,b,rule in q:
  if a>0 and b<len(line) and types[a-1]=='Planet' and types[b]=='PeriodRole':patterns.append({'edition':ed,'locus':locus,'rule':'G05','quantity_rule':rule,'ids':[x['source_group_id'] for x in line[a-1:b+1]]})
  if b+1<len(line) and types[b:b+2]==['Planet','PeriodRole']:patterns.append({'edition':ed,'locus':locus,'rule':'G06','quantity_rule':rule,'ids':[x['source_group_id'] for x in line[a:b+2]]})
remaining=[{'raw':k,'ids':[i for i in occ[k] if i not in consumed]} for k in product]
result={'kind':'LITERAL_HASH_AND_FINITE_INVENTORY_ONLY','created_utc':datetime.now(timezone.utc).isoformat(),'status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','checks':len(checks),'failures':[c for c in checks if not c['pass']],'input_hashes':inputs,'original_tuple_fields':fields,'readers':readers,'counts':counts,'product':product,'all_G01_occurrences':{k:occ[k] for k in product},'non_G01_residual_type_count':len(residual),'non_G01_residual_row_count':sum(len(x['source_group_ids']) for x in residual.values()),'non_G01_residual_inventory':list(residual.values()),'literal_clauses':clauses,'eligible_G01_occurrences_consumed_by_three_templates':sorted(consumed),'unconsumed_G01_occurrences':remaining,'finite_type_pattern_opportunities':patterns,'limits':['No semantic executor, historical meaning validation, grammar repair, source correction or whole-content PASS.','G01 exact-full-group eligibility differs from a complete named-planet assertion.','Finite type-pattern enumeration permits G03 pairs and one G04 sum; it does not certify an exhaustive general grammar.','The three readings are alternatives of one manuscript, not independent evidence.','All prior project and authorized target exposure retained; no blinding claim.','No root/B review, new target image, mixed raw table, reserve, or new source accessed.']}
print(json.dumps(result,ensure_ascii=False,indent=2))
