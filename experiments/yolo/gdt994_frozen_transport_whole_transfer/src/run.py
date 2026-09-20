import collections,csv,datetime,hashlib,importlib.util,itertools,json,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts';OLD=R/'experiments/yolo/gdt993_complete_transport_consequence_audit'
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def load_model():
 s=importlib.util.spec_from_file_location('frozen993',OLD/'src/model.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def main():
 for n,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/n).read_bytes()).hexdigest()==h,n
 receipt=read(A/'PUBLIC_REGISTRATION.json');assert subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],cwd=R).returncode==0
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();spec=read(OLD/'src/SPEC.json');model=load_model();lex={x['raw']:x['symbol'] for x in read(R/spec['source_draft'])['lexicon']};sources=read(R/spec['paragraph_cache'])
 oldcases=read(OLD/'artifacts/CASES.json');survivors=[c for c in oldcases if c['status']=='CONDITIONAL_CONSISTENT'];assert [x['id'] for x in survivors]==[f'ZL-P00-V{i:02d}' for i in (0,2,4,6)]
 rows=[];cases=[]
 for edition,paragraphs in sources.items():
  for p in paragraphs:
   assert not p['page'].startswith('f84') and p['page']!='f116v'
   words=[w for l in p['lines'] for w in l['words']];ids=[i for l in p['lines'] for i in l['source_ids']];assert len(words)==len(ids)==p['groups']
   unknown=[dict(position=i+1,source_id=s,raw=w) for i,(w,s) in enumerate(zip(words,ids)) if w not in lex]
   partition='ORIGINAL_PARAGRAPH' if p['id']=='f83r|f83r.18-f83r.24' else 'OTHER_SAME_LEAF' if p['leaf']==83 else 'OTHER_EXPOSED_LEAF'
   row=dict(id=edition+'|'+p['id'],edition=edition,paragraph=p['id'],page=p['page'],leaf=p['leaf'],partition=partition,groups=len(words),known_groups=len(words)-len(unknown),unknown=unknown,strict_anchor_eligible=all(l['anchor_eligible'] for l in p['lines']),parses=[],case_ids=[],survivor_ids=[c['id'] for c in survivors],independent_meaning_capacity=0)
   if unknown:row['status']='OUTSIDE_FROZEN_LEXICON'
   else:
    parses=model.parse_all([lex[w] for w in words],spec);row['parses']=parses;row['status']='NO_PARSE_FIXED_FRAGMENT' if not parses else 'FIXED_READING_CONTRADICTED'
    for pi,parse in enumerate(parses):
     for c in survivors:
      case=dict(id=row['id']+f'|P{pi:02d}|'+c['id'],paragraph_id=row['id'],survivor_id=c['id'],parse_index=pi,variant=c['variant'])
      try:
       program=model.compile_reading(parse,c['variant']);paths=model.execute(program,c['variant']);case.update(program=program,paths=paths,status='CONDITIONAL_CONSISTENT' if any(p['consistent'] for p in paths) else 'SEMANTIC_CONTRADICTION')
      except ValueError as ex:case.update(status='BINDING_CONTRADICTION',error=str(ex),paths=[])
      cases.append(case);row['case_ids'].append(case['id'])
      if case['status']=='CONDITIONAL_CONSISTENT':row['status']='CONDITIONAL_WHOLE_READING'
   rows.append(row)
 result=dict(status='COMPLETE_FIXED_TRANSFER_CAPACITY_AUDIT',started_utc=start,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),registration_commit=receipt['commit'],rows=len(rows),executable_cases=len(cases),readers={},partitions={},claims=dict(confirmed_words=0,independent_meaning_capacity=0,significance=False))
 for edition,ps in sources.items():
  rs=[r for r in rows if r['edition']==edition];result['readers'][edition]=dict(paragraphs=len(ps),status_counts=dict(collections.Counter(r['status'] for r in rs)),whole_paragraph_capacity=bool(ps),physical_leaves=len({r['leaf'] for r in rs}))
 for part in ('ORIGINAL_PARAGRAPH','OTHER_SAME_LEAF','OTHER_EXPOSED_LEAF'):
  rs=[r for r in rows if r['partition']==part];result['partitions'][part]=dict(rows=len(rs),status_counts=dict(collections.Counter(r['status'] for r in rs)),physical_leaves=sorted({r['leaf'] for r in rs}))
 result['additional_whole_readings']=[r['id'] for r in rows if r['partition']!='ORIGINAL_PARAGRAPH' and r['status']=='CONDITIONAL_WHOLE_READING']
 result['decision']='RETAIN_EXPOSED_TRANSFER_CANDIDATE' if result['additional_whole_readings'] else 'PARK_UNCHANGED_WHOLE_TRANSFER'
 write(A/'ROWS.json',rows);write(A/'CASES.json',cases);write(A/'RESULT.json',result)
 with (A/'CANDIDATES.tsv').open('w',newline='') as f:
  fields=['id','partition','groups','known_groups','unknown_groups','strict_anchor_eligible','parse_count','case_count','status','independent_meaning_capacity'];w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader()
  for r in rows:w.writerow({**{k:r[k] for k in fields if k in r},'unknown_groups':len(r['unknown']),'parse_count':len(r['parses']),'case_count':len(r['case_ids'])})
 print(json.dumps(result))
if __name__=='__main__':main()
