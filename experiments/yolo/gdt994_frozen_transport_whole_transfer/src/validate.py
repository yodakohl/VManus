"""Full inventory/partition checker and separate frozen993regex/bit replay."""
import collections,csv,datetime,hashlib,importlib.util,json
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts';OLD=R/'experiments/yolo/gdt993_complete_transport_consequence_audit'
def read(p):return json.loads(p.read_text())
def binding_error(parse,v):
 kinds=[c['kind'] for c in parse]
 for k in ('INITIAL','GOAL','SAFETY','CAPACITY','CONCLUSION'):
  if kinds.count(k)!=1:return 'MISSING_OR_DUPLICATE_'+k
 if kinds[0]!='INITIAL' or kinds[-1]!='CONCLUSION':return 'BAD_PARAGRAPH_SCOPE'
 introduced=[];pair=None
 for c in parse:
  ss=c['symbols'];kind=c['kind']
  for x in ss:
   if x in ('W','G','C') and x not in introduced:introduced.append(x)
  def ref(s):
   if s in ('W','G','C'):return s
   if s=='FIRST_CARGO':
    if not introduced:raise ValueError('NO_PRIOR_CARGO')
    return introduced[0 if v['first']=='FIRST' else -1]
   if pair is None and v['other']=='OTHER':raise ValueError('NO_PAIR_FOR_OTHER')
   if v['other']=='FIRST':
    if not introduced:raise ValueError('NO_PRIOR_CARGO')
    return introduced[0]
   rest=set(introduced)-set(pair)
   if len(rest)!=1:raise ValueError('NONUNIQUE_OTHER')
   return next(iter(rest))
  try:
   if kind=='PAIR':
    pair=tuple(ref(ss[i]) for i in (0,3))
    if pair[0]==pair[1]:return 'PAIR_ARGUMENTS_IDENTICAL'
   elif kind=='COPY':
    if pair is None:return 'NO_PAIR_TO_COPY'
    other=ref('OTHER_CARGO');copied=(other,pair[1]) if v['copy']=='FIRST' else (pair[0],other)
    if copied[0]==copied[1]:return 'COPIED_PAIR_ARGUMENTS_IDENTICAL'
   elif kind in ('WITH_OUT','EXCLUDE','FERRY','WITH_RETURN','CONVEY','FINAL_TRIP','RESULT'):
    index={'WITH_OUT':3,'EXCLUDE':1,'FERRY':1,'WITH_RETURN':1,'CONVEY':2,'FINAL_TRIP':4,'RESULT':3}[kind];ref(ss[index])
  except ValueError as ex:return str(ex)
 return None

