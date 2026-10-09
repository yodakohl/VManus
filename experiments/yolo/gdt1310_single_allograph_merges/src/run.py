import collections,csv,gzip,hashlib,itertools,json,re
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SOURCE='experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz'
OLD='experiments/yolo/gdt1295_local_allograph_letter_bound/artifacts/CONFLICTS.json.gz'
A=sorted('a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split())
READERS=['ZL3b','IT2a','RF1b']
def save(name,value):(B/'artifacts'/name).write_text(json.dumps(value,indent=2)+'\n')
def pair_check(rows,x,y,old=False):
 pair={x,y};cells=collections.defaultdict(lambda:collections.defaultdict(list));positions=0
 def psi(g):return '@' if g in pair else g
 for row in rows:
  u=row['units'];n=len(u)
  for i,g in enumerate(u):
   if g not in pair:continue
   left=u[i-1] if i else 'BOS';right=u[i+1] if i+1<n else 'EOS';k=(row['page'],n,i,psi(left),psi(right));positions+=1
   cells[k][g].append({'id':row['id'],'index':i,'whole':row['ivtff_group_raw'],'written':g,'left':left,'right':right})
 bad=sorted(k for k,v in cells.items() if len(v)>1);witness=None
 if bad:
  k=bad[0];witness={'source_context':list(k),'first':min(cells[k][x],key=lambda a:a['id']),'second':min(cells[k][y],key=lambda a:a['id'])}
 selectors=sorted({k[0] for k in bad});leaves=sorted({int(re.match(r'f(\d+)',p)[1]) for p in selectors}) if selectors and all(p.startswith('f') for p in selectors) else []
 table=[[list(k),next(iter(v))] for k,v in sorted(cells.items())] if not bad else None
 return {'units':[x,y],'status':'CONTRADICTED' if bad else 'COMPATIBLE_SINGLE_MERGE','old_literal_edge':old,'positions':positions,'observed_merged_contexts':len(cells),'conflicting_contexts':len(bad),'selectors':selectors,'physical_leaves':leaves,'first_conflict':witness,'nondefault_lookup_entries':sum(g!=x for k,g in table) if table is not None else None,'lookup_sha256':hashlib.sha256(json.dumps(table,separators=(',',':')).encode()).hexdigest() if table is not None else None}

def partition_patterns(n):
 def grow(p):
  if len(p)==n:yield tuple(p);return
  for c in range(max(p,default=-1)+2):yield from grow(p+[c])
 yield from grow([])
def generic_conflict(rows,psi):
 seen={}
 for row in rows:
  u=row['units'];n=len(u)
  for i,g in enumerate(u):
   k=(row['page'],n,i,psi.get(u[i-1],u[i-1]) if i else 'BOS',psi[g],psi.get(u[i+1],u[i+1]) if i+1<n else 'EOS')
   if k in seen and seen[k]!=g:return True
   seen[k]=g
 return False

def fixtures():
 def rows(words):return [{'id':str(i),'page':'toy','units':list(w),'ivtff_group_raw':w} for i,w in enumerate(words)]
 same=rows(['axb','ayb']);assert pair_check(same,'x','y')['status']=='CONTRADICTED'
 new=rows(['xxz','yyz']);assert pair_check(new,'x','y')['conflicting_contexts']==2
 oldframes=collections.defaultdict(set)
 for r in new:
  for i,g in enumerate(r['units']):oldframes[(i,r['units'][i-1] if i else 'BOS',r['units'][i+1] if i<2 else 'EOS')].add(g)
 assert not any({'x','y'}<=v for v in oldframes.values())
 separate=rows(['axb','ayb']);separate[1]['page']='other';assert pair_check(separate,'x','y')['status']=='COMPATIBLE_SINGLE_MERGE'
 words=[]
 for n in range(1,6):
  for w in itertools.product('ab',repeat=n):words.append(''.join('z' if g=='b' else 'y' if i and w[i-1]=='b' else 'x' for i,g in enumerate(w)))
 assert pair_check(rows(words),'x','y')['status']=='COMPATIBLE_SINGLE_MERGE'
 joint=rows(['axb','cyb']);assert pair_check(joint,'x','y')['status']=='COMPATIBLE_SINGLE_MERGE';assert pair_check(joint,'a','c')['status']=='COMPATIBLE_SINGLE_MERGE'
 assert generic_conflict(joint,{'a':0,'c':0,'x':1,'y':1,'b':2})
 checked=0
 for p in partition_patterns(3):
  psi=dict(zip('xyz',p))
  if psi['x']==psi['y']:assert generic_conflict(new,psi);checked+=1
 return {'status':'PASS','valid_two_letter_words':len(words),'merged_neighbor_new_contexts':2,'coarser_partitions_checked':checked,'separately_compatible_joint_failure':True,'page_change_blocks_conflict':True}

def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixtures();data=json.loads(gzip.decompress((R/SOURCE).read_bytes()));old=json.loads(gzip.decompress((R/OLD).read_bytes()));allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
 results={};summaries={}
 for reader in READERS:
  rows=data[reader]
  for row in rows:
   assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v'];assert row['kind']=='P' and row['left_separator']==row['right_separator']=='DEFINITE_SPACE';assert ''.join(row['units'])==row['ivtff_group_raw'] and set(row['units'])<=set(A)
  oldedges={tuple(e['units']) for e in old[reader]['edges']};ps=[]
  for x,y in itertools.combinations(A,2):ps.append(pair_check(rows,x,y,(x,y) in oldedges))
  assert all(p['status']=='CONTRADICTED' for p in ps if p['old_literal_edge'])
  failed=[p for p in ps if p['status']=='CONTRADICTED'];new=[p for p in failed if not p['old_literal_edge']];compatible=[p for p in ps if p['status']!='CONTRADICTED']
  summaries[reader]={'groups':len(rows),'positions':sum(len(r['units']) for r in rows),'pairs':len(ps),'old_literal_edges':len(oldedges),'contradicted_pairs':len(failed),'additional_contradicted_pairs':len(new),'additional_pairs':[p['units'] for p in new],'additional_with_two_leaves':[p['units'] for p in new if len(p['physical_leaves'])>=2],'compatible_pairs':[p['units'] for p in compatible],'compatible_count':len(compatible),'all_nontrivial_partitions_excluded':not compatible}
  results[reader]=ps;print(reader,'old',len(oldedges),'failed',len(failed),'new',len(new),'compatible',len(compatible),flush=True)
 save('PAIR_RESULTS.json',results);save('RESULT.json',{'status':'EXACT_SINGLE_MERGE_COMPATIBILITY','readers':summaries,'fixtures':fx,'claim_ceiling':'Conditional single-pair compatibility and monotone obstructions; no native alphabet or compact human rule.'})
if __name__=='__main__':main()
