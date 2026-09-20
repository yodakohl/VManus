import argparse,collections,hashlib,itertools,json,string
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def reference(ctx,c):
    endings=['aiin','ain'] if c[0]=='F' else ['ain','aiin'];checks=[];roots=[]
    for text,end in zip([ctx[0],ctx[2]],endings):
        if text is None:checks.append(False);roots.append(None)
        elif not text or any(x not in string.ascii_lowercase for x in text):checks.append(None);roots.append(None)
        else:
            valid=text.endswith(end) and len(text)>len(end);checks.append(valid);roots.append(text[:-len(end)] if valid else None)
    p=ctx[3];checks.append(None if p is not None and (not p or any(x not in string.ascii_lowercase for x in p)) else p=='cheedy')
    if c.split('_')[1]=='same':
        if checks[0] is False or checks[1] is False:checks.append(False)
        elif checks[0] is None or checks[1] is None:checks.append(None)
        else:checks.append(roots[0]==roots[1])
    return dict(status='CONTRADICTS' if any(x is False for x in checks) else 'UNKNOWN' if any(x is None for x in checks) else 'MATCH',checks=checks,roots=roots)
def preflight():
    from run import check_context
    examples=[('qokaiin','qokain','cheedy','F_same','MATCH'),('qokaiin','otain','cheedy','F_same','CONTRADICTS'),('qokaiin','otain','cheedy','F_any','MATCH'),('qokain','qokaiin','cheedy','R_same','MATCH'),('aiin','ain','cheedy','F_any','CONTRADICTS'),('qokaiin','qokain','chedy','F_same','CONTRADICTS'),(None,'qokain','cheedy','F_same','CONTRADICTS'),('qokaiin','qok[?:a]in','cheedy','F_same','UNKNOWN'),('qokaiin','qok[?:a]in','chedy','F_same','CONTRADICTS')]
    for l,r,p,c,status in examples:assert reference([l,'ykar',r,p],c)['status']==status
    n=0
    for l,r,p in itertools.product(['qokaiin','qokain','otaiin','otain','aiin','ain','[a:b]',None],['qokaiin','qokain','otaiin','otain','aiin','ain','[a:b]',None],['cheedy','chedy','[a:b]',None]):
        for c in ['F_same','F_any','R_same','R_any']:
            assert check_context([l,'ykar',r,p],c)==reference([l,'ykar',r,p],c);n+=1
    return dict(status='PASS',synthetic_cases=n,hand_specified_cases=len(examples),target_loaded=False)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--preflight',action='store_true');args=ap.parse_args()
    if args.preflight:x=preflight();write(A/'PREFLIGHT.json',x);print(json.dumps(x));return
    for path,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/path).read_bytes()).hexdigest()==h
    spec=read(E/'src/SPEC.json');src=read(R/spec['input']);actual=read(A/'CASES.json');coverage=read(A/'COVERAGE.json');matches=read(A/'MATCHING_PARAGRAPHS.json');result=read(A/'RESULT.json')
    expected=[];cov=[];full=[]
    for ed,ps in src.items():
        for p in ps:
            words=[];ids=[];lines=[]
            for ln,line in enumerate(p['lines']):words+=line['words'];ids+=line['source_ids'];lines+=[ln]*len(line['words'])
            assert len(words)==len(ids)==p['groups'];assert not p['page'].startswith('f84') and p['page']!='f116v'
            pid=ed+'|'+p['id'];part='SEED_PARAGRAPH' if p['id']=='f106r|f106r.42-f106r.47' else 'SAME_PHYSICAL_LEAF' if p['leaf']==106 else 'OTHER_EXPOSED_LEAF'
            pos=[i for i in range(len(words)) if words[i]=='ykar'];cov.append(dict(id=pid,groups=len(words),ykar_positions=[i+1 for i in pos],partition=part,page=p['page'],leaf=p['leaf']))
            for i in pos:
                js=list(range(i-1,i+3));context=[words[j] if 0<=j<len(words) else None for j in js]
                row=dict(id=pid+'|'+str(i+1),paragraph=pid,edition=ed,page=p['page'],leaf=p['leaf'],partition=part,position=i+1,context=context,source_ids=[ids[j] if 0<=j<len(ids) else None for j in js],cross_line=len(set(lines[j] for j in js if 0<=j<len(lines)))>1,candidates={c:reference(context,c) for c in spec['candidates']})
                expected.append(row)
                if any(x['status']=='MATCH' for x in row['candidates'].values()):full.append(dict(case=row['id'],edition=ed,paragraph=p,interpreted_group_positions=[j+1 for j in js],uninterpreted_groups=len(words)-4))
    assert actual==expected and cov==coverage and full==matches
    assert len(cov)==1349 and len(expected)==result['ykar_cases'];assert result['paragraphs']==1349
    for c in spec['candidates']:
        z=result['candidates'][c];good=[r for r in expected if r['candidates'][c]['status']=='MATCH'];cts=dict(collections.Counter(r['candidates'][c]['status'] for r in expected))
        assert z['counts']==cts and z['matches']==[r['id'] for r in good]
        assert z['roots']==[list(x) for x in sorted(set(tuple(r['candidates'][c]['roots']) for r in good))]
        assert z['physical_leaves']==sorted(set(r['leaf'] for r in good))
        assert z['global_writer']==('CONTRADICTED' if cts.get('CONTRADICTS') else 'UNKNOWN' if cts.get('UNKNOWN') or not expected else 'ALL_OBSERVED_MATCH')
        assert z['transfer']==('EXPOSED_OTHER_LEAF_CAPACITY' if any(r['partition']=='OTHER_EXPOSED_LEAF' for r in good) else 'NO_OTHER_LEAF_MATCH')
        for ed in src:assert z['by_reader'][ed]==dict(collections.Counter(r['candidates'][c]['status'] for r in expected if r['edition']==ed))
        for part in z['by_partition']:assert z['by_partition'][part]==dict(collections.Counter(r['candidates'][c]['status'] for r in expected if r['partition']==part))
    assert result['semantic_equivalence']==spec['semantic_equivalence'] and result['confirmed_words']==result['independent_meaning_capacity']==0
    x=dict(status='PASS',paragraphs=len(cov),ykar_cases=len(expected),candidate_decisions=4*len(expected),whole_matching_paragraph_records=len(full),scope='complete literal-ykar census and independent candidate checks; no meaning validation');write(A/'VALIDATION.json',x);print(json.dumps(x))
if __name__=='__main__':main()
