from pathlib import Path
import json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);expected=[];lines=[]
for p in s['sources']:
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==s['hashes'][p]
 d=json.loads(Path(p).read_text())
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84')
  gs=[dict(zip(d['group_columns'],g)) for g in l['groups']];ws=[g['ivtff_group_raw'] for g in gs];lines.append(dict(edition=m['edition'],locus=m['locus'],words=ws))
  for i,w in enumerate(ws):
   if w=='solchey':expected.append(dict(edition=m['edition'],locus=m['locus'],at=gs[i]['source_group_id'],index=i+1,line_initial=i==0,right=ws[i+1] if i+1<len(ws) else None,words=ws))
assert expected==json.loads((D/'OCCURRENCES.json').read_text()) and len(expected)==7
loci={r['locus'] for r in expected};assert [r for r in lines if r['locus'] in loci]==json.loads((D/'ALL_READINGS.json').read_text())
src=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());ps=[dict(edition=ed,**p) for ed,pp in src.items() for p in pp if loci & {l['locus'] for l in p['lines']}];assert ps==json.loads((D/'PARAGRAPHS.json').read_text()) and len(ps)==4
v=dict(status='PASS',scope='all seven exact occurrences, alternate complete lines and four paragraphs',meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
