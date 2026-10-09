#!/usr/bin/env python3
"""Necessary capacity with at most one changed group per touched line."""
from collections import Counter, defaultdict
from pathlib import Path
import csv, hashlib, io, json, random, subprocess, sys
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]; A=E/'artifacts'
OLD=ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison'
sys.path.insert(0,str(OLD/'src'))
import metrics
BASE=ROOT/'experiments/yolo/gdt1202_whole_word_two_alias_capacity/artifacts'
GUARDED=ROOT/'experiments/yolo/gdt1170_repetition_context_neutral_copy/artifacts/GUARDED.tsv'
SPEC=ROOT/'experiments/yolo/gdt1170_repetition_context_neutral_copy/src/SPEC.json'
N=8000; BOOKS=('b4','w1','bs1','gr1')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,x): (A/name).write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def main():
    assert not (A/'RESULT.json').exists(), 'Use a clean reproduction checkout'
    for rel,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items(): assert sha(ROOT/rel)==h,rel
    allowed=json.loads(SPEC.read_text())['allowed']
    assert all(not p.startswith('f84') and p!='f116v' for p in allowed)
    cols='edition,page,locus,kind,source_group_index,source_group_count,ivtff_group_raw,left_separator,right_separator'
    cmd=['./vmanus-exp','query-tsv',str(GUARDED.relative_to(ROOT)),'--selector','page']
    for page in allowed: cmd+=['--allow',page]
    cmd+=['--columns',cols]
    call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    rows=[r for r in csv.DictReader(io.StringIO(call.stdout),delimiter='\t') if r['kind']=='P']
    pages=sorted({r['page'] for r in rows}); random.Random(1174).shuffle(pages); ranks={p:i for i,p in enumerate(pages)}
    rows.sort(key=lambda r:(ranks[r['page']],r['locus'],r['edition'],int(r['source_group_index'])))
    selected=defaultdict(list)
    for r in rows:
        if len(selected[r['edition']])==N: continue
        definite=r['left_separator'] in ('DEFINITE_SPACE','LINE_START') and r['right_separator'] in ('DEFINITE_SPACE','LINE_END')
        if definite and metrics.glyphs(r['ivtff_group_raw']): selected[r['edition']].append(r)
    target=json.loads((OLD/'artifacts/RESULT.json').read_text())['targets']
    native={}; sample_ids={}
    for ed,rs in sorted(selected.items()):
        assert len(rs)==N
        wc=Counter(r['ivtff_group_raw'] for r in rs); lines=Counter((r['page'],r['locus']) for r in rs)
        top=sum(sorted(wc.values(),reverse=True)[:10]); t=target[ed]
        assert len(wc)==t['types'] and top==round(N*t['top10_share'])
        native[ed]={'tokens':N,'types':len(wc),'top10_count':top,'touched_lines':len(lines),'type_min':len(wc)-400,'top10_max':top+400,
            'line_membership':[{'page':p,'locus':l,'sample_groups':n} for (p,l),n in sorted(lines.items())]}
        sample_ids[ed]=[f"{ed}|{r['locus']}|G{int(r['source_group_index']):03d}" for r in rs]
    assert set(native)=={'ZL3b','IT2a','RF1b'}
    frequencies=json.loads((BASE/'FREQUENCIES.json').read_text()); prior=json.loads((BASE/'RESULT.json').read_text())['books']
    outcomes={}
    for book in BOOKS:
        fs=[row['count'] for row in frequencies[book]]; assert sum(fs)==N
        d=len(fs); s=sum(sorted(fs,reverse=True)[:10]); assert d==prior[book]['source_types'] and s==prior[book]['source_top10_count']
        tests={}
        for ed,t in native.items():
            k=t['touched_lines']; maxd=min(N,d+k); mins=max(0,s-k)
            tests[ed]={'K_max':k,'types_upper':maxd,'top10_lower':mins,'types_capacity':maxd>=t['type_min'],'top10_capacity':mins<=t['top10_max'],
                'K_necessary_lower':max(0,t['type_min']-d,s-t['top10_max'])}
            tests[ed]['not_excluded']=tests[ed]['types_capacity'] and tests[ed]['top10_capacity']
        outcomes[book]={'source_types':d,'source_top10_count':s,'conditions':tests}
    passed=all(c['not_excluded'] for b in outcomes.values() for c in b['conditions'].values())
    result={'experiment':'GDT1211','status':'ONE_VARIANT_PER_LINE_NOT_EXCLUDED' if passed else 'ONE_VARIANT_PER_LINE_CAPACITY_EXCLUDED','native':native,'books':outcomes,
        'all_cases_not_excluded':passed,'claim_ceiling':'Necessary fixed-source/projected-target capacity only; no native causal shortening, word meaning, general language exclusion or independent confirmation.'}
    save('TARGET_SAMPLE_IDS.json',sample_ids);save('RESULT.json',result)
    save('RUN_RECEIPT.json',{'runner_sha256':sha(Path(__file__)),'guard_command':cmd,'guard_receipt':call.stderr.strip(),'guard_projection_sha256':hashlib.sha256(call.stdout.encode()).hexdigest()})
    print(json.dumps({'status':result['status'],'native':{ed:{k:v for k,v in t.items() if k!='line_membership'} for ed,t in native.items()},'books':outcomes},indent=2))
if __name__=='__main__':main()
