"""Pre-implementation literal ordering diagnostic, not a reference/meaning scorer."""
import hashlib,json
from pathlib import Path
B=Path(__file__).resolve().parent
p=B/'F83R_JOINT_MEDICAL_SOURCE_PACKET_20260920.json';packet=json.loads(p.read_text())
gram=json.loads((B/'F83R_JOINT_MEDICAL_GRAMMAR_20260920.json').read_text());core=gram['core_dictionary'];rows=[]
for edition,paragraphs in packet['readers'].items():
 prior_apply=None;prior_med=None;prior_site=None;index=0;history=[]
 for para in paragraphs:
  for line in para['lines']:
   assert len(line['words'])==len(line['source_ids'])
   for word,source_id in zip(line['words'],line['source_ids']):
    here=dict(id=source_id,raw=word,position=index+1,paragraph=para['id']);history.append(here)
    if word in ['qokal','qokeedy']:
     between=[] if prior_apply is None else history[prior_apply['position']:index]
     rows.append(dict(edition=edition,target=here,tag=core[word],previous_literal_qokal=prior_apply,previous_literal_shedy=prior_med,previous_literal_site_form=prior_site,intervening_groups_from_qokal=None if prior_apply is None else len(between),noncore_intervening=None if prior_apply is None else sum(x['raw'] not in core for x in between),semantic_reference_asserted=False))
    if word=='qokal':prior_apply=here
    if word=='shedy':prior_med=here
    if word in ['qokaiin','lchedy']:prior_site=here
    index+=1
out=dict(status='LITERAL_ORDER_PRECHECK_ONLY',packet_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),rows=rows,unknowns_still_unknown=True,reference_binding_proved=False,meaning_test=False,confirmed_words=0)
(B/'F83R_JOINT_MEDICAL_ORDER_PRECHECK_20260920.json').write_text(json.dumps(out,indent=2)+'\n')
for r in rows:print(r['edition'],r['target']['id'],r['target']['raw'],'previous_qokal=',r['previous_literal_qokal']['id'] if r['previous_literal_qokal'] else None,'previous_site=',r['previous_literal_site_form']['id'] if r['previous_literal_site_form'] else None,'unknown_between=',r['noncore_intervening'])
