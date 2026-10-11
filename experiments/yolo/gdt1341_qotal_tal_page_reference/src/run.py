from pathlib import Path
import collections,gzip,hashlib,json
B=Path(__file__).resolve().parents[1];R=B.parents[2];PAGES=['f75v','f83r','f104v'];EDS=['ZL3b','IT2a','RF1b'];CLEAR={'DEFINITE_SPACE','LINE_START','LINE_END'}
def read(p):return json.loads(p.read_text())
def scene(r):
 n=int(r['locus'].split('.')[1]);return 'P1' if n<=8 else 'P2' if n<=17 else 'P3' if n<=24 else 'LOWER'
def clear(r):return r['left'] in CLEAR and r['right'] in CLEAR
def main():
 for p,h in read(B/'src/REGISTRATION_LOCK.json')['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 rows=[]
 for ed in EDS:
  for phase in ['DISCOVERY','EVALUATION']:
   d=read(R/f'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts/SOURCE_{phase}_{ed}.json')
   for line in d['lines']:
    m=line['metadata']
    if m['page'] not in PAGES or m['kind']!='P':continue
    assert m['edition']==ed
    for ident,index,raw,left,right in line['groups']:rows.append({'id':ident,'edition':ed,'page':m['page'],'locus':m['locus'],'row':int(m['source_row_index']),'index':int(index),'count':int(m['source_group_count']),'raw':raw,'left':left,'right':right})
 assert len({r['id'] for r in rows})==len(rows);rows.sort(key=lambda r:(r['edition'],r['page'],r['row'],r['index']));pages={};summary={}
 for ed in EDS:
  records=[]
  for page in PAGES:
   rr=[r for r in rows if r['edition']==ed and r['page']==page];assert rr
   for locus in {r['locus'] for r in rr}:
    line=[r for r in rr if r['locus']==locus];assert [r['index'] for r in line]==list(range(1,line[0]['count']+1))
   donors=[r for r in rr if r['raw']=='qotal'];pairs=[];uncertain=[];joined=[r for r in rr if r['raw']=='cheytal']
   for i,left in enumerate(rr[:-1]):
    right=rr[i+1]
    if left['locus']!=right['locus'] or left['index']+1!=right['index'] or (left['raw'],right['raw'])!=('chey','tal'):continue
    strict=clear(left) and clear(right) and left['right']==right['left']=='DEFINITE_SPACE';earlier=[d for d in donors if (d['row'],d['index'])<(left['row'],left['index'])];good=[d for d in earlier if clear(d)];bad=[d for d in earlier if not clear(d)];status='NECESSARY_POINTER_AVAILABLE' if good else 'SOURCE_UNCERTAIN' if bad else 'MISSING_LITERAL_PRODUCER';rec={'chey':left,'tal':right,'strict':strict,'earlier_strict_producers':good,'earlier_uncertain_producers':bad,'latest_strict_producer':good[-1] if good else None,'status':status}
    if page=='f83r':rec['same_scene_strict_producers']=[d for d in good if scene(d)==scene(left)]
    (pairs if strict else uncertain).append(rec)
   records.append({'page':page,'P_groups':len(rr),'qotal_all':donors,'strict_consumers':pairs,'uncertain_pairs':uncertain,'joined_cheytal':joined})
  tests=[c for p in records if p['page']!='f83r' for c in p['strict_consumers']];statuses=[c['status'] for c in tests];decision='NO_CAPACITY' if not tests else 'FIXED_PAGE_RULE_CONTRADICTED' if 'MISSING_LITERAL_PRODUCER' in statuses else 'SOURCE_UNCERTAIN' if 'SOURCE_UNCERTAIN' in statuses else 'NECESSARY_CAPACITY_ONLY';pages[ed]=records;summary[ed]={'additional_strict_consumers':len(tests),'status_counts':dict(collections.Counter(statuses)),'decision':decision};print(ed,summary[ed],flush=True)
 (B/'artifacts/SOURCE.json.gz').write_bytes(gzip.compress(json.dumps(rows,sort_keys=True,separators=(',',':')).encode(),mtime=0));(B/'artifacts/CASES.json').write_text(json.dumps(pages,indent=2,sort_keys=True)+'\n');(B/'artifacts/RESULT.json').write_text(json.dumps({'readers':summary,'claim_ceiling':'Fixed page-bounded literal prerequisite only; latest-vs-any resolver untested, no meaning or anaphora confirmation.'},indent=2,sort_keys=True)+'\n')
if __name__=='__main__':main()
