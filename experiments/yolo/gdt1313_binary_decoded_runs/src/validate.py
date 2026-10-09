import collections,csv,gzip,hashlib,json
from pathlib import Path
import numpy as np
B=Path(__file__).resolve().parents[1];R=B.parents[2];A='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
def load(p):return json.loads(p.read_text())
def main():
 for p,h in load(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 source=json.loads(gzip.decompress((R/'experiments/yolo/gdt1233_distinct_initial_fixed_expansion/artifacts/GROUPS.json.gz').read_bytes()));result=load(B/'artifacts/RESULT.json');savedruns=json.loads(gzip.decompress((B/'artifacts/RUNS.json.gz').read_bytes()));allow={r['page'] for r in csv.DictReader((R/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')};joins=checked=0
 for reader in ['ZL3b','IT2a','RF1b']:
  indexed={};metadata={}
  for phase in ['DISCOVERY','EVALUATION']:
   for line in load(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{reader}.json')['lines']:
    for g in line['groups']:indexed[g[0]]=g;metadata[g[0]]=line['metadata']
  rows=source[reader];lookup={};pred={};order=[]
  for r in rows:
   assert r['page'] in allow and not r['page'].startswith('f84') and r['page'] not in ['f1r','f116v'];g=indexed[r['id']];assert g[2]==r['ivtff_group_raw'] and g[3]==g[4]==r['left_separator']==r['right_separator']=='DEFINITE_SPACE';assert int(g[1])==int(r['source_group_index']);assert metadata[r['id']]['kind']==r['kind']=='P' and metadata[r['id']]['page']==r['page'];k=(r['locus'],int(g[1]));assert k not in lookup;lookup[k]=r;order.append(k);joins+=1
  order.sort();blockcount=sum((l,i-1) not in lookup for l,i in order);ks=np.frombuffer(gzip.decompress((R/f'experiments/yolo/gdt1312_binary_whole_code_capacity/artifacts/COUNTS_{reader}.u16.gz').read_bytes()),dtype='<u2');masks=[int(i)*2 for i in range(1,len(ks)) if ks[i]<=32];actual=result['readers'][reader];assert [x['mask'] for x in actual['partitions']]==masks and actual['groups']==len(rows) and actual['blocks']==blockcount
  maxes=[];lettermax=[]
  for mask,expected in zip(masks,actual['partitions']):
   encoded={k:''.join('1' if mask&(1<<A.index(g)) else '0' for g in r['units']) for k,r in lookup.items()};stats={};runs=[];hist=collections.Counter()
   # Start only where the previous original position is absent or differently coded.
   for l,i in order:
    code=encoded[(l,i)]
    if encoded.get((l,i-1))==code:continue
    end=i
    while encoded.get((l,end+1))==code:end+=1
    rr=[lookup[(l,j)] for j in range(i,end+1)];n=len(rr);w={'locus':l,'page':rr[0]['page'],'start_index':i,'length':n,'bits':code,'ids':[r['id'] for r in rr],'raw':[r['ivtff_group_raw'] for r in rr],'indices':list(range(i,end+1))};z=stats.setdefault(code,{'occurrences':0,'maximum':0,'repeated_runs':0,'witness':None});z['occurrences']+=n
    if n>z['maximum']:z['maximum']=n;z['witness']=w
    if n>1:z['repeated_runs']+=1;runs.append(w);hist[str(n)]+=1
   m=sorted((z['maximum'] for z in stats.values()),reverse=True);mx=m[0];lm=m[6] if len(m)>6 else 0
   assert expected['codes']==stats and expected['overall_maximum']==mx and expected['letter_run_lower_bound']==lm and expected['repeated_run_histogram']==dict(hist)
   assert expected['class1']==[s for i,s in enumerate(A) if mask>>i&1]
   assert expected['overall_witnesses']==[z['witness'] for z in stats.values() if z['maximum']==mx]
   assert savedruns[reader][str(mask)]==runs;assert sum(z['occurrences'] for z in stats.values())==len(rows);maxes.append(mx);lettermax.append(lm);checked+=len(stats)
  assert actual['family_character_run_lower_bound']==min(maxes) and actual['family_letter_run_lower_bound']==min(lettermax)
  assert actual['character_bound_attaining_masks']==[m for m,v in zip(masks,maxes) if v==min(maxes)];assert actual['letter_bound_attaining_masks']==[m for m,v in zip(masks,lettermax) if v==min(lettermax)]
 assert joins==result['source_joins']==61181
 out={'status':'PASS','source_joins':joins,'partition_count':sum(len(v['partitions']) for v in result['readers'].values()),'per_code_maxima_checked':checked,'implementation':'independent source-position dictionary and exact successor-window extension; no runner import','ceiling':'Source/sequence/count fidelity, not palaeography, source letters or language rejection.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
