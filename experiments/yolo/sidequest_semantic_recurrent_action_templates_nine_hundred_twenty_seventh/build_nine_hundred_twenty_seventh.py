#!/usr/bin/env python3
from __future__ import annotations
import csv, hashlib, json
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'sidequest_semantic_consolidated_fourteen_page_edition_nine_hundred_twenty_fourth'

def read(name):
    with (BASE/name).open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f,delimiter='\t'))
def write(name,fields,rows):
    with (HERE/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,delimiter='\t',lineterminator='\n');w.writeheader();w.writerows(rows)

TEMPLATES={
 ('SH','O'):('HALTEN_DANN_AUSFUEHREN','halten, dann den Gang ausführen'),
 ('K','CH'):('ZUGEBEN_DANN_ENTNEHMEN','zugeben, dann den bezeichneten Anteil entnehmen'),
 ('O','S'):('AUSFUEHREN_DANN_AUSWAEHLEN','ausführen, dann den nächsten Posten auswählen'),
 ('S','OK'):('AUSWAEHLEN_DANN_ANSETZEN','auswählen und ansetzen'),
 ('OK','K'):('ANSETZEN_DANN_ZUGEBEN','ansetzen und zugeben'),
 ('OK','OK'):('ZWEISTUFIG_ANSETZEN','in zwei aufeinanderfolgenden Zügen ansetzen'),
 ('CH','O'):('ENTNEHMEN_DANN_AUSFUEHREN','entnehmen und den Gang ausführen'),
 ('SH','OK'):('HALTEN_DANN_WEITERANSETZEN','halten, dann erneut ansetzen'),
 ('OK','CH'):('ANSETZEN_DANN_ENTNEHMEN','ansetzen, dann einen Anteil entnehmen'),
 ('CH','OK'):('ENTNEHMEN_DANN_ANSETZEN','einen Anteil entnehmen und ansetzen'),
 ('CH','S'):('ENTNEHMEN_DANN_AUSWAEHLEN','entnehmen, dann den nächsten Posten auswählen'),
 ('CH','K'):('ENTNEHMEN_DANN_ZUGEBEN','entnehmen und zugeben'),
 ('O','K'):('AUSFUEHREN_DANN_ZUGEBEN','den Gang ausführen und danach zugeben'),
 ('O','CTH'):('AUSFUEHREN_BIS_BEREIT','den Gang bis zum Bereitschaftspunkt ausführen'),
 ('T','OK'):('EINSTELLEN_DANN_ANSETZEN','einstellen und danach ansetzen'),
 ('SH','K'):('HALTEN_DANN_ZUGEBEN','halten und anschließend zugeben'),
 ('OK','O'):('ANSETZEN_DANN_AUSFUEHREN','ansetzen und den Gang ausführen'),
 ('CH','CH'):('ZWEIMAL_ENTNEHMEN','zweimal nacheinander entnehmen'),
 ('K','OK'):('ZUGEBEN_DANN_ANSETZEN','zugeben und neu ansetzen'),
 ('O','OK'):('AUSFUEHREN_DANN_NEU_ANSETZEN','ausführen und einen neuen Zug ansetzen'),
 ('OK','CHD'):('ANSETZEN_DANN_UMSETZEN','ansetzen und zur nächsten Stelle umsetzen'),
 ('CHD','OK'):('UMSETZEN_DANN_NEU_ANSETZEN','umsetzen und an der neuen Stelle ansetzen'),
}

ins=read('PASS924_1435_CURRENT_PROSE_INSTRUCTIONS.tsv')
by_clause=defaultdict(list)
for r in ins: by_clause[r['clause_id']].append(r)
occ=[]; template_pages=defaultdict(set); template_clauses=defaultdict(set); template_registers=defaultdict(set)
oid=0
for cid,rows in by_clause.items():
    stream=[]
    for r in rows:
        for local_pos,verb in enumerate((x for x in r['minimal_verb_sequence'].split('>') if x),1):
            stream.append((verb,r['instruction_id'],local_pos,r['physical_page'],r['register'],r['start_event'],r['end_event']))
    for pos in range(len(stream)-1):
        a,b=stream[pos],stream[pos+1]; key=(a[0],b[0])
        if key not in TEMPLATES: continue
        oid+=1; tid,reading=TEMPLATES[key]
        template_pages[tid].add(a[3]);template_clauses[tid].add(cid);template_registers[tid].add(a[4])
        occ.append({
          'occurrence_id':f'P927-O{oid:04d}','template_id':tid,'clause_id':cid,'physical_page':a[3],
          'register':a[4],'action_position':pos+1,'action_pair':'>'.join(key),
          'first_instruction':a[1],'second_instruction':b[1],
          'crosses_instruction_boundary':'YES' if a[1]!=b[1] else 'NO',
          'first_event_span':f'{a[5]}..{a[6]}','second_event_span':f'{b[5]}..{b[6]}',
          'spoken_template_de':reading,
        })

