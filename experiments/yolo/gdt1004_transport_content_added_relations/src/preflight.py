import argparse,json,subprocess,sys
from pathlib import Path
import z3
from grammar import build
E=Path(__file__).resolve().parents[1]
g=dict(patterns=dict(INITIAL=['START','@Agent'],GOAL=['GO'],SAFETY=['SAFE'],CAPACITY=['ONE'],THEN=['T'],ALTERNATE=['U'],CONCLUSION=['END','@Agent']),types=dict(Agent=['M']))
a=dict(words='a m g s c z m'.split());b=dict(words='b n h t d z n'.split());bad=dict(words='z n h t d e n'.split());c=dict(words='a m x g s c z m'.split());d=dict(words='b n x h t d z n'.split());lex=dict(a='START',m='M',g='GO',s='SAFE',c='ONE',z='END')
fixtures=[('unique',[a],lex,[dict(id='exists')],['sat']),('shared_compatible',[a,b],{},[dict(id='exists')],['sat']),('shared_conflict',[a,bad],{},[dict(id='exists')],['unsat']),('alternatives',[c],lex,[dict(id='exists'),dict(id='T',word='x',value='T'),dict(id='U',word='x',value='U'),dict(id='M',word='x',value='M'),dict(id='exhausted',blocked_tuples=[{'x':'T'},{'x':'U'}])],['sat','sat','sat','unsat','unsat']),('joint_alternative',[c,d],{},[dict(id='T',word='x',value='T'),dict(id='U',word='x',value='U'),dict(id='not_exhausted',blocked_tuples=[{'x':'T'},{'x':'U'}])],['sat','sat','sat'])]
ap=argparse.ArgumentParser();ap.add_argument('--cvc5-python',default=sys.executable);args=ap.parse_args();out=[]
for name,ps,l,qs,expected in fixtures:
 built=build(ps,l,g);s=built['solver'];observed=[]
 for q in qs:
  s.push()
  if 'word' in q:s.add(built['xs'][q['word']]==built['num'][q['value']])
  for t in q.get('blocked_tuples',[]):s.add(z3.Or([built['xs'][w]!=built['num'][v] for w,v in t.items()]))
  observed.append(str(s.check()));s.pop()
 assert observed==expected,(name,observed,expected)
 job=dict(paragraphs=ps,lexicon=l,grammar=g,queries=qs)
 other=json.loads(subprocess.run([args.cvc5_python,str(E/'src/independent.py')],input=json.dumps(job),text=True,capture_output=True,check=True).stdout)
 assert [x['status'] for x in other['queries']]==expected
 out.append(dict(name=name,queries=qs,expected=expected,primary=observed,independent=other['queries']))
r=dict(status='PASS',cases=out,scope='Synthetic unchanged shared grammar and marginal/tuple query interfaces, not manuscript meaning');(E/'artifacts/PREFLIGHT.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(status='PASS',fixtures=len(out),queries=sum(len(x['queries']) for x in out))))
