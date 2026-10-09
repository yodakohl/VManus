#!/usr/bin/env python3
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
import hashlib,json,re
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
CONTRACT='research_registry/proposals/production_origin_supply_20261003/HAND_WRITER_LEMMA_BUNDLE_CONTRACT_20261006.json'
def wire(x):return json.dumps(x,ensure_ascii=False,separators=(',',':'))
def digest(x):return hashlib.sha256(wire(x).encode()).hexdigest()
def save(n,x):(A/(n+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def fields(raw):
 if raw=='_':return None
 pairs=[x.split('=',1) for x in raw.split('|')]
 assert all(len(x)==2 and x[0] and x[1] for x in pairs)
 assert len({x[0] for x in pairs})==len(pairs)
 return sorted(pairs)
def atom(c):
 assert len(c)==10
 if c[3]=='PUNCT':return ['P',c[1]]
 misc=dict(fields(c[9]) or [])
 return ['W',c[2],c[3],fields(c[5]),misc.get('TraditionalMood'),misc.get('TraditionalTense'),c[1] if c[2]=='_' else None]
def sentences(path):
 ident=None;rows=[]
 for line in path.read_text().splitlines():
  if not line:
   if ident is not None:yield ident,rows
   ident=None;rows=[]
  elif line.startswith('# sent_id = '):
   assert ident is None
   ident=line.split(' = ',1)[1]
  elif not line.startswith('#'):
   c=line.split('\t')
   if c[0].isdigit():rows.append(c)
 if ident is not None:yield ident,rows

def groups(atoms):
 result=[];leading=[]
 for a in atoms:
  if a[0]=='P':
   if result:result[-1].append(a)
   else:leading.append(a)
  else:result.append(leading+[a]);leading=[]
 if leading:result.append(leading)
 return result

def main():
 started=datetime.now(timezone.utc).isoformat();lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 contract=json.loads((ROOT/CONTRACT).read_text()); target=json.loads((ROOT/contract['screen']['target']).read_text())['targets']
 examples={e['id']:e for e in contract['manual_observations']};observed={}
 books={b:dict(sentences=0,source_tokens=0,lexical_tokens=0,groups=0,unknown_lemma_tokens=0,analysis_stream_sha256=hashlib.sha256(),group_stream_sha256=hashlib.sha256()) for b in contract['scope']}
 samples={b:[] for b in books};ids={b:[] for b in books};lemmas={b:set() for b in books};analyses={b:set() for b in books};f_to_a={b:defaultdict(set) for b in books};a_to_f={b:defaultdict(set) for b in books}
 for ident,rows in sentences(ROOT/contract['source']):
  n=int(re.fullmatch('train-s([0-9]+)',ident)[1]);book=next((b for b,(lo,hi) in contract['scope'].items() if lo<=n<=hi),None)
  if not book and not any(k.startswith(ident+':') for k in examples):continue
  assert [int(c[0]) for c in rows]==list(range(1,len(rows)+1)),ident
  aa=[atom(c) for c in rows]
  for c,a in zip(rows,aa):
   key=ident+':'+c[0]
   if key in examples:
    e=examples[key]
    assert c[1]==e['form'] and a==['W',e['lemma'],e['upos'],fields(e['feats']),e['traditional_mood'],e['traditional_tense'],None]
    observed[key]=a
  if not book:continue
  gg=groups(aa);assert [a for g in gg for a in g]==aa
  for g in gg:assert sum(a[0]=='W' for a in g) in (0,1)
  ids[book].append(n);v=books[book];v['sentences']+=1;v['source_tokens']+=len(rows);v['groups']+=len(gg)
  v['analysis_stream_sha256'].update((digest([ident,aa])+'\n').encode());v['group_stream_sha256'].update((digest([ident,gg])+'\n').encode())
  for c,a in zip(rows,aa):
   if a[0]=='W':
    v['lexical_tokens']+=1;v['unknown_lemma_tokens']+=int(c[2]=='_');lemmas[book].add((a[1],a[2]));key=wire(a);analyses[book].add(key);f_to_a[book][c[1]].add(key);a_to_f[book][key].add(c[1])
  samples[book].extend(gg[:max(0,8000-len(samples[book]))])
 assert set(observed)==set(examples)
 result={'experiment':'GDT1222','books':{},'manual_observations':observed,'comparisons':[],'all_projected_sentence_roundtrips':True,'original_FORM_roundtrip_claimed':False}
 for b,v in books.items():
  lo,hi=contract['scope'][b];assert ids[b]==list(range(lo,hi+1)),b;assert len(samples[b])==8000
  cc=Counter(map(wire,samples[b]));t10=sum(sorted(cc.values(),reverse=True)[:10]);types=len(cc)
  out={k:(x.hexdigest() if k.endswith('sha256') else x) for k,x in v.items()}
  out.update(sample_groups=8000,sample_sha256=digest(samples[b]),types=types,top10_count=t10,type_ratio=types/8000,top10_share=t10/8000,lemma_upos_types=len(lemmas[b]),analysis_types=len(analyses[b]),form_types=len(f_to_a[b]),forms_with_multiple_analyses=sum(len(x)>1 for x in f_to_a[b].values()),analyses_with_multiple_forms=sum(len(x)>1 for x in a_to_f[b].values()),max_analyses_per_form=max(map(len,f_to_a[b].values()),default=0),max_forms_per_analysis=max(map(len,a_to_f[b].values()),default=0))
  result['books'][b]=out
  for ed,t in target.items():
   for name,value,ref in [('types',types,t['types']),('top10_count',t10,round(t['top10_share']*8000))]:
    result['comparisons'].append(dict(book=b,reader=ed,metric=name,value=value,target=ref,difference=abs(value-ref),within=abs(value-ref)<=400))
 result['all_necessary_conditions']=all(x['within'] for x in result['comparisons'])
 result['status']='LEMMA_INFLECTION_FREQUENCY_COMPATIBLE' if result['all_necessary_conditions'] else 'LEMMA_INFLECTION_FREQUENCY_FAIL'
 result['claim_ceiling']='Projected historical-source analysis and necessary common-injective-word frequencies only. No physical writer, full meaning/FORM inverse, native value, language identification or independent confirmation.'
 save('RESULT',result);save('RUN_RECEIPT',dict(started_utc=started,finished_utc=datetime.now(timezone.utc).isoformat(),registration_lock_sha256=hashlib.sha256((A/'REGISTRATION_LOCK.json').read_bytes()).hexdigest()))
 print(json.dumps({'status':result['status'],'books':result['books'],'failed_conditions':sum(not x['within'] for x in result['comparisons'])},indent=2))
if __name__=='__main__':main()
