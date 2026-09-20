import datetime, hashlib, json, time
from pathlib import Path
import z3
E=Path(__file__).resolve().parents[1]; R=E.parents[2]; A=E/'artifacts'
FIXED={'ol':2,'or':7,'qol':1,'sheedy':1}
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def verify_lock():
 for n,h in json.loads((E/'PREREG_LOCK.json').read_text())['files'].items():
  assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n

def solve(words,start,query=None):
 s=z3.Solver();s.set(timeout=10000)
 forms=sorted(set(words)); f={w:[z3.Int(f'w{k}_{i}') for i in range(2)] for k,w in enumerate(forms)}
 states=[z3.Int(f's{i}') for i in range(len(words)+1)]
 for x in states:s.add(x>=0,x<=1)
 s.add(states[0]==start)
 for w,pair in f.items():
  for x in pair:s.add(x>=0,x<=2)
  if w in FIXED:s.add(pair[0]==FIXED[w]//3,pair[1]==FIXED[w]%3)
 for i,w in enumerate(words):s.add(states[i+1]==z3.If(states[i]==0,f[w][0],f[w][1]))
 if query:
  if query['kind']=='word':
   s.add(f[query['word']][0]==query['code']//3,f[query['word']][1]==query['code']%3)
  elif query['kind']=='final':s.add(states[-1]==query['state'])
 result=s.check()
 if result==z3.unsat:return {'status':'UNSAT'}
 if result==z3.unknown:return {'status':'UNKNOWN','reason':s.reason_unknown()}
 m=s.model()
 return {'status':'SAT','witness':{'dictionary':{w:[m.eval(x).as_long() for x in pair] for w,pair in f.items()},'states':[m.eval(x).as_long() for x in states]}}

def get_sources():
 raw={ed:[] for ed in ['ZL3b','IT2a','RF1b']}
 for ed in raw:
  for split in ['DISCOVERY','EVALUATION']:
   d=json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{split}_{ed}.json').read_text())
   for line in d['lines']:
    if line['metadata']['locus'] in [f'f75v.{i}' for i in range(38,43)]:
     raw[ed].append({'metadata':line['metadata'],'groups':[dict(zip(d['group_columns'],x)) for x in line['groups']]})
  raw[ed].sort(key=lambda x:int(x['metadata']['locus'].split('.')[-1]))
 pars=json.loads((R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text())
 chosen={}
 for ed,rows in pars.items():
  found=[p for p in rows if p['id']=='f75v|f75v.38-f75v.42']
  chosen[ed]=found
 return raw,chosen

def main():
 verify_lock();t=time.monotonic(); A.mkdir(exist_ok=True)
 raw,pars=get_sources();dump(A/'SOURCE_PACKET.json',{'raw':raw,'paragraphs':pars})
 previous=json.loads((R/'experiments/yolo/gdt982_reciprocal_flow_clause_readings/artifacts/RESULT.json').read_text())['local_outcomes']
 capacity={}; allqueries=[]; domains=[]; candidates=[]
 for ed in raw:
  pp=pars.get(ed,[])
  continuation=[l for l in pp[0]['lines'] if l['locus'] in ['f75v.40','f75v.41','f75v.42']] if pp else []
  eligible=len(continuation)==3 and all(l['anchor_eligible'] for l in continuation)
  capacity[ed]={'eligible':eligible,'complete_paragraphs':len(pp),'continuation_lines':len(continuation),'ineligible_loci':[l['locus'] for l in continuation if not l['anchor_eligible']],'raw_groups':sum(len(l['groups']) for l in raw[ed])}
  if not eligible:
   for old in previous:candidates.append({'edition':ed,'candidate':old['model'],'status':'NO_CAPACITY','inherited_status':old['status'],'independent_confirmation':0})
   continue
  words=[w for l in continuation for w in l['words']]; forms=sorted(set(words)-FIXED.keys())
  capacity[ed].update(continuation_groups=len(words),unknown_wholes=len(forms))
  by_start={}
  for start in [0,1]:
   questions=[{'kind':'base'}]+[{'kind':'word','word':w,'code':c} for w in forms for c in range(9)]+[{'kind':'final','state':v} for v in [0,1]]
   result=[]
   for q in questions:
    answer=solve(words,start,q) if time.monotonic()-t<120 else {'status':'UNKNOWN','reason':'BATCH_CHECKPOINT'}
    row={'edition':ed,'start':start,'query':q,**answer}; result.append(row);allqueries.append(row)
   by_start[start]=result
   for w in forms:
    domains.append({'edition':ed,'start':start,'word':w,'positions':[i for i,x in enumerate(words) if x==w],'possible_codes':[r['query']['code'] for r in result if r['query'].get('word')==w and r['status']=='SAT'],'unknown_codes':[r['query']['code'] for r in result if r['query'].get('word')==w and r['status']=='UNKNOWN']})
  for old in previous:
   row={'edition':ed,'candidate':old['model'],'inherited_status':old['status'],'independent_confirmation':0}
   if old['status']=='INTERNAL_CONTRADICTION':row['status']='INHERITED_CONTRADICTION'
   elif old['status']=='DESCRIPTIVE_UNSCORED':row['status']='DESCRIPTION_UNSCORED'
   else:
    start={'l':0,'r':1}[old['final']];qs=by_start[start];dom=[d for d in domains if d['edition']==ed and d['start']==start]
    sh=next(d for d in dom if d['word']=='sheolo')
    row.update(status='CONTINUATION_'+qs[0]['status'],initial=start,final_states=[r['query']['state'] for r in qs if r['query']['kind']=='final' and r['status']=='SAT'],sheolo_codes=sh['possible_codes'],sheolo_unknown=sh['unknown_codes'],forced_B_to_A=bool(sh['possible_codes']) and not sh['unknown_codes'] and all(c%3==0 for c in sh['possible_codes']))
   candidates.append(row)
 dump(A/'QUERIES.json',allqueries);dump(A/'WORD_DOMAINS.json',domains);dump(A/'CANDIDATES.json',candidates)
 with (A/'WORD_DOMAINS.tsv').open('w') as f:
  f.write('edition\tstart\tword\tpositions_zero_based\tpossible_codes\tunknown_codes\n')
  for d in domains:f.write('\t'.join(str(d[k]) if k in ['edition','start','word'] else ','.join(map(str,d[k])) for k in ['edition','start','word','positions','possible_codes','unknown_codes'])+'\n')
 result={'status':'CONDITIONAL_ROLE_LEAD' if any(r.get('forced_B_to_A') for r in candidates) else 'NO_FORCED_ROLE','capacity':capacity,'query_counts':{s:sum(q['status']==s for q in allqueries) for s in ['SAT','UNSAT','UNKNOWN']},'candidate_rows':len(candidates),'domain_rows':len(domains),'initial_equivalence_classes':{'A':['NOT_ONCE'],'B':['THEN_ONCE','THEN_REPEAT']},'confirmed_words':0,'independent_confirmation':0,'complete_paragraph_translation':False,'elapsed_seconds':time.monotonic()-t,'z3_version':z3.get_version_string()}
 dump(A/'RESULT.json',result);dump(A/'EXECUTION_RECEIPT.json',{'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'lock_sha256':hashlib.sha256((E/'PREREG_LOCK.json').read_bytes()).hexdigest()});print(json.dumps(result,indent=2))
if __name__=='__main__':main()
