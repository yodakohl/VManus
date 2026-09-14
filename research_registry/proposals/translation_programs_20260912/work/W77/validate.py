from pathlib import Path
import csv,json,hashlib
D=Path(__file__).parent
for p,h in json.loads((D/'HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h,p
occ=[r for r in json.loads((D.parent/'W75/OCCURRENCES.json').read_text()) if r['word']=='otchy'];lex=json.loads((D.parent/'P09/MODELS.json').read_text())['models']['R1']['lexicon'];rr=list(csv.DictReader((D/'ROLES.tsv').open(),delimiter='\t'));al=list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));assert len(occ)==len(rr)==117
for o,r in zip(occ,rr):
 assert (o['at'],o['edition'],' '.join(o['words']))==(r['at'],r['edition'],r['full_line'])
 left=o['left'] if lex.get(o['left'],{}).get('kind')=='MATERIAL' else '';right=o['right'] if lex.get(o['right'],{}).get('kind')=='MATERIAL' else ''
 assert (r['Q_left_material'],r['Q_right_material'],r['Q_carrier'])==(left,right,left or right)
 assert r['N_right_quality']==(o['right'] if lex.get(o['right'],{}).get('kind')=='QUALITY_OR_STATE' else '')
unique={}
for o in occ:unique.setdefault((o['edition'],o['locus']),o['words'])
expected=[]
for m,g in [('N','Material T'),('Q','Eigenschaft T')]:
 for (ed,locus),ws in unique.items():
  for i,w in enumerate(ws,1):expected.append(dict(model=m,edition=ed,locus=locus,index=str(i),word=w,hypothesis=g if w=='otchy' else lex[w]['meaning'] if w in lex else '⟦'+w+'⟧'))
assert expected==al and len(al)==2068
v=dict(status='PASS',all_targets=117,unique_reading_lines=114,alignment_rows=2068,meaning_validated=False)
(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
