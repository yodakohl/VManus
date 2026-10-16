"""Prepare frozen spelling and source models; never generate controls."""
import collections,csv,gzip,hashlib,json,re
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parents[1]; R=B.parents[2]
SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
LANGS='latin middle_high_german middle_french old_italian_tuscan medieval_czech old_hungarian'.split()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p): return json.loads(gzip.decompress(p.read_bytes()) if p.suffix=='.gz' else p.read_text())
def save(p,obj):
 data=(json.dumps(obj,separators=(',',':'),ensure_ascii=False)+'\n').encode(); p.write_bytes(gzip.compress(data,mtime=0) if p.suffix=='.gz' else data)
def source(lang,manifest):
 p=R/f'.gdt001/language_packs/{lang}.txt'; assert sha(p)==manifest['packs'][lang]['prepared_sha256']
 s=' '.join(p.read_text().split()); assert set(s)<=set(' abcdefghijklmnopqrstuvwxyz')
 return p,s

def main():
 inputs=[]
 def pinned(rel):
  p=R/rel; inputs.append({'path':rel,'sha256':sha(p)}); return load(p)
 allowpath='experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
 allowed={r['page'] for r in csv.DictReader((R/allowpath).open(),delimiter='\t')}; inputs.append({'path':allowpath,'sha256':sha(R/allowpath)})
 data=pinned('experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz')['IT2a']; lines={}
 for phase in ['DISCOVERY','EVALUATION']:
  d=pinned(f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_IT2a.json')
  for line in d['lines']: lines[line['metadata']['locus']]=line
 counts=collections.defaultdict(collections.Counter); whole=collections.defaultdict(collections.Counter); lengths=collections.Counter(); ids=[]
 for row in data:
  assert row['page'] in allowed and not row['page'].startswith('f84') and row['page'] not in ['f1r','f116v']
  line=lines[row['locus']]; m=line['metadata']; g=next(g for g in line['groups'] if g[0]==row['id'])
  assert g[2]==row['ivtff_group_raw'] and row['kind']==m['kind']=='P' and row['page']==m['page'] and m['edition']=='IT2a'
  assert row['left_separator']==row['right_separator']=='DEFINITE_SPACE' and ''.join(row['units'])==row['ivtff_group_raw'] and set(row['units'])<=set(SIGNS)
  if int(re.match(r'f(\d+)',row['page'])[1])%2!=1 or m['currier']!='B': continue
  u=tuple(row['units']); n=len(u); assert n>0; ids.append(row['id']); lengths[n]+=1; whole[n][u]+=1
  for i,s in enumerate(u): counts[(n,i,u[i-1] if i else '^')][s]+=1
 old=pinned('experiments/yolo/gdt1308_whole_form_prediction/artifacts/MODEL.json')['IT2a']
 lock=pinned('experiments/yolo/gdt1308_whole_form_prediction/artifacts/MODEL_LOCK.json'); assert inputs[-2]['sha256']==lock['sha256']
 oldm={tuple(x['context'][1:]):x['counts'] for x in old['m1'] if x['context'][0]=='B'}
 assert {k:dict(v) for k,v in counts.items() if k[0]>=4}==oldm
 oldw={x['cell'][1]:{tuple(t['units']):t['count'] for t in x['counts']} for x in old['whole'] if x['cell'][0]=='B'}
 assert {n:dict(v) for n,v in whole.items() if n>=4}==oldw
 L=max(27,max(lengths)); N=sum(lengths.values())
 def prob(n,i,prev):
  c=counts.get((n,i,prev),{}); return [(c.get(s,0)+.5)/(sum(c.values())+11) for s in SIGNS]
 shape={'signs':SIGNS,'L':L,'p_len':[0]+[(lengths[n]+.5)/(N+.5*L) for n in range(1,L+1)],'initial':[[0]*22]+[prob(n,0,'^') for n in range(1,L+1)],'transition':[[]]+[[[prob(n,i,p) for p in SIGNS] for i in range(1,n)] for n in range(1,L+1)],'provenance':{'reader':'IT2a','currier':'B','partition':'odd physical leaf TRAIN','inputs':inputs,'train_groups':N,'source_ids':ids,'length_counts':dict(sorted(lengths.items())),'m1':[{'context':['B',*k],'counts':dict(v)} for k,v in sorted(counts.items())],'whole':[{'cell':['B',n],'counts':[{'units':u,'count':c} for u,c in sorted(v.items())]} for n,v in sorted(whole.items())],'old_long_counts_exact':True}}
 save(B/'artifacts/SHAPE.json.gz',shape)
 manifestpath=R/'gdt001_language_pack_manifest.json'; manifest=load(manifestpath); models=[]
 for lang in LANGS:
  p,s=source(lang,manifest); split=4*len(s)//5; raw=np.frombuffer(s[:split].encode('ascii'),dtype=np.uint8).astype(np.int64); a=np.where(raw==32,0,raw-96); c=np.zeros((20440,27),dtype=np.int64)
  c[0]=np.bincount(a,minlength=27)
  for k in [1,2,3]:
   idx=np.full(len(a)-k,[0,1,28,757][k],dtype=np.int64)
   for j in range(k): idx+=a[j:len(a)-k+j]*(27**(k-1-j))
   np.add.at(c,(idx,a[k:]),1)
  logp=np.log((c+.5)/(c.sum(axis=1)[:,None]+13.5))
  out=B/f'artifacts/SOURCE_{lang}.json.gz'; save(out,{'language':lang,'logp':logp.tolist()})
  starts=[i for i in range(split,len(s)-119) if (i==0 or s[i-1]==' ') and s[i]!=' ']; assert len(starts)>=2 and starts[-1]-starts[0]>=120
  models.append({'language':lang,'path':str(out.relative_to(R)),'sha256':sha(out),'source_path':str(p.relative_to(R)),'source_sha256':sha(p),'collapsed_sha256':hashlib.sha256(s.encode()).hexdigest(),'characters':len(s),'split_index':split,'train_characters':split,'suffix_characters':len(s)-split})
  print('Prepared source model',lang,flush=True)
 save(B/'artifacts/MODELS.json',{'models':models,'shape':{'path':str((B/'artifacts/SHAPE.json.gz').relative_to(R)),'sha256':sha(B/'artifacts/SHAPE.json.gz')},'manifest':{'path':str(manifestpath.relative_to(R)),'sha256':sha(manifestpath)},'source_order':3,'source_alpha':.5,'fragment_selection':'Uniform eligible suffix word-boundary 77 start, then uniform disjoint eligible suffix word-boundary 120 start; no resampling.','inputs':inputs})
if __name__=='__main__': main()
