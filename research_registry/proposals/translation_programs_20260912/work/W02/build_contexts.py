"""Complete reference alternatives and transcription display for the fixed packet."""
import csv,json,collections
from pathlib import Path
E=Path(__file__).resolve().parent
S=json.loads((E/'SOURCE.json').read_text());alt=json.loads((E/'ALTERNATE_LINES.json').read_text())
ms=list(csv.DictReader((E/'MATERIAL_MENTIONS.tsv').open(),delimiter='\t'));bs=[r for r in csv.DictReader((E/'ARGUMENTS.tsv').open(),delimiter='\t') if r['model']=='A'];idx=collections.defaultdict(list)
for r in ms:idx[(r['paragraph'],r['form'])].append(r)
rows=[]
for (p,w),ls in sorted(idx.items()):
 if len(ls)<2:continue
 ids={r['mention'] for r in ls};ops=[b for b in bs if b['patient'] in ids]
 rows.append({'paragraph':p,'form':w,'meaning':ls[0]['meaning'],'mentions':';'.join(r['mention'] for r in ls),'all_assumed_operations':';'.join(b['operation']+'='+b['meaning']+'@'+b['patient'] for b in ops),'SAME_objects':1,'NEW_objects':len(ls),'operation_debts':';'.join(b['operation']+':'+b['debts'] for b in ops if b['debts']),'identity_selected':False})
with (E/'MATERIAL_CHAINS.tsv').open('w') as f:
 out=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t',lineterminator='\n');out.writeheader();out.writerows(rows)
text=['# Alle alternativen Zielzeilen und Absatzgrenzen','','ZL3b ist nur die fest gewählte Arbeitsdarstellung, kein bevorzugter Wahrheitszeuge. IT2a und RF1b sind Lesarten desselben Manuskripts. Alle152Zeilen der ZL-Absatzumfänge bleiben in ALTERNATE_LINES.json mit ihren Rohgruppen und Herkunfts-IDs in allen drei Lesarten erhalten. RF1b hat hier keine markierten Absatzgrenzen.','','| Ziel | W01-Darstellung | ZL3b roh | IT2a roh | RF1b roh |','|---|---|---|---|---|']
for t in S['targets']:
 columns=[t['target'],t['W01_line']]
 for ed in ['ZL3b','IT2a','RF1b']:
  rs=[r for r in alt['readings'][ed] if r['metadata']['locus']==t['target']];assert len(rs)==1
  columns.append(' '.join(g['ivtff_group_raw'] for g in rs[0]['groups']))
 text.append('| '+' | '.join('`'+x+'`' for x in columns)+' |')
text+=['','## Absatzgrenzen','', '| Ziel | ZL-Absatz | IT-Absatz |','|---|---|---|']
for t in S['targets']:text.append('| '+t['target']+' | '+t['hosts']['ZL3b'][0]['id'].replace('|',':')+' | '+t['hosts']['IT2a'][0]['id'].replace('|',':')+' |')
text+=['','W01s geglättete Körperdarstellung unterscheidet sich an drei Zielzeilen vom jetzigen unbereinigten ZL-Rohtext: che\'eky auf f17v.15, yt[o:a]l auf f19v.9 und da[ir:in] auf f23r.5. W02 übernimmt diese Gruppen unverändert und lässt sie ungelesen. Kein Rückgriff auf die jeweils passendere Einzelvariante.']
(E/'READING_VARIANTS.md').write_text('\n'.join(text)+'\n')
print('All',len(rows),'repeated-material groups and all13target variants written')
