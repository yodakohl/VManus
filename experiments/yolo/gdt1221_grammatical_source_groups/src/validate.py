#!/usr/bin/env python3
# Independent implementation: connected components and boundary splitting.
from pathlib import Path
from collections import Counter
import hashlib,json,re
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
C='research_registry/proposals/production_origin_supply_20261003/HAND_WRITER_GRAMMATICAL_GROUP_CONTRACT_20261006.json'
def sha(x):return hashlib.sha256(json.dumps(x,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def construct(rows,allowed):
 # rows: index, FORM, UPOS, head, base-relation
 ids=[r[0] for r in rows];assert ids==list(range(1,len(rows)+1))
 parent={r[0]:r[3] for r in rows};punct={r[0] for r in rows if r[2]=='PUNCT'}
 for node in ids:
  path=[]
  while node:
   assert node in parent and node not in path
   path.append(node);node=parent[node]
 comp={i:i for i in ids}
 def find(i):
  while comp[i]!=i:i=comp[i]
  return i
 for i,form,pos,head,rel in rows:
  if pos!='PUNCT' and head and head not in punct and rel in allowed:comp[find(i)]=find(head)
 # Boundaries go immediately before each nonpunctuation token unless it
 # directly follows a nonpunctuation member of the same component.
 cuts=[0]
 for j in range(1,len(rows)):
  r=rows[j];prev=rows[j-1]
  if r[2]=='PUNCT':continue
  if all(t[2]=='PUNCT' for t in rows[:j]):continue
  if prev[2]=='PUNCT' or find(prev[0])!=find(r[0]):cuts.append(j)
 cuts.append(len(rows))
 out=[[r[1] for r in rows[a:b]] for a,b in zip(cuts,cuts[1:]) if b>a]
 assert sum(out,[])==[r[1] for r in rows]
 return out

def main():
 lock=json.loads((A/'REGISTRATION_LOCK.json').read_text())
 for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
 c=json.loads((ROOT/C).read_text());r=json.loads((A/'RESULT.json').read_text());targets=json.loads((ROOT/c['screen']['target']).read_text())['targets']
 selected={b:[] for b in c['scope']};all_groups={b:[] for b in c['scope']};seen={b:[] for b in c['scope']};totals={b:[0,0] for b in c['scope']};examples={e['sent_id']:e['groups'] for e in c['manual_examples']};example_count=0
 source_digest={b:hashlib.sha256() for b in c['scope']};group_digest={b:hashlib.sha256() for b in c['scope']}
 text=(ROOT/c['source']).read_text()
 for block in re.split(r'\n\s*\n',text.strip()):
  match=re.search(r'^# sent_id = (train-s(\d+))$',block,re.M);assert match
  ident=match[1];n=int(match[2]);book=next((b for b,span in c['scope'].items() if span[0]<=n<=span[1]),None)
  if not book and ident not in examples:continue
  rows=[]
  for line in block.splitlines():
   if re.match(r'^\d+\t',line):
    col=line.split('\t');assert len(col)==10
    rows.append((int(col[0]),col[1],col[3],int(col[6]),col[7].partition(':')[0]))
  out=construct(rows,set(c['bound_relations']))
  if ident in examples:assert out==examples[ident];example_count+=1
  if book:
   seen[book].append(n);totals[book][0]+=len(rows);totals[book][1]+=len(out)
   source_digest[book].update((sha([ident,[x[1] for x in rows]])+'\n').encode());group_digest[book].update((sha([ident,out])+'\n').encode())
   selected[book]+=out[:max(0,8000-len(selected[book]))]
 assert example_count==3
 comparison=[]
 for b,(lo,hi) in c['scope'].items():
  assert seen[b]==list(range(lo,hi+1));assert len(selected[b])==8000
  values=Counter(map(tuple,selected[b]));top=sum(sorted(values.values())[-10:]);got=r['books'][b]
  expected=dict(sentences=len(seen[b]),source_tokens=totals[b][0],groups=totals[b][1],source_sha256=source_digest[b].hexdigest(),groups_sha256=group_digest[b].hexdigest(),types=len(values),top10_count=top,type_ratio=len(values)/8000,top10_share=top/8000,sample_sha256=sha(selected[b]))
  assert got==expected,(b,got,expected)
  for ed,t in targets.items():
   for metric,value,ref in [('types',len(values),t['types']),('top10_count',top,round(8000*t['top10_share']))]:
    comparison.append(dict(book=b,reader=ed,metric=metric,source=value,target=ref,absolute_difference=abs(value-ref),within=abs(value-ref)<=400))
 assert r['comparison']==comparison and len(comparison)==18
 passed=all(x['within'] for x in comparison);assert r['all_necessary_conditions']==passed
 assert r['status']==('GRAMMATICAL_GROUP_FREQUENCY_COMPATIBLE' if passed else 'GRAMMATICAL_GROUP_FREQUENCY_FAIL')
 # Leading punctuation, hard punctuation cut, recursive dependency and
 # all-punctuation examples are fixed parser obligations, not target data.
 fixtures=[
 ([(1,'(', 'PUNCT',2,'punct'),(2,'a','NOUN',0,'root'),(3,',','PUNCT',2,'punct'),(4,'b','ADJ',2,'amod'),(5,'.','PUNCT',2,'punct')],[['(','a',','],['b','.']]),
 ([(1,'x','DET',2,'det'),(2,'y','ADJ',3,'amod'),(3,'z','NOUN',0,'root')],[['x','y','z']]),
 ([(1,'!','PUNCT',0,'root'),(2,'?','PUNCT',1,'punct')],[['!','?']])]
 for rows,want in fixtures:assert construct(rows,set(c['bound_relations']))==want
 validation=dict(status='PASS',experiment='GDT1221',source_sentences=sum(len(x) for x in seen.values()),source_tokens=sum(x[0] for x in totals.values()),manual_examples=3,edge_fixtures=3,conditions=18,roundtrip='All full scoped FORM sequences retained and independently reconstructed',implementation='Separate union-find components and run boundaries; no runner import. Same author, not blinded.',native_meanings=0)
 (A/'VALIDATION.json').write_text(json.dumps(validation,indent=2)+'\n');print(json.dumps(validation,indent=2))
if __name__=='__main__':main()
