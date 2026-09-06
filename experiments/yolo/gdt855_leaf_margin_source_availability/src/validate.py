"""Independent first-record join, exposure-set and remainder audit."""
import json,re
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def read(n):return json.loads((E/'artifacts'/n).read_text())
s=json.loads((E/'src/SPEC.json').read_text());data=read('PROJECTED_METADATA.json');old=read('OLD_EXPOSURE.json');safe=read('SAFE_METADATA.json');remaining=read('REMAINDER.json');result=read('RESULT.json');guards=read('GUARD.json');issues=[];folios=[]
for q in s['queries']:
 rr=data[q['name']];assert all(set(r)==set(q['columns']) for r in rr);assert all(r[q['selector']] in q['allow'] and not r[q['selector']].startswith('f84') for r in rr);assert guards[q['name']]['stats']['selected']==len(rr)
 if q['name'].startswith('LM'):
  f=[r['physical_folio'] for r in rr];folios.extend(f)
  if len(rr)!=q['expected_rows']:issues.append(q['name']+'_ROW_COUNT')
  if len(f)!=len(set(f)):issues.append(q['name']+'_DUPLICATE_FOLIO')
if len(folios)!=60 or len(set(folios))!=60:issues.append('EXPOSURE_NOT_DISJOINT_60')
if len(set(r['page'] for r in data['ANN']))!=len(data['ANN']):issues.append('ANN_DUPLICATE_PAGE')
assert old['issues']==issues and old['consistent']==(not issues) and old['physical_folios']==sorted(set(folios)) and old['rows']==len(folios) and old['unique_folios']==len(set(folios))
for q in s['queries'][2:]:assert old['batches'][q['name']]==data[q['name']]
assert [r['page'] for r in safe]==s['allowed_selectors'];pool=[]
for r in safe:
 page=r['page'];a=next((x for x in data['ANN'] if x['page']==page),{});z=next((x for x in data['ZL'] if x['page']==page),{});m=re.match('^f([0-9]+)',page);f='f'+m.group(1) if m else None;eligible=('SOURCE_HERBAL_PAGE' in a.get('source_tags','')) and z.get('language') in ('A','B') and f is not None
 assert r==dict(page=page,physical_folio=f,source_tags=a.get('source_tags',''),language=z.get('language'),section=z.get('section'),hand=z.get('hand'),ann_quire=a.get('quire'),zl_quire=z.get('quire'),quire=a.get('quire') if a.get('quire') else z.get('quire'),ann_present=bool(a),zl_present=bool(z),eligible_pool=eligible)
 if eligible:pool.append(r)
if issues:assert remaining==[] and result==dict(status='SOURCE_INCONSISTENCY_STOP',issues=issues,remainder_pages=None,remainder_physical_folios=None)
else:
 expected=[r for r in pool if not any(r['physical_folio']==f for f in folios)];assert remaining==expected;expectedresult=dict(status='NEW_METADATA_CANDIDATES_AVAILABLE_NO_VISUAL_ADMISSION' if expected else 'NO_NEW_PHYSICAL_FOLIOS_IN_CURRENT_SCOPE',old_exposure_rows=60,old_exposure_folios=60,safe_selectors=len(safe),eligible_pool_pages=len(pool),eligible_pool_folios=len(set(r['physical_folio'] for r in pool)),remainder_pages=len(expected),remainder_physical_folios=len(set(r['physical_folio'] for r in expected)),remaining_folios=sorted(set(r['physical_folio'] for r in expected)));assert result==expectedresult
(E/'artifacts/VALIDATION.json').write_text(json.dumps(dict(status='PASS_INDEPENDENT_METADATA_JOIN_EXPOSURE_AND_SUBTRACTION',source_exposure_consistent=not issues,outcomes_accessed=False,images_accessed=False),indent=2)+'\n');print('PASS')
