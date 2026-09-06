import argparse,csv,hashlib,io,json,re,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];ROOT=E.parents[2]
def enc(x):return json.dumps(x,sort_keys=True,separators=(',',':'))+'\n'
def save(n,x,check=False):
 p=E/'artifacts'/n
 if check:assert p.read_text()==enc(x),n
 else:p.write_text(enc(x))
def query(q):
 cmd=['./vmanus-exp','query-tsv',q['source'],'--selector',q['selector']]
 for v in q['allow']:cmd+=['--allow',v]
 cmd+=['--columns',','.join(q['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r'];p=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True);reader=csv.DictReader(io.StringIO(p.stdout),delimiter='\t');assert reader.fieldnames==q['columns'];rows=list(reader);stats=[json.loads(x[len('GUARD_STATS '):]) for x in p.stderr.splitlines() if x.startswith('GUARD_STATS ')];assert len(stats)==1 and stats[0]['selected']==len(rows)
 assert all(r[q['selector']] in q['allow'] and not r[q['selector']].startswith('f84') for r in rows)
 return rows,dict(command=cmd,stats=stats[0],projection_sha256=hashlib.sha256(p.stdout.encode()).hexdigest())
def derive(data,s):
 batches={q['name']:data[q['name']] for q in s['queries'] if q['name'].startswith('LM')};allfolios=[];issues=[]
 for q in s['queries'][2:]:
  rr=data[q['name']];ff=[r['physical_folio'] for r in rr]
  if len(rr)!=q['expected_rows']:issues.append(q['name']+'_ROW_COUNT')
  if len(set(ff))!=len(ff):issues.append(q['name']+'_DUPLICATE_FOLIO')
  allfolios+=ff
 if len(allfolios)!=60 or len(set(allfolios))!=60:issues.append('EXPOSURE_NOT_DISJOINT_60')
 if len({r['page'] for r in data['ANN']})!=len(data['ANN']):issues.append('ANN_DUPLICATE_PAGE')
 exposure=dict(batches=batches,physical_folios=sorted(set(allfolios)),rows=len(allfolios),unique_folios=len(set(allfolios)),consistent=not issues,issues=issues)
 ann={};zl={}
 for r in data['ANN']:ann.setdefault(r['page'],r)
 for r in data['ZL']:zl.setdefault(r['page'],r)
 safe=[]
 for page in s['allowed_selectors']:
  a=ann.get(page,{});z=zl.get(page,{});match=re.match(r'^f(\d+)',page);folio='f'+match[1] if match else None;tags=a.get('source_tags','');eligible='SOURCE_HERBAL_PAGE' in tags and z.get('language') in ['A','B'] and folio is not None
  safe.append(dict(page=page,physical_folio=folio,source_tags=tags,language=z.get('language'),section=z.get('section'),hand=z.get('hand'),ann_quire=a.get('quire'),zl_quire=z.get('quire'),quire=a.get('quire') or z.get('quire'),ann_present=bool(a),zl_present=bool(z),eligible_pool=eligible))
 if issues:return exposure,safe,[],dict(status='SOURCE_INCONSISTENCY_STOP',issues=issues,remainder_pages=None,remainder_physical_folios=None)
 pool=[r for r in safe if r['eligible_pool']];remainder=[r for r in pool if r['physical_folio'] not in set(allfolios)];result=dict(status='NEW_METADATA_CANDIDATES_AVAILABLE_NO_VISUAL_ADMISSION' if remainder else 'NO_NEW_PHYSICAL_FOLIOS_IN_CURRENT_SCOPE',old_exposure_rows=len(allfolios),old_exposure_folios=len(set(allfolios)),safe_selectors=len(safe),eligible_pool_pages=len(pool),eligible_pool_folios=len({r['physical_folio'] for r in pool}),remainder_pages=len(remainder),remainder_physical_folios=len({r['physical_folio'] for r in remainder}),remaining_folios=sorted({r['physical_folio'] for r in remainder}))
 return exposure,safe,remainder,result
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');args=ap.parse_args();s=json.loads((E/'src/SPEC.json').read_text())
 if args.check:data=json.loads((E/'artifacts/PROJECTED_METADATA.json').read_text())
 else:
  data={};guards={}
  for q in s['queries']:data[q['name']],guards[q['name']]=query(q)
  save('PROJECTED_METADATA.json',data);save('GUARD.json',guards)
 exposure,safe,remainder,result=derive(data,s)
 for n,x in [('OLD_EXPOSURE.json',exposure),('SAFE_METADATA.json',safe),('REMAINDER.json',remainder),('RESULT.json',result)]:save(n,x,args.check)
 print(enc(result))
if __name__=='__main__':main()
