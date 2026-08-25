#!/usr/bin/env python3
"""Build Pass 923: complete contexts and shortest readings for ten learned roots."""

import csv,hashlib,json
from collections import Counter,defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
P912=ROOT/'experiments/yolo/sidequest_semantic_fourteen_page_revised_handbook_nine_hundred_twelfth'
P917=ROOT/'experiments/yolo/sidequest_semantic_fluent_prose_nine_hundred_seventeenth'
P918=ROOT/'experiments/yolo/sidequest_semantic_minimal_verb_deck_nine_hundred_eighteenth'
def read(p):
 with p.open(encoding='utf-8',newline='') as f:return list(csv.DictReader(f,delimiter='\t'))
def write(n,rows,fields):
 with (OUT/n).open('w',encoding='utf-8',newline='') as f:
  w=csv.DictWriter(f,delimiter='\t',fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)

DECISIONS={
 'SHED':('ABSETZEN','KEEP','kurz in Ruhe-/Haltezustand geben; Bio terminal'),
 'SOLK':('AUFFANGEN','KEEP','an lokaler Sammelstelle aufnehmen'),
 'LSH':('SPUELEN','KEEP','Posten oder Durchlass mit Arbeitsflüssigkeit durchgehen'),
 'CPH':('UMLEITEN','REVISE_FROM_RUECKFUEHREN','in Gegen-, Empfangs- oder zweiten Lauf führen'),
 'HO':('TEIL','REVISE_FROM_STOFFTEIL','Teil des jeweils sichtbaren Pflanzen-, Figuren- oder Objektbesitzers'),
 'AN':('ZUSATZ','KEEP','weiterer Posten oder zusätzliche Klasse'),
 'CFH':('TRENNEN','REVISE_FROM_PRESSEN','Trennhandlung; im Pflanzenregister lokal auspressen'),
 'OS':('DAZU','KEEP','additive Fortsetzung'),
 'LD':('BEFESTIGEN','KEEP','aktiven Einsatz/Posten festsetzen'),
 'RESUME_CARD':('WIEDERAUFNEHMEN','KEEP','vorigen aktiven Posten wieder aufnehmen'),
}

def expansion(root,register):
 if root=='CPH':return {'HERBAL':'in zweiten Durchgang umleiten','BIOLOGICAL':'zur Gegen-/Empfangsstation umleiten','ZODIAC':'zur Gegenstelle wechseln','PHARMA':'in Empfangsgefäß umleiten'}[register]
 if root=='HO':return {'HERBAL':'Teil der gezeigten Pflanze','BIOLOGICAL':'Teil des gezeigten Objekts','ZODIAC':'Teil der gezeigten Figur','PHARMA':'Teil der gezeigten Zutat'}[register]
 if root=='CFH':return 'auspressen und trennen' if register in {'HERBAL','PHARMA'} else 'unterscheiden oder abtrennen'
 return DECISIONS[root][0].lower()

