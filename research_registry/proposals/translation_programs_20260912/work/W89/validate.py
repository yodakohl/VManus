from pathlib import Path
import json,csv,hashlib,collections
D=Path(__file__).resolve().parent.relative_to(Path.cwd());B=D.parent
for p,h in json.loads((D/'SOURCE_HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
ps={}
for path in [B/'W84/PARAGRAPHS.json',B/'W88/PARAGRAPHS.json']:
 for p in json.loads(path.read_text()):
  assert not p['page'].startswith('f84');k=p['edition'],p['id']
  if k in ps:assert ps[k]==p
  ps[k]=p
assert list(ps.values())==json.loads((D/'PARAGRAPHS.json').read_text());lex=json.loads((D/'COMMON_LEXICON.json').read_text());assert lex==json.loads((B/'W88/LEXICON.json').read_text());desc=json.loads((D/'DESCRIPTIVE_OVERRIDES.json').read_text());assert desc==dict(qotchy='beigefügt',qotaiin='abgeseiht',chkaiin='vermischt',sheey='benetzt',ychocthy='vermischt');mat={w for w,v in lex.items() if v['kind'] in {'MATERIAL','MATERIAL_DOSE'}};rows=[];al=[]
def status(w):return 'MISSING' if not w else 'MATERIAL_ASSUMED' if w in mat else 'WRONG_KNOWN_ROLE' if w in lex else 'UNKNOWN'
for p in ps.values():
 flat=[(w,s) for l in p['lines'] for w,s in zip(l['words'],l['source_ids'])];ix={s:i for i,(w,s) in enumerate(flat)}
 for l in p['lines']:
  pairs=list(zip(l['words'],l['source_ids']))
  for i,(w,at) in enumerate(pairs):
   if w not in desc:continue
   previous=next(((x,y) for x,y in reversed(flat[:ix[at]]) if x in mat),('',''));lastword,last=previous
   a,a_at=pairs[i+1] if i+1<len(pairs) else ('','');b,b_at=pairs[i+2] if w=='ychocthy' and i+2<len(pairs) else ('','');need=w in {'qotchy','chkaiin'}
   rows.append(dict(edition=p['edition'],paragraph=p['id'],at=at,word=w,R_directive=lex[w]['meaning'],R_input1=a,R_input1_at=a_at,R_input1_status=status(a),R_input2=b,R_input2_at=b_at,R_input2_status=status(b) if w=='ychocthy' else 'NOT_REQUIRED',R_recipient=last if need else '',R_recipient_word=lastword if need else '',R_recipient_status=('MATERIAL_ASSUMED' if last else 'MISSING') if need else 'NOT_REQUIRED',D_property=desc[w],D_subject=last,D_subject_word=lastword,D_subject_status='MATERIAL_ASSUMED' if last else 'MISSING',independent_discriminator='NONE_ESTABLISHED',independent_evidence=''))
assert rows==list(csv.DictReader((D/'CLAIMS.tsv').open(),delimiter='\t'))
for m in ['R','D']:
 for p in ps.values():
  for l in p['lines']:
   for w,at in zip(l['words'],l['source_ids']):
    n={'dair':'A','dain':'B','daiin':'C'}.get(w);g='Masse '+n+'·Uₚ' if n else desc[w] if m=='D' and w in desc else lex.get(w,{}).get('meaning','⟦'+w+'⟧');al.append(dict(model=m,edition=p['edition'],paragraph=p['id'],at=at,word=w,gloss=g))
assert al==list(csv.DictReader((D/'ALIGNMENT.tsv').open(),delimiter='\t'));r=json.loads((D/'RESULT.json').read_text());assert len(ps)==r['paragraphs']==140 and len(al)==r['groups']*2==17200 and len(rows)==r['claims']==106
for f in ['R_input1_status','R_input2_status','R_recipient_status']:assert r['R_obligations'][f]==dict(collections.Counter(x[f] for x in rows))
assert r['D_subjects']==dict(collections.Counter(x['D_subject_status'] for x in rows));assert r['R_conflicts']==[x for x in rows if x['R_input1_status']=='WRONG_KNOWN_ROLE' or x['R_input2_status']=='WRONG_KNOWN_ROLE']
assert r['R_complete']==sum(all(x[f] in {'MATERIAL_ASSUMED','NOT_REQUIRED'} for f in ['R_input1_status','R_input2_status','R_recipient_status']) for x in rows)==10
v=dict(status='PASS',paragraphs=140,groups_per_model=8600,claim_pairs=106,known_role_conflicts=5,descriptive_missing_subjects=43,meaning_validated=False,independent_evidence_assessment='manual EVIDENCE_REVIEW.md, not proved by validator');(D/'VALIDATION.json').write_text(json.dumps(v,indent=2)+'\n');print(v)
