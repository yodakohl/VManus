#!/usr/bin/env python3
"""Exact complete native unit coverage, no parser or semantic execution."""
from pathlib import Path
import collections,csv,datetime,hashlib,json,re,subprocess
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n')
def main():
 for path,digest in read(E/'PREREG_LOCK.json')['files'].items():assert sha(R/path)==digest,path
 receipt=read(A/'PUBLIC_REGISTRATION.json');subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],cwd=R,check=True)
 start=datetime.datetime.now(datetime.timezone.utc).isoformat();spec=read(E/'src/SPEC.json')
 lex=read(R/spec['lexicon']);assert len(lex)==spec['lexicon_count']==91
 admitted=set(read(R/spec['admission_projection'])['allowed_selectors']);assert len(admitted)==179
 source=read(R/spec['cache']);assert {k:len(v) for k,v in source.items()}==spec['expected_reader_rows']
 rows=[];survivors=[]
 for edition,paras in source.items():
  for p in paras:
   page=p['page'];assert page in admitted and not page.startswith('f84') and page!='f116v'
   leaf=int(re.match(r'f(\d+)',page).group(1));assert leaf==p['leaf']
   assert p['lines'][0]['start'] and p['lines'][-1]['end']
   offset=0
   for line in p['lines']:
    assert line['offset']==offset and len(line['words'])==len(line['source_ids'])
    offset+=len(line['words'])
   numbers=[int(line['locus'].split('.')[1]) for line in p['lines']]
   assert numbers==list(range(numbers[0],numbers[-1]+1))
   words=[w for line in p['lines'] for w in line['words']];ids=[v for line in p['lines'] for v in line['source_ids']]
   assert len(words)==len(ids)==p['groups'];assert len(set(ids))==len(ids)
   unknown=[{'position':i+1,'source_id':sid,'raw':word} for i,(word,sid) in enumerate(zip(words,ids)) if word not in lex]
   alltypes=set(words);known=alltypes.intersection(lex)
   row={'id':edition+'|'+p['id'],'edition':edition,'paragraph':p['id'],'page':page,'leaf':leaf,'partition':'DEVELOPMENT_PHYSICAL_LEAF' if leaf in spec['development_physical_leaves'] else 'OTHER_ADMITTED_EXPOSED_LEAF','groups':len(words),'types':len(alltypes),'known_groups':len(words)-len(unknown),'known_types':len(known),'unknown_types':len(alltypes)-len(known),'unknown':unknown,'strict_anchor_eligible':all(line['anchor_eligible'] for line in p['lines']),'status':'MISSING_FIXED_VALUES' if unknown else 'FULL_LEXICAL_CAPACITY'}
   rows.append(row)
   if not unknown:survivors.append({'id':row['id'],'partition':row['partition'],'native_record':p,'semantic_status':'NOT_ASSESSED_NO_TRANSFER_GRAMMAR'})
 def summary(rs):return {'rows':len(rs),'status_counts':dict(collections.Counter(r['status'] for r in rs)),'physical_leaves':sorted({r['leaf'] for r in rs}),'strict_rows':sum(r['strict_anchor_eligible'] for r in rs),'strict_covered':sum(r['strict_anchor_eligible'] and not r['unknown'] for r in rs)}
 covered=[r['id'] for r in rows if not r['unknown']];extra=[r['id'] for r in rows if not r['unknown'] and r['partition']=='OTHER_ADMITTED_EXPOSED_LEAF']
 result={'status':'COMPLETE_FIXED_LEXICAL_CAPACITY','started_utc':start,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'registration_commit':receipt['commit'],'rows':len(rows),'readers':{k:summary([r for r in rows if r['edition']==k]) for k in source},'partitions':{k:summary([r for r in rows if r['partition']==k]) for k in ['DEVELOPMENT_PHYSICAL_LEAF','OTHER_ADMITTED_EXPOSED_LEAF']},'covered':covered,'extension_survivors':extra,'decision':'RETAIN_ALL_EXPOSED_CAPACITY_UNITS_GRAMMAR_UNASSESSED' if extra else 'STOP_UNCHANGED_MUSIC91_EXTENSION_CAPACITY','semantic_execution':False,'new_meanings':0,'new_productions':0,'confirmed_words':0,'independent_meaning_capacity':0,'significance_claim':False}
 write(A/'ROWS.json',rows);write(A/'SURVIVORS.json',survivors);write(A/'RESULT.json',result)
 fields=['id','edition','paragraph','page','leaf','partition','groups','types','known_groups','unknown_groups','known_types','unknown_types','strict_anchor_eligible','status']
 with (A/'CANDIDATES.tsv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader()
  for r in rows:w.writerow({**{k:r[k] for k in fields if k!='unknown_groups'},'unknown_groups':len(r['unknown'])})
 print(json.dumps({k:result[k] for k in ['rows','covered','extension_survivors','decision','semantic_execution']}))
if __name__=='__main__':main()
