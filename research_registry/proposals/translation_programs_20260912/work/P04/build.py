#!/usr/bin/env python3
import csv,json,hashlib,itertools
from pathlib import Path
from collections import defaultdict
D=Path('research_registry/proposals/translation_programs_20260912/work/P04');P=D.parent/'P11'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def js(n,x):(D/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def tab(n,rows,fields=None):
 with (D/n).open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields or list(rows[0]),delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)
src=json.loads((P/'INPUT.json').read_text());old=json.loads((P/'MODEL.json').read_text())
materials=old['materials']|{'chocthy':'Feinpulver A','cthaiin':'Grobpulver B'}
goals={'cfhy':'Bindung einer feuchten Masse','taiin':'Klärung einer Flüssigkeit'}
lex=materials|old['locations']|old['other']|{w:v['D0'] for w,v in old['predicates'].items()}|goals|{'qotchy':'für den Zweck','sho':'füge hinzu','skey':'Auswahl-/Listenbedingung'}
records=defaultdict(list)
for line in src['lines']:
 for i,w in enumerate(line['groups'],1):records[line['locus'].split('.')[0]].append({'locus':line['locus']+':'+str(i),'line':line['locus'],'word':w})
js('SOURCE.json',{'input':str(P/'INPUT.json'),'input_sha256':sha(P/'INPUT.json'),'base_model':str(P/'MODEL.json'),'base_model_sha256':sha(P/'MODEL.json'),'decision_sha256':sha(D/'DECISION.md')})
js('MODEL.json',{'whole_values':lex,'all_hypotheses':True,'new_values':{w:lex[w] for w in ['chocthy','cthaiin','cfhy','taiin','sho','qotchy','skey']},'S':'if A absent use B; otherwise A','L':'use A and B','quantity':'symbolic Gamma; no numerical dose','functional_equivalence':'required, not assumed true'})
allops=[];allstates=[];allfields=[];alleq=[];network=[];summary=[];coverage=[]
for scenario in ['S_A','S_B','L_AB']:
 rows=[];ops=[];states=[];fields=[]
 for rec,words in records.items():
  topic=None;purpose=None;purpose_locus=None;claimed={};finish={};attrs={}
  for j,x in enumerate(words):
   w=x['word'];loc=x['locus'];role='KNOWN' if w in lex else 'OPEN';reading=lex.get(w,'['+w+']')
   if w in materials and j not in claimed:topic=loc
   if w=='qotchy':
    target=words[j+1] if j+1<len(words) and words[j+1]['word'] in goals else None
    if target:purpose=target['word'];purpose_locus=target['locus'];claimed[j+1]=loc
    else:purpose=None;purpose_locus=None
    reading='für '+goals.get(purpose,'?Zweck')
    ops.append({'scenario':scenario,'record':rec,'locus':loc,'kind':'PURPOSE','subject':topic or 'MISSING','target':purpose_locus or 'MISSING','purpose':purpose or 'MISSING','selection_related':0,'issues':'NONE' if target else 'MISSING_PURPOSE','reading':reading})
   elif w=='skey':
    pair=words[j+1:j+5];valid=len(pair)==4 and pair[0]['word'] in materials and pair[1]['word']=='daiin' and pair[2]['word'] in materials and pair[3]['word']=='daiin'
    if valid:
     a,b=pair[0],pair[2];selection=rec+':choice@'+loc
     for k in range(j+1,j+5):claimed[k]=loc
     finish[j+4]=selection
     selected=a['word'] if scenario=='S_A' else b['word'] if scenario=='S_B' else a['word']+'+'+b['word']
     reading=('bei vorhandenem '+materials[a['word']]+': verwende '+materials[a['word']] if scenario=='S_A' else 'bei fehlendem '+materials[a['word']]+': verwende '+materials[b['word']] if scenario=='S_B' else 'verwende beide: '+materials[a['word']]+' und '+materials[b['word']])+'; je Maß Γ'
     if scenario=='S_A':network.append({'record':rec,'condition_locus':loc,'original_locus':a['locus'],'original':a['word'],'replacement_locus':b['locus'],'replacement':b['word'],'condition':'original unavailable and replacement available','purpose_locus':purpose_locus or 'MISSING','purpose':purpose or 'MISSING','performance_preservation':'UNESTABLISHED'})
     ops.append({'scenario':scenario,'record':rec,'locus':loc,'kind':'CHOICE' if scenario!='L_AB' else 'JOINT_USE','subject':selection,'target':selected,'purpose':purpose or 'MISSING','selection_related':1,'issues':'EFFECT_EQUIVALENCE_UNESTABLISHED' if scenario!='L_AB' else 'JOINT_EFFECT_UNESTABLISHED','reading':reading})
    else:
     reading='[unvollständige Auswahl bei skey]';ops.append({'scenario':scenario,'record':rec,'locus':loc,'kind':'CHOICE','subject':'MISSING','target':'MISSING','purpose':purpose or 'MISSING','selection_related':0,'issues':'INCOMPLETE_PAIR','reading':reading})
   elif w=='sho':
    target=words[j+1] if j+1<len(words) and words[j+1]['word'] in materials else None
    if target:claimed[j+1]=loc
    reading='füge '+(materials[target['word']] if target else '?Zusatz')+' zu '+(topic or '?Träger')+' hinzu'
    ops.append({'scenario':scenario,'record':rec,'locus':loc,'kind':'ADD','subject':topic or 'MISSING','target':target['locus'] if target else 'MISSING','purpose':purpose or 'MISSING','selection_related':int(bool(topic and ':choice@' in topic)),'issues':';'.join(z for z in ['MISSING_SUBJECT' if not topic else '', 'MISSING_ADDITIVE' if not target else ''] if z) or 'NONE','reading':reading})
   elif w in ['chol','shol','shey','chkaiin']:
    reading=lex[w]+' → '+(topic or '?Träger');states.append({'scenario':scenario,'record':rec,'locus':loc,'word':w,'subject':topic or 'MISSING','selection_related':int(bool(topic and ':choice@' in topic))})
   if w=='daiin':
    prev=words[j-1] if j>0 and words[j-1]['line']==x['line'] else None
    target=prev['locus'] if prev and (prev['word'] in materials or prev['word'] in ['chol','shol','shey','chkaiin','shy']) else 'MISSING'
    fields.append({'scenario':scenario,'record':rec,'locus':loc,'target':target,'symbol':'Gamma','pair_field':int(j in claimed)})
   if j in finish:topic=finish[j]
   rows.append({'record':rec,'locus':loc,'word':w,'role':role,'claimed_by':claimed.get(j,'NA'),'reading':reading})
 assert len(rows)==145
 tab('ALIGNMENT_'+scenario+'.tsv',rows)
 out=['# P04 '+scenario+' — vollständige hypothetische Kapitelversion','','Die Quelle bleibt vollständig. Auch lesbare Werte und Bedingungen sind unbestätigte Annahmen.']
 for line in src['lines']:
  a=[x for x in rows if x['locus'].rsplit(':',1)[0]==line['locus']]
  out+=['','## '+line['locus'],'','Quelle: `'+line['raw_line']+'`','','Lesung: '+' · '.join(x['reading'] for x in a)]
 (D/('READING_'+scenario+'.md')).write_text('\n'.join(out)+'\n')
 for rec in records:
  a=[x for x in rows if x['record']==rec];coverage.append({'scenario':scenario,'record':rec,'groups':len(a),'hypothesis_positions':sum(x['role']!='OPEN' for x in a),'purpose_markers':sum(x['record']==rec and x['kind']=='PURPOSE' for x in ops),'choice_markers':sum(x['record']==rec and x['kind'] in ['CHOICE','JOINT_USE'] for x in ops)})
 summary.append({'scenario':scenario,'hypothesis_positions':sum(x['role']!='OPEN' for x in rows),'open_positions':sum(x['role']=='OPEN' for x in rows),'purpose_markers':sum(x['kind']=='PURPOSE' for x in ops),'choice_or_joint_markers':sum(x['kind'] in ['CHOICE','JOINT_USE'] for x in ops),'additions':sum(x['kind']=='ADD' for x in ops),'additions_to_selection':sum(x['kind']=='ADD' and x['selection_related'] for x in ops),'states_bound_to_selection':sum(x['selection_related'] for x in states),'unbound_gamma':sum(x['target']=='MISSING' for x in fields)})
 allops+=ops;allstates+=states;allfields+=fields
 for e in network:
  if scenario=='S_B':alleq.append({'record':e['record'],'edge':e['condition_locus'],'required_equality':'Performance(A,Gamma,oil;binding)=Performance(B,Gamma,oil;binding)','observed_performance':'NONE','branch_specific_compensation':'NONE','status':'REQUIRED_NOT_PROVED'})
