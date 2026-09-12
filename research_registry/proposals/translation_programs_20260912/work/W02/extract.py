"""Reproduce the fixed previously exposed packet; no raw mixed TSV access."""
import json,hashlib
from pathlib import Path
E=Path(__file__).resolve().parent;R=E.parents[4]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def relative(p):return str(p.relative_to(R))
base=R/'experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json'
d=json.loads(base.read_text());w01=E.parent/'W01/SOURCE.json';targets=json.loads(w01.read_text())['lines'];rows=[]
for t in targets:
 l=t['locus'];assert not l.startswith('f84')
 hosts={ed:[p for p in ps if any(x['locus']==l for x in p['lines'])] for ed,ps in d.items()}
 assert all(len(ps)<=1 for ps in hosts.values()) and len(hosts['ZL3b'])==1
 rows.append({'target':l,'W01_line':t['raw'],'hosts':hosts})
out={'scope':'13 frozen W01 target loci, complete host paragraphs independently by reading; all sources exposed','inputs':[{'path':relative(base),'sha256':sha(base)},{'path':relative(w01),'sha256':sha(w01)}],'targets':rows}
(E/'SOURCE.json').write_text(json.dumps(out,ensure_ascii=False,separators=(',',':'))+'\n')
text=[]
for r in rows:
 text+=['## '+r['target']]
 for ed in ['ZL3b','IT2a']:text.append(ed+': '+', '.join(p['id'] for p in r['hosts'][ed]))
 for p in r['hosts']['ZL3b']:text.extend(l['locus']+' '+ ' '.join(l['words']) for l in p['lines'])
(E/'RAW_PARAGRAPHS.md').write_text('\n\n'.join(text)+'\n')
loci={l['locus'] for t in rows for p in t['hosts']['ZL3b'] for l in p['lines']};pages={l.split('.')[0] for l in loci};alts={ed:[] for ed in ['ZL3b','IT2a','RF1b']};inputs=[]
for ed in alts:
 for phase in ['DISCOVERY','EVALUATION']:
  p=R/'experiments/yolo/gdt915_terminal_lr_phrase_transfer/artifacts'/f'SOURCE_{phase}_{ed}.json';d=json.loads(p.read_text());inputs.append({'path':relative(p),'sha256':sha(p)})
  for r in d['lines']:
   m=r['metadata']
   if m['page'] not in pages or m['locus'] not in loci:continue
   assert not m['page'].startswith('f84')
   alts[ed].append({'metadata':m,'groups':[dict(zip(d['group_columns'],g)) for g in r['groups']]})
(E/'ALTERNATE_LINES.json').write_text(json.dumps({'scope':'Exactly the primary ZL paragraph loci; no extra target rows','inputs':inputs,'readings':alts},ensure_ascii=False,separators=(',',':'))+'\n')
print('Fixed exposed packet:',len(rows),'paragraphs;',len(loci),'loci')
