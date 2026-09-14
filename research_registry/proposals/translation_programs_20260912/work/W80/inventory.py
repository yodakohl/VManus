from pathlib import Path
import json,hashlib,collections
D=Path(__file__).parent
s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);out=[]
for path in s['sources']:
 assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==s['hashes'][path]
 d=json.loads(Path(path).read_text())
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84');gs=[dict(zip(d['group_columns'],g)) for g in l['groups']];ws=[g['ivtff_group_raw'] for g in gs]
  for i,w in enumerate(ws):
   if w=='qoteey':out.append(dict(edition=m['edition'],page=m['page'],locus=m['locus'],at=gs[i]['source_group_id'],left=ws[i-1] if i else '',right=ws[i+1] if i+1<len(ws) else '',words=ws))
loci={r['locus'] for r in out};src=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());ps=[dict(edition=ed,**p) for ed,pp in src.items() for p in pp if loci & {l['locus'] for l in p['lines']}]
(D/'OCCURRENCES.json').write_text(json.dumps(out,indent=2)+'\n');(D/'PARAGRAPHS.json').write_text(json.dumps(ps,indent=2)+'\n');print(json.dumps(dict(occurrences=len(out),readings=dict(collections.Counter(r['edition'] for r in out)),loci=len(loci),paragraphs=len(ps),groups=sum(len(l['words']) for p in ps for l in p['lines']))));print(json.dumps([r for r in out if r['edition']=='ZL3b']))
