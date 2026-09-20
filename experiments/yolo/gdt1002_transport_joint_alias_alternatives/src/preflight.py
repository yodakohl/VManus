import argparse,json,subprocess,sys
from pathlib import Path
from solver import solve
E=Path(__file__).resolve().parents[1]
g=dict(patterns=dict(INITIAL=['START','@Agent'],GOAL=['GO'],SAFETY=['SAFE'],CAPACITY=['ONE'],THEN=['T'],ALTERNATE=['U'],CONCLUSION=['END','@Agent']),types=dict(Agent=['M']))
a=dict(words='a m g s c z m'.split());b=dict(words='b n h t d z n'.split());bad=dict(words='z n h t d e n'.split())
c=dict(words='a m x g s c z m'.split());d=dict(words='b n x h t d z n'.split())
fixtures=[('unique',[a],dict(a='START',m='M',g='GO',s='SAFE',c='ONE',z='END'),'SAT'),('shared_compatible',[a,b],{},'SAT'),('shared_conflict',[a,bad],{},'UNSAT'),('alternatives',[c],dict(a='START',m='M',g='GO',s='SAFE',c='ONE',z='END'),'SAT'),('joint_alternative',[c,d],{'x':'T'},'SAT')]
p=argparse.ArgumentParser();p.add_argument('--cvc5-python',default=sys.executable);args=p.parse_args();out=[]
for name,ps,lex,expected in fixtures:
    r=solve(ps,lex,g);assert r['status']==expected
    other=subprocess.run([args.cvc5_python,str(E/'src/independent.py')],input=json.dumps(dict(paragraphs=ps,lexicon=lex,grammar=g)),text=True,capture_output=True,check=True);q=json.loads(other.stdout);assert q['status']==expected.lower()
    if name=='unique':
        assert r['exhaustive'] and len(r['witnesses'])==1
        block=subprocess.run([args.cvc5_python,str(E/'src/independent.py')],input=json.dumps(dict(paragraphs=ps,lexicon=lex,grammar=g,blocked=r['witnesses'][0])),text=True,capture_output=True,check=True)
        assert json.loads(block.stdout)['status']=='unsat'
    if name=='alternatives':assert len(r['witnesses'])==2 and {w['aliases']['x'] for w in r['witnesses']}=={'T','U'}
    out.append(dict(name=name,primary=r['status'],independent=q['status'],witnesses=len(r['witnesses'])))
result=dict(status='PASS',cases=out,scope='Synthetic complete shared-code grammar checks; no manuscript content')
(E/'artifacts/PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
