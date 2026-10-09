"""Explicit post-result consequence of the finite GDT1235 cap22 survivors."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json,gzip,hashlib
P=Path('research_registry/proposals/production_origin_supply_20261003');D=Path('experiments/yolo/gdt1235_ud_short_word_capacity');spec=json.loads((D/'src/SPEC.json').read_text());source=Path(spec['source']);groups=json.loads(gzip.decompress(source.read_bytes()));R=json.loads((D/'artifacts/RESULT.json').read_text());assert json.loads((D/'artifacts/VALIDATION.json').read_text())['status']=='PASS'
files=[source,D/'src/SPEC.json',D/'artifacts/RESULT.json',D/'artifacts/VALIDATION.json',P/'HUMAN_UD_POSTRESULT_AIN_AIIN_REMNANT_REVIEW_20261006.json',*sorted((D/'artifacts').glob('CERTIFICATE_*.json.gz'))]
out={'status':'ALL_NONTRIVIAL_UD_CODES_AT_MOST22_EXCLUDED_ALL_READINGS','recorded_utc':datetime.now(timezone.utc).isoformat(),'phase':'POST_RESULT_ANALYTICAL_CONSEQUENCE_NOT_PREREGISTERED_TEST','sources':{str(p):hashlib.sha256(p.read_bytes()).hexdigest()for p in files},'contract':'Exactly the1235fixed freeUD one-code-per-sourceletter whole-word22working-unit contract, with |C|<=22. Identity remains possible. This cap counts source-code entries, not output drawing types.22working drawings alone do not prove a22letter source alphabet.','registered_result_preserved':'GDT1235necessarybounds23IT22RF22ZLremain unchanged. This finite remnant closure is a separate consequence using already exposed whole forms.','readers':{},'limits':['No new physical atomicity or boundary evidence; rare dependencies of1235enumeration remain.','No sourceletter values, meanings, historical attestation or exclusion of larger/source-context/ligature systems.','No new full-code solver, native query, image or reserve; no independent confirmation.']}
for reader,rows in groups.items():
 C=json.loads(gzip.decompress((D/f'artifacts/CERTIFICATE_{reader}.json.gz').read_bytes()));A=set(spec['signs']);W={tuple(r['units'])for r in rows};pairs={w for w in W if len(w)==2};survivors=[r for r in C['rows']if r['ud']['status']=='UD'and r['bound']<=22];cases=[]
 witness={}
 for form in ('an','ain','aiin'):
  hit=[r for r in rows if r['ivtff_group_raw']==form];assert all(tuple(r['units'])==tuple(form)for r in hit)
  witness[form]={'panel_count':len(hit),'pages':sorted({r['page']for r in hit}),'first_occurrence':hit[0]if hit else None}
 for case in survivors:
  S=set(case['singletons']);missing=A-S;B={(g,)for g in S}|{p for p in pairs if not set(p)<=S};extra=B-{(g,)for g in S};record={'mask':case['mask'],'missing_singletons':sorted(missing),'forced_entries':len(B),'forced_long_codes':[list(w)for w in sorted(extra)],'free_entry_slots_at_cap22':22-len(B)}
  assert tuple('ain')in W and tuple('aiin')in W
  if missing in ({'i'},{'i','n'}):
   assert len(B)==21 and all('i'not in w for w in B);assert extra==(set()if missing=={'i'}else{tuple('an')})
   n1,n2=Counter('ain'),Counter('aiin');assert n1['i']==1 and n2['i']==2
   assert all(n2[g]<2 for g in n1 if g!='i')
   record.update(contradiction='ONE_I_CODE_FORCED_TO_SINGLETON_I',proof='All21mandatory entries contain no i. One additional i-containing code L must cover ain, hence has exactly one i and uses only a,i,n. To cover aiin it must occur twice, so cannot contain a or n (each occurs once). Thus L=i, contradicting the exact singleton set.')
  elif missing=={'n'}:
   assert len(B)==22 and extra=={tuple('an')};assert all('n'not in w or w==tuple('an')for w in B)
   assert not any(tuple('aiin')[j:j+2]==tuple('an')for j in range(3))
   record.update(contradiction='FIXED_AN_CODE_CANNOT_COVER_AIIN',proof='The21singletons plus an use all22entries. Only an contains n, but aiin contains no contiguous an; no parse is possible.')
  else:raise AssertionError(('Unaccounted residual case',reader,missing))
  cases.append(record)
 assert [set(x['missing_singletons'])for x in cases]==({'IT2a':[],'RF1b':[{'i'}],'ZL3b':[{'i','n'},{'n'},{'i'}]}[reader])
 out['readers'][reader]={'registered_bound':R['readers'][reader]['summary']['necessary_nontrivial_bound'],'remaining_sets_at22':len(cases),'all_remaining_cases':cases,'whole_form_witnesses':witness,'decision':'EXCLUDED_NONTRIVIAL_AT_MOST22','basis':'Registered bound alone'if not cases else'Registered complete necessary cases plus explicit post-result word-count contradictions'}
(P/'UD22_POSTRESULT_CAPACITY_CLOSURE_20261006.json').write_text(json.dumps(out,indent=2)+'\n')
print({r:{'cases':len(v['all_remaining_cases']),'word_counts':{w:q['panel_count']for w,q in v['whole_form_witnesses'].items()}}for r,v in out['readers'].items()})
