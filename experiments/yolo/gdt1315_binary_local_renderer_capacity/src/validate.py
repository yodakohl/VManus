import collections,csv,gzip,hashlib,itertools,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(path):
 data=path.read_bytes();return json.loads(gzip.decompress(data) if path.suffix=='.gz' else data)
def parse(raw):
 dp=[[] for _ in range(len(raw)+1)];dp[0]=[()]
 for i in range(len(raw)):
  for u in A:
   if raw[i:i+len(u)]==u:dp[i+len(u)].extend(x+(u,) for x in dp[i]);dp[i+len(u)]=dp[i+len(u)][:2]
 return dp[-1]
def projection(units,mask):
 val=0
 for unit in units:val=val*2+int(bool(mask&(1<<A.index(unit))))
 return (len(units),val)
def from_binary(s):return len(s),int(s,2)
def normalized(k):return tuple(k[:-3])+tuple(from_binary(s) for s in k[-3:])
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 strict=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');edges=read(R/'experiments/yolo/gdt1314_binary_line_edge_capacity/artifacts/EDGES.json.gz');prior=read(R/'experiments/yolo/gdt1314_binary_line_edge_capacity/artifacts/RESULT.json');result=read(B/'artifacts/RESULT.json');packets=read(B/'artifacts/EVENTS.json.gz');conflicts=read(B/'artifacts/CONFLICTS.json.gz');allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;events_total=0;cases=0;cells_total=0
 assert projection(['a'],1<<21)!=projection(['a','a'],1<<21)
 for ed,report in result['readers'].items():
  rows={r['id']:r for r in strict[ed]+edges[ed]};events=[];found=set()
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    m=line['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84') and m['page'] not in ('f1r','f116v');gs=sorted(line['groups'],key=lambda g:int(g[1]));assert len(gs)==int(m['source_group_count'])
    for g in gs:
     if g[0] not in rows:continue
     r=rows[g[0]];assert g[0] not in found;found.add(g[0]);assert int(g[1])==int(r['source_group_index']) and g[2]==r['ivtff_group_raw'] and g[3]==r['left_separator'] and g[4]==r['right_separator'];assert r['page']==m['page'] and r['locus']==m['locus'] and m['kind']=='P';assert parse(g[2])==[tuple(r['units'])];joins+=1
    for i in range(1,len(gs)-1):
     tri=gs[i-1:i+2]
     if not all(g[0] in rows for g in tri):continue
     if [int(g[1]) for g in tri]!=list(range(int(tri[0][1]),int(tri[0][1])+3)):continue
     if any(s!='DEFINITE_SPACE' for s in [tri[0][4],tri[1][3],tri[1][4],tri[2][3]]):continue
     events.append({'left':rows[tri[0][0]],'center':rows[tri[1][0]],'right':rows[tri[2][0]],'line_group_count':len(gs),'paragraph_start':m['paragraph_start'],'paragraph_end':m['paragraph_end']})
  events.sort(key=lambda e:(e['center']['locus'],int(e['center']['source_group_index'])))
  assert set(rows)==found and events==packets[ed];assert len(rows)==report['joined_groups'] and len(events)==report['eligible_triples'];events_total+=len(events)
  assert [k['mask'] for k in report['keys']]==prior['readers'][ed]['surviving_masks']
  for k in report['keys']:
   mask=k['mask'];assert k['class1']==[s for i,s in enumerate(A) if mask>>i&1];bounds=[]
   for level in ['SOURCE','PAGE','LAYOUT']:
    decorated=[]
    for e in events:
     c=e['center'];triple=tuple(projection(e[t]['units'],mask) for t in ['left','center','right']);prefix=() if level=='SOURCE' else ((c['page'],) if level=='PAGE' else (c['page'],int(c['source_group_index']),e['line_group_count']));decorated.append((prefix+triple,e))
    decorated.sort(key=lambda t:t[0]);groups={}
    for ctx,items in itertools.groupby(decorated,key=lambda t:t[0]):
     output={}
     for _,e in items:output.setdefault(e['center']['ivtff_group_raw'],e['center']['id'])
     groups[ctx]=output
    summary=k['levels'][level];hist=collections.Counter(map(len,groups.values()));maximum=max(hist,default=0);bounds.append(maximum);assert {str(a):b for a,b in hist.items()}==summary['distinct_output_histogram'];assert summary['cells']==len(groups);assert summary['state_lower_bound']==maximum;assert summary['cells_exceeding_two']==sum(v for c,v in hist.items() if c>2)
    if maximum:
     wc=normalized(summary['maximum_context']);assert wc in groups and len(groups[wc])==maximum and groups[wc]==summary['maximum_witnesses']
     # Bitstring ordering differs from integer-code ordering across lengths;
     # check the registered lexical selection via its reversible representation.
     def lexical(ctx):return tuple(ctx[:-3])+tuple(format(v,'0'+str(n)+'b') for n,v in ctx[-3:])
     assert lexical(wc)==min(lexical(ctx) for ctx,vals in groups.items() if len(vals)==maximum)
    cells_total+=len(groups)
    if level=='LAYOUT':
     want={ctx:vals for ctx,vals in groups.items() if len(vals)>2};got={normalized(x['context']):x['outputs'] for x in conflicts[ed][str(mask)]};assert got==want
   assert bounds[2]<=bounds[1]<=bounds[0];assert k['two_state_excluded']==(bounds[2]>2);cases+=1
  assert report['all_keys_two_state_excluded']==all(k['two_state_excluded'] for k in report['keys'])
 assert result['source_joins']==joins
 assert result['status']==('LOCAL_TWO_STATE_RENDERER_EXCLUDED' if all(r['all_keys_two_state_excluded'] for r in result['readers'].values()) else 'LOCAL_RENDERER_BOUND_ONLY')
 out={'status':'PASS','source_joins':joins,'independently_reconstructed_triples':events_total,'reader_key_cases':cases,'context_cells_verified':cells_total,'method':'Independent source-line windows, iterative parsing, integer projections, sort/group cell reconstruction; not palaeography or a sufficient state-machine construction.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
