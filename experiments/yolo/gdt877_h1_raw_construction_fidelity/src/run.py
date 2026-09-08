"""Fixed construction source fidelity; no meaning inference."""
import csv, hashlib, json, subprocess
from collections import defaultdict
from pathlib import Path
B=Path(__file__).resolve().parents[1]; ROOT=B.parents[2]; A=B/'artifacts'
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,x): p.write_text(json.dumps(x,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
def query(d,pages):
    cmd=[str(ROOT/'vmanus-exp'),'query-tsv',d['path'],'--selector',d['selector']]
    for p in pages: cmd+=['--allow',p]
    cmd+=['--columns',','.join(d['columns']),'--forbid-prefix','f84','--forbid-prefix','f84r']
    z=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    stats=[json.loads(t[12:]) for t in z.stderr.splitlines() if t.startswith('GUARD_STATS ')]
    assert len(stats)==1
    return z.stdout,stats[0]
def main():
    for p,h in read(B/'src/PREREG_LOCK.json').items(): assert sha(ROOT/p)==h,p
    s=read(B/'src/SPEC.json'); ts=read(ROOT/s['targets_path'])
    assert len(ts)==5 and len({t['locus'] for t in ts})==5
    assert s['sealed_data']=={'f84':'FORBIDDEN','f84r':'FORBIDDEN'}
    assert not any(p.startswith('f84') for p in s['selectors'])
    prior=read(B/'src/TARGET_SOURCE_RECEIPT.json')
    old_text,_=query({'path':prior['source'],'selector':prior['selector'],'columns':prior['columns']},s['selectors'])
    assert hashlib.sha256(old_text.encode()).hexdigest()==prior['projection_sha256']
    assert list(csv.DictReader(old_text.splitlines(),delimiter='\t'))==ts
    wanted={(t['page'],t['locus']) for t in ts}; data={};receipts={}
    for name,d in s['sources'].items():
        text,stats=query(d,s['selectors']); cache=B/'runtime'/f'{name}.tsv'
        cache.parent.mkdir(exist_ok=True);cache.write_text(text)
        rows=list(csv.DictReader(text.splitlines(),delimiter='\t'))
        assert len(rows)==stats['selected'] and all(r['page'] in s['selectors'] for r in rows)
        data[name]=[r for r in rows if (r['page'],r['locus']) in wanted]
        receipts[name]={'source':d['path'],'projection_sha256':sha(cache),'guard_stats':stats,'retained_rows':len(data[name])}
        write(A/f'SOURCE_{name}.json',data[name])
    cross={(r['page'],r['locus']):r for r in data['CROSS']}; assert len(cross)==len(data['CROSS'])==5
    groups=defaultdict(list); ids=set()
    for r in data['ATLAS']:
        assert r['source_group_id'] not in ids;ids.add(r['source_group_id'])
        groups[r['page'],r['locus'],r['edition']].append(r)
    prepared={}; parity=[]
    for t in ts:
        for e in s['editions']:
            key=t['page'],t['locus'],e; gs=sorted(groups[key],key=lambda r:int(r['source_group_index']))
            clean=cross[key[:2]][s['clean_columns'][e]].split(); flat=[];mapped=[]
            if not gs:
                assert not clean,('missing raw but nonempty clean',key)
                prepared[key]=None;continue
            assert [int(g['source_group_index']) for g in gs]==list(range(1,len(gs)+1))
            for n,g in enumerate(gs):
                assert int(g['source_group_count'])==len(gs)
                fragments=g['clean_ascii_fragments'].split(); assert len(fragments)==int(g['clean_ascii_fragment_count'])
                pos=[int(x) for x in g['legacy_surface_positions_1based'].split(',')] if g['legacy_surface_positions_1based'] else []
                assert pos==list(range(len(flat)+1,len(flat)+len(fragments)+1))
                if n:
                    assert gs[n-1]['right_separator']==g['left_separator']
                    assert g['left_separator'] in ['DEFINITE_SPACE','UNCERTAIN_SMALL_SPACE','DRAWING_INTERRUPTION','DRAWING_INTERRUPTION_UNALIGNED']
                flat+=fragments;mapped.extend([g]*len(fragments))
            assert flat==clean,('full line parity',key)
            prepared[key]=(flat,mapped)
            parity.append({'page':t['page'],'locus':t['locus'],'edition':e,'raw_groups':len(gs),'clean_tokens':len(flat),'passed':True})
    out=[]
    for t in ts:
        pattern=t['written_pattern_eva'].split(); assert len(pattern)==3
        for e in s['editions']:
            row={'h1_field_id':t['h1_field_id'],'locus':t['locus'],'page':t['page'],'edition':e,'pattern':pattern,'clean_match_starts':[],'raw_groups':[],'group_indices':[],'internal_separators':[],'consecutive_raw_groups':False,'literal_single_raw_groups':False,'clear_internal_gaps':False,'eligible':False}
            entry=prepared[t['page'],t['locus'],e]
            if entry is None: row['status']='MISSING_READING';out.append(row);continue
            flat,mapped=entry;starts=[i for i in range(len(flat)-2) if flat[i:i+3]==pattern]
            row['clean_match_starts']=[i+1 for i in starts]
            if len(starts)!=1:
                row['status']='ABSENT_PATTERN' if not starts else 'AMBIGUOUS_PATTERN';out.append(row);continue
            i=starts[0]; selected=mapped[i:i+3];indices=[int(g['source_group_index']) for g in selected]
            consecutive=indices==list(range(indices[0],indices[0]+3))
            literal=all(int(g['clean_ascii_fragment_count'])==1 and g['ivtff_group_raw']==p and g['clean_ascii_fragments']==p for g,p in zip(selected,pattern))
            gaps=[g['right_separator'] for g in selected[:2]] if consecutive else []
            clear=consecutive and gaps==['DEFINITE_SPACE','DEFINITE_SPACE'];eligible=consecutive and literal and clear
            row.update(raw_groups=selected,group_indices=indices,internal_separators=gaps,consecutive_raw_groups=consecutive,literal_single_raw_groups=literal,clear_internal_gaps=clear,eligible=eligible,status='EXACT_CLEAR' if eligible else 'QUALIFIED');out.append(row)
    result={'experiment_id':'GDT877','status':'COMPLETE_FIXED_CONSTRUCTION_SOURCE_AUDIT','readings':out,'constructions':5,'reading_results':len(out),'all_three_eligible':sum(all(r['eligible'] for r in out if r['h1_field_id']==t['h1_field_id']) for t in ts),'eligible_by_edition':{e:sum(r['eligible'] for r in out if r['edition']==e) for e in s['editions']},'claim_ceiling':s['claim_ceiling']}
    write(A/'SOURCE_RECEIPTS.json',receipts);write(A/'LINE_PARITY.json',parity);write(A/'RESULT.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='readings'}))
if __name__=='__main__':main()
