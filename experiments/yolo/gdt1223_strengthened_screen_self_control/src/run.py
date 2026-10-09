#!/usr/bin/env python3
"""Frozen stronger-screen self-control; no candidate fitting."""
from pathlib import Path
from collections import defaultdict, Counter
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime, timezone
import argparse,csv,hashlib,io,json,multiprocessing,random,subprocess,sys
D=Path(__file__).resolve().parents[1];ROOT=D.parents[2];A=D/'artifacts'
sys.path.insert(0,str(ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/src'))
import metrics as m
m.glyphs=lru_cache(maxsize=None)(m.glyphs)
SPEC=json.loads((D/'src/SPEC.json').read_text())
BY={};PAGES=[];TARGET={};PRIOR={}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(x):return hashlib.sha256(json.dumps(x,separators=(',',':')).encode()).hexdigest()
def compare(a,b):
    rows=m.compare(a,b)['diagnostics']
    extras={'tight_edit1':(abs(a['edit1_repeat']-b['edit1_repeat']),.01),
            'q_followed_o':(abs(a['q_followed_o']-b['q_followed_o']),.03),
            'q_count':(abs(a['q_count']-b['q_count']),.25*b['q_count']),
            'y_final':(abs(a['y_final']-b['y_final']),.05),
            'glyph_entropy':(abs(a['glyph_entropy']-b['glyph_entropy']),.15),
            'word_entropy':(abs(a['word_entropy']-b['word_entropy']),.30)}
    rows.update({k:{'difference':d,'limit':lim,'within':d<=lim} for k,(d,lim) in extras.items()})
    assert len(rows)==16
    return {k:{f:r[f] for f in ('difference','limit','within')} for k,r in rows.items()}
def sample(seed):
    order=PAGES.copy();random.Random(seed).shuffle(order);readings={};ids_by={}
    for ed in sorted(TARGET):
        segments=[];ids=[];touched=set();remaining=8000
        for page in order:
            for seg in BY.get((ed,page),[]):
                part=seg[:remaining]
                if part:
                    segments.append([w for w,_ in part]);ids.extend(i for _,i in part);touched.add(page);remaining-=len(part)
                if not remaining:break
            if not remaining:break
        assert not remaining
        met=m.measure(segments)
        assert met['q_followed_o'] is not None and met['adjacent_pairs']>0
        if seed==1174:ids_by[ed]=ids
        else:
            old=PRIOR[seed]['readers'][ed]
            assert digest(ids)==old['sample_ids_sha256']
            assert met['types']==old['types'] and round(met['top10_share']*8000)==old['top10_count']
        readings[ed]={'sample_ids_sha256':digest(ids),'last_group_id':ids[-1],'pages_touched':len(touched),'metrics':met}
    comparisons={f'{ed}->{ref}':compare(r['metrics'],t) for ed,r in readings.items() for ref,t in TARGET.items()}
    pair_pass={k:all(x['within'] for x in rows.values()) for k,rows in comparisons.items()}
    out={'seed':seed,'readings':readings,'comparisons':comparisons,'pair_pass':pair_pass,
         'all_cross':all(pair_pass.values()),'all_matched':all(pair_pass[f'{ed}->{ed}'] for ed in TARGET)}
    if seed==1174:
        assert ids_by==json.loads((ROOT/SPEC['anchor_ids']).read_text())
        for ed in TARGET:
            for k,v in TARGET[ed].items():
                got=readings[ed]['metrics'][k]
                if isinstance(v,dict):assert got==v,(ed,k)
                elif isinstance(v,(int,float)):assert abs(got-v)<=1e-10,(ed,k,got,v)
                else:assert got==v
    return out

def main():
    global BY,PAGES,TARGET,PRIOR
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=A);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    assert not (args.out/'RESULT.json').exists(),'Use a fresh --out directory for replay.'
    started=datetime.now(timezone.utc).isoformat()
    for rel,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():assert sha(ROOT/rel)==h,rel
    allowed=json.loads((ROOT/SPEC['scope_spec']).read_text())['allowed'];assert len(allowed)==179
    assert all(not p.startswith('f84') and p!='f116v' for p in allowed)
    cmd=['./vmanus-exp','query-tsv',SPEC['source'],'--selector','page']
    for page in allowed:cmd+=['--allow',page]
    cmd+=['--columns','edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator']
    call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    lines=defaultdict(list)
    for r in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
        if r['kind']=='P':lines[r['edition'],r['page'],r['locus']].append(r)
    PAGES=sorted({p for _,p,_ in lines});BY=defaultdict(list);eligible=Counter()
    for (ed,page,loc),rs in sorted(lines.items()):
        seg=[];prev=None
        for r in sorted(rs,key=lambda r:int(r['source_group_index'])):
            valid=(r['left_separator'] in ('DEFINITE_SPACE','LINE_START') and r['right_separator'] in ('DEFINITE_SPACE','LINE_END') and bool(m.glyphs(r['ivtff_group_raw'])))
            linked=prev is not None and int(r['source_group_index'])==int(prev['source_group_index'])+1 and prev['right_separator']==r['left_separator']=='DEFINITE_SPACE'
            if not valid or (seg and not linked):
                if seg:BY[ed,page].append(seg);seg=[]
            if valid:
                seg.append((r['ivtff_group_raw'],f"{ed}|{loc}|G{int(r['source_group_index']):03d}"));eligible[ed]+=1
            prev=r
        if seg:BY[ed,page].append(seg)
    prior=json.loads((ROOT/SPEC['prior_frequency_control']).read_text());PRIOR={r['seed']:r for r in prior['samples']}
    base=json.loads((ROOT/SPEC['reference']).read_text());TARGET=base['targets']
    assert dict(eligible)==prior['eligible_groups']
    assert len(PAGES)==prior['prose_page_universe']
    anchor=sample(1174);print(json.dumps({'stage':'ANCHOR_ALL_METRICS_AND_24000_IDS_PASS','cross_pass':anchor['all_cross']}),flush=True)
    with ProcessPoolExecutor(max_workers=16,mp_context=multiprocessing.get_context('fork')) as pool:
        samples=list(pool.map(sample,SPEC['seeds']))
    pairs=sorted(samples[0]['pair_pass']);gates=sorted(next(iter(samples[0]['comparisons'].values())))
    joint=sum(r['all_cross'] for r in samples);matched=sum(r['all_matched'] for r in samples)
    pair_counts={k:sum(r['pair_pass'][k] for r in samples) for k in pairs}
    failures={k:{g:sum(not r['comparisons'][k][g]['within'] for r in samples) for g in gates} for k in pairs}
    metric_names=[k for k,v in anchor['readings'][next(iter(TARGET))]['metrics'].items() if isinstance(v,(int,float))]
    ranges={ed:{k:[min(r['readings'][ed]['metrics'][k] for r in samples),max(r['readings'][ed]['metrics'][k] for r in samples)] for k in metric_names} for ed in TARGET}
    result={'experiment':'GDT1223','status':'STRENGTHENED_SCREEN_OPERATIONALLY_STABLE' if joint>=122 else 'STRENGTHENED_SCREEN_OPERATIONALLY_UNSTABLE',
            'joint_cross_passes':joint,'joint_matched_passes':matched,'required_joint_passes':122,'seeds':128,'pair_pass_counts':pair_counts,
            'gate_failure_counts':failures,'metric_ranges':ranges,'eligible_groups':dict(eligible),'prose_page_universe':len(PAGES),
            'anchor':anchor,'samples':samples,'claim_ceiling':'Overlapping exposed selection sensitivity only; no independent error rate, meaning, writer rescue or threshold revision.'}
    (args.out/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    receipt={'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'guard_command':cmd,'guard_receipt':call.stderr.strip(),'guard_output_sha256':hashlib.sha256(call.stdout.encode()).hexdigest(),'workers':16}
    (args.out/'RUN_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','joint_cross_passes','joint_matched_passes','pair_pass_counts')},indent=2))
if __name__=='__main__':main()
