import collections,csv,gzip,hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(p):
 d=p.read_bytes();return json.loads(gzip.decompress(d) if p.suffix=='.gz' else d)
def components(edges):
 adj=collections.defaultdict(set)
 for a,b in edges:adj[a].add(b);adj[b].add(a)
 unseen=set(adj);parts=[]
 while unseen:
  seed=min(unseen);seen={seed};queue=collections.deque([seed])
  while queue:
   for other in adj[queue.popleft()]:
    if other not in seen:seen.add(other);queue.append(other)
  unseen-=seen;parts.append(sorted(seen))
 return sorted(parts)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');got=read(B/'artifacts/PAIRS.json.gz');edges_saved=read(B/'artifacts/EDGES.json');result=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;totalpairs=0;totaledges=0;forestsize=0
 assert len(components([('O:g','I:a'),('O:b','I:g')]))==2
 for ed,r in result['readers'].items():
  rows={row['id']:row for row in data[ed]};found=set();pairs=[]
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    m=line['metadata'];gs=sorted(line['groups'],key=lambda g:int(g[1]))
    for g in gs:
     if g[0] not in rows:continue
     row=rows[g[0]];assert g[0] not in found;found.add(g[0]);assert m['edition']==ed and m['kind']==row['kind']=='P' and m['page']==row['page'] and m['locus']==row['locus'];assert row['page'] in allow and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');assert g[2]==row['ivtff_group_raw']==''.join(row['units']) and set(row['units'])<=set(A);assert int(g[1])==int(row['source_group_index']) and g[3]==g[4]==row['left_separator']==row['right_separator']=='DEFINITE_SPACE';joins+=1
    for left,right in zip(gs,gs[1:]):
     if left[0] not in rows or right[0] not in rows or int(right[1])!=int(left[1])+1:continue
     assert left[4]==right[3]=='DEFINITE_SPACE';l,u=rows[left[0]],rows[right[0]];pairs.append({'left':l,'right':u,'edge':['O:'+l['units'][-1],'I:'+u['units'][0]]})
  assert found==set(rows);pairs.sort(key=lambda p:(p['left']['locus'],int(p['left']['source_group_index'])));assert pairs==got[ed];counts=collections.Counter(tuple(p['edge']) for p in pairs);witnesses={};selectors=collections.defaultdict(set)
  for p in pairs:witnesses.setdefault(tuple(p['edge']),p);selectors[tuple(p['edge'])].add(p['left']['page'])
  assert len(edges_saved[ed])==len(counts)
  for e in edges_saved[ed]:
   k=tuple(e['edge']);assert e['count']==counts[k] and e['selectors']==sorted(selectors[k]) and e['witness']==witnesses[k]
  cs=components(counts);assert cs==r['components'];nodes=sorted(x for c in cs for x in c);assert nodes==r['active_nodes'] and r['inactive_nodes']==[role+g for role in ['I:','O:'] for g in A if role+g not in nodes];assert r['max_observed_state_values']==len(cs);assert r['pairs']==len(pairs) and r['groups']==len(rows) and r['distinct_edges']==len(counts)
  forest=[tuple(e) for e in r['forest_edges']];assert len(forest)==len(set(forest))==r['forest_size']==len(nodes)-len(cs);assert set(forest)<=set(counts);assert components(forest)==cs
  label={v:i for i,c in enumerate(cs) for v in c};assert all(label[a]==label[b] for a,b in counts)
  status='NO_CAPACITY' if not counts else ('ACTIVE_MARKER_CHANNEL_CONSTANT' if len(cs)==1 else 'MULTIPLE_MARKER_STATES_CAPACITY');assert r['status']==status;totalpairs+=len(pairs);totaledges+=len(counts);forestsize+=len(forest)
 assert result['source_joins']==joins;assert result['status']==('ACTIVE_CHANNEL_CONSTANT_ALL_READINGS' if all(r['max_observed_state_values']==1 for r in result['readers'].values()) else 'READER_SPECIFIC_MARKER_STATE_CAPACITY')
 out={'status':'PASS','source_joins':joins,'original_consecutive_pairs':totalpairs,'distinct_reader_edges':totaledges,'source_witness_forest_edges':forestsize,'method':'Independent full-source-line windows and BFS closure; all witnesses, active roles and exact maximal component-state assignment checked. No palaeography or full writer-state identification.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
