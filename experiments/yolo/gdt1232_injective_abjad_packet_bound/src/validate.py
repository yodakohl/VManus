#!/usr/bin/env python3
"""Separate source reconstruction and set-arithmetic proof replay; no Z3 import."""
from pathlib import Path
from collections import Counter,defaultdict
from datetime import datetime,timezone
from itertools import product
import hashlib,json,re,time
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
def read(p):return json.loads(p.read_text())
def save(n,x):(A/n).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def tokenize(raw,alphabet):
    if not raw or any(not('a'<=c<='z') for c in raw):return []
    found=[]
    def walk(pos,parts):
        if pos==len(raw):found.append(parts);return
        for symbol in alphabet:
            if raw[pos:pos+len(symbol)]==symbol:walk(pos+len(symbol),parts+[symbol])
    walk(0,[]);return found

def reconstruct(packet,spec):
    words=defaultdict(lambda:defaultdict(list));rejected=defaultdict(Counter);ids=set();raw_count=0
    for line in packet['lines']:
        assert line['page'] not in ['f84','f84r','f116v'];assert len(line['groups'])==line['groups'][0]['source_group_count']
        for row in line['groups']:
            assert row['edition']==line['edition'] and row['locus']==line['locus'];assert row['source_group_id'] not in ids;ids.add(row['source_group_id']);raw_count+=1
            raw=row['ivtff_group_raw'];paths=tokenize(raw,spec['inventory']);ed=row['edition']
            if row['kind']!='P':why='NON_PROSE'
            elif (row['left_separator'],row['right_separator'])!=('DEFINITE_SPACE','DEFINITE_SPACE'):why='NOT_STRICT_INTERIOR'
            elif len(paths)!=1:why='NONLITERAL_OR_NONUNIQUE_PARSE'
            else:why=None
            if why:rejected[ed][why]+=1
            else:words[ed][raw].append({**row,'units':paths[0]})
    assert raw_count==297 and len(packet['lines'])==36
    return {ed:{'forms':[{'form':w,'counts':dict(sorted(Counter(rows[0]['units']).items())),'occurrences':rows} for w,rows in sorted(words[ed].items())],'excluded':dict(rejected[ed])} for ed in spec['readers']}

def support(constraint,variable,domains,targets):
    # Explicit integer sets, unlike the runner's bit-vector convolution.
    other={0};cap=max(targets)
    for name,co in constraint.items():
        if name==variable:continue
        other={old+co*x for old in other for x in domains[name] if old+co*x<=cap}
    return [x for x in domains[variable] if any(t-constraint[variable]*x in other for t in targets)]

def replay(constraints,values,targets,certificate):
    variables=sorted(set().union(*(set(c) for c in constraints)));nodes=0;steps=0
    def visit(node,parent):
        nonlocal nodes,steps
        nodes+=1;domains={k:list(v) for k,v in parent.items()}
        for change in node['reductions']:
            v=change['variable'];keep=change['keep']
            if 'different_from' in change:
                u=change['different_from'];assert u!=v and len(domains[u])==1
                expected=[x for x in domains[v] if x not in domains[u]]
            else:
                i=change['constraint'];assert 0<=i<len(constraints) and v in constraints[i]
                expected=support(constraints[i],v,domains,targets)
            assert keep==expected,(change,expected);assert keep!=domains[v]
            domains[v]=keep;steps+=1
        if 'empty_variable' in node:
            assert domains[node['empty_variable']]==[];assert 'children' not in node;return
        assert all(domains.values());v=node['branch_variable'];assert len(domains[v])>1
        assert [c['value'] for c in node['children']]==domains[v]
        for child in node['children']:
            ds={k:list(x) for k,x in domains.items()};ds[v]=[child['value']];visit(child['node'],ds)
    visit(certificate,{v:list(values) for v in variables});return {'nodes':nodes,'support_reductions':steps}

def brute(cs,values,targets):
    names=sorted(set().union(*(set(c) for c in cs)))
    for vals in product(values,repeat=len(names)):
        w=dict(zip(names,vals))
        if len(set(vals))!=len(vals):continue
        if all(sum(w[v]*n for v,n in c.items()) in targets for c in cs):return True
    return False

