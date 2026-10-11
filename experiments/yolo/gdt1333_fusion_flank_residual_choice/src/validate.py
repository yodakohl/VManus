from pathlib import Path
import collections,csv,gzip,hashlib,itertools,json,math,random,re
B=Path(__file__).resolve().parents[1];R=B.parents[2]
U='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def close(a,b):
 if isinstance(a,dict):assert set(a)==set(b);[close(a[k],b[k]) for k in a]
 elif isinstance(a,list):assert len(a)==len(b);[close(x,y) for x,y in zip(a,b)]
 elif isinstance(a,float) or isinstance(b,float):assert abs(a-b)<1e-10,(a,b)
 else:assert a==b,(a,b)
def keys(e):
 s=e['source'];i=e['position'];g=(e['c'],e['h']);local=(*g,s[i-1] if i>0 else 'BOS',s[i+2] if i+2<len(s) else 'EOS');return g,local,(*g,tuple(s),i)
def prep(es):
 ks=[keys(e) for e in es];strata=collections.defaultdict(list)
 for i,k in enumerate(ks):strata[k[1]].append(i)
 mobile={k for k,indices in strata.items() if 0<sum(es[i]['y'] for i in indices)<len(indices)}
 return ks,strata,mobile

def estimate(es,ks,mobile,ys,detail=False):
 tables=[collections.defaultdict(lambda:[0,0]) for _ in range(3)]
 for i,e in enumerate(es):
  if e['train']:
   for t,k in zip(tables,ks[i]):t[k][0]+=ys[i];t[k][1]+=1
 byleaf=collections.defaultdict(list);full=collections.defaultdict(list);localgain=collections.defaultdict(list);details=[];unseen=0;nh=0
 for i,e in enumerate(es):
  if e['train']:continue
  (fg,ng),(fl,nl),(fw,nw)=[t[k] for t,k in zip(tables,ks[i])];pg=(fg+.5)/(ng+1);pl=(fl+2*pg)/(nl+2);pw=(fw+2*pl)/(nw+2);y=ys[i];v=math.log((pw if y else 1-pw)/(pl if y else 1-pl));full[e['leaf']].append(v);ismobile=ks[i][1] in mobile
  if ismobile:
   byleaf[e['leaf']].append(v);localgain[e['leaf']].append(math.log((pl if y else 1-pl)/(pg if y else 1-pg)));nh+=1;unseen+=int(nw==0)
  if nw==0:assert v==0
  if detail:details.append({'event_index':i,'mobile':ismobile,'CH_p':pg,'local_p':pl,'word_site_p':pw,'gain':v,'train_word_site_count':nw})
 per={str(k):math.fsum(v)/len(v) for k,v in sorted(byleaf.items())};value=math.fsum(per.values())/len(per) if per else 0.
 if not detail:return value
 summary={'equal_leaf_gain':value,'mobile_held_opportunities':nh,'mobile_held_leaves':len(per),'positive_leaves':sum(v>0 for v in per.values()),'per_leaf':per,'all_held_opportunities':sum(map(len,full.values())),'all_held_equal_leaf_gain_descriptive':math.fsum(math.fsum(v)/len(v) for v in full.values())/len(full) if full else 0.,'local_vs_CH_mobile_equal_leaf_gain_descriptive':math.fsum(math.fsum(v)/len(v) for v in localgain.values())/len(localgain) if localgain else 0.,'mobile_unseen_word_site_opportunities':unseen,'mobile_strata':len(mobile)}
 return summary,details