def main():
 for n,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 spec=read(OLD/'src/SPEC.json');lex={x['raw']:x['symbol'] for x in read(R/spec['source_draft'])['lexicon']};sources=read(R/spec['paragraph_cache']);rows=read(A/'ROWS.json');cases=read(A/'CASES.json');result=read(A/'RESULT.json')
 modspec=importlib.util.spec_from_file_location('independent993',OLD/'src/validate.py');checker=importlib.util.module_from_spec(modspec);modspec.loader.exec_module(checker)
 oldcases=read(OLD/'artifacts/CASES.json');survivors={c['id']:c['variant'] for c in oldcases if c['status']=='CONDITIONAL_CONSISTENT'};assert list(survivors)==[f'ZL-P00-V{i:02d}' for i in (0,2,4,6)]
 expected_ids=[ed+'|'+p['id'] for ed,ps in sources.items() for p in ps];assert [r['id'] for r in rows]==expected_ids
 byid={r['id']:r for r in rows};casebyid={c['id']:c for c in cases};assert len(casebyid)==len(cases);all_case_ids=[]
 for ed,ps in sources.items():
  for p in ps:
   row=byid[ed+'|'+p['id']];assert row['edition']==ed and row['paragraph']==p['id'] and row['page']==p['page'] and row['leaf']==p['leaf']
   raw=[];source_ids=[]
   for line in p['lines']:raw.extend(line['words']);source_ids.extend(line['source_ids'])
   missing=[dict(position=i+1,source_id=source_ids[i],raw=w) for i,w in enumerate(raw) if w not in lex]
   assert row['unknown']==missing and row['groups']==len(raw)==p['groups'] and row['known_groups']==len(raw)-len(missing)
   part='ORIGINAL_PARAGRAPH' if p['page']=='f83r' and p['lines'][0]['locus']=='f83r.18' and p['lines'][-1]['locus']=='f83r.24' else 'OTHER_SAME_LEAF' if p['leaf']==83 else 'OTHER_EXPOSED_LEAF'
   assert row['partition']==part and row['strict_anchor_eligible']==all(l['anchor_eligible'] for l in p['lines']) and row['independent_meaning_capacity']==0
   parses=[] if missing else checker.regex_parses([lex[x] for x in raw],spec);assert row['parses']==parses
   ids=[row['id']+f'|P{i:02d}|'+sid for i in range(len(parses)) for sid in survivors];assert row['case_ids']==ids and row['survivor_ids']==list(survivors);all_case_ids.extend(ids)
   good=False
   for i,parse in enumerate(parses):
    for sid,v in survivors.items():
     c=casebyid[row['id']+f'|P{i:02d}|'+sid];assert c['variant']==v and c['paragraph_id']==row['id'] and c['survivor_id']==sid and c['parse_index']==i
     error=binding_error(parse,v)
     if error:assert c['status']=='BINDING_CONTRADICTION' and c['error']==error and c['paths']==[];continue
     paths,hazards,refs=checker.replay(parse,v)
     # Frozen bit replayer reserves slots for all three Cargo names. Remove
     # unused slots only from reported positions when the paragraph names fewer.
     named={x for clause in parse for x in clause['symbols'] if x in ('W','G','C')}
     for path in paths:
      for state in [path,*path['trace']]:state['positions']={k:value for k,value in state['positions'].items() if k in named|{'M','B'}}
     assert paths==c['paths'] and hazards==c['program']['hazards'] and refs==c['program']['references']
     ok=any(p['consistent'] for p in paths);good=good or ok;assert c['status']==('CONDITIONAL_CONSISTENT' if ok else 'SEMANTIC_CONTRADICTION')
   status='OUTSIDE_FROZEN_LEXICON' if missing else 'NO_PARSE_FIXED_FRAGMENT' if not parses else 'CONDITIONAL_WHOLE_READING' if good else 'FIXED_READING_CONTRADICTED';assert row['status']==status
 assert [c['id'] for c in cases]==all_case_ids
 assert result['rows']==len(rows) and result['executable_cases']==len(cases)
 for ed,ps in sources.items():
  rs=[r for r in rows if r['edition']==ed];assert result['readers'][ed]==dict(paragraphs=len(ps),status_counts=dict(collections.Counter(r['status'] for r in rs)),whole_paragraph_capacity=bool(ps),physical_leaves=len({r['leaf'] for r in rs}))
 for part in ('ORIGINAL_PARAGRAPH','OTHER_SAME_LEAF','OTHER_EXPOSED_LEAF'):
  rs=[r for r in rows if r['partition']==part];assert result['partitions'][part]==dict(rows=len(rs),status_counts=dict(collections.Counter(r['status'] for r in rs)),physical_leaves=sorted({r['leaf'] for r in rs}))
 additional=[r['id'] for r in rows if r['partition']!='ORIGINAL_PARAGRAPH' and r['status']=='CONDITIONAL_WHOLE_READING'];assert result['additional_whole_readings']==additional
 assert result['decision']==('RETAIN_EXPOSED_TRANSFER_CANDIDATE' if additional else 'PARK_UNCHANGED_WHOLE_TRANSFER') and result['claims']==dict(confirmed_words=0,independent_meaning_capacity=0,significance=False)
 with (A/'CANDIDATES.tsv').open() as f:table=list(csv.DictReader(f,delimiter='\t'))
 assert len(table)==len(rows)
 for t,r in zip(table,rows):
  expected={k:str(r[k]) for k in ('id','partition','groups','known_groups','strict_anchor_eligible','status','independent_meaning_capacity')};expected.update(unknown_groups=str(len(r['unknown'])),parse_count=str(len(r['parses'])),case_count=str(len(r['case_ids'])));assert t==expected
 out=dict(status='PASS',completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),paragraphs_checked=len(rows),cases_checked=len(cases),coverage='all source rows,raw words,unknowns,partitions,parses,variants,paths,counts and TSV;separate993regex/bit implementation;same author',confirmed_words=0)
 (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
