import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parents[1];R=B.parents[2]
def main():
 lock=json.loads((B/'src/REGISTRATION_LOCK.json').read_text())
 for p,h in lock['hashes'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
 old=json.loads((R/'research_registry/proposals/production_origin_supply_20261003/OKA_OTA_PARADIGM_CONTEXT_RESULT_20261008.json').read_text());out=json.loads((B/'artifacts/RESULT.json').read_text())
 count=0
 for reader,block in old['readers'].items():
  expected=[]
  for row in block['all_old_occurrences']:
   target_id=row['occurrence']['source_ids'][0];gs=row['raw_line']['groups'];g=next(x for x in gs if x[0]==target_id);p=next(x for x in gs if int(x[1])==int(g[1])-1)
   assert p[4]==g[3]=='DEFINITE_SPACE';prediction={'aiin':'okal','kaiin':'okal'}.get(p[2],'okar')
   expected.append({'target_id':target_id,'previous':p[2],'observed':g[2],'predicted':prediction,'correct':prediction==g[2]})
  observed=out['nomination_fit'][reader];assert observed['events']==expected;assert observed['correct']==sum(x['correct'] for x in expected) and observed['total']==len(expected);count+=len(expected)
  line=next(x for x in old['qoka_o_same_locus_reader_comparison'][reader] if x['metadata']['locus']=='f58v.26');assert line==out['fixed_case'][reader]['raw_line'];groups={g[0]:g for g in line['groups']};case=out['fixed_case'][reader];p=groups[case['previous_id']];g=groups[case['target_id']]
  assert [p[2],g[2]]==[case['previous'],case['observed']];assert int(g[1])==int(p[1])+1 and p[4]==g[3]=='DEFINITE_SPACE'
  if reader=='IT2a':assert g[2]=='okalar' and case['decision']=='INELIGIBLE_WHOLE_FORM' and not case['eligible'] and case['predicted'] is None
  else:assert (p[2],g[2],case['predicted'],case['decision'],case['eligible'])==('qokeos','okal','okar','CONTRADICTION',True)
 assert not out['full_transfer_census_executed'];assert out['status']=='KNOWN_COUNTERCASE_STOP_BEFORE_BROAD_TRANSFER'
 v={'status':'PASS','nomination_events_checked':count,'case_readings_checked':3,'scope':'Source/identity/seam/prediction and stop-account check, independent implementation with sharedold915source. No newimage or global transfer test.'};(B/'artifacts/VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
if __name__=='__main__':main()
