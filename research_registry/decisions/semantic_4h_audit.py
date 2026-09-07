"""Reproduce the four-hour baseline comparison. Run from repo root:
PYTHONPATH=. python research_registry/decisions/semantic_4h_audit.py
Read-only: emits JSON; retains source cases and distinguishes count units.
"""
from pathlib import Path
import json,subprocess,hashlib
from collections import Counter
from tools import research_registry as r,semantic_ideas as s,semantic_identity as i
root=Path(__file__).resolve().parents[2];base='e76e60a255f6c3ddf1d83c971d035fb995f1428c';D=root/'research_registry/decisions'
def before(p):return [json.loads(x)for x in subprocess.check_output(['git','show',base+':'+p],text=True,cwd=root).splitlines()if x]
def current(p):return r.read_jsonl(root/p)
A=before(s.DATA);AA=before(s.ARCHIVE);B=current(s.DATA);BA=current(s.ARCHIVE);ac={c['id']:c for c in A+AA};bc={c['id']:c for c in B+BA}
missing=[];changed_cases=[];missing_evidence=[]
for cid,c in ac.items():
 if cid not in bc:missing.append(cid);continue
 q=bc[cid];cases={z['id']:z for z in q['cases']}
 for z in c['cases']:
  if cases.get(z['id'])!=z:changed_cases.append([cid,z['id']])
 for e in c['evidence']:
  if e not in q['evidence']:missing_evidence.append([cid,e['path'],e['line']])
assert not missing and not changed_cases and not missing_evidence
ai=i.build_index(A,before(s.IDENTITIES),root,archived_ids=[c['id']for c in AA]);bi=i.build_index(B,current(s.IDENTITIES),root,archived_ids=[c['id']for c in BA]);oldcases={z['id']for c in ac.values()for z in c['cases']};newcases={z['id']for c in bc.values()for z in c['cases']};newids=sorted(set(bc)-set(ac));baselinequestions={d['decision_key']:d for d in before(s.FAILURES)};nowquestions={d['decision_key']:d for d in current(s.FAILURES)}
oldcorr=Counter(d['action']for d in before(s.CORRECTIONS));newcorr=Counter(d['action']for d in current(s.CORRECTIONS))
def summary(cards,archive,idx,qs):
 sem={c['id']for c in cards if c['claim_type']!='formal_role'};groupsem=0
 for st in range(0,idx.counts['groups'],100):
  for g in idx.page_groups(st,100):
   representative=idx.get_group(g['id'],limit=1)['member_ids'][0]
   groupsem+=representative in sem
 return {'active_cards':len(cards),'semantic_cards':len(sem),'formal_cards':len(cards)-len(sem),'archived_cards':len(archive),'all_source_cases':sum(len(c['cases'])for c in cards+archive),'equivalence_groups':idx.counts['multi_member_groups'],'total_display_reduction':len(cards)-idx.counts['groups'],'public_semantic_display':groupsem,'nonidentity_relations':idx.counts['relations'],'scoped_questions':len(qs),'direct_semantic_question_targets':len({t for q in qs.values()for t in q['targets']}&sem)}
x={'status':'ROOT_BASELINE_TO_CURRENT_SAME_UNIT_AUDIT_PASS','baseline_commit':subprocess.check_output(['git','rev-parse',base],text=True,cwd=root).strip(),'baseline':summary(A,AA,ai,baselinequestions),'current':summary(B,BA,bi,nowquestions),'source_preservation':{'baseline_active_plus_archived_cards':len(ac),'current_active_plus_archived_cards':len(bc),'all_original_cards_survive':True,'all_original_case_payloads_byte_equivalent_canonical_json':True,'all_original_evidence_objects_preserved':True,'baseline_all_source_case_ids':len(oldcases),'current_all_source_case_ids':len(newcases),'new_source_case_ids':sorted(newcases-oldcases),'new_card_ids':newids},'source_correction_action_delta':dict(newcorr-oldcorr),'peer_corrections':['JA compares baseline active-only4596cases with current active+archive4647; the resulting51 is not a new-case count. Same-unit totals are4640→4647, seven new cases.','JA decision-row/member-reference deltas are log statistics, not the operative equivalence-group or display-reduction delta. Root rebuilds both identity indices with their actual baseline/current cards and archives.'],'peer':{'path':'research_registry/decisions/ja_four_hour_source_preservation.json','sha256':r.digest(D/'ja_four_hour_source_preservation.json')},'current_input_sha256':{p:r.digest(root/p)for p in [s.DATA,s.ARCHIVE,s.IDENTITIES,s.FAILURES,s.CORRECTIONS]},'limits':'Source preservation and operative memory counts only; no global semantic assessment or new manuscript result.'}
x['delta']={k:x['current'][k]-x['baseline'][k]for k in x['baseline']}
def raw_summary(proposals, reviews):
 ids = {z['id'] for z in proposals}
 latest = {z['record_id']: z for z in reviews}
 method = sorted(k for k, v in latest.items() if k in ids and v['scope'] == 'method')
 return {'raw_proposals': len(ids), 'method_reviewed': len(method),
         'unreviewed_for_method': len(ids)-len(method), 'method_ids': method}
oldraw = raw_summary(before('research_registry/ideas.jsonl'), before('research_registry/curation.jsonl'))
nowraw = raw_summary(current('research_registry/ideas.jsonl'), current('research_registry/curation.jsonl'))
x['raw_queue'] = {'baseline': oldraw, 'current': nowraw,
                  'delta': {k: nowraw[k]-oldraw[k] for k in ['raw_proposals','method_reviewed','unreviewed_for_method']}}
x['peer_corrections'] += [
 'JB repeats a superseded baseline prose count10methodreviews; actual baseline latest curation contains11. The current final queue includes the later two JG method reviews.',
 'JB direct targets91→138include2formal-role cards at each end; root semantic counts are89→136.',
 'JF reviewed the earlier report at52/25/27raw/method/unreviewed; the final report includes JG and is52/27/25. Its expected JE relation count53 is now operative.'
]
x['additional_peer'] = {'path':'research_registry/decisions/jb_four_hour_claim_scope_audit.json',
                        'sha256':r.digest(D/'jb_four_hour_claim_scope_audit.json')}
for p in ['research_registry/ideas.jsonl','research_registry/curation.jsonl','research_registry/IDENTITY_REVIEW_INPUTS.json']:
 x['current_input_sha256'][p] = r.digest(root/p)
x['audit_program'] = {'path':'research_registry/decisions/semantic_4h_audit.py',
                      'sha256':r.digest(Path(__file__))}
print(json.dumps(x, ensure_ascii=False, indent=2))
