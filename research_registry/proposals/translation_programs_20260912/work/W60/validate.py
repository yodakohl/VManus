from pathlib import Path
import json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());expected=[]
allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors'])
for p in s['sources']:
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==s['hashes'][p]
 d=json.loads(Path(p).read_text())
 for l in d['lines']:
  assert l['metadata']['page'] in allow and not l['metadata']['page'].startswith('f84')
  gs=[dict(zip(d['group_columns'],g)) for g in l['groups']]
  for i,g in enumerate(gs):
   if g['ivtff_group_raw'] not in ('qolshey','charor'):continue
   n=gs[i+1] if i+1<len(gs) else None
   expected.append((g['source_group_id'],g['ivtff_group_raw'],n['ivtff_group_raw'] if n else None,bool(n and g['right_separator']==n['left_separator']=='DEFINITE_SPACE' and int(n['source_group_index'])==int(g['source_group_index'])+1)))
o=json.loads((D/'OCCURRENCES.json').read_text());assert expected==[(r['id'],r['word'],r['right'],r['right_definite']) for r in o]
ps=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());loci={r['locus'] for r in o}
p=[dict(edition=ed,**x) for ed,rows in ps.items() for x in rows if loci & {l['locus'] for l in x['lines']}]
assert p==json.loads((D/'PARAGRAPHS.json').read_text()) and len(p)==4
v=dict(status='PASS',scope='complete exact occurrence retrieval and paragraph export',meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
