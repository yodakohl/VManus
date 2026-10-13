#!/usr/bin/env python3
"""Independent source selection, dynamic parse and direct writer check."""
import argparse, collections, csv, functools, hashlib, itertools, json, re
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
SIGNS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
READERS=['ZL3b','IT2a','RF1b']
PREFIX='experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/'
SOURCE_HASHES={'ZL3b':'7ab2cafe31d50b4013682c9b73d867bd36bae9a0a4addc0de509be7be48e44c0','IT2a':'2c62ef9c6c1cec11fd0e0e383b85190705a6059439163509213df2bd56d0e8c9','RF1b':'ccace49eb471825f70afff673cf8bcb60ec9a41fbb8eb96dfbef1f2fef1ec99c'}
def read(path):return json.loads(Path(path).read_text())
def parses(word):
 if not isinstance(word,str) or re.fullmatch('[a-z]+',word) is None:return []
 # Forward dynamic segmentation, capped only after a suffix-independent complete result.
 cells=[[] for _ in range(len(word)+1)];cells[0]=[()]
 for i in range(len(word)):
  for prefix in cells[i]:
   for symbol in SIGNS:
    if word.startswith(symbol,i):cells[i+len(symbol)].append(prefix+(symbol,))
 return [list(x) for x in cells[-1]]

def writer(words,a,b):
 pairs=[i for i in range(len(words)-1) if words[i][-1]==a and words[i+1][0]==b]
 out=[w[:] for w in words];seen=set()
 for i in pairs:
  positions=((i,len(words[i])-1),(i+1,0));assert not seen.intersection(positions);seen.update(positions)
  out[i][-1],out[i+1][0]=words[i+1][0],words[i][-1]
 return out

def direct(units):
 padded=[['cph','cph']]+units+[['sh','sh']]
 candidate=writer(padded,'cph','sh');forward=writer(candidate,'sh','cph')
 middle_preserved=forward[2][-1]=='sh' and forward[3][0]=='cph'
 return {'padded_output':padded,'canonical_preimage':candidate,'forward_output':forward,'full_window_image':forward==padded,'middle_obligation_preserved':middle_preserved}

def controls():
 assert parses('cphoy')==[['cph','o','y']]
 assert parses('sh')==[['sh']]
 assert parses('ch')==[['ch']] # A greedy prefix-free premise is not used.
 for invalid in ('','?','@152;','{ch}', 'ABC','sh cph'):assert parses(invalid)==[]
 for left in (['cph'],['o','cph'],['sh'],['o','y'],['sh','cph']):
  got=direct([left,['sh'],['cph','o','y']]);assert got['middle_obligation_preserved']==(left[-1]=='cph')
  if left[-1]!='cph':assert not got['full_window_image']
 return {'literal_parse_fixtures':9,'fixed_middle_writer_fixtures':5,'status':'PASS'}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--controls-only',action='store_true');args=ap.parse_args();check=controls()
 if args.controls_only:print(json.dumps(check));return
 lock=read(B/'src/REGISTRATION_LOCK.json')
 for path,digest in lock['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
 spec=read(B/'src/SPEC.json');assert spec['readers']==READERS and spec['units']==SIGNS and spec['indices']==[1,2,3] and spec['A']=='sh' and spec['B']=='cph' and spec['primary']=='ZL3b'
 assert 'f18v' in {x['page'] for x in csv.DictReader((ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
 expected_context={};expected_readers={};direct_checks={}
 for ed in READERS:
  path=PREFIX+'SOURCE_EVALUATION_'+ed+'.json';entry=next(x for x in spec['inputs'] if x['path']==path)
  assert entry['sha256']==SOURCE_HASHES[ed] and hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==SOURCE_HASHES[ed]
  data=read(ROOT/path);columns=data['group_columns'];assert len(columns)==len(set(columns))
  selected=[line for line in data['lines'] if line['metadata'].get('page')=='f18v' and line['metadata'].get('locus')=='f18v.8']
  failures=[]
  if len(selected)!=1:
   failures.append('unique_target_line');metadata=None;groups=[]
  else:
   metadata=selected[0]['metadata'];group_index=columns.index('source_group_index')
   groups=[dict(zip(columns,values)) for values in selected[0]['groups'] if int(values[group_index]) in (1,2,3)]
   groups.sort(key=lambda g:int(g['source_group_index']))
   if not(metadata.get('edition')==ed and metadata.get('page')=='f18v' and metadata.get('locus')=='f18v.8' and metadata.get('kind')=='P' and int(metadata.get('source_group_count',0))>=3):failures.append('metadata')
  indices=[int(g['source_group_index']) for g in groups]
  if indices!=[1,2,3]:failures.append('unique_original_indices')
  if len({g['source_group_id'] for g in groups})!=len(groups) or any(g['source_group_id']!=f"{ed}|f18v.8|G{int(g['source_group_index']):03d}" for g in groups):failures.append('source_ids')
  fixed=len(groups)==3 and groups[1]['ivtff_group_raw']=='sh' and groups[2]['ivtff_group_raw']=='cphoy'
  if not fixed:failures.append('fixed_witnesses')
  shared=len(groups)==3 and all(groups[i]['right_separator']==groups[i+1]['left_separator']=='DEFINITE_SPACE' for i in (0,1))
  if not shared:failures.append('shared_seams')
  parsed=[]
  for group in groups:
   candidates=parses(group['ivtff_group_raw']);parsed.append(candidates[0] if len(candidates)==1 else None)
  if len(parsed)!=3 or any(x is None for x in parsed):failures.append('complete_unique_literal_parse')
  final=parsed[0][-1] if parsed and parsed[0] else None
  status='UNSCORABLE' if failures else ('REQUIRED_RESCUE_PRESENT' if final=='cph' else 'FIXED_KEY_EXCLUDED_AT_BOUND_CONTEXT')
  if not failures:
   dc=direct(parsed);assert dc['middle_obligation_preserved']==(status=='REQUIRED_RESCUE_PRESENT')
   if status=='FIXED_KEY_EXCLUDED_AT_BOUND_CONTEXT':assert not dc['full_window_image']
   direct_checks[ed]=dc
  expected_context[ed]={'metadata':metadata,'groups':groups,'source':entry}
  expected_readers[ed]={'status':status,'failed_gates':failures,'parsed_groups':parsed,'g001_final_unit':final}
 actual_context=read(B/'artifacts/CONTEXT.json');assert actual_context==expected_context,'context discrepancy'
 actual=read(B/'artifacts/RESULT.json');assert set(actual)=={'status','primary','key','readers','claim_ceiling'}
 assert actual['primary']=='ZL3b' and actual['key']=={'A':'sh','B':'cph'} and isinstance(actual['claim_ceiling'],str)
 assert actual['status']=='BOUND_CONTEXT_'+expected_readers['ZL3b']['status']
 assert actual['readers']==expected_readers,('result discrepancy',actual['readers'],expected_readers)
 receipt={'status':'PASS','source_free_controls':check,'readers':{ed:r['status'] for ed,r in expected_readers.items()},'direct_window_checks':direct_checks,'method':'Independent metadata-first915cache extraction; exact sourcehashes/IDs; forward dynamic segmentation and direct canonicalinverse/forward simulation; no primary import.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','readers':receipt['readers']}))
if __name__=='__main__':main()
