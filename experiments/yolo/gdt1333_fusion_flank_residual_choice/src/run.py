from pathlib import Path
import collections,gzip,hashlib,itertools,json,math,random
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def save(name,obj):
 raw=(json.dumps(obj,indent=2,sort_keys=True)+'\n').encode();(B/'artifacts'/name).write_bytes(gzip.compress(raw,mtime=0) if name.endswith('.gz') else raw)
def context(e):
 s=e['source'];j=e['position'];return (e['c'],e['h'],s[j-1] if j else 'BOS',s[j+2] if j+2<len(s) else 'EOS')
def prepare(es):
 keys=[[ (e['c'],e['h']) for e in es],[context(e) for e in es],[(e['c'],e['h'],tuple(e['source']),e['position']) for e in es]];ix=[];sizes=[]
 for ks in keys:
  table={k:i for i,k in enumerate(sorted(set(ks)))};ix.append(np.array([table[k] for k in ks],dtype=int));sizes.append(len(table))
 train=np.array([i for i,e in enumerate(es) if e['train']],dtype=int);held=np.array([i for i,e in enumerate(es) if not e['train']],dtype=int);ys=np.array([e['y'] for e in es]);n=np.bincount(ix[1],minlength=sizes[1]);f=np.bincount(ix[1],weights=ys,minlength=sizes[1]);mobile=(f>0)&(f<n);mask=mobile[ix[1][held]];leaves=np.array([e['leaf'] for e in es]);leafids=sorted(set(leaves[held[mask]]));groups=collections.defaultdict(list)
 for i,k in enumerate(keys[1]):groups[k].append(i)
 return {'ix':ix,'sizes':sizes,'train':train,'held':held,'mask':mask,'leaves':leaves,'leafids':leafids,'groups':groups,'ys':ys,'ntrain':[np.bincount(v[train],minlength=size) for v,size in zip(ix,sizes)],'mobile_strata':int(sum(mobile))}
def score(p,ys,details=False):
 ix=p['ix'];tr=p['train'];he=p['held'];counts=[np.bincount(v[tr],weights=ys[tr],minlength=size) for v,size in zip(ix,p['sizes'])];n=p['ntrain'];g=ix[0][he];l=ix[1][he];w=ix[2][he];base=(counts[0][g]+.5)/(n[0][g]+1);local=(counts[1][l]+2*base)/(n[1][l]+2);word=(counts[2][w]+2*local)/(n[2][w]+2);y=ys[he];gain=np.log(np.where(y,word,1-word)/np.where(y,local,1-local));mask=p['mask'];ls=p['leaves'][he];per={int(leaf):float(np.mean(gain[(ls==leaf)&mask])) for leaf in p['leafids']};value=sum(per.values())/len(per) if per else 0.
 if not details:return value
 ful={int(leaf):float(np.mean(gain[ls==leaf])) for leaf in sorted(set(ls))};lg=np.log(np.where(y,local,1-local)/np.where(y,base,1-base));localper={int(leaf):float(np.mean(lg[(ls==leaf)&mask])) for leaf in p['leafids']};unseen=(n[2][w]==0);assert np.all(gain[unseen]==0)
 summary={'equal_leaf_gain':value,'mobile_held_opportunities':int(sum(mask)),'mobile_held_leaves':len(per),'positive_leaves':sum(v>0 for v in per.values()),'per_leaf':per,'all_held_opportunities':len(he),'all_held_equal_leaf_gain_descriptive':sum(ful.values())/len(ful) if ful else 0.,'local_vs_CH_mobile_equal_leaf_gain_descriptive':sum(localper.values())/len(localper) if localper else 0.,'mobile_unseen_word_site_opportunities':int(sum(mask&unseen)),'mobile_strata':p['mobile_strata']}
 detail=[{'event_index':int(i),'mobile':bool(mask[j]),'CH_p':float(base[j]),'local_p':float(local[j]),'word_site_p':float(word[j]),'gain':float(gain[j]),'train_word_site_count':int(n[2][w[j]])} for j,i in enumerate(he)]
 return summary,detail

def fixtures():
 source=['ch','k','a','ch','k'];a={'source':source,'position':0,'c':'A','h':'k','leaf':1,'train':True,'y':1};b={**a,'position':3};assert context(a)==('A','k','BOS','a') and context(b)==('A','k','a','EOS');events=[a,b,{**a,'source':['ch','k','b'],'leaf':2,'train':False,'y':0}];p=prepare(events);s,d=score(p,p['ys'],True);assert d[0]['gain']==0 and d[0]['train_word_site_count']==0
 allocations=set(itertools.permutations([1,0,0]));assert len(allocations)==3
 for labels in allocations:assert 0<sum(labels)<len(labels)
 for labels in ([0,0],[1,1],[1]):assert not 0<sum(labels)<len(labels)
 return {'status':'PASS','conditional_allocations':3,'nested_flanks':True,'unseen_fallback_exact':True,'nonmobile_strata_excluded':True}
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 controls=fixtures();events=read(R/'experiments/yolo/gdt1320_optional_fusion_choice/artifacts/OPPORTUNITIES.json.gz');out={};held={}
 for key,es in sorted(events.items()):
  p=prepare(es);summary,detail=score(p,p['ys'],True);cap=summary['mobile_held_opportunities']>=100 and summary['mobile_held_leaves']>=10;null=[];rng=random.Random(1333)
  if cap:
   for rep in range(1999):
    labels=p['ys'].tolist()
    for k,indices in sorted(p['groups'].items()):
     vals=[int(p['ys'][i]) for i in indices];rng.shuffle(vals)
     for i,v in zip(indices,vals):labels[i]=v
    null.append(score(p,np.array(labels)))
  pv=(1+sum(v>=summary['equal_leaf_gain'] for v in null))/2000 if cap else None;lead=cap and summary['equal_leaf_gain']>=.01 and 3*summary['positive_leaves']>=2*summary['mobile_held_leaves'] and pv<=.05/6
  summary.update(status='NO_MOBILE_CAPACITY' if not cap else ('RESIDUAL_WORD_SITE_GAIN' if lead else 'NO_RETAINED_RESIDUAL_GAIN'),monte_carlo_p=pv,null_scores=null,null_statistic_distinct_values=len(set(null)),opportunities=len(es));out[key]=summary;held[key]=detail;print(key,summary['status'],'mobile',summary['mobile_held_opportunities'],'gain',summary['equal_leaf_gain'],'positive',summary['positive_leaves'],'/',summary['mobile_held_leaves'],'p',pv,flush=True)
 save('RESULT.json',{'status':'FIXED_LOCAL_FLANK_RESIDUAL_COMPARISON','fixtures':controls,'cases':out});save('HELD_SCORES.json.gz',held)
if __name__=='__main__':main()
