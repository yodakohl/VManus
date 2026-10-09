import collections,csv,hashlib,io,json,re,subprocess
from fractions import Fraction
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 s=json.loads((B/'src/SPEC.json').read_text());lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((B/p).read_bytes()).hexdigest()==h
 for x in s['inputs']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
 allowed=json.loads((R/s['scope_spec']).read_text())['allowed'];assert len(set(allowed))==179 and all(not p.startswith('f84') and p!='f116v' for p in allowed)
 cmd=['./vmanus-exp','query-tsv',s['native_source'],'--selector','page']
 for p in allowed:cmd+=['--allow',p]
 cmd+=['--columns',','.join(s['columns'])]
 call=subprocess.run(cmd,cwd=R,text=True,capture_output=True,check=True)
 (B/'artifacts/GUARD_RECEIPT.json').write_text(json.dumps({'command':cmd,'receipt':call.stderr.strip(),'output_sha256':hashlib.sha256(call.stdout.encode()).hexdigest()},indent=2)+'\n')
 lines=collections.defaultdict(list);rawcount=0
 for row in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
  rawcount+=1
  if row['edition'] in s['readers']:lines[(row['edition'],row['page'],row['locus'])].append(row)
 pages=collections.defaultdict(list)
 for key,rows in lines.items():
  rows.sort(key=lambda x:int(x['source_group_index']));r=rows[0]
  assert [int(x['source_group_index']) for x in rows]==list(range(1,int(r['source_group_count'])+1))
  assert all(all(x[k]==r[k] for k in ['source_row_index','source_group_count','paragraph_start','paragraph_end','kind']) for x in rows)
  pages[key[:2]].append(rows)
 pattern=re.compile('|'.join(sorted(s['working_signs'],key=lambda x:(-len(x),x))))
 census={r:[] for r in s['readers']};raw_paras={};events={r:collections.Counter() for r in s['readers']};excluded={r:[] for r in s['readers']}
 for (reader,page),ls in sorted(pages.items()):
  ls.sort(key=lambda x:int(x[0]['source_row_index']));pending=[];last=None
  for line in ls:
   x=line[0];idx=int(x['source_row_index']);start=x['paragraph_start']=='1';end=x['paragraph_end']=='1'
   reason=None
   if pending:
    if idx!=last+1:reason='source_row_gap'
    elif x['kind']!='P':reason='non_P_interruption'
    elif start:reason='new_start_before_end'
    if reason:
     events[reader][reason]+=1;excluded[reader].append({'first':pending[0][0]['locus'],'last':pending[-1][0]['locus'],'reason':reason});pending=[]
   if x['kind']=='P' and start:pending=[line];events[reader]['marked_starts']+=1
   elif pending:pending.append(line)
   if pending and end:
    flat=[g for ln in pending for g in ln];counts=collections.Counter();bad=set()
    for g in flat:
     raw=g['ivtff_group_raw'];parts=pattern.findall(raw)
     if not raw or ''.join(parts)!=raw:bad.add('unsupported_raw_group')
     if g['left_separator'] not in s['permitted_separators'] or g['right_separator'] not in s['permitted_separators']:bad.add('interrupted_separator')
     counts.update(parts)
    events[reader]['complete_candidates']+=1
    identity=page+'|'+pending[0][0]['locus']+'|'+pending[-1][0]['locus']
    if bad:
     reason='+'.join(sorted(bad));events[reader]['excluded_'+reason]+=1;excluded[reader].append({'first':pending[0][0]['locus'],'last':pending[-1][0]['locus'],'reason':reason})
    else:
     rec={'id':identity,'page':page,'loci':[ln[0]['locus'] for ln in pending],'source_rows':[int(ln[0]['source_row_index']) for ln in pending],'groups':len(flat),'counts':[counts[u] for u in s['working_signs']]}
     census[reader].append(rec);raw_paras[(reader,identity)]=flat;events[reader]['retained']+=1
    pending=[]
   last=idx
  if pending:events[reader]['page_end_before_end']+=1;excluded[reader].append({'first':pending[0][0]['locus'],'last':pending[-1][0]['locus'],'reason':'page_end_before_end'})
 results={};certs={}
 for reader in s['readers']:
  rows=census[reader];active=[j for j in range(len(s['working_signs'])) if any(p['counts'][j] for p in rows)];basis={};chosen=[]
  for p in rows:
   vec=[Fraction(p['counts'][j]) for j in active]+[Fraction(-1)]
   for pivot,b in sorted(basis.items()):
    if vec[pivot]:
     fac=vec[pivot];vec=[x-fac*y for x,y in zip(vec,b)]
   nz=next((j for j,x in enumerate(vec) if x),None)
   if nz is not None:
    fac=vec[nz];basis[nz]=[x/fac for x in vec];chosen.append(p)
  rank=len(basis);m=len(active);status='NO_COMPLETE_PARAGRAPHS' if not rows else ('FIXED_INTEGER_PARAGRAPH_BALANCE_EXCLUDED' if rank==m+1 else 'NECESSARY_CAPACITY_ONLY')
  results[reader]={'status':status,'paragraphs':len(rows),'pages':len(set(p['page'] for p in rows)),'active_units':[s['working_signs'][j] for j in active],'rank':rank,'columns':m+1,'events':dict(events[reader]),'certificate_ids':[p['id'] for p in chosen]}
  certs[reader]=[{'paragraph':p,'raw_groups':raw_paras[(reader,p['id'])]} for p in chosen]
 result={'status':'BOTH_READERS_FIXED_INTEGER_PARAGRAPH_BALANCE_EXCLUDED' if all(x['status']=='FIXED_INTEGER_PARAGRAPH_BALANCE_EXCLUDED' for x in results.values()) else 'MIXED_OR_CAPACITY_LIMITED','guarded_rows':rawcount,'readers':results,'scope':'Exact22working-unit and own source-marked complete-paragraph contract; integer not modular; no word meanings.'}
 for name,obj in [('RESULT',result),('CENSUS',census),('CERTIFICATES',certs),('EXCLUSIONS',excluded)]: (B/('artifacts/'+name+'.json')).write_text(json.dumps(obj,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
