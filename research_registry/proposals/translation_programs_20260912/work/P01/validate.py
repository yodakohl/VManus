#!/usr/bin/env python3
import csv,json,hashlib,itertools
from pathlib import Path
D=Path('research_registry/proposals/translation_programs_20260912/work/P01');read=lambda n:list(csv.DictReader((D/n).open(),delimiter='\t'))
s=json.loads((D/'SOURCE.json').read_text());assert hashlib.sha256(Path(s['path']).read_bytes()).hexdigest()==s['sha256']
source=json.loads(Path(s['path']).read_text())['lines'];raw=[(r['locus']+':'+str(i),w) for r in source for i,w in enumerate(r['groups'],1)];lookup=dict(raw);index={loc:i for i,(loc,w) in enumerate(raw)}
for mode in ['D','R']:assert [(x['locus'],x['word']) for x in read('ALIGNMENT_'+mode+'.tsv')]==raw
obs=read('FINDINGS.tsv');dec=read('ALL_DECISIONS.tsv');assert len(obs)==23 and len(dec)==8
for e in dec:
 prior=[x for x in obs if x['record']==e['record'] and index[x['locus']]<index[e['locus']]]
 hot=[x for x in prior if x['word']=='shey'];moist=[x for x in prior if x['word'] in ['chol','shol']]
 cause=hot[-1] if hot else moist[-1] if moist else None
 assert e['reason_locus']==(cause['locus'] if cause else 'NONE')
 expected={'shey':'Kühlen','chol':'Benetzen','shol':'Trocknen'}[cause['word']] if cause else 'UNRESOLVED'
 assert expected==e['expected_by_authored_rule']
for g in read('GRADES.tsv'):
 assert lookup[g['locus']]==g['word']
 if g['target']!='UNBOUND':assert index[g['locus']]==index[g['target']]+1 and lookup[g['target']] in ['cthy','chor','shor','chol','shol','shey']
pairs=read('ALL_CASE_PAIRS.tsv');assert len(pairs)==28 and {(x['a'],x['b']) for x in pairs}=={(a['locus'],b['locus']) for a,b in itertools.combinations(dec,2)}
conflicts=[x for x in pairs if x['status']=='SAME_NONEMPTY_REGISTER_DIFFERENT_ACTION'];assert len(conflicts)==1
for p in conflicts:
 a=next(e for e in dec if e['locus']==p['a']);b=next(e for e in dec if e['locus']==p['b']);assert a['register']==b['register'] and a['nonempty_register']=='1' and a['observed_action_hypothesis']!=b['observed_action_hypothesis']
out={'status':'PASS','scope':'source hash, 2x145 groups, all8 backward reasons, all28case pairs and every bound grade; no diagnosis or medical validation','confirmed_meanings':0}
(D/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
