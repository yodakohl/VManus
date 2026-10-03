"""Frozen same-face residual association, not production-order inference."""
import collections,csv,hashlib,itertools,json,math,random
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
EVENTS='experiments/yolo/gdt1155_terminal_drawing_edge_transport/artifacts/EVENTS.json'
INV='experiments/yolo/gdt800_terminal_b2_b3_line_final_bridge/artifacts/GDT800_155_MATCHED_STEM_SUMMARY.tsv'
def dump(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def avg(x):return math.fsum(x)/len(x) if x else None

def fit(events,exclude):
 c=collections.defaultdict(lambda:[0,0])
 for e in events:
  if e['leaf'] in exclude or e['boundary'] not in ['END','SPACE']:continue
  b=e['boundary'];s=tuple(e['stratum'])
  for k in [(b,),(b,s),(b,s,e['stem'])]:c[k][0]+=1;c[k][1]+=e['m']
 return c

def predict(e,c):
 b=e['boundary'];s=tuple(e['stratum']);ng,mg=c.get((b,),(0,0));ns,ms=c.get((b,s),(0,0));nt,mt=c.get((b,s,e['stem']),(0,0))
 g=(mg+.5)/(ng+1);ss=(ms+20*g)/(ns+20);p=(mt+10*ss)/(nt+10)
 return {'N_global':ng,'M_global':mg,'g':g,'N_stratum':ns,'M_stratum':ms,'s':ss,'N_stem_stratum':nt,'M_stem_stratum':mt,'p':p}

def rank(values):
 pairs=sorted((v,i) for i,v in enumerate(values));out=[0.]*len(values);i=0
 while i<len(pairs):
  j=i+1
  while j<len(pairs) and pairs[j][0]==pairs[i][0]:j+=1
  for _,idx in pairs[i:j]:out[idx]=(i+1+j)/2
  i=j
 return out

def spearman(xs,ys):
 if len(xs)<2:return None
 a=rank(xs);b=rank(ys);ma=avg(a);mb=avg(b);va=math.fsum((x-ma)**2 for x in a);vb=math.fsum((y-mb)**2 for y in b)
 if not va or not vb:return None
 return math.fsum((x-ma)*(y-mb) for x,y in zip(a,b))/math.sqrt(va*vb)

def diagnostic(sheets):
 return {side:{'n':len(sheets),'rho':spearman([s[side] for s in sheets],[s['delta_'+side] for s in sheets])} for side in ['a','b']}

def main():
 pins=json.loads((E/'PREREG_LOCK.json').read_text())['files']
 for p,h in pins.items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 source=json.loads((E/'src/SOURCE.json').read_text());quires={int(k):v for k,v in source['nominal_quires'].items()};allowed=set(json.loads((R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/src/SPEC.json').read_text())['allowed_selectors'])
 forms={}
 for row in csv.DictReader((R/INV).open(),delimiter='\t'):
  for suffix,col in [('l','l_surface'),('m','m_surface')]:assert row[col]==row['stem']+suffix;forms[row[col]]=(row['stem'],suffix)
 assert len(forms)==310
 data=json.loads((R/EVENTS).read_text());all_elig={};all_pred={};all_pages={};all_sheets={};all_quires={};all_null={};all_diag={};results={}
 for reader,events in sorted(data.items()):
  pages=collections.defaultdict(list)
  for e in events:
   assert e['page'] in allowed and not e['page'].startswith('f84') and e['page']!='f116v'
   assert forms[e['word']]==(e['stem'],e['ending']) and e['m']==int(e['ending']=='m')
   if e['boundary'] in ['END','SPACE']:pages[e['page']].append(e)
  pageinfo={};bifolia=[];predictions=[];residuals={}
  for q,leaves in sorted(quires.items()):
   c=fit(events,set(leaves)|{104,115})
   for leaf in leaves:
    for side in ['r','v']:
     page=f'f{leaf}{side}';es=pages.get(page,[]);strata=sorted({tuple(e['stratum']) for e in es});reasons=[]
     if leaf in [104,115]:reasons.append('MIXED_HAND_EXPLICIT_EXCLUSION')
     if leaf in [103,116]:reasons.append('INCOMPLETE_BIFOLIUM_EXPLICIT_EXCLUSION')
     if page not in allowed:reasons.append('PAGE_NOT_ADMITTED')
     if not es:reasons.append('NO_END_SPACE_EVENTS')
     if len(es)<10:reasons.append('FEWER_THAN_10_EVENTS')
     known=len(strata)==1 and strata[0][0]!='' and strata[0][1] in ['A','B'] and strata[0][2] in ['1','2','3','4','5']
     if not known:reasons.append('NOT_SINGLE_KNOWN_STRATUM')
     pageinfo[page]={'quire':q,'leaf':leaf,'page':page,'admitted':page in allowed,'events':len(es),'m':sum(e['m'] for e in es),'boundaries':dict(collections.Counter(e['boundary'] for e in es)),'strata':strata,'eligible':not reasons,'reasons':reasons}
     if es and leaf not in [103,104,115,116]:
      pp=[]
      for e in es:
       model=predict(e,c);pr={**e,'quire':q,'model':model,'residual':e['m']-model['p']};predictions.append(pr);pp.append(pr)
      residuals[page]={'page':page,'quire':q,'events':len(pp),'observed_m_rate':avg([e['m'] for e in pp]),'predicted_m_rate':avg([e['model']['p'] for e in pp]),'residual':avg([e['residual'] for e in pp]),'page_eligible':not reasons,'source_ids':[e['source_id'] for e in pp]}
   for a,b in zip(leaves[:len(leaves)//2],reversed(leaves[len(leaves)//2:])):
    ps=[f'f{a}r',f'f{a}v',f'f{b}r',f'f{b}v'];reasons=[]
    if any(not pageinfo[p]['eligible'] for p in ps):reasons.append('PAGE_ELIGIBILITY_FAILED')
    strata={tuple(s) for p in ps for s in pageinfo[p]['strata']}
    if len(strata)!=1:reasons.append('FOUR_PAGE_STRATUM_MISMATCH')
    st=sorted(strata)[0] if len(strata)==1 else None
    bifolia.append({'quire':q,'a':a,'b':b,'pages':ps,'stratum':st,'base_eligible':not reasons,'eligible':not reasons,'reasons':reasons})
  blocks=collections.defaultdict(list)
  for s in bifolia:
   if s['base_eligible']:blocks[(s['quire'],tuple(s['stratum']))].append(s)
  for key,ss in blocks.items():
   if len(ss)<2:
    for s in ss:s['eligible']=False;s['reasons'].append('QUIRE_STRATUM_FEWER_THAN_TWO_BIFOLIA')
  sheets=[]
  for s in bifolia:
   if not s['eligible']:continue
   a,b=s['a'],s['b'];da=residuals[f'f{a}r']['residual']-residuals[f'f{a}v']['residual'];db=residuals[f'f{b}r']['residual']-residuals[f'f{b}v']['residual']
   sheets.append({**s,'delta_a':da,'delta_b':db,'contribution':-.5*da*db})
  keys=sorted({(s['quire'],tuple(s['stratum'])) for s in sheets});bs=[[s for s in sheets if (s['quire'],tuple(s['stratum']))==k] for k in keys]
  for ss in bs:ss.sort(key=lambda s:s['a'])
  qs=sorted({s['quire'] for s in sheets});qdata={}
  for q in qs:
   ss=[s for s in sheets if s['quire']==q];observed=avg([s['contribution'] for s in ss]);center=math.fsum(len(block)*(-.5*avg([s['delta_a'] for s in block])*avg([s['delta_b'] for s in block])) for key,block in zip(keys,bs) if key[0]==q)/len(ss)
   qdata[str(q)]={'sheets':len(ss),'observed':observed,'analytical_null_mean':center,'centered':observed-center}
  observed=avg([qdata[str(q)]['observed'] for q in qs]);center=avg([qdata[str(q)]['analytical_null_mean'] for q in qs]);orbit=math.prod(math.factorial(len(block)) for block in bs) if bs else 0
  exact=orbit<=100000;rng=random.Random(1156);nullrows=[]
  def score(perms):
   vals=collections.defaultdict(list)
   for (q,st),ss,perm in zip(keys,bs,perms):
    ub={s['b']:s['delta_b'] for s in ss}
    vals[q].extend(-.5*s['delta_a']*ub[b] for s,b in zip(ss,perm))
   qq={str(q):avg(vals[q]) for q in qs};return {'score':avg(list(qq.values())),'quires':qq}
  if bs:
   if exact:
    grids=[itertools.permutations(sorted(s['b'] for s in block)) for block in bs]
    for perms in itertools.product(*grids):nullrows.append(score(perms))
   else:
    for _ in range(9999):
     perms=[]
     for block in bs:
      upper=sorted(s['b'] for s in block);rng.shuffle(upper);perms.append(upper)
     nullrows.append(score(perms))
  ge=sum(x['score']>=observed-1e-15 for x in nullrows) if observed is not None else 0
  p=ge/len(nullrows) if exact and nullrows else (1+ge)/10000 if nullrows else None
  capacity=len(sheets)>=8 and len(qs)>=3;positive=sum(qdata[str(q)]['centered']>0 for q in qs)
  passed=capacity and observed-center>0 and p<=.05 and 3*positive>=2*len(qs)
  status='NO_CAPACITY' if not capacity else 'SAME_FACE_RESIDUAL_CANDIDATE' if passed else 'NOT_SUPPORTED'
  for q in qs:qdata[str(q)]['empirical_null_mean']=avg([x['quires'][str(q)] for x in nullrows])
  for page,rec in residuals.items():
   rec['retained_sheet']=any(page in s['pages'] for s in sheets);rec['diagnostic_only']=not rec['retained_sheet']
  for pr in predictions:pr['diagnostic_only']=not residuals[pr['page']]['retained_sheet']
  all_elig[reader]={'pages':pageinfo,'bifolia':bifolia};all_pred[reader]=predictions;all_pages[reader]=residuals;all_sheets[reader]=sheets;all_quires[reader]=qdata
  all_null[reader]={'method':'EXACT' if exact else 'MONTE_CARLO','orbit_size':orbit,'seed':1156,'blocks':[{'quire':k[0],'stratum':list(k[1]),'lower_leaves':[s['a'] for s in block],'upper_leaves':sorted(s['b'] for s in block)} for k,block in zip(keys,bs)],'scores':nullrows}
  all_diag[reader]={'pooled':diagnostic(sheets),'quires':{str(q):diagnostic([s for s in sheets if s['quire']==q]) for q in qs}}
  results[reader]={'status':status,'capacity':capacity,'sheets':len(sheets),'quires':len(qs),'observed':observed,'analytical_null_mean':center,'centered':observed-center if observed is not None else None,'empirical_null_mean':avg([x['score'] for x in nullrows]),'positive_centered_quires':positive,'null_method':'EXACT' if exact else 'MONTE_CARLO','orbit_size':orbit,'draws':len(nullrows),'null_at_least_observed':ge,'reference_rank':p}
 result={'status':results['IT2a']['status'],'primary_reader':'IT2a','readers':results,'meanings':0,'causal_production_vs_reading_order_claim':False,'independent_confirmation':False,'significance_claim':False,'pins_verified':True}
 for n,x in [('ELIGIBILITY.json',all_elig),('PREDICTIONS.json',all_pred),('PAGE_RESIDUALS.json',all_pages),('SHEETS.json',all_sheets),('QUIRES.json',all_quires),('NULL_SCORES.json',all_null),('DIAGNOSTICS.json',all_diag),('RESULT.json',result)]:dump(n,x)
 text=['# GDT1156 all retained bifolia','','Residual association only; serial gradients and content remain rival explanations.','','|Reader|Quire|Lower leaf|Upper leaf|Delta lower|Delta upper|Sheet contribution|','|---|---:|---:|---:|---:|---:|---:|']
 for reader,ss in all_sheets.items():
  for s in ss:text.append(f"|{reader}|{s['quire']}|{s['a']}|{s['b']}|{s['delta_a']:.10f}|{s['delta_b']:.10f}|{s['contribution']:.10f}|")
 (E/'CANDIDATE_TABLE.md').write_text('\n'.join(text)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
