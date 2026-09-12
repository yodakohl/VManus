from pathlib import Path
import csv,json,hashlib
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def rows(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
for x in json.loads((D/'SOURCE.json').read_text())['files']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
s=[x for x in rows(D.parent/'S05/INPUT.tsv') if x['record']=='f29v'];a=rows(D/'ALIGNMENT.tsv');assert len(s)==len(a)==40
assert [(x['at'],x['word']) for x in s]==[(x['at'],x['word']) for x in a]
lex={x['form']:x['meaning_hypothesis'] for x in rows(D.parent/'P05/LEXICON_v03.tsv')};assert all(x['gloss']==lex.get(x['word'],'OPEN') for x in a)
order={x['at']:i for i,x in enumerate(s)}
assert order['f29v.1:6']<order['f29v.1:7']<order['f29v.2:3']<order['f29v.2:5']<order['f29v.4:4']
expected={'f29v.1:6':'f29v.1:7','f29v.1:8':'f29v.1:7','f29v.1:10':'f29v.1:11','f29v.2:3':'f29v.1:7','f29v.2:4':'f29v.2:1','f29v.3:1':'f29v.2:7','f29v.3:2':'f29v.2:8','f29v.4:2':'f29v.4:3','f29v.4:5':'f29v.4:4','f29v.4:7':'f29v.4:8'}
for mode in ['SAME','FRESH','TIME']:
 e=rows(D/f'EVENTS_{mode}.tsv');assert {x['at']:x['target_at'] for x in e}==expected
 issues=[x for x in e if x['status']!='SET_OR_COMPATIBLE'];assert len(issues)==1
 z=issues[0];assert (z['prior_event'],z['at'],z['target_at'],z['prior'],z['value'])==('f29v.1:6','f29v.2:3','f29v.1:7','wet','dry')
 assert z['status']==('TRANSITION_UNEXPLAINED' if mode=='TIME' else 'PERSISTENCE_CONFLICT')
 assert e[0]['individual']==z['individual']
 text=(D/f'READING_{mode}.md').read_text()
 for locus in dict.fromkeys(x['locus'] for x in s):assert '`'+' '.join(x['word'] for x in s if x['locus']==locus)+'`' in text
m={x['at']:x['individual'] for x in rows(D/'MATERIALS_FRESH.tsv')};assert len({m[p] for p in ['f29v.1:7','f29v.2:5','f29v.4:4']})==3
out={'status':'PASS','coverage':'source conservation,40groups,fixed glosses,all10bindings in3models,chronology,issue endpoints,fresh mentions,full readings','semantic_validation':False,'physical_impossibility_claim':False}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
