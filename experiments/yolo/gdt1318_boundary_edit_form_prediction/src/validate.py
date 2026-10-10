import collections,csv,gzip,hashlib,json,math,re,statistics
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(p):
 d=p.read_bytes();return json.loads(gzip.decompress(d) if p.suffix=='.gz' else d)
def close(a,b):
 if a is None or b is None:assert a==b
 else:assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-11),(a,b)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h
 old=R/'experiments/yolo/gdt1308_whole_form_prediction/artifacts';oldmodels=read(old/'MODEL.json');old_events=read(old/'EVENTS.json.gz');strict=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');allowed={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};rules_saved=read(B/'artifacts/RULES.json');ds=read(B/'artifacts/EDIT_DISTRIBUTIONS.json.gz');events=read(B/'artifacts/EVENTS.json.gz');result=read(B/'artifacts/RESULT.json');assert [e['id'] for e in events]==[e['id'] for e in old_events];joins=0;outputs_checked=0;scores_checked=0
 for olde,e in zip(old_events,events):assert all(e[k]==v for k,v in olde.items())
 for ed,summary in result['readers'].items():
  source={}
  for phase in ['DISCOVERY','EVALUATION']:
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')['lines']:
    for g in line['groups']:source[g[0]]=(line['metadata'],g)
  rawcounts=collections.defaultdict(collections.Counter);held={}
  for row in strict[ed]:
   m,g=source[row['id']];assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ('f1r','f116v');assert m['page']==row['page'] and m['locus']==row['locus'] and m['edition']==ed and m['kind']==row['kind']=='P';assert g[2]==row['ivtff_group_raw'] and g[3]==g[4]=='DEFINITE_SPACE';u=tuple(row['units']);assert ''.join(u)==g[2] and set(u)<=set(A);joins+=1
   if len(u)<4:continue
   leaf=int(re.match(r'f(\d+)',row['page'])[1]);cell=(m['currier'],len(u))
   if leaf%2:rawcounts[cell][u]+=1
   else:held[row['id']]=(cell,u,leaf)
  counts={tuple(x['cell']):{tuple(w['units']):w['count'] for w in x['counts']} for x in oldmodels[ed]['whole']};assert counts==dict(rawcounts);types=collections.defaultdict(set)
  for (c,n),words in counts.items():types[c].update(words)
  rules={}
  for c,words in types.items():
   rc=collections.Counter()
   for u in words:
    for pos,side in [(0,'FIRST'),(len(u)-1,'LAST')]:
     for b in A:
      if b==u[pos]:continue
      v=u[:pos]+(b,)+u[pos+1:]
      if v in words:rc[side,u[pos],b]+=1
   assert rc=={(r['side'],r['old'],r['new']):r['count'] for r in rules_saved[ed][c]};assert all(v==rc[side,b,a] for (side,a,b),v in rc.items());rules[c]=rc
  verified={};assert len(ds[ed])==len(counts)
  for d in ds[ed]:
   cell=tuple(d['cell']);words=counts[cell];N=sum(words.values());rr=rules[cell[0]];den={u:sum(v for (side,a,b),v in rr.items() if a==(u[0] if side=='FIRST' else u[-1])) for u in words};candidate=set();paths=0;fallback=0
   for u in words:
    if not den[u]:candidate.add(u);fallback+=words[u];paths+=1
    else:
     for pos,side in [(0,'FIRST'),(len(u)-1,'LAST')]:
      for b in A:
       if rr.get((side,u[pos],b),0):candidate.add(u[:pos]+(b,)+u[pos+1:]);paths+=1
   got={tuple(x['units']):x['p'] for x in d['outputs']};assert set(got)==candidate and d['N']==N and d['fallback_tokens']==fallback and d['paths']==paths and d['mass']=='1';probs={}
   for w in candidate:
    total=F(words.get(w,0),N) if w in den and den[w]==0 else F(0)
    for pos,side in [(0,'FIRST'),(len(w)-1,'LAST')]:
     for a in A:
      weight=rr.get((side,a,w[pos]),0)
      if not weight:continue
      u=w[:pos]+(a,)+w[pos+1:]
      if u in words:total+=F(words[u]*weight,N*den[u])
    assert total>0;close(float(total),got[w]);assert w[1:-1] in {u[1:-1] for u in words};probs[w]=total;outputs_checked+=1
   assert sum(probs.values())==1;verified[cell]=probs
  assert summary['rule_entries']==sum(map(len,rules.values())) and summary['ordered_training_pair_supports']==sum(sum(x.values()) for x in rules.values()) and summary['generated_cell_outputs']==sum(map(len,verified.values())) and summary['train_whole_cell_entries']==sum(map(len,counts.values()))
  es=[e for e in events if e['reader']==ed];assert set(held)=={e['id'] for e in es};known={u for ws in counts.values() for u in ws}
  for e in es:
   cell,u,leaf=held[e['id']];assert e['c']==cell[0] and tuple(e['units'])==u and e['leaf']==leaf and e['global_unseen']==(u not in known);ep=float(verified.get(cell,{}).get(u,0));new=(2*e['p']+e['q']+ep)/4 if cell in verified else e['p'];close(e['edit_p'],ep);close(e['new_p'],new);close(e['gain_old'],math.log(new)-math.log(e['mix']));close(e['gain_m1'],math.log(new)-math.log(e['p']));scores_checked+=1
   if e['global_unseen']:close(new/e['mix'],1+ep/(2*e['p']))
  novel=[e for e in es if e['global_unseen'] and e['edit_p']>0];cov=summary['novel_edit_coverage'];assert cov['words']==len(novel) and cov['leaves']==len({e['leaf'] for e in novel}) and cov['gate']==(cov['words']>=100 and cov['leaves']>=10)
  for co,s in summary['cohorts'].items():
   subset=[e for e in es if co=='ALL' or co=='GLOBAL_UNSEEN' and e['global_unseen'] or co=='GLOBAL_KNOWN' and not e['global_unseen'] or co=='E_POSITIVE' and e['edit_p']>0 or co=='E_ZERO' and e['edit_p']==0];leaves=sorted({e['leaf'] for e in subset});po={str(l):statistics.fmean(e['gain_old'] for e in subset if e['leaf']==l) for l in leaves};pm={str(l):statistics.fmean(e['gain_m1'] for e in subset if e['leaf']==l) for l in leaves};mean=statistics.fmean(po.values()) if po else None;N=len(subset);L=len(leaves);positive=sum(v>0 for v in po.values());assert s['words']==N and s['leaves']==L and s['positive_leaves_old']==positive;close(s['equal_leaf_gain_old'],mean);close(s['equal_leaf_gain_m1'],statistics.fmean(pm.values()) if pm else None);close(s['token_gain_old'],statistics.fmean(e['gain_old'] for e in subset) if N else None);assert s['material_gate']==bool(N>=100 and L>=10 and mean>=.01 and positive*3>=2*L);assert set(po)==set(s['per_leaf_old'])==set(s['per_leaf_m1'])
   for l in po:close(po[l],s['per_leaf_old'][l]);close(pm[l],s['per_leaf_m1'][l])
  assert summary['lead']==(summary['cohorts']['ALL']['material_gate'] and cov['gate'])
 assert result['status']==('BOUNDARY_EDIT_PREDICTIVE_LEAD' if result['readers']['ZL3b']['lead'] else 'NO_BOUNDARY_EDIT_PREDICTIVE_LEAD')
 receipt={'status':'PASS','source_joins':joins,'inverse_generated_outputs':outputs_checked,'held_scores':scores_checked,'method':'Independent literal-neighbor rule discovery and inverse-path exact probabilities; full source TRAINcounts, support, normalization, scores and gates. Not native semantics or independent replication.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
