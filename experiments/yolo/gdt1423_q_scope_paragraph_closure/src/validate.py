#!/usr/bin/env python3
"""Independent interval-cut reconstruction. No primary or legacy code imports."""
import csv,hashlib,io,json,subprocess
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def reconstruct(rows):
    keyed=defaultdict(list)
    for r in rows:keyed[(r['edition'],r['page'],r['locus'])].append(r)
    pages=defaultdict(list)
    for (ed,page,loc),rr in keyed.items():
        rr=sorted(rr,key=lambda r:int(r['source_group_index']))
        n=len(rr);assert [int(r['source_group_index']) for r in rr]==list(range(1,n+1))
        for key in ['source_row_index','source_group_count','kind','paragraph_start','paragraph_end']:
            assert len({r[key] for r in rr})==1,(ed,page,loc,key)
        assert int(rr[0]['source_group_count'])==n
        pages[(ed,page)].append(rr)
    blocks=[]
    for (ed,page),lines in sorted(pages.items()):
        lines.sort(key=lambda rr:int(rr[0]['source_row_index']))
        assert len({rr[0]['source_row_index'] for rr in lines})==len(lines)
        cuts={0,len(lines)}
        for i,rr in enumerate(lines):
            r=rr[0]
            if r['kind']!='P':cuts.update([i,i+1])
            if r['paragraph_start']=='1':cuts.add(i)
            if r['paragraph_end']=='1':cuts.add(i+1)
        ordered=sorted(cuts)
        for lo,hi in zip(ordered,ordered[1:]):
            part=lines[lo:hi]
            if not part or part[0][0]['kind']!='P':continue
            assert all(rr[0]['kind']=='P' for rr in part)
            gs=[g for rr in part for g in rr];start=part[0][0]['paragraph_start']=='1';end=part[-1][0]['paragraph_end']=='1'
            tier='primary' if start and end else 'right_only' if end else 'unknown_end'
            j=len(gs)
            while j and gs[j-1]['ivtff_group_raw'].startswith('q'):j-=1
            blocks.append({'edition':ed,'page':page,'loci':[rr[0]['locus'] for rr in part],'start':start,'end':end,'tier':tier,'groups':gs,'terminal_q_run':gs[j:],'empty_q_ids':[g['source_group_id'] for g in gs if g['ivtff_group_raw']=='q']})
    return blocks

def fixture(ed,page,li,words,start=0,end=0,kind='P'):
    return [dict(source_group_id=f'{ed}|{page}.{li}|G{i:03d}',edition=ed,page=page,locus=f'{page}.{li}',source_row_index=str(li),source_group_index=str(i),source_group_count=str(len(words)),kind=kind,paragraph_start=str(start),paragraph_end=str(end),left_separator='LINE_START' if i==1 else 'DEFINITE_SPACE',right_separator='LINE_END' if i==len(words) else 'DEFINITE_SPACE',ivtff_group_raw=w) for i,w in enumerate(words,1)]
def controls():
    checks=0
    for words,tail in [(['a','qfoo'],1),(['qfoo','a'],0),(['a','qfoo','qbar'],2),(['q'],1),(['a','q@152;'],1),(['a','@152;q'],0)]:
        b=reconstruct(fixture('IT','f2r',1,words,1,1));assert len(b)==1 and b[0]['tier']=='primary' and len(b[0]['terminal_q_run'])==tail;checks+=1
    b=reconstruct(fixture('IT','f2r',1,['qfoo'],1)+fixture('IT','f2r',2,['a'],0,1));assert len(b)==1 and not b[0]['terminal_q_run'];checks+=1
    b=reconstruct(fixture('IT','f2r',1,['qfoo'],1)+fixture('IT','f2r',2,['x'],kind='L')+fixture('IT','f2r',3,['qbar'],0,1));assert [z['tier'] for z in b]==['unknown_end','right_only'];checks+=1
    b=reconstruct(fixture('IT','f2r',1,['qfoo'],1)+fixture('IT','f2r',2,['a'],1,1));assert [z['tier'] for z in b]==['unknown_end','primary'];checks+=1
    b=reconstruct(fixture('IT','f2r',1,['qfoo'],1)+fixture('IT','f3r',1,['qbar'],0,1)+fixture('RF','f2r',1,['qfoo'],0,0));assert len(b)==3 and sum(z['tier']=='primary' for z in b)==0;checks+=1
    bad=fixture('IT','f2r',1,['a','qfoo'],1,1);bad[-1]['paragraph_end']='0'
    try:reconstruct(bad)
    except AssertionError:checks+=1
    else:raise AssertionError('inconsistent whole-line flags accepted')
    assert reconstruct([])==[];checks+=1
    return checks

