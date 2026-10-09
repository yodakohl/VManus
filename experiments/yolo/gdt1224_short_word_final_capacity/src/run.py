#!/usr/bin/env python3
"""Necessary short-group capacity, without fitting or rescoring a writer."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import argparse,csv,hashlib,io,json,subprocess,sys
D=Path(__file__).resolve().parents[1]; ROOT=D.parents[2]; A=D/'artifacts'
sys.path.insert(0,str(ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison/src'))
import metrics as m
S=json.loads((D/'src/SPEC.json').read_text())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,default=A);args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True);assert not (args.out/'RESULT.json').exists()
    started=datetime.now(timezone.utc).isoformat()
    for p,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items():
        assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    allowed=json.loads((ROOT/S['scope_spec']).read_text())['allowed']
    assert len(allowed)==179 and all(not p.startswith('f84') and p!='f116v' for p in allowed)
    cmd=['./vmanus-exp','query-tsv',S['source'],'--selector','page']
    for p in allowed:cmd+=['--allow',p]
    cmd+=['--columns','edition,page,locus,kind,source_group_index,ivtff_group_raw,left_separator,right_separator']
    call=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,check=True)
    rows={}
    for r in csv.DictReader(io.StringIO(call.stdout),delimiter='\t'):
        key=f"{r['edition']}|{r['locus']}|G{int(r['source_group_index']):03d}"
        assert key not in rows;rows[key]=r
    ids=json.loads((ROOT/S['anchor_ids']).read_text());out={}
    for ed,selected in sorted(ids.items()):
        assert len(selected)==len(set(selected))==8000
        counts=Counter();finals=Counter();witness={};all_short=0
        for key in selected:
            r=rows[key];gs=m.glyphs(r['ivtff_group_raw'])
            assert r['edition']==ed and r['kind']=='P' and gs
            assert r['left_separator'] in ('DEFINITE_SPACE','LINE_START') and r['right_separator'] in ('DEFINITE_SPACE','LINE_END')
            if len(gs)!=2:continue
            all_short+=1
            if (r['left_separator'],r['right_separator'])!=('DEFINITE_SPACE','DEFINITE_SPACE'):continue
            counts[r['ivtff_group_raw']]+=1;finals[gs[-1]]+=1
            witness.setdefault(gs[-1],dict(id=key,word=r['ivtff_group_raw'],glyphs=gs,page=r['page'],locus=r['locus'],source_group_index=int(r['source_group_index']),left_separator=r['left_separator'],right_separator=r['right_separator']))
        out[ed]={'sample_groups':8000,'all_two_glyph_groups':all_short,'internal_two_glyph_groups':sum(counts.values()),'internal_two_glyph_types':len(counts),'final_glyph_types':len(finals),'final_counts':dict(sorted(finals.items())),'word_counts':dict(sorted(counts.items())),'witnesses':dict(sorted(witness.items())),'exceeds_bound':len(finals)>6}
    passed=[ed for ed,r in out.items() if r['exceeds_bound']]
    status='SIX_FINAL_SHORT_GROUP_ARCHITECTURE_EXCLUDED' if len(passed)==3 else 'SIX_FINAL_BOUND_EXCEEDED_SOME_READINGS' if passed else 'NO_SHORT_FINAL_CONTRADICTION_IN_FIXED_SAMPLE'
    result={'experiment':'GDT1224','status':status,'model_final_capacity':6,'readings':out,'claim_ceiling':S['claim_ceiling']}
    (args.out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    (args.out/'RUN_RECEIPT.json').write_text(json.dumps({'started_utc':started,'finished_utc':datetime.now(timezone.utc).isoformat(),'guard_command':cmd,'guard_receipt':call.stderr.strip(),'guard_output_sha256':hashlib.sha256(call.stdout.encode()).hexdigest()},indent=2)+'\n')
    print(json.dumps({'status':status,'readings':{ed:{k:r[k] for k in ('internal_two_glyph_groups','internal_two_glyph_types','final_glyph_types','final_counts')} for ed,r in out.items()}},indent=2))
if __name__=='__main__':main()
