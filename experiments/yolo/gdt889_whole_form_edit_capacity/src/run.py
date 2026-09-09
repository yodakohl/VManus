"""Explicit radius-one balls; deterministic union-find witness forest."""
import hashlib,json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
SOURCE='experiments/yolo/gdt883_overlapping_digram_constraints/artifacts/SELECTED_GROUPS.json'
def canonical(x):return json.dumps(x,sort_keys=True,separators=(',',':'))
def balls(w,alphabet):
 out={w}
 for i in range(len(w)):
  out.add(w[:i]+w[i+1:])
  for a in alphabet:out.add(w[:i]+a+w[i+1:])
 for i in range(len(w)+1):
  for a in alphabet:out.add(w[:i]+a+w[i:])
 return out

def solve(words):
 words=sorted(set(words));alphabet=sorted(set(''.join(words)));parent=list(range(len(words)))
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 owner={};forest=[]
 for i,w in enumerate(words):
  for received in sorted(balls(w,alphabet)):
   if received not in owner:owner[received]=i;continue
   j=owner[received];a,b=find(i),find(j)
   if a!=b:
    parent[max(a,b)]=min(a,b)
    forest.append(dict(left=words[j],right=w,received=received))
 classes={}
 for i,w in enumerate(words):classes.setdefault(find(i),[]).append(w)
 components=sorted(classes.values(),key=lambda c:c[0])
 return dict(alphabet=alphabet,words=words,components=components,max_distinct_messages=len(components),injective_possible=all(len(c)==1 for c in components),forest=forest)

def main():
 for name,digest in json.loads((E/'src/PREREG_LOCK.json').read_text()).items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
 source=ROOT/SOURCE;rows=json.loads(source.read_text());assert len(rows)==1617
 assert all(not r['page'].startswith('f84') and r['raw'].isascii() and r['raw'].isalpha() and r['raw'].islower() for r in rows)
 result=solve([r['raw'] for r in rows]);assert len(result['words'])==749
 result.update(experiment_id='GDT889',source=SOURCE,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),group_count=len(rows),physical_leaves=sorted({re.match(r'f[0-9]+',r['page']).group() for r in rows}))
 (E/'artifacts/RESULT.json').write_text(canonical(result)+'\n')
 print(canonical({k:result[k] for k in ['max_distinct_messages','injective_possible']}));print('component sizes',sorted(map(len,result['components']),reverse=True))
if __name__=='__main__':main()
