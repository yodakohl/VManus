from pathlib import Path
import json,csv,collections
D=Path(__file__).parent
occ=[r for r in json.loads((D.parent/'W75/OCCURRENCES.json').read_text()) if r['word']=='otchy'];lex=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];rows=[]
for r in occ:
 assert not r['page'].startswith('f84')
 left=lex.get(r['left'],{});right=lex.get(r['right'],{});lc=left.get('kind')=='MATERIAL';rc=right.get('kind')=='MATERIAL'
 rows.append(dict(edition=r['edition'],locus=r['locus'],at=r['at'],left=r['left'],right=r['right'],Q_left_material=r['left'] if lc else '',Q_right_material=r['right'] if rc else '',Q_carrier=r['left'] if lc else r['right'] if rc else '',Q_status='ADJACENT_ASSUMED_CARRIER' if lc or rc else 'NO_KNOWN_ADJACENT_CARRIER',N_right_quality=r['right'] if right.get('kind')=='QUALITY_OR_STATE' else '',full_line=' '.join(r['words'])))
unique={}
for r in occ:unique.setdefault((r['edition'],r['locus']),r)
al=[];md=['# Vollständige otchy-Zeilen in zwei Rollenfassungen','','Material T/Eigenschaft T sind Platzhalter, keine entzifferten Bedeutungen. Andere Glossen geerbt und unbestätigt.','']
for model,gloss in [('N','Material T'),('Q','Eigenschaft T')]:
 for (ed,locus),r in unique.items():
  md+=['## '+model+' '+ed+' '+locus,'','`'+ ' '.join(r['words'])+'`',''];out=[]
  for i,w in enumerate(r['words'],1):
   g=gloss if w=='otchy' else lex[w]['meaning'] if w in lex else '⟦'+w+'⟧';out.append(g);al.append(dict(model=model,edition=ed,locus=locus,index=i,word=w,hypothesis=g))
  md+=[' · '.join(out),'']
for name,data in [('ROLES.tsv',rows),('ALIGNMENT.tsv',al)]:
 with (D/name).open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(data[0]),delimiter='\t');w.writeheader();w.writerows(data)
(D/'READING.md').write_text('\n'.join(md)+'\n');res=dict(target_positions=len(rows),unique_reading_lines=len(unique),alignment_rows=len(al),Q_status=dict(collections.Counter(r['Q_status'] for r in rows)),N_right_quality_positions=sum(bool(r['N_right_quality']) for r in rows),selected=None,meaning_confirmed=False)
(D/'RESULT.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res));print(json.dumps([r for r in rows if r['Q_carrier'] or r['N_right_quality']]))
