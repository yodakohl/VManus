"""Separate coverage, immutable-source and algebra audit; no semantic validation."""
import csv,json,hashlib
from pathlib import Path
D=Path(__file__).resolve().parent
R=next(p for p in D.parents if (p/'vmanus-work').exists())
def rows(p):
 with p.open() as f:return list(csv.DictReader(f,delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text())
for f in s['files']:assert hashlib.sha256((R/f['path']).read_bytes()).hexdigest()==f['sha256']
expected={7:'ksho cphos she sheaiin otshcho r dain shckhy s odan',8:'otchol daiin daiin ctho daiin qotaiin otchy d shan',9:'qotchy cfhy skey chocthy daiin cthaiin daiin',10:'sho keol chor chol daiin cpho l cthol da ar',11:'ol sho chy'}
e=[(f'f32v.{n}:{i}',w) for n,t in expected.items() for i,w in enumerate(t.split(),1)]
assert [(x['at'],x['word']) for x in rows(D/'INPUT.tsv')]==e
lex={x['form']:x['meaning_hypothesis'] for x in rows(D.parent/'P05/LEXICON_v03.tsv')}
for v in ['M','K']:
 a=rows(D/f'ALIGNMENT_{v}.tsv');assert [(x['at'],x['word']) for x in a]==e
 assert sum(x['status']=='OPEN' for x in a)==4
 for w in set(w for _,w in e):assert len({x['gloss'] for x in a if x['word']==w})==1
 if v=='M':assert all(x['gloss']==lex.get(x['word'],'OPEN') for x in a)
expected_q={'f32v.7:7':'OPEN','f32v.8:2':'f32v.7:10','f32v.8:3':'f32v.8:1','f32v.8:5':'f32v.8:4','f32v.9:5':'f32v.9:4','f32v.9:7':'f32v.9:6','f32v.10:5':'f32v.10:3'}
assert {x['at']:x['target_at'] for x in rows(D/'QUANTITIES.tsv')}==expected_q
f=rows(D/'FRAMES_M.tsv');assert len(f)==8
assert {x['word'] for x in f}=={'cphos','she','shckhy','otchy','qotchy','skey','cpho','chy'}
audit=json.loads((D/'MASS_AUDIT.json').read_text());w=audit['M_without_origin_bridge_witness']
assert w['Q']>0 and w['O1']==w['Q']==w['O2'] and w['O1']+w['O2']<=w['F']<=w['P']
# Sum inequalities O1+O2-F<=0, F-P<=0, P-Q<=0, substituting O1=O2=Q.
# Coefficients in order Q,F,P; resulting Q<=0 contradicts positive Q.
coeffs=[(2,-1,0),(0,1,-1),(-1,0,1)]
assert tuple(map(sum,zip(*coeffs)))==(1,0,0)
assert w['P']>w['Q'] # primary M witness intentionally does not satisfy M+ origin bridge
out={'status':'PASS','checks':['source hashes','all39groups exact','both alignments complete and stable','M values unchanged from P05','all7quantity loci and targets','all8action frames','M conditional mass witness','M+ symbolic inequality sum'],'semantic_validation':False,'blind_test':False,'limitation':'Audits authored model and source conservation, not historical truth or completeness of alternative interpretations.'}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
