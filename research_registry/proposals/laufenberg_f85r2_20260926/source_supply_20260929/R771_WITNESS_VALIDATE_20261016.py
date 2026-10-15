"""Independent scoped Class/Proposition reconstruction and finite-model check."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def load(name): return json.loads((HERE/name).read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
CLASSES={'ol':['A'],'qol':['B'],'chedy':['P'],'shedy':['Q'],
         'olchedy':['A','P'],'qolchedy':['B','P'],'olshedy':['A','Q']}
OPERATORS={'qokar','tol','daiin'}
def cls(w):
    assert w not in OPERATORS, ('operator cannot supply Class',w)
    return CLASSES.get(w,['N_'+w])

def reconstruct(unit,phase):
    rows=[]
    for line in unit['lines']:
        rows.extend(dict(zip(unit['group_columns'],v)) for v in line['groups'])
    assert [r['source_group_id'] for r in rows]==sorted(
        [r['source_group_id'] for r in rows],key=lambda s:(int(s.split('|')[1].split('.')[1]),int(s.rsplit('G',1)[1])))
    allowed={('ol','chedy'),('qol','chedy'),('ol','shedy')}
    if phase=='PRE': allowed={tuple(reversed(p)) for p in allowed}
    frames=[dict(quantifier='EXISTS',restriction=[],binder_source_ids=[],implicit=True,body=[])]
    events=[]; i=0
    def definite(k):
        return k+1<len(rows) and rows[k]['right_separator']==rows[k+1]['left_separator']=='DEFINITE_SPACE'
    while i<len(rows):
        r=rows[i]; word=r['ivtff_group_raw']; sid=r['source_group_id']
        if word in ('qokar','tol'):
            assert i+1<len(rows) and definite(i)
            frames[-1]['closed_before_source_id']=sid
            f=dict(quantifier='EXISTS' if word=='qokar' else 'ALL',
                   restriction=cls(rows[i+1]['ivtff_group_raw']),
                   binder_source_ids=[sid,rows[i+1]['source_group_id']],implicit=False,body=[])
            frames.append(f); events.append(('BINDER',len(frames)-1,f['binder_source_ids']));i+=2;continue
        assert word!='daiin','orphan marker'
        if definite(i) and (word,rows[i+1]['ivtff_group_raw']) in allowed:
            count=2;kind='LOCAL_EXISTS'
            atoms=list(dict.fromkeys(cls(word)+cls(rows[i+1]['ivtff_group_raw'])))
            explicit=False
        else:
            explicit=definite(i) and rows[i+1]['ivtff_group_raw']=='daiin'
            count=2 if explicit else 1; kind='PREDICATE';atoms=cls(word)
        tokenrows=rows[i:i+count]
        node=dict(kind=kind,predicates=atoms,source_ids=[r['source_group_id'] for r in tokenrows],
                  raw=[r['ivtff_group_raw'] for r in tokenrows])
        if kind=='PREDICATE':node['explicit_daiin']=explicit
        else:node['changes_current']=False
        frames[-1]['body'].append(node)
        events.append((kind,len(frames)-1,node['source_ids']));i+=count
    frames[-1]['closed_at_selected_endpoint']=True
    return rows,frames,events

def main():
    plan=load('R771_WITNESS_PLAN_20261016.json')
    result=load('R771_WITNESS_READING_20261016.json')
    for x in plan['sources']: assert sha(ROOT/x['path'])==x['sha256'],x['path']
    assert result['plan_sha256']==sha(HERE/'R771_WITNESS_PLAN_20261016.json')
    assert result['builder_sha256']==sha(HERE/'R771_WITNESS_BUILD_20261016.py')
    source=load('R_COMPLETE_UNITS.json')
    assert result['source_units']==source['units']
    assert result['source']['sha256']==sha(HERE/'R_COMPLETE_UNITS.json')
    assert result['assumptions']==plan['assumptions']
    assert result['retained_stops']==plan['retained_stops']
    units={u['edition']:u for u in source['units']}
    assert set(units)=={'IT2a','ZL3b','RF1b'}
    assert len(result['cases'])==6
    assert {c['id'] for c in result['cases']}=={p+'_'+e for p in ('POST','PRE') for e in units}
    atoms=set(CLASSES['ol']+CLASSES['qol']+CLASSES['chedy']+CLASSES['shedy'])
    rebuilt={}; local_count=0
    for c in result['cases']:
        unit=units[c['reader']]
        assert c['source_unit']==unit and c['errors']==[]
        rows,frames,events=reconstruct(unit,c['phase']);rebuilt[c['id']]=frames
        assert len(rows)==c['source_group_count']=={'IT2a':77,'ZL3b':75,'RF1b':73}[c['reader']]
        assert len(c['frames'])==len(frames)==(5 if c['reader']=='IT2a' else 4)
        expected_status='ADDITIONAL_WINDOW_ENDPOINT_ASSUMPTION' if c['reader']=='RF1b' else 'SOURCE_FLAGGED_PARAGRAPH_ENDPOINT'
        assert c['endpoint_status']==expected_status
        if c['reader']=='RF1b':
            assert not any(l['metadata']['paragraph_start']=='1' or l['metadata']['paragraph_end']=='1' for l in unit['lines'])
        else:
            assert unit['lines'][0]['metadata']['paragraph_start']=='1'
            assert unit['lines'][-1]['metadata']['paragraph_end']=='1'
        framevars=[f['variable'] for f in c['frames']]
        assert len(set(framevars))==len(framevars)
        localvars=[]; expected_unknown={}
        for r in rows:
            w=r['ivtff_group_raw']
            if w not in CLASSES and w not in OPERATORS:
                expected_unknown.setdefault('N_'+w,[]).append(r['source_group_id']);atoms.add('N_'+w)
        assert c['unknown_atoms']==expected_unknown
        for expected,got in zip(frames,c['frames']):
            for key in ('quantifier','restriction','binder_source_ids','implicit'):
                assert got[key]==expected[key],(c['id'],key)
            assert got.get('closed_before_source_id')==expected.get('closed_before_source_id')
            assert got.get('closed_at_selected_endpoint',False)==expected.get('closed_at_selected_endpoint',False)
            assert len(got['body'])==len(expected['body'])
            for b,a in zip(expected['body'],got['body']):
                assert {k:v for k,v in a.items() if k!='variable'}==b,(c['id'],a,b)
                if a['kind']=='PREDICATE':assert a['variable']==got['variable']
                else:
                    assert a['variable'] not in framevars
                    localvars.append(a['variable']);local_count+=1
        assert len(set(localvars))==len(localvars)
        assert c['events']==[dict(kind=k,frame=c['frames'][f]['id'],source_ids=ids) for k,f,ids in events]
        flattened=[sid for _,_,ids in events for sid in ids]
        assert flattened==[r['source_group_id'] for r in rows]
        all_ap=[(f,g) for f,g in zip(frames,c['frames']) if f['quantifier']=='ALL' and set(f['restriction'])=={'A','P'}]
        sites=[b['source_ids'] for f,_ in all_ap for b in f['body'] if b['kind']=='PREDICATE' and 'Q' in b['predicates']]
        localsites=[b['source_ids'] for f,_ in all_ap for b in f['body'] if b['kind']=='LOCAL_EXISTS' and {'A','Q'}<=set(b['predicates'])]
        nonempty=[g['id'] for f,g in zip(frames,c['frames']) if f['quantifier']=='EXISTS' and {'A','P'}<=set(f['restriction'])]
        assert c['scope_consequences']==dict(AP_subset_Q_direct_body=bool(sites),source_sites=sites,
            AP_nonempty_explicit_frames=nonempty,local_AQ_exists_under_ALL_sites=localsites,
            AQ_nonempty_from_AP_and_local_exists=bool(nonempty and localsites))
        assert c['native_truth']=='UNASSIGNED_PREDICATE_INTERPRETATIONS'
    worlds={}
    for name in ('UNIVERSAL','SELECTIVE_Q','RF_TAIL','EMPTY_AP'):
        predicates={a:['a','b'] for a in atoms}
        if name=='SELECTIVE_Q':predicates['Q']=['b']
        if name=='RF_TAIL':predicates.update(A=['b'],Q=['b'],N_otar=['a'])
        if name=='EMPTY_AP':predicates['A']=[]
        worlds[name]=dict(domain=['a','b'],predicates=predicates)
    assert result['toy_worlds']==worlds
    assert result['toy_status']=='COMPLETE_FINITE_INTERPRETATIONS_NOT_NATIVE_VALUES'
    truths={}
    for c in result['cases']:
        for name,world in worlds.items():
            domain=set(world['domain']); ext={a:set(v) for a,v in world['predicates'].items()}
            def extension(names):
                value=domain.copy()
                for atom in names:value &= ext[atom]
                return value
            frame_results=[]
            for f,g in zip(rebuilt[c['id']],c['frames']):
                restriction=extension(f['restriction']); tests=[]
                for node in f['body']:
                    val=extension(node['predicates'])
                    tests.append(domain.copy() if node['kind']=='LOCAL_EXISTS' and val else
                                 set() if node['kind']=='LOCAL_EXISTS' else val)
                body=domain.copy()
                for val in tests: body &= val
                truth=bool(restriction & body) if f['quantifier']=='EXISTS' else restriction<=body
                rr=[dict(entity=x,restriction=x in restriction,body_terms=[x in t for t in tests],body=x in body) for x in world['domain']]
                frame_results.append(dict(frame=g['id'],quantifier=f['quantifier'],rows=rr,truth=truth))
            stored=c['toy_results'][name]
            assert stored['frames']==frame_results
            overall=all(f['truth'] for f in frame_results)
            assert stored['complete_truth']==overall
            truths.setdefault(name,{})[c['id']]=overall
    assert all(truths['UNIVERSAL'].values()) and not any(truths['EMPTY_AP'].values())
    assert [k for k,v in truths['SELECTIVE_Q'].items() if v]==['POST_IT2a']
    assert {k for k,v in truths['RF_TAIL'].items() if v}=={'POST_RF1b','PRE_RF1b'}
    assert result['summary']==dict(source_reader_groups=225,model_cases=6,physical_manuscript_paragraphs=1,
        parsed_model_positions=450,parser_errors=0,confirmed_words=0)
    return dict(status='PASS',source_groups=225,model_positions=450,cases=6,toy_worlds=4,
        finite_case_evaluations=24,local_existential_nodes=local_count,toy_truths=truths,
        semantic_or_native_confirmation=False,
        scope='Source, whole-phase typed reconstruction and exact finite truth tables only. RF remains a window with assumed endpoint.')

if __name__=='__main__':
    r=main()
    r['hashes']={n:sha(HERE/n) for n in ('R771_WITNESS_PLAN_20261016.json','R771_WITNESS_READING_20261016.json','R771_WITNESS_VALIDATE_20261016.py')}
    (HERE/'R771_WITNESS_VALIDATION_20261016.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,sort_keys=True))
