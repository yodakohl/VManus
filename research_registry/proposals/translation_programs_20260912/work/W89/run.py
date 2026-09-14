from pathlib import Path
import json,csv,hashlib,collections
D=Path(__file__).resolve().parent.relative_to(Path.cwd());B=D.parent;sources=[B/'W84/PARAGRAPHS.json',B/'W88/PARAGRAPHS.json',B/'W88/LEXICON.json'];ps={}
for src in sources[:2]:
 for p in json.loads(src.read_text()):
  assert not p['page'].startswith('f84');key=p['edition'],p['id']
  if key in ps:assert ps[key]==p
  ps[key]=p
lex=json.loads(sources[2].read_text());desc={'qotchy':'beigefügt','qotaiin':'abgeseiht','chkaiin':'vermischt','sheey':'benetzt','ychocthy':'vermischt'};mat={w for w,v in lex.items() if v['kind'] in {'MATERIAL','MATERIAL_DOSE'}};rows=[];al=[];md=['# W89 vollständige eingefrorene Gegenlesungen','Alle Wortwerte und Zuordnungen sind unbestätigte Annahmen. Die fünf Prädikate unterscheiden die Fassungen.']
def status(w):return 'MISSING' if not w else 'MATERIAL_ASSUMED' if w in mat else 'WRONG_KNOWN_ROLE' if w in lex else 'UNKNOWN'
for p in ps.values():
 last=lastword=''
 for l in p['lines']:
  ws=l['words'];ids=l['source_ids']
  for i,(w,at) in enumerate(zip(ws,ids)):
   if w in mat:last,lastword=at,w
   if w not in desc:continue
   a=ws[i+1] if i+1<len(ws) else '';a_at=ids[i+1] if a else '';b=ws[i+2] if w=='ychocthy' and i+2<len(ws) else '';b_at=ids[i+2] if b else '';needprior=w in {'qotchy','chkaiin'}
   rows.append(dict(edition=p['edition'],paragraph=p['id'],at=at,word=w,R_directive=lex[w]['meaning'],R_input1=a,R_input1_at=a_at,R_input1_status=status(a),R_input2=b,R_input2_at=b_at,R_input2_status=status(b) if w=='ychocthy' else 'NOT_REQUIRED',R_recipient=last if needprior else '',R_recipient_word=lastword if needprior else '',R_recipient_status=('MATERIAL_ASSUMED' if last else 'MISSING') if needprior else 'NOT_REQUIRED',D_property=desc[w],D_subject=last,D_subject_word=lastword,D_subject_status='MATERIAL_ASSUMED' if last else 'MISSING',independent_discriminator='NONE_ESTABLISHED',independent_evidence=''))
for model in ['R','D']:
 for p in ps.values():
  md+=['\n## '+model+' '+p['edition']+' '+p['id']]
  for l in p['lines']:
   gg=[]
   for w,at in zip(l['words'],l['source_ids']):
    n={'dair':'A','dain':'B','daiin':'C'}.get(w);g='Masse '+n+'·Uₚ' if n else desc[w] if model=='D' and w in desc else lex.get(w,{}).get('meaning','⟦'+w+'⟧');gg.append(g);al.append(dict(model=model,edition=p['edition'],paragraph=p['id'],at=at,word=w,gloss=g))
   md+=['\n'+l['locus']+' `'+ ' '.join(l['words'])+'`','\n'+' · '.join(gg)]
for name,rr in [('CLAIMS.tsv',rows),('ALIGNMENT.tsv',al)]:
 with (D/name).open('w') as f:
  wr=csv.DictWriter(f,fieldnames=list(rr[0]),delimiter='\t');wr.writeheader();wr.writerows(rr)
for name,obj in [('PARAGRAPHS.json',list(ps.values())),('COMMON_LEXICON.json',lex),('DESCRIPTIVE_OVERRIDES.json',desc)]: (D/name).write_text(json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n')
(D/'READING.md').write_text('\n'.join(md)+'\n')
fields=['R_input1_status','R_input2_status','R_recipient_status'];conflicts=[r for r in rows if any(r[f]=='WRONG_KNOWN_ROLE' for f in fields)];r=dict(paragraphs=len(ps),groups=len(al)//2,claims=len(rows),predicates=dict(collections.Counter(r['word'] for r in rows)),R_obligations={f:dict(collections.Counter(r[f] for r in rows)) for f in fields},R_complete=sum(all(r[f] in {'MATERIAL_ASSUMED','NOT_REQUIRED'} for f in fields) for r in rows),R_conflicts=conflicts,D_subjects=dict(collections.Counter(r['D_subject_status'] for r in rows)),independent_semantic_discriminators=0,decision='SUSPEND_RECIPE_EXPANSION_NO_DESCRIPTIVE_PROMOTION',meaning_confirmed=False);(D/'RESULT.json').write_text(json.dumps(r,indent=2)+'\n');(D/'SOURCE_HASHES.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2)+'\n');print(json.dumps(r))
