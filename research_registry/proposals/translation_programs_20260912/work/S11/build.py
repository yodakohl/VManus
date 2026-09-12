from pathlib import Path
import csv,json,hashlib
D=Path(__file__).resolve().parent;W=D.parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def read(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def tab(n,k,rs):
 with (D/n).open('w') as f:
  w=csv.writer(f,delimiter='\t',lineterminator='\n');w.writerow(k+['row_status']);w.writerows([list(x)+['recorded'] for x in rs])
def js(n,x):(D/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
s=read(W/'S05/INPUT.tsv');lex=json.loads((W/'S10/MODEL.json').read_text())['lexicon'];comp=[];spans=[];dec=[]
for i,d in enumerate(s):
 if d['word'] not in {'chkaiin','qody'}:continue
 prefix=[x for x in s[:i] if x['record']==d['record']];heads=[x for x in prefix if x['word'] in {'chor','shor'}];qualities=[x for x in prefix if x['word'] in {'chol','shol'}];q=qualities[-1]['word'] if qualities else 'NONE'
 for m in ['FIRST','LAST']:
  claim=heads[0 if m=='FIRST' else -1] if heads else None;features=[x for x in heads if x is not claim]
  expect='REJECT' if claim and any(x['word']!=claim['word'] for x in features) else ('ACCEPT' if features and q=='chol' else 'UNKNOWN')
  assigned='ACCEPT' if d['word']=='chkaiin' else 'REJECT'
  dec.append((d['record'],d['at'],m,claim['at'] if claim else 'NONE',claim['word'] if claim else 'NONE',','.join(x['at'] for x in features) or 'NONE',q,expect,assigned,'UNBOUND' if expect=='UNKNOWN' else ('MODEL_MATCH' if expect==assigned else 'MODEL_CONTRADICTION')))
 boundaries=[(a,b,'BETWEEN_CLASSES') for a,b in zip(heads,heads[1:])]+([(heads[-1],d,'BEFORE_DECISION')] if heads else [])
 if not heads:boundaries=[(None,d,'NO_CLASS_ALL_PREFIX')]
 for a,b,kind in boundaries:
  start=next((j+1 for j,x in enumerate(prefix) if a and x['at']==a['at']),0);end=next((j for j,x in enumerate(prefix) if x['at']==b['at']),len(prefix));gap=prefix[start:end]
  spans.append((d['at'],kind,a['at'] if a else 'RECORD_START',b['at'],' '.join(x['word'] for x in gap) or 'EMPTY',len(gap)))
  for x in gap:comp.append((d['at'],kind,x['at'],x['word'],lex.get(x['word'],'OPEN')))
tab('DECISIONS.tsv',['record','decision_at','mode','claim_at','claim_word','feature_loci','latest_quality','expected','assigned','result'],dec)
tab('SPANS.tsv',['decision_at','kind','left','right','complete_text','groups'],spans)
tab('COMPANIONS.tsv',['decision_at','kind','at','word','S10_value'],comp)
forms=sorted({x[3] for x in comp});tab('ALL_COMPANION_OCCURRENCES.tsv',['word','count','all_loci','S10_value'],[(w,sum(x['word']==w for x in s),','.join(x['at'] for x in s if x['word']==w),lex.get(w,'OPEN')) for w in forms])
for m in ['FIRST','LAST']:
 tab(f'ALIGNMENT_{m}.tsv',['record','at','word','gloss'],[(x['record'],x['at'],x['word'],lex.get(x['word'],'OPEN')) for x in s])
 out=[f'# S11 {m} — vollständige Wortlesung und Rollenrichtung','','Alle sechs S10-Werte unverändert und hypothetisch; jede offene Quellgruppe erhalten. Rollen werden pro Entscheidung nur aus deren Präfix vergeben. Keine neue Syntax- oder Wortbedeutung.','']
 for locus in dict.fromkeys(x['locus'] for x in s):
  rr=[x for x in s if x['locus']==locus];out+=['## '+locus,'','`'+' '.join(x['word'] for x in rr)+'`','',' · '.join(lex.get(x['word'],'⟦OPEN: '+x['word']+'⟧') for x in rr),'']
  for z in dec:
   if z[2]==m and z[1].rsplit(':',1)[0]==locus:out += [f'Zusätzliche Rollen bei {z[1]}: behauptete Klasse {z[3]} ({z[4]}); beobachtete Klassen {z[5]}; erwartet {z[7]}, angenommene Entscheidung {z[8]}. {z[9]}.','']
 (D/f'READING_{m}.md').write_text('\n'.join(out).rstrip()+'\n')
js('RULE_REDUCTION.json',{'for_any_chosen_head':'if at least two distinct class words occur, at least one differs from chosen head; if all equal, no chosen head has a differing feature','equivalent_rule':['distinct_classes>=2 => REJECT','distinct_classes==1 and mentions>=2 and latest_quality==chol => ACCEPT','otherwise UNKNOWN'],'consequence':'No choice of claimed head among prefix class mentions changes output. More examples with this same rule alone cannot identify direction.','limits':'Only fixed S10 any-different rule and shared quality binding; role-sensitive rules or independently read relational markers are different tests.'})
js('RESULT.json',{'groups':len(s),'hypothesis_occurrences':sum(x['word'] in lex for x in s),'decisions':len(dec)//2,'identical_direction_results':sum(dec[i][7:]==dec[i+1][7:] for i in range(0,len(dec),2)),'different_claim_loci':sum(dec[i][3]!=dec[i+1][3] for i in range(0,len(dec),2)),'companions':len(comp),'confirmed_relational_markers':0,'confirmed_meanings':0,'held_access':False,'decision':'S10 decisions are invariant to claim-head choice; no role-direction evidence;stop this fixed selection test'})
files=['S05/INPUT.tsv','S10/MODEL.json','S10/REPORT.md','S11/DECISION.md']
js('SOURCE.json',{'files':[{'path':str((W/p).relative_to(R)),'sha256':hashlib.sha256((W/p).read_bytes()).hexdigest()} for p in files],'exposure':'all145groups already seen; no new manuscript access','sealed':['f84','f84r']})
print((D/'RESULT.json').read_text())
