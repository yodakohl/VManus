import collections,gzip,hashlib,itertools,json,math
from fractions import Fraction as F
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 d=p.read_bytes();return json.loads(gzip.decompress(d) if p.suffix=='.gz' else d)
def save(n,o):
 d=(json.dumps(o,indent=2)+'\n').encode();(B/'artifacts'/n).write_bytes(gzip.compress(d,mtime=0) if n.endswith('.gz') else d)
def rules_for(types):
 rules=collections.Counter()
 for side in ['FIRST','LAST']:
  groups=collections.defaultdict(set)
  for u in types:groups[u[1:] if side=='FIRST' else u[:-1]].add(u[0] if side=='FIRST' else u[-1])
  for letters in groups.values():
   for a,b in itertools.permutations(sorted(letters),2):rules[side,a,b]+=1
 return rules

def generate(counts,rules):
 N=sum(counts.values());dist=collections.defaultdict(F);fallback=0;paths=0
 for u,c in counts.items():
  choices=[(k,v) for k,v in rules.items() if (k[0]=='FIRST' and k[1]==u[0]) or (k[0]=='LAST' and k[1]==u[-1])];Z=sum(v for k,v in choices)
  if not Z:dist[u]+=F(c,N);fallback+=c;paths+=1;continue
  for (side,a,b),weight in choices:
   w=(b,)+u[1:] if side=='FIRST' else u[:-1]+(b,);dist[w]+=F(c*weight,N*Z);paths+=1
 assert sum(dist.values())==1
 return dist,fallback,paths

def fixtures():
 counts={tuple(w):1 for w in ['aaaa','baaa','aabb','aaab','cccc']};rules=rules_for(set(counts));dist,fallback,paths=generate(counts,rules);assert dist[tuple('babb')]>0 and tuple('babb') not in counts;assert fallback==1 and dist[tuple('cccc')]==F(1,5)
 # baaa and aaab each have a return path to aaaa.
 expected=sum(F(1,5)*F(rules[k],sum(v for j,v in rules.items() if (j[0]=='FIRST' and j[1]==u[0]) or (j[0]=='LAST' and j[1]==u[-1]))) for u,k in [(tuple('baaa'),('FIRST','b','a')),(tuple('aaab'),('LAST','b','a'))]);assert dist[tuple('aaaa')]==expected
 return {'status':'PASS','novel_transfer':'babb','fallback':'cccc','multiple_path_output':'aaaa','mass':'1'}
def summarize(events):
 out={}
 for cohort in ['ALL','GLOBAL_UNSEEN','GLOBAL_KNOWN','E_POSITIVE','E_ZERO']:
  es=[e for e in events if cohort=='ALL' or cohort=='GLOBAL_UNSEEN' and e['global_unseen'] or cohort=='GLOBAL_KNOWN' and not e['global_unseen'] or cohort=='E_POSITIVE' and e['edit_p']>0 or cohort=='E_ZERO' and e['edit_p']==0];leaves=collections.defaultdict(list)
  for e in es:leaves[e['leaf']].append(e)
  po={str(k):sum(e['gain_old'] for e in v)/len(v) for k,v in sorted(leaves.items())};pm={str(k):sum(e['gain_m1'] for e in v)/len(v) for k,v in sorted(leaves.items())};N=len(es);L=len(po);mean=sum(po.values())/L if L else None;pos=sum(v>0 for v in po.values())
  out[cohort]={'words':N,'leaves':L,'positive_leaves_old':pos,'equal_leaf_gain_old':mean,'equal_leaf_gain_m1':sum(pm.values())/L if L else None,'token_gain_old':sum(e['gain_old'] for e in es)/N if N else None,'per_leaf_old':po,'per_leaf_m1':pm,'material_gate':bool(N>=100 and L>=10 and mean>=.01 and pos*3>=2*L)}
 return out

def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixtures();old=R/'experiments/yolo/gdt1308_whole_form_prediction/artifacts';models=read(old/'MODEL.json');events=read(old/'EVENTS.json.gz');results={};allrules={};distributions={};all_events=[]
 for ed in ['ZL3b','IT2a','RF1b']:
  counts={tuple(x['cell']):{tuple(w['units']):w['count'] for w in x['counts']} for x in models[ed]['whole']};types=collections.defaultdict(set)
  for (c,n),ws in counts.items():types[c].update(ws)
  rules={c:rules_for(ws) for c,ws in types.items()};allrules[ed]={c:[{'side':k[0],'old':k[1],'new':k[2],'count':v} for k,v in sorted(rr.items())] for c,rr in sorted(rules.items())};E={};cells=[]
  for cell,ws in sorted(counts.items()):
   dist,fallback,paths=generate(ws,rules[cell[0]]);E[cell]=dist;cells.append({'cell':cell,'N':sum(ws.values()),'fallback_tokens':fallback,'paths':paths,'mass':'1','outputs':[{'units':u,'p':float(p)} for u,p in sorted(dist.items())]})
  distributions[ed]=cells;es=[]
  for e in events:
   if e['reader']!=ed:continue
   u=tuple(e['units']);cell=(e['c'],len(u));p=float(E[cell].get(u,0)) if cell in E else 0;new=.5*e['p']+.25*e['q']+.25*p if cell in E else e['p'];es.append({**e,'edit_p':p,'new_p':new,'gain_old':math.log(new/e['mix']),'gain_m1':math.log(new/e['p'])})
  scores=summarize(es);novel=[e for e in es if e['global_unseen'] and e['edit_p']>0];coverage={'words':len(novel),'leaves':len({e['leaf'] for e in novel})};coverage['gate']=coverage['words']>=100 and coverage['leaves']>=10;lead=scores['ALL']['material_gate'] and coverage['gate'];results[ed]={'cohorts':scores,'novel_edit_coverage':coverage,'lead':lead,'rule_entries':sum(map(len,rules.values())),'ordered_training_pair_supports':sum(sum(rr.values()) for rr in rules.values()),'generated_cell_outputs':sum(len(v) for v in E.values()),'train_whole_cell_entries':sum(map(len,counts.values()))};all_events.extend(es);print(ed,'lead',lead,'ALLvsOLD',scores['ALL']['equal_leaf_gain_old'],'positive',scores['ALL']['positive_leaves_old'],'novel',coverage,flush=True)
 save('RULES.json',allrules);save('EDIT_DISTRIBUTIONS.json.gz',distributions);save('EVENTS.json.gz',all_events);save('RESULT.json',{'status':'BOUNDARY_EDIT_PREDICTIVE_LEAD' if results['ZL3b']['lead'] else 'NO_BOUNDARY_EDIT_PREDICTIVE_LEAD','fixtures':fx,'readers':results,'ceiling':'Fixed normalized spelling predictor only; no semantic edit meaning, inverse sourcewriter or mechanism rejection.'})
if __name__=='__main__':main()
