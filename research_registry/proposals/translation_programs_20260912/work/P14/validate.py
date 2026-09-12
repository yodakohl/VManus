import csv,json,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P14')
def read(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text())
for key,h in [('source','sha256'),('lexicon','lexicon_sha256')]:assert hashlib.sha256(Path(s[key]).read_bytes()).hexdigest()==s[h]
assert hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
raw=json.loads(Path(s['source']).read_text());seq=[(r['locus'].split('.')[0],r['locus'],r['locus']+':'+str(i),w) for r in raw['lines'] for i,w in enumerate(r['groups'],1)]
m=json.loads((D/'MODEL.json').read_text());idx={a:i for i,(_,_,a,_) in enumerate(seq)}
for scope in ['RECORD','LINE']:
 for mode in ['G','M','R']:assert [(r['record'],r['at'],r['word']) for r in read('ALIGNMENT_'+mode+'_'+scope+'.tsv')]==[(r,a,w) for r,_,a,w in seq]
 fs=read('FIELDS_'+scope+'.tsv');assert len(fs)==10
 for f in fs:
  i=idx[f['at']];r,line,_,_=seq[i];left=[t for t in seq[:i] if t[0]==r and (scope=='RECORD' or t[1]==line)];n=[t for t in left if t[3] in m['materials']]
  assert f['material']==(n[-1][2] if n else '')
  den=next((t for t in reversed(n[:-1]) if t[3]!=n[-1][3]),None) if n else None
  assert f['denominator']==(den[2] if den else '')
  q=[t for t in left if t[3] in m['qualities'] and (not n or idx[t[2]]>idx[n[-1][2]])]
  assert f['quality']==(q[-1][2] if q else '')
 es=json.loads((D/('RATIO_ELIMINATION_'+scope+'.json')).read_text())
 # Independent forest certificate: every edge adds a new connectivity link,
 # so arbitrary positive A/B/C can be realized by assigning node masses.
 parent={n:n for n in es['nodes']}
 def root(n):
  while parent[n]!=n:n=parent[n]
  return n
 for e in es['edges']:
  a,b=root(e['numerator']),root(e['denominator']);assert a!=b;parent[a]=b
 assert es['material_rank']==len(es['edges']) and es['value_constraints']==[]
 for a in read('ACTIONS_'+scope+'.tsv'):
  i=idx[a['at']];candidate=''
  for r,line,at,w in seq[i+1:]:
   if r!=a['record'] or (scope=='LINE' and line!=seq[i][1]) or w in m['verbs'] or w in m['values']:break
   if w in m['materials']:candidate=at;break
  assert a['target']==candidate
for c in read('M_R_CONTRASTS.tsv'):
 fs=read('FIELDS_'+c['scope']+'.tsv');edge=next(f for f in fs if f['at']==c['at']);assert not edge['R_missing']
 for word in [c['numerator'],c['denominator']]:assert any(f['record']==edge['record'] and f['material_word']==word and f['value']==c['shared_M_value'] for f in fs)
 assert c['M_implied_ratio']=='1' and c['R_stated_ratio']==edge['value']
for c in read('RATIO_CHAINS.tsv'):
 fs={f['at']:f for f in read('FIELDS_'+c['scope']+'.tsv')};a,b=fs[c['first']],fs[c['second']];assert a['record']==b['record'] and a['material_word']==b['denominator_word'] and not a['R_missing'] and not b['R_missing']
 assert c['implied_ratio']==b['value']+'*'+a['value']
(D/'VALIDATION.json').write_text(json.dumps(dict(status='PASS',checks=['input/lexicon/decision hashes','six full145group alignments','all10value antecedents each scope','all action arguments','independent forest proof of unconstrained positive ratios','all cross-model equal-mass contrasts','derived ratio chain'],limitation='No independent dimensions, units, numeric values or meanings'),indent=2)+'\n')
print('PASS')
