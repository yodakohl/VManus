from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone
import json, hashlib, re
E=Path(__file__).resolve().parents[1]; R=E.parents[2]
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def intact(gs):
    if any(not re.fullmatch('[a-z]+',g['ivtff_group_raw']) or g['left_separator'] not in {'DEFINITE_SPACE','LINE_START','LINE_END'} or g['right_separator'] not in {'DEFINITE_SPACE','LINE_START','LINE_END'} for g in gs): return False
    for a,b in zip(gs,gs[1:]):
        if a['locus']==b['locus']:
            if int(b['source_group_index'])!=int(a['source_group_index'])+1 or (a['right_separator'],b['left_separator'])!=('DEFINITE_SPACE','DEFINITE_SPACE'):return False
        elif int(b['locus'].rsplit('.',1)[1])!=int(a['locus'].rsplit('.',1)[1])+1 or (a['right_separator'],b['left_separator'])!=('LINE_END','LINE_START'):return False
    return True

def evaluate(base,cues):
    positions=[[i for i in range(len(base)-len(c)+1) if base[i:i+len(c)]==c] for c in cues]
    reasons=[]
    if len(set(sum(cues,[])))!=5:reasons.append('CUE_WORDS_NOT_DISTINCT')
    if any(len(x)!=1 for x in positions):reasons.append('NO_UNIQUE_BASE_MATCH')
    else:
        starts=[x[0] for x in positions]
        if min(starts)<1:reasons.append('NOT_STRICTLY_INTERNAL')
        if not (starts[0]+2<=starts[1] and starts[1]+1<=starts[2]):reasons.append('NOT_ORDERED_NONOVERLAPPING')
    return positions,reasons

def main():
    if (E/'artifacts/RESULT.json').exists():raise SystemExit('Retained result exists; no overwrite.')
    lock=read(E/'REGISTRATION_LOCK.json')
    for path,h in lock['files'].items():assert sha(R/path)==h,path
    for fixture in read(E/'src/FIXTURES.json'):
        assert bool(evaluate(fixture['base'],fixture['cues'])[1])==fixture['contradicted']
    spec=read(E/'src/SPEC.json');allowed=set(read(R/spec['allow_source'])['allowed_selectors'])
    assert len(allowed)==179 and not any(p.startswith('f84') or p=='f116v' for p in allowed)
    lines={}
    for path in spec['sources']:
        s=read(R/path)
        for row in s['lines']:
            m=row['metadata'];assert m['page'] in allowed and not m['page'].startswith('f84')
            key=m['edition'],m['locus'];assert key not in lines
            lines[key]=[dict(m,**dict(zip(s['group_columns'],g))) for g in row['groups']]
    ps=read(R/spec['paragraph_source']);assert not ps.get('RF1b',[])
    groups={};by=defaultdict(list);lookup={}
    for ed in ('ZL3b','IT2a'):
        for p in ps[ed]:
            assert p['page'] in allowed
            gs=[]
            for ln in p['lines']:
                g=lines[ed,ln['locus']]
                assert [x['ivtff_group_raw'] for x in g]==ln['words']
                assert [x['source_group_id'] for x in g]==ln['source_ids']
                gs+=g
            assert len(gs)==p['groups']
            groups[ed,p['id']]=gs;lookup[ed,p['id']]=p;by[ed,p['page']].append(p)
    cases=[];candidates=[];counts={ed:Counter() for ed in ('ZL3b','IT2a')}
    for (ed,page),pars in sorted(by.items()):
        pars.sort(key=lambda p:p['lines'][0]['row'])
        for ix in range(len(pars)-3):
            w=pars[ix:ix+4];gs=[groups[ed,p['id']] for p in w]
            row={'edition':ed,'page':page,'paragraph_ids':[p['id'] for p in w]}
            adjacent=all(int(b['lines'][0]['locus'].rsplit('.',1)[1])==int(a['lines'][-1]['locus'].rsplit('.',1)[1])+1 for a,b in zip(w,w[1:]))
            if not adjacent:row['status']='GAP_EXCLUDED'
            elif len(gs[0])<2 or any(len(g)<=n for g,n in zip(gs[1:],(2,1,2))):row['status']='TOO_SHORT'
            else:
                selected=[g[-n:] for g,n in zip(gs[1:],(2,1,2))]
                row['cue_words']=[[x['ivtff_group_raw'] for x in g] for g in selected]
                row['cue_source_ids']=[[x['source_group_id'] for x in g] for g in selected]
                if not all(intact(g) for g in [gs[0]]+selected):row['status']='UNRESOLVED'
                else:
                    pos,reasons=evaluate([g['ivtff_group_raw'] for g in gs[0]],row['cue_words'])
                    row.update(base_match_starts=pos,reasons=reasons,status='CONTRADICTED' if reasons else 'FORMAL_CAPACITY_ONLY')
                    if not reasons:candidates.append({'edition':ed,'page':page,'paragraphs':w,'base_match_starts':pos,'cue_words':row['cue_words']})
            cases.append(row);counts[ed][row['status']]+=1
    out={'decision':'FORMAL_CAPACITY_ONLY' if candidates else 'NO_SCORABLE_LOCAL_CUE_TEMPLATE','counts':{ed:dict(c) for ed,c in counts.items()},'paragraph_counts':{ed:len(ps.get(ed,[])) for ed in ('ZL3b','IT2a','RF1b')},'RF1b':'NO_OWN_PARAGRAPH_CAPACITY','cases':cases,'candidate_count':len(candidates),'claim_ceiling':'Necessary textual equations only; no meaning, reference operation, significance or independent confirmation.'}
    for name,obj in [('RESULT.json',out),('CANDIDATES.json',candidates)]: (E/'artifacts'/name).write_text(json.dumps(obj,indent=2)+'\n')
    (E/'artifacts/RUN_RECEIPT.json').write_text(json.dumps({'finished_utc':datetime.now(timezone.utc).isoformat(),'registration_lock_sha256':sha(E/'REGISTRATION_LOCK.json'),'result_sha256':sha(E/'artifacts/RESULT.json')},indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ['decision','counts','paragraph_counts','candidate_count']}))
if __name__=='__main__':main()