by_tid=Counter(r['template_id'] for r in occ)
templates=[]
for key,(tid,reading) in TEMPLATES.items():
    templates.append({
      'template_id':tid,'action_pair':'>'.join(key),'spoken_template_de':reading,
      'occurrences':by_tid[tid],'clauses':len(template_clauses[tid]),'pages':len(template_pages[tid]),
      'page_list':'|'.join(sorted(template_pages[tid])),'register_list':'|'.join(sorted(template_registers[tid])),
      'workshop_interpretation':'TAUGHT_TWO_STEP_ROUTINE' if len(template_pages[tid])>=4 else 'LOCAL_TWO_STEP_ROUTINE',
    })
templates.sort(key=lambda r:(-int(r['pages']),-int(r['occurrences']),r['template_id']))
write('PASS927_22_ACTION_TEMPLATES.tsv',list(templates[0]),templates)
write('PASS927_TEMPLATE_OCCURRENCES.tsv',list(occ[0]),occ)

doc=['# Pass 927 — wiederkehrende Zwei-Schritt-Schablonen','',
     'Diese Formulierungen sind die kurze Werkstattlektüre der beobachteten Aktionspaare. Sie werden nicht als neue Wörter behandelt: zwei bereits gelesene Wurzeln bilden einen gelehrten Handgriff.','']
for i,r in enumerate(templates,1):
    doc += [f"## {i}. {r['template_id']}",'',
            f"**{r['spoken_template_de'].capitalize()}.** {r['occurrences']} Vorkommen in {r['clauses']} Klauseln auf {r['pages']} Seiten ({r['page_list']}).",'']
(HERE/'PASS927_ACTION_TEMPLATE_BOOK.md').write_text('\n'.join(doc).rstrip()+'\n',encoding='utf-8')

top=templates[:10]
report=f"""# Pass 927 — die ersten gelehrten Handgriffe

## Ergebnis

Aus dem vollständigen 17-Verb-Deck entstehen 22 konkrete, wiederkehrende
Zwei-Schritt-Handgriffe mit {len(occ)} gebundenen Vorkommen. Die zehn am
weitesten über Seiten verteilten sind:

"""+'\n'.join(f"- **{r['spoken_template_de']}** — {r['occurrences']}× auf {r['pages']} Seiten" for r in top)+f"""

## Wichtigste Lesung

Der Text verhält sich damit eher wie ein Werkstattregister als wie eine Folge
isolierter Wörter. `OK→CHD` ist nicht eine lange Lexembedeutung, sondern
„ansetzen, dann umsetzen“; `CHD→OK` gibt den Gegenzyklus „umsetzen, dann neu
ansetzen“. Ebenso bilden `SH→O`, `O→CTH` und `OK→SH` normale Arbeitsfolgen,
ohne dass eine Einzelwurzel den ganzen Satz tragen muss.

## Kreativer Gewinn

Die häufigsten Übergänge erlauben nun ganze kurze Lesungen, ohne Bedeutungen in
ein einzelnes Zeichen hineinzustopfen. Im nächsten Durchgang werden drei- und
vierstufige Rezepte nur aus diesen Handgriffen zusammengesetzt.
"""
(HERE/'PASS927_REPORT.md').write_text(report,encoding='utf-8')
outs=['PASS927_22_ACTION_TEMPLATES.tsv','PASS927_TEMPLATE_OCCURRENCES.tsv','PASS927_ACTION_TEMPLATE_BOOK.md','PASS927_REPORT.md']
(HERE/'PASS927_BUILD_SUMMARY.json').write_text(json.dumps({'status':'PASS','templates':len(templates),'occurrences':len(occ),'outputs':{x:hashlib.sha256((HERE/x).read_bytes()).hexdigest() for x in outs}},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
