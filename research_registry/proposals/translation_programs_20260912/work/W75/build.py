from pathlib import Path
import json,hashlib,collections,csv
D=Path(__file__).parent
s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text());allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);forms={'qotchol','yteol','otchy','odaiin','cfhy','taiin'};anchors={'qotaiin','shey','qotchy','sho','chkaiin'};out=[]
for path in s['sources']:
 assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==s['hashes'][path]
 d=json.loads(Path(path).read_text())
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84')
  gs=[dict(zip(d['group_columns'],g)) for g in l['groups']];ws=[g['ivtff_group_raw'] for g in gs]
  for i,w in enumerate(ws):
   if w in forms:out.append(dict(edition=m['edition'],page=m['page'],locus=m['locus'],at=gs[i]['source_group_id'],word=w,left=ws[i-1] if i else '',right=ws[i+1] if i+1<len(ws) else '',left_separator=gs[i].get('left_separator',''),right_separator=gs[i].get('right_separator',''),relational_contact=i>0 and ws[i-1] in anchors,words=ws))
(D/'OCCURRENCES.json').write_text(json.dumps(out,indent=2)+'\n');contacts=[r for r in out if r['relational_contact']];(D/'CONTACTS.json').write_text(json.dumps(contacts,indent=2)+'\n')
loci={r['locus'] for r in contacts};src=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());ps=[dict(edition=ed,**p) for ed,pp in src.items() for p in pp if loci & {l['locus'] for l in p['lines']}];(D/'PARAGRAPHS.json').write_text(json.dumps(ps,indent=2)+'\n')
md=['# Vollständige Absätze aller festen Relationskontakte','','Keine neuen Wortwerte. Andere Vorkommen bleiben vollständig in OCCURRENCES.json.','']
for p in ps:
 md+=['## '+p['edition']+' '+p['id'],'']
 for l in p['lines']:md+=[l['locus']+' `'+ ' '.join(l['words'])+'`','']
(D/'PARAGRAPHS.md').write_text('\n'.join(md)+'\n')
counts=[dict(word=w,**{ed:sum(r['word']==w and r['edition']==ed for r in out) for ed in ['ZL3b','IT2a','RF1b']},loci=len({r['locus'] for r in out if r['word']==w}),selectors=len({r['page'] for r in out if r['word']==w})) for w in sorted(forms)]
with (D/'COUNTS.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(counts[0]),delimiter='\t');w.writeheader();w.writerows(counts)
r=dict(occurrences=len(out),counts=counts,contacts=len(contacts),contact_loci=len(loci),complete_paragraphs=len(ps),meaning_confirmed=False)
(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r));print(json.dumps([{k:r[k] for k in ['edition','locus','word','left']} for r in contacts]))
