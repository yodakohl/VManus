"""Separate integer-map sort/group replay and raw segmentation checks."""
import csv,gzip,hashlib,itertools,json,re
from collections import defaultdict
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
A=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split());INDEX={s:i for i,s in enumerate(A)}
def load(p):return json.loads(p.read_text())
def parse(raw):
 ways=[[] for _ in range(len(raw)+1)];ways[0]=[()]
 for i in range(len(raw)):
  for prefix in ways[i]:
   for s in A:
    if raw.startswith(s,i):ways[i+len(s)].append(prefix+(s,))
 assert len(ways[-1])==1,raw
 return list(ways[-1][0])
def generic_bad(words,mapping):
 groups=defaultdict(set)
 for page,u in words:
  for i,g in enumerate(u):
   k=(page,len(u),i,mapping[u[i-1]] if i else 'BOS',mapping[g],mapping[u[i+1]] if i+1<len(u) else 'EOS');groups[k].add(g)
 return any(len(v)>1 for v in groups.values())
def patterns(n):
 def walk(p):
  if len(p)==n:yield p;return
  for k in range(max(p,default=-1)+2):yield from walk(p+[k])
 yield from walk([])
def main():
 for p,h in load(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));old=json.loads(gzip.decompress((R/'experiments/yolo/gdt1295_local_allograph_letter_bound/artifacts/CONFLICTS.json.gz').read_bytes()));saved=load(B/'artifacts/PAIR_RESULTS.json');result=load(B/'artifacts/RESULT.json')
 allow={row['page'] for row in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};cache={};totalpos=0;checked=0;compatible=0;witnesses=0
 for reader in ['ZL3b','IT2a','RF1b']:
  rows=data[reader];positions=defaultdict(list);literal=defaultdict(set)
  for row in rows:
   assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE'
   raw=row['ivtff_group_raw']
   if raw not in cache:cache[raw]=parse(raw)
   assert cache[raw]==row['units'];u=cache[raw]
   for i,g in enumerate(u):
    left=u[i-1] if i else 'BOS';right=u[i+1] if i+1<len(u) else 'EOS';record=(row['page'],len(u),i,left,g,right,row['id'],raw)
    positions[g].append(record);literal[(row['page'],len(u),i,left,right)].add(g);totalpos+=1
  literal_edges=set()
  for gs in literal.values():literal_edges.update(itertools.combinations(sorted(gs),2))
  assert literal_edges=={tuple(e['units']) for e in old[reader]['edges']}
  pair_results=[]
  for j,(x,y) in enumerate(itertools.combinations(A,2)):
   indexmap=dict(INDEX);indexmap[y]=indexmap[x];indexmap['BOS']=22;indexmap['EOS']=23
   center_positions=positions[x]+positions[y];records=[]
   for rec in center_positions:
    page,n,i,l,g,r,ident,raw=rec;key=(page,n,i,indexmap[l],indexmap[g],indexmap[r]);records.append((key,ident,rec))
   records.sort(key=lambda q:(q[0],q[1]));table=[];conflicts=[]
   def label(v):return '@' if v==INDEX[x] else 'BOS' if v==22 else 'EOS' if v==23 else A[v]
   for key,stream in itertools.groupby(records,key=lambda q:q[0]):
    group=list(stream);written={z[2][4] for z in group};canonical=(key[0],key[1],key[2],label(key[3]),label(key[5]))
    if len(written)>1:
     contexts={}
     for g in [x,y]:
      rec=min((z[2] for z in group if z[2][4]==g),key=lambda q:q[6]);contexts[g]={'id':rec[6],'index':rec[2],'whole':rec[7],'written':g,'left':rec[3],'right':rec[5]}
     conflicts.append((canonical,contexts))
    else:table.append([list(canonical),next(iter(written))])
   conflicts.sort(key=lambda q:q[0]);selectors=sorted({k[0] for k,v in conflicts});leaves=sorted({int(re.match(r'f(\d+)',p).group(1)) for p in selectors});first=None
   if conflicts:
    k,v=conflicts[0];first={'source_context':list(k),'first':v[x],'second':v[y]};witnesses+=1
   table.sort(key=lambda q:q[0]);digest=None if conflicts else hashlib.sha256(json.dumps(table,separators=(',',':')).encode()).hexdigest()
   derived={'units':[x,y],'status':'CONTRADICTED' if conflicts else 'COMPATIBLE_SINGLE_MERGE','old_literal_edge':(x,y) in literal_edges,'positions':len(center_positions),'observed_merged_contexts':len(table)+len(conflicts),'conflicting_contexts':len(conflicts),'selectors':selectors,'physical_leaves':leaves,'first_conflict':first,'nondefault_lookup_entries':None if conflicts else sum(g!=x for k,g in table),'lookup_sha256':digest}
   assert derived==saved[reader][j],(reader,x,y);pair_results.append(derived);checked+=1;compatible+=not conflicts
  failed=[p for p in pair_results if p['status']=='CONTRADICTED'];new=[p for p in failed if not p['old_literal_edge']];good=[p for p in pair_results if p['status']!='CONTRADICTED'];summary={'groups':len(rows),'positions':sum(len(r['units']) for r in rows),'pairs':231,'old_literal_edges':len(literal_edges),'contradicted_pairs':len(failed),'additional_contradicted_pairs':len(new),'additional_pairs':[p['units'] for p in new],'additional_with_two_leaves':[p['units'] for p in new if len(p['physical_leaves'])>=2],'compatible_pairs':[p['units'] for p in good],'compatible_count':len(good),'all_nontrivial_partitions_excluded':not good};assert summary==result['readers'][reader]
  print(reader,'all231pair decisions and witnesses PASS',flush=True)
 # Independently enumerate the finite proof fixtures.
 checked_parts=0
 for p in patterns(3):
  m=dict(zip('xyz',p))
  if m['x']==m['y']:assert generic_bad([('toy','xxz'),('toy','yyz')],m);checked_parts+=1
 assert not generic_bad([('toy','axb'),('toy','cyb')],{'a':0,'b':1,'c':2,'x':3,'y':3})
 assert not generic_bad([('toy','axb'),('toy','cyb')],{'a':0,'b':1,'c':0,'x':2,'y':3})
 assert generic_bad([('toy','axb'),('toy','cyb')],{'a':0,'b':1,'c':0,'x':2,'y':2})
 words=[]
 for n in range(1,6):
  for w in itertools.product('ab',repeat=n):words.append(('toy',''.join('z' if s=='b' else 'y' if i and w[i-1]=='b' else 'x' for i,s in enumerate(w))))
 assert not generic_bad(words,{'x':0,'y':0,'z':1});assert len(words)==62
 assert result['fixtures']['coarser_partitions_checked']==checked_parts
 out={'status':'PASS','source_positions':totalpos,'pair_decisions':checked,'counterexample_witnesses':witnesses,'compatible_lookup_digests':compatible,'distinct_raw_forms_reparsed':len(cache),'monotone_fixture_partitions':checked_parts,'valid_contextual_writer_words':62,'implementation':'separate integer source mapping, sort/group full contexts and dynamic raw segmentation; no runner import','ceiling':'Conditional finite compatibility only, no native allograph, phoneme, meaning or economical writing rule.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
