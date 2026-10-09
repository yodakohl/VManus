#!/usr/bin/env python3
"""Independent original-source and finite certificate replay; no search import."""
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
import json,csv,io,re,hashlib,gzip,subprocess
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'

def sha(data):return hashlib.sha256(data).hexdigest()
def load(name):
    b=(A/name).read_bytes()
    return json.loads(gzip.decompress(b)if name.endswith('.gz')else b)

def replay(tree, words, alphabet):
    ordered=[(i,list(w))for i,w in words]
    tally=Counter()
    def scan(table):
        left={};used=set();bad=None
        for identifier,original in ordered:
            rest=original.copy()
            while rest:
                g=rest[0]
                if g not in table:
                    left.setdefault(g,[]).append(tuple(rest));break
                c=list(table[g]);position=len(original)-len(rest)
                if rest[:len(c)]!=c:
                    bad={'word_id':identifier,'offset':position,'head':g,'code':c,'remainder':rest}
                    return left,used,bad
                used.add(g);del rest[:len(c)]
        return left,used,bad
    def visit(node,table):
        tally['nodes']+=1;tally['max_depth']=max(tally['max_depth'],len(table))
        kind=node['kind']
        if kind=='timeout':return 'UNKNOWN'
        left,used,bad=scan(table)
        if kind=='conflict':
            assert bad is not None
            assert all(node[k]==v for k,v in bad.items())
            tally['contradictions']+=1
            return 'NEGATIVE'
        assert bad is None
        if kind in ['identity_only','positive']:
            assert not left and sorted(used)==node['used_heads']
            longer=sorted(g for g in used if len(table[g])>1)
            if kind=='positive':
                assert longer and longer==node['longer_used_heads'];tally['positive_leaves']+=1
                return 'NONTRIVIAL'
            assert not longer;tally['identity_leaves']+=1
            return 'NEGATIVE'
        assert kind=='branch'and left
        domains={}
        for g,remainders in left.items():
            common=None
            for rest in remainders:
                possible={rest[:i]for i in range(1,len(rest)+1)}
                common=possible if common is None else common & possible
            assert common
            domains[g]=sorted(common,key=lambda c:-len(c))
        chosen=min(domains,key=lambda g:(len(domains[g]),alphabet.index(g)))
        assert node['head']==chosen and node['options']==[list(c)for c in domains[chosen]]
        children=node['children'];assert 0<len(children)<=len(domains[chosen])
        outcome='NEGATIVE'
        for i,child in enumerate(children):
            code=domains[chosen][i];assert child['code']==list(code)
            updated={**table,chosen:code};outcome=visit(child['node'],updated)
            if outcome!='NEGATIVE':assert i==len(children)-1
        if outcome=='NEGATIVE':assert len(children)==len(domains[chosen])
        assert node['search_status']==outcome
        return outcome
    state=visit(tree,{})
    stats={k:tally[k]for k in ['nodes','contradictions','identity_leaves','positive_leaves','max_depth']}
    return ('ALL_USED_CODES_SINGLETON'if state=='NEGATIVE'else state),stats

