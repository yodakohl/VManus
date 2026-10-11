from pathlib import Path
import collections,csv,gzip,hashlib,io,json,re,subprocess
B=Path(__file__).resolve().parents[1];R=B.parents[2]
SOURCE='experiments/semantic_assumptions/results/source_separator_transcription.tsv'
ALLOW='experiments/yolo/gdt631_prefixed_cth_quality_parts/artifacts/PAGE_ALLOWLIST.tsv'
COLS=['source_group_id','edition','page','locus','kind','source_row_index','source_group_index','source_group_count','ivtff_group_raw','left_separator','right_separator','section','currier']
CLEAR={'DEFINITE_SPACE','LINE_START','LINE_END'};FAMILY={'qokey','qokeey','qokedy','qokeedy'};EDS=['ZL3b','IT2a','RF1b']
def save(name,x): (B/'artifacts'/name).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items(): assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 allowed=[r['page'] for r in csv.DictReader((R/ALLOW).open(),delimiter='\t')]
 assert len(allowed)==len(set(allowed))==179
 assert not any(p.startswith('f84') or p in {'f1r','f116v'} for p in allowed)
 command=['./vmanus-exp','query-tsv',SOURCE,'--selector','page']
 for page in allowed:command+=['--allow',page]
 command+=['--columns',','.join(COLS),'--forbid-prefix','f84','--forbid-prefix','f84r']
 q=subprocess.run(command,cwd=R,text=True,capture_output=True,check=True)
 receipt=[json.loads(x[12:]) for x in q.stderr.splitlines() if x.startswith('GUARD_STATS ')]
 assert len(receipt)==1
 rows=[]
 for v in csv.DictReader(io.StringIO(q.stdout),delimiter='\t'):
  assert v['page'] in allowed
  if v['kind']!='P':continue
  rows.append(dict(id=v['source_group_id'],edition=v['edition'],page=v['page'],locus=v['locus'],row=int(v['source_row_index']),index=int(v['source_group_index']),count=int(v['source_group_count']),raw=v['ivtff_group_raw'],left=v['left_separator'],right=v['right_separator'],section=v['section'],currier=v['currier']))
 rows.sort(key=lambda r:(r['edition'],r['page'],r['row'],r['index']))
 assert len({r['id'] for r in rows})==len(rows)
 lines=collections.defaultdict(list);pages=collections.defaultdict(list)
 for r in rows:lines[(r['edition'],r['locus'])].append(r);pages[(r['edition'],r['page'])].append(r)
 for rr in lines.values():assert [r['index'] for r in rr]==list(range(1,rr[0]['count']+1))
 cases=[]
 for (ed,page),rr in sorted(pages.items()):
  producers=[];uncertain=[]
  for r in rr:
   clear=r['left'] in CLEAR and r['right'] in CLEAR
   reliable=clear and re.fullmatch('[a-z]+',r['raw']) is not None
   if r['raw']=='qoky':
    state='CONSUMER_UNCERTAIN' if not clear else 'AVAILABLE' if producers else 'SOURCE_UNCERTAIN' if uncertain else 'MISSING_PREDECESSOR'
    cases.append(dict(consumer=r,status=state,earlier_producers=list(producers),uncertain_prefix=list(uncertain),consumer_line=[x['id'] for x in lines[(ed,r['locus'])]]))
   if reliable and r['raw'] in FAMILY:producers.append(r['id'])
   if not reliable:uncertain.append(r['id'])
 summary={}
 for ed in EDS:
  summary[ed]={}
  for phase in ['f83r_development','other_exposed_pages']:
   cc=[c for c in cases if c['consumer']['edition']==ed and (c['consumer']['page']=='f83r')==(phase=='f83r_development')]
   counts=dict(collections.Counter(c['status'] for c in cc));assess=counts.get('AVAILABLE',0)+counts.get('MISSING_PREDECESSOR',0)
   decision='CONTRADICTED' if counts.get('MISSING_PREDECESSOR',0) else 'NECESSARY_ONLY' if assess else 'NO_ASSESSABLE_CAPACITY'
   summary[ed][phase]=dict(cases=len(cc),counts=counts,decision=decision,missing_pages=sorted({c['consumer']['page'] for c in cc if c['status']=='MISSING_PREDECESSOR'}))
 (B/'artifacts/SOURCE.json.gz').write_bytes(gzip.compress(json.dumps(rows,sort_keys=True,separators=(',',':')).encode(),mtime=0))
 save('CASES.json',cases);save('GUARD_RECEIPT.json',dict(command=command,receipt=receipt[0],P_groups=len(rows)))
 save('RESULT.json',dict(readers=summary,claim_ceiling='Necessary literal prior occurrence only; no meanings, synonyms or latest-reference confirmation.'))
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
