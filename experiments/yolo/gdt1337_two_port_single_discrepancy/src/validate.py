from pathlib import Path
import collections,csv,gzip,hashlib,importlib.util,itertools,json,re,sys
import z3
sys.dont_write_bytecode=True
B=Path(__file__).resolve().parents[1];R=B.parents[2]
spec=importlib.util.spec_from_file_location('independent1334',R/'experiments/yolo/gdt1334_canonical_two_port_alias_capacity/src/validate.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
U=old.U;I=old.I;PAT=re.compile('|'.join(sorted(U,key=lambda u:(-len(u),u))))
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def solve(cs):
 vs=[z3.Bool('p'+str(i)) for i in range(44)];s=z3.Solver();s.set(timeout=30000)
 for c in cs:s.add(z3.Or([vs[abs(l)-1] if l>0 else z3.Not(vs[abs(l)-1]) for l in c]))
 v=s.check();assert v in (z3.sat,z3.unsat);return v,s,vs
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');saved=read(B/'artifacts/DECISIONS.json.gz');result=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;branches=0;tests=0;positives=0;wordchecks=0;context_skips=0;cores=0
 for ed,rows in sorted(data.items()):
  byid={r['id']:r for r in rows};seen=set();original=[]
  for ph in ('DISCOVERY','EVALUATION'):
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json')['lines']:
    m=line['metadata']
    for g in line['groups']:
     if g[0] not in byid:continue
     r=byid[g[0]];assert g[0] not in seen;seen.add(g[0]);assert m['edition']==ed and m['kind']==r['kind']=='P' and m['page']==r['page'] and m['locus']==r['locus'];assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert g[2]==r['ivtff_group_raw']==''.join(r['units']);assert PAT.findall(g[2])==r['units'];assert int(g[1])==int(r['source_group_index']) and g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';joins+=1;original.append((r,tuple(I[u] for u in PAT.findall(g[2]))))
  assert seen==set(byid);byword=collections.defaultdict(list);ctx={u:collections.defaultdict(set) for u in range(22)}
  for r,w in original:
   byword[w].append(r)
   for i,u in enumerate(w):ctx[u][(U[w[i-1]] if i else 'BOS',U[w[i+1]] if i+1<len(w) else 'EOS')].add(w)
  words=sorted(byword);hap={w for w,rr in byword.items() if len(rr)==1};raw=lambda w:''.join(U[u] for u in w);byraw={raw(w):w for w in words};assert len(byraw)==len(words);witnesses=[];pair_summ=[];nbranches=0;ntests=0;nskips=0
  assert len(saved[ed]['pairs'])==231
  for rec,pair in zip(saved[ed]['pairs'],itertools.combinations(range(22),2)):
   x,y=pair;assert rec['pair']==[U[x],U[y]];common=sorted(set(ctx[x])&set(ctx[y]));assert rec['shared_contexts']==len(common);candidate=None;steps=[]
   for c in common:
    sides=[ctx[x][c],ctx[y][c]];possible={w for ss in sides if len(ss)==1 for w in ss if w in hap};candidate=possible if candidate is None else candidate&possible;steps.append({'context':list(c),'removable_words':sorted(raw(w) for w in possible)})
    if not candidate:break
   assert rec['context_steps']==steps;assert rec['context_candidates']==(None if candidate is None else sorted(raw(w) for w in candidate))
   if candidate==set():assert rec['status']=='NO_SINGLE_DISCREPANCY_CONTEXT' and not rec['port_cases'];context_skips+=1;nskips+=1;continue
   assert len(rec['port_cases'])==12;has=False
   for case,(px,py) in zip(rec['port_cases'],itertools.permutations(range(4),2)):
    assert case['pair_ports']==[px,py];mandatory=set(old.derive_clauses([],pair,px,py)[0]);support=collections.defaultdict(set)
    for w in words:
     if x not in w and y not in w:continue
     cs,_=old.derive_clauses([w],pair,px,py)
     for c in set(cs)-mandatory:support[c].add(w)
    full=mandatory|set(support);assert solve(full)[0]==z3.unsat;branches+=1;nbranches+=1
    if candidate is None:
     core={tuple(c) for c in case['unsat_core']};assert core<=full and solve(core)[0]==z3.unsat;cores+=1;eligible={w for c in core-mandatory if len(support[c])==1 for w in support[c] if w in hap}
    else:assert case['unsat_core']==[];eligible=candidate
    assert case['candidate_words']==sorted(raw(w) for w in eligible);assert len(case['checks'])==len(eligible)
    for test,w in zip(case['checks'],sorted(eligible,key=raw)):
     assert test['removed_word']==raw(w);accepted=[(r,v) for r,v in original if v!=w];gx=[r for r,v in accepted if x in v];gy=[r for r,v in accepted if y in v];assert test['accepted_x_groups']==len(gx) and test['accepted_y_groups']==len(gy);tests+=1;ntests+=1
     if not gx or not gy:assert test['status']=='INACTIVE_ALIAS_MEMBER' and test['bits'] is None;continue
     cs=mandatory|{c for c,ss in support.items() if ss-{w}};decision,solver,vs=solve(cs);bits=test['bits'];assert (decision==z3.sat)==(bits is not None);assert test['status']==('ONE_DISCREPANCY_WRITER' if bits is not None else 'UNSAT')
     if bits is None:continue
     assert len(bits)==44 and all(b in (0,1) for b in bits);assert all(any(bool(bits[abs(l)-1])==(l>0) for l in c) for c in cs)
     for i,bit in enumerate(bits):
      if bit:solver.push();solver.add(z3.Not(vs[i]));assert solver.check()==z3.unsat;solver.pop()
      solver.add(vs[i] if bit else z3.Not(vs[i]))
     ports=[2*bits[2*i]+bits[2*i+1] for i in range(22)];assert ports[x]==px and ports[y]==py;bad=[];rendered={}
     for v in words:
      out=old.canonical([pair if u in pair else (u,) for u in v],ports);wordchecks+=1
      if out!=v:bad.append(v);rendered[v]=out
     assert bad==[w] and len(byword[w])==1;witness={'pair':[U[x],U[y]],'pair_ports':[px,py],'bits':bits,'residual':byword[w][0],'canonical_residual':' '.join(U[u] for u in rendered[w]),'accepted_x_groups':len(gx),'accepted_y_groups':len(gy),'accepted_union':len({r['id'] for r in gx}|{r['id'] for r in gy}),'accepted_intersection':len({r['id'] for r in gx}&{r['id'] for r in gy}),'x_pages':sorted({r['page'] for r in gx}),'y_pages':sorted({r['page'] for r in gy}),'minority_mass':[min(len(gx),len(gy)),len(rows)],'full_word_types_checked':len(words)};witnesses.append(witness);has=True;positives+=1
   assert rec['status']==('ONE_DISCREPANCY_PAIR_WITNESSES' if has else 'NO_SINGLE_DISCREPANCY_RUN')
   if has:pair_summ.append([U[x],U[y]])
  assert witnesses==saved[ed]['witnesses'];maximum=max((w['minority_mass'][0] for w in witnesses),default=None)
  expected={'groups':len(rows),'types':len(words),'pairs':231,'context_excluded_pairs':nskips,'port_branches':nbranches,'candidate_checks':ntests,'SAT_witnesses':len(witnesses),'compatible_pairs':pair_summ,'residual_types':sorted({w['residual']['ivtff_group_raw'] for w in witnesses}),'maximum_single_pair_minority_mass':None if maximum is None else [maximum,len(rows)],'status':'EXACT_USED_ALIAS_RADIUS_ONE' if witnesses else 'USED_ALIAS_RADIUS_AT_LEAST_TWO'};assert result['readers'][ed]==expected;print(ed,'validated',flush=True)
 assert result['status']=='COMPLETE_ONE_DISCREPANCY_CLASSIFICATION';out={'status':'PASS','source_joins':joins,'context_excluded_pairs':context_skips,'original_UNSAT_branches':branches,'independent_UNSAT_cores':cores,'candidate_checks':tests,'positive_port_witnesses':positives,'whole_word_render_checks':wordchecks,'method':'Original915provenance; independently derived per-word backward-DP clauses and support; shared-context candidate intersections; Z3 vs SCC; all positive full-word renderings and lexleast bits.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
