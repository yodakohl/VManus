from pathlib import Path
import json,csv,hashlib
D=Path(__file__).parent
P=Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json')
F=Path('experiments/yolo/gdt929_fixed_four_form_context_square/artifacts/FRAMES.json')
loci={r['locus'] for x in json.loads(F.read_text()) for r in x['witnesses']}
paras=json.loads(P.read_text());selected=[];rows=[];md=['# Alle vollständigen Absätze hinter den sechs GDT929-Loci','']
for ed,pp in paras.items():
 for p in pp:
  hits=sorted(loci & {l['locus'] for l in p['lines']})
  if not hits:continue
  selected.append(dict(edition=ed,**p));tokens=[]
  md+=['## '+ed+' '+p['id'],'']
  for l in p['lines']:
   md+=[l['locus']+' `'+ ' '.join(l['words'])+'`','']
   for word,sid in zip(l['words'],l['source_ids']):
    if word in ['cheey','sheey']:tokens.append(dict(word=word,id=sid,locus=l['locus']))
  words=[t['word'] for t in tokens]
  rows.append(dict(edition=ed,paragraph=p['id'],target_loci=';'.join(hits),cheey=words.count('cheey'),sheey=words.count('sheey'),sequence=' '.join(words),both_forms=len(set(words))==2,reverse_transition=any(a=='sheey' and b=='cheey' for a,b in zip(words,words[1:])),positions=';'.join(t['id']+':'+t['word'] for t in tokens)))
(D/'PARAGRAPHS.json').write_text(json.dumps(selected,indent=2)+'\n')
(D/'COMPLETE_PARAGRAPHS.md').write_text('\n'.join(md)+'\n')
with (D/'TABLE.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
result=dict(paragraphs=len(rows),physical_paragraphs=len({r['paragraph'] for r in rows}),missing_complete_paragraph_reading='RF1b',both_forms=[r for r in rows if r['both_forms']],reverse_transition=[r['edition']+'|'+r['paragraph'] for r in rows if r['reverse_transition']],meaning_confirmed=False,post_exposure_audit=True)
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
