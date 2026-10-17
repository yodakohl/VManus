#!/usr/bin/env python3
"""Necessary overt-consequent capacity; no q or whole-word meaning assigned."""
from pathlib import Path
from collections import defaultdict
import json,hashlib,csv,subprocess,sys
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):
 text=json.dumps(d,ensure_ascii=False,indent=2)+'\n'
 if '--check' in sys.argv:assert p.read_text()==text,str(p)
 else:p.write_text(text)
def source():
 spec=json.loads((E/'src/SPEC.json').read_text());s=spec['source']
 for p,h in [(s['path'],s['sha256']),(s['allowlist'],s['allowlist_sha256'])]:assert sha(ROOT/p)==h,p
 for item in json.loads((E/'LOCK.json').read_text())['files']:assert sha(ROOT/item['path'])==item['sha256']
 cache=ROOT/s['cache']
 if not cache.exists():
  cache=E/'runtime/PROJECTION.tsv';cache.parent.mkdir(exist_ok=True)
  if not cache.exists():
   allow=list(csv.DictReader((ROOT/s['allowlist']).open(),delimiter='\t'));pages=sorted({r['page'] for r in allow});assert len(pages)==179
   cmd=['./vmanus-exp','query-tsv',s['path'],'--selector','page']
   for p in pages:assert not p.startswith('f84') and p!='f116v';cmd+=['--allow',p]
   cmd+=['--columns',','.join(s['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']
   proc=subprocess.run(cmd,cwd=ROOT,capture_output=True,check=True);cache.write_bytes(proc.stdout)
 assert sha(cache)==s['cache_sha256']
 reader=csv.DictReader(cache.open(),delimiter='\t');assert reader.fieldnames==s['columns'];rows=list(reader);assert len(rows)==s['selected_rows']
 assert all(not r['page'].startswith('f84') and r['page']!='f116v' for r in rows)
 assert len({r['source_group_id'] for r in rows})==len(rows)
 return spec,rows

def build_blocks(rows):
 loci=defaultdict(list)
 for r in rows:loci[(r['edition'],r['page'],r['locus'])].append(r)
 pages=defaultdict(list)
 for (ed,page,locus),gs in loci.items():
  gs=sorted(gs,key=lambda r:int(r['source_group_index']));n=len(gs)
  assert [int(g['source_group_index']) for g in gs]==list(range(1,n+1))
  assert all(int(g['source_group_count'])==n for g in gs)
  for k in ['source_row_index','kind','paragraph_start','paragraph_end']:assert len({g[k] for g in gs})==1
  assert gs[0]['paragraph_start'] in ['0','1'] and gs[0]['paragraph_end'] in ['0','1']
  pages[(ed,page)].append({'locus':locus,'source_row_index':int(gs[0]['source_row_index']),'kind':gs[0]['kind'],'paragraph_start':gs[0]['paragraph_start'],'paragraph_end':gs[0]['paragraph_end'],'groups':gs})
 blocks=[]
 for (ed,page),lines in sorted(pages.items()):
  lines.sort(key=lambda x:x['source_row_index']);assert len({l['source_row_index'] for l in lines})==len(lines)
  current=[]
  def flush():
   if current:
    blocks.append({'edition':ed,'page':page,'block_id':f"{ed}:{page}:{current[0]['locus']}",'left_marked':current[0]['paragraph_start']=='1','right_marked':current[-1]['paragraph_end']=='1','lines':current.copy()});current.clear()
  for line in lines:
   if line['kind']!='P':flush();continue
   if line['paragraph_start']=='1':flush()
   current.append(line)
   if line['paragraph_end']=='1':flush()
  flush()
 return blocks

def evaluate(blocks):
 result={};counter=[]
 for ed in ['ZL3b','IT2a','RF1b']:
  counts={k:0 for k in ['blocks','complete_blocks','right_only_blocks','unmarked_end_blocks','complete_q_end_blocks','right_only_q_end_blocks','unmarked_q_end_blocks','q_only_groups']}
  for b in [b for b in blocks if b['edition']==ed]:
   counts['blocks']+=1
   category='complete' if b['left_marked'] and b['right_marked'] else 'right_only' if b['right_marked'] else 'unmarked'
   counts[{'complete':'complete_blocks','right_only':'right_only_blocks','unmarked':'unmarked_end_blocks'}[category]]+=1
   groups=[r for l in b['lines'] for r in l['groups']];counts['q_only_groups']+=sum(r['ivtff_group_raw']=='q' for r in groups)
   trailing=[]
   for r in reversed(groups):
    if not r['ivtff_group_raw'].startswith('q'):break
    trailing.append(r)
   trailing.reverse()
   if trailing:
    counts[category+'_q_end_blocks']+=1
    if b['right_marked']:counter.append({**b,'terminal_run':trailing,'primary':category=='complete'})
  result[ed]=counts
 return {'status':'STRICT_GLOBAL_Q_SCOPE_CONTRADICTED' if any(v['complete_q_end_blocks'] for v in result.values()) else 'NECESSARY_END_CAPACITY_ONLY','source_projection_sha256':json.loads((E/'src/SPEC.json').read_text())['source']['cache_sha256'],'per_reader':result,'counterparagraphs':counter,'primary_falsified_editions':[ed for ed,v in result.items() if v['complete_q_end_blocks']],'translated_words':0,'limits':['Exact global all-literal-q grammar and own paragraph flags only; no q translation, global conditional-language ban or local sketch contradiction.','All text previously exposed; alternate readers are one manuscript.','Unknown fragment ends are not contradictions. Right-only cases are separate diagnostics.','No hidden consequence, q exception, paragraph repair or new image.']}
def main():
 spec,rows=source();blocks=build_blocks(rows);assert sum(len(l['groups']) for b in blocks for l in b['lines'])==sum(r['kind']=='P' for r in rows)
 result=evaluate(blocks);save(E/'artifacts/RESULT.json',result);print(json.dumps({k:v for k,v in result.items() if k!='counterparagraphs'}))
if __name__=='__main__':main()
