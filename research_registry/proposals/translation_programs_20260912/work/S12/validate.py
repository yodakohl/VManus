from pathlib import Path
import csv,json,hashlib
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def rows(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
for x in json.loads((D/'SOURCE.json').read_text())['files']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
s=rows(D.parent/'S05/INPUT.tsv');model=json.loads((D/'MODEL.json').read_text());n={'cthy','chor','shor','okaiin'}
for m in ['A','M','L']:
 a=rows(D/f'ALIGNMENT_{m}.tsv');assert len(a)==145
 assert [(x['at'],x['word']) for x in a]==[(x['at'],x['word']) for x in s]
 assert all(x['gloss']==model[m].get(x['word'],'OPEN') for x in a)
 text=(D/f'READING_{m}.md').read_text()
 for locus in dict.fromkeys(x['locus'] for x in s):assert '`'+' '.join(x['word'] for x in s if x['locus']==locus)+'`' in text
b=rows(D/'BINDINGS.tsv');assert len(b)==6
for x in b:
 ss=[z for z in s if z['record']==x['record']];i=next(i for i,z in enumerate(ss) if z['at']==x['at']);left=[z for z in ss[:i] if z['word'] in n];right=[]
 for z in ss[i+1:]:
  if z['word'] in {'sho','qotchy'}:break
  if z['word'] in n:right.append(z);break
 assert x['left_at']==(left[-1]['at'] if left else 'NONE') and x['right_at']==(right[0]['at'] if right else 'NONE')
e=rows(D/'EVENTS.tsv');expected={'f21r.9:2':'JOINED','f32v.9:1':'MISSING_ARGUMENT','f32v.10:1':'MISSING_ARGUMENT','f32v.11:2':'MISSING_ARGUMENT','f29v.3:6':'NO_PRIOR_EDGE','f29v.4:8':'JOINED'}
assert {x['at']:x['assembly'] for x in e}==expected
for x in e:
 if x['assembly']=='JOINED':
  z=next(z for z in b if z['at']==x['at']);i=next(i for i,t in enumerate(s) if t['at']==z['right_at']);assert not any(t['record']==x['record'] and t['word'] in {x['left'],x['right']} for t in s[i+1:])
assert rows(D/'LATER_COMPONENT_MENTIONS.tsv')==[]
p=rows(D/'ALL_JOIN_PAIRS.tsv');assert len(p)==1 and p[0]['same_unordered_classes']=='True' and p[0]['same_direction']=='False'
out={'status':'PASS','coverage':'sources,all145groups3fixedreaders,all6roles independently reconstructed,all operation outcomes,reverse-class pair,zero later component mentions','semantic_validation':False,'independent_confirmation':False}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
