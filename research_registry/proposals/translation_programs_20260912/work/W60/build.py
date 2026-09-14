from pathlib import Path
import json,hashlib,collections
D=Path(__file__).parent
s=json.loads(Path('experiments/yolo/gdt929_fixed_four_form_context_square/src/SPEC.json').read_text())
allow=set(json.loads(Path(s['allow_source']).read_text())['allowed_selectors']);occ=[];den=collections.Counter()
for p in s['sources']:
 assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==s['hashes'][p]
 d=json.loads(Path(p).read_text())
 for l in d['lines']:
  m=l['metadata'];assert m['page'] in allow and not m['page'].startswith('f84')
  gs=[dict(zip(d['group_columns'],g)) for g in l['groups']];den[m['edition']]+=len(gs)
  for i,g in enumerate(gs):
   if g['ivtff_group_raw'] not in ['qolshey','charor']:continue
   nxt=gs[i+1] if i+1<len(gs) else None
   occ.append(dict(edition=m['edition'],locus=m['locus'],word=g['ivtff_group_raw'],id=g['source_group_id'],words=[x['ivtff_group_raw'] for x in gs],right=nxt['ivtff_group_raw'] if nxt else None,right_definite=bool(nxt and g['right_separator']==nxt['left_separator']=='DEFINITE_SPACE' and int(nxt['source_group_index'])==int(g['source_group_index'])+1)))
loci={r['locus'] for r in occ};ps=json.loads(Path('experiments/yolo/gdt928_multi_anchor_complete_paragraphs/artifacts/PARAGRAPHS.json').read_text());pp=[dict(edition=ed,**p) for ed,rows in ps.items() for p in rows if loci & {l['locus'] for l in p['lines']}]
md=['# Sämtliche vollständigen verfügbaren Trefferabsätze','']
for p in pp:md+=['## '+p['edition']+' '+p['id'],'']+[l['locus']+' `'+ ' '.join(l['words'])+'`' for l in p['lines']]+['']
(D/'COMPLETE_PARAGRAPHS.md').write_text('\n'.join(md)+'\n')
res=dict(groups=dict(den),counts={ed:{w:sum(r['edition']==ed and r['word']==w for r in occ) for w in ['qolshey','charor']} for ed in sorted(den)},complete_paragraphs=len(pp),physical_loci=sorted(loci),qolshey_followed_qokain=sum(r['word']=='qolshey' and r['right']=='qokain' for r in occ),definite_qolshey_qokain=sum(r['word']=='qolshey' and r['right']=='qokain' and r['right_definite'] for r in occ),f80r_exact_sheey={p['edition']:sum(w=='sheey' for l in p['lines'] for w in l['words']) for p in pp if p['page']=='f80r'},meaning_confirmations=0)
for n,v in [('OCCURRENCES.json',occ),('PARAGRAPHS.json',pp),('RESULT.json',res)]: (D/n).write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(res,indent=2))
