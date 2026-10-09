import collections,csv,gzip,hashlib,itertools,json
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2];A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split();READERS=['ZL3b','IT2a','RF1b']
def save(n,x):(B/'artifacts'/n).write_text(json.dumps(x,indent=2)+'\n')
def projection(u,mask):return ''.join(str((mask>>A.index(s))&1) for s in u)
def witness(rows,code):return {'locus':rows[0]['locus'],'page':rows[0]['page'],'start_index':int(rows[0]['source_group_index']),'length':len(rows),'bits':code,'ids':[r['id'] for r in rows],'raw':[r['ivtff_group_raw'] for r in rows],'indices':[int(r['source_group_index']) for r in rows]}
def blocks(rows):
 by=collections.defaultdict(list)
 for r in rows:by[r['locus']].append(r)
 out=[]
 for locus,rs in sorted(by.items()):
  rs.sort(key=lambda r:int(r['source_group_index']));current=[]
  for r in rs:
   if current and int(r['source_group_index'])!=int(current[-1]['source_group_index'])+1:out.append(current);current=[]
   current.append(r)
  if current:out.append(current)
 return out

def measure(bs,mask):
 stats={};repeats=[];hist=collections.Counter()
 for block in bs:
  for code,iterator in itertools.groupby(block,key=lambda r:projection(r['units'],mask)):
   rs=list(iterator);w=witness(rs,code);z=stats.setdefault(code,{'occurrences':0,'maximum':0,'repeated_runs':0,'witness':None});z['occurrences']+=len(rs)
   if len(rs)>z['maximum']:z['maximum']=len(rs);z['witness']=w
   if len(rs)>=2:z['repeated_runs']+=1;repeats.append(w);hist[len(rs)]+=1
 maxima=sorted((z['maximum'] for z in stats.values()),reverse=True);overall=max(maxima);letter=maxima[6] if len(maxima)>6 else 0
 return {'mask':mask,'class1':[s for i,s in enumerate(A) if mask>>i&1],'codes':{c:stats[c] for c in sorted(stats,key=lambda x:(len(x),x))},'overall_maximum':overall,'letter_run_lower_bound':letter,'repeated_run_histogram':dict(sorted(hist.items())),'overall_witnesses':[z['witness'] for z in stats.values() if z['maximum']==overall]},repeats

def fixtures():
 def row(locus,i,word):return {'locus':locus,'page':'toy','source_group_index':i,'id':f'{locus}:{i}','ivtff_group_raw':word,'units':list(word)}
 rs=[row('toy.1',1,'ao'),row('toy.1',2,'oa'),row('toy.1',4,'aa'),row('toy.2',1,'oo')];bs=blocks(rs);assert list(map(len,bs))==[2,1,1]
 s,_=measure(bs,1<<A.index('m'));assert s['overall_maximum']==2 and s['codes']['00']['occurrences']==4
 s,_=measure([[row('toy.1',1,'a'),row('toy.1',2,'aa')]],1<<A.index('m'));assert s['overall_maximum']==1 and len(s['codes'])==2
 assert sorted([9,8,7,6,5,4,3,2],reverse=True)[6]==3
 return {'status':'PASS','gap_and_line_breaks':True,'different_forms_same_bits':True,'leading_zero_length':True,'seventh_rank_pigeonhole':3}

def main():
 for p,h in json.loads((B/'src/REGISTRATION_LOCK.json').read_text())['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 fx=fixtures();data=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));previous=json.loads((R/'experiments/yolo/gdt1312_binary_whole_code_capacity/artifacts/RESULT.json').read_text());allowed={q['page'] for q in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};res={};allruns={};joined=0
 for reader in READERS:
  lines={}
  for phase in ['DISCOVERY','EVALUATION']:
   for l in json.loads((R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{reader}.json').read_text())['lines']:lines[l['metadata']['locus']]=l
  for r in data[reader]:
   assert r['page'] in allowed and not r['page'].startswith('f84') and r['page'] not in ['f1r','f116v'];assert r['kind']=='P' and r['left_separator']==r['right_separator']=='DEFINITE_SPACE';l=lines[r['locus']];g=next(g for g in l['groups'] if g[0]==r['id']);assert int(g[1])==int(r['source_group_index']) and g[2]==r['ivtff_group_raw'] and g[3]==g[4]=='DEFINITE_SPACE' and l['metadata']['page']==r['page'];joined+=1
  bs=blocks(data[reader]);ks=np.frombuffer(gzip.decompress((R/f'experiments/yolo/gdt1312_binary_whole_code_capacity/artifacts/COUNTS_{reader}.u16.gz').read_bytes()),dtype='<u2');masks=[int(i)<<1 for i in np.flatnonzero(ks<=32) if i];assert len(masks)==previous['readers'][reader]['feasible_at_most32'];out=[];runs={}
  for mask in masks:
   s,rr=measure(bs,mask);assert len(s['codes'])==int(ks[mask>>1]);out.append(s);runs[str(mask)]=rr
  mn=min(s['overall_maximum'] for s in out);ml=min(s['letter_run_lower_bound'] for s in out)
  res[reader]={'groups':len(data[reader]),'blocks':len(bs),'partitions':out,'family_character_run_lower_bound':mn,'character_bound_attaining_masks':[s['mask'] for s in out if s['overall_maximum']==mn],'family_letter_run_lower_bound':ml,'letter_bound_attaining_masks':[s['mask'] for s in out if s['letter_run_lower_bound']==ml]};allruns[reader]=runs
  print(reader,'character bound',mn,'letter bound',ml,'perkey',[(s['class1'],s['overall_maximum'],s['letter_run_lower_bound']) for s in out],flush=True)
 save('RESULT.json',{'status':'DECODED_RUN_OBLIGATIONS','source_joins':joined,'fixtures':fx,'readers':res,'ceiling':'Conditional equal decoded values/continuous block runs; no plaintext character assignment or language exclusion.'});(B/'artifacts/RUNS.json.gz').write_bytes(gzip.compress(json.dumps(allruns,separators=(',',':')).encode(),mtime=0))
if __name__=='__main__':main()