def source(spec):
    ss=spec['source'];p=ROOT/ss['cache'];assert sha(ROOT/ss['allowlist'])==ss['allowlist_sha256']
    if p.exists():
        assert sha(p)==ss['cache_sha256'];payload=p.read_text()
    else:
        assert sha(ROOT/ss['path'])==ss['sha256']
        with (ROOT/ss['allowlist']).open() as f:allowed=[r['page'] for r in csv.DictReader(f,delimiter='\t')]
        assert len(allowed)==ss['selector_count'] and not any(v.startswith('f84') or v=='f116v' for v in allowed)
        cmd=['./vmanus-exp','query-tsv',ss['path'],'--selector','page']
        for page in allowed:cmd+=['--allow',page]
        cmd+=['--columns',','.join(ss['columns'])]
        cp=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True);payload=cp.stdout
        assert hashlib.sha256(payload.encode()).hexdigest()==ss['cache_sha256']
    rows=list(csv.DictReader(io.StringIO(payload),delimiter='\t'))
    assert len(rows)==ss['selected_rows'];assert not any(r['page'].startswith('f84') or r['page']=='f116v' for r in rows)
    return rows

def main():
    n=controls();spec=json.loads((HERE/'src/SPEC.json').read_text());result_path=HERE/'artifacts/RESULT.json'
    assert result_path.exists(),'Await primary result; do not create validation yet'
    rows=source(spec);blocks=reconstruct(rows);result=json.loads(result_path.read_text())
    # Schema adapter is supplied only after the independent reconstruction is authored.
    verify_result(result,blocks,rows)
    out={'status':'PASS_INDEPENDENT_SOURCE_AND_BOUNDARY_RECONSTRUCTION','validator_sha256':sha(Path(__file__)),'result_sha256':sha(result_path),'spec_sha256':sha(HERE/'src/SPEC.json'),'source_cache_sha256':spec['source']['cache_sha256'],'source_rows':len(rows),'reconstructed_blocks':len(blocks),'synthetic_checks':n,'limits':['Source bookkeeping and conditional syntax consequence only; no semantic reading, q meaning or general conditional-language exclusion.','Only both-own-marked P blocks are primary; right-only and unknown endings stay distinct. RF flags are never borrowed.','No primary/legacy runner imported; no source images or new admissions.']}
    (HERE/'artifacts/VALIDATION.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(json.dumps(out))

# Filled against declared RESULT schema, never by importing primary computation.
def verify_result(result,blocks,rows):
    spec=json.loads((HERE/'src/SPEC.json').read_text())
    lock=json.loads((HERE/'LOCK.json').read_text())
    for pin in lock['files']:assert sha(ROOT/pin['path'])==pin['sha256']
    assert result['source_projection_sha256']==spec['source']['cache_sha256']
    editions=sorted({r['edition'] for r in rows});expected_counts={}
    for ed in editions:
        bb=[b for b in blocks if b['edition']==ed]
        expected_counts[ed]={'blocks':len(bb),'complete_blocks':sum(b['tier']=='primary' for b in bb),'right_only_blocks':sum(b['tier']=='right_only' for b in bb),'unmarked_end_blocks':sum(b['tier']=='unknown_end' for b in bb),'complete_q_end_blocks':sum(b['tier']=='primary' and bool(b['terminal_q_run']) for b in bb),'right_only_q_end_blocks':sum(b['tier']=='right_only' and bool(b['terminal_q_run']) for b in bb),'unmarked_q_end_blocks':sum(b['tier']=='unknown_end' and bool(b['terminal_q_run']) for b in bb),'q_only_groups':sum(len(b['empty_q_ids']) for b in bb)}
    assert result['per_reader']==expected_counts,('count mismatch',expected_counts,result['per_reader'])
    expected={tuple(g['source_group_id'] for g in b['groups']):b for b in blocks if b['end'] and b['terminal_q_run']}
    got={};blockids=[]
    def flag(v):
        assert v in [False,True,0,1,'0','1']
        return v is True or v==1 or v=='1'
    for b in result['counterparagraphs']:
        gs=[r for line in b['lines'] for r in line['groups']];key=tuple(r['source_group_id'] for r in gs)
        assert key not in got and key in expected;got[key]=b;want=expected[key]
        assert gs==want['groups'] and b['terminal_run']==want['terminal_q_run']
        assert b['edition']==want['edition'] and b['page']==want['page']
        assert flag(b['left_marked'])==want['start'] and flag(b['right_marked'])==want['end'] and flag(b['primary'])==(want['tier']=='primary')
        blockids.append((b['edition'],b['page'],b['block_id']))
        assert [l['locus'] for l in b['lines']]==want['loci']
        for line in b['lines']:
            rr=line['groups'];r=rr[0]
            assert line['source_row_index']==int(r['source_row_index']) and line['kind']==r['kind']
            assert flag(line['paragraph_start'])==(r['paragraph_start']=='1') and flag(line['paragraph_end'])==(r['paragraph_end']=='1')
    assert set(got)==set(expected) and len(blockids)==len(set(blockids))
    bad=sorted(ed for ed,v in expected_counts.items() if v['complete_q_end_blocks'])
    assert sorted(result['primary_falsified_editions'])==bad and result['translated_words']==0
    assert 'status' in result and isinstance(result['status'],str)

if __name__=='__main__':main()
