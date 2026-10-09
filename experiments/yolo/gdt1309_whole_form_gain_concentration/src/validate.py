"""Independent score recomputation, per-leaf aggregation and TSV reconstruction."""
import csv,gzip,hashlib,json,math
from collections import defaultdict,Counter
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2];OLD=R/'experiments/yolo/gdt1308_whole_form_prediction/artifacts'
def read(p):return json.loads(p.read_text())
def equal(x,y):assert math.isclose(x,y,abs_tol=1e-11,rel_tol=1e-10),(x,y)
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 events=json.loads(gzip.decompress((OLD/'EVENTS.json.gz').read_bytes()));model=read(OLD/'MODEL.json');old=read(OLD/'RESULT.json');result=read(B/'artifacts/RESULT.json')
 with (B/'artifacts/TYPE_CONTRIBUTIONS.tsv').open() as f:stored=list(csv.DictReader(f,delimiter='\t'))
 checked=0
 for reader in ['ZL3b','IT2a','RF1b']:
  es=[e for e in events if e['reader']==reader];perleaf=defaultdict(list)
  for e in es:perleaf[e['leaf']].append(e)
  contrib=defaultdict(list);pos=defaultdict(list);neg=defaultdict(list);occ=Counter();leafsets=defaultdict(set);qpos=Counter();qzero=Counter();train=Counter();cells=Counter()
  for c in model[reader]['whole']:
   for item in c['counts']:w=tuple(item['units']);train[w]+=item['count'];cells[w]+=1
  for leaf,group in perleaf.items():
   for e in group:
    g=math.log(e['mix'])-math.log(e['p']);equal(g,e['gain']);v=g/len(group)/len(perleaf);w=tuple(e['units']);contrib[w].append(v);occ[w]+=1;leafsets[w].add(leaf);pos[w].append(max(v,0));neg[w].append(min(v,0));qpos[w]+=e['q']>0;qzero[w]+=e['q']==0
  C={w:sum(v) for w,v in contrib.items()};S=result['readers'][reader]
  own=[r for r in stored if r['reader']==reader];assert len(own)==len(C)
  for row in own:
   w=tuple(row['units'].split());assert row['whole']==''.join(w)
   for field,val in [('train_frequency',train[w]),('train_cells',cells[w]),('held_occurrences',occ[w]),('held_leaves',len(leafsets[w])),('q_positive',qpos[w]),('q_zero',qzero[w])]:assert int(row[field])==val,(reader,w,field)
   equal(float(row['contribution']),C[w]);equal(float(row['positive_occurrence_mass']),sum(pos[w]));equal(float(row['negative_occurrence_mass']),sum(neg[w]));checked+=1
  positive=sorted((w for w in C if C[w]>0),key=lambda w:(-C[w],w));negative=sorted((w for w in C if C[w]<0),key=lambda w:(C[w],w));P=sum(C[w] for w in positive);N=sum(C[w] for w in negative);G=sum(C.values())
  assert S['held_words']==len(es) and S['held_leaves']==len(perleaf) and S['held_types']==len(C)
  assert S['positive_net_types']==len(positive) and S['negative_net_types']==len(negative) and S['zero_net_types']==sum(C[w]==0 for w in C)
  for field,v in [('positive_type_mass',P),('negative_type_mass',N),('net_gain',G),('occurrence_positive_mass',sum(sum(v) for v in pos.values())),('occurrence_negative_mass',sum(sum(v) for v in neg.values()))]:equal(S[field],v)
  equal(G,old['readers'][reader]['cohorts']['ALL']['equal_leaf_gain']);equal(P+N,G)
  for k in [1,5,10,20,50,100]:
   a=S['ranked_positive_top'][str(k)];assert a['types']==min(k,len(positive));mass=sum(C[w] for w in positive[:k]);equal(a['positive_mass'],mass);equal(a['share_of_positive_mass'],mass/P)
  for q in [.5,.9]:
   j=next(i for i in range(1,len(positive)+1) if sum(C[w] for w in positive[:i])>=q*P)
   assert S['coverage'][str(q)]['types']==j;equal(S['coverage'][str(q)]['attained_share'],sum(C[w] for w in positive[:j])/P)
  TT=sorted(train,key=lambda w:(-train[w],w))[:20];assert S['train_top20']['forms']==[''.join(w) for w in TT]
  inside=set(C)&set(TT);outside=set(C)-set(TT);equal(S['train_top20']['original_contribution'],sum(C[w] for w in inside));equal(S['train_top20']['complement_contribution'],sum(C[w] for w in outside));assert S['train_top20']['held_types']==len(inside) and S['train_top20']['held_occurrences']==sum(occ[w] for w in inside)
  ranges={'0':(0,0),'1':(1,1),'2-4':(2,4),'5-19':(5,19),'20-99':(20,99),'100+':(100,float('inf'))}
  for name,(lo,hi) in ranges.items():
   ws=[w for w in C if lo<=train[w]<=hi];a=S['train_frequency_bands'][name];assert a['types']==len(ws) and a['occurrences']==sum(occ[w] for w in ws);equal(a['contribution'],sum(C[w] for w in ws));equal(a['positive_occurrence_mass'],sum(sum(pos[w]) for w in ws));equal(a['negative_occurrence_mass'],sum(sum(neg[w]) for w in ws))
  for name,ranking in [('top_positive_10',positive),('top_negative_10',negative)]:
   assert [tuple(r['units'].split()) for r in S[name]]==ranking[:10]
   for r in S[name]:
    w=tuple(r['units'].split());equal(r['contribution'],C[w]);assert r['held_occurrences']==occ[w] and r['held_leaves']==len(leafsets[w]) and r['train_frequency']==train[w]
 equal(.3/(.3-.2),3);equal(.3/.3,1)
 out={'status':'PASS','type_rows_checked':checked,'word_scores_recomputed':len(events),'readers':3,'implementation':'separate log-domain score recomputation and per-leaf/type accounting; no runner imports or model refits','ceiling':'Exact attribution only, not independently tested word shortlist or semantic evidence.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