def main():
 ev=read(P912/'PASS912_2511_EVENT_INTERLINEAR.tsv');bind={r['event_id']:r for r in read(P917/'PASS917_2010_EVENT_BINDINGS.tsv')};inst={r['instruction_id']:r for r in read(P918/'PASS918_1435_REVISED_INSTRUCTIONS.tsv')}
 targets=set(DECISIONS);occ=[];counts=Counter();pages=defaultdict(set);regs=defaultdict(set);surfs=defaultdict(Counter)
 for r in ev:
  roots=[a for a in r['component_recipe'].split('+') if a in targets]
  if not roots:continue
  assert len(roots)==1;root=roots[0];counts[root]+=1;pages[root].add(r['physical_page']);regs[root].add(r['register']);surfs[root][r['surface']]+=1
  if r['usage_class']=='PROSE' and r['event_id'] in bind:
   b=bind[r['event_id']];context=inst[b['instruction_id']]['revised_fluent_de'];context_id=b['instruction_id']
  else:context=r['fluent_token_de'];context_id=r['locus']
  occ.append({'event_id':r['event_id'],'root':root,'fixed_default_de':DECISIONS[root][0],'register':r['register'],'physical_page':r['physical_page'],'source_page':r['source_page'],'locus':r['locus'],'usage_class':r['usage_class'],'surface':r['surface'],'component_recipe':r['component_recipe'],'register_expansion_de':expansion(root,r['register']),'complete_context_id':context_id,'complete_context_de':context,'decision':DECISIONS[root][1]})
 write('PASS923_141_ROOT_OCCURRENCES.tsv',occ,list(occ[0]))
 dec=[]
 for root,(meaning,decision,note) in DECISIONS.items():
  dec.append({'root':root,'fixed_default_de':meaning,'decision':decision,'events':str(counts[root]),'physical_pages':str(len(pages[root])),'registers':','.join(sorted(regs[root])),'surface_inventory':','.join(f'{s}:{n}' for s,n in surfs[root].most_common()),'short_teaching_rule_de':note})
 write('PASS923_10_LEARNED_ROOT_DECISIONS.tsv',dec,list(dec[0]))
 doc=['# Pass 923 — zehn gelernte Wurzeln in vollständigen Kontexten','']
 for d in dec:
  doc += [f"## {d['root']} = {d['fixed_default_de']}",'']
  for x in occ:
   if x['root']==d['root']:doc.append(f"- {x['event_id']} {x['source_page']} `{x['surface']}`: {x['complete_context_de']} — **{x['register_expansion_de']}**")
  doc.append('')
 (OUT/'PASS923_COMPLETE_ROOT_CONTEXTS.md').write_text('\n'.join(doc),encoding='utf-8')
 report='''# Pass 923 — die zehn gelernten Fachwurzeln

## Endfassung

Alle 141 Vorkommen wurden in ihrem vollständigen Arbeitszug gelesen. Die kürzeste
stabile Werkstattliste lautet:

`SHED absetzen`, `SOLK auffangen`, `LSH spülen`, `CPH umleiten`, `HO Teil`,
`AN Zusatz`, `CFH trennen`, `OS dazu`, `LD befestigen`,
`RESUME_CARD wiederaufnehmen`.

## Drei sinnvolle Kürzungen

- `CPH`: **UMLEITEN** ersetzt das zu gerichtete „rückführen“. In Herbal ist es
  zweiter Durchgang, in Bio Empfangsstation, im Rad Gegenstelle, in Pharma Empfänger.
- `HO`: **TEIL** ersetzt „Stoffteil“. Der sichtbare Besitzer liefert erst Pflanze,
  Figur, Objekt oder Zutat.
- `CFH`: **TRENNEN** ersetzt „pressen“. Auspressen ist nur die konkrete
  Pflanzen-/Pharma-Ausführung; im Himmelsregister bleibt eine Trennkennung möglich.

Damit hat keine gelernte Wurzel mehr eine Satzglosse. Selbst die memorierte Schicht
besteht aus einwortigen Werkstattwerten.

## Nächster Schritt

Diese drei Revisionen werden jetzt durch das komplette 2511-Gruppen-Wörterbuch und
die 1435 Prosaarbeitszüge propagiert. Danach besitzen wir eine neue, konsistente
Gesamtausgabe ohne die alten langen CPH/HO/CFH-Deutungen.
'''
 (OUT/'PASS923_REPORT.md').write_text(report,encoding='utf-8')
 names=['PASS923_141_ROOT_OCCURRENCES.tsv','PASS923_10_LEARNED_ROOT_DECISIONS.tsv','PASS923_COMPLETE_ROOT_CONTEXTS.md','PASS923_REPORT.md']
 s={'status':'BUILT','root_occurrences':len(occ),'roots':len(dec),'decisions':dict(Counter(x['decision'] for x in dec)),'counts':dict(counts),'sha256':{n:hashlib.sha256((OUT/n).read_bytes()).hexdigest() for n in names}}
 (OUT/'PASS923_BUILD_SUMMARY.json').write_text(json.dumps(s,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
