#!/usr/bin/env python3
"""Compact review tables from all independently validated fixed cases."""
import csv
from collections import Counter
from pathlib import Path
E=Path(__file__).resolve().parents[1]
def build():
 with (E/'artifacts/CASES.tsv').open() as f:rows=list(csv.DictReader(f,delimiter='\t'))
 doc=['# GDT947 — vollständige Kandidatenbilanz','','B = zuvor ausdrücklich genannt; F = nachfolgend ausdrücklich genannt. Die Bedeutung des Kerns bleibt offen. Zahlen zählen alternative Transkriptionsvorkommen, keine unabhängigen Manuskriptbelege. Bestätigte Wörter:0. Unabhängige Bedeutungsprüfung:0.','','| Form | Quelle | Richtung | Vorkommen | Kern auf Pflichtseite | Klar fehlend | Quelle unklar | Zielgrenze unklar | Keine Absatzkapazität | Entscheidung |','|---|---|---|---:|---:|---:|---:|---:|---:|---|']
 for form in ['olshedy','olshey','olkain','olkeedy','olchey']:
  for ed in ['ZL3b','IT2a','RF1b']:
   for direction in ['BACK','FORWARD']:
    rr=[r for r in rows if (r['form'],r['edition'],r['direction'])==(form,ed,direction)];c=Counter(r['status'] for r in rr)
    verdict='Vertrag widersprochen' if c['MISSING_WRITTEN_ANCHOR'] else 'Keine Absatzkapazität' if c['NO_PARAGRAPH_CAPACITY']==len(rr) else 'Offen' if c['UNRESOLVED_SOURCE']+c['TARGET_BOUNDARY_UNCERTAIN']+c['NO_PARAGRAPH_CAPACITY'] else 'Schriftpflicht erfüllt; Bedeutung offen'
    vals=[form,ed,direction,len(rr),c['WRITTEN_ANCHOR_PRESENT'],c['MISSING_WRITTEN_ANCHOR'],c['UNRESOLVED_SOURCE'],c['TARGET_BOUNDARY_UNCERTAIN'],c['NO_PARAGRAPH_CAPACITY'],verdict]
    doc.append('| '+' | '.join(map(str,vals))+' |')
 doc+=['','Die drei Formen olkain, olkeedy und olchey sind vorab gewählte Familiendiagnostik. Ihre Bedeutungen sind unbekannt; sie liefern keine semantische Negativkontrolle.','','## Alle klaren Gegenfälle der zwei primären Formen','','Jeder Fall verletzt nur die ausdrücklich registrierte exakte Schriftpflicht. Die Liste ist vollständig; Unsicherheiten und alle passenden Fälle stehen separat in CASES.tsv. Keine Auswahl erfolgreicher Einzelstellen.','','| Form | Richtung | Quelle | Stelle | Gruppe | Physisches Blatt | Exposition |','|---|---|---|---|---|---:|---|']
 bad=[r for r in rows if r['family']=='PRIMARY' and r['status']=='MISSING_WRITTEN_ANCHOR']
 for r in bad:doc.append('| '+' | '.join([r['form'],r['direction'],r['edition'],r['locus'],r['source_group_id'].rsplit('|',1)[1],r['physical_leaf'],r['exposure']])+' |')
 doc+=['','## Ganze physische Blätter','','Für jede Form/Richtung wird jedes beobachtete Blatt gezeigt. ZL/IT/RF bleiben in der ersten Tabelle getrennt; diese Blattbilanz addiert nur Quellvorkommen.77/80/85 sind Auswahlblätter, alle anderen bereits exponiertes internes Transfermaterial.','','| Form | Richtung | Blatt | Exposition | Vorkommen | Passender Kern | Klar fehlend | Quelle unklar | Zielgrenze unklar | Keine Absatzkapazität |','|---|---|---:|---|---:|---:|---:|---:|---:|---:|']
 keys=sorted({(r['form'],r['direction'],int(r['physical_leaf'])) for r in rows if r['family']=='PRIMARY'})
 for form,direction,leaf in keys:
  rr=[r for r in rows if r['form']==form and r['direction']==direction and int(r['physical_leaf'])==leaf];c=Counter(r['status'] for r in rr)
  vals=[form,direction,leaf,rr[0]['exposure'],len(rr)]+[c[k] for k in ['WRITTEN_ANCHOR_PRESENT','MISSING_WRITTEN_ANCHOR','UNRESOLVED_SOURCE','TARGET_BOUNDARY_UNCERTAIN','NO_PARAGRAPH_CAPACITY']]
  doc.append('| '+' | '.join(map(str,vals))+' |')
 return '\n'.join(doc)+'\n'
if __name__=='__main__':(E/'artifacts/CANDIDATES.md').write_text(build())
