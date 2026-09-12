from pathlib import Path
import csv,json,hashlib
D=Path(__file__).resolve().parent;R=next(p for p in D.parents if (p/'vmanus-work').exists())
def rows(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
for x in json.loads((D/'SOURCE.json').read_text())['files']:assert hashlib.sha256((R/x['path']).read_bytes()).hexdigest()==x['sha256']
s=[x for x in rows(D.parent/'S05/INPUT.tsv') if x['record']=='f29v'];a=rows(D/'ALIGNMENT.tsv');assert len(a)==40
assert [(x['at'],x['word']) for x in a]==[(x['at'],x['word']) for x in s]
lex={x['form']:x['meaning_hypothesis'] for x in rows(D.parent/'P05/LEXICON_v03.tsv')};assert all(x['gloss']==lex.get(x['word'],'OPEN') for x in a)
expected={x['at'] for x in s if x['word'] in {'shy','chol','otshy','oltchy','sy'}};assert len(expected)==9
for m in ['REPORT','REQUIRE','MIX']:
 q=rows(D/f'QUALITIES_{m}.tsv');assert {x['at'] for x in q}==expected
 assert sum(x['mode']=='REQUIREMENT' for x in q)=={'REPORT':0,'REQUIRE':9,'MIX':1}[m]
 dry=next(x for x in q if x['at']=='f29v.2:3');assert dry['prior_effect_or_report']=='wet' and dry['target_at']=='f29v.1:7'
 assert dry['status']==('CONTRARY_TO_LAST_EFFECT' if m=='REQUIRE' else 'REPORTED_TRANSITION_UNEXPLAINED')
 if m=='REQUIRE':assert sum(x['status']=='UNKNOWN' for x in q)==8
 text=(D/f'READING_{m}.md').read_text()
 for locus in dict.fromkeys(x['locus'] for x in s):assert '`'+' '.join(x['word'] for x in s if x['locus']==locus)+'`' in text
assert ' '.join(x['word'] for x in s if x['at'] in ['f29v.3:9','f29v.3:10','f29v.3:11'])=='she otey sy'
assert all(x['patient']=='OPEN' and x['independent_later_observation']=='NONE' for x in rows(D/'UNTIL_CHAIN.tsv'))
out={'status':'PASS','coverage':'source hashes,40groups,fixed values,all9quality loci in3modes,wet/dry endpoint,three entire readers,until chain with missing patient','semantic_validation':False}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
