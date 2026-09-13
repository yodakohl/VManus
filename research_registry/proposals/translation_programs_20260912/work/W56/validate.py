from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
src=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text())
f=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/artifacts/FRAMES.json').read_text());loci={r['locus'] for x in f for r in x['witnesses']}
want=[dict(edition=ed,**p) for ed,pp in src.items() for p in pp if loci & {l['locus'] for l in p['lines']}]
assert want==json.loads((D/'PARAGRAPHS.json').read_text()) and len(want)==12
rows=list(csv.DictReader((D/'TABLE.tsv').open(),delimiter='\t'));assert len(rows)==12
for p,r in zip(want,rows):
 words=[w for l in p['lines'] for w in l['words'] if w in ('cheey','sheey')]
 assert r['edition']==p['edition'] and r['paragraph']==p['id']
 assert r['sequence']==' '.join(words)
 assert int(r['cheey'])==words.count('cheey') and int(r['sheey'])==words.count('sheey')
 assert (r['both_forms']=='True')==(len(set(words))==2)
 assert (r['reverse_transition']=='True')==('sheey cheey' in ' '.join(words))
v=dict(status='PASS',scope='complete selected paragraph export and exact occurrence sequence',meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