def main():
    started=datetime.now(timezone.utc).isoformat();spec=json.loads((D/'src/SPEC.json').read_text());result=load('RESULT.json');saved=load('GROUPS.json.gz')
    for p,h in load('REGISTRATION_LOCK.json')['files'].items():assert sha((ROOT/p).read_bytes())==h,p
    allowed=json.loads((ROOT/spec['scope_spec']).read_text())['allowed'];assert len(allowed)==179
    assert not any(x.startswith('f84')or x=='f116v'for x in allowed)
    args=['./vmanus-exp','query-tsv',spec['source'],'--selector','page']
    for p in allowed:args.extend(['--allow',p])
    args+=['--columns','edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator']
    response=subprocess.run(args,cwd=ROOT,text=True,capture_output=True,check=True)
    assert sha(response.stdout.encode())==load('RUN_RECEIPT.json')['guard_output_sha256']
    atom=re.compile('|'.join(re.escape(g)for g in sorted(spec['signs'],key=lambda x:(-len(x),x))))
    reconstructed={ed:[]for ed in ['IT2a','RF1b','ZL3b']};counter={ed:Counter()for ed in reconstructed};seen=set()
    for row in csv.DictReader(io.StringIO(response.stdout),delimiter='\t'):
        ed=row['edition'];c=counter[ed];identifier='{}|{}|G{:03}'.format(ed,row['locus'],int(row['source_group_index']))
        assert identifier not in seen;seen.add(identifier);c['raw']+=1
        if row['kind']!='P':c['non_prose']+=1;continue
        if (row['left_separator'],row['right_separator'])!=('DEFINITE_SPACE','DEFINITE_SPACE'):c['non_interior']+=1;continue
        raw=row['ivtff_group_raw']
        if not raw or any(not('a'<=ch<='z')for ch in raw):c['non_literal']+=1;continue
        parts=atom.findall(raw)
        if ''.join(parts)!=raw:c['non_unique_parse']+=1;continue
        row.update(id=identifier,units=parts);reconstructed[ed].append(row);c['eligible']+=1
    assert reconstructed==saved
    fixtures=load('FIXTURES.json');assert fixtures['status']=='PASS'and fixtures['native_data_read']is False
    fixture_results={}
    for key,strings in [('positive',['ab','abab','bb']),('parity',['aa','aaa','b'])]:
        rec=fixtures['named'][key];st,stats=replay(rec['certificate'],[(str(i),tuple(w))for i,w in enumerate(strings)],list('ab'))
        assert st==rec['status']and stats==rec['statistics'];fixture_results[key]=st
    summaries={}
    for ed,rows in reconstructed.items():
        r=result['readings'][ed];by_form={}
        for row in rows:by_form.setdefault(row['ivtff_group_raw'],row)
        types=[by_form[k]for k in sorted(by_form)];words=[(row['id'],tuple(row['units']))for row in types]
        assert dict(counter[ed])==r['counts']and len(types)==r['types']
        assert sum(len(x['units'])for x in rows)==r['glyph_tokens']
        assert sorted({g for x in rows for g in x['units']})==r['alphabet_present']
        assert sha('\n'.join(x['id']for x in rows).encode())==r['eligible_ids_sha256']
        assert sha('\n'.join(x['id']for x in types).encode())==r['type_order_ids_sha256']
        state,stats=replay(load(f'CERTIFICATE_{ed}.json.gz'),words,spec['signs'])
        assert state==r['status']and stats==r['statistics']
        if state=='NONTRIVIAL':
            table=r['witness'];assert set(table)==set(spec['signs']);used=set()
            for g,c in table.items():assert c and c[0]==g and set(c)<=set(spec['signs'])
            for _,word in words:
                remaining=list(word)
                while remaining:
                    g=remaining[0];code=table[g];assert remaining[:len(code)]==code
                    del remaining[:len(code)];used.add(g)
            assert any(len(table[g])>1 for g in used)
        else:assert r['witness']is None
        summaries[ed]={'status':state,'eligible_groups':len(rows),'types':len(types),'proof':stats}
    expected='ALL_USED_CODES_SINGLETON_ALL_READINGS'if all(r['status']=='ALL_USED_CODES_SINGLETON'for r in summaries.values())else'READER_SPECIFIC_CODE_CAPACITY'
    assert expected==result['status']
    out={'status':'PASS','started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'readings':summaries,'fixtures_replayed':fixture_results,'source_rows':len(seen),'source_and_selection_reconstructed':True,'imports_search_or_runner':False,'scope':'Independent implementation by same root; original guarded rows, every saved branch and exclusion or entire positive witness. No independent semantic or palaeographic validation.'}
    (A/'VALIDATION.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
