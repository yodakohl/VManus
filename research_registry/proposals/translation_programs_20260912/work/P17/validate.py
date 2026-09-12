"""Reconstruct eligible activation events from prefix lists, independently of builder."""
import csv,json,hashlib
from pathlib import Path
from collections import Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P17')
def rr(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
src=json.loads((D/'SOURCE.json').read_text())
for p,h in src['inputs'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
orig=list(csv.DictReader((D.parent/'P12/PROSE.tsv').open(),delimiter='\t'));flat=[]
for r in orig:
 for i,w in enumerate(r['zl3b_line'].split(),1):flat.append((r['record_id'],r['locus'],f'{r["locus"]}:{i}',w))
assert [(r['record'],r['line'],r['locus'],r['word']) for r in rr('INPUT.tsv')]==flat
mat={'shedy':'A','lchedy':'C'};pred=rr('PREDICATIONS.tsv');blocks=rr('TOPIC_BLOCKS.tsv');mentions=rr('MENTIONS.tsv')
def activations(prefix,mode):
 ms=[t for t in prefix if t[3] in mat];eligible=[]
 for k,t in enumerate(ms):
  repeated=any(x[3]==t[3] for x in ms[:k])
  if k==0 or mode=='L1' or (mode=='N' and not repeated) or (mode=='R' and repeated):eligible.append(t)
 compressed=[]
 for t in eligible:
  if not compressed or compressed[-1][3]!=t[3]:compressed.append(t)
 return ms,compressed
for mode in ['N','R','L1','T0']:
 aa=rr(f'ALIGNMENT_{mode}.tsv');assert [(r['record'],r['line'],r['locus'],r['word']) for r in aa]==flat
 assert sum(r['kind']=='OPEN' for r in aa)==291
 assert all(r['rendering']=='⟦'+r['word']+'⟧' for r in aa if r['kind']=='OPEN')
 actual=[r for r in pred if r['mode']==mode];assert len(actual)==20
 for p in actual:
  j=next(i for i,t in enumerate(flat) if t[2]==p['locus']);prefix=[t for t in flat[:j] if t[0]==p['record']]
  ms,acts=activations(prefix,mode);active=acts[-1] if acts else None
  bs=[t for t in prefix if t[3]=='qokaiin']
  patient=mat[active[3]] if active else 'NA';origin=(ms[-1] if mode=='L1' else active)[2] if active else 'NA'
  dest='B' if bs and p['word']=='qokeedy' else 'NA';ds=bs[-1][2] if dest=='B' else 'NA'
  assert (p['patient'],p['patient_source'],p['destination'],p['destination_source'])==(patient,origin,dest,ds)
  assert p['block_id']==mode+':'+active[2] if active else p['block_id']=='NA'
 for rec in dict.fromkeys(t[0] for t in flat):
  full=[t for t in flat if t[0]==rec];_,acts=activations(full,mode)
  rb=[b for b in blocks if b['mode']==mode and b['record']==rec];assert len(rb)==len(acts)
  for k,(b,a) in enumerate(zip(rb,acts)):
   assert b['origin']==a[2] and b['topic']==mat[a[3]]
   assert b['kind']==('INITIAL' if k==0 else 'SWITCH')
   assert b['end_before']==(acts[k+1][2] if k+1<len(acts) else 'RECORD_END')
   pp=[p for p in actual if p['block_id']==b['block_id']]
   assert b['actions']==(','.join(p['locus'] for p in pp) or 'NONE')
   assert int(b['predicate_count'])==len(pp)
   assert int(b['complete_predicates'])==sum(p['status']=='COMPLETE' for p in pp)
   for base in ['L1','T0']:
    assert int(b['different_from_'+base])==sum(p['patient']!=next(x['patient'] for x in pred if x['mode']==base and x['locus']==p['locus']) for p in pp)
 reading=(D/f'READING_{mode}.md').read_text();assert all('`'+r['zl3b_line']+'`' in reading for r in orig)
 result=json.loads((D/'RESULT.json').read_text())['models'][mode]
 assert result['predications']==dict(Counter(p['status'] for p in actual))
 assert result['missing_patient_total']==3 and result['missing_destination_total']==4
 ss=[b for b in blocks if b['mode']==mode and b['kind']=='SWITCH']
 assert result['switches']==len(ss)
 assert result['switch_blocks_with_two_predicates']==sum(int(b['predicate_count'])>=2 for b in ss)
 assert result['switch_blocks_two_changes_vs_both']==sum(int(b['different_from_L1'])>=2 and int(b['different_from_T0'])>=2 for b in ss)
 assert len([m for m in mentions if m['mode']==mode])==30
assert len(flat)==341
result=json.loads((D/'RESULT.json').read_text());assert result['models']['N']['switch_blocks_two_changes_vs_both']==2;assert result['models']['R']['switch_blocks_with_two_predicates']==0
receipt={'status':'PASS','source_hashes':len(src['inputs']),'groups_per_reading':341,'full_readings':4,'independently_replayed_predications':len(pred),'checked_topic_blocks':len(blocks),'checks':['bounded source equality','direct prefix eligible activations','block starts ends and all children','all argument and destination sources','baseline differences','N two multiple-change blocks; R none','missing argument overlap retained'],'limit':'Internal execution and conditional discourse consequences, not translation truth.'}
(D/'VALIDATION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
