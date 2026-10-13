#!/usr/bin/env python3
"""Independent nine-field scope and pairwise equality verifier."""
import argparse, csv, gzip, hashlib, itertools, json, re
from pathlib import Path
B=Path(__file__).resolve().parents[1];ROOT=B.parents[2]
UNITS='a o e i n d q y s r l m k t p f ch sh ckh cth cph cfh'.split()
READERS=['ZL3b','IT2a','RF1b'];PATTERN=[0,1,2,3,1,3,4,1,5,6]
def load(p):
 p=Path(p);raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def parse(raw):
 if not isinstance(raw,str) or not re.fullmatch('[a-z]+',raw):return None
 # Suffix dynamic segmentation, independent of any greedy lexical scanner.
 possibilities=[[] for _ in range(len(raw)+1)];possibilities[-1]=[()]
 for i in range(len(raw)-1,-1,-1):
  for unit in UNITS:
   if raw.startswith(unit,i):
    for tail in possibilities[i+len(unit)]:possibilities[i].append((unit,)+tail)
 return list(possibilities[0][0]) if len(possibilities[0])==1 else None

def pairwise_match(seq):
 return len(seq)==len(PATTERN) and all((seq[i]==seq[j])==(PATTERN[i]==PATTERN[j]) for i in range(10) for j in range(i))
def canonical_labels(seq):
 first=[seq.index(x) for x in seq];classes=sorted(set(first));return [classes.index(i) for i in first]
def controls():
 positive=[UNITS[k] for k in PATTERN];assert pairwise_match(positive)
 assert pairwise_match(['name'+str(k) for k in PATTERN])
 assert canonical_labels(positive)==PATTERN
 bad_equal=positive[:];bad_equal[4]='cfh';assert not pairwise_match(bad_equal)
 bad_distinct=positive[:];bad_distinct[0]=bad_distinct[2];assert not pairwise_match(bad_distinct)
 assert not pairwise_match(positive[:-1]) and not pairwise_match(positive+['a'])
 assert parse('cphoy')==['cph','o','y'] and parse('ckh')==['ckh'] and parse('ch')==['ch']
 for raw in ('','@152;','a?','A','a a'):assert parse(raw) is None
 # Eleven distinct abstract code symbols fit the unchanged22inventory; F8 itself uses7.
 code=dict(zip('0123456789:',UNITS));literal='5:14:42:39';assert pairwise_match([code[x] for x in literal])
 assert len(set(literal))==7 and len(set(code.values()))==11
 return {'positive_renamings':3,'negative_pattern_fixtures':4,'valid_parses':3,'invalid_parses':5,'status':'PASS'}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--controls-only',action='store_true');args=parser.parse_args();checks=controls()
 if args.controls_only:print(json.dumps(checks));return
 lock=load(B/'src/REGISTRATION_LOCK.json')
 for path,digest in lock['hashes'].items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
 spec=load(B/'src/SPEC.json');assert spec['readers']==READERS and spec['units']==UNITS and spec['pattern']==PATTERN and spec['phases']==['DISCOVERY','EVALUATION'] and spec['primary']=='ZL3b'
 allowed={r['page'] for r in csv.DictReader((ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv').open(),delimiter='\t')}
 collected={};results={}
 for reader in READERS:
  selected=[];seen=set()
  for phase in spec['phases']:
   path=f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{reader}.json';entry=next(e for e in spec['inputs'] if e['path']==path)
   assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==entry['sha256']
   source=load(ROOT/path);columns=source['group_columns'];assert columns==spec['group_columns']
   for line in source['lines']:
    meta=line['metadata'];page=meta['page']
    if page not in allowed or page in ('f1r','f116v') or page.startswith('f84'):continue
    if meta['kind']!='P' or int(meta['source_group_count'])!=9 or meta['edition']!=reader:continue
    key=(page,meta['locus']);assert key not in seen;seen.add(key)
    selected.append(line)
  selected.sort(key=lambda line:(line['metadata']['page'],line['metadata']['locus']));collected[reader]=selected
  cases=[];strict=matches=0;leaves=set();mismatches={'LENGTH_MISMATCH':0,'EQUALITY_PATTERN_MISMATCH':0}
  for line in selected:
   meta=line['metadata'];rows=sorted([dict(zip(spec['group_columns'],g)) for g in line['groups']],key=lambda g:int(g['source_group_index']))
   assert all(len(g)==len(spec['group_columns']) for g in line['groups'])
   failures=[];indices=[int(g['source_group_index']) for g in rows]
   if indices!=list(range(1,10)):failures.append('indices')
   ids=[g['source_group_id'] for g in rows]
   if len(set(ids))!=len(ids) or any(g['source_group_id']!=f"{reader}|{meta['locus']}|G{int(g['source_group_index']):03d}" for g in rows):failures.append('ids')
   if not all(rows[i]['right_separator']==rows[i+1]['left_separator']=='DEFINITE_SPACE' for i in range(len(rows)-1)):failures.append('seams')
   parsed=[parse(g['ivtff_group_raw']) for g in rows]
   if any(x is None for x in parsed):failures.append('literal_parse')
   case={'page':meta['page'],'locus':meta['locus'],'status':'UNSCORABLE','failed_gates':failures,'field8_units':None,'field8_pattern':None}
   if not failures:
    strict+=1;leaves.add(int(re.match(r'f(\d+)',meta['page'])[1]));field=parsed[7]
    labels=canonical_labels(field);case['field8_units']=field;case['field8_pattern']=labels
    if len(field)!=10:status='LENGTH_MISMATCH'
    elif pairwise_match(field):status='MATCH';matches+=1
    else:status='EQUALITY_PATTERN_MISMATCH'
    assert (status=='MATCH')==(labels==PATTERN)
    case['status']=status
    if status!='MATCH':mismatches[status]+=1
   cases.append(case)
  status='NO_STRICT_LINE_CAPACITY' if not strict else ('NECESSARY_FIELD_CAPACITY_ONLY' if matches else 'NO_FIXED_EPOCH_FIELD_CANDIDATE')
  results[reader]={'metadata_lines':len(selected),'strict_lines':strict,'unscorable_lines':len(selected)-strict,'strict_leaves':len(leaves),'matching_lines':matches,'mismatch_counts':mismatches,'status':status,'cases':cases}
 assert collected==load(B/'artifacts/CANDIDATE_LINES.json.gz'),'source-line mismatch'
 expected={'status':'NECESSARY_FIXED_EPOCH_FIELD_TEST','primary':'ZL3b','readers':results};actual=load(B/'artifacts/RESULT.json')
 assert expected==actual,'result mismatch'
 receipt={'status':'PASS','source_free_controls':checks,'readers':{r:{k:v for k,v in x.items() if k!='cases'} for r,x in results.items()},'method':'Independent915metadata/source hash selection, suffix dynamic unit parsing and every pairwise equality/inequality of fixedfield8; no primary code import or other field fitting.'}
 (B/'artifacts/VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({'status':'PASS','readers':{r:x['status'] for r,x in results.items()}}))
if __name__=='__main__':main()
