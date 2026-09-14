from pathlib import Path
import json,hashlib
D=Path(__file__).parent;s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);occ=[];alllines=[]
for p in s['sources']:
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==s['hashes'][p]
 d=json.loads(Path(p).read_text())
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84')
  gs=[dict(zip(d['group_columns'],g)) for g in l['groups']];ws=[g['ivtff_group_raw'] for g in gs]
  alllines.append(dict(edition=m['edition'],locus=m['locus'],words=ws))
  for i,w in enumerate(ws):
   if w=='solchey':occ.append(dict(edition=m['edition'],locus=m['locus'],at=gs[i]['source_group_id'],index=i+1,line_initial=i==0,right=ws[i+1] if i+1<len(ws) else None,words=ws))
loci={r['locus'] for r in occ};allread=[r for r in alllines if r['locus'] in loci]
src=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());ps=[dict(edition=ed,**p) for ed,pp in src.items() for p in pp if loci & {l['locus'] for l in p['lines']}]
md=['# Alle vollständigen verfügbaren solchey-Trefferabsätze','']
for p in ps:md+=['## '+p['edition']+' '+p['id'],'']+[l['locus']+' `'+ ' '.join(l['words'])+'`' for l in p['lines']]+['']
(D/'COMPLETE_PARAGRAPHS.md').write_text('\n'.join(md)+'\n')
r=dict(counts={ed:sum(x['edition']==ed for x in occ) for ed in ['ZL3b','IT2a','RF1b']},physical_loci=sorted(loci),line_initial=sum(x['line_initial'] for x in occ),medial=sum(not x['line_initial'] for x in occ),complete_paragraphs=len(ps),meanings_confirmed=0)
for n,v in [('OCCURRENCES.json',occ),('ALL_READINGS.json',allread),('PARAGRAPHS.json',ps),('RESULT.json',r)]: (D/n).write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(r))
for x in allread:
 if x['edition']=='RF1b' and x['locus']=='f80r.32':print(x)
