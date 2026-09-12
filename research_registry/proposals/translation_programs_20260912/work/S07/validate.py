from pathlib import Path
import csv,json,hashlib
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def read(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
for x in json.loads((D/'SOURCE.json').read_text())['files']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
s=read(D.parent/'S05/INPUT.tsv');a=read(D/'ALIGNMENT.tsv');assert len(a)==145
assert [(x['at'],x['word']) for x in a]==[(x['at'],x['word']) for x in s]
lex={x['form']:x['meaning_hypothesis'] for x in read(D.parent/'P05/LEXICON_v03.tsv')}
assert all(x['gloss']==lex.get(x['word'],'OPEN') for x in a)
c=read(D/'CENSUS.tsv')
expected={('f32v.8:2','f32v.7:10','f32v.8:1','f32v.7:8'),('f32v.9:4','f32v.9:4','f32v.9:6','f32v.9:3'),('f29v.2:3','f29v.1:7','f29v.2:1','f29v.1:6'),('f29v.3:1','f29v.2:7','f29v.2:8','f29v.2:6')}
assert {(x['start'],x['target1'],x['target2'],x['previous_action']) for x in c}==expected
# Exhaustive alternate window census on source, including record boundaries.
mat=set(json.loads((D.parent/'P05/REFERENCE_RULE_v02.json').read_text())['material_forms'])
starts=set()
for i in range(len(s)):
 for n in [2,4]:
  z=s[i:i+n]
  if len(z)!=n or len({x['record'] for x in z})!=1:continue
  w=[x['word'] for x in z]
  if (n==2 and w[0]==w[1] and w[0] in {'chol','daiin'}) or (n==4 and w[0] in mat and w[2] in mat and w[1]==w[3]=='daiin'):starts.add(z[0]['at'])
assert starts=={x['start'] for x in c}
for row in c:
 end=next(i for i,x in enumerate(s) if x['at']==row['end']);targets={next(x['word'] for x in s if x['at']==t) for t in [row['target1'],row['target2']]}
 actual=[x['at'] for x in s[end+1:] if x['record']==row['record'] and x['word'] in targets]
 assert (','.join(actual) or 'NONE')==row['later_same_forms']
assert len(read(D/'ROLE_CONSEQUENCES.tsv'))==6
for m in ['I','O','A']:
 text=(D/f'READING_{m}.md').read_text()
 for locus in dict.fromkeys(x['locus'] for x in s):assert '`'+' '.join(x['word'] for x in s if x['locus']==locus)+'`' in text
out={'status':'PASS','coverage':'all145groups, stable P05 values, exhaustive four-case census, all bindings, all later exact-form rementions, full three renderings','semantic_validation':False,'independent_folio_confirmation':False}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