def main():
    started=datetime.now(timezone.utc).isoformat();spec=read(D/'src/SPEC.json');lock=read(A/'REGISTRATION_LOCK.json')
    for p,h in lock['files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    assert set(spec['values'])==set(range(1,10))|set(range(10,100,10))|set(range(100,1000,100))|{1000}
    assert len(spec['inventory'])==22 and len(set(spec['inventory']))==22
    source=read(A/'HISTORICAL_SOURCE_REVIEW.json');assert list(source['values_by_letter'].values())==spec['values']
    for f in read(A/'FIXTURES.json'):
        good=brute(f['constraints'],f['values'],f['targets']);assert good==(f['status']=='SAT')
        if not good:replay(f['constraints'],f['values'],f['targets'],f['certificate'])
        else:
            assert len(set(f['witness'].values()))==len(f['witness'])
            assert all(sum(f['witness'][v]*n for v,n in c.items()) in f['targets'] for c in f['constraints'])
    packet=read(ROOT/spec['packet']);selection=reconstruct(packet,spec);assert selection==read(A/'SELECTED_GROUPS.json');assert selection==read(ROOT/'experiments/yolo/gdt1231_additive_abjad_packet_bound/artifacts/SELECTED_GROUPS.json')
    results=read(A/'RESULT.json');decisions=[]
    for record in results['readers']:
        ed=record['reader'];forms=selection[ed]['forms'];assert record['types']==len(forms) and record['tokens']==sum(len(f['occurrences']) for f in forms);assert record['excluded']==selection[ed]['excluded']
        if record['solver']['status']=='SAT':
            w=record['solver']['witness'];assert len(set(w.values()))==len(w);assert all(x in spec['values'] for x in w.values());assert all(sum(w[v]*n for v,n in f['counts'].items()) in spec['values'] for f in forms)
            decision={'reader':ed,'decision':'NECESSARY_INJECTIVE_ARITHMETIC_CAPACITY_ONLY','witness_verified':True}
        elif record['decision']=='CERTIFICATE_READY_FOR_REPLAY':
            cert=read(A/f'CERTIFICATE_{ed}.json');idx=cert['core_indices'];assert idx==record['solver']['core_indices'];assert len(set(idx))==len(idx);assert cert['status']=='UNSAT';cs=[forms[i]['counts'] for i in idx];assert cs==cert['constraints']
            receipt=replay(cs,spec['values'],spec['values'],cert['certificate']);assert receipt['nodes']==cert['nodes'];decision={'reader':ed,'decision':'INJECTIVE_ADDITIVE_PACKET_CLASS_EXCLUDED',**receipt,'core_forms':[forms[i]['form'] for i in idx],'core_occurrences':{forms[i]['form']:[r['source_group_id'] for r in forms[i]['occurrences']] for i in idx}}
        else:decision={'reader':ed,'decision':'INCONCLUSIVE_NO_CERTIFIED_RESULT'}
        decisions.append(decision)
    all_excluded=all(x['decision']=='INJECTIVE_ADDITIVE_PACKET_CLASS_EXCLUDED' for x in decisions)
    status='INJECTIVE_ADDITIVE_PACKETS_EXCLUDED_ALL_READINGS' if all_excluded else 'READER_SPECIFIC_RESULTS'
    save('VALIDATION.json',{'status':'PASS','scientific_status':status,'readers':decisions,'source_groups_checked':297,'new_native_queries':0,'fixtures':'All5 compared with complete independent brute force and distinctness;3 negative certificates replayed.','independence':'Separate implementation by same root; no separate researcher or transcription independence. Validator imports neither runner nor Z3. Exact set support independently replays each domain reduction and exhaustive branch.','started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'claim_ceiling':spec['claim_ceiling']})
    print(json.dumps({'status':'PASS','scientific_status':status,'readers':decisions},indent=2))
if __name__=='__main__':main()