def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 data=read(R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz');cached=read(R/'experiments/yolo/gdt1320_optional_fusion_choice/artifacts/OPPORTUNITIES.json.gz');saved=read(B/'artifacts/HELD_SCORES.json.gz');res=read(B/'artifacts/RESULT.json');allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};pattern=re.compile('|'.join(sorted(U,key=lambda s:(-len(s),s))));joins=0;reconstructed={}
 for ed,rows in sorted(data.items()):
  byid={r['id']:r for r in rows};seen=set();metadata={}
  for ph in ('DISCOVERY','EVALUATION'):
   for line in read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{ph}_{ed}.json')['lines']:
    m=line['metadata']
    for g in line['groups']:
     if g[0] not in byid:continue
     r=byid[g[0]];assert g[0] not in seen;seen.add(g[0]);metadata[g[0]]=m;assert m['edition']==ed and m['kind']==r['kind']=='P' and m['page']==r['page'] and m['locus']==r['locus'];assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ('f1r','f116v');assert g[2]==r['ivtff_group_raw']==''.join(r['units']);assert pattern.findall(g[2])==r['units'];assert int(g[1])==int(r['source_group_index']) and g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';joins+=1
  assert seen==set(byid)
  for order in ('BH','HB'):
   events=[]
   for r in rows:
    m=metadata[r['id']]
    if m['currier'] not in ('A','B'):continue
    s=[];origin=[]
    for i,u in enumerate(r['units']):
     expanded=(['ch',u[1]] if order=='BH' else [u[1],'ch']) if u in ('ckh','cth','cph','cfh') else [u];s.extend(expanded);origin.extend([i]*len(expanded))
    leaf=int(re.match(r'f(\d+)',r['page'])[1])
    for j in range(len(s)-1):
     a,b=s[j:j+2]
     if (order=='BH' and a=='ch' and b in ('k','t','p','f')) or (order=='HB' and b=='ch' and a in ('k','t','p','f')):
      h=b if order=='BH' else a;events.append({'id':r['id'],'page':r['page'],'locus':r['locus'],'units':r['units'],'source':s,'position':j,'h':h,'y':int(origin[j]==origin[j+1]),'c':m['currier'],'leaf':leaf,'train':bool(leaf%2)})
   assert events==cached[ed+'_'+order];reconstructed[ed+'_'+order]=events
 checked=0;held=0;maxdiff=0.
 for case,es in sorted(reconstructed.items()):
  ks,strata,mobile=prep(es);ys=[e['y'] for e in es];summary,detail=estimate(es,ks,mobile,ys,True);close(detail,saved[case]);held+=len(detail);observed=res['cases'][case];close(summary,{k:observed[k] for k in summary});cap=summary['mobile_held_opportunities']>=100 and summary['mobile_held_leaves']>=10;null=[];rng=random.Random(1333)
  if cap:
   for rep in range(1999):
    labels=list(ys)
    for k,indices in sorted(strata.items()):
     shuffled=[ys[i] for i in indices];rng.shuffle(shuffled)
     for i,v in zip(indices,shuffled):labels[i]=v
    null.append(estimate(es,ks,mobile,labels))
  close(null,observed['null_scores']);checked+=len(null)
  if null:maxdiff=max(maxdiff,max(abs(a-b) for a,b in zip(null,observed['null_scores'])))
  pv=(1+sum(v>=summary['equal_leaf_gain'] for v in null))/2000 if cap else None;close(pv,observed['monte_carlo_p']);lead=cap and summary['equal_leaf_gain']>=.01 and summary['positive_leaves']*3>=2*summary['mobile_held_leaves'] and pv<=.05/6;assert observed['status']==('NO_MOBILE_CAPACITY' if not cap else ('RESIDUAL_WORD_SITE_GAIN' if lead else 'NO_RETAINED_RESIDUAL_GAIN'));assert observed['opportunities']==len(es);print(case,'validated',flush=True)
 assert res['fixtures']=={'status':'PASS','conditional_allocations':3,'nested_flanks':True,'unseen_fallback_exact':True,'nonmobile_strata_excluded':True}
 # Independently enumerate all conditional one-success configurations on3sites.
 choices=[tuple(int(j==i) for j in range(3)) for i in range(3)];assert len(set(choices))==3 and all(sum(c)==1 for c in choices)
 out={'status':'PASS','source_joins':joins,'held_probabilities_checked':held,'conditional_null_scores_checked':checked,'maximum_null_score_absolute_difference':maxdiff,'method':'Tagged-origin full source reconstruction; independent dictionary train counts, direct held likelihoods and conditional shuffle replay; no runner import.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