tab('OPERATIONS.tsv',allops);tab('STATES.tsv',allstates);tab('VALUE_FIELDS.tsv',allfields);tab('SUBSTITUTION_NETWORK.tsv',network);tab('PERFORMANCE_REQUIREMENTS.tsv',alleq);tab('RECORD_COVERAGE.tsv',coverage)
chains=[{'edge1':a['condition_locus'],'edge2':b['condition_locus'],'shared_material':a['replacement'],'status':'CONDITIONS_MUST_BE_COMBINED'} for a in network for b in network if a['replacement']==b['original']]
tab('NETWORK_CHAINS.tsv',chains,['edge1','edge2','shared_material','status'])
av=[]
for a,b in itertools.product([0,1],repeat=2):av.append({'A_available':a,'B_available':b,'S_selection':'A' if a else 'B' if b else 'UNRESOLVED','L_selection':'A+B' if a and b else 'INCOMPLETE','status':'AUTHORED_SCENARIO_NOT_OBSERVED'})
tab('AVAILABILITY_SCENARIOS.tsv',av)
res={'status':'PARTIAL_CONDITIONAL_SUBSTITUTION_READING','groups_each':145,'summaries':summary,'directed_replacement_edges':len(network),'two_edge_chains':len(chains),'independently_bound_equal_performance':0,'branch_specific_compensations':0,'confirmed_meanings':0,'independent_confirmation_capacity':0,'held_pages_opened':0};js('RESULT.json',res);print(json.dumps(res,indent=2))
