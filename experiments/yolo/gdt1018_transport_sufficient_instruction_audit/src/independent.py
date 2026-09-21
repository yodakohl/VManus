"""Universal prefix trie over frozen independent bit-executor complete paths.
Future failure never determines current edge eligibility.
"""
from common import *
from collections import defaultdict

def evaluate(parsed,variant):
    s=inputs();error=load(s['binding_checker'],'binding994').binding_error(parsed,variant)
    if error:return dict(status='INVALID',error=error)
    paths,hazards,refs=load(s['bit_replay'],'bits1006').replay(parsed,variant)
    failures=[];successes=[];choices=[]
    def current(p,cid):
        failed=p['physical_failure'];at_fail=failed if failed and failed['clause']==cid else None
        step=next((t for t in p['trace'] if t['clause']==cid),None)
        reasons=[]
        if at_fail:reasons.extend(at_fail['reasons'])
        reasons += [a['reason'] for a in p['assertions'] if a['clause']==cid]
        if any(a['after']==cid for a in p['safety_violations']):reasons.append('UNSAFE_STATE')
        load_=at_fail['attempted_load'] if at_fail else step['load'] if step else None
        return step,load_,reasons
    def visit(i,rows,prefix):
        if i==len(parsed):
            assert rows
            if all(paths[r]['goal_reached'] for r in rows):successes.append(prefix)
            else:failures.append(dict(clause='END',reason='GOAL_UNREACHED',prefix=prefix))
            return
        c=parsed[i];cid=f'S{i+1:02d}'
        opened=c['kind']=='EXCLUDE' and variant['exclude']=='EXCLUDING'
        groups=defaultdict(list)
        for j in rows:
            step,load_,reasons=current(paths[j],cid)
            key=json.dumps([step,load_,reasons],sort_keys=True)
            groups[key].append(j)
        eligible=0;excluded=[]
        for key,indices in sorted(groups.items()):
            step,load_,reasons=json.loads(key)
            if reasons:
                if opened:excluded.append(dict(load=load_,reasons=reasons))
                else:failures.append(dict(clause=cid,reason='FIXED_OR_ASSERTION_FAILED',reasons=reasons,prefix=prefix))
                continue
            eligible+=1
            visit(i+1,indices,prefix+([dict(clause=cid,load=load_)] if step is not None else []))
        if opened:
            choices.append(dict(clause=cid,prefix=prefix,eligible_count=eligible,excluded=excluded))
            if not eligible:failures.append(dict(clause=cid,reason='NO_PERMISSIBLE_LOAD',prefix=prefix))
    visit(0,list(range(len(paths))),[])
    return dict(status='SUFFICIENT' if not failures and successes else 'INSUFFICIENT',
                successful_paths=len(successes),failed_prefixes=len(failures),failures=failures,choices=choices,
                old_existential=any(p['consistent'] for p in paths),old_enumerated_paths=len(paths))
