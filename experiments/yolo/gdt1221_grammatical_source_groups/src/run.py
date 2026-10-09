#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import hashlib,json,re
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
CONTRACT='research_registry/proposals/production_origin_supply_20261003/HAND_WRITER_GRAMMATICAL_GROUP_CONTRACT_20261006.json'
def digest(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def save(n,x):(A/(n+'.json')).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def sentences(path):
 ident=None;rows=[]
 with path.open() as f:
  for line in f:
   line=line.rstrip('\n')
   if not line:
    if ident is not None:yield ident,rows
    ident=None;rows=[]
   elif line.startswith('# sent_id = '):ident=line.split(' = ',1)[1]
   elif not line.startswith('#'):
    col=line.split('\t')
    if col[0].isdigit():
     assert len(col)==10
     rows.append(dict(id=int(col[0]),form=col[1],punct=col[3]=='PUNCT',head=int(col[6]),rel=col[7].split(':')[0]))
 if ident is not None:yield ident,rows

def partition(rows,eligible):
 nodes={r['id']:r for r in rows};assert len(nodes)==len(rows)
 assert list(nodes)==list(range(1,len(rows)+1))
 for r in rows:
  assert r['head']==0 or r['head'] in nodes
  seen=set();i=r['id']
  while i:
   assert i not in seen,'cyclic annotation'
   seen.add(i);i=nodes[i]['head']
 def anchor(i):
  while nodes[i]['head'] and nodes[i]['rel'] in eligible:
   parent=nodes[i]['head']
   if nodes[parent]['punct']:break
   i=parent
  return i
 groups=[];leading=[];current=None
 for r in rows:
  if r['punct']:
   if groups:groups[-1].append(r['form'])
   else:leading.append(r['form'])
   current=None
  else:
   a=anchor(r['id'])
   if current==a:groups[-1].append(r['form'])
   else:groups.append(leading+[r['form']]);leading=[]
   current=a
 if leading:groups.append(leading)
 assert [x for g in groups for x in g]==[r['form'] for r in rows]
 return groups

def main():
 start=datetime.now(timezone.utc).isoformat();lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 c=json.loads((ROOT/CONTRACT).read_text());eligible=set(c['bound_relations']);assert len(eligible)==14
 target=json.loads((ROOT/c['screen']['target']).read_text())['targets']
 samples={b:[] for b in c['scope']};ids={b:[] for b in c['scope']};books={b:dict(sentences=0,source_tokens=0,groups=0,source_sha256=hashlib.sha256(),groups_sha256=hashlib.sha256()) for b in c['scope']}
 examples={e['sent_id']:e['groups'] for e in c['manual_examples']};seen_examples=set()
 for ident,rows in sentences(ROOT/c['source']):
  match=re.fullmatch(r'train-s(\d+)',ident);assert match,ident
  n=int(match[1]);book=next((b for b,(lo,hi) in c['scope'].items() if lo<=n<=hi),None)
  if ident in examples:
   assert partition(rows,eligible)==examples[ident],ident;seen_examples.add(ident)
  if not book:continue
  groups=partition(rows,eligible);v=books[book];forms=[r['form'] for r in rows]
  ids[book].append(n);v['sentences']+=1;v['source_tokens']+=len(forms);v['groups']+=len(groups)
  v['source_sha256'].update((digest([ident,forms])+'\n').encode());v['groups_sha256'].update((digest([ident,groups])+'\n').encode())
  samples[book].extend(tuple(g) for g in groups[:max(0,8000-len(samples[book]))])
 assert seen_examples==set(examples)
 result={'experiment':'GDT1221','manual_examples':len(examples),'books':{},'comparison':[],'source_roundtrip':True}
 for b,v in books.items():
  lo,hi=c['scope'][b];assert ids[b]==list(range(lo,hi+1)),b;assert len(samples[b])==8000,b
  counts=Counter(samples[b]);top=sum(sorted(counts.values(),reverse=True)[:10])
  out={k:(x.hexdigest() if k.endswith('sha256') else x) for k,x in v.items()}
  out.update(types=len(counts),top10_count=top,type_ratio=len(counts)/8000,top10_share=top/8000,sample_sha256=digest(samples[b]))
  result['books'][b]=out
  for ed,t in target.items():
   for m,val,ref in [('types',len(counts),t['types']),('top10_count',top,round(t['top10_share']*8000))]:
    result['comparison'].append(dict(book=b,reader=ed,metric=m,source=val,target=ref,absolute_difference=abs(val-ref),within=abs(val-ref)<=400))
 result['all_necessary_conditions']=all(x['within'] for x in result['comparison'])
 result['status']='GRAMMATICAL_GROUP_FREQUENCY_COMPATIBLE' if result['all_necessary_conditions'] else 'GRAMMATICAL_GROUP_FREQUENCY_FAIL'
 result['claim_ceiling']='Necessary source-control tuple frequencies only; no physical glyph writer, native grammar/meaning, language identification or independent confirmation.'
 save('RESULT',result);save('RUN_RECEIPT',dict(started_utc=start,finished_utc=datetime.now(timezone.utc).isoformat(),registration_lock_sha256=hashlib.sha256((A/'REGISTRATION_LOCK.json').read_bytes()).hexdigest()))
 print(json.dumps({'status':result['status'],'books':result['books'],'failed_conditions':sum(not x['within'] for x in result['comparison'])},indent=2))
if __name__=='__main__':main()
