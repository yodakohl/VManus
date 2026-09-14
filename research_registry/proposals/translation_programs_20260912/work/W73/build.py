from pathlib import Path
import csv,json,collections
D=Path(__file__).parent
ps=json.loads((D.parent/'W63/PARAGRAPHS.json').read_text());ev=list(csv.DictReader((D.parent/'W69/EVENTS.tsv').open(),delimiter='\t'));base={r['form']:r['role'] for r in csv.DictReader((D.parent/'W02/LEXICON.tsv').open(),delimiter='\t')};mod=set(json.loads((D.parent/'W05/SPEC.json').read_text())['transparent_roles']);rows=[];md=['# Vollständige Absätze und feste gemeinsame Rechtsanschlüsse','','Alle Rollen hypothetisch; offene Gruppen blockieren die Anschlussregel.','']
for p in ps:
 for m in ['NRC','AMV']:
  roles=dict(base,sheedy='MATERIAL',shey='MATERIAL',sheckhy='MATERIAL' if m=='NRC' else 'ACTION')
  if m=='AMV':roles.update(ol='MATERIAL',chey='NEGATION')
  es={e['at']:e for e in ev if e['model']==m and e['edition']==p['edition'] and e['paragraph']==p['id'] and e['kind']=='ACTION'}
  md+=['## '+p['edition']+' '+m+' '+p['id'],'']
  for l in p['lines']:
   ws=l['words'];ids=l['source_ids'];md += [l['locus']+' `'+ ' '.join(ws)+'`',''];i=0
   while i<len(ws):
    if ids[i] not in es:i+=1;continue
    j=i+1
    while j<len(ws) and ids[j] in es:j+=1
    if j-i>=2:
     for variant in ['J','M']:
      k=j
      if variant=='M':
       while k<len(ws) and roles.get(ws[k],'OPEN') in mod:k+=1
      target=k if k<len(ws) and roles.get(ws[k],'OPEN') in {'MATERIAL','MATERIAL_DOSE'} else None
      r=dict(edition=p['edition'],model=m,paragraph=p['id'],locus=l['locus'],variant=variant,operations=';'.join(ids[i:j]),words=' '.join(ws[i:j]),same_word_repeat=str(len(set(ws[i:j]))<j-i),status='SHARED_EXPLICIT_RIGHT' if target is not None else 'LINE_END' if k==len(ws) else 'BLOCKED_'+roles.get(ws[k],'OPEN'),target=ids[target] if target is not None else '',target_word=ws[target] if target is not None else '',stop_word=ws[k] if k<len(ws) else '',bridge=' '.join(ws[j:k]),old_patients=';'.join(es[a]['patient'] or 'UNBOUND' for a in ids[i:j]),raw_line=' '.join(ws))
      rows.append(r);md+=['- '+variant+' '+r['words']+': '+r['status']+'; rechts '+(r['target_word'] or 'KEIN MATERIAL')+'; Halt '+r['stop_word']]
    i=j
   md+=['']
with (D/'RUNS.tsv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
(D/'READING.md').write_text('\n'.join(md)+'\n');r=dict(run_variant_rows=len(rows),runs=len(rows)//2,status_counts=dict(collections.Counter(x['status'] for x in rows)),shared_tails=[x for x in rows if x['target']],meaning_confirmed=False)
(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
