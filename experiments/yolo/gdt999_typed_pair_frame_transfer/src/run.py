import collections,csv,datetime,hashlib,json,re,subprocess
from pathlib import Path
E=Path(__file__).resolve().parents[1];R=E.parents[2];A=E/'artifacts'
def read(p):return json.loads(p.read_text())
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def check_context(context,candidate):
    left,bridge,right,predicate=context
    ends=('ain','aiin') if candidate.startswith('R') else ('aiin','ain')
    checks=[];roots=[]
    for token,end in zip((left,right),ends):
        if token is None:checks.append(False);roots.append(None)
        elif not re.fullmatch('[a-z]+',token):checks.append(None);roots.append(None)
        else:
            m=re.fullmatch('([a-z]+)'+end,token);checks.append(bool(m));roots.append(m[1] if m else None)
    checks.append(None if predicate is not None and not re.fullmatch('[a-z]+',predicate) else predicate=='cheedy')
    if candidate.endswith('same'):checks.append(roots[0]==roots[1] if all(x is not None for x in roots) else (False if False in checks[:2] else None))
    status='CONTRADICTS' if False in checks else 'UNKNOWN' if None in checks else 'MATCH'
    return dict(status=status,checks=checks,roots=roots)
def main():
    for p,h in read(E/'PREREG_LOCK.json')['files'].items():assert hashlib.sha256((R/p).read_bytes()).hexdigest()==h,p
    receipt=read(A/'PUBLIC_REGISTRATION.json');assert subprocess.run(['git','cat-file','-e',receipt['commit']+'^{commit}'],cwd=R).returncode==0
    spec=read(E/'src/SPEC.json');src=read(R/spec['input']);started=datetime.datetime.now(datetime.timezone.utc).isoformat()
    rows=[];coverage=[];matched=[]
    for ed,ps in src.items():
        for p in ps:
            assert not p['page'].startswith('f84') and p['page']!='f116v'
            ws=[w for line in p['lines'] for w in line['words']];ids=[x for line in p['lines'] for x in line['source_ids']]
            ls=[i for i,line in enumerate(p['lines']) for _ in line['words']]
            assert len(ws)==len(ids)==p['groups']
            part='SEED_PARAGRAPH' if p['id']=='f106r|f106r.42-f106r.47' else 'SAME_PHYSICAL_LEAF' if p['leaf']==106 else 'OTHER_EXPOSED_LEAF'
            pid=ed+'|'+p['id'];positions=[i for i,w in enumerate(ws) if w=='ykar'];coverage.append(dict(id=pid,groups=len(ws),ykar_positions=[i+1 for i in positions],partition=part,page=p['page'],leaf=p['leaf']))
            for i in positions:
                inds=[i-1,i,i+1,i+2];ctx=[ws[j] if 0<=j<len(ws) else None for j in inds]
                row=dict(id=pid+'|'+str(i+1),paragraph=pid,edition=ed,page=p['page'],leaf=p['leaf'],partition=part,position=i+1,context=ctx,source_ids=[ids[j] if 0<=j<len(ids) else None for j in inds],cross_line=len({ls[j] for j in inds if 0<=j<len(ls)})>1,candidates={c:check_context(ctx,c) for c in spec['candidates']})
                rows.append(row)
                if any(v['status']=='MATCH' for v in row['candidates'].values()):matched.append(dict(case=row['id'],edition=ed,paragraph=p,interpreted_group_positions=[j+1 for j in inds],uninterpreted_groups=len(ws)-4))
    assert {ed:len(ps) for ed,ps in src.items()}==spec['paragraph_counts']
    result=dict(status='COMPLETE_FIXED_FRAME_CENSUS',started_utc=started,completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),registration_commit=receipt['commit'],paragraphs=len(coverage),ykar_cases=len(rows),candidates={},independent_meaning_capacity=0,confirmed_words=0,semantic_equivalence=spec['semantic_equivalence'])
    for c in spec['candidates']:
        counts=dict(collections.Counter(r['candidates'][c]['status'] for r in rows));matches=[r for r in rows if r['candidates'][c]['status']=='MATCH'];other=[r for r in matches if r['partition']=='OTHER_EXPOSED_LEAF']
        result['candidates'][c]=dict(counts=counts,by_reader={ed:dict(collections.Counter(r['candidates'][c]['status'] for r in rows if r['edition']==ed)) for ed in src},by_partition={k:dict(collections.Counter(r['candidates'][c]['status'] for r in rows if r['partition']==k)) for k in ['SEED_PARAGRAPH','SAME_PHYSICAL_LEAF','OTHER_EXPOSED_LEAF']},matches=[r['id'] for r in matches],roots=sorted({tuple(r['candidates'][c]['roots']) for r in matches}),physical_leaves=sorted({r['leaf'] for r in matches}),global_writer='CONTRADICTED' if counts.get('CONTRADICTS') else 'UNKNOWN' if counts.get('UNKNOWN') or not rows else 'ALL_OBSERVED_MATCH',transfer='EXPOSED_OTHER_LEAF_CAPACITY' if other else 'NO_OTHER_LEAF_MATCH',independent_meaning_capacity=0)
    write(A/'CASES.json',rows);write(A/'COVERAGE.json',coverage);write(A/'MATCHING_PARAGRAPHS.json',matched);write(A/'RESULT.json',result)
    with (A/'CANDIDATES.tsv').open('w',newline='') as f:
        fields=['id','partition','leaf','candidate','left','bridge','right','predicate','status','roots'];w=csv.DictWriter(f,fields,delimiter='\t',lineterminator='\n');w.writeheader()
        for row in rows:
            for c,v in row['candidates'].items():w.writerow(dict(id=row['id'],partition=row['partition'],leaf=row['leaf'],candidate=c,**dict(zip(['left','bridge','right','predicate'],row['context'])),status=v['status'],roots=json.dumps(v['roots'])))
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
