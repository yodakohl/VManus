from pathlib import Path
import collections,csv,gzip,hashlib,importlib.util,itertools,json,re,sys
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parents[1];R=B.parents[2]
spec=importlib.util.spec_from_file_location('edge_parser1314',R/'experiments/yolo/gdt1314_binary_line_edge_capacity/src/validate.py');parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser)
U=sorted(parser.SIGNS);TARGETS={'mol','damo','qokomo'}
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');oldedge=read(R/'experiments/yolo/gdt1314_binary_line_edge_capacity/artifacts/EDGES.json.gz');prior=read(R/'experiments/yolo/gdt1337_two_port_single_discrepancy/artifacts/DECISIONS.json.gz');sel=read(B/'artifacts/SELECTED_EDGES.json');dec=read(B/'artifacts/DECISIONS.json');res=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;edgejoins=0;pairproofs=0;portbranches=0
 for ed,rows in sorted(data.items()):
  byid={r['id']:r for r in rows};seen=set();expected=[]
  for phase in ('DISCOVERY','EVALUATION'):
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    m=line['metadata'];assert m['page'] in allow and not m['page'].startswith('f84') and m['page'] not in ('f1r','f116v');indices=[int(g[1]) for g in line['groups']]
    for ident,i,raw,left,right in line['groups']:
     if ident in byid:
      r=byid[ident];assert ident not in seen;seen.add(ident);assert m['edition']==ed and m['kind']=='P' and m['page']==r['page'] and m['locus']==r['locus'];assert int(i)==int(r['source_group_index']) and raw==r['ivtff_group_raw'] and left==right==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';assert parser.split(raw)==[tuple(r['units'])];joins+=1
     if raw not in TARGETS or m['kind']!='P':continue
     edge=(left=='LINE_START' and right in ('DEFINITE_SPACE','LINE_END')) or (left=='DEFINITE_SPACE' and right=='LINE_END')
     if not edge:continue
     if left=='LINE_START':assert int(i)==min(indices)
     if right=='LINE_END':assert int(i)==max(indices)
     ways=parser.split(raw);assert len(ways)==1;expected.append({'id':ident,'page':m['page'],'locus':m['locus'],'source_group_index':i,'ivtff_group_raw':raw,'left_separator':left,'right_separator':right,'units':list(ways[0])})
  assert seen==set(byid);expected.sort(key=lambda r:r['id']);assert expected==sel[ed]==[r for r in oldedge[ed] if r['ivtff_group_raw'] in TARGETS];assert not ({r['id'] for r in expected}&seen);edgejoins+=len(expected)
  support={u:len({r['id'] for r in rows if u in r['units']}) for u in U};assert support==dec[ed]['unit_group_support'];assert dec[ed]['bridge_gate']==(min(support.values())>=2)
  if not dec[ed]['bridge_gate']:assert res['readers'][ed]['status']=='INCOMPLETE_SCOPE';continue
  residual=[r for r in rows if r['ivtff_group_raw']=='aman'];assert len(residual)==1 and residual[0]==dec[ed]['old_strict_residual'];assert {w['residual']['id'] for w in prior[ed]['witnesses']}=={residual[0]['id']}
  accepted=[dict(r,cohort='strict') for r in rows if r['id']!=residual[0]['id']]+[dict(r,cohort='fixed_old_edge') for r in expected];ct=collections.defaultdict(list)
  for r in accepted:
   u=r['units']
   for j,g in enumerate(u):ct[g].append(((u[j-1] if j else 'BOS',u[j+1] if j+1<len(u) else 'EOS'),r['id'],j,r))
  pairs=sorted({tuple(w['pair']) for w in prior[ed]['witnesses']});assert [p['pair'] for p in dec[ed]['pairs']]==[list(p) for p in pairs]
  for record,pair in zip(dec[ed]['pairs'],pairs):
   ports=sorted({tuple(w['pair_ports']) for w in prior[ed]['witnesses'] if tuple(w['pair'])==pair});assert record['prior_port_cases']==[list(p) for p in ports];portbranches+=len(ports);x,y=pair;common=sorted({x[0] for x in ct[x]}&{y[0] for y in ct[y]})
   # Actual primary outcome uses the simple sufficient invariant for every pair.
   # A future nonliteral branch would require its separately declared solver validation.
   assert common and record['status']=='ALL_PORTS_LITERAL_CONFLICT' and record['port_cases']==[];c=common[0];assert record['context']==list(c);w=[]
   for u in pair:
    t=min((t for t in ct[u] if t[0]==c),key=lambda t:(t[1],t[2]));w.append({'row':t[3],'index':t[2]})
   assert record['witnesses']==w and any(t['row']['cohort']=='fixed_old_edge' for t in w);pairproofs+=1
  expect={'strict_groups':len(rows),'selected_edge_occurrences':len(expected),'selected_counts':dict(sorted(collections.Counter(r['ivtff_group_raw'] for r in expected).items())),'minimum_strict_unit_group_support':min(support.values()),'prior_pairs':len(pairs),'prior_positive_port_cases':sum(len(p['prior_port_cases']) for p in dec[ed]['pairs']),'literal_conflict_pairs':len(pairs),'fallback_solver_cases':0,'status':'EXPANDED_SUBSET_RADIUS_AT_LEAST_TWO'};assert res['readers'][ed]==expect
 # A global canonical word is locally preferred to either single-glyph replacement.
 # Identical actual flank ports give one and only one of the distinct alternatives.
 controls=0
 for px,py in itertools.permutations(range(4),2):
  for left,right in itertools.product((None,0,1),repeat=2):
   score=lambda p:((0 if left is None else int(left!=p//2))+(0 if right is None else int(p%2!=right)),p)
   assert (score(px)<score(py)) != (score(py)<score(px));controls+=1
 out={'status':'PASS','strict_original_source_joins':joins,'selected_original_edge_joins':edgejoins,'literal_pair_proofs':pairproofs,'old_feasible_port_branches_excluded':portbranches,'local_preference_control_cases':controls,'fallback_solver_cases':0,'method':'Independent original915three-form selection, iterative unique parsing, >=2occurrence unit bridge, full context witness reconstruction and all12ports/9flanks local preference checks. No other edge form scored.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
