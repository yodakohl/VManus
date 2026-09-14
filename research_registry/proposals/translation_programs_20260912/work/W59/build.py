from pathlib import Path
import json,csv
D=Path(__file__).parent
ps=[p for p in json.loads((D.parent/'W56/PARAGRAPHS.json').read_text()) if p['page']=='f75v']
actions=list(csv.DictReader((D.parent/'W58/ACTIONS.tsv').open(),delimiter='\t'));occ=[];bindings=[];md=['# Vollständige unveränderte Quellabsätze','']
for p in ps:
 ed=p['edition'];flat=[(sid,w,l['locus']) for l in p['lines'] for sid,w in zip(l['source_ids'],l['words'])]
 md+=['## '+ed,'']+[l['locus']+' `'+ ' '.join(l['words'])+'`' for l in p['lines']]+['']
 for i,(sid,w,locus) in enumerate(flat):
  if w=='qokain':occ.append(dict(edition=ed,at=sid,left=flat[i-1][1] if i else 'BOUNDARY',right=flat[i+1][1] if i+1<len(flat) else 'BOUNDARY',locus=locus,raw_line=' '.join(next(l['words'] for l in p['lines'] if l['locus']==locus))))
 for a in actions:
  if a['edition']!=ed or a['action']!='benetze':continue
  i=next(i for i,t in enumerate(flat) if t[0]==a['at']);n=flat[i+1] if i+1<len(flat) and flat[i+1][2]==flat[i][2] else None
  bindings.append(dict(edition=ed,model=a['model'],at=a['at'],word=a['word'],patient=a['patient'],right_word=n[1] if n else 'BOUNDARY',I_medium=n[0] if n and n[1]=='qokain' else 'UNBOUND',Q_medium='UNBOUND'))
for name,data in [('QOKAIN.tsv',occ),('WETTING.tsv',bindings)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]),delimiter='\t');w.writeheader();w.writerows(data)
(D/'COMPLETE_SOURCE.md').write_text('\n'.join(md)+'\n')
result=dict(qokain_reading_occurrences=len(occ),wetting_reading_cases=len(bindings),I_bound=sum(r['I_medium']!='UNBOUND' for r in bindings),distinct_I_bound_loci=['f75v.40'],meaning_confirmations=0,prior_patient_bindings_changed=False)
(D/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
