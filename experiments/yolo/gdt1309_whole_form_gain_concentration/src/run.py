import collections,csv,gzip,hashlib,json,math
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
OLD=R/'experiments/yolo/gdt1308_whole_form_prediction/artifacts'
READERS=['ZL3b','IT2a','RF1b']
COLS=['reader','whole','units','train_frequency','train_cells','held_occurrences','held_leaves','contribution','positive_occurrence_mass','negative_occurrence_mass','q_positive','q_zero']
def save(name,x):(B/'artifacts'/name).write_text(json.dumps(x,indent=2)+'\n')
def band(n):return '0' if n==0 else '1' if n==1 else '2-4' if n<5 else '5-19' if n<20 else '20-99' if n<100 else '100+'
def accounting(events,train,cells):
 leafN=collections.Counter(e['leaf'] for e in events); L=len(leafN); byword=collections.defaultdict(list)
 for e in events:byword[tuple(e['units'])].append(e)
 rows=[]
 for w,es in sorted(byword.items()):
  cs=[e['gain']/(L*leafN[e['leaf']]) for e in es]
  rows.append({'whole':''.join(w),'units':' '.join(w),'train_frequency':train[w],'train_cells':cells[w],'held_occurrences':len(es),'held_leaves':len({e['leaf'] for e in es}),'contribution':math.fsum(cs),'positive_occurrence_mass':math.fsum(x for x in cs if x>0),'negative_occurrence_mass':math.fsum(x for x in cs if x<0),'q_positive':sum(e['q']>0 for e in es),'q_zero':sum(e['q']==0 for e in es)})
 positive=sorted([r for r in rows if r['contribution']>0],key=lambda r:(-r['contribution'],tuple(r['units'].split())))
 P=math.fsum(r['contribution'] for r in positive); N=math.fsum(r['contribution'] for r in rows if r['contribution']<0); G=math.fsum(r['contribution'] for r in rows)
 top={str(k):{'types':min(k,len(positive)),'positive_mass':math.fsum(r['contribution'] for r in positive[:k]),'share_of_positive_mass':math.fsum(r['contribution'] for r in positive[:k])/P if P else None} for k in [1,5,10,20,50,100]}
 coverage={}
 for share in [.5,.9]:
  cum=0;needed=0
  for r in positive:
   needed+=1;cum+=r['contribution']
   if cum>=share*P:break
  coverage[str(share)]={'types':needed,'attained_share':cum/P if P else None}
 train_top=sorted(train,key=lambda w:(-train[w],w))[:20]; selected=set(train_top);mask=[r for r in rows if tuple(r['units'].split()) in selected];other=[r for r in rows if tuple(r['units'].split()) not in selected]
 bands={}
 for name in ['0','1','2-4','5-19','20-99','100+']:
  rs=[r for r in rows if band(r['train_frequency'])==name]
  bands[name]={'types':len(rs),'occurrences':sum(r['held_occurrences'] for r in rs),'contribution':math.fsum(r['contribution'] for r in rs),'positive_occurrence_mass':math.fsum(r['positive_occurrence_mass'] for r in rs),'negative_occurrence_mass':math.fsum(r['negative_occurrence_mass'] for r in rs)}
 summary={'held_words':len(events),'held_leaves':L,'held_types':len(rows),'positive_net_types':len(positive),'negative_net_types':sum(r['contribution']<0 for r in rows),'zero_net_types':sum(r['contribution']==0 for r in rows),'positive_type_mass':P,'negative_type_mass':N,'net_gain':G,'occurrence_positive_mass':math.fsum(r['positive_occurrence_mass'] for r in rows),'occurrence_negative_mass':math.fsum(r['negative_occurrence_mass'] for r in rows),'ranked_positive_top':top,'coverage':coverage,'train_top20':{'forms':[''.join(w) for w in train_top],'held_types':len(mask),'held_occurrences':sum(r['held_occurrences'] for r in mask),'original_contribution':math.fsum(r['contribution'] for r in mask),'complement_contribution':math.fsum(r['contribution'] for r in other)},'train_frequency_bands':bands,'top_positive_10':positive[:10],'top_negative_10':sorted([r for r in rows if r['contribution']<0],key=lambda r:(r['contribution'],tuple(r['units'].split())))[:10]}
 return rows,summary

def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 events=json.loads(gzip.decompress((OLD/'EVENTS.json.gz').read_bytes())); model=json.loads((OLD/'MODEL.json').read_text()); old=json.loads((OLD/'RESULT.json').read_text())
 rows=[];results={}
 # Signed-mass fixture: positive mass .3, loss -.2, net .1; positive/net is3.
 assert math.isclose(.3/(.3-.2),3); assert math.isclose(.3/.3,1)
 for reader in READERS:
  train=collections.Counter();cells=collections.Counter()
  for cell in model[reader]['whole']:
   for item in cell['counts']:w=tuple(item['units']);train[w]+=item['count'];cells[w]+=1
  es=[e for e in events if e['reader']==reader];rs,summary=accounting(es,train,cells)
  assert math.isclose(summary['net_gain'],old['readers'][reader]['cohorts']['ALL']['equal_leaf_gain'],abs_tol=1e-12)
  assert math.isclose(summary['positive_type_mass']+summary['negative_type_mass'],summary['net_gain'],abs_tol=1e-12)
  results[reader]=summary;rows.extend({'reader':reader,**r} for r in rs)
 with (B/'artifacts/TYPE_CONTRIBUTIONS.tsv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=COLS,delimiter='\t');writer.writeheader();writer.writerows(rows)
 save('RESULT.json',{'status':'FIXED_SCORE_CONCENTRATION_ACCOUNTED','readers':results,'claim_ceiling':'Post-result attribution, not a selected small dictionary, new predictor, lexical minimum or meaning.'})
 for reader,s in results.items():print(reader,'positive/negative/net',s['positive_type_mass'],s['negative_type_mass'],s['net_gain'],'top20share',s['ranked_positive_top']['20']['share_of_positive_mass'],'coverage',s['coverage'],'TRAINtop20',s['train_top20']['original_contribution'],flush=True)
if __name__=='__main__':main()
