#!/usr/bin/env python3
"""Independent intake/filter/summary replay using frozen893 explicit-map window oracle."""
import csv,gzip,json,hashlib,re,subprocess,tempfile
from pathlib import Path
from collections import Counter,defaultdict
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2];OLD=E.parent/'gdt893_global_source_montage_word_code';EDS=['RF1b','ZL3b','IT2a','CONSENSUS']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def logical(p):return p.read_bytes() if p.exists() else gzip.decompress(Path(str(p)+'.gz').read_bytes())
def phash(words):return hashlib.sha256(json.dumps(words,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
def conflict(words,plain,key):
 rev={v:k for k,v in key.items()}
 for c,p in zip(words,plain):
  if c in key and key[c]!=p:return 'forward:'+c
  if p in rev and rev[p]!=c:return 'inverse:'+rev[p]
 return None

def intake(cache,key):
 count=Counter();panels={ed:[] for ed in EDS}
 for f in cache['frames']:
  assert not f['page'].startswith('f84') and re.fullmatch('f[0-9]+',f['physical_folio'])
  n=int(f['physical_folio'][1:])
  if n%2:count['odd_frames_not_screened']+=1;continue
  count['even_frames']+=1
  for ed in EDS:
   r=f['readings'][ed];assert r['eligible']==(not r['reasons'])
   if not r['eligible']:count[ed+'_ineligible']+=1;continue
   groups=r['groups'];assert groups and all(re.fullmatch('[a-z]+',g['raw']) and g['sta'] and g['kind']=='P' for g in groups)
   if ed=='CONSENSUS':
    fields=lambda r:[(g['raw'],g['sta'],g['locus']) for g in r['groups']]
    assert all(f['readings'][d]['eligible'] and fields(f['readings'][d])==fields(r) for d in EDS[:3])
   words=[g['raw'] for g in groups];kt=sorted(set(words)&key.keys())
   panels[ed].append(dict(fold='A' if n%4==0 else 'B',id=f['paragraph_id'],informative=len(kt)>=2,locked_tokens=sum(w in key for w in words),locked_types=kt,page=f['page'],physical_folio=f['physical_folio'],source_group_ids=[g['source_group_id'] for g in groups],words=words))
 return dict(intake=dict(count),key=key,panels=panels,schema='GDT923_FROZEN_KEY_PREDICTIONS')
def write_records(path,seqs):
 vocab={}
 with path.open('w') as f:
  f.write(str(len(seqs))+'\n')
  for i,seq in enumerate(seqs):
   ids=[vocab.setdefault(w,len(vocab)) for w in seq]
   f.write(' '.join(map(str,[i,len(seq)]+ids))+'\n')
def rows_csv(path,zipped=False):
 with (gzip.open(path,'rt',newline='') if zipped else path.open(newline='')) as f:return [tuple(map(int,r)) for r in list(csv.reader(f))[1:]]
def summary(rows):
 inf=[r for r in rows if r['informative']];sur=[r for r in rows if r['compatible_windows']];bi=[r for r in inf if r['baseline_windows']];si=[r for r in inf if r['compatible_windows']]
 return dict(paragraphs=len(rows),physical_leaves=len({r['physical_folio'] for r in rows}),zero_key_paragraphs=sum(r['locked_types']==0 for r in rows),one_key_paragraphs=sum(r['locked_types']==1 for r in rows),informative_paragraphs=len(inf),informative_leaves=len({r['physical_folio'] for r in inf}),baseline_positive_paragraphs=sum(r['baseline_windows']>0 for r in rows),baseline_windows=sum(r['baseline_windows'] for r in rows),compatible_paragraphs=len(sur),compatible_windows=sum(r['compatible_windows'] for r in rows),informative_baseline_positive=len(bi),informative_compatible_paragraphs=len(si),informative_compatible_leaves=len({r['physical_folio'] for r in si}))
def fixtures():
 assert conflict(['a'],['x'],{'a':'x'}) is None
 assert conflict(['b'],['x'],{'a':'x'})=='inverse:a'
 assert conflict(['a'],['y'],{'a':'x'})=='forward:a'
 assert conflict(['b'],['z'],{'a':'x'}) is None
 return 4

def main():
 for p,h in read(E/'PREREG_LOCK.json').items():assert sha(E/p)==h,p
 spec=read(E/'src/SOURCE.json')
 for row in spec['inputs']:assert sha(ROOT/row['path'])==row['sha256']
 assert sha(E/'artifacts/SOURCE_UNITS.json')==spec['source_units_sha256']
 for p,h in read(E/'artifacts/PREDICTION_LOCK.json').items():assert sha(E/'artifacts'/p)==h
 key=read(OLD/'artifacts/RF_FORCED_SOURCE.json')['conditional_global_map'];assert len(key)==len(set(key.values()))==26
 cache=read(E.parent/'gdt887_tacuinum_joint_entry_reconstruction/artifacts/SELECTED.json');packet=intake(cache,key);assert packet==read(E/'artifacts/PREDICTION_PACKET.json')
 expectedpred=[]
 for ed,ts in packet['panels'].items():
  for t in ts:
   for i,(w,gid) in enumerate(zip(t['words'],t['source_group_ids'])):expectedpred.append(dict(edition=ed,paragraph=t['id'],page=t['page'],physical_folio=t['physical_folio'],fold=t['fold'],index=str(i),source_group_id=gid,cipher_word=w,prediction=key.get(w,'UNKNOWN')))
 with (E/'artifacts/PREDICTIONS.tsv').open(newline='') as f:actual=list(csv.DictReader(f,delimiter='\t'))
 canonical=lambda rows:sorted(json.dumps(x,sort_keys=True) for x in rows)
 assert canonical(expectedpred)==canonical(actual)
 units=read(E/'artifacts/SOURCE_UNITS.json')['units'];allparas=[];witnesses=[];keyresults={};summaries={};oraclecounts={}
 with tempfile.TemporaryDirectory(prefix='gdt923_independent_') as tmp:
  d=Path(tmp);binary=d/'oracle';oracle=OLD/'src/validate_windows.cpp'
  subprocess.run(['g++','-O3','-std=c++17',str(oracle),'-o',str(binary)],check=True,capture_output=True)
  write_records(d/'source.txt',[u['words'] for u in units])
  # Direct oracle checks repeated words, incompatible repeated values and no source-unit bridging.
  write_records(d/'toy_source.txt',[['x','y','x'],['u'],['v']]);write_records(d/'toy_target.txt',[['a','b','a'],['a','a'],['a','b']])
  subprocess.run([str(binary),str(d/'toy_target.txt'),str(d/'toy_source.txt'),str(d/'toy.csv')],check=True,capture_output=True)
  assert rows_csv(d/'toy.csv')==[(0,0,0,3),(2,0,0,2),(2,0,1,2)]
  for ed,targets in packet['panels'].items():
   write_records(d/'target.txt',[t['words'] for t in targets]);proc=subprocess.run([str(binary),str(d/'target.txt'),str(d/'source.txt'),str(d/'oracle.csv')],check=True,capture_output=True,text=True)
   baseline=rows_csv(d/'oracle.csv');actual=rows_csv(E/'artifacts'/f'{ed}_BASELINE_WINDOWS.csv.gz',True);assert baseline==actual,ed
   oraclecounts[ed]=json.loads(proc.stdout);bytarget=defaultdict(list)
   for row in baseline:bytarget[row[0]].append(row)
   kr={k:dict(value=v,positions=0,paragraphs=0,compatible_paragraphs=0,first_forward_conflicts=0,first_inverse_conflicts=0) for k,v in key.items()};ers=[]
   for ti,t in enumerate(targets):
    n=len(t['words']);conf=Counter();hashes=set();survive=0
    for _,si,start,length in bytarget[ti]:
     assert length==n;u=units[si];plain=u['words'][start:start+n];bad=conflict(t['words'],plain,key)
     if bad:
      conf[bad]+=1;direction,k=bad.split(':');kr[k]['first_'+direction+'_conflicts']+=1;continue
     h=phash(plain);hashes.add(h);survive+=1;witnesses.append(dict(edition=ed,informative=t['informative'],length=n,paragraph=t['id'],plaintext_sha256=h,source=u['source'],start=start,unit=u['id']))
    for k in t['locked_types']:
     kr[k]['positions']+=t['words'].count(k);kr[k]['paragraphs']+=1;kr[k]['compatible_paragraphs']+=int(survive>0)
    nb=len(bytarget[ti]);r=dict(baseline_windows=nb,compatible_windows=survive,distinct_compatible_plaintexts=len(hashes),edition=ed,first_conflicts=dict(conf),fold=t['fold'],informative=t['informative'],length=n,locked_tokens=t['locked_tokens'],locked_types=len(t['locked_types']),outcome='COMPATIBLE' if survive else 'FIXED_KEY_CONTRADICTION' if nb else 'NO_BASELINE_PATTERN_WINDOW',page=t['page'],paragraph=t['id'],physical_folio=t['physical_folio']);ers.append(r)
   allparas.extend(ers);keyresults[ed]=kr;summaries[ed]=summary(ers);summaries[ed]['folds']={f:summary([r for r in ers if r['fold']==f]) for f in ['A','B']};summaries[ed]['matcher']=dict(matches=len(baseline),source_units=len(units),status='COMPLETE',target_paragraphs=len(targets))
 assert allparas==read(E/'artifacts/PARAGRAPH_RESULTS.json')
 with (E/'artifacts/PARAGRAPH_RESULTS.tsv').open(newline='') as f:
  table=list(csv.DictReader(f,delimiter='\t'))
 assert len(table)==len(allparas) and all(all(str(r[k])==v for k,v in row.items()) for row,r in zip(table,allparas))
 assert keyresults==read(E/'artifacts/KEY_RESULTS.json')
 witnessbytes=logical(E/'artifacts/WITNESSES.json');assert witnesses==json.loads(witnessbytes)
 result=read(E/'artifacts/RESULT.json');assert result['panels']==summaries and result['intake']==packet['intake'];assert result['confirmed_meanings']==0
 expected_status='CAPACITY_STOP' if not summaries['RF1b']['informative_paragraphs'] else 'HAS_INFORMATIVE_COMPATIBILITY' if summaries['RF1b']['informative_compatible_paragraphs'] else 'NO_INFORMATIVE_COMPATIBILITY'
 assert result['status']==expected_status and result['prediction_lock_sha256']==sha(E/'artifacts/PREDICTION_LOCK.json')
 receipt=dict(status='PASS',validator_sha256=sha(Path(__file__)),independent_window_oracle_sha256=sha(OLD/'src/validate_windows.cpp'),prereg_lock_sha256=sha(E/'PREREG_LOCK.json'),source_units_sha256=sha(E/'artifacts/SOURCE_UNITS.json'),witnesses_logical_sha256=hashlib.sha256(witnessbytes).hexdigest(),output_sha256={p.name:sha(p) for p in sorted((E/'artifacts').glob('*.json')) if p.name not in ['VALIDATION.json','WITNESSES.json']},panels=summaries,oracle_counts=oraclecounts,prediction_positions=len(expectedpred),synthetic_filter_checks=fixtures(),synthetic_oracle_check=True,scope='Independent complete even eligibility replay from frozen upstream eligibility/reasons (native separator/STA acquisition not repeated), all predictions, exhaustive baseline window sets, forward/inverse fixed-key filtering, all provenance witnesses and per-key/paragraph/fold summaries. No unknown values decoded or global key extended.')
 (E/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n');print(json.dumps(dict(status='PASS',validator_sha256=receipt['validator_sha256'],paragraphs=len(allparas),witnesses=len(witnesses))))
if __name__=='__main__':main()
