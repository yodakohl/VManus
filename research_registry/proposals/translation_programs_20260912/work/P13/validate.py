import json,csv,hashlib
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P13')
def read(n):return list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text())
for f in s['sources']:assert hashlib.sha256(Path(f['path']).read_bytes()).hexdigest()==f['sha256']
assert hashlib.sha256((D/'DECISION.md').read_bytes()).hexdigest()==s['decision_sha256']
x=json.loads(Path(s['sources'][0]['path']).read_text());seq=[(r['locus'].split('.')[0],r['locus']+':'+str(i),w) for r in x['lines'] for i,w in enumerate(r['groups'],1)]
idx={a:i for i,(_,a,_) in enumerate(seq)};m=json.loads((D/'MODEL.json').read_text())
for mode in ['U','P','N']:assert [(r['record'],r['at'],r['word']) for r in read('ALIGNMENT_'+mode+'.tsv')]==seq
acts=read('ALL_ACTIONS.tsv');targets=read('ALL_TARGETS.tsv')
assert [a['at'] for a in acts]==[a for _,a,w in seq if w in m['verbs']]
for a in acts:
 target=''
 for r,at,w in seq[idx[a['at']]+1:]:
  if r!=a['record'] or w in m['verbs']:break
  if w in m['materials']:target=at;break
 assert a['argument']==target
assert [o['at'] for o in targets]==[a for _,a,w in seq if w in m['targets']]
for o in targets:
 past=[a for a in acts if a['record']==o['record'] and idx[a['at']]<idx[o['at']]]
 assert o['trigger']==(past[-1]['at'] if past else '')
 completed=[a['at'] for a in past if a['argument_word']==o['word'] and idx[a['argument']]<idx[o['at']]]
 assert o['prior_producers']==','.join(completed)
 assert o['current_input']==','.join(a['at'] for a in past if a['argument']==o['at'])
 assert o['P_sense']==('processed' if past else 'raw')
 assert (o['U_conflict']=='True')==bool(completed)
res=json.loads((D/'RESULT.json').read_text());assert res['target_occurrences']==len(targets)==9
assert res['switches']==sum(o['P_sense']=='processed' for o in targets)==5
assert res['supported_switches']==sum(o['status']=='SUPPORTED_PROCESS_STATE' for o in targets)==0
(D/'VALIDATION.json').write_text(json.dumps(dict(status='PASS',checks=['source/lexicon/decision hashes','three full alignments','all six action arguments','all nine exact target forms','common trigger at every target','same-material completion chronology','no shey/sheey conflation'],limitation='Internal model consequences, not word-meaning evidence'),indent=2)+'\n')
print('PASS')
