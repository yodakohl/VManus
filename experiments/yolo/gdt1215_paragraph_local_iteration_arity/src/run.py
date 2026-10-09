#!/usr/bin/env python3
"""Necessary right-argument space under explicit paragraph closure."""
import csv, hashlib, io, json, subprocess
from collections import Counter, defaultdict
from datetime import datetime,timezone
from pathlib import Path
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
SOURCE=ROOT/'experiments/semantic_assumptions/results/source_separator_transcription.tsv'
ALLOW=ROOT/'experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
COLS='source_group_id,edition,page,locus,kind,source_row_index,source_group_index,source_group_count,paragraph_start,paragraph_end,left_separator,right_separator,ivtff_group_raw'
def dump(v):return json.dumps(v,ensure_ascii=False,indent=2)+'\n'
def main():
 started=datetime.now(timezone.utc).isoformat()
 for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
 pages=sorted({r['page'] for r in csv.DictReader(ALLOW.open(),delimiter='\t')})
 assert len(pages)==179 and not any(p.startswith('f84') or p=='f116v' for p in pages)
 cmd=[str(ROOT/'vmanus-exp'),'query-tsv',str(SOURCE),'--selector','page','--columns',COLS]
 for page in pages:cmd+=['--allow',page]
 query=subprocess.run(cmd,capture_output=True,text=True,check=True);rows=list(csv.DictReader(io.StringIO(query.stdout),delimiter='\t'))
 lines=defaultdict(list);bypage=defaultdict(list)
 for r in rows:
  assert r['page'] in pages;lines[(r['edition'],r['page'],r['locus'])].append(r)
 for (ed,page,locus),rs in lines.items():
  rs.sort(key=lambda r:int(r['source_group_index']))
  assert [int(r['source_group_index']) for r in rs]==list(range(1,len(rs)+1))
  assert all(int(r['source_group_count'])==len(rs) for r in rs)
  if rs[0]['kind']=='P':bypage[(ed,page)].append(rs)
 units={};binding={}
 for (ed,page),ls in sorted(bypage.items()):
  active=[]
  for line in sorted(ls,key=lambda rs:int(rs[0]['source_row_index'])):
   if line[0]['paragraph_start']=='1':active=[]
   if active or line[0]['paragraph_start']=='1':active.append(line)
   if active and line[0]['paragraph_end']=='1':
    ns=[int(x[0]['locus'].rsplit('.',1)[1]) for x in active]
    if all(y==x+1 for x,y in zip(ns,ns[1:])):
     uid=ed+'|'+page+'|'+active[0][0]['locus']+'-'+active[-1][0]['locus'];flat=[r for line in active for r in line];units[uid]=flat
     for i,r in enumerate(flat):binding[r['source_group_id']]=(uid,i)
    active=[]
 cases=[];retained=set();contexts=[]
 for r in rows:
  if r['ivtff_group_raw']!='olol':continue
  bound=binding.get(r['source_group_id']);uid,pos=bound if bound else ('',None);whole=lines[(r['edition'],r['page'],r['locus'])];reasons=[]
  if r['kind']!='P':reasons.append('NON_PROSE')
  if r['left_separator'] not in ('DEFINITE_SPACE','LINE_START') or r['right_separator'] not in ('DEFINITE_SPACE','LINE_END'):reasons.append('UNCERTAIN_WORD_BOUNDARY')
  if not bound:reasons.append('NO_COMPLETE_NATIVE_PARAGRAPH')
  remaining=None if not bound else len(units[uid])-pos-1
  outcome='UNTESTABLE' if reasons else ('CONTRADICTION' if remaining<1 else 'RIGHT_SPACE_PRESENT')
  case={k:r[k] for k in ('source_group_id','edition','page','locus','kind','ivtff_group_raw','left_separator','right_separator')}
  case.update(unit_id=uid,position=None if pos is None else pos+1,right_group_count=remaining,first_right_id=None if not bound or remaining==0 else units[uid][pos+1]['source_group_id'],outcome=outcome,reasons=reasons,whole_line=' '.join(x['ivtff_group_raw'] for x in whole));cases.append(case);contexts.append(whole)
  if uid:retained.add(uid)
 editions=['ZL3b','IT2a','RF1b'];assert all(sum(c['edition']==e for c in cases)==14 for e in editions)
 result={'experiment':'GDT1215','status':'PARAGRAPH_LOCAL_ITERATION_CONTRADICTED' if any(c['outcome']=='CONTRADICTION' for c in cases) else 'NO_ELIGIBLE_PARAGRAPH_END_CONTRADICTION','groups_queried':len(rows),'complete_paragraphs':{e:sum(u.startswith(e+'|') for u in units) for e in editions},'outcomes':{e:dict(Counter(c['outcome'] for c in cases if c['edition']==e)) for e in editions},'cases':cases,'claim_ceiling':'Conditional paragraph-local application only; no native ITER meaning, sentence-boundary fact or universal iteration rejection.'}
 (A/'RESULT.json').write_text(dump(result));(A/'RETAINED_CONTEXTS.json').write_text(dump({'occurrence_lines':contexts,'paragraphs':{u:units[u] for u in sorted(retained)}}))
 md=['# Every exact olol case and available complete paragraph','No native word meanings; readings kept separate.']
 for c in cases:md+=['',c['source_group_id']+' '+c['outcome']+' right='+str(c['right_group_count']),'`'+c['whole_line']+'`']
 for uid in sorted(retained):
  md+=['','## '+uid];group=defaultdict(list)
  for r in units[uid]:group[r['locus']].append(r['ivtff_group_raw'])
  md += [loc+'  '+' '.join(words) for loc,words in group.items()]
 (A/'COMPLETE_CONTEXTS.md').write_text('\n'.join(md)+'\n')
 (A/'RUN_RECEIPT.json').write_text(dump({'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'guard_stderr':query.stderr,'projection_sha256':hashlib.sha256(query.stdout.encode()).hexdigest(),'selector_count':len(pages)}))
 print(dump({k:v for k,v in result.items() if k!='cases'}))
if __name__=='__main__':main()
