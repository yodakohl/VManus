from pathlib import Path
from collections import defaultdict
import csv,gzip,hashlib,itertools,json,re
B=Path(__file__).resolve().parents[1];R=B.parents[2];U='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def parse(s):
 ways=[[] for _ in range(len(s)+1)];ways[0]=[()]
 for i in range(len(s)):
  for u in U:
   if s.startswith(u,i):ways[i+len(u)].extend(v+(u,) for v in ways[i])
 return ways[-1]
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 strict=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');edges=read(R/'experiments/yolo/gdt1314_binary_line_edge_capacity/artifacts/EDGES.json.gz');prior=read(R/'research_registry/proposals/production_origin_supply_20261003/BINARY_WORD_RANK_BOUND_20261011.json');res=read(B/'artifacts/RESULT.json');allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=0;checks=0
 for ed in sorted(strict):
  byid={r['id']:r for r in strict[ed]+edges[ed]};assert len(byid)==len(strict[ed])+len(edges[ed]);seen=set();selected_edges=set();original={}
  for phase in ['DISCOVERY','EVALUATION']:
   source=read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')
   for line in source['lines']:
    m=line['metadata'];assert m['edition']==ed and m['page'] in allowed and not m['page'].startswith('f84') and m['page'] not in ('f1r','f116v');indices=[int(g[1]) for g in line['groups']]
    for ident,index,raw,left,right in line['groups']:
     edge=(left=='LINE_START' and right in ('DEFINITE_SPACE','LINE_END')) or (left=='DEFINITE_SPACE' and right=='LINE_END')
     if m['kind']=='P' and edge and re.fullmatch('[a-z]+',raw):
      ps=parse(raw)
      if len(ps)==1:
       selected_edges.add(ident)
       if left=='LINE_START':assert int(index)==min(indices)
       if right=='LINE_END':assert int(index)==max(indices)
     if ident not in byid:continue
     r=byid[ident];assert ident not in seen;seen.add(ident);assert m['kind']=='P' and (r['page'],r['locus'],int(r['source_group_index']),r['ivtff_group_raw'],r['left_separator'],r['right_separator'])==(m['page'],m['locus'],int(index),raw,left,right);ps=parse(raw);assert ps==[tuple(r['units'])];original[ident]=(r,ps[0]);joins+=1
  assert seen==set(byid) and selected_edges=={r['id'] for r in edges[ed]}
  heads={r['units'][0] for r in strict[ed]};mandatory=set(prior['readers'][ed]['required_one_drawings']);assert mandatory<=heads
  missing=sorted(set(U)-mandatory);allkeys=[list(k) for n in range(1,len(missing)+1) for k in itertools.combinations(missing,n)];assert {tuple(sorted(k)) for k in allkeys}=={tuple(sorted(c['necessary_zero_set'])) for c in prior['readers'][ed]['necessary_candidates_not_validated_keys']}
  for name,group in [('STRICT',strict[ed]),('STRICT_PLUS_EDGES',strict[ed]+edges[ed])]:
   rows=sorted(group,key=lambda r:r['id']);rr=res['readers'][ed][name];assert rr['groups']==len(rows);L=max(len(original[r['id']][1]) for r in rows);assert rr['max_units']==L and rr['elementary_length_bound']==1<<(L-1);assert {tuple(sorted(c['zero'])) for c in rr['keys']}=={tuple(sorted(k)) for k in allkeys};good=[]
   for c in rr['keys']:
    zero=set(c['zero']);bad=[];pagevals=defaultdict(list);vals=[]
    for r in rows:
     us=original[r['id']][1]
     if us[0] in zero:bad.append({'id':r['id'],'raw':r['ivtff_group_raw'],'page':r['page']})
     v=sum(2**j for j,u in enumerate(reversed(us)) if u not in zero);vals.append((v,r));pagevals[str(int(re.search(r'\d+',r['page']).group()))].append(v)
    assert c['head_violations']==bad and c['valid']==(not bad);checks+=1
    if bad:assert set(c)=={'zero','head_violations','valid'};continue
    N=max(v for v,r in vals);w=next(r for v,r in vals if v==N);assert c['required_dictionary_size']==N and c['maximum_witness']=={'id':w['id'],'raw':w['ivtff_group_raw'],'units':w['units'],'rank':N};fm={f:max(vs) for f,vs in pagevals.items()};assert c['folio_maxima']==fm;values=sorted(fm.values(),reverse=True);assert c['second_folio_maximum']==values[1];assert (1<<(L-1))<=N<(1<<L);good.append(c)
   assert rr['surviving_zero_sets']==[c['zero'] for c in good];assert rr['minimum_required_dictionary_size']==min((c['required_dictionary_size'] for c in good),default=None);assert rr['minimum_second_folio_maximum']==min((c['second_folio_maximum'] for c in good),default=None);assert rr['status']==('CANONICAL_HEAD_EXCLUDED' if not good else 'NECESSARY_DICTIONARY_COST_ONLY')
 # State distinctions are source-free, not native meanings.
 d=list('ABC');ranks=[]
 for token in 'BCBC':i=d.index(token);ranks.append(i+1);d.insert(0,d.pop(i))
 assert ranks==[2,3,2,2];d=list('ABC');decoded=[]
 for r in [2,2,2,2]:decoded.append(d[r-1]);d.insert(0,d.pop(r-1))
 assert decoded==list('BABA')
 out={'status':'PASS','original_source_groups':joins,'panel_key_cases':checks,'method':'Independent original915source recollation and complete edge reselection; dynamic unit parsing, weighted-power ranks and independently reconstructed folio extrema; source-free MTF fixtures.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
