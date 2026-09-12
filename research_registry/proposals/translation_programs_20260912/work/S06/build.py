"""Rebuild exposed S06 synthesis; no raw manuscript or held inputs."""
from pathlib import Path
import csv,json,hashlib
D=Path(__file__).resolve().parent
R=next(p for p in D.parents if (p/'vmanus-work').exists())
W=D.parent
sources=['S05/INPUT.tsv','P05/LEXICON_v03.tsv','P05/REFERENCE_RULE_v02.json','P04/MODEL.json','P11/COMMON_LEXICON.tsv','P25/MODEL.json','P13/MODEL.json','S05/REPORT.md','P05/REPORT.md','S06/DECISION.md']
def read(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
def put(name,keys,rows):
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=keys+['row_status'],delimiter='\t',lineterminator='\n');w.writeheader()
  for r in rows:w.writerow(dict(zip(keys,r),row_status='recorded'))
def js(name,x):(D/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
rows=[r for r in read(W/'S05/INPUT.tsv') if r['locus'] in ['f32v.'+str(n) for n in range(7,12)]]
lex={r['form']:r['meaning_hypothesis'] for r in read(W/'P05/LEXICON_v03.tsv')}
nom={'cphos':'Zerreiben','she':'Stehenlassen','shckhy':'Vermischen','otchy':'Entnahme','qotchy':'Sieben','skey':'Zurückhalten','cpho':'Zerstoßen','chy':'Verarbeitung'}
p4=json.loads((W/'P04/MODEL.json').read_text())['whole_values']
p11={r['word']:r['value'] for r in read(W/'P11/COMMON_LEXICON.tsv')}
p25=json.loads((W/'P25/MODEL.json').read_text())['whole_word_hypotheses']
p13=json.loads((W/'P13/MODEL.json').read_text());s5=p13['materials']|p13['verbs'];s5['chor']=p13['targets']['chor']['neutral']
put('INPUT.tsv',['locus','at','word'],[(r['locus'],r['at'],r['word']) for r in rows])
forms=sorted({r['word'] for r in rows})
put('PRIOR_WORD_VALUES.tsv',['word','P05_V03','P04','P11','P25','S05'],[(f,*[d.get(f,'OPEN_NOT_ASSIGNED') for d in [lex,p4,p11,p25,s5]]) for f in forms])
put('FIXED_LEXICON.tsv',['word','M','K','status'],[(f,lex.get(f,'OPEN'),nom.get(f,lex.get(f,'OPEN')),'HYPOTHESIS' if f in lex else 'OPEN') for f in forms])
for variant in ['M','K']:
 put('ALIGNMENT_'+variant+'.tsv',['locus','at','word','gloss','status'],[(r['locus'],r['at'],r['word'],(nom.get(r['word'],lex.get(r['word'],'OPEN')) if variant=='K' else lex.get(r['word'],'OPEN')),'HYPOTHESIS' if r['word'] in lex else 'OPEN') for r in rows])
materials=set(json.loads((W/'P05/REFERENCE_RULE_v02.json').read_text())['material_forms'])
quant=[];i=0;seen=[]
while i<len(rows):
 r=rows[i];word=r['word']
 if word in materials:seen.append(r)
 if word=='daiin':
  if i+1<len(rows) and rows[i+1]['word']=='daiin':
   last=[]
   for m in reversed(seen):
    if m['word'] not in [x['word'] for x in last]:last.append(m)
    if len(last)==2:break
   for q,m in zip(rows[i:i+2],reversed(last)):quant.append((q['at'],q['word'],'Q',m['at'],m['word'],'P05_DOUBLE_RULE'))
   i+=2;continue
  m=seen[-1];quant.append((r['at'],word,'Q',m['at'],m['word'],'P05_NEAREST_MATERIAL'))
 if word=='dain':quant.append((r['at'],word,'D','OPEN','OPEN','NO_SECURE_PATIENT'))
 i+=1
put('QUANTITIES.tsv',['at','word','symbol','target_at','target_word','rule'],quant)
frames=[
('F1','f32v.7:2','cphos','unknown initial material','ground initial material','missing written input','initial patient invented; result identity model only'),
('F2','f32v.7:3','she','F1 product','standing F1 product','sheaiin stand time; otshcho cool interior','same patient and circumstance syntax assumed'),
('F3','f32v.7:8','shckhy','F2 product + odan .7:10','mixture','s je; dain small dose unbound','continuation and two-input syntax assumed; dosage target unresolved'),
('F4','f32v.8:7','otchy','qotaiin .8:6 independent portion','shan .8:9 fine fraction','d OPEN','source-extract-result syntax assumed; qotaiin origin OPEN'),
('F5','f32v.9:1','qotchy','F4 fine fraction','sieved fine fraction','cfhy filter','patient continuation and instrument role assumed'),
('F6','f32v.9:3','skey','F5 product','chocthy .9:4 Q + cthaiin .9:6 Q','two simultaneous disjoint portions assumed','could instead be inputs or alternatives; no independent output binding'),
('F7','f32v.10:6','cpho','cthol .10:8','crushed cthol','l OPEN; da OPEN; ar share without number','right patient over OPEN group assumed; .10 fluids/oil/flowers not linked'),
('F8','f32v.11:3','chy','F7 product + sho .11:2 fluid adjunct','processed material','ol with','same cthol individual continues; ol-sho adjunct excludes it from main patient selection')]
put('FRAMES_M.tsv',['id','at','word','input','output','written_context','added_or_missing'],frames)
assumptions=[
('A1','P05 word values and four OPEN groups','M,K','35 glossed occurrences do not identify meanings','independent semantics unavailable'),
('A2','double daiin distributes over odan and otchol','M,K','one Q for each; not both on otchol','grammar still hypothetical; prior P14 different binding'),
('A3','F4-F6 form one local extraction-sieving-retention chain','M','qotaiin must supply two retained portions','requires action/output and identity grammar'),
('A4','last cthol continues through chy, sho is fluid adjunct','M','F7-F8 local continuation','conflicts with earlier sho=verb/chy=water; those excluded here'),
('A5','Q measures common positive handled mass','M+ and conditional M mass account','each output weighs Q','dose need not imply same mass across substances'),
('A6','retained outputs simultaneous and disjoint; no additions','M+ and conditional M mass account','source >= 2Q','word list does not establish disjointness or simultaneous retention'),
('A7','qotaiin is aliquot of previous ctho Q','M+ only','source <= Q, hence contradiction with A5+A6','not present in primary M; cannot silently add'),
('A8','nominal fields rather than executed operations','K','no material-flow assertion to contradict','not a successful alternative translation proof')]
put('ASSUMPTIONS.tsv',['id','assumption','scope','consequence','limitation'],assumptions)
js('MASS_AUDIT.json',{'status':'CONDITIONAL_CONJUNCTION_CONTRADICTION','premises':['Q>0','P<=Q [M+ only]','F<=P','O1=Q','O2=Q','O1+O2<=F'],'deduction':['2Q<=F<=P<=Q','Q<=0 contradicts Q>0'],'M_without_origin_bridge_witness':{'Q':1,'P':2,'F':2,'O1':1,'O2':1},'witness_scale':'arbitrary algebraic normalization, not a decoded numeral','K':'NO_MASS_CLAIM','meaning_evidence':False})
proseM=[
'⟦ksho offen⟧. Zerreibe ⟨unbenanntes Ausgangsmaterial⟩; lasse ⟨es⟩ stehen: Standzeit, kühles Inneres. Danach: kleine Dosis ⟨Ziel offen⟩; vermische ⟨den bisherigen Ansatz⟩ je ⟨mit dem⟩ Rest.',
'Getrocknetes Gut; festgelegte Dosis ⟨für den vorher genannten Rest⟩, festgelegte Dosis ⟨für das getrocknete Gut⟩. Pflanzenpulver: festgelegte Dosis. Abgeteilte Portion ⟨Herkunft offen⟩: entnimm ⟦d offen⟧ Feinanteil.',
'Siebe ⟨den Feinanteil durch den⟩ Filter. Halte zurück: Pflanzenmark, festgelegte Dosis; Pflanzenportion, festgelegte Dosis ⟨beide als getrennte Ausgaben derselben Bearbeitung angenommen⟩.',
'Flüssigkeit; Öl; Blüten, trocken, festgelegte Dosis. Zerstoße ⟦l offen⟧ trockenes Pflanzengut ⟦da offen⟧ Anteil ⟨Menge offen⟩. ⟨Eine Verbindung der ersten drei Stoffnennungen mit dem Zerstoßen ist nicht gebunden.⟩',
'Mit Flüssigkeit verarbeite ⟨das zuletzt zerstoßene trockene Pflanzengut⟩.'
]
proseK=[
'⟦ksho offen⟧; Zerreiben; Stehenlassen; Standzeit; kühles Inneres; danach; kleine Dosis ⟨Bezugsfeld offen⟩; Vermischen; je; Rest.',
'Getrocknetes Gut; festgelegte Dosis ⟨Rest⟩; festgelegte Dosis ⟨getrocknetes Gut⟩; Pflanzenpulver; festgelegte Dosis ⟨Pflanzenpulver⟩; abgeteilte Portion; Entnahme; ⟦d offen⟧; Feinanteil.',
'Sieben; Filter; Zurückhalten; Pflanzenmark; festgelegte Dosis ⟨Pflanzenmark⟩; Pflanzenportion; festgelegte Dosis ⟨Pflanzenportion⟩.',
'Flüssigkeit; Öl; Blüten; trocken; festgelegte Dosis ⟨Blüten⟩; Zerstoßen; ⟦l offen⟧; trockenes Pflanzengut; ⟦da offen⟧; Anteil.',
'Mit Flüssigkeit: Verarbeitung.'
]
for v,prose in [('M',proseM),('K',proseK)]:
 lines=['# S06 '+v+' — vollständige hypothetische Lesung','','Keine bestätigte Übersetzung. ⟦…⟧ = offene Quellgruppe; ⟨…⟩ = zusätzliche Bindung/Erklärung ohne eigenes Quellwort. Die wortweise Tabelle bleibt maßgeblich. K nominalisiert nur die acht Tätigkeitswerte; es behauptet keine Ausführung oder Produktidentität.','']
 for n,p in zip(range(7,12),prose):
  source=' '.join(r['word'] for r in rows if r['locus']==f'f32v.{n}')
  lines += [f'## f32v.{n}','',f'`{source}`','',p,'']
 (D/f'READING_{v}.md').write_text('\n'.join(lines).rstrip()+'\n')
js('SOURCE.json',{'files':[{'path':str((W/s).relative_to(R)),'sha256':hashlib.sha256((W/s).read_bytes()).hexdigest()} for s in sources],'scope':'only exposed f32v.7–11; not entire physical folio','sealed':['f84','f84r'],'prior_exposure':'all target content and compared programs already exposed; no blinded prediction','new_manuscript_access':False})
js('RESULT.json',{'groups':len(rows),'hypothesis_occurrences':sum(r['word'] in lex for r in rows),'open_occurrences':[r['at'] for r in rows if r['word'] not in lex],'quantity_occurrences':len(quant),'Q_occurrences':sum(q[2]=='Q' for q in quant),'action_frames':len(frames),'M':'two local action chains plus unresolved initial/material contexts; no complete genealogy','K':'full nominal rival; no independent meaning or syntactic selection','M_plus':'conditional origin bridge incompatible with common positive mass and disjoint outputs','independent_semantic_confirmation':0,'held_access':False,'significance_claim':False})
print(json.dumps(json.loads((D/'RESULT.json').read_text()),ensure_ascii=False))
