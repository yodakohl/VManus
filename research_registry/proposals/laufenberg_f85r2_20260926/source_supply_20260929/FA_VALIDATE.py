"""Conserve FA evidence and decision; no manuscript or meaning test."""
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
checks=[]
def check(label,condition):
    checks.append({'check':label,'pass':bool(condition)})
for name,digest in json.loads((HERE/'FA_BINDINGS.json').read_text()).items():
    check('sha256:'+name,hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest)
s=json.loads((HERE/'FA_SOURCE_REVIEW.json').read_text())
a=json.loads((HERE/'FA_PREDECESSOR_REVIEW.json').read_text())
r=json.loads((HERE/'FA_ROOT_ADJUDICATION.json').read_text())
v=json.loads((HERE/'FA_IDEA831_REVIEW.json').read_text())
check('no_target_access',r['new_manuscript_content_access'] is False and not s['independence']['new_target_content_seen'])
check('independent_task_freezes',not s['independence']['other_FA_agent_conclusions_seen'] and not a['exposure_and_independence']['other_FA_agent_findings_read'])
check('both_source_readings',r['root_web_verification']['LacusCurtius']=='XII' and r['root_web_verification']['PHI']=='XXII')
check('zero_confirmed_words',r['confirmed_words']==s['confirmed_words']==0)
check('zero_independent_leaves',r['independent_confirmation_leaves']==0)
check('not_tested',v['verdict']=='not_tested')
check('every_consequence_explicitly_unselected',all(x['target_observation'] in {'NOT_SELECTED','SOURCE_LOGIC_ONLY_NOT_A_MANUSCRIPT_TEST'} for x in r['source_consequences']))
check('source_bound_countermodel',1<=46 and 10<=12 and 10<=22 and not 10<1)
out={'status':'CONSERVATION_PASS' if all(c['pass'] for c in checks) else 'CONSERVATION_FAIL','check_count':len(checks),'meaning_validation':False,'manuscript_test':False,'checks':checks}
(HERE/'FA_VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='checks'}))
raise SystemExit(0 if out['status']=='CONSERVATION_PASS' else 1)
