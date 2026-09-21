from common import *
from model import compile_program,execute
from independent import compile_reverse,execute_facts
import copy

def main():
    s=source();clauses=s['complete_clauses'];tags={t for c in clauses for t in c['terminal_tags']}
    lex={'invented_'+t:{'tag':t} for t in tags};lines=[dict(raw=' '.join('invented_'+t for t in c['terminal_tags'])) for c in clauses]
    results=[]
    for branch in ['E','H']:
        for mode in ['BASELINE','CHOICE_IN_IMAGE','EARLY_ENCLOSE','IMAGE_AS_PART','BOTH_BRANCHES']:
            g=compile_program(lines,lex,clauses,branch,mode);h=compile_reverse(lines,lex,clauses,branch,mode)
            assert g==h
            x=execute(g);y=execute_facts(h);assert x==y,(branch,mode)
            assert (x['physical_status']=='COMPLETE')==(mode in ['BASELINE','CHOICE_IN_IMAGE'])
            assert bool(x['content_mismatches'])==(mode=='CHOICE_IN_IMAGE' and branch=='H')
            results.append(dict(branch=branch,mode=mode,status=x['physical_status'],mismatches=x['content_mismatches'],failure=x['first_failure']))
    g=compile_program(lines,lex,clauses,'E','BASELINE');negative=[]
    for loose in [['G','P'],['P','S'],['G','S'],['S']]:
        x=execute(g,{'loose':loose});y=execute_facts(g,{'loose':loose});assert x==y and x['physical_status']=='BLOCKED'
        negative.append(dict(loose=loose,failure=x['first_failure']))
    for item in ['G','P']:
        h=copy.deepcopy(g);h['required_under'].remove(item)
        x=execute(h);y=execute_facts(h);assert x==y and 'MISSING_POSE:'+item in x['first_failure']
        negative.append(dict(missing_pose=item,failure=x['first_failure']))
    for i in range(9):
        mutated=copy.deepcopy(lines);mutated[i]['raw']=' '.join(mutated[i]['raw'].split()[1:])
        for fn in [compile_program,compile_reverse]:
            try:fn(mutated,lex,clauses,'E','BASELINE')
            except (AssertionError,KeyError):pass
            else:raise AssertionError(('unrejected missing terminal',i))
    write(A/'PREFLIGHT.json',dict(status='PASS',executed_utc=now(),invented_complete_programs=results,missing_input_cases=negative,missing_clause_terminal_cases=9,scope='Invented terminals; no target parse or target execution.'))
    print('PASS: 10 synthetic programs, 6 missing-input cases, 9 omitted-terminal negatives.')

if __name__=='__main__':main()
