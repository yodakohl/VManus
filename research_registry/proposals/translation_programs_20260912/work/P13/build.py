import json,csv,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P13');S=D.parent/'P11/INPUT.json';L=D.parent/'P11/COMMON_LEXICON.tsv'
materials={r['word']:r['value'] for r in csv.DictReader(L.open(),delimiter='\t') if r['type']=='MATERIAL'}
targets={'chor':{'raw':'unbearbeitetes Blütenmaterial','processed':'Blütenzubereitung','neutral':'Blütenmaterial'},'cthy':{'raw':'unbearbeitetes Kraut','processed':'Krautzubereitung','neutral':'Krautmaterial'}};verbs={'sho':'vermische','qotchy':'zerkleinere'}
records={}
for r in json.loads(S.read_text())['lines']:
 rid=r['locus'].split('.')[0];records.setdefault(rid,[]).extend(dict(record=rid,at=r['locus']+':'+str(i),word=w) for i,w in enumerate(r['groups'],1))
def dump(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tab(n,rs):
 with (D/n).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rs[0])+['row_status'],delimiter='\t',lineterminator='\n');wr.writeheader();wr.writerows(dict(r,row_status='recorded') for r in rs)
dump('SOURCE.json',dict(sources=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in [S,L]],decision_sha256=hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest(),sealed=['f84','f84r'],exposure='Previously exposed HERB4; no validation partition'))
dump('MODEL.json',dict(materials=materials,targets=targets,verbs=verbs,trigger='preceding sho or qotchy within record',identity='same whole within record',completion='after explicit argument, not at earlier verb'))
actions=[];occ=[];coverage=[]
for rid,ts in records.items():
 for i,t in enumerate(ts):
  if t['word'] not in verbs:continue
  dest=None
  for j in range(i+1,len(ts)):
   if ts[j]['word'] in verbs:break
   if ts[j]['word'] in materials:dest=ts[j];break
  actions.append(dict(record=rid,at=t['at'],word=t['word'],argument=dest['at'] if dest else '',argument_word=dest['word'] if dest else ''))
 lookup={t['at']:i for i,t in enumerate(ts)}
 for i,t in enumerate(ts):
  if t['word'] not in targets:continue
  past=[a for a in actions if a['record']==rid and lookup[a['at']]<i]
  trigger=past[-1] if past else None
  producers=[a for a in past if a['argument_word']==t['word'] and lookup[a['argument']]<i]
  inputs=[a for a in past if a['argument']==t['at']]
  occ.append(dict(record=rid,at=t['at'],word=t['word'],trigger=trigger['at'] if trigger else '',trigger_word=trigger['word'] if trigger else '',trigger_argument=trigger['argument'] if trigger else '',trigger_argument_word=trigger['argument_word'] if trigger else '',P_sense='processed' if trigger else 'raw',prior_producers=','.join(a['at'] for a in producers),current_input=','.join(a['at'] for a in inputs),status='SUPPORTED_PROCESS_STATE' if trigger and producers else 'UNSUPPORTED_RESULT_ASSUMPTION' if trigger else 'NO_SWITCH',U_conflict=bool(producers)))
 coverage.append(dict(record=rid,groups=len(ts),hypothesis=sum(t['word'] in materials or t['word'] in verbs for t in ts)))
tab('ALL_ACTIONS.tsv',actions);tab('ALL_TARGETS.tsv',occ);tab('COVERAGE.tsv',coverage)
for mode in ['U','P','N']:
 alignment=[]
 for rid,ts in records.items():
  md=['# '+rid+' / '+mode,'','Alle Bedeutungen und Prozesszuordnungen hypothetisch. ⟦…⟧ offen.','']
  for t in ts:
   w=t['word'];reading=materials.get(w,'⟦'+w+'⟧')
   if w in targets:
    o=next(o for o in occ if o['at']==t['at']);sense='raw' if mode=='U' else 'neutral' if mode=='N' else o['P_sense'];reading=targets[w][sense]+' [Auslöser='+o['trigger']+'; frühere Verarbeitung='+o['prior_producers']+'; aktuelles Eingabeargument='+o['current_input']+']'
   if w in verbs:
    a=next(a for a in actions if a['at']==t['at']);name=materials.get(a['argument_word'],'?')
    if a['argument_word'] in targets:
     o=next(o for o in occ if o['at']==a['argument']);sense='raw' if mode=='U' else 'neutral' if mode=='N' else o['P_sense'];name=targets[a['argument_word']][sense]
    reading=verbs[w]+' '+name+' [Argument='+a['argument']+']'
   alignment.append(dict(record=rid,at=t['at'],word=w,reading=reading));md.append(t['at']+' '+reading)
  (D/(rid+'_'+mode+'.md')).write_text('\n'.join(md)+'\n')
 tab('ALIGNMENT_'+mode+'.tsv',alignment)
dump('RESULT.json',dict(groups=145,hypothesis_positions=sum(r['hypothesis'] for r in coverage),open_positions=145-sum(r['hypothesis'] for r in coverage),target_occurrences=len(occ),switches=sum(o['P_sense']=='processed' for o in occ),supported_switches=sum(o['status']=='SUPPORTED_PROCESS_STATE' for o in occ),current_input_switches=sum(bool(o['current_input']) and o['P_sense']=='processed' for o in occ),other_argument_switches=sum(o['P_sense']=='processed' and o['trigger_argument_word']!=o['word'] for o in occ),U_conflicts=sum(o['U_conflict'] for o in occ),actions=len(actions),bound_actions=sum(bool(a['argument']) for a in actions),confirmed_meanings=0))
print((D/'RESULT.json').read_text())
