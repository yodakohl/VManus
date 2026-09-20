"""Known full content fixtures against both new encodings and the old executor."""
import argparse,importlib.util,itertools,json,subprocess,sys
from pathlib import Path
from world import build,witness
E=Path(__file__).resolve().parents[1];R=E.parents[2]
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
g=json.loads((R/'experiments/yolo/gdt993_complete_transport_consequence_audit/src/SPEC.json').read_text());model=load(R/'experiments/yolo/gdt993_complete_transport_consequence_audit/src/model.py','fixedmodel')
base=[('INITIAL',['INIT','CARGOS','COLOC','M','HOME']),('GOAL',['GOAL','FAR_BANK','WITHOUT_HARM','HARM']),('SAFETY',['UNSAFE','PAIRS','FORBIDDEN','WHEN','WITHOUT_AGENT','M']),('CAPACITY',['AT_MOST_ONE','BESIDES','M','EXAMPLE','W'])]
end=('CONCLUSION',['THUS','ALL','UNHARMED','THERE','ATTENDED_BY','M'])
F=lambda cargo:('FERRY',['FERRY',cargo]);OUT=lambda cargo:('WITH_OUT',['WITH_TRIP','B','TAKE_OUT',cargo]);BACK=lambda cargo:('WITH_RETURN',['WITH_TRIP',cargo,'RETURN']);EX=lambda cargo:('EXCLUDE',['RETURN_EXCLUDING',cargo]);ALONE=('ALONE',['RETURN','ALONE']);STAY=('STAY',['LEAVE','THERE']);FINAL=('FINAL_TRIP',['FINALLY','OUTWARD','TRAVEL_TOGETHER','M','W'])
fixtures=[('out',[OUT('W')],True),('convey',[('CONVEY',['CONVEY_OUT','NEXT','W'])],True),('ferry',[F('W')],True),('final',[FINAL],True),('return_at_home',[ALONE],False),('stay_without_load',[STAY],False),('back_to_home',[F('W'),F('W')],False),('cargo_wrong_bank',[F('W'),ALONE,F('W')],False),('future_named_cargo',[F('W'),ALONE,F('G')],True),('loaded_return',[F('W'),BACK('W'),F('W')],True),('stay_then_other',[OUT('W'),STAY,ALONE,F('G')],True),('stay_after_empty_return',[OUT('W'),ALONE,STAY,F('G')],False),('trip_after_final',[FINAL,F('W')],False),('first_ref',[F('FIRST_CARGO')],True),('other_ref',[F('OTHER_CARGO')],True),('excluding_at_home',[EX('W'),F('W')],False),('excluding_then_other',[OUT('W'),EX('W'),F('G')],True),('future_cargo_cannot_disappear',[OUT('W'),EX('G'),F('W')],False),('current_stay',[F('W'),BACK('W'),STAY,F('W')],True),('unmoved_example',[('CONVEY',['CONVEY_OUT','NEXT','G'])],False)]
a=argparse.ArgumentParser();a.add_argument('--cvc5-python',default=sys.executable);args=a.parse_args();results=[]
variants=[dict(exclude='EXCLUDING',first='FIRST',other=other,there=there,copy='FIRST') for other,there in itertools.product(('OTHER','FIRST'),('GOAL','CURRENT'))]
for name,body,expected in fixtures:
    clauses=base+body+[end];symbols=[x for k,ss in clauses for x in ss];words=['fixture_'+x.lower() for x in symbols];lex=dict(zip(words,symbols));p=dict(words=words);pos=0;parsed=[]
    for k,ss in clauses:parsed.append(dict(start=pos,end=pos+len(ss),kind=k,symbols=ss));pos+=len(ss)
    truth=[]
    for variant in variants:
        try:truth.append(any(t['consistent'] for t in model.execute(model.compile_reading(parsed,variant),variant)))
        except ValueError:truth.append(False)
    assert any(truth)==expected,(name,truth)
    b=build([p],lex,g);answer=str(b['solver'].check());assert answer==('sat' if expected else 'unsat'),(name,answer)
    if expected:
        w=witness(b);assert any(t['consistent'] for t in model.execute(model.compile_reading(w['parses'][0],w['variant']),w['variant']))
    queries=[dict(id='exists')]
    if name=='other_ref':queries+=[dict(id='other_first_false',other_first=False),dict(id='other_first_true',other_first=True)]
    if name=='current_stay':queries+=[dict(id='there_goal',there_current=False),dict(id='there_current',there_current=True)]
    out=subprocess.run([args.cvc5_python,str(E/'src/independent.py')],input=json.dumps(dict(paragraphs=[p],lexicon=lex,grammar=g,queries=queries)),capture_output=True,text=True,check=True);other=json.loads(out.stdout)
    assert other['queries'][0]['status']==answer,(name,other)
    if len(queries)>1:assert [q['status'] for q in other['queries'][1:]]==['unsat','sat']
    results.append(dict(name=name,groups=len(words),primary=answer,independent=other,old_executor=truth))
result=dict(status='PASS',cases=len(results),results=results,scope='Synthetic whole semantic programs, including future cargo and explicit references; not manuscript/source truth')
(E/'artifacts/PREFLIGHT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='results'},indent=2))
