#!/usr/bin/env python3
import csv,json,hashlib,itertools
from pathlib import Path
from collections import defaultdict,Counter
D=Path('research_registry/proposals/translation_programs_20260912/work/P01');S=D.parent/'P11/INPUT.json'
def js(n,x):(D/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def tab(n,rs,fields=None):
 with (D/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rs[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rs)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=json.loads(S.read_text())['lines'];findings={'cthy':'Schwellung','chor':'Schmerz','shor':'Absonderung','chol':'Trockenheit','shol':'Feuchtigkeit','shey':'Hitze'};grades={'dair':'A','dain':'B','daiin':'C'};actions={'sho':'Benetzen','chkaiin':'Trocknen','qotchy':'Kühlen'};states={'sho':'ist benetzt','chkaiin':'ist getrocknet','qotchy':'ist gekühlt'}
js('MODEL.json',{'findings':findings,'grades':grades,'D_actions':actions,'R_states':states,'rule_priority':['heat->cool','latest moisture wet->dry','latest moisture dry->moisten','otherwise unresolved'],'all_authored_hypotheses':True,'unmentioned_is_not_absent':True})
js('SOURCE.json',{'path':str(S),'sha256':sha(S),'decision_sha256':sha(D/'DECISION.md'),'source_reading_notes':'experiments/yolo/gdt809_record_conditioned_whole_head_semantic_tournament/artifacts/JOINT_COMPETING_PARAGRAPH_READINGS.md'})
records=defaultdict(list)
for r in source:
 for i,w in enumerate(r['groups'],1):records[r['locus'].split('.')[0]].append({'locus':r['locus']+':'+str(i),'line':r['locus'],'word':w})
cases=[];obs=[];gg=[];allalign={};coverage=[]
for mode in ['D','R']:
 alignment=[]
 for rec,words in records.items():
  seen={};moisture=None;moistloc=None;heatloc=None;levels={}
  for i,x in enumerate(words):
   w=x['word'];loc=x['locus'];reading='['+w+']';role='OPEN'
   if w in findings:
    role='FINDING';reading=findings[w];seen[w]=loc
    if w in ['chol','shol']:moisture=w;moistloc=loc
    if w=='shey':heatloc=loc
    if mode=='D':obs.append({'record':rec,'locus':loc,'word':w,'finding':findings[w],'status':'AUTHORED_MEANING'})
   elif w in grades:
    role='GRADE';left=words[i-1] if i and words[i-1]['line']==x['line'] else None;target=left['locus'] if left and left['word'] in findings else 'UNBOUND'
    reading='Grad '+grades[w]+' → '+target
    if target!='UNBOUND':levels[left['word']]=grades[w]
    if mode=='D':gg.append({'record':rec,'locus':loc,'word':w,'grade':grades[w],'target':target})
   elif w in actions:
    role='ACTION' if mode=='D' else 'DESCRIBED_STATE';reading=actions[w] if mode=='D' else states[w]
    expected='Kühlen' if heatloc else 'Trocknen' if moisture=='shol' else 'Benetzen' if moisture=='chol' else 'UNRESOLVED'
    reason=heatloc or moistloc or 'NONE'
    register={'swelling_mentioned':'cthy' in seen,'pain_mentioned':'chor' in seen,'secretion_mentioned':'shor' in seen,'latest_moisture':moisture,'heat_mentioned':bool(heatloc),'grades':dict(sorted(levels.items()))}
    if mode=='D':cases.append({'record':rec,'locus':loc,'word':w,'observed_action_hypothesis':actions[w],'expected_by_authored_rule':expected,'reason_locus':reason,'diagnostic_conclusion':'Hitze-betont' if heatloc else 'Feuchte-betont' if moisture=='shol' else 'Trockenheits-betont' if moisture=='chol' else 'UNRESOLVED','status':'NO_PRIOR_DECISIVE_FINDING' if expected=='UNRESOLVED' else 'MATCH_UNDER_ASSUMPTIONS' if expected==actions[w] else 'CONTRADICTS_AUTHORED_RULE','register':json.dumps(register,sort_keys=True),'nonempty_register':int(bool(seen))})
   alignment.append({'record':rec,'locus':loc,'word':w,'role':role,'reading':reading})
  aa=[r for r in alignment if r['record']==rec];coverage.append({'mode':mode,'record':rec,'groups':len(aa),'hypothesis_positions':sum(x['role']!='OPEN' for x in aa),'findings':sum(x['role']=='FINDING' for x in aa),'actions_or_states':sum(x['role'] in ['ACTION','DESCRIBED_STATE'] for x in aa)})
 assert len(alignment)==145
 tab('ALIGNMENT_'+mode+'.tsv',alignment);allalign[mode]=alignment
 text=['# P01 '+mode+' — vollständige hypothetische Fassung','','Offene Wörter bleiben geklammert. Symptome, Grade und Zustände/Maßnahmen sind Annahmen. Fallträger und Diagnosebezeichnungen sind nicht gelesene Namen.']
 for r in source:
  aa=[x for x in alignment if x['locus'].rsplit(':',1)[0]==r['locus']]
  text+=['','## '+r['locus'],'','Quelle: `'+r['raw_line']+'`','','Lesung: '+' · '.join(x['reading'] for x in aa)]
 (D/('READING_'+mode+'.md')).write_text('\n'.join(text)+'\n')
tab('ALL_DECISIONS.tsv',cases);tab('FINDINGS.tsv',obs);tab('GRADES.tsv',gg);tab('RECORD_COVERAGE.tsv',coverage)
pairs=[]
for a,b in itertools.combinations(cases,2):
 same=a['register']==b['register'];different=a['observed_action_hypothesis']!=b['observed_action_hypothesis'];nonempty=a['nonempty_register'] and b['nonempty_register']
 pairs.append({'a':a['locus'],'b':b['locus'],'same_observed_register':int(same),'different_action':int(different),'nonempty_register':int(nonempty),'status':'SAME_NONEMPTY_REGISTER_DIFFERENT_ACTION' if same and different and nonempty else 'SAME_EMPTY_REGISTER_NOT_FULL_CLINICAL_EQUIVALENCE' if same and not nonempty else 'NO_SAME_REGISTER_CONFLICT'})
tab('ALL_CASE_PAIRS.tsv',pairs)
result={'status':'PARTIAL_DIAGNOSTIC_RULE_COMPARISON','groups_each':145,'finding_forms':6,'grade_forms':3,'action_forms':3,'hypothesis_positions':sum(x['role']!='OPEN' for x in allalign['D']),'open_positions':sum(x['role']=='OPEN' for x in allalign['D']),'finding_occurrences':len(obs),'grade_occurrences':len(gg),'unbound_grades':sum(x['target']=='UNBOUND' for x in gg),'action_positions':len(cases),'decision_counts':dict(Counter(x['status'] for x in cases)),'case_pairs':len(pairs),'same_nonempty_register_different_action':sum(x['status']=='SAME_NONEMPTY_REGISTER_DIFFERENT_ACTION' for x in pairs),'same_empty_register_pairs':sum(x['status']=='SAME_EMPTY_REGISTER_NOT_FULL_CLINICAL_EQUIVALENCE' for x in pairs),'confirmed_meanings':0,'independent_confirmation_capacity':0,'held_pages_opened':0};js('RESULT.json',result);print(json.dumps(result,indent=2))
