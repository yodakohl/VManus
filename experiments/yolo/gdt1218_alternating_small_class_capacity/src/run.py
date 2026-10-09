#!/usr/bin/env python3
from pathlib import Path
from collections import Counter
import csv, hashlib, io, json, subprocess, sys
E=Path(__file__).resolve().parents[1]; ROOT=E.parents[2]; A=E/'artifacts'
P1174=ROOT/'experiments/yolo/gdt1174_ten_scribes_forward_comparison'
P1170=ROOT/'experiments/yolo/gdt1170_repetition_context_neutral_copy'
IDS=ROOT/'experiments/yolo/gdt1211_one_variant_per_line_capacity/artifacts/TARGET_SAMPLE_IDS.json'
sys.path.insert(0,str(P1174/'src')); import metrics
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, value): (A/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
def main():
    assert not (A/'RESULT.json').exists()
    for rel,h in json.loads((A/'REGISTRATION_LOCK.json').read_text())['files'].items(): assert digest(ROOT/rel)==h,rel
    allowed=json.loads((P1170/'src/SPEC.json').read_text())['allowed']
    assert all(not p.startswith('f84') and p!='f116v' for p in allowed)
    cmd=['./vmanus-exp','query-tsv',str((P1170/'artifacts/GUARDED.tsv').relative_to(ROOT)),'--selector','page']
    for p in allowed: cmd.extend(['--allow',p])
    cmd+=['--columns','edition,page,locus,kind,source_group_index,source_group_count,ivtff_group_raw,left_separator,right_separator']
    q=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,check=True)
    sample=json.loads(IDS.read_text()); wanted={x for xs in sample.values() for x in xs}; selected={}
    for r in csv.DictReader(io.StringIO(q.stdout),delimiter='\t'):
        uid=f"{r['edition']}|{r['locus']}|G{int(r['source_group_index']):03d}"
        if uid not in wanted: continue
        assert uid not in selected
        assert r['kind']=='P' and r['left_separator'] in ('DEFINITE_SPACE','LINE_START') and r['right_separator'] in ('DEFINITE_SPACE','LINE_END')
        assert metrics.glyphs(r['ivtff_group_raw'])
        selected[uid]=r
    assert set(selected)==wanted and len(wanted)==24000
    targets=json.loads((P1174/'artifacts/RESULT.json').read_text())['targets']; out={}; certs={}
    for ed,ids in sorted(sample.items()):
        assert len(ids)==8000
        rs=[selected[x] for x in ids]; counts=Counter(r['ivtff_group_raw'] for r in rs)
        assert len(counts)==targets[ed]['types'] and sum(sorted(counts.values(),reverse=True)[:10])==round(8000*targets[ed]['top10_share'])
        bypos={(r['page'],r['locus'],int(r['source_group_index'])):r for r in rs}; used=set(); cert=[]
        for left in rs:
            j=int(left['source_group_index']); right=bypos.get((left['page'],left['locus'],j+1))
            if right is None or left['right_separator']!='DEFINITE_SPACE' or right['left_separator']!='DEFINITE_SPACE': continue
            a=left['ivtff_group_raw'];b=right['ivtff_group_raw']
            if a==b or a in used or b in used: continue
            cert.append({'page':left['page'],'locus':left['locus'],'left_index':j,'right_index':j+1,'left':a,'right':b});used.update((a,b))
            if len(cert)==65: break
        certs[ed]=cert
        out[ed]={'selected_groups':len(rs),'types':len(counts),'top10_count':sum(sorted(counts.values(),reverse=True)[:10]),'certificate_edges':len(cert),'distinct_endpoint_forms':len(used),'minimum_small_class_size_certified':len(cert),'status':'EXCLUDED_64_FORM_ALTERNATION' if len(cert)==65 else 'NOT_EXCLUDED_BY_THIS_CERTIFICATE'}
    result={'experiment':'GDT1218','status':'EXCLUDED_64_FORM_ALTERNATION' if any(x['certificate_edges']==65 for x in out.values()) else 'NOT_EXCLUDED_BY_THIS_CERTIFICATE','readers':out,'scope':'Fixed global whole-form class <=64, strict within-line alternation, conditional on existing transcriptions; no meanings or general semantic grammar exclusion.'}
    save('CERTIFICATES.json',certs); save('RESULT.json',result)
    save('RUN_RECEIPT.json',{'guard_command':cmd,'guard_receipt':q.stderr.strip(),'projection_sha256':hashlib.sha256(q.stdout.encode()).hexdigest(),'sample_ids_sha256':digest(IDS)})
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
